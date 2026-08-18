# Requirements Document

**Story US-07 — Frontend: section-variant editor field browser & shared-section deps**

> Mini-spec derived from parent spec **contract-note-data-source-extensibility**.
> Delivers user story **US-07**. See `manifest.yaml` for the component
> exports/dependencies and `../../graph.yaml` for the full delivery graph.
>
> NOTE: the top heading MUST be exactly `# Requirements Document` and the sections
> below (Introduction, Glossary, Requirements) MUST be present so the folder passes
> Kiro's spec-format checks and a developer can pull it straight into `.kiro/specs/`.

## Introduction

This story is the Admin Portal frontend slice of the data source extensibility feature. It gives Business_Users data source fields inside the section-variant editor palette, a missing-dependency prompt when adding a shared section to a template, and a dependencies view on the shared section detail screen. It covers parent Requirement 3 (Data Source Fields in Section Editor) and the frontend parts of parent Requirement 4 (Shared Section Data Source Dependencies — checks 4.3/4.4 and detail display 4.5).

This is a **Wave 5** story. It depends on the `DataSourceService` (US-06), the backend column and dependency API endpoints (US-03), and the shared dependency scanner (US-04). US-08 (integration wiring) depends on this story.

## Glossary

- **Section_Variant**: A variant of a section with its own pdf-me schema and optional selection rule; one variant is chosen per render. The Section_Editor edits a single variant's schema.
- **Section_Editor**: The Admin Portal screen that edits a variant's pdf-me schema, embedding the `pdfme-designer` web component.
- **Data_Source**: A Glue Data Catalog table subscribed to the Unified Studio project, queryable by BrytNumber.
- **Schema_JSON**: The pdf-me template document (`{ schemas: [[...]] }`); a data source field is a pdf-me element whose `name` is namespaced `{table_name}.{column_name}`.
- **Section_Data_Source_Dependency**: A record (`DATASOURCE_DEP#{database}#{tableName}`) of which Data_Sources a shared section requires, derived from field references across its variants' schemas.
- **Template_Data_Source**: An association between a template and a Data_Source; the set of attachments scopes which fields the editor exposes.

## Delivered components

This story is responsible for creating and owning:

- `frontend-component:section-variant-field-browser` — data source field groups in the pdfme-designer palette for the edited variant
- `frontend-component:shared-section-dependency-check` — the missing-dependency prompt shown when adding a shared section to a template
- `frontend-component:shared-section-deps-display` — the data source dependencies view on the shared section detail screen

## Dependencies

This story depends on components delivered by other stories (must be available first):

- `service:DataSourceService` (from US-06) — Angular service for list-available, get-columns, attach/detach, list-attached, and list-shared-section-deps calls
- `api-endpoint:GET /contract-note-data-sources/{database}/{table}/columns` (from US-03) — column names and types for the field browser
- `api-endpoint:GET /contract-note-shared-sections/{sharedSectionId}/data-source-dependencies` (from US-03) — a shared section's tracked dependencies
- `shared-lib:dependency-scanner` (from US-04) — scans pdf-me schema field references to map namespaced names to data source tables

## Requirements

### Requirement 1: Data Source Fields in Section Editor  _(parent: Requirement 3)_

**User Story:** As a Business_User, I want to use data source fields when designing section variants, so that I can include enriched data on contract notes.

#### Acceptance Criteria

1. WHEN a Business_User opens the Section_Editor for a Section_Variant within a template, THE Section_Editor SHALL display available fields from all attached Data_Sources alongside core contract data fields _(parent 3.1)_
2. THE Section_Editor SHALL distinguish data source fields from core contract fields by grouping them in a collapsible group per data source name _(parent 3.2)_
3. WHEN a Business_User places a data source field on the variant canvas, THE Section_Editor SHALL record the field reference as a namespaced pdf-me element name including the Data_Source table and column (`{table_name}.{column_name}`) _(parent 3.3)_
4. THE Section_Editor SHALL display data source fields with their column type to help users understand the data format _(parent 3.4)_
5. WHERE a section is shared, THE Section_Editor SHALL surface data source fields consistently across all templates the shared section is referenced by, independent of any single template's attachments _(parent 3.5)_

### Requirement 2: Shared Section Data Source Dependencies (frontend)  _(parent: Requirement 4)_

**User Story:** As a Business_User, I want shared sections to track their data source dependencies, so that templates using those sections have the required data sources attached.

#### Acceptance Criteria

1. WHEN a Business_User adds a shared section to a template, THE Admin_Portal SHALL check if the template has all required Data_Sources attached by reading the shared section's `DATASOURCE_DEP` records _(parent 4.3)_
2. IF a shared section requires a Data_Source not attached to the template, THEN THE Admin_Portal SHALL prompt the user to add the missing Data_Source to the template before proceeding _(parent 4.4)_
3. THE Admin_Portal SHALL display data source dependencies on the shared section detail screen _(parent 4.5)_
