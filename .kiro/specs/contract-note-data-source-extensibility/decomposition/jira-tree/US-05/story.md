---
issue_type: Story
key: US-05
summary: Render pipeline enrichment (new Step Functions state)
parent_epic: contract-note-data-source-extensibility
identity_label: s2s-contract-note-data-source-extensibility-US-05
labels:
- s2s-contract-note-data-source-extensibility
- s2s-contract-note-data-source-extensibility-US-05
- backend
- pipeline
estimate_days: 1.5
covers_requirements:
- '5'
wave: 3
depends_on:
- US-01
- US-02
blocks:
- US-08
---

As a system operator, I want a new enrich-data-sources state between select-template and render-sections that queries each attached data source by BrytNumber via Athena and merges the results into ContractData, so that data source fields populate on the PDF.

## Description

Adds render-time enrichment as a dedicated Step Functions state. A new `enrich-data-sources` Lambda is inserted between `select-template` and `render-sections`, so enrichment runs once and the enriched `ContractData` fans into every section-render Map iteration — `render-section` and `variant-selection` are untouched. The state reads the template's attached data sources, queries each via Athena using the contract's BrytNumber (`customerreference`) as the join key, and merges the results into `ContractData` under a per-table namespace. It reuses the existing `handle-failure` catch for error routing.

## Delivers

- `shared-lib:athena-client` — Athena query executor (`api/src/render/athena-client.ts`): assumes the Project Role and runs the per-data-source lookup query.
- `lambda:enrich-data-sources` — the `enrich-data-sources` handler (`api/src/render/enrich-data-sources.ts`): reads attachments, queries each source concurrently, merges namespaced results into `ContractData`.
- `state-machine:render-pipeline-enrichment` — wiring in `render-pipeline.ts` that inserts the new state between `selectTemplate` and `renderSections` and registers it on the `handle-failure` catch.

## Acceptance criteria

- **Given** a matching PUBLISHED template is selected, **when** the pipeline runs, **then** enrichment executes as a dedicated state between `select-template` and `render-sections`, and the enriched `ContractData` is passed to every section-render Map iteration.
- **Given** a template with attached data sources and contract data with a valid BrytNumber, **when** enrichment runs, **then** each source is queried by BrytNumber (`customerreference`) via Athena and its columns are merged into `ContractData` under the `{tableName}.{columnName}` namespace.
- **Given** a template with no attached data sources, **when** enrichment runs, **then** the contract data passes through unchanged and no Athena queries are issued.
- **Given** a data source query returns no rows for the BrytNumber, **when** enrichment runs, **then** a warning is logged and rendering continues with those fields empty.
- **Given** a data source query fails with an Athena error or timeout, **when** enrichment runs, **then** the state throws so the state machine routes to the existing `handle-failure` state.

## Dependencies

- US-01 — Foundation: shared data-source types & infrastructure
- US-02 — Glue Data Catalog discovery client

## Traceability

Covers parent requirements: 5 · `s2s-contract-note-data-source-extensibility-US-05`
