---
issue_type: Story
key: US-07
summary: pdf-me Designer web component
parent_epic: contract-note-template-management
identity_label: s2s-contract-note-template-management-US-07
labels:
- s2s-contract-note-template-management
- s2s-contract-note-template-management-US-07
- frontend
estimate_days: 1.0
covers_requirements:
- '7'
wave: 1
depends_on: []
blocks:
- US-09
---

As a Business_User, I want an embedded visual designer, so that I can position fields on a section layout without developer help.

## Description

Delivers the `<pdfme-designer>` Web Component: a thin, framework-agnostic custom element that wraps the React pdf-me Designer. It takes schema JSON in via a property and emits updated schema JSON out via a CustomEvent, so a Business_User can position fields on a section layout without developer help. Using a custom element avoids an Angular-React bridge library and isolates the React dependency in its own on-demand bundle. This is a wave-1 story with no upstream dependencies — pure presentation packaging. The Angular SectionEditorComponent (US-09) hosts this element and wires it to the Section API (US-03).

## Delivers

- `web-component:pdfme-designer` — the `<pdfme-designer>` custom element wrapping the React pdf-me Designer.
- A separate frontend bundle (React + pdf-me Designer) loaded on demand when the section editor opens.
- A `schema-json` attribute/property (schema JSON in) and a `schema-save` CustomEvent (updated schema JSON out).

## Acceptance criteria

- **Given** the `<pdfme-designer>` element is added to the DOM, **when** `connectedCallback` fires, **then** it loads the React pdf-me Designer from the on-demand bundle and mounts the React root; **when** the element is removed, **then** `disconnectedCallback` unmounts the React root.
- **Given** a `schema-json` attribute/property holding valid schema JSON, **when** the component initialises, **then** it renders the designer with that schema and supports text, multiVariableText and table schema types, each with field position (x, y), dimensions (width, height), font settings and alignment.
- **Given** the user has edited a section layout, **when** they save, **then** the component dispatches a `schema-save` CustomEvent carrying an equivalent, well-formed schema JSON structure (Property 15: save/load round-trip).
- **Given** the designer bundle fails to load or mount, **when** the component tries to render, **then** it surfaces a failure state so the host (US-09) can show an error with a retry option.
- **Given** malformed incoming `schema-json`, **when** the component initialises, **then** it defensively starts an empty designer rather than crashing the host page.

## Dependencies

- None — foundation story.

## Traceability

Covers parent requirements: 7 · `s2s-contract-note-template-management-US-07`
