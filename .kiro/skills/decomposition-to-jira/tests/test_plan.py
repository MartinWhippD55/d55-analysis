"""Unit + property tests for the decomposition-to-jira planner.

The planner is pure: given a decomposition folder it must produce a deterministic,
idempotent Jira plan. These tests assert the mapping conventions (epic/story/
sub-task/blocks), stable identity labels, valid label tokens and determinism.
"""
from __future__ import annotations

from pathlib import Path

import yaml
from hypothesis import given, settings
from hypothesis import strategies as st

from engine.plan import (
    BLOCKS_LINK_TYPE,
    build_plan,
    plan_to_dict,
    sanitize_label,
)


def _write_decomposition(root: Path, graph: dict, manifests: dict[str, dict]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    with open(root / "graph.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(graph, f, sort_keys=False)
    for sid, m in manifests.items():
        d = root / "stories" / sid
        d.mkdir(parents=True, exist_ok=True)
        with open(d / "manifest.yaml", "w", encoding="utf-8") as f:
            yaml.safe_dump(m, f, sort_keys=False)


def _sample(root: Path) -> None:
    graph = {
        "parentSpec": "demo-spec",
        "stories": ["US-01", "US-02"],
        "edges": [{"from": "US-02", "to": "US-01", "via": ["type:Foo"]}],
        "waves": [{"wave": 1, "stories": ["US-01"]}, {"wave": 2, "stories": ["US-02"]}],
    }
    manifests = {
        "US-01": {
            "id": "US-01",
            "title": "Foundation",
            "userStory": "As a dev I want a base.",
            "coversRequirements": ["1", "2"],
            "subtasks": [
                {"id": "US-01-1", "title": "Do thing", "requirements": ["1"], "optional": False},
                {"id": "US-01-2", "title": "Test thing", "requirements": ["2"], "optional": True},
            ],
            "jira": {"issueType": "Story", "labels": ["infra"], "estimateDays": 2.5},
        },
        "US-02": {
            "id": "US-02",
            "title": "Feature on top",
            "userStory": "As a dev I want a feature.",
            "coversRequirements": ["3"],
            "subtasks": [{"id": "US-02-1", "title": "Build feature", "requirements": ["3"]}],
            "jira": {"issueType": "Story", "labels": ["backend"]},
        },
    }
    _write_decomposition(root, graph, manifests)


def test_build_plan_maps_epic_stories_subtasks(tmp_path: Path):
    _sample(tmp_path)
    plan = build_plan(tmp_path)

    assert plan.parent_spec == "demo-spec"
    assert plan.set_label == "s2s-demo-spec"
    # epic
    assert plan.epic.epic_name == "demo-spec"
    assert plan.epic.identity_label == "s2s-demo-spec-epic"
    assert plan.set_label in plan.epic.labels
    # stories preserve graph order
    assert [s.sid for s in plan.stories] == ["US-01", "US-02"]
    us01 = plan.stories[0]
    assert us01.identity_label == "s2s-demo-spec-US-01"
    assert us01.estimate_days == 2.5
    assert "infra" in us01.labels
    assert [t.tid for t in us01.subtasks] == ["US-01-1", "US-01-2"]
    assert us01.subtasks[1].optional is True
    assert "optional" in us01.subtasks[1].labels


def test_blocks_link_direction(tmp_path: Path):
    """Edge from=US-02 to=US-01 means US-02 depends on US-01, so US-01 blocks US-02."""
    _sample(tmp_path)
    plan = build_plan(tmp_path)
    assert len(plan.links) == 1
    link = plan.links[0]
    assert link.link_type == BLOCKS_LINK_TYPE
    assert link.outward == "US-01"  # blocker (ships first)
    assert link.inward == "US-02"  # blocked


def test_identity_labels_unique_and_valid(tmp_path: Path):
    _sample(tmp_path)
    plan = build_plan(tmp_path)
    labels = [plan.epic.identity_label]
    for s in plan.stories:
        labels.append(s.identity_label)
        labels.extend(t.identity_label for t in s.subtasks)
    # unique
    assert len(labels) == len(set(labels))
    # no spaces, valid token
    for lab in labels:
        assert " " not in lab
        assert sanitize_label(lab) == lab


def test_description_has_traceability(tmp_path: Path):
    _sample(tmp_path)
    plan = build_plan(tmp_path)
    us01 = plan.stories[0]
    assert "Traceability: s2s-demo-spec-US-01" in us01.description
    assert "Covers parent requirements: 1, 2" in us01.description


def test_determinism(tmp_path: Path):
    _sample(tmp_path)
    a = plan_to_dict(build_plan(tmp_path))
    b = plan_to_dict(build_plan(tmp_path))
    assert a == b


@given(
    st.text(
        alphabet=st.characters(blacklist_categories=("Cs",)),
        min_size=1,
        max_size=40,
    )
)
@settings(max_examples=200)
def test_sanitize_label_never_has_spaces(text: str):
    out = sanitize_label(text)
    assert " " not in out
    # only the allowed token characters survive
    assert all(c.isalnum() or c in "._-" for c in out)


@given(st.integers(min_value=1, max_value=8))
@settings(max_examples=25)
def test_every_edge_becomes_one_link(n_extra_edges: int):
    """Property: the plan emits exactly one blocks-link per graph edge, with
    outward=dst (the dependency, ships first) and inward=src."""
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        stories = [f"US-{i:02d}" for i in range(1, n_extra_edges + 2)]
        edges = [
            {"from": stories[i + 1], "to": stories[0], "via": []}
            for i in range(n_extra_edges)
        ]
        graph = {"parentSpec": "p", "stories": stories, "edges": edges, "waves": []}
        manifests = {
            sid: {"id": sid, "title": sid, "userStory": "", "jira": {"issueType": "Story"}}
            for sid in stories
        }
        _write_decomposition(root, graph, manifests)
        plan = build_plan(root)
        assert len(plan.links) == len(edges)
        for link, e in zip(plan.links, edges):
            assert link.outward == e["to"]
            assert link.inward == e["from"]
