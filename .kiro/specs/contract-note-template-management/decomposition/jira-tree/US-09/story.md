---
issue_type: Story
key: US-09
summary: Angular screens & components
parent_epic: contract-note-template-management
identity_label: s2s-contract-note-template-management-US-09
labels:
- s2s-contract-note-template-management
- s2s-contract-note-template-management-US-09
- frontend
estimate_days: 3.0
covers_requirements:
- '1'
- '2'
- '3'
- '4'
- '5'
- '6'
- '7'
- '8'
- '9'
- '10'
- '16'
- '17'
- '18'
- '19'
- '21'
wave: 5
depends_on:
- US-07
- US-08
blocks:
- US-10
---

As a Business_User, I want the full set of screens (template list, template edit, rules config, section editor, shared sections, version history, variants, publish) and navigation, so that I can manage everything from the portal.

## Description

This wave-5 frontend story builds every user-facing screen and component of the contract-note admin area. It owns the presentation layer inside the `ContractNoteModule` from US-08: the template list and template edit landing pages, the recursive rules tree editor, the section editor modal that hosts the US-07 `<pdfme-designer>` web component, the shared sections library, the section version history and publish surfaces, the inline section variants manager, and the navigation that ties the landing pages together.

It defines no persisted data of its own. Every component injects the US-08 services (`TemplateService`, `SectionService`, `RulesService`) for data and binds the shared DTOs (`Template`, `Section`, `SharedSection`, `SectionVariant`, `SectionReference`, `SpecificationNode`) into forms, tables and the tree editor. It is the last user-facing piece before integration: it depends on US-07 (pdf-me designer) and US-08 (module, routing, services) and unblocks US-10, which adds the portal sidebar entry that routes into the navigation exposed here.

## Delivers

- `frontend-screen:TemplateList` — the template list landing page (name, description, section count, priority) with reorder, create, edit, delete, configure-rules actions and an empty state.
- `frontend-screen:TemplateEdit` — the template edit page: name/description form, ordered section list (add/remove/reorder new, shared, T&C), per-section version badge + history button, inline variant list, and a collapsible change log panel.
- `frontend-screen:SharedSectionsLibrary` — the shared sections landing page listing shared sections (name, type, reference count) with referencing-template detail and create/edit/delete.
- `frontend-component:RulesConfigComponent` — the recursive specification tree editor (AND/OR/NOT + EQUALS/LESS_THAN/MORE_THAN/IN), reused for template selection rules and variant rules.
- `frontend-component:SectionEditorComponent` — modal host for `<pdfme-designer>` (US-07).
- `frontend-component:SectionVersionHistoryComponent` — version list with preview and revert.
- `frontend-component:SectionVariantsComponent` — inline variant management on the template edit page.
- `frontend-component:SectionPublishComponent` — publish a chosen version to linked templates.
- `frontend-component:Navigation` — Cognito-gated entry points to the Template List and Shared Sections Library landing pages.

## Acceptance criteria

- **Given** the template management screen, **when** a Business_User navigates to it, **then** `TemplateList` shows all templates (name, description, section count, priority) ordered by priority with reorder, create, edit, delete and configure-rules actions, and an empty state when no templates exist (parent 1.1, 1.2, 1.3, 4.1, 5.1).
- **Given** a template open for editing, **when** the Business_User views `TemplateEdit`, **then** it shows the name/description form with required + duplicate validation, the ordered section list with add/remove/reorder (new, shared, T&C), a per-section version badge and history button, and a collapsible change log panel (parent 2.1, 2.3, 2.4, 3.1, 3.2, 3.3, 6.1, 6.2, 6.3, 6.4, 6.5, 17.2, 17.3).
- **Given** the rules configuration for a template or variant, **when** the Business_User edits and saves the specification, **then** `RulesConfigComponent` renders the tree with AND/OR/NOT and EQUALS/LESS_THAN/MORE_THAN/IN nodes, allows add/remove and leaf configuration, and validates before save — blocking save and highlighting incomplete nodes for a malformed tree (Property 21, parent 10.1–10.6, 19.7).
- **Given** a section open for editing, **when** the Business_User opens `SectionEditorComponent`, **then** it hosts `<pdfme-designer>` in a modal, loads the schema from the API, saves on the `schema-save` event, and shows an error state with a retry button if the designer fails to load (parent 7.1, 7.3, 7.5).
- **Given** a section with history, **when** the Business_User opens `SectionVersionHistoryComponent`, **then** the current version is highlighted and previous versions (number, timestamp, user) offer preview (read-only in the editor) and revert (parent 16.2, 16.3, 16.4).
- **Given** a chosen section version, **when** the Business_User launches `SectionPublishComponent`, **then** it lists linked templates with their pinned version and update-available indicators and publishes the chosen version (defaulting to latest) to all linked templates with confirmation (parent 18.3, 18.4, 18.5).
- **Given** the shared sections area, **when** the Business_User opens `SharedSectionsLibrary`, **then** it lists shared sections (name, type, reference count), shows referencing templates, and supports create/edit/delete with a referenced-deletion warning (parent 8.1, 8.2, 8.3, 8.4, 9.1, 9.3, 9.4).
- **Given** a section with variants on the template edit page, **when** the Business_User manages them, **then** `SectionVariantsComponent` lists variants inline (name, rule summary, default badge, order) with add/reorder/set-default/delete, a per-variant section editor and a per-variant rules editor (parent 19.1, 19.2, 19.3, 21.4).
- **Given** the Admin Portal navigation, **when** a Business_User in the required Cognito group uses it, **then** `Navigation` exposes entry points to the Template List and Shared Sections Library as full landing pages, with the section editor and version history presented as modals launched from within a landing page (parent 21.1, 21.2, 21.3, 21.5).

## Dependencies

- US-07 — pdf-me Designer web component
- US-08 — Angular module, routing & services

## Traceability

Covers parent requirements: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 16, 17, 18, 19, 21 · `s2s-contract-note-template-management-US-09`
