---
issue_type: Story
key: US-07
summary: Estimate 1 metadata surfacing (Requirement 12)
parent_epic: contract-note-docusign-integration
identity_label: s2s-contract-note-docusign-integration-US-07
labels:
- s2s-contract-note-docusign-integration
- s2s-contract-note-docusign-integration-US-07
- backend
- estimate-1
- cross-team
estimate_days: 1.0
covers_requirements:
- '12'
wave: 1
depends_on: []
blocks:
- US-08
---

As a developer, I want the Estimate 1 render pipeline to surface the customer reference and related metadata alongside the produced PDF, so that the DocuSign pipeline knows who to send each contract note to.

## Description

An additive change to Estimate 1's landed render pipeline: surface the customer reference and related metadata alongside the produced PDF so the DocuSign pipeline knows who to send each contract note to. Today `parse-input.ts` extracts only `contractId` and `write-output.ts` writes the PDF with only `{ templateId, pageCount }` metadata — the `customersalesforceref` in the source contract data is never carried through. This story extracts it and threads `Contract_Metadata` through the state machine payload to the write-output and `SendEnvelope` stages.

This is a cross-team change to Estimate 1 code, coordinated and reviewed with the Estimate 1 pipeline owner (Jabez), and kept strictly additive so render behaviour is unchanged when the reference is absent. It is a wave-1 story with no dependency on any DocuSign work and can start immediately. Its output is consumed by US-05 and wired into the `SendEnvelope` task by US-08.

## Delivers

- `state-machine:render-metadata-passthrough` — the Estimate 1 render-pipeline change that extracts and threads `Contract_Metadata` through the state payload.

## Acceptance criteria

- **Given** parsed contract data that contains a `customersalesforceref`, **when** `buildContractSummary` runs in the render pipeline, **then** it extracts `customersalesforceref`, the offer reference, and the customer name (in addition to the existing `contractId`).
- **Given** the extracted metadata, **when** the pipeline runs from `parseInput` through to `write-output` and the `SendEnvelope` stage, **then** `Contract_Metadata` is threaded through the state payload and made available to the Send Envelope Lambda.
- **Given** the `Contract_Metadata` on the state payload, **when** it reaches the `SendEnvelope` stage, **then** it includes `salesforceRef`, `offerReference`, `customerName`, and `contractNoteS3Key`.
- **Given** source contract data with no `customersalesforceref`, **when** the pipeline runs, **then** it still produces the PDF but marks the `Contract_Metadata` reference-absent so US-05 halts.

## Dependencies

- None — foundation story.

## Traceability

Covers parent requirements: 12 · `s2s-contract-note-docusign-integration-US-07`

## Architecture

Builds `state-machine:render-metadata-passthrough`: an additive Estimate 1 change that extracts `customersalesforceref` at `ParseInput` and threads `Contract_Metadata` through the state payload to `WriteOutput` and the `SendEnvelope` stage. Its output feeds the Send Envelope Lambda (US-05) and is wired into the state machine by US-08.

See the attached `US-07.png` for what this story builds and where each piece is used.
