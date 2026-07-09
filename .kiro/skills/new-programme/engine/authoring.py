"""Dimensions and module authoring steps (Task 10).

Where the scaffold (Task 9) lays down skeletons with TODO placeholders, the
authoring steps here take fully-specified content and emit complete, publishable
documents:

- :func:`author_dimensions` writes ``dimensions.md`` with 1–5 maturity rubrics,
  calibration examples, and must-ask/go-deeper questions per dimension. Dimension
  names remain the join key to module ``dimensions_covered`` and to scores.
- :func:`author_module` writes one schema-conformant ``module.md`` (frontmatter +
  the standard body sections). :func:`author_modules` authors many, and in
  client-instance mode (an assessment is supplied) authors **only** the modules
  the shared recommendation logic puts in scope (Requirement 6.4).

Both validate join keys after writing and return any :class:`ContractViolation`
so a caller can hard-stop before generating assets (Requirement 6.3).
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from .layout import ProgrammeLayout
from .manifest import dimension_names, load_manifest, validate_join_keys
from .models import Assessment, ContractViolation
from .recommend import recommend_modules
from .scaffold import _module_frontmatter as module_frontmatter


# ---------------------------------------------------------------------------
# 10.1 — dimensions authoring
# ---------------------------------------------------------------------------

_DEFAULT_LEVELS = ("Absent", "Aware", "Endorsed", "Mandated", "Strategic")


def _render_dimension(dim: Mapping[str, Any]) -> str:
    """Render one fully-authored dimension section."""
    name = dim["name"]
    what = dim.get("what", "")
    levels = dim.get("levels")
    if levels:
        rows = "\n".join(
            f"| {lv['score']} | {lv.get('level', _DEFAULT_LEVELS[lv['score'] - 1])} | {lv['description']} |"
            for lv in levels
        )
    else:
        rows = "\n".join(f"| {i} | {lvl} | TODO |" for i, lvl in enumerate(_DEFAULT_LEVELS, 1))

    parts = [
        f"## {name}",
        "",
        f"**What we're assessing:** {what}" if what else "**What we're assessing:** TODO",
        "",
        "| Score | Level | Description |",
        "|-------|-------|-------------|",
        rows,
        "",
    ]
    calibration = dim.get("calibration") or []
    parts.append("**Calibration examples:**")
    parts += [f"- {c}" for c in calibration] or ["- TODO"]
    parts.append("")
    parts.append("**Key workshop questions:**")
    parts.append("")
    parts.append("\u2605 Must-ask:")
    parts += [f"- {q}" for q in (dim.get("must_ask") or ["TODO"])]
    parts.append("")
    parts.append("Go deeper:")
    parts += [f"- {q}" for q in (dim.get("go_deeper") or ["TODO"])]
    return "\n".join(parts)


def author_dimensions(
    layout: ProgrammeLayout,
    dimensions: Sequence[Mapping[str, Any]],
    programme_name: str | None = None,
) -> list[ContractViolation]:
    """Author ``dimensions.md`` and check names align with the manifest (join key).

    Returns violations where an authored dimension is not in the manifest or a
    manifest dimension was not authored — the names must be a bijection so they
    can serve as the join key.
    """
    manifest = load_manifest(layout.root)
    if programme_name is None:
        programme_name = manifest.get("programme", {}).get("name", "Programme")

    header = (
        f"# {programme_name} — Assessment Dimensions\n\n"
        "These are the axes of the radar chart, scored 1–5 (current vs target). "
        "Dimension names here are the join key to module `dimensions_covered` and "
        "to assessment scores.\n\n"
        "## Scoring Guidance for Facilitators\n\n"
        "- **\u2605 Must-ask questions** — always ask these.\n"
        "- **Go-deeper questions** — use when conversation flows or a score is ambiguous.\n"
        "- **Calibration examples** — validate scoring against these.\n"
        "- **When between levels** — score the lower.\n"
        "- **Let the prospect self-score first**, then validate or challenge.\n\n"
        "---\n\n"
    )
    body = "\n\n---\n\n".join(_render_dimension(d) for d in dimensions)
    layout.dimensions_md.write_text(header + body + "\n", encoding="utf-8")

    # Join-key check: authored names must match the manifest dimension set exactly.
    authored = [d["name"] for d in dimensions]
    manifest_dims = set(dimension_names(manifest))
    violations: list[ContractViolation] = []
    for name in authored:
        if name not in manifest_dims:
            violations.append(ContractViolation("unknown_dimension", "dimensions.md", name))
    for name in manifest_dims:
        if name not in authored:
            violations.append(ContractViolation("unscored_dimension", "dimensions.md", name))
    return violations


# ---------------------------------------------------------------------------
# 10.2 — module authoring
# ---------------------------------------------------------------------------

def _bullets(items: Sequence[str] | None) -> str:
    return "\n".join(f"- {i}" for i in items) if items else "TODO"


def _numbered(items: Sequence[str] | None) -> str:
    return "\n".join(f"{n}. {s}" for n, s in enumerate(items, 1)) if items else "TODO"


def _render_module_body(module: Mapping[str, Any]) -> str:
    return "\n".join([
        f"# Module {module['id']} — {module['title']}",
        "",
        "## Objective",
        module.get("objective", "TODO"),
        "",
        "## Why it matters (client outcome)",
        module.get("why", "TODO"),
        "",
        "## Who's in the room",
        module.get("who", "TODO"),
        "",
        "## Inputs (from assessment)",
        _bullets(module.get("inputs")),
        "",
        "## Session flow",
        _numbered(module.get("session_flow")),
        "",
        "## Deliverables (what they leave with)",
        _bullets(module.get("deliverables")),
        "",
        "## Writes to Client Operating Manual",
        f"Section: {module['manual_section']}",
        module.get("writes_to_manual", ""),
        "",
        "## How it sets up the embed",
        module.get("embed", "TODO"),
        "",
    ])


def author_module(layout: ProgrammeLayout, module: Mapping[str, Any]) -> None:
    """Write one schema-conformant, fully-authored ``module.md`` (+ assets dir)."""
    mod_dir = layout.module_dir(module["id"], module["slug"])
    (mod_dir / "assets").mkdir(parents=True, exist_ok=True)
    content = f"---\n{module_frontmatter(module)}---\n\n{_render_module_body(module)}"
    (mod_dir / "module.md").write_text(content, encoding="utf-8")


def author_modules(
    layout: ProgrammeLayout,
    modules: Sequence[Mapping[str, Any]],
    assessment: Assessment | None = None,
) -> tuple[list[int], list[ContractViolation]]:
    """Author modules and validate join keys.

    In **template mode** (``assessment is None``) every module is authored. In
    **client-instance mode** only modules the shared recommendation logic puts in
    scope for ``assessment`` are authored (Requirement 6.4). Returns the authored
    module ids and the post-authoring join-key violations.
    """
    if assessment is None:
        in_scope = [m for m in modules]
    else:
        recommended = {r.module_id for r in recommend_modules(assessment, modules)}
        in_scope = [m for m in modules if m["id"] in recommended]

    for module in in_scope:
        author_module(layout, module)

    authored_ids = [m["id"] for m in in_scope]
    return authored_ids, validate_join_keys(layout.root)


__all__ = ["author_dimensions", "author_module", "author_modules"]
