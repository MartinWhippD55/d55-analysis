# Bryt-number audit — `rel_esg_prod_data_eng_master_record_db`

> Task 0.2. Which column pins each table to a customer (**bryt number**), and for
> tables with no such column, how they are reached via joins. (R10, R11)
>
> Source of truth: the Glue catalog (`schema.md` / `glue-tables-raw.json`), which
> is authoritative for column presence. Live value-level verification via Athena
> is **blocked by Lake Formation** — see "Verification status" at the bottom.

## Summary

| Table | Bryt-pinning column(s) | How it's pinned |
|---|---|---|
| `account_activity` | `bryt_number` | Direct |
| `case_activity` | `bryt_number` | Direct |
| `financial_activity` | `bryt_number` | Direct |
| `statement_of_account_activity` | `bryt_number` | Direct |
| `supply_activity` | `bryt_number` | Direct |
| `loa_activity` | `customer_bryt_number` **and** `tpi_bryt_number` | Direct — **two** bryt columns (see note) |
| `consumption_activity` | — | Indirect via `mpan` → supply/account |
| `consumption_activity_view_test` | — | Indirect via `mpan` (view-test candidate) |
| `meter_reading_activity` | — | Indirect via `mpan` → supply/account |
| `sm_consumption_activity` | — | Indirect via `mpan` → supply/account |
| `ecoes_activity` | — | Indirect via `queried_mpan` / `mpan_core` → supply/account |
| `jira_issue_activity` | — | **No customer scope** — internal ops data (see note) |
| `jira_changelog_activity` | — | **No customer scope** — internal ops data (see note) |

**Tally:** 6 directly pinned · 5 reachable via `mpan` · 2 non-customer (Jira).

## Directly pinned (6)

These carry a customer bryt number as a top-level column, so the run pin is a
simple `WHERE <col> = :bryt_number` (server-supplied, per R10.3 / R11).

- `account_activity` — `bryt_number` (col 5)
- `case_activity` — `bryt_number` (col 6)
- `financial_activity` — `bryt_number` (col 6)
- `statement_of_account_activity` — `bryt_number` (col 6)
- `supply_activity` — `bryt_number` (col 4)
- `loa_activity` — `customer_bryt_number` (col 6) and `tpi_bryt_number` (col 8)

### ⚠️ `loa_activity` has two bryt columns

A Letter-of-Authority row links a **customer** (`customer_bryt_number`) to a
**third-party intermediary** (`tpi_bryt_number`). Pinning on only one side leaks
the other party's rows. The pin predicate must be decided against the portal
user's role:

- If the portal user is always the customer: pin on `customer_bryt_number`.
- If a TPI can also sign in and should see LOAs where they are the agent: the
  pin must be `customer_bryt_number = :b OR tpi_bryt_number = :b`.

This needs an explicit product decision and must be encoded in the
`Query_Verifier` (R11) as a table-specific rule, not the generic single-column
check. Flagging for Phase 0.5 / design.

## Reachable via `mpan` (5)

No bryt column; each row is keyed to a metering point (`mpan`). To pin these to a
customer they must be joined to a bryt-carrying table on `mpan`:

- `consumption_activity` — `mpan` (col 24)
- `consumption_activity_view_test` — `mpan` (col 27) — this is a `_view_test`
  table; treat as a candidate, not necessarily allow-listed (per Task 0.1 note).
- `meter_reading_activity` — `mpan` (col 13)
- `sm_consumption_activity` — `mpan` (col 5)
- `ecoes_activity` — `queried_mpan` (col 1) / `mpan_core` (col 2)

**mpan → bryt_number source.** Two tables expose the `mpan`↔`bryt_number`
relationship:

- `supply_activity`: `bryt_number` (top-level) with `supplies[].mpan` inside the
  `supplies` array<struct> — requires `UNNEST` to flatten to `(bryt_number, mpan)`.
- `account_activity`: `bryt_number` (top-level) with `mpan` nested deep in
  `customer_supply[].supply[].mpan` — also requires `UNNEST`.

`supply_activity` is the cleaner mapping source (single level of nesting on
`supplies`). The exact predicate + how to expose it is Task 0.3 (Join_Manifest).

**Security implication (R11/R13).** For these tables the bryt pin is enforced
*through the join*, not a direct column. The `Query_Verifier` must confirm the
mpan-keyed table is always joined to an authoritative `(bryt_number, mpan)`
mapping that is itself pinned — otherwise an unjoined `SELECT` over
`consumption_activity` returns cross-tenant data. This is the highest-risk area
of the pinning design.

## No customer scope (2) — recommend excluding from the allow-list

- `jira_issue_activity` (249 cols) and `jira_changelog_activity` — these are
  internal Jira project/ops data (issues, sprints, changelogs). They have no
  `bryt_number`, no `mpan`, and no other customer key. There is no safe way to
  pin them to a customer. Recommendation: **exclude both from the customer-facing
  allow-list** (R18.2). If internal reporting on them is ever wanted, that is a
  separate, non-customer-scoped surface. Confirm in Phase 0.5.

## Verification status

- **Schema-level (column presence):** ✅ confirmed from the Glue catalog.
- **Value-level:** ✅ confirmed in **dev**, not prod. Prod (`bryt-report` /
  acct 837413265725) blocks Athena data queries via **Lake Formation** (IAM
  admin ≠ LF data grant), so value checks were run against the dev equivalent
  `dev_esg_ci_data_eng_master_record_db` (`bryt-dev` / acct 783535217689,
  eu-west-2), where data access works. Dev has 9 of the 13 tables — missing
  `ecoes_activity`, `consumption_activity_view_test`, and the two Jira tables —
  but all tables needed for the pin/join checks are present.

### Dev-verified findings (2026-08-27)

- **`bryt_number` format:** `BRYT` + 6 digits, e.g. `BRYT031884`. 13-char `mpan`
  is a fixed-width string on both `supply_activity` and `consumption_activity`
  (min=max=13), so **no normalisation is needed to join on `mpan`**.
- **⚠️ mpan → bryt is many over time (cross-tenancy).** `supply_activity`
  unnested gives 1,338 (mpan, bryt) pairs but only 1,323 distinct mpans — 7 mpans
  map to more than one `bryt_number` (change of tenancy / CoT; the `supplies`
  struct carries `supply_start_date`/`supply_end_date` and
  `incoming_/outgoing_bryt_number` + `move_in/out_date`). **Consequence:** pinning
  an mpan-keyed table on `mpan = :b`'s mpans alone can leak another tenant's rows
  for periods the mpan wasn't theirs. The Join_Manifest predicate for these
  tables (Task 0.3) must include the **effective-date window**, and the
  `Query_Verifier` must enforce it — not just mpan equality.
- **Match rate is a dev-data artifact, not a join defect.** Only 1,289 of
  `consumption_activity`'s 31,861 distinct mpans resolve to a supply row, because
  dev has far more consumption loaded than supply. Completeness of the mapping is
  a **prod-only** check (deferred).
- **`loa_activity` dual-bryt is real.** 410 rows: all 410 have
  `customer_bryt_number`, 407 also have `tpi_bryt_number` (both populated on
  407). **No** bryt appears as both a customer and a TPI in dev (roles disjoint),
  which supports a role-based pin: pin on `customer_bryt_number` for a customer
  login, `tpi_bryt_number` for a TPI login. Confirm the role model in Phase 0.5.

> Value-level checks used the `bryt-dev` profile against a scratch output prefix
> `s3://aws-athena-query-results-eu-west-2-783535217689/reportbuilder-validate/`.
> Prod value-level confirmation (esp. the mpan-mapping completeness and whether a
> bryt is ever both customer and TPI) still needs either a scoped Lake Formation
> grant or someone with prod data access running the queries.
