# Find-Bugs Snapshot -- 2026-06-24

Point-in-time defect snapshot for the IP and DBT codenames, produced via `/find-bugs IP` and `/find-bugs DBT`. Includes the label-backfill action taken during the same session.

## Scope

In-scope initiatives sourced from `programme-report/2026-05-22/initiatives.xlsx`:

- **IP** (9 initiatives): UBT-13416, UBT-13417, UBT-13418, UBT-13419, UBT-13420, UBT-13421, UBT-13422, UBT-13423, UBT-13424
- **DBT** (10 initiatives): UBT-13473, UBT-12542, UBT-13504, UBT-13505, UBT-13506, UBT-13507, UBT-13508, UBT-13509, UBT-13510, UBT-13511

Defects discovered via `parent in (initiatives + linked stories) AND issuetype in ("Defect", "Defect Sub-task", "Bug")`. Linked stories walked through `Polaris work item link` and `Relates` link types (UBT-13504 and UBT-13506 use `Relates`).

The xlsx snapshot used for scope is ~5 weeks old at time of writing; consider re-running `/programme-completion` before relying on these CSVs for cross-stream reporting.

## Headline numbers

| Codename | Total | Closed | Open | % Closed |
|---|---:|---:|---:|---:|
| IP | 69 | 69 | 0 | 100% |
| DBT | 58 | 54 | 4 | 93% |
| **Combined** | **127** | **123** | **4** | **97%** |

Open defects are all DBT and live on UBT-13504 (2), UBT-13506 (1), UBT-13507 (1). See `open-defects.csv` for detail.

## Labelling action taken in this session

The snapshot fetched 64 defects without a `DEV_TEST` / `SYSTEM_TEST` origin tag (34 IP, 30 DBT). Applied the reporter-based convention as an additive label edit (existing `release-notes-generated`, `defect`, `peer-review-feedback`, `PR_FIX_REGRESSION` were preserved):

- **IP SYSTEM_TEST reporters** (formal system test pass): Gary Cannon, Mike Sanusi
- **DBT SYSTEM_TEST reporters** (broader set -- confirmed by user during the session): Gary Cannon, Mike Sanusi, Stacie.Cohen, Rebecca.Bakewell
- **DEV_TEST**: everyone else (internal dev test pass / peer-review feedback)

The `origin` column in the per-defect CSVs reflects the post-labelling state.

Saved to memory: `reference_dbt_system_test_reporters.md` documents the broader DBT system-test set so future `/find-bugs DBT` runs don't flag Stacie.Cohen / Rebecca.Bakewell as mislabelled reporters.

## Files

| File | Contents |
|---|---|
| `combined-summary.csv` | Per-codename totals: total / closed / open / % closed, SYSTEM_TEST + DEV_TEST counts, open status breakdown |
| `per-initiative-rollup.csv` | Defect counts per initiative for both codenames (19 rows) |
| `reporters.csv` | Reporter cross-rollup with IP + DBT splits and currently-open counts |
| `ip-defects.csv` | All 69 IP defects with key, summary, status, parent, initiative, reporter, assignee, origin, labels, updated |
| `dbt-defects.csv` | All 58 DBT defects with same shape |
| `open-defects.csv` | The 4 currently-open defects across both codenames (all DBT in this snapshot) |

CSV `labels` column uses `|` as the separator between tags.

## Flags worth noting

- **UBT-13505** (Debt Management: Generic Communication Triggers and Logic) had zero defects logged at snapshot time -- worth confirming with the team whether that initiative has been tested yet.
- **No `Bug`-type results** in either codename -- both use `Defect Sub-task` exclusively.
- Two peer-review-feedback defects (UBT-15264, UBT-15270) and one fresh design-review defect (UBT-15679) remain open on DBT.
