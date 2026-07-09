"""Recommendation logic: assessment scores -> recommended modules.

This is the **single** implementation of the MODULE-SCHEMA trigger logic. Both
build-time client-instance scoping and the interactive questionnaire's
client-side recommendation must produce identical results for identical scores
(Property 6) — so this module is the one source of truth and must not be forked.
The interactive questionnaire (Task 13) mirrors this algorithm in JavaScript and
is parity-tested against it.

Trigger semantics (from ``MODULE-SCHEMA.md``), per module, over each covered
dimension:

1. ``current <= recommend_when_current_at_or_below``            -> included
2. ``(target - current) >= include_when_gap_at_or_above``       -> included (ambition-driven)
3. ``critical_when_current_at_or_below`` set AND dimension in
   ``critical_dimensions`` AND ``current <=`` that threshold     -> included + critical (hard gate)

A module is included if 1, 2, or 3 fires on any covered dimension. For an
included module, if ``(target - current) >= prioritise_when_gap_at_or_above`` on
any covered dimension it is flagged **high**. The reported status is the highest
level triggered: critical > high > standard. Excluded modules are not returned.
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping

from .models import Assessment, ContractViolation, Recommendation, Status


# ---------------------------------------------------------------------------
# Module normalisation (accept manifest `modules[]` or parsed frontmatter)
# ---------------------------------------------------------------------------

def _module_id(module: Mapping[str, Any]) -> int:
    """Module id from either frontmatter (``module_id``) or manifest (``id``)."""
    if "module_id" in module:
        return int(module["module_id"])
    if "id" in module:
        return int(module["id"])
    raise KeyError("module has neither 'module_id' nor 'id'")


def _covered(module: Mapping[str, Any]) -> list[str]:
    return list(module.get("dimensions_covered", []) or [])


def _trigger(module: Mapping[str, Any]) -> Mapping[str, Any]:
    return module.get("trigger", {}) or {}


# ---------------------------------------------------------------------------
# Assessment validation (scoring bijection + 1..5 range — Property 2)
# ---------------------------------------------------------------------------

def validate_assessment(
    assessment: Assessment, dimensions: Iterable[str]
) -> list[ContractViolation]:
    """Validate the scoring contract: bijection with the manifest, 1..5 range.

    Returns violations for:

    - ``out_of_range_score`` — a current/target outside 1..5.
    - ``duplicate_score``    — a dimension scored more than once.
    - ``unknown_dimension``  — a score for a dimension not in the manifest.
    - ``unscored_dimension`` — a manifest dimension with no score.

    An empty list means the assessment is a valid bijection over the manifest
    dimensions; ``recommend_modules`` assumes this precondition holds.
    """
    dim_set = set(dimensions)
    violations: list[ContractViolation] = []

    seen: dict[str, int] = {}
    for s in assessment.scores:
        seen[s.dimension] = seen.get(s.dimension, 0) + 1
        for label, val in (("current", s.current), ("target", s.target)):
            if not isinstance(val, int) or not (1 <= val <= 5):
                violations.append(
                    ContractViolation("out_of_range_score", s.dimension, f"{label}={val}")
                )
        if s.dimension not in dim_set:
            violations.append(ContractViolation("unknown_dimension", "assessment", s.dimension))

    for dim, count in seen.items():
        if count > 1:
            violations.append(ContractViolation("duplicate_score", "assessment", dim))

    for dim in dim_set:
        if dim not in seen:
            violations.append(ContractViolation("unscored_dimension", "assessment", dim))

    return violations


# ---------------------------------------------------------------------------
# Recommendation (the shared trigger algorithm)
# ---------------------------------------------------------------------------

def recommend_modules(
    assessment: Assessment, modules: Iterable[Mapping[str, Any]]
) -> list[Recommendation]:
    """Return the included modules with their status (critical > high > standard).

    Preconditions: ``assessment`` covers every dimension a module references
    exactly once (validate with :func:`validate_assessment` first). Modules are
    dict-like, shaped as manifest ``modules[]`` entries or parsed ``module.md``
    frontmatter.

    Postconditions: each module appears at most once; only included modules are
    returned; ``status`` is the highest level triggered; an excluded module is
    never returned with a priority.
    """
    results: list[Recommendation] = []

    for module in modules:
        covered = _covered(module)
        trig = _trigger(module)
        recommend_at = trig.get("recommend_when_current_at_or_below")
        include_gap = trig.get("include_when_gap_at_or_above")
        prioritise_gap = trig.get("prioritise_when_gap_at_or_above")
        critical_dims = set(trig.get("critical_dimensions", []) or [])
        critical_at = trig.get("critical_when_current_at_or_below")

        included = False
        critical = False
        include_reasons: list[str] = []

        for d in covered:
            s = assessment.score_for(d)
            gap = s.target - s.current
            if recommend_at is not None and s.current <= recommend_at:
                included = True
                include_reasons.append(f"{d} current {s.current} \u2264 {recommend_at}")
            if include_gap is not None and gap >= include_gap:
                included = True
                include_reasons.append(f"{d} gap {gap} \u2265 {include_gap} (ambition)")
            if critical_at is not None and d in critical_dims and s.current <= critical_at:
                included = True
                critical = True
                include_reasons.append(
                    f"{d} current {s.current} \u2264 critical gate {critical_at}"
                )

        if not included:
            continue

        high = False
        for d in covered:
            s = assessment.score_for(d)
            if prioritise_gap is not None and (s.target - s.current) >= prioritise_gap:
                high = True

        status: Status = "critical" if critical else ("high" if high else "standard")
        reason = _reason(status, include_reasons)
        results.append(Recommendation(_module_id(module), status, reason))

    return results


def _reason(status: Status, include_reasons: list[str]) -> str:
    lead = {
        "critical": "Critical (hard gate): ",
        "high": "High priority: ",
        "standard": "Recommended: ",
    }[status]
    # Dedupe while preserving order; keep the rationale concise.
    seen: list[str] = []
    for r in include_reasons:
        if r not in seen:
            seen.append(r)
    return lead + "; ".join(seen)


__all__ = ["validate_assessment", "recommend_modules"]
