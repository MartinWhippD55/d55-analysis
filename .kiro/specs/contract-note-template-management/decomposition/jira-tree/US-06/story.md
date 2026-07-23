---
issue_type: Story
key: US-06
summary: Render pipeline (Step Functions)
parent_epic: contract-note-template-management
identity_label: s2s-contract-note-template-management-US-06
labels:
- s2s-contract-note-template-management
- s2s-contract-note-template-management-US-06
- backend
- pipeline
- infra
estimate_days: 3.0
covers_requirements:
- '11'
- '12'
- '13'
- '14'
- '18'
- '19'
- '20'
wave: 2
depends_on:
- US-01
blocks:
- US-10
---

As a Business_User, I want contract data to be rendered to a PDF automatically via an orchestrated pipeline that selects the template, resolves pinned versions, picks section variants, renders and stitches, so that contract notes are produced reliably.

## Description

This backend/pipeline/infra story implements the `render-contract-note` render pipeline that replaces the legacy CreateHtml + html-to-pdf steps. It is an AWS Step Functions state machine, `RenderStateMachine`, triggered by an XML file landing in the input bucket. It coordinates single-purpose Lambdas: `parse-input` (XML → JSON), `select-template` (first-match-wins via the priority-ordered GSI and the shared specification evaluator), `render-section` inside a Map state (resolves the reference's pinned version, selects the section variant, fetches schema JSON, renders with @pdfme/generator), `stitch` (pdf-lib), and `write-output`. On any state failure after retries it routes to `handle-failure`, which writes a JSON error record and never leaves a partial output PDF.

It depends on the US-01 foundation (shared table, GSI, buckets, types) and, at render time, reads the template selection rule persisted by US-05 and the pinned versions and ordered variants/rules persisted by US-04 through the shared table. It exposes the state machine that US-10 wires into deployment (S3 trigger, IAM). It covers parent requirements 11 (rules engine and template selection), 12 (section rendering), 13 (PDF stitching), 14 (S3-triggered processing), 18 (pinned-version resolution), 19 (section variants and variant rules) and 20 (render orchestration).

## Delivers

- `state-machine:RenderStateMachine` — the orchestrating Step Functions state machine (`ParseInput` → `SelectTemplate` → `RenderSections` (Map) → `Stitch` → `WriteOutput`, with a `HandleFailure` catch).
- `shared-lib:spec-evaluator` — the recursive specification-tree evaluator (EQUALS / IN / LESS_THAN / MORE_THAN + AND / OR / NOT), reused for template and variant selection.
- `lambda:parse-input` — parses the dropped XML into a JSON contract-data object.
- `lambda:select-template` — first-match-wins template selection over the priority-ordered GSI.
- `lambda:render-section` — pinned-version resolution + variant selection + @pdfme/generator render, run per section in the Map state.
- `lambda:stitch` — pdf-lib concatenation of section PDFs in order, T&C pages last.
- `lambda:write-output` — writes the stitched PDF to the output bucket.
- `lambda:handle-failure` — writes a JSON error record to the error bucket and ensures no partial output.
- `s3-bucket:input-xml` — the XML input bucket (pipeline entry point).
- `s3-bucket:output-pdf` — the final PDF output bucket.

## Acceptance criteria

- **Given** contract data has been parsed, **when** the pipeline selects a template, **then** it evaluates template specifications in Template_List priority order (via `gsi:PriorityIndex`) and selects the first that evaluates true, stopping evaluation; if none match it logs an error and halts (Property 22, parent 11.1, 11.2, 11.3).
- **Given** a leaf specification node, **when** the evaluator runs, **then** EQUALS is true iff the field equals the value, IN true iff the value is in the set, LESS_THAN true iff the field is numerically below the threshold and MORE_THAN true iff above, combined with AND / OR / NOT (Property 23, parent 11.4, 11.5, 11.6).
- **Given** a section is being rendered, **when** the renderer resolves the section version, **then** it uses the reference's `pinnedVersionId` rather than the latest version (Property 34, parent 18.6).
- **Given** a section that has variants, **when** the renderer selects a variant, **then** it evaluates each Variant_Rule in variant order and takes the first match, falling back to the default; a section with no variants uses the section's own schema; if none match and there is no default it logs an error identifying the section and halts (Properties 35, 36, 37, parent 19.5, 19.6, 19.8).
- **Given** a selected variant with valid schema JSON and complete input data, **when** the section is rendered via @pdfme/generator with the text/multiVariableText/table plugins and NotoSans, **then** it produces a non-empty valid PDF buffer; a render failure is logged with section and template context and halts (Property 24, parent 12.1, 12.2, 12.3).
- **Given** all sections have rendered successfully, **when** the pipeline stitches, **then** it concatenates the section PDFs in section order with pdf-lib (T&C pages last) into a single PDF whose page count equals the sum of the inputs' and writes it to the output bucket (Property 25, parent 13.1, 13.2, 13.3).
- **Given** an XML file is dropped in the input bucket, **when** the pipeline starts, **then** it parses the XML into a JSON structure preserving all fields present in the XML and, on success, writes the output PDF to the output bucket (Property 26, parent 14.1, 14.2, 14.3).
- **Given** a run that fails at any stage after retries, **when** the failure is handled, **then** the state machine routes to `HandleFailure`, writes a JSON error record (timestamp, inputFile, stage, templateId, sectionId, error, context) to the error bucket, and the output bucket contains no file for that contract note (Properties 27, 38, parent 14.4, 20.3).
- **Given** the render is orchestrated as discrete states, **when** a section-level state runs, **then** the Map state processes each section as an independent, retryable unit and the per-run outcome (success, or the failing state and reason) is recorded for observability (parent 20.1, 20.2, 20.4, 20.5).

## Dependencies

- US-01 — Foundation: infrastructure & shared types

## Traceability

Covers parent requirements: 11, 12, 13, 14, 18, 19, 20 · `s2s-contract-note-template-management-US-06`
