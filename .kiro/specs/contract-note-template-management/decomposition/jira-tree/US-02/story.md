---
issue_type: Story
key: US-02
summary: Template CRUD API
parent_epic: contract-note-template-management
identity_label: s2s-contract-note-template-management-US-02
labels:
- s2s-contract-note-template-management
- s2s-contract-note-template-management-US-02
- backend
- api
estimate_days: 1.5
covers_requirements:
- '1'
- '2'
- '3'
- '4'
- '5'
wave: 2
depends_on:
- US-01
blocks:
- US-08
- US-10
---

As a Business_User, I want to create, list, edit, delete and reorder templates, so that I can manage contract note template definitions.

## Description

Delivers the Template API — the metadata backbone of the feature. This story implements the Lambda handlers behind the `/contract-note-templates` routes that let a Business_User list, create, edit, delete and reorder contract note templates. The handlers read and write the `ContractNoteTemplates` table and attach to the API Gateway route surface provisioned by US-01. They perform no rendering and define no new storage. This is a wave-2 story: it depends on the US-01 foundation and unblocks the frontend services (US-08) and the render pipeline (US-06), which read templates in priority order via the shared table.

## Delivers

- `lambda:template-handlers` — the Lambda handler set implementing all six operations.
- `api-endpoint:GET /contract-note-templates` — list templates in priority order.
- `api-endpoint:POST /contract-note-templates` — create a template at lowest priority, with validation.
- `api-endpoint:GET /contract-note-templates/{id}` — get a single template's metadata (404 if absent).
- `api-endpoint:PUT /contract-note-templates/{id}` — update name/description.
- `api-endpoint:DELETE /contract-note-templates/{id}` — delete and re-compact remaining priorities.
- `api-endpoint:PUT /contract-note-templates/reorder` — batch reorder priority.

## Acceptance criteria

- **Given** a set of stored templates, **when** the list endpoint is called, **then** the handler queries the `PriorityIndex` GSI and returns all templates ordered by `priority` ascending, each with `name`, `description`, `sectionCount` and `priority`.
- **Given** no templates exist, **when** the list endpoint is called, **then** the handler returns an empty collection so the frontend can render an empty state.
- **Given** a valid create request with `name` and `description`, **when** it is received, **then** the handler creates the template and assigns it the lowest priority (existing count + 1).
- **Given** a create request whose `name` duplicates an existing template, **when** it is received, **then** the handler returns a 409 error indicating the name is already in use.
- **Given** a create request with missing required fields, **when** it is received, **then** the handler returns a 400 with field-level validation errors identifying the missing fields.
- **Given** a template id, **when** get is called, **then** the handler returns its metadata, or 404 if not found.
- **Given** an existing template and a valid update, **when** update is called, **then** the handler persists the new `name` and `description`.
- **Given** N templates with contiguous priorities 1..N, **when** one is deleted, **then** the handler removes the template and its template-owned `SECTION#` records, leaves shared sections untouched, and re-compacts the remaining priorities to 1..N-1.
- **Given** an ordered array of template ids, **when** reorder is called, **then** the handler batch-updates priorities to contiguous integers starting at 1 matching the requested order, and the change persists across sessions.

## Dependencies

- US-01 — Foundation: infrastructure & shared types

## Traceability

Covers parent requirements: 1, 2, 3, 4, 5 · `s2s-contract-note-template-management-US-02`
