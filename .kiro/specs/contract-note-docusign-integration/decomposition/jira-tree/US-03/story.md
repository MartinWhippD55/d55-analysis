---
issue_type: Story
key: US-03
summary: DocuSign integration client
parent_epic: contract-note-docusign-integration
identity_label: s2s-contract-note-docusign-integration-US-03
labels:
- s2s-contract-note-docusign-integration
- s2s-contract-note-docusign-integration-US-03
- backend
- docusign
estimate_days: 2.5
covers_requirements:
- '3'
- '4'
- '6'
- '7'
wave: 2
depends_on:
- US-01
blocks:
- US-05
- US-06
---

As a system operator, I want a DocuSign client that authenticates via JWT, creates/sends envelopes, downloads signed documents, and validates webhook signatures, so that the pipeline can drive e-signature end to end.

## Description

Builds the DocuSign client that wraps the eSignature REST API: JWT-grant authentication with a cached access token, envelope creation (base64 PDF document + sole signer + signing tab + per-envelope Connect webhook, status "sent"), signed-document download, and HMAC validation of incoming Connect callbacks. A wave-2 story depending only on the US-01 foundation (shared types + retry utility). Auth + envelope creation feed the send flow (US-05); download + HMAC validation feed the webhook flow (US-06). The `docusign-esign` npm package handles the JWT token exchange.

## Delivers

- `service:docusign-client` — a single client module providing JWT authentication (cached token), envelope creation, signed-document download, and HMAC webhook validation. It reads the DocuSign secret (`{resourcePrefix}contract-note/docusign`) at runtime and operates on the shared `CreateEnvelopeRequest` / `DocuSignWebhookEvent` types from US-01.

## Acceptance criteria

- **Given** valid DocuSign credentials in Secrets Manager (`integrationKey`, `rsaPrivateKey`, `impersonatedUserGuid`, `accountId`, `authServer`), **when** the client authenticates via the JWT_Grant flow (`POST /oauth/token`), **then** it obtains an access token, caches it, and reuses it within its validity period, only refreshing when expired or near-expiry.
- **Given** a `CreateEnvelopeRequest` with a contract note PDF and customer name + email, **when** the client calls `POST /v2.1/accounts/{accountId}/envelopes`, **then** it creates an envelope containing the base64 PDF as the document, the customer as the sole signer with a signing tab, a per-envelope `eventNotification` webhook pointing to the webhook endpoint, and status "sent", and returns the envelope ID.
- **Given** an `envelopeId` for a completed envelope, **when** the client calls `GET /v2.1/accounts/{accountId}/envelopes/{envelopeId}/documents/combined`, **then** it returns the combined signed PDF buffer, retrying transient failures up to 3 times with exponential backoff.
- **Given** an incoming Connect callback with an `X-DocuSign-Signature-1` header, **when** the client validates the raw body using HMAC-SHA256 with the shared `hmacSecret`, **then** it returns true only if the signature matches and false otherwise.

## Dependencies

- US-01 — Foundation: DocuSign pipeline infra, shared types & utilities

## Traceability

Covers parent requirements: 3, 4, 6, 7 · `s2s-contract-note-docusign-integration-US-03`

## Architecture

Builds `service:docusign-client` (JWT auth → `createEnvelope`, `downloadSigned`, `validateHmac`) on the US-01 shared types and retry utility. Auth + envelope creation feed the Send Envelope Lambda (US-05); HMAC validation + signed-document download feed the Webhook Lambda (US-06).

See the attached `US-03.png` for what this story builds and where each piece is used.
