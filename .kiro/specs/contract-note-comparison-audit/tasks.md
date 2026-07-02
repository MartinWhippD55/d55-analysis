# Implementation Plan: Contract Note Comparison Audit

## Overview

Build a developer-operated Step Function pipeline that compares original rendered contract note PDFs against the versions actually sent to customers (retrieved from Outlook), using AWS Bedrock to identify discrepancies. Results are stored in S3 and queryable via Athena.

## Tasks

- [ ] 1. Infrastructure
  - [ ] 1.1 Define CDK infrastructure
    - Create Step Function (`CompareContractNotes`) with Map state
    - Create Lambda functions (init, fetch-original, fetch-sent, invoke-bedrock, store-finding, update-summary)
    - Create S3 bucket for comparison results (with lifecycle policy for cost management)
    - Create Secrets Manager secret for Graph API credentials
    - Create SSM Parameter for comparison prompt (versioned)
    - Configure IAM roles (Bedrock access, S3 access, Secrets Manager access, Graph API outbound HTTPS)
    - _Requirements: 1.1, 5.1, 7.1_

  - [ ] 1.2 Configure Athena for results querying
    - Create Glue table definition over the S3 results prefix (JSON SerDe, date partitioned)
    - Verify Athena can query findings by status, date, run ID
    - _Requirements: 5.4_

- [ ] 2. Original PDF retrieval
  - [ ] 2.1 Implement `comparison-fetch-original` Lambda
    - Look up original rendered PDF in S3 by offer reference / document ID
    - Handle: not found → return error status
    - Store PDF reference (S3 key) for comparison step
    - _Requirements: 2.1, 2.2_

- [ ] 3. Sent PDF retrieval (Graph API)
  - [ ] 3.1 Implement Graph API OAuth client
    - Read credentials from Secrets Manager
    - Obtain access token via client credentials flow
    - Cache token within Lambda execution
    - _Requirements: 3.1_

  - [ ] 3.2 Implement mailbox search
    - Search configured mailbox for sent messages matching the offer reference
    - Filter by subject line and/or attachment filename
    - Handle: not found, multiple matches (use most recent)
    - _Requirements: 3.2, 3.4, 3.5_

  - [ ] 3.3 Implement attachment extraction
    - Download PDF attachment from the matched email
    - Store temporarily in S3 (working bucket) for Bedrock comparison
    - Handle: no PDF attachment on email
    - _Requirements: 3.3_

- [ ] 4. Bedrock comparison
  - [ ] 4.1 Implement `comparison-invoke-bedrock` Lambda
    - Load prompt from SSM Parameter Store
    - Prepare inputs (PDF content — base64 or extracted text depending on prompt strategy)
    - Invoke Bedrock (Claude) with both documents + prompt
    - Parse structured JSON response
    - Handle: invocation failure (retry once), unparseable response (store raw)
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [ ] 4.2 Create initial comparison prompt
    - Store in SSM Parameter Store as version v1
    - Focus on: identical yes/no, list of differences with location and severity
    - _Requirements: 4.2, 7.1_

- [ ] 5. Results storage and run management
  - [ ] 5.1 Implement `comparison-init` Lambda
    - Validate input payload
    - Create run summary record in S3
    - Return structured input for Map state
    - _Requirements: 1.1, 1.3, 6.1_

  - [ ] 5.2 Implement `comparison-store-finding` Lambda
    - Write finding JSON to S3 at date-partitioned path
    - Include: status, both PDF keys, Bedrock response, prompt version, timestamps
    - Update record during processing (queued → processing → complete)
    - _Requirements: 5.1, 5.2, 5.3, 7.2_

  - [ ] 5.3 Implement `comparison-update-summary` Lambda
    - Increment match/mismatch/error counters
    - Update processed count
    - Write completion timestamp when all records processed
    - _Requirements: 6.1, 6.2_

- [ ] 6. Checkpoint - Pipeline functional
  - Run against a small batch (5-10 records) end-to-end.
  - Verify: findings appear in S3, Athena queries work, Bedrock produces structured output.

- [ ] 7. Prompt iteration (budget: 3-5 cycles)
  - [ ] 7.1 Iteration cycle 1: Run batch, review Bedrock output quality
    - Identify false positives/negatives
    - Refine prompt (store as v2)
    - Re-run subset
    - _Requirements: 7.1, 7.3_

  - [ ] 7.2 Iteration cycle 2: Refine based on BRYT feedback
    - Share initial results with BRYT
    - Adjust prompt based on what they consider meaningful vs noise
    - _Requirements: 7.1_

  - [ ] 7.3 Iteration cycle 3+: Final refinement
    - Aim for acceptable signal-to-noise ratio
    - Document final prompt and reasoning
    - _Requirements: 7.1_

- [ ] 8. Results analysis and delivery
  - [ ] 8.1 Create Athena queries for common analysis patterns
    - All mismatches for a run
    - Mismatches grouped by severity
    - Error breakdown (not found vs comparison failure)
    - Summary statistics per run
    - _Requirements: 5.4_

  - [ ] 8.2 Produce first spreadsheet report for BRYT
    - Run full batch on BRYT-provided list
    - Export results via Athena → CSV
    - Format as spreadsheet with summary + detail tabs
    - _Requirements: 5.4_

- [ ] 9. Final checkpoint
  - Pipeline operational, prompt stable, first report delivered.

## Notes

- This is a developer-operated tool, not a production system. No UI.
- Graph API access is the critical dependency — requires BRYT's M365 admin to grant permissions
- Bedrock comparison quality depends on prompt engineering — budget iteration time
- Step Function max concurrency of 5 avoids Graph API throttling
- Results S3 bucket should have lifecycle policy (e.g., expire after 12 months)
- Consider cost: Bedrock invocations + Graph API calls + S3 storage. For 500 records/month this should be minimal.
- The prompt is the most valuable artefact — document iterations and reasoning
