# Questions — CDC High-Volume Table Onboarding

## Open

- What source system(s) are the 4500 tables coming from?
- Are all tables full-load + CDC, or a mix?
- What's the expected change volume (rows/sec) across the estate?
- Do we have a table catalogue/manifest with metadata (schema, size, update frequency)?
- What does the current Glue pipeline pattern look like — one job per table or shared?
- Is there an existing metadata-driven framework, or do we need to build one?
- How do we handle schema drift at this scale (new columns, type changes)?
- What's the SLA for data freshness in curated?
- Are there natural groupings (by source schema, priority, size) we can use to batch?
- What's the budget envelope for DMS instances and Glue compute?

## Answered

_(none yet)_
