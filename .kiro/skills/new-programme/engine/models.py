"""Core data models for the New Programme skill.

These dataclasses are the shared vocabulary across the engine: assessment
scores (radar input), module recommendations (trigger-logic output), the
six-persona critique models, and contract violations from join-key validation.

They mirror the definitions in the design document exactly so the recommendation
logic (build-time and the interactive questionnaire) and the critique loop can
be built test-first against a stable contract.

``BrandConfig`` lives in ``programme_engine`` (the render engine) and is
re-exported here so callers have a single import surface for "the models".
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

# Re-export the render engine's BrandConfig so models are a single import point.
from .programme_engine import BrandConfig  # noqa: F401


# ---------------------------------------------------------------------------
# Assessment scores (radar input)
# ---------------------------------------------------------------------------

@dataclass
class DimensionScore:
    """One dimension's current-vs-target maturity score (1..5).

    ``dimension`` is the exact dimension name — the JOIN KEY to
    ``dimensions[].name`` in the manifest and to a module's
    ``dimensions_covered``. Keep it byte-identical to those.
    """
    dimension: str        # exact dimension name (join key)
    current: int          # 1..5
    target: int           # 1..5
    notes: str = ""

    @property
    def gap(self) -> int:
        """Non-negative ambition gap (target minus current, floored at 0)."""
        return max(0, self.target - self.current)


@dataclass
class Assessment:
    """A full set of dimension scores for one client (or a template blank)."""
    client_name: str | None          # None in template mode
    scores: list[DimensionScore]     # exactly one per manifest dimension
    captured_at: str = ""

    def score_for(self, dimension: str) -> DimensionScore:
        """Return the score for ``dimension`` (exact-match join key).

        Raises ``KeyError`` if the dimension is not scored — the scoring
        bijection is enforced separately by ``validate_assessment``; callers
        that reach here are expected to have validated first.
        """
        for s in self.scores:
            if s.dimension == dimension:
                return s
        raise KeyError(f"dimension not scored: {dimension!r}")


# ---------------------------------------------------------------------------
# Module recommendation (output of trigger logic)
# ---------------------------------------------------------------------------

Status = Literal["critical", "high", "standard", "excluded"]


@dataclass
class Recommendation:
    """A module's recommendation status for a given assessment.

    ``status`` is the highest level triggered (critical > high > standard);
    an excluded module is not returned by ``recommend_modules``.
    """
    module_id: int
    status: Status
    reason: str            # human-readable rationale


# ---------------------------------------------------------------------------
# Critique data models (six-persona loop)
# ---------------------------------------------------------------------------

Severity = Literal["blocker", "major", "minor", "nit"]
Persona = Literal[
    "d55_ceo", "d55_cto", "d55_marketing",
    "client_csuite", "client_middle_mgmt", "client_technical",
]
# parked = needs a person/decision, never counts against an artefact's score.
Disposition = Literal["addressable", "parked"]


@dataclass
class Finding:
    """A single critique finding from one persona."""
    persona: Persona
    severity: Severity
    disposition: Disposition
    target: str            # artefact path / logical id the finding is about
    issue: str             # what's wrong (specific)
    suggestion: str        # what to change
    owner: str | None = None   # for parked items (e.g. "Rhys", "Marketing/Design")
    dedupe_key: str = ""   # normalised issue signature for cross-persona merge
    rank: float = 0.0      # computed by the aggregator (severity x weight x freq)


@dataclass
class CritiqueResult:
    """One persona's scorecard for an artefact in one iteration."""
    phase: str             # "A" | "B" | "D" | "G" | "H"
    persona: Persona
    score: int             # 1..5 readiness (addressable items only)
    findings: list[Finding]
    verdict: Literal["PASS", "ITERATE"]
    summary: str = ""


@dataclass
class AggregateVerdict:
    """The merged verdict across all personas for one iteration."""
    phase: str
    iteration: int
    per_persona_scores: dict[Persona, int]
    backlog: list[Finding]          # deduped, ranked, addressable only
    parked: list[Finding]           # accumulates into working-assumptions.md
    passed: bool                    # primary thresholds met AND no open blockers


# ---------------------------------------------------------------------------
# Contract violation (join-key validation output)
# ---------------------------------------------------------------------------

ViolationKind = Literal[
    "unknown_dimension", "unknown_manual_section",
    "critical_not_covered", "unscored_dimension", "duplicate_score",
    "out_of_range_score",
]


@dataclass
class ContractViolation:
    """A single join-key / scoring contract failure."""
    kind: ViolationKind
    where: str        # module id / file
    value: str        # the offending string


__all__ = [
    "BrandConfig",
    "DimensionScore",
    "Assessment",
    "Status",
    "Recommendation",
    "Severity",
    "Persona",
    "Disposition",
    "Finding",
    "CritiqueResult",
    "AggregateVerdict",
    "ViolationKind",
    "ContractViolation",
]
