---
issue_type: Story
key: US-06
summary: Webhook Lambda (completion + declined/expired)
parent_epic: contract-note-docusign-integration
identity_label: s2s-contract-note-docusign-integration-US-06
labels:
- s2s-contract-note-docusign-integration
- s2s-contract-note-docusign-integration-US-06
- backend
- lambda
- api
estimate_days: 2.0
covers_requirements:
- '6'
- '7'
- '8'
- '9'
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

As a system operator, I want a webhook Lambda that validates DocuSign callbacks and, on completion, stores the signed PDF in S3 and Salesforce (or notifies on declined/expired), so that post-signing actions happen automatically.

## Description

Implements the Webhook Lambda (`api/src/docusign/webhook.ts`) behind the `POST /docusign-webhook` route. It receives DocuSign Connect callbacks, validates the HMAC signature, looks up the envelope record by envelope ID, and routes by status. On `completed` it downloads the signed PDF, stores it in the signed-documents bucket, uploads it to Salesforce, and updates metadata; on `declined`/`expired` it updates metadata and writes a notification to the error bucket (`voided` is out of scope). It is a wave-3 story composing the US-02/US-03/US-04 services on the US-01 foundation; the route-to-Lambda binding is finalised in US-08.

## Delivers

- `lambda:webhook` — the DocuSign Connect callback handler and its completion / declined / expired flows.
- `api-endpoint:POST /docusign-webhook` — the route binding for the webhook handler.

## Acceptance criteria

- **Given** a DocuSign Connect notification, **when** it is POSTed to the API Gateway `POST /docusign-webhook` route, **then** the handler receives and processes it.
- **Given** an incoming request, **when** HMAC signature validation fails, **then** the handler returns HTTP 401 and logs the invalid request.
- **Given** an incoming request, **when** the HMAC signature is valid, **then** the handler parses the event, routes by envelope status, and returns HTTP 200 to acknowledge receipt.
- **Given** a valid event, **when** the envelope ID is unknown (no matching record), **then** the handler logs a warning and returns HTTP 200.
- **Given** a `completed` event, **when** it is processed, **then** the handler downloads the signed PDF, stores it in the signed-documents bucket, uploads it to Salesforce, and updates metadata to `completed` with the signed PDF S3 key, retrying download and upload up to 3 times with exponential backoff.
- **Given** a `completed` event, **when** all retries fail, **then** the handler writes an error record to the error bucket for manual investigation.
- **Given** a `declined` or `expired` event, **when** it is processed, **then** the handler updates the metadata record with the status (and decline reason if provided) and writes a notification record to the error bucket.

## Dependencies

- US-01 — Foundation: DocuSign pipeline infra, shared types & utilities
- US-02 — Salesforce integration client (greenfield)
- US-03 — DocuSign integration client
- US-04 — Envelope metadata service

## Traceability

Covers parent requirements: 6, 7, 8, 9, 10 · `s2s-contract-note-docusign-integration-US-06`

## Architecture

Builds `lambda:webhook` and the `POST /docusign-webhook` route (bound by US-08): HMAC gate (US-03) then routing — on `completed`, download (US-03) + store in the signed bucket (US-01) + upload to Salesforce (US-02) + update metadata (US-04); on `declined`/`expired`, update metadata and write a notification to the error bucket (US-01).

See the attached `US-06.png` for what this story builds and where each piece is used.

## Reference documentation

This Lambda orchestrates the service clients rather than calling DocuSign or Salesforce directly, so the vendor API references live on the client stories:

- DocuSign Connect HMAC validation + signed-document download — see **US-03** (Reference documentation).
- Salesforce signed-document upload — see **US-02** (Reference documentation).
