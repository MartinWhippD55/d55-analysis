# Requirements Document

**Story US-04 — Data source dependency scanner**

> Mini-spec derived from parent spec **contract-note-data-source-extensibility**.
> Delivers user story **US-04**. See `manifest.yaml` for the component
> exports/dependencies and `../../graph.yaml` for the full delivery graph.
>
> NOTE: the top heading MUST be exactly `# Requirements Document` and the sections
> below (Introduction, Glossary, Requirements) MUST be present so the folder passes
> Kiro's spec-format checks and a developer can pull it straight into `.kiro/specs/`.

## Introduction

This story delivers the shared dependency scanner that lets shared sections
automatically track which data sources they depend on. Given a pdf-me Schema_JSON
document (`{ schemas: [[...]] }`), it walks every page, collects the namespaced field
references (element `name`s containing a `.`), and maps each prefix to a data source
table. On a shared section variant schema save or version publish, it recomputes the
shared section's dependencies as the union of data sources referenced across all of
that section's variants' schemas and reconciles the `DATASOURCE_DEP` records.

This is a **Wave 2** story. It depends on the shared data source types from US-01
(`shared-lib:data-source-types`). Its exported scanner (`shared-lib:dependency-scanner`)
is consumed downstream by US-07. It covers parent Requirement 4 (Shared Section Data
Source Dependencies — specifically the auto-tracking and recompute behaviour of 4.1,
4.2 and the tracked-dependency data behind 4.5) and validates parent Property 5
(dependency = union across variants).

## Glossary

- **Schema_JSON**: The pdf-me template document (`{ schemas: [[...]] }`) stored in the schema bucket in S3; field references are the `name` values of pdf-me schema elements
- **Section_Variant**: A variant of a section (`SectionVariant`) with its own pdf-me schema and optional selection rule; one variant is chosen per render
- **Section_Version**: A pinned, versioned snapshot of a variant's pdf-me schema JSON in S3, keyed `SECTION_VERSION#{sectionId}#{variantId}`
- **Section_Data_Source_Dependency**: A record of which Data_Sources a shared section requires, derived from the data source fields referenced across its variants' schemas
- **Data_Source**: A Glue Data Catalog table subscribed to the SageMaker Unified Studio project, containing customer-related data queryable by BrytNumber
- **DATASOURCE_DEP record**: The DynamoDB record (`PK: SHARED_SECTION#{id}`, `SK: DATASOURCE_DEP#{database}#{tableName}`) recording one tracked dependency of a shared section

## Delivered components

This story is responsible for creating and owning:

- `shared-lib:dependency-scanner` — the pdf-me Schema_JSON field-reference scanner plus the shared-section dependency recompute/reconcile logic

## Dependencies

This story depends on components delivered by other stories (must be available first):

- `shared-lib:data-source-types` (from US-01) — shared TypeScript interfaces and the `SharedSectionDataSourceDependency` entity/record shape used to reconcile `DATASOURCE_DEP` records

## Requirements

### Requirement 1: Shared Section Data Source Dependencies  _(parent: Requirement 4)_

**User Story:** As a Business_User, I want shared sections to automatically track which data sources they depend on, derived from the namespaced fields used across all of a section's variant schemas, so that templates using them can be checked.

#### Acceptance Criteria

1. THE system SHALL automatically track which Data_Sources a shared section depends on, derived from the data source fields used across the Schema_JSON of all its variants _(parent 4.1)_
2. WHEN a shared section variant's schema is saved or a new version is published, THE system SHALL recompute the shared section's data source dependencies _(parent 4.2)_
3. THE system SHALL persist the recomputed dependencies as `DATASOURCE_DEP` records so they can be displayed on the shared section detail screen _(parent 4.5)_
