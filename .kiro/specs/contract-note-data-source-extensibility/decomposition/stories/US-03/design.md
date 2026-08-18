# Design Document

**Story US-03 — Data Source API handlers + routing**

> Mini-spec derived from parent spec **contract-note-data-source-extensibility**, story **US-03**.
> This design is an excerpt of the parent design scoped to this story's components.
>
> NOTE: the sections `## Overview`, `## Architecture`, `## Components and Interfaces`
> and `## Data Models` are REQUIRED by Kiro's spec-format checks; the sections
> `## Correctness Properties`, `## Error Handling` and `## Testing Strategy` are
> recommended. Keep all of them so the folder is a valid, pullable Kiro spec.

## Overview

This story implements the backend API layer for data source management. It provides six API Gateway endpoints (one Lambda per operation under `api/src/data-sources/`) and the `DataSourceApi` CDK construct that creates the handlers, grants table/Glue/Athena/AssumeRole access, and wires the `LambdaIntegration`s. Routes are declared centrally in `contract-note-foundation.ts::createRoutes`, following the Estimate 1 convention.

The list/columns handlers read from the Glue Data Catalog (via the shared client from US-02, assuming the Project Role). The attach/detach/list handlers read and write DynamoDB `DATASOURCE` records on the template partition. The shared-section-deps handler reads `DATASOURCE_DEP` records. This story does not touch the render pipeline or the frontend — it exposes the surface those later stories consume.

## Architecture

The story adds a `DataSourceApi` construct alongside the existing `TemplateApi`, `SectionApi`, and `RulesApi` constructs. New route resources are added to `TemplateRouteResources`, `SharedSectionRouteResources`, and a new `DataSourceRouteResources` in `ContractNoteApiRoutes`.

```mermaid
graph TB
    subgraph API Gateway - routes declared in contract-note-foundation.ts
        R1[GET /contract-note-data-sources]
        R2[GET /contract-note-data-sources/{database}/{table}/columns]
        R3[GET /contract-note-templates/{templateId}/data-sources]
        R4[POST /contract-note-templates/{templateId}/data-sources]
        R5[DELETE /contract-note-templates/{templateId}/data-sources/{database}/{table}]
        R6[GET /contract-note-shared-sections/{sharedSectionId}/data-source-dependencies]
    end

    subgraph DataSourceApi CDK construct
        H1[list-available.ts]
        H2[get-columns.ts]
        H3[list-attached.ts]
        H4[attach-data-source.ts]
        H5[detach-data-source.ts]
        H6[list-shared-section-deps.ts]
    end

    R1 --> H1
    R2 --> H2
    R3 --> H3
    R4 --> H4
    R5 --> H5
    R6 --> H6

    H1 -->|AssumeRole: ProjectRole| GC[(Glue Data Catalog)]
    H2 -->|AssumeRole: ProjectRole| GC
    H3 --> DDB[(DynamoDB - single table)]
    H4 --> DDB
    H5 --> DDB
    H6 --> DDB
    H4 -->|validate bryt_number| GC
```

## Components and Interfaces

### API endpoints (`api/src/data-sources/`, one Lambda per operation)

| Method | Route (declared in `contract-note-foundation.ts`) | Handler file | Description |
|--------|----------------------------------------------------|--------------|-------------|
| GET | `/contract-note-data-sources` | `data-sources/list-available.ts` | Lists all Glue tables accessible via Project Role with `bryt_number` column |
| GET | `/contract-note-data-sources/{database}/{table}/columns` | `data-sources/get-columns.ts` | Returns column names and types for a specific table |
| GET | `/contract-note-templates/{templateId}/data-sources` | `data-sources/list-attached.ts` | Returns data sources attached to a template |
| POST | `/contract-note-templates/{templateId}/data-sources` | `data-sources/attach-data-source.ts` | Attaches a data source to a template |
| DELETE | `/contract-note-templates/{templateId}/data-sources/{database}/{table}` | `data-sources/detach-data-source.ts` | Detaches a data source (with variant-field-in-use check) |
| GET | `/contract-note-shared-sections/{sharedSectionId}/data-source-dependencies` | `data-sources/list-shared-section-deps.ts` | Returns a shared section's tracked data source dependencies |

**Handler behaviour:**
- `list-available` — calls the Glue client (assumes Project Role); returns `[{ database, tableName, columnCount }]` for tables containing `bryt_number`.
- `get-columns` — returns the full column list (name, type) for a specific `{database}/{table}`.
- `list-attached` — queries `DATASOURCE` records for the template and projects them to `TemplateDataSource[]`.
- `attach-data-source` — validates the table exists and has a `bryt_number` column (via Glue client), then writes a `DATASOURCE` record under the template partition.
- `detach-data-source` — scans all sections' variants in the template for fields referencing this data source; if referenced, returns 409 with the affected section+variant list, otherwise removes the record.
- `list-shared-section-deps` — queries `DATASOURCE_DEP` records for the shared section.

### CDK construct: `DataSourceApi`

Mirrors `template-api.ts`: creates one `NodejsFunction` per operation, grants table read/write, Glue and Athena access, and `sts:AssumeRole` for the Project Role, then wires `LambdaIntegration`s to the route resources from `contract-note-foundation.ts`. The list-available and get-columns handlers additionally receive `PROJECT_ROLE_ARN` and Athena config as environment variables. The construct is instantiated in `contract-note-stack.ts`.

### Interfaces consumed (dependencies)

- `shared-lib:data-source-types` (US-01) — `TemplateDataSource`, `AvailableDataSource`, `DataSourceColumn`, `SectionDataSourceDependency` interfaces and the `TemplateDataSource` / `SharedSectionDataSourceDependency` entity types / record shapes.
- `shared-lib:glue-catalog-client` (US-02) — the Glue discovery and column-fetch client used by `list-available`, `get-columns`, and the `attach-data-source` validation.
- `cdk-construct:project-role-trust-policy` (US-01) — the trust policy allowing these Lambda roles to assume the Project Role, plus the `PROJECT_ROLE_ARN` parameter/env var.

### Touch points with other stories

- **Exposes** the six endpoints consumed by the frontend data sources panel (US-06), the section-variant field browser (US-07), and integration wiring (US-08).
- **Assumes** the Glue client returns `AvailableDataSource[]` filtered to `bryt_number` tables (US-02) and that the Project Role trust policy already permits assumption (US-01).
- The `detach-data-source` variant-field scan reuses the field-reference format that US-04's dependency scanner also relies on; this story scans in-line for the in-use check.

## Data Models

This story reads and writes two DynamoDB record types on the existing single table. It does not create new tables.

### Template Data Source Record (written by attach, read by list-attached, deleted by detach)

| Attribute | Type | Description |
|-----------|------|-------------|
| PK | `TEMPLATE#{templateId}` | Existing template partition |
| SK | `DATASOURCE#{database}#{tableName}` | Data source attachment |
| entityType | `"TemplateDataSource"` | |
| database | String | Glue database name |
| tableName | String | Glue table name |
| displayName | String | User-friendly name (defaults to table name) |
| attachedAt | String | ISO 8601 timestamp |
| attachedBy | String | Cognito username |

### Shared Section Dependency Record (read by list-shared-section-deps)

| Attribute | Type | Description |
|-----------|------|-------------|
| PK | `SHARED_SECTION#{sharedSectionId}` | Existing shared section partition |
| SK | `DATASOURCE_DEP#{database}#{tableName}` | Dependency |
| entityType | `"SharedSectionDataSourceDependency"` | |
| database | String | Glue database name |
| tableName | String | Glue table name |

### API projections (TypeScript, from `shared-lib/types.ts`)

```typescript
interface AvailableDataSource {
  database: string;
  tableName: string;
  columns: DataSourceColumn[];
  location?: string;
}

interface DataSourceColumn {
  name: string;
  type: string; // Glue/Athena type: string, int, bigint, double, boolean, etc.
}

interface TemplateDataSource {
  database: string;
  tableName: string;
  displayName: string;
  attachedAt: string;
  attachedBy: string;
}

interface SectionDataSourceDependency {
  database: string;
  tableName: string;
}
```

## Correctness Properties

This story validates the parent's Property 2 and Property 3 (see the optional property-test task US-03-9).

### Property 2: Data source attachment round-trip

*For any* valid data source attachment to a template, listing the template's data sources SHALL include that attachment with correct database, table name, and display name. **Validates: Requirements 2.1, 2.2**

### Property 3: Detachment with variant-field-in-use warning

*For any* attached data source referenced by fields in any variant of any section in the template, detachment SHALL be blocked or warned with the affected section+variant list. **Validates: Requirements 2.4**

## Error Handling

| Scenario | Handling | HTTP Status |
|----------|----------|-------------|
| AssumeRole failure (Project Role) | Log error, return 500 with message | 500 |
| Glue catalog unreachable | Log error, return 503 | 503 |
| Table not found in catalog | Return 404 | 404 |
| Table missing bryt_number column | Return 400 with validation message | 400 |
| Detach blocked by variant field references | Return 409 with affected section+variant list | 409 |

## Testing Strategy

### Unit Testing
- `attach-data-source` — validation path (table exists + has `bryt_number`), record write shape.
- `detach-data-source` — variant field scan, 409 vs remove decision.
- `list-attached` / `list-shared-section-deps` — DynamoDB query → projection.
- `list-available` / `get-columns` — Glue client wiring, `bryt_number` filtering, column mapping.

### Property-Based Testing (optional, US-03-9)
- **Property 2: attachment round-trip** — random valid attachments; attach then list includes the attachment.
- **Property 3: detachment with variant-field-in-use warning** — random schemas referencing an attached data source; detach is blocked with the affected section+variant list.

### Integration Testing
- Attach a data source, list it back, detach when unreferenced, and confirm a 409 when a variant field references it.
