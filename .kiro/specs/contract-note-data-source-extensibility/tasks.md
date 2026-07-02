# Implementation Plan: Contract Note Data Source Extensibility

## Overview

Extend the contract note template management system to support external data sources from SageMaker Unified Studio. Business users subscribe data sources in Unified Studio; the system auto-discovers them via Glue Data Catalog, allows attaching them to templates, exposes their fields in the section editor, and queries them at render time via Athena using BrytNumber as the join key.

## Tasks

- [ ] 1. Infrastructure and IAM setup
  - [ ] 1.1 Modify Project Role trust policy to allow Lambda assumption
    - Add Lambda execution roles (API + render pipeline) as trusted principals on the Unified Studio Project Role
    - Ensure Lambda roles have `sts:AssumeRole` permission for the Project Role ARN
    - Store Project Role ARN as a CDK parameter / environment variable for both Lambdas
    - _Requirements: 6.1, 6.2_

  - [ ] 1.2 Configure Athena workgroup and results bucket
    - Create or configure an Athena workgroup for contract note queries
    - Create S3 bucket (or prefix) for Athena query results
    - Ensure the Project Role has access to the Athena workgroup and results location
    - _Requirements: 5.2_

  - [ ] 1.3 Add DynamoDB records for template data source attachments
    - Extend existing `ContractNoteTemplates` table with DATASOURCE and DATASOURCE_DEP record types
    - No new table needed (single-table design)
    - _Requirements: 2.1, 4.1_

- [ ] 2. Glue Data Catalog discovery client
  - [ ] 2.1 Implement Glue catalog client (assumes Project Role)
    - AssumeRole to get temporary credentials for the Project Role
    - List databases and tables in the project's Glue catalog
    - Filter tables: only include those with a `bryt_number` column
    - Return structured list of available data sources with column metadata
    - _Requirements: 1.1, 1.2, 1.4_

  - [ ] 2.2 Implement column detail fetcher
    - Get full column list (name, type) for a specific table
    - Used by the Section Editor field browser
    - _Requirements: 3.4, 7.4_

  - [ ]* 2.3 Write property tests for discovery
    - **Property 1: Only bryt_number tables are discoverable**
    - **Property 10: New subscriptions are immediately discoverable**
    - **Validates: Requirements 1.3, 1.4, 6.3**

- [ ] 3. Data Source API endpoints
  - [ ] 3.1 Implement `list-available` handler
    - Call Glue catalog client to get available data sources
    - Return list with database, table name, column count
    - _Requirements: 1.1, 1.2, 7.1_

  - [ ] 3.2 Implement `get-columns` handler
    - Return column names and types for a specific table
    - _Requirements: 7.4_

  - [ ] 3.3 Implement `attach-data-source` handler
    - Validate table exists and has bryt_number column
    - Create DATASOURCE record in DynamoDB under the template
    - _Requirements: 2.2, 7.2, 7.5_

  - [ ] 3.4 Implement `detach-data-source` handler
    - Check if any sections in the template reference fields from this data source
    - If referenced: return 409 with affected section list
    - If not referenced: remove DATASOURCE record
    - _Requirements: 2.3, 2.4, 7.2_

  - [ ] 3.5 Implement `list-attached` handler
    - Query DATASOURCE records for a given template
    - Return list of attached data sources
    - _Requirements: 2.1, 7.3_

  - [ ]* 3.6 Write property tests for data source API
    - **Property 2: Data source attachment round-trip**
    - **Property 3: Detachment with field-in-use warning**
    - **Validates: Requirements 2.1, 2.2, 2.4**

- [ ] 4. Render pipeline enrichment
  - [ ] 4.1 Implement Athena query executor
    - Assume Project Role
    - Build and execute query: `SELECT * FROM {database}.{table} WHERE bryt_number = ? LIMIT 1`
    - Wait for query completion (poll or use async with wait)
    - Parse results into key-value object
    - Handle: no rows (return empty), multiple rows (use first, log warning), errors (throw)
    - _Requirements: 5.2, 5.4, 5.5_

  - [ ] 4.2 Implement enrichment orchestrator
    - Fetch template's attached data sources from DynamoDB
    - Extract BrytNumber from contract data (`customerreference` field)
    - Query each data source in parallel via Athena
    - Merge results into contract data under namespace: `{tableName}.{column}`
    - _Requirements: 5.1, 5.2, 5.3_

  - [ ] 4.3 Integrate enrichment step into render pipeline
    - Insert enrichment between template selection and section rendering
    - Pass enriched data to section renderer instead of raw contract data
    - Error in enrichment halts pipeline (same pattern as other pipeline errors)
    - _Requirements: 5.1, 5.5_

  - [ ]* 4.4 Write property tests for enrichment
    - **Property 7: Enrichment produces namespaced data**
    - **Property 8: Missing data source rows produce empty fields**
    - **Property 9: Data source query failure halts rendering**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**

- [ ] 5. Checkpoint - Backend complete
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Frontend: Template Edit data sources panel
  - [ ] 6.1 Implement DataSourceService
    - List available data sources, get columns, attach/detach, list attached
    - Wire to API Gateway endpoints
    - _Requirements: 1.1, 2.1, 2.2, 2.3_

  - [ ] 6.2 Extend TemplateEditComponent with Data Sources panel
    - Display attached data sources below the section list
    - [+ Attach Data Source] button opens a picker showing available (unattached) sources
    - Detach button per data source with confirmation warning if fields are in use
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [ ] 6.3 Implement data source picker dialog
    - Show available data sources (filtered to exclude already-attached)
    - Display table name, database, column count
    - Select to attach
    - _Requirements: 2.2_

- [ ] 7. Frontend: Section Editor field browser extension
  - [ ] 7.1 Extend SectionEditorComponent to show data source fields
    - Fetch attached data sources for the current template
    - For each, fetch columns
    - Display as collapsible field groups in the designer palette
    - Fields labelled as `{tableName}.{columnName}` with type indicator
    - Visually distinguish from core contract fields
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [ ] 7.2 Implement shared section dependency tracking
    - When saving a section, scan schema JSON for data source field references (fields with `.` namespace prefix matching an attached data source)
    - Write/update DATASOURCE_DEP records for shared sections
    - _Requirements: 4.1_

  - [ ] 7.3 Implement shared section attachment dependency check
    - When adding a shared section to a template, check its DATASOURCE_DEP records
    - If template is missing required data sources, prompt user to add them
    - _Requirements: 4.2, 4.3_

  - [ ] 7.4 Display data source dependencies on Shared Section detail screen
    - Show which data sources a shared section requires
    - _Requirements: 4.4_

  - [ ]* 7.5 Write property tests for frontend logic
    - **Property 4: Field availability scoped to attached data sources**
    - **Property 5: Shared section dependency tracking**
    - **Property 6: Missing dependency enforcement**
    - **Validates: Requirements 2.5, 3.1, 4.1, 4.2, 4.3**

- [ ] 8. Checkpoint - Frontend complete
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Integration wiring
  - [ ] 9.1 Wire CDK deployment for new components
    - Add API Gateway routes for data source endpoints
    - Ensure Lambda roles can assume Project Role
    - Add Athena workgroup and results bucket to CDK
    - Add Project Role ARN to Lambda environment variables
    - _Requirements: 6.1, 6.2, 6.3_

  - [ ]* 9.2 Write integration tests
    - Test: subscribe table in Glue → verify appears in available list
    - Test: attach to template → render with BrytNumber → verify enriched fields in output
    - Test: remove bryt_number column from table → verify filtered from available list
    - _Requirements: 1.3, 1.4, 5.1_

- [ ] 10. Final checkpoint
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- The Project Role ARN and Athena workgroup name should be CDK parameters (vary by environment)
- Athena queries are metered per data scanned — consider partition pruning on bryt_number if tables are large
- BrytNumber = `customerreference` field in the contract payload
- Field namespacing (`tableName.columnName`) avoids collisions and makes data provenance clear
- The enrichment step runs data source queries in parallel to minimize latency
