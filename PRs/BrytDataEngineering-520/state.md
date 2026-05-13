# Review State — PR #520

## Review Groups

Prioritised by blast radius and complexity:

| # | Group | Files | Status |
|---|---|---|---|
| 1 | Step Functions (orchestration) | orchestrator-sf.ts, source-system-sf.ts, master-record-sf.ts | ✅ Complete |
| 2 | Dependency Map & Config | dependency-map.json, dependency-map.ts, table-config.ts, centrestage.json, phidex.json | ✅ Complete |
| 3 | Data Orchestration CDK | data-orchestration.ts | ⬜ Pending |
| 4 | Partition Tracker Lambda | lambdas/partition-tracker/* (index.ts, orchestrator-handler.ts, partition-utils.ts, step-function-handler.ts) | ✅ Complete |
| 5 | Schema Change Lambda | lambdas/crawler-schema-change/* (index.ts, schema-detection.ts, schema-compare.ts, partition-reset.ts, loop-prevention.ts) | ⬜ Pending |
| 6 | CDC Staging Generic (CDK) | cdc-staging-generic.ts, cdc-staging-jira.ts | ✅ Complete |
| 7 | CDC Staging Scripts (new) | staging.py for centrestage, phidex, salesforce, bryt, ensek | ✅ Complete |
| 8 | Master Record Scripts | 11 modified v3 scripts | ⬜ Pending |
| 9 | Infrastructure (DynamoDB, SQS, EventBridge, Lambda CDK) | partition-tracker.ts, schema-change-rule.ts, partition-event-queue.ts, schema-change-queue.ts, partition-tracker-lambda.ts, schema-change-lambda.ts | ⬜ Pending |
| 10 | DMS Changes | centrestage.ts, phidex.ts | ⬜ Pending |
| 11 | Documentation | data-orchestration-architecture.md | ⬜ Pending |

## Current Position

Group: 1 (Step Functions) — COMPLETE
File: All 3 reviewed

## Issues Found

### Group 1: Step Functions

**orchestrator-sf.ts** (316 lines, added)
- ⚠️ WARNING: IAM policy `resources: ["*"]` for EventBridge rules (line ~85). Should be scoped to specific rule ARN patterns.
- ⚠️ WARNING: The `masterRecordFailure` Pass state is defined but the chain after it doesn't lead to a terminal state — it just formats output. The orchestrator won't explicitly fail if master record fails; it'll succeed with `PARTIAL_FAILURE` status. Is this intentional? Downstream consumers need to check the status field.
- ✅ GOOD: Source system branches catch errors individually so one failure doesn't block others.
- ✅ GOOD: Evaluator Lambda checks dependency map before triggering master records.
- 💡 SUGGESTION: The `isNotPresent("$.evaluationResult.jobsToRun[0]")` check for empty array is a common Step Functions pattern but fragile — if the Lambda returns `null` instead of `[]`, this will behave unexpectedly. Consider adding a validation step.

**source-system-sf.ts** (290 lines, added)
- ⚠️ WARNING: IAM policy `resources: ["*"]` for Glue actions (line ~57). Should be scoped to the specific Glue job ARN.
- ⚠️ WARNING: `maxConcurrency: 5` on the Map state — this limits to 5 entities processing at once per source system. With 55 centrestage tables, this means sequential batches of 5. Is this intentional for throttle mitigation, or should it be configurable?
- 💡 SUGGESTION: The `formatOutput` uses `"updatedEntities.$": "$.entities[*].entityName"` — this JSONPath may not work as expected in Step Functions. Step Functions doesn't support `[*]` projection in Pass state parameters. This might need to be handled in the Lambda instead.
- ✅ GOOD: Passes `pushdownPredicate` to the Glue job — this addresses the S3 throttle issue we investigated!
- ✅ GOOD: Failed entities leave partitions unprocessed for retry on next run.
- ✅ GOOD: Only processes entities with unprocessed partitions (event-driven, not polling everything).

**master-record-sf.ts** (231 lines, added)
- ⚠️ WARNING: IAM policy `resources: ["*"]` for Glue actions. Same as above — should be scoped.
- ⚠️ WARNING: `maxConcurrency: 5` — same consideration as source-system-sf. Master record jobs may have dependencies between them (e.g., invoice-activity before allocated-payment-refund-activity). The Map state with maxConcurrency doesn't respect ordering. Is the dependency map handling this upstream?
- 💡 SUGGESTION: The `prepareJobInput` extracts `$.Map.Item.Value` into `$.jobName`, but the Map state's `parameters` block isn't set — it relies on the default Map item passing. This should work but could be clearer.
- ✅ GOOD: Unknown job names are skipped gracefully rather than failing.
- ✅ GOOD: Per-job error handling — one job failure doesn't block others.

### Group 2: Dependency Map & Config

**dependency-map.json** (108 lines, added)
- ✅ GOOD: Clear, declarative mapping of master record jobs to their staging entity dependencies.
- ✅ GOOD: Covers all 13 master record jobs with their full dependency chains.
- 💡 NOTE: `invoice-activity` depends on `titanium_siteCrmData` (camelCase) but the centrestage.json config uses `titanium_sitecrmdata` (lowercase). This case mismatch could cause the dependency check to miss updates. Needs verification.
- 💡 NOTE: `allocated-payment-refund-activity` has no dependency on `invoice-activity` in this map — the old step function had a sequential dependency (invoice runs before allocated-payment-refund). Is this now handled differently, or is the ordering no longer required?

**dependency-map.ts** (112 lines, added)
- ✅ GOOD: Strong validation on load — catches malformed config early at deploy time.
- ✅ GOOD: `evaluateDependencies` is clean and simple — any updated dependency triggers the job.
- ✅ GOOD: `aggregateUpdatedEntities` only includes successful source system outputs.
- ✅ GOOD: Uses `Set<string>` with `sourceSystem#entity` composite key for O(1) lookups.

**table-config.ts** (97 lines, added)
- ✅ GOOD: Validates config at load time with clear error messages.
- ✅ GOOD: Supports `compositeKey`, `syntheticIdExpression`, and per-table worker sizing.
- 💡 SUGGESTION: The `validateEntry` function doesn't validate `compositeKey` or `syntheticIdExpression` fields — it only checks `idColumn`, `workerType`, `numberOfWorkers`. If someone adds a malformed `compositeKey` (e.g., a string instead of array), it won't be caught.

**centrestage.json** (57 entries) / **phidex.json** (34 entries)
- ✅ GOOD: Config-driven approach — adding a new table is just a JSON entry.
- ✅ GOOD: Special cases handled (compositeKey for billing_wide, syntheticIdExpression for bol_xread tables).
- 💡 NOTE: No `idColumn` specified for most tables — the staging script presumably defaults to `<tableName>id`. Worth confirming this convention is documented.

**dependency-map.test.ts** (284 lines, added)
- ✅ GOOD: Comprehensive tests covering loading, validation, evaluation, and aggregation.

### Group 4: Partition Tracker Lambda

**index.ts** (173 lines, added) — S3 event → DynamoDB partition record writer
- ✅ GOOD: Elegant DynamoDB conditional write handles all 3 cases (new, re-process, already-queued) in a single UpdateItem.
- ✅ GOOD: SQS batch response with partial failure reporting — individual message failures don't block the batch.
- ✅ GOOD: `if_not_exists(created_at, :now)` preserves original creation timestamp on re-processing.
- ⚠️ WARNING: `deriveSourceSystem` uses `includes()` on bucket name — if a bucket name contains multiple keywords (e.g., "centrestage-bryt-backup"), it would match the first one found. Order matters. Currently fine for the known buckets but fragile for future additions.
- 💡 SUGGESTION: The `parseS3KeyToPartitionRecord` assumes a fixed key format with schema_prefix at index 0. If DMS ever changes its output path structure, this will silently produce wrong entity names. Consider adding a validation that the entity_name matches a known table list.

**orchestrator-handler.ts** (121 lines, added) — Evaluates dependencies after source systems complete
- ✅ GOOD: Clean separation — aggregates entities, evaluates deps, returns jobs to run.
- ✅ GOOD: Reports `failedSystems` for visibility without blocking.
- 💡 NOTE: Duplicates `aggregateUpdatedEntities` and `evaluateDependencies` from `dependency-map.ts`. This is likely intentional (Lambda bundle vs CDK code), but worth noting for maintenance — changes need to be made in both places.

**partition-utils.ts** (130 lines, added) — DynamoDB query/update utilities
- ✅ GOOD: `queryUnprocessedPartitions` handles pagination correctly.
- ✅ GOOD: `markPartitionProcessed` is idempotent — ConditionalCheckFailed treated as success.
- ✅ GOOD: `buildPushdownPredicate` generates exact partition predicates — this directly addresses the S3 throttle issue by limiting bookmark file listing to only the partitions with new data!
- ⚠️ WARNING: `buildPushdownPredicate` uses string interpolation to build the predicate. If partition values ever contain single quotes (unlikely for date parts, but possible for other partition schemes), this would produce invalid predicates. No sanitisation is applied.
- ⚠️ WARNING: If there are many unprocessed partitions (e.g., 100+), the generated predicate string could become very long. Glue has a limit on push-down predicate length. Consider adding a fallback or chunking mechanism.

**step-function-handler.ts** (100 lines, added) — Dispatches Step Function task actions
- ✅ GOOD: Clean action-based dispatch pattern.
- ✅ GOOD: `groupByEntity` builds pushdown predicates per entity — each Glue job only reads the partitions it needs.
- ⚠️ WARNING: `handleMarkProcessed` processes partitions sequentially (`for...of` with `await`). With many partitions, this could be slow. Consider using `Promise.all` with batching (e.g., 25 at a time to respect DynamoDB batch limits) or `BatchWriteItem`.

### Group 6+7: CDC Staging Generic + Scripts

**staging.py (centrestage)** (270 lines, added) — Parameterized generic staging script
- ✅ GOOD: Replaces ~50 individual scripts with one parameterized script. Massive reduction in maintenance burden.
- ✅ GOOD: **Disables job bookmarks** and uses pushdown predicates instead — directly fixes the S3 throttle root cause we identified!
- ✅ GOOD: Uses `create_data_frame_from_catalog` (not `create_dynamic_frame`) — avoids the bookmark file listing entirely.
- ✅ GOOD: Schema evolution — detects new columns in source and adds them to the Iceberg table automatically.
- ✅ GOOD: Supports composite keys, synthetic ID expressions, and standard single-column IDs.
- ✅ GOOD: Comprehensive logging throughout.
- ⚠️ WARNING: `evolve_schema` uses `spark.sql(f"ALTER TABLE ... ADD COLUMNS ({col_name} {col_type})")` — the column name is not quoted/escaped. If a column name contains special characters or is a reserved word, this will fail. Consider using backtick quoting: `` `{col_name}` ``.
- ⚠️ WARNING: The `derive_id_column` function has hardcoded naming conventions. If a new entity doesn't follow the convention, it will silently use the wrong ID column. The `ID_COLUMN` override parameter mitigates this, but it relies on the table config being correct.
- 💡 SUGGESTION: `df.count()` is called twice (once after read, once after dedup). Each `count()` triggers a full Spark action. Consider caching the DataFrame or removing the first count if it's just for logging.
- 💡 NOTE: The MERGE uses `UPDATE SET *` and `INSERT *` — this means all columns are updated on match. If schema evolution adds a column that doesn't exist in the source partition being processed, this could set new columns to null on existing rows. The `select([col(c) for c in columns])` step should handle this, but worth testing.
