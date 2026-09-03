---
name: spec-walkthrough-pdf
description: Produce a branded per-spec technical walkthrough as standalone HTML + A4 PDF (context, architecture, screen tour, key decisions, data model, delivery breakdown).
inclusion: manual
---

# Spec Walkthrough PDF

Produce a branded, per-spec technical walkthrough as standalone HTML + A4 PDF: background/context, how it works, architecture and flow diagrams, an annotated screen-by-screen tour where mockups exist, key design decisions, data model summary, open questions, and a delivery breakdown. Outputs land in the run's `<deliverables-dir>/outputs/` (default `deliverables/<spec>/outputs/`). Optional worked example: `analysis/BRYT/contract-note/walkthroughs/` (`build_walkthrough.py` engine + `estimate_0X.py` content modules) if present in this repo — reference only.

Read `deliverables-toolkit.md` (in this folder) first — this skill uses its engine, verification method, and gotchas.

## Steps

### Step 1: Read the spec

Read the spec's `requirements.md`, `design.md`, `tasks.md` (under `.kiro/specs/<spec>/`). Pull out: the problem/background, the architecture, the key design decisions and their rationale, the data model, any UI mockups, and the task breakdown (for the delivery section). Note whether it's UI-bearing or headless — that changes which blocks you use.

### Step 2: Write a content module

Create one content module in `<deliverables-dir>/` exposing a `DOC` dict with an ordered list of blocks. A good default structure:

1. `section` — Background (the problem and what this changes)
2. `callout` — a one-line framing of the change, or how it builds on other specs
3. `section` — How it works
4. `pipeline` / `layers` — CSS-rendered flow and architecture diagrams
5. `table` — Key design decisions (decision / choice / why)
6. `screens` — annotated mockups (interactions + "behind the screen" data notes) — **only if the spec has UI**
7. `table` — data model at a glance (or defer to the dedicated data-model document)
8. `table` — open questions with working assumptions, if the spec has unknowns
9. `table` — delivery breakdown (pull day figures from the `figures` module, never hardcode)
10. `callout` — testing note

Adapt to the spec: headless specs (pipelines, tools) lean on diagrams and tables instead of `screens`. Draw effort figures from `figures` via `effort_line()` and `fmt()`.

### Step 3: Generate

Render with the vendored engine:

```python
import sys; sys.path.insert(0, ".kiro/skills/spec-to-deliverables")
from engine.walkthrough import build_document
from engine.brand import BrandConfig
brand = BrandConfig.from_assets_dir("deliverables/<spec>/assets", eyebrow="<Programme>", date="<Month Year>")
build_document(DOC, out_dir="deliverables/<spec>/outputs", brand=brand, base_dir="deliverables/<spec>")
```

Give non-estimate documents a clean `slug` (in the `DOC`, else it's derived from the title). Cover fields (`title`, `subtitle`, `eyebrow`, `effort`, `date`) come from the `DOC` (falling back to the `BrandConfig`).

### Step 4: Verify

Per the toolkit: serve on localhost, measure the DOM (images loaded, expected block counts, no overflow), and check the PDF for page count and orphaned headings. If a mockup is a wide letterboxed screenshot, ask the user to crop it (or crop it) and regenerate.

## Notes

- Keep prose tight and factual; the value is clarity, not volume.
- Reuse CSS-rendered diagrams over embedded images where possible (see the Excalidraw gotcha in the toolkit).
- Mark any inferred detail as an assumption.
