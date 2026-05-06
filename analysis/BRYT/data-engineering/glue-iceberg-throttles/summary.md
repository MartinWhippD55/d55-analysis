# Glue Iceberg Throttle — Summary

## Problem

The `rel-esg-prod-data-eng--data-orchestration` Step Function fails on almost every run. It orchestrates 94 Glue jobs in parallel, and 1-2 jobs fail each time with S3 503 SlowDown errors, causing the entire orchestration to fail (no retry logic).

## Root Cause

**Glue Job Bookmarks overwhelm the source S3 buckets with parallel file-listing requests.**

When `getDynamicFrame` is called with `job-bookmark-enable`, Glue's internal `PartitionFilesListerUsingBookmark` enumerates all files in the source S3 path using parallel `listObjectsV2` and `getObjectMetadata` calls. With 55 centrestage jobs and 33 phidex jobs all starting simultaneously, the combined request rate exceeds S3's per-prefix rate limits on the source buckets.

**Throttled buckets:**
- `s3://rel-esg-prod-data-eng-cdc-centrestage/usmart_repo/` — 55 jobs hitting it at once
- `s3://rel-esg-prod-data-eng-cdc-phidex/dbo/` — 33 jobs hitting it at once

## How to Verify

1. Find a failed orchestration execution:
```bash
aws stepfunctions list-executions \
  --state-machine-arn "arn:aws:states:eu-west-2:837413265725:stateMachine:rel-esg-prod-data-eng--data-orchestration" \
  --status-filter FAILED --max-items 5 --profile bryt-inv-prod
```

2. Get the failed sub-execution from the history (look for `TaskFailed` events):
```bash
aws stepfunctions get-execution-history \
  --execution-arn "<orchestration-execution-arn>" \
  --query "events[?type=='TaskFailed'].taskFailedEventDetails.cause" \
  --profile bryt-inv-prod
```

3. Extract the Glue job run ID from the sub-execution's `FailStateEntered` event:
```bash
aws stepfunctions get-execution-history \
  --execution-arn "<sub-execution-arn>" \
  --query "events[?type=='FailStateEntered'].stateEnteredEventDetails.input" \
  --output text --profile bryt-inv-prod
```

4. Check the CloudWatch error logs for that job run:
```bash
aws logs filter-log-events \
  --log-group-name "/aws-glue/jobs/error" \
  --log-stream-names "<job-run-id>" \
  --filter-pattern "SlowDown" \
  --profile bryt-inv-prod
```

5. Confirm the stack trace shows:
```
PartitionFilesListerUsingBookmark.$anonfun$partitions$3(FileSystemBookmark.scala:404)
→ listObjectsV2 / getObjectMetadata
→ AmazonS3Exception: Please reduce your request rate (503 SlowDown)
```

## Mitigation Options

| # | Option | Effort | Impact | Risk |
|---|---|---|---|---|
| 1 | **Batch jobs into groups of 15-20** with waits between batches in the Step Function | Medium | High | Low |
| 2 | **Add retry with backoff** to the `run-glue-job` sub-state-machine (e.g., 2 retries, 60s/120s) | Low | Medium | Low |
| 3 | **Compact CDC source files** to reduce the number of files the bookmark needs to list | Medium-High | High | Medium |
| 4 | **Replace bookmarks with timestamp filtering** — read all data, filter by `dms_timestamp > last_run` | Medium | High | Medium |

**Recommended approach:** Implement options 1 + 2 together for immediate relief, then pursue option 3 for long-term improvement.

## Notes

- A recent deployment (around 05/05/2026) introduced a **separate** issue: Lake Formation credential failures (`LFCredential fetch failed with status code: 400`). This is unrelated to the S3 throttle and should be investigated independently.
- `phidex-project-unit-rate` has an additional issue: connection pool timeout during MERGE, likely due to under-resourcing for its data volume.
