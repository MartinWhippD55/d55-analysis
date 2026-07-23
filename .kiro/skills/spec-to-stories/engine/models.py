"""
Core data models for spec-to-stories.

A parent spec is decomposed into a set of user Stories. Each story delivers
(exports) a set of software Components and consumes (depends on) components
exported by other stories. From those export/depend relations we build a
dependency graph and topologically sort it into implementation waves.

All models are plain dataclasses with light validation so they are easy to
construct from YAML manifests and to test.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# Controlled vocabulary of component kinds. `OTHER` is the escape hatch; the
# `kind` on a Component is free-form but SHOULD be one of these for consistent
# graphing and Jira labelling.
COMPONENT_KINDS = (
    "data-table",
    "gsi",
    "s3-bucket",
    "api-endpoint",
    "lambda",
    "state-machine",
    "cdk-construct",
    "cdk-stack",
    "cdk-instance",
    "frontend-component",
    "frontend-screen",
    "web-component",
    "service",
    "type",
    "shared-lib",
    "other",
)


@dataclass(frozen=True)
class Component:
    """A single software component, identified by `kind:name`.

    Equality/hashing is by the normalised (kind, name) pair so the same
    component referenced from two stories resolves to one graph node.
    """

    kind: str
    name: str

    def __post_init__(self) -> None:
        if not self.kind or not self.kind.strip():
            raise ValueError("Component.kind must be non-empty")
        if not self.name or not self.name.strip():
            raise ValueError("Component.name must be non-empty")
        # normalise
        object.__setattr__(self, "kind", self.kind.strip().lower())
        object.__setattr__(self, "name", self.name.strip())

    @property
    def ref(self) -> str:
        return f"{self.kind}:{self.name}"

    @classmethod
    def parse(cls, ref: str) -> "Component":
        """Parse a `kind:name` reference. Only the first colon splits, so
        names may contain colons (e.g. `api-endpoint:GET /x?a=b`)."""
        if ":" not in ref:
            raise ValueError(f"Component ref must be 'kind:name', got: {ref!r}")
        kind, name = ref.split(":", 1)
        return cls(kind=kind, name=name)

    def __str__(self) -> str:  # pragma: no cover - convenience
        return self.ref


@dataclass
class JiraMeta:
    issue_type: str = "Story"
    epic: Optional[str] = None
    labels: list[str] = field(default_factory=list)
    estimate_days: Optional[float] = None


@dataclass
class SubTask:
    """A coding sub-task within a story (maps to a Jira sub-task)."""

    id: str
    title: str
    requirements: list[str] = field(default_factory=list)
    optional: bool = False


@dataclass
class Story:
    """A user story: a vertical slice of the parent spec."""

    id: str
    title: str
    user_story: str = ""
    covers_requirements: list[str] = field(default_factory=list)
    exports: list[Component] = field(default_factory=list)
    depends_on: list[Component] = field(default_factory=list)
    subtasks: list[SubTask] = field(default_factory=list)
    jira: JiraMeta = field(default_factory=JiraMeta)

    def __post_init__(self) -> None:
        if not self.id or not self.id.strip():
            raise ValueError("Story.id must be non-empty")

    @property
    def export_refs(self) -> set[str]:
        return {c.ref for c in self.exports}

    @property
    def depend_refs(self) -> set[str]:
        return {c.ref for c in self.depends_on}


@dataclass
class Edge:
    """`src` depends on `dst` (dst must be implemented first), via components."""

    src: str  # story id
    dst: str  # story id
    via: list[str] = field(default_factory=list)  # component refs


@dataclass
class Issue:
    """A validation problem found while building the graph."""

    kind: str  # dangling-dependency | duplicate-exporter | cycle | self-dependency | uncovered-requirement
    detail: str
    stories: list[str] = field(default_factory=list)
    components: list[str] = field(default_factory=list)


@dataclass
class Decomposition:
    """The full result: stories, resolved edges, waves, and any issues."""

    parent_spec: str
    stories: list[Story]
    edges: list[Edge] = field(default_factory=list)
    waves: list[list[str]] = field(default_factory=list)  # each wave = list of story ids
    issues: list[Issue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """True when there are no blocking issues (cycles / dangling deps /
        duplicate exporters). Uncovered requirements are warnings, not blockers."""
        blocking = {"dangling-dependency", "duplicate-exporter", "cycle", "self-dependency"}
        return not any(i.kind in blocking for i in self.issues)
