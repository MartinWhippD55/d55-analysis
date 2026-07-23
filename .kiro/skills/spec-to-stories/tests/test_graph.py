"""
Tests for the spec-to-stories graph engine: unit tests for the worked cases and
property-based tests (hypothesis) for the correctness properties.

Correctness properties under test:
  P1  Every dependency resolves to exactly one exporting story (else an issue).
  P2  Topological order: for every edge src->dst, dst precedes src.
  P3  Wave integrity: no two stories in the same wave depend on each other, and
      wave(story) == 1 + max(wave(dep)).
  P4  Cycle detection: a graph with a cycle yields a `cycle` issue and no waves.
  P5  Determinism: same input -> identical edges, order and waves.
  P6  Coverage: uncovered parent requirements are reported.
"""
from __future__ import annotations

import string

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from engine.graph import (
    build_decomposition,
    detect_cycles,
    partition_waves,
    topological_order,
)
from engine.models import Component, Story


# --------------------------------------------------------------------------
# Helpers / strategies
# --------------------------------------------------------------------------

def make_story(sid: str, exports=(), depends=()):
    return Story(
        id=sid,
        title=f"Story {sid}",
        exports=[Component.parse(r) for r in exports],
        depends_on=[Component.parse(r) for r in depends],
    )


def dag_stories(draw):
    """Draw a random DAG of stories. Story i may only depend on components
    exported by stories j < i, guaranteeing acyclicity."""
    n = draw(st.integers(min_value=1, max_value=8))
    stories: list[Story] = []
    for i in range(n):
        sid = f"US-{i:02d}"
        exports = [f"type:C{i}"]  # each story exports one unique component
        deps: list[str] = []
        if i > 0:
            targets = draw(
                st.lists(st.integers(min_value=0, max_value=i - 1), unique=True, max_size=i)
            )
            deps = [f"type:C{j}" for j in targets]
        stories.append(make_story(sid, exports=exports, depends=deps))
    return stories


# --------------------------------------------------------------------------
# Unit tests - worked cases
# --------------------------------------------------------------------------

def test_linear_chain_orders_and_waves():
    stories = [
        make_story("US-01", exports=["data-table:T"]),
        make_story("US-02", exports=["api-endpoint:GET /t"], depends=["data-table:T"]),
        make_story("US-03", exports=["frontend-screen:List"], depends=["api-endpoint:GET /t"]),
    ]
    dec = build_decomposition("demo", stories)
    assert dec.ok
    assert [w for w in dec.waves] == [["US-01"], ["US-02"], ["US-03"]]
    order = topological_order([s.id for s in stories], dec.edges)
    assert order == ["US-01", "US-02", "US-03"]


def test_parallel_stories_share_a_wave():
    stories = [
        make_story("US-01", exports=["shared-lib:types"]),
        make_story("US-02", exports=["api-endpoint:a"], depends=["shared-lib:types"]),
        make_story("US-03", exports=["api-endpoint:b"], depends=["shared-lib:types"]),
    ]
    dec = build_decomposition("demo", stories)
    assert dec.ok
    assert dec.waves == [["US-01"], ["US-02", "US-03"]]


def test_dangling_dependency_is_flagged():
    stories = [make_story("US-01", exports=["api:x"], depends=["data-table:missing"])]
    dec = build_decomposition("demo", stories)
    assert not dec.ok
    assert any(i.kind == "dangling-dependency" for i in dec.issues)


def test_duplicate_exporter_is_flagged():
    stories = [
        make_story("US-01", exports=["data-table:T"]),
        make_story("US-02", exports=["data-table:T"]),
    ]
    dec = build_decomposition("demo", stories)
    assert not dec.ok
    assert any(i.kind == "duplicate-exporter" for i in dec.issues)


def test_cycle_is_detected_and_blocks():
    stories = [
        make_story("US-01", exports=["type:A"], depends=["type:B"]),
        make_story("US-02", exports=["type:B"], depends=["type:A"]),
    ]
    dec = build_decomposition("demo", stories)
    assert not dec.ok
    assert any(i.kind == "cycle" for i in dec.issues)
    assert dec.waves == []
    with pytest.raises(ValueError):
        topological_order([s.id for s in stories], dec.edges)


def test_self_dependency_flagged():
    stories = [make_story("US-01", exports=["type:A"], depends=["type:A"])]
    dec = build_decomposition("demo", stories)
    assert any(i.kind == "self-dependency" for i in dec.issues)


def test_uncovered_requirement_reported():
    stories = [make_story("US-01", exports=["type:A"])]
    stories[0].covers_requirements = ["1"]
    dec = build_decomposition("demo", stories, all_requirement_ids=["1", "2"])
    assert any(i.kind == "uncovered-requirement" and "2" in i.detail for i in dec.issues)
    # coverage is a warning, not a blocker
    assert dec.ok


# --------------------------------------------------------------------------
# Property-based tests
# --------------------------------------------------------------------------

@settings(max_examples=200)
@given(st.data())
def test_p2_topological_order_respects_edges(data):
    stories = dag_stories(data.draw)
    dec = build_decomposition("demo", stories)
    assert dec.ok
    order = topological_order([s.id for s in stories], dec.edges)
    pos = {sid: i for i, sid in enumerate(order)}
    for e in dec.edges:  # src depends on dst -> dst before src
        assert pos[e.dst] < pos[e.src]


@settings(max_examples=200)
@given(st.data())
def test_p3_wave_integrity(data):
    stories = dag_stories(data.draw)
    dec = build_decomposition("demo", stories)
    wave_of = {sid: w for w, members in enumerate(dec.waves, start=1) for sid in members}
    deps = {}
    for e in dec.edges:
        deps.setdefault(e.src, set()).add(e.dst)
    # no intra-wave dependency
    for e in dec.edges:
        assert wave_of[e.src] != wave_of[e.dst]
    # wave == 1 + max(dep waves)
    for sid, w in wave_of.items():
        expected = 1 + max((wave_of[d] for d in deps.get(sid, ())), default=0)
        assert w == expected


@settings(max_examples=200)
@given(st.data())
def test_p5_determinism(data):
    stories = dag_stories(data.draw)
    d1 = build_decomposition("demo", stories)
    d2 = build_decomposition("demo", stories)
    assert [(e.src, e.dst, e.via) for e in d1.edges] == [(e.src, e.dst, e.via) for e in d2.edges]
    assert d1.waves == d2.waves


@settings(max_examples=100)
@given(
    st.lists(
        st.text(alphabet=string.ascii_uppercase, min_size=1, max_size=3),
        min_size=2,
        max_size=6,
        unique=True,
    )
)
def test_p4_injected_cycle_detected(ids):
    # Build a ring: each exports Ci and depends on the next story's component.
    stories = []
    n = len(ids)
    for i, sid in enumerate(ids):
        nxt = (i + 1) % n
        stories.append(
            Story(
                id=sid,
                title=sid,
                exports=[Component.parse(f"type:C{i}")],
                depends_on=[Component.parse(f"type:C{nxt}")],
            )
        )
    dec = build_decomposition("demo", stories)
    cycles = detect_cycles([s.id for s in stories], dec.edges)
    assert cycles, "expected at least one cycle in a ring graph"
    assert not dec.ok
