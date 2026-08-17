# Requirements Document

**Story US-01 — Foundation: DocuSign pipeline infra, shared types & utilities**

> Mini-spec derived from parent spec **contract-note-docusign-integration**.
> Delivers user story **US-01**. See `manifest.yaml` for the component
> exports/dependencies and `../../graph.yaml` for the full delivery graph.

## Introduction

This story lays the foundation for the DocuSign e-signature pipeline delivered inside
the `BrytBusinessServices` monorepo. It provisions the base infrastructure (the
`DocuSignPipeline` CDK construct with the envelope metadata table, the signed-documents
bucket, credential secret placeholders, and the webhook API route surface), the shared
TypeScript types every handler consumes, and two cross-cutting utilities (an
exponential-backoff retry wrapper and an error-record writer).

It is a wave-1 story with no upstream dependencies. Every other backend story builds on
it: the Salesforce client (US-02), DocuSign client (US-03) and metadata service (US-04)
consume its types and utilities; the send (US-05) and webhook (US-06) Lambdas run
against its table, bucket and route surface; and integration (US-08) wires the construct
into `ContractNoteStack`.

## Glossary

- **Resource_Prefix**: The environment-specific CDK naming prefix (`dev-ci-bbs-`,
  `rel-uat-bbs-`, `rel-prod-bbs-`) applied to all resources in `BrytBusinessServices`.
- **DocuSignPipeline**: The new CDK construct (`cdk/lib/contract-notes/docusign-pipeline.ts`)
  that owns this estimate's infrastructure and is wired into `ContractNoteStack`.
- **Envelope_Record**: The DynamoDB metadata record tracking a DocuSign envelope.
- **Error_Bucket**: Estimate 1's `{resourcePrefix}contract-note-error-output` bucket,
  reused here under a `docusign/` key prefix (no new bucket is provisioned).

## Delivered components

This story is responsible for creating and owning:

- `cdk-construct:DocuSignPipeline` — the CDK construct provisioning the table, signed-docs
  bucket, secret placeholders, webhook API route surface and least-privilege IAM scaffolding
- `data-table:DocuSignEnvelopes` — the dedicated `{resourcePrefix}docusign-envelopes` table
- `gsi:SalesforceRefIndex` — the GSI enabling query-by-Salesforce_Ref
- `s3-bucket:signed-contract-notes` — the `{resourcePrefix}signed-contract-notes` bucket
- `shared-lib:docusign-types` — the shared TypeScript interfaces consumed by all handlers
- `shared-lib:retry` — the exponential-backoff retry wrapper
- `shared-lib:error-writer` — the JSON error-record writer to the reused error bucket

## Dependencies

None — this is a wave-1 foundation story.

## Requirements

### Requirement 1: Pipeline infrastructure and security  _(parent: Requirement 11)_

**User Story:** As a system operator, I want credentials securely managed and
infrastructure deployed via CDK, so that the system follows the `BrytBusinessServices`
conventions.

#### Acceptance Criteria

1. THE system SHALL store DocuSign credentials (Integration_Key, RSA private key,
   impersonating user ID, account ID, HMAC secret) in AWS Secrets Manager under a
   Resource_Prefix-scoped secret name. _(parent 11.1)_
2. THE system SHALL store Salesforce OAuth credentials in AWS Secrets Manager under a
   Resource_Prefix-scoped secret name, created fresh (no existing Salesforce secret to
   reuse). _(parent 11.2)_
3. THE system SHALL be deployed via CDK as a construct under `cdk/lib/contract-notes/`
   wired into `ContractNoteStack`, following the existing patterns (`NodejsFunction`
   handlers from `api/src/`, Resource_Prefix naming, `CfnOutput` exposure). _(parent 11.3)_
4. ALL Estimate 2 resources (DynamoDB table, S3 bucket, Lambdas, API Gateway route,
   secrets) SHALL be named using the Resource_Prefix convention. _(parent 11.4)_
5. THE webhook endpoint SHALL be publicly accessible (required for DocuSign_Connect) but
   SHALL validate all requests via HMAC verification. _(parent 11.5)_
6. Lambda functions SHALL have least-privilege IAM permissions: only access to the
   specific DynamoDB table, S3 buckets, and Secrets Manager secrets they require. _(parent 11.6)_
7. THE system SHALL reuse Estimate 1's error output bucket (`{resourcePrefix}contract-note-error-output`)
   for error and notification records, under a `docusign/` key prefix, rather than
   provisioning a new error bucket. _(parent 11.7)_

### Requirement 2: Envelope metadata table  _(parent: Requirement 5)_

**User Story:** As a developer, I want a dedicated envelope metadata store, so that
envelopes are queryable for webhook processing and debugging.

#### Acceptance Criteria

1. THE system SHALL provision a dedicated `{resourcePrefix}docusign-envelopes` DynamoDB
   table with `PK`/`SK` keys following the repo convention. _(parent 5.1)_
2. THE table SHALL expose a `SalesforceRefIndex` GSI (`GSI_PK` = `salesforceRef`) so that
   records are queryable by Envelope_ID (base table) and by Salesforce_Ref (GSI). _(parent 5.2)_

### Requirement 3: Webhook API route surface  _(parent: Requirement 6)_

**User Story:** As a system operator, I want a public HTTPS endpoint provisioned for
DocuSign callbacks, so that the webhook handler has a route to attach to.

#### Acceptance Criteria

1. THE construct SHALL provision an API Gateway `POST /docusign-webhook` route surface
   (on the existing `ContractNoteApi` or a dedicated API) for the webhook handler,
   publicly accessible for DocuSign_Connect. _(parent 6.1)_

### Requirement 4: Retry utility  _(parent: Requirements 7, 8)_

**User Story:** As a developer, I want a reusable exponential-backoff retry wrapper, so
that external API calls survive transient failures.

#### Acceptance Criteria

1. THE retry utility SHALL retry a wrapped call up to 3 attempts with exponential backoff
   (1s, 2s, 4s) and jitter (±500ms), configurable per call. _(parent 7.3, 8.3)_

### Requirement 5: Error record writer  _(parent: Requirement 10)_

**User Story:** As a developer, I want a standard error-record writer, so that all
pipeline failures land in the error bucket in a consistent format.

#### Acceptance Criteria

1. THE error-writer utility SHALL write JSON error records to the reused error S3 bucket
   under the `docusign/` prefix, containing timestamp, stage, Envelope_ID (if known),
   Salesforce_Ref, error message, and context. _(parent 10.1)_

### Requirement 6: Shared types  _(parent: Requirements 5, 6)_

**User Story:** As a developer, I want shared TypeScript interfaces, so that the `api`
and `cdk` workspaces consume one consistent set of types.

#### Acceptance Criteria

1. THE shared library SHALL export `EnvelopeRecord`, `EnvelopeStatus`, `ContractMetadata`,
   `SalesforceContact`, `CreateEnvelopeRequest`, `DocuSignWebhookEvent`, and the error-record
   type from `shared-lib/src/index.ts`. _(parent 5.1, 6.4)_
