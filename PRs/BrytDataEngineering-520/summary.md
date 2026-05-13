# PR #520 Review Summary — Data Orchestration Rework

## Overall Assessment: ✅ Approve (with suggestions)

This is a well-architected rework that directly addresses the S3 throttling issues we've been investigating. The move from 94 parallel bookmark-based jobs to event-driven partition tracking with pushdown predicates is the right solution. The code quality is high, with good error handling, idempotency, and separation of concerns.

## Key Findings

### Critical (0)
None.

### Warnings (8)

1. **IAM `resources: ["*"]`** — Three step functions use wildcard resources for Glue and EventBridge permissions. Should be scoped to specific ARNs. (orchestrator-sf.ts, source-system-sf.ts, master-record-sf.ts)

2. **Master record job ordering** — The old step function had `invoice-activity → allocated-payment-refund-activity` as a sequential dependency. The new Map state with `maxConcurrency: 5` doesn't enforce this ordering. If the ordering is still required, the dependency map or master-record-sf needs to handle it.

3. **Case mismatch in dependency-map.json** — `titanium_siteCrmData` (camelCase) vs `titanium_sitecrmdata` (lowercase in centrestage.json). Could cause missed dependency triggers.

4. **`buildPushdownPredicate` string interpolation** — No sanitisation of partition values. Unlikely to be an issue with date-based partitions, but fragile. Also, very long predicates (100+ partitions) could exceed Glue's predicate length limit.

5. **Sequential `markPartitionProcessed`** — Processes partitions one-by-one with `await`. Could be slow with many partitions. Consider batching with `Promise.all`.

6. **`evolve_schema` unquoted column names** — `ALTER TABLE ADD COLUMNS` uses unquoted column names. Reserved words or special characters would break this.

7. **`deriveSourceSystem` bucket matching** — Uses `includes()` which could match incorrectly if bucket names overlap. Order-dependent.

8. **JSONPath `[*]` in Pass state** — `source-system-sf.ts` uses `"$.entities[*].entityName"` in a Pass state parameters block. Step Functions may not support this projection — needs testing.

### Suggestions (5)

1. **Double `df.count()`** in staging.py — Two full Spark actions for logging. Consider caching or removing the first count.

2. **Duplicated logic** — `aggregateUpdatedEntities` and `evaluateDependencies` exist in both `dependency-map.ts` (CDK) and `orchestrator-handler.ts` (Lambda). Consider sharing via a common package.

3. **`isNotPresent("$.evaluationResult.jobsToRun[0]")` for empty array check** — Fragile if Lambda returns `null` instead of `[]`. Add validation.

4. **`table-config.ts` validation gaps** — Doesn't validate `compositeKey` (should be string array) or `syntheticIdExpression` (should be string) fields.

5. **Default ID column convention** — `derive_id_column` relies on naming conventions. Document this clearly so future table additions don't silently use wrong keys.

## Positive Observations

- **Directly fixes the S3 throttle root cause** — Disables bookmarks, uses pushdown predicates built from partition tracker. This is exactly the mitigation we identified.
- **Event-driven architecture** — Only processes what's changed, rather than polling all tables every run.
- **Graceful failure handling** — Individual entity/job failures don't cascade. Failed partitions remain unprocessed for retry.
- **Config-driven** — Adding new tables is a JSON entry, not a new script. Scales to 4,500 tables.
- **DynamoDB partition tracker** — Elegant conditional writes handle all state transitions in a single atomic operation.
- **Dependency-aware master records** — Only triggers downstream jobs when their inputs have actually changed.
- **Good test coverage** — dependency-map.test.ts, table-config.test.ts, partition-tracker tests.
- **`maxConcurrency: 5`** — Limits parallel Glue jobs per source system, preventing the thundering herd.

## Questions for Author

1. Is the `invoice-activity → allocated-payment-refund-activity` ordering still required? If so, how is it enforced in the new architecture?
2. What happens if the partition tracker DynamoDB table gets very large over time? Is there a TTL or cleanup mechanism for processed records?
3. The `maxConcurrency: 5` — was this tuned based on the S3 throttle investigation, or is it arbitrary? Could it be configurable per source system?
4. How does the schema change Lambda interact with the partition tracker? Does marking partitions as unprocessed trigger an immediate orchestration run, or does it wait for the next scheduled trigger?

## Summary for PR Comment

> **Review: ✅ Approve with suggestions**
>
> Excellent architectural rework. The move to event-driven partition tracking with pushdown predicates directly addresses the S3 503 throttling we've been seeing in production. Code quality is high with good error handling and idempotency throughout.
>
> Key items to address before merge:
> - Case mismatch: `titanium_siteCrmData` in dependency-map.json vs `titanium_sitecrmdata` in centrestage.json
> - Verify master record job ordering (invoice before allocated-payment-refund) is handled
> - Scope IAM wildcard policies to specific resource ARNs
> - Test the JSONPath `[*]` projection in source-system-sf Pass state
>
> Minor suggestions in the full review. Happy to discuss any of these.
