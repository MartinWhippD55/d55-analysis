---
issue_type: Story
key: US-05
summary: Template selection rules API
parent_epic: contract-note-template-management
identity_label: s2s-contract-note-template-management-US-05
labels:
- s2s-contract-note-template-management
- s2s-contract-note-template-management-US-05
- backend
- api
estimate_days: 0.5
covers_requirements:
- '10'
wave: 2
depends_on:
- US-01
blocks:
- US-08
- US-10
---

As a Business_User, I want to get and save a template's selection rule, so that the pipeline can pick the right template automatically.

## Description

Delivers the Rules API: two handlers that read and write a template's selection Specification (a JSON rule tree stored as the `TEMPLATE#{id}` / `RULE` record on the shared table). `save-rule` validates the tree with the shared `spec-validation` utility from US-01 before persisting, rejecting malformed trees with node-path errors. This is the persistence half of rule configuration — a small wave-2 vertical slice that depends only on the US-01 foundation. Render-time evaluation of the saved rule lives in US-06, and the tree editor UI (RulesConfigComponent) lives in US-09.

## Delivers

- `api-endpoint:template-rule` — GET and PUT `/contract-note-templates/{id}/rule` for a template's selection specification.
- `lambda:rules-handlers` — the Lambda handlers implementing those routes: `get-rule` and `save-rule`.

## Acceptance criteria

- **Given** a template with a saved rule, **when** `GET /contract-note-templates/{id}/rule` is called, **then** the handler returns the specification JSON tree from the `TEMPLATE#{id}` / `RULE` record.
- **Given** a request for a template that does not exist, **when** `get-rule` runs, **then** the handler returns 404 (not found).
- **Given** a valid specification tree, **when** `PUT /contract-note-templates/{id}/rule` is called, **then** the handler validates it with the shared `spec-validation` utility and persists it as a JSON tree (`leftOperand`/`rightOperand` for AND/OR, a single `operand` for NOT, and comparison values for leaf nodes) with `updatedAt` and `updatedBy`.
- **Given** an incomplete specification tree (missing operands or comparison values), **when** `save-rule` runs, **then** the handler returns 400 with the incomplete node paths and does not write the record.
- **Given** any valid specification tree, **when** it is saved then fetched, **then** the round-tripped tree is equivalent to the original (Property 20).

## Dependencies

- US-01 — Foundation: infrastructure & shared types

## Traceability

Covers parent requirements: 10 · `s2s-contract-note-template-management-US-05`
