---
issue_type: Story
key: US-02
summary: Glue Data Catalog discovery client
parent_epic: contract-note-data-source-extensibility
identity_label: s2s-contract-note-data-source-extensibility-US-02
labels:
- s2s-contract-note-data-source-extensibility
- s2s-contract-note-data-source-extensibility-US-02
- backend
estimate_days: 1.0
covers_requirements:
- '1'
wave: 2
depends_on:
- US-01
blocks:
- US-03
- US-05
---

As a Business_User, I want the system to discover the Glue tables available to the Project Role (filtered to those joinable by bryt_number) with their columns, so that subscribed data sources become usable without code changes.

## Description

Delivers the Glue Data Catalog discovery client: a shared backend module that assumes the Unified Studio Project Role, lists the Glue tables that role can see, filters them to those joinable by `bryt_number`, and returns structured `AvailableDataSource[]` with columns. It also exposes a per-table column detail fetcher. This is the "read side" of the architecture — it feeds the Data Source API (US-03) and the render-time enrichment step (US-05), and because access is via the Project Role, any newly subscribed table becomes discoverable with no per-table IAM change and no redeployment.

## Delivers

- `shared-lib:glue-catalog-client` (`api/src/data-sources/`) — exports `listAvailableDataSources()` returning `AvailableDataSource[]` and `getDataSourceColumns(database, table)` returning `DataSourceColumn[]`.

## Acceptance criteria

- **Given** the Project Role has Lake Formation grants for several Glue tables, **when** `listAvailableDataSources()` is called, **then** only tables containing a `bryt_number` column are returned and tables without it are filtered out.
- **Given** a discoverable table, **when** it is returned by the client, **then** each entry carries its `database`, `tableName`, and `columns` (each column with `name` and Glue/Athena `type`).
- **Given** a new data source is subscribed to the Unified Studio project, **when** `listAvailableDataSources()` is next called, **then** it appears in the results with no code change and no redeployment.

## Dependencies

- US-01 — Foundation: shared data-source types & infrastructure

## Traceability

Covers parent requirements: 1 · `s2s-contract-note-data-source-extensibility-US-02`
