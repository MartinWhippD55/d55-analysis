# Requirements Document

**Story US-07 — pdf-me Designer web component**

> Mini-spec derived from parent spec **contract-note-template-management**.
> Delivers user story **US-07**. See `manifest.yaml` for the component
> exports/dependencies and `../../graph.yaml` for the full delivery graph.

## Introduction

This story delivers the `<pdfme-designer>` Web Component: a thin wrapper around the
React pdf-me Designer that lets a Business_User position fields on a section layout
without developer help. It is a self-contained, framework-agnostic custom element that
takes schema JSON in and emits updated schema JSON out, built as a separate bundle
loaded on demand.

It is a wave-1 story with no upstream dependencies — it is pure frontend packaging with
no reliance on the API or shared types. The Angular section-editor host (US-09) mounts
this component and wires it to the Section API.

## Glossary

- **Section_Editor**: The embedded pdf-me visual designer used to configure section
  layout and field placement.
- **Schema_JSON**: The pdf-me template definition (a `schemas` array, one entry per page)
  with positioned field definitions (type, position, dimensions, font).
- **Web Component**: A framework-agnostic custom element (`<pdfme-designer>`) wrapping
  the React designer so Angular can host it without a React bridge.

## Delivered components

This story is responsible for creating and owning:

- `web-component:pdfme-designer` — the `<pdfme-designer>` custom element wrapping the
  React pdf-me Designer, built as an on-demand bundle

## Dependencies

None — this is a wave-1 story with no upstream dependencies. It is a standalone
frontend bundle; the Angular host that consumes it lives in US-09.

## Requirements

### Requirement 1: Embedded visual section designer  _(parent: Requirement 7)_

**User Story:** As a Business_User, I want an embedded visual designer, so that I can
position fields on a section layout without developer help.

#### Acceptance Criteria

1. THE `<pdfme-designer>` Web Component SHALL load the React pdf-me Designer and mount it
   on `connectedCallback`, unmounting the React root on `disconnectedCallback`. _(parent 7.1)_
2. THE component SHALL accept a `schema-json` attribute/property for its initial state and
   support text, multiVariableText and table schema types with field position (x, y),
   dimensions (width, height), font settings and alignment. _(parent 7.2, 7.4)_
3. WHEN the user saves, THE component SHALL dispatch a `schema-save` CustomEvent carrying
   the updated schema JSON. _(parent 7.3)_
4. THE component SHALL be built as a separate bundle (React + pdf-me Designer) loaded
   on-demand when the section editor opens. _(parent 7.1)_
