# Report Builder POC — Task List

A short, phased plan for the **proof of concept**. It is the working-plan
companion to the formal POC spec checklist at
[`.kiro/specs/report-builder-poc/tasks.md`](../../../.kiro/specs/report-builder-poc/tasks.md).
Keep [`session.md`](session.md) in step — it is the entry point a fresh session
reads first.

**Legend:** `[ ]` todo · `[~]` in progress · `[x]` done · `[!]` blocked ·
`*` optional / polish

Requirement references (e.g. `R4.3`) point at
[`.kiro/specs/report-builder-poc/requirements.md`](../../../.kiro/specs/report-builder-poc/requirements.md).

---

## Phase A — Foundations

- [ ] **A.1** Scaffold the POC project (`api/` + `web/`), domain folders. (tasks.md 1)
- [ ] **A.2** Define `core` domain types — `ReportDesign` etc. (same shapes as the
  full spec so they carry forward). (R8; tasks.md 2)
- [ ] **A.3** Bring in the Join_Manifest + pick the minimal demo table set; define
  `DEMO_SCOPE` + fixed `LIMIT`s. (tasks.md 3)

## Phase B — Query core

- [ ] **B.1** `validateDesign` — allow-list + manifest correctness check. (R8.5; tasks.md 4)
- [ ] **B.2** `Query_Generator` — design → Athena SQL, scoped to `DEMO_SCOPE`,
  fixed `LIMIT`, bound parameters. (R9; tasks.md 5)
- [ ] **B.3** `Report_Design` serialise/deserialise round-trip. (R8.3; tasks.md 6)

## Phase C — Backend services

- [ ] **C.1** Catalog service (static/cached allow-list + manifest). (R10; tasks.md 7)
- [ ] **C.2** Reports CRUD against a simple store. (R1, R6; tasks.md 8)
- [ ] **C.3** Assistant Converse loop + mutation tools — **the star**. (R4; tasks.md 9)
- [ ]* **C.4** Optional `validate_query` (`EXPLAIN`) polish — not a gate. (tasks.md 10)

## Phase D — Run, preview, download

- [ ] **D.1** Run handler: generate → Athena → CSV (no Step Functions). (R7; tasks.md 11)
- [ ] **D.2** CSV download handler. (R7.3, R7.4; tasks.md 12)
- [ ] **D.3** Preview handler (bounded, synchronous). (R5; tasks.md 13)

## Phase E — Frontend

- [ ]* **E.1** Flow-canvas library spike (`ngx-xyflow` vs `f-flow`). (tasks.md 14)
- [ ] **E.2** Client `Report_Design` model + graph mapping. (R8.2, R8.4; tasks.md 15)
- [ ] **E.3** Screens: My Reports, canvas, column picker, assistant drawer, run,
  preview, save. (R1–R7; tasks.md 16)

## Phase F — Demo readiness

- [ ] **F.1** Seed a demo report + demo data; script the assistant moment. (tasks.md 17)
- [ ] **F.2** End-to-end demo run-through — smooth and repeatable. (tasks.md 18)

## Deliverables (client-facing)

- [x] **Estimate spreadsheet + summary deck** generated from the POC `tasks.md`.
  → [`deliverables/`](deliverables/): `generate_estimates.py` (spreadsheet),
  `figures.py` (single source of truth), `build_standalone_html.py` (10-slide
  deck), `regenerate_all.py`. **POC total ≈ 35.5 developer days** (30.5 required +
  5 optional), ~half the full feature's ~78. Regenerate:
  `python analysis/BRYT/report-builder-poc/deliverables/regenerate_all.py`.

---

## Decision log

Record notable POC decisions here (date · decision · why).

- **2026-08-28 · POC cloned from the full report-builder assets.** Created
  `.kiro/specs/report-builder-poc/` (requirements/design/tasks) +
  `analysis/BRYT/report-builder-poc/` (overview/plan/session) as a stripped clone
  of the full feature. **Kept:** the core demo experience — builder canvas, column
  picker, **assistant drawer (the star)**, preview, run→CSV, light My Reports/Save,
  and the shared `Report_Design` model + Catalog/Join_Manifest that feed them.
  **Stripped (deferred to the full spec on green-light):** the entire governance &
  security spine (data isolation R10, output verification R11, injection defence
  R12, query bounds R13, bryt resolution + admin override R19, the independent
  Query_Verifier) and all production infra (DynamoDB single-table, versioned S3,
  Step Functions pipeline, per-env IAM + Lake Formation role, JWT authorizer),
  plus run cancellation / deep history / presigned downloads / conversation
  persistence. **Why:** the demo needs to prove the *experience*, not the
  plumbing; the POC runs as one `Demo_User` against one configured `DEMO_SCOPE` so
  it is single-tenant and does not need the isolation machinery. **Reuse, don't
  duplicate:** the POC references the shared mockups, schema, Join_Manifest, and
  Bedrock approach in the full analysis folder rather than copying them. **On
  green-light** we build the full `report-builder` spec, not a hardened POC; the
  kept pieces seed that build.

- **2026-08-28 · POC deliverables set generated (stripped clone).** Created
  `analysis/BRYT/report-builder-poc/deliverables/` as a lean clone of the full
  feature's deliverables — **kept** the estimate spreadsheet (`generate_estimates.py`
  → `BRYT Report Builder POC Estimates.xlsx`), the figures single-source-of-truth
  (`figures.py`), and the standalone summary deck (`build_standalone_html.py` →
  `outputs/presentation-preview.html`, 10 slides), orchestrated by
  `regenerate_all.py`. **Dropped** the full set's technical walkthrough (HTML+PDF),
  data-model doc (HTML+PDF), and OpenAPI reference — a POC is a demo pitch, not a
  production design package. POC weighting table is lighter than the full feature
  (no `security_core`, no heavy `infrastructure`, no formal `testing` suite
  categories). **Result: ≈ 35.5 developer days** (30.5 required + 5 optional
  polish) across 6 phases — roughly half the full feature's ~78, which is the
  headline story for the client (prove the concept at ~half the cost, then commit
  to the full build). Deck narrative leads with kept-vs-stripped so the client
  sees exactly where the POC line sits. Branding assets copied from the full
  deliverables. Verified: `regenerate_all.py` runs clean; deck renders in-browser.
