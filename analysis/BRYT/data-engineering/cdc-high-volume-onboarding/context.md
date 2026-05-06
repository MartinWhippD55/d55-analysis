# CDC High-Volume Table Onboarding

## Summary

Introducing ~4500 new tables via CDC (DMS into S3), then processing through raw → refined → curated layers using Glue. Need to design the right model to handle this at scale.

## Background

- ~4500 new tables arriving via AWS DMS (Change Data Capture)
- Landing in S3, then processed through the standard layer pipeline (raw → refined → curated)
- Current Glue patterns may not scale to this volume without rethinking the approach
- Need a model that balances automation, observability, and maintainability

## Key Areas

- DMS task design (one task per table? grouped by schema/source?)
- S3 landing zone structure and partitioning strategy
- Glue job design — per-table jobs vs parameterised/generic jobs
- Metadata-driven pipeline orchestration
- Schema evolution handling at scale
- Monitoring and alerting across 4500+ tables
- Cost implications (Glue DPUs, S3 requests, DMS instance sizing)

## Status

🟡 Not started
