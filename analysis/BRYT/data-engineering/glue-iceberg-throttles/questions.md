# Questions — Glue & Iceberg Throttles

## Open

- What are the actual S3 bucket locations for each of the 5 source databases?
- Is there any retry/backoff logic in the scripts or the step function?
- Could the jobs be batched into smaller parallel groups to reduce thundering herd?
- Is Lake Formation configured with per-table or per-database grants (affects credential caching)?
- Are there any S3 request metrics (CloudWatch) showing the spike pattern?
- Has the number of parallel jobs grown recently (was it always 94)?
- What is the Lake Formation API throttle limit for GetTemporaryGluePartitionCredentials?
- Could the source reads be split across different S3 prefixes to distribute load?

## Answered

- **Which specific Glue jobs are being throttled?**
  → 26 unique jobs have failed across 30 executions. It's not specific jobs — it's random based on which ones lose the race. Top offenders: titanium-document-data, titanium-invoice-crm-data, phidex-project-unit-rate, titanium-invoice-detail (3x each).

- **Are the throttles at the Glue service level (concurrency) or S3 request level?**
  → Three distinct failure modes: (1) Lake Formation credential API saturation (most common), (2) S3 503 SlowDown rate limiting, (3) connection pool timeout. Not Glue concurrency.

- **How many concurrent Iceberg commits are happening across jobs?**
  → Up to 94 jobs run simultaneously in the `run-titanium-jobs` stage.

- **Is there contention on specific Iceberg tables (hot tables)?**
  → No — each job writes to its own dedicated Iceberg table. The contention is at the shared infrastructure level (LF API, S3 bucket, Glue Catalog).

- **What does the S3 key prefix structure look like?**
  → All 94 jobs write to `s3://rel-esg-prod-data-eng-cdc-staging/` under 5 database prefixes. Reads come from 5 different source databases (likely separate buckets).

- **What Glue worker type and DPU count are we using?**
  → 85 jobs: 2x G.1X. 5 jobs: 4x G.4X. 1 job: 5x G.8X.

- **Are we running Iceberg compaction/maintenance, and could that be competing with writes?**
  → Not observed in the step function. The MERGE operations themselves are the only Iceberg writes visible.
