# Requirements Document

**Story US-08 — Angular module, routing & services**

> Mini-spec derived from parent spec **contract-note-template-management**.
> Delivers user story **US-08**. See `manifest.yaml` for the component
> exports/dependencies and `../../graph.yaml` for the full delivery graph.

## Introduction

This story delivers the Angular scaffolding for the contract-note admin area: the
`ContractNoteModule` with its routes and a Cognito-group route guard, plus the API
services (`TemplateService`, `SectionService`, `RulesService`) that wrap the backend
endpoints. It gives the screens (US-09) their data plumbing and restricts access to
authorised staff.

It is a wave-4 story. It depends on the shared types (US-01) and on the API endpoints
delivered by US-02/US-03/US-04/US-05 so the services have real contracts to call. The
screens and components (US-09) build on this module and consume these services.

## Glossary

- **Admin_Portal**: The existing BrytAdminPortal Angular application.
- **ContractNoteModule**: The Angular feature module hosting the contract-note admin
  routes and screens.
- **Business_User**: An authenticated Admin Portal user with the appropriate Cognito
  group membership to manage contract note templates.

## Delivered components

This story is responsible for creating and owning:

- `frontend-component:ContractNoteModule` — the Angular module with routes + route guard
- `service:TemplateService` — template list/create/get/update/delete/reorder over HTTP
- `service:SectionService` — sections, schema, versions, shared sections, publish, variants
- `service:RulesService` — get/save template and variant specifications

## Dependencies

This story depends on components delivered by other stories (must be available first):

- `shared-lib:types` (from US-01) — the interfaces the services type their payloads with
- `api-endpoint:GET /contract-note-templates` (from US-02) — template listing
- `api-endpoint:sections-crud` (from US-03) — section composition
- `api-endpoint:section-versions` (from US-03) — version history
- `api-endpoint:section-publish` (from US-04) — publishing
- `api-endpoint:section-variants-crud` (from US-04) — variants
- `api-endpoint:variant-rule` (from US-04) — variant rules
- `api-endpoint:shared-sections-crud` (from US-03) — shared sections
- `api-endpoint:template-rule` (from US-05) — template selection rule

## Requirements

### Requirement 1: Module, routing & access control  _(parent: Requirement 15)_

**User Story:** As a Business_User, I want the contract-note admin module wired into the
portal with auth-guarded routes, so that access is restricted to authorised staff.

#### Acceptance Criteria

1. THE `ContractNoteModule` SHALL define routes for the template list, template edit,
   shared sections and rules configuration areas. _(parent 15.1)_
2. THE module SHALL apply a route guard that restricts access to authenticated users
   with the required Cognito group membership. _(parent 15.1)_
3. WHEN an unauthenticated user attempts access, THE guard SHALL redirect to the login
   flow; WHEN an authenticated user lacks the group, it SHALL show an access-denied
   message. _(parent 15.2, 15.3)_

### Requirement 2: API services  _(parent: Requirement 15)_

**User Story:** As a Business_User, I want the screens to be backed by API services, so
that they have real data to show and mutate.

#### Acceptance Criteria

1. THE `TemplateService` SHALL provide list, create, get, update, delete and reorder
   operations over the template endpoints. _(parent 15.1)_
2. THE `SectionService` SHALL provide section CRUD, schema get/save, version
   list/get/revert, shared-section CRUD + references, publish, and variant operations.
   _(parent 15.1)_
3. THE `RulesService` SHALL provide get/save of the specification for a template (and be
   reusable for variant rules). _(parent 15.1)_
4. THE services SHALL type their requests and responses with the shared interfaces and
   target the API Gateway endpoints. _(parent 15.1)_
