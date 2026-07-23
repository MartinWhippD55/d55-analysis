# Requirements Document

**Story US-05 — Template selection rules API**

> Mini-spec derived from parent spec **contract-note-template-management**.
> Delivers user story **US-05**. See `manifest.yaml` for the component
> exports/dependencies and `../../graph.yaml` for the full delivery graph.

## Introduction

This story delivers the Rules API: the two handlers that get and save a template's
selection Specification. The saved rule is what the render pipeline evaluates against
contract data to pick the right template automatically. It is a small, focused
vertical slice: read the rule, validate and persist the rule.

It is a wave-2 story depending only on the US-01 foundation (types, table,
spec-validation, route surface). Its consumers are the render pipeline (US-06) which
evaluates the saved specification, and the frontend RulesConfigComponent (US-09).

## Glossary

- **Specification**: A JSON-serialised rule tree of logical operators (AND, OR, NOT)
  and leaf comparison operators (EQUALS, LESS_THAN, MORE_THAN, IN).
- **Rules_Engine**: The specification-pattern system for automated template selection.
- **Rule Record**: The `TEMPLATE#{id}` / `RULE` DynamoDB record holding a template's
  specification.

## Delivered components

This story is responsible for creating and owning:

- `api-endpoint:template-rule` — get and save a template's selection specification
- `lambda:rules-handlers` — the Lambda handlers implementing the above

## Dependencies

This story depends on components delivered by other stories (must be available first):

- `shared-lib:types` (from US-01) — `SpecificationNode` union
- `shared-lib:spec-validation` (from US-01) — validates the specification tree on save
- `data-table:ContractNoteTemplates` (from US-01) — the Rule record store
- `cdk-construct:ApiGatewayRoutes` (from US-01) — the route surface these handlers attach to

## Requirements

### Requirement 1: Template selection rule get/save  _(parent: Requirement 10)_

**User Story:** As a Business_User, I want to get and save a template's selection rule,
so that the pipeline can pick the right template automatically.

#### Acceptance Criteria

1. WHEN a template's rule is requested, THE handler SHALL return the specification JSON
   tree for that template (`TEMPLATE#{id}` / `RULE`). _(parent 10.1)_
2. WHEN a rule is saved, THE handler SHALL validate the specification tree with the
   shared `spec-validation` utility before persisting. _(parent 10.4, 10.5)_
3. IF the specification is incomplete (missing operands or comparison values), THEN THE
   handler SHALL return a 400 with node-path errors and SHALL NOT persist. _(parent 10.6)_
4. WHEN a valid specification is saved, THE handler SHALL persist it as a JSON tree with
   `leftOperand`/`rightOperand` for AND/OR, a single `operand` for NOT, and comparison
   values for leaf nodes. _(parent 10.4)_
