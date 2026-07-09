"""Unit tests for manifest parsing and the join-key validator (Task 4, Property 1).

Builds small programme directories in ``tmp_path`` — a valid one plus deliberately
broken variants — and asserts ``validate_join_keys`` reports exactly the expected
violations, and nothing on the valid case.
"""
from __future__ import annotations

import textwrap
from pathlib import Path

import yaml

from engine.manifest import (
    JoinKeyError,
    dimension_names,
    load_toc_titles,
    parse_frontmatter,
    require_valid_join_keys,
    validate_join_keys,
)

# ---------------------------------------------------------------------------
# Fixture builders
# ---------------------------------------------------------------------------

DIMENSIONS = ["Leadership & Mandate", "Metrics & ROI", "Governance, Security & Compliance"]

TOC = textwrap.dedent(
    """\
    # Client Operating Manual — Table of Contents

    ## How the manual gets written
    some preamble

    ## 0. Where We Are & Where We're Going
    *from the assessment*

    ## 1. Mandate & Measurement
    *from Module 1*

    ## 3. Shipping Safely
    *from Module 3*
    """
)


def _manifest_yaml() -> str:
    return yaml.safe_dump(
        {
            "programme": {"slug": "demo", "name": "Demo Programme"},
            "dimensions": [{"name": d, "short": d.split()[0]} for d in DIMENSIONS],
            "modules": [],
        },
        sort_keys=False,
        allow_unicode=True,
    )


def _module_md(
    module_id: int,
    dimensions_covered: list[str],
    manual_section: str,
    critical_dimensions: list[str] | None = None,
) -> str:
    fm: dict = {
        "module_id": module_id,
        "title": f"Module {module_id}",
        "dimensions_covered": dimensions_covered,
        "trigger": {
            "recommend_when_current_at_or_below": 2,
            "include_when_gap_at_or_above": 2,
            "prioritise_when_gap_at_or_above": 2,
        },
        "audience": ["Someone"],
        "duration": "Half day",
        "format": "Workshop",
        "manual_section": manual_section,
        "sets_up_embed": True,
    }
    if critical_dimensions is not None:
        fm["trigger"]["critical_dimensions"] = critical_dimensions
        fm["trigger"]["critical_when_current_at_or_below"] = 2
    front = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True)
    return f"---\n{front}---\n\n# {fm['title']}\n\n## Objective\nDo the thing.\n"


def _write_programme(root: Path, modules: list[str]) -> Path:
    (root / "programme.yaml").write_text(_manifest_yaml(), encoding="utf-8")
    (root / "client-operating-manual-toc.md").write_text(TOC, encoding="utf-8")
    for i, md in enumerate(modules, start=1):
        mod_dir = root / "modules" / f"module-{i}-slug"
        mod_dir.mkdir(parents=True, exist_ok=True)
        (mod_dir / "module.md").write_text(md, encoding="utf-8")
    return root


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def test_parse_frontmatter_reads_fields(tmp_path: Path):
    root = _write_programme(
        tmp_path,
        [_module_md(1, ["Leadership & Mandate"], "1. Mandate & Measurement")],
    )
    fm = parse_frontmatter(root / "modules" / "module-1-slug" / "module.md")
    assert fm["module_id"] == 1
    assert fm["dimensions_covered"] == ["Leadership & Mandate"]
    assert fm["manual_section"] == "1. Mandate & Measurement"


def test_parse_frontmatter_missing_block_raises(tmp_path: Path):
    p = tmp_path / "no_fm.md"
    p.write_text("# Just a heading\n", encoding="utf-8")
    import pytest

    with pytest.raises(ValueError):
        parse_frontmatter(p)


def test_load_toc_titles_extracts_section_headings(tmp_path: Path):
    p = tmp_path / "toc.md"
    p.write_text(TOC, encoding="utf-8")
    titles = load_toc_titles(p)
    assert "1. Mandate & Measurement" in titles
    assert "3. Shipping Safely" in titles
    # H1 is not a section title.
    assert "Client Operating Manual — Table of Contents" not in titles


def test_dimension_names_from_manifest():
    manifest = yaml.safe_load(_manifest_yaml())
    assert dimension_names(manifest) == DIMENSIONS


# ---------------------------------------------------------------------------
# Valid case → no violations (Property 1)
# ---------------------------------------------------------------------------

def test_valid_programme_has_no_violations(tmp_path: Path):
    root = _write_programme(
        tmp_path,
        [
            _module_md(1, ["Leadership & Mandate", "Metrics & ROI"], "1. Mandate & Measurement"),
            _module_md(
                2,
                ["Governance, Security & Compliance"],
                "3. Shipping Safely",
                critical_dimensions=["Governance, Security & Compliance"],
            ),
        ],
    )
    assert validate_join_keys(root) == []
    # Hard-stop helper must not raise on a clean programme.
    require_valid_join_keys(root)


# ---------------------------------------------------------------------------
# Broken cases → the specific violation, and nothing spurious
# ---------------------------------------------------------------------------

def test_unknown_dimension_detected(tmp_path: Path):
    root = _write_programme(
        tmp_path,
        [_module_md(1, ["Not A Real Dimension"], "1. Mandate & Measurement")],
    )
    violations = validate_join_keys(root)
    kinds = [(v.kind, v.value) for v in violations]
    assert ("unknown_dimension", "Not A Real Dimension") in kinds
    assert all(v.kind != "unknown_manual_section" for v in violations)


def test_unknown_manual_section_detected(tmp_path: Path):
    root = _write_programme(
        tmp_path,
        [_module_md(1, ["Leadership & Mandate"], "99. Nonexistent Section")],
    )
    violations = validate_join_keys(root)
    assert [(v.kind, v.value) for v in violations] == [
        ("unknown_manual_section", "99. Nonexistent Section")
    ]


def test_critical_not_covered_detected(tmp_path: Path):
    # critical_dimensions names a dimension the module does not cover.
    root = _write_programme(
        tmp_path,
        [
            _module_md(
                1,
                ["Leadership & Mandate"],
                "1. Mandate & Measurement",
                critical_dimensions=["Governance, Security & Compliance"],
            )
        ],
    )
    violations = validate_join_keys(root)
    assert ("critical_not_covered", "Governance, Security & Compliance") in [
        (v.kind, v.value) for v in violations
    ]


def test_require_valid_join_keys_raises_on_broken(tmp_path: Path):
    root = _write_programme(
        tmp_path,
        [_module_md(1, ["Bad Dimension"], "1. Mandate & Measurement")],
    )
    import pytest

    with pytest.raises(JoinKeyError) as exc:
        require_valid_join_keys(root)
    assert exc.value.violations  # carries the violation list for routing back
