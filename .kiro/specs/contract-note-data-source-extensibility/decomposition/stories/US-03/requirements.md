# Requirements Document

**Story US-03 — Data Source API handlers + routing**

> Mini-spec derived from parent spec **contract-note-data-source-extensibility**.
> Delivers user story **US-03**. See `manifest.yaml` for the component
> exports/dependencies and `../../graph.yaml` for the full delivery graph.
>
> NOTE: the top heading MUST be exactly `# Requirements Document` and the sections
> below (Introduction, Glossary, Requirements) MUST be present so the folder passes
> Kiro's spec-format checks and a developer can pull it straight into `.kiro/specs/`.

## Introduction

This story delivers the backend API surface for contract note data sources: the six REST endpoints and the `DataSourceApi` CDK construct that lets the Admin Portal discover Glue tables, read their columns, and attach/detach/list data sources on a template (plus a shared section's tracked dependencies). It is a vertical slice of the parent spec covering **Requirement 2 (Template Data Source Attachment)** and **Requirement 7 (Data Source API)**.

It sits in **Wave 3** of the delivery graph. It depends on the shared data source types (US-01), the Glue Data Catalog client (US-02), and the Project Role trust policy (US-01). Its downstream consumers are the frontend data sources panel (US-06), the section-variant field browser (US-07), and integration wiring (US-08), which all call these endpoints.

## Glossary

- **Data_Source**: A Glue Data Catalog table subscribed to the SageMaker Unified Studio project, queryable by BrytNumber.
- **BrytNumber**: The unique customer identifier (`customerreference` in the contract payload) used as the join key across all data sources.
- **Project_Role**: The IAM role associated with the Unified Studio project, holding Lake Formation grants for all subscribed data sources.
- **Glue_Data_Catalog**: The AWS Glue metadata catalog containing table schemas (databases, tables, columns) for subscribed data sources.
- **Template_Data_Source**: An association between a template and a Data_Source, indicating the template uses fields from that data source at render time.
- **Section_Variant**: A variant of a section (`SectionVariant`) with its own pdf-me schema and optional selection rule; one variant is chosen per render.
- **Section_Data_Source_Dependency**: A record of which Data_Sources a shared section requires, derived from the data source fields referenced across its variants' schemas.
- **DataSourceApi**: The CDK construct that creates the per-operation Lambdas, grants table/Glue/Athena/AssumeRole access, and wires the API Gateway integrations.

## Delivered components

This story is responsible for creating and owning:

- `api-endpoint:GET /contract-note-data-sources` — lists all Glue tables accessible via the Project Role that have a `bryt_number` column.
- `api-endpoint:GET /contract-note-data-sources/{database}/{table}/columns` — returns column names and types for a specific table.
- `api-endpoint:GET /contract-note-templates/{templateId}/data-sources` — returns data sources attached to a template.
- `api-endpoint:POST /contract-note-templates/{templateId}/data-sources` — attaches a data source to a template.
- `api-endpoint:DELETE /contract-note-templates/{templateId}/data-sources/{database}/{table}` — detaches a data source (with variant-field-in-use check).
- `api-endpoint:GET /contract-note-shared-sections/{sharedSectionId}/data-source-dependencies` — returns a shared section's tracked data source dependencies.
- `cdk-construct:DataSourceApi` — the construct wiring the handlers, IAM grants, and route integrations.

## Dependencies

This story depends on components delivered by other stories (must be available first):

- `shared-lib:data-source-types` (from US-01) — the `TemplateDataSource`, `AvailableDataSource`, `DataSourceColumn`, and `SectionDataSourceDependency` interfaces plus the new `ContractNoteEntityType` records.
- `shared-lib:glue-catalog-client` (from US-02) — the Glue discovery/column-fetch client used by the list-available and get-columns handlers.
- `cdk-construct:project-role-trust-policy` (from US-01) — the Project Role trust policy allowing the Lambda execution roles to assume it, and the `PROJECT_ROLE_ARN` parameter.

## Requirements

### Requirement 1: Template Data Source Attachment  _(parent: Requirement 2)_

**User Story:** As a Business_User, I want to attach data sources to a template, so that the template's sections can reference fields from those data sources.

#### Acceptance Criteria

1. THE API SHALL return the currently attached data sources for a template when its attached-list endpoint is called _(parent 2.1)_
2. THE API SHALL allow a Business_User to attach an available Data_Source to a template _(parent 2.2)_
3. THE API SHALL allow a Business_User to detach a Data_Source from a template _(parent 2.3)_
4. IF a detach targets a Data_Source referenced by one or more section variants in the template, THEN THE API SHALL block the detach and return the affected sections and variants for confirmation _(parent 2.4)_
5. THE API SHALL allow data sources to be attached or detached regardless of the template's DRAFT/PUBLISHED status _(parent 2.6)_

### Requirement 2: Data Source API  _(parent: Requirement 7)_

**User Story:** As a frontend developer, I want API endpoints for data source operations, so that the Admin Portal can manage template data source attachments.

#### Acceptance Criteria

1. THE API SHALL expose an endpoint to list all available data sources from the Glue catalog via the Project_Role _(parent 7.1)_
2. THE API SHALL expose endpoints to attach and detach data sources from a template, hung off the existing `contract-note-templates/{templateId}` route surface _(parent 7.2)_
3. THE API SHALL expose an endpoint to list attached data sources for a given template _(parent 7.3)_
4. THE API SHALL expose an endpoint to get column details for a specific data source _(parent 7.4)_
5. THE API SHALL validate that a data source exists and contains a `bryt_number` column before allowing attachment _(parent 7.5)_
6. THE API SHALL follow the established backend conventions: one Lambda per operation under `api/src/data-sources/`, routes declared in `contract-note-foundation.ts`, and wiring in a dedicated `DataSourceApi` CDK construct _(parent 7.6)_

### Requirement 3: Shared Section Data Source Dependencies (read surface)  _(parent: Requirement 4)_

**User Story:** As a frontend developer, I want an endpoint that returns a shared section's tracked data source dependencies, so that the Admin Portal can check a template has the required data sources attached.

#### Acceptance Criteria

1. THE API SHALL expose an endpoint that returns a shared section's tracked Data_Source dependencies from its `DATASOURCE_DEP` records _(parent 4.5)_
