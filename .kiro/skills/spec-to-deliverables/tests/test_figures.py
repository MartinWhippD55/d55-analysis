"""Tests for the figures single-source-of-truth computation (pure core)."""
import pytest

from engine.figures import compute_figures, fmt


DETAIL = [
    ("Est 1: Templates", 1.0, ""),
    ("Est 1: Templates", 0.5, ""),
    ("Est 1: Templates", 0.5, "Yes"),   # optional
    ("Est 2: DocuSign", 0.75, ""),
    (None, 1.0, ""),                       # ignored (no name)
    ("Est 2: DocuSign", None, ""),        # ignored (no days)
]


def test_required_optional_total_and_count():
    figs = compute_figures(DETAIL, name_to_key={"Est 1: Templates": "est1", "Est 2: DocuSign": "est2"})
    e1 = figs.get("est1")
    assert e1.required == 1.5
    assert e1.optional == 0.5
    assert e1.total == 2.0
    assert e1.task_count == 3
    e2 = figs.get("est2")
    assert e2.required == 0.75
    assert e2.task_count == 1


def test_lookup_by_name_and_key():
    figs = compute_figures(DETAIL, name_to_key={"Est 1: Templates": "est1"})
    assert figs.get("est1") is figs.get("Est 1: Templates")


def test_grand_total_default_and_subset():
    figs = compute_figures(DETAIL, name_to_key={"Est 1: Templates": "est1", "Est 2: DocuSign": "est2"})
    gt = figs.grand_total()
    assert gt.required == 2.25
    assert gt.optional == 0.5
    assert gt.total == 2.75
    subset = figs.grand_total(["est1"])
    assert subset.total == 2.0


def test_manual_summary_row_added_when_missing():
    figs = compute_figures(
        DETAIL,
        summary_rows=[("Est 3a: Training", 7, 8.0, 0.0, 8.0)],
        name_to_key={"Est 3a: Training": "est3a"},
    )
    assert figs.get("est3a").total == 8.0
    assert figs.get("est3a").task_count == 7


def test_manual_row_ignored_if_in_detail():
    # A name already present from detail rows must not be overwritten by a Summary row.
    figs = compute_figures(
        DETAIL,
        summary_rows=[("Est 1: Templates", 99, 99.0, 99.0, 198.0)],
        name_to_key={"Est 1: Templates": "est1"},
    )
    assert figs.get("est1").total == 2.0


def test_total_summary_row_is_not_ingested():
    # A spreadsheet's TOTAL rollup row must not be treated as an estimate,
    # else grand_total() double-counts.
    figs = compute_figures(
        DETAIL,
        summary_rows=[("TOTAL", 4, 2.25, 0.5, 2.75)],
        name_to_key={"Est 1: Templates": "est1", "Est 2: DocuSign": "est2"},
    )
    assert "total" not in figs.by_key
    assert figs.grand_total().total == 2.75


def test_slug_key_fallback():
    figs = compute_figures([("My Estimate Name", 1.0, "")])
    assert figs.get("my-estimate-name").required == 1.0


@pytest.mark.parametrize("value,expected", [
    (13.0, "13"), (13.5, "13.5"), (13.04, "13"), (13.06, "13.1"), (0, "0"),
])
def test_fmt(value, expected):
    assert fmt(value) == expected
