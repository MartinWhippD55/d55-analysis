# Requirements Document

_Report Builder — Proof of Concept (POC)_

## Introduction

This is the **proof-of-concept (POC)** cut of the Report Builder. It is a
deliberately stripped-down clone of the full feature
(`.kiro/specs/report-builder/`) whose only job is to **showcase the core
experience to the client**: visually assemble a report by dragging tables onto a
canvas and picking columns, refine it in plain language with an AWS Bedrock
assistant, preview it, run it, and download a CSV.

Everything that exists to make the feature safe, multi-tenant, and
production-grade is **out of scope for the POC** and deferred to the full spec on
green-light. In particular the entire **governance & security spine** —
per-customer data isolation, the independent query verifier, output verification,
prompt-injection defence, configurable query bounds, and admin-override identity
resolution — is **not** built here. Instead the POC runs against a **single,
configured demo scope** (one demo customer / bryt number) so the demo still shows
realistic single-customer data without the isolation machinery.

Production infrastructure is likewise simplified: no DynamoDB single-table design,
no Step Functions async pipeline, no per-environment IAM + Lake Formation role, no
JWT authorizer. The POC uses the simplest thing that demos well and can be thrown
away or hardened later.

> **This POC is throwaway-quality by design.** When the client approves, the full
> `report-builder` spec — not this one — is what gets built. Nothing here should be
> mistaken for the production contract.

Source of truth for scope, screens, and flow (shared with the full spec):
`analysis/BRYT/report-builder/overview.md` and `screen-mockups.md`. POC-specific
scoping lives in `analysis/BRYT/report-builder-poc/`.

## Relationship to the full spec

| Full spec requirement | POC treatment |
|---|---|
| R1 My Reports | **Kept, simplified** — flat list, single demo user, no JWT scoping. |
| R2 Builder canvas | **Kept** — core demo. |
| R3 Column selection | **Kept** — core demo. |
| R4 Assistant drawer | **Kept** — the star of the demo. |
| R5 Preview | **Kept, simplified** — bounded sample, no formal verification step. |
| R6 Save | **Kept, simplified** — lightweight persistence so a report reopens. |
| R7 Run & history | **Kept, simplified** — run + download CSV; no cancel, shallow history. |
| R8 Shared Report_Design model | **Kept** — needed by canvas + assistant. |
| R9 Agent→SQL | **Kept, simplified** — generate SQL; dry-run `EXPLAIN` optional. |
| R10 Data isolation (bryt numbers) | **Deferred** — replaced by a single configured demo scope. |
| R11 Output verification | **Deferred**. |
| R12 Prompt-injection defence | **Deferred**. |
| R13 Query bounds | **Deferred** — a single fixed `LIMIT` only. |
| R14 Persistence | **Deferred** — minimal store, no S3 snapshot / conversation store. |
| R15 Run lifecycle | **Simplified** — Queued→Running→Complete/Failed; no Cancelled. |
| R16 Backend APIs | **Trimmed** — core endpoints only. |
| R17 Repo structure & prod patterns | **Deferred** — lightweight structure, no SFN/DDB/LF. |
| R18 Catalog & Join_Manifest | **Kept, simplified** — serve the allow-list + manifest; no fail-closed rigor. |
| R19 Bryt resolution + admin override | **Deferred** — single configured demo scope. |

## Glossary

- **Report_Builder_POC**: The proof-of-concept report/query builder (frontend + backend).
- **Demo_User**: The single signed-in user the POC runs as. No multi-user scoping.
- **Demo_Scope**: A single configured bryt number (or equivalent filter) the POC
  applies to every query so the demo shows one customer's data. Configured, not
  resolved per request. This is the POC stand-in for the full spec's
  Authorised_Bryt_Numbers and exists only so the demo is realistic — it is **not**
  a security boundary.
- **Report_Design**: The shared, serialisable model representing a report —
  selected tables, columns, joins, filters, and sort order.
- **Flow_Canvas / Data_Table_Palette / Column_Picker / Assistant**: as in the full spec.
- **Catalog**: The curated, allow-listed set of tables and columns.
- **Join_Manifest**: The manifest of join predicates between Catalog tables.
- **Query_Generator**: Translates a Report_Design into Athena SQL.
- **Run / Run_Status**: One execution of a report's query and its lifecycle state
  (Queued, Running, Complete, Failed).

## Requirements

### Requirement 1: My Reports (Screen 01, simplified)

**User Story:** As a Demo_User, I want a simple list of saved reports, so that I can open or create one during the demo.

#### Acceptance Criteria

1. WHEN the Demo_User opens the My Reports screen, THE Report_Builder_POC SHALL display the saved reports for the Demo_User.
2. THE Report_Builder_POC SHALL display, for each listed report, the report name and the actions View and Delete.
3. WHEN the Demo_User selects "+ New Report", THE Report_Builder_POC SHALL open the Flow_Canvas builder with an empty Report_Design.
4. WHEN the Demo_User selects View on a report, THE Report_Builder_POC SHALL open that report's Report_Design in the Flow_Canvas builder.
5. WHEN the Demo_User selects Delete on a report, THE Report_Builder_POC SHALL remove that report from the store and the list.
6. IF the Demo_User has no saved reports, THEN THE Report_Builder_POC SHALL display an empty-state message inviting them to create one.

_Deferred to full spec: JWT scoping, per-user ownership, search/sort, error/retry states, load-time SLAs._

### Requirement 2: Builder Canvas (Screen 02)

**User Story:** As a Demo_User, I want to assemble a report visually on a canvas, so that I can design a report without writing SQL.

#### Acceptance Criteria

1. THE Report_Builder_POC SHALL display a searchable Data_Table_Palette listing each allow-listed Catalog table with its name and column count.
2. WHEN the Demo_User drags a table from the palette onto the Flow_Canvas, THE Report_Builder_POC SHALL open the Column_Picker for that table.
3. THE Report_Builder_POC SHALL render each table on the Flow_Canvas as a node showing its selected columns and an "X of N selected" summary.
4. WHEN the Demo_User drags from one node's edge to another, THE Report_Builder_POC SHALL create a join using the predicate defined in the Join_Manifest for that table pair.
5. WHILE two joined nodes are displayed, THE Report_Builder_POC SHALL display a join line with a join-condition badge between them.
6. IF the Demo_User attempts to join two tables with no Join_Manifest predicate, THEN THE Report_Builder_POC SHALL reject the join and display a message that the tables cannot be joined.
7. WHEN the Demo_User selects the remove control on a node, THE Report_Builder_POC SHALL remove that table and its joins from the Report_Design.
8. WHEN the Demo_User edits the report name in the header, THE Report_Builder_POC SHALL update the report name in the current Report_Design.
9. THE Report_Builder_POC SHALL provide Preview, Ask assistant, Run, and Save actions in the builder header.
10. WHEN the Demo_User enters text in the palette search, THE Report_Builder_POC SHALL display only tables whose name contains the text (case-insensitive).

### Requirement 3: Column Selection (Screen 03)

**User Story:** As a Demo_User, I want to choose which columns a table contributes, so that my report includes only the data I need.

#### Acceptance Criteria

1. WHEN the Column_Picker opens for a table, THE Report_Builder_POC SHALL list all allow-listed columns from the Catalog, showing each column's name, data type, and a key tag on join/primary keys.
2. WHEN the Column_Picker opens for a newly added table, THE Report_Builder_POC SHALL pre-select the key columns and display the "X of N selected" count.
3. WHEN the Demo_User selects "Select all", THE Report_Builder_POC SHALL select every currently displayed column and update the count.
4. WHEN the Demo_User toggles an individual column, THE Report_Builder_POC SHALL update that column's selected state and the count.
5. WHEN the Demo_User enters text in the column filter, THE Report_Builder_POC SHALL display only columns whose name contains the text (case-insensitive).
6. WHEN the Demo_User confirms with at least one column selected, THE Report_Builder_POC SHALL record the selected columns and place the node on the canvas.
7. IF the Demo_User confirms with zero columns selected, THEN THE Report_Builder_POC SHALL keep the picker open and display a message that at least one column is required.

### Requirement 4: Assistant Drawer and Agent-Driven Editing (Screen 04)

**User Story:** As a Demo_User, I want to refine my report in plain language with an assistant, so that the demo shows conversational editing.

#### Acceptance Criteria

1. WHEN the Demo_User selects "Ask assistant", THE Report_Builder_POC SHALL open the Assistant drawer while keeping the canvas visible.
2. WHEN the Demo_User submits a natural-language message, THE Report_Builder_POC SHALL send the message together with the current Report_Design to the Assistant.
3. WHEN the Report_Builder_POC receives an applied-change response, THE Report_Builder_POC SHALL update the shared Report_Design and reflect the change on the canvas.
4. WHEN the Assistant applies a change, THE Assistant SHALL return a description of each change and an applied-change summary.
5. THE Assistant SHALL read and write the same Report_Design structure the Flow_Canvas edits.
6. IF a request cannot be satisfied within the allow-listed Catalog and Join_Manifest, THEN THE Assistant SHALL decline, explain the limitation, and leave the Report_Design unchanged.
7. WHEN the Demo_User closes the drawer, THE Report_Builder_POC SHALL return to full-width editing with the current Report_Design retained.

_Deferred to full spec: prompt-injection defence and audit logging (R12), message-length hard limits and timeout error handling as governance concerns._

### Requirement 5: Report Preview (Screen 06, simplified)

**User Story:** As a Demo_User, I want a quick sample of my report's output, so that I can sanity-check the layout before running.

#### Acceptance Criteria

1. WHEN the Demo_User selects Preview, THE Report_Builder_POC SHALL display a dialog showing a sample of at most 100 result rows, presenting only the selected columns in Report_Design order.
2. WHEN the preview dialog is displayed, THE Report_Builder_POC SHALL display a filter and sort summary strip.
3. WHEN the Demo_User selects Preview, THE Report_Builder_POC SHALL NOT queue an asynchronous Run.
4. WHEN the preview is generated, THE Query_Generator SHALL produce a query bounded to at most 100 rows and scoped to the Demo_Scope.
5. WHILE a preview is generating, THE Report_Builder_POC SHALL display a progress indicator.
6. WHEN the Demo_User selects Close, THE Report_Builder_POC SHALL dismiss the dialog and return to the builder.
7. IF preview generation fails, THEN THE Report_Builder_POC SHALL display an error in the dialog and leave the Report_Design unchanged.

_Deferred to full spec: the independent verification step over preview output, 10s hard timeout as a governance guarantee._

### Requirement 6: Save Report (Screen 07, simplified)

**User Story:** As a Demo_User, I want to save my report design, so that I can reopen it from My Reports during the demo.

#### Acceptance Criteria

1. WHEN the Demo_User selects Save, THE Report_Builder_POC SHALL display a form containing a report name field, an optional description, and the tables used as badges.
2. WHEN the Demo_User confirms with a non-empty name, THE Report_Builder_POC SHALL persist the serialised Report_Design.
3. IF the Demo_User confirms with an empty name, THEN THE Report_Builder_POC SHALL prevent the save and display a message that a name is required.
4. WHEN a save completes, THE Report_Builder_POC SHALL make the saved report appear in My Reports.
5. WHEN the Demo_User saves a report that already exists, THE Report_Builder_POC SHALL update it in place rather than create a duplicate.

### Requirement 7: Run and Download (Screen 05, simplified)

**User Story:** As a Demo_User, I want to run my report and download the CSV, so that the demo ends in a real result.

#### Acceptance Criteria

1. WHEN the Demo_User selects "Run now", THE Report_Builder_POC SHALL start a Run and display it with Run_Status Queued, transitioning to Running and then to Complete or Failed.
2. THE Report_Builder_POC SHALL display this report's recent runs, showing each run's number, started time, Run_Status, and row count.
3. WHEN a Run reaches Complete, THE Report_Builder_POC SHALL offer a Download CSV action.
4. WHEN the Demo_User selects Download CSV, THE Report_Builder_POC SHALL provide the CSV result for that Run.
5. WHERE a Run is Failed, THE Report_Builder_POC SHALL display the error message.
6. WHEN the Demo_User selects Refresh, THE Report_Builder_POC SHALL retrieve and display the current Run_Status.

_Deferred to full spec: async Step Functions pipeline, Cancel, deep 50-run history in the user's local time zone, presigned owner-scoped download URLs, result verification before download._

### Requirement 8: Shared Report-Design Domain Model

**User Story:** As a Demo_User, I want the canvas and the assistant to edit one consistent design, so that visual and conversational edits stay in sync.

#### Acceptance Criteria

1. THE Report_Builder_POC SHALL represent a report as a single Report_Design containing selected tables, columns per table, joins, filters, and sort order.
2. THE Report_Builder_POC SHALL use the same Report_Design for both the Flow_Canvas editor and the Assistant.
3. WHEN a Report_Design is serialised and then deserialised, THE Report_Builder_POC SHALL reproduce the same selected tables, columns, joins, filters, and sort order.
4. THE Report_Builder_POC SHALL map the Report_Design to the flow graph such that each node is one selected table and each edge is one join.
5. IF a Report_Design references a table or column not in the Catalog, or a join not in the Join_Manifest, THEN THE Report_Builder_POC SHALL reject it as invalid, naming the offender.

### Requirement 9: Agent-to-SQL Translation (simplified)

**User Story:** As a Demo_User, I want my design turned into a working query, so that runs and previews produce results.

#### Acceptance Criteria

1. WHEN a Run or preview is requested, THE Query_Generator SHALL translate the current Report_Design into executable Athena SQL.
2. THE Query_Generator SHALL reference only tables and columns present in the allow-listed Catalog.
3. THE Query_Generator SHALL construct joins using only Join_Manifest predicates.
4. THE Query_Generator SHALL scope every generated query to the Demo_Scope and apply a fixed row `LIMIT`.
5. IF the Report_Design references a disallowed table/column or an undefined join, THEN THE Query_Generator SHALL prevent execution and surface a validation error naming the offender.

_Deferred to full spec: forced dry-run `EXPLAIN` before finalisation with a 30s timeout (R9.4/R9.9) as a governance guarantee, and the independent Query_Verifier (R11). A best-effort `EXPLAIN` may be included for demo polish but is not a gate._

### Requirement 10: Catalog and Join Manifest (simplified)

**User Story:** As a Demo_User, I want a curated set of tables and joins, so that I can build reports over well-understood demo data.

#### Acceptance Criteria

1. THE Catalog SHALL expose only the allow-listed demo tables and columns.
2. THE Data_Table_Palette SHALL list only tables present in the Catalog.
3. WHEN the Demo_User selects a table, THE Column_Picker SHALL list only that table's allow-listed columns.
4. THE Join_Manifest SHALL define the join predicates used to auto-connect Catalog tables, and THE Report_Builder_POC SHALL supply it to the Assistant as context.

_Deferred to full spec: fail-closed behaviour on Glue unavailability (R18.6), Lake-Formation-gated live intersection — the POC may serve a static/cached catalog for reliability during the demo._

## Assumptions

1. The POC runs as a single Demo_User against a single configured Demo_Scope; no
   JWT, no per-request identity resolution, no admin override.
2. Data is the dev twin (`dev_esg_ci_data_eng_master_record_db`) or a small
   fixture dataset — whichever demos most reliably.
3. Persistence can be the simplest available store (a single table or even local
   JSON) — durability and production data patterns are out of scope.
4. Runs may execute synchronously or with a lightweight poll; a full async
   Step Functions pipeline is out of scope.

## Out of Scope (deferred to the full `report-builder` spec on green-light)

- **The entire governance & security spine:** per-customer data isolation (R10),
  output verification (R11), prompt-injection defence (R12), configurable query
  bounds (R13), the independent Query_Verifier, and bryt-number resolution +
  admin override (R19).
- Multi-user / multi-tenant scoping; JWT authorizer.
- Production infrastructure: DynamoDB single-table design, versioned/encrypted S3
  buckets with lifecycle rules, Step Functions async run pipeline, per-environment
  IAM + Lake Formation execution role.
- Run cancellation, deep run history, presigned owner-scoped downloads,
  conversation-history persistence store.
- Sharing, teams, folders, scheduling, CSV retention/expiry.
