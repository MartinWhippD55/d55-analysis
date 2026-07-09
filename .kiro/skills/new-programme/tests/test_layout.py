"""Tests for programme layout, modes, and internal/client separation (Task 8)."""
from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from engine.layout import (
    PROGRAMME_DOCS,
    assert_client_safe,
    client_bundle,
    client_layout,
    clone_for_client,
    contains_internal,
    is_internal_path,
    template_layout,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _hash_tree(root: Path) -> dict[str, str]:
    """Map of relative path -> sha256 for every file under root (byte snapshot)."""
    out: dict[str, str] = {}
    for p in sorted(root.rglob("*")):
        if p.is_file():
            rel = str(p.relative_to(root)).replace("\\", "/")
            out[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def _make_template(root: Path):
    layout = template_layout(root, "demo").create()
    layout.manifest.write_text("programme:\n  slug: demo\n", encoding="utf-8")
    layout.context_md.write_text("# Context\n", encoding="utf-8")
    layout.dimensions_md.write_text("# Dimensions\n", encoding="utf-8")
    layout.toc_md.write_text("# TOC\n", encoding="utf-8")
    layout.working_assumptions_md.write_text("# Assumptions\n", encoding="utf-8")
    # A module with source + a template-side asset.
    mdir = layout.module_dir(1, "leadership")
    (mdir / "assets").mkdir(parents=True, exist_ok=True)
    (mdir / "module.md").write_text("---\nmodule_id: 1\n---\n# M1\n", encoding="utf-8")
    (mdir / "assets" / "starter.txt").write_text("starter", encoding="utf-8")
    layout.brand_dir.mkdir(parents=True, exist_ok=True)
    (layout.brand_dir / "logo.txt").write_text("logo", encoding="utf-8")
    return layout


# ---------------------------------------------------------------------------
# 8.1 — layout + modes
# ---------------------------------------------------------------------------

def test_template_layout_paths_and_default_root(tmp_path):
    layout = template_layout(tmp_path / "programmes", "ai-dlc")
    assert layout.root == tmp_path / "programmes" / "ai-dlc"
    assert layout.manifest.name == "programme.yaml"
    assert layout.internal_dir.name == "internal"
    assert layout.client_dir.name == "client"
    assert layout.brand_dir == layout.root / "assets" / "brand"
    assert layout.module_dir(2, "lifecycle").name == "module-2-lifecycle"


def test_create_makes_full_skeleton(tmp_path):
    layout = template_layout(tmp_path, "demo").create()
    for d in (layout.modules_dir, layout.internal_dir, layout.critique_dir,
              layout.client_dir, layout.brand_dir):
        assert d.is_dir()


def test_client_layout_nests_under_clients(tmp_path):
    layout = client_layout(tmp_path, "ai-dlc", "acme")
    assert layout.root == tmp_path / "ai-dlc" / "clients" / "acme"


def test_output_root_is_a_parameter_not_absolute(tmp_path):
    # The same slug can be rooted anywhere the caller chooses.
    a = template_layout(tmp_path / "one", "demo")
    b = template_layout(tmp_path / "two", "demo")
    assert a.root != b.root


# ---------------------------------------------------------------------------
# 8.2 — internal/client separation
# ---------------------------------------------------------------------------

def test_is_internal_path_detects_internal(tmp_path):
    layout = template_layout(tmp_path, "demo").create()
    assert is_internal_path(layout.internal_path("runbook.xlsx"), layout)
    assert not is_internal_path(layout.client_path("manual.html"), layout)
    assert not is_internal_path(layout.module_assets_dir(1, "x") / "d.html", layout)


def test_assert_client_safe_rejects_internal_target(tmp_path):
    layout = template_layout(tmp_path, "demo").create()
    assert_client_safe(layout.client_path("pitch.html"), layout)  # ok
    with pytest.raises(ValueError):
        assert_client_safe(layout.internal_path("runbook.xlsx"), layout)


def test_client_bundle_excludes_internal(tmp_path):
    layout = _make_template(tmp_path)
    # Put an internal-only asset + a critique log in place.
    layout.internal_path("Delivery Playbook.xlsx").write_text("secret runbook", encoding="utf-8")
    layout.critique_dir.mkdir(parents=True, exist_ok=True)
    (layout.critique_dir / "critique-D-1.md").write_text("log", encoding="utf-8")
    # And a client-facing asset.
    layout.client_path("elevator-pitch.html").write_text("<html></html>", encoding="utf-8")

    dest = tmp_path / "delivery"
    client_bundle(layout, dest)

    assert (dest / "client" / "elevator-pitch.html").exists()
    assert not (dest / "internal").exists()
    assert not contains_internal(dest)


# ---------------------------------------------------------------------------
# 8.3 — client-instance cloning never mutates the template (Property 11)
# ---------------------------------------------------------------------------

def test_clone_creates_instance_with_source_material(tmp_path):
    template = _make_template(tmp_path)
    instance = clone_for_client(template, "acme")
    assert instance.root == template.clients_dir / "acme"
    # Source docs + module library are present in the clone.
    for name in PROGRAMME_DOCS:
        assert (instance.root / name).exists()
    assert (instance.module_dir(1, "leadership") / "module.md").exists()
    # Fresh output skeleton exists and is empty of generated content.
    assert instance.internal_dir.is_dir()
    assert instance.client_dir.is_dir()


def test_clone_does_not_mutate_template(tmp_path):
    template = _make_template(tmp_path)
    before = _hash_tree(template.root)
    # Remove the clones subtree from the snapshot comparison (it's created by clone).
    clone_for_client(template, "acme")
    after = _hash_tree(template.root)
    # Every original template file is byte-identical; only new files under clients/ were added.
    for rel, digest in before.items():
        assert after.get(rel) == digest, f"template file changed: {rel}"
    new_files = set(after) - set(before)
    assert new_files, "clone should have added files"
    assert all(rel.startswith("clients/") for rel in new_files)


def test_two_client_clones_are_isolated(tmp_path):
    template = _make_template(tmp_path)
    a = clone_for_client(template, "acme")
    b = clone_for_client(template, "globex")
    a.client_path("pitch.html").parent.mkdir(parents=True, exist_ok=True)
    a.client_path("pitch.html").write_text("acme pitch", encoding="utf-8")
    assert not b.client_path("pitch.html").exists()
