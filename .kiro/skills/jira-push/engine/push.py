"""
Plan and reconcile a push of a *Jira tree* into live Jira.

Why this exists
---------------
`jira-tree` renders an editable filesystem mirror of the Jira hierarchy (Epic ->
Stories -> Sub-tasks + "blocks" links) and lets you enrich the descriptions locally.
`jira-push` is the step that takes that reviewed tree and creates the matching issues
in Jira — idempotently, so re-running never duplicates anything.

The push itself is a sequence of Atlassian MCP calls, which only the agent can make.
What this module owns is the **deterministic, no-Jira core** of that push:

1. `build_push_plan(tree)` — turn a loaded tree into an **ordered action list**
   (epic first, then each story followed by its sub-tasks, then the links). The order
   guarantees a parent always precedes its children and every story exists before any
   link that references it.
2. `reconcile(plan, existing_labels, existing_links)` — given what the agent has
   already found in Jira (issue identity labels that exist, links that exist), mark
   each action `create` / `reuse` / `skip`. Pure and total: the agent then walks the
   plan and only calls the MCP for `create` actions.
3. `validate_plan(plan)` — structural invariants (single epic first, parents precede
   children, unique identity refs, link endpoints are known stories).

Idempotency is by **identity label** — copied straight through from the tree
(`s2s-<parent>-epic`, `s2s-<parent>-US-01`, `s2s-<parent>-US-01-1`), exactly matching
`decomposition-to-jira` and `jira-tree`. Links dedupe by their `(outward, inward)`
story-key pair.

This module makes no Jira calls and does not import the network. `load_tree_view`
is a thin adapter that reuses the sibling `jira-tree` engine to read a real tree from
disk; everything else operates on plain, duck-typed objects so the core is testable
in isolation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Optional

BLOCKS_LINK_TYPE = "Blocks"

# Action kinds
EPIC = "epic"
STORY = "story"
SUBTASK = "subtask"
LINK = "link"

# Ops (set by reconcile)
CREATE = "create"
REUSE = "reuse"
SKIP = "skip"

# The mini-spec files attached to a story issue in opt-in attachment mode. These are
# the authoritative source the tree's story body was derived from; attaching them is
# a traceability aid, not the source of truth (see the staleness note in SKILL.md).
DEFAULT_SPEC_FILES = ("requirements.md", "design.md", "tasks.md")


# --------------------------------------------------------------------------- #
# Push-plan models (this module's unique contribution)
# --------------------------------------------------------------------------- #
@dataclass
class AttachmentAction:
    """A single mini-spec file to upload to a story issue (opt-in attachment mode)."""

    filename: str  # e.g. "design.md" — the dedupe key within an issue
    source_path: str  # absolute/relative path the agent uploads from
    op: str = CREATE  # CREATE | SKIP (set by reconcile)


@dataclass
class IssueAction:
    """A single epic/story/sub-task to create-or-reuse in Jira."""

    kind: str  # EPIC | STORY | SUBTASK
    ref: str  # identity_label — the idempotency key
    key: str  # human key: epic_name / US-01 / US-01-1 (for reporting)
    summary: str
    issue_type: str
    description: str = ""
    labels: list[str] = field(default_factory=list)
    parent_ref: str = ""  # identity_label of the parent (epic for a story, story for a sub-task)
    estimate_days: Optional[float] = None
    attachments: list[AttachmentAction] = field(default_factory=list)  # stories only, opt-in
    op: str = CREATE  # CREATE | REUSE (set by reconcile)


@dataclass
class LinkAction:
    """A single "blocks" link to create in Jira. outward blocks inward."""

    outward: str  # story key that ships first (blocks)
    inward: str  # story key that is blocked
    outward_ref: str = ""  # identity_label of the outward story
    inward_ref: str = ""  # identity_label of the inward story
    link_type: str = BLOCKS_LINK_TYPE
    op: str = CREATE  # CREATE | SKIP (set by reconcile)


@dataclass
class PushPlan:
    parent_spec: str
    set_label: str
    issues: list[IssueAction] = field(default_factory=list)
    links: list[LinkAction] = field(default_factory=list)


# --------------------------------------------------------------------------- #
# Build a push plan from a (loaded) tree
# --------------------------------------------------------------------------- #
def build_push_plan(tree) -> PushPlan:
    """Turn a loaded tree into an ordered, idempotent `PushPlan`.

    `tree` is duck-typed on the `jira-tree` `Tree` model: it must expose
    `parent_spec`, `set_label`, `epic`, `stories` and `links`, where `epic` has
    `summary/epic_name/identity_label/labels/issue_type/description`, each story has
    `key/summary/identity_label/labels/issue_type/description/estimate_days/subtasks`,
    each sub-task has `key/summary/identity_label/labels/issue_type/description`, and
    each link has `outward/inward/link_type`.

    Ordering: epic, then for every story (in tree order) the story immediately
    followed by its sub-tasks, then all links. This guarantees a parent is always
    created before its children and every story exists before its links are made.
    All actions start as ``create``; call `reconcile` to mark reuse/skip.
    """
    epic = tree.epic
    issues: list[IssueAction] = [
        IssueAction(
            kind=EPIC,
            ref=epic.identity_label,
            key=epic.epic_name,
            summary=epic.summary,
            issue_type=getattr(epic, "issue_type", "Epic"),
            description=epic.description,
            labels=list(epic.labels),
            parent_ref="",
        )
    ]

    # map story key -> identity label so links can carry both
    label_of: dict[str, str] = {s.key: s.identity_label for s in tree.stories}

    for story in tree.stories:
        issues.append(
            IssueAction(
                kind=STORY,
                ref=story.identity_label,
                key=story.key,
                summary=story.summary,
                issue_type=getattr(story, "issue_type", "Story"),
                description=story.description,
                labels=list(story.labels),
                parent_ref=epic.identity_label,
                estimate_days=getattr(story, "estimate_days", None),
            )
        )
        for sub in story.subtasks:
            issues.append(
                IssueAction(
                    kind=SUBTASK,
                    ref=sub.identity_label,
                    key=sub.key,
                    summary=sub.summary,
                    issue_type=getattr(sub, "issue_type", "Sub-task"),
                    description=sub.description,
                    labels=list(sub.labels),
                    parent_ref=story.identity_label,
                )
            )

    links: list[LinkAction] = [
        LinkAction(
            outward=l.outward,
            inward=l.inward,
            outward_ref=label_of.get(l.outward, ""),
            inward_ref=label_of.get(l.inward, ""),
            link_type=getattr(l, "link_type", BLOCKS_LINK_TYPE),
        )
        for l in tree.links
    ]

    return PushPlan(
        parent_spec=tree.parent_spec,
        set_label=tree.set_label,
        issues=issues,
        links=links,
    )


# --------------------------------------------------------------------------- #
# Opt-in: attach each story's mini-spec files
# --------------------------------------------------------------------------- #
def attach_specs(
    plan: PushPlan,
    stories_dir: str,
    which: Iterable[str] = DEFAULT_SPEC_FILES,
) -> PushPlan:
    """Return a new `PushPlan` with each **story** action carrying attachment actions
    for the mini-spec files that exist under ``<stories_dir>/<story.key>/``.

    `stories_dir` is the decomposition's `stories/` folder (sibling of `jira-tree/`),
    where each `US-xx/` holds `requirements.md`, `design.md`, `tasks.md`. Only files
    that actually exist are added; a missing file is silently skipped. All added
    attachments start as `create`; call `reconcile(..., existing_attachments=...)` to
    mark ones already uploaded as `skip`.

    Opt-in and non-destructive: epics and sub-tasks are never given attachments, and
    the returned plan is a copy (the input is not mutated). This is a traceability aid
    — the attached spec files are the source the story body was derived from and can
    drift from it; the tree/description remains what is reviewed.
    """
    from pathlib import Path

    root = Path(stories_dir)
    want = list(which)

    def _attachments_for(story_key: str) -> list[AttachmentAction]:
        sdir = root / story_key
        out: list[AttachmentAction] = []
        for name in want:
            p = sdir / name
            if p.exists():
                out.append(AttachmentAction(filename=name, source_path=str(p)))
        return out

    issues = [
        IssueAction(
            kind=a.kind,
            ref=a.ref,
            key=a.key,
            summary=a.summary,
            issue_type=a.issue_type,
            description=a.description,
            labels=list(a.labels),
            parent_ref=a.parent_ref,
            estimate_days=a.estimate_days,
            attachments=_attachments_for(a.key) if a.kind == STORY else list(a.attachments),
            op=a.op,
        )
        for a in plan.issues
    ]
    return PushPlan(
        parent_spec=plan.parent_spec,
        set_label=plan.set_label,
        issues=issues,
        links=list(plan.links),
    )


# --------------------------------------------------------------------------- #
# Reconcile a plan against what already exists in Jira
# --------------------------------------------------------------------------- #
def reconcile(
    plan: PushPlan,
    existing_labels: Iterable[str] = (),
    existing_links: Iterable[tuple[str, str]] = (),
    existing_attachments: Optional[dict[str, Iterable[str]]] = None,
) -> PushPlan:
    """Return a new `PushPlan` with each action's `op` set from what already exists.

    - `existing_labels`: identity labels the agent found in Jira (via
      `jira_search labels = "<ref>"`). Any issue whose `ref` is present becomes
      `reuse`; otherwise it stays `create`.
    - `existing_links`: `(outward_key, inward_key)` pairs already linked in Jira.
      Any matching link becomes `skip`; otherwise it stays `create`.
    - `existing_attachments`: `{story_key -> {filename, ...}}` of attachments already
      on each story issue. Any attachment whose filename is present becomes `skip`;
      otherwise it stays `create`. Omit to leave attachment ops untouched.

    Pure — does not mutate `plan`.
    """
    have_labels = set(existing_labels)
    have_links = {(str(o), str(i)) for o, i in existing_links}
    have_attach = {k: set(v) for k, v in (existing_attachments or {}).items()}

    def _attachments(a: IssueAction) -> list[AttachmentAction]:
        present = have_attach.get(a.key, set()) if existing_attachments is not None else set()
        return [
            AttachmentAction(
                filename=att.filename,
                source_path=att.source_path,
                op=SKIP if att.filename in present else CREATE,
            )
            for att in a.attachments
        ]

    issues = [
        IssueAction(
            kind=a.kind,
            ref=a.ref,
            key=a.key,
            summary=a.summary,
            issue_type=a.issue_type,
            description=a.description,
            labels=list(a.labels),
            parent_ref=a.parent_ref,
            estimate_days=a.estimate_days,
            attachments=_attachments(a),
            op=REUSE if a.ref in have_labels else CREATE,
        )
        for a in plan.issues
    ]
    links = [
        LinkAction(
            outward=l.outward,
            inward=l.inward,
            outward_ref=l.outward_ref,
            inward_ref=l.inward_ref,
            link_type=l.link_type,
            op=SKIP if (l.outward, l.inward) in have_links else CREATE,
        )
        for l in plan.links
    ]
    return PushPlan(
        parent_spec=plan.parent_spec,
        set_label=plan.set_label,
        issues=issues,
        links=links,
    )


# --------------------------------------------------------------------------- #
# Validate a plan's structure
# --------------------------------------------------------------------------- #
def validate_plan(plan: PushPlan) -> list[str]:
    """Return a list of structural problems. Empty means the plan is safe to execute.

    Checks: exactly one epic and it is first; identity refs unique across issues;
    every story's parent is the epic; every sub-task's parent is a story that appears
    earlier in the list; and every link endpoint is a known story key.
    """
    problems: list[str] = []

    epics = [a for a in plan.issues if a.kind == EPIC]
    if len(epics) != 1:
        problems.append(f"expected exactly 1 epic, found {len(epics)}")
    elif plan.issues[0].kind != EPIC:
        problems.append("epic must be the first action in the plan")
    epic_ref = epics[0].ref if epics else None

    seen_refs: set[str] = set()
    seen_before: set[str] = set()  # refs encountered so far (for parent-precedence)
    story_keys: set[str] = set()

    for a in plan.issues:
        if not a.ref:
            problems.append(f"{a.kind} '{a.key}': missing identity ref")
        elif a.ref in seen_refs:
            problems.append(f"{a.kind} '{a.key}': duplicate identity ref '{a.ref}'")
        seen_refs.add(a.ref)

        if a.kind == STORY:
            story_keys.add(a.key)
            if epic_ref is not None and a.parent_ref != epic_ref:
                problems.append(
                    f"story '{a.key}': parent_ref '{a.parent_ref}' != epic '{epic_ref}'"
                )
        elif a.kind == SUBTASK:
            if a.parent_ref not in seen_before:
                problems.append(
                    f"sub-task '{a.key}': parent '{a.parent_ref}' not created before it"
                )
        seen_before.add(a.ref)

    for l in plan.links:
        if l.outward not in story_keys:
            problems.append(f"link: outward '{l.outward}' is not a known story")
        if l.inward not in story_keys:
            problems.append(f"link: inward '{l.inward}' is not a known story")

    return problems


# --------------------------------------------------------------------------- #
# Summarise
# --------------------------------------------------------------------------- #
def summarize_plan(plan: PushPlan) -> str:
    """One-line human summary with per-op counts (before or after reconcile)."""

    def counts(actions, kind=None):
        c = {CREATE: 0, REUSE: 0, SKIP: 0}
        for a in actions:
            if kind is None or a.kind == kind:
                c[a.op] = c.get(a.op, 0) + 1
        return c

    n_epic = sum(1 for a in plan.issues if a.kind == EPIC)
    n_story = sum(1 for a in plan.issues if a.kind == STORY)
    n_sub = sum(1 for a in plan.issues if a.kind == SUBTASK)
    ic = counts(plan.issues)
    lc = counts(plan.links)
    atts = [att for a in plan.issues for att in a.attachments]
    base = (
        f"{plan.parent_spec}: {n_epic} epic, {n_story} stories, {n_sub} sub-tasks, "
        f"{len(plan.links)} links (set label '{plan.set_label}') — "
        f"issues: {ic[CREATE]} create / {ic[REUSE]} reuse; "
        f"links: {lc[CREATE]} create / {lc[SKIP]} skip."
    )
    if atts:
        n_create = sum(1 for x in atts if x.op == CREATE)
        n_skip = sum(1 for x in atts if x.op == SKIP)
        base += f" attachments: {n_create} upload / {n_skip} skip."
    return base


# --------------------------------------------------------------------------- #
# Adapter: load a real tree from disk via the sibling jira-tree engine
# --------------------------------------------------------------------------- #
def load_tree_view(tree_dir: str):
    """Load a Jira tree from disk and return a `(tree, problems)` pair.

    Reuses the sibling **jira-tree** engine (`load_tree` + `validate_tree`) so the
    tree format has a single source of truth. `problems` is the result of
    `validate_tree` — it must be empty before you build/execute a push plan.

    Requires the `jira-tree` skill bundle to sit alongside this one under
    `.kiro/skills/`. Raises `ImportError` with guidance if it cannot be found.
    """
    import importlib.util
    from pathlib import Path

    here = Path(__file__).resolve()
    tree_py = here.parents[2] / "jira-tree" / "engine" / "tree.py"
    if not tree_py.exists():
        raise ImportError(
            "jira-push needs the sibling 'jira-tree' skill to read a tree from disk; "
            f"expected engine at {tree_py}. Build/enrich the tree with jira-tree "
            "first, or pass an already-loaded tree to build_push_plan."
        )
    # Load tree.py by path under a unique module name to avoid clashing with this
    # bundle's own `engine` package.
    import sys

    spec = importlib.util.spec_from_file_location("jira_tree_engine_tree", tree_py)
    mod = importlib.util.module_from_spec(spec)
    # Register before exec so dataclass field resolution can see the module.
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]

    tree = mod.load_tree(tree_dir)
    return tree, mod.validate_tree(tree)
