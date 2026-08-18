# Design Document

**Story US-06 — Frontend: Template Edit data sources panel**

> Mini-spec derived from parent spec **contract-note-data-source-extensibility**, story **US-06**.
> This design is an excerpt of the parent design scoped to this story's components.

## Overview

This story implements the Admin Portal front end for template data source attachment
(parent Requirement 2). It adds a Data Sources panel to the existing `template-edit`
component, a picker dialog for choosing an available data source, and a
`DataSourceService` that fronts the data source API Gateway endpoints. All rendering-time
behaviour lives in the backend (US-04); this story is the wiring that lets business users
view, attach, and detach data sources from a template.

## Architecture

The panel and dialog are Angular components in the Admin Portal (`sqp-4962` baseline).
They call the `DataSourceService`, which is the single client for the data source API
endpoints owned by US-03. Attachment changes affect rendering only once the template is
PUBLISHED, but the panel is available in both DRAFT and PUBLISHED states.

```mermaid
graph TB
    TE[template-edit component] --> DSP[Data Sources panel]
    DSP --> PICK[data-source-picker-dialog]
    DSP --> DSS[DataSourceService]
    PICK --> DSS
    DSS -->|GET /contract-note-data-sources| API[(Data Source API - US-03)]
    DSS -->|GET/POST/DELETE .../templates/{id}/data-sources| API
```

## Components and Interfaces

### `service:DataSourceService`

The single frontend client for data source operations, wired to the API Gateway
endpoints owned by US-03:

- `listAvailable()` → `GET /contract-note-data-sources` → `AvailableDataSource[]`
- `getColumns(database, table)` → `GET /contract-note-data-sources/{database}/{table}/columns` → `DataSourceColumn[]`
- `listAttached(templateId)` → `GET /contract-note-templates/{templateId}/data-sources` → `TemplateDataSource[]`
- `attach(templateId, database, table)` → `POST /contract-note-templates/{templateId}/data-sources`
- `detach(templateId, database, table)` → `DELETE /contract-note-templates/{templateId}/data-sources/{database}/{table}` (surfaces the 409 affected section+variant list on in-use conflict)
- `listSharedSectionDeps(sharedSectionId)` → for downstream US-08 consumption

### `frontend-component:template-edit-data-sources-panel`

New panel added to the existing `template-edit` component:

- Header: "Data Sources" with a [+ Attach Data Source] button.
- List of attached data sources with name and column count.
- Detach button per data source; on a 409 in-use response, shows a warning listing the affected sections and variants and requires confirmation.
- Attach action opens the picker dialog.
- Available regardless of DRAFT/PUBLISHED status.

### `frontend-component:data-source-picker-dialog`

- Shows available data sources **excluding** those already attached, with table name, database name, and column count.
- Selecting one calls `DataSourceService.attach` and refreshes the panel.

### Interfaces consumed (dependencies)

- `shared-lib:data-source-types` (US-01) — `AvailableDataSource`, `DataSourceColumn`, `TemplateDataSource`, `SectionDataSourceDependency` interfaces used by the service and components.
- Data source API endpoints (US-03) — `GET /contract-note-data-sources`, `GET/POST/DELETE` on `/contract-note-templates/{templateId}/data-sources`.

### Touch points with other stories

- **Exposes** `DataSourceService` for US-07 (section-variant field browser) and US-08 (shared section dependency checks).
- **Assumes** US-03 provides the API endpoints (including the DELETE 409 in-use response used to drive the detach warning) and US-01 provides the shared types.

## Data Models

This story defines no persistent data. It reads and writes via the API using the
types owned by US-01:

- `AvailableDataSource` `{ database, tableName, columns: DataSourceColumn[], location? }`
- `DataSourceColumn` `{ name, type }`
- `TemplateDataSource` `{ database, tableName, displayName, attachedAt, attachedBy }`

The picker computes its list as the available data sources minus those already attached to
the current template.

## Correctness Properties

### Property 12: Picker excludes already-attached data sources

*For any* template with a set of attached data sources A and a set of available data
sources V, the data source picker dialog SHALL present exactly `V \ A` (the available
sources not already attached to the template). **Validates: Requirements 2.2**

## Error Handling

| Scenario | Handling |
|----------|----------|
| `listAvailable`/`listAttached` request fails | Surface an error state in the panel; do not render a stale/partial list |
| Detach returns 409 (variant fields in use) | Show a confirmation warning listing the affected sections and variants; only proceed if the user confirms |
| Attach returns 400 (missing `bryt_number`) or 404 (table not found) | Surface the API validation message in the picker; keep the dialog open |
| API unreachable (5xx) | Show a ret/retry-able error; leave the current attached list intact |

## Testing Strategy

### Unit Testing
- `DataSourceService` — correct endpoint URLs, request bodies, and response mapping for each method.
- Panel — renders attached list with column counts; wires [+ Attach] to the picker; drives the detach confirmation flow off a 409 response.
- Picker dialog — computes available-minus-attached correctly; disables/hides already-attached sources.

### Property-Based Testing
- **Property 12: Picker excludes already-attached data sources** — generate random available and attached sets and assert the picker shows exactly the set difference.

### Integration Testing
- Open template edit → panel lists attached sources → [+ Attach] → pick a source → it appears attached and disappears from the picker.
- Detach a source referenced by a variant → warning with affected sections+variants → confirm → source removed.
