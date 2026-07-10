"""End-to-end example builder — the bundle's own worked-example driver.

Reads the trimmed example programme from ``examples/example_programme.yaml``
(bundle-relative, via ``paths``) and runs the full pipeline into a caller-supplied
output root: scaffold → author dimensions → author modules → per-module assets →
spreadsheets → interactive questionnaire → elevator pitch.

Used by the portability check (Task 17) and end-to-end integration (Task 18).
Everything resolves relative to the bundle, so this runs unchanged after the
bundle is copied elsewhere. Accepts an ``Assessment`` to exercise client-instance
mode; ``None`` builds the full template.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from . import paths
from .authoring import author_dimensions, author_modules
from .layout import ProgrammeLayout, template_layout
from .models import Assessment
from .module_assets import generate_module_assets
from .pitch import generate_pitch
from .questionnaire import generate_questionnaire
from .scaffold import scaffold_programme
from .spreadsheets import generate_delivery_playbook, generate_questionnaire_spreadsheet


def load_example_spec() -> dict[str, Any]:
    """Load the bundled example programme spec (bundle-relative path)."""
    path = paths.examples_dir() / "example_programme.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def build_example(
    output_root: Path,
    assessment: Assessment | None = None,
    make_pdf: bool = False,
) -> ProgrammeLayout:
    """Run the full pipeline for the bundled example into ``output_root``.

    Returns the programme layout. In template mode all modules are authored and
    given assets; with an ``assessment`` only recommended modules are authored,
    and only those get assets.
    """
    spec = load_example_spec()
    layout = template_layout(output_root, spec["slug"])

    dimensions = spec["dimensions"]
    modules = spec["modules"]
    manual_sections = spec["manual_sections"]

    # 1. Scaffold (manifest + docs + module skeletons) and validate join keys.
    violations = scaffold_programme(
        layout,
        name=spec["name"], slug=spec["slug"], one_liner=spec.get("one_liner", ""),
        dimensions=[{"name": d["name"], "short": d.get("short", ""), "what": d.get("description", "")} for d in dimensions],
        modules=modules,
        manual_sections=manual_sections,
    )
    if violations:
        raise RuntimeError(f"scaffold join-key violations: {violations}")

    # 2. Author dimensions (full rubrics/questions).
    dim_violations = author_dimensions(layout, [
        {"name": d["name"], "what": d.get("description", ""),
         "must_ask": d.get("must_ask"), "go_deeper": d.get("go_deeper"),
         "levels": [{"score": i + 1, "level": _level_name(lv), "description": _level_desc(lv)}
                    for i, lv in enumerate(d.get("levels", []))]}
        for d in dimensions
    ])
    if dim_violations:
        raise RuntimeError(f"dimension join-key violations: {dim_violations}")

    # 3. Author modules (client-instance authors only recommended ones).
    authored_ids, mod_violations = author_modules(layout, modules, assessment=assessment)
    if mod_violations:
        raise RuntimeError(f"module join-key violations: {mod_violations}")

    # 4. Per-module assets (only for authored modules).
    authored = [m for m in modules if m["id"] in authored_ids]
    for module in authored:
        generate_module_assets(layout, module, make_pdf=make_pdf)

    # 5. Spreadsheets (internal runbook + client questionnaire).
    generate_delivery_playbook(layout)
    questions = {d["name"]: {"must_ask": d.get("must_ask", []), "go_deeper": d.get("go_deeper", [])}
                 for d in dimensions}
    generate_questionnaire_spreadsheet(layout, questions=questions)

    # 6. Interactive questionnaire (client-facing, self-contained).
    dimension_content = {d["name"]: {"description": d.get("description", ""),
                                     "levels": d.get("levels", []),
                                     "questions": d.get("must_ask", []) + d.get("go_deeper", [])}
                         for d in dimensions}
    generate_questionnaire(layout, dimension_content=dimension_content)

    # 7. Elevator pitch (gap-tailored if client-instance).
    generate_pitch(layout, assessment=assessment)

    return layout


def _level_name(level_str: str) -> str:
    # "Absent — no leadership acknowledgement" -> "Absent"
    return level_str.split("—")[0].split("-")[0].strip() or level_str


def _level_desc(level_str: str) -> str:
    parts = level_str.split("—", 1)
    return parts[1].strip() if len(parts) == 2 else level_str


__all__ = ["load_example_spec", "build_example"]
