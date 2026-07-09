"""Bundle-relative path resolution for the New Programme skill.

Every resource the skill needs (engine code, templates, persona rubrics, brand
assets, worked examples) lives inside this bundle. All paths are resolved
relative to the *bundle root* — the directory that contains ``SKILL.md`` — which
is the parent of the ``engine/`` package this module lives in.

Design constraint (Requirement 14.2): resolve relative to the bundle
(``Path(__file__).parent``), never relative to the repo root or ``analysis/``,
and never via a hard-coded absolute path. This is what makes the bundle portable:
copy the directory anywhere and every helper below still points at the right
resource.
"""

from __future__ import annotations

from pathlib import Path

# ``engine/paths.py`` -> ``engine/`` -> bundle root.
ENGINE_DIR: Path = Path(__file__).resolve().parent
BUNDLE_ROOT: Path = ENGINE_DIR.parent


def bundle_root() -> Path:
    """Return the bundle root (the directory containing ``SKILL.md``)."""
    return BUNDLE_ROOT


def engine_dir() -> Path:
    """Return the vendored engine package directory."""
    return ENGINE_DIR


def templates_dir() -> Path:
    """Return the templates/skeletons directory."""
    return BUNDLE_ROOT / "templates"


def personas_dir() -> Path:
    """Return the persona rubrics directory."""
    return BUNDLE_ROOT / "personas"


def brand_assets_dir() -> Path:
    """Return the default brand assets directory (``assets/brand/``)."""
    return BUNDLE_ROOT / "assets" / "brand"


def examples_dir() -> Path:
    """Return the worked-example directory."""
    return BUNDLE_ROOT / "examples"


def resource(*parts: str) -> Path:
    """Resolve an arbitrary bundle-relative resource path.

    Example::

        resource("templates", "module.md.tmpl")

    Always anchored at :data:`BUNDLE_ROOT`, so it can never escape the bundle
    via a repo-relative or absolute path.
    """
    return BUNDLE_ROOT.joinpath(*parts)


__all__ = [
    "BUNDLE_ROOT",
    "ENGINE_DIR",
    "bundle_root",
    "engine_dir",
    "templates_dir",
    "personas_dir",
    "brand_assets_dir",
    "examples_dir",
    "resource",
]
