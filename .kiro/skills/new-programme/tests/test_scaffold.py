"""Tests for the templates and scaffolding step (Task 9)."""
from __future__ import annotations

import yaml

from engine.layout import template_layout
from engine.manifest import load_manifest, parse_frontmatter, load_toc_titles, validate_join_keys
from engine.scaffold import render_template, scaffold_programme

DIMENSIONS = [
    {"name": "Leadership & Mandate", "short": "Leadership", "what": "Is there exec sponsorship?"},
    {"name": "Metrics & ROI", "short": "Metrics"},
    {"name": "Governance, Security & Compliance", "short": "Governance"},
]

MANUAL_SECTIONS = [
    "0. Where We Are & Where We're Going",
    "1. Mandate & Measurement",
    "3. Shipping Safely",
]

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


def _scaffold(tmp_path, modules=MODULES, sections=MANUAL_SECTIONS):
    layout = template_layout(tmp_path, "demo")
    violations = scaffold_programme(
        layout, name="Demo Programme", slug="demo", one_liner="Assess to scale.",
        dimensions=DIMENSIONS, modules=modules, manual_sections=sections,
    )
    return layout, violations


# ---------------------------------------------------------------------------
# render_template
# ---------------------------------------------------------------------------

def test_render_template_substitutes_tokens():
    out = render_template("client-operating-manual-toc.md.tmpl",
                          programme_name="Demo", sections="## 1. X")
    assert "Demo — Client Operating Manual" in out
    assert "## 1. X" in out
    assert "{{" not in out  # all tokens in this template were provided


def test_all_four_templates_exist_and_render():
    for name in ("programme.yaml.tmpl", "dimensions.md.tmpl",
                 "module.md.tmpl", "client-operating-manual-toc.md.tmpl"):
        # render with no context returns the raw skeleton (tokens left intact).
        text = render_template(name)
        assert text.strip()


def test_programme_yaml_tmpl_is_valid_yaml_when_filled():
    filled = render_template("programme.yaml.tmpl", slug="demo", name="Demo",
                             one_liner="x", brand_primary="#111111")
    data = yaml.safe_load(filled)
    assert data["programme"]["slug"] == "demo"
    assert "dimensions" in data and "modules" in data


# ---------------------------------------------------------------------------
# scaffold_programme — happy path
# ---------------------------------------------------------------------------

def test_scaffold_creates_all_artefacts_and_validates_clean(tmp_path):
    layout, violations = _scaffold(tmp_path)
    assert violations == []                       # join keys hold by construction

    assert layout.manifest.exists()
    assert layout.dimensions_md.exists()
    assert layout.toc_md.exists()
    assert layout.context_md.exists()
    assert layout.working_assumptions_md.exists()
    for m in MODULES:
        mod = layout.module_dir(m["id"], m["slug"])
        assert (mod / "module.md").exists()
        assert (mod / "assets").is_dir()


def test_scaffolded_manifest_and_frontmatter_are_consistent(tmp_path):
    layout, _ = _scaffold(tmp_path)
    manifest = load_manifest(layout.root)
    assert [d["name"] for d in manifest["dimensions"]] == [d["name"] for d in DIMENSIONS]

    fm = parse_frontmatter(layout.module_dir(3, "shipping-safely") / "module.md")
    assert fm["module_id"] == 3
    assert fm["manual_section"] == "3. Shipping Safely"
    assert fm["trigger"]["critical_dimensions"] == ["Governance, Security & Compliance"]


def test_scaffolded_toc_contains_module_sections(tmp_path):
    layout, _ = _scaffold(tmp_path)
    titles = load_toc_titles(layout.toc_md)
    for m in MODULES:
        assert m["manual_section"] in titles


# ---------------------------------------------------------------------------
# scaffold_programme — drift is caught (hard stop)
# ---------------------------------------------------------------------------

def test_scaffold_reports_unknown_manual_section(tmp_path):
    bad = [dict(MODULES[0], manual_section="99. Missing Section")]
    _, violations = _scaffold(tmp_path, modules=bad)
    assert any(v.kind == "unknown_manual_section" for v in violations)


def test_scaffold_reports_unknown_dimension(tmp_path):
    bad = [dict(MODULES[0], dimensions_covered=["Not A Dimension"])]
    _, violations = _scaffold(tmp_path, modules=bad)
    assert any(v.kind == "unknown_dimension" for v in violations)
