# Requirements Document

**Story US-02 — Salesforce integration client (greenfield)**

> Mini-spec derived from parent spec **contract-note-docusign-integration**.
> Delivers user story **US-02**. See `manifest.yaml` for the component
> exports/dependencies and `../../graph.yaml` for the full delivery graph.

## Introduction

This story builds the Salesforce integration client from scratch — there is no reusable
Salesforce OAuth/REST client in `BrytBusinessServices` or `BrytAdminPortal`. The client
provides three capabilities: OAuth authentication, customer contact lookup by
`customersalesforceref`, and signed-document upload (Files: ContentVersion +
ContentDocumentLink).

It is a wave-2 story depending only on the US-01 foundation (shared types + retry
utility). Its consumers are the Send Envelope Lambda (US-05, which uses the lookup) and
the Webhook Lambda (US-06, which uses the upload).

## Glossary

- **Salesforce_Ref**: The `customersalesforceref` field used to correlate to the customer
  record in Salesforce.
- **ContentVersion / ContentDocumentLink**: The Salesforce Files API objects used to
  store a document and attach it to a record (preferred over legacy Attachments).
- **Signed_PDF**: The completed document returned by DocuSign after signing.

## Delivered components

This story is responsible for creating and owning:

- `service:salesforce-client` — OAuth authentication, customer contact lookup, and
  signed-document upload

## Dependencies

This story depends on components delivered by other stories (must be available first):

- `shared-lib:docusign-types` (from US-01) — the `SalesforceContact` type
- `shared-lib:retry` (from US-01) — the exponential-backoff wrapper used by upload

The Salesforce OAuth secret is provisioned by the US-01 construct; the client reads it at
runtime via its secret ARN environment variable.

## Requirements

### Requirement 1: Salesforce customer lookup  _(parent: Requirement 2)_

**User Story:** As a system operator, I want customer contact details retrieved from
Salesforce, so that the signing email is sent to the correct recipient.

#### Acceptance Criteria

1. WHEN the client processes a contract note, IT SHALL authenticate to the Salesforce API
   using OAuth credentials stored in AWS Secrets Manager. _(parent 2.1)_
2. THE client SHALL query Salesforce using the Salesforce_Ref to retrieve the customer
   contact name and email address. _(parent 2.2)_
3. IF the Salesforce lookup fails (network error, invalid credentials, or record not
   found), THEN THE client SHALL throw an error carrying the Salesforce_Ref. _(parent 2.3)_
4. IF the customer record exists but has no email address, THEN THE client SHALL throw an
   error indicating missing contact email. _(parent 2.4)_

### Requirement 2: Signed document upload to Salesforce  _(parent: Requirement 8)_

**User Story:** As a system operator, I want the signed contract note attached to the
customer's Salesforce record, so that the sales team has immediate access.

#### Acceptance Criteria

1. THE client SHALL upload the signed PDF as a ContentVersion and link it to the record
   identified by the Salesforce_Ref via a ContentDocumentLink. _(parent 8.1)_
2. THE client SHALL set the filename as `Contract-Note-{offerReference}-Signed-{date}.pdf`
   and an appropriate content type on the upload. _(parent 8.2)_
3. IF the Salesforce upload fails, THEN THE client SHALL retry up to 3 times with
   exponential backoff (via the US-01 retry utility). _(parent 8.3)_
