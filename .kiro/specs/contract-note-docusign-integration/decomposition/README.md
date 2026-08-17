# Decomposition: contract-note-docusign-integration

This folder decomposes the parent spec into independently deliverable user stories. Each `stories/<id>/` folder is a self-contained Kiro spec a developer can copy into their own `.kiro/specs/`. `graph.yaml` holds the machine-readable dependency graph; `jira-import.csv` is ready for Jira's CSV importer.

**Status:** OK - no blocking issues

## Implementation waves

Stories in the same wave have no dependency on each other and can be built in parallel. Each wave depends only on earlier waves.

- **Wave 1:** US-01, US-07
- **Wave 2:** US-02, US-03, US-04
- **Wave 3:** US-05, US-06
- **Wave 4:** US-08

## Dependency graph

```mermaid
graph TD
    US_01["US-01: Foundation: DocuSign pipeline infra, shared types & utilities"]
    US_02["US-02: Salesforce integration client (greenfield)"]
    US_03["US-03: DocuSign integration client"]
    US_04["US-04: Envelope metadata service"]
    US_05["US-05: Send Envelope Lambda"]
    US_06["US-06: Webhook Lambda (completion + declined/expired)"]
    US_07["US-07: Estimate 1 metadata surfacing (Requirement 12)"]
    US_08["US-08: Integration wiring & deployment"]
    US_01 --> US_02
    US_01 --> US_03
    US_01 --> US_04
    US_01 --> US_05
    US_02 --> US_05
    US_03 --> US_05
    US_04 --> US_05
    US_01 --> US_06
    US_02 --> US_06
    US_03 --> US_06
    US_04 --> US_06
    US_05 --> US_08
    US_06 --> US_08
    US_07 --> US_08
```

## Stories

| Story | Title | Exports | Depends on | Requirements |
|-------|-------|---------|-----------|--------------|
| US-01 | Foundation: DocuSign pipeline infra, shared types & utilities | shared-lib:docusign-types<br>shared-lib:retry<br>shared-lib:error-writer<br>cdk-construct:DocuSignPipeline<br>data-table:DocuSignEnvelopes<br>gsi:SalesforceRefIndex<br>s3-bucket:signed-contract-notes | - | 5, 6, 7, 8, 10, 11 |
| US-02 | Salesforce integration client (greenfield) | service:salesforce-client | shared-lib:docusign-types<br>shared-lib:retry | 2, 8 |
| US-03 | DocuSign integration client | service:docusign-client | shared-lib:docusign-types<br>shared-lib:retry | 3, 4, 6, 7 |
| US-04 | Envelope metadata service | service:metadata-service | shared-lib:docusign-types<br>data-table:DocuSignEnvelopes<br>gsi:SalesforceRefIndex | 5 |
| US-05 | Send Envelope Lambda | lambda:send-envelope | service:salesforce-client<br>service:docusign-client<br>service:metadata-service<br>shared-lib:docusign-types<br>shared-lib:error-writer | 1, 2, 3, 4, 5, 10 |
| US-06 | Webhook Lambda (completion + declined/expired) | lambda:webhook<br>api-endpoint:POST /docusign-webhook | service:salesforce-client<br>service:docusign-client<br>service:metadata-service<br>s3-bucket:signed-contract-notes<br>shared-lib:error-writer<br>cdk-construct:DocuSignPipeline | 6, 7, 8, 9, 10 |
| US-07 | Estimate 1 metadata surfacing (Requirement 12) | state-machine:render-metadata-passthrough | - | 12 |
| US-08 | Integration wiring & deployment | cdk-instance:deployment | lambda:send-envelope<br>lambda:webhook<br>api-endpoint:POST /docusign-webhook<br>state-machine:render-metadata-passthrough | 1, 6, 11 |
