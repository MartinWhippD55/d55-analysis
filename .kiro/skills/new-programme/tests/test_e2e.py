"""End-to-end integration tests (Task 18).

- 18.1 template mode on the bundled fixture: deliverable completeness + self-containment.
- 18.2 client-instance mode: only in-scope modules get assets; template untouched.
- 18.3 reconstruct the AI-DLC structure through the skill and assert structural parity
  against the hand-built reference (skipped if the reference is not present).
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest

from engine.build_example import build_example
from engine.layout import template_layout
from engine.manifest import dimension_names, load_manifest, load_toc_titles, parse_frontmatter, validate_join_keys
from engine.module_assets import is_self_contained
from engine.models import Assessment, DimensionScore
from engine.scaffold import scaffold_programme

BUNDLE = Path(__file__).resolve().parent.parent
REPO_ROOT = BUNDLE.parents[2]
AI_DLC = REPO_ROOT / "analysis" / "D55" / "ai-dlc"


def _hash_tree(root: Path) -> dict[str, str]:
    out = {}
    for p in sorted(root.rglob("*")):
        if p.is_file():
            out[str(p.relative_to(root)).replace("\\", "/")] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


# ---------------------------------------------------------------------------
# 18.1 — template mode end-to-end
# ---------------------------------------------------------------------------

def test_template_mode_produces_complete_self_contained_asset_set(tmp_path):
    layout = build_example(tmp_path / "out", make_pdf=False)

    # Manifest + docs.
    assert layout.manifest.exists()
    assert layout.dimensions_md.exists()
    assert layout.toc_md.exists()
    assert layout.context_md.exists()
    assert layout.working_assumptions_md.exists()

    # Both modules authored with assets.
    for mid, slug in [(1, "leadership-and-investment-case"), (3, "shipping-safely")]:
        assert (layout.module_dir(mid, slug) / "module.md").exists()
        assert list((layout.module_dir(mid, slug) / "assets").glob("*.html"))

    # Internal runbook + client-facing deliverables.
    assert any(layout.internal_dir.glob("*.xlsx"))
    assert (layout.client_dir / "assessment-questionnaire.xlsx").exists()
    assert (layout.client_dir / "workshop.html").exists()
    assert (layout.client_dir / "elevator-pitch.html").exists()

    # Self-containment (Property 12) across every generated HTML.
    htmls = list(layout.client_dir.glob("*.html")) + list(layout.modules_dir.rglob("*.html"))
    assert htmls
    for h in htmls:
        assert is_self_contained(h.read_text(encoding="utf-8")), f"not self-contained: {h.name}"

    # Join keys hold for the generated programme.
    assert validate_join_keys(layout.root) == []


# ---------------------------------------------------------------------------
# 18.2 — client-instance mode
# ---------------------------------------------------------------------------

def test_client_instance_scopes_assets_and_leaves_template_untouched(tmp_path):
    # A template build we must not disturb.
    template = build_example(tmp_path / "template", make_pdf=False)
    before = _hash_tree(template.root)

    # Client-instance: governance weak (critical gate) -> module 3 only; leadership strong -> module 1 out.
    assessment = Assessment(
        client_name="Acme",
        scores=[
            DimensionScore("Leadership & Mandate", 5, 5),
            DimensionScore("Governance, Security & Compliance", 1, 4),
        ],
    )
    client = build_example(tmp_path / "client", assessment=assessment, make_pdf=False)

    # Only the recommended module got authored + assets.
    m3_assets = list((client.module_dir(3, "shipping-safely") / "assets").glob("*.html"))
    m1_assets = list((client.module_dir(1, "leadership-and-investment-case") / "assets").glob("*.html"))
    assert m3_assets and not m1_assets

    m3 = (client.module_dir(3, "shipping-safely") / "module.md").read_text(encoding="utf-8")
    m1 = (client.module_dir(1, "leadership-and-investment-case") / "module.md").read_text(encoding="utf-8")
    assert "Put guardrails in place" in m3          # authored client content
    assert "TODO" in m1                             # left as scaffold skeleton (out of scope)

    # The template build is byte-identical after the client build.
    assert _hash_tree(template.root) == before


# ---------------------------------------------------------------------------
# 18.3 — AI-DLC structural parity through the skill
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not AI_DLC.exists(), reason="AI-DLC reference not present (portable checkout)")
def test_ai_dlc_structure_reproduced_through_the_skill(tmp_path):
    # Parse the reference dimensions (## N. Name), TOC section titles, and modules.
    dim_names = []
    for line in (AI_DLC / "dimensions.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^## \d+\.\s+(.*)$", line)
        if m:
            dim_names.append(m.group(1).strip())

    toc_titles = load_toc_titles(AI_DLC / "client-operating-manual-toc.md")

    ref_module_dirs = sorted(p.name for p in (AI_DLC / "modules").glob("module-*") if p.is_dir())
    modules = []
    for folder in ref_module_dirs:
        fm = parse_frontmatter(AI_DLC / "modules" / folder / "module.md")
        mid = fm["module_id"]
        slug = folder[len(f"module-{mid}-"):]
        modules.append({
            "id": mid, "slug": slug, "title": fm["title"],
            "dimensions_covered": fm["dimensions_covered"],
            "manual_section": fm["manual_section"], "trigger": fm["trigger"],
        })

    # Reconstruct the programme through the skill's scaffold.
    layout = template_layout(tmp_path, "ai-dlc")
    violations = scaffold_programme(
        layout, name="AI Development Lifecycle", slug="ai-dlc",
        dimensions=[{"name": n, "short": n.split()[0]} for n in dim_names],
        modules=modules, manual_sections=toc_titles,
    )

    # Structural parity: joins clean, folder names + dimensions + sections reproduced.
    assert violations == [], f"reconstruction drifted: {violations}"
    generated = sorted(p.name for p in layout.modules_dir.glob("module-*") if p.is_dir())
    assert generated == ref_module_dirs
    assert dimension_names(load_manifest(layout.root)) == dim_names
    covered = {d for m in modules for d in m["dimensions_covered"]}
    assert covered.issubset(set(dim_names))         # every covered dimension exists as an axis
