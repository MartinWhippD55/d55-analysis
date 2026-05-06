# Glue & Iceberg Throttle Investigation

## Summary

Investigating throttling issues in the `rel-esg-prod-data-eng--data-orchestration` Step Function, which orchestrates **94 parallel Glue jobs** writing to Iceberg tables on S3.

## Environment

- Account: `837413265725` (eu-west-2)
- Step Function: `rel-esg-prod-data-eng--data-orchestration`
- Sub-state-machine: `rel-esg-prod-data-eng--run-glue-job` (poll-based: start → wait 30s → check status → loop)
- Glue version: 5.0
- Job mode: SCRIPT
- All jobs share the same script template

## Orchestration Flow

1. `get-execution-id` — Pass state
2. `run-crawlers` — Parallel: 2 crawlers (centrestage + phidex)
3. `run-titanium-jobs` — Parallel: **94 Glue jobs** fired simultaneously
4. `run-glue-jobs` — Parallel: 8 master-record jobs (sequential dep: invoice-activity → allocated-payment-refund-activity)
5. `data-orchestration-failed` — Fail state (catch-all, no retry)

## Job Inventory (94 jobs)

All 94 jobs write to the **same warehouse bucket**: `s3://rel-esg-prod-data-eng-cdc-staging/`

### Source Distribution

| Source Database | S3 Source Bucket | Job Count | Staging Database |
|---|---|---|---|
| `rel-esg-prod-data-eng-centrestage-db` | `s3://rel-esg-prod-data-eng-cdc-centrestage/usmart_repo/` | ~55 | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` |
| `rel-esg-prod-data-eng-phidex-db` | `s3://rel-esg-prod-data-eng-cdc-phidex/dbo/` | ~33 | `rel_esg_prod_data_eng_phidex_cdc_staging_db` |
| `rel-esg-prod-data-eng-salesforce-db` | `s3://prod-salesforce-cdc/replication/` | 3 | `rel_esg_prod_data_eng_salesforce_cdc_staging_db` |
| `rel-esg-prod-data-eng-ensek-db` | `s3://master-prod-ensek-ignition-cdc/` | 2 | `rel_esg_prod_data_eng_ensek_cdc_staging_db` |
| `rel-esg-prod-data-eng-bryt-db` | `s3://rel-esg-prod-data-eng-cdc-bryt/` | 2 | `rel_esg_prod_data_eng_bryt_cdc_staging_db` |

### Worker Sizing

| Workers | Count | Jobs |
|---|---|---|
| 2x G.1X | 85 | Most jobs |
| 4x G.4X | 5 | phidex-billing-contract-mpan-rate, phidex-billing-invoice-error, phidex-project-document, phidex-project-unit-rate, salesforce-case |
| 5x G.8X | 1 | phidex-billing-contract-mpan-volume |

### Shared Script Template

All jobs use the same pattern:
1. `create_dynamic_frame.from_catalog()` with `job-bookmark-enable` — reads CDC data from source
2. Deduplicate by primary key using latest `dms_timestamp`
3. `MERGE INTO` Iceberg table in staging bucket

### Source Partition Structure

Source tables are partitioned by `year/month/day/hour`:
```
s3://rel-esg-prod-data-eng-cdc-centrestage/usmart_repo/titanium_documentdata/
├── 2025/
├── 2026/
│   ├── 01/ ... 05/
│   │   ├── 01/ ... 06/
│   │   │   ├── 07/ 08/ 10/ 13/   (hourly partitions)
```

Partition keys in Glue Catalog: `partition_0` (year), `partition_1` (month), `partition_2` (day), `partition_3` (hour).

## Root Cause (Confirmed)

**Glue Job Bookmark's `PartitionFilesListerUsingBookmark` overwhelms source S3 buckets with parallel `listObjectsV2` and `getObjectMetadata` requests.**

### Mechanism

1. Each job calls `getDynamicFrame` with job bookmarking enabled
2. Glue's bookmark system uses `PartitionFilesListerUsingBookmark` to enumerate all files in the source S3 path (to determine which are new since last bookmark)
3. This listing is done using **parallel** `listObjectsV2` + `getObjectMetadata` calls via Scala's `ForkJoinPool`
4. With 55 centrestage jobs (or 33 phidex jobs) all doing this simultaneously against the same source bucket, the combined request rate exceeds S3's per-prefix partition limits
5. S3 returns 503 SlowDown, Glue does not retry, and the job fails

### Evidence

Cross-checked with CloudWatch logs from both source buckets:

| Job Source | Bucket Being Throttled | S3 Request ID Prefixes | Jobs Hitting It |
|---|---|---|---|
| centrestage | `s3://rel-esg-prod-data-eng-cdc-centrestage` | `68P`, `Q1N`, `KCCW` | ~55 simultaneous |
| phidex | `s3://rel-esg-prod-data-eng-cdc-phidex` | `PDF`, `Q44` | ~33 simultaneous |

Both show identical stack traces:
```
PartitionFilesListerUsingBookmark.$anonfun$partitions$3(FileSystemBookmark.scala:404/419)
→ listObjectsV2 / getObjectMetadata
→ S3 503 SlowDown
```

The source buckets are being **independently** throttled — each bucket's own rate limit is exceeded by the thundering herd of bookmark file-listing operations from its respective group of jobs.

### Secondary Issue: phidex-project-unit-rate timeout

Separate from the S3 throttle: `phidex-project-unit-rate` (4x G.4X) hits "Timeout waiting for connection from pool" during its MERGE/SQL phase. Likely Iceberg catalog contention or under-resourcing for its data volume.

### Post-Deployment Issue (after 05/05/2026)

A recent deployment introduced a **separate** failure mode: `LFCredential fetch failed with status code: 400`. This is a Lake Formation credential vending issue unrelated to the original S3 throttle problem.

## Key Finding: Push-Down Predicates Reduce Bookmark Listing Scope

Per [AWS documentation](https://docs.aws.amazon.com/glue/latest/dg/monitor-continuations.html), the execution order is:

1. Push-down predicate filters partitions using Glue Catalog metadata (no S3 calls)
2. Bookmark then lists files **only within the filtered partitions**
3. Bookmark filters to files newer than the last bookmark timestamp
4. Data is read

This means a push-down predicate on the partition keys (e.g., last 7 days) would dramatically reduce the `listObjectsV2` scope — from listing all files across the entire table history to just ~168 hourly partitions.

The AWS docs explicitly state: "A bookmark will list all files under each input partition and do the filtering, so if there are too many files under a single partition the bookmark can run into driver OOM. Use the AWS Glue Amazon S3 file lister to avoid listing all files in memory at once."

## Status

🟢 Root cause confirmed, mitigation identified

## Next Steps

- [ ] Implement push-down predicate (last 7 days) on all 94 jobs to reduce bookmark listing scope
- [ ] Add retry with backoff to the `run-glue-job` sub-state-machine
- [ ] Consider batching jobs if push-down predicate alone isn't sufficient
- [ ] Investigate the post-deployment LF credential issue separately
- [ ] Address phidex-project-unit-rate timeout separately
