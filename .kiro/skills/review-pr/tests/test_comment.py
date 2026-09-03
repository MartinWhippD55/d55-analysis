"""Tests for the review-comment rendering engine (pure)."""
import pytest
from hypothesis import given, strategies as st

from engine.comment import (
    Finding, VerdictRow, render_comment, render_findings_table,
    render_verdict_table, escape_cell, SEVERITY_LABELS, STATUS_LABELS,
)


def test_findings_table_numbers_rows_and_maps_severity():
    md = render_findings_table([
        Finding("blocking", "auth.py", "leaks a token", "redact it"),
        Finding("non_blocking", "utils.py", "dead code", "remove it"),
    ])
    lines = md.splitlines()
    assert lines[0].startswith("| # | Severity |")
    assert "| 1 | 🔴 Blocking | auth.py | leaks a token | redact it |" in md
    assert "| 2 | 🔵 Non-blocking | utils.py | dead code | remove it |" in md


def test_findings_table_empty_has_header_only():
    md = render_findings_table([])
    assert md.count("\n") == 1   # header + separator, no data rows


def test_unknown_severity_raises():
    with pytest.raises(ValueError):
        render_findings_table([Finding("bogus", "a", "b", "c")])


def test_unknown_status_raises():
    with pytest.raises(ValueError):
        render_verdict_table([VerdictRow("Overall", "meh", "x")])


def test_pipe_and_newline_escaped_in_cells():
    md = render_findings_table([
        Finding("confirm", "a|b", "line one\nline two", "do | this"),
    ])
    # No raw pipe from content should appear unescaped inside the row body.
    row = [ln for ln in md.splitlines() if ln.startswith("| 1 |")][0]
    assert "a\\|b" in row
    assert "do \\| this" in row
    assert "line one line two" in row   # newline flattened
    # The row still has exactly the 5 column separators + 2 edges = 6 pipes... plus escaped ones are '\|'
    assert "\n" not in row


def test_verdict_bold_row():
    md = render_verdict_table([
        VerdictRow("Code quality", "good", "solid"),
        VerdictRow("Overall", "good", "ship it", bold=True),
    ])
    assert "| Code quality | 🟢 | solid |" in md
    assert "| **Overall** | **🟢** | **ship it** |" in md


def test_render_comment_has_all_sections():
    md = render_comment(
        title="My Feature",
        summary="Looks good, one thing to confirm.",
        findings=[Finding("confirm", "api.py", "n+1 query", "batch it")],
        positives=["clear tests"],
        verdict=[VerdictRow("Overall", "confirm", "confirm the query", bold=True)],
    )
    assert "## Review Summary — My Feature" in md
    assert "### Findings" in md
    assert "### Positives" in md
    assert "- ✅ clear tests" in md
    assert "### Verdict" in md
    assert "| 1 | 🟡 Confirm | api.py | n+1 query | batch it |" in md


def test_render_comment_empty_positives_placeholder():
    md = render_comment("T", "summary", findings=[], positives=[], verdict=[])
    assert "_None noted._" in md


@pytest.mark.parametrize("key,label", list(SEVERITY_LABELS.items()))
def test_all_severities_render(key, label):
    assert Finding(key, "a", "b", "c").label() == label


@pytest.mark.parametrize("key,label", list(STATUS_LABELS.items()))
def test_all_statuses_render(key, label):
    assert VerdictRow("a", key, "n").label() == label


@given(st.text())
def test_escape_cell_never_emits_raw_pipe_or_newline(text):
    out = escape_cell(text)
    assert "\n" not in out
    # every pipe in the output must be an escaped one
    assert "|" not in out.replace("\\|", "")
