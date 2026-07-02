# Requirements Document

## Introduction

This document specifies the requirements for Estimate 3b of the Bryt Energy Contract Note Rework project. The system enables business users to enrich contract note templates with data from external sources managed in SageMaker Unified Studio, without requiring developer involvement to add new data sources.

Business users create and manage data sources in SageMaker Unified Studio (backed by Glue Data Catalog). When they subscribe a data source to the contract note project, it becomes automatically discoverable by the template management system. Users can then attach data sources to templates and reference their fields in the section designer.

At render time, the pipeline queries each attached data source via Athena using the BrytNumber (customer reference) as the lookup key, merging the results into the template input data.

## Glossary

- **Data_Source**: A Glue Data Catalog table subscribed to the SageMaker Unified Studio project, containing customer-related data queryable by BrytNumber
- **BrytNumber**: The unique customer identifier (`customerreference` in the contract payload, e.g., "BRYT002618") used as the join key across all data sources
- **Unified_Studio_Project**: The SageMaker Unified Studio project that manages data subscriptions and Lake Formation permissions
- **Project_Role**: The IAM role associated with the Unified Studio project, which has Lake Formation grants for all subscribed data sources
- **Glue_Data_Catalog**: The AWS Glue metadata catalog containing table schemas (databases, tables, columns) for subscribed data sources
- **Template_Data_Source**: An association between a template and a Data_Source, indicating the template uses fields from that data source at render time
- **Section_Data_Source_Dependency**: A record of which Data_Sources a shared section requires, derived from which data source fields it references
- **Enriched_Data**: The additional columns fetched from subscribed data sources at render time and merged into the contract JSON for template field resolution

## Requirements

### Requirement 1: Data Source Discovery

**User Story:** As a Business_User, I want to see which data sources are available to use in templates, so that I can incorporate additional data into contract notes.

#### Acceptance Criteria

1. THE Admin_Portal SHALL query the Glue_Data_Catalog to discover all tables available to the Project_Role within the Unified_Studio_Project
2. THE Admin_Portal SHALL display discovered data sources with their table name, database name, and column list (name and type)
3. WHEN a new data source is subscribed in Unified Studio, IT SHALL become visible in the Admin Portal without code changes or redeployment
4. THE Admin_Portal SHALL only display data sources that contain a `bryt_number` column (or configured equivalent), filtering out tables that cannot be joined

### Requirement 2: Template Data Source Attachment

**User Story:** As a Business_User, I want to attach data sources to a template, so that the template's sections can reference fields from those data sources.

#### Acceptance Criteria

1. WHEN a Business_User opens the template edit screen, THE Admin_Portal SHALL display the currently attached data sources for that template
2. THE Admin_Portal SHALL allow a Business_User to attach an available Data_Source to a template
3. THE Admin_Portal SHALL allow a Business_User to detach a Data_Source from a template
4. IF a Business_User attempts to detach a Data_Source that is referenced by one or more sections in the template, THEN THE Admin_Portal SHALL display a warning listing the affected sections and require confirmation
5. WHEN a Data_Source is attached to a template, ITS columns SHALL become available as fields in the Section_Editor for any section in that template

### Requirement 3: Data Source Fields in Section Editor

**User Story:** As a Business_User, I want to use data source fields when designing template sections, so that I can include enriched data on contract notes.

#### Acceptance Criteria

1. WHEN a Business_User opens the Section_Editor for a section within a template, THE Section_Editor SHALL display available fields from all attached Data_Sources alongside core contract data fields
2. THE Section_Editor SHALL distinguish data source fields from core contract fields (e.g., by grouping or prefixing with the data source name)
3. WHEN a Business_User places a data source field on the section canvas, THE Section_Editor SHALL record the field reference including the Data_Source identifier and column name
4. THE Section_Editor SHALL display data source fields with their column type to help users understand the data format

### Requirement 4: Shared Section Data Source Dependencies

**User Story:** As a Business_User, I want shared sections to track their data source dependencies, so that templates using those sections have the required data sources attached.

#### Acceptance Criteria

1. THE Admin_Portal SHALL automatically track which Data_Sources a shared section depends on, based on the data source fields used in its Schema_JSON
2. WHEN a Business_User adds a shared section to a template, THE Admin_Portal SHALL check if the template has all required Data_Sources attached
3. IF a shared section requires a Data_Source not attached to the template, THEN THE Admin_Portal SHALL prompt the user to add the missing Data_Source to the template before proceeding
4. THE Admin_Portal SHALL display data source dependencies on the shared section detail screen

### Requirement 5: Render Pipeline Data Enrichment

**User Story:** As a system operator, I want the render pipeline to automatically fetch data from attached data sources at render time, so that data source fields are populated on the final PDF.

#### Acceptance Criteria

1. WHEN the Render_Pipeline selects a matching template, IT SHALL identify all Data_Sources attached to that template
2. FOR each attached Data_Source, THE Render_Pipeline SHALL execute an Athena query to fetch the row matching the BrytNumber from the contract data
3. THE Render_Pipeline SHALL merge the fetched data into the contract JSON, namespaced by data source name to avoid field collisions (e.g., `datasource_name.column_name`)
4. IF a Data_Source query returns no rows for the given BrytNumber, THE Render_Pipeline SHALL log a warning and continue rendering with those fields empty
5. IF a Data_Source query fails (Athena error, timeout), THE Render_Pipeline SHALL log the error and halt processing for that contract note

### Requirement 6: Authentication via Project Role

**User Story:** As a system operator, I want the pipeline and API to access data sources using the Unified Studio project role, so that Lake Formation permissions are automatically inherited.

#### Acceptance Criteria

1. THE Lambda functions (API and Render Pipeline) SHALL assume the Project_Role to access Glue Data Catalog and execute Athena queries
2. THE Project_Role trust policy SHALL be modified to allow the Lambda execution roles to assume it
3. WHEN new data sources are subscribed in Unified Studio, THE system SHALL automatically have access via the existing Project_Role grants without manual IAM changes

### Requirement 7: Data Source API

**User Story:** As a frontend developer, I want API endpoints for data source operations, so that the Admin Portal can manage template data source attachments.

#### Acceptance Criteria

1. THE API SHALL expose an endpoint to list all available data sources (from Glue catalog via Project_Role)
2. THE API SHALL expose endpoints to attach and detach data sources from a template
3. THE API SHALL expose an endpoint to list attached data sources for a given template
4. THE API SHALL expose an endpoint to get column details for a specific data source (for the field browser in the Section Editor)
5. THE API SHALL validate that a data source exists and contains a `bryt_number` column before allowing attachment
