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

| Source Database | Job Count | Staging Database |
|---|---|---|
| `rel-esg-prod-data-eng-centrestage-db` | ~55 | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` |
| `rel-esg-prod-data-eng-phidex-db` | ~33 | `rel_esg_prod_data_eng_phidex_cdc_staging_db` |
| `rel-esg-prod-data-eng-salesforce-db` | 3 | `rel_esg_prod_data_eng_salesforce_cdc_staging_db` |
| `rel-esg-prod-data-eng-bryt-db` | 2 | `rel_esg_prod_data_eng_bryt_cdc_staging_db` |
| `rel-esg-prod-data-eng-ensek-db` | 2 | `rel_esg_prod_data_eng_ensek_cdc_staging_db` |

### Worker Sizing

| Workers | Count | Jobs |
|---|---|---|
| 2x G.1X | 85 | Most jobs |
| 4x G.4X | 5 | phidex-billing-contract-mpan-rate, phidex-billing-invoice-error, phidex-project-document, phidex-project-unit-rate, salesforce-case |
| 5x G.8X | 1 | phidex-billing-contract-mpan-volume |

### S3 Bucket Layout (write target)

```
s3://rel-esg-prod-data-eng-cdc-staging/
├── rel_esg_prod_data_eng_centrestage_cdc_staging_db.db/   (~55 Iceberg tables)
├── rel_esg_prod_data_eng_phidex_cdc_staging_db.db/        (~33 Iceberg tables)
├── rel_esg_prod_data_eng_salesforce_cdc_staging_db.db/    (3 Iceberg tables)
├── rel_esg_prod_data_eng_bryt_cdc_staging_db.db/          (2 Iceberg tables)
└── rel_esg_prod_data_eng_ensek_cdc_staging_db.db/         (2 Iceberg tables)
```

### Shared Script Template

All jobs use the same pattern:
1. `create_dynamic_frame.from_catalog()` — reads CDC data from source database (Lake Formation governed)
2. Deduplicate by primary key using latest `dms_timestamp`
3. `MERGE INTO` Iceberg table in staging bucket

## Findings — Pre-Deployment (before 05/05/2026)

Analysed 20 failed executions from Apr 30 – May 4 2026.

### Error Categories

| Error Type | Count | Percentage |
|---|---|---|
| S3 503 SlowDown (THROTTLING_ERROR) | 15 | 83% |
| Connection pool timeout (TIMEOUT_ERROR) | 3 | 17% |

**No Lake Formation credential errors** — those only appear post-deployment and are likely a separate issue introduced by the recent release.

### Error Details

- All S3 throttle errors occur at **line 31** (`getDynamicFrame`) — during the source read phase
- Error: `"Slow Down (Service: Amazon S3; Status Code: 503; Error Code: 503 Slow Down)"`
- Typical runtime before failure: 100-180 seconds
- The timeout errors affect `phidex-project-unit-rate` (4x G.4X) at line 65 (`o149.sql`) — "Timeout waiting for connection from pool"

### Most Affected Jobs (pre-deployment)

| Failures | Job |
|---|---|
| 3x | centerstage-titanium-invoice-detail |
| 3x | phidex-project-unit-rate |
| 2x | centerstage-titanium-invoice-crm-data |
| 2x | phidex-billing-invoice |
| 2x | centerstage-titanium-document-data |
| 2x | centerstage-titanium-site-billing-raw-data |
| 1x | 5 other jobs |

### Root Cause

**94 Glue jobs start simultaneously and collectively exceed S3 request rate limits.**

- The throttle occurs during the **read phase** (`getDynamicFrame` from source), not during writes
- S3 returns 503 SlowDown after ~100-180 seconds of sustained parallel reads
- The jobs that fail are essentially random — whichever ones are still reading when the rate limit is hit
- The `phidex-project-unit-rate` job has a separate issue: connection pool timeout during its SQL/MERGE phase, likely due to Iceberg catalog contention

## Status

🟡 In progress — root cause confirmed as S3 read-side throttling from parallel burst

## Next Steps

- [ ] Confirm source bucket locations for each of the 5 source databases (to understand read-side S3 layout)
- [ ] Determine whether the reads are all hitting the same S3 bucket/prefix
- [ ] Identify mitigation strategies (batching, staggered starts, retry logic)
- [ ] Separately investigate the post-deployment Lake Formation credential issue
