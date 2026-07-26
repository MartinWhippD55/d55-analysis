"""
Tests for the jira-push planner/reconciler.

The core (`build_push_plan`, `reconcile`, `validate_plan`, `summarize_plan`) is pure
and operates on duck-typed tree objects, so these tests build lightweight stand-ins
locally — no dependency on the jira-tree engine or on Jira.
"""
import os
import sys
from dataclasses import dataclass, field
from typing import Optional

from hypothesis import given
from hypothesis import strategies as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.push import (  # noqa: E402
    BLOCKS_LINK_TYPE,
    CREATE,
    DEFAULT_SPEC_FILES,
    EPIC,
    REUSE,
    SKIP,
    STORY,
    SUBTASK,
    attach_specs,
    build_key_map,
    build_push_plan,
    plan_description_updates,
    reconcile,
    render_placeholder_doc,
    substitute_keys,
    summarize_plan,
    validate_plan,
)


# --------------------------------------------------------------------------- #
# Lightweight tree stand-ins (mirror the jira-tree Tree model's attributes)
# --------------------------------------------------------------------------- #
@dataclass
class FSub:
    key: str
    summary: str
    identity_label: str
    labels: list = field(default_factory=list)
    issue_type: str = "Sub-task"
    description: str = ""


@dataclass
class FStory:
    key: str
    summary: str
    identity_label: str
    labels: list = field(default_factory=list)
    issue_type: str = "Story"
    description: str = ""
    estimate_days: Optional[float] = None
    subtasks: list = field(default_factory=list)


@dataclass
class FEpic:
    summary: str
    epic_name: str
    identity_label: str
    labels: list = field(default_factory=list)
    issue_type: str = "Epic"
    description: str = ""


@dataclass
class FLink:
    outward: str
    inward: str
    link_type: str = BLOCKS_LINK_TYPE


@dataclass
class FTree:
    parent_spec: str
    set_label: str
    epic: FEpic
    stories: list = field(default_factory=list)
    links: list = field(default_factory=list)


def sample_tree(n_stories: int = 3, subs_per_story: int = 2) -> FTree:
    parent = "demo-spec"
    setl = f"s2s-{parent}"
    epic = FEpic(
        summary=f"{parent} (delivery)",
        epic_name=parent,
        identity_label=f"{setl}-epic",
        labels=[setl, f"{setl}-epic"],
        description="epic body",
    )
    stories = []
    for i in range(1, n_stories + 1):
        sid = f"US-{i:02d}"
        subs = [
            FSub(
                key=f"{sid}-{j}",
                summary=f"{sid} sub {j}",
                identity_label=f"{setl}-{sid}-{j}",
                labels=[setl, f"{setl}-{sid}-{j}"],
                description=f"sub {sid}-{j} body",
            )
            for j in range(1, subs_per_story + 1)
        ]
        stories.append(
            FStory(
                key=sid,
                summary=f"Story {sid}",
                identity_label=f"{setl}-{sid}",
                labels=[setl, f"{setl}-{sid}"],
                description=f"story {sid} body",
                estimate_days=float(i),
                subtasks=subs,
            )
        )
    # chain dependencies: US-01 blocks US-02 blocks US-03 ...
    links = [
        FLink(outward=f"US-{i:02d}", inward=f"US-{i + 1:02d}")
        for i in range(1, n_stories)
    ]
    return FTree(parent_spec=parent, set_label=setl, epic=epic, stories=stories, links=links)


# --------------------------------------------------------------------------- #
# build_push_plan — mapping + ordering
# --------------------------------------------------------------------------- #
def test_plan_counts_match_tree():
    tree = sample_tree(3, 2)
    plan = build_push_plan(tree)
    kinds = [a.kind for a in plan.issues]
    assert kinds.count(EPIC) == 1
    assert kinds.count(STORY) == 3
    assert kinds.count(SUBTASK) == 6
    assert len(plan.links) == 2
    assert plan.parent_spec == "demo-spec"
    assert plan.set_label == "s2s-demo-spec"


def test_plan_ordering_epic_first_then_story_then_its_subtasks():
    tree = sample_tree(2, 2)
    plan = build_push_plan(tree)
    assert plan.issues[0].kind == EPIC
    # US-01 then its two subtasks, then US-02 then its two subtasks
    seq = [(a.kind, a.key) for a in plan.issues[1:]]
    assert seq == [
        (STORY, "US-01"),
        (SUBTASK, "US-01-1"),
        (SUBTASK, "US-01-2"),
        (STORY, "US-02"),
        (SUBTASK, "US-02-1"),
        (SUBTASK, "US-02-2"),
    ]


def test_story_parent_is_epic_and_subtask_parent_is_story():
    tree = sample_tree(2, 1)
    plan = build_push_plan(tree)
    epic = plan.issues[0]
    for a in plan.issues:
        if a.kind == STORY:
            assert a.parent_ref == epic.ref
        if a.kind == SUBTASK:
            assert a.parent_ref.startswith("s2s-demo-spec-US-")
            assert not a.parent_ref[-1].isdigit() or "-US-" in a.parent_ref
    # sub-task US-01-1's parent is story US-01's ref
    sub = next(a for a in plan.issues if a.kind == SUBTASK and a.key == "US-01-1")
    story = next(a for a in plan.issues if a.kind == STORY and a.key == "US-01")
    assert sub.parent_ref == story.ref


def test_link_direction_and_refs_preserved():
    tree = sample_tree(3, 1)
    plan = build_push_plan(tree)
    l = plan.links[0]
    assert (l.outward, l.inward) == ("US-01", "US-02")
    assert l.outward_ref == "s2s-demo-spec-US-01"
    assert l.inward_ref == "s2s-demo-spec-US-02"
    assert l.link_type == BLOCKS_LINK_TYPE


def test_all_actions_start_as_create():
    plan = build_push_plan(sample_tree(3, 2))
    assert all(a.op == CREATE for a in plan.issues)
    assert all(l.op == CREATE for l in plan.links)


def test_descriptions_and_estimates_carried_through():
    plan = build_push_plan(sample_tree(2, 1))
    story = next(a for a in plan.issues if a.kind == STORY and a.key == "US-01")
    assert story.description == "story US-01 body"
    assert story.estimate_days == 1.0
    sub = next(a for a in plan.issues if a.kind == SUBTASK and a.key == "US-01-1")
    assert sub.description == "sub US-01-1 body"


# --------------------------------------------------------------------------- #
# reconcile — idempotency
# --------------------------------------------------------------------------- #
def test_reconcile_empty_existing_is_all_create():
    plan = reconcile(build_push_plan(sample_tree(2, 2)))
    assert all(a.op == CREATE for a in plan.issues)
    assert all(l.op == CREATE for l in plan.links)


def test_reconcile_marks_existing_issues_reuse():
    plan = build_push_plan(sample_tree(2, 1))
    existing = {"s2s-demo-spec-epic", "s2s-demo-spec-US-01"}
    out = reconcile(plan, existing_labels=existing)
    by_ref = {a.ref: a.op for a in out.issues}
    assert by_ref["s2s-demo-spec-epic"] == REUSE
    assert by_ref["s2s-demo-spec-US-01"] == REUSE
    assert by_ref["s2s-demo-spec-US-02"] == CREATE  # not in existing


def test_reconcile_marks_existing_links_skip():
    plan = build_push_plan(sample_tree(3, 1))
    out = reconcile(plan, existing_links={("US-01", "US-02")})
    ops = {(l.outward, l.inward): l.op for l in out.links}
    assert ops[("US-01", "US-02")] == SKIP
    assert ops[("US-02", "US-03")] == CREATE


def test_reconcile_is_pure_does_not_mutate_input():
    plan = build_push_plan(sample_tree(2, 1))
    _ = reconcile(plan, existing_labels={"s2s-demo-spec-epic"})
    assert all(a.op == CREATE for a in plan.issues)  # original untouched


def test_full_reconcile_second_run_creates_nothing():
    """Simulate a completed first push: everything exists -> a re-run is all reuse/skip."""
    plan = build_push_plan(sample_tree(3, 2))
    all_labels = {a.ref for a in plan.issues}
    all_links = {(l.outward, l.inward) for l in plan.links}
    out = reconcile(plan, existing_labels=all_labels, existing_links=all_links)
    assert all(a.op == REUSE for a in out.issues)
    assert all(l.op == SKIP for l in out.links)


# --------------------------------------------------------------------------- #
# validate_plan
# --------------------------------------------------------------------------- #
def test_valid_plan_has_no_problems():
    assert validate_plan(build_push_plan(sample_tree(4, 3))) == []


def test_validate_detects_duplicate_ref():
    plan = build_push_plan(sample_tree(2, 1))
    plan.issues[2].ref = plan.issues[1].ref  # duplicate a ref
    problems = validate_plan(plan)
    assert any("duplicate identity ref" in p for p in problems)


def test_validate_detects_link_to_unknown_story():
    plan = build_push_plan(sample_tree(2, 1))
    plan.links[0].inward = "US-99"
    problems = validate_plan(plan)
    assert any("US-99" in p for p in problems)


def test_validate_detects_subtask_before_parent():
    plan = build_push_plan(sample_tree(1, 1))
    # swap story and its sub-task so the sub-task comes first
    plan.issues[1], plan.issues[2] = plan.issues[2], plan.issues[1]
    problems = validate_plan(plan)
    assert any("not created before it" in p for p in problems)


# --------------------------------------------------------------------------- #
# summarize
# --------------------------------------------------------------------------- #
def test_summary_reports_op_counts():
    plan = build_push_plan(sample_tree(2, 1))
    out = reconcile(plan, existing_labels={"s2s-demo-spec-epic"})
    s = summarize_plan(out)
    assert "1 epic" in s and "2 stories" in s
    assert "1 reuse" in s  # the epic was reused


# --------------------------------------------------------------------------- #
# attach_specs — opt-in mini-spec attachments (stories only)
# --------------------------------------------------------------------------- #
def _make_stories_dir(tmp_path, story_keys, files=DEFAULT_SPEC_FILES):
    """Create <tmp>/stories/<US-xx>/<file> for each key, return the stories dir."""
    stories = tmp_path / "stories"
    for k in story_keys:
        d = stories / k
        d.mkdir(parents=True)
        for f in files:
            (d / f).write_text(f"# {k} {f}", encoding="utf-8")
    return str(stories)


def test_attach_specs_adds_files_to_stories_only(tmp_path):
    plan = build_push_plan(sample_tree(2, 2))
    stories_dir = _make_stories_dir(tmp_path, ["US-01", "US-02"])
    out = attach_specs(plan, stories_dir)
    for a in out.issues:
        if a.kind == STORY:
            assert [x.filename for x in a.attachments] == list(DEFAULT_SPEC_FILES)
            assert all(x.op == CREATE for x in a.attachments)
        else:  # epic + sub-tasks never get attachments
            assert a.attachments == []


def test_attach_specs_skips_missing_files(tmp_path):
    plan = build_push_plan(sample_tree(1, 0))
    # only design.md present for US-01
    stories_dir = _make_stories_dir(tmp_path, ["US-01"], files=("design.md",))
    out = attach_specs(plan, stories_dir)
    story = next(a for a in out.issues if a.kind == STORY)
    assert [x.filename for x in story.attachments] == ["design.md"]


def test_attach_specs_does_not_mutate_input(tmp_path):
    plan = build_push_plan(sample_tree(1, 0))
    stories_dir = _make_stories_dir(tmp_path, ["US-01"])
    _ = attach_specs(plan, stories_dir)
    story = next(a for a in plan.issues if a.kind == STORY)
    assert story.attachments == []  # original untouched


def test_reconcile_marks_existing_attachments_skip(tmp_path):
    plan = build_push_plan(sample_tree(1, 0))
    stories_dir = _make_stories_dir(tmp_path, ["US-01"])
    plan = attach_specs(plan, stories_dir)
    # design.md already uploaded to US-01
    out = reconcile(plan, existing_attachments={"US-01": {"design.md"}})
    story = next(a for a in out.issues if a.kind == STORY)
    ops = {x.filename: x.op for x in story.attachments}
    assert ops["design.md"] == SKIP
    assert ops["requirements.md"] == CREATE
    assert ops["tasks.md"] == CREATE


def test_reconcile_without_attachment_arg_leaves_them_create(tmp_path):
    plan = build_push_plan(sample_tree(1, 0))
    stories_dir = _make_stories_dir(tmp_path, ["US-01"])
    plan = attach_specs(plan, stories_dir)
    out = reconcile(plan, existing_labels={"s2s-demo-spec-epic"})
    story = next(a for a in out.issues if a.kind == STORY)
    assert all(x.op == CREATE for x in story.attachments)


def test_summary_reports_attachment_counts(tmp_path):
    plan = build_push_plan(sample_tree(2, 0))
    stories_dir = _make_stories_dir(tmp_path, ["US-01", "US-02"])
    plan = attach_specs(plan, stories_dir)
    out = reconcile(plan, existing_attachments={"US-01": {"design.md"}})
    s = summarize_plan(out)
    assert "attachments:" in s
    assert "5 upload" in s and "1 skip" in s  # 6 total, 1 already present


def test_second_run_with_attachments_uploads_nothing(tmp_path):
    plan = build_push_plan(sample_tree(2, 1))
    stories_dir = _make_stories_dir(tmp_path, ["US-01", "US-02"])
    plan = attach_specs(plan, stories_dir)
    all_labels = {a.ref for a in plan.issues}
    all_links = {(l.outward, l.inward) for l in plan.links}
    existing_att = {"US-01": set(DEFAULT_SPEC_FILES), "US-02": set(DEFAULT_SPEC_FILES)}
    out = reconcile(plan, all_labels, all_links, existing_attachments=existing_att)
    assert all(a.op == REUSE for a in out.issues)
    assert all(l.op == SKIP for l in out.links)
    assert all(x.op == SKIP for a in out.issues for x in a.attachments)


# --------------------------------------------------------------------------- #
# build_key_map — identity label -> tree key
# --------------------------------------------------------------------------- #
def test_build_key_map_strips_set_label_prefix():
    existing = {
        "s2s-demo-spec-epic": "SQP-1",
        "s2s-demo-spec-US-01": "SQP-2",
        "s2s-demo-spec-US-01-1": "SQP-3",
    }
    km = build_key_map(existing, "s2s-demo-spec")
    assert km == {"epic": "SQP-1", "US-01": "SQP-2", "US-01-1": "SQP-3"}


def test_build_key_map_ignores_foreign_labels():
    existing = {"s2s-demo-spec-US-01": "SQP-2", "some-other-label": "SQP-9"}
    km = build_key_map(existing, "s2s-demo-spec")
    assert km == {"US-01": "SQP-2"}


# --------------------------------------------------------------------------- #
# substitute_keys — the core rewrite
# --------------------------------------------------------------------------- #
KM = {
    "epic": "SQP-1",
    "US-01": "SQP-10",
    "US-04": "SQP-40",
    "US-04-2": "SQP-42",
    "US-04-3": "SQP-43",
    "US-06": "SQP-60",
    "US-09": "SQP-90",
    "US-10": "SQP-100",
}


def test_substitute_plain_reference():
    assert substitute_keys("blocked by US-01 today", KM) == "blocked by SQP-10 today"


def test_substitute_reference_in_parentheses_and_slashes():
    assert substitute_keys("the frontend (US-09/US-10)", KM) == "the frontend (SQP-90/SQP-100)"


def test_substitute_longest_key_wins_over_prefix():
    # US-04-2 must map to SQP-42, not "SQP-40-2"
    assert substitute_keys("variant rules (US-04-3) attach", KM) == "variant rules (SQP-43) attach"
    assert substitute_keys("see US-04-2 for detail", KM) == "see SQP-42 for detail"


def test_substitute_leaves_identity_label_intact():
    # The Traceability footer prints the identity label; the leading hyphen guards it.
    body = "Covers 18 · `s2s-contract-note-template-management-US-04`"
    assert substitute_keys(body, KM) == body


def test_substitute_bare_story_key_still_rewritten_next_to_identity_label():
    body = "depends on US-04 · label s2s-demo-US-04"
    # the free-standing US-04 is rewritten; the labelled one is not
    assert substitute_keys(body, KM) == "depends on SQP-40 · label s2s-demo-US-04"


def test_substitute_does_not_touch_requirement_numbers():
    assert substitute_keys("parent 18.2 and 19.3", KM) == "parent 18.2 and 19.3"


def test_substitute_empty_map_is_identity():
    assert substitute_keys("US-01 and US-04-2", {}) == "US-01 and US-04-2"


def test_substitute_epic_token_is_never_used():
    # 'epic' is not a US-reference, so it is never matched even if present in text.
    assert substitute_keys("the epic body", KM) == "the epic body"


# --------------------------------------------------------------------------- #
# plan_description_updates — pairs substituted bodies with live keys
# --------------------------------------------------------------------------- #
def test_plan_description_updates_flags_changed_only_when_body_differs():
    tree = sample_tree(2, 1)
    # give US-01's body a reference to US-02; US-02's body has no cross-reference
    tree.stories[0].description = "This story is blocked-by US-02 downstream."
    tree.stories[1].description = "A self-contained story with no cross-references."
    plan = build_push_plan(tree)
    existing = {
        "s2s-demo-spec-epic": "SQP-1",
        "s2s-demo-spec-US-01": "SQP-2",
        "s2s-demo-spec-US-01-1": "SQP-3",
        "s2s-demo-spec-US-02": "SQP-4",
        "s2s-demo-spec-US-02-1": "SQP-5",
    }
    km = build_key_map(existing, "s2s-demo-spec")
    updates = plan_description_updates(plan, km, existing)
    by_key = {u.tree_key: u for u in updates}
    assert by_key["US-01"].description == "This story is blocked-by SQP-4 downstream."
    assert by_key["US-01"].changed is True
    assert by_key["US-01"].jira_key == "SQP-2"
    # a body with no cross-reference is unchanged
    assert by_key["US-02"].changed is False


def test_plan_description_updates_skips_unpushed_issues():
    plan = build_push_plan(sample_tree(2, 0))
    existing = {"s2s-demo-spec-epic": "SQP-1", "s2s-demo-spec-US-01": "SQP-2"}
    km = build_key_map(existing, "s2s-demo-spec")
    updates = plan_description_updates(plan, km, existing)
    # US-02 has no Jira key -> not in the update list
    assert {u.tree_key for u in updates} == {"demo-spec", "US-01"}


# --------------------------------------------------------------------------- #
# render_placeholder_doc — the _placeholders.md mirror
# --------------------------------------------------------------------------- #
def test_render_placeholder_doc_has_frontmatter_map_and_table():
    plan = build_push_plan(sample_tree(2, 1))
    existing = {
        "s2s-demo-spec-epic": "SQP-1",
        "s2s-demo-spec-US-01": "SQP-2",
        "s2s-demo-spec-US-01-1": "SQP-3",
        "s2s-demo-spec-US-02": "SQP-4",
        "s2s-demo-spec-US-02-1": "SQP-5",
    }
    doc = render_placeholder_doc(plan, existing, project_key="SQP")
    assert "project: SQP" in doc
    assert "set_label: s2s-demo-spec" in doc
    assert "US-01: SQP-2" in doc
    assert "US-01-1: SQP-3" in doc
    assert "| US-01 | SQP-2 | Story |" in doc
    assert "| US-01-1 | SQP-3 | Sub-task |" in doc


def test_render_placeholder_doc_marks_unpushed_with_dash():
    plan = build_push_plan(sample_tree(2, 0))
    existing = {"s2s-demo-spec-epic": "SQP-1", "s2s-demo-spec-US-01": "SQP-2"}
    doc = render_placeholder_doc(plan, existing)
    assert "| US-02 | — |" in doc


# --------------------------------------------------------------------------- #
# Property-based: plan is well-formed and reconcile is idempotent, any tree size
# --------------------------------------------------------------------------- #
@given(
    n_stories=st.integers(min_value=1, max_value=12),
    subs=st.integers(min_value=0, max_value=4),
)
def test_property_plan_always_valid_and_ordered(n_stories, subs):
    plan = build_push_plan(sample_tree(n_stories, subs))
    assert validate_plan(plan) == []
    # every sub-task's parent story appears earlier in the list
    seen: set[str] = set()
    for a in plan.issues:
        if a.kind == SUBTASK:
            assert a.parent_ref in seen
        seen.add(a.ref)


@given(
    story=st.integers(min_value=1, max_value=10),
    sub=st.integers(min_value=1, max_value=9),
)
def test_property_substitution_is_idempotent(story, sub):
    """Substituting an already-substituted body is a no-op: Jira keys (SQP-n) don't
    match the US-<n> token shape, so a second pass changes nothing."""
    km = {f"US-{story:02d}": "SQP-500", f"US-{story:02d}-{sub}": "SQP-600"}
    text = f"blocks US-{story:02d} and detail in (US-{story:02d}-{sub})."
    once = substitute_keys(text, km)
    assert substitute_keys(once, km) == once
    assert f"US-{story:02d}" not in once  # both references were rewritten


@given(parent=st.integers(min_value=1, max_value=99), n=st.integers(min_value=1, max_value=99))
def test_property_identity_label_suffix_never_rewritten(parent, n):
    """A US key appearing as the suffix of an identity label (…-US-04) is guarded by
    the preceding hyphen and must survive substitution verbatim."""
    key = f"US-{parent:02d}"
    km = {key: "SQP-999"}
    label = f"s2s-some-spec-{key}"
    assert substitute_keys(label, km) == label


@given(
    n_stories=st.integers(min_value=1, max_value=10),
    subs=st.integers(min_value=0, max_value=3),
)
def test_property_reconcile_twice_is_stable(n_stories, subs):
    plan = build_push_plan(sample_tree(n_stories, subs))
    labels = {a.ref for a in plan.issues}
    links = {(l.outward, l.inward) for l in plan.links}
    once = reconcile(plan, existing_labels=labels, existing_links=links)
    twice = reconcile(once, existing_labels=labels, existing_links=links)
    assert [a.op for a in once.issues] == [a.op for a in twice.issues]
    assert [l.op for l in once.links] == [l.op for l in twice.links]
    assert all(a.op == REUSE for a in twice.issues)
    assert all(l.op == SKIP for l in twice.links)
