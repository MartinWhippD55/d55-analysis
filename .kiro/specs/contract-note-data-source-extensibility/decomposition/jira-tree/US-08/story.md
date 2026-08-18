---
issue_type: Story
key: US-08
summary: Integration wiring & end-to-end validation
parent_epic: contract-note-data-source-extensibility
identity_label: s2s-contract-note-data-source-extensibility-US-08
labels:
- s2s-contract-note-data-source-extensibility
- s2s-contract-note-data-source-extensibility-US-08
- infra
- integration
estimate_days: 1.0
covers_requirements:
- '6'
wave: 6
depends_on:
- US-03
- US-05
- US-06
- US-07
blocks: []
---

As a developer, I want all components deployed and wired (API Gateway routes, Lambda->Project Role assume, Athena workgroup/results bucket, env vars) with end-to-end tests, so that the data source feature works as a whole.

## Description

Terminal, Wave 6 story. It wires the components delivered by the earlier waves — the `DataSourceApi` construct (US-03), the `enrich-data-sources` Lambda and render-pipeline enrichment state (US-05), and the two Admin Portal frontend panels (US-06, US-07) — into a single working CDK deployment, then validates the feature end to end. There is no new business logic: the work is finalising the deployment surface described by parent Requirement 6 (API Gateway routes, Lambda→Project Role assume, Athena workgroup/results bucket, environment variables) and confirming discovery and enrichment function through the deployed stack.

## Delivers

- `cdk-instance:deployment` — the finalised, fully-wired CDK deployment of the data source feature in `contract-note-stack.ts`: `DataSourceApi` construct instantiated and its `LambdaIntegration`s bound to the routes from `contract-note-foundation.ts::createRoutes`; the `enrich-data-sources` state inserted between `select-template` and `render-sections` in `render-pipeline.ts` and registered in the `handle-failure` catch array; the Project Role trust policy extended to trust the `list-available`, `get-columns`, and `enrich-data-sources` execution roles; the Athena workgroup and results bucket configured for contract note queries; and `PROJECT_ROLE_ARN` plus Athena config passed as environment variables — plus end-to-end validation of the wired system.

## Acceptance criteria

- **Given** the CDK stack, **when** it is synthesised/deployed, **then** the `DataSourceApi` construct is instantiated and its `LambdaIntegration`s are wired to the `contract-note-data-sources`, template-scoped `data-sources`, and shared-section `data-source-dependencies` routes from `contract-note-foundation.ts::createRoutes`.
- **Given** the render pipeline, **when** the stack is deployed, **then** the `enrich-data-sources` state sits between `select-template` and `render-sections` in `render-pipeline.ts` and is registered in the `handle-failure` catch array.
- **Given** the data source Lambdas (`list-available`, `get-columns`, `enrich-data-sources`), **when** they run, **then** each execution role is listed as an allowed `sts:AssumeRole` principal on the Project Role trust policy and holds `sts:AssumeRole` on the Project Role ARN.
- **Given** the enrichment queries, **when** the stack is deployed, **then** the Athena workgroup and results bucket exist, the Project Role can use them, and `PROJECT_ROLE_ARN` plus Athena config are passed as environment variables to the Glue/Athena-backed handlers and the enrichment state.
- **Given** the deployed system, **when** a Glue table is subscribed in Unified Studio, **then** it appears in the available data sources list without code changes or redeployment.
- **Given** the deployed system, **when** a data source is attached to a template and a matching XML is dropped, **then** the Render_Pipeline populates the namespaced enriched fields and renders them in the output PDF.
- **Given** a subscribed table lacking a `bryt_number` column, **when** the available list is fetched, **then** the table is filtered out.
- **Given** a data source query, **when** it fails with an Athena error, **then** the Render_Pipeline routes to the existing `handle-failure` state.

## Dependencies

- US-03 — Data Source API handlers + routing
- US-05 — Render pipeline enrichment (new Step Functions state)
- US-06 — Frontend: Template Edit data sources panel
- US-07 — Frontend: section-variant editor field browser & shared-section deps

## Traceability

Covers parent requirements: 6 · `s2s-contract-note-data-source-extensibility-US-08`
