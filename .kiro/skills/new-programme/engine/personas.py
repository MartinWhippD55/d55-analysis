"""Persona metadata, rubric loading, and the critic invocation contract.

The six critique personas are defined as vendored rubric files under
``personas/`` (loaded via the bundle path helper). This module exposes their
metadata, loads a rubric, and defines the structured input/output contract the
orchestrator uses when invoking a critic sub-agent.

Invocation contract (per critic sub-agent):

- **Input** (:class:`CriticInput`): the persona id, the persona rubric text, the
  artefact file(s) to read, the programme context, the phase, and the scoring
  guidance (score addressable-in-document quality only; park anything needing a
  person or a decision).
- **Output**: a :class:`~engine.models.CritiqueResult` — a 1..5 score plus a list
  of :class:`~engine.models.Finding` items each tagged addressable/parked with a
  severity, an issue, and a concrete suggestion. The orchestrator feeds the
  per-iteration results to :func:`engine.critique.aggregate`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from . import paths
from .models import Persona

# Persona display metadata (design "critique panel" table).
PERSONA_META: dict[Persona, dict[str, str]] = {
    "d55_ceo": {
        "name": "Jonathan — D55 CEO",
        "lens": "Internal / commercial",
        "cares": "Strategic fit, brand, margin; is this a sellable programme, not a list of workshops",
    },
    "d55_cto": {
        "name": "Rhys — D55 CTO",
        "lens": "Internal / delivery",
        "cares": "Technical credibility, can a consultant actually run this, delivery risk",
    },
    "d55_marketing": {
        "name": "Marketing",
        "lens": "Internal / GTM",
        "cares": "Elevator pitch, funnel, the free-assessment hook, differentiation",
    },
    "client_csuite": {
        "name": "Client C-Suite",
        "lens": "External / buyer",
        "cares": "ROI, risk, why-you / why-now, board-defensibility",
    },
    "client_middle_mgmt": {
        "name": "Client Middle-Management",
        "lens": "External / feasibility",
        "cares": "Disruption to my team, workload, what this means for me on Monday",
    },
    "client_technical": {
        "name": "Client Technical Teams",
        "lens": "External / credibility",
        "cares": "Is this real or vendor fluff, depth, respect for how engineers actually work",
    },
}

ALL_PERSONAS: tuple[Persona, ...] = tuple(PERSONA_META.keys())


def rubric_path(persona: Persona) -> Path:
    """Bundle-relative path to a persona's rubric file."""
    return paths.personas_dir() / f"{persona}.md"


def load_rubric(persona: Persona) -> str:
    """Load a persona's rubric markdown from the bundle."""
    return rubric_path(persona).read_text(encoding="utf-8")


@dataclass
class CriticInput:
    """The payload handed to one critic sub-agent for one iteration."""
    persona: Persona
    phase: str                       # "A" | "B" | "D" | "G" | "H"
    artefact_paths: list[str]        # files the critic must read
    programme_context: str           # short programme framing (positioning, ICP)
    rubric: str = ""                 # persona rubric text (loaded from personas/)
    scoring_guidance: str = field(
        default=(
            "Score only what is addressable in the documents themselves (1..5). "
            "A 4 means ready to use with a real prospect with minor polish; a 5 means "
            "confidently client-ready. If an issue needs a person or a decision "
            "(pricing sign-off, real case studies, design assets, live pilots), mark it "
            "PARKED with an owner and do NOT let it reduce the score."
        )
    )

    @classmethod
    def build(cls, persona: Persona, phase: str, artefact_paths: list[str],
              programme_context: str) -> "CriticInput":
        """Construct an input with the persona rubric loaded from the bundle."""
        return cls(
            persona=persona,
            phase=phase,
            artefact_paths=artefact_paths,
            programme_context=programme_context,
            rubric=load_rubric(persona),
        )


__all__ = [
    "PERSONA_META",
    "ALL_PERSONAS",
    "rubric_path",
    "load_rubric",
    "CriticInput",
]
