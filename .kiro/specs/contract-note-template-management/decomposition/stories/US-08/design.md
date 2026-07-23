# Design Document

**Story US-08 — Angular module, routing & services**

> Mini-spec derived from parent spec **contract-note-template-management**, story **US-08**.
> This design is an excerpt of the parent design scoped to this story's components.

## Overview

US-08 sets up the Angular feature module for the contract-note admin area at
`portal/src/app/components/contract-notes/`: routes for the list/edit/shared-section/
rules areas, a Cognito-group route guard, and the three HTTP services that wrap the
backend. It carries no screen markup of its own — it is the routing and data layer the
components in US-09 build on.

## Architecture

This story owns the frontend module boundary and service layer. Services call the API
Gateway endpoints delivered by US-02/03/04/05 and type payloads with the US-01 shared
interfaces; the route guard reuses the portal's existing auth mechanism.

```mermaid
graph TD
    subgraph ContractNoteModule (US-08)
        RT[Routes + Cognito guard]
        TS[TemplateService]
        SS[SectionService]
        RS[RulesService]
    end
    TS --> TAPI[Template API — US-02]
    SS --> SAPI[Section API — US-03]
    SS --> PVAPI[Publish/Variants API — US-04]
    RS --> RAPI[Rules API — US-05]
```

## Components and Interfaces

### frontend-component:ContractNoteModule

An Angular module declaring routes: template list, template edit, shared sections, rules
config. A route guard checks Cognito group membership, redirecting unauthenticated users
to login and showing an access-denied view for authenticated users without the group.

### service:TemplateService

`list`, `create`, `get`, `update`, `delete`, `reorder` templates over the
`/contract-note-templates` endpoints (US-02).

### service:SectionService

Section CRUD + reorder, schema get/save, version list/get/revert, shared-section CRUD +
references (US-03), and publish + variant + variant-rule operations (US-04).

### service:RulesService

`get`/`save` the specification for a template (US-05); reused by the variant-rule flow.

### Interfaces consumed (dependencies)

- `shared-lib:types` (US-01) — request/response typing.
- Template API (US-02), Section API + versions + shared sections (US-03), publish +
  variants + variant-rule (US-04), template-rule (US-05) — the endpoints the services call.

### Touch points with other stories

- **US-09 components/screens** inject these services and render the module's routes.
- **US-10** adds the portal sidebar navigation entry that links into this module's routes.

## Data Models

This story defines no persisted data. Its services carry the shared DTOs — `Template`,
`Section`, `SharedSection`, `SectionVariant`, `SectionReference`, `SpecificationNode` —
between the screens and the API.

## Correctness Properties

This story is Angular wiring (module, guard, HTTP services); the parent's business
invariants are validated in the API stories (US-02–US-05) and the render pipeline
(US-06). The one universal invariant this story owns is route access control.

### Property 39: Route guard enforces authenticated group membership

*For any* navigation into a ContractNoteModule route, access SHALL be granted if and
only if the user is authenticated and holds the required Cognito group; unauthenticated
users SHALL be redirected to login and authenticated users without the group SHALL be
denied. **Validates: Requirements 15.1, 15.2, 15.3**

## Error Handling

| Scenario | Handling |
|----------|----------|
| API request failure (network) | Surface an error to the caller for a retry/toast; preserve caller state |
| Unauthorized (401) | Route guard redirects to the login flow |
| Forbidden (403) / missing group | Route guard shows an access-denied view |
| Not found (404) | Service surfaces a not-found the component can handle |
| Server error (500) | Service surfaces a generic error for the component to display |

## Testing Strategy

- Unit tests for the route guard: authenticated + in-group allowed; unauthenticated
  redirected; authenticated + not-in-group denied.
- Unit tests for each service verifying correct HTTP method, URL and payload mapping
  (with HttpTestingController).
