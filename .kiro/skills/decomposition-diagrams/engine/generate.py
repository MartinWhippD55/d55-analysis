"""Generate the full set of ``.mmd`` sources for a decomposition.

Ties :mod:`engine.graph`, :mod:`engine.keymap` and :mod:`engine.mermaid` together:
reads ``graph.yaml`` (+ the optional ``jira-tree/_placeholders.md`` key map and story
summaries) and writes ``diagrams/epic-service-interaction.mmd`` and one
``diagrams/<US-xx>.mmd`` per story. The per-story files are ready to render; the epic
file is a labelled overview the agent should refine into the runtime flow.

CLI:
    python -m engine.generate <decomposition_dir> [--out <dir>]

``<decomposition_dir>`` is ``.kiro/specs/<parent>/decomposition`` — it must contain
``graph.yaml`` and (ideally) ``jira-tree/``.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

import yaml

from .graph import load_graph, Graph
from .keymap import load_key_map
from . import mermaid


def _story_summaries(jira_tree_dir: Path) -> dict[str, str]:
    """Read ``summary`` from each ``<US-xx>/story.md`` front-matter, if present."""
    out: dict[str, str] = {}
    if not jira_tree_dir.exists():
        return out
    for story_md in sorted(jira_tree_dir.glob("US-*/story.md")):
        text = story_md.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        end = text.find("\n---", 3)
        if end == -1:
            continue
        fm = yaml.safe_load(text[3:end]) or {}
        key = fm.get("key")
        summary = fm.get("summary")
        if key and summary:
            out[str(key)] = str(summary)
    return out


def generate_all(decomposition_dir: str | Path, out_dir: Optional[str | Path] = None) -> list[str]:
    """Write all ``.mmd`` sources. Returns the list of files written (names)."""
    decomp = Path(decomposition_dir)
    graph = load_graph(decomp / "graph.yaml")
    jira_tree = decomp / "jira-tree"
    key_map = load_key_map(jira_tree / "_placeholders.md") if (jira_tree / "_placeholders.md").exists() else {}
    summaries = _story_summaries(jira_tree)

    out = Path(out_dir) if out_dir else (decomp / "diagrams")
    out.mkdir(parents=True, exist_ok=True)

    written: list[str] = []

    epic_key = key_map.get(graph.parent_spec)
    epic_mmd = mermaid.build_epic_overview(graph, epic_key=epic_key, key_map=key_map, summaries=summaries)
    (out / "epic-service-interaction.mmd").write_text(epic_mmd, encoding="utf-8")
    written.append("epic-service-interaction.mmd")

    for story in graph.stories:
        mmd = mermaid.build_story_diagram(graph, story, key_map=key_map, summaries=summaries)
        (out / f"{story}.mmd").write_text(mmd, encoding="utf-8")
        written.append(f"{story}.mmd")

    return written


def _main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="generate", description=__doc__)
    parser.add_argument("decomposition_dir", help=".kiro/specs/<parent>/decomposition")
    parser.add_argument("--out", help="output dir (default: <decomposition_dir>/diagrams)")
    args = parser.parse_args(argv)
    written = generate_all(args.decomposition_dir, args.out)
    for name in written:
        print(f"wrote {name}")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
