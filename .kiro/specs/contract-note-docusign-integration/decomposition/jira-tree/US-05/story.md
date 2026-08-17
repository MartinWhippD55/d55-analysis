---
issue_type: Story
key: US-05
summary: Send Envelope Lambda
parent_epic: contract-note-docusign-integration
identity_label: s2s-contract-note-docusign-integration-US-05
labels:
- s2s-contract-note-docusign-integration
- s2s-contract-note-docusign-integration-US-05
- backend
- lambda
estimate_days: 1.5
covers_requirements:
- '1'
- '2'
- '3'
- '4'
- '5'
- '10'
wave: 3
depends_on:
- US-01
- US-02
- US-03
- US-04
blocks:
- US-08
---

As a system operator, I want a Lambda that, on the SendEnvelope task, reads the contract metadata, looks up the customer, and creates a DocuSign envelope idempotently, so that signing starts automatically without duplicates.

## Description

The Send Envelope Lambda (`api/src/docusign/send-envelope.ts`) is the handler invoked by the `SendEnvelope` state-machine task after `writeOutput`. It reads the render output location and Contract_Metadata from the state payload, validates the metadata, enforces idempotency by the contract note S3 key, then orchestrates the send: Salesforce lookup → DocuSign auth + envelope creation → metadata store. It composes the three service stories (US-02, US-03, US-04) on the US-01 foundation and holds only orchestration and idempotency logic. The `SendEnvelope` task itself and its DocuSign-specific catch are wired at the state-machine level in US-08.

## Delivers

- `lambda:send-envelope` — the `SendEnvelope` task handler and its send orchestration: metadata extraction and validation, idempotency check by contract note S3 key, and the composed flow across `lookupContact`, `authenticate`/`createEnvelope`, and `createRecord`, with error records on failure.

## Acceptance criteria

- **Given** a `SendEnvelope` invocation, **when** the handler runs, **then** it reads the render output location (`output.bucket`/`output.key`) and Contract_Metadata (including `salesforceRef`, `offerReference`, `customerName`) from the state payload.
- **Given** a state payload without valid Contract_Metadata (missing or unusable `salesforceRef`), **when** the handler runs, **then** it logs a structured error and halts without creating an envelope.
- **Given** an envelope record already exists for the same contract note S3 key, **when** the handler runs, **then** it skips creation, logs, and returns without error (no double-send on task retry).
- **Given** valid metadata and no existing envelope, **when** the handler runs, **then** it orchestrates `lookupContact` (US-02) → `authenticate` + `createEnvelope` (US-03) → `createRecord` (US-04) with status "sent".
- **Given** any stage of the orchestration fails, **when** the handler catches the error, **then** it writes an error record to the error bucket (US-01 error-writer) and logs structured JSON to CloudWatch including the S3 key, Salesforce_Ref, and Envelope_ID for the stage.

## Dependencies

- US-01 — Foundation: DocuSign pipeline infra, shared types & utilities
- US-02 — Salesforce integration client (greenfield)
- US-03 — DocuSign integration client
- US-04 — Envelope metadata service

## Traceability

Covers parent requirements: 1, 2, 3, 4, 5, 10 · `s2s-contract-note-docusign-integration-US-05`

## Architecture

Builds `lambda:send-envelope`, the orchestration invoked by the `SendEnvelope` task (wired by US-08): extract + validate metadata, idempotency check by contract note S3 key, then `lookupContact` (US-02) → auth + `createEnvelope` (US-03) → `createRecord` (US-04), using US-01 types and error-writer.

See the attached `US-05.png` for what this story builds and where each piece is used.
