# Requirements Document

**Story US-02 — Glue Data Catalog discovery client**

> Mini-spec derived from parent spec **contract-note-data-source-extensibility**.
> Delivers user story **US-02**. See `manifest.yaml` for the component
> exports/dependencies and `../../graph.yaml` for the full delivery graph.

## Introduction

This story delivers the Glue Data Catalog discovery client (`shared-lib:glue-catalog-client`): the backend module that assumes the Unified Studio Project Role, lists the Glue tables accessible to it, filters them to those joinable by `bryt_number`, and returns structured `AvailableDataSource[]` with columns. It also delivers the per-table column detail fetcher used later by the Data Source API's field browser and by shared-section dependency work.

It is a Wave 2 story. It depends on the shared data source types and the Project Role trust-policy change (both from US-01), and it is consumed downstream by US-03 (Data Source API) and US-05 (render enrichment). This story covers parent Requirement 1 (Data Source Discovery) and delivers the column fetcher used by parent Requirements 3.4 and 7.4.

## Glossary

- **Data_Source**: A Glue Data Catalog table subscribed to the SageMaker Unified Studio project, containing customer-related data queryable by BrytNumber.
- **BrytNumber**: The unique customer identifier (`customerreference` in the contract payload, e.g., "BRYT002618") used as the join key across all data sources.
- **Unified_Studio_Project**: The SageMaker Unified Studio project that manages data subscriptions and Lake Formation permissions.
- **Project_Role**: The IAM role associated with the Unified Studio project, which has Lake Formation grants for all subscribed data sources.
- **Glue_Data_Catalog**: The AWS Glue metadata catalog containing table schemas (databases, tables, columns) for subscribed data sources.

## Delivered components

This story is responsible for creating and owning:

- `shared-lib:glue-catalog-client` — the Glue Data Catalog discovery client (`api/src/data-sources/`) that assumes the Project Role, lists/filters tables, and returns `AvailableDataSource[]` plus the per-table column detail fetcher.

## Dependencies

This story depends on components delivered by other stories (must be available first):

- `shared-lib:data-source-types` (from US-01) — the `AvailableDataSource` and `DataSourceColumn` interfaces the client returns.
- `cdk-construct:project-role-trust-policy` (from US-01) — the modified Project Role trust policy that lets this module's Lambda execution role assume the Project Role.

## Requirements

### Requirement 1: Data Source Discovery  _(parent: Requirement 1)_

**User Story:** As a Business_User, I want the system to discover the Glue tables available to the Project Role (filtered to those joinable by `bryt_number`) with their columns, so that subscribed data sources become usable without code changes.

#### Acceptance Criteria

1. THE discovery client SHALL query the Glue_Data_Catalog to discover all tables available to the Project_Role within the Unified_Studio_Project _(parent 1.1)_
2. THE discovery client SHALL return discovered data sources with their table name, database name, and column list (name and type) _(parent 1.2)_
3. WHEN a new data source is subscribed in Unified Studio, IT SHALL become discoverable by the client without code changes or redeployment _(parent 1.3)_
4. THE discovery client SHALL only return data sources that contain a `bryt_number` column (or configured equivalent), filtering out tables that cannot be joined _(parent 1.4)_

### Requirement 2: Column detail fetcher  _(parent: Requirements 3.4, 7.4)_

**User Story:** As a frontend developer, I want to fetch the full column detail for a specific data source, so that the Section Editor field browser can display column names and types.

#### Acceptance Criteria

1. THE discovery client SHALL expose a column detail fetcher that returns the full column list (name and type) for a specific `{database}/{table}` _(parent 7.4)_
2. THE column detail fetcher SHALL return each column with its Glue/Athena type so that consumers can display the data format _(parent 3.4)_
