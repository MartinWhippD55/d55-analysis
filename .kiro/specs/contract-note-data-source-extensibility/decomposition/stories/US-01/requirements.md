# Requirements Document

**Story US-01 — Foundation: shared data-source types & infrastructure**

> Mini-spec derived from parent spec **contract-note-data-source-extensibility**.
> Delivers user story **US-01**. See `manifest.yaml` for the component
> exports/dependencies and `../../graph.yaml` for the full delivery graph.

## Introduction

This story is the wave-1 foundation of Estimate 3b (Contract Note Data Source Extensibility). It delivers the stable base every other story builds on: the shared TypeScript types and DynamoDB record shapes for data sources, the SageMaker Unified Studio Project Role trust-policy change (so the data-source and enrichment Lambda execution roles can assume it), and the Athena workgroup plus S3 results bucket. It creates no user-facing behaviour on its own; instead it lays groundwork so discovery (US-02), the data source API (US-03), dependency tracking (US-04), the render enrichment state (US-05), and the frontend (US-06) can proceed. All of those stories depend on this one.

Its primary parent coverage is Requirement 6 (Authentication via Project Role). It also seeds the shared type surface that Requirements 2 and 4 rely on, and stands up the Athena configuration that Requirement 5 render-time enrichment needs.

## Glossary

- **Data_Source**: A Glue Data Catalog table subscribed to the SageMaker Unified Studio project, queryable by BrytNumber.
- **BrytNumber**: The unique customer identifier (`customerreference` in the contract payload) used as the join key across all data sources.
- **Project_Role**: The IAM role associated with the Unified Studio project, holding Lake Formation grants for all subscribed data sources.
- **Template_Data_Source**: An association between a template and a Data_Source, stored as a DynamoDB record.
- **Section_Data_Source_Dependency**: A record of which Data_Sources a shared section requires.
- **Athena workgroup**: The Athena query execution context (with an S3 results location) used by the render pipeline to query data sources.

## Delivered components

This story is responsible for creating and owning:

- `shared-lib:data-source-types` — the data source entity types, DynamoDB record shapes, and TypeScript interfaces in `shared-lib/types.ts`
- `cdk-construct:project-role-trust-policy` — the modified Unified Studio Project Role trust policy and the `PROJECT_ROLE_ARN` CDK parameter/env var
- `cdk-construct:athena-workgroup` — the Athena workgroup and S3 results bucket, with Project Role access

## Dependencies

This story depends on components delivered by other stories (must be available first):

- None — this is a wave-1 foundation story.

## Requirements

### Requirement 1: Authentication via Project Role  _(parent: Requirement 6)_

**User Story:** As a system operator, I want the pipeline and API to access data sources using the Unified Studio project role, so that Lake Formation permissions are automatically inherited.

#### Acceptance Criteria

1. THE Lambda functions (data source API and the enrichment state) SHALL assume the Project_Role to access Glue Data Catalog and execute Athena queries _(parent 6.1)_
2. THE Project_Role trust policy SHALL be modified to allow the relevant Lambda execution roles to assume it _(parent 6.2)_
3. WHEN new data sources are subscribed in Unified Studio, THE system SHALL automatically have access via the existing Project_Role grants without manual IAM changes _(parent 6.3)_

### Requirement 2: Shared Data Source Types  _(parent: Requirements 2, 4)_

**User Story:** As a developer, I want shared TypeScript types and DynamoDB record shapes for data sources, so that every downstream story reads and writes attachments and dependencies consistently.

#### Acceptance Criteria

1. THE `shared-lib/types.ts` module SHALL define `TemplateDataSource` and `SharedSectionDataSourceDependency` as `ContractNoteEntityType` values, plus the `TemplateDataSourceRecord` (`PK: TEMPLATE#{id}`, `SK: DATASOURCE#{db}#{table}`) and `SharedSectionDataSourceDependencyRecord` (`PK: SHARED_SECTION#{id}`, `SK: DATASOURCE_DEP#{db}#{table}`) shapes _(parent 2.1)_
2. THE `shared-lib/types.ts` module SHALL define the `AvailableDataSource`, `DataSourceColumn`, `TemplateDataSource`, and `SectionDataSourceDependency` interfaces and extend `ContractNoteDynamoDbRecord` with the new SK type aliases _(parent 4.1)_

### Requirement 3: Athena Workgroup & Results Bucket  _(parent: Requirement 5)_

**User Story:** As a system operator, I want an Athena workgroup and results bucket configured with Project Role access, so that render-time enrichment can execute queries against data sources.

#### Acceptance Criteria

1. THE CDK stack SHALL create/configure an Athena workgroup for contract note queries together with an S3 results location _(parent 5.3)_
2. THE Project_Role SHALL be granted access to the Athena workgroup and the S3 results location _(parent 5.3)_
