"""Tests for the data-driven presentation deck (pure HTML assembly)."""
import pytest

from engine.presentation import build_deck_html


DECK = {
    "title": "My Deck",
    "subtitle": "Playback",
    "org": "Acme",
    "date": "July 2026",
    "slides": [
        {"type": "table", "heading": "Summary",
         "columns": ["Estimate", "Total"], "rows": [["One", "5"], ["TOTAL", "5"]]},
        {"type": "content", "heading": "Est 1", "hero": "~5 days",
         "bullets": ["does <strong>a thing</strong>", "and another"], "note": "a footnote"},
    ],
}


def test_slide_count_includes_title():
    html = build_deck_html(DECK)
    assert html.count('<div class="slide ') == 3   # title + table + content


def test_numbering_and_total():
    html = build_deck_html(DECK)
    assert "1 / 3" in html
    assert "2 / 3" in html
    assert "3 / 3" in html


def test_title_fields_and_footer():
    html = build_deck_html(DECK)
    assert "My Deck" in html
    assert "Playback" in html
    assert "Acme" in html
    assert "July 2026" in html


def test_content_bullets_are_trusted_html():
    html = build_deck_html(DECK)
    assert "<strong>a thing</strong>" in html   # not escaped
    assert html.count("<li>") == 2


def test_heading_is_escaped():
    deck = {"title": "T", "slides": [{"type": "content", "heading": "a < b", "bullets": []}]}
    html = build_deck_html(deck)
    assert "a &lt; b" in html


def test_autoscale_script_present():
    html = build_deck_html(DECK)
    assert "document.body.style.zoom" in html


def test_unknown_slide_type_raises():
    with pytest.raises(ValueError):
        build_deck_html({"title": "T", "slides": [{"type": "bogus"}]})
