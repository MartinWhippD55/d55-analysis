"""
Build a deterministic Jira creation plan from a spec-to-stories decomposition.

Input is a decomposition folder produced by the `spec-to-stories` skill:

    <root>/graph.yaml                    parentSpec, story order, edges, waves
    <root>/stories/<id>/manifest.yaml    per-story title/userStory/subtasks/jira meta

Output is a `JiraPlan`: an ordered, side-effect-free description of the issues to
create and the links to make. The plan is what the *agent* executes by calling the
Atlassian Jira MCP; this module never touches Jira. Keeping the maths here makes
the export deterministic and testable, and keeps the agent's job to "look up, then
create".

Mapping (the spec-to-stories convention):
    parent spec        -> Epic
    each story (US-xx) -> Story  under the epic
    each sub-task      -> Sub-task under its story
    dependency edge    -> "Blocks" link (dst blocks src: dst must ship first)

Idempotency: every planned issue carries a **stable identity label** derived from
the parent spec + its id (e.g. `s2s-<parent>-US-01`). Before creating anything the
agent searches for that label; if a match exists it reuses the key instead of
creating a duplicate. Identity labels are stable across runs, so re-running the
export is safe.
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

import yaml

# Prefix that scopes every label and JQL lookup this skill emits.
LABEL_PREFIX = "s2s"
BLOCKS_LINK_TYPE = "Blocks"


def sanitize_label(text: str) -> str:
    """Jira labels may not contain spaces. Collapse anything that is not a
    letter, digit, dot, underscore or hyphen into a single hyphen so the label
    is a stable, valid token."""
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", text.strip())
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-")
    return cleaned


@dataclass
class SubtaskPlan:
    tid: str
    summary: str
    identity_label: str
    labels: list[str]
    requirements: list[str] = field(default_factory=list)
    optional: bool = False


@dataclass
class StoryPlan:
    sid: str
    summary: str
    description: str
    issue_type: str
    identity_label: str
    labels: list[str]
    covers_requirements: list[str] = field(default_factory=list)
    estimate_days: Optional[float] = None
    subtasks: list[SubtaskPlan] = field(default_factory=list)


@dataclass
class EpicPlan:
    summary: str
    epic_name: str
    description: str
    identity_label: str
    labels: list[str]


@dataclass
class LinkPlan:
    """`outward` blocks `inward` (outward must ship first). These are story ids;
    the agent resolves them to freshly created Jira keys before making the link."""

    link_type: str
    outward: str
    inward: str
    via: list[str] = field(default_factory=list)


@dataclass
class JiraPlan:
    parent_spec: str
    set_label: str
    epic: EpicPlan
    stories: list[StoryPlan] = field(default_factory=list)
    links: list[LinkPlan] = field(default_factory=list)
    waves: list[list[str]] = field(default_factory=list)


def load_decomposition(root: str | Path) -> tuple[dict, dict[str, dict]]:
    """Read `graph.yaml` and every `stories/<id>/manifest.yaml` under `root`.

    Returns (graph_dict, {story_id: manifest_dict}). Raises FileNotFoundError if
    the graph is missing and ValueError if a story listed in the graph has no
    manifest."""
    root = Path(root)
    graph_path = root / "graph.yaml"
    if not graph_path.exists():
        raise FileNotFoundError(f"No graph.yaml under {root}")
    with open(graph_path, "r", encoding="utf-8") as f:
        graph = yaml.safe_load(f) or {}

    manifests: dict[str, dict] = {}
    for sid in graph.get("stories", []):
        mpath = root / "stories" / str(sid) / "manifest.yaml"
        if not mpath.exists():
            raise ValueError(f"Story {sid} in graph.yaml has no manifest at {mpath}")
        with open(mpath, "r", encoding="utf-8") as f:
            manifests[str(sid)] = yaml.safe_load(f) or {}
    return graph, manifests


def _story_description(manifest: dict, identity_label: str) -> str:
    """Build a Story description from its manifest, with a traceability footer so
    the issue can always be tied back to its mini-spec and requirements."""
    user_story = (manifest.get("userStory") or manifest.get("user_story") or "").strip()
    covers = [str(r) for r in manifest.get("coversRequirements", manifest.get("covers_requirements", []))]
    lines: list[str] = []
    if user_story:
        lines.append(user_story)
        lines.append("")
    if covers:
        lines.append(f"Covers parent requirements: {', '.join(covers)}")
    lines.append(f"Traceability: {identity_label}")
    return "\n".join(lines).strip()


def build_plan(root: str | Path) -> JiraPlan:
    """Turn a decomposition folder into a deterministic `JiraPlan`.

    Order is stable: stories follow `graph.yaml`'s `stories` list, sub-tasks follow
    manifest order, and links follow `edges` order."""
    graph, manifests = load_decomposition(root)
    parent = str(graph.get("parentSpec") or Path(root).parent.name)
    set_label = sanitize_label(f"{LABEL_PREFIX}-{parent}")

    epic = EpicPlan(
        summary=f"{parent} (delivery)",
        epic_name=parent,
        description=f"Umbrella epic decomposed from spec '{parent}' by spec-to-stories.",
        identity_label=sanitize_label(f"{LABEL_PREFIX}-{parent}-epic"),
        labels=[set_label, sanitize_label(f"{LABEL_PREFIX}-{parent}-epic")],
    )

    stories: list[StoryPlan] = []
    for sid in graph.get("stories", []):
        sid = str(sid)
        m = manifests[sid]
        jira = m.get("jira", {}) or {}
        identity = sanitize_label(f"{LABEL_PREFIX}-{parent}-{sid}")
        base_labels = [sanitize_label(str(l)) for l in jira.get("labels", [])]
        story_labels = [set_label, identity] + base_labels

        subtasks: list[SubtaskPlan] = []
        for t in m.get("subtasks", []) or []:
            tid = str(t["id"])
            t_identity = sanitize_label(f"{LABEL_PREFIX}-{parent}-{tid}")
            t_labels = [set_label, t_identity]
            if t.get("optional"):
                t_labels.append("optional")
            subtasks.append(
                SubtaskPlan(
                    tid=tid,
                    summary=t.get("title", tid),
                    identity_label=t_identity,
                    labels=t_labels,
                    requirements=[str(r) for r in t.get("requirements", [])],
                    optional=bool(t.get("optional", False)),
                )
            )

        stories.append(
            StoryPlan(
                sid=sid,
                summary=m.get("title", sid),
                description=_story_description(m, identity),
                issue_type=jira.get("issueType", jira.get("issue_type", "Story")),
                identity_label=identity,
                labels=story_labels,
                covers_requirements=[str(r) for r in m.get("coversRequirements", m.get("covers_requirements", []))],
                estimate_days=jira.get("estimateDays", jira.get("estimate_days")),
                subtasks=subtasks,
            )
        )

    # edges: {from: src, to: dst} means src depends on dst -> dst blocks src.
    links: list[LinkPlan] = []
    for e in graph.get("edges", []) or []:
        src = str(e.get("from"))
        dst = str(e.get("to"))
        via = [str(v) for v in e.get("via", [])]
        links.append(LinkPlan(link_type=BLOCKS_LINK_TYPE, outward=dst, inward=src, via=via))

    waves = [[str(s) for s in w.get("stories", [])] for w in graph.get("waves", []) or []]

    return JiraPlan(
        parent_spec=parent,
        set_label=set_label,
        epic=epic,
        stories=stories,
        links=links,
        waves=waves,
    )


def plan_to_dict(plan: JiraPlan) -> dict:
    return asdict(plan)


def write_plan(plan: JiraPlan, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(plan_to_dict(plan), f, indent=2)


def summarize(plan: JiraPlan) -> str:
    """A short human summary of what the plan will create."""
    n_sub = sum(len(s.subtasks) for s in plan.stories)
    return (
        f"{plan.parent_spec}: 1 epic, {len(plan.stories)} stories, "
        f"{n_sub} sub-tasks, {len(plan.links)} blocks-links "
        f"(set label '{plan.set_label}')."
    )
