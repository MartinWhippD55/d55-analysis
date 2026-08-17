# Requirements Document

**Story US-04 — Envelope metadata service**

> Mini-spec derived from parent spec **contract-note-docusign-integration**.
> Delivers user story **US-04**. See `manifest.yaml` for the component
> exports/dependencies and `../../graph.yaml` for the full delivery graph.

## Introduction

This story delivers the envelope metadata service: the DynamoDB access layer over the
`docusign-envelopes` table. It creates a record on send, gets a record by Envelope_ID for
webhook processing, updates status on webhook events, and queries by Salesforce_Ref (via
the GSI) for debugging.

It is a wave-2 story depending only on the US-01 foundation (shared types + the table and
GSI). Its consumers are the Send Envelope Lambda (US-05, create) and the Webhook Lambda
(US-06, get + update).

## Glossary

- **Envelope_Record**: The `ENVELOPE#{envelopeId}` / `METADATA` DynamoDB record.
- **Envelope_Status**: The lifecycle state (sent, delivered, completed, declined, expired).
- **Salesforce_Ref**: Customer reference used by the `SalesforceRefIndex` GSI.

## Delivered components

This story is responsible for creating and owning:

- `service:metadata-service` — the DynamoDB create/get/update/query access layer for
  envelope metadata

## Dependencies

This story depends on components delivered by other stories (must be available first):

- `shared-lib:docusign-types` (from US-01) — the `EnvelopeRecord` and `EnvelopeStatus` types
- `data-table:DocuSignEnvelopes` (from US-01) — the metadata table
- `gsi:SalesforceRefIndex` (from US-01) — the query-by-Salesforce_Ref index

## Requirements

### Requirement 1: Envelope metadata operations  _(parent: Requirement 5)_

**User Story:** As a developer, I want envelope metadata stored and queryable, so that I
can drive webhook processing and investigate signing issues.

#### Acceptance Criteria

1. WHEN an envelope is successfully created, THE service SHALL store a metadata record
   containing the Envelope_ID, Salesforce_Ref, contract note S3 key, customer email,
   customer name, envelope status, and timestamps. _(parent 5.1)_
2. THE metadata record SHALL be queryable by Envelope_ID (base table, for webhook
   processing) and by Salesforce_Ref (via `SalesforceRefIndex`, for debugging). _(parent 5.2)_
3. WHEN a status update is applied, THE service SHALL update the corresponding record with
   the new Envelope_Status and `updatedAt` timestamp. _(parent 5.3)_
