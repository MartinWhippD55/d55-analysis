"""Tests for the block-based walkthrough engine (pure HTML assembly)."""
from hypothesis import given, strategies as st

from engine.walkthrough import build_html, slugify, RENDERERS
import pytest


def _doc(blocks, **extra):
    return {"title": "My Doc", "subtitle": "A subtitle", "blocks": blocks, **extra}


def test_cover_fields_render():
    html = build_html(_doc([], effort="~5 days", eyebrow="Kicker", date="July 2026"))
    assert "My Doc" in html
    assert "A subtitle" in html
    assert "~5 days" in html
    assert "Kicker" in html
    assert "July 2026" in html


def test_section_and_bullets():
    html = build_html(_doc([
        {"type": "section", "heading": "Overview", "body": ["Para one"], "bullets": ["a", "b", "c"]},
    ]))
    assert "<h2>Overview</h2>" in html
    assert "<p>Para one</p>" in html
    assert html.count("<li>") == 3


def test_table_columns_and_rows():
    html = build_html(_doc([
        {"type": "table", "heading": "T", "columns": ["A", "B"], "rows": [["1", "2"], ["3", "4"]]},
    ]))
    assert html.count("<th>") == 2
    assert html.count("<tr>") == 3  # header + 2 body rows


def test_entities_pk_sk_and_gsi():
    html = build_html(_doc([
        {"type": "entities", "heading": "Data", "table": "MyTable",
         "entities": [
             {"name": "Rec", "pk": "PK#1", "sk": "SK#1", "note": "a note",
              "attributes": [["id", "string", "the id"], ["n", "number", "count"]]},
         ],
         "gsi": [{"name": "GSI1", "pk": "gpk", "sk": "gsk", "enables": "lookup"}]},
    ]))
    assert html.count('class="entity"') == 1
    assert "PK</span><code>PK#1" in html
    assert "SK</span><code>SK#1" in html
    assert "Global Secondary Indexes" in html
    assert "MyTable" in html


def test_layers_and_pipeline():
    html = build_html(_doc([
        {"type": "layers", "heading": "Arch", "lanes": [
            {"label": "UI", "nodes": ["screen", "form"]},
            {"label": "API", "nodes": ["lambda"]},
        ]},
        {"type": "pipeline", "heading": "Flow", "steps": ["a", "b", "c"]},
    ]))
    assert html.count('class="lane"') == 2
    assert html.count('class="lane-arrow"') == 1   # one arrow between two lanes
    assert html.count('class="step"') == 3
    assert html.count('class="step-arrow"') == 2


def test_callout():
    html = build_html(_doc([{"type": "callout", "heading": "Note", "body": ["watch out"]}]))
    assert 'class="block callout"' in html
    assert "watch out" in html


def test_page_break_adds_section_break():
    html = build_html(_doc([{"type": "section", "heading": "H", "body": ["x"], "pageBreak": True}]))
    assert "section-break" in html


def test_unknown_block_raises():
    with pytest.raises(ValueError):
        build_html(_doc([{"type": "nonsense"}]))


def test_all_renderers_registered():
    assert set(RENDERERS) == {
        "section", "table", "diagram", "callout", "screens", "layers", "pipeline", "entities"
    }


@given(st.text())
def test_section_text_is_escaped(text):
    # Arbitrary body text must never inject a raw tag into the output.
    html = build_html(_doc([{"type": "section", "body": [text]}]))
    assert "<script>" not in html.replace("</script>", "")  # no injected script open tag
    if "<" in text:
        assert "&lt;" in html


def test_slugify():
    assert slugify("Est 1: PDF / Template Management") == "est-1-pdf-template-management"
    assert slugify("!!!") == "document"
