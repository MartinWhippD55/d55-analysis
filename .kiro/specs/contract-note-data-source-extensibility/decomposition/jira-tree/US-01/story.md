---
issue_type: Story
key: US-01
summary: 'Foundation: shared data-source types & infrastructure'
parent_epic: contract-note-data-source-extensibility
identity_label: s2s-contract-note-data-source-extensibility-US-01
labels:
- s2s-contract-note-data-source-extensibility
- s2s-contract-note-data-source-extensibility-US-01
- infra
- backend
estimate_days: 1.5
covers_requirements:
- '6'
wave: 1
depends_on: []
blocks:
- US-02
- US-03
- US-04
- US-05
- US-06
---

As a developer, I want the shared data-source TypeScript types + DynamoDB record shapes, the Unified Studio Project Role trust-policy change, and the Athena workgroup + results bucket, so that every other story has a stable foundation to build on.

## Description

Wave-1 foundation of Estimate 3b. It delivers the shared data-source TypeScript types and DynamoDB record shapes, the SageMaker Unified Studio Project Role trust-policy change that lets the data-source and enrichment Lambda execution roles assume it, and the Athena workgroup plus S3 results bucket. It adds no user-facing behaviour itself; it extends the landed Estimate 1 `shared-lib/` and `cdk/` so discovery (US-02), the data source API (US-03), dependency tracking (US-04), render enrichment (US-05), and the frontend (US-06) can build on a stable base.

## Delivers

- `shared-lib:data-source-types` — data source entity types, DynamoDB record shapes, and TypeScript interfaces in `shared-lib/types.ts`.
- `cdk-construct:project-role-trust-policy` — the modified Unified Studio Project Role trust policy and the `PROJECT_ROLE_ARN` CDK parameter/env var.
- `cdk-construct:athena-workgroup` — the Athena workgroup and S3 results bucket, with Project Role access.

## Acceptance criteria

- **Given** the data source API and enrichment-state Lambda execution roles, **when** they need Glue Data Catalog or Athena access, **then** they SHALL assume the Project_Role and inherit its Lake Formation grants.
- **Given** the Unified Studio Project Role, **when** its trust policy is deployed, **then** it SHALL be modified to allow the relevant Lambda execution roles to assume it.
- **Given** a new data source subscribed in Unified Studio, **when** the pipeline accesses it, **then** the system SHALL have access via the existing Project_Role grants without manual IAM changes.
- **Given** `shared-lib/types.ts`, **when** it is compiled, **then** it SHALL define `TemplateDataSource` and `SharedSectionDataSourceDependency` as `ContractNoteEntityType` values plus the `TemplateDataSourceRecord` (`PK: TEMPLATE#{id}`, `SK: DATASOURCE#{db}#{table}`) and `SharedSectionDataSourceDependencyRecord` (`PK: SHARED_SECTION#{id}`, `SK: DATASOURCE_DEP#{db}#{table}`) shapes.
- **Given** `shared-lib/types.ts`, **when** it is compiled, **then** it SHALL define the `AvailableDataSource`, `DataSourceColumn`, `TemplateDataSource`, and `SectionDataSourceDependency` interfaces and extend `ContractNoteDynamoDbRecord` with the new SK type aliases.
- **Given** the CDK stack, **when** it is deployed, **then** it SHALL create/configure an Athena workgroup for contract note queries together with an S3 results location.
- **Given** the Athena workgroup and S3 results location, **when** the stack is deployed, **then** the Project_Role SHALL be granted access to both.

## Dependencies

- None — foundation story.

## Traceability

Covers parent requirements: 6 · `s2s-contract-note-data-source-extensibility-US-01`

## Architecture

The diagram shows what this story builds and where it is used. As the Wave 1 foundation, US-01 delivers three components — the shared data-source types (`shared-lib:data-source-types`), the Project Role trust-policy change, and the Athena workgroup + results bucket — and adds no runtime behaviour of its own. Its outputs feed almost every downstream story: the types are consumed by US-02, US-03, US-04, US-05 and US-06; the trust policy is assumed by the Glue/Athena work in US-02, US-03 and US-05; and the Athena workgroup underpins the render-time enrichment in US-05. It has no dependencies of its own.
