---
issue_type: Story
key: US-03
summary: Section, shared-section, version history & change log API
parent_epic: contract-note-template-management
identity_label: s2s-contract-note-template-management-US-03
labels:
- s2s-contract-note-template-management
- s2s-contract-note-template-management-US-03
- backend
- api
estimate_days: 2.0
covers_requirements:
- '3'
- '6'
- '7'
- '8'
- '9'
- '16'
- '17'
wave: 2
depends_on:
- US-01
blocks:
- US-04
- US-08
- US-10
---

As a Business_User, I want to compose sections, edit their schema with version history, manage shared sections and see a change log, so that I can build and maintain template content.

## Description

This story delivers the Section API: the Lambda handlers that let a Business_User compose a template's sections (add, remove, reorder, including T&C positioning), edit each section's pdf-me schema JSON with full version history, manage reusable shared sections and their references, and read a per-template change log. It is the content-management backbone that sits alongside the Template API (US-02) on the shared `ContractNoteTemplates` table.

It is a wave-2 story that depends on the US-01 foundation (table, `schema-json` bucket, shared types, route surface). It attaches its handlers to the US-01 route surface, reads and writes section/shared-section/version/reference/change-log records on the shared table, and stores schema JSON blobs in the `schema-json` S3 bucket. It provides the `section-versions` and section/variant records that US-04 (publishing & variants) builds on, and the endpoints the frontend (US-08, US-10) consumes.

## Delivers

- `api-endpoint:sections-crud` — list/add/remove/reorder template sections (list-sections, add-section, remove-section, reorder-sections).
- `api-endpoint:section-schema` — get/save a section's schema JSON; save writes a new version (get-section-schema, save-section-schema).
- `api-endpoint:section-versions` — list/get/revert section versions (list-section-versions, get-section-version, revert-section-version).
- `api-endpoint:shared-sections-crud` — shared section CRUD plus reference listing (list/create/update/delete-shared-section, get-shared-section-refs).
- `api-endpoint:template-changelog` — read a template's change log (list-template-changelog).
- `lambda:section-handlers` — the Lambda handler set implementing all of the above.

## Acceptance criteria

- **Given** a template with sections, **when** its sections are listed, **then** the handler returns them ordered by `sortOrder` ascending.
- **Given** a template with N sections, **when** a section is added, **then** the handler appends it with `sortOrder = current max + 1`, giving N+1 sections; and when the added section is a shared section, it creates a reference (sets `isShared`, `sharedSectionId` and reuses the shared `schemaS3Key`) rather than duplicating the definition.
- **Given** a template with N sections, **when** a section is removed, **then** the remaining sections are re-ordered to contiguous `sortOrder` (N-1 sections) and the shared-section reference is removed if present.
- **Given** a template with regular and T&C sections, **when** sections are reordered, **then** the new order is persisted and all T&C sections keep a `sortOrder` greater than every non-T&C section.
- **Given** a section, **when** its schema is fetched, **then** the handler reads the schema JSON from S3 at the section's `schemaS3Key` and returns it.
- **Given** a valid schema JSON, **when** it is saved for a section, **then** the handler validates it, writes it to S3, and appends a new Section Version record (timestamp + user) rather than overwriting the previous version, so the version count increases by exactly 1; an invalid schema JSON returns a 400.
- **Given** a section with version history, **when** versions are listed, **then** the handler returns records ordered by timestamp descending (version, timestamp, user); and when a specific version is requested, it returns that version's schema JSON.
- **Given** a historical section version V, **when** a revert is confirmed, **then** the handler creates a new version N+1 with V's content (non-destructive) and all intermediate versions remain accessible.
- **Given** the set of shared sections, **when** they are listed, **then** the handler returns all of them (including T&C) with reference counts; and it supports creating and updating a shared section including T&C designation.
- **Given** a shared section, **when** its references are requested, **then** the handler returns exactly the templates that include it.
- **Given** a shared section referenced by one or more templates, **when** a delete targets it, **then** the handler blocks with a 409 and returns the referencing templates.
- **Given** a template modification (section add/remove/reorder, metadata or rule change), **when** it occurs, **then** the handler records a change log entry with timestamp, user and description; and when the change log is requested, it returns the chronological list of changes for that template.

## Dependencies

- US-01 — Foundation: infrastructure & shared types

## Traceability

Covers parent requirements: 3, 6, 7, 8, 9, 16, 17 · `s2s-contract-note-template-management-US-03`
