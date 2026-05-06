# Questions — Glue & Iceberg Throttles

## Open

- What S3 bucket/prefix structure are the jobs reading from and writing to?
- Are all 65 jobs hitting the same S3 prefix (causing per-prefix rate limit saturation)?
- What does the shared Glue script template look like (line 48 = getDynamicFrame)?
- Is there any retry/backoff logic in the scripts or the step function?
- Could the jobs be batched into smaller parallel groups to reduce thundering herd?
- Is Lake Formation configured with per-table or per-database grants (affects credential caching)?
- Are there any S3 request metrics (CloudWatch) showing the spike pattern?
- Has the number of parallel jobs grown recently (was it always 65)?

## Answered

- **Which specific Glue jobs are being throttled?**
  → 26 unique jobs have failed across 30 executions. It's not specific jobs — it's random based on which ones lose the race. Top offenders: titanium-document-data, titanium-invoice-crm-data, phidex-project-unit-rate, titanium-invoice-detail.

- **Are the throttles at the Glue service level (concurrency) or S3 request level?**
  → Three distinct failure modes: (1) Lake Formation credential API saturation (most common), (2) S3 503 SlowDown rate limiting, (3) connection pool timeout. Not Glue concurrency.

- **How many concurrent Iceberg commits are happening across jobs?**
  → Up to 65 jobs run simultaneously in the `run-titanium-jobs` stage.

- **What Glue worker type and DPU count are we using?**
  → Most jobs: 2x G.1X (2 DPU). Exception: phidex-project-unit-rate uses 4x G.4X (16 DPU).
