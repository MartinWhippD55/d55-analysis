# Flatten JSON Master-Record Tables

## Summary

Key master-record tables currently contain JSON columns that are difficult to query. Need to flatten these into proper columnar structures.

## Background

- Master-record tables hold critical reference/dimension data
- JSON columns make ad-hoc querying painful (especially in Athena/Spark SQL)
- Flattening will improve query performance and usability for downstream consumers

## Key Areas

- Identify which master-record tables have JSON columns
- Understand the schema within the JSON (is it stable or evolving?)
- Determine target flattened schema
- Migration strategy (in-place transform vs new table + backfill)
- Impact on downstream consumers during transition

## Status

🟡 Not started
