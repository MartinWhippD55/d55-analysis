# Join_Manifest — `report-builder`

> Task 0.3 (R18.4/R18.5). The **canonical, machine-readable** manifest is
> [`join-manifest.json`](join-manifest.json); this file documents its format,
> the rationale, and the settled decisions. It mirrors how `schema.md` documents
> `glue-tables-raw.json`.
>
> Grounded in [`schema.md`](schema.md) and [`bryt-number-audit.md`](bryt-number-audit.md).

## What the manifest is for

The Join_Manifest is the single, curated definition of **how allow-listed tables
connect** and, critically, **how every table is pinned to a customer's bryt
number**. It is consumed by three surfaces (all downstream tasks):

- **Builder canvas** — auto-connect join predicates when a customer drops two
  tables on the flow (R2, feeds Task 2.4 / Phase 6).
- **Assistant** — fed to the Bedrock agent as context so generated SQL only uses
  known-good joins (R4, R18.5).
- **Query_Generator / Query_Verifier** — the pin predicates are the security
  spine: they define the `WHERE`/`JOIN` that scopes each table to `:bryt_number`,
  and the verifier rejects any query that doesn't honour them (R9–R13).

## Format & where it lives

- **Canonical format: JSON** (`schema/join-manifest.json`). JSON because the
  backend (`BrytReportBuilder`, TypeScript) is the primary consumer — it becomes
  a typed `shared-lib` model in Task 1.3 and is served by the Catalog API in
  Task 2.4. It is also compact enough to hand to the agent as context.
- **Lives (now):** `analysis/BRYT/report-builder/schema/` alongside the schema
  dump and audit it derives from — it is a Phase-0 design artifact.
- **Lives (later):** promoted into the `BrytReportBuilder` repo (shared-lib +
  Catalog API). The Phase-0 copy stays as the reviewed source of the decisions.

## Three kinds of relationship (don't conflate them)

The manifest deliberately separates **security pins** from **content joins**:

1. **`pins`** — how each table is scoped to the customer. This is a security
   control, not a UX convenience.
   - `direct` — the table has a `bryt_number` column:
     `WHERE <col> IN (:authorised_bryt_numbers)`. `loa_activity` is also `direct`,
     pinned on `customer_bryt_number` (Phase 0.5, R1 — customer-only login).
   - `via-mpan` — no bryt column; the table is pinned **through a join** to the
     `supply_mpan` mapping, **including the effective-date window**.

   > **Phase 0.5 (Q8):** the pin scopes to the **set** of Authorised_Bryt_Numbers
   > via `IN (:authorised_bryt_numbers)`, not a single `= :bryt_number`. A
   > single-account selection passes a one-element list whose member must be in
   > the set (R10.6). See [`../phase-0.5-decisions.md`](../phase-0.5-decisions.md).
2. **`mappings`** — `supply_mpan`, the authoritative `(bryt_number, mpan, window)`
   relation derived by unnesting `supply_activity.supplies[]`. Every `via-mpan`
   pin resolves through it.
3. **`joins`** — well-understood table-to-table predicates for the canvas and the
   agent (analytics joins). Each carries a `confidence` and a `note`.
   **A content join on `mpan` never establishes the pin** — both sides still need
   their `supply_mpan` pin join.

## The `supply_mpan` mapping

```sql
SELECT s.bryt_number, sup.mpan, sup.supply_start_date, sup.supply_end_date
FROM supply_activity s
CROSS JOIN UNNEST(s.supplies) AS t(sup)
```

`supply_activity` is the cleaner source (single-level `supplies[]` unnest);
`account_activity` reaches the same via `customer_supply[].supply[].mpan` (double
nesting) and is the fallback.

## The highest-risk rule: effective-date window (carry this into the verifier)

`mpan → bryt_number` is **many over time** (change of tenancy). In the dev twin, 7
mpans map to more than one bryt. So an mpan-keyed row belongs to a bryt **only for
the period that bryt held the supply**. The pin for a `via-mpan` table is
therefore:

```sql
JOIN supply_mpan m
  ON  t.mpan = m.mpan
  AND t.<event_date> >= m.supply_start_date
  AND (m.supply_end_date IS NULL OR t.<event_date> <= m.supply_end_date)
WHERE m.bryt_number = :bryt_number
```

- `consumption_activity` → `date`
- `meter_reading_activity` → `date(reading_date)` (timestamp → date)
- `sm_consumption_activity` → `date_only`
- `ecoes_activity` → **no clean per-row event date** (snapshot); **excluded from
  the MVP allow-list** in Phase 0.5 (R2) — see the resolved open items below.

The `Query_Verifier` (Phase 3.5) must **reject** any query that reads a `via-mpan`
table without this join to a pinned `supply_mpan`, and must **reject** mpan-only
joins that drop the window.

## Allow-list coverage

| Table | Pin kind | Key |
|---|---|---|
| `account_activity` | direct | `bryt_number` |
| `case_activity` | direct | `bryt_number` |
| `financial_activity` | direct | `bryt_number` |
| `statement_of_account_activity` | direct | `bryt_number` |
| `supply_activity` | direct | `bryt_number` |
| `loa_activity` | direct | `customer_bryt_number` (Phase 0.5 R1; `tpi_bryt_number` = content) |
| `consumption_activity` | via-mpan | `mpan` + window |
| `meter_reading_activity` | via-mpan | `mpan` + window |
| `sm_consumption_activity` | via-mpan | `mpan` + window |
| `ecoes_activity` | **excluded** (deferred) | Phase 0.5 R2 — no window, unverified in dev |
| `jira_issue_activity` | **excluded** | no customer key |
| `jira_changelog_activity` | **excluded** | no customer key |
| `consumption_activity_view_test` | **excluded** (candidate) | `_view_test` |

**MVP allow-list = the 9 dev-verified tables** (the 6 `direct` + the 3 windowed
`via-mpan` consumption/reading tables). `supply_activity` also provides the
`supply_mpan` mapping.

## Open items — resolved in Phase 0.5

Closed by [`../phase-0.5-decisions.md`](../phase-0.5-decisions.md) and encoded in
`join-manifest.json` v0.2.0:

- **`loa_activity` role pin — RESOLVED (R1).** The Customer Portal signs in
  customers, so `loa_activity` pins **customer-only** on `customer_bryt_number`
  (`kind: direct`). `tpi_bryt_number` is a non-pinning content column. Add a
  role-based TPI pin only if TPI logins are ever introduced.
- **`ecoes_activity` as-of anchor — RESOLVED (R2).** **Excluded** from the MVP
  allow-list (unverifiable in dev, no per-row event date to window on). Re-admit
  when a scoped prod LF grant allows value checks and an as-of anchor
  (candidate `master_record_created_datetime`) is agreed.
- **`customer_id` type mismatch — RESOLVED (R3).** Cast the int side to varchar
  on `account__supply`:
  `CAST(supply_activity.customer_id AS varchar) = account_activity.customer_id`.
  Same treatment flagged on `account__financial` / `account__statement` pending
  per-table type confirmation.

## Open items still deferred

- **Prod value verification.** Mapping completeness and the medium-confidence
  content joins are schema-derived / dev-checked only; confirm in prod once a
  scoped Lake Formation grant exists (deferred, per Decision log).
