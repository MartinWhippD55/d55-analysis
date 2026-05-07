# Cheap CDC

## Summary

Exploring cost-effective approaches to bring ~4,500 additional MySQL tables into the data platform via CDC, without impacting source database performance.

## Background

- Current CDC pipeline uses AWS DMS replicating MySQL → S3 (parquet, partitioned by year/month/day/hour)
- Glue jobs then process through raw → curated → refined layers (Iceberg tables)
- Currently handling ~94 tables; about to scale to ~4,500 tables
- Cost implications of DMS at this scale are significant (instance sizing, storage, S3 PUT costs)
- Source database performance must not be degraded

## Constraints

- Source: MySQL databases (likely RDS or Aurora MySQL)
- Target: S3 (for downstream Glue processing into Iceberg)
- Must not impact source database performance
- Need CDC (not just full-load snapshots) for ongoing changes
- Data flows through raw → curated → refined pipeline
- Cost is the primary concern at 4,500 table scale

## Options Analysis

### Option 1: AWS DMS (current approach, scaled up)

**How it works:** DMS reads MySQL binlog, writes CDC files to S3 in parquet/CSV format.

**Costs at scale:**
- Replication instance: need larger instance(s) for 4,500 tables — likely multiple `dms.r5.2xlarge` or `dms.r5.4xlarge` instances
- DMS is priced per-hour for the replication instance (always-on for CDC)
- S3 PUT requests for every change event
- DMS Serverless alternative: auto-scales capacity (DCU-hours), may be more cost-effective for variable workloads

**Pros:**
- Already in use, team has operational experience
- Fully managed, handles schema changes
- Native S3 target with parquet output
- DMS Serverless can scale down during quiet periods

**Cons:**
- Expensive at scale — always-on instances for CDC
- Binlog reading adds load to source (though reads from replica if configured)
- DMS has a soft limit of ~500 tables per task; 4,500 tables = ~9+ tasks
- Generates many small files (the exact problem causing throttles in the Glue jobs)

**Estimated cost:** High — multiple large replication instances running 24/7

---

### Option 2: DMS Serverless

**How it works:** Same as DMS but with serverless capacity. You specify min/max DCU (Data Capacity Units) and it auto-scales.

**Costs at scale:**
- Priced per DCU-hour (1 DCU ≈ $0.018/hour in eu-west-2)
- Scales down to minimum during low-change periods
- Still need multiple replication configs for 4,500 tables

**Pros:**
- Scales down during off-peak (nights, weekends)
- Same operational model as current DMS
- No instance management

**Cons:**
- Still fundamentally DMS — same small-file problem
- May not be significantly cheaper for high-throughput continuous CDC
- Same table-per-task limits apply

**Estimated cost:** Medium-High — cheaper than provisioned during quiet periods, similar during peak

---

### Option 3: Read from MySQL replica + batch export to S3

**How it works:** Point reads at a MySQL read replica. Periodically (e.g., hourly) run batch queries to extract changed rows (using `updated_at` timestamps or similar) and write to S3.

**Costs at scale:**
- Read replica cost (already exists if using RDS Multi-AZ or Aurora)
- Glue/Lambda/ECS compute for the batch export jobs
- S3 storage

**Pros:**
- Very cheap — no DMS instance needed
- Zero impact on primary (reads from replica)
- Produces fewer, larger files (one per table per batch)
- Simple to implement with Glue JDBC connections or Lambda

**Cons:**
- Not true CDC — relies on tables having `updated_at` columns
- Misses deletes unless soft-delete pattern is used
- Higher latency (batch interval, e.g., hourly)
- Need to handle schema changes manually
- Requires JDBC connections from Glue/Lambda to replica

**Estimated cost:** Low — just replica + compute for batch jobs

---

### Option 4: Debezium on MSK/MSK Serverless → S3

**How it works:** Debezium MySQL connector reads binlog, publishes to Kafka (MSK). A sink connector (S3 Sink or Firehose) writes to S3.

**Costs at scale:**
- MSK Serverless: pay per data in/out + storage
- MSK Connect for Debezium source + S3 sink connectors
- Or MSK Provisioned if throughput is predictable

**Pros:**
- True CDC from binlog — captures all changes including deletes
- Debezium is battle-tested for MySQL CDC
- MSK Serverless scales with throughput
- Can fan out to multiple consumers
- Produces well-structured change events

**Cons:**
- More infrastructure to manage (MSK, connectors, monitoring)
- MSK Serverless can be expensive at high throughput
- Connector management (schema registry, dead letter queues)
- Still reads binlog from source (use replica)
- Operational complexity significantly higher than DMS

**Estimated cost:** Medium — depends heavily on change volume

---

### Option 5: Aurora MySQL native S3 export (SELECT INTO OUTFILE S3)

**How it works:** Aurora MySQL supports `SELECT INTO OUTFILE S3` to export query results directly to S3. Can be scheduled to export changed rows periodically.

**Costs at scale:**
- No additional infrastructure — runs on the Aurora instance itself
- S3 storage costs only
- Scheduling via EventBridge + Lambda or Step Functions

**Pros:**
- Extremely cheap — no DMS, no Kafka, no additional compute
- Native Aurora feature, very fast
- Produces larger files (one per export)
- Can target a read replica to avoid primary impact

**Cons:**
- Only works with Aurora MySQL (not standard RDS MySQL)
- Not true CDC — batch export of changed rows
- Requires `updated_at` columns or equivalent
- Misses deletes unless soft-delete
- Output format is CSV (not parquet) — needs conversion downstream
- Limited to 6GB per file

**Estimated cost:** Very Low — essentially just S3 storage

---

### Option 6: RDS Snapshot Export to S3

**How it works:** AWS natively exports RDS/Aurora snapshots to S3 in Apache Parquet format. Can be automated daily/hourly.

**Costs at scale:**
- Snapshot export pricing: ~$0.012 per GB exported
- S3 storage
- No impact on source (exports from snapshot, not live DB)

**Pros:**
- Zero source impact — works from snapshots
- Native parquet output
- No additional infrastructure
- Can export specific tables
- Consistent point-in-time data

**Cons:**
- Full table export each time (not incremental CDC)
- Latency tied to snapshot frequency (typically daily)
- Cost scales with total data size, not change volume
- Need to diff snapshots downstream to identify changes
- Snapshot creation itself has a brief I/O impact

**Estimated cost:** Low for small tables, High for large tables (full export each time)

---

### Option 7: Maxwell's Daemon → Kinesis/S3

**How it works:** Maxwell is a lightweight open-source MySQL binlog reader that outputs JSON change events. Can write to Kinesis, Kafka, or directly to files.

**Costs at scale:**
- Single lightweight process (runs on EC2/ECS)
- Kinesis Data Streams or Firehose for delivery to S3
- Or direct file output to S3

**Pros:**
- Very lightweight — single Java process
- True CDC from binlog
- Low operational overhead compared to Debezium+Kafka
- Can run against a replica
- Kinesis Firehose provides automatic batching to S3

**Cons:**
- Less mature than Debezium for production use
- Single-threaded — may struggle with 4,500 tables at high throughput
- Need to self-manage (no managed service)
- Schema handling is basic
- Community support smaller than Debezium

**Estimated cost:** Low — EC2/ECS instance + Kinesis Firehose

## Status

🟡 Options identified, needs cost modelling and decision
