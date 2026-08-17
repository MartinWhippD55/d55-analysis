# Requirements Document

**Story US-05 — Send Envelope Lambda**

> Mini-spec derived from parent spec **contract-note-docusign-integration**.
> Delivers user story **US-05**. See `manifest.yaml` for the component
> exports/dependencies and `../../graph.yaml` for the full delivery graph.

## Introduction

This story delivers the Send Envelope Lambda — the handler invoked by the `SendEnvelope`
state-machine task after `writeOutput`. It reads Contract_Metadata from the state payload,
validates it, checks idempotency by contract note S3 key, then orchestrates the send:
Salesforce lookup → DocuSign auth → envelope creation → metadata store.

It is a wave-3 story consuming the three service stories (US-02 Salesforce client, US-03
DocuSign client, US-04 metadata service) plus the US-01 foundation (types + error-writer).
The state-machine wiring of the `SendEnvelope` task and its DocuSign-specific catch is
delivered by US-08.

## Glossary

- **Contract_Metadata**: Salesforce_Ref, offer reference, customer name, and contract note
  S3 key, carried in the state payload (surfaced by US-07).
- **Send_Envelope_Lambda**: This handler (`api/src/docusign/send-envelope.ts`).
- **Idempotency key**: The contract note S3 key, used to avoid double-sending on a
  `SendEnvelope` task retry.

## Delivered components

This story is responsible for creating and owning:

- `lambda:send-envelope` — the `SendEnvelope` task handler and its send orchestration

## Dependencies

This story depends on components delivered by other stories (must be available first):

- `service:salesforce-client` (from US-02) — customer contact lookup
- `service:docusign-client` (from US-03) — JWT auth + envelope creation
- `service:metadata-service` (from US-04) — idempotency lookup + record create
- `shared-lib:docusign-types` (from US-01) — `ContractMetadata`, `EnvelopeRecord`
- `shared-lib:error-writer` (from US-01) — error-record writes on failure

## Requirements

### Requirement 1: SendEnvelope task handling and idempotency  _(parent: Requirement 1)_

**User Story:** As a system operator, I want signing to begin automatically and exactly
once when a contract note PDF is generated.

#### Acceptance Criteria

1. WHEN invoked by the `SendEnvelope` task, THE handler SHALL read the render output
   location and Contract_Metadata (including Salesforce_Ref) from the state payload. _(parent 1.1, 1.2)_
2. IF the state payload does not carry valid Contract_Metadata (including a usable
   Salesforce_Ref), THEN THE handler SHALL log an error and halt without creating an
   envelope. _(parent 1.3)_
3. THE handler SHALL be idempotent: before creating an envelope it SHALL check for an
   existing envelope record for the same contract note (keyed on the contract note S3 key)
   and SHALL NOT create a duplicate. _(parent 1.5)_

### Requirement 2: Send envelope orchestration  _(parent: Requirements 2, 3, 4, 5, 10)_

**User Story:** As a system operator, I want the full send flow orchestrated reliably,
with failures captured for diagnosis.

#### Acceptance Criteria

1. THE handler SHALL orchestrate the flow: Salesforce lookup (US-02) → DocuSign auth +
   envelope creation (US-03) → metadata store (US-04). _(parent 2.1, 3.1, 4.1, 5.1)_
2. ON any failure, THE handler SHALL write an error record to the error bucket (via the
   US-01 error-writer) and log structured JSON to CloudWatch including the S3 key,
   Salesforce_Ref, and Envelope_ID at each processing stage. _(parent 10.2)_
