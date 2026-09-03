"""Render a PR review comment from structured findings (pure, deterministic).

The agent supplies `Finding`s and `VerdictRow`s; this module renders the exact
markdown shape the skill posts — a findings table (auto-numbered), a positives
list, and a verdict table — with consistent severity/status emojis and safe
cell escaping (pipes and newlines never break a table).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

# Findings-table severity keys -> rendered label.
SEVERITY_LABELS = {
    "blocking": "🔴 Blocking",
    "confirm": "🟡 Confirm",
    "non_blocking": "🔵 Non-blocking",
    "acknowledged": "✅ Acknowledged",
}

# Verdict-table status keys -> rendered emoji.
STATUS_LABELS = {
    "good": "🟢",
    "confirm": "🟡",
    "problem": "🔴",
}


@dataclass
class Finding:
    severity: str   # one of SEVERITY_LABELS
    area: str
    finding: str
    action: str

    def label(self) -> str:
        if self.severity not in SEVERITY_LABELS:
            raise ValueError(
                f"Unknown severity {self.severity!r}; expected one of {sorted(SEVERITY_LABELS)}"
            )
        return SEVERITY_LABELS[self.severity]


@dataclass
class VerdictRow:
    aspect: str
    status: str     # one of STATUS_LABELS
    notes: str = ""
    bold: bool = False   # e.g. the final "Overall" row

    def label(self) -> str:
        if self.status not in STATUS_LABELS:
            raise ValueError(
                f"Unknown status {self.status!r}; expected one of {sorted(STATUS_LABELS)}"
            )
        return STATUS_LABELS[self.status]


def escape_cell(text) -> str:
    """Make text safe for a markdown table cell: escape pipes, flatten newlines."""
    s = str(text).replace("\r\n", "\n").replace("\r", "\n")
    s = s.replace("\n", " ").replace("|", "\\|")
    return s.strip()


def _bold(text: str, on: bool) -> str:
    return f"**{text}**" if on else text


def render_findings_table(findings: list[Finding]) -> str:
    header = (
        "| # | Severity | Area | Finding | Suggested action |\n"
        "|---|----------|------|---------|------------------|"
    )
    lines = [header]
    for i, f in enumerate(findings, 1):
        lines.append(
            f"| {i} | {f.label()} | {escape_cell(f.area)} | "
            f"{escape_cell(f.finding)} | {escape_cell(f.action)} |"
        )
    return "\n".join(lines)


def render_verdict_table(rows: list[VerdictRow]) -> str:
    header = "| Aspect | Status | Notes |\n|--------|--------|-------|"
    lines = [header]
    for r in rows:
        aspect = _bold(escape_cell(r.aspect), r.bold)
        status = _bold(r.label(), r.bold)
        notes = _bold(escape_cell(r.notes), r.bold)
        lines.append(f"| {aspect} | {status} | {notes} |")
    return "\n".join(lines)


def render_comment(
    title: str,
    summary: str,
    findings: Optional[list[Finding]] = None,
    positives: Optional[list[str]] = None,
    verdict: Optional[list[VerdictRow]] = None,
) -> str:
    """Assemble the full review comment markdown."""
    findings = findings or []
    positives = positives or []
    verdict = verdict or []

    parts = [f"## Review Summary — {escape_cell(title)}", "", summary.strip(), "", "### Findings", ""]
    parts.append(render_findings_table(findings))
    parts += ["", "### Positives", ""]
    if positives:
        parts += [f"- ✅ {p.strip()}" for p in positives]
    else:
        parts.append("- _None noted._")
    parts += ["", "### Verdict", ""]
    parts.append(render_verdict_table(verdict))
    parts.append("")
    return "\n".join(parts)
