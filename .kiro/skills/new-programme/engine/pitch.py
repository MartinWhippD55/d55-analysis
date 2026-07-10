"""Elevator-pitch deck generator (Task 14).

Produces a branded, self-contained exec deck summarising the programme — the
2-minute narrative, the Assess→Teach→Prove→Scale stage path, the value, and the
recommended next step (the free assessment). Reuses the ``summary-presentation``
pattern: 16:9 slides, base64-embedded assets, and an auto-scale script. In
client-instance mode the deck gains a slide tailored to that client's gap
profile. Client-facing output, written under ``client/`` (Requirement 13).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from . import paths
from .layout import ProgrammeLayout
from .manifest import load_manifest
from .models import Assessment
from .programme_engine import b64_uri, esc
from .recommend import recommend_modules

_TEMPLATE = "pitch_template.html"


def _slide(inner: str, number: int, total: int, logo_uri: str, cls: str = "") -> str:
    klass = f"slide {cls}".strip()
    return (
        f'<div class="{klass}">'
        f'<img class="logo" src="{logo_uri}" alt="logo">'
        f'{inner}'
        f'<div class="slide-number">{number} / {total}</div>'
        f'</div>'
    )


def _title_slide(programme: Mapping[str, Any]) -> str:
    return (
        f'<div class="eyebrow">D55 Programme</div>'
        f'<h1>{esc(programme.get("name", "Programme"))}</h1>'
        f'<div class="subtitle">{esc(programme.get("one_liner", ""))}</div>'
    )


def _statement_slide(heading: str, statement_html: str) -> str:
    return f'<h2>{esc(heading)}</h2><div class="statement">{statement_html}</div>'


def _pipeline_slide(heading: str, phases: list[str]) -> str:
    parts: list[str] = []
    for i, p in enumerate(phases):
        parts.append(f'<div class="step">{esc(p)}</div>')
        if i < len(phases) - 1:
            parts.append('<div class="arrow">&#9654;</div>')
    return f'<h2>{esc(heading)}</h2><div class="pipeline">{"".join(parts)}</div>'


def _bullets_slide(heading: str, bullets: list[str]) -> str:
    lis = "".join(f"<li>{esc(b)}</li>" for b in bullets)
    return f'<h2>{esc(heading)}</h2><ul>{lis}</ul>'


def _next_step_slide(programme: Mapping[str, Any]) -> str:
    free = programme.get("commercial", {}).get("free_assessment", True)
    cta = ("Book your free assessment — one hour, a radar chart and a roadmap you can take to your board."
           if free else "Book an assessment to get your tailored radar and roadmap.")
    return (
        f'<h2>Your next step</h2>'
        f'<div class="statement">See exactly where you stand and what it takes to close the gaps.</div>'
        f'<div class="cta">{esc(cta)}</div>'
    )


def _gap_slide(assessment: Assessment, modules: list[Mapping[str, Any]]) -> str:
    ranked = sorted(assessment.scores, key=lambda s: s.gap, reverse=True)
    top = [s for s in ranked if s.gap > 0][:4]
    rows = "".join(
        f'<div class="gap-row"><span>{esc(s.dimension)}</span>'
        f'<span class="g">{s.current} &#8594; {s.target} (gap {s.gap})</span></div>'
        for s in top
    ) or '<div class="statement">You are strong across the board — let\'s talk about scaling.</div>'

    recs = recommend_modules(assessment, modules)
    order = {"critical": 0, "high": 1, "standard": 2}
    recs = sorted(recs, key=lambda r: order.get(r.status, 3))
    title_for = {m.get("id", m.get("module_id")): m.get("title", "") for m in modules}
    rec_bullets = "".join(
        f"<li>{esc(title_for.get(r.module_id, 'Module'))} — <strong>{esc(r.status)}</strong></li>"
        for r in recs
    )
    client = assessment.client_name or "your team"
    return (
        f'<h2>Where {esc(client)} is today</h2>'
        f'{rows}'
        f'<ul style="margin-top:18px">{rec_bullets or "<li>No modules triggered.</li>"}</ul>'
    )


def generate_pitch(
    layout: ProgrammeLayout,
    assessment: Assessment | None = None,
    content: Mapping[str, Any] | None = None,
    logo: Path | None = None,
    background: Path | None = None,
    output_name: str = "elevator-pitch.html",
) -> Path:
    """Render the elevator-pitch deck into ``client/`` (self-contained HTML).

    ``content`` may override ``narrative`` (HTML string) and ``value_points``
    (list of bullets). In client-instance mode (``assessment`` supplied) a
    gap-profile slide tailored to the client is inserted and the deck leads with
    their picture.
    """
    manifest = load_manifest(layout.root)
    programme = manifest.get("programme", {})
    modules = manifest.get("modules", [])
    content = content or {}

    logo_uri = b64_uri(logo or paths.default_logo())
    bg_uri = b64_uri(background or paths.default_background())

    phases = programme.get("phases", ["Assess", "Teach", "Prove", "Scale"])
    narrative = content.get(
        "narrative",
        f"Your teams have the ambition. <strong>{esc(programme.get('name', 'this programme'))}</strong> "
        "turns it into measured, repeatable capability — we assess, teach, prove it on real work, "
        "then leave you self-sufficient.",
    )
    value_points = content.get("value_points", [
        "A credible, evidence-led assessment — not a sales pitch.",
        "We prove the value on real work before you commit to scale.",
        "You keep the capability: we build, upskill, and exit.",
    ])

    # Assemble slide bodies (before wrapping, so we can number them).
    bodies: list[tuple[str, str]] = [
        (_title_slide(programme), "slide-title"),
        (_statement_slide("The 2-minute version", narrative), ""),
    ]
    if assessment is not None:
        bodies.append((_gap_slide(assessment, modules), ""))
    bodies += [
        (_pipeline_slide("How the programme runs", phases), ""),
        (_bullets_slide("Why it works", value_points), ""),
        (_next_step_slide(programme), ""),
    ]

    total = len(bodies)
    slides = "\n".join(
        _slide(body, i, total, logo_uri, cls) for i, (body, cls) in enumerate(bodies, 1)
    )

    template = (paths.templates_dir() / _TEMPLATE).read_text(encoding="utf-8")
    html = (
        template
        .replace("__TITLE__", f"{programme.get('name', 'Programme')} — Elevator Pitch")
        .replace("__LOGO_DATA_URI__", logo_uri)
        .replace("__BG_DATA_URI__", bg_uri)
        .replace("__SLIDES__", slides)
    )

    layout.client_dir.mkdir(parents=True, exist_ok=True)
    out = layout.client_dir / output_name
    out.write_text(html, encoding="utf-8")
    return out


__all__ = ["generate_pitch"]
