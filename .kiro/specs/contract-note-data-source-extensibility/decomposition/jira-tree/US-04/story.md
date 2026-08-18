---
issue_type: Story
key: US-04
summary: Data source dependency scanner
parent_epic: contract-note-data-source-extensibility
identity_label: s2s-contract-note-data-source-extensibility-US-04
labels:
- s2s-contract-note-data-source-extensibility
- s2s-contract-note-data-source-extensibility-US-04
- backend
estimate_days: 1.0
covers_requirements:
- '4'
wave: 2
depends_on:
- US-01
blocks:
- US-07
---

As a Business_User, I want shared sections to automatically track which data sources they depend on, derived from the namespaced fields used across all of a section's variant schemas, so that templates using them can be checked.

## Description

Delivers the shared dependency scanner that lets shared sections auto-track which data sources they depend on. It reads a shared section's variant Schema_JSON (`{ schemas: [[...]] }`), collects the namespaced field references (element `name`s containing a `.`), and maps each prefix to a data source table. On a variant schema save or version publish, it recomputes the section's dependencies as the union across all of that section's variants and reconciles the `DATASOURCE_DEP` records so they can be displayed on the shared section detail screen. Wave 2 story; consumed downstream by US-07's missing-dependency enforcement.

## Delivers

- `shared-lib:dependency-scanner` — the pdf-me Schema_JSON field-reference scanner plus the shared-section dependency recompute/reconcile logic.

## Acceptance criteria

- **Given** a shared section whose variant schemas reference namespaced fields, **when** dependencies are tracked, **then** the section's dependency list equals the union of distinct data sources referenced across all of its variants' schemas.
- **Given** a shared section variant, **when** its schema is saved or a new version is published, **then** the system recomputes the section's data source dependencies from all variants' current schemas.
- **Given** a recomputed dependency set, **when** reconciliation runs, **then** `DATASOURCE_DEP` records are added or removed to match, so they display on the shared section detail screen.

## Dependencies

- US-01 — Foundation: shared data-source types & infrastructure

## Traceability

Covers parent requirements: 4 · `s2s-contract-note-data-source-extensibility-US-04`
