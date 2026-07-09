"""Tests for critique aggregation and termination (Task 6).

- 6.3 unit: aggregate (dedupe / weighting / gate) and should_continue
  (PASS, cap ESCALATE, stall ESCALATE, ITERATE).
- 6.4 property: loop termination within the cap for adversarial/oscillating
  streams (Properties 7, 8), gate integrity — parked never counts (Property 9),
  aggregator determinism / dedupe (Property 10).
"""
from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from engine.critique import (
    MAX_ITERATIONS,
    aggregate,
    should_continue,
    write_critique_log,
)
from engine.models import AggregateVerdict, CritiqueResult, Finding


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------

def _finding(persona, severity="major", disposition="addressable", issue="x", key=""):
    return Finding(
        persona=persona,
        severity=severity,
        disposition=disposition,
        target="artefact",
        issue=issue,
        suggestion="fix it",
        dedupe_key=key,
    )


def _result(persona, score, findings, phase="D"):
    return CritiqueResult(phase=phase, persona=persona, score=score, findings=findings, verdict="ITERATE")


def _verdict(passed, backlog_size, phase="D", iteration=1):
    return AggregateVerdict(
        phase=phase,
        iteration=iteration,
        per_persona_scores={},
        backlog=[_finding("d55_cto")] * backlog_size,
        parked=[],
        passed=passed,
    )


# ---------------------------------------------------------------------------
# 6.3 — aggregate: dedupe, weighting, gate
# ---------------------------------------------------------------------------

def test_identical_findings_across_personas_collapse_to_one():
    # Three primary personas raise the same issue (same signature).
    results = [
        _result("d55_cto", 4, [_finding("d55_cto", issue="weak governance story")]),
        _result("client_middle_mgmt", 4, [_finding("client_middle_mgmt", issue="weak governance story")]),
        _result("client_technical", 4, [_finding("client_technical", issue="weak governance story")]),
    ]
    v = aggregate(results, phase="D", iteration=1)
    assert len(v.backlog) == 1                      # collapsed (Property 10)
    # rank reflects cross-persona frequency of 3.
    from engine.critique import PERSONA_WEIGHTS, SEVERITY_WEIGHT
    rep = v.backlog[0]
    assert rep.rank == SEVERITY_WEIGHT["major"] * PERSONA_WEIGHTS[rep.persona] * 3


def test_higher_severity_ranks_first():
    results = [
        _result("d55_cto", 4, [
            _finding("d55_cto", severity="nit", issue="a nit"),
            _finding("d55_cto", severity="blocker", issue="a blocker"),
        ]),
    ]
    v = aggregate(results, phase="D", iteration=1)
    assert v.backlog[0].issue == "a blocker"
    assert v.backlog[-1].issue == "a nit"


def test_gate_passes_when_primaries_meet_threshold_and_no_blocker():
    # Phase D primaries: d55_cto (>=4), client_middle_mgmt (>=3), client_technical (>=3).
    results = [
        _result("d55_cto", 4, [_finding("d55_cto", severity="minor")]),
        _result("client_middle_mgmt", 3, []),
        _result("client_technical", 3, []),
    ]
    v = aggregate(results, phase="D", iteration=1)
    assert v.passed is True


def test_gate_fails_on_open_blocker():
    results = [
        _result("d55_cto", 5, [_finding("d55_cto", severity="blocker")]),
        _result("client_middle_mgmt", 5, []),
        _result("client_technical", 5, []),
    ]
    assert aggregate(results, "D", 1).passed is False


def test_gate_fails_when_primary_below_threshold():
    results = [
        _result("d55_cto", 3, []),   # internal primary needs >= 4
        _result("client_middle_mgmt", 5, []),
        _result("client_technical", 5, []),
    ]
    assert aggregate(results, "D", 1).passed is False


def test_gate_fails_when_primary_persona_absent():
    # Only one of three primaries reported — the gate must not silently pass.
    results = [_result("d55_cto", 5, [])]
    assert aggregate(results, "D", 1).passed is False


def test_parked_findings_are_separated_from_backlog():
    results = [
        _result("d55_cto", 4, [
            _finding("d55_cto", disposition="parked", severity="blocker", issue="needs pricing sign-off"),
            _finding("d55_cto", disposition="addressable", severity="minor", issue="tighten wording"),
        ]),
        _result("client_middle_mgmt", 3, []),
        _result("client_technical", 3, []),
    ]
    v = aggregate(results, "D", 1)
    assert len(v.parked) == 1
    assert len(v.backlog) == 1
    assert v.passed is True   # parked blocker must NOT fail the gate (Property 9)


# ---------------------------------------------------------------------------
# 6.3 — should_continue
# ---------------------------------------------------------------------------

def test_should_continue_pass():
    assert should_continue([_verdict(passed=True, backlog_size=2)]) == "PASS"


def test_should_continue_iterate_while_shrinking_under_cap():
    history = [_verdict(False, 5, iteration=1), _verdict(False, 3, iteration=2)]
    assert should_continue(history) == "ITERATE"


def test_should_continue_escalates_on_cap():
    history = [_verdict(False, 5, iteration=i) for i in range(1, MAX_ITERATIONS + 1)]
    assert should_continue(history) == "ESCALATE"


def test_should_continue_escalates_on_stall():
    # Backlog did not shrink between the last two rounds.
    history = [_verdict(False, 4, iteration=1), _verdict(False, 4, iteration=2)]
    assert should_continue(history) == "ESCALATE"


# ---------------------------------------------------------------------------
# 6.4 — property tests
# ---------------------------------------------------------------------------

@given(st.data())
@settings(max_examples=300)
def test_loop_always_terminates_within_cap(data):
    """Adversarial/oscillating streams still stop within MAX_ITERATIONS (Props 7, 8)."""
    history: list[AggregateVerdict] = []
    decision = "ITERATE"
    for i in range(MAX_ITERATIONS + 5):
        size = data.draw(st.integers(min_value=0, max_value=10))
        passed = data.draw(st.booleans())
        history.append(_verdict(passed, size, iteration=i + 1))
        decision = should_continue(history)
        if decision != "ITERATE":
            break
    assert decision in {"PASS", "ESCALATE"}
    assert len(history) <= MAX_ITERATIONS


PERSONAS = ["d55_ceo", "d55_cto", "d55_marketing", "client_csuite", "client_middle_mgmt", "client_technical"]
SEVERITIES = ["blocker", "major", "minor", "nit"]


@st.composite
def results_lists(draw):
    n = draw(st.integers(min_value=1, max_value=6))
    out = []
    for _ in range(n):
        persona = draw(st.sampled_from(PERSONAS))
        score = draw(st.integers(1, 5))
        fcount = draw(st.integers(0, 4))
        findings = [
            _finding(
                persona,
                severity=draw(st.sampled_from(SEVERITIES)),
                disposition="addressable",
                issue=draw(st.sampled_from(["a", "b", "c", "d"])),
            )
            for _ in range(fcount)
        ]
        out.append(_result(persona, score, findings))
    return out


@given(results_lists())
@settings(max_examples=200)
def test_aggregate_is_deterministic(results):
    """Property 10: aggregation is order-stable and repeatable."""
    a = aggregate(results, "D", 1)
    b = aggregate(results, "D", 1)
    proj = lambda v: [(f.persona, f.severity, f.issue, round(f.rank, 4)) for f in v.backlog]
    assert proj(a) == proj(b)


@given(results_lists())
@settings(max_examples=200)
def test_dedupe_collapses_same_signature(results):
    """No two backlog items share a signature (Property 10)."""
    v = aggregate(results, "D", 1)
    keys = [(f.issue).strip().lower() for f in v.backlog]
    assert len(keys) == len(set(keys))


@given(results_lists(), st.integers(0, 5))
@settings(max_examples=200)
def test_parked_never_affects_gate(results, n_parked):
    """Property 9: adding parked findings (any severity) never changes the gate."""
    passed_before = aggregate(results, "D", 1).passed
    if results:
        results[0].findings.extend(
            _finding(results[0].persona, severity="blocker", disposition="parked", issue=f"parked-{i}")
            for i in range(n_parked)
        )
    passed_after = aggregate(results, "D", 1).passed
    assert passed_before == passed_after


# ---------------------------------------------------------------------------
# 6.2 — critique log writer
# ---------------------------------------------------------------------------

def test_write_critique_log_writes_under_internal(tmp_path):
    results = [
        _result("d55_cto", 4, [_finding("d55_cto", severity="major", issue="x")]),
        _result("client_middle_mgmt", 3, []),
        _result("client_technical", 3, []),
    ]
    v = aggregate(results, "D", 2)
    path = write_critique_log(tmp_path, v, decision="ITERATE", prev_backlog_size=3)
    # Internal-only location.
    assert path.parent == tmp_path / "internal" / "critique"
    assert path.name == "critique-D-2.md"
    text = path.read_text(encoding="utf-8")
    assert "Decision:** ITERATE" in text
    assert "3 \u2192 1" in text   # backlog delta recorded
    assert "d55_cto=4" in text
