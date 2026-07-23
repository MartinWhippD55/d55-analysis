# Requirements Document

**Story US-02 — Template CRUD API**

> Mini-spec derived from parent spec **contract-note-template-management**.
> Delivers user story **US-02**. See `manifest.yaml` for the component
> exports/dependencies and `../../graph.yaml` for the full delivery graph.

## Introduction

This story delivers the Template API: the Lambda handlers behind the
`/contract-note-templates` routes that let a Business_User list, create, edit,
delete and reorder contract note templates. It is the metadata backbone of the
feature — every template the frontend shows and every template the render
pipeline selects from is created and ordered here.

It is a wave-2 story. It depends on the US-01 foundation (the
`ContractNoteTemplates` table, the `PriorityIndex` GSI, the shared types and the
API Gateway route surface) and attaches its handlers to that route surface. Its
consumers are the frontend services (US-08) and, indirectly through the shared
table, the render pipeline (US-06).

## Glossary

- **Template**: A contract note PDF template composed of ordered sections with an
  associated selection rule, stored as a `TEMPLATE#{id}` / `METADATA` record.
- **Template_List**: The ordered set of templates; ordering (the `priority`
  integer) determines rule-evaluation priority.
- **PriorityIndex**: The GSI (from US-01) that returns all templates ordered by
  `priority` in a single query.

## Delivered components

This story is responsible for creating and owning:

- `api-endpoint:GET /contract-note-templates` — list templates in priority order
- `api-endpoint:POST /contract-note-templates` — create a template at lowest priority
- `api-endpoint:PUT /contract-note-templates/{id}` — update name/description
- `api-endpoint:DELETE /contract-note-templates/{id}` — delete and reorder remaining
- `api-endpoint:PUT /contract-note-templates/reorder` — batch reorder priority
- `lambda:template-handlers` — the Lambda handlers implementing the above

## Dependencies

This story depends on components delivered by other stories (must be available first):

- `shared-lib:types` (from US-01) — `Template` interface and DynamoDB record types
- `data-table:ContractNoteTemplates` (from US-01) — the metadata store
- `gsi:PriorityIndex` (from US-01) — priority-ordered template queries
- `cdk-construct:ApiGatewayRoutes` (from US-01) — the route surface these handlers attach to

## Requirements

### Requirement 1: Template listing  _(parent: Requirement 1)_

**User Story:** As a Business_User, I want to view all contract note templates in an
ordered list, so that I can understand which templates exist and their evaluation
priority.

#### Acceptance Criteria

1. WHEN the list endpoint is called, THE handler SHALL query the `PriorityIndex`
   GSI and return all templates ordered by priority ascending. _(parent 1.1)_
2. THE handler SHALL return the name, description, section count and priority for
   each template. _(parent 1.2)_
3. WHEN no templates exist, THE handler SHALL return an empty collection so the
   frontend can render an empty state. _(parent 1.3)_

### Requirement 2: Template creation  _(parent: Requirement 2)_

**User Story:** As a Business_User, I want to create new contract note templates, so
that I can define new document layouts for different contract types.

#### Acceptance Criteria

1. WHEN a valid create request is received, THE handler SHALL create a template
   with the provided name and description. _(parent 2.1)_
2. THE handler SHALL assign the new template the lowest priority (existing count + 1).
   _(parent 2.2)_
3. IF the name duplicates an existing template, THEN THE handler SHALL return a 409
   validation error indicating the name is already in use. _(parent 2.3)_
4. IF required fields are missing, THEN THE handler SHALL return a 400 with
   field-level validation errors. _(parent 2.4)_

### Requirement 3: Template editing  _(parent: Requirement 3)_

**User Story:** As a Business_User, I want to edit existing templates, so that I can
update template metadata.

#### Acceptance Criteria

1. WHEN a template is fetched by id, THE handler SHALL return its metadata, or 404
   if not found. _(parent 3.1)_
2. WHEN an update request is received, THE handler SHALL persist the updated name
   and description. _(parent 3.2)_

### Requirement 4: Template deletion  _(parent: Requirement 4)_

**User Story:** As a Business_User, I want to delete templates that are no longer
needed, so that the template list remains current.

#### Acceptance Criteria

1. WHEN a delete request is received, THE handler SHALL remove the template and its
   template-owned section records. _(parent 4.1, 4.2)_
2. THE handler SHALL re-order the remaining templates to maintain contiguous
   priority ordering 1..N-1. _(parent 4.2)_
3. THE handler SHALL NOT delete shared sections referenced by the template. _(parent 4.3)_

### Requirement 5: Template priority ordering  _(parent: Requirement 5)_

**User Story:** As a Business_User, I want to reorder templates, so that I can control
which template rules are evaluated first during automated processing.

#### Acceptance Criteria

1. WHEN a reorder request with an ordered list of template ids is received, THE
   handler SHALL batch-update priority values to contiguous integers starting at 1
   matching the requested order. _(parent 5.1)_
2. THE handler SHALL persist the updated priority ordering so it survives across
   sessions. _(parent 5.2)_
