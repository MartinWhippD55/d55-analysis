"""Unit + property tests for the jira-tree engine.

The engine is pure: it seeds a Tree from a jira-plan dict, renders it to markdown +
frontmatter, parses it back, and validates it. These tests assert the seed mapping,
render/parse round-trip, non-destructive writes, and internal-consistency checks.
"""
from __future__ import annotations

from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

from engine.tree import (
    BLOCKS_LINK_TYPE,
    PLACEHOLDER_MARKER,
    Link,
    Story,
    Subtask,
    Tree,
    build_tree_from_plan,
    find_placeholders,
    load_tree,
    sanitize_label,
    split_frontmatter,
    validate_tree,
    write_tree,
)


def _sample_plan() -> dict:
    return {
        "parent_spec": "demo-spec",
        "set_label": "s2s-demo-spec",
        "epic": {
            "summary": "demo-spec (delivery)",
            "epic_name": "demo-spec",
            "description": "Umbrella epic.",
            "identity_label": "s2s-demo-spec-epic",
            "labels": ["s2s-demo-spec", "s2s-demo-spec-epic"],
        },
        "stories": [
            {
                "sid": "US-01",
                "summary": "Foundation",
                "description": "As a dev I want a base.\n\nTraceability: s2s-demo-spec-US-01",
                "issue_type": "Story",
                "identity_label": "s2s-demo-spec-US-01",
                "labels": ["s2s-demo-spec", "s2s-demo-spec-US-01", "infra"],
                "covers_requirements": ["1", "2"],
                "estimate_days": 2.5,
                "subtasks": [
                    {
                        "tid": "US-01-1",
                        "summary": "Do thing",
                        "identity_label": "s2s-demo-spec-US-01-1",
                        "labels": ["s2s-demo-spec", "s2s-demo-spec-US-01-1"],
                        "requirements": ["1"],
                        "optional": False,
                    },
                    {
                        "tid": "US-01-2",
                        "summary": "Test thing",
                        "identity_label": "s2s-demo-spec-US-01-2",
                        "labels": ["s2s-demo-spec", "s2s-demo-spec-US-01-2", "optional"],
                        "requirements": ["2"],
                        "optional": True,
                    },
                ],
            },
            {
                "sid": "US-02",
                "summary": "Feature on top",
                "description": "As a dev I want a feature.\n\nTraceability: s2s-demo-spec-US-02",
                "issue_type": "Story",
                "identity_label": "s2s-demo-spec-US-02",
                "labels": ["s2s-demo-spec", "s2s-demo-spec-US-02", "backend"],
                "covers_requirements": ["3"],
                "estimate_days": 1.0,
                "subtasks": [
                    {
                        "tid": "US-02-1",
                        "summary": "Build feature",
                        "identity_label": "s2s-demo-spec-US-02-1",
                        "labels": ["s2s-demo-spec", "s2s-demo-spec-US-02-1"],
                        "requirements": ["3"],
                        "optional": False,
                    }
                ],
            },
        ],
        "links": [{"link_type": "Blocks", "outward": "US-01", "inward": "US-02"}],
        "waves": [["US-01"], ["US-02"]],
    }


def test_build_tree_from_plan_maps_hierarchy():
    tree = build_tree_from_plan(_sample_plan())
    assert tree.parent_spec == "demo-spec"
    assert tree.set_label == "s2s-demo-spec"
    assert tree.epic.identity_label == "s2s-demo-spec-epic"
    assert [s.key for s in tree.stories] == ["US-01", "US-02"]
    us01 = tree.stories[0]
    assert us01.estimate_days == 2.5
    assert us01.wave == 1
    assert us01.blocks == ["US-02"]  # US-01 blocks US-02
    assert us01.depends_on == []
    us02 = tree.stories[1]
    assert us02.wave == 2
    assert us02.depends_on == ["US-01"]
    assert [t.key for t in us01.subtasks] == ["US-01-1", "US-01-2"]
    assert us01.subtasks[1].optional is True


def test_seeded_tree_is_valid():
    tree = build_tree_from_plan(_sample_plan())
    assert validate_tree(tree) == []


def test_seeded_bodies_follow_templates():
    tree = build_tree_from_plan(_sample_plan())
    # epic: delivery plan + story index + DoD
    assert "## Delivery plan" in tree.epic.description
    assert "## Stories" in tree.epic.description
    assert "## Definition of done" in tree.epic.description
    # story: user story line + GWT acceptance criteria + resolved dependency name
    us01, us02 = tree.stories
    assert us01.description.startswith("As a dev I want a base.")
    assert "## Acceptance criteria" in us01.description
    assert "**Given**" in us01.description
    assert "None — foundation story." in us01.description  # US-01 has no deps
    assert "US-01 — Foundation" in us02.description  # US-02 depends on US-01, named
    # sub-task: greppable bullets + suggested-approach code fence
    sub = us01.subtasks[0]
    assert "- **What:** Do thing" in sub.description
    assert "### Suggested approach" in sub.description
    assert "```" in sub.description


def test_find_placeholders_flags_seeded_then_clears_when_enriched():
    tree = build_tree_from_plan(_sample_plan())
    # freshly seeded → every issue still has TODO placeholders
    owners = find_placeholders(tree)
    assert "epic" in owners
    assert "story US-01" in owners
    assert "sub-task US-01-1" in owners
    # enrich everything → no placeholders remain
    tree.epic.description = "Fully written epic."
    for s in tree.stories:
        s.description = "Fully written story."
        for t in s.subtasks:
            t.description = "Fully written sub-task."
    assert find_placeholders(tree) == []


def test_link_direction():
    tree = build_tree_from_plan(_sample_plan())
    assert len(tree.links) == 1
    link = tree.links[0]
    assert link.link_type == BLOCKS_LINK_TYPE
    assert link.outward == "US-01"  # ships first / blocks
    assert link.inward == "US-02"  # blocked


def test_write_then_load_roundtrip(tmp_path: Path):
    tree = build_tree_from_plan(_sample_plan())
    write_tree(tree, tmp_path)
    reloaded = load_tree(tmp_path)
    assert reloaded == tree


def test_write_is_non_destructive_by_default(tmp_path: Path):
    tree = build_tree_from_plan(_sample_plan())
    write_tree(tree, tmp_path)
    # hand-edit a description
    story_file = tmp_path / "US-01" / "story.md"
    edited = story_file.read_text(encoding="utf-8") + "\n\nHand-added note.\n"
    story_file.write_text(edited, encoding="utf-8")
    # re-render without overwrite: file must be untouched
    written = write_tree(tree, tmp_path)
    assert str(story_file) not in written
    assert "Hand-added note." in story_file.read_text(encoding="utf-8")
    # and the edit survives a reload
    reloaded = load_tree(tmp_path)
    assert "Hand-added note." in reloaded.stories[0].description


def test_edited_description_survives_roundtrip(tmp_path: Path):
    tree = build_tree_from_plan(_sample_plan())
    write_tree(tree, tmp_path)
    sub = tmp_path / "US-01" / "US-01-1.md"
    fm, body = split_frontmatter(sub.read_text(encoding="utf-8"))
    new_body = body + "\n\nExtra detail for the implementer."
    from engine.tree import _compose, _subtask_frontmatter  # internal reuse for the test

    # rewrite the file with an enriched body but identical frontmatter
    sub.write_text(
        _compose(
            {
                "issue_type": "Sub-task",
                "key": "US-01-1",
                "summary": "Do thing",
                "parent": "US-01",
                "identity_label": "s2s-demo-spec-US-01-1",
                "labels": ["s2s-demo-spec", "s2s-demo-spec-US-01-1"],
                "requirements": ["1"],
                "optional": False,
            },
            new_body,
        ),
        encoding="utf-8",
    )
    reloaded = load_tree(tmp_path)
    assert "Extra detail for the implementer." in reloaded.stories[0].subtasks[0].description


def test_validate_flags_unknown_link(tmp_path: Path):
    tree = build_tree_from_plan(_sample_plan())
    tree.links.append(Link(link_type="Blocks", outward="US-01", inward="US-99"))
    problems = validate_tree(tree)
    assert any("US-99" in p for p in problems)


def test_validate_flags_duplicate_identity_label():
    tree = build_tree_from_plan(_sample_plan())
    tree.stories[1].identity_label = tree.stories[0].identity_label
    problems = validate_tree(tree)
    assert any("duplicates" in p for p in problems)


def test_validate_flags_optional_label_mismatch():
    tree = build_tree_from_plan(_sample_plan())
    # mark optional True but without the 'optional' label
    tree.stories[0].subtasks[0].optional = True
    problems = validate_tree(tree)
    assert any("optional" in p for p in problems)


def test_validate_flags_links_blocks_disagreement():
    tree = build_tree_from_plan(_sample_plan())
    tree.stories[0].blocks = []  # remove the block that _links.md still has
    problems = validate_tree(tree)
    assert any("_links.md" in p for p in problems)


@given(
    st.text(alphabet=st.characters(blacklist_categories=("Cs",)), min_size=1, max_size=60)
)
@settings(max_examples=200)
def test_sanitize_label_never_has_spaces(text: str):
    out = sanitize_label(text)
    assert " " not in out
    assert all(c.isalnum() or c in "._-" for c in out)


@given(st.integers(min_value=1, max_value=6))
@settings(max_examples=25)
def test_roundtrip_scales_with_stories(n: int):
    """Property: a synthesised tree of N stories round-trips through write/load."""
    import tempfile

    stories = []
    links = []
    for i in range(1, n + 1):
        sid = f"US-{i:02d}"
        blocks = [f"US-{i+1:02d}"] if i < n else []
        depends = [f"US-{i-1:02d}"] if i > 1 else []
        stories.append(
            Story(
                key=sid,
                summary=f"Story {i}",
                identity_label=f"s2s-p-{sid}",
                parent_epic="p",
                labels=[f"s2s-p", f"s2s-p-{sid}"],
                covers_requirements=[str(i)],
                estimate_days=float(i),
                wave=i,
                depends_on=depends,
                blocks=blocks,
                description=f"Body for story {i}.",
                subtasks=[
                    Subtask(
                        key=f"{sid}-1",
                        summary=f"Task for {sid}",
                        identity_label=f"s2s-p-{sid}-1",
                        labels=[f"s2s-p", f"s2s-p-{sid}-1"],
                        requirements=[str(i)],
                        optional=False,
                        parent=sid,
                        description=f"Do the work for {sid}.",
                    )
                ],
            )
        )
        if blocks:
            links.append(Link(link_type="Blocks", outward=sid, inward=blocks[0]))

    from engine.tree import Epic

    tree = Tree(
        parent_spec="p",
        set_label="s2s-p",
        epic=Epic(
            summary="p (delivery)",
            epic_name="p",
            identity_label="s2s-p-epic",
            set_label="s2s-p",
            labels=["s2s-p", "s2s-p-epic"],
            description="Umbrella.",
        ),
        stories=stories,
        links=links,
    )
    assert validate_tree(tree) == []
    with tempfile.TemporaryDirectory() as td:
        write_tree(tree, td)
        assert load_tree(td) == tree
