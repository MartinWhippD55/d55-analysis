"""review-pr engine.

Deterministic rendering of the PR review comment (findings table, positives,
verdict table) from structured findings. No GitHub / `gh` calls — the agent
gathers the review; this module only formats it consistently.
"""

from .comment import Finding, VerdictRow, render_comment, render_findings_table, render_verdict_table

__all__ = [
    "Finding",
    "VerdictRow",
    "render_comment",
    "render_findings_table",
    "render_verdict_table",
]
