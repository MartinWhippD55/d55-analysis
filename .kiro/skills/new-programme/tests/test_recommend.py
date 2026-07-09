"""Tests for the shared recommendation logic (Task 5).

- Unit tests against the MODULE-SCHEMA worked example and the AI-DLC modules
  (5.2): weak-governance -> critical, high-ambition-from-strong-base -> included.
- Property tests (5.3): monotonicity (Property 3), priority-implies-inclusion
  (Property 4), critical gate (Property 5), scoring bijection (Property 2).
"""
from __future__ import annotations

from hypothesis import assume, given, settings
from hypothesis import strategies as st

from engine.models import Assessment, DimensionScore, Recommendation
from engine.recommend import recommend_modules, validate_assessment


# ---------------------------------------------------------------------------
# Reference modules (mirrors AI-DLC frontmatter)
# ---------------------------------------------------------------------------

MODULE_1 = {
    "module_id": 1,
    "dimensions_covered": ["Leadership & Mandate", "Metrics & ROI"],
    "trigger": {
        "recommend_when_current_at_or_below": 2,
        "include_when_gap_at_or_above": 2,
        "prioritise_when_gap_at_or_above": 2,
    },
}

MODULE_3 = {
    "module_id": 3,
    "dimensions_covered": ["Testing & Quality Assurance", "Governance, Security & Compliance"],
    "trigger": {
        "recommend_when_current_at_or_below": 3,
        "include_when_gap_at_or_above": 2,
        "prioritise_when_gap_at_or_above": 2,
        "critical_dimensions": ["Governance, Security & Compliance"],
        "critical_when_current_at_or_below": 2,
    },
}

ALL_DIMS = [
    "Leadership & Mandate",
    "Metrics & ROI",
    "Testing & Quality Assurance",
    "Governance, Security & Compliance",
]


def _assessment(**scores: tuple[int, int]) -> Assessment:
    """Build an assessment; unspecified dims default to current=5, target=5 (no gap)."""
    ds = []
    for dim in ALL_DIMS:
        current, target = scores.get(_key(dim), (5, 5))
        ds.append(DimensionScore(dim, current, target))
    return Assessment(client_name=None, scores=ds)


def _key(dim: str) -> str:
    return dim.lower().split()[0].strip(",")  # "leadership", "metrics", "testing", "governance"


def _by_id(recs: list[Recommendation]) -> dict[int, Recommendation]:
    return {r.module_id: r for r in recs}


# ---------------------------------------------------------------------------
# 5.2 — Worked examples
# ---------------------------------------------------------------------------

def test_weak_governance_is_critical():
    # Governance current 1 (<= critical gate 2) -> Module 3 critical.
    a = _assessment(governance=(1, 4), testing=(4, 4))
    recs = _by_id(recommend_modules(a, [MODULE_1, MODULE_3]))
    assert 3 in recs
    assert recs[3].status == "critical"


def test_high_ambition_from_strong_base_is_included():
    # Leadership current 3 (> recommend threshold 2) but gap 2 -> ambition-driven inclusion.
    a = _assessment(leadership=(3, 5), metrics=(4, 4))
    recs = _by_id(recommend_modules(a, [MODULE_1]))
    assert 1 in recs                       # included despite a base above the recommend threshold
    assert recs[1].status == "high"        # gap of 2 also meets the prioritise threshold


def test_recommend_threshold_inclusion_standard():
    # Metrics current 2 (<= recommend 2), gap 1 (< prioritise 2) -> included, standard.
    a = _assessment(leadership=(4, 4), metrics=(2, 3))
    recs = _by_id(recommend_modules(a, [MODULE_1]))
    assert 1 in recs
    assert recs[1].status == "standard"


def test_excluded_when_no_trigger_fires():
    # Everything strong, no gaps -> nothing recommended.
    a = _assessment()  # all 5/5
    recs = recommend_modules(a, [MODULE_1, MODULE_3])
    assert recs == []


def test_critical_only_applies_to_listed_dimension():
    # Testing current 1 is weak, but Testing is NOT a critical dimension for M3.
    # Governance is healthy (4). So M3 is included (testing <= 3) but NOT critical.
    a = _assessment(testing=(1, 2), governance=(4, 4))
    recs = _by_id(recommend_modules(a, [MODULE_3]))
    assert 3 in recs
    assert recs[3].status != "critical"


def test_each_module_appears_at_most_once():
    a = _assessment(leadership=(1, 5), metrics=(1, 5))
    recs = recommend_modules(a, [MODULE_1])
    assert len(recs) == 1


# ---------------------------------------------------------------------------
# 5.3 — Hypothesis strategies
# ---------------------------------------------------------------------------

DIMS = ["D1", "D2", "D3", "D4"]

score_pair = st.tuples(st.integers(1, 5), st.integers(1, 5))


@st.composite
def assessments(draw) -> Assessment:
    scores = [DimensionScore(d, *draw(score_pair)) for d in DIMS]
    return Assessment(client_name=None, scores=scores)


@st.composite
def modules(draw) -> dict:
    covered = draw(st.lists(st.sampled_from(DIMS), min_size=1, max_size=4, unique=True))
    trig = {
        "recommend_when_current_at_or_below": draw(st.integers(1, 5)),
        "include_when_gap_at_or_above": draw(st.integers(1, 4)),
        "prioritise_when_gap_at_or_above": draw(st.integers(1, 4)),
    }
    if draw(st.booleans()):
        crit = draw(st.lists(st.sampled_from(covered), min_size=1, max_size=len(covered), unique=True))
        trig["critical_dimensions"] = crit
        trig["critical_when_current_at_or_below"] = draw(st.integers(1, 5))
    return {"module_id": 1, "dimensions_covered": covered, "trigger": trig}


def _included_ids(a: Assessment, mods: list[dict]) -> set[int]:
    return {r.module_id for r in recommend_modules(a, mods)}


# ---- Property 2: scoring bijection ----------------------------------------

@given(assessments())
@settings(max_examples=200)
def test_valid_assessment_has_no_violations(a: Assessment):
    assert validate_assessment(a, DIMS) == []


def test_duplicate_score_detected():
    a = Assessment(None, [DimensionScore("D1", 3, 4), DimensionScore("D1", 2, 5),
                          DimensionScore("D2", 1, 1), DimensionScore("D3", 1, 1),
                          DimensionScore("D4", 1, 1)])
    kinds = {v.kind for v in validate_assessment(a, DIMS)}
    assert "duplicate_score" in kinds


def test_unscored_dimension_detected():
    a = Assessment(None, [DimensionScore("D1", 3, 4)])  # D2..D4 missing
    kinds = {v.kind for v in validate_assessment(a, DIMS)}
    assert "unscored_dimension" in kinds


def test_out_of_range_and_unknown_detected():
    a = Assessment(None, [DimensionScore("D1", 0, 6), DimensionScore("D2", 3, 3),
                          DimensionScore("D3", 3, 3), DimensionScore("D4", 3, 3),
                          DimensionScore("ROGUE", 3, 3)])
    kinds = {v.kind for v in validate_assessment(a, DIMS)}
    assert "out_of_range_score" in kinds
    assert "unknown_dimension" in kinds


# ---- Property 4: priority implies inclusion -------------------------------

@given(assessments(), modules())
@settings(max_examples=300)
def test_only_included_modules_returned_and_never_excluded(a: Assessment, m: dict):
    recs = recommend_modules(a, [m])
    for r in recs:
        assert r.status in {"critical", "high", "standard"}  # never "excluded"
    # A returned module is, by definition, included.
    assert len(recs) <= 1


# ---- Property 5: critical gate --------------------------------------------

@given(assessments(), modules())
@settings(max_examples=400)
def test_critical_gate_forces_inclusion_and_flag(a: Assessment, m: dict):
    trig = m["trigger"]
    crit_dims = trig.get("critical_dimensions", [])
    crit_at = trig.get("critical_when_current_at_or_below")
    gate_fires = crit_at is not None and any(
        a.score_for(d).current <= crit_at for d in crit_dims
    )
    recs = {r.module_id: r for r in recommend_modules(a, [m])}
    if gate_fires:
        assert 1 in recs
        assert recs[1].status == "critical"


# ---- Property 3: monotonicity ---------------------------------------------

@given(assessments(), modules(), st.data())
@settings(max_examples=400)
def test_monotonicity_never_drops_recommendation(a: Assessment, m: dict, data):
    before = _included_ids(a, [m])
    assume(1 in before)  # only meaningful when the module was recommended

    covered = m["dimensions_covered"]
    # Pick a covered dimension we can push "toward more need": lower current or raise target.
    mutable = [
        d for d in covered
        if a.score_for(d).current > 1 or a.score_for(d).target < 5
    ]
    assume(mutable)
    dim = data.draw(st.sampled_from(mutable))

    new_scores = []
    for s in a.scores:
        if s.dimension == dim:
            can_lower = s.current > 1
            can_raise = s.target < 5
            lower = data.draw(st.booleans()) if (can_lower and can_raise) else can_lower
            if lower:
                new_scores.append(DimensionScore(s.dimension, s.current - 1, s.target, s.notes))
            else:
                new_scores.append(DimensionScore(s.dimension, s.current, s.target + 1, s.notes))
        else:
            new_scores.append(s)
    after = _included_ids(Assessment(a.client_name, new_scores), [m])
    assert 1 in after  # lowering current / raising target must never drop it
