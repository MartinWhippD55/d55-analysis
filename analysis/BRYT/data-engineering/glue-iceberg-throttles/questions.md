# Questions — Glue & Iceberg Throttles

## Open

- What are the actual S3 bucket locations for each of the 5 source databases? (read-side)
- Are all source reads hitting the same S3 bucket or different buckets?
- Is there any retry/backoff logic in the scripts or the step function?
- Has the number of parallel jobs grown recently (was it always 94)?
- Could the jobs be batched into smaller parallel groups to reduce the burst?
- What is the S3 request rate at the time of failure? (CloudWatch metrics)
- What changed in the recent deployment that introduced the LF credential errors? (separate issue)

## Answered

- **What is the primary error pre-deployment?**
  → S3 503 SlowDown (83% of failures). Pure request rate throttling during the read phase.

- **Is the Lake Formation credential error the root cause?**
  → No. LF errors only appear post-deployment (after 05/05/2026). They are a separate issue introduced by a recent release.

- **Where in the script does the failure occur?**
  → Line 31 (pre-deployment) / Line 48 (post-deployment) — both are `getDynamicFrame`, the source read. The line number changed because the script template was updated in the deployment.

- **How many concurrent jobs are running?**
  → 94 jobs run simultaneously in the `run-titanium-jobs` stage.

- **What Glue worker type and DPU count are we using?**
  → 85 jobs: 2x G.1X. 5 jobs: 4x G.4X. 1 job: 5x G.8X.

- **What does the S3 key prefix structure look like (write side)?**
  → All 94 jobs write to `s3://rel-esg-prod-data-eng-cdc-staging/` under 5 database prefixes.

- **Is there contention on specific Iceberg tables?**
  → No — each job writes to its own dedicated Iceberg table. The contention is at the S3 request rate level during reads.

- **What about the phidex-project-unit-rate timeout?**
  → Separate issue: connection pool timeout during MERGE/SQL phase. Likely Iceberg catalog contention or the job being under-resourced for its data volume.
