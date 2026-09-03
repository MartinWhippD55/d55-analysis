"""
PDF verification helpers (the agent cannot see images — measure, don't look).

Small wrappers over ``pypdf`` for the checks the deliverables verification step
relies on: page count, A4 page size, and orphan-heading detection (a page whose
last non-empty text line is one of the known section headings).

DOM/browser measurement (image load, block counts, overflow) is done separately
with the Playwright browser tools per the toolkit; this module covers the PDF.
"""
from __future__ import annotations

from pathlib import Path

# A4 in PostScript points, with a small tolerance.
A4_PT = (595.0, 842.0)
_TOL = 3.0


def page_count(pdf_path) -> int:
    from pypdf import PdfReader

    return len(PdfReader(str(pdf_path)).pages)


def page_sizes(pdf_path) -> list[tuple[float, float]]:
    from pypdf import PdfReader

    sizes = []
    for page in PdfReader(str(pdf_path)).pages:
        box = page.mediabox
        sizes.append((round(float(box.width), 1), round(float(box.height), 1)))
    return sizes


def is_a4(pdf_path, tol: float = _TOL) -> bool:
    """True if every page is A4 portrait within tolerance."""
    for w, h in page_sizes(pdf_path):
        if abs(w - A4_PT[0]) > tol or abs(h - A4_PT[1]) > tol:
            return False
    return True


def find_orphan_headings(pdf_path, headings) -> list[tuple[int, str]]:
    """Return (page_index, heading) where a page ends on a known heading line.

    An orphaned heading (last line on a page) usually means a section title got
    stranded at the page bottom, away from its content.
    """
    from pypdf import PdfReader

    wanted = {h.strip() for h in headings}
    orphans = []
    for i, page in enumerate(PdfReader(str(pdf_path)).pages):
        text = page.extract_text() or ""
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        if lines and lines[-1] in wanted:
            orphans.append((i, lines[-1]))
    return orphans
