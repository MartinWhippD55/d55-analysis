---
project: SQP
set_label: s2s-contract-note-template-management
key_map:
  contract-note-template-management: SQP-4951
  US-01: SQP-4952
  US-01-1: SQP-4953
  US-01-2: SQP-4954
  US-01-3: SQP-4955
  US-01-4: SQP-4956
  US-02: SQP-4958
  US-02-1: SQP-4967
  US-02-2: SQP-4968
  US-02-3: SQP-4969
  US-02-4: SQP-4970
  US-02-5: SQP-4971
  US-03: SQP-4959
  US-03-1: SQP-4972
  US-03-2: SQP-4973
  US-03-3: SQP-4974
  US-03-4: SQP-4975
  US-03-5: SQP-4976
  US-03-6: SQP-4977
  US-04: SQP-4960
  US-04-1: SQP-4978
  US-04-2: SQP-4979
  US-04-3: SQP-4980
  US-04-4: SQP-4981
  US-05: SQP-4961
  US-05-1: SQP-4982
  US-05-2: SQP-4983
  US-06: SQP-4963
  US-06-1: SQP-4984
  US-06-2: SQP-4985
  US-06-3: SQP-4986
  US-06-4: SQP-4987
  US-06-5: SQP-4988
  US-06-6: SQP-4989
  US-06-7: SQP-4990
  US-06-8: SQP-4991
  US-07: SQP-4962
  US-07-1: SQP-4992
  US-07-2: SQP-4993
  US-08: SQP-4964
  US-08-1: SQP-4994
  US-08-2: SQP-4995
  US-09: SQP-4965
  US-09-1: SQP-4996
  US-09-2: SQP-4997
  US-09-3: SQP-4998
  US-09-4: SQP-4999
  US-09-5: SQP-5000
  US-09-6: SQP-5001
  US-09-7: SQP-5002
  US-09-8: SQP-5003
  US-10: SQP-4966
  US-10-1: SQP-5004
  US-10-2: SQP-5005
  US-10-3: SQP-5006
---

# Placeholder key map

Correlates each tree key to the live Jira issue it was pushed to. jira-push uses this to rewrite cross-references (US-01, US-04-2, …) in issue descriptions to real Jira keys before the update pass. Regenerated from live Jira on each run; safe to delete once descriptions are finalised.

| Tree key | Jira | Type | Summary |
|----------|------|------|---------|
| contract-note-template-management | SQP-4951 | Epic | contract-note-template-management (delivery) |
| US-01 | SQP-4952 | Story | Foundation: infrastructure & shared types |
| US-01-1 | SQP-4953 | Sub-task | CDK: DynamoDB table + PriorityIndex GSI, S3 buckets, API Gateway routes |
| US-01-2 | SQP-4954 | Sub-task | Shared TypeScript interfaces and DynamoDB record types |
| US-01-3 | SQP-4955 | Sub-task | Specification tree validation utility |
| US-01-4 | SQP-4956 | Sub-task | Property tests for specification validation |
| US-02 | SQP-4958 | Story | Template CRUD API |
| US-02-1 | SQP-4967 | Sub-task | list-templates handler (priority-ordered) |
| US-02-2 | SQP-4968 | Sub-task | create-template handler (validation, duplicate check, priority) |
| US-02-3 | SQP-4969 | Sub-task | get/update/delete-template handlers |
| US-02-4 | SQP-4970 | Sub-task | reorder-templates handler |
| US-02-5 | SQP-4971 | Sub-task | Property tests for template API logic |
| US-03 | SQP-4959 | Story | Section, shared-section, version history & change log API |
| US-03-1 | SQP-4972 | Sub-task | list/add/remove/reorder-section handlers (incl. T&C positioning) |
| US-03-2 | SQP-4973 | Sub-task | get/save-section-schema handlers (writes a new version) |
| US-03-3 | SQP-4974 | Sub-task | section version history handlers (list/get/revert) |
| US-03-4 | SQP-4975 | Sub-task | shared section CRUD handlers + references |
| US-03-5 | SQP-4976 | Sub-task | template change log |
| US-03-6 | SQP-4977 | Sub-task | Property tests for section API logic |
| US-04 | SQP-4960 | Story | Section version publishing & variants API |
| US-04-1 | SQP-4978 | Sub-task | get-linked-templates + publish-section-version handlers |
| US-04-2 | SQP-4979 | Sub-task | section variant CRUD handlers (order, default) |
| US-04-3 | SQP-4980 | Sub-task | variant rule get/save handlers (reuse validation) |
| US-04-4 | SQP-4981 | Sub-task | Property tests for publishing and variants |
| US-05 | SQP-4961 | Story | Template selection rules API |
| US-05-1 | SQP-4982 | Sub-task | get-rule handler |
| US-05-2 | SQP-4983 | Sub-task | save-rule handler (validate specification) |
| US-06 | SQP-4963 | Story | Render pipeline (Step Functions) |
| US-06-1 | SQP-4984 | Sub-task | Specification evaluator |
| US-06-2 | SQP-4985 | Sub-task | Template selection (first-match-wins) |
| US-06-3 | SQP-4986 | Sub-task | Section renderer (pdf-me) + pinned-version resolution |
| US-06-4 | SQP-4987 | Sub-task | Section variant selection (first match, default fallback) |
| US-06-5 | SQP-4988 | Sub-task | PDF stitcher (pdf-lib) |
| US-06-6 | SQP-4989 | Sub-task | Step Functions state handlers + Map state + failure state |
| US-06-7 | SQP-4990 | Sub-task | XML-to-JSON parse + S3 trigger |
| US-06-8 | SQP-4991 | Sub-task | Property tests: evaluation, variants, stitching, failure isolation |
| US-07 | SQP-4962 | Story | pdf-me Designer web component |
| US-07-1 | SQP-4992 | Sub-task | <pdfme-designer> web component wrapping the React pdf-me Designer |
| US-07-2 | SQP-4993 | Sub-task | schema-json in / schema-save event out; on-demand bundle load |
| US-08 | SQP-4964 | Story | Angular module, routing & services |
| US-08-1 | SQP-4994 | Sub-task | ContractNoteModule with routes + Cognito group route guard |
| US-08-2 | SQP-4995 | Sub-task | TemplateService, SectionService, RulesService wired to the API |
| US-09 | SQP-4965 | Story | Angular screens & components |
| US-09-1 | SQP-4996 | Sub-task | TemplateListComponent (landing page) |
| US-09-2 | SQP-4997 | Sub-task | TemplateEditComponent + change log + variant list |
| US-09-3 | SQP-4998 | Sub-task | RulesConfigComponent (shared by template + variant rules) |
| US-09-4 | SQP-4999 | Sub-task | SectionEditorComponent host (modal) |
| US-09-5 | SQP-5000 | Sub-task | SharedSectionsComponent + detail |
| US-09-6 | SQP-5001 | Sub-task | SectionVersionHistoryComponent + SectionPublishComponent |
| US-09-7 | SQP-5002 | Sub-task | Navigation + landing pages (page vs modal) |
| US-09-8 | SQP-5003 | Sub-task | Component unit tests |
| US-10 | SQP-4966 | Story | Integration wiring & end-to-end validation |
| US-10-1 | SQP-5004 | Sub-task | CDK deployment wiring: IAM, S3-triggered state machine, API routes, CORS |
| US-10-2 | SQP-5005 | Sub-task | Portal sidebar navigation entry (Cognito-gated) |
| US-10-3 | SQP-5006 | Sub-task | End-to-end pipeline integration tests |
