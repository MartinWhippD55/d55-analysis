# Phase 0.5 — Open questions resolved

> Task 0.5 (see [`plan.md`](plan.md)). Closes the working assumptions in the
> requirements' **Assumptions and Open Questions** section
> ([`requirements.md`](../../../.kiro/specs/report-builder/requirements.md)) and the
> residual open items carried forward from Task 0.3
> ([`schema/join-manifest.md`](schema/join-manifest.md)).
>
> These decisions feed **Task 0.6 (`design.md`)**. Requirement IDs (e.g. `R5.5`)
> point at the approved requirements. Where a decision is an engineering default
> open to a product/cost tweak, it is flagged **[confirm]** — but it is concrete
> enough to unblock design.

---

## Summary table

| # | Open question | Decision |
|---|---|---|
| Q1 | Preview execution | Server-side **bounded Athena query** (`LIMIT 100`), same generate→verify path. Not a client-side sample. |
| Q2 | Screen-01 "View" target | Opens the **builder** (R1.4). Runs/results reached via the Run & history modal. |
| Q3 | CSV retention | **Retain indefinitely** for MVP; lifecycle hook designed but not enabled. |
| Q4 | Run-completion notifications | **In-portal polling/refresh only**. No email/push for MVP. |
| Q5 | Query-bound defaults | Run: **100,000 rows / 50 GiB** scan. Preview: **100 rows / 1 GiB** scan. Configurable. |
| Q6 | Report_Store split | **Primary in DynamoDB** (single table); **versioned JSON snapshot in S3** on save; CSVs in Result_Store S3. |
| Q8 | Multi-account scoping | Default **`bryt_number IN (Authorised_Bryt_Numbers)`**; optional narrowing to one member. |
| R1 | `loa_activity` role pin | Customer Portal → pin on **`customer_bryt_number`** only; `tpi_bryt_number` is content. |
| R2 | `ecoes_activity` as-of anchor | **Exclude from the MVP allow-list** (unverifiable in dev, no per-row date); defer. |
| R3 | `customer_id` type cast | Cast **int→varchar** on `customer_id` joins (`CAST(supply.customer_id AS varchar)`). |

Assumptions **6 (Bedrock)** and **9 (bryt field name)** were already closed in
Tasks 0.4 and 0.2 respectively. Assumption **7** is Q6 below. The **MVP
allow-list is the 9 dev-verified tables** (see R2).

---

## Q1 — Preview execution (requirements assumption 1, R5)

**Decision: run a small server-side bounded Athena query (`LIMIT 100`) through
the same Query_Generator → Query_Verifier path as a full run — not a client-side
sample.**

- The generator produces a query bounded to ≤100 rows, pinned to the
  Authorised_Bryt_Numbers, and subject to the same verification as runs — this is
  exactly what **R5.5** already mandates, so a client-side sample is not viable.
- A client-side "sample" would require first pulling a larger, less-scoped result
  to the browser and trimming it there — a security regression that defeats the
  pin-and-verify model (R10, R11). Rejected.
- Preview is **synchronous** and does **not** queue a Run (R5.4). It runs under a
  **10 s** budget (R5.8) with a tighter scanned-bytes bound than a full run (see
  Q5) and the `EXPLAIN` dry-run in front of it (Task 0.4) to fail fast.
- Cost is contained by `LIMIT 100` + the preview byte bound; Athena still scans
  per the query, so the byte bound is the real cost control, not the row limit.

## Q2 — Screen-01 "View" target (requirements assumption 2, R1.4)

**Decision: "View" opens the report in the builder (screen 02). No separate
output-only landing.**

- Confirmed by both **R1.4** and the mockup: *"View opens the report in the
  builder, where running the query and the full execution history live (05)."*
- Runs and downloadable results are reached from the builder's **Run & history**
  modal (screen 05), keeping a single mental model. An "output-only" role is not
  in scope (no sharing/roles — Out of Scope).

## Q3 — CSV retention (requirements assumption 3, Out of Scope)

**Decision: retain completed CSV results in S3 indefinitely for MVP.**

- The Out-of-Scope list explicitly excludes "CSV retention/expiry handling", so
  MVP does not implement expiry.
- Result_Store is a private, versioned, server-side-encrypted bucket with public
  access blocked (**R17.4**).
- **Design the hook, don't enable it:** the CDK bucket definition reserves an S3
  lifecycle-policy slot (documented, disabled) so an expiry rule can be switched
  on later without a data-model change. Nothing about expiry is surfaced in the
  UI now.

## Q4 — Run-completion notifications (requirements assumption 4)

**Decision: in-portal polling / manual Refresh only. No email or push for MVP.**

- The Run & history modal is the surface: **R7.1** shows a Queued row within 3 s,
  **R7.8** refreshes statuses within 3 s. The modal polls while open; the user can
  also click Refresh.
- Async Athena runs for bounded queries are typically short, so email (SES) /
  toast / WebSocket push is unnecessary infrastructure for MVP. **[confirm]** as a
  future enhancement if long-running queries become common.

## Q5 — Concrete query-bound defaults (requirements assumption 5, R13)

**Decision (all configurable per R13.6, range-validated per R13.7, enforced by
the Query_Verifier per R13.5):**

| Context | Max rows | Max scanned bytes |
|---|---|---|
| **Full run** | **100,000** | **50 GiB** (53,687,091,200) |
| **Preview** | **100** (R5) | **1 GiB** (1,073,741,824) |

- 100,000 rows is a generous CSV for a non-technical portal user while staying
  well inside R13.3's 1..1,000,000 ceiling.
- 50 GiB scan is inside R13.4's ≤1 TiB ceiling and, at Athena's ~$5/TB, caps a
  single run at a few dollars — a safe guardrail, not a target. **[confirm]** the
  exact ceiling with whoever owns the Athena cost budget.
- Preview's tighter 1 GiB keeps it inside the 10 s budget (Q1/R5.8).

## Q6 — Report_Store split: DynamoDB vs S3 (requirements assumption 7, R14/R17)

**Decision: the Report_Design lives primarily in the DynamoDB single table; a
versioned JSON snapshot is written to S3 on each save; run CSVs live in the
separate Result_Store S3 bucket.**

- **Why DynamoDB is primary:** a Report_Design (selected tables, columns, joins,
  filters, sort) is small JSON, far under the 400 KB item limit. The My Reports
  list (R1, ≤5 s), owner-scoped CRUD (R16.1), and update-in-place on re-save
  (R6.7) all want a fast, key-scoped store — that is DynamoDB, not S3 GETs.
- **Why S3 too (satisfies R17.4):** R17.4 requires report-design objects to live
  in a versioned/encrypted S3 bucket. We honour it by writing a **versioned JSON
  snapshot on each save** — it gives design history and restore (R14.3, R14.5)
  and export, but is **off the read path**.
- **Result CSVs** go to the distinct Result_Store bucket (R14.8, R7.4).
  Conversation history stays in DynamoDB, scoped to report + owner (R14.2).

**Provisional single-table key design** (to feed Tasks 0.6 / 1.3 / 1.4):

| Entity | PK | SK | Notes |
|---|---|---|---|
| Report | `USER#<effectiveId>` | `REPORT#<reportId>` | GSI1 on name for A–Z / Z–A sort + search (R1.6/R1.7) |
| Conversation msg | `USER#<effectiveId>` | `REPORT#<reportId>#MSG#<ts>` | per-report history (R14.2) |
| Run | `USER#<effectiveId>` | `REPORT#<reportId>#RUN#<runNo>` | GSI on status/started for recency + list (R7.2) |

`<effectiveId>` is the effective Portal_User identity (Admin_Override email when
present) — every read/write is scoped by it (R10.8). Provisional; finalise in 0.6.

## Q8 — Multi-account report scoping (requirements assumption 8)

**Decision: by default a report filters to the FULL Authorised_Bryt_Numbers set
via `bryt_number IN (:b1, :b2, …)`, with optional UI narrowing to a single
selected Bryt_Number that MUST be a member of the set.**

- Matches the Trusted_Context definition and **R10.6** (a targeted Bryt_Number
  must be a member). **R11.1** already verifies the filter restricts results to a
  **subset** of Authorised_Bryt_Numbers — an `IN` list is a subset, so no
  requirement change is needed.
- **Manifest impact:** the `:bryt_number` bind generalises to a bind **list**
  (one or more). The pin predicates become `... IN (:authorised_bryt_numbers)`;
  single-account selection just passes a one-element list. Documented in the
  manifest `conventions`.
- Single-account narrowing is a builder affordance, never a security relaxation —
  the server still intersects against the resolved set.

---

## Residuals carried from Task 0.3

### R1 — `loa_activity` role pin (was `direct-role`)

**Decision: pin `loa_activity` on `customer_bryt_number` only. Treat
`tpi_bryt_number` as a non-pinning content column.**

- The Report Builder ships inside the **Customer Portal**; its signed-in users
  are customers, so the customer side is the correct scope.
- The `loa_tpi__account` join stays in the manifest as content but is **not** used
  to establish the pin under a customer login. If TPI logins are ever added, add a
  role-based `tpi_bryt_number` pin + a table-specific verifier rule then.
- Net effect for MVP: `loa_activity` behaves like a **`direct`** pin on
  `customer_bryt_number` (generalised to `IN (:authorised_bryt_numbers)` per Q8).

### R2 — `ecoes_activity` as-of anchor

**Decision: exclude `ecoes_activity` from the MVP allow-list. Defer to a later
phase.**

- It is not present in the dev twin (so the pin is schema-verified only, never
  value-checked) and it has no clean per-row event date, so the effective-date
  window that protects every other `via-mpan` table cannot be applied per row.
- **Fail closed:** we do not allow-list a table whose pin we cannot verify and
  whose tenancy window we cannot enforce. This makes the **MVP allow-list the 9
  dev-verified tables** (6 `direct` + `supply_activity`'s mapping + the 3
  windowed `via-mpan` consumption/reading tables).
- Re-admit when (a) a scoped prod Lake Formation grant allows value verification
  and (b) an as-of anchor is agreed — candidate: `master_record_created_datetime`
  as the snapshot as-of, resolved against the supply window containing it.

### R3 — `account ↔ supply` `customer_id` type mismatch

**Decision: cast int → varchar on the `customer_id` join predicate:
`CAST(supply_activity.customer_id AS varchar) = account_activity.customer_id`.**

- `account_activity.customer_id` is `string`, `supply_activity.customer_id` is
  `int`. Casting the **int side to varchar** avoids failed `string→int` parses if
  the string side ever holds a non-numeric value.
- Encoded on the `account__supply` join in the manifest. The same treatment
  applies to any other `customer_id` join where one side is `int`
  (`account__financial`, `account__statement`) — flagged in the manifest pending
  per-table type confirmation. These are **content** joins, so lower risk than a
  pin, but must be encoded so auto-join emits valid Athena SQL.
