# Requirements Document

**Story US-05 — Render pipeline enrichment (new Step Functions state)**

> Mini-spec derived from parent spec **contract-note-data-source-extensibility**.
> Delivers user story **US-05**. See `manifest.yaml` for the component
> exports/dependencies and `../../graph.yaml` for the full delivery graph.

## Introduction

This story delivers the render-time enrichment slice of the parent spec: a dedicated `enrich-data-sources` Step Functions state inserted between `select-template` and `render-sections`. When a matching PUBLISHED template is selected, the new state reads the template's attached data sources, queries each via Athena using the contract's BrytNumber (`customerreference`) as the join key, and merges the results into `ContractData` under a per-table namespace so every section-render Map iteration receives the enriched data. It is a Wave 3 backend story that depends on the shared data source types (US-01), the Glue catalog client (US-02), the Project Role trust policy (US-01), and the Athena workgroup (US-01). Downstream, US-08 (integration wiring) depends on it. This story covers parent Requirement 5 (Render Pipeline Data Enrichment).

## Glossary

- **BrytNumber**: The unique customer identifier (`customerreference` in the contract payload, e.g., "BRYT002618") used as the join key across all data sources.
- **Data_Source**: A Glue Data Catalog table subscribed to the SageMaker Unified Studio project, queryable by BrytNumber.
- **Template_Data_Source**: An association between a template and a Data_Source, stored as a `DATASOURCE` record under the template partition.
- **Enriched_Data**: The additional columns fetched from subscribed data sources at render time and merged into the contract JSON (`ContractData`) under the `{tableName}.{columnName}` namespace.
- **Render_Pipeline**: The Step Functions state machine (`parse-input → select-template → enrich-data-sources → render-sections (Map) → stitch → write-output`).
- **Project_Role**: The IAM role associated with the Unified Studio project, which holds the Lake Formation grants for subscribed data sources.

## Delivered components

This story is responsible for creating and owning:

- `shared-lib:athena-client` — the Athena query executor (`api/src/render/athena-client.ts`) that assumes the Project Role and runs the per-data-source lookup query.
- `lambda:enrich-data-sources` — the `enrich-data-sources` handler (`api/src/render/enrich-data-sources.ts`) that reads attachments, queries each source, and merges namespaced results into `ContractData`.
- `state-machine:render-pipeline-enrichment` — the wiring in `render-pipeline.ts` that inserts the new state between `select-template` and `render-sections` and registers it on the `handle-failure` catch.

## Dependencies

This story depends on components delivered by other stories (must be available first):

- `shared-lib:data-source-types` (from US-01) — `TemplateDataSource` entity/records and enrichment interfaces.
- `shared-lib:glue-catalog-client` (from US-02) — Project Role assumption and catalog access patterns reused by the Athena client.
- `cdk-construct:project-role-trust-policy` (from US-01) — trust policy allowing the `enrich-data-sources` execution role to assume the Project Role.
- `cdk-construct:athena-workgroup` (from US-01) — the Athena workgroup and S3 results location the query executor targets.

## Requirements

### Requirement 1: Render Pipeline Data Enrichment  _(parent: Requirement 5)_

**User Story:** As a system operator, I want a new `enrich-data-sources` state between `select-template` and `render-sections` that queries each attached data source by BrytNumber via Athena and merges the results into `ContractData`, so that data source fields populate on the final PDF.

#### Acceptance Criteria

1. WHEN the Render_Pipeline selects a matching PUBLISHED template, IT SHALL identify all Data_Sources attached to that template _(parent 5.1)_
2. THE Render_Pipeline SHALL perform enrichment as a dedicated state between template selection and section rendering, so that the enriched `ContractData` is passed to every section-render Map iteration _(parent 5.2)_
3. FOR each attached Data_Source, THE Render_Pipeline SHALL execute an Athena query to fetch the row matching the BrytNumber from the contract data _(parent 5.3)_
4. THE Render_Pipeline SHALL merge the fetched data into the `ContractData` under a namespace derived from the data source table name to avoid field collisions (e.g., `datasource_table.column_name`) _(parent 5.4)_
5. IF a Data_Source query returns no rows for the given BrytNumber, THE Render_Pipeline SHALL log a warning and continue rendering with those fields empty _(parent 5.5)_
6. IF a Data_Source query fails (Athena error, timeout), THE Render_Pipeline SHALL route to the existing `handle-failure` state and halt processing for that contract note _(parent 5.6)_
7. WHEN a template has no attached Data_Sources, THE Render_Pipeline SHALL pass the contract data through unchanged with no Athena calls _(parent 5.7)_
