"""
Render, parse and validate a *Jira tree*: a filesystem mirror of the Jira issue
hierarchy (Epic -> Stories -> Sub-tasks, plus cross-story "blocks" links) as
markdown files with YAML frontmatter.

Why this exists
---------------
`decomposition-to-jira` turns a decomposition into a deterministic `jira-plan.json`
and pushes it straight to Jira. That leaves no room to review or enrich the issue
*descriptions* before they land. The Jira tree is that missing middle step: a
human-readable, diff-able, git-friendly mirror you edit locally, then push once
happy. It sits between `jira-plan.json` and live Jira.

Layout produced/consumed
-------------------------
    <out>/epic.md                 Epic  (frontmatter + description body)
    <out>/_links.md               all "blocks" links (peer relationships)
    <out>/<US-xx>/story.md        Story (frontmatter + description body)
    <out>/<US-xx>/<US-xx-n>.md    Sub-task (frontmatter + description body)

The markdown **body** of each file *is* the Jira description. `load_tree` reads the
whole body verbatim, so any hand-editing of a description is preserved on the next
push. Frontmatter carries the structured Jira fields (issue type, summary, labels,
identity label, parent, requirements, links, ...).

Contracts
---------
- **Round-trip:** `load_tree(dir)` after `write_tree(tree, dir)` reproduces an equal
  `Tree` (model-level equality, not byte-identity).
- **Idempotency labels:** identity labels are copied straight through from the plan
  (`s2s-<parent>-US-01-1` etc.), so a downstream push dedupes exactly like
  `decomposition-to-jira`.
- **Non-destructive render:** `write_tree(..., overwrite=False)` (the default) skips
  files that already exist, so regenerating never clobbers hand-edited descriptions.

This module makes no Jira calls; the agent does that using the parsed tree.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml

LABEL_PREFIX = "s2s"
BLOCKS_LINK_TYPE = "Blocks"

EPIC_FILE = "epic.md"
LINKS_FILE = "_links.md"
STORY_FILE = "story.md"

# Marker left in seeded bodies where a human or sub-agent must enrich the content
# (acceptance criteria, suggested code, background, ...). `find_placeholders` reports
# any that survive, so a tree can be checked "fully enriched" before a push.
PLACEHOLDER_MARKER = "TODO"


# --------------------------------------------------------------------------- #
# Models
# --------------------------------------------------------------------------- #
@dataclass
class Subtask:
    key: str
    summary: str
    identity_label: str
    labels: list[str] = field(default_factory=list)
    requirements: list[str] = field(default_factory=list)
    optional: bool = False
    parent: str = ""
    issue_type: str = "Sub-task"
    description: str = ""


@dataclass
class Story:
    key: str
    summary: str
    identity_label: str
    parent_epic: str
    labels: list[str] = field(default_factory=list)
    covers_requirements: list[str] = field(default_factory=list)
    estimate_days: Optional[float] = None
    wave: Optional[int] = None
    depends_on: list[str] = field(default_factory=list)
    blocks: list[str] = field(default_factory=list)
    issue_type: str = "Story"
    description: str = ""
    subtasks: list[Subtask] = field(default_factory=list)


@dataclass
class Epic:
    summary: str
    epic_name: str
    identity_label: str
    set_label: str
    labels: list[str] = field(default_factory=list)
    issue_type: str = "Epic"
    description: str = ""


@dataclass
class Link:
    link_type: str
    outward: str  # ships first / blocks
    inward: str  # blocked


@dataclass
class Tree:
    parent_spec: str
    set_label: str
    epic: Epic
    stories: list[Story] = field(default_factory=list)
    links: list[Link] = field(default_factory=list)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def sanitize_label(text: str) -> str:
    """Jira labels may not contain spaces. Collapse anything that is not a letter,
    digit, dot, underscore or hyphen into a single hyphen."""
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", str(text).strip())
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-")
    return cleaned


def _as_str_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [str(v) for v in value]
    return [str(value)]


def split_frontmatter(text: str) -> tuple[dict, str]:
    """Split a markdown file into (frontmatter_dict, body). Frontmatter is the YAML
    block delimited by lines that are exactly `---`. If absent, returns ({}, text)."""
    if not text.startswith("---"):
        return {}, text.strip("\n")
    lines = text.splitlines()
    # first line is the opening fence; find the closing fence
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            fm_text = "\n".join(lines[1:i])
            body = "\n".join(lines[i + 1 :])
            data = yaml.safe_load(fm_text) or {}
            if not isinstance(data, dict):
                data = {}
            return data, body.strip("\n")
    # no closing fence: treat whole thing as body
    return {}, text.strip("\n")


def _dump_frontmatter(ordered: dict) -> str:
    """Dump an ordered dict as a YAML frontmatter block (keys in insertion order)."""
    body = yaml.safe_dump(ordered, sort_keys=False, allow_unicode=True, width=1000)
    return f"---\n{body}---\n"


def _compose(frontmatter: dict, description: str) -> str:
    return f"{_dump_frontmatter(frontmatter)}\n{description.strip(chr(10))}\n"


# --------------------------------------------------------------------------- #
# Build a Tree from a jira-plan.json (dict) -- the seed step
# --------------------------------------------------------------------------- #
def load_plan(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _user_story_line(story: dict) -> str:
    """Pull the 'As a ... so that ...' line out of the plan's story description
    (its first paragraph), falling back to the summary."""
    desc = str(story.get("description", "")).strip()
    if desc:
        first = desc.split("\n\n", 1)[0].strip()
        if first:
            return first
    return str(story.get("summary", story.get("sid", ""))).strip()


def _seed_epic_body(parent: str, stories: list[dict], waves: list[list[str]]) -> str:
    """Seed a scannable Epic body: goal/background/scope placeholders plus a
    delivery-plan table and story index built from the plan (which we have in full)."""
    summary_of = {str(s.get("sid")): str(s.get("summary", s.get("sid"))) for s in stories}
    est_of = {str(s.get("sid")): s.get("estimate_days") for s in stories}

    lines = [
        "## Goal",
        "",
        f"<{PLACEHOLDER_MARKER}: one or two sentences — the capability this delivers and who benefits.>",
        "",
        "## Background",
        "",
        f"Decomposed from spec `{parent}` by spec-to-stories. "
        f"<{PLACEHOLDER_MARKER}: why now — the problem or opportunity.>",
        "",
        "## Scope",
        "",
        "- In scope: the stories and waves below.",
        f"- Out of scope: <{PLACEHOLDER_MARKER}: what this epic explicitly does not cover.>",
        "",
        "## Delivery plan",
        "",
        "| Wave | Stories |",
        "|------|---------|",
    ]
    for idx, wave_stories in enumerate(waves, start=1):
        lines.append(f"| {idx} | {', '.join(str(s) for s in wave_stories)} |")
    if not waves:
        lines.append("| 1 | (no waves recorded) |")

    lines += ["", "## Stories", "", "| Story | Summary | Est (days) |", "|-------|---------|------------|"]
    total = 0.0
    reqs: set[str] = set()
    for s in stories:
        sid = str(s.get("sid"))
        est = est_of.get(sid)
        if isinstance(est, (int, float)):
            total += float(est)
        for r in _as_str_list(s.get("covers_requirements")):
            reqs.add(r)
        lines.append(f"| {sid} | {summary_of.get(sid, sid)} | {est if est is not None else '—'} |")

    req_list = ", ".join(sorted(reqs, key=lambda x: (len(x), x))) if reqs else "—"
    lines += [
        "",
        f"_Total estimate: {total:g} days (excludes optional test sub-tasks)._",
        "",
        "## Definition of done",
        "",
        f"- All {len(stories)} stories delivered.",
        f"- Parent requirements covered: {req_list}.",
    ]
    return "\n".join(lines).strip()


def _seed_story_body(story: dict, summary_of: dict[str, str], depends: list[str]) -> str:
    """Seed a Story body following the house template: user story, description,
    delivers, Given/When/Then acceptance criteria, dependencies, traceability.
    `depends` is the list of upstream story ids (resolved to names via summary_of)."""
    sid = str(story.get("sid"))
    covers = _as_str_list(story.get("covers_requirements"))
    identity = str(story.get("identity_label", sanitize_label(f"{LABEL_PREFIX}-{sid}")))

    if depends:
        dep_lines = [f"- {d} — {summary_of.get(d, d)}" for d in depends]
    else:
        dep_lines = ["- None — foundation story."]

    lines = [
        _user_story_line(story),
        "",
        "## Description",
        "",
        f"<{PLACEHOLDER_MARKER}: short prose — what this story does and where it fits.>",
        "",
        "## Delivers",
        "",
        f"- <{PLACEHOLDER_MARKER}: the components/exports this story produces.>",
        "",
        "## Acceptance criteria",
        "",
        f"- **Given** <context>, **when** <action>, **then** <expected outcome>. "
        f"<{PLACEHOLDER_MARKER}: replace with real criteria.>",
        "",
        "## Dependencies",
        "",
        *dep_lines,
        "",
        "## Traceability",
        "",
        f"Covers parent requirements: {', '.join(covers) if covers else '—'} · `{identity}`",
    ]
    return "\n".join(lines).strip()


def _seed_subtask_body(sub: dict) -> str:
    """Seed a greppable, code-forward Sub-task body: What/Why/Done-when bullets and a
    Suggested-approach code fence for the developer to run with."""
    summary = str(sub.get("summary", sub.get("tid", ""))).strip()
    reqs = _as_str_list(sub.get("requirements"))
    optional = bool(sub.get("optional", False))

    lines = [
        f"- **What:** {summary}",
        f"- **Why:** <{PLACEHOLDER_MARKER}: where it fits / what it unblocks>",
        "- **Done when:**",
        f"  - <{PLACEHOLDER_MARKER}: checkable outcome>",
        "",
        "### Suggested approach",
        "",
        "```text",
        f"// {PLACEHOLDER_MARKER}: suggestive starting point — replace with real implementation",
        "```",
    ]
    if optional:
        lines += ["", "_Optional — can be deferred for a faster MVP._"]
    lines += ["", f"_Requirements: {', '.join(reqs) if reqs else '—'}_"]
    return "\n".join(lines).strip()


def build_tree_from_plan(plan: dict) -> Tree:
    """Turn a parsed `jira-plan.json` into a `Tree`, seeding descriptions from the
    plan. Deterministic and pure. `depends_on`/`blocks`/`wave` are derived from the
    plan's links and waves so each story frontmatter is self-describing."""
    parent = str(plan.get("parent_spec"))
    set_label = str(plan.get("set_label") or sanitize_label(f"{LABEL_PREFIX}-{parent}"))

    plan_stories = plan.get("stories", []) or []
    summary_of = {str(s.get("sid")): str(s.get("summary", s.get("sid"))) for s in plan_stories}
    waves = [[str(s) for s in w] for w in (plan.get("waves", []) or [])]

    ep = plan.get("epic", {}) or {}
    epic = Epic(
        summary=str(ep.get("summary", f"{parent} (delivery)")),
        epic_name=str(ep.get("epic_name", parent)),
        identity_label=str(ep.get("identity_label", sanitize_label(f"{LABEL_PREFIX}-{parent}-epic"))),
        set_label=set_label,
        labels=_as_str_list(ep.get("labels")),
        description=_seed_epic_body(parent, plan_stories, waves),
    )

    # link-derived maps
    links = [
        Link(
            link_type=str(l.get("link_type", BLOCKS_LINK_TYPE)),
            outward=str(l.get("outward")),
            inward=str(l.get("inward")),
        )
        for l in plan.get("links", []) or []
    ]
    blocks_map: dict[str, list[str]] = {}
    depends_map: dict[str, list[str]] = {}
    for l in links:
        blocks_map.setdefault(l.outward, []).append(l.inward)
        depends_map.setdefault(l.inward, []).append(l.outward)

    # wave lookup
    wave_of: dict[str, int] = {}
    for idx, wave_stories in enumerate(waves, start=1):
        for sid in wave_stories:
            wave_of[str(sid)] = idx

    stories: list[Story] = []
    for s in plan_stories:
        sid = str(s.get("sid"))
        subtasks = [
            Subtask(
                key=str(t.get("tid")),
                summary=str(t.get("summary", t.get("tid"))),
                identity_label=str(t.get("identity_label")),
                labels=_as_str_list(t.get("labels")),
                requirements=_as_str_list(t.get("requirements")),
                optional=bool(t.get("optional", False)),
                parent=sid,
                description=_seed_subtask_body(t),
            )
            for t in s.get("subtasks", []) or []
        ]
        depends = sorted(depends_map.get(sid, []))
        stories.append(
            Story(
                key=sid,
                summary=str(s.get("summary", sid)),
                identity_label=str(s.get("identity_label")),
                parent_epic=epic.epic_name,
                labels=_as_str_list(s.get("labels")),
                covers_requirements=_as_str_list(s.get("covers_requirements")),
                estimate_days=s.get("estimate_days"),
                wave=wave_of.get(sid),
                depends_on=depends,
                blocks=sorted(blocks_map.get(sid, [])),
                description=_seed_story_body(s, summary_of, depends),
                subtasks=subtasks,
            )
        )

    return Tree(parent_spec=parent, set_label=set_label, epic=epic, stories=stories, links=links)


# --------------------------------------------------------------------------- #
# Render a Tree to disk
# --------------------------------------------------------------------------- #
def _epic_frontmatter(epic: Epic) -> dict:
    return {
        "issue_type": epic.issue_type,
        "summary": epic.summary,
        "epic_name": epic.epic_name,
        "identity_label": epic.identity_label,
        "set_label": epic.set_label,
        "labels": list(epic.labels),
    }


def _story_frontmatter(story: Story) -> dict:
    fm: dict[str, Any] = {
        "issue_type": story.issue_type,
        "key": story.key,
        "summary": story.summary,
        "parent_epic": story.parent_epic,
        "identity_label": story.identity_label,
        "labels": list(story.labels),
    }
    if story.estimate_days is not None:
        fm["estimate_days"] = story.estimate_days
    fm["covers_requirements"] = list(story.covers_requirements)
    if story.wave is not None:
        fm["wave"] = story.wave
    fm["depends_on"] = list(story.depends_on)
    fm["blocks"] = list(story.blocks)
    return fm


def _subtask_frontmatter(sub: Subtask) -> dict:
    return {
        "issue_type": sub.issue_type,
        "key": sub.key,
        "summary": sub.summary,
        "parent": sub.parent,
        "identity_label": sub.identity_label,
        "labels": list(sub.labels),
        "requirements": list(sub.requirements),
        "optional": sub.optional,
    }


def _links_document(tree: Tree) -> str:
    fm = {
        "link_type": BLOCKS_LINK_TYPE,
        "links": [{"outward": l.outward, "inward": l.inward} for l in tree.links],
    }
    body = (
        "# Cross-story dependency links (Blocks)\n\n"
        "`outward` **blocks** `inward` — the outward story must ship first. "
        "Mirrors the `blocks:` list in each story's frontmatter."
    )
    return _compose(fm, body)


def write_tree(tree: Tree, out_dir: str | Path, overwrite: bool = False) -> list[str]:
    """Render the tree under `out_dir`. Returns the list of paths written. With
    `overwrite=False` (default) existing files are skipped so hand-edited
    descriptions are never clobbered."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    written: list[str] = []

    def _write(path: Path, content: str) -> None:
        if path.exists() and not overwrite:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        written.append(str(path))

    _write(out / EPIC_FILE, _compose(_epic_frontmatter(tree.epic), tree.epic.description))
    for story in tree.stories:
        sdir = out / story.key
        _write(sdir / STORY_FILE, _compose(_story_frontmatter(story), story.description))
        for sub in story.subtasks:
            _write(sdir / f"{sub.key}.md", _compose(_subtask_frontmatter(sub), sub.description))
    _write(out / LINKS_FILE, _links_document(tree))
    return written


# --------------------------------------------------------------------------- #
# Parse a Tree from disk
# --------------------------------------------------------------------------- #
def load_tree(in_dir: str | Path) -> Tree:
    """Parse a Jira tree back into a `Tree`. The description of each issue is the
    markdown body verbatim (so hand edits are preserved)."""
    root = Path(in_dir)
    epic_fm, epic_body = split_frontmatter((root / EPIC_FILE).read_text(encoding="utf-8"))
    set_label = str(epic_fm.get("set_label", ""))
    parent_spec = str(epic_fm.get("epic_name", ""))
    epic = Epic(
        summary=str(epic_fm.get("summary", "")),
        epic_name=parent_spec,
        identity_label=str(epic_fm.get("identity_label", "")),
        set_label=set_label,
        labels=_as_str_list(epic_fm.get("labels")),
        issue_type=str(epic_fm.get("issue_type", "Epic")),
        description=epic_body,
    )

    stories: list[Story] = []
    story_dirs = sorted(p for p in root.iterdir() if p.is_dir())
    for sdir in story_dirs:
        story_path = sdir / STORY_FILE
        if not story_path.exists():
            continue
        fm, body = split_frontmatter(story_path.read_text(encoding="utf-8"))
        subtasks: list[Subtask] = []
        sub_files = sorted(p for p in sdir.iterdir() if p.is_file() and p.name != STORY_FILE and p.suffix == ".md")
        for spath in sub_files:
            sfm, sbody = split_frontmatter(spath.read_text(encoding="utf-8"))
            subtasks.append(
                Subtask(
                    key=str(sfm.get("key", spath.stem)),
                    summary=str(sfm.get("summary", "")),
                    identity_label=str(sfm.get("identity_label", "")),
                    labels=_as_str_list(sfm.get("labels")),
                    requirements=_as_str_list(sfm.get("requirements")),
                    optional=bool(sfm.get("optional", False)),
                    parent=str(sfm.get("parent", sdir.name)),
                    issue_type=str(sfm.get("issue_type", "Sub-task")),
                    description=sbody,
                )
            )
        stories.append(
            Story(
                key=str(fm.get("key", sdir.name)),
                summary=str(fm.get("summary", "")),
                identity_label=str(fm.get("identity_label", "")),
                parent_epic=str(fm.get("parent_epic", parent_spec)),
                labels=_as_str_list(fm.get("labels")),
                covers_requirements=_as_str_list(fm.get("covers_requirements")),
                estimate_days=fm.get("estimate_days"),
                wave=fm.get("wave"),
                depends_on=_as_str_list(fm.get("depends_on")),
                blocks=_as_str_list(fm.get("blocks")),
                issue_type=str(fm.get("issue_type", "Story")),
                description=body,
                subtasks=subtasks,
            )
        )

    links: list[Link] = []
    links_path = root / LINKS_FILE
    if links_path.exists():
        lfm, _ = split_frontmatter(links_path.read_text(encoding="utf-8"))
        for l in lfm.get("links", []) or []:
            links.append(
                Link(
                    link_type=str(lfm.get("link_type", BLOCKS_LINK_TYPE)),
                    outward=str(l.get("outward")),
                    inward=str(l.get("inward")),
                )
            )

    return Tree(parent_spec=parent_spec, set_label=set_label, epic=epic, stories=stories, links=links)


# --------------------------------------------------------------------------- #
# Validate a Tree
# --------------------------------------------------------------------------- #
def validate_tree(tree: Tree) -> list[str]:
    """Return a list of human-readable problems. An empty list means the tree is
    internally consistent and safe to push."""
    problems: list[str] = []
    story_keys = {s.key for s in tree.stories}

    # identity labels: present, valid, unique
    seen: dict[str, str] = {}

    def _check_label(label: str, owner: str) -> None:
        if not label:
            problems.append(f"{owner}: missing identity_label")
            return
        if sanitize_label(label) != label:
            problems.append(f"{owner}: identity_label '{label}' is not a valid Jira label token")
        if label in seen:
            problems.append(f"{owner}: identity_label '{label}' duplicates {seen[label]}")
        else:
            seen[label] = owner

    _check_label(tree.epic.identity_label, "epic")
    for s in tree.stories:
        _check_label(s.identity_label, f"story {s.key}")
        if s.parent_epic != tree.epic.epic_name:
            problems.append(
                f"story {s.key}: parent_epic '{s.parent_epic}' != epic '{tree.epic.epic_name}'"
            )
        for b in s.blocks:
            if b not in story_keys:
                problems.append(f"story {s.key}: blocks unknown story '{b}'")
        for d in s.depends_on:
            if d not in story_keys:
                problems.append(f"story {s.key}: depends_on unknown story '{d}'")
        for t in s.subtasks:
            _check_label(t.identity_label, f"sub-task {t.key}")
            if t.parent != s.key:
                problems.append(f"sub-task {t.key}: parent '{t.parent}' != story '{s.key}'")
            has_opt_label = "optional" in t.labels
            if has_opt_label != t.optional:
                problems.append(
                    f"sub-task {t.key}: optional flag ({t.optional}) disagrees with 'optional' label"
                )

    # links resolve to known stories
    for l in tree.links:
        if l.outward not in story_keys:
            problems.append(f"link: outward '{l.outward}' is not a known story")
        if l.inward not in story_keys:
            problems.append(f"link: inward '{l.inward}' is not a known story")

    # _links.md and per-story blocks: frontmatter must agree
    link_pairs = {(l.outward, l.inward) for l in tree.links}
    block_pairs = {(s.key, b) for s in tree.stories for b in s.blocks}
    only_links = link_pairs - block_pairs
    only_blocks = block_pairs - link_pairs
    for o, i in sorted(only_links):
        problems.append(f"link {o}->{i} present in _links.md but missing from story {o} 'blocks:'")
    for o, i in sorted(only_blocks):
        problems.append(f"link {o}->{i} present in story {o} 'blocks:' but missing from _links.md")

    return problems


def summarize(tree: Tree) -> str:
    n_sub = sum(len(s.subtasks) for s in tree.stories)
    return (
        f"{tree.parent_spec}: 1 epic, {len(tree.stories)} stories, {n_sub} sub-tasks, "
        f"{len(tree.links)} blocks-links (set label '{tree.set_label}')."
    )


def find_placeholders(tree: Tree) -> list[str]:
    """Return the owners (epic / story key / sub-task key) whose description still
    contains a `PLACEHOLDER_MARKER` — i.e. seeded content not yet enriched. This is a
    soft, pre-push check: a non-empty result means "still has TODOs", not "invalid"."""
    owners: list[str] = []
    if PLACEHOLDER_MARKER in tree.epic.description:
        owners.append("epic")
    for s in tree.stories:
        if PLACEHOLDER_MARKER in s.description:
            owners.append(f"story {s.key}")
        for t in s.subtasks:
            if PLACEHOLDER_MARKER in t.description:
                owners.append(f"sub-task {t.key}")
    return owners
