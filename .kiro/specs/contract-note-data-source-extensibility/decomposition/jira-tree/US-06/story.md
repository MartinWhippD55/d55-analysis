---
issue_type: Story
key: US-06
summary: 'Frontend: Template Edit data sources panel'
parent_epic: contract-note-data-source-extensibility
identity_label: s2s-contract-note-data-source-extensibility-US-06
labels:
- s2s-contract-note-data-source-extensibility
- s2s-contract-note-data-source-extensibility-US-06
- frontend
estimate_days: 1.5
covers_requirements:
- '2'
wave: 4
depends_on:
- US-01
- US-03
blocks:
- US-07
- US-08
---

As a Business_User, I want a Data Sources panel on the template edit screen to view, attach and detach data sources (with an in-use warning), so that a template's sections can reference their fields.

## Description

Delivers the Admin Portal front end for attaching data sources to a contract note template (parent Requirement 2). It adds a Data Sources panel to the existing `template-edit` component, a picker dialog for choosing an available (unattached) source, and a shared `DataSourceService` that wires both to the US-03 API Gateway endpoints. Rendering-time behaviour lives in the backend (US-04); this story is the wiring that lets business users view, attach, and detach data sources on a template.

## Delivers

- `service:DataSourceService` — frontend client for the data source API endpoints (list available, get columns, attach/detach, list attached, list shared-section deps).
- `frontend-component:template-edit-data-sources-panel` — the Data Sources panel added to the `template-edit` component.
- `frontend-component:data-source-picker-dialog` — the picker dialog for selecting an available (unattached) data source.

## Acceptance criteria

- **Given** a template edit screen, **when** the Business_User opens it, **then** the Data Sources panel lists the template's currently attached data sources with name and column count.
- **Given** the Data Sources panel, **when** the Business_User clicks [+ Attach Data Source], **then** a picker opens showing available (unattached) sources with table, database, and column count, and selecting one attaches it and refreshes the panel.
- **Given** an attached data source that no section variant references, **when** the Business_User detaches it, **then** it is removed from the template's attached list.
- **Given** an attached data source referenced by one or more section variants, **when** the Business_User attempts to detach it, **then** the panel shows a warning listing the affected sections and variants and requires confirmation before removing it.
- **Given** a template in either DRAFT or PUBLISHED status, **when** the Business_User opens the Data Sources panel, **then** attach and detach are available regardless of the template's status.

## Dependencies

- US-01 — Foundation: shared data-source types & infrastructure
- US-03 — Data Source API handlers + routing

## Traceability

Covers parent requirements: 2 · `s2s-contract-note-data-source-extensibility-US-06`

## Architecture

The diagram shows what this story builds and where it is used. US-06 delivers the Template Edit frontend slice: the Data Sources panel, the picker dialog, and the shared `DataSourceService` that wires both to the US-03 API. It depends on US-01 (shared types) and US-03 (the API endpoints it calls). Its `DataSourceService` is reused by US-07's field browser and dependency checks, and US-08 wires the panel into the deployed system for end-to-end validation.
