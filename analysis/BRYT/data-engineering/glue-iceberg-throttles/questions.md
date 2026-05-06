# Questions — Glue & Iceberg Throttles

## Open

- What mitigation strategy should we pursue? (batching, staggered starts, retry, source compaction)
- How many files exist in each source table path? (more files = more listObjectsV2 calls per job)
- Could we reduce the number of files via CDC source compaction?
- Is there a way to disable parallel file listing in the bookmark mechanism?
- What changed in the recent deployment that introduced the LF credential errors?
- Why does phidex-project-unit-rate hit connection pool timeout during MERGE?

## Answered

- **What is the root cause of the S3 503 SlowDown?**
  → Glue Job Bookmark's `PartitionFilesListerUsingBookmark` does parallel `listObjectsV2`/`getObjectMetadata` on source S3 paths. With 55+ or 33+ jobs doing this simultaneously, the source buckets' rate limits are exceeded.

- **Which S3 buckets are being throttled?**
  → The **source** buckets: `rel-esg-prod-data-eng-cdc-centrestage` (55 jobs) and `rel-esg-prod-data-eng-cdc-phidex` (33 jobs). Confirmed via distinct S3 Request ID prefixes in CloudWatch logs. NOT the shared staging/Iceberg bucket.

- **Is the Lake Formation credential error the root cause?**
  → No. LF errors only appear post-deployment (after 05/05/2026). Separate issue.

- **Where in the script does the failure occur?**
  → Line 31 (pre-deployment): `getDynamicFrame` → `PartitionFilesListerUsingBookmark` → `listObjectsV2` on source bucket.

- **How many concurrent jobs are running?**
  → 94 jobs simultaneously in `run-titanium-jobs`.

- **What Glue worker type and DPU count are we using?**
  → 85 jobs: 2x G.1X. 5 jobs: 4x G.4X. 1 job: 5x G.8X.

- **Is there contention on specific Iceberg tables?**
  → No. The throttle is on the source read (bookmark listing), not the Iceberg write.

- **Is it the top-level prefix causing the issue?**
  → Not exactly. It's the combined request rate from many jobs doing parallel file listings against the same bucket. S3 partitions by prefix, and the burst pattern doesn't give S3 time to scale partitions.
