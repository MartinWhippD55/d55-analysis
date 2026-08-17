"""Load and model a decomposition ``graph.yaml``.

``graph.yaml`` (produced by spec-to-stories) is the single source of truth for what
each story delivers and how the stories depend on one another:

- ``components``: ``{"<kind>:<name>": "US-xx"}`` — which story delivers each component.
- ``edges``: ``[{from: US-a, to: US-b, via: [components]}]`` where **``from`` depends
  on ``to``** (US-a is built on US-b, using the ``via`` components). So "where is
  US-b used?" is the *reverse*: every edge whose ``to == US-b``.
- ``waves``: delivery ordering (informational here).

This module is pure: it parses the file into a small model and answers the three
questions the diagram generator needs — what a story *builds*, what it *depends on*,
and who *consumes* it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


@dataclass(frozen=True)
class Edge:
    """A dependency edge: ``frm`` depends on ``to`` via ``via`` components."""

    frm: str
    to: str
    via: tuple[str, ...] = ()


@dataclass
class Graph:
    parent_spec: str
    stories: list[str]
    components: dict[str, str]  # "<kind>:<name>" -> story
    edges: list[Edge] = field(default_factory=list)

    # -- queries used by the diagram generator ----------------------------- #
    def delivers(self, story: str) -> list[str]:
        """Components delivered by ``story`` (in stable, sorted order)."""
        return sorted(c for c, owner in self.components.items() if owner == story)

    def depends_on(self, story: str) -> list[Edge]:
        """Edges where ``story`` depends on another story (``frm == story``)."""
        return [e for e in self.edges if e.frm == story]

    def consumers(self, story: str) -> list[Edge]:
        """Edges where another story consumes ``story`` (``to == story``).

        This is the reverse of ``depends_on`` and answers "where is this used?".
        """
        return [e for e in self.edges if e.to == story]


def load_graph(path: str | Path) -> Graph:
    """Parse a ``graph.yaml`` file into a :class:`Graph`."""
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return graph_from_dict(data)


def graph_from_dict(data: dict) -> Graph:
    """Build a :class:`Graph` from an already-parsed mapping (pure; testable)."""
    edges = [
        Edge(frm=e["from"], to=e["to"], via=tuple(e.get("via", []) or []))
        for e in (data.get("edges") or [])
    ]
    return Graph(
        parent_spec=data.get("parentSpec", ""),
        stories=list(data.get("stories") or []),
        components=dict(data.get("components") or {}),
        edges=edges,
    )
