# BrytDataEngineering Dev & UAT Environment Strategy

## Problem Statement

Dev and UAT environments cannot be used to test all functionality in isolation. The client's expectation for support is that engineers have access to production data — "I have a problem with customer XYZ" requires being able to see that customer's data.

### Constraints

1. **Cost**: We cannot 1:1 replicate production in dev and UAT — it would be prohibitively expensive.
2. **Upstream system reliability**: We cannot maintain "proper" dev/UAT environments with their own independent data because:
   - UAT CentreStage and UAT Phidex are notoriously unreliable
   - They are not kept up to date with production code
   - They do not contain sensible test data
3. **UAT systems do exist** for Salesforce, CentreStage, and Phidex — they're just not reliable as data sources.

## Solution

### Data Replication: S3 Same-Region Replication (CentreStage/Phidex CDC)

Production CDC S3 buckets (CentreStage, Phidex) will be replicated into the dev and UAT account buckets using **S3 same-region replication rules**.

- S3 replication emits object-created events on the destination bucket, which the pipeline orchestration relies on to trigger downstream processing.
- Chosen over a scheduled Lambda (`aws s3 sync`) because the marginal cost difference (~$2/day) is not material compared to the operational overhead of maintaining another Lambda.

#### Initial Backfill

S3 live replication only applies to objects created after the replication rule is enabled — pre-existing objects are not replicated. The setup sequence is:

1. **One-off backfill** of existing objects into dev/UAT buckets (either `aws s3 sync` or S3 Batch Replication)
2. **Enable live replication** for ongoing new objects

Both `aws s3 sync` and S3 Batch Replication will emit object-created events on the destination bucket, so pipeline orchestration will trigger as expected during backfill.

### Data Replication: Salesforce (AppFlow)

1. **AppFlow** pulls Salesforce data into a bucket in a **4th (shared) account**
2. Object-created events from that bucket are **forwarded to dev, UAT, and prod**
3. All three environments already receive the same Salesforce data — no additional replication needed for this source

This means Salesforce data does not need S3 replication rules — it's already fanned out to all environments via event forwarding from the shared AppFlow account.

### API Integration: Point at UAT Instances

Dev and UAT environments will point at the UAT instances of downstream APIs:

- **UAT CentreStage (Titanium API)** — critical for detecting API contract changes that would break features without warning
- **UAT Salesforce** — for any Salesforce API calls
- **UAT Phidex** — for Phidex API interactions

This gives us prod-like data flowing through the pipelines while exercising real API contracts against non-production systems.

### Master Record Jobs: external_reference Fallback

The Glue jobs in BrytDataEngineering (particularly the master record jobs) already handle this hybrid scenario gracefully. They use `external_reference` as a fallback when there is no `bryt_number` match. This means:

- Jobs won't fail when processing prod data against UAT systems where account numbers may not align
- The same pattern applies to Salesforce — we can run off prod data but point at Salesforce UAT for API calls, and the external_reference fallback ensures matching still works

### Meter Read Submission to Titanium API (Confirmed by Simon F)

The UAT path for meter reads is: **Salesforce UAT → CentreStage PROD → Phidex PROD**

#### How it works

1. **Account mapping**: The bryt number of the PROD account is mapped into the corresponding Salesforce UAT `test_external_account_id__c` field. This functionality already exists.
2. **Meter read submission**: Bryt determines a master list of account MPAN(s) for testing. For these accounts, when not running in PROD, the customer and supply IDs from the PROD data are replaced with the relevant UAT ones so the submission is correctly sent to the UAT Titanium API.
3. **Visibility**: Submitted reads will be viewable in the ESG UAT Titanium portal, but will not make it back into the Customer/TPI portals.

#### Document submission from portals to Salesforce

Two options:
- **Per-account approach**: Use the same meter read mapping approach (replace IDs for known test accounts)
- **Automatic for all accounts**: Modify the master account records to also contain the originating account bryt number and use that when submitting to Salesforce

#### Operational considerations

- Bryt must maintain which UAT Salesforce accounts have the relevant `test_external_account_id__c` values populated
- Adding new test accounts may take over an hour to appear (they need to be processed by AppFlow and then data orchestration)
- For TPIs: a LOA shell(s) would need to be set up in PROD specifically for testing purposes

## Cost Estimate

Post-optimisation (weekly crawl on Sundays), the production S3 buckets cost ~$3-4/day.

S3 same-region replication into two additional accounts adds approximately:

| Component | Estimated Additional Cost |
|-----------|--------------------------|
| Storage (2x replica) | ~$3-4/day |
| Replication requests | ~$1-2/day |
| Replication time ($0.015/GB) | Minimal |
| Data transfer (same-region) | $0 |
| **Total additional** | **~$5-7/day** |

## Summary of Approach

| Concern | Approach |
|---------|----------|
| Data freshness | S3 replication from prod CDC buckets |
| API testing | Point at UAT CentreStage, Salesforce, Phidex |
| Account matching | external_reference fallback in Glue jobs |
| Meter read testing | ID replacement for known test MPANs → UAT Titanium (confirmed Simon F) |
| Event triggering | S3 replication emits object-created events natively |
| Cost | ~$5-7/day additional, accepted as reasonable |

## Open Actions

- [ ] Bryt to determine master list of account MPAN(s) for meter read testing
- [ ] Decide on document submission approach: per-account mapping vs. modifying master account records with originating bryt number
- [ ] Set up LOA shell(s) in PROD for TPI testing
- [ ] Identify and populate `test_external_account_id__c` on relevant UAT Salesforce accounts
