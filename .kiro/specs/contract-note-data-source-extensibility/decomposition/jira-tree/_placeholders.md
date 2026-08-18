---
project: SQP
set_label: s2s-contract-note-data-source-extensibility
key_map:
  contract-note-data-source-extensibility: SQP-5079
  US-01: SQP-5080
  US-01-1: SQP-5081
  US-01-2: SQP-5082
  US-01-3: SQP-5083
  US-02: SQP-5085
  US-02-1: SQP-5091
  US-02-2: SQP-5092
  US-02-3: SQP-5093
  US-03: SQP-5086
  US-03-1: SQP-5100
  US-03-2: SQP-5097
  US-03-3: SQP-5098
  US-03-4: SQP-5101
  US-03-5: SQP-5102
  US-03-6: SQP-5103
  US-03-7: SQP-5104
  US-03-8: SQP-5105
  US-03-9: SQP-5106
  US-04: SQP-5084
  US-04-1: SQP-5088
  US-04-2: SQP-5090
  US-04-3: SQP-5089
  US-05: SQP-5087
  US-05-1: SQP-5094
  US-05-2: SQP-5095
  US-05-3: SQP-5096
  US-05-4: SQP-5099
  US-06: SQP-5108
  US-06-1: SQP-5115
  US-06-2: SQP-5117
  US-06-3: SQP-5116
  US-07: SQP-5107
  US-07-1: SQP-5110
  US-07-2: SQP-5112
  US-07-3: SQP-5111
  US-07-4: SQP-5113
  US-08: SQP-5109
  US-08-1: SQP-5114
  US-08-2: SQP-5118
---

# Placeholder key map

Correlates each tree key to the live Jira issue it was pushed to. jira-push uses this to rewrite cross-references (US-01, US-04-2, …) in issue descriptions to real Jira keys before the update pass. Regenerated from live Jira on each run; safe to delete once descriptions are finalised.

| Tree key | Jira | Type | Summary |
|----------|------|------|---------|
| contract-note-data-source-extensibility | SQP-5079 | Epic | contract-note-data-source-extensibility (delivery) |
| US-01 | SQP-5080 | Story | Foundation: shared data-source types & infrastructure |
| US-01-1 | SQP-5081 | Sub-task | Extend shared-lib/types.ts with data source entities (TemplateDataSource, SharedSectionDataSourceDependency entity types + records + AvailableDataSource/DataSourceColumn/SectionDataSourceDependency interfaces + SK aliases) |
| US-01-2 | SQP-5082 | Sub-task | Modify Project Role trust policy to allow the data-source + enrich Lambda execution roles to assume it; expose PROJECT_ROLE_ARN as a CDK param/env var |
| US-01-3 | SQP-5083 | Sub-task | Configure Athena workgroup and S3 results bucket; grant the Project Role access to both |
| US-02 | SQP-5085 | Story | Glue Data Catalog discovery client |
| US-02-1 | SQP-5091 | Sub-task | Implement Glue catalog client: AssumeRole -> Project Role creds, list databases/tables, filter to bryt_number tables, return AvailableDataSource[] with columns |
| US-02-2 | SQP-5092 | Sub-task | Implement column detail fetcher: full column list (name, type) for a specific {database}/{table} |
| US-02-3 | SQP-5093 | Sub-task | Property tests for discovery (Property 1: only bryt_number tables discoverable; Property 11: new subscriptions immediately discoverable) |
| US-03 | SQP-5086 | Story | Data Source API handlers + routing |
| US-03-1 | SQP-5100 | Sub-task | Declare routes in contract-note-foundation.ts: contract-note-data-sources root (+ {database}/{table}/columns), data-sources under templates/{templateId}, data-source-dependencies under shared-sections/{id}; extend ContractNoteApiRoutes with DataSourceRouteResources |
| US-03-2 | SQP-5097 | Sub-task | Implement list-available handler (Glue client -> [{database, tableName, columnCount}]) |
| US-03-3 | SQP-5098 | Sub-task | Implement get-columns handler (column names + types for a table) |
| US-03-4 | SQP-5101 | Sub-task | Implement attach-data-source handler (validate table exists + has bryt_number; write DATASOURCE record) |
| US-03-5 | SQP-5102 | Sub-task | Implement detach-data-source handler (scan all sections' variants for referencing fields; 409 with affected section+variant list, else remove) |
| US-03-6 | SQP-5103 | Sub-task | Implement list-attached handler (query DATASOURCE records for a template) |
| US-03-7 | SQP-5104 | Sub-task | Implement list-shared-section-deps handler (query DATASOURCE_DEP records) |
| US-03-8 | SQP-5105 | Sub-task | Create DataSourceApi CDK construct (per-op NodejsFunctions, grant table/Glue/Athena/AssumeRole, wire LambdaIntegrations, pass PROJECT_ROLE_ARN + Athena config); instantiate in contract-note-stack.ts |
| US-03-9 | SQP-5106 | Sub-task | Property tests for data source API (Property 2: attachment round-trip; Property 3: detachment with variant-field-in-use warning) |
| US-04 | SQP-5084 | Story | Data source dependency scanner |
| US-04-1 | SQP-5088 | Sub-task | Implement pdf-me schema field-reference scanner: walk all pages of { schemas: [[...]] }, collect element names containing '.', map prefix -> table name |
| US-04-2 | SQP-5090 | Sub-task | Implement shared-section dependency recompute: on variant schema save / version publish, scan all variants' schemas, compute union of referenced data sources, reconcile DATASOURCE_DEP records |
| US-04-3 | SQP-5089 | Sub-task | Property tests for dependency tracking (Property 5: dependency = union across variants) |
| US-05 | SQP-5087 | Story | Render pipeline enrichment (new Step Functions state) |
| US-05-1 | SQP-5094 | Sub-task | Implement Athena query executor (api/src/render/athena-client.ts): assume Project Role; run SELECT * FROM {db}.{table} WHERE bryt_number = ? LIMIT 1; parse rows; no rows -> empty, multiple -> first+warn, error -> throw |
| US-05-2 | SQP-5095 | Sub-task | Implement enrich-data-sources handler (api/src/render/enrich-data-sources.ts): read template DATASOURCE records; none -> pass through; extract customerreference; query each source concurrently; merge under {table}.{column} |
| US-05-3 | SQP-5096 | Sub-task | Wire the state into render-pipeline.ts: add EnrichDataSourcesHandler NodejsFunction, insert between selectTemplate and renderSections, add to handle-failure catch array, grant table read + Athena/AssumeRole |
| US-05-4 | SQP-5099 | Sub-task | Property tests for enrichment (Property 7: namespaced data; 8: empty pass-through; 9: empty rows continue; 10: failure routes to handle-failure) |
| US-06 | SQP-5108 | Story | Frontend: Template Edit data sources panel |
| US-06-1 | SQP-5115 | Sub-task | Implement DataSourceService (list available, get columns, attach/detach, list attached, list shared-section deps) wired to the API Gateway endpoints |
| US-06-2 | SQP-5117 | Sub-task | Extend template-edit component with a Data Sources panel (show attached; [+ Attach] picker; detach with confirmation warning if a variant references its fields; available regardless of DRAFT/PUBLISHED) |
| US-06-3 | SQP-5116 | Sub-task | Implement data source picker dialog (available sources excluding attached, with table/database/column count) |
| US-07 | SQP-5107 | Story | Frontend: section-variant editor field browser & shared-section deps |
| US-07-1 | SQP-5110 | Sub-task | Surface data source fields in the pdfme-designer palette for the edited variant: collapsible groups per data source; fields labelled {table}.{column} with type, visually distinct; placed fields use the namespaced name |
| US-07-2 | SQP-5112 | Sub-task | Implement shared section attachment dependency check: on adding a shared section, read its DATASOURCE_DEP records; if the template is missing required sources, prompt to add them first |
| US-07-3 | SQP-5111 | Sub-task | Display data source dependencies on the shared section detail screen |
| US-07-4 | SQP-5113 | Sub-task | Property tests for frontend logic (Property 4: field availability scoped to attachments; Property 6: missing dependency enforcement) |
| US-08 | SQP-5109 | Story | Integration wiring & end-to-end validation |
| US-08-1 | SQP-5114 | Sub-task | Finalise CDK deployment: confirm API Gateway routes, Lambda->Project Role assume, Athena workgroup/results bucket, and env vars are all wired in the stack |
| US-08-2 | SQP-5118 | Sub-task | Integration tests: subscribe Glue table -> appears; attach -> drop XML -> enriched fields render; remove bryt_number -> filtered out; force Athena error -> handle-failure |
