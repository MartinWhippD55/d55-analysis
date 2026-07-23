"""
Write the mechanical decomposition artifacts to disk.

Given the parent spec name, a list of Stories and the parent requirement ids,
this builds the dependency graph and writes:

  <out>/graph.yaml                    the component registry, edges, waves, issues
  <out>/jira-import.csv               Jira CSV importer file (epic/stories/sub-tasks)
  <out>/jira-import.json              same, as JSON (for the REST API)
  <out>/README.md                     human summary: wave plan + a mermaid graph
  <out>/stories/<id>/manifest.yaml    per-story machine manifest

The per-story requirements.md / design.md / tasks.md are authored by the skill
(the agent) from the parent spec using the templates; this module does not write
them, but it creates the story folders so those files have a home.

Returns the Decomposition so callers can inspect `.ok` / `.issues`.
"""
from __future__ import annotations

from pathlib import Path

from . import jira_export
from .graph import build_decomposition
from .manifest import write_graph, write_story_manifest
from .models import Decomposition, Story


def _mermaid(dec: Decomposition) -> str:
    lines = ["```mermaid", "graph TD"]
    for s in dec.stories:
        label = s.title.replace('"', "'")
        lines.append(f'    {_node(s.id)}["{s.id}: {label}"]')
    for e in dec.edges:
        # dst must be built before src: draw dst --> src
        lines.append(f"    {_node(e.dst)} --> {_node(e.src)}")
    lines.append("```")
    return "\n".join(lines)


def _node(sid: str) -> str:
    return sid.replace("-", "_").replace(".", "_")


def _readme(dec: Decomposition) -> str:
    out: list[str] = []
    out.append(f"# Decomposition: {dec.parent_spec}\n")
    out.append(
        "This folder decomposes the parent spec into independently deliverable user "
        "stories. Each `stories/<id>/` folder is a self-contained Kiro spec a developer "
        "can copy into their own `.kiro/specs/`. `graph.yaml` holds the machine-readable "
        "dependency graph; `jira-import.csv` is ready for Jira's CSV importer.\n"
    )
    status = "OK - no blocking issues" if dec.ok else "BLOCKED - see issues below"
    out.append(f"**Status:** {status}\n")

    out.append("## Implementation waves\n")
    out.append(
        "Stories in the same wave have no dependency on each other and can be built in "
        "parallel. Each wave depends only on earlier waves.\n"
    )
    for i, wave in enumerate(dec.waves, start=1):
        names = ", ".join(wave)
        out.append(f"- **Wave {i}:** {names}")
    out.append("")

    out.append("## Dependency graph\n")
    out.append(_mermaid(dec))
    out.append("")

    if dec.issues:
        out.append("## Issues\n")
        for iss in dec.issues:
            out.append(f"- **{iss.kind}**: {iss.detail}")
        out.append("")

    out.append("## Stories\n")
    out.append("| Story | Title | Exports | Depends on | Requirements |")
    out.append("|-------|-------|---------|-----------|--------------|")
    for s in dec.stories:
        exp = "<br>".join(c.ref for c in s.exports) or "-"
        dep = "<br>".join(c.ref for c in s.depends_on) or "-"
        reqs = ", ".join(s.covers_requirements) or "-"
        out.append(f"| {s.id} | {s.title} | {exp} | {dep} | {reqs} |")
    out.append("")
    return "\n".join(out)


def build_outputs(
    parent_spec: str,
    stories: list[Story],
    out_dir: str | Path,
    all_requirement_ids: list[str] | None = None,
) -> Decomposition:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    dec = build_decomposition(parent_spec, stories, all_requirement_ids=all_requirement_ids)

    write_graph(dec, out / "graph.yaml")
    jira_export.write_csv(dec, str(out / "jira-import.csv"))
    jira_export.write_json(dec, str(out / "jira-import.json"))
    (out / "README.md").write_text(_readme(dec), encoding="utf-8")

    for story in stories:
        write_story_manifest(story, out / "stories" / story.id / "manifest.yaml")

    return dec
