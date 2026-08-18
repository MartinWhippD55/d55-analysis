# Requirements Document

**Story US-08 — Integration wiring & end-to-end validation**

> Mini-spec derived from parent spec **contract-note-data-source-extensibility**.
> Delivers user story **US-08**. See `manifest.yaml` for the component
> exports/dependencies and `../../graph.yaml` for the full delivery graph.

## Introduction

This story is the terminal, Wave 6 slice of the parent spec. It deploys and wires together every component the earlier waves produced — the `DataSourceApi` construct (US-03), the `enrich-data-sources` Lambda and render-pipeline enrichment state (US-05), and the two Admin Portal frontend components (US-06 template edit data sources panel, US-07 section-variant field browser) — into a single working CDK deployment, and validates the feature end to end. It finalises the authentication wiring introduced in parent Requirement 6 (Lambda→Project Role assume, API Gateway routes, Athena workgroup/results bucket, env vars). The optional integration tests exercise the discovery (parent Requirement 1) and render enrichment (parent Requirement 5) paths through the deployed stack. It has no downstream stories.

## Glossary

- **Project_Role**: The IAM role associated with the Unified Studio project, which holds Lake Formation grants for all subscribed data sources; the data source API and enrichment Lambdas assume it.
- **Data_Source**: A Glue Data Catalog table subscribed to the SageMaker Unified Studio project, queryable by BrytNumber.
- **BrytNumber**: The unique customer identifier (`customerreference` in the contract payload) used as the join key across all data sources.
- **Render_Pipeline**: The Step Functions state machine (`parse-input → select-template → enrich-data-sources → render-sections → stitch → write-output`).
- **Athena_Workgroup**: The workgroup and S3 results location configured for contract note enrichment queries.

## Delivered components

This story is responsible for creating and owning:

- `cdk-instance:deployment` — the finalised, fully-wired CDK deployment of the data source feature (API Gateway routes, Lambda→Project Role trust, Athena workgroup/results bucket, and environment variables) plus end-to-end validation.

## Dependencies

This story depends on components delivered by other stories (must be available first):

- `cdk-construct:DataSourceApi` (from US-03) — the data source API handlers, routing, and construct.
- `lambda:enrich-data-sources` + `state-machine:render-pipeline-enrichment` (from US-05) — the render-time enrichment Lambda and its Step Functions state.
- `frontend-component:template-edit-data-sources-panel` (from US-06) — the Admin Portal template edit data sources panel.
- `frontend-component:section-variant-field-browser` (from US-07) — the section-variant editor field browser.

## Requirements

### Requirement 1: Authentication via Project Role  _(parent: Requirement 6)_

**User Story:** As a system operator, I want the pipeline and API to access data sources using the Unified Studio project role, so that Lake Formation permissions are automatically inherited.

#### Acceptance Criteria

1. THE Lambda functions (data source API and the enrichment state) SHALL assume the Project_Role to access Glue Data Catalog and execute Athena queries _(parent 6.1)_
2. THE Project_Role trust policy SHALL be modified to allow the relevant Lambda execution roles to assume it _(parent 6.2)_
3. WHEN new data sources are subscribed in Unified Studio, THE system SHALL automatically have access via the existing Project_Role grants without manual IAM changes _(parent 6.3)_

### Requirement 2: End-to-end validation  _(parent: Requirements 1, 5)_

**User Story:** As a developer, I want the deployed data source feature validated end to end, so that discovery and render-time enrichment work as a whole across the wired stack.

#### Acceptance Criteria

1. WHEN a Glue table is subscribed in Unified Studio, THEN the deployed system SHALL surface it in the available data sources list without code changes or redeployment _(parent 1.3)_
2. WHERE a subscribed table lacks a `bryt_number` column, THE deployed system SHALL filter it out of the available data sources list _(parent 1.4)_
3. WHEN a data source is attached to a template and a matching XML is dropped, THE Render_Pipeline SHALL populate the namespaced enriched fields and render them in the output PDF _(parent 5.1)_
4. IF a Data_Source query fails with an Athena error, THEN the Render_Pipeline SHALL route to the existing `handle-failure` state _(parent 5.6)_
