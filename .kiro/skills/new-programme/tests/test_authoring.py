"""Tests for the dimensions and module authoring steps (Task 10)."""
from __future__ import annotations

from engine.authoring import author_dimensions, author_module, author_modules
from engine.layout import template_layout
from engine.manifest import parse_frontmatter, validate_join_keys
from engine.models import Assessment, DimensionScore
from engine.scaffold import scaffold_programme

DIMENSIONS = [
    {"name": "Leadership & Mandate", "short": "Leadership"},
    {"name": "Metrics & ROI", "short": "Metrics"},
    {"name": "Governance, Security & Compliance", "short": "Governance"},
]

MANUAL_SECTIONS = ["1. Mandate & Measurement", "2. Metrics", "3. Shipping Safely"]

MODULES = [
    {
        "id": 1, "slug": "leadership", "title": "Leadership & the Investment Case",
        "dimensions_covered": ["Leadership & Mandate", "Metrics & ROI"],
        "manual_section": "1. Mandate & Measurement",
        "trigger": {"recommend_when_current_at_or_below": 2, "include_when_gap_at_or_above": 2,
                    "prioritise_when_gap_at_or_above": 2},
    },
    {
        "id": 3, "slug": "shipping-safely", "title": "Shipping Safely",
        "dimensions_covered": ["Governance, Security & Compliance"],
        "manual_section": "3. Shipping Safely",
        "trigger": {"recommend_when_current_at_or_below": 3, "include_when_gap_at_or_above": 2,
                    "prioritise_when_gap_at_or_above": 2,
                    "critical_dimensions": ["Governance, Security & Compliance"],
                    "critical_when_current_at_or_below": 2},
    },
]


def _scaffolded(tmp_path):
    layout = template_layout(tmp_path, "demo")
    scaffold_programme(layout, name="Demo", slug="demo", dimensions=DIMENSIONS,
                       modules=MODULES, manual_sections=MANUAL_SECTIONS)
    return layout


# ---------------------------------------------------------------------------
# 10.1 — dimensions authoring
# ---------------------------------------------------------------------------

RICH_DIMS = [
    {
        "name": "Leadership & Mandate",
        "what": "Is there executive sponsorship for AI-assisted development?",
        "levels": [
            {"score": 1, "level": "Absent", "description": "No leadership acknowledgement."},
            {"score": 2, "level": "Aware", "description": "Leadership knows; no position."},
            {"score": 3, "level": "Endorsed", "description": "Sponsor + budget."},
            {"score": 4, "level": "Mandated", "description": "Expected way of working."},
            {"score": 5, "level": "Strategic", "description": "Board-level advantage."},
        ],
        "calibration": ["Level 2: a few devs use Copilot on personal accounts."],
        "must_ask": ["Who sponsors AI tooling?", "Optional, encouraged, or mandated?"],
        "go_deeper": ["Who fights for the budget if cut?"],
    },
    {"name": "Metrics & ROI", "what": "Is value measured?"},
    {"name": "Governance, Security & Compliance", "what": "Are guardrails in place?"},
]


def test_author_dimensions_writes_full_rubric(tmp_path):
    layout = _scaffolded(tmp_path)
    violations = author_dimensions(layout, RICH_DIMS)
    assert violations == []
    text = layout.dimensions_md.read_text(encoding="utf-8")
    assert "## Leadership & Mandate" in text
    assert "| 4 | Mandated | Expected way of working. |" in text
    assert "\u2605 Must-ask" in text
    assert "Who sponsors AI tooling?" in text


def test_author_dimensions_flags_join_key_mismatch(tmp_path):
    layout = _scaffolded(tmp_path)
    # Author a dimension not present in the manifest, and omit a manifest one.
    bad = [{"name": "Totally New Dimension", "what": "x"},
           {"name": "Metrics & ROI"}, {"name": "Governance, Security & Compliance"}]
    violations = author_dimensions(layout, bad)
    kinds = {(v.kind, v.value) for v in violations}
    assert ("unknown_dimension", "Totally New Dimension") in kinds
    assert ("unscored_dimension", "Leadership & Mandate") in kinds


# ---------------------------------------------------------------------------
# 10.2 — module authoring
# ---------------------------------------------------------------------------

def test_author_module_writes_schema_conformant_content(tmp_path):
    layout = _scaffolded(tmp_path)
    module = dict(MODULES[0], objective="Turn AI into a sponsored initiative.",
                  deliverables=["Investment case", "Metrics scorecard"],
                  session_flow=["Frame the mandate", "Build the case"])
    author_module(layout, module)
    md = layout.module_dir(1, "leadership") / "module.md"
    fm = parse_frontmatter(md)
    assert fm["module_id"] == 1
    assert fm["dimensions_covered"] == ["Leadership & Mandate", "Metrics & ROI"]
    body = md.read_text(encoding="utf-8")
    assert "Turn AI into a sponsored initiative." in body
    assert "1. Frame the mandate" in body
    assert "- Investment case" in body


def test_author_modules_template_mode_authors_all(tmp_path):
    layout = _scaffolded(tmp_path)
    authored, violations = author_modules(layout, MODULES)   # no assessment
    assert set(authored) == {1, 3}
    assert violations == []


def test_author_modules_client_instance_only_authors_recommended(tmp_path):
    layout = _scaffolded(tmp_path)
    # Governance weak (critical gate) -> module 3 in scope; leadership/metrics strong -> module 1 out.
    assessment = Assessment(
        client_name="Acme",
        scores=[
            DimensionScore("Leadership & Mandate", 5, 5),
            DimensionScore("Metrics & ROI", 5, 5),
            DimensionScore("Governance, Security & Compliance", 1, 4),
        ],
    )
    authored, violations = author_modules(layout, MODULES, assessment=assessment)
    assert authored == [3]                                  # only the recommended module
    assert violations == []
    # Module 1 was NOT authored with client content (still the scaffold skeleton).
    m1 = (layout.module_dir(1, "leadership") / "module.md").read_text(encoding="utf-8")
    assert "TODO" in m1
