"""Generate baseline mermaid diagrams from a :class:`~engine.graph.Graph`.

What is deterministic vs. what the agent refines
------------------------------------------------
Per-story "what it builds / where it's used" diagrams *can* be derived mechanically:
the nodes are the components the story delivers, arrows out go to the stories that
consume it (reverse edges), arrows in come from the foundation stories it depends on.
This module produces that solid **baseline**.

The **epic service-interaction** diagram is different: the runtime flow
(render -> send -> sign -> webhook -> store) is *not* encoded in ``graph.yaml`` (whose
edges are build-time dependencies, not runtime calls). So the epic generator emits a
faithful **component-by-story overview** plus a clearly marked TODO banner; the agent
is expected to rewrite it into the real runtime flow (see SKILL.md for the worked
example). Both outputs are valid mermaid and safe to render immediately.
"""
from __future__ import annotations

import re
from typing import Optional

from .graph import Graph

_LAYOUTS = ("center",)


def _slug(text: str) -> str:
    """A mermaid-safe node id derived from an arbitrary token."""
    return re.sub(r"[^0-9A-Za-z]+", "_", text).strip("_")


def _story_label(story: str, key_map: dict[str, str], summaries: Optional[dict[str, str]]) -> str:
    key = key_map.get(story)
    head = f"{story} / {key}" if key else story
    summ = (summaries or {}).get(story)
    return f"{head}<br/>{summ}" if summ else head


def _via_label(via: tuple[str, ...]) -> str:
    return ", ".join(via)


def build_story_diagram(
    graph: Graph,
    story: str,
    key_map: Optional[dict[str, str]] = None,
    summaries: Optional[dict[str, str]] = None,
) -> str:
    """Return a baseline ``flowchart LR`` for one story.

    Shows the components the story delivers (in a ``builds`` subgraph), the foundation
    stories it depends on feeding in, and the stories that consume it fanning out —
    every arrow labelled with the ``via`` components from ``graph.yaml``.
    """
    key_map = key_map or {}
    delivered = graph.delivers(story)
    deps = graph.depends_on(story)
    cons = graph.consumers(story)

    lines: list[str] = []
    lines.append(f"%% {story}{(' / ' + key_map[story]) if story in key_map else ''}"
                 " — what it builds and where it's used (baseline from graph.yaml).")
    lines.append("flowchart LR")

    # builds subgraph
    title = _story_label(story, key_map, summaries) + " builds"
    lines.append(f'  subgraph BUILDS["{title}"]')
    lines.append("    direction TB")
    if delivered:
        for comp in delivered:
            lines.append(f'    {_slug(comp)}["{comp}"]')
    else:
        lines.append('    _none["(no delivered components in graph.yaml)"]')
    lines.append("  end")

    # upstream dependencies feed into the builds subgraph
    for e in sorted(deps, key=lambda x: x.to):
        nid = _slug(e.to)
        lines.append(f'  {nid}["{_story_label(e.to, key_map, summaries)}"]')
        label = _via_label(e.via)
        arrow = f'  {nid} -->|"{label}"| BUILDS' if label else f"  {nid} --> BUILDS"
        lines.append(arrow)

    # consumers fan out from the builds subgraph
    for e in sorted(cons, key=lambda x: x.frm):
        nid = _slug(e.frm)
        lines.append(f'  {nid}["{_story_label(e.frm, key_map, summaries)}"]')
        label = _via_label(e.via)
        arrow = f'  BUILDS -->|"{label}"| {nid}' if label else f"  BUILDS --> {nid}"
        lines.append(arrow)

    return "\n".join(lines) + "\n"


def build_epic_overview(
    graph: Graph,
    epic_key: Optional[str] = None,
    key_map: Optional[dict[str, str]] = None,
    summaries: Optional[dict[str, str]] = None,
) -> str:
    """Return a baseline epic diagram: components grouped by delivering story, with the
    build-dependency edges between stories.

    This is an *overview*, not the runtime service-interaction flow — the banner and
    SKILL.md tell the agent to replace it with the real end-to-end flow.
    """
    key_map = key_map or {}
    lines: list[str] = []
    head = f"Epic{(' ' + epic_key) if epic_key else ''}"
    lines.append(f"%% {head} — component/story OVERVIEW auto-generated from graph.yaml.")
    lines.append("%% TODO(agent): replace with the runtime service-interaction flow"
                 " (render -> send -> sign -> webhook -> store), annotating each")
    lines.append("%% participant with its delivering story (US-xx / key). See SKILL.md.")
    lines.append("flowchart LR")

    for story in graph.stories:
        comps = graph.delivers(story)
        title = _story_label(story, key_map, summaries)
        lines.append(f'  subgraph {_slug(story)}["{title}"]')
        lines.append("    direction TB")
        if comps:
            for comp in comps:
                lines.append(f'    {_slug(story + "_" + comp)}["{comp}"]')
        else:
            lines.append(f'    {_slug(story + "_none")}["(no components)"]')
        lines.append("  end")

    for e in graph.edges:
        label = _via_label(e.via)
        src, dst = _slug(e.frm), _slug(e.to)
        lines.append(f'  {src} -->|"{label}"| {dst}' if label else f"  {src} --> {dst}")

    return "\n".join(lines) + "\n"
