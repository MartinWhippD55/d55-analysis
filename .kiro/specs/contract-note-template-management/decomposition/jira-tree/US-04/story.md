---
issue_type: Story
key: US-04
summary: Section version publishing & variants API
parent_epic: contract-note-template-management
identity_label: s2s-contract-note-template-management-US-04
labels:
- s2s-contract-note-template-management
- s2s-contract-note-template-management-US-04
- backend
- api
estimate_days: 1.0
covers_requirements:
- '18'
- '19'
wave: 3
depends_on:
- US-01
- US-03
blocks:
- US-08
- US-10
---

As a Business_User, I want to publish a section version to all linked templates and define rule-driven section variants, so that I control rollout and can render alternatives from one section slot.

## Description

This wave-3 backend/API story adds controlled rollout and layout alternatives on top of the section and version handlers from US-03. It replaces "every section edit goes live immediately" with an explicit publish action: each template's section reference resolves to a *pinned version*, and publishing pushes a chosen version out to all linked templates. It also lets a single section slot hold several ordered, rule-guarded *variants* (each independently versioned) with a default fallback, reusing the shared specification validator from US-01.

It exposes no rendering behaviour itself. Its consumers are the render pipeline (US-06), which resolves the `pinnedVersionId` this story maintains and evaluates the variant order/rules it persists (first-match-wins, default fallback), and the frontend (US-09/US-10), which drives the publish and variants UI. It covers parent requirements 18 (section version publishing) and 19 (section variants and variant rules).

## Delivers

- `api-endpoint:section-publish` — `get-linked-templates` (list linked templates with their pinned version and an update-available flag) and `publish-section-version` (push a chosen version to all linked templates and log a change per template).
- `api-endpoint:section-variants-crud` — `list/add/reorder/update/delete-section-variant`; ordered variants with at most one default; a section with no variants behaves as a single implicit variant.
- `api-endpoint:variant-rule` — `get-variant-rule` and `save-variant-rule`; save validates the specification tree via `shared-lib:spec-validation`.
- `lambda:variant-publish-handlers` — the Lambda handlers implementing the above, writing variant records under `SECTION#{sectionId}`, updating `pinnedVersionId` on `SHARED_SECTION#{id}` / `REF#{templateId}` records, and recording change-log entries per affected template.

## Acceptance criteria

- **Given** a section referenced by one or more templates, **when** a new section version is created (in US-03), **then** every linked template's `pinnedVersionId` is left unchanged until an explicit publish — publish is the only mutation of `pinnedVersionId` (Property 31, parent 18.2).
- **Given** a section with linked templates, **when** `get-linked-templates` (`GET /contract-note-sections/{id}/linked-templates`) is called, **then** each linked template is returned as a `SectionReference` with `templateId`, `templateName`, `pinnedVersionId` and an `updateAvailable` flag that is true if and only if its pinned version is older than the section's latest version (Property 33, parent 18.3 and 18.5).
- **Given** a chosen version (defaulting to the latest), **when** `publish-section-version` (`POST /contract-note-sections/{id}/versions/{versionId}/publish`) is confirmed, **then** the `pinnedVersionId` of every template linked to that section is set to the chosen version and a change-log entry is recorded against each affected template (Property 32, parent 18.4).
- **Given** a section, **when** variants are defined, **then** the section may hold one or more variants, each with its own `schemaS3Key` and its own version history keyed by `{sectionId}#{variantId}`, with a persisted evaluation order (`variantOrder`, first match wins) and at most one variant marked `isDefault` (parent 19.1, 19.3, 19.4).
- **Given** a section with no variant records, **when** it is resolved, **then** it is treated as a single implicit variant using the section's own `schemaS3Key`, preserving existing behaviour (Property 36, parent 19.8).
- **Given** a `save-variant-rule` request, **when** the specification tree is submitted, **then** it is validated with the shared `spec-validation` utility and malformed trees are rejected with node-path errors and HTTP 400 (parent 19.7); requesting more than one default variant is likewise rejected with HTTP 400.

## Dependencies

- US-01 — Foundation: infrastructure & shared types
- US-03 — Section, shared-section, version history & change log API

## Traceability

Covers parent requirements: 18, 19 · `s2s-contract-note-template-management-US-04`
