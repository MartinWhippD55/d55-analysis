---
issue_type: Story
key: US-04
summary: Envelope metadata service
parent_epic: contract-note-docusign-integration
identity_label: s2s-contract-note-docusign-integration-US-04
labels:
- s2s-contract-note-docusign-integration
- s2s-contract-note-docusign-integration-US-04
- backend
- data
estimate_days: 1.0
covers_requirements:
- '5'
wave: 2
depends_on:
- US-01
blocks:
- US-05
- US-06
---

As a developer, I want envelope metadata persisted and queryable, so that the webhook can find records by envelope ID and I can debug by Salesforce reference.

## Description

Delivers the envelope metadata service: a thin, well-tested DynamoDB access layer over the US-01 `{resourcePrefix}docusign-envelopes` table. It creates a record when an envelope is sent, gets a record by envelope ID for webhook processing, updates the status on webhook events, and queries by Salesforce reference via the `SalesforceRefIndex` GSI for debugging. This is a wave-2 story depending only on the US-01 foundation (shared types plus the table and GSI); its consumers are the Send Envelope Lambda (US-05, create) and the Webhook Lambda (US-06, get + update).

## Delivers

- `service:metadata-service` — the DynamoDB create/get/update/query-by-GSI access layer over the `{resourcePrefix}docusign-envelopes` table (base-table key `PK = ENVELOPE#{envelopeId}`, `SK = METADATA`; GSI `SalesforceRefIndex`).

## Acceptance criteria

- **Given** an envelope has been successfully sent, **when** `createRecord` is called, **then** a metadata record is stored with the envelope ID, Salesforce reference, contract note S3 key, customer email, customer name, envelope status, and `createdAt`/`updatedAt` timestamps.
- **Given** a stored envelope record, **when** it is fetched by envelope ID via the base table, **then** the corresponding `EnvelopeRecord` is returned (or `undefined` when no record exists).
- **Given** a webhook event for an existing envelope, **when** `updateStatus` is applied, **then** the record is updated with the new `EnvelopeStatus` and a newer `updatedAt` timestamp.
- **Given** stored envelope records, **when** queried by Salesforce reference via `SalesforceRefIndex`, **then** the matching `EnvelopeRecord`s are returned for debugging.

## Dependencies

- US-01 — Foundation: DocuSign pipeline infra, shared types & utilities

## Traceability

Covers parent requirements: 5 · `s2s-contract-note-docusign-integration-US-04`

## Architecture

Builds `service:metadata-service` — the DynamoDB `create` / `get` / `update` / `queryByGSI` access layer over the US-01 `DocuSignEnvelopes` table and `SalesforceRefIndex` GSI. Consumed by the Send Envelope Lambda (US-05, create) and the Webhook Lambda (US-06, get + update status).

See the attached `US-04.png` for what this story builds and where each piece is used.
