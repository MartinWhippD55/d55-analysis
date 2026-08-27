# Report Builder — Overview

## What we're building

A self-service **report / query builder** for the (Angular) **Customer Portal**.
It lets a non-technical customer assemble a report visually — drag tables onto a
flow canvas, pick the columns they want from each, and connect them — then
iterate on the design in plain language with an AI assistant. When they're happy,
they save the report and run it; runs execute asynchronously against **Athena**
and produce a downloadable CSV.

The goal is to give customers ad-hoc reporting over their own data **without SQL
or engineering involvement**, while keeping the underlying query generation safe
and constrained.

## Who it's for

- **Primary user:** a signed-in Customer Portal user (non-technical). Reports are
  **private to that user** — identity is taken from their JWT. There is no
  sharing, team, or ownership concept.

## Core concepts

- **Report** — a saved, reusable design: the chosen tables, selected columns,
  joins, filters, and sort order. Lives in the user's "My Reports" list.
- **Run / execution** — one asynchronous execution of a report's query. A report
  has many runs over time (manual or, potentially, scheduled). Each run has a
  status lifecycle and, when complete, a downloadable CSV.
- **Assistant** — an AWS Bedrock–backed helper that reads and edits the live
  report design in response to natural-language requests, describing each change.

## Key user flow

1. **My Reports** — see your saved reports; open one (View) or start a New Report.
2. **Builder canvas** — drag tables from the palette onto the canvas; a column
   picker opens so you select all or individual columns; connect tables to define
   joins.
3. **Assistant drawer** — pop the assistant over the builder to refine the report
   in plain language ("only contracts ending in the next 90 days, include the
   site"); the canvas updates live as changes are applied.
4. **Preview** — a lightweight dialog showing a sample snippet of the results to
   sanity-check layout (does not run the full job).
5. **Save** — persist the design (name + optional description) so it appears in
   My Reports.
6. **Run & history** — queue an async execution and review this report's past
   runs; download the CSV when a run completes.

See [`screen-mockups.md`](screen-mockups.md) for the wireframes of each screen.

## Run lifecycle

`Queued → Running → Complete | Failed`

- **Run now** queues a separate execution via the API (ultimately an Athena
  query).
- **Complete** runs offer **Download CSV** (results stored in S3).
- **Failed** runs show a truncated error inline, with the full message on hover.
- Queued/Running runs can be **Cancelled**.

## Technical direction

- **Frontend:** Angular, as an extension to the existing Customer Portal.
- **Flow canvas:** a ReactFlow-style graph library — candidates are
  [`ngx-xyflow`](https://github.com/knackstedt/ngx-xyflow) and
  [`f-flow`](https://github.com/Foblex/f-flow).
- **Assistant:** AWS Bedrock (+ Core) editing a structured representation of the
  report design.
- **Query execution:** async API that runs generated queries against **Athena**;
  results persisted to **S3** and offered as CSV downloads.
- **Auth / scoping:** reports and runs are scoped to the user id derived from the
  JWT.

## Explicitly out of scope (for now)

- Sharing reports, teams, or per-report permissions.
- Folders / report organisation.
- Scheduled/automatic refresh (the runs model leaves room for it, but the save
  dialog does not expose it).
- CSV retention/expiry handling.

## Considerations for spec

These are the areas a spec should work through in detail, beyond the flow and
screens above.

### 1. Object / domain model
Define the shared model that represents a report design — tables, selected
columns, joins, filters, and sort order. It must serve **both** the drag-and-drop
designer and the agent: the canvas edits it, and the agent reads and writes the
same structure. Consider how it serialises for persistence and how it maps to the
flow-graph representation on the frontend.

### 2. Agent → SQL translation
How the Bedrock assistant consumes the model and translates it into executable
SQL. The agent will likely need **tools to test its generated query** (e.g. dry
runs / validation) before finalising it. Investigate how to do this with **Bedrock
Core** (agent tool use / action groups) and pull in the relevant AWS
documentation, citing sources.

### 3. Persistence
- **Reports:** where the saved report designs live (assumed **S3**).
- **Assistant conversation:** a persistent store for the per-report chat history
  so users can resume iterating.
- **Runs/executions:** records of each async execution and its status/result
  location.

### 4. Governance & security (first-class)
- **Data isolation:** ensure a customer can only query **data relevant to them** —
  how every query is scoped/filtered to their identity, and how we **verify query
  outputs** so results can never include another customer's data.
- **Prompt injection:** guard the agent against injection via the user's prompts
  or any data pulled into context.
- **Query bounds:** limit generated queries (row/scan limits, allow-listed tables
  and columns per customer) so ad-hoc reporting stays safe and performant.

### 5. Backend / APIs
New APIs will likely be needed to support these screens (reports CRUD, run /
execute, run status, CSV download, assistant chat). Review the reference repos
`reference-repos/BrytPortalCustomer` and `reference-repos/BrytBusinessServices`,
and adopt a **pattern similar to the contract-note work in BrytBusinessServices**.
The new code could potentially live alongside that.

## Open questions

- **View (screen 01)** currently opens the builder. Should it instead land on the
  latest results or the runs list for users who only want output?
- **CSV retention:** do completed results live in S3 indefinitely, or is there a
  lifecycle policy? If they expire, how is that surfaced?
- **Long-running runs:** since Athena queries can take a while, do we notify the
  user (email / in-portal toast) when a run finishes, given they may have
  navigated away?
- **Query safety:** how do we bound generated queries (row/scan limits, allowed
  tables/columns per customer) so ad-hoc reports stay safe and performant?
