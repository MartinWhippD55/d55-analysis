# Design Document

**Story US-09 — Angular screens & components**

> Mini-spec derived from parent spec **contract-note-template-management**, story **US-09**.
> This design is an excerpt of the parent design scoped to this story's components.

## Overview

US-09 implements every user-facing screen and component of the contract-note admin area
inside the US-08 module: the template list and edit landing pages, the recursive rules
tree editor, the section editor modal hosting the US-07 pdf-me designer, the shared
sections library, the version history and publish surfaces, the inline variants manager,
and the navigation between landing pages. It consumes the US-08 services for all data.

## Architecture

This story owns the presentation layer. Components inject the US-08 services; the section
editor hosts the US-07 web component; landing pages are full screens while the editor and
version history are modals launched from within them.

```mermaid
graph TD
    subgraph Screens/Components (US-09)
        TLC[TemplateList] --> TEC[TemplateEdit]
        TEC --> RCC[RulesConfig]
        TEC --> SEC[SectionEditor modal]
        TEC --> SVH[VersionHistory modal]
        TEC --> SV[SectionVariants inline]
        SVH --> SP[SectionPublish]
        SSL[SharedSectionsLibrary]
        NAV[Navigation]
    end
    SEC --> WC[<pdfme-designer> — US-07]
    TLC --> TS[TemplateService — US-08]
    SV --> SS[SectionService — US-08]
    RCC --> RS[RulesService — US-08]
```

## Components and Interfaces

### frontend-screen:TemplateList

Ordered table (name, description, section count, priority), reorder (drag/up-down),
create/edit/delete/configure-rules actions, empty state, deletion confirmation.

### frontend-screen:TemplateEdit

Name/description form (required + duplicate validation), ordered section list with
add/remove/reorder (new, shared, T&C), per-section version badge and history button,
inline variants list, and a collapsible change log panel.

### frontend-component:RulesConfigComponent

Recursive tree editor: AND/OR/NOT + EQUALS/LESS_THAN/MORE_THAN/IN, add/remove nodes, leaf
field/value inputs, validation with incomplete-node highlighting. Reused for template and
variant rules.

### frontend-component:SectionEditorComponent

Angular modal host for `<pdfme-designer>` (US-07): loads schema from the API, saves on the
`schema-save` event, shows an error/retry state if the designer fails to load.

### frontend-component:SectionVersionHistoryComponent

Current version highlighted; previous versions (number, timestamp, user) with preview
(read-only in editor) and revert; launches SectionPublishComponent.

### frontend-component:SectionVariantsComponent

Inline variant list on the template edit page (name, rule summary, default badge, order)
with add/reorder/set-default/delete, per-variant section editor and per-variant rules
editor (reusing RulesConfigComponent).

### frontend-component:SectionPublishComponent

Lists linked templates with pinned version + update-available; publishes a chosen version
(default latest) to all linked templates with confirmation.

### frontend-screen:SharedSectionsLibrary

Lists shared sections (name, type, reference count); detail shows referencing templates;
create/edit/delete with referenced-deletion warnings.

### frontend-component:Navigation

Entry points to the Template List and Shared Sections Library landing pages, gated by
Cognito group; keeps the section editor and version history as modals within a landing page.

### Interfaces consumed (dependencies)

- `frontend-component:ContractNoteModule`, `service:TemplateService`, `service:SectionService`,
  `service:RulesService` (US-08) — module + data layer.
- `web-component:pdfme-designer` (US-07) — the designer the section editor hosts.

### Touch points with other stories

- **US-08** provides the services and routes; this story fills them with screens.
- **US-10** adds the portal sidebar entry that routes into the Navigation exposed here.

## Data Models

This story defines no persisted data. It binds the shared DTOs (`Template`, `Section`,
`SharedSection`, `SectionVariant`, `SectionReference`, `SpecificationNode`) into forms,
tables and the tree editor.

## Correctness Properties

The parent's universal invariants are validated server-side (US-02–US-06). This story's
front-end guarantee is presentational — the rules editor's client-side well-formedness
check mirrors the server validation before save.

### Property 21: Specification validation rejects malformed trees

*For any* incomplete specification tree built in the editor (missing operands or
comparison values), the editor SHALL block save and highlight the incomplete nodes.
**Validates: Requirements 10.5**

## Error Handling

| Scenario | Handling |
|----------|----------|
| API request failure (network) | Toast with retry; preserve form state |
| Validation errors (400) | Highlight invalid fields; field-level messages |
| Section Editor fails to load | Error state in modal with retry button |
| Drag-and-drop reorder fails | Revert to previous order; error notification |
| Not found (404) | Message + redirect to the relevant list |

## Testing Strategy

- Unit tests: TemplateListComponent rendering/empty state/action triggers;
  RulesConfigComponent tree manipulation and validation display (Property 21);
  SectionEditorComponent lifecycle and event handling; SectionVariantsComponent
  ordering/default logic; SectionPublishComponent publish-to-all confirmation.
- Component tests use the US-08 services mocked.
