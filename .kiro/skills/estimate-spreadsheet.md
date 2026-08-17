---
name: estimate-spreadsheet
description: Build an estimates spreadsheet from spec task files and expose the figures via a shared module so every generated document reads from one source of truth.
inclusion: manual
---

# Estimate Spreadsheet

Build an estimates spreadsheet from a set of spec task files and expose the figures through a shared module so every generated document reads from **one source of truth** — no hardcoded day numbers anywhere. Reference implementation: `analysis/BRYT/contract-note/generate_estimates.py`, `figures.py`, `read_estimates.py`.

## Why this matters

The failure mode to avoid: figures duplicated across the spreadsheet, the presentation, and every walkthrough, so a revised estimate silently fails to propagate. The fix is a single `figures` module that all generators import.

## Steps

### Step 1: Generate the spreadsheet from task files

1. Parse each spec's `tasks.md`, extracting sub-tasks and whether each is optional (e.g. tasks marked with `*`).
2. Classify each task and assign a day weight (infrastructure, api/backend, frontend, testing, integration, etc.). Keep the weighting table explicit and editable at the top of the script.
3. Write an xlsx with two sheets:
   - **Task Detail** — one row per task: estimate name, task id, description, category, days, optional flag. This is the raw, authoritative data.
   - **Summary** — per-estimate rollups. Use live `SUMIFS`/`COUNTIF` formulas over Task Detail so the sheet stays correct if edited in Excel.
4. For any estimate that has no task breakdown (e.g. a training/enablement line), add it as a manual row on the Summary sheet.

### Step 2: Create the shared `figures` module

Create a `figures.py` that:

1. Reads the spreadsheet's **Task Detail** rows directly with `openpyxl` (raw numbers — do not rely on Excel's cached formula values, which go stale when edited by non-Excel tools).
2. Computes per-estimate `required`, `optional`, `total`, and `task_count` (the same logic as the Summary SUMIFS).
3. Reads any manual Summary-only rows (like training) from the Summary sheet.
4. Exposes a stable API: a `FIGURES` dict keyed by stable ids (`est1`, `est2`, …), a `fmt()` helper (one decimal, trailing `.0` trimmed), an `effort_line()` helper for cover badges, and a `grand_total()`.
5. Runs as a script to print all current figures for quick verification.

### Step 3: Wire generators to it

Every generator that shows a day figure imports `figures` and interpolates from it instead of hardcoding. Add the module's directory to `sys.path` where needed so content modules can `import figures`.

### Step 4: Prove propagation

Do a round-trip test: bump one task's days in the spreadsheet, reload `figures`, assert the estimate's total moved by the expected amount, then restore. Confirms edits flow through before you rely on it. Restore the spreadsheet from git afterwards (openpyxl rewrites the binary).

## Notes

- Task Detail is the source of truth; the Summary sheet is a convenience view.
- Keep the day-weighting table visible and documented — it's the main lever reviewers will want to adjust.
- After changing figures: edit the spreadsheet, run `figures.py` to verify, then regenerate documents.
