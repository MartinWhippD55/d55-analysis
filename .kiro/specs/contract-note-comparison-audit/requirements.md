# Requirements Document

## Introduction

This document specifies the requirements for Estimate 5 of the Bryt Energy Contract Note Rework project. The system provides an audit tool to detect whether contract note PDFs are being manually edited between rendering and sending to customers.

BRYT suspects that users may be modifying the rendered PDF before emailing it to customers, bypassing the controlled template system. This estimate builds a comparison pipeline that retrieves the original rendered PDF and the actually-sent PDF (from Outlook), compares them using AWS Bedrock, and reports any discrepancies.

This is a developer-operated analytical tool, not a production user-facing system. It processes batches of contract notes on an ad-hoc basis (e.g., monthly) and produces results queryable via Athena.

## Glossary

- **Rendered_PDF**: The original contract note PDF as produced by the current rendering pipeline, stored in S3
- **Sent_PDF**: The PDF that was actually attached to the email sent to the customer, retrieved from Outlook via Microsoft Graph API
- **Comparison_Run**: A batch execution of the comparison pipeline for a set of contract note references
- **Finding**: The result of comparing a single contract note's Rendered_PDF against its Sent_PDF (match, mismatch, or error)
- **Graph_API**: Microsoft Graph API used to search Outlook mailboxes and retrieve email attachments
- **Bedrock**: AWS Bedrock (Claude) used to analyse and describe differences between two PDFs

## Requirements

### Requirement 1: Batch Input

**User Story:** As a developer, I want to provide a list of contract note references for comparison, so that I can run the audit on a specific set of documents.

#### Acceptance Criteria

1. THE system SHALL accept a JSON payload containing a list of contract note references (offer references or document IDs) as input to the Step Function
2. THE system SHALL support batch sizes of up to 500 contract notes per run
3. THE system SHALL create a Comparison_Run record in S3 with a unique run ID, timestamp, and the input list

### Requirement 2: Original PDF Retrieval

**User Story:** As a developer, I want the system to fetch the original rendered PDF from S3, so that it can be compared against what was sent.

#### Acceptance Criteria

1. FOR each contract note reference in the batch, THE system SHALL locate the corresponding Rendered_PDF in the S3 output bucket
2. IF the Rendered_PDF cannot be found, THE system SHALL record the Finding as "error: original not found" and continue to the next record

### Requirement 3: Sent PDF Retrieval via Graph API

**User Story:** As a developer, I want the system to retrieve the PDF that was actually emailed to the customer, so that it can be compared against the rendered original.

#### Acceptance Criteria

1. THE system SHALL authenticate to Microsoft Graph API using OAuth client credentials stored in Secrets Manager
2. FOR each contract note reference, THE system SHALL search the configured mailbox for sent emails containing the contract note (by offer reference in subject or attachment filename)
3. THE system SHALL extract the PDF attachment from the matching email
4. IF no matching email is found, THE system SHALL record the Finding as "error: email not found" and continue
5. IF multiple matching emails are found, THE system SHALL use the most recent one

### Requirement 4: Bedrock Comparison

**User Story:** As a developer, I want the system to use Bedrock to compare the two PDFs and report whether they differ, so that we can identify tampered documents.

#### Acceptance Criteria

1. FOR each contract note where both PDFs were retrieved, THE system SHALL send both documents to Bedrock (Claude) with a comparison prompt
2. THE comparison prompt SHALL ask Bedrock to identify whether the documents are identical or different, and if different, describe the specific changes
3. THE system SHALL record the Bedrock response as the Finding (match/mismatch + description of differences)
4. IF Bedrock invocation fails, THE system SHALL record the Finding as "error: comparison failed" and continue

### Requirement 5: Results Storage and Querying

**User Story:** As a developer, I want comparison results stored in S3 and queryable via Athena, so that I can analyse findings efficiently.

#### Acceptance Criteria

1. THE system SHALL store each Finding as a JSON record in S3, partitioned by date (e.g., `s3://bucket/comparison-results/date={YYYY-MM-DD}/{runId}/{offerReference}.json`)
2. EACH Finding record SHALL contain: offer reference, run ID, timestamp, status (match/mismatch/error), original PDF S3 key, sent PDF S3 key (if found), Bedrock response (if applicable), and error message (if applicable)
3. THE system SHALL update the Finding record during processing as status changes (queued → processing → complete)
4. THE results SHALL be queryable via Athena without additional ETL

### Requirement 6: Status Tracking

**User Story:** As a developer, I want to monitor the progress of a comparison run, so that I know when it's complete and if there were errors.

#### Acceptance Criteria

1. THE system SHALL maintain a run-level summary record containing: total records, processed count, match count, mismatch count, error count
2. THE run summary SHALL be updated as each record completes
3. THE developer SHALL be able to check run progress by reading the summary record from S3

### Requirement 7: Prompt Iteration Support

**User Story:** As a developer, I want to easily iterate on the Bedrock comparison prompt, so that I can refine the output until BRYT is satisfied with the quality.

#### Acceptance Criteria

1. THE comparison prompt SHALL be stored as a configurable parameter (not hardcoded), allowing updates without redeployment
2. THE system SHALL store the prompt version used in each Finding record, enabling traceability across iterations
3. THE developer SHALL be able to re-run a subset of records with an updated prompt without reprocessing the entire batch
