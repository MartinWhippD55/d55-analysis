---
inclusion: manual
---

# Spec to Deliverables

Turn one or more specs (requirements / design / tasks, e.g. under `.kiro/specs/`) into a suite of polished, client-facing deliverables: an estimate spreadsheet, a summary presentation, per-spec technical walkthrough PDFs, an OpenAPI reference where APIs exist, and a data-model document where data entities exist.

This is the **parent/orchestrator** skill. It decides what to produce and delegates the actual building to focused child skills. The worked reference implementation for everything here lives in `analysis/BRYT/contract-note/` in this repo — read it when a child skill points at it.

## Child skills

| Skill | Produces | Use when |
|-------|----------|----------|
| `deliverables-toolkit` | (shared foundation — patterns, gotchas, verification) | Always read first; the others build on it |
| `estimate-spreadsheet` | Estimates spreadsheet (single source of truth for day figures) | Effort/estimates are in scope |
| `summary-presentation` | Branded HTML slide deck | The user wants an exec-level overview |
| `spec-walkthrough-pdf` | Per-spec branded walkthrough (HTML + PDF) | The user wants detailed per-spec documents |
| `openapi-html` | OpenAPI 3.1 YAML + self-contained Redoc HTML | A spec defines an API surface |
| `data-model-pdf` | Entity / PK-SK data-model document | A spec defines data entities (tables, records) |

## Steps

### Step 1: Understand the input specs

1. Confirm which spec or specs are in scope. Typically these are folders under `.kiro/specs/<name>/` each containing `requirements.md`, `design.md`, `tasks.md`.
2. Read them. For each spec note:
   - Whether it has an **estimate / task breakdown** (drives the spreadsheet + presentation figures)
   - Whether it defines an **API surface** (endpoint tables, request/response shapes → OpenAPI)
   - Whether it defines **data entities** (tables, records, PK/SK patterns → data-model doc)
   - Whether it has **UI mockups / screenshots** (drives the screen-by-screen sections of walkthroughs)
3. Note any existing branding assets (logos, background) and the output location convention. In the reference repo these are in `assets/` and `outputs/`.

### Step 2: Ask the user which deliverables they want

Present a short menu and let the user choose (default to all that apply):

- **Summary presentation** — one exec-level deck covering all specs in scope
- **Per-spec walkthrough PDFs** — one detailed document per spec
- **Estimate spreadsheet** — if effort figures are wanted (also underpins figures in the other docs)
- **API reference** — offered automatically for any spec that defines an API
- **Data-model document** — offered automatically for any spec that defines data entities

Confirm the output directory and the branding to use before building.

### Step 3: Read the shared toolkit

Read the `deliverables-toolkit` skill. It defines the reusable generator engine, the branding approach, the verification method, and the non-obvious gotchas that every child skill relies on. Do not skip this — most of the time saved is in these lessons.

### Step 4: Establish the single source of truth (if figures are in scope)

If any deliverable shows effort/day figures, follow `estimate-spreadsheet` first. It creates the spreadsheet and a shared `figures` module that every other generator reads from, so numbers never get hardcoded in more than one place.

### Step 5: Build the chosen deliverables

Delegate to each relevant child skill, in this order (later ones can reuse assets/figures from earlier ones):

1. `estimate-spreadsheet` (if figures in scope)
2. `spec-walkthrough-pdf` (one per spec)
3. `data-model-pdf` (per spec with entities, or one combined document)
4. `openapi-html` (per API, or one combined spec)
5. `summary-presentation` (last — it summarises everything)

### Step 6: Add an orchestrator and verify

1. Create a `regenerate_all.py` that runs every generator in order and prints a pass/fail summary (see the reference repo's `regenerate_all.py`). This lets the user rebuild everything with one command after a spec or figure change.
2. Run it, and verify each artifact per the toolkit's verification method.
3. Write or update a `README.md` in the output folder listing every deliverable and the regeneration workflow.

## Notes

- Keep the BRYT/reference content out of new work — copy the **patterns**, not the prose.
- Prefer one skill invocation per deliverable type; they are designed to be run independently as well as via this parent.
- If a spec lacks the material for a given deliverable (e.g. no API), skip it rather than inventing content. Where you must infer, mark it clearly as an assumption so the client can confirm.
