# Glue & Iceberg Throttle Investigation

## Summary

Investigating throttling and credential failures in the `rel-esg-prod-data-eng--data-orchestration` Step Function, which orchestrates **94 parallel Glue jobs** writing to Iceberg tables on S3.

## Environment

- Account: `837413265725` (eu-west-2)
- Step Function: `rel-esg-prod-data-eng--data-orchestration`
- Sub-state-machine: `rel-esg-prod-data-eng--run-glue-job` (poll-based: start → wait 30s → check status → loop)
- Glue version: 5.0
- Job mode: SCRIPT
- All jobs share the same script template (fail at line 48 calling `getDynamicFrame`)

## Orchestration Flow

1. `get-execution-id` — Pass state
2. `run-crawlers` — Parallel: 2 crawlers (centrestage + phidex)
3. `run-titanium-jobs` — Parallel: **94 Glue jobs** fired simultaneously
4. `run-glue-jobs` — Parallel: 8 master-record jobs (sequential dep: invoice-activity → allocated-payment-refund-activity)
5. `data-orchestration-failed` — Fail state (catch-all, no retry)

## Findings (30 failed executions, Apr 30 – May 6 2026)

### Error Categories

| Error Type | Frequency | Category | Detail |
|---|---|---|---|
| Lake Formation credential failure | Most common | `UNCLASSIFIED_ERROR` | "LFCredential fetch failed with status code: 400" |
| S3 request rate throttle | 2-3 explicit | `THROTTLING_ERROR` | S3 503 SlowDown during `getDynamicFrame` |
| Connection pool timeout | 1-3 | `TIMEOUT_ERROR` | "Timeout waiting for connection from pool" (Iceberg catalog contention) |

### Failure Distribution

- **26 unique jobs** have failed across 30 executions
- Failures are essentially random — whichever job loses the race for credentials or S3 capacity
- Top offenders: titanium-document-data (3x), titanium-invoice-crm-data (3x), phidex-project-unit-rate (3x), titanium-invoice-detail (3x)

### Job Inventory (94 jobs)

All 94 jobs write to the **same warehouse bucket**: `s3://rel-esg-prod-data-eng-cdc-staging/`

#### Source Distribution

| Source Database | Job Count | Staging Database |
|---|---|---|
| `rel-esg-prod-data-eng-centrestage-db` | ~55 | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` |
| `rel-esg-prod-data-eng-phidex-db` | ~33 | `rel_esg_prod_data_eng_phidex_cdc_staging_db` |
| `rel-esg-prod-data-eng-salesforce-db` | 3 | `rel_esg_prod_data_eng_salesforce_cdc_staging_db` |
| `rel-esg-prod-data-eng-bryt-db` | 2 | `rel_esg_prod_data_eng_bryt_cdc_staging_db` |
| `rel-esg-prod-data-eng-ensek-db` | 2 | `rel_esg_prod_data_eng_ensek_cdc_staging_db` |

#### Worker Sizing

| Workers | Count | Jobs |
|---|---|---|
| 2x G.1X | 85 | Most jobs |
| 4x G.4X | 5 | phidex-billing-contract-mpan-rate, phidex-billing-invoice-error, phidex-project-document, phidex-project-unit-rate, salesforce-case |
| 5x G.8X | 1 | phidex-billing-contract-mpan-volume |

#### S3 Bucket Layout (write target)

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

The failure point (line 48) is the `getDynamicFrame` call, which requires Lake Formation credentials to access the source data.

## Root Cause Analysis

The core problem is **94 Glue jobs starting simultaneously**, causing a thundering herd:

1. **Lake Formation API saturation** (most frequent) — All 94 jobs request temporary credentials at the same moment. LF's credential vending API throttles, returning 400 errors.

2. **S3 503 SlowDown** — Jobs that get past credential fetch collectively exceed S3's per-prefix rate limits (3,500 PUT/5,500 GET per second per prefix). All writes target the same bucket.

3. **Connection pool exhaustion** — Larger jobs (4x G.4X) timeout waiting for connections, likely due to Iceberg metadata/Glue Catalog contention from the parallel blast.

## Status

🟡 In progress — root cause identified, job inventory complete

## Next Steps

- [ ] Confirm source bucket locations for each of the 5 source databases
- [ ] Identify mitigation strategies (batching, backoff, prefix distribution, concurrency limits)
- [ ] Examine whether Lake Formation credential caching could help
- [ ] Consider restructuring the step function to batch jobs in groups of 15-20
