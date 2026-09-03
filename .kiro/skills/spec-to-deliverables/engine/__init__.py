"""
spec-to-deliverables engine.

A generalised, brand-configurable, spec-parameterised port of the reference
deliverables generator. Nothing here is tied to a particular spec or repo folder:
callers pass the spec content (as DOC / deck dicts) and a BrandConfig, and choose
where outputs are written (default convention: deliverables/<spec>/).

Modules:
    brand         BrandConfig — colours, fonts, cover assets (all optional).
    walkthrough   Block-based branded HTML + A4 PDF document engine.
    presentation  Data-driven branded HTML slide deck (auto-scaling).
    figures       Read a per-spec estimates spreadsheet into a single source of truth.
    estimates     Build an estimates spreadsheet from spec tasks.md files.
    openapi_html  Self-contained (offline) Redoc HTML from an OpenAPI YAML.
    verify        PDF verification helpers (page count, size, orphan headings).
"""

from .brand import BrandConfig

__all__ = ["BrandConfig"]
