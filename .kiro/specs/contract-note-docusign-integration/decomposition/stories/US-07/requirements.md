# Requirements Document

**Story US-07 — Estimate 1 metadata surfacing (Requirement 12)**

> Mini-spec derived from parent spec **contract-note-docusign-integration**.
> Delivers user story **US-07**. See `manifest.yaml` for the component
> exports/dependencies and `../../graph.yaml` for the full delivery graph.

## Introduction

This story is a small, additive change to **Estimate 1's** landed render pipeline: surface
the customer reference and related metadata alongside the produced PDF, so the DocuSign
pipeline knows who to send each contract note to. Today `parse-input.ts` extracts only
`contractId`, and `write-output.ts` writes the PDF with only `{ templateId, pageCount }`
object metadata — the `customersalesforceref` present in the source contract data is not
carried through.

It is a wave-1 story with no dependency on any DocuSign work; it can start immediately.
Because it changes Estimate 1 code, it is **owned/coordinated with the Estimate 1 pipeline
owner (Jabez)**. Its output (the Contract_Metadata on the state payload) is consumed by the
Send Envelope Lambda (US-05) and wired into the `SendEnvelope` task by US-08.

## Glossary

- **Render_Pipeline**: Estimate 1's Step Functions state machine
  (`parseInput → selectTemplate → renderSections → stitch → writeOutput`).
- **Contract_Metadata**: Salesforce_Ref, offer reference, customer name, and contract note
  S3 key, threaded through the state payload.
- **Salesforce_Ref**: The `customersalesforceref` field in the source contract data.

## Delivered components

This story is responsible for creating and owning:

- `state-machine:render-metadata-passthrough` — the Estimate 1 render-pipeline change that
  extracts and threads Contract_Metadata through the state payload

## Dependencies

None — this is a wave-1 story (a self-contained change to Estimate 1's code).

## Requirements

### Requirement 1: Surface the customer reference from the render pipeline  _(parent: Requirement 12)_

**User Story:** As a developer, I want the render pipeline to surface the customer
reference alongside the produced PDF, so that the signing pipeline knows who to send each
contract note to.

#### Acceptance Criteria

1. THE Render_Pipeline SHALL extract `customersalesforceref`, offer reference, and customer
   name from the parsed contract data and carry them through the state machine payload from
   `parseInput` to the `writeOutput` and `SendEnvelope` stages. _(parent 12.1)_
2. THE Render_Pipeline SHALL make the Contract_Metadata available to the Send Envelope
   Lambda in the state payload passed to the `SendEnvelope` task. _(parent 12.2)_
3. THE Contract_Metadata SHALL include: Salesforce_Ref, offer reference, customer name, and
   the contract note S3 key. _(parent 12.3)_
4. IF the source contract data does not contain a `customersalesforceref`, THEN the
   Render_Pipeline SHALL still produce the PDF but the Contract_Metadata SHALL indicate the
   reference is absent (so the Send Envelope Lambda halts per US-05). _(parent 12.4)_
