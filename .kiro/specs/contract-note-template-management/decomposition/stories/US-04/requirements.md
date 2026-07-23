# Requirements Document

**Story US-04 — Section version publishing & variants API**

> Mini-spec derived from parent spec **contract-note-template-management**.
> Delivers user story **US-04**. See `manifest.yaml` for the component
> exports/dependencies and `../../graph.yaml` for the full delivery graph.

## Introduction

This story delivers controlled rollout and layout alternatives for sections: the
handlers that publish a chosen section version to all linked templates (updating each
template's pinned version), and the handlers that define ordered, rule-driven section
variants. It turns "every edit goes live immediately" into an explicit publish action
and lets one section slot render different layouts depending on contract data.

It is a wave-3 story. It depends on the US-01 foundation (types, table,
spec-validation) and on the `section-versions` handlers from US-03. Its consumers are
the render pipeline (US-06, which resolves pinned versions and selects variants) and
the frontend publish/variants UI (US-09).

## Glossary

- **Pinned_Version**: The specific section version a template's section reference
  resolves to at render time (rather than always the latest).
- **Section_Publish**: The explicit action of pushing a chosen section version out to
  all templates linked to that section, updating their Pinned_Version.
- **Section_Variant**: One of several alternative layouts of a single section, each
  with its own Schema_JSON and version history, guarded by a Variant_Rule.
- **Variant_Rule**: A Specification attached to a variant, evaluated at render time to
  decide whether that variant is the one to render.

## Delivered components

This story is responsible for creating and owning:

- `api-endpoint:section-publish` — get-linked-templates + publish-section-version
- `api-endpoint:section-variants-crud` — list/add/reorder/update/delete variants
- `api-endpoint:variant-rule` — get/save a variant's specification (reuses validation)
- `lambda:variant-publish-handlers` — the Lambda handlers implementing the above

## Dependencies

This story depends on components delivered by other stories (must be available first):

- `shared-lib:types` (from US-01) — `SectionVariant`, `SectionReference`, `SpecificationNode`
- `shared-lib:spec-validation` (from US-01) — validates variant rule trees
- `data-table:ContractNoteTemplates` (from US-01) — variant, version and reference records
- `api-endpoint:section-versions` (from US-03) — the version records publishing acts on

## Requirements

### Requirement 1: Section version publishing to linked templates  _(parent: Requirement 18)_

**User Story:** As a Business_User, I want to publish a specific section version to the
templates that use that section, so that I control exactly when a design change goes
live.

#### Acceptance Criteria

1. THE handler SHALL record, for each template's use of a section, the Pinned_Version
   it resolves to at render time. _(parent 18.1)_
2. WHEN a new section version is created, THE handler SHALL NOT change any linked
   template's Pinned_Version until an explicit publish action. _(parent 18.2)_
3. WHEN linked templates are requested, THE handler SHALL return each linked template
   with its current Pinned_Version and whether an update is available (pinned older
   than latest). _(parent 18.3, 18.5)_
4. WHEN a publish for a chosen version (defaulting to latest) is confirmed, THE handler
   SHALL update the Pinned_Version of every linked template and record a change log
   entry against each affected template. _(parent 18.4)_

### Requirement 2: Section variants  _(parent: Requirement 19)_

**User Story:** As a Business_User, I want a section to contain multiple layout variants,
so that a single slot can render different content without duplicating whole templates.

#### Acceptance Criteria

1. THE handler SHALL allow defining one or more variants within a section, each with
   its own Schema_JSON and its own version history (keyed by `{sectionId}#{variantId}`).
   _(parent 19.1)_
2. THE handler SHALL allow designating exactly one variant as the default, used when no
   Variant_Rule matches. _(parent 19.3)_
3. WHEN variants are ordered, THE handler SHALL persist the evaluation order (first
   match wins at render time). _(parent 19.4)_
4. WHERE a section has no variants, THE handler SHALL treat it as a single implicit
   variant, preserving existing behaviour. _(parent 19.8)_

### Requirement 3: Variant rules  _(parent: Requirement 19)_

**User Story:** As a Business_User, I want to attach a rule to each variant reusing the
existing rule engine, so that variant selection is consistent with template selection.

#### Acceptance Criteria

1. THE handler SHALL allow getting and saving a Variant_Rule (a Specification) for a
   variant. _(parent 19.2)_
2. WHEN a Variant_Rule is saved, THE handler SHALL validate the specification tree with
   the shared `spec-validation` utility, rejecting malformed trees. _(parent 19.7)_
