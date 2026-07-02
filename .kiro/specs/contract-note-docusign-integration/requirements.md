# Requirements Document

## Introduction

This document specifies the requirements for Estimate 2 of the Bryt Energy Contract Note Rework project. The system automates the e-signature process for contract notes by integrating with DocuSign: taking the rendered PDF from Estimate 1's pipeline, sending it to the customer for electronic signature via DocuSign, and storing the signed copy back in Salesforce.

The solution is a fully automated, headless pipeline with no Admin Portal UI. It triggers when a contract note PDF is produced, looks up customer contact details in Salesforce, creates a DocuSign envelope, and handles the completion webhook to retrieve and store the signed document.

## Glossary

- **Render_Pipeline**: The automated process from Estimate 1 that generates contract note PDFs and writes them to the S3 output bucket
- **Envelope**: A DocuSign container that holds the document(s) to be signed, recipient information, and signing workflow configuration
- **Envelope_ID**: The unique identifier returned by DocuSign when an envelope is created
- **Signing_Tab**: A DocuSign signature field placed on the document that the recipient must sign
- **DocuSign_Connect**: DocuSign's webhook notification system that sends HTTP POST callbacks when envelope status changes occur
- **JWT_Grant**: The OAuth 2.0 server-to-server authentication flow used to obtain DocuSign API access tokens without user interaction
- **Integration_Key**: The DocuSign client ID that identifies the application (equivalent to an OAuth client_id)
- **Salesforce_Ref**: The `customersalesforceref` field from the contract data payload, used to correlate back to the customer record in Salesforce
- **Signed_PDF**: The completed document returned by DocuSign after all signatories have signed
- **Envelope_Status**: The lifecycle state of a DocuSign envelope (created, sent, delivered, viewed, completed, declined, voided, expired)
- **Send_Envelope_Lambda**: The Lambda function triggered by the S3 output event that orchestrates the Salesforce lookup and DocuSign envelope creation
- **Webhook_Lambda**: The Lambda function that receives DocuSign Connect callbacks and handles signed document retrieval and storage

## Requirements

### Requirement 1: Automated Trigger from Render Pipeline

**User Story:** As a system operator, I want the signing process to begin automatically when a contract note PDF is generated, so that no manual intervention is required to initiate e-signatures.

#### Acceptance Criteria

1. WHEN the Render_Pipeline writes a contract note PDF to the S3 output bucket, THE Send_Envelope_Lambda SHALL be triggered automatically via an S3 event notification
2. THE Send_Envelope_Lambda SHALL extract the contract data metadata (including Salesforce_Ref) from the S3 object metadata or an accompanying JSON sidecar file
3. IF the trigger event does not contain valid contract data metadata, THEN THE Send_Envelope_Lambda SHALL log an error and halt processing without creating an envelope

### Requirement 2: Salesforce Customer Lookup

**User Story:** As a system operator, I want customer contact details to be retrieved from Salesforce, so that the signing email is sent to the correct recipient.

#### Acceptance Criteria

1. WHEN the Send_Envelope_Lambda processes a contract note, IT SHALL authenticate to the Salesforce API using OAuth credentials stored in AWS Secrets Manager
2. THE Send_Envelope_Lambda SHALL query Salesforce using the Salesforce_Ref to retrieve the customer contact name and email address
3. IF the Salesforce lookup fails (network error, invalid credentials, or record not found), THEN THE Send_Envelope_Lambda SHALL log the error with the Salesforce_Ref and halt processing
4. IF the customer record exists but has no email address, THEN THE Send_Envelope_Lambda SHALL log an error indicating missing contact email and halt processing

### Requirement 3: DocuSign Authentication

**User Story:** As a system operator, I want the system to authenticate with DocuSign automatically, so that envelopes can be created without manual login.

#### Acceptance Criteria

1. THE Send_Envelope_Lambda SHALL authenticate to DocuSign using the JWT_Grant flow with credentials stored in AWS Secrets Manager
2. THE Send_Envelope_Lambda SHALL use the Integration_Key, RSA private key, and impersonating user ID to obtain an access token
3. IF DocuSign authentication fails, THEN THE Send_Envelope_Lambda SHALL log the error and halt processing
4. THE Send_Envelope_Lambda SHALL cache the access token and refresh it before expiry to avoid unnecessary token requests

### Requirement 4: Envelope Creation and Sending

**User Story:** As a system operator, I want the contract note PDF to be sent to the customer for signing via DocuSign, so that the customer can e-sign without printing or scanning.

#### Acceptance Criteria

1. THE Send_Envelope_Lambda SHALL create a DocuSign envelope containing the contract note PDF as the document to be signed
2. THE Send_Envelope_Lambda SHALL configure the customer (name and email from Salesforce) as the sole signer recipient on the envelope
3. THE Send_Envelope_Lambda SHALL place a Signing_Tab (signature field) on the document for the customer to sign
4. THE Send_Envelope_Lambda SHALL set the envelope status to "sent" on creation, causing DocuSign to immediately email the signing request to the customer
5. THE Send_Envelope_Lambda SHALL configure a per-envelope event notification (DocuSign_Connect) pointing to the Webhook_Lambda endpoint for status callbacks
6. IF envelope creation fails, THEN THE Send_Envelope_Lambda SHALL log the error with the contract note reference and Salesforce_Ref

### Requirement 5: Envelope Metadata Storage

**User Story:** As a developer, I want envelope metadata stored for debugging and traceability, so that I can investigate issues with the signing process.

#### Acceptance Criteria

1. WHEN an envelope is successfully created, THE Send_Envelope_Lambda SHALL store a metadata record in DynamoDB containing the Envelope_ID, Salesforce_Ref, contract note S3 key, customer email, envelope status, and timestamps
2. THE metadata record SHALL be queryable by Envelope_ID (for webhook processing) and by Salesforce_Ref (for debugging)
3. WHEN the Webhook_Lambda receives a status update, IT SHALL update the corresponding metadata record with the new Envelope_Status and timestamp

### Requirement 6: Webhook Reception and Validation

**User Story:** As a system operator, I want the system to securely receive signing completion notifications from DocuSign, so that post-signing actions happen automatically.

#### Acceptance Criteria

1. THE Webhook_Lambda SHALL expose an HTTPS endpoint via API Gateway to receive DocuSign_Connect POST notifications
2. THE Webhook_Lambda SHALL validate incoming webhook requests using HMAC signature verification to confirm they originate from DocuSign
3. IF webhook validation fails, THEN THE Webhook_Lambda SHALL return HTTP 401 and log the invalid request
4. THE Webhook_Lambda SHALL handle the following Envelope_Status events: completed, declined, and expired (voided is out of scope)

### Requirement 7: Signed Document Retrieval

**User Story:** As a system operator, I want the signed PDF to be automatically retrieved when signing is complete, so that it can be stored without manual download.

#### Acceptance Criteria

1. WHEN the Webhook_Lambda receives a "completed" status event, IT SHALL authenticate to DocuSign and download the Signed_PDF using the Envelope_ID
2. THE Webhook_Lambda SHALL store the Signed_PDF in the designated S3 bucket for signed documents, with the Salesforce_Ref and Envelope_ID in the object key for traceability
3. IF the signed document download fails, THEN THE Webhook_Lambda SHALL log the error and retry up to 3 times with exponential backoff

### Requirement 8: Salesforce Attachment

**User Story:** As a system operator, I want the signed contract note to be automatically attached to the customer's Salesforce record, so that the sales team has immediate access to the completed contract.

#### Acceptance Criteria

1. WHEN the Signed_PDF has been stored in S3, THE Webhook_Lambda SHALL upload the document to Salesforce and attach it to the record identified by the Salesforce_Ref
2. THE Webhook_Lambda SHALL set appropriate metadata on the Salesforce attachment (filename including contract reference and date, content type)
3. IF the Salesforce upload fails, THEN THE Webhook_Lambda SHALL log the error and retry up to 3 times with exponential backoff
4. IF all retries fail, THEN THE Webhook_Lambda SHALL write an error record to the error S3 bucket for manual investigation

### Requirement 9: Declined and Expired Envelope Handling

**User Story:** As a system operator, I want to be notified when a customer declines or ignores a contract note, so that appropriate follow-up can occur.

#### Acceptance Criteria

1. WHEN the Webhook_Lambda receives a "declined" status event, IT SHALL update the envelope metadata record with the declined status and the decline reason (if provided by DocuSign)
2. WHEN the Webhook_Lambda receives an "expired" status event, IT SHALL update the envelope metadata record with the expired status
3. FOR declined and expired events, THE Webhook_Lambda SHALL write a notification record to the error S3 bucket containing the Envelope_ID, Salesforce_Ref, status, and timestamp for operational visibility

### Requirement 10: Error Handling and Observability

**User Story:** As a developer, I want comprehensive error logging throughout the pipeline, so that failures can be diagnosed quickly.

#### Acceptance Criteria

1. ALL pipeline errors SHALL be written as JSON error records to the error S3 bucket, containing: timestamp, stage, Envelope_ID (if known), Salesforce_Ref, error message, and context
2. THE Send_Envelope_Lambda SHALL log structured JSON to CloudWatch including the S3 key, Salesforce_Ref, and Envelope_ID at each processing stage
3. THE Webhook_Lambda SHALL log structured JSON to CloudWatch including the Envelope_ID, event type, and processing outcome
4. IF any Lambda invocation fails with an unhandled exception, IT SHALL write to the error bucket and not leave the system in an inconsistent state

### Requirement 11: Infrastructure and Security

**User Story:** As a system operator, I want credentials to be securely managed and infrastructure to be deployed via CDK, so that the system follows existing BRYT patterns.

#### Acceptance Criteria

1. THE system SHALL store DocuSign credentials (Integration_Key, RSA private key, impersonating user ID, account ID) in AWS Secrets Manager
2. THE system SHALL store Salesforce OAuth credentials in AWS Secrets Manager (following the existing pattern of `salesforceOauthKey` + `salesforceOauthSecret`)
3. THE system SHALL be deployed via CDK, following the existing BrytAdminPortal infrastructure patterns
4. THE Webhook_Lambda endpoint SHALL be publicly accessible (required for DocuSign_Connect) but SHALL validate all requests via HMAC verification
5. Lambda functions SHALL have least-privilege IAM permissions: only access to the specific DynamoDB table, S3 buckets, and Secrets Manager secrets they require
