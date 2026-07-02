# Implementation Plan: Contract Note DocuSign Integration

## Overview

Implement an automated e-signature pipeline that takes rendered contract note PDFs from Estimate 1, sends them to customers via DocuSign, and stores signed copies in S3 and Salesforce. The implementation uses AWS Lambda (Node.js/TypeScript), API Gateway, DynamoDB, S3, Secrets Manager, and CDK for infrastructure.

## Tasks

- [ ] 1. Infrastructure and shared utilities
  - [ ] 1.1 Define CDK infrastructure for DynamoDB table, S3 bucket, API Gateway, and Secrets Manager
    - Create DynamoDB table `DocuSignEnvelopes` with PK/SK pattern and GSI `SalesforceRefIndex`
    - Create S3 bucket for signed documents
    - Add S3 event notification on Estimate 1's output bucket to trigger Send Envelope Lambda
    - Add API Gateway POST route `/docusign-webhook` for webhook handler
    - Create Secrets Manager secret placeholders for DocuSign and Salesforce credentials
    - Configure IAM roles with least-privilege access
    - _Requirements: 1.1, 6.1, 11.3, 11.4, 11.5_

  - [ ] 1.2 Create shared TypeScript interfaces and types
    - Define `EnvelopeRecord`, `EnvelopeStatus`, `ContractMetadata`, `SalesforceContact` types
    - Define `CreateEnvelopeRequest`, `DocuSignWebhookEvent` interfaces
    - Define error record structure type
    - Place in a shared `types/` module accessible by both Lambda functions
    - _Requirements: 5.1, 6.4_

  - [ ] 1.3 Implement retry utility with exponential backoff
    - Generic retry wrapper: max attempts, exponential backoff (1s, 2s, 4s), jitter (±500ms)
    - Configurable per-call; used by DocuSign download and Salesforce upload
    - _Requirements: 7.3, 8.3_

  - [ ] 1.4 Implement error record writer utility
    - Write JSON error records to the error S3 bucket
    - Standard format: timestamp, stage, envelopeId, salesforceRef, error, context
    - _Requirements: 10.1_

- [ ] 2. Salesforce integration client
  - [ ] 2.1 Implement Salesforce OAuth client
    - Read credentials from Secrets Manager (`contract-note/salesforce`)
    - Obtain and cache access token using client credentials flow
    - Refresh token before expiry
    - _Requirements: 2.1_

  - [ ] 2.2 Implement customer contact lookup
    - Query Salesforce using `customersalesforceref` to find customer record
    - Return contact name and email address
    - Handle: record not found (throw), no email on record (throw), network errors (throw)
    - _Requirements: 2.2, 2.3, 2.4_

  - [ ] 2.3 Implement signed document upload to Salesforce
    - Create ContentVersion record with signed PDF bytes
    - Create ContentDocumentLink to attach to the customer record
    - Set filename: `Contract-Note-{offerReference}-Signed-{date}.pdf`
    - Use retry utility for transient failures
    - _Requirements: 8.1, 8.2, 8.3_

  - [ ]* 2.4 Write property tests for Salesforce client
    - **Property 2: Salesforce lookup correctness**
    - **Property 3: Missing contact halts processing**
    - **Validates: Requirements 2.2, 2.3, 2.4**

- [ ] 3. DocuSign integration client
  - [ ] 3.1 Implement DocuSign JWT authentication
    - Read credentials from Secrets Manager (`contract-note/docusign`)
    - Build JWT assertion with integration key, impersonated user, scope
    - Exchange JWT for access token
    - Cache token and refresh before expiry
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [ ] 3.2 Implement envelope creation
    - Build envelope definition: document (base64 PDF), recipient (name, email), signing tabs
    - Configure per-envelope webhook (eventNotification) pointing to webhook endpoint
    - Set status to "sent" to trigger immediate email delivery
    - Return envelope ID
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

  - [ ] 3.3 Implement signed document download
    - Download combined document from envelope using envelope ID
    - Return PDF buffer
    - Use retry utility for transient failures
    - _Requirements: 7.1, 7.3_

  - [ ] 3.4 Implement HMAC webhook signature validation
    - Validate X-DocuSign-Signature-1 header against payload using HMAC-SHA256
    - Return valid/invalid result
    - _Requirements: 6.2, 6.3_

  - [ ]* 3.5 Write property tests for DocuSign client
    - **Property 4: JWT authentication token management**
    - **Property 5: Envelope contains correct document and recipient**
    - **Property 6: Webhook HMAC validation**
    - **Validates: Requirements 3.1, 3.2, 3.4, 4.1, 4.2, 4.3, 6.2, 6.3**

- [ ] 4. Envelope metadata service
  - [ ] 4.1 Implement DynamoDB metadata operations
    - Create envelope record (on successful send)
    - Get envelope record by envelope ID (for webhook processing)
    - Update envelope status (on webhook events)
    - Query by Salesforce_Ref (for debugging, uses GSI)
    - _Requirements: 5.1, 5.2, 5.3_

  - [ ]* 4.2 Write property tests for metadata service
    - **Property 8: Metadata record reflects current status**
    - **Validates: Requirements 5.1, 5.2, 5.3**

- [ ] 5. Send Envelope Lambda handler
  - [ ] 5.1 Implement S3 event handler and contract metadata extraction
    - Parse S3 event to get bucket and key
    - Read contract data metadata from S3 object metadata or sidecar JSON file
    - Extract customersalesforceref, offerReference, customerName
    - Validate required fields present; log error and halt if missing
    - _Requirements: 1.1, 1.2, 1.3_

  - [ ] 5.2 Implement send envelope orchestration
    - Orchestrate the full flow: extract metadata → Salesforce lookup → DocuSign auth → create envelope → store metadata
    - On any failure: write error record to error bucket, log to CloudWatch
    - _Requirements: 1.1, 2.1, 3.1, 4.1, 5.1, 10.2_

  - [ ]* 5.3 Write property tests for send envelope flow
    - **Property 1: Trigger-to-envelope correlation**
    - **Validates: Requirements 1.1, 4.1, 5.1**

- [ ] 6. Checkpoint - Send side complete
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Webhook Lambda handler
  - [ ] 7.1 Implement webhook request handler
    - Validate HMAC signature; return 401 if invalid
    - Parse webhook event payload
    - Route by status: completed → completion flow, declined/expired → notification flow
    - Return 200 to acknowledge receipt
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

  - [ ] 7.2 Implement completion flow
    - Look up envelope metadata by envelope ID
    - Download signed PDF from DocuSign (with retries)
    - Store signed PDF in S3 signed documents bucket
    - Upload signed PDF to Salesforce (with retries)
    - Update envelope metadata with "completed" status and signed PDF S3 key
    - On final failure: write to error bucket
    - _Requirements: 7.1, 7.2, 7.3, 8.1, 8.2, 8.3, 8.4_

  - [ ] 7.3 Implement declined/expired flow
    - Look up envelope metadata by envelope ID
    - Update metadata with declined/expired status and reason
    - Write notification record to error bucket
    - _Requirements: 9.1, 9.2, 9.3_

  - [ ]* 7.4 Write property tests for webhook handler
    - **Property 7: Completed envelope produces signed PDF in both S3 and Salesforce**
    - **Property 9: Declined/expired produces notification**
    - **Property 10: Failure produces no partial state**
    - **Validates: Requirements 7.1, 7.2, 8.1, 9.1, 9.2, 9.3, 10.4**

- [ ] 8. Checkpoint - Webhook side complete
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Integration wiring and deployment
  - [ ] 9.1 Wire CDK deployment for all components
    - Ensure S3 event notification connects output bucket to Send Envelope Lambda
    - Ensure API Gateway route connects to Webhook Lambda
    - Ensure Lambda functions have correct IAM permissions for DynamoDB, S3, and Secrets Manager
    - Configure Lambda environment variables (table name, bucket names, webhook URL, secret ARNs)
    - _Requirements: 1.1, 6.1, 11.3, 11.5_

  - [ ] 9.2 Configure contract metadata sidecar in Estimate 1 render pipeline
    - Modify render pipeline to write a JSON sidecar file alongside the PDF output
    - Sidecar contains: customersalesforceref, offerReference, customerName, contractNoteS3Key
    - _Requirements: 1.2_

  - [ ]* 9.3 Write integration tests for full pipeline flow
    - Test: PDF + sidecar in output bucket → verify envelope metadata in DynamoDB
    - Test: valid webhook POST → verify signed PDF in S3
    - Test: invalid HMAC → verify 401 response
    - Test: declined webhook → verify notification in error bucket
    - _Requirements: 1.1, 6.2, 7.2, 9.3_

- [ ] 10. Final checkpoint
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- The DocuSign SDK (`docusign-esign`) is available as an npm package and handles JWT token exchange
- Salesforce attachment uses ContentVersion + ContentDocumentLink pattern (Files, not legacy Attachments)
- The webhook endpoint must be publicly accessible for DocuSign Connect to reach it
- Per-envelope webhook config avoids needing DocuSign admin account-level configuration
- Error bucket is shared with Estimate 1 but uses a `docusign/` prefix for organisation
