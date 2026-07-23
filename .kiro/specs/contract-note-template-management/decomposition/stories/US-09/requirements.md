# Requirements Document

**Story US-09 — Angular screens & components**

> Mini-spec derived from parent spec **contract-note-template-management**.
> Delivers user story **US-09**. See `manifest.yaml` for the component
> exports/dependencies and `../../graph.yaml` for the full delivery graph.

## Introduction

This story delivers the full set of contract-note admin screens and components: the
template list landing page, the template edit page (with change log and inline variant
list), the rules tree editor, the section editor modal hosting the pdf-me designer, the
shared sections library, the version history and publish surfaces, the variants
manager, and the navigation that ties the landing pages together.

It is a wave-5 story. It depends on the US-08 module and services and on the US-07
pdf-me designer web component. It is the last user-facing piece before integration
(US-10).

## Glossary

- **Landing_Page**: A full-screen list/management view (as distinct from a modal).
- **Section_Editor**: The pdf-me designer surface, presented as a modal.
- **RulesConfigComponent**: The visual specification tree editor, reused for template and
  variant rules.
- **Section_Variant / Pinned_Version**: See parent glossary; surfaced inline on the
  template edit page and in the publish flow.

## Delivered components

This story is responsible for creating and owning:

- `frontend-screen:TemplateList` — the template list landing page
- `frontend-screen:TemplateEdit` — the template edit page (sections, change log, variants)
- `frontend-screen:SharedSectionsLibrary` — the shared sections landing page
- `frontend-component:RulesConfigComponent` — the specification tree editor
- `frontend-component:SectionEditorComponent` — modal host for `<pdfme-designer>`
- `frontend-component:SectionVersionHistoryComponent` — version list, preview, revert
- `frontend-component:SectionVariantsComponent` — inline variant management
- `frontend-component:SectionPublishComponent` — publish a version to linked templates
- `frontend-component:Navigation` — nav entry points to the landing pages

## Dependencies

This story depends on components delivered by other stories (must be available first):

- `frontend-component:ContractNoteModule` (from US-08) — the module + routes these screens live in
- `service:TemplateService` (from US-08) — template data
- `service:SectionService` (from US-08) — section/version/shared/publish/variant data
- `service:RulesService` (from US-08) — specification get/save
- `web-component:pdfme-designer` (from US-07) — the designer the section editor hosts

## Requirements

### Requirement 1: Template list & edit screens  _(parent: Requirements 1, 2, 3, 4, 5, 6, 17)_

**User Story:** As a Business_User, I want template list and edit screens, so that I can
manage templates and their sections.

#### Acceptance Criteria

1. THE `TemplateList` screen SHALL show templates (name, description, section count,
   priority) with reorder, create, edit, delete and configure-rules actions and an empty
   state. _(parent 1.1, 1.2, 1.3, 4.1, 5.1)_
2. THE `TemplateEdit` screen SHALL show the name/description form (with duplicate/required
   validation), the ordered section list with add/remove/reorder (new, shared, T&C), a
   per-section version badge and history button, and a collapsible change log panel.
   _(parent 2.1, 2.3, 2.4, 3.1, 3.2, 3.3, 6.1, 6.2, 6.3, 6.4, 6.5, 17.2, 17.3)_

### Requirement 2: Rules editor  _(parent: Requirement 10)_

**User Story:** As a Business_User, I want a visual rule editor, so that I can configure
selection specifications without code.

#### Acceptance Criteria

1. THE `RulesConfigComponent` SHALL render the specification tree with AND/OR/NOT and
   EQUALS/LESS_THAN/MORE_THAN/IN nodes, allow add/remove and leaf configuration, and
   validate before save with error highlighting on incomplete nodes. _(parent 10.1–10.6)_
2. THE same editor SHALL be reused for both template selection rules and variant rules.
   _(parent 19.7)_

### Requirement 3: Section editor & version history  _(parent: Requirements 7, 16, 18)_

**User Story:** As a Business_User, I want to edit section layouts and manage their
versions, so that I can design sections and control history.

#### Acceptance Criteria

1. THE `SectionEditorComponent` SHALL host `<pdfme-designer>` in a modal, load the schema
   from the API, save on the `schema-save` event, and show an error state with retry if
   the designer fails to load. _(parent 7.1, 7.3, 7.5)_
2. THE `SectionVersionHistoryComponent` SHALL show the current version highlighted and
   previous versions (number, timestamp, user) with preview (read-only in the editor) and
   revert actions. _(parent 16.2, 16.3, 16.4)_
3. THE `SectionPublishComponent` SHALL list linked templates with pinned version and
   update-available indicators and publish a chosen version (defaulting to latest) with
   confirmation. _(parent 18.3, 18.4, 18.5)_

### Requirement 4: Shared sections, variants & navigation  _(parent: Requirements 8, 9, 19, 21)_

**User Story:** As a Business_User, I want a shared sections library, inline variant
management and clear navigation, so that I can manage everything from the portal.

#### Acceptance Criteria

1. THE `SharedSectionsLibrary` screen SHALL list shared sections (name, type, reference
   count), show referencing templates, and support create/edit/delete with a
   referenced-deletion warning. _(parent 8.1, 8.2, 8.3, 8.4, 9.1, 9.3, 9.4)_
2. THE `SectionVariantsComponent` SHALL list variants inline on the template edit page
   (name, rule summary, default badge, order) with add/reorder/set-default/delete, the
   per-variant section editor, and the per-variant rules editor. _(parent 19.1, 19.2, 19.3, 21.4)_
3. THE `Navigation` SHALL expose entry points to the Template List and Shared Sections
   Library as full landing pages (gated by Cognito group), with the section editor and
   version history presented as modals launched from within a landing page. _(parent 21.1, 21.2, 21.3, 21.5)_
