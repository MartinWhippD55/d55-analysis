# Dev & UAT Environment Strategy — Review Questions

## 1. Data Sensitivity / PII

Prod customer data is being replicated into dev/UAT accounts. Is there any PII masking or anonymisation requirement, or is this accepted because all accounts sit within the same org's AWS boundary with equivalent access controls?

### Recommendation: Accept unmasked, document as risk acceptance

Adding a masking layer (Glue job, S3 Object Lambda, tokenisation) introduces:

- **Additional cost** — another job to run, monitor, and maintain per source
- **Schema coupling** — masking logic must know which fields to hit across every CDC table, and must be updated as new sources are onboarded
- **Bug risk** — if masking corrupts a field, drops a record, or changes a data type, it introduces a discrepancy between prod and dev/UAT — defeating the purpose of the environment
- **Debugging the debugger** — "is this a real issue or did masking break something?"

Given the whole point of this strategy is prod-faithful data for support/debugging, the pragmatic position is:

1. Accept unmasked data in dev/UAT with equivalent access controls (same team, same SSO, same account boundaries)
2. Document as an explicit risk acceptance rather than a gap
3. Revisit if the access model changes (e.g., third-party contractor gets dev access, broader IAM policies)

**Question for client**: Do dev/UAT access controls provide equivalent protection to prod? If yes, is access control alone sufficient for the data classification policy, or is masking mandated in non-prod regardless of access controls?

## 2. Replication Lag

S3 same-region replication is eventually consistent (typically seconds to minutes, but can lag under high object throughput). Is there a support scenario where an engineer says "I just saw this in prod" and it hasn't landed in dev/UAT yet?

If so, worth noting the expected lag window and whether there's a way to force-sync a specific prefix on demand.

## 3. Backfill Blast Radius & Orchestration Toggle

The initial backfill (`aws s3 sync` or S3 Batch Replication) will emit a large burst of object-created events. The doc states orchestration "will trigger as expected during backfill" — implying it runs hot.

Questions:

- Will the downstream orchestration (Step Functions / EventBridge / Glue triggers) handle that burst gracefully, or will it hit concurrency/throttle limits?
- What's the estimated object count for the initial backfill?
- **Should orchestration be toggled off during backfill?** Two sub-options:
  - **Toggle off, backfill, toggle on**: Cleaner, avoids stampede. But backfilled data remains unprocessed unless a manual catchup run is triggered afterwards.
  - **Leave on, let it run hot**: Simpler operationally, but relies on idempotency and sufficient concurrency headroom.
- Does dev/UAT actually need fully processed data from day one, or is having the raw CDC files in S3 sufficient for support/debugging? If the latter, toggling off orchestration during backfill is the obvious choice — no catchup needed.

## 4. Meter Read UAT Path — Prod Side Effects

The UAT path for meter reads is: Salesforce UAT → CentreStage **PROD** → Phidex **PROD**.

This means UAT testing hits production CentreStage and Phidex. Is this safe? A one-liner explaining why would help (e.g., "read-only operations" or "writes are isolated to test accounts that don't affect real customers").

## 5. Rollback / Kill Switch

If replication causes unexpected cost spikes or pipeline issues:

- Disabling the replication rule stops new objects — but what about data already replicated?
- Is there a lifecycle rule or retention policy on the dev/UAT buckets to auto-expire replicated data?
- Should there be a runbook for "turn off dev/UAT environment" that covers both replication and orchestration?

## 6. Monitoring & Alerting

No mention of how we'd know if replication falls behind or fails silently. Consider:

- S3 replication metrics (ReplicationLatency, OperationsFailedReplication) → CloudWatch alarm
- Pipeline health checks in dev/UAT — if no new objects arrive for N hours, alert

## 7. Document Submission Decision

The two options (per-account mapping vs. modifying master records with originating bryt number) have different maintenance burdens:

- Per-account is simpler but requires manual upkeep of the test account list
- Modifying master records is more automated but changes the data model

Is there a preference, or does this need a spike to assess effort?

## 8. Test Account Onboarding Latency

> Adding new test accounts may take over an hour to appear

For a support scenario where someone needs to debug a specific customer, is an hour acceptable? Or does this imply that a pre-populated set of "always available" test accounts is the practical path?
