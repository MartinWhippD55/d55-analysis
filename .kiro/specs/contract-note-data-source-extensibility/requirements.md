# Requirements Document

## Introduction

This document specifies the requirements for Estimate 3b of the Bryt Energy Contract Note Rework project. The system enables business users to enrich contract note templates with data from external sources managed in SageMaker Unified Studio, without requiring developer involvement to add new data sources.

Business users create and manage data sources in SageMaker Unified Studio (backed by Glue Data Catalog). When they subscribe a data source to the contract note project, it becomes automatically discoverable by the template management system. Users can then attach data sources to templates and reference their fields in the section designer.

At render time, the pipeline queries each attached data source via Athena using the BrytNumber (customer reference) as the lookup key, merging the results into the template input data.

> **Implementation baseline (2026-08).** This spec is written against the contract note system now landed on `BrytBusinessServices` `dev` (Jabez's `sqp-4960*` series) and the Admin Portal frontend on `sqp-4962`. Estimate 1 introduced concepts this spec must respect that were not present when 3b was first drafted:
> - **Sections have _variants_** — each `Section` owns one or more `SectionVariant`s, each with its own pdf-me schema and its own selection rule. Variants are chosen at render time by first-match-wins spec evaluation with a default fallback.
> - **Schema JSON is stored in S3**, not DynamoDB, in pdf-me shape (`{ schemas: [[...]] }`), and is **versioned** — sections render from a *pinned version* of the selected variant's schema.
> - **Templates and section versions have a `DRAFT`/`PUBLISHED` lifecycle.** Template selection at render time only considers `PUBLISHED` templates.
> - **The render pipeline is a Step Functions state machine** (`parse-input → select-template → render-sections (Map) → stitch → write-output`), not a single Lambda.
> - **The backend is a TypeScript monorepo** (`api/` handlers, `cdk/` infra, `shared-lib/` types + spec evaluator) with one Lambda per operation and routes declared centrally in `contract-note-foundation.ts`.

## Glossary

- **Data_Source**: A Glue Data Catalog table subscribed to the SageMaker Unified Studio project, containing customer-related data queryable by BrytNumber
- **BrytNumber**: The unique customer identifier (`customerreference` in the contract payload, e.g., "BRYT002618") used as the join key across all data sources
- **Unified_Studio_Project**: The SageMaker Unified Studio project that manages data subscriptions and Lake Formation permissions
- **Project_Role**: The IAM role associated with the Unified Studio project, which has Lake Formation grants for all subscribed data sources
- **Glue_Data_Catalog**: The AWS Glue metadata catalog containing table schemas (databases, tables, columns) for subscribed data sources
- **Template_Data_Source**: An association between a template and a Data_Source, indicating the template uses fields from that data source at render time
- **Section_Variant**: A variant of a section (`SectionVariant`) with its own pdf-me schema and optional selection rule; one variant is chosen per render
- **Section_Version**: A pinned, versioned snapshot of a variant's pdf-me schema JSON in S3, keyed `SECTION_VERSION#{sectionId}#{variantId}`; the render pipeline renders the pinned version
- **Section_Data_Source_Dependency**: A record of which Data_Sources a shared section requires, derived from the data source fields referenced across its variants' schemas
- **Schema_JSON**: The pdf-me template document (`{ schemas: [[...]] }`) stored in the schema bucket in S3; field references are the `name` values of pdf-me schema elements
- **Enriched_Data**: The additional columns fetched from subscribed data sources at render time and merged into the contract JSON (`ContractData`) for template field resolution

## Requirements

### Requirement 1: Data Source Discovery

**User Story:** As a Business_User, I want to see which data sources are available to use in templates, so that I can incorporate additional data into contract notes.

#### Acceptance Criteria

1. THE Admin_Portal SHALL query the Glue_Data_Catalog to discover all tables available to the Project_Role within the Unified_Studio_Project
2. THE Admin_Portal SHALL display discovered data sources with their table name, database name, and column list (name and type)
3. WHEN a new data source is subscribed in Unified Studio, IT SHALL become visible in the Admin Portal without code changes or redeployment
4. THE Admin_Portal SHALL only display data sources that contain a `bryt_number` column (or configured equivalent), filtering out tables that cannot be joined

### Requirement 2: Template Data Source Attachment

**User Story:** As a Business_User, I want to attach data sources to a template, so that the template's sections can reference fields from those data sources.

#### Acceptance Criteria

1. WHEN a Business_User opens the template edit screen, THE Admin_Portal SHALL display the currently attached data sources for that template
2. THE Admin_Portal SHALL allow a Business_User to attach an available Data_Source to a template
3. THE Admin_Portal SHALL allow a Business_User to detach a Data_Source from a template
4. IF a Business_User attempts to detach a Data_Source that is referenced by one or more section variants in the template, THEN THE Admin_Portal SHALL display a warning listing the affected sections and variants and require confirmation
5. WHEN a Data_Source is attached to a template, ITS columns SHALL become available as fields in the Section_Editor for any variant of any section in that template
6. THE Admin_Portal SHALL allow data sources to be attached or detached regardless of the template's DRAFT/PUBLISHED status; attachment changes SHALL only affect rendering once the template is PUBLISHED

### Requirement 3: Data Source Fields in Section Editor

**User Story:** As a Business_User, I want to use data source fields when designing section variants, so that I can include enriched data on contract notes.

#### Acceptance Criteria

1. WHEN a Business_User opens the Section_Editor for a Section_Variant within a template, THE Section_Editor SHALL display available fields from all attached Data_Sources alongside core contract data fields
2. THE Section_Editor SHALL distinguish data source fields from core contract fields (e.g., by grouping or prefixing with the data source name)
3. WHEN a Business_User places a data source field on the variant canvas, THE Section_Editor SHALL record the field reference as a namespaced pdf-me element name including the Data_Source table and column
4. THE Section_Editor SHALL display data source fields with their column type to help users understand the data format
5. WHERE a section is shared, THE Section_Editor SHALL surface data source fields consistently across all templates the shared section is referenced by, independent of any single template's attachments

### Requirement 4: Shared Section Data Source Dependencies

**User Story:** As a Business_User, I want shared sections to track their data source dependencies, so that templates using those sections have the required data sources attached.

#### Acceptance Criteria

1. THE Admin_Portal SHALL automatically track which Data_Sources a shared section depends on, derived from the data source fields used across the Schema_JSON of all its variants
2. WHEN a shared section variant's schema is saved or a new version is published, THE Admin_Portal SHALL recompute the shared section's data source dependencies
3. WHEN a Business_User adds a shared section to a template, THE Admin_Portal SHALL check if the template has all required Data_Sources attached
4. IF a shared section requires a Data_Source not attached to the template, THEN THE Admin_Portal SHALL prompt the user to add the missing Data_Source to the template before proceeding
5. THE Admin_Portal SHALL display data source dependencies on the shared section detail screen

### Requirement 5: Render Pipeline Data Enrichment

**User Story:** As a system operator, I want the render pipeline to automatically fetch data from attached data sources at render time, so that data source fields are populated on the final PDF.

#### Acceptance Criteria

1. WHEN the Render_Pipeline selects a matching PUBLISHED template, IT SHALL identify all Data_Sources attached to that template
2. THE Render_Pipeline SHALL perform enrichment as a dedicated state between template selection and section rendering, so that the enriched `ContractData` is passed to every section-render Map iteration
3. FOR each attached Data_Source, THE Render_Pipeline SHALL execute an Athena query to fetch the row matching the BrytNumber from the contract data
4. THE Render_Pipeline SHALL merge the fetched data into the `ContractData` under a namespace derived from the data source table name to avoid field collisions (e.g., `datasource_table.column_name`)
5. IF a Data_Source query returns no rows for the given BrytNumber, THE Render_Pipeline SHALL log a warning and continue rendering with those fields empty
6. IF a Data_Source query fails (Athena error, timeout), THE Render_Pipeline SHALL route to the existing `handle-failure` state and halt processing for that contract note
7. WHEN a template has no attached Data_Sources, THE Render_Pipeline SHALL pass the contract data through unchanged with no Athena calls

### Requirement 6: Authentication via Project Role

**User Story:** As a system operator, I want the pipeline and API to access data sources using the Unified Studio project role, so that Lake Formation permissions are automatically inherited.

#### Acceptance Criteria

1. THE Lambda functions (data source API and the enrichment state) SHALL assume the Project_Role to access Glue Data Catalog and execute Athena queries
2. THE Project_Role trust policy SHALL be modified to allow the relevant Lambda execution roles to assume it
3. WHEN new data sources are subscribed in Unified Studio, THE system SHALL automatically have access via the existing Project_Role grants without manual IAM changes

### Requirement 7: Data Source API

**User Story:** As a frontend developer, I want API endpoints for data source operations, so that the Admin Portal can manage template data source attachments.

#### Acceptance Criteria

1. THE API SHALL expose an endpoint to list all available data sources (from Glue catalog via Project_Role)
2. THE API SHALL expose endpoints to attach and detach data sources from a template, hung off the existing `contract-note-templates/{templateId}` route surface
3. THE API SHALL expose an endpoint to list attached data sources for a given template
4. THE API SHALL expose an endpoint to get column details for a specific data source (for the field browser in the Section Editor)
5. THE API SHALL validate that a data source exists and contains a `bryt_number` column before allowing attachment
6. THE API SHALL follow the established backend conventions: one Lambda per operation under `api/src/data-sources/`, routes declared in `contract-note-foundation.ts`, and wiring in a dedicated `DataSourceApi` CDK construct
