# BRYT Contract Note Rework - Outputs

## What this is

Client-facing deliverables for the BRYT Energy contract note rework project. Contains all assets needed to play back the 5 estimates to the client (exec-level presentation, detailed spreadsheet, wireframes, and flow diagrams).

## Contents

| File | Description |
|------|-------------|
| `presentation-preview.html` | Standalone HTML presentation (8 slides, D55 + Bryt branded). Open in any browser. |
| `BRYT Contract Note Estimates.xlsx` | Task breakdown spreadsheet with formula-driven summary. Edit days in "Task Detail" tab → Summary auto-calculates. |
| `BRYT Contract Note Rework - Estimates.pptx` | PowerPoint version of the presentation (generated via python-pptx). |
| `open-questions.md` | 11 open questions requiring client confirmation before/during implementation. |
| `docusign-flow.png` | Technical sequence diagram — DocuSign integration (Estimate 2). |
| `docusign-flow-simple.png` | Simplified flowchart — DocuSign integration (stakeholder-friendly). |
| `01-template-list.png` | Wireframe: Template list screen (Est 1). |
| `02-template-edit.png` | Wireframe: Template edit with version badges + History button (Est 1). |
| `03-rules-config.png` | Wireframe: Rules engine configuration (Est 1). |
| `04-section-editor.png` | Wireframe: pdf-me section editor modal (Est 1). |
| `05-shared-sections.png` | Wireframe: Shared sections library (Est 1). |
| `06-version-history.png` | Wireframe: Section version history panel (Est 1). |
| `01-template-edit-data-sources.png` | Wireframe: Template edit with data sources panel (Est 3b). |
| `01-bespoke-list.png` | Wireframe: Bespoke contract notes list (Est 4). |
| `02-bespoke-editor.png` | Wireframe: Bespoke contract editor with reference panel (Est 4). |

## PDF Walkthroughs

Per-estimate technical walkthrough documents — the detailed companion to the exec-level presentation. Each one explains the background context, how the solution works, key design decisions, an annotated screen-by-screen tour (interactions + the data model behind each screen), and a delivery breakdown.

| File | Description |
|------|-------------|
| `estimate-1-walkthrough.pdf` | Estimate 1: PDF / Template Management. Full walkthrough with architecture + pipeline diagrams, all 6 screen mockups annotated, rules engine explainer, and data model. |
| `estimate-1-walkthrough.html` | Standalone HTML source for the above (embedded base64 images). |
| `estimate-2-walkthrough.pdf` | Estimate 2: DocuSign Integration. Headless e-signature pipeline — send/completion phase flows, both DocuSign sequence diagrams, external integrations, open questions, and data model. |
| `estimate-2-walkthrough.html` | Standalone HTML source for the above (embedded base64 images). |
| `estimate-3-walkthrough.pdf` | Estimate 3: Training & Data Sources. Brief 3a (training/enablement) intent plus full 3b (data source extensibility) — Unified Studio/Glue/Athena flow, data sources panel mockup, enrichment pipeline, and data model. |
| `estimate-3-walkthrough.html` | Standalone HTML source for the above (embedded base64 images). |
| `estimate-4-walkthrough.pdf` | Estimate 4: Bespoke Contracts. Pipeline skip, bespoke list + editor mockups, on-demand rendering and history, manual DocuSign trigger, and data model. |
| `estimate-4-walkthrough.html` | Standalone HTML source for the above (embedded base64 images). |
| `estimate-5-walkthrough.pdf` | Estimate 5: Comparison Audit. Developer-operated Step Function tool — per-record comparison flow, Graph API + Bedrock architecture, findings model, open questions (M365 dependency), and delivery breakdown. |
| `estimate-5-walkthrough.html` | Standalone HTML source for the above (embedded base64 images). |

All five estimates now have walkthrough documents.

### Data Model

| File | Description |
|------|-------------|
| `data-model.pdf` | DynamoDB table & record reference across Estimates 1-4. Each record rendered with its PK/SK key pattern, attribute table, and GSIs. |
| `data-model.html` | Standalone HTML source for the above. |

## API Specification

An OpenAPI 3.1 spec for the Admin Portal API surface (Estimates 1 + 3b + 4, plus the Estimate 2 DocuSign webhook) lives in `analysis/BRYT/contract-note/api/`:
- `contract-note-api.yaml` — the spec itself
- `contract-note-api.html` — a fully self-contained Redoc rendering (open in any browser, no network needed)

See `api/README.md` for scope, assumptions, and how to view/validate/regenerate.

## Scripts

All scripts are in `analysis/BRYT/contract-note/`. Run from the repo root.

| Script | Purpose | Usage |
|--------|---------|-------|
| `regenerate_all.py` | **Orchestrator.** Regenerates every deliverable (presentation HTML, all walkthroughs + data model, API HTML) from source, in order. Add `--no-pdf` to skip PDF rendering. | `python analysis/BRYT/contract-note/regenerate_all.py` |
| `figures.py` | **Single source of truth for estimate figures.** Reads the spreadsheet's Task Detail tab and exposes per-estimate day figures. All generators import from here — nothing hardcodes numbers. Run directly to print current figures. | `python analysis/BRYT/contract-note/figures.py` |
| `generate_estimates.py` | Parses all task files from `.kiro/specs/` and generates the estimates spreadsheet with auto-calculated weights. | `python analysis/BRYT/contract-note/generate_estimates.py` |
| `rebuild_summary.py` | Rebuilds the Summary sheet with SUMIFS formulas driven from the Task Detail sheet. Run after manually editing the spreadsheet structure. | `python analysis/BRYT/contract-note/rebuild_summary.py` |
| `read_estimates.py` | Reads the current spreadsheet and prints the updated figures to the console. | `python analysis/BRYT/contract-note/read_estimates.py` |
| `build_standalone_html.py` | Generates the standalone HTML presentation with embedded base64 images. Figures read from `figures.py`. Output: `outputs/presentation-preview.html`. | `python analysis/BRYT/contract-note/build_standalone_html.py` |
| `generate_presentation.py` | Generates the .pptx PowerPoint (not part of `regenerate_all.py`; run separately if needed). Figures read from `figures.py`. | `python analysis/BRYT/contract-note/generate_presentation.py` |
| `walkthroughs/build_walkthrough.py` | Reusable engine that renders a walkthrough (branded HTML + PDF) from a content module. Add `--no-pdf` to skip PDF rendering. | `python analysis/BRYT/contract-note/walkthroughs/build_walkthrough.py estimate_01` |

### Dependencies

```
pip install openpyxl python-pptx playwright
python -m playwright install chromium   # one-time, for PDF walkthrough rendering
```

### Workflow

Estimate figures flow from a single source — the spreadsheet's `Task Detail` tab — through `figures.py` into every generated document. To update figures after a technical discussion:

1. Edit task days / optional flags in the spreadsheet (`Task Detail` tab) and save. (Estimate 3a has no task breakdown; edit its row on the `Summary` sheet.)
2. Run `python analysis/BRYT/contract-note/figures.py` to verify the new totals.
3. Run `python analysis/BRYT/contract-note/regenerate_all.py` to rebuild every deliverable with the updated figures.

That's it — no hand-editing of numbers in any generator. The `.pptx` is regenerated separately via `generate_presentation.py` if required.
