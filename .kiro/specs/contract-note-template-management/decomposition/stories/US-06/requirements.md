# Requirements Document

**Story US-06 — Render pipeline (Step Functions)**

> Mini-spec derived from parent spec **contract-note-template-management**.
> Delivers user story **US-06**. See `manifest.yaml` for the component
> exports/dependencies and `../../graph.yaml` for the full delivery graph.

## Introduction

This story delivers the render pipeline: an AWS Step Functions state machine, triggered
by an XML file landing in S3, that parses the input, selects the matching template by
rule, resolves each section's pinned version, selects the right section variant, renders
each section with @pdfme/generator, stitches the results with pdf-lib, and writes the
final PDF to S3 — isolating and retrying per-section work and writing no partial output
on failure.

It is a wave-4 story. It depends on the US-01 foundation (table, GSI, buckets, types)
and consumes the rules and variant/pinned-version data persisted by US-04/US-05 through
the shared table. It exposes the state machine that the integration story (US-10) wires
into deployment.

## Glossary

- **Render_State_Machine**: The Step Functions state machine orchestrating the render.
- **Specification evaluator**: The recursive evaluator of a Specification tree against
  contract data (AND/OR/NOT + EQUALS/LESS_THAN/MORE_THAN/IN).
- **Pinned_Version**: The section version a template reference resolves to at render time.
- **Section_Variant**: An alternative section layout guarded by a Variant_Rule; first
  match wins, with a default fallback.
- **Map state**: The Step Functions state that renders sections as independent, retryable
  units of work.

## Delivered components

This story is responsible for creating and owning:

- `state-machine:RenderStateMachine` — the orchestrating Step Functions state machine
- `shared-lib:spec-evaluator` — the specification tree evaluator
- `lambda:parse-input` — XML → JSON parse
- `lambda:select-template` — first-match-wins template selection
- `lambda:render-section` — pinned-version resolution + variant selection + pdf-me render
- `lambda:stitch` — pdf-lib PDF concatenation
- `lambda:write-output` — write final PDF to output bucket
- `lambda:handle-failure` — write an error record, no partial output
- `s3-bucket:input-xml` — the XML input bucket (pipeline entry point)
- `s3-bucket:output-pdf` — the final PDF output bucket

## Dependencies

This story depends on components delivered by other stories (must be available first):

- `shared-lib:types` (from US-01) — `SpecificationNode`, `Section`, `SectionVariant`, records
- `data-table:ContractNoteTemplates` (from US-01) — templates, sections, variants, rules
- `gsi:PriorityIndex` (from US-01) — priority-ordered template evaluation
- `s3-bucket:schema-json` (from US-01) — section/variant/version schema JSON
- `s3-bucket:error-output` (from US-01) — error records on failure

## Requirements

### Requirement 1: Rules engine evaluation & template selection  _(parent: Requirement 11)_

**User Story:** As a Business_User, I want the pipeline to select the correct template
using the configured rules, so that contract notes use the appropriate layout.

#### Acceptance Criteria

1. WHEN contract data arrives, THE pipeline SHALL evaluate template Specifications in
   Template_List priority order and select the first that evaluates true, stopping
   evaluation. _(parent 11.1, 11.2)_
2. THE evaluator SHALL evaluate EQUALS (field equals value), IN (field value in set),
   LESS_THAN and MORE_THAN (numeric comparison), and combine with AND/OR/NOT. _(parent 11.4, 11.5, 11.6)_
3. IF no template Specification matches, THEN THE pipeline SHALL log an error and halt.
   _(parent 11.3)_

### Requirement 2: Section rendering with pinned versions & variants  _(parent: Requirements 12, 18, 19)_

**User Story:** As a Business_User, I want each section rendered independently at the
right pinned version and variant, so that dynamic content and alternatives are handled
correctly.

#### Acceptance Criteria

1. WHEN a section is rendered, THE pipeline SHALL resolve the template reference's
   Pinned_Version rather than the latest. _(parent 18.6)_
2. WHERE a section has variants, THE pipeline SHALL evaluate each Variant_Rule in order
   and select the first match, falling back to the default. _(parent 19.5)_
3. IF a section has variants but none match and no default exists, THEN THE pipeline
   SHALL log an error identifying the section and halt. _(parent 19.6)_
4. THE pipeline SHALL render each section independently via @pdfme/generator with the
   selected variant's schema JSON, the configured fonts and the text/multiVariableText/
   table plugins. _(parent 12.1, 12.2)_
5. IF a section render fails, THEN THE pipeline SHALL log the error with section and
   template context and halt. _(parent 12.3)_

### Requirement 3: PDF stitching  _(parent: Requirement 13)_

**User Story:** As a Business_User, I want rendered sections combined into a single PDF,
so that the final contract note is a complete document.

#### Acceptance Criteria

1. WHEN all sections render successfully, THE pipeline SHALL stitch the section PDFs in
   section order using pdf-lib, with T&C pages last. _(parent 13.1, 13.2)_
2. WHEN stitching completes, THE pipeline SHALL write the final PDF to the configured S3
   output bucket. _(parent 13.3)_

### Requirement 4: S3-triggered processing  _(parent: Requirement 14)_

**User Story:** As a Business_User, I want the pipeline to trigger automatically on XML
arrival, so that contract notes generate without manual intervention.

#### Acceptance Criteria

1. WHEN an XML file is dropped in the input bucket, THE pipeline SHALL start and parse
   the XML into a JSON data structure. _(parent 14.1, 14.2)_
2. WHEN rendering completes, THE pipeline SHALL write the output PDF to the output
   bucket. _(parent 14.3)_
3. IF processing fails at any stage, THEN THE pipeline SHALL log the failure with context
   and SHALL NOT write a partial output. _(parent 14.4)_

### Requirement 5: Render orchestration  _(parent: Requirement 20)_

**User Story:** As a Business_User, I want the render orchestrated as discrete,
observable steps, so that failures are isolated, retryable and diagnosable.

#### Acceptance Criteria

1. THE state machine SHALL orchestrate discrete states: parse input, select template,
   select-and-render each section (Map state), stitch, write output. _(parent 20.1, 20.2)_
2. THE Map state SHALL process each section as an independent, retryable unit. _(parent 20.2)_
3. WHEN a section-level state fails after its configured retries, THE state machine SHALL
   route to a failure state that logs an error record and writes no partial output.
   _(parent 20.3)_
4. THE state machine SHALL be triggered by the S3 input event and record the outcome
   (success, or the failing state and reason) for observability. _(parent 20.4, 20.5)_
