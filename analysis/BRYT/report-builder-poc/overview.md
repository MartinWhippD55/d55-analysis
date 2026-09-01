# Report Builder POC — Overview

## What we're building

A **proof of concept (POC)** of the Report Builder — a stripped-down, demo-able
clone of the full feature (`analysis/BRYT/report-builder/` +
`.kiro/specs/report-builder/`). The goal is to put the **core experience** in
front of the client quickly: drag tables onto a flow canvas, pick columns,
connect joins, then **refine the report in plain language with an AI assistant**,
preview it, run it, and download a CSV.

If the client likes it, we build the full thing — the complete `report-builder`
spec, which layers the governance, security, and production infrastructure on top
of the pieces proven here.

## The one-line pitch to the client

*"Build a report by dragging tables and picking columns — then just tell the
assistant what you want, and watch it change."*

The demo is about the **experience**, not the plumbing.

## What the POC keeps (the core demo)

| Screen / capability | Why it's in the demo |
|---|---|
| **Builder canvas** (drag tables, joins) | The visual "no-SQL" promise. |
| **Column picker** | Shows control over exactly what's in the report. |
| **Assistant drawer** (Bedrock Converse) | **The star** — conversational editing of the live design. |
| **Preview** | Instant sanity-check of the output. |
| **Run → Download CSV** | Ends the demo on a real, tangible result. |
| **My Reports + Save** (light) | So a report can be saved and reopened live. |
| Shared **Report_Design** model + **Catalog / Join_Manifest** | The machinery that makes the canvas + assistant work. |

## What the POC strips (deferred to productionisation)

Everything that makes the feature *safe and production-grade* rather than
*demo-able* is deliberately left out and picked up in the full spec on green-light:

- **The entire governance & security spine:** per-customer data isolation,
  the independent Query_Verifier, output verification, prompt-injection defence,
  configurable query bounds, bryt-number resolution + admin override.
- **Production infrastructure:** DynamoDB single-table design, versioned/encrypted
  S3 with lifecycle, Step Functions async run pipeline, per-environment
  IAM + Lake Formation execution role, JWT authorizer.
- **Run lifecycle depth:** cancellation, deep run history, presigned owner-scoped
  downloads, conversation-history persistence.

In place of the identity/isolation stack, the POC uses a **single configured
Demo_Scope** (one demo bryt number) so the demo still shows realistic
single-customer data — but this is a demo convenience, **not** a security
boundary.

## Who it's for

- **Demo audience:** the client, evaluating whether to fund the full build.
- **Demo operator:** us, running as a single `Demo_User` against a demo dataset
  (the dev twin `dev_esg_ci_data_eng_master_record_db`, or a small fixture).

## Key user flow (the demo script)

1. **My Reports** — open the list, hit **+ New Report**.
2. **Builder canvas** — drag two tables from the palette; the column picker opens
   for each; connect them into a join.
3. **Assistant** — open the drawer and say *"only contracts ending in the next 90
   days, and add the site"*; the canvas updates as the assistant applies changes.
4. **Preview** — show a sample of the output.
5. **Run** — queue it, watch it complete, **download the CSV**.
6. **Save** — save the report; it appears back in My Reports.

## Technical direction (simplified)

- **Frontend:** Angular feature module (same target as the full spec), flow canvas
  via `ngx-xyflow` or `f-flow`.
- **Assistant:** AWS Bedrock **Converse** tool-use loop (Claude) — same approach as
  the full spec (`../report-builder/bedrock-approach.md`), minus injection defence.
- **Query execution:** `Query_Generator` → **Athena** directly (no Step Functions);
  results as CSV in S3 (or local for a local demo).
- **Scoping:** a single `DEMO_SCOPE` constant + a fixed `LIMIT`. No JWT, no
  per-request resolution, no verifier.
- **Persistence:** the simplest store that works (one table, or local JSON).

## Reused assets (not duplicated)

To keep the POC lean, it **reuses** the shared Phase 0 artefacts from the full
analysis rather than copying them:

- **Mockups:** `analysis/BRYT/report-builder/screen-mockups.md` + `mockups/`
- **Schema & bryt audit:** `analysis/BRYT/report-builder/schema/`
- **Join_Manifest:** `analysis/BRYT/report-builder/schema/join-manifest.json`
- **Bedrock approach:** `analysis/BRYT/report-builder/bedrock-approach.md`

## Explicitly out of scope (for the POC)

- All governance/security (isolation, verification, injection defence, bounds).
- Multi-user / multi-tenant; JWT auth; admin override.
- Production AWS infra (SFN, DDB single-table, versioned S3, LF role).
- Run cancellation, deep history, presigned downloads, conversation persistence.
- Sharing, teams, folders, scheduling, CSV retention/expiry.

## After the demo (green-light path)

On approval we **do not harden this POC** — we execute the full
`.kiro/specs/report-builder/` spec, which already carries the security spine and
production infrastructure. The POC's kept pieces (Report_Design model,
Query_Generator, Catalog/Join_Manifest, Converse assistant) are a genuine seed for
that build, so the work here is not thrown away.
