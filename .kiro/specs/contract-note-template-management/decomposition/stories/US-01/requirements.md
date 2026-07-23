# Requirements Document

**Story US-01 — Foundation: infrastructure & shared types**

> Mini-spec derived from parent spec **contract-note-template-management**.
> Delivers user story **US-01**. See `manifest.yaml` for the component
> exports/dependencies and `../../graph.yaml` for the full delivery graph.

## Introduction

This story establishes the platform foundation that every other story in the
contract-note template management feature builds on: the single DynamoDB table
and its priority GSI, the S3 buckets for schema JSON and error output, the API
Gateway route surface, the shared TypeScript types (including the specification
tree), and the specification-tree validation utility.

It is a wave-1 story with no upstream dependencies. It exposes no user-facing
behaviour on its own; its value is that the API stories (US-02, US-03, US-04,
US-05), the render pipeline (US-06) and the frontend (US-08) can all be built
against a stable, shared contract.

## Glossary

- **ContractNoteTemplates**: The single DynamoDB table holding all template, section,
  variant, version, rule and change-log records via a PK/SK pattern.
- **PriorityIndex**: The GSI (constant `ALL_TEMPLATES` partition, numeric `priority`
  sort key) that returns templates in priority order in one query.
- **SpecificationNode**: The rule-tree type (AND/OR/NOT + EQUALS/LESS_THAN/MORE_THAN/IN)
  shared by template selection and section-variant rules.
- **spec-validation**: The shared utility that checks a SpecificationNode tree is
  well-formed and reports incomplete nodes by path.

## Delivered components

- `data-table:ContractNoteTemplates` — single-table DynamoDB store (PK/SK) for
  templates, sections, shared sections, variants, versions, rules and change log
- `gsi:PriorityIndex` — GSI (`ALL_TEMPLATES` / `priority`) for priority-ordered
  template queries
- `s3-bucket:schema-json` — stores pdf-me section/variant schema JSON
- `s3-bucket:error-output` — stores render pipeline error records
- `cdk-construct:ApiGatewayRoutes` — the API Gateway route surface the API
  stories attach handlers to
- `shared-lib:types` — shared TypeScript interfaces (`Template`, `Section`,
  `SectionVariant`, `SharedSection`, `SectionReference`, `SpecificationNode`, …)
  and DynamoDB record types
- `shared-lib:spec-validation` — the specification-tree well-formedness validator

## Dependencies

None — this is a wave-1 foundation story.

## Requirements

### Requirement 1: Priority-ordered template storage  _(parent: Requirements 1, 5)_

**User Story:** As a developer, I want the template store to support priority-ordered
retrieval, so that listing and rule evaluation can read templates in priority order.

#### Acceptance Criteria

1. THE data model SHALL store templates in the `ContractNoteTemplates` table using a
   `TEMPLATE#{templateId}` / `METADATA` key pattern. _(parent 1.1)_
2. THE data model SHALL provide a `PriorityIndex` GSI keyed on a constant
   `ALL_TEMPLATES` partition and a numeric `priority` sort key, enabling all
   templates to be queried in priority order in a single query. _(parent 1.1, 5.2)_
3. THE priority ordering SHALL persist across sessions. _(parent 5.2)_

### Requirement 2: Shared types  _(parent: Requirements 10.2, 10.3, 10.4)_

**User Story:** As a developer, I want shared TypeScript types, so that the API
lambdas, render pipeline and frontend share one definition of every record and the
specification tree.

#### Acceptance Criteria

1. THE `shared-lib:types` module SHALL define the `SpecificationNode` union
   (`AndOrNode`, `NotNode`, `ComparisonNode`, `InNode`) covering the logical
   operators AND/OR/NOT and comparison operators EQUALS/LESS_THAN/MORE_THAN/IN.
   _(parent 10.2, 10.3)_
2. THE module SHALL define the `Template`, `Section`, `SectionVariant`,
   `SharedSection` and `SectionReference` interfaces and the DynamoDB record types.
3. THE serialised specification SHALL use `leftOperand`/`rightOperand` for AND/OR,
   a single `operand` for NOT, and comparison values for leaf nodes. _(parent 10.4)_

### Requirement 3: Specification validation  _(parent: Requirements 10.5, 10.6)_

**User Story:** As a developer, I want a shared validator for specification trees, so
that the rules API and the variant-rule API can reject malformed trees consistently.

#### Acceptance Criteria

1. WHEN a specification tree is validated, THE `shared-lib:spec-validation` utility
   SHALL confirm AND/OR nodes have both operands, NOT nodes have their operand, and
   comparison leaves have a field and value/values. _(parent 10.5)_
2. IF the tree is incomplete, THEN the validator SHALL return errors identifying the
   incomplete nodes by path. _(parent 10.6)_

### Requirement 4: Pipeline storage buckets and route surface  _(parent: Requirement 14.1)_

**User Story:** As a developer, I want the buckets and API route surface provisioned,
so that the render pipeline and API handlers have somewhere to attach.

#### Acceptance Criteria

1. THE infrastructure SHALL provision an S3 bucket for section/variant schema JSON.
2. THE infrastructure SHALL provision an S3 bucket for render error records.
3. THE infrastructure SHALL define the API Gateway route surface for the template,
   section and rules endpoints so downstream stories can attach handlers. _(parent 14.1)_
