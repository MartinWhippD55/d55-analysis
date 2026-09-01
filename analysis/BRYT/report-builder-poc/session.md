# Report Builder POC — Session Handoff

**Read this first.** It tells a fresh session what the POC is, where things live,
what's done, and what to do next.

---

## What we're building

A **proof of concept** of the Report Builder — a stripped-down clone of the full
feature, built to **showcase the core experience to the client**: drag tables onto
a flow canvas, pick columns, connect joins, refine the report in plain language
with an AWS Bedrock assistant, preview, run, and download a CSV. It runs as a
single `Demo_User` against a single configured `DEMO_SCOPE` (one demo bryt number)
on a demo dataset. **No governance/security spine and no production infra** — those
are the full spec's job on green-light.

## Where things live

| Document | Path | Purpose |
|---|---|---|
| Overview | [`overview.md`](overview.md) | POC scope, the demo pitch, kept vs stripped |
| Working plan | [`plan.md`](plan.md) | Phased, checkable POC plan + decision log |
| Requirements | [`../../../.kiro/specs/report-builder-poc/requirements.md`](../../../.kiro/specs/report-builder-poc/requirements.md) | POC requirements + full-spec relationship table |
| Design | [`../../../.kiro/specs/report-builder-poc/design.md`](../../../.kiro/specs/report-builder-poc/design.md) | POC design + "what changed from the full design" |
| Task list | [`../../../.kiro/specs/report-builder-poc/tasks.md`](../../../.kiro/specs/report-builder-poc/tasks.md) | Formal POC implementation checklist (18 tasks) |
| Deliverables | [`deliverables/`](deliverables/) | Client estimate spreadsheet + summary deck (≈ 35.5 dev days) |

### Reused (shared with the full feature — not duplicated)

| Asset | Path |
|---|---|
| Mockups | `analysis/BRYT/report-builder/screen-mockups.md` + `mockups/` |
| Schema & bryt audit | `analysis/BRYT/report-builder/schema/` |
| Join_Manifest | `analysis/BRYT/report-builder/schema/join-manifest.json` |
| Bedrock approach | `analysis/BRYT/report-builder/bedrock-approach.md` |

### The full feature (what we build on green-light)

- `analysis/BRYT/report-builder/` + `.kiro/specs/report-builder/` — the complete
  spec with the security spine + production infrastructure.

## Status

- **Current phase:** POC spec, analysis & deliverables authored → **Phase A —
  Foundations** next (start building the demo).
- **Done:** Cloned the full report-builder assets into a stripped POC.
  `.kiro/specs/report-builder-poc/` (requirements, design, tasks, `.config.kiro`)
  and `analysis/BRYT/report-builder-poc/` (overview, plan, session) created. Scope
  decided: keep the core demo (canvas, column picker, **assistant**, preview,
  run→CSV, light My Reports/Save, shared model + catalog/manifest); strip the whole
  governance/security spine (R10–R13, R19, the Query_Verifier) and all production
  infra (SFN, DDB single-table, versioned S3, LF role, JWT), plus cancel / deep
  history / presigned downloads / conversation persistence. Substituted a single
  configured `DEMO_SCOPE` for the identity/isolation stack. **Client deliverables
  generated** → [`deliverables/`](deliverables/): estimate spreadsheet + 10-slide
  summary deck, **≈ 35.5 developer days** (30.5 required + 5 optional), ~half the
  full feature's ~78. Regenerate with
  `python analysis/BRYT/report-builder-poc/deliverables/regenerate_all.py`.
- **In progress:** _nothing yet._
- **Next action:** **Phase A** in [`plan.md`](plan.md) / Task 1 in
  [`tasks.md`](../../../.kiro/specs/report-builder-poc/tasks.md) — scaffold the POC
  project (`api/` + `web/`), then define the `core` domain types (Task 2) using the
  same `ReportDesign` shapes as the full spec so they carry forward.

## How to work a session

1. Read this file, then open [`plan.md`](plan.md).
2. Find the first `[ ]` (or `[~]`) item — that's the next thing to do.
3. Mark it `[~]` when you start, `[x]` when done; `[!]` if blocked.
4. Before ending, update the **Status** block above and add any decisions to the
   **Decision log** in `plan.md`.

## Key facts & constraints (don't re-derive)

- **This is a throwaway-quality demo.** On client green-light we build the full
  `report-builder` spec (with the spine + infra), **not** a hardened version of
  this POC. Keep POC code simple; don't gold-plate.
- **Single-tenant by construction.** One `Demo_User`, one `DEMO_SCOPE` constant
  (a single bryt number) applied by the `Query_Generator`, a fixed `LIMIT`. No
  JWT, no per-request resolution, no verifier. `DEMO_SCOPE` is a demo convenience,
  **not** a security boundary.
- **Keep the carry-forward pieces faithful.** The `Report_Design` model,
  `Query_Generator`, Catalog/`CatalogTable`/`CatalogColumn` shapes, and the
  Converse assistant are kept intact so they seed the production build — match the
  full spec's type shapes.
- **The assistant is the star.** Prioritise a smooth Converse tool-use loop over
  everything else; it's what sells the demo.
- **Assistant approach:** Bedrock **Converse** tool-use (Claude), per
  `../report-builder/bedrock-approach.md` — minus injection defence / audit /
  forced-validate, all deferred.
- **Data source:** dev twin `dev_esg_ci_data_eng_master_record_db` (profile
  `bryt-dev`, acct 783535217689, eu-west-2, workgroup `primary`) or a small
  fixture — whichever demos most reliably. Prefer `direct`-pinned tables to keep
  the demo query surface small.
- **Reuse, don't duplicate:** mockups, schema, Join_Manifest, and the Bedrock
  approach live in the full analysis folder; reference them, don't copy.

## Deferred to the full spec (do NOT build in the POC)

Governance & security spine (R10–R13, R19, Query_Verifier) · production infra
(Step Functions, DynamoDB single-table, versioned/encrypted S3 + lifecycle,
per-env IAM + Lake Formation role, JWT authorizer) · run cancellation · deep run
history · presigned owner-scoped downloads · conversation-history persistence ·
fail-closed catalog on Glue unavailability.
