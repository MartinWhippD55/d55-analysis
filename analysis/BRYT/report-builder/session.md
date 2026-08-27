# Report Builder — Session Handoff

**Read this first.** It tells a fresh session what we're building, where things
live, what's done, and what to do next.

---

## What we're building

A self-service report/query builder for the Angular Customer Portal. A
non-technical customer drags tables onto a flow canvas, picks columns, connects
joins, and iterates in plain language with an AWS Bedrock assistant. Reports are
private to the signed-in user (scoped by **bryt number** from the JWT), run
asynchronously against Athena, and produce downloadable CSVs from S3. Backend
lives in a new repo, `BrytReportBuilder`, mirroring the BrytBusinessServices
patterns.

## Where things live

| Document | Path | Purpose |
|---|---|---|
| Overview | [`overview.md`](overview.md) | Scope, users, flow, technical direction |
| Mockups | [`screen-mockups.md`](screen-mockups.md) | Wireframes for the 7 screens |
| Requirements | [`../../../.kiro/specs/report-builder/requirements.md`](../../../.kiro/specs/report-builder/requirements.md) | Approved EARS requirements (18) — source of truth |
| Design | [`../../../.kiro/specs/report-builder/design.md`](../../../.kiro/specs/report-builder/design.md) | Task 0.6: full design — domain model, security spine, run pipeline, API, CDK, frontend, 13 correctness properties |
| Task list | [`plan.md`](plan.md) | Phased, checkable plan across sessions |
| Schema dump | [`schema/`](schema/) | Glue catalog: `glue-tables-raw.json` (raw) + `schema.md` (readable) + `bryt-number-audit.md` (Task 0.2 pin/join audit) |
| Join_Manifest | [`schema/join-manifest.json`](schema/join-manifest.json) + [`schema/join-manifest.md`](schema/join-manifest.md) | Task 0.3: canonical join/pin manifest (JSON) + format & rationale |
| Bedrock approach | [`bedrock-approach.md`](bedrock-approach.md) | Task 0.4: Converse tool-use vs managed Agents decision + AWS citations |
| Open questions | [`phase-0.5-decisions.md`](phase-0.5-decisions.md) | Task 0.5: the 6 requirement assumptions + multi-account scoping + 3 manifest residuals, resolved |

## Status

- **Current phase:** Phase 0 complete → **Phase 1 — Backend foundations** next
- **Done:** Requirements written and refined (18 requirements, EARS, reviewed).
  **Task 0.1** — Glue schema pulled into `schema/`. **Task 0.2** — bryt-number
  audit → `schema/bryt-number-audit.md`: 6 tables directly pinned, 5 reached via
  `mpan` (join to `supply_activity`/`account_activity`), 2 Jira tables have no
  customer scope (recommend excluding). Value-checked in the dev twin. Design
  flags to carry forward: (a) `bryt_number` = `BRYT`+6 digits, `mpan` fixed
  13-char (no normalisation to join); (b) **mpan → bryt is many over time**
  (change-of-tenancy) so mpan-keyed tables need the supply **effective-date
  window** in the pin, not mpan-equality alone, and the verifier must reject an
  unjoined query over them; (c) `loa_activity` has two bryt columns — pin by the
  signed-in user's role.
  **Task 0.3** — Join_Manifest drafted → `schema/join-manifest.json` (canonical,
  format = **JSON**) + `schema/join-manifest.md` (rationale). It **separates
  `pins` (security scoping to `:bryt_number`) from `joins` (content/UX)**, defines
  the `supply_mpan` mapping (UNNEST of `supply_activity.supplies[]`), and encodes
  the effective-date window on all 4 `via-mpan` pins. Excludes both Jira tables +
  `consumption_activity_view_test`.
  **Task 0.4** — Bedrock approach decided → `bedrock-approach.md`: **roll our own
  Converse API tool-use** in a `BrytReportBuilder` Lambda, **not** managed Bedrock
  Agents/return-of-control. The dry-run itself is Athena `EXPLAIN` (validates SQL +
  catalog, no data scan, not charged). Converse keeps the loop, Trusted_Context
  injection, `Conversation_Store` persistence, audit logging, and `toolChoice`-forced
  validate in our code, with the independent `Query_Verifier` outside the model.
  **Task 0.5** — open questions resolved → `phase-0.5-decisions.md` (manifest
  bumped to v0.2.0). Preview = server-side bounded Athena query (`LIMIT 100`) via
  the same generate→verify path; screen-01 View opens the builder; CSVs kept
  indefinitely for MVP (lifecycle hook reserved but disabled); in-portal
  polling/Refresh only; bound defaults **run 100k rows / 50 GiB, preview 100 rows
  / 1 GiB** (configurable); Report_Design primary in DynamoDB + versioned S3
  snapshot on save, run CSVs in Result_Store S3; scope to
  `bryt_number IN (:authorised_bryt_numbers)` with optional single-member
  narrowing. Manifest residuals closed: **loa_activity** pins customer-only on
  `customer_bryt_number`; **ecoes_activity** excluded from the MVP allow-list
  (deferred, fail-closed); **customer_id** joins cast int→varchar. **MVP
  allow-list = the 9 dev-verified tables.**
  **Task 0.6** — design written → `.kiro/specs/report-builder/design.md`.
  Consolidates 0.1–0.5 (no new decisions). Structure: Overview + requirement
  traceability; Architecture (flow/system mermaid, repo layout, key-decisions
  table); Domain model (`ReportDesign` TS interfaces, graph mapping, round-trip,
  validation); **Security & verification spine** = 3 independent layers
  (server-side identity/bryt resolution → pure `Query_Generator` that pins from
  Trusted_Context only, incl. the `supply_mpan` CTE + effective-date window →
  independent `Query_Verifier` pre-exec + result-set, both outside the model);
  Components (Catalog fail-closed, Assistant Converse loop + mutation/validate
  tools, Step Functions run pipeline, Preview, download, API route table); Data
  models (DynamoDB single-table keys/GSIs, S3 snapshot + Result_Store, Run types);
  CDK topology (per-env role = IAM + Lake Formation); Frontend architecture; **13
  correctness properties** mapped to requirements; Error handling; Testing.
  **Task 0.7** — formal spec checklist generated →
  `.kiro/specs/report-builder/tasks.md`. **38 ordered, checkable tasks** across 8
  phases, each annotated with its requirements + the correctness property (P1–P13)
  it upholds, plus a per-task Mermaid dependency graph + 11 execution waves. The
  **security spine (Tasks 5–10) is sequenced before any execution path** — no query
  runs before `Query_Verifier` exists and is property-tested. No new decisions.
  **Phase 0 (Design & decisions) is now complete.**
- **In progress:** _nothing yet_
- **Next action:** **Phase 1** in [`plan.md`](plan.md) / Task 1 in
  [`tasks.md`](../../../.kiro/specs/report-builder/tasks.md) — scaffold the
  `BrytReportBuilder` repo (`api/`, `cdk/`, `shared-lib/`) mirroring
  `reference-repos/BrytBusinessServices`. Still deferred: prod value verification
  of the mpan mapping + medium-confidence joins (needs a scoped Lake Formation
  grant).
- **AWS access note:** **prod** (`bryt-report`, acct 837413265725) works for Glue
  metadata but **blocks Athena data queries via Lake Formation** (IAM admin ≠ LF
  data grant). For value-level data checks use the **dev twin**: profile
  **`bryt-dev`** (acct 783535217689, eu-west-2), database
  `dev_esg_ci_data_eng_master_record_db`, Athena workgroup `primary` with output
  `s3://aws-athena-query-results-eu-west-2-783535217689/reportbuilder-validate/`.
  Dev has 9 of 13 tables (no `ecoes_activity`, `_view_test`, or Jira). `bryt-proddy`
  is documented for prod metadata. See Decision log.

## How to work a session

1. Read this file, then open [`plan.md`](plan.md).
2. Find the first `[ ]` (or `[~]`) item — that's the next thing to do.
3. Mark it `[~]` when you start, `[x]` when done; add a note if it's `[!]` blocked.
4. Before ending the session, update the **Status** block above (current phase,
   what's done, next action) and add any decisions to the **Decision log** in
   `plan.md`.

## Key facts & constraints (don't re-derive)

- **Data isolation:** every query is pinned to the customer's **bryt number**,
  taken from a Cognito user attribute on the JWT and supplied server-side as
  trusted context — never from the model or user prompt. A separate verifier
  confirms the filter before execution and checks the result set before download.
- **Data source:** Glue database `rel_esg_prod_data_eng_master_record_db` is the
  initial allow-listed catalog (dev twin: `dev_esg_ci_data_eng_master_record_db`).
- **Catalog access model:** the catalog is a **curated allow-list** of
  tables/columns, not "whatever the service role can see". Access needs **IAM**
  (API actions) **and Lake Formation** (data grants) — they're separate; grants
  are per-environment (dev/prod are different accounts). Role-visible metadata ≠
  queryable. See the "Catalog access model" entry in the Decision log.
- **Joins:** auto-connected from a **Join_Manifest** of well-understood
  predicates, also fed to the agent as context. Drafted in Task 0.3 →
  `schema/join-manifest.json` (+ `.md`). Note the manifest separates **`pins`**
  (bryt-number security scoping — direct, direct-role for `loa`, and via-mpan
  through the `supply_mpan` UNNEST with the effective-date window) from **`joins`**
  (content/UX predicates); a content join on `mpan` alone never establishes the pin.
- **Bedrock approach:** decided (Task 0.4) — **roll-our-own Converse API
  tool-use** in a Lambda, not managed Agents; dry-run = Athena `EXPLAIN`. Assume
  Claude on Bedrock. See [`bedrock-approach.md`](bedrock-approach.md).
- **Backend repo:** new `BrytReportBuilder` (`api/`, `cdk/`, `shared-lib/`),
  patterned on `reference-repos/BrytBusinessServices` (contract-note).

## Open questions — CLOSED in Phase 0.5

Resolved in [`phase-0.5-decisions.md`](phase-0.5-decisions.md): preview execution
· screen-01 "View" · CSV retention · run-completion notifications · query-bound
defaults · Report_Store split · multi-account scoping · the 3 manifest residuals
(loa role pin, ecoes anchor, customer_id cast). Only remaining deferral: prod
value verification of the mpan mapping + medium-confidence joins (needs a scoped
Lake Formation grant on prod).
