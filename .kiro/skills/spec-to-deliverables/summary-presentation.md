---
name: summary-presentation
description: Produce a branded exec-level HTML slide deck summarising a set of specs (title, estimate summary, per-spec slides, next steps). Standalone and auto-scaling.
inclusion: manual
---

# Summary Presentation

Produce a branded, exec-level HTML slide deck summarising a set of specs: a title slide, an estimate summary table, one slide per spec with a headline figure and key points, and a next-steps slide. Standalone HTML that opens in any browser and auto-scales to fill the viewport. Outputs land in the run's `<deliverables-dir>/outputs/` (default `deliverables/<spec>/outputs/`). Optional worked example: `analysis/BRYT/contract-note/build_standalone_html.py` if present in this repo — reference only.

Read `deliverables-toolkit.md` (in this folder) first.

## Steps

### Step 1: Gather the content

1. One slide per spec: a headline (effort figure from the `figures` module), a one-line summary, and 4-6 concise bullets of what it delivers.
2. A summary table slide: per-estimate required/total days, with a total row — all pulled from `figures`, never hardcoded.
3. Title and next-steps slides (open questions count, delivery order, etc.).

### Step 2: Build the standalone HTML

Assemble a `deck` dict (title + `slides` list of `table`/`content` slides) and render with the vendored engine:

```python
import sys; sys.path.insert(0, ".kiro/skills/spec-to-deliverables")
from engine.presentation import write_deck
from engine.brand import BrandConfig
deck = {
    "title": "<Programme> Rework", "subtitle": "Estimate Playback",
    "org": "D55 Consulting", "date": "<Month Year>",
    "slides": [
        {"type": "table", "heading": "Estimate Summary",
         "columns": ["Estimate", "Required", "Total"], "rows": [[...], ["TOTAL", ...]]},
        {"type": "content", "heading": "Est 1: <name>", "hero": "~5 days",
         "bullets": ["<b>delivers</b> …", "…"], "note": "…"},
    ],
}
write_deck(deck, "deliverables/<spec>/outputs/presentation.html",
           BrandConfig.from_assets_dir("deliverables/<spec>/assets"))
```

The engine handles the rest: 16:9 slides (960×540), full-bleed branded title slide, content/table slides on the brand gradient, base64-embedded assets, the last table row auto-styled as a total, and the **auto-scale script** (`document.body.style.zoom`, capped ~1.9x — `zoom`, not `transform: scale`, see toolkit). Pull every figure from the spec's `figures` module so the deck stays in sync with the spreadsheet; `content` slide `bullets` are trusted author HTML so `<strong>` and `&rarr;` render.

### Step 3: Verify

Serve on localhost, load in the browser, and measure: slide count, that figures rendered (not placeholders), the slide fills ~95% of viewport width at a typical size, and no horizontal overflow. Optionally check a wider viewport to confirm the cap behaves.

## Notes

- Keep it exec-level: short bullets, one headline figure per slide, minimal prose.
- The deck is the last thing to regenerate since it summarises the others.
