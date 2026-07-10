"""Interactive questionnaire generator (Task 13).

Generalises the AI-DLC ``workshop.html`` into a manifest-driven, self-contained
tool: it embeds the programme's dimensions and the module trigger logic from the
manifest, lets a user score each dimension current-vs-target (1–5), renders a
radar chart of the gap, and recommends modules.

Two hard constraints:

- **Parity (Property 6).** The client-side ``recommendModules`` in the template
  mirrors ``engine/recommend.py::recommend_modules`` exactly, and is driven by the
  same manifest module triggers — so client-side output matches build-time for
  identical scores. This is verified by a Playwright parity test.
- **Self-contained (Property 12).** The logo is embedded as base64 and the radar
  is drawn with a small dependency-free canvas routine (no CDN Chart.js), so the
  delivered HTML has no external dependencies. Output is written under ``client/``.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from . import paths
from .layout import ProgrammeLayout
from .manifest import load_manifest
from .programme_engine import b64_uri

_TEMPLATE = "questionnaire_template.html"

_DEFAULT_LEVELS = [
    "Absent — no capability in place",
    "Aware — informal / ad-hoc",
    "Endorsed — provisioned but inconsistent",
    "Effective — embedded for the majority",
    "Strategic — a stated competitive advantage",
]


def _dimensions_ui(
    manifest: Mapping[str, Any],
    dimension_content: Mapping[str, Mapping[str, Any]] | None,
) -> list[dict]:
    content = dimension_content or {}
    out: list[dict] = []
    for d in manifest.get("dimensions", []):
        name = d["name"]
        c = content.get(name, {})
        out.append({
            "name": name,                                  # JOIN KEY (exact)
            "short": d.get("short", name.split()[0]),
            "title": name,
            "description": c.get("description", ""),
            "levels": c.get("levels", _DEFAULT_LEVELS),
            "questions": c.get("questions", []),
        })
    return out


def _modules_ui(manifest: Mapping[str, Any]) -> list[dict]:
    # Embed exactly what the recommendation logic needs (id, title, coverage, trigger).
    out: list[dict] = []
    for m in manifest.get("modules", []):
        out.append({
            "id": m.get("id", m.get("module_id")),
            "title": m.get("title", f"Module {m.get('id', m.get('module_id'))}"),
            "dimensions_covered": list(m.get("dimensions_covered", [])),
            "trigger": dict(m.get("trigger", {})),
        })
    return out


def generate_questionnaire(
    layout: ProgrammeLayout,
    dimension_content: Mapping[str, Mapping[str, Any]] | None = None,
    logo: Path | None = None,
    output_name: str = "workshop.html",
) -> Path:
    """Render the interactive questionnaire into ``client/`` (self-contained HTML).

    ``dimension_content`` optionally enriches each dimension with a description,
    five level labels, and questions (keyed by exact dimension name). Modules and
    triggers come from the manifest.
    """
    manifest = load_manifest(layout.root)
    programme = manifest.get("programme", {})

    template = (paths.templates_dir() / _TEMPLATE).read_text(encoding="utf-8")
    logo_uri = b64_uri(logo or paths.default_logo())

    replacements = {
        "__TITLE__": f"{programme.get('name', 'Programme')} — Readiness Assessment",
        "__PROGRAMME_NAME__": programme.get("name", "Programme"),
        "__ONE_LINER__": programme.get("one_liner", ""),
        "__LOGO_DATA_URI__": logo_uri,
        "__PROGRAMME_JSON__": json.dumps(programme, ensure_ascii=False),
        "__DIMENSIONS_JSON__": json.dumps(_dimensions_ui(manifest, dimension_content), ensure_ascii=False),
        "__MODULES_JSON__": json.dumps(_modules_ui(manifest), ensure_ascii=False),
    }
    html = template
    for token, value in replacements.items():
        html = html.replace(token, value)

    layout.client_dir.mkdir(parents=True, exist_ok=True)
    out = layout.client_dir / output_name
    out.write_text(html, encoding="utf-8")
    return out


__all__ = ["generate_questionnaire"]
