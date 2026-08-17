---
issue_type: Story
key: US-02
summary: Salesforce integration client (greenfield)
parent_epic: contract-note-docusign-integration
identity_label: s2s-contract-note-docusign-integration-US-02
labels:
- s2s-contract-note-docusign-integration
- s2s-contract-note-docusign-integration-US-02
- backend
- salesforce
estimate_days: 2.0
covers_requirements:
- '2'
- '8'
wave: 2
depends_on:
- US-01
blocks:
- US-05
- US-06
---

As a system operator, I want a Salesforce client that authenticates, looks up customer contacts, and uploads signed documents, so that contract notes reach the right recipient and land back on the record.

## Description

Builds the Salesforce integration client from scratch — there is no reusable Salesforce OAuth/REST client in `BrytBusinessServices` or `BrytAdminPortal`, so this is greenfield. The client authenticates via OAuth (client credentials), looks up a customer contact by `customersalesforceref`, and uploads a signed PDF using the Files API (ContentVersion + ContentDocumentLink). It is a wave-2 story depending only on the US-01 foundation (shared types + retry utility); its lookup feeds the Send Envelope Lambda (US-05) and its upload feeds the Webhook Lambda (US-06).

## Delivers

- `service:salesforce-client` — OAuth authentication (client credentials), customer contact lookup by `customersalesforceref`, and signed-document upload (ContentVersion + ContentDocumentLink).

## Acceptance criteria

- **Given** the client is processing a contract note, **when** it calls the Salesforce API, **then** it authenticates using OAuth credentials read from AWS Secrets Manager.
- **Given** a valid `customersalesforceref`, **when** the client queries Salesforce, **then** it returns the customer contact name and email address.
- **Given** a lookup that fails (network error, invalid credentials, or record not found), **when** the client queries Salesforce, **then** it throws an error carrying the `customersalesforceref`.
- **Given** a customer record with no email address, **when** the client looks it up, **then** it throws an error indicating a missing contact email.
- **Given** a signed PDF, **when** the client uploads it, **then** it creates a ContentVersion and links it to the record via a ContentDocumentLink, using filename `Contract-Note-{offerReference}-Signed-{date}.pdf` and retrying with exponential backoff on transient failure.

## Dependencies

- US-01 — Foundation: DocuSign pipeline infra, shared types & utilities

## Traceability

Covers parent requirements: 2, 8 · `s2s-contract-note-docusign-integration-US-02`
