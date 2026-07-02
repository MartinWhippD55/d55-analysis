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

### Still TODO

- Walkthroughs for Estimates 2 (DocuSign), 3b (Data Sources), and 4 (Bespoke Contracts) — reuse the same generator by adding a content module per estimate.

## Scripts

All scripts are in `analysis/BRYT/contract-note/`. Run from the repo root.

| Script | Purpose | Usage |
|--------|---------|-------|
| `generate_estimates.py` | Parses all task files from `.kiro/specs/` and generates the estimates spreadsheet with auto-calculated weights. | `python analysis/BRYT/contract-note/generate_estimates.py` |
| `rebuild_summary.py` | Rebuilds the Summary sheet with SUMIFS formulas driven from the Task Detail sheet. Run after manually editing the spreadsheet structure. | `python analysis/BRYT/contract-note/rebuild_summary.py` |
| `read_estimates.py` | Reads the current spreadsheet and prints the updated figures to the console. Useful after manual edits to verify totals. | `python analysis/BRYT/contract-note/read_estimates.py` |
| `build_standalone_html.py` | Generates the standalone HTML presentation with embedded base64 images (D55 + Bryt logos, background). Output: `outputs/presentation-preview.html`. | `python analysis/BRYT/contract-note/build_standalone_html.py` |
| `generate_presentation.py` | Generates the .pptx PowerPoint file using python-pptx and the D55 template. | `python analysis/BRYT/contract-note/generate_presentation.py` |
| `walkthroughs/build_walkthrough.py` | Reusable engine that renders a per-estimate walkthrough (branded HTML + PDF) from a content module. Add `--no-pdf` to skip PDF rendering. | `python analysis/BRYT/contract-note/walkthroughs/build_walkthrough.py estimate_01` |

### Dependencies

```
pip install openpyxl python-pptx playwright
python -m playwright install chromium   # one-time, for PDF walkthrough rendering
```

### Workflow

1. Edit task days in the spreadsheet (`Task Detail` tab) → Summary auto-updates
2. Run `read_estimates.py` to verify totals
3. Update figures in `build_standalone_html.py` if they've changed
4. Run `build_standalone_html.py` to regenerate the HTML presentation
5. Optionally run `generate_presentation.py` to regenerate the .pptx
