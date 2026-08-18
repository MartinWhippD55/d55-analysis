# Requirements Document

**Story US-06 — Frontend: Template Edit data sources panel**

> Mini-spec derived from parent spec **contract-note-data-source-extensibility**.
> Delivers user story **US-06**. See `manifest.yaml` for the component
> exports/dependencies and `../../graph.yaml` for the full delivery graph.

## Introduction

This story delivers the Admin Portal front end for attaching data sources to a contract
note template. It adds a **Data Sources panel** to the existing `template-edit`
component, a **data source picker dialog** for choosing an available (unattached)
source, and a shared `DataSourceService` that wires all of these to the backend API
Gateway endpoints. It covers parent **Requirement 2 (Template Data Source Attachment)**
from the frontend side.

This is a **Wave 4** story. It depends on the shared data source types (US-01) and on the
data source API endpoints (US-03) being available. Downstream, US-07 (section-variant
field browser) and US-08 (shared section dependency checks) consume the
`DataSourceService` and the panel this story provides.

## Glossary

- **Data_Source**: A Glue Data Catalog table subscribed to the SageMaker Unified Studio project, containing customer-related data queryable by BrytNumber.
- **Template_Data_Source**: An association between a template and a Data_Source, indicating the template uses fields from that data source at render time.
- **Section_Variant**: A variant of a section (`SectionVariant`) with its own pdf-me schema and optional selection rule; one variant is chosen per render.
- **Admin_Portal**: The `sqp-4962` Angular front end where business users manage templates.
- **DataSourceService**: The frontend service that calls the data source API Gateway endpoints (list available, get columns, attach/detach, list attached, list shared-section deps).

## Delivered components

This story is responsible for creating and owning:

- `service:DataSourceService` — the frontend service wrapping the data source API endpoints (list available, get columns, attach/detach, list attached, list shared-section deps).
- `frontend-component:template-edit-data-sources-panel` — the Data Sources panel added to the `template-edit` component.
- `frontend-component:data-source-picker-dialog` — the picker dialog for selecting an available (unattached) data source.

## Dependencies

This story depends on components delivered by other stories (must be available first):

- `shared-lib:data-source-types` (from US-01) — shared TypeScript interfaces (`AvailableDataSource`, `DataSourceColumn`, `TemplateDataSource`, `SectionDataSourceDependency`).
- `api-endpoint:GET /contract-note-data-sources` (from US-03) — list available data sources.
- `api-endpoint:GET /contract-note-templates/{templateId}/data-sources` (from US-03) — list attached data sources.
- `api-endpoint:POST /contract-note-templates/{templateId}/data-sources` (from US-03) — attach a data source.
- `api-endpoint:DELETE /contract-note-templates/{templateId}/data-sources/{database}/{table}` (from US-03) — detach a data source (with variant-field-in-use check).

## Requirements

### Requirement 1: Template Data Source Attachment (frontend)  _(parent: Requirement 2)_

**User Story:** As a Business_User, I want a Data Sources panel on the template edit
screen to view, attach and detach data sources (with an in-use warning), so that a
template's sections can reference their fields.

#### Acceptance Criteria

1. WHEN a Business_User opens the template edit screen, THE Admin_Portal SHALL display the currently attached data sources for that template with name and column count _(parent 2.1)_
2. THE Admin_Portal SHALL allow a Business_User to attach an available Data_Source to a template via a [+ Attach Data Source] action that opens a picker showing available (unattached) data sources with table, database, and column count _(parent 2.2)_
3. THE Admin_Portal SHALL allow a Business_User to detach a Data_Source from a template _(parent 2.3)_
4. IF a Business_User attempts to detach a Data_Source that is referenced by one or more section variants in the template, THEN THE Admin_Portal SHALL display a warning listing the affected sections and variants and require confirmation _(parent 2.4)_
5. WHEN a Data_Source is attached to a template, ITS columns SHALL become available (via `DataSourceService`) as fields for any variant of any section in that template _(parent 2.5)_
6. THE Admin_Portal SHALL allow data sources to be attached or detached regardless of the template's DRAFT/PUBLISHED status _(parent 2.6)_
