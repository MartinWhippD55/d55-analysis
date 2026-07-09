"""Manifest loading, frontmatter/TOC parsing, and join-key validation.

The manifest (``programme.yaml``) is the single machine-readable source of truth
for a programme: identity, brand, dimensions (the radar axes / join keys), and a
mirror of each module's frontmatter for fast consumption.

Three joins make a programme tooling-consumable (design "Join-key contracts"):

======================  =======================================  ==================
Join                    Authority                                Rule
======================  =======================================  ==================
Dimension coverage      ``dimensions[].name`` (manifest)         subset, exact string
Manual mapping          section titles in the manual TOC         member, exact string
Criticality             a module's ``dimensions_covered``        subset
======================  =======================================  ==================

``validate_join_keys`` enforces these and is a **hard stop** for callers: asset
generation must not proceed while any violation exists (Requirement 2.5,
Property 1). The scoring bijection (assessment covers every dimension exactly
once, 1..5) is a distinct contract enforced by ``validate_assessment`` in
``recommend.py`` (Property 2).
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

from .models import ContractViolation


# ---------------------------------------------------------------------------
# Manifest read/write
# ---------------------------------------------------------------------------

def load_manifest(programme_dir: Path) -> dict:
    """Load ``programme.yaml`` from a programme directory."""
    path = Path(programme_dir) / "programme.yaml"
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def write_manifest(manifest: dict, programme_dir: Path) -> Path:
    """Write a manifest dict to ``programme.yaml`` (block style, stable key order)."""
    path = Path(programme_dir) / "programme.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(manifest, fh, sort_keys=False, allow_unicode=True, default_flow_style=False)
    return path


def dimension_names(manifest: dict) -> list[str]:
    """Return the ordered dimension names (the radar axes / join keys)."""
    return [d["name"] for d in manifest.get("dimensions", [])]


# ---------------------------------------------------------------------------
# Frontmatter + TOC parsing
# ---------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", re.DOTALL)


def parse_frontmatter(module_md_path: Path) -> dict:
    """Parse the YAML frontmatter block from a ``module.md`` file.

    Returns the frontmatter as a dict. Raises ``ValueError`` if the file has no
    ``---`` delimited frontmatter block.
    """
    text = Path(module_md_path).read_text(encoding="utf-8")
    match = _FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError(f"no frontmatter block found in {module_md_path}")
    data = yaml.safe_load(match.group(1))
    return data or {}


def load_toc_titles(toc_path: Path) -> list[str]:
    """Return the ``## `` section titles from the manual TOC, in document order.

    ``manual_section`` in a module must match one of these titles exactly
    (e.g. ``"1. Mandate & Measurement"``).
    """
    text = Path(toc_path).read_text(encoding="utf-8")
    titles: list[str] = []
    for line in text.splitlines():
        if line.startswith("## "):
            titles.append(line[3:].strip())
    return titles


def iter_module_files(programme_dir: Path) -> list[Path]:
    """Return the ``modules/*/module.md`` files, sorted for determinism."""
    return sorted(Path(programme_dir).glob("modules/*/module.md"))


# ---------------------------------------------------------------------------
# Join-key validator (Property 1 — hard stop before generation)
# ---------------------------------------------------------------------------

def validate_join_keys(programme_dir: Path) -> list[ContractViolation]:
    """Validate the three programme joins; return every violation found.

    Checks each ``modules/*/module.md`` against the manifest dimensions and the
    manual-TOC section titles:

    - ``unknown_dimension`` — a ``dimensions_covered`` entry not in the manifest.
    - ``unknown_manual_section`` — a ``manual_section`` not among the TOC titles.
    - ``critical_not_covered`` — a ``trigger.critical_dimensions`` entry that is
      not a subset of that module's own ``dimensions_covered``.

    An empty list means all joins hold. Callers MUST treat a non-empty result as
    a hard stop and not proceed to asset generation (Requirement 2.5).
    """
    programme_dir = Path(programme_dir)
    manifest = load_manifest(programme_dir)
    dims = set(dimension_names(manifest))
    toc = set(load_toc_titles(programme_dir / "client-operating-manual-toc.md"))

    violations: list[ContractViolation] = []
    for module_md in iter_module_files(programme_dir):
        fm = parse_frontmatter(module_md)
        where = str(module_md.relative_to(programme_dir)).replace("\\", "/")

        covered = fm.get("dimensions_covered", []) or []
        for d in covered:
            if d not in dims:
                violations.append(ContractViolation("unknown_dimension", where, d))

        manual_section = fm.get("manual_section", "")
        if manual_section not in toc:
            violations.append(ContractViolation("unknown_manual_section", where, manual_section))

        trigger = fm.get("trigger", {}) or {}
        for cd in trigger.get("critical_dimensions", []) or []:
            if cd not in covered:
                violations.append(ContractViolation("critical_not_covered", where, cd))

    return violations


class JoinKeyError(RuntimeError):
    """Raised to hard-stop callers when join-key validation fails."""

    def __init__(self, violations: list[ContractViolation]):
        self.violations = violations
        lines = "\n".join(f"  - [{v.kind}] {v.where}: {v.value!r}" for v in violations)
        super().__init__(f"{len(violations)} join-key violation(s):\n{lines}")


def require_valid_join_keys(programme_dir: Path) -> None:
    """Hard-stop helper: raise :class:`JoinKeyError` if any join is broken."""
    violations = validate_join_keys(programme_dir)
    if violations:
        raise JoinKeyError(violations)


__all__ = [
    "load_manifest",
    "write_manifest",
    "dimension_names",
    "parse_frontmatter",
    "load_toc_titles",
    "iter_module_files",
    "validate_join_keys",
    "JoinKeyError",
    "require_valid_join_keys",
]
