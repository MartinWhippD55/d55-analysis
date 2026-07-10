"""Tests for the interactive questionnaire generator (Task 13, Properties 6 & 12)."""
from __future__ import annotations

import json
import random

import pytest

from engine.layout import template_layout
from engine.models import Assessment, DimensionScore
from engine.module_assets import is_self_contained
from engine.questionnaire import generate_questionnaire
from engine.recommend import recommend_modules
from engine.scaffold import scaffold_programme

DIMENSIONS = [
    {"name": "Leadership & Mandate", "short": "Leadership"},
    {"name": "Metrics & ROI", "short": "Metrics"},
    {"name": "Testing & Quality Assurance", "short": "Testing"},
    {"name": "Governance, Security & Compliance", "short": "Governance"},
]

MANUAL_SECTIONS = ["1. Mandate & Measurement", "3. Shipping Safely"]

MODULES = [
    {"id": 1, "slug": "leadership", "title": "Leadership & the Investment Case",
     "dimensions_covered": ["Leadership & Mandate", "Metrics & ROI"],
     "manual_section": "1. Mandate & Measurement",
     "trigger": {"recommend_when_current_at_or_below": 2, "include_when_gap_at_or_above": 2,
                 "prioritise_when_gap_at_or_above": 2}},
    {"id": 3, "slug": "shipping-safely", "title": "Shipping Safely",
     "dimensions_covered": ["Testing & Quality Assurance", "Governance, Security & Compliance"],
     "manual_section": "3. Shipping Safely",
     "trigger": {"recommend_when_current_at_or_below": 3, "include_when_gap_at_or_above": 2,
                 "prioritise_when_gap_at_or_above": 2,
                 "critical_dimensions": ["Governance, Security & Compliance"],
                 "critical_when_current_at_or_below": 2}},
]

ALL_DIMS = [d["name"] for d in DIMENSIONS]


def _programme(tmp_path):
    layout = template_layout(tmp_path, "demo")
    scaffold_programme(layout, name="Demo Programme", slug="demo", one_liner="Assess to scale.",
                       dimensions=DIMENSIONS, modules=MODULES, manual_sections=MANUAL_SECTIONS)
    return layout


# ---------------------------------------------------------------------------
# Generation + self-containment (Property 12)
# ---------------------------------------------------------------------------

def test_questionnaire_written_under_client_and_self_contained(tmp_path):
    layout = _programme(tmp_path)
    out = generate_questionnaire(layout)
    assert out.parent == layout.client_dir
    assert out.name == "workshop.html"
    html = out.read_text(encoding="utf-8")
    assert "data:image" in html                    # logo embedded as base64
    assert is_self_contained(html)                 # no CDN / external links
    assert "cdn.jsdelivr" not in html              # no Chart.js CDN (unlike the reference)


def test_questionnaire_embeds_manifest_dimensions_and_modules(tmp_path):
    layout = _programme(tmp_path)
    html = generate_questionnaire(layout).read_text(encoding="utf-8")
    # Dimension names embedded exactly (join key), and module triggers present.
    for d in ALL_DIMS:
        assert d in html
    assert "critical_when_current_at_or_below" in html


# ---------------------------------------------------------------------------
# Parity: client-side JS == build-time Python (Property 6)
# ---------------------------------------------------------------------------

def _score_vectors():
    """Deterministic edge cases plus a seeded random spread."""
    vectors = [
        {"Leadership & Mandate": (1, 5), "Metrics & ROI": (1, 5),
         "Testing & Quality Assurance": (1, 5), "Governance, Security & Compliance": (1, 5)},
        {"Leadership & Mandate": (5, 5), "Metrics & ROI": (5, 5),
         "Testing & Quality Assurance": (5, 5), "Governance, Security & Compliance": (5, 5)},
        {"Leadership & Mandate": (3, 5), "Metrics & ROI": (4, 4),
         "Testing & Quality Assurance": (4, 4), "Governance, Security & Compliance": (1, 4)},  # crit gate
        {"Leadership & Mandate": (4, 4), "Metrics & ROI": (2, 3),
         "Testing & Quality Assurance": (4, 5), "Governance, Security & Compliance": (4, 4)},
    ]
    rng = random.Random(42)
    for _ in range(30):
        vectors.append({d: (rng.randint(1, 5), rng.randint(1, 5)) for d in ALL_DIMS})
    return vectors


def _py_recommend(vector):
    a = Assessment(None, [DimensionScore(d, c, t) for d, (c, t) in vector.items()])
    return {(r.module_id, r.status) for r in recommend_modules(a, MODULES)}


@pytest.mark.browser
def test_client_side_matches_build_time_recommendation(tmp_path):
    """For identical scores, the embedded JS recommendation matches recommend_modules."""
    sync_api = pytest.importorskip("playwright.sync_api")
    layout = _programme(tmp_path)
    out = generate_questionnaire(layout)

    try:
        with sync_api.sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(out.resolve().as_uri(), wait_until="load")

            for vector in _score_vectors():
                assessment = {"scores": [{"dimension": d, "current": c, "target": t}
                                         for d, (c, t) in vector.items()]}
                js = page.evaluate("(a) => window.recommendModules(a, window.MODULES)", assessment)
                js_set = {(r["module_id"], r["status"]) for r in js}
                assert js_set == _py_recommend(vector), f"parity mismatch for {vector}"

            browser.close()
    except sync_api.Error as exc:
        pytest.skip(f"Chromium unavailable: {exc}")
