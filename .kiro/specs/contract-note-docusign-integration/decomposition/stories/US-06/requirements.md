# Requirements Document

**Story US-06 — Webhook Lambda (completion + declined/expired)**

> Mini-spec derived from parent spec **contract-note-docusign-integration**.
> Delivers user story **US-06**. See `manifest.yaml` for the component
> exports/dependencies and `../../graph.yaml` for the full delivery graph.

## Introduction

This story delivers the Webhook Lambda that receives DocuSign Connect callbacks. It
validates the HMAC signature, routes by envelope status, and on completion downloads the
signed PDF, stores it in S3, uploads it to Salesforce, and updates metadata; on declined
or expired it updates metadata and writes a notification to the error bucket.

It is a wave-3 story consuming the three service stories (US-02, US-03, US-04) and the
US-01 foundation (signed-docs bucket, webhook route surface, error-writer). It has no
dependency on the Send Envelope Lambda (US-05) — both consume the same services. The
route-to-Lambda binding is finalised in US-08.

## Glossary

- **Webhook_Lambda**: This handler (`api/src/docusign/webhook.ts`).
- **Signed_PDF**: The completed document returned by DocuSign after signing.
- **Envelope_Status**: completed, declined, or expired (voided is out of scope).

## Delivered components

This story is responsible for creating and owning:

- `lambda:webhook` — the DocuSign Connect callback handler and its completion / declined /
  expired flows
- `api-endpoint:POST /docusign-webhook` — the route binding for the webhook handler

## Dependencies

This story depends on components delivered by other stories (must be available first):

- `service:docusign-client` (from US-03) — HMAC validation + signed-document download
- `service:salesforce-client` (from US-02) — signed-document upload
- `service:metadata-service` (from US-04) — get + update envelope records
- `s3-bucket:signed-contract-notes` (from US-01) — signed-document storage
- `shared-lib:error-writer` (from US-01) — notification + failure records
- `cdk-construct:DocuSignPipeline` (from US-01) — the webhook API route surface

## Requirements

### Requirement 1: Webhook reception and validation  _(parent: Requirement 6)_

**User Story:** As a system operator, I want to securely receive signing notifications
from DocuSign.

#### Acceptance Criteria

1. THE handler SHALL be reachable via the API Gateway `POST /docusign-webhook` route to
   receive DocuSign_Connect POST notifications. _(parent 6.1)_
2. THE handler SHALL validate incoming requests using HMAC signature verification (via the
   US-03 client) and return HTTP 401 with a logged invalid request if validation fails. _(parent 6.2, 6.3)_
3. THE handler SHALL handle the Envelope_Status events completed, declined, and expired
   (voided is out of scope), returning HTTP 200 to acknowledge receipt. _(parent 6.4)_

### Requirement 2: Signed document retrieval and storage  _(parent: Requirements 7, 8)_

**User Story:** As a system operator, I want the signed PDF retrieved and stored on
completion, and attached to the customer's Salesforce record.

#### Acceptance Criteria

1. WHEN a "completed" event is received, THE handler SHALL download the Signed_PDF by
   Envelope_ID (US-03) and store it in the signed-documents bucket with the Salesforce_Ref
   and Envelope_ID in the object key. _(parent 7.1, 7.2)_
2. THE handler SHALL upload the Signed_PDF to Salesforce and attach it to the record
   identified by the Salesforce_Ref (US-02), retrying download and upload up to 3 times
   with exponential backoff. _(parent 7.3, 8.1, 8.2, 8.3)_
3. IF all retries fail, THEN THE handler SHALL write an error record to the error bucket
   for manual investigation. _(parent 8.4)_
4. THE handler SHALL update the envelope metadata with "completed" status and the signed
   PDF S3 key (US-04). _(parent 5.3)_

### Requirement 3: Declined and expired handling  _(parent: Requirement 9)_

**User Story:** As a system operator, I want to be notified when a customer declines or
ignores a contract note.

#### Acceptance Criteria

1. WHEN a "declined" event is received, THE handler SHALL update the metadata record with
   the declined status and decline reason (if provided). _(parent 9.1)_
2. WHEN an "expired" event is received, THE handler SHALL update the metadata record with
   the expired status. _(parent 9.2)_
3. FOR declined and expired events, THE handler SHALL write a notification record to the
   error bucket containing the Envelope_ID, Salesforce_Ref, status, and timestamp. _(parent 9.3)_

### Requirement 4: Webhook observability  _(parent: Requirement 10)_

**User Story:** As a developer, I want the webhook flow logged and free of partial state.

#### Acceptance Criteria

1. THE handler SHALL log structured JSON to CloudWatch including the Envelope_ID, event
   type, and processing outcome. _(parent 10.3)_
2. THE handler SHALL not leave the system in an inconsistent state on failure (e.g. signed
   PDF in S3 but not in Salesforce without a logged error). _(parent 10.4)_
