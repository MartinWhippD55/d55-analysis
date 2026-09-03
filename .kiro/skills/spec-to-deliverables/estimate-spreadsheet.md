---
name: estimate-spreadsheet
description: Build an estimates spreadsheet from spec task files and expose the figures via a shared module so every generated document reads from one source of truth.
inclusion: manual
---

# Estimate Spreadsheet

Build an estimates spreadsheet from a set of spec task files and expose the figures through a shared module so every generated document reads from **one source of truth** — no hardcoded day numbers anywhere. All outputs land in the run's `<deliverables-dir>` (default `deliverables/<spec>/`). An optional worked example is `analysis/BRYT/contract-note/` (`generate_estimates.py`, `figures.py`, `read_estimates.py`) if present in this repo — reference only, not a dependency.

Read `deliverables-toolkit.md` (in this folder) first.

## Why this matters

The failure mode to avoid: figures duplicated across the spreadsheet, the presentation, and every walkthrough, so a revised estimate silently fails to propagate. The fix is a single `figures` module that all generators import.

This is done by the vendored engine: `engine.estimates` builds the spreadsheet from tasks.md files, and `engine.figures` reads it back as the single source of truth.

## Steps

### Step 1: Generate the spreadsheet from task files

Call `engine.estimates.generate_estimates` with the specs in scope:

```python
import sys; sys.path.insert(0, ".kiro/skills/spec-to-deliverables")
from engine.estimates import generate_estimates
generate_estimates(
    task_files=[(".kiro/specs/<spec>/tasks.md", "Est 1: <name>"), ...],
    output_path="deliverables/<spec>/estimates.xlsx",
    manual_rows=[{"name": "Est 3a: Training", "total_tasks": 7,
                  "required_days": 8.0, "optional_days": 0.0}],   # estimates with no task breakdown
    # weights={...}  # optional override of engine.estimates.DEFAULT_WEIGHTS
)
```

It parses each `tasks.md` (sub-tasks; `*` marks optional), classifies + weights each task, and writes two sheets: **Task Detail** (one row per task — the authoritative data) and **Summary** (per-estimate rollups). The day-weight table is `engine.estimates.DEFAULT_WEIGHTS`; override it via `weights=` — this is the main lever reviewers adjust.

### Step 2: Create the shared `figures` module

Write a thin `deliverables/<spec>/figures.py` that wraps `engine.figures.load_figures` so every generator imports one object:

```python
import sys; sys.path.insert(0, ".kiro/skills/spec-to-deliverables")
from engine.figures import load_figures, fmt   # noqa: F401  (re-export fmt for callers)
FIG = load_figures("deliverables/<spec>/estimates.xlsx",
                   name_to_key={"Est 1: <name>": "est1", ...})
```

`load_figures` reads the raw **Task Detail** rows (not Excel's cached formula values, which go stale when edited by non-Excel tools), computes `required`/`optional`/`total`/`task_count` per estimate, folds in manual Summary rows, and skips the `TOTAL` rollup row. The returned `Figures` object exposes `.get(key)`, `.effort_line(key)`, `.grand_total(keys=None)`, and the module-level `fmt()` helper.

### Step 3: Wire generators to it

Every generator that shows a day figure imports the spec's `figures` module and interpolates from it instead of hardcoding (e.g. `FIG.effort_line("est1")`, `fmt(FIG.get("est2").total)`).

### Step 4: Prove propagation

Do a round-trip test: bump one task's days in the spreadsheet, reload figures, assert the estimate's total moved by the expected amount, then restore. Confirms edits flow through before you rely on it. Restore the spreadsheet from git afterwards (openpyxl rewrites the binary).

## Notes

- Task Detail is the source of truth; the Summary sheet is a convenience view.
- Keep the day-weighting table visible and documented — it's the main lever reviewers will want to adjust.
- After changing figures: edit the spreadsheet, run `figures.py` to verify, then regenerate documents.
