---
name: data-model-pdf
description: Produce a branded data-model PDF from a spec's data entities — each record with its key pattern (e.g. DynamoDB PK/SK), attribute table, and indexes. Part of the spec-to-deliverables suite.
inclusion: manual
---

# Data Model PDF

Where a spec defines data entities (tables, records, keys), produce a branded data-model document that renders each record with its **key pattern shown prominently** (e.g. DynamoDB PK/SK as monospace badges), an attribute table, and any indexes (GSIs). Reference: `analysis/BRYT/contract-note/walkthroughs/data_model.py` (uses the `entities` block in `build_walkthrough.py`).

Read `deliverables-toolkit` first — this uses the same engine as the walkthroughs.

## Steps

### Step 1: Extract the data model

From each spec's `design.md`, pull the record/table definitions: for each record, its key pattern (PK/SK or primary key), attributes (name, type, description), and any secondary indexes and what they enable. Note which storage is used and what deliberately lives elsewhere (e.g. large blobs in S3 referenced by key).

### Step 2: Write the content module

Use the `entities` block type. Each entity provides: `name`, `pk`, optional `sk`, an optional `note` on its role, and an `attributes` list of `[name, type, description]`. A block can also carry a `table` label and a `gsi` list (name / PK / SK / enables).

Suggested structure:

1. `section` — Overview: the storage approach (e.g. single-table design per bounded area), how records share partitions.
2. `callout` — how to read the key patterns (braced values substituted at runtime; records sharing a PK retrieved together).
3. `table` — tables at a glance.
4. One `entities` block **per logical grouping** (e.g. per estimate or per aggregate), each with its records and any GSIs. Use `pageBreak` to keep groups tidy.
5. `section` — what lives outside the database (S3 blobs, etc.) and why.
6. `callout` — a scope note that names/optionality may be refined during implementation.

### Step 3: Generate and verify

Run the engine (clean `slug`, e.g. `data-model`). Verify per the toolkit: entity-card count, that PK/SK badges render, GSI blocks present, no overflow, and the PDF has no orphaned headings and breaks cleanly between records.

## Notes

- The `entities` block renders PK/SK as labelled monospace badges above the attribute table — that prominence is the whole point; don't bury keys in a plain table.
- One combined data-model document across related specs usually reads better than many tiny ones.
