"""Tests for the orchestrator: critique loop, gates, modes, assumptions (Task 16)."""
from __future__ import annotations

import pytest

from engine.critique import MAX_ITERATIONS
from engine.layout import template_layout
from engine.manifest import write_manifest
from engine.models import Assessment, CritiqueResult, DimensionScore, Finding
from engine.orchestrator import (
    InvalidAssessmentError,
    MissingInputError,
    Orchestrator,
    WorkingAssumptions,
    prepare_run,
    run_critique_loop,
    run_phase_with_gate,
)

DIMS = ["Leadership & Mandate", "Governance, Security & Compliance"]


def _layout(tmp_path):
    layout = template_layout(tmp_path, "demo").create()
    write_manifest({"programme": {"slug": "demo", "name": "Demo"},
                    "dimensions": [{"name": d} for d in DIMS], "modules": []}, layout.root)
    return layout


def _finding(persona, severity="major", disposition="addressable", issue="i", owner=None):
    return Finding(persona, severity, disposition, "artefact", issue, "fix", owner=owner)


def _results(scores: dict, findings_by_persona: dict | None = None):
    findings_by_persona = findings_by_persona or {}
    return [
        CritiqueResult(phase="D", persona=p, score=s,
                       findings=findings_by_persona.get(p, []), verdict="ITERATE")
        for p, s in scores.items()
    ]


# Phase D primaries: d55_cto (>=4), client_middle_mgmt (>=3), client_technical (>=3).
PASS_SCORES = {"d55_cto": 4, "client_middle_mgmt": 3, "client_technical": 3}


# ---------------------------------------------------------------------------
# Critique loop
# ---------------------------------------------------------------------------

def test_loop_passes_immediately_on_clean_critique(tmp_path):
    layout = _layout(tmp_path)
    critique_fn = lambda phase, it: _results(PASS_SCORES)
    result = run_critique_loop("D", critique_fn, programme_dir=layout.root)
    assert result.decision == "PASS"
    assert result.iterations == 1
    # An audit log was written under internal/critique.
    assert (layout.critique_dir / "critique-D-1.md").exists()


def test_loop_iterates_then_passes_after_fixes(tmp_path):
    layout = _layout(tmp_path)
    state = {"fixed": False}

    def critique_fn(phase, it):
        if state["fixed"]:
            return _results(PASS_SCORES)
        return _results({"d55_cto": 2, "client_middle_mgmt": 3, "client_technical": 3},
                        {"d55_cto": [_finding("d55_cto", issue="tighten spec")]})

    def apply_fixes(backlog):
        state["fixed"] = True

    result = run_critique_loop("D", critique_fn, apply_fixes, programme_dir=layout.root)
    assert result.decision == "PASS"
    assert result.iterations == 2


def test_loop_escalates_on_cap(tmp_path):
    layout = _layout(tmp_path)
    # Never passes; backlog shrinks by 1 each round so it runs to the cap.
    sizes = iter([3, 2, 1, 1, 1])

    def critique_fn(phase, it):
        n = next(sizes)
        findings = [_finding("d55_cto", issue=f"issue-{k}") for k in range(n)]
        return _results({"d55_cto": 2, "client_middle_mgmt": 3, "client_technical": 3},
                        {"d55_cto": findings})

    result = run_critique_loop("D", critique_fn, apply_fixes_fn=lambda b: None,
                               programme_dir=layout.root)
    assert result.decision == "ESCALATE"
    assert result.iterations == MAX_ITERATIONS


def test_loop_escalates_on_stall(tmp_path):
    layout = _layout(tmp_path)
    # Backlog never shrinks -> stall -> escalate at iteration 2.
    def critique_fn(phase, it):
        findings = [_finding("d55_cto", issue=f"issue-{k}") for k in range(3)]
        return _results({"d55_cto": 2, "client_middle_mgmt": 3, "client_technical": 3},
                        {"d55_cto": findings})

    result = run_critique_loop("D", critique_fn, apply_fixes_fn=lambda b: None)
    assert result.decision == "ESCALATE"
    assert result.iterations == 2


# ---------------------------------------------------------------------------
# Human gate cycle
# ---------------------------------------------------------------------------

def test_gate_cycles_on_no_then_advances_on_yes(tmp_path):
    layout = _layout(tmp_path)
    critique_fn = lambda phase, it: _results(PASS_SCORES)
    answers = iter([("N", "make it punchier"), ("Y", "")])
    revised = {"count": 0}

    outcome = run_phase_with_gate(
        "D", critique_fn,
        gate_fn=lambda phase, loop: next(answers),
        revise_fn=lambda steer: revised.__setitem__("count", revised["count"] + 1),
        programme_dir=layout.root,
    )
    assert outcome.approved is True
    assert outcome.gate_rounds == 2
    assert revised["count"] == 1


# ---------------------------------------------------------------------------
# Mode handling / required inputs
# ---------------------------------------------------------------------------

def test_prepare_run_template_needs_nothing(tmp_path):
    prepare_run(_layout(tmp_path), "template")  # no raise


def test_prepare_run_client_instance_requires_assessment(tmp_path):
    with pytest.raises(MissingInputError):
        prepare_run(_layout(tmp_path), "client-instance", assessment=None)


def test_prepare_run_rejects_invalid_assessment(tmp_path):
    layout = _layout(tmp_path)
    bad = Assessment("Acme", [DimensionScore("Leadership & Mandate", 0, 6)])  # bad range + missing dim
    with pytest.raises(InvalidAssessmentError):
        prepare_run(layout, "client-instance", assessment=bad)


def test_prepare_run_accepts_valid_assessment(tmp_path):
    layout = _layout(tmp_path)
    good = Assessment("Acme", [DimensionScore(d, 2, 4) for d in DIMS])
    prepare_run(layout, "client-instance", assessment=good)  # no raise


# ---------------------------------------------------------------------------
# Working assumptions register
# ---------------------------------------------------------------------------

def test_working_assumptions_write_and_parked(tmp_path):
    layout = _layout(tmp_path)
    wa = WorkingAssumptions()
    wa.add("Confirm default output root with Rhys", owner="Rhys")
    wa.extend_from_parked([_finding("client_csuite", disposition="parked",
                                    issue="Need real case studies", owner="Marketing")])
    path = wa.write(layout)
    text = path.read_text(encoding="utf-8")
    assert "Confirm default output root with Rhys | Rhys | open" in text
    assert "Need real case studies | Marketing | parked" in text


def test_orchestrator_prepare_and_finalize(tmp_path):
    layout = _layout(tmp_path)
    orch = Orchestrator(layout, mode="template")
    orch.prepare()
    critique_fn = lambda phase, it: _results(
        PASS_SCORES, {"d55_cto": [_finding("d55_cto", disposition="parked",
                                           issue="pricing sign-off", owner="Rhys")]})
    outcome = orch.critique_phase("D", critique_fn, gate_fn=lambda p, l: ("Y", ""))
    assert outcome.approved
    path = orch.finalize()
    assert "pricing sign-off | Rhys | parked" in path.read_text(encoding="utf-8")
