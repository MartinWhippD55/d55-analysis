---
issue_type: Story
key: US-07
summary: 'Frontend: section-variant editor field browser & shared-section deps'
parent_epic: contract-note-data-source-extensibility
identity_label: s2s-contract-note-data-source-extensibility-US-07
labels:
- s2s-contract-note-data-source-extensibility
- s2s-contract-note-data-source-extensibility-US-07
- frontend
estimate_days: 1.5
covers_requirements:
- '3'
- '4'
wave: 5
depends_on:
- US-03
- US-04
- US-06
blocks:
- US-08
---

As a Business_User, I want data source fields in the section-variant editor palette, a missing-dependency prompt when adding a shared section, and dependencies shown on the shared section detail screen, so that I can design enriched sections safely.

## Description

The Admin Portal frontend slice of the data source extensibility feature. It extends the Section_Editor's `pdfme-designer` field palette to show data source columns for the variant being edited, adds a missing-dependency prompt when a shared section is added to a template, and lists a shared section's tracked data source dependencies on its detail screen. This is a pure frontend story built on `DataSourceService` (US-06), the backend column and dependency endpoints (US-03), and the shared dependency scanner (US-04); US-08 wires it up end-to-end.

## Delivers

- `frontend-component:section-variant-field-browser` — data source field groups in the pdfme-designer palette for the edited variant
- `frontend-component:shared-section-dependency-check` — the missing-dependency prompt shown when adding a shared section to a template
- `frontend-component:shared-section-deps-display` — the data source dependencies view on the shared section detail screen

## Acceptance criteria

- **Given** a template with attached data sources, **when** a Business_User opens the Section_Editor for a variant, **then** the pdfme-designer palette shows a collapsible group per data source, each column rendered as a draggable field labelled `{table}.{column}` with its column type and visually distinct from core contract fields.
- **Given** a data source field in the palette, **when** the user places it on the variant canvas, **then** the pdf-me element `name` is written as the namespaced `{table_name}.{column_name}` so enrichment populates the same key at render time.
- **Given** a shared section being added to a template, **when** the section's `DATASOURCE_DEP` records reference a data source not attached to the template, **then** the Admin_Portal prompts the user to add the missing Data_Source(s) before the section can be attached.
- **Given** the shared section detail screen, **when** it loads, **then** it lists the section's tracked data source dependencies (database + table name).

## Dependencies

- US-03 — Data Source API handlers + routing
- US-04 — Data source dependency scanner
- US-06 — Frontend: Template Edit data sources panel

## Traceability

Covers parent requirements: 3, 4 · `s2s-contract-note-data-source-extensibility-US-07`

## Architecture

The diagram shows what this story builds and where it is used. US-07 delivers the section-variant editor frontend: the field browser that surfaces data source columns as draggable `{table}.{column}` fields, the missing-dependency prompt when adding a shared section, and the dependency display on the shared section detail screen. It builds on US-03 (columns + dependency endpoints), US-04 (the dependency scanner), and US-06 (`DataSourceService`). US-08 wires it into the deployed system and validates the full authoring-to-render flow.
