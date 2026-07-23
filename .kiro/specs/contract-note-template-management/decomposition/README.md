# Decomposition: contract-note-template-management

This folder decomposes the parent spec into independently deliverable user stories. Each `stories/<id>/` folder is a self-contained Kiro spec a developer can copy into their own `.kiro/specs/`. `graph.yaml` holds the machine-readable dependency graph; `jira-import.csv` is ready for Jira's CSV importer.

**Status:** OK - no blocking issues

## Implementation waves

Stories in the same wave have no dependency on each other and can be built in parallel. Each wave depends only on earlier waves.

- **Wave 1:** US-01, US-07
- **Wave 2:** US-02, US-03, US-05, US-06
- **Wave 3:** US-04
- **Wave 4:** US-08
- **Wave 5:** US-09
- **Wave 6:** US-10

## Dependency graph

```mermaid
graph TD
    US_01["US-01: Foundation: infrastructure & shared types"]
    US_02["US-02: Template CRUD API"]
    US_03["US-03: Section, shared-section, version history & change log API"]
    US_04["US-04: Section version publishing & variants API"]
    US_05["US-05: Template selection rules API"]
    US_06["US-06: Render pipeline (Step Functions)"]
    US_07["US-07: pdf-me Designer web component"]
    US_08["US-08: Angular module, routing & services"]
    US_09["US-09: Angular screens & components"]
    US_10["US-10: Integration wiring & end-to-end validation"]
    US_01 --> US_02
    US_01 --> US_03
    US_01 --> US_04
    US_03 --> US_04
    US_01 --> US_05
    US_01 --> US_06
    US_01 --> US_08
    US_02 --> US_08
    US_03 --> US_08
    US_04 --> US_08
    US_05 --> US_08
    US_07 --> US_09
    US_08 --> US_09
    US_02 --> US_10
    US_03 --> US_10
    US_04 --> US_10
    US_05 --> US_10
    US_06 --> US_10
    US_09 --> US_10
```

## Stories

| Story | Title | Exports | Depends on | Requirements |
|-------|-------|---------|-----------|--------------|
| US-01 | Foundation: infrastructure & shared types | shared-lib:types<br>shared-lib:spec-validation<br>data-table:ContractNoteTemplates<br>gsi:PriorityIndex<br>s3-bucket:schema-json<br>s3-bucket:error-output<br>cdk-construct:ApiGatewayRoutes | - | 1, 5, 10, 14 |
| US-02 | Template CRUD API | api-endpoint:GET /contract-note-templates<br>api-endpoint:POST /contract-note-templates<br>api-endpoint:PUT /contract-note-templates/{id}<br>api-endpoint:DELETE /contract-note-templates/{id}<br>api-endpoint:PUT /contract-note-templates/reorder<br>lambda:template-handlers | shared-lib:types<br>data-table:ContractNoteTemplates<br>gsi:PriorityIndex<br>cdk-construct:ApiGatewayRoutes | 1, 2, 3, 4, 5 |
| US-03 | Section, shared-section, version history & change log API | api-endpoint:sections-crud<br>api-endpoint:section-schema<br>api-endpoint:section-versions<br>api-endpoint:shared-sections-crud<br>api-endpoint:template-changelog<br>lambda:section-handlers | shared-lib:types<br>data-table:ContractNoteTemplates<br>s3-bucket:schema-json<br>cdk-construct:ApiGatewayRoutes | 3, 6, 7, 8, 9, 16, 17 |
| US-04 | Section version publishing & variants API | api-endpoint:section-publish<br>api-endpoint:section-variants-crud<br>api-endpoint:variant-rule<br>lambda:variant-publish-handlers | shared-lib:types<br>shared-lib:spec-validation<br>data-table:ContractNoteTemplates<br>api-endpoint:section-versions | 18, 19 |
| US-05 | Template selection rules API | api-endpoint:template-rule<br>lambda:rules-handlers | shared-lib:types<br>shared-lib:spec-validation<br>data-table:ContractNoteTemplates<br>cdk-construct:ApiGatewayRoutes | 10 |
| US-06 | Render pipeline (Step Functions) | state-machine:RenderStateMachine<br>shared-lib:spec-evaluator<br>lambda:parse-input<br>lambda:select-template<br>lambda:render-section<br>lambda:stitch<br>lambda:write-output<br>lambda:handle-failure<br>s3-bucket:input-xml<br>s3-bucket:output-pdf | shared-lib:types<br>data-table:ContractNoteTemplates<br>gsi:PriorityIndex<br>s3-bucket:schema-json<br>s3-bucket:error-output | 11, 12, 13, 14, 18, 19, 20 |
| US-07 | pdf-me Designer web component | web-component:pdfme-designer | - | 7 |
| US-08 | Angular module, routing & services | frontend-component:ContractNoteModule<br>service:TemplateService<br>service:SectionService<br>service:RulesService | shared-lib:types<br>api-endpoint:GET /contract-note-templates<br>api-endpoint:sections-crud<br>api-endpoint:section-versions<br>api-endpoint:section-publish<br>api-endpoint:section-variants-crud<br>api-endpoint:variant-rule<br>api-endpoint:shared-sections-crud<br>api-endpoint:template-rule | 15 |
| US-09 | Angular screens & components | frontend-screen:TemplateList<br>frontend-screen:TemplateEdit<br>frontend-screen:SharedSectionsLibrary<br>frontend-component:RulesConfigComponent<br>frontend-component:SectionEditorComponent<br>frontend-component:SectionVersionHistoryComponent<br>frontend-component:SectionVariantsComponent<br>frontend-component:SectionPublishComponent<br>frontend-component:Navigation | frontend-component:ContractNoteModule<br>service:TemplateService<br>service:SectionService<br>service:RulesService<br>web-component:pdfme-designer | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 16, 17, 18, 19, 21 |
| US-10 | Integration wiring & end-to-end validation | cdk-instance:deployment | lambda:template-handlers<br>lambda:section-handlers<br>lambda:variant-publish-handlers<br>lambda:rules-handlers<br>state-machine:RenderStateMachine<br>frontend-component:Navigation | 14, 15, 20 |
