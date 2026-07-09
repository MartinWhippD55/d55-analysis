"""Per-module asset generation (Task 11).

For each deliverable a module promises, render a branded, self-contained HTML
starter template and a matching A4 PDF into that module's ``assets/`` folder,
using the vendored render engine (``programme_engine.build``). A deliverable may
be a bare title (a starter skeleton is generated) or a structured spec with its
own content blocks.

Self-containment (Requirement 8.3 / Property 12): the engine embeds images as
base64 and uses a system font stack, so output has no CDN/external asset links.
``is_self_contained`` verifies this on the produced HTML.
"""
from __future__ import annotations

import re
from dataclasses import replace
from pathlib import Path
from typing import Any, Mapping, Sequence

from .programme_engine import BrandConfig, build

# Matches external asset references in the HTML (any http/https URL).
_EXTERNAL_URL_RE = re.compile(r"https?://[^'\"\)\s]+")


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")


def is_self_contained(html: str) -> bool:
    """True if the HTML has no external http(s) asset references."""
    return not _EXTERNAL_URL_RE.search(html)


def _normalise_deliverable(deliverable: str | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(deliverable, str):
        return {"title": deliverable}
    return dict(deliverable)


def _starter_blocks(module: Mapping[str, Any], title: str) -> list[dict]:
    """Default starter-template content when a deliverable has no blocks."""
    return [
        {"type": "section", "heading": "Purpose",
         "body": [f"Starter template for <strong>{title}</strong>, produced by "
                  f"Module {module['id']} — {module['title']}."]},
        {"type": "section", "heading": "How to use",
         "bullets": ["Replace the placeholder content with the client's specifics.",
                     "Keep the D55 branding and structure.",
                     "This artefact writes into the Client Operating Manual section: "
                     f"{module.get('manual_section', 'TODO')}."]},
        {"type": "callout", "heading": "Notes",
         "body": ["TODO — capture decisions, owners, and follow-ups here."]},
    ]


def _deliverable_doc(module: Mapping[str, Any], deliverable: Mapping[str, Any]) -> dict:
    title = deliverable["title"]
    return {
        "slug": slugify(title),
        "title": title,
        "eyebrow": f"Module {module['id']}",
        "subtitle": deliverable.get("subtitle", module["title"]),
        "badge": deliverable.get("badge", "Starter template"),
        "date": deliverable.get("date", ""),
        "blocks": deliverable.get("blocks") or _starter_blocks(module, title),
    }


def generate_module_assets(
    layout,
    module: Mapping[str, Any],
    brand: BrandConfig | None = None,
    make_pdf: bool = True,
) -> list[Path]:
    """Render every deliverable of ``module`` into its ``assets/`` folder.

    ``module`` must have ``id``, ``slug``, ``title`` and a ``deliverables`` list
    (bare title strings or ``{title, subtitle?, badge?, blocks?}`` dicts). Returns
    the generated HTML paths (matching PDFs sit alongside when ``make_pdf``).
    """
    deliverables: Sequence = module.get("deliverables") or []
    if not deliverables:
        return []

    assets_dir = layout.module_assets_dir(module["id"], module["slug"])
    assets_dir.mkdir(parents=True, exist_ok=True)

    cfg = replace(brand or BrandConfig(), output_dir=assets_dir)

    html_paths: list[Path] = []
    for raw in deliverables:
        deliverable = _normalise_deliverable(raw)
        doc = _deliverable_doc(module, deliverable)
        html_paths.append(build(doc, cfg, make_pdf=make_pdf))
    return html_paths


__all__ = ["slugify", "is_self_contained", "generate_module_assets"]
