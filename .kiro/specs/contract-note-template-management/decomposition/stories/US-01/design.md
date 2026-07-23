# Design Document

**Story US-01 — Foundation: infrastructure & shared types**

> Mini-spec derived from parent spec **contract-note-template-management**, story **US-01**.
> This design is an excerpt of the parent design scoped to this story's components.

## Overview

US-01 provisions the shared storage, route surface and type contracts for the whole
feature. It is deliberately thin on behaviour and heavy on contracts: a single
DynamoDB table with a priority GSI, two S3 buckets, the API Gateway route surface,
the shared TypeScript types (including the specification tree) and the
specification-tree validator that the rules and variant-rule stories reuse.

## Architecture

This story owns the foundational infrastructure layer. It creates the persistence
and routing surfaces and the shared code contracts, but attaches no behaviour of its
own — the API stories (US-02/03/04/05), the render pipeline (US-06) and the frontend
(US-08) attach to what this story provisions.

```mermaid
graph TD
    subgraph Foundation (US-01)
        DDB[(DynamoDB: ContractNoteTemplates + PriorityIndex GSI)]
        S3S[S3: schema-json]
        S3E[S3: error-output]
        APIR[API Gateway route surface]
        TYPES[shared-lib: types]
        VAL[shared-lib: spec-validation]
    end
    APIR -. handlers attached by .-> US02[US-02..05 APIs]
    DDB -. read/written by .-> US02
    VAL -. reused by .-> US0405[US-04 / US-05]
```

## Components and Interfaces

### cdk-construct:ApiGatewayRoutes

The API Gateway route surface (paths + integration placeholders) for the template,
section and rules endpoints, so US-02/03/04/05 attach their handlers without each
re-declaring the gateway.

### shared-lib:types

Shared TypeScript interfaces used across lambdas, render pipeline and frontend:
`Template`, `Section` (with `pinnedVersionId`), `SectionVariant`, `SharedSection`,
`SectionReference`, and the specification tree union:

```typescript
type SpecificationNode = AndOrNode | NotNode | ComparisonNode | InNode;
// AND/OR: { type, leftOperand, rightOperand }
// NOT:    { type, operand }
// EQUALS/LESS_THAN/MORE_THAN: { type, field, value }
// IN:     { type, field, values }
```

### shared-lib:spec-validation

Pure function that checks a `SpecificationNode` tree is well-formed (AND/OR have both
operands, NOT has its operand, comparisons have field + value/values) and returns
errors with node paths. Reused by the rules API (US-05) and variant-rule API (US-04).

### Interfaces consumed (dependencies)

None — US-01 is a wave-1 foundation story.

### Touch points with other stories

- **US-02 Template API** consumes `data-table`, `gsi:PriorityIndex`, `shared-lib:types`,
  `cdk-construct:ApiGatewayRoutes`.
- **US-03 Section API** consumes `data-table`, `s3-bucket:schema-json`, `shared-lib:types`,
  `cdk-construct:ApiGatewayRoutes`.
- **US-04 Publishing & variants** and **US-05 Rules API** consume `shared-lib:spec-validation`
  in addition to `data-table` and `shared-lib:types`.
- **US-06 Render pipeline** consumes `data-table`, `gsi:PriorityIndex`,
  `s3-bucket:schema-json`, `s3-bucket:error-output`, `shared-lib:types`.
- **US-08 Services** consume `shared-lib:types`.

This story must not depend on any of them; it defines the contracts they rely on.

## Data Models

### data-table:ContractNoteTemplates + gsi:PriorityIndex

Single-table design (PK/SK). This story creates the table and the GSI; the record
shapes it must accommodate (owned by later stories) are:

| Record | PK | SK |
|--------|----|----|
| Template | `TEMPLATE#{templateId}` | `METADATA` |
| Section | `TEMPLATE#{templateId}` | `SECTION#{sortOrder}#{sectionId}` |
| Section Variant | `SECTION#{sectionId}` | `VARIANT#{variantOrder}#{variantId}` |
| Shared Section | `SHARED_SECTION#{sectionId}` | `METADATA` |
| Shared Section Reference | `SHARED_SECTION#{sectionId}` | `REF#{templateId}` |
| Section Version | `SECTION_VERSION#{sectionId}#{variantId}` | `VERSION#{timestamp}` |
| Rule | `TEMPLATE#{templateId}` | `RULE` |
| Template Change Log | `TEMPLATE#{templateId}` | `CHANGELOG#{timestamp}` |

**GSI PriorityIndex:** GSI PK = `ALL_TEMPLATES` (constant), GSI SK = `priority`
(Number) — query all templates ordered by priority in a single call.

### S3 layout

- `s3-bucket:schema-json`: pdf-me schema JSON per section/variant/version, at
  `s3://{schema-bucket}/{sectionId}/schema.json` (and per-version keys).
- `s3-bucket:error-output`: JSON error records written by the render pipeline on failure.

## Correctness Properties

These are carried from the parent spec; this story's types + validator implement them.

### Property 20: Specification tree serialization round-trip

*For any* valid specification tree, serializing to JSON and deserializing SHALL
produce an equivalent tree. **Validates: Requirements 10.2, 10.3, 10.4**

### Property 21: Specification validation rejects malformed trees

*For any* structurally incomplete specification tree (AND/OR missing operands,
comparison nodes missing field or value), validation SHALL fail and identify the
incomplete nodes. **Validates: Requirements 10.5**

## Error Handling

- Invalid schema JSON format → validation error surfaced to the caller (400) by the
  consuming API story; this story provides the type/validation primitives.
- Malformed specification tree → `shared-lib:spec-validation` returns node-path errors.
- Infrastructure provisioning failures are handled by CDK deployment (fail the stack;
  no partial route surface published).

## Testing Strategy

- Property tests for `shared-lib:spec-validation` (Properties 20, 21).
- Type-level checks compile against the shared `types/` module.
- CDK synth/assertion tests confirm the table, GSI, buckets and routes are declared.
