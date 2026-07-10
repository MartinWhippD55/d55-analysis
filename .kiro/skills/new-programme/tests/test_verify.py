"""Tests for the output verification harness (Task 15)."""
from __future__ import annotations

import urllib.request

import pytest

from engine.layout import template_layout
from engine.manifest import write_manifest
from engine.module_assets import generate_module_assets
from engine.spreadsheets import generate_delivery_playbook, generate_questionnaire_spreadsheet
from engine.verify import serve_directory, verify_html, verify_pdf, verify_xlsx

MODULE = {
    "id": 1, "slug": "leadership", "title": "Leadership", "manual_section": "1. Mandate",
    "deliverables": ["Investment Case One-Pager"],
}


def _manifest(tmp_path):
    layout = template_layout(tmp_path, "demo").create()
    write_manifest({"programme": {"slug": "demo", "name": "Demo"},
                    "dimensions": [{"name": "Leadership & Mandate"}], "modules": []}, layout.root)
    return layout


# ---------------------------------------------------------------------------
# serve_directory (cleanup)
# ---------------------------------------------------------------------------

def test_serve_directory_serves_and_shuts_down(tmp_path):
    (tmp_path / "hello.txt").write_text("hi there", encoding="utf-8")
    with serve_directory(tmp_path) as base:
        with urllib.request.urlopen(f"{base}/hello.txt", timeout=5) as resp:
            assert resp.status == 200
            assert resp.read().decode() == "hi there"
    # After exit the server is down: a new connection should fail quickly.
    with pytest.raises(Exception):
        urllib.request.urlopen(f"{base}/hello.txt", timeout=1)


# ---------------------------------------------------------------------------
# HTML verification (browser)
# ---------------------------------------------------------------------------

@pytest.mark.browser
def test_verify_html_passes_for_self_contained_asset(tmp_path):
    pytest.importorskip("playwright.sync_api")
    layout = template_layout(tmp_path, "demo").create()
    paths = generate_module_assets(layout, MODULE, make_pdf=False)
    try:
        report = verify_html(paths[0], expect_selectors={"section.block": 3})
    except Exception as exc:  # pragma: no cover
        pytest.skip(f"Chromium unavailable: {exc}")
    assert report.ok, report.issues
    assert report.metrics["images"]["loaded"] == report.metrics["images"]["total"]
    assert report.metrics["horizontal_overflow"] is False


@pytest.mark.browser
def test_verify_html_flags_overflow_and_missing_image(tmp_path):
    pytest.importorskip("playwright.sync_api")
    bad = tmp_path / "bad.html"
    bad.write_text(
        "<html><body><div style='width:4000px'>wide</div>"
        "<img src='data:image/png;base64,not-valid'></body></html>",
        encoding="utf-8",
    )
    try:
        report = verify_html(bad, require_images=True)
    except Exception as exc:  # pragma: no cover
        pytest.skip(f"Chromium unavailable: {exc}")
    assert not report.ok
    kinds = {i.kind for i in report.issues}
    assert "horizontal_overflow" in kinds
    assert "images_not_loaded" in kinds


@pytest.mark.browser
def test_verify_html_flags_selector_shortfall(tmp_path):
    pytest.importorskip("playwright.sync_api")
    layout = template_layout(tmp_path, "demo").create()
    paths = generate_module_assets(layout, MODULE, make_pdf=False)
    try:
        report = verify_html(paths[0], expect_selectors={"section.block": 99})
    except Exception as exc:  # pragma: no cover
        pytest.skip(f"Chromium unavailable: {exc}")
    assert not report.ok
    assert any(i.kind == "selector_count" for i in report.issues)


# ---------------------------------------------------------------------------
# PDF verification
# ---------------------------------------------------------------------------

@pytest.mark.pdf
def test_verify_pdf_checks_a4_and_pages(tmp_path):
    pytest.importorskip("playwright.sync_api")
    pytest.importorskip("pypdf")
    layout = template_layout(tmp_path, "demo").create()
    paths = generate_module_assets(layout, MODULE, make_pdf=True)
    pdf = paths[0].with_suffix(".pdf")
    if not pdf.exists():
        pytest.skip("Chromium not installed; PDF not rendered")
    report = verify_pdf(pdf)
    assert report.ok, report.issues
    assert report.metrics["page_size_mm"][0] == pytest.approx(210, abs=2)


def test_verify_pdf_flags_wrong_page_count(tmp_path):
    pytest.importorskip("pypdf")
    from pypdf import PdfWriter
    pdf = tmp_path / "one.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=595, height=842)  # A4 in points
    with pdf.open("wb") as fh:
        writer.write(fh)
    report = verify_pdf(pdf, expected_pages=3)
    assert not report.ok
    assert any(i.kind == "page_count" for i in report.issues)


# ---------------------------------------------------------------------------
# Spreadsheet verification
# ---------------------------------------------------------------------------

def test_verify_xlsx_passes_for_generated_sheets(tmp_path):
    layout = _manifest(tmp_path)
    playbook = generate_delivery_playbook(layout)
    report = verify_xlsx(playbook, expected_sheets=["Delivery Playbook"],
                         min_rows={"Delivery Playbook": 5})
    assert report.ok, report.issues


def test_verify_xlsx_flags_missing_sheet_and_thin_rows(tmp_path):
    layout = _manifest(tmp_path)
    qn = generate_questionnaire_spreadsheet(layout)
    report = verify_xlsx(qn, expected_sheets=["Nonexistent"],
                         min_rows={"Assessment Questionnaire": 999})
    assert not report.ok
    kinds = {i.kind for i in report.issues}
    assert "missing_sheet" in kinds
    assert "row_count" in kinds
