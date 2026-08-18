---
issue_type: Epic
summary: contract-note-data-source-extensibility (delivery)
epic_name: contract-note-data-source-extensibility
identity_label: s2s-contract-note-data-source-extensibility-epic
set_label: s2s-contract-note-data-source-extensibility
labels:
- s2s-contract-note-data-source-extensibility
- s2s-contract-note-data-source-extensibility-epic
---

## Goal

Let business users enrich contract note templates with data from external sources managed in SageMaker Unified Studio, without a developer being involved to add each new data source. Subscribed Glue tables become discoverable, attachable to templates, referenceable as fields in the section-variant editor, and are queried by BrytNumber at render time.

## Background

Decomposed from spec `contract-note-data-source-extensibility` by spec-to-stories. This is Estimate 3b, built on the landed Estimate 1 template-management system (`BrytBusinessServices`: variants, versioned S3 schema JSON, DRAFT/PUBLISHED lifecycle, Step Functions render pipeline). Business users increasingly need customer-specific data (e.g. credit, usage) on contract notes; today every new data source needs code and a redeploy. This epic removes that bottleneck by leaning on SageMaker Unified Studio's Glue catalog + Lake Formation grants inherited via the project role.

## Scope

- In scope: the stories and waves below — Glue discovery, template attachment, section-editor field browser, shared-section dependency tracking, render-time Athena enrichment, and the supporting API/IAM/infra.
- Out of scope: creating or subscribing data sources inside SageMaker Unified Studio (a business-user action in SageMaker, not this system); changes to the pdf-me rendering engine or the section-variant/version model itself; join keys other than `bryt_number` (`customerreference`).

## Delivery plan

| Wave | Stories |
|------|---------|
| 1 | US-01 |
| 2 | US-02, US-04 |
| 3 | US-03, US-05 |
| 4 | US-06 |
| 5 | US-07 |
| 6 | US-08 |

## Stories

| Story | Summary | Est (days) |
|-------|---------|------------|
| US-01 | Foundation: shared data-source types & infrastructure | 1.5 |
| US-02 | Glue Data Catalog discovery client | 1.0 |
| US-04 | Data source dependency scanner | 1.0 |
| US-03 | Data Source API handlers + routing | 2.0 |
| US-05 | Render pipeline enrichment (new Step Functions state) | 1.5 |
| US-06 | Frontend: Template Edit data sources panel | 1.5 |
| US-07 | Frontend: section-variant editor field browser & shared-section deps | 1.5 |
| US-08 | Integration wiring & end-to-end validation | 1.0 |

_Total estimate: 11 days (excludes optional test sub-tasks)._

## Definition of done

- All 8 stories delivered.
- Parent requirements covered: 1, 2, 3, 4, 5, 6, 7.
