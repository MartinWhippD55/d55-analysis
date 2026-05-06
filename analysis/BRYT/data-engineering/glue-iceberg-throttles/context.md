# Glue & Iceberg Throttle Investigation

## Summary

Investigating throttling and credential failures in the `rel-esg-prod-data-eng--data-orchestration` Step Function, which orchestrates ~65 parallel Glue jobs writing to Iceberg tables on S3.

## Environment

- Account: `837413265725` (eu-west-2)
- Step Function: `rel-esg-prod-data-eng--data-orchestration`
- Sub-state-machine: `rel-esg-prod-data-eng--run-glue-job` (poll-based: start → wait 30s → check status → loop)
- Glue version: 5.0
- Worker type: G.1X, 2 workers (most jobs); G.4X, 4 workers (phidex-project-unit-rate)
- Job mode: SCRIPT
- All jobs share the same script template (fail at line 48 calling `getDynamicFrame`)

## Orchestration Flow

1. `get-execution-id` — Pass state
2. `run-crawlers` — Parallel: 2 crawlers (centrestage + phidex)
3. `run-titanium-jobs` — Parallel: **65 Glue jobs** fired simultaneously
4. `run-glue-jobs` — Parallel: 8 master-record jobs (sequential dep: invoice-activity → allocated-payment-refund-activity)
5. `data-orchestration-failed` — Fail state (catch-all, no retry)

## Findings (30 failed executions, Apr 30 – May 6 2026)

### Error Categories

| Error Type | Frequency | Category | Detail |
|---|---|---|---|
| Lake Formation credential failure | ~10+ occurrences | `UNCLASSIFIED_ERROR` | "LFCredential fetch failed with status code: 400" |
| S3 request rate throttle | ~2-3 explicit | `THROTTLING_ERROR` | S3 503 SlowDown during `getDynamicFrame` |
| Connection pool timeout | ~1-3 | `TIMEOUT_ERROR` | "Timeout waiting for connection from pool" (Iceberg catalog contention) |

### Failure Distribution by Job (top offenders)

| Failures | Job |
|---|---|
| 3x | centerstage-titanium-document-data |
| 3x | centerstage-titanium-invoice-crm-data |
| 3x | phidex-project-unit-rate |
| 3x | centerstage-titanium-invoice-detail |
| 2x | phidex-billing-contract-mpan-volume |
| 2x | centerstage-titanium-customer |
| 2x | centerstage-titanium-meter-electricity |
| 2x | phidex-billing-invoice |
| 2x | centerstage-titanium-site-billing-raw-data |
| 1x | 17 other jobs |

- **26 unique jobs** have failed across 30 executions
- Failures are essentially random — whichever job loses the race for credentials or S3 capacity

### Root Cause Analysis

The core problem is **65 Glue jobs starting simultaneously**, causing:

1. **Lake Formation API saturation** — All 65 jobs request temporary credentials at the same moment. LF's `GetTemporaryGluePartitionCredentials` API throttles, returning 400 errors. This is the most frequent failure mode.

2. **S3 503 SlowDown** — Jobs that get past credential fetch then collectively exceed S3's per-prefix rate limits (3,500 PUT/5,500 GET per second per prefix). The jobs all read from shared source prefixes.

3. **Connection pool exhaustion** — Larger jobs (phidex-project-unit-rate with 4x G.4X) timeout waiting for connections, likely due to Iceberg metadata/Glue Catalog contention from the parallel blast.

## Status

🟡 In progress — root cause identified, next steps: examine S3 prefix structure and Glue job scripts

## Next Steps

- [ ] Examine S3 bucket/prefix structure to understand read/write patterns
- [ ] Look at Glue job scripts (shared template) to understand how they interact with Iceberg
- [ ] Identify mitigation strategies (batching, backoff, prefix distribution, concurrency limits)
