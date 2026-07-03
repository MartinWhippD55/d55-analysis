---
inclusion: manual
---

# Summary Presentation

Produce a branded, exec-level HTML slide deck summarising a set of specs: a title slide, an estimate summary table, one slide per spec with a headline figure and key points, and a next-steps slide. Standalone HTML that opens in any browser and auto-scales to fill the viewport. Reference: `analysis/BRYT/contract-note/build_standalone_html.py`.

Read `deliverables-toolkit` first.

## Steps

### Step 1: Gather the content

1. One slide per spec: a headline (effort figure from the `figures` module), a one-line summary, and 4-6 concise bullets of what it delivers.
2. A summary table slide: per-estimate required/total days, with a total row — all pulled from `figures`, never hardcoded.
3. Title and next-steps slides (open questions count, delivery order, etc.).

### Step 2: Build the standalone HTML

1. 16:9 slides (960×540 base), branded: full-bleed title slide using the background asset + gradient overlay; content slides on the brand gradient. Embed logos/background as base64.
2. Pull every figure from `figures` (`fmt()`, `grand_total()`), so the deck stays in sync with the spreadsheet.
3. Add the **auto-scale script**: set `document.body.style.zoom` to fit the viewport width (preserve 16:9, cap ~1.9x, recompute on resize). Use `zoom`, not `transform: scale` (see toolkit). This makes it render at a comfortable size by default instead of a small fixed box.
4. Custom list markers (e.g. chevrons): pin them to the first-line box so they align with the text (see the marker-alignment gotcha).

### Step 3: Verify

Serve on localhost, load in the browser, and measure: slide count, that figures rendered (not placeholders), the slide fills ~95% of viewport width at a typical size, and no horizontal overflow. Optionally check a wider viewport to confirm the cap behaves.

## Notes

- Keep it exec-level: short bullets, one headline figure per slide, minimal prose.
- The deck is the last thing to regenerate since it summarises the others.
