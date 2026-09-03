---
name: spec-to-deliverables
description: Orchestrator that turns specs into a suite of client-facing deliverables (estimate spreadsheet, summary deck, walkthrough PDFs, OpenAPI reference, data-model doc), delegating to bundled child skills.
inclusion: manual
---

# Spec to Deliverables

Turn one or more specs (requirements / design / tasks, e.g. under `.kiro/specs/`) into a suite of polished, client-facing deliverables: an estimate spreadsheet, a summary presentation, per-spec technical walkthrough PDFs, an OpenAPI reference where APIs exist, and a data-model document where data entities exist.

This is the **parent/orchestrator** skill. It decides what to produce and delegates the actual building to focused child skills that live **alongside this file in the same folder**.

## Inputs (what to provide when invoking)

1. **`spec`** *(required)* — the name of the spec to build deliverables for, i.e. a folder `.kiro/specs/<spec>/` containing `requirements.md`, `design.md`, `tasks.md`. More than one spec may be given for a combined summary/estimate.
2. **`deliverables-dir`** *(optional)* — the output root. Defaults to **`deliverables/<spec>/`** at the repo root (one subfolder per spec). Everything this skill produces — the engine (`build_walkthrough.py`, `figures.py`, …), the `assets/`, and the rendered `outputs/` — lands under here, so a spec's deliverables are self-contained and never collide with another spec's.
3. **branding** *(optional)* — logo / background / client logo. Defaults to the assets already in `<deliverables-dir>/assets/` if present, otherwise the D55 brand assets bundled with `markdown-to-pdf`. Copy brand assets into `<deliverables-dir>/assets/` on first run so the output stays portable.

There is **no dependency on any specific spec or repo folder**. Point the skill at any spec and it builds into that spec's own `deliverables/<spec>/` directory.

## Self-sufficient bundle

Everything needed to build the deliverables is vendored here — a generalised,
brand-configurable render engine plus its tests. Dependencies are in
`requirements.txt` (`openpyxl`, `playwright`, `pypdf`, `pyyaml`); a Python
interpreter + Chromium is assumed. There is no prebuilt engine to copy from
another folder.

```
.kiro/skills/spec-to-deliverables/
  SKILL.md                 this file (orchestrator)
  deliverables-toolkit.md  shared foundation — engine API, branding, verification, gotchas
  estimate-spreadsheet.md  estimates spreadsheet + shared figures module
  spec-walkthrough-pdf.md  per-spec technical walkthrough (HTML + PDF)
  data-model-pdf.md        entity / PK-SK data-model document
  openapi-html.md          OpenAPI 3.1 YAML + self-contained Redoc HTML
  summary-presentation.md  branded HTML slide deck
  requirements.txt         bundle-local dependencies
  pytest.ini               test config
  engine/
    brand.py               BrandConfig — palette, fonts, cover assets (all optional)
    walkthrough.py         block-based branded HTML + A4 PDF document engine
    css.py                 print stylesheet, parameterised by BrandConfig
    presentation.py        data-driven branded HTML slide deck (auto-scaling)
    figures.py             read a per-spec estimates spreadsheet (single source of truth)
    estimates.py           build an estimates spreadsheet from spec tasks.md files
    openapi_html.py        self-contained (offline) Redoc HTML from an OpenAPI YAML
    verify.py              PDF verification (page count, A4 size, orphan headings)
  tests/                   engine unit + property tests
```

Run the engine from the bundle root (`python -m pytest`, or `import engine.*`).
Read a child skill by opening its file in this folder (e.g. `deliverables-toolkit.md`).

## Child skills

| Child | Produces | Use when |
|-------|----------|----------|
| `deliverables-toolkit.md` | (shared foundation — patterns, gotchas, verification) | Always read first; the others build on it |
| `estimate-spreadsheet.md` | Estimates spreadsheet (single source of truth for day figures) | Effort/estimates are in scope |
| `summary-presentation.md` | Branded HTML slide deck | The user wants an exec-level overview |
| `spec-walkthrough-pdf.md` | Per-spec branded walkthrough (HTML + PDF) | The user wants detailed per-spec documents |
| `openapi-html.md` | OpenAPI 3.1 YAML + self-contained Redoc HTML | A spec defines an API surface |
| `data-model-pdf.md` | Entity / PK-SK data-model document | A spec defines data entities (tables, records) |

## Optional worked example

A complete deliverables set built with this pattern lives at `analysis/BRYT/contract-note/` **in this repo, if present** — most useful now as a **content** reference (its `walkthroughs/*.py` show real `DOC` modules). Note it predates the vendored engine and carried its own copy of the renderer; the code of record is `engine/` in this bundle. The skill does **not** depend on the folder — if it isn't there (e.g. shared standalone), ignore it and build fresh with the engine.

## Steps

### Step 1: Understand the input specs

1. Confirm the `spec` (or specs) in scope. These are folders under `.kiro/specs/<spec>/` each containing `requirements.md`, `design.md`, `tasks.md`.
2. Read them. For each spec note:
   - Whether it has an **estimate / task breakdown** (drives the spreadsheet + presentation figures)
   - Whether it defines an **API surface** (endpoint tables, request/response shapes → OpenAPI)
   - Whether it defines **data entities** (tables, records, PK/SK patterns → data-model doc)
   - Whether it has **UI mockups / screenshots** (drives the screen-by-screen sections of walkthroughs)
3. Establish the output root `<deliverables-dir>` (default `deliverables/<spec>/`). Create it, with an `assets/` subfolder for branding and an `outputs/` subfolder for rendered files.

### Step 2: Ask the user which deliverables they want

Present a short menu and let the user choose (default to all that apply):

- **Summary presentation** — one exec-level deck covering all specs in scope
- **Per-spec walkthrough PDFs** — one detailed document per spec
- **Estimate spreadsheet** — if effort figures are wanted (also underpins figures in the other docs)
- **API reference** — offered automatically for any spec that defines an API
- **Data-model document** — offered automatically for any spec that defines data entities

Confirm `<deliverables-dir>` and the branding to use before building.

### Step 3: Read the shared toolkit

Read `deliverables-toolkit.md` (in this folder). It defines the reusable generator engine, the branding approach, the verification method, and the non-obvious gotchas that every child skill relies on. Do not skip this — most of the time saved is in these lessons.

### Step 4: Establish the single source of truth (if figures are in scope)

If any deliverable shows effort/day figures, follow `estimate-spreadsheet.md` first. It creates the spreadsheet and a shared `figures` module (under `<deliverables-dir>/`) that every other generator reads from, so numbers never get hardcoded in more than one place.

### Step 5: Build the chosen deliverables

Delegate to each relevant child skill, in this order (later ones can reuse assets/figures from earlier ones):

1. `estimate-spreadsheet.md` (if figures in scope)
2. `spec-walkthrough-pdf.md` (one per spec)
3. `data-model-pdf.md` (per spec with entities, or one combined document)
4. `openapi-html.md` (per API, or one combined spec)
5. `summary-presentation.md` (last — it summarises everything)

### Step 6: Add an orchestrator and verify

1. Create a `regenerate_all.py` in `<deliverables-dir>/` that imports `engine.*` and runs every generator in order (estimates → figures → walkthroughs → data-model → OpenAPI → deck), printing a pass/fail summary. This lets the user rebuild everything with one command after a spec or figure change.
2. Run it, and verify each artifact per the toolkit's verification method (`engine.verify` for PDFs; the Playwright browser tools for the DOM). Run `python -m pytest` from the bundle root to confirm the engine itself is sound.
3. Write or update a `README.md` in `<deliverables-dir>/` listing every deliverable and the regeneration workflow.

## Notes

- Keep any reference/example content (e.g. the optional BRYT worked example) out of new work — copy the **patterns**, not the prose.
- Prefer one child invocation per deliverable type; they are designed to be run independently as well as via this parent.
- If a spec lacks the material for a given deliverable (e.g. no API), skip it rather than inventing content. Where you must infer, mark it clearly as an assumption so the client can confirm.
