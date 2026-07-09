"""Programme output layout, modes, and internal/client separation (Requirement 12).

A programme is written under a configurable output root (default
``programmes/<slug>/``) with a fixed, predictable layout:

    programmes/<slug>/
      programme.yaml, context.md, dimensions.md,
      client-operating-manual-toc.md, working-assumptions.md
      modules/module-{id}-{slug}/{module.md, assets/}
      internal/          internal-only assets (Delivery Playbook, critique/ logs)
      client/            client-facing deliverables (manual, questionnaires, pitch)
      assets/brand/      brand assets
      clients/<client-slug>/   per-engagement clones (same layout)

Two hard rules this module enforces:

- **internal/ vs client/ separation.** Internal-only assets are written under
  ``internal/`` and never under ``client/`` or a module's client-facing
  ``assets/``. ``client_bundle()`` assembles a delivery bundle that excludes
  everything under ``internal/`` (Requirement 12.3, 12.4).
- **Client instances never mutate the template.** ``clone_for_client()`` copies
  template source material into ``clients/<client-slug>/`` and never writes back
  into the template library (Requirement 12.6, Property 11).

The output root is always a parameter — never a hard-coded absolute path
(Requirement 12.1).
"""
from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

# Top-level docs that make up a programme's source spine.
PROGRAMME_DOCS = (
    "programme.yaml",
    "context.md",
    "dimensions.md",
    "client-operating-manual-toc.md",
    "working-assumptions.md",
)

# Subtrees that are generated *output* (regenerated per instance), not source.
_OUTPUT_SUBTREES = ("internal", "client", "clients")

INTERNAL_DIRNAME = "internal"
CLIENT_DIRNAME = "client"
CLIENTS_DIRNAME = "clients"


@dataclass(frozen=True)
class ProgrammeLayout:
    """Resolved paths for one programme (a template or a client instance)."""
    root: Path

    # --- source docs ---
    @property
    def manifest(self) -> Path:
        return self.root / "programme.yaml"

    @property
    def context_md(self) -> Path:
        return self.root / "context.md"

    @property
    def dimensions_md(self) -> Path:
        return self.root / "dimensions.md"

    @property
    def toc_md(self) -> Path:
        return self.root / "client-operating-manual-toc.md"

    @property
    def working_assumptions_md(self) -> Path:
        return self.root / "working-assumptions.md"

    # --- directories ---
    @property
    def modules_dir(self) -> Path:
        return self.root / "modules"

    @property
    def internal_dir(self) -> Path:
        return self.root / INTERNAL_DIRNAME

    @property
    def critique_dir(self) -> Path:
        return self.internal_dir / "critique"

    @property
    def client_dir(self) -> Path:
        return self.root / CLIENT_DIRNAME

    @property
    def brand_dir(self) -> Path:
        return self.root / "assets" / "brand"

    @property
    def clients_dir(self) -> Path:
        return self.root / CLIENTS_DIRNAME

    # --- path builders ---
    def module_dir(self, module_id: int, slug: str) -> Path:
        return self.modules_dir / f"module-{module_id}-{slug}"

    def module_assets_dir(self, module_id: int, slug: str) -> Path:
        return self.module_dir(module_id, slug) / "assets"

    def internal_path(self, *parts: str) -> Path:
        """A path under ``internal/`` (internal-only assets)."""
        return self.internal_dir.joinpath(*parts)

    def client_path(self, *parts: str) -> Path:
        """A path under ``client/`` (client-facing deliverables)."""
        return self.client_dir.joinpath(*parts)

    def create(self) -> "ProgrammeLayout":
        """Create the directory skeleton for this layout."""
        for d in (self.root, self.modules_dir, self.internal_dir,
                  self.critique_dir, self.client_dir, self.brand_dir):
            d.mkdir(parents=True, exist_ok=True)
        return self


# ---------------------------------------------------------------------------
# Layout constructors (modes)
# ---------------------------------------------------------------------------

def template_layout(output_root: Path, slug: str) -> ProgrammeLayout:
    """Template-mode layout at ``<output_root>/<slug>/`` (default output_root=programmes/)."""
    return ProgrammeLayout(root=Path(output_root) / slug)


def client_layout(output_root: Path, slug: str, client_slug: str) -> ProgrammeLayout:
    """Client-instance layout at ``<output_root>/<slug>/clients/<client_slug>/``."""
    return ProgrammeLayout(root=Path(output_root) / slug / CLIENTS_DIRNAME / client_slug)


def default_output_root() -> Path:
    """The default output root (a relative, caller-anchored ``programmes/`` dir)."""
    return Path("programmes")


# ---------------------------------------------------------------------------
# Internal/client separation helpers (Requirement 12.3, 12.4)
# ---------------------------------------------------------------------------

def is_internal_path(path: Path, layout: ProgrammeLayout) -> bool:
    """True if ``path`` resolves under this layout's ``internal/`` subtree."""
    try:
        Path(path).resolve().relative_to(layout.internal_dir.resolve())
        return True
    except ValueError:
        return False


def assert_client_safe(path: Path, layout: ProgrammeLayout) -> None:
    """Guard: raise if a client-facing write target lands under ``internal/``."""
    if is_internal_path(path, layout):
        raise ValueError(f"refusing to place a client-facing asset under internal/: {path}")


def client_bundle(layout: ProgrammeLayout, dest: Path) -> Path:
    """Assemble a client-facing delivery bundle, excluding everything under ``internal/``.

    Copies the programme tree to ``dest`` but omits the ``internal/`` subtree
    (Delivery Playbook, critique logs) and any nested ``clients/`` instances.
    Returns ``dest``.
    """
    dest = Path(dest)
    if dest.exists():
        shutil.rmtree(dest)

    def _ignore(dir_path: str, names: list[str]) -> set[str]:
        ignored: set[str] = set()
        if Path(dir_path).resolve() == layout.root.resolve():
            ignored |= {INTERNAL_DIRNAME, CLIENTS_DIRNAME} & set(names)
        return ignored

    shutil.copytree(layout.root, dest, ignore=_ignore)
    return dest


def contains_internal(bundle_dir: Path) -> bool:
    """True if a delivered bundle still contains an ``internal/`` directory."""
    return any(p.name == INTERNAL_DIRNAME for p in Path(bundle_dir).rglob(INTERNAL_DIRNAME) if p.is_dir())


# ---------------------------------------------------------------------------
# Client-instance cloning (Requirement 12.5, 12.6, Property 11)
# ---------------------------------------------------------------------------

def clone_for_client(
    template: ProgrammeLayout,
    client_slug: str,
    output_root: Path | None = None,
    programme_slug: str | None = None,
) -> ProgrammeLayout:
    """Clone template source material into a fresh client instance.

    Copies the programme docs, ``modules/``, and ``assets/`` from the template
    into ``clients/<client_slug>/`` (by default a child of the template root),
    leaving generated output subtrees (``internal/``, ``client/``, ``clients/``)
    out so they are regenerated for the client. The template library is never
    modified (Property 11).
    """
    if output_root is not None and programme_slug is not None:
        instance = client_layout(output_root, programme_slug, client_slug)
    else:
        # Default: nest the instance under the template's own clients/ dir.
        instance = ProgrammeLayout(root=template.clients_dir / client_slug)

    instance.root.mkdir(parents=True, exist_ok=True)

    # Copy source docs (never the generated output subtrees).
    for name in PROGRAMME_DOCS:
        src = template.root / name
        if src.exists():
            shutil.copy2(src, instance.root / name)

    # Copy the module library and brand assets wholesale (read-only from template).
    if template.modules_dir.exists():
        shutil.copytree(template.modules_dir, instance.modules_dir, dirs_exist_ok=True)
    template_assets = template.root / "assets"
    if template_assets.exists():
        shutil.copytree(template_assets, instance.root / "assets", dirs_exist_ok=True)

    # Fresh, empty output skeleton for this client.
    for d in (instance.internal_dir, instance.critique_dir, instance.client_dir):
        d.mkdir(parents=True, exist_ok=True)

    return instance


__all__ = [
    "PROGRAMME_DOCS",
    "ProgrammeLayout",
    "template_layout",
    "client_layout",
    "default_output_root",
    "is_internal_path",
    "assert_client_safe",
    "client_bundle",
    "contains_internal",
    "clone_for_client",
]
