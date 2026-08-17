# Requirements Document

**Story US-03 — DocuSign integration client**

> Mini-spec derived from parent spec **contract-note-docusign-integration**.
> Delivers user story **US-03**. See `manifest.yaml` for the component
> exports/dependencies and `../../graph.yaml` for the full delivery graph.

## Introduction

This story builds the DocuSign client that drives the eSignature REST API: JWT-grant
authentication, envelope creation (document + recipient + signing tab + per-envelope
webhook), signed-document download, and HMAC validation of incoming Connect callbacks.

It is a wave-2 story depending only on the US-01 foundation (shared types + retry
utility). Its consumers are the Send Envelope Lambda (US-05, which uses auth + envelope
creation) and the Webhook Lambda (US-06, which uses HMAC validation + download).

## Glossary

- **JWT_Grant**: The OAuth 2.0 server-to-server flow used to obtain DocuSign access
  tokens without user interaction.
- **Integration_Key**: The DocuSign client ID identifying the application.
- **Envelope / Envelope_ID**: A DocuSign container for documents/recipients, and its
  unique identifier.
- **Signing_Tab**: A signature field placed on the document for the recipient.
- **DocuSign_Connect**: DocuSign's webhook notification system.

## Delivered components

This story is responsible for creating and owning:

- `service:docusign-client` — JWT authentication, envelope creation, signed-document
  download, and HMAC webhook validation

## Dependencies

This story depends on components delivered by other stories (must be available first):

- `shared-lib:docusign-types` (from US-01) — `CreateEnvelopeRequest`, `DocuSignWebhookEvent`
- `shared-lib:retry` (from US-01) — the exponential-backoff wrapper used by download

The DocuSign secret is provisioned by the US-01 construct; the client reads it at runtime
via its secret ARN environment variable.

## Requirements

### Requirement 1: DocuSign authentication  _(parent: Requirement 3)_

**User Story:** As a system operator, I want the system to authenticate with DocuSign
automatically, so that envelopes can be created without manual login.

#### Acceptance Criteria

1. THE client SHALL authenticate to DocuSign using the JWT_Grant flow with credentials
   stored in AWS Secrets Manager. _(parent 3.1)_
2. THE client SHALL use the Integration_Key, RSA private key, and impersonating user ID
   to obtain an access token. _(parent 3.2)_
3. IF DocuSign authentication fails, THEN THE client SHALL throw the error for the caller
   to log and halt. _(parent 3.3)_
4. THE client SHALL cache the access token and refresh it before expiry to avoid
   unnecessary token requests. _(parent 3.4)_

### Requirement 2: Envelope creation and sending  _(parent: Requirement 4)_

**User Story:** As a system operator, I want the contract note PDF sent to the customer
for signing via DocuSign.

#### Acceptance Criteria

1. THE client SHALL create an envelope containing the contract note PDF as the document
   to be signed. _(parent 4.1)_
2. THE client SHALL configure the customer (name + email) as the sole signer recipient
   and place a Signing_Tab on the document. _(parent 4.2, 4.3)_
3. THE client SHALL set the envelope status to "sent" on creation and configure a
   per-envelope event notification (DocuSign_Connect) pointing to the webhook endpoint. _(parent 4.4, 4.5)_
4. IF envelope creation fails, THEN THE client SHALL throw with the contract note
   reference and Salesforce_Ref for the caller to log. _(parent 4.6)_

### Requirement 3: Signed document download  _(parent: Requirement 7)_

**User Story:** As a system operator, I want the signed PDF retrieved when signing is
complete.

#### Acceptance Criteria

1. THE client SHALL download the combined signed document for an Envelope_ID and return
   the PDF buffer, retrying transient failures up to 3 times with exponential backoff. _(parent 7.1, 7.3)_

### Requirement 4: HMAC webhook signature validation  _(parent: Requirement 6)_

**User Story:** As a system operator, I want to confirm callbacks originate from DocuSign.

#### Acceptance Criteria

1. THE client SHALL validate the `X-DocuSign-Signature-1` header against the payload using
   HMAC-SHA256 and return a valid/invalid result. _(parent 6.2, 6.3)_
