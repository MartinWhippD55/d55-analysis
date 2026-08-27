# Report Builder — Task List

A phased, multi-session plan. Check items off as they land. Keep
[`session.md`](session.md) in step with progress — it is the entry point a fresh
session reads first.

> Note: this is a working plan, distinct from the formal spec implementation
> checklist that will be generated at `.kiro/specs/report-builder/tasks.md`
> (Task 0.7).

**Legend:** `[ ]` todo · `[~]` in progress · `[x]` done · `[!]` blocked

Requirement references (e.g. `R10.3`) point at
[`.kiro/specs/report-builder/requirements.md`](../../../.kiro/specs/report-builder/requirements.md).

---

## Phase 0 — Design & decisions

Goal: turn the approved requirements into a design and resolve the open
questions. No production code yet.

- [x] **0.1 Pull the real schema.** Use the schema/data profile (currently
  **`bryt-dev`** — see the AWS access note in `session.md`) to list tables,
  columns, and data types in the master-record Glue database. Capture the raw
  output under `analysis/BRYT/report-builder/schema/`. (R18)
  (The original prod pull used `bryt-proddy` against
  `rel_esg_prod_data_eng_master_record_db`; ongoing schema/value work is on the
  dev twin `dev_esg_ci_data_eng_master_record_db`.)
  → `schema/glue-tables-raw.json` (raw) + `schema/schema.md` (readable). 13
  tables, no partition keys. `bryt_number` present on `account_activity` (col 5)
  and others — full audit is Task 0.2.
- [x] **0.2 Identify the bryt-number column(s).** Confirm which column pins each
  table to a customer, and note tables that lack one (and how they are reached
  via joins). (R10, R11)
  → `schema/bryt-number-audit.md`. **6 directly pinned** (`account_`, `case_`,
  `financial_`, `statement_of_account_`, `supply_activity` on `bryt_number`;
  `loa_activity` on **both** `customer_bryt_number` + `tpi_bryt_number`).
  **5 reachable via `mpan`** (`consumption_activity`,
  `consumption_activity_view_test`, `meter_reading_activity`,
  `sm_consumption_activity`, `ecoes_activity` via `queried_mpan`/`mpan_core`) —
  mapped to bryt through `supply_activity` (`supplies[].mpan`, cleanest) or
  `account_activity`. **2 non-customer** (`jira_issue_activity`,
  `jira_changelog_activity`) — recommend excluding from the allow-list.
  Value-level checks verified against the **dev twin** (prod blocked by Lake
  Formation) — see Decision log.
- [x] **0.3 Draft the Join_Manifest.** From the real schema, define the
  well-understood join predicates between tables. Decide the manifest format and
  where it lives. (R18.4)
  → `schema/join-manifest.json` (canonical, machine-readable) + `schema/join-manifest.md`
  (format + rationale). Format decision: **JSON**, lives in `schema/` now, promoted
  into `BrytReportBuilder` shared-lib + Catalog API later (Tasks 1.3/2.4). Manifest
  separates **`pins`** (security scoping) from **`joins`** (content/UX) and defines
  the **`supply_mpan`** mapping (UNNEST of `supply_activity.supplies[]`). All 4
  `via-mpan` pins carry the effective-date window; the `Query_Verifier` must reject
  unjoined/window-less reads of them. Open items carried forward: `loa_activity`
  role pin, `ecoes_activity` as-of anchor (no per-row date; not in dev),
  `customer_id` string/int cast.
- [x] **0.4 Investigate Bedrock approach.** Compare managed **Bedrock Agents
  (action groups / return-of-control)** vs **roll-our-own Converse API tool-use**
  for the dry-run validation tool. Cite AWS docs. Recommend one. (R9, assumption 6)
  → `bedrock-approach.md`. **Decision: roll our own Converse API tool-use** in a
  `BrytReportBuilder` Lambda; not managed Agents/RoC. Dry-run itself = Athena
  `EXPLAIN` (validates SQL + catalog, no data scan, not charged). Converse keeps
  the loop, Trusted_Context injection, `Conversation_Store` persistence, audit
  logging (R12.4), and `toolChoice`-forced validate (R9.4) in our code, with the
  independent `Query_Verifier` outside the model. Agents' RoC benefit is moot
  (Converse runs the loop natively, more simply) and its managed session state
  would clash with our Bryt-scoped store. Revisit **AgentCore** (not classic
  Agents) only if we later need managed multi-step orchestration/RAG/memory.
- [x] **0.5 Resolve open questions** (requirements Assumptions section): preview
  execution, screen-01 "View" target, CSV retention, run-completion
  notifications, concrete query-bound defaults, Report_Store split (DynamoDB vs S3).
  → `phase-0.5-decisions.md`. **Q1** preview = server-side bounded Athena query
  (`LIMIT 100`) via the same generate→verify path (not a client sample). **Q2**
  screen-01 View opens the builder (R1.4). **Q3** CSV retained indefinitely for
  MVP (expiry out of scope); lifecycle hook designed, not enabled. **Q4**
  in-portal polling/Refresh only. **Q5** defaults: run **100k rows / 50 GiB**,
  preview **100 rows / 1 GiB**, configurable. **Q6** Report_Design primary in
  DynamoDB + versioned JSON snapshot in S3 on save; CSVs in Result_Store S3
  (provisional single-table key design included). **Q8** scope to
  `bryt_number IN (Authorised_Bryt_Numbers)` with optional single-member
  narrowing. Also closed the 0.3 residuals in `join-manifest.json` v0.2.0:
  **loa_activity** pins customer-only on `customer_bryt_number`; **ecoes_activity**
  excluded from the MVP allow-list (deferred); **customer_id** joins cast
  int→varchar. **MVP allow-list = the 9 dev-verified tables.**
- [x] **0.6 Write `design.md`** in the spec: domain model, agent→SQL flow,
  persistence model, security/verification design, API contracts, CDK topology,
  frontend architecture. Ground it in 0.1–0.5.
  → `.kiro/specs/report-builder/design.md`. Sections: Overview + requirement
  traceability; Architecture (flow + system mermaid diagrams, repo structure,
  key-decisions table); **Domain model** (`ReportDesign` TS interfaces, graph
  mapping, round-trip, validation); **Security & verification spine** (Layer 1
  identity/bryt resolution, Layer 2 `Query_Generator` incl. `supply_mpan` CTE +
  window, Layer 3 independent `Query_Verifier` pre-exec + result-set, injection
  defence); Components (Catalog fail-closed, Assistant Converse loop + tools,
  Step Functions run pipeline, Preview, download, full API route table); Data
  models (DynamoDB single-table keys + GSIs, S3 snapshot + Result_Store, Run
  types); CDK topology (per-env role = IAM + LF); Frontend architecture; **13
  correctness properties** mapped to requirements; Error handling; Testing
  strategy. No new decisions — consolidates 0.1–0.5.
- [x] **0.7 Generate the formal spec `tasks.md`** from the design (the
  `.kiro/specs/report-builder/tasks.md` implementation checklist).
  → `.kiro/specs/report-builder/tasks.md`. 38 ordered, checkable tasks across 8
  implementation phases, each annotated with its requirements and the correctness
  property (P1–P13) it upholds. The **security spine** (Tasks 5–10: `validateDesign`,
  identity resolution, `Query_Generator`, `Query_Verifier`, round-trip, property
  tests) is sequenced **before any execution path**. Includes a per-task Mermaid
  dependency graph + 11 execution waves for parallelisation. Optional/deferrable
  tasks marked `*`. No new decisions — pure translation of `design.md`.

## Phase 1 — Backend foundations (`BrytReportBuilder` repo)

Goal: an empty-but-deployable skeleton following BrytBusinessServices patterns. (R17)

- [ ] **1.1** Create the `BrytReportBuilder` repo with `api/`, `cdk/`,
  `shared-lib/` and root tsconfig/package config. (R17.1)
- [ ] **1.2** Port shared HTTP + identity helpers; add **Bryt_Number resolution**
  from JWT claims. (R10.1, R17.8)
- [ ] **1.3** Define `shared-lib` types: `Report_Design`, `Run`, `Run_Status`,
  records, request/response contracts. (R8, R16)
- [ ] **1.4** CDK foundation: single DynamoDB table (PK/SK + GSIs, PAY_PER_REQUEST),
  private versioned encrypted S3 buckets, REST API shell. (R17.3, R17.4, R17.5)
- [ ] **1.5** Wire a smoke-test health route and confirm a deploy to a dev stage.

## Phase 2 — Reports CRUD API + Catalog

- [ ] **2.1** Reports create / read / update / delete / list, all scoped to
  Bryt_Number. (R16.1, R6, R1, R14.1)
- [ ] **2.2** Report_Design validation (allow-listed tables/columns, manifest
  joins) with round-trip serialise/deserialise. (R8)
- [ ] **2.3** Catalog API sourced from Glue; expose only allow-listed
  tables/columns; fail closed if the source is unavailable. (R18.1–R18.3, R18.6)
- [ ] **2.4** Serve the Join_Manifest to clients + assistant. (R18.4, R18.5)

## Phase 3 — Assistant + query generation/verification

- [ ] **3.1** Assistant chat API (Bedrock) that reads/writes Report_Design and
  returns an applied-change summary. (R4, R16.5)
- [ ] **3.2** Conversation persistence per report, scoped to Bryt_Number. (R14.2, R14.3)
- [ ] **3.3** `Query_Generator`: Report_Design → Athena SQL, catalog/manifest
  constrained, bryt-number pinned, bounded. (R9, R10.3, R13)
- [ ] **3.4** Dry-run validation tool the agent calls before finalising. (R9.4, R9.9)
- [ ] **3.5** `Query_Verifier`: independent bryt-number-filter + bounds check that
  blocks execution on failure. (R11.1–R11.2, R12.5–R12.6, R13.5)
- [ ] **3.6** Prompt-injection defences + audit logging of ignored attempts. (R12)

## Phase 4 — Run execution pipeline

- [ ] **4.1** Step Functions pipeline: generate → verify → execute (Athena) →
  write CSV → finalise, with failure-catch states. (R15, R17.6, R17.7)
- [ ] **4.2** Run queue/execute API returning run id + Queued status. (R16.2)
- [ ] **4.3** Run status + list APIs. (R16.3, R14.4–R14.7)
- [ ] **4.4** CSV result to S3 (Result_Store) + download API. (R7.3–R7.4, R16.4, R14.8)
- [ ] **4.5** Result-set output verification before download is offered. (R11.3–R11.6)
- [ ] **4.6** Cancel API for Queued/Running runs + terminal-state protection. (R16.6, R15.5–R15.7)

## Phase 5 — Preview

- [ ] **5.1** Preview API: bounded query (≤100 rows), bryt-number pinned, same
  verification as runs, no async Run queued. (R5)

## Phase 6 — Frontend (Angular Customer Portal extension)

- [ ] **6.1** Choose flow library (`ngx-xyflow` vs `f-flow`) and spike the canvas.
- [ ] **6.2** Report_Design client model + graph mapping (shared with assistant). (R8.2, R8.4)
- [ ] **6.3** My Reports screen. (R1)
- [ ] **6.4** Builder canvas: palette, nodes, joins, name edit. (R2)
- [ ] **6.5** Column picker modal. (R3)
- [ ] **6.6** Assistant drawer. (R4)
- [ ] **6.7** Run & history modal. (R7)
- [ ] **6.8** Preview dialog. (R5)
- [ ] **6.9** Save modal. (R6)

## Phase 7 — Hardening, tests, deploy

- [ ] **7.1** Security tests: cross-tenant isolation, injection, bounds, verifier. (R10–R13)
- [ ] **7.2** Unit/integration tests across API + pipeline; frontend component tests.
- [ ] **7.3** Observability: logging, tracing, alarms on verification failures.
- [ ] **7.4** CI/CD pipeline for `BrytReportBuilder`.
- [ ] **7.5** End-to-end walkthrough against a dev stage; sign-off.

---

## Decision log

Record notable decisions here as they are made (date · decision · why).

- **2026-08-27 · Formal spec `tasks.md` generated (Task 0.7).** →
  `.kiro/specs/report-builder/tasks.md`. Turned `design.md`'s components + the 13
  correctness properties into **38 ordered, checkable tasks** across 8 phases, each
  carrying its `_Requirements:_` and (where applicable) `_Upholds:_ P#` references.
  Key ordering decision: the **security spine is built and property-tested first**
  (Tasks 5–10 = `validateDesign`, identity/`Authorised_Bryt_Numbers` resolution,
  `Query_Generator`, independent `Query_Verifier`, round-trip serialise, spine
  property tests) so **no query can execute before the verifier exists and is
  tested** — Phases 5–6 (assistant, pipeline, preview) depend on it. Added a
  per-task Mermaid dependency graph + an 11-wave parallelisation schedule (matches
  the spec `tasks.md` format used elsewhere in the workspace). Optional/MVP-deferrable
  tasks flagged `*`. **No new decisions** — pure translation of the design; Phase 0
  is now complete and Phase 1 (repo scaffold, Task 1) is next.

- **2026-08-27 · Design written (Task 0.6).** → `.kiro/specs/report-builder/design.md`.
  Consolidates 0.1–0.5 into the formal design; **no new decisions**, but records
  the shape to build against. Highlights: (1) `Query_Generator` + `Query_Verifier`
  live in `shared-lib` because they run in three contexts (assistant validate,
  preview, run pipeline) and are the security spine — one impl, one test surface.
  (2) The security spine is **three independent layers** — server-side identity/
  bryt resolution (Trusted_Context), a pure generator that pins from
  Trusted_Context only, and an **independent verifier** (not a model tool) that
  re-derives its expectations from Trusted_Context + manifest and blocks pre-exec
  and post-result — so even a fully-compromised assistant cannot leak data.
  (3) `via-mpan` pin emitted as a `supply_mpan` CTE with the effective-date window;
  the generator always projects the pinning bryt column(s) internally (stripped
  from the delivered CSV if unselected) so the result-set verifier (R11.4) can run.
  (4) DynamoDB keys: Report `USER#<eid>`/`REPORT#<id>` + GSI1 name (sort/search),
  Run GSI2 recency; design JSON inline in the Report item + versioned S3 snapshot
  on save. (5) 13 correctness properties mapped to R5/R8/R10–R13/R15/R18/R19 to
  drive Task 0.7's `tasks.md`. Carry into **Task 0.7**: turn the components + the
  13 properties into the implementation checklist.

- **2026-08-27 · Open questions resolved (Task 0.5).** → `phase-0.5-decisions.md`.
  Six requirement assumptions + assumption 8 + the three 0.3 manifest residuals
  closed. Highlights and why: (Q1) **preview = server-side bounded Athena query
  (`LIMIT 100`)** through the same Query_Generator→Query_Verifier path, not a
  client sample — R5.5 already mandates a bounded/pinned/verified query, and a
  client sample would need unscoped data client-side (security regression). (Q2)
  **screen-01 View opens the builder** (R1.4 + mockup); runs/results live in the
  Run & history modal. (Q3) **CSVs retained indefinitely** for MVP — expiry is
  Out of Scope; a disabled S3 lifecycle hook is reserved in CDK. (Q4) **in-portal
  polling/Refresh only** (R7.1/R7.8); no SES/push for MVP. (Q5) concrete bounds
  (all configurable, R13.6/R13.7): **run 100k rows / 50 GiB**, **preview 100 rows
  / 1 GiB** — inside R13.3/R13.4 ceilings and ≈ a few $/run at Athena $5/TB. (Q6)
  **Report_Design primary in the DynamoDB single table** (small JSON, fast
  owner-scoped list/CRUD/update-in-place — R1/R6.7/R14.1) with a **versioned JSON
  snapshot in S3 on each save** to satisfy R17.4 + give history/restore; **run
  CSVs in the separate Result_Store S3 bucket**; provisional single-table key
  design recorded for 0.6/1.3/1.4. (Q8) **scope to
  `bryt_number IN (:authorised_bryt_numbers)`** with optional single-member
  narrowing that must be in the set (R10.6; R11.1 already verifies a *subset*).
  Residuals (encoded in `join-manifest.json` v0.2.0): **loa_activity** pins
  **customer-only** on `customer_bryt_number` (Customer Portal signs in
  customers; `tpi_bryt_number` demoted to content); **ecoes_activity** **excluded
  from the MVP allow-list** — fail closed: not in dev (never value-checked) and no
  per-row event date to window on; **customer_id** joins **cast int→varchar** so
  auto-join emits valid Athena SQL. Net: **MVP allow-list = the 9 dev-verified
  tables**. Carry into Task 0.6 (design.md): the DynamoDB key model, the
  `IN`-list pin/verifier shape, the preview vs run bound split, and the
  disabled-lifecycle Result_Store bucket.

- **2026-08-27 · Bedrock approach = roll-our-own Converse API tool-use (Task
  0.4).** → `bedrock-approach.md`. Chose the **Converse API** tool-use loop over
  managed **Bedrock Agents (action groups / return-of-control)** for the Assistant
  and its dry-run validate tool. Why: (1) the dry-run itself is just Athena
  `EXPLAIN` (validates SQL + resolves catalog metadata, **no data scan, not
  charged** by Athena), so the real question was only how the model reaches the
  tool. (2) Converse keeps the entire loop in our Lambda, so **Trusted_Context**
  (Authorised_Bryt_Numbers) injection, per-call **audit logging** of ignored
  injection attempts (R12.4), and `toolChoice`-forced validation before
  finalisation (R9.4, 30s timeout R9.9) are all ours to control, and the
  independent `Query_Verifier` (R11, R12.5–R12.6) stays entirely outside the
  model. (3) Converse is stateless, matching our Bryt-scoped `Conversation_Store`
  (R14); Agents' managed session memory would duplicate/clash with it. (4) Agents'
  return-of-control benefit (skip Lambda executors, run logic in-app) is moot —
  Converse already runs the loop in-app, with fewer moving parts and matching the
  BrytBusinessServices Lambda pattern (R17). Model portability (swap `modelId`) is
  a bonus. Carry into Task 3.1 (Assistant = Converse loop with Report_Design
  mutation tools + `validate_query`) and Task 3.4 (validate tool = `EXPLAIN`).
  Revisit **Amazon Bedrock AgentCore** (the current managed-harness offering, not
  classic Agents) only if managed multi-step orchestration / KB-RAG / long-term
  memory is later required.

- **2026-05-19 · Use the `bryt-proddy` profile, not `bryt-prod`, for account
  837413265725.** The `bryt-prod` profile is misconfigured — it carries both a
  `role_arn`/`source_profile = bryt-users` (whose static creds are invalid) and
  an `sso_session`; the AssumeRole path wins and fails with
  `InvalidClientTokenId`. `bryt-proddy` reaches the same account/region
  (837413265725 / eu-west-2) cleanly via the `bryt-prod` SSO session
  (`aws sso login --profile bryt-prod` first). Downstream schema/Athena work
  should use `bryt-proddy`. **(Superseded 2026-08-27: schema/value work now runs
  on the dev twin via `bryt-dev`; `bryt-proddy` remains for prod metadata only.)**
- **2026-08-27 · Catalog access model — allow-list, not role-reflection; IAM +
  Lake Formation per environment.** Two independent access layers govern this
  stack: **IAM** (which API actions the role may call —
  `glue:GetDatabases`/`GetTables`, `athena:StartQueryExecution`, `s3:GetObject`
  on results) and **Lake Formation** (which databases/tables/columns the role may
  actually read). They are separate: IAM admin ≠ LF data grant (this is exactly
  why `bryt-report` could list metadata but not query rows). Design implications
  to carry into Task 0.6 (security/catalog design), Task 2.3 (catalog API), and
  Phase 1.4 (CDK role):
  - The catalog is a **curated allow-list** of tables/columns (per R18.2), **not**
    "whatever the service role can see." Glue `GetTables` metadata visibility does
    not guarantee queryability (in prod all 13 tables' metadata were visible yet
    unqueryable), so role-visible ≠ usable.
  - One CDK-defined execution-role **pattern**, deployed **per environment** (dev
    783535217689 / prod 837413265725 are separate accounts with separate grants
    and different DB names — `dev_esg_ci_data_eng_master_record_db` vs
    `rel_esg_prod_data_eng_master_record_db`). Each deployment is granted LF
    `SELECT` on exactly the allow-listed tables in that account. It is **not** one
    cross-account role.
  - Catalog API intersects the allow-list with what is actually present/queryable
    and **fails closed** on gaps (R18.6).
  - Enumerating the role's actual LF grants is a **validation/health check**
    (does the role have access to everything on the allow-list?), not the source
    of the catalog.
- **2026-08-27 · Value-level checks run in DEV, not prod.** Prod (`bryt-report`,
  acct 837413265725) blocks Athena data queries via **Lake Formation** (IAM admin
  ≠ LF data grant; workgroup `prod-bryt-reporting` is otherwise fine). Rather than
  grant on prod, validation was run against the dev twin
  `dev_esg_ci_data_eng_master_record_db` (`bryt-dev`, acct 783535217689). Dev has
  9 of 13 tables (no `ecoes_activity`, `consumption_activity_view_test`, or Jira),
  which covered every pin/join check. Prod value-level confirmation (mpan-mapping
  completeness; whether a bryt is ever both customer & TPI) still needs a scoped
  LF grant or someone with prod data access — deferred.
- **2026-08-27 · Bryt-number audit done (Task 0.2).** Column-presence audit from
  the Glue catalog + dev value checks → `schema/bryt-number-audit.md`. Findings to
  carry into design: (1) `bryt_number` = `BRYT`+6 digits; `mpan` is fixed 13-char
  on both sides (no normalisation to join). (2) **mpan → bryt is many over time**
  — 7 mpans in dev map to >1 bryt via change-of-tenancy, so the mpan-keyed tables
  must be pinned with the supply **effective-date window**, not mpan-equality
  alone; the `Query_Verifier` must enforce this (highest-risk pinning area).
  (3) `loa_activity` has **two** bryt columns (`customer_bryt_number` +
  `tpi_bryt_number`, both populated on 407/410 dev rows; roles disjoint in dev) —
  pin by the signed-in user's role; needs a product decision + table-specific
  verifier rule, not the generic single-column check. (4) `jira_issue_activity`
  and `jira_changelog_activity` have no customer scope — recommend excluding from
  the allow-list.
- **2026-05-19 · Glue catalog captured (Task 0.1).** 13 tables in
  `rel_esg_prod_data_eng_master_record_db`, all unpartitioned, backed by S3 under
  `s3://rel-esg-prod-data-eng-master-record/`. Largest by width:
  `jira_issue_activity` (249 cols), `ecoes_activity` (67),
  `consumption_activity_view_test` (33, a `_view_test` — treat as candidate, not
  necessarily allow-listed). All 13 share the `_activity` naming convention.
- **2026-08-27 · Join_Manifest drafted (Task 0.3) — format JSON, pins ≠ joins.**
  Canonical manifest is `schema/join-manifest.json` (readable companion
  `schema/join-manifest.md`). Chose **JSON** over YAML/Markdown because the
  backend (`BrytReportBuilder`, TS) is the primary consumer — it becomes a typed
  `shared-lib` model (Task 1.3) served by the Catalog API (Task 2.4); the Phase-0
  copy stays as the reviewed source. Key design choices carried forward: (1) the
  manifest **separates `pins` (security scoping to `:bryt_number`) from `joins`
  (content/UX predicates)** — a content join on `mpan` never establishes the pin.
  (2) `via-mpan` tables (`consumption_activity`, `meter_reading_activity`,
  `sm_consumption_activity`, `ecoes_activity`) pin **through** the `supply_mpan`
  mapping (UNNEST of `supply_activity.supplies[]` → `bryt_number, mpan,
  supply_start_date, supply_end_date`) **with the effective-date window**; the
  `Query_Verifier` (Phase 3.5) must reject any read of them that lacks the pinned,
  windowed join. (3) `loa_activity` keeps the role-based dual-column pin as a
  table-specific verifier rule. Excluded from the allow-list: both Jira tables and
  `consumption_activity_view_test`. Residual open items (Phase 0.5): `loa_activity`
  role model, an `ecoes_activity` as-of anchor (snapshot, no per-row event date,
  not in dev), and the `account↔supply` `customer_id` string/int cast.