---
issue_type: Story
key: US-01
summary: 'Foundation: infrastructure & shared types'
parent_epic: contract-note-template-management
identity_label: s2s-contract-note-template-management-US-01
labels:
- s2s-contract-note-template-management
- s2s-contract-note-template-management-US-01
- infra
- backend
estimate_days: 2.5
covers_requirements:
- '1'
- '5'
- '10'
- '14'
wave: 1
depends_on: []
blocks:
- US-02
- US-03
- US-04
- US-05
- US-06
- US-08
---

As a developer, I want the base table, buckets, API Gateway routes, shared types and the specification-tree validator, so that every other story has a stable foundation to build on.

## Description

This is the wave-1 foundation story for the contract-note template management feature. It provisions the shared persistence, routing surface and code contracts that every other story builds on: a single DynamoDB table with a priority GSI, two S3 buckets, the API Gateway route surface, the shared TypeScript types (including the specification tree), and the specification-tree validator.

It exposes no user-facing behaviour on its own. Its value is that the API stories (US-02, US-03, US-04, US-05), the render pipeline (US-06) and the frontend (US-08) can all be built against a stable, shared contract. Nothing downstream can start until this story's exports exist.

## Delivers

- `data-table:ContractNoteTemplates` — single-table DynamoDB store (PK/SK) for templates, sections, shared sections, variants, versions, rules and change log.
- `gsi:PriorityIndex` — GSI keyed on a constant `ALL_TEMPLATES` partition and a numeric `priority` sort key, for priority-ordered template queries in a single call.
- `s3-bucket:schema-json` — stores pdf-me section/variant schema JSON at `s3://{schema-bucket}/{sectionId}/schema.json`.
- `s3-bucket:error-output` — stores render pipeline error records.
- `cdk-construct:ApiGatewayRoutes` — the API Gateway route surface (paths + integration placeholders) for the template, section and rules endpoints, that US-02/03/04/05 attach handlers to.
- `shared-lib:types` — shared TypeScript interfaces (`Template`, `Section`, `SectionVariant`, `SharedSection`, `SectionReference`, the `SpecificationNode` union) and the DynamoDB record types.
- `shared-lib:spec-validation` — the specification-tree well-formedness validator, reused by the rules API (US-05) and variant-rule API (US-04).

## Acceptance criteria

- **Given** a template stored in the `ContractNoteTemplates` table, **when** it is written, **then** it uses the `TEMPLATE#{templateId}` / `METADATA` key pattern.
- **Given** templates in the table, **when** the `PriorityIndex` GSI is queried (GSI PK = `ALL_TEMPLATES`, GSI SK = numeric `priority`), **then** all templates are returned in priority order in a single query, and that order persists across sessions.
- **Given** the shared code contract, **when** the `shared-lib:types` module is consumed, **then** it exposes the `SpecificationNode` union (`AndOrNode`, `NotNode`, `ComparisonNode`, `InNode`) covering AND/OR/NOT and EQUALS/LESS_THAN/MORE_THAN/IN, plus the `Template`, `Section`, `SectionVariant`, `SharedSection` and `SectionReference` interfaces and the DynamoDB record types.
- **Given** a valid specification tree, **when** it is serialized to JSON and deserialized, **then** an equivalent tree is produced, using `leftOperand`/`rightOperand` for AND/OR, a single `operand` for NOT, and comparison values for leaf nodes (Property 20).
- **Given** a structurally incomplete specification tree (AND/OR missing an operand, NOT missing its operand, or a comparison leaf missing field or value/values), **when** it is validated by `shared-lib:spec-validation`, **then** validation fails and returns errors identifying the incomplete nodes by path (Property 21).
- **Given** the infrastructure stack, **when** it is deployed, **then** the S3 buckets for schema JSON and error output are provisioned and the API Gateway route surface for the template, section and rules endpoints is defined so downstream stories can attach handlers.

## Dependencies

- None — foundation story.

## Traceability

Covers parent requirements: 1, 5, 10, 14 · `s2s-contract-note-template-management-US-01`
