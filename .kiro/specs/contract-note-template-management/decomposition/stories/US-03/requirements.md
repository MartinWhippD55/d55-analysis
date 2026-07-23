# Requirements Document

**Story US-03 — Section, shared-section, version history & change log API**

> Mini-spec derived from parent spec **contract-note-template-management**.
> Delivers user story **US-03**. See `manifest.yaml` for the component
> exports/dependencies and `../../graph.yaml` for the full delivery graph.

## Introduction

This story delivers the Section API: the Lambda handlers that let a Business_User
compose a template's sections (add, remove, reorder, including T&C positioning),
edit each section's pdf-me schema JSON with full version history, manage reusable
shared sections and their references, and read a per-template change log. It is the
content-management backbone that sits alongside the Template API (US-02) on the same
table.

It is a wave-2 story depending on the US-01 foundation (table, schema-json bucket,
shared types, route surface). It provides the section/version handlers that US-04
(publishing & variants) builds on and that the frontend (US-08/09) consumes.

## Glossary

- **Section**: An independently editable portion of a template, stored as a pdf-me
  Schema_JSON; a template-owned `SECTION#` record.
- **Shared_Section**: A section marked reusable across templates (headers, footers,
  T&Cs), stored under `SHARED_SECTION#{id}`.
- **Terms_And_Conditions_Document**: A Shared_Section designated as T&C, positioned as
  the final section(s) of a template.
- **Schema_JSON**: The pdf-me template definition (a `schemas` array, one entry per
  page) stored in the `schema-json` S3 bucket.
- **Section Version**: An immutable record of a section's schema JSON at a point in
  time, keyed by `SECTION_VERSION#{sectionId}#{variantId}`.
- **Template Change Log**: The chronological record of template modifications.

## Delivered components

This story is responsible for creating and owning:

- `api-endpoint:sections-crud` — list/add/remove/reorder template sections
- `api-endpoint:section-schema` — get/save a section's schema JSON (save writes a version)
- `api-endpoint:section-versions` — list/get/revert section versions
- `api-endpoint:shared-sections-crud` — shared section CRUD + reference listing
- `api-endpoint:template-changelog` — read a template's change log
- `lambda:section-handlers` — the Lambda handlers implementing the above

## Dependencies

This story depends on components delivered by other stories (must be available first):

- `shared-lib:types` (from US-01) — `Section`, `SharedSection`, record types
- `data-table:ContractNoteTemplates` (from US-01) — the metadata store
- `s3-bucket:schema-json` (from US-01) — schema JSON storage
- `cdk-construct:ApiGatewayRoutes` (from US-01) — the route surface these handlers attach to

## Requirements

### Requirement 1: Section composition  _(parent: Requirements 3, 6)_

**User Story:** As a Business_User, I want to add, remove and reorder sections within a
template, so that I can compose the contract note document structure.

#### Acceptance Criteria

1. WHEN sections are listed for a template, THE handler SHALL return them ordered by
   sortOrder ascending. _(parent 3.3, 6.1)_
2. WHEN a section is added, THE handler SHALL append it (sortOrder = current max + 1);
   when a shared section is added it SHALL create a reference (isShared, sharedSectionId,
   shared schemaS3Key) without duplicating the definition. _(parent 6.1, 6.4)_
3. WHEN a section is removed, THE handler SHALL re-order remaining sections to contiguous
   sortOrder and remove the shared-section reference if present. _(parent 6.2)_
4. WHEN sections are reordered, THE handler SHALL persist the new order and keep T&C
   sections positioned after all non-T&C sections. _(parent 6.3, 6.5, 9.2)_

### Requirement 2: Section schema editing with versioning  _(parent: Requirements 7, 16)_

**User Story:** As a Business_User, I want to save a section's schema JSON as a new
version each time, so that edits are visually applied without losing history.

#### Acceptance Criteria

1. WHEN a section's schema is fetched, THE handler SHALL read the schema JSON from S3
   at the section's schemaS3Key and return it. _(parent 7.1)_
2. WHEN a section's schema is saved, THE handler SHALL validate the schema JSON, write
   it to S3, and create a new Section Version record (timestamp + user) rather than
   overwriting the previous version. _(parent 7.3, 16.1)_

### Requirement 3: Section version history  _(parent: Requirement 16)_

**User Story:** As a Business_User, I want to view and revert to previous section
versions, so that I can undo mistakes or compare changes.

#### Acceptance Criteria

1. WHEN versions are listed, THE handler SHALL return version records ordered by
   timestamp descending (version number, timestamp, user). _(parent 16.2)_
2. WHEN a specific version is requested, THE handler SHALL return that version's schema
   JSON. _(parent 16.3)_
3. WHEN a revert to a historical version is confirmed, THE handler SHALL create a new
   version with that historical content (non-destructive), leaving intermediate
   versions accessible. _(parent 16.4, 16.5)_

### Requirement 4: Shared section management  _(parent: Requirements 8, 9)_

**User Story:** As a Business_User, I want to create and manage shared sections
(including T&Cs), so that common elements are reusable across templates.

#### Acceptance Criteria

1. WHEN shared sections are listed, THE handler SHALL return all of them (including
   T&C) with reference counts. _(parent 8.1, 9.1, 9.4)_
2. THE handler SHALL support creating and updating a shared section, including T&C
   designation. _(parent 8.1, 9.1)_
3. WHEN a shared section's references are requested, THE handler SHALL return exactly
   the templates that include it. _(parent 8.3)_
4. IF a delete targets a shared section referenced by one or more templates, THEN THE
   handler SHALL block with a 409 and return the referencing templates. _(parent 8.4)_

### Requirement 5: Template change log  _(parent: Requirement 17)_

**User Story:** As a Business_User, I want a change log of a template's configuration
changes, so that I can understand what changed and when.

#### Acceptance Criteria

1. WHEN a template is modified (section add/remove/reorder, metadata or rule change),
   THE handler SHALL record a change log entry with timestamp, user and description.
   _(parent 17.1)_
2. WHEN the change log is requested, THE handler SHALL return the chronological list of
   changes for that template. _(parent 17.2, 17.3)_
