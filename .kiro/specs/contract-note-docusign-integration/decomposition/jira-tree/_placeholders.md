---
project: SQP
set_label: s2s-contract-note-docusign-integration
key_map:
  contract-note-docusign-integration: SQP-5045
  US-01: SQP-5046
  US-01-1: SQP-5057
  US-01-2: SQP-5054
  US-01-3: SQP-5055
  US-01-4: SQP-5056
  US-02: SQP-5047
  US-02-1: SQP-5058
  US-02-2: SQP-5059
  US-02-3: SQP-5060
  US-02-4: SQP-5061
  US-03: SQP-5048
  US-03-1: SQP-5062
  US-03-2: SQP-5063
  US-03-3: SQP-5064
  US-03-4: SQP-5065
  US-03-5: SQP-5066
  US-04: SQP-5049
  US-04-1: SQP-5067
  US-04-2: SQP-5068
  US-05: SQP-5050
  US-05-1: SQP-5069
  US-05-2: SQP-5070
  US-05-3: SQP-5071
  US-06: SQP-5051
  US-06-1: SQP-5072
  US-06-2: SQP-5073
  US-06-3: SQP-5074
  US-06-4: SQP-5075
  US-07: SQP-5052
  US-07-1: SQP-5076
  US-08: SQP-5053
  US-08-1: SQP-5077
  US-08-2: SQP-5078
---

# Placeholder key map

Correlates each tree key to the live Jira issue it was pushed to. jira-push uses this to rewrite cross-references (US-01, US-04-2, …) in issue descriptions to real Jira keys before the update pass. Regenerated from live Jira on each run; safe to delete once descriptions are finalised.

| Tree key | Jira | Type | Summary |
|----------|------|------|---------|
| contract-note-docusign-integration | SQP-5045 | Epic | contract-note-docusign-integration (delivery) |
| US-01 | SQP-5046 | Story | Foundation: DocuSign pipeline infra, shared types & utilities |
| US-01-1 | SQP-5057 | Sub-task | DocuSignPipeline CDK construct: envelopes table + SalesforceRefIndex GSI, signed-contract-notes bucket, DocuSign/Salesforce secret placeholders, webhook API route surface, least-privilege IAM scaffolding, CfnOutputs; reuse Estimate 1's error bucket (docusign/ prefix) |
| US-01-2 | SQP-5054 | Sub-task | Shared TypeScript interfaces and types (EnvelopeRecord, EnvelopeStatus, ContractMetadata, SalesforceContact, CreateEnvelopeRequest, DocuSignWebhookEvent, error-record type) in shared-lib/src |
| US-01-3 | SQP-5055 | Sub-task | Retry utility with exponential backoff (1s/2s/4s + jitter), configurable per-call |
| US-01-4 | SQP-5056 | Sub-task | Error record writer utility (JSON records to the reused error bucket) |
| US-02 | SQP-5047 | Story | Salesforce integration client (greenfield) |
| US-02-1 | SQP-5058 | Sub-task | Salesforce OAuth client: read credentials from Secrets Manager, obtain/cache access token (client credentials flow), refresh before expiry |
| US-02-2 | SQP-5059 | Sub-task | Customer contact lookup by customersalesforceref: return name + email; throw on not-found, missing email, or network error |
| US-02-3 | SQP-5060 | Sub-task | Signed document upload: ContentVersion + ContentDocumentLink, filename Contract-Note-{offerReference}-Signed-{date}.pdf, using the retry utility |
| US-02-4 | SQP-5061 | Sub-task | Property tests for the Salesforce client (Property 2: lookup correctness; Property 3: missing contact halts) |
| US-03 | SQP-5048 | Story | DocuSign integration client |
| US-03-1 | SQP-5062 | Sub-task | DocuSign JWT authentication: build assertion (integration key, impersonated user, scope), exchange for access token, cache + refresh before expiry |
| US-03-2 | SQP-5063 | Sub-task | Envelope creation: document (base64 PDF), signer recipient, signing tab, per-envelope Connect webhook, status 'sent'; return envelope ID |
| US-03-3 | SQP-5064 | Sub-task | Signed document download (combined) by envelope ID, using the retry utility |
| US-03-4 | SQP-5065 | Sub-task | HMAC webhook signature validation (X-DocuSign-Signature-1, HMAC-SHA256) |
| US-03-5 | SQP-5066 | Sub-task | Property tests for the DocuSign client (Property 4: token management; Property 5: envelope contents; Property 6: HMAC validation) |
| US-04 | SQP-5049 | Story | Envelope metadata service |
| US-04-1 | SQP-5067 | Sub-task | DynamoDB metadata operations: create record on send, get by envelope ID, update status on webhook events, query by Salesforce_Ref via GSI |
| US-04-2 | SQP-5068 | Sub-task | Property tests for the metadata service (Property 8: record reflects current status) |
| US-05 | SQP-5050 | Story | Send Envelope Lambda |
| US-05-1 | SQP-5069 | Sub-task | SendEnvelope task handler + contract-metadata extraction from the state payload; validate required fields (halt if missing); idempotency check by contract note S3 key |
| US-05-2 | SQP-5070 | Sub-task | Send-envelope orchestration: Salesforce lookup -> DocuSign auth -> create envelope -> store metadata; on failure write error record + structured CloudWatch log |
| US-05-3 | SQP-5071 | Sub-task | Property tests for the send flow (Property 1: trigger-to-envelope correlation / idempotency) |
| US-06 | SQP-5051 | Story | Webhook Lambda (completion + declined/expired) |
| US-06-1 | SQP-5072 | Sub-task | Webhook request handler: HMAC validation (401 if invalid), parse event, route by status, return 200 to acknowledge |
| US-06-2 | SQP-5073 | Sub-task | Completion flow: download signed PDF (retries) -> store in S3 -> upload to Salesforce (retries) -> update metadata; on final failure write to error bucket |
| US-06-3 | SQP-5074 | Sub-task | Declined/expired flow: update metadata with status + reason, write notification record to the error bucket |
| US-06-4 | SQP-5075 | Sub-task | Property tests for the webhook handler (Property 7: completed -> S3 + Salesforce; Property 9: declined/expired notification; Property 10: no partial state) |
| US-07 | SQP-5052 | Story | Estimate 1 metadata surfacing (Requirement 12) |
| US-07-1 | SQP-5076 | Sub-task | Extend render/parse-input.ts buildContractSummary to extract customersalesforceref, offerReference and customerName; thread Contract_Metadata through the state payload from parseInput to write-output and on to the SendEnvelope task. Coordinate with Estimate 1 owner (Jabez) |
| US-08 | SQP-5053 | Story | Integration wiring & deployment |
| US-08-1 | SQP-5077 | Sub-task | Wire DocuSignPipeline into ContractNoteStack; append the SendEnvelope LambdaInvoke task after WriteOutput with its OWN DocuSign-specific catch (not render handleFailure) and its own retry/timeout; connect the API Gateway webhook route to the Webhook Lambda; set env vars (table, buckets, webhook URL, secret ARNs); finalise least-privilege IAM |
| US-08-2 | SQP-5078 | Sub-task | Integration tests for the full pipeline flow (SendEnvelope -> DynamoDB record; valid webhook -> signed PDF in S3; invalid HMAC -> 401; declined -> notification in error bucket) |
