# Questions — Cheap CDC

## Open

- Is the source MySQL on RDS, Aurora, or self-managed?
- Do all 4,500 tables have `updated_at` / timestamp columns? (needed for batch approaches)
- What's the average change volume per hour across the 4,500 tables?
- Are there existing read replicas we can point CDC at?
- What latency is acceptable? (real-time, hourly, daily?)
- Do we need to capture deletes, or is soft-delete used?
- What's the total data size across the 4,500 tables?
- Are there any tables with very high change rates that need special handling?
- Is there budget for Kafka/MSK infrastructure, or do we need to stay serverless/managed?
- Could we tier the tables — high-priority (real-time CDC) vs low-priority (batch)?

## Answered

_(none yet)_
