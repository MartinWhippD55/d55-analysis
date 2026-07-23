---
issue_type: Story
key: US-08
summary: Angular module, routing & services
parent_epic: contract-note-template-management
identity_label: s2s-contract-note-template-management-US-08
labels:
- s2s-contract-note-template-management
- s2s-contract-note-template-management-US-08
- frontend
estimate_days: 1.0
covers_requirements:
- '15'
wave: 4
depends_on:
- US-01
- US-02
- US-03
- US-04
- US-05
blocks:
- US-09
---

As a Business_User, I want the contract-note admin module wired into the portal with auth-guarded routes and API services, so that the screens have data and access is restricted.

## Description

This wave-4 frontend story sets up the Angular feature module for the contract-note admin area at `portal/src/app/components/contract-notes/`. It delivers the module's routes (template list, template edit, shared sections, rules configuration), a Cognito-group route guard, and the three HTTP services (`TemplateService`, `SectionService`, `RulesService`) that wrap the backend endpoints from US-02/US-03/US-04/US-05.

It carries no screen markup of its own — it is the routing and data layer the screens and components in US-09 build on. The services type their payloads with the shared interfaces from US-01. It covers parent requirement 15 (authentication and authorisation), owning route access control; the sidebar navigation entry that links into these routes is added in US-10.

## Delivers

- `frontend-component:ContractNoteModule` — the Angular feature module at `portal/src/app/components/contract-notes/`, declaring routes for the template list, template edit, shared sections and rules configuration areas, plus a Cognito-group route guard.
- `service:TemplateService` — `list`, `create`, `get`, `update`, `delete`, `reorder` over the `/contract-note-templates` endpoints (US-02).
- `service:SectionService` — section CRUD + reorder, schema get/save, version list/get/revert, shared-section CRUD + references, publish + linked-templates, and variant + variant-rule operations over the `/contract-note-sections` and `/contract-note-templates/{id}/sections` endpoints (US-03/US-04).
- `service:RulesService` — `get`/`save` the specification for a template over `/contract-note-templates/{id}/rule` (US-05), reusable for the variant-rule flow.

## Acceptance criteria

- **Given** the portal, **when** the `ContractNoteModule` is loaded, **then** it defines routes for the template list, template edit, shared sections and rules configuration areas (parent 15.1).
- **Given** any navigation into a `ContractNoteModule` route, **when** the route guard runs, **then** access is granted if and only if the user is authenticated and holds the required Cognito group (Property 39, parent 15.1).
- **Given** an unauthenticated user, **when** they attempt to access a module route, **then** the guard redirects them to the login flow (parent 15.2).
- **Given** an authenticated user without the required Cognito group, **when** they attempt to access a module route, **then** the guard shows an access-denied view (parent 15.3).
- **Given** the services, **when** any operation is invoked, **then** it targets the correct API Gateway endpoint with the correct HTTP method and payload, typed with the US-01 shared interfaces — `TemplateService` covers list/create/get/update/delete/reorder; `SectionService` covers section CRUD + reorder, schema get/save, version list/get/revert, shared-section CRUD + references, publish, and variants; `RulesService` covers get/save of a template's specification (parent 15.1).

## Dependencies

- US-01 — Foundation: infrastructure & shared types
- US-02 — Template CRUD API
- US-03 — Section, shared-section, version history & change log API
- US-04 — Section version publishing & variants API
- US-05 — Template selection rules API

## Traceability

Covers parent requirements: 15 · `s2s-contract-note-template-management-US-08`
