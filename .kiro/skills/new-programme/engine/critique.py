"""Critique aggregation, convergence, and termination (the six-persona loop).

The aggregator merges one iteration's per-persona results into a single ranked,
deduped backlog and a pass/fail verdict; ``should_continue`` decides PASS /
ITERATE / ESCALATE. Three guards guarantee the loop always terminates
(Properties 7, 8): a clean pass, a hard iteration cap, and stall detection when
the addressable backlog stops shrinking.

Scoring integrity (Property 9): only *addressable* findings and per-persona
scores gate an artefact. *Parked* findings (needing a person or a decision) never
count against the score or the gate — they accumulate for the human review.

Deterministic dedupe (Property 10): identical findings raised by multiple
personas collapse to exactly one ranked backlog item, deterministically.
"""
from __future__ import annotations

from pathlib import Path
from typing import Literal

from .models import AggregateVerdict, CritiqueResult, Finding, Persona


# ---------------------------------------------------------------------------
# Tunable configuration (design "critique aggregation" section)
# ---------------------------------------------------------------------------

# Weights bias ranking, never gating.
PERSONA_WEIGHTS: dict[Persona, float] = {
    "d55_cto": 1.3,          # technical credibility gates internal sign-off
    "client_csuite": 1.3,    # the buyer gates the sale
    "d55_ceo": 1.1,
    "d55_marketing": 1.0,
    "client_technical": 1.0,
    "client_middle_mgmt": 0.9,
}

SEVERITY_WEIGHT: dict[str, int] = {"blocker": 8, "major": 4, "minor": 2, "nit": 1}

MAX_ITERATIONS = 3           # per artefact; matches the established process. Tunable.
CONVERGENCE_DELTA = 1        # backlog must shrink by >= this each round, else stall.

# Internal vs external personas -> primary-persona pass thresholds.
INTERNAL_PERSONAS: frozenset[Persona] = frozenset({"d55_ceo", "d55_cto", "d55_marketing"})
INTERNAL_THRESHOLD = 4       # internal primary >= 4/5
EXTERNAL_THRESHOLD = 3       # external primary >= 3/5 (credibility, not perfection)

# Persona -> artefact relevance matrix: the PRIMARY (score-gating, "●●") personas
# per phase. Contributing/light-touch personas critique but do not gate.
# (Fuller matrix + rubric files are authored in Task 7.)
PRIMARY_PERSONAS: dict[str, tuple[Persona, ...]] = {
    "A": ("d55_ceo", "d55_marketing", "client_csuite"),          # Context / positioning
    "B": ("d55_cto", "client_middle_mgmt", "client_technical"),  # Dimensions / questions
    "D": ("d55_cto", "client_middle_mgmt", "client_technical"),  # Module content
    "G": ("d55_marketing", "client_csuite"),                     # Interactive questionnaire
    "H": ("d55_ceo", "d55_marketing", "client_csuite"),          # Elevator pitch
}


def primary_thresholds(
    phase: str, overrides: dict[Persona, int] | None = None
) -> dict[Persona, int]:
    """Return ``{persona: threshold}`` for the phase's primary personas.

    Internal primaries need >= 4, external primaries >= 3. ``overrides`` (e.g.
    from the manifest) may tune individual thresholds.
    """
    thresholds = {
        p: (INTERNAL_THRESHOLD if p in INTERNAL_PERSONAS else EXTERNAL_THRESHOLD)
        for p in PRIMARY_PERSONAS.get(phase, ())
    }
    if overrides:
        thresholds.update({p: t for p, t in overrides.items() if p in thresholds})
    return thresholds


# ---------------------------------------------------------------------------
# Dedupe helpers (deterministic — Property 10)
# ---------------------------------------------------------------------------

_SEVERITY_ORDER = {"blocker": 0, "major": 1, "minor": 2, "nit": 3}


def _key(f: Finding) -> str:
    """Normalised signature used to merge the same finding across personas."""
    return (f.dedupe_key or f.issue).strip().lower()


def _cross_persona_freq(key: str, results: list[CritiqueResult]) -> int:
    """How many distinct personas raised a finding with this signature."""
    personas = {
        r.persona
        for r in results
        for f in r.findings
        if _key(f) == key
    }
    return len(personas)


def _dedupe(findings: list[Finding]) -> list[Finding]:
    """Collapse findings sharing a signature into one representative, deterministically.

    The representative is the highest-severity finding; ties break by higher
    persona weight, then persona name, then the signature — so the result never
    depends on input ordering.
    """
    groups: dict[str, list[Finding]] = {}
    for f in findings:
        groups.setdefault(_key(f), []).append(f)

    representatives: list[Finding] = []
    for key, group in groups.items():
        rep = min(
            group,
            key=lambda f: (
                _SEVERITY_ORDER[f.severity],
                -PERSONA_WEIGHTS[f.persona],
                f.persona,
            ),
        )
        representatives.append(rep)
    # Stable, input-order-independent ordering.
    representatives.sort(key=lambda f: (_SEVERITY_ORDER[f.severity], _key(f)))
    return representatives


# ---------------------------------------------------------------------------
# Aggregation + gating
# ---------------------------------------------------------------------------

def aggregate(results: list[CritiqueResult], phase: str, iteration: int) -> AggregateVerdict:
    """Merge one iteration's persona results into a ranked verdict."""
    addressable_raw = [f for r in results for f in r.findings if f.disposition == "addressable"]
    parked_raw = [f for r in results for f in r.findings if f.disposition == "parked"]

    addressable = _dedupe(addressable_raw)
    parked = _dedupe(parked_raw)

    for f in addressable:
        freq = _cross_persona_freq(_key(f), results)
        f.rank = SEVERITY_WEIGHT[f.severity] * PERSONA_WEIGHTS[f.persona] * freq

    # Rank desc; deterministic tie-break by signature.
    backlog = sorted(addressable, key=lambda f: (-f.rank, _key(f)))
    scores = {r.persona: r.score for r in results}

    return AggregateVerdict(
        phase=phase,
        iteration=iteration,
        per_persona_scores=scores,
        backlog=backlog,
        parked=parked,
        passed=_gates_met(phase, scores, backlog),
    )


def _gates_met(phase: str, scores: dict[Persona, int], backlog: list[Finding]) -> bool:
    """Primary-persona thresholds met AND no open blocker in the addressable backlog."""
    if any(f.severity == "blocker" for f in backlog):
        return False
    return all(
        scores.get(p, 0) >= threshold
        for p, threshold in primary_thresholds(phase).items()
    )


# ---------------------------------------------------------------------------
# Termination decision (always terminates — Properties 7, 8)
# ---------------------------------------------------------------------------

Decision = Literal["PASS", "ITERATE", "ESCALATE"]


def should_continue(history: list[AggregateVerdict]) -> Decision:
    """Decide the next step from the verdict history.

    - PASS      — latest verdict passed -> hand to the human gate.
    - ESCALATE  — iteration cap hit, or the backlog stalled (shrank by
                  < ``CONVERGENCE_DELTA``) -> stop, surface open items.
    - ITERATE   — apply top addressable findings and re-critique.
    """
    if not history:
        return "ITERATE"
    latest = history[-1]
    if latest.passed:
        return "PASS"
    if len(history) >= MAX_ITERATIONS:
        return "ESCALATE"
    if len(history) >= 2 and (len(history[-2].backlog) - len(latest.backlog)) < CONVERGENCE_DELTA:
        return "ESCALATE"
    return "ITERATE"


# ---------------------------------------------------------------------------
# Auditable critique log (Requirement 4.8)
# ---------------------------------------------------------------------------

def write_critique_log(
    programme_dir: Path,
    verdict: AggregateVerdict,
    decision: Decision,
    prev_backlog_size: int | None = None,
) -> Path:
    """Append this round's scores, backlog delta, and decision to an audit log.

    Writes ``internal/critique/critique-<phase>-<iter>.md`` under the programme
    directory (critique logs are internal-only). Returns the log path.
    """
    log_dir = Path(programme_dir) / "internal" / "critique"
    log_dir.mkdir(parents=True, exist_ok=True)
    path = log_dir / f"critique-{verdict.phase}-{verdict.iteration}.md"

    delta = (
        "n/a (first round)"
        if prev_backlog_size is None
        else f"{prev_backlog_size} \u2192 {len(verdict.backlog)} "
        f"({len(verdict.backlog) - prev_backlog_size:+d})"
    )
    scores = ", ".join(f"{p}={s}" for p, s in sorted(verdict.per_persona_scores.items()))

    lines = [
        f"# Critique — phase {verdict.phase}, iteration {verdict.iteration}",
        "",
        f"- **Decision:** {decision}",
        f"- **Passed:** {verdict.passed}",
        f"- **Per-persona scores:** {scores or '(none)'}",
        f"- **Addressable backlog:** {len(verdict.backlog)} (delta {delta})",
        f"- **Parked:** {len(verdict.parked)}",
        "",
        "## Addressable backlog (ranked)",
        "",
    ]
    if verdict.backlog:
        for i, f in enumerate(verdict.backlog, 1):
            lines.append(
                f"{i}. [{f.severity}] ({f.persona}, rank {f.rank:.1f}) "
                f"{f.issue} — *{f.suggestion}*"
            )
    else:
        lines.append("_none_")
    lines += ["", "## Parked (needs a person / decision)", ""]
    if verdict.parked:
        for f in verdict.parked:
            owner = f" [owner: {f.owner}]" if f.owner else ""
            lines.append(f"- [{f.severity}] {f.issue}{owner} — *{f.suggestion}*")
    else:
        lines.append("_none_")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


__all__ = [
    "PERSONA_WEIGHTS",
    "SEVERITY_WEIGHT",
    "MAX_ITERATIONS",
    "CONVERGENCE_DELTA",
    "PRIMARY_PERSONAS",
    "primary_thresholds",
    "aggregate",
    "should_continue",
    "write_critique_log",
    "Decision",
]
