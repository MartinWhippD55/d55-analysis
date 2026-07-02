# Contract Note - Open Questions

Questions that need answers from BRYT before or during implementation.

## Estimate 2 - DocuSign Integration

| # | Question | Context | Status |
|---|----------|---------|--------|
| 1 | Are there multi-party signing scenarios (BRYT rep, TPI) or is it always just the customer? | Current assumption: single signatory (customer only). If multi-party is needed, affects envelope routing and signing order. | 🔴 Open |
| 2 | Does BRYT have an existing DocuSign account? | No evidence in AWS (no secrets, no infrastructure). Assumption: starting from scratch — new DocuSign account, API credentials, and sandbox needed. | 🔴 Open |
| 3 | Is DocuSign's standard branded email acceptable, or does BRYT need full control over email delivery? | Assumption: DocuSign sends the signing email directly, with BRYT branding configured in the DocuSign account settings. If BRYT needs custom email via SES or similar, the architecture changes. | 🔴 Open |
| 4 | Is an Admin Portal UI needed for envelope status tracking (sent/viewed/signed/declined)? | Assumption: No UI in this phase. Backend stores envelope metadata in DynamoDB for developer debugging, but no user-facing status screen. Signed PDF landing in Salesforce is the only visible outcome. | 🔴 Open |
| 5 | What Salesforce object does `customersalesforceref` map to? (Account? Opportunity? Custom object?) | Needed at implementation time to know where the signed PDF gets attached. Doesn't affect the overall architecture. | 🔴 Open |
| 6 | Are voided envelopes, resend, and reminder functionality out of scope for this phase? | Assumption: out of scope. We handle completed, declined, and expired statuses only. No automated retry or manual resend capability. Can be added in a future phase if needed. | 🔴 Open |
