"""Scaffolding step: instantiate the programme skeleton, then validate join keys.

Renders the bundle templates (``templates/*.tmpl``) into a programme directory
and builds the ``programme.yaml`` manifest structurally, then runs
``validate_join_keys`` so a scaffold that would drift is caught immediately
(Requirement 2.1, 6.1, 6.3). Returns the (hopefully empty) violation list; a
non-empty result is a hard stop for the caller.

Templates use a minimal ``{{token}}`` substitution so the skeletons stay readable
and are themselves valid documents. The manifest is written via
``manifest.write_manifest`` (structured YAML) rather than string-templated, so the
machine source of truth is always well-formed; ``programme.yaml.tmpl`` remains the
human-authoring reference skeleton.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml

from . import paths
from .layout import ProgrammeLayout
from .manifest import validate_join_keys, write_manifest
from .models import ContractViolation

_TOKEN_RE = re.compile(r"\{\{(\w+)\}\}")


def render_template(name: str, /, **context: Any) -> str:
    """Render a bundle template by substituting ``{{token}}`` placeholders."""
    text = (paths.templates_dir() / name).read_text(encoding="utf-8")

    def _sub(m: re.Match[str]) -> str:
        key = m.group(1)
        return str(context[key]) if key in context else m.group(0)

    return _TOKEN_RE.sub(_sub, text)


# ---------------------------------------------------------------------------
# Rendered blocks
# ---------------------------------------------------------------------------

def _dimension_section(dim: Mapping[str, Any]) -> str:
    """A dimensions.md section skeleton for one dimension (table + question tiers)."""
    name = dim["name"]
    what = dim.get("what", "TODO — what this dimension assesses.")
    rows = "\n".join(
        f"| {i} | {level} | TODO |"
        for i, level in enumerate(["Absent", "Aware", "Endorsed", "Mandated", "Strategic"], start=1)
    )
    return (
        f"## {name}\n\n"
        f"**What we're assessing:** {what}\n\n"
        f"| Score | Level | Description |\n"
        f"|-------|-------|-------------|\n"
        f"{rows}\n\n"
        f"**Calibration examples:**\n- Level 2: TODO\n- Level 3: TODO\n- Level 4: TODO\n\n"
        f"**Key workshop questions:**\n\n"
        f"\u2605 Must-ask:\n- TODO\n\nGo deeper:\n- TODO\n"
    )


def _toc_sections(manual_sections: Sequence[str]) -> str:
    """Render the manual TOC section headings from the provided section titles."""
    return "\n\n".join(f"## {title}\n*TODO — what this section captures.*" for title in manual_sections)


def _module_frontmatter(module: Mapping[str, Any]) -> str:
    """Schema-ordered frontmatter YAML for a module.md."""
    fm: dict[str, Any] = {
        "module_id": module["id"],
        "title": module["title"],
        "dimensions_covered": list(module["dimensions_covered"]),
        "trigger": dict(module["trigger"]),
        "audience": list(module.get("audience", ["TODO"])),
        "duration": module.get("duration", "TODO"),
        "format": module.get("format", "TODO"),
        "manual_section": module["manual_section"],
        "sets_up_embed": bool(module.get("sets_up_embed", False)),
    }
    if module.get("d55_ip"):
        fm["d55_ip"] = list(module["d55_ip"])
    return yaml.safe_dump(fm, sort_keys=False, allow_unicode=True)


# ---------------------------------------------------------------------------
# Scaffold routine
# ---------------------------------------------------------------------------

def scaffold_programme(
    layout: ProgrammeLayout,
    *,
    name: str,
    slug: str,
    one_liner: str = "TODO",
    brand_primary: str = "#1a0a3e",
    dimensions: Sequence[Mapping[str, Any]],
    modules: Sequence[Mapping[str, Any]],
    manual_sections: Sequence[str],
    context_text: str = "# Context\n\nTODO — background, ICP, positioning, commercial model.\n",
) -> list[ContractViolation]:
    """Instantiate the programme skeleton and validate join keys.

    ``dimensions`` are ``{name, short?, what?}``; ``modules`` mirror module.md
    frontmatter (``id, slug, title, dimensions_covered, trigger, manual_section``,
    plus optional audience/duration/format/sets_up_embed/d55_ip);
    ``manual_sections`` are the manual TOC section titles (must include every
    module's ``manual_section``).

    Returns the join-key violations found after scaffolding — empty means the
    programme is internally consistent and safe to build from.
    """
    layout.create()

    # --- manifest (structured source of truth) ---
    manifest = {
        "programme": {
            "slug": slug,
            "name": name,
            "external_name": None,
            "one_liner": one_liner,
            "phases": ["Assess", "Teach", "Prove", "Scale"],
            "commercial": {"free_assessment": True, "tiers": ["Assess", "Assess+Teach", "Full programme"]},
        },
        "brand": {
            "primary": brand_primary,
            "logo": "assets/brand/d55-logo-white.png",
            "background": "assets/brand/d55-background.jpg",
        },
        "dimensions": [
            {"name": d["name"], "short": d.get("short", d["name"].split()[0]),
             "rubric_ref": f"dimensions.md#{_anchor(d['name'])}"}
            for d in dimensions
        ],
        "modules": [
            {
                "id": m["id"],
                "slug": m["slug"],
                "title": m["title"],
                "dimensions_covered": list(m["dimensions_covered"]),
                "manual_section": m["manual_section"],
                "trigger": dict(m["trigger"]),
            }
            for m in modules
        ],
    }
    write_manifest(manifest, layout.root)

    # --- docs ---
    layout.dimensions_md.write_text(
        render_template(
            "dimensions.md.tmpl",
            programme_name=name,
            dimension_sections="\n\n---\n\n".join(_dimension_section(d) for d in dimensions),
        ),
        encoding="utf-8",
    )
    layout.toc_md.write_text(
        render_template(
            "client-operating-manual-toc.md.tmpl",
            programme_name=name,
            sections=_toc_sections(manual_sections),
        ),
        encoding="utf-8",
    )
    layout.context_md.write_text(context_text, encoding="utf-8")
    layout.working_assumptions_md.write_text(
        "# Working Assumptions\n\n| Assumption | Owner | Status |\n|---|---|---|\n", encoding="utf-8"
    )

    # --- modules ---
    for m in modules:
        mod_dir = layout.module_dir(m["id"], m["slug"])
        (mod_dir / "assets").mkdir(parents=True, exist_ok=True)
        (mod_dir / "module.md").write_text(
            render_template(
                "module.md.tmpl",
                frontmatter=_module_frontmatter(m),
                module_heading=f"Module {m['id']} — {m['title']}",
                objective=m.get("objective", "TODO — the client outcome in 2–3 sentences."),
                manual_section=m["manual_section"],
            ),
            encoding="utf-8",
        )

    # --- validate join keys (hard stop for callers if non-empty) ---
    return validate_join_keys(layout.root)


def _anchor(text: str) -> str:
    """A GitHub-style heading anchor for a dimension name."""
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug


__all__ = ["render_template", "scaffold_programme"]
