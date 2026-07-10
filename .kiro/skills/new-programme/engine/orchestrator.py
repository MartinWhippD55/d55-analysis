"""Orchestrator: stages, phases, critique loop, human gates, and modes (Task 16).

Ties the engine together into the four-stage flow (Scope & Frame → Build Modules
→ Generate Assets → Verify & Ship). The autonomous six-persona critique loop runs
per artefact *before* each human "Happy?" gate; the module loop applies the gate
per in-scope module.

The runtime pieces that need a human or an LLM sub-agent — producing/critiquing
an artefact and answering a gate — are injected as callbacks, so the control flow
(loop termination, gate cycling, mode handling, the working-assumptions register)
is deterministic and testable. In production the orchestrator wires these
callbacks to the producer sub-skills, the persona critics (see
``personas/CRITIC-CONTRACT.md``), and the user prompt.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Literal, Sequence

from .critique import Decision, aggregate, should_continue, write_critique_log
from .layout import ProgrammeLayout
from .manifest import dimension_names, load_manifest
from .models import AggregateVerdict, Assessment, CritiqueResult, Finding
from .recommend import validate_assessment

STAGES = ("Scope & Frame", "Build Modules", "Generate Assets", "Verify & Ship")
CRITIQUE_PHASES = {
    "A": "Context / positioning",
    "B": "Dimensions / questions",
    "D": "Module content",
    "G": "Interactive questionnaire",
    "H": "Elevator pitch",
}

Mode = Literal["template", "client-instance"]

# Callback contracts.
CritiqueFn = Callable[[str, int], Sequence[CritiqueResult]]   # (phase, iteration) -> results
ApplyFixesFn = Callable[[Sequence[Finding]], None]            # apply top-K addressable findings
GateFn = Callable[[str, "LoopResult"], tuple[str, str]]       # -> ("Y"|"N", steer)
ReviseFn = Callable[[str], None]                              # incorporate the user's steer


# ---------------------------------------------------------------------------
# Mode handling and required-input validation (16.2)
# ---------------------------------------------------------------------------

class MissingInputError(RuntimeError):
    """Raised when a required input for the chosen mode is absent."""


class InvalidAssessmentError(RuntimeError):
    """Raised when a client-instance assessment fails the scoring contract."""

    def __init__(self, violations):
        self.violations = violations
        super().__init__(f"{len(violations)} assessment violation(s): "
                         + "; ".join(f"{v.kind}:{v.value}" for v in violations))


def prepare_run(layout: ProgrammeLayout, mode: Mode, assessment: Assessment | None = None) -> None:
    """Validate the required inputs for a run in the given mode.

    - ``template``: no assessment required.
    - ``client-instance``: an assessment is required and must satisfy the scoring
      bijection over the manifest dimensions (else prompt to run the assessment).
    """
    if mode == "template":
        return
    if mode != "client-instance":
        raise ValueError(f"unknown mode: {mode!r}")
    if assessment is None:
        raise MissingInputError(
            "client-instance mode requires the client's assessment scores — "
            "run the assessment first, or supply scores."
        )
    dims = dimension_names(load_manifest(layout.root))
    violations = validate_assessment(assessment, dims)
    if violations:
        raise InvalidAssessmentError(violations)


# ---------------------------------------------------------------------------
# Working-assumptions register (16.2)
# ---------------------------------------------------------------------------

@dataclass
class WorkingAssumption:
    assumption: str
    owner: str | None = None
    status: str = "open"


@dataclass
class WorkingAssumptions:
    """Provisional decisions to confirm; parked critique items accumulate here."""
    items: list[WorkingAssumption] = field(default_factory=list)

    def add(self, assumption: str, owner: str | None = None, status: str = "open") -> None:
        self.items.append(WorkingAssumption(assumption, owner, status))

    def extend_from_parked(self, parked: Sequence[Finding]) -> None:
        """Fold parked critique findings (need a person/decision) into the register."""
        for f in parked:
            self.add(f.issue, owner=f.owner, status="parked")

    def write(self, layout: ProgrammeLayout) -> Path:
        lines = ["# Working Assumptions", "",
                 "Provisional decisions to confirm (parked critique items included).", "",
                 "| Assumption | Owner | Status |", "|---|---|---|"]
        for a in self.items:
            lines.append(f"| {a.assumption} | {a.owner or '—'} | {a.status} |")
        lines.append("")
        layout.working_assumptions_md.parent.mkdir(parents=True, exist_ok=True)
        layout.working_assumptions_md.write_text("\n".join(lines), encoding="utf-8")
        return layout.working_assumptions_md


# ---------------------------------------------------------------------------
# Critique loop (16.1) — autonomous refinement before the human gate
# ---------------------------------------------------------------------------

@dataclass
class LoopResult:
    phase: str
    decision: Decision
    history: list[AggregateVerdict]

    @property
    def final(self) -> AggregateVerdict:
        return self.history[-1]

    @property
    def iterations(self) -> int:
        return len(self.history)


def run_critique_loop(
    phase: str,
    critique_fn: CritiqueFn,
    apply_fixes_fn: ApplyFixesFn | None = None,
    *,
    programme_dir: Path | None = None,
    top_k: int = 3,
) -> LoopResult:
    """Run the bounded critique loop for one artefact and return the outcome.

    Each round: gather persona results, aggregate, decide PASS/ITERATE/ESCALATE.
    On ITERATE apply the top-K addressable findings and re-critique. Always
    terminates (cap + stall guards in ``should_continue``). Appends an audit log
    per round when ``programme_dir`` is given.
    """
    history: list[AggregateVerdict] = []
    while True:
        iteration = len(history) + 1
        results = list(critique_fn(phase, iteration))
        verdict = aggregate(results, phase, iteration)
        prev = len(history[-1].backlog) if history else None
        history.append(verdict)
        decision = should_continue(history)
        if programme_dir is not None:
            write_critique_log(programme_dir, verdict, decision, prev_backlog_size=prev)
        if decision in ("PASS", "ESCALATE"):
            return LoopResult(phase, decision, history)
        if apply_fixes_fn is not None:
            apply_fixes_fn(verdict.backlog[:top_k])


# ---------------------------------------------------------------------------
# Human gate cycle (16.1)
# ---------------------------------------------------------------------------

@dataclass
class PhaseOutcome:
    phase: str
    loop: LoopResult
    approved: bool
    gate_rounds: int


def run_phase_with_gate(
    phase: str,
    critique_fn: CritiqueFn,
    gate_fn: GateFn,
    apply_fixes_fn: ApplyFixesFn | None = None,
    revise_fn: ReviseFn | None = None,
    *,
    programme_dir: Path | None = None,
    max_gate_rounds: int = 5,
) -> PhaseOutcome:
    """Run the critique loop then the human gate; re-refine on 'No'.

    Returns when the user answers 'Y' (approved) or the gate-round cap is hit
    (not approved — surface the open backlog).
    """
    loop = None
    for rnd in range(1, max_gate_rounds + 1):
        loop = run_critique_loop(phase, critique_fn, apply_fixes_fn, programme_dir=programme_dir)
        answer, steer = gate_fn(phase, loop)
        if answer == "Y":
            return PhaseOutcome(phase, loop, approved=True, gate_rounds=rnd)
        if revise_fn is not None:
            revise_fn(steer)
    return PhaseOutcome(phase, loop, approved=False, gate_rounds=max_gate_rounds)


# ---------------------------------------------------------------------------
# Orchestrator (state)
# ---------------------------------------------------------------------------

@dataclass
class Orchestrator:
    """Holds run state (mode, layout, assumptions) and sequences phases."""
    layout: ProgrammeLayout
    mode: Mode
    assessment: Assessment | None = None
    assumptions: WorkingAssumptions = field(default_factory=WorkingAssumptions)

    def prepare(self) -> None:
        prepare_run(self.layout, self.mode, self.assessment)

    def critique_phase(
        self,
        phase: str,
        critique_fn: CritiqueFn,
        gate_fn: GateFn,
        apply_fixes_fn: ApplyFixesFn | None = None,
        revise_fn: ReviseFn | None = None,
    ) -> PhaseOutcome:
        outcome = run_phase_with_gate(
            phase, critique_fn, gate_fn, apply_fixes_fn, revise_fn,
            programme_dir=self.layout.root,
        )
        # Parked items from the final round accumulate in the register.
        self.assumptions.extend_from_parked(outcome.loop.final.parked)
        return outcome

    def finalize(self) -> Path:
        return self.assumptions.write(self.layout)


__all__ = [
    "STAGES",
    "CRITIQUE_PHASES",
    "Mode",
    "MissingInputError",
    "InvalidAssessmentError",
    "prepare_run",
    "WorkingAssumption",
    "WorkingAssumptions",
    "LoopResult",
    "run_critique_loop",
    "PhaseOutcome",
    "run_phase_with_gate",
    "Orchestrator",
]
