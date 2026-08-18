---
issue_type: Story
key: US-03
summary: Data Source API handlers + routing
parent_epic: contract-note-data-source-extensibility
identity_label: s2s-contract-note-data-source-extensibility-US-03
labels:
- s2s-contract-note-data-source-extensibility
- s2s-contract-note-data-source-extensibility-US-03
- backend
- api
estimate_days: 2.0
covers_requirements:
- '2'
- '7'
wave: 3
depends_on:
- US-01
- US-02
blocks:
- US-06
- US-07
- US-08
---

As a frontend developer, I want API endpoints to list available data sources, get their columns, and attach/detach/list data sources on a template (plus a shared section's tracked dependencies), so that the Admin Portal can manage attachments.

## Description

Implements the backend API layer for data source management: six API Gateway endpoints (one Lambda per operation under `api/src/data-sources/`) plus the `DataSourceApi` CDK construct that creates the handlers, grants table/Glue/Athena/AssumeRole access, and wires the `LambdaIntegration`s. Routes are declared centrally in `contract-note-foundation.ts::createRoutes`, following the Estimate 1 convention. This is the Wave 3 surface that the frontend (US-06, US-07) and integration wiring (US-08) consume.

## Delivers

- `api-endpoint:GET /contract-note-data-sources` — lists Glue tables accessible via the Project Role that have a `bryt_number` column.
- `api-endpoint:GET /contract-note-data-sources/{database}/{table}/columns` — returns column names and types for a specific table.
- `api-endpoint:GET /contract-note-templates/{templateId}/data-sources` — returns data sources attached to a template.
- `api-endpoint:POST /contract-note-templates/{templateId}/data-sources` — attaches a data source to a template.
- `api-endpoint:DELETE /contract-note-templates/{templateId}/data-sources/{database}/{table}` — detaches a data source (with variant-field-in-use check).
- `api-endpoint:GET /contract-note-shared-sections/{sharedSectionId}/data-source-dependencies` — returns a shared section's tracked data source dependencies.
- `cdk-construct:DataSourceApi` — the construct wiring the per-operation Lambdas, IAM grants, and route integrations.

## Acceptance criteria

- **Given** a template with attached data sources, **when** `GET /contract-note-templates/{templateId}/data-sources` is called, **then** the API returns the attached data sources projected to `TemplateDataSource[]` (database, tableName, displayName, attachedAt, attachedBy).
- **Given** the Project Role can reach the Glue catalog, **when** `GET /contract-note-data-sources` is called, **then** the API lists only tables containing a `bryt_number` column as `[{ database, tableName, columnCount }]`.
- **Given** a `{database}/{table}`, **when** `GET /contract-note-data-sources/{database}/{table}/columns` is called, **then** the API returns the full column list as `[{ name, type }]`.
- **Given** an available data source that exists and has a `bryt_number` column, **when** `POST /contract-note-templates/{templateId}/data-sources` is called, **then** the API writes a `DATASOURCE#{database}#{tableName}` record under the template partition and returns the attachment; **and** a table missing `bryt_number` (or not found) is rejected with 400 (or 404).
- **Given** an attached data source **not** referenced by any variant, **when** `DELETE /contract-note-templates/{templateId}/data-sources/{database}/{table}` is called, **then** the API removes the `DATASOURCE` record.
- **Given** an attached data source referenced by fields in one or more section variants, **when** the detach endpoint is called, **then** the API blocks the detach and returns **409** with the affected section+variant list.
- **Given** a shared section with tracked dependencies, **when** `GET /contract-note-shared-sections/{sharedSectionId}/data-source-dependencies` is called, **then** the API returns its `DATASOURCE_DEP` records as `SectionDataSourceDependency[]`.
- **Given** any template regardless of DRAFT/PUBLISHED status, **when** a data source is attached or detached, **then** the operation is permitted.

## Dependencies

- US-01 — Foundation: shared data-source types & infrastructure
- US-02 — Glue Data Catalog discovery client

## Traceability

Covers parent requirements: 2, 7 · `s2s-contract-note-data-source-extensibility-US-03`

## Architecture

The diagram shows what this story builds and where it is used. US-03 delivers the six Data Source API endpoints and the `DataSourceApi` CDK construct — the backend surface for listing, attaching, detaching and inspecting data sources. It depends on US-01 (shared types + trust policy) and US-02 (the Glue discovery client it calls for available sources and columns). Its endpoints are consumed by the frontend panels in US-06 (attach/detach/list) and US-07 (columns + shared-section dependencies), and its construct is wired into the deployed stack by US-08.
