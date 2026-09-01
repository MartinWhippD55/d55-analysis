# Report Builder POC — Client Deliverables

A **stripped** client-facing deliverables set for the Report Builder **proof of
concept**, generated from the POC spec (`.kiro/specs/report-builder-poc/`) and its
analysis (`analysis/BRYT/report-builder-poc/`). It is a lean clone of the full
feature's deliverables (`../../report-builder/deliverables/`): the estimate
spreadsheet, the figures single-source-of-truth, a summary presentation, and a
technical walkthrough.

## What's here

| Deliverable | File(s) | Built by |
|---|---|---|
| **Summary presentation** | [`outputs/presentation-preview.html`](outputs/presentation-preview.html) (+ `.pdf` via `render_pdf.py`) | `build_standalone_html.py` |
| **Technical walkthrough** | [`outputs/report-builder-poc.html`](outputs/report-builder-poc.html) + [`outputs/report-builder-poc.pdf`](outputs/report-builder-poc.pdf) | `walkthroughs/build_walkthrough.py report_builder_poc` |
| **Estimate spreadsheet** | `BRYT Report Builder POC Estimates.xlsx` | `generate_estimates.py` |

- The **presentation** is a standalone, auto-scaling 16:9 HTML deck (10 slides):
  title → what the POC shows (kept) → what it defers (stripped) → estimate summary
  → the six POC phases → next steps. `render_pdf.py` renders it to a landscape,
  one-slide-per-page PDF.
- The **walkthrough** is a branded A4 document (HTML + PDF) reusing the shared
  `report-builder/mockups/` screens: what the POC keeps vs defers, the simplified
  architecture + run flow, a screen-by-screen tour at POC fidelity, demo setup,
  and the delivery breakdown. All effort figures come from the `figures` module.

## What was intentionally dropped vs the full feature

The full feature's deliverables also include a data-model document (HTML + PDF)
and a self-contained OpenAPI reference. Those are **not** part of the POC set —
the POC is a demo pitch, not a production design package. On green-light, the full
`report-builder` deliverables cover all of that.

## Single source of truth for effort figures

No day number is hardcoded anywhere. `generate_estimates.py` parses the POC spec's
`tasks.md` (18 tasks across 6 phases), classifies and weights each task, and writes
the spreadsheet. `figures.py` reads the spreadsheet's authoritative **Task Detail**
rows and the presentation imports from it. So a single edit propagates everywhere
on the next regenerate.

Current POC total: **~35.5 developer days** (30.5 required + 5 optional polish) —
roughly half the full feature's ~78 days, because the POC carries no security
spine and no production infrastructure.

> The figures are **inferred** from the task breakdown — the spec carries no day
> numbers. The POC day-weighting table at the top of `generate_estimates.py` (and
> the per-task `OVERRIDES`) is the main lever a reviewer will want to adjust. POC
> weights are deliberately lighter than the full feature's.

## Regenerate everything

```bash
python analysis/BRYT/report-builder-poc/deliverables/regenerate_all.py
```

Options:

- `--no-estimates` — keep manual spreadsheet edits instead of regenerating it
  from `tasks.md`
- `--no-pdf` — skip the walkthrough PDF render (HTML only)

To change effort figures, either edit the **Task Detail** tab of the spreadsheet
then run with `--no-estimates`, or adjust the weighting table in
`generate_estimates.py` and run normally. Run `python figures.py` to print the
current figures.

## One-time setup

```bash
pip install openpyxl playwright
python -m playwright install chromium
```

(`openpyxl` reads the spreadsheet; `playwright` + a Chromium build render the
walkthrough — and the optional presentation — to PDF. Use `--no-pdf` to skip PDF
rendering if Chromium isn't installed.)

## Notes

- The POC is throwaway-quality by design. These figures estimate the **demo
  build**, not the production build — on client green-light the full
  `report-builder` spec (with its own estimate) is what gets costed and built.
- Branding assets in `assets/` are copied from the full feature's deliverables
  (D55 + BRYT Energy).
