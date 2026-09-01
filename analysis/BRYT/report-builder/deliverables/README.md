# Report Builder — Client Deliverables

A suite of client-facing deliverables generated from the Report Builder spec
(`.kiro/specs/report-builder/`) and its Phase 0 analysis
(`analysis/BRYT/report-builder/`). Built with the D55 `spec-to-deliverables`
skill suite; branding is D55 + BRYT Energy.

## What's here

| Deliverable | File(s) | Built by |
|---|---|---|
| **Summary presentation** | [`outputs/presentation-preview.html`](outputs/presentation-preview.html) | `build_standalone_html.py` |
| **Executive summary** | [`outputs/report-builder-exec-summary.html`](outputs/report-builder-exec-summary.html) · [`.pdf`](outputs/report-builder-exec-summary.pdf) | `walkthroughs/report_builder_exec_summary.py` |
| **Technical walkthrough** | [`outputs/report-builder.html`](outputs/report-builder.html) · [`.pdf`](outputs/report-builder.pdf) | `walkthroughs/report_builder.py` |
| **Data model** | [`outputs/data-model.html`](outputs/data-model.html) · [`.pdf`](outputs/data-model.pdf) | `walkthroughs/data_model.py` |
| **API reference (OpenAPI 3.1)** | [`api/report-builder-api.yaml`](api/report-builder-api.yaml) · [`api/report-builder-api.html`](api/report-builder-api.html) | `api/build_html.py` |
| **Estimate spreadsheet** | `BRYT Report Builder Estimates.xlsx` | `generate_estimates.py` |

- The **presentation** is a standalone, auto-scaling 16:9 HTML deck (11 slides).
- The **walkthrough** and **data model** are standalone HTML plus A4 PDF, images
  embedded as base64 so the files are portable.
- The **API HTML** is fully self-contained (spec + Redoc runtime both inlined) —
  it opens offline with zero external references.

## Single source of truth for effort figures

No day number is hardcoded anywhere. `generate_estimates.py` parses the spec's
`tasks.md` (38 tasks across 8 phases), classifies and weights each task, and
writes the spreadsheet. `figures.py` reads the spreadsheet's authoritative
**Task Detail** rows and every generator imports from it. So a single edit
propagates everywhere on the next regenerate.

Current total: **~24 developer days** (~15 required core build + ~9 optional testing).

> The figures are **inferred** from the task breakdown — the spec carries no day
> numbers of its own. The day-weighting table at the top of
> `generate_estimates.py` (and the per-task `OVERRIDES`) is the main lever a
> reviewer will want to adjust.

## Regenerate everything

```bash
python analysis/BRYT/report-builder/deliverables/regenerate_all.py
```

Options:

- `--no-pdf` — skip the (slower) PDF rendering, HTML only
- `--no-estimates` — keep manual spreadsheet edits instead of regenerating it
  from `tasks.md`

To change effort figures, either edit the **Task Detail** tab of the spreadsheet
then run with `--no-estimates`, or adjust the weighting table in
`generate_estimates.py` and run normally. Run `python figures.py` to print the
current figures.

## One-time setup

```bash
pip install openpyxl playwright pyyaml pypdf
python -m playwright install chromium
```

## Verification (how these were checked)

- **PDFs** — A4 (595×842 pt), correct page counts (walkthrough 21, data model 7),
  no orphaned headings.
- **HTML** — served on localhost and measured in a browser: all images loaded,
  7 screens + 6 tables + 2 architecture diagrams + 1 pipeline in the walkthrough,
  cover background applied, no horizontal overflow; deck 11 slides with all
  figures populated; API HTML with 14 operations and no external references.

## Notes

- The API spec marks inferred request/response shapes with `ASSUMPTION:` — these
  should be confirmed against the implementation.
- Content mirrors the spec and the Phase 0.5 decisions; where detail is inferred
  it is flagged as an assumption so the client can confirm.
