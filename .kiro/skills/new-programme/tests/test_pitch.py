"""Tests for the elevator-pitch generator (Task 14)."""
from __future__ import annotations

from engine.layout import template_layout
from engine.module_assets import is_self_contained
from engine.models import Assessment, DimensionScore
from engine.pitch import generate_pitch
from engine.scaffold import scaffold_programme

DIMENSIONS = [
    {"name": "Leadership & Mandate", "short": "Leadership"},
    {"name": "Governance, Security & Compliance", "short": "Governance"},
]
MANUAL_SECTIONS = ["1. Mandate & Measurement", "3. Shipping Safely"]
MODULES = [
    {"id": 1, "slug": "leadership", "title": "Leadership & the Investment Case",
     "dimensions_covered": ["Leadership & Mandate"], "manual_section": "1. Mandate & Measurement",
     "trigger": {"recommend_when_current_at_or_below": 2, "include_when_gap_at_or_above": 2,
                 "prioritise_when_gap_at_or_above": 2}},
    {"id": 3, "slug": "shipping-safely", "title": "Shipping Safely",
     "dimensions_covered": ["Governance, Security & Compliance"], "manual_section": "3. Shipping Safely",
     "trigger": {"recommend_when_current_at_or_below": 3, "include_when_gap_at_or_above": 2,
                 "prioritise_when_gap_at_or_above": 2,
                 "critical_dimensions": ["Governance, Security & Compliance"],
                 "critical_when_current_at_or_below": 2}},
]


def _programme(tmp_path):
    layout = template_layout(tmp_path, "demo")
    scaffold_programme(layout, name="Demo Programme", slug="demo",
                       one_liner="Assess to scale. We leave, you keep the capability.",
                       dimensions=DIMENSIONS, modules=MODULES, manual_sections=MANUAL_SECTIONS)
    return layout


def test_pitch_written_under_client_and_self_contained(tmp_path):
    layout = _programme(tmp_path)
    out = generate_pitch(layout)
    assert out.parent == layout.client_dir
    assert out.name == "elevator-pitch.html"
    html = out.read_text(encoding="utf-8")
    assert "data:image" in html                 # logo + background embedded
    assert is_self_contained(html)              # no CDN / external links
    assert "fonts.googleapis" not in html       # dropped the reference's CDN font


def test_template_mode_has_core_slides_not_gap(tmp_path):
    layout = _programme(tmp_path)
    html = generate_pitch(layout).read_text(encoding="utf-8")
    assert "Demo Programme" in html
    assert "The 2-minute version" in html
    assert "How the programme runs" in html
    assert "Your next step" in html
    assert "Assess" in html and "Scale" in html   # stage path
    # No client gap slide in template mode.
    assert "Where" not in html or "today" not in html


def test_client_instance_mode_adds_tailored_gap_slide(tmp_path):
    layout = _programme(tmp_path)
    assessment = Assessment(
        client_name="Acme",
        scores=[
            DimensionScore("Leadership & Mandate", 4, 4),
            DimensionScore("Governance, Security & Compliance", 1, 4),  # big gap + critical
        ],
    )
    html = generate_pitch(layout, assessment=assessment).read_text(encoding="utf-8")
    assert "Where Acme is today" in html
    assert "Governance, Security &amp; Compliance" in html or "Governance, Security & Compliance" in html
    assert "Shipping Safely" in html            # recommended module surfaced
    assert "critical" in html


def test_content_overrides(tmp_path):
    layout = _programme(tmp_path)
    html = generate_pitch(layout, content={
        "narrative": "Custom <strong>narrative</strong>.",
        "value_points": ["Point A", "Point B"],
    }).read_text(encoding="utf-8")
    assert "Custom <strong>narrative</strong>." in html
    assert "Point A" in html and "Point B" in html


def test_slides_are_numbered(tmp_path):
    layout = _programme(tmp_path)
    html = generate_pitch(layout).read_text(encoding="utf-8")
    # Template mode: 5 slides (title, narrative, pipeline, value, next step).
    assert html.count('class="slide-number"') == 5
    assert "5 / 5" in html
