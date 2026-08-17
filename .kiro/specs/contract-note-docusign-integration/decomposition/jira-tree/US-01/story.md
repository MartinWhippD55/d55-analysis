---
issue_type: Story
key: US-01
summary: 'Foundation: DocuSign pipeline infra, shared types & utilities'
parent_epic: contract-note-docusign-integration
identity_label: s2s-contract-note-docusign-integration-US-01
labels:
- s2s-contract-note-docusign-integration
- s2s-contract-note-docusign-integration-US-01
- infra
- backend
estimate_days: 2.5
covers_requirements:
- '5'
- '6'
- '7'
- '8'
- '10'
- '11'
wave: 1
depends_on: []
blocks:
- US-02
- US-03
- US-04
- US-05
- US-06
---

As a developer, I want the DocuSign pipeline's base infrastructure (envelope table, signed-docs bucket, credential secrets, webhook API surface), the shared TypeScript types, and the retry + error-writer utilities, so that every other story has a stable foundation to build on.

## Description

US-01 provisions the wave-1 foundation for the DocuSign e-signature pipeline inside the `BrytBusinessServices` monorepo. It delivers the `DocuSignPipeline` CDK construct (envelope metadata table, signed-documents bucket, credential secret placeholders, webhook API route surface, IAM scaffolding), the shared TypeScript types every handler consumes, and two cross-cutting utilities (an exponential-backoff retry wrapper and an error-record writer). It has no upstream dependencies and creates no runtime behaviour of its own — it is the stable substrate that US-02 through US-08 build on.

## Delivers

- `DocuSignPipeline` CDK construct provisioning the table, signed-docs bucket, secret placeholders, webhook route surface and least-privilege IAM scaffolding.
- `DocuSignEnvelopes` table — the dedicated `{resourcePrefix}docusign-envelopes` DynamoDB table with `PK`/`SK` keys.
- `SalesforceRefIndex` GSI enabling query-by-Salesforce_Ref (`GSI_PK` = `salesforceRef`).
- `signed-contract-notes` bucket — the `{resourcePrefix}signed-contract-notes` S3 bucket.
- `shared-lib:docusign-types` — the shared TypeScript interfaces consumed by all handlers.
- `shared-lib:retry` — the exponential-backoff retry wrapper (`withRetry`).
- `shared-lib:error-writer` — the JSON error-record writer (`writeErrorRecord`) to the reused error bucket.

## Acceptance criteria

- **Given** the CDK stack, **when** the construct synthesises, **then** all Estimate 2 resources (table, bucket, Lambdas, API route, secrets) are named using the Resource_Prefix convention.
- **Given** DocuSign and Salesforce credentials, **when** the construct is deployed, **then** they are stored in AWS Secrets Manager under Resource_Prefix-scoped secret names.
- **Given** the envelope metadata store, **when** the table is provisioned, **then** it is a dedicated `{resourcePrefix}docusign-envelopes` table with `PK`/`SK` keys and a `SalesforceRefIndex` GSI on `GSI_PK` = `salesforceRef`.
- **Given** DocuSign_Connect callbacks, **when** the webhook route surface is provisioned, **then** it exposes a publicly accessible `POST /docusign-webhook` route that validates requests via HMAC verification.
- **Given** the Lambda functions, **when** IAM is configured, **then** each has least-privilege access only to the specific table, buckets, and secrets it requires.
- **Given** Estimate 1's `{resourcePrefix}contract-note-error-output` bucket, **when** error records are written, **then** they land under the `docusign/` key prefix and no new error bucket is provisioned.
- **Given** a sequence of transient failures, **when** the retry utility wraps a call, **then** it makes at most the configured attempts (default 3) with non-decreasing backoff and re-throws the last error if all fail.
- **Given** a pipeline failure, **when** the error-writer runs, **then** it writes a JSON record containing timestamp, stage, Envelope_ID (if known), Salesforce_Ref, error message, and context.
- **Given** the `api` and `cdk` workspaces, **when** they import shared types, **then** `EnvelopeRecord`, `EnvelopeStatus`, `ContractMetadata`, `SalesforceContact`, `CreateEnvelopeRequest`, `DocuSignWebhookEvent`, and the error-record type are exported from `shared-lib/src/index.ts`.

## Dependencies

- None — foundation story.

## Traceability

Covers parent requirements: 5, 6, 7, 8, 10, 11 · `s2s-contract-note-docusign-integration-US-01`

## Architecture

The stable substrate every other story builds on: the `DocuSignPipeline` CDK construct, the shared library (`docusign-types`, `withRetry`, `writeErrorRecord`), the `DocuSignEnvelopes` table with its `SalesforceRefIndex` GSI, and the `signed-contract-notes` bucket. It is consumed by US-02 and US-03 (types + retry), US-04 (table + GSI + types), US-05 (types + error-writer), and US-06 (construct + bucket + error-writer).

See the attached `US-01.png` for what this story builds and where each piece is used.
