"""Tests for per-module asset generation (Task 11, Property 12)."""
from __future__ import annotations

import pytest

from engine.layout import template_layout
from engine.module_assets import generate_module_assets, is_self_contained, slugify

MODULE = {
    "id": 1,
    "slug": "leadership",
    "title": "Leadership & the Investment Case",
    "manual_section": "1. Mandate & Measurement",
    "deliverables": [
        "Investment Case One-Pager",
        {"title": "Metrics Scorecard", "badge": "Template",
         "blocks": [{"type": "table", "heading": "Scorecard",
                     "columns": ["Metric", "Baseline", "Target"],
                     "rows": [["Cycle time", "TODO", "TODO"]]}]},
    ],
}


def test_slugify():
    assert slugify("Investment Case One-Pager!") == "investment-case-one-pager"


def test_is_self_contained():
    assert is_self_contained("<img src='data:image/png;base64,AAAA'>")
    assert not is_self_contained("<link href='https://fonts.googleapis.com/x'>")


def test_generates_html_per_deliverable_into_assets(tmp_path):
    layout = template_layout(tmp_path, "demo").create()
    paths = generate_module_assets(layout, MODULE, make_pdf=False)
    assets_dir = layout.module_assets_dir(1, "leadership")

    assert len(paths) == 2
    assert (assets_dir / "investment-case-one-pager.html").exists()
    assert (assets_dir / "metrics-scorecard.html").exists()
    # All output lives under the module's assets/ folder.
    for p in paths:
        assert p.parent == assets_dir


def test_generated_html_is_self_contained_and_base64(tmp_path):
    layout = template_layout(tmp_path, "demo").create()
    paths = generate_module_assets(layout, MODULE, make_pdf=False)
    for p in paths:
        html = p.read_text(encoding="utf-8")
        assert "data:image" in html          # brand assets embedded as base64
        assert is_self_contained(html)        # no CDN / external links (Property 12)


def test_structured_deliverable_uses_its_blocks(tmp_path):
    layout = template_layout(tmp_path, "demo").create()
    generate_module_assets(layout, MODULE, make_pdf=False)
    html = (layout.module_assets_dir(1, "leadership") / "metrics-scorecard.html").read_text("utf-8")
    assert "Cycle time" in html
    assert "Scorecard" in html


def test_no_deliverables_generates_nothing(tmp_path):
    layout = template_layout(tmp_path, "demo").create()
    assert generate_module_assets(layout, dict(MODULE, deliverables=[]), make_pdf=False) == []


@pytest.mark.pdf
def test_generates_matching_a4_pdf(tmp_path):
    """Renders a PDF and asserts A4. Skips gracefully if Chromium is unavailable."""
    playwright = pytest.importorskip("playwright")  # noqa: F841
    pypdf = pytest.importorskip("pypdf")
    layout = template_layout(tmp_path, "demo").create()
    single = dict(MODULE, deliverables=["Investment Case One-Pager"])
    paths = generate_module_assets(layout, single, make_pdf=True)
    pdf = paths[0].with_suffix(".pdf")
    if not pdf.exists():
        pytest.skip("Chromium not installed; PDF not rendered")
    reader = pypdf.PdfReader(str(pdf))
    box = reader.pages[0].mediabox
    w_mm = float(box.width) / 72 * 25.4
    h_mm = float(box.height) / 72 * 25.4
    assert abs(w_mm - 210) < 2 and abs(h_mm - 297) < 2
