# Requirements Document

## Introduction

The Report Builder is a self-service report/query builder delivered as an extension to the existing Angular Customer Portal. It lets a non-technical, signed-in customer assemble a report visually: drag tables from a palette onto a flow canvas, pick the columns they want per table, connect tables into joins, and iterate on the design in plain language with an AWS Bedrock assistant. When satisfied, the customer saves the report and runs it. Runs execute asynchronously against Amazon Athena, results are stored in S3, and completed results are downloadable as CSV.

Reports and runs are private to the signed-in customer, whose identity is derived from JWT claims. A Portal_User may be associated with many customer accounts, so data access is scoped to the SET of bryt numbers the user is authorised for (the Authorised_Bryt_Numbers), resolved server-side by replicating the Customer Portal's customer-access logic. Where an authorised admin operates the session on behalf of another user (Admin_Override), the effective identity — and therefore the Authorised_Bryt_Numbers — is that of the overridden user. A shared report-design model serves both the drag-and-drop designer and the assistant. Governance and security are first-class: every generated query is pinned to the user's Authorised_Bryt_Numbers using trusted server-side context, a separate verification step confirms that scoping before execution and again over results, and query generation is bounded to an allow-listed catalog and defended against prompt injection.

The backend lives in a new repository, `BrytReportBuilder`, mirroring the structure and established patterns of `BrytBusinessServices` (per-operation TypeScript Lambda handlers grouped by domain folder, DynamoDB single-table design, versioned encrypted S3 buckets, API Gateway REST resource tree, Step Functions async pipelines, and a shared library for shared types).

Source of truth for scope, screens, and flow: `analysis/BRYT/report-builder/overview.md` and `analysis/BRYT/report-builder/screen-mockups.md`.

## Glossary

- **Report_Builder**: The overall self-service report/query building feature (frontend + backend).
- **Customer_Portal**: The existing Angular application that Report_Builder extends.
- **Portal_User**: A signed-in, non-technical Customer_Portal user who owns and operates reports, identified by their email derived from JWT claims; under Admin_Override the effective identity is the override email.
- **Bryt_Number**: An identifier associated with a customer account. A Portal_User may be authorised for many bryt numbers, one per accessible customer account.
- **Authorised_Bryt_Numbers**: The set of Bryt_Numbers a Portal_User may query, resolved server-side by replicating the Customer Portal logic — take the effective email (Admin_Override.OverrideEmail if present, otherwise the user's email), look up the accessible customer accounts from the User_Customer_Mapping, intersect with the user's CustomerIds claim (CanAccessCustomer), exclude hidden accounts, and map each remaining account to its Bryt_Number.
- **Admin_Override**: A mode in which an authorised admin operates the session as another user's email, changing the effective Portal_User identity and therefore the Authorised_Bryt_Numbers.
- **User_Customer_Mapping**: The store that maps a user email to the customer accounts they may access (as in the Customer Portal's user↔customer table).
- **Report_Design**: The shared, serialisable model representing a report — selected tables, selected columns, joins, filters, and sort order.
- **Flow_Canvas**: The ReactFlow-style graph surface on which tables appear as nodes and joins as edges (screen 02).
- **Data_Table_Palette**: The searchable left-panel list of allow-listed tables available to drag onto the Flow_Canvas.
- **Column_Picker**: The modal used to select all or individual columns for a table (screen 03).
- **Catalog**: The curated, allow-listed set of tables and columns sourced from the Glue database `rel_esg_prod_data_eng_master_record_db`.
- **Join_Manifest**: A manifest file defining well-understood join predicates between Catalog tables, used by both the auto-connect designer and the Assistant.
- **Assistant**: The AWS Bedrock–backed helper (assume Claude on Bedrock) that reads and edits the Report_Design in response to natural-language requests.
- **Query_Generator**: The backend component that translates a Report_Design into executable Athena SQL.
- **Query_Verifier**: The backend component that, after generation and before execution, confirms the bryt-number scoping and query bounds are present and correct, and that verifies results before download.
- **Run**: One asynchronous execution of a report's query against Athena.
- **Run_Status**: The lifecycle state of a Run — Queued, Running, Complete, Failed, or Cancelled.
- **Report_Store**: The persistence layer for saved Report_Designs.
- **Conversation_Store**: The persistence layer for per-report Assistant conversation history.
- **Run_Store**: The persistence layer for Run records and their result locations.
- **Result_Store**: The private, versioned, encrypted S3 storage holding Run result objects (CSV).
- **Report_API**: The backend API surface (reports CRUD, run/execute, run status/list, CSV download, assistant chat, cancel).
- **Trusted_Context**: Server-resolved data supplied to the Query_Generator/Assistant that cannot be overridden by model output or prompt content — includes the Authorised_Bryt_Numbers, the Join_Manifest, and (where a report targets a specific account) the selected Bryt_Number, which MUST be a member of the Authorised_Bryt_Numbers.

## Requirements

### Requirement 1: My Reports List (Screen 01)

**User Story:** As a Portal_User, I want to see and manage my saved reports, so that I can open, create, or remove reports scoped to me.

#### Acceptance Criteria

1. WHEN a Portal_User opens the My Reports screen, THE Report_Builder SHALL display only the reports in the Report_Store owned by the effective Portal_User identity, and SHALL complete this display within 5 seconds of the screen opening.
2. THE Report_Builder SHALL display, for each listed report, the report name, each table the report uses shown as a separate badge, and the actions View and Delete.
3. WHEN a Portal_User selects "+ New Report", THE Report_Builder SHALL open the Flow_Canvas builder with an empty Report_Design.
4. WHEN a Portal_User selects View on a report, THE Report_Builder SHALL open that report's Report_Design in the Flow_Canvas builder.
5. WHEN a Portal_User selects Delete on a report, THE Report_Builder SHALL display a confirmation prompt, and upon the Portal_User confirming SHALL remove that report from the Report_Store and from the displayed list within 5 seconds.
6. WHEN a Portal_User enters text in the search control, THE Report_Builder SHALL display only reports whose name contains the entered text as a case-insensitive substring, and SHALL display a no-results message when no report name matches.
7. WHEN a Portal_User selects a sort option, THE Report_Builder SHALL order the displayed reports by report name ascending (A–Z) or descending (Z–A) according to the selected option, defaulting to ascending when none is selected.
8. IF the Portal_User has no saved reports in the Report_Store, THEN THE Report_Builder SHALL display an empty-state message inviting the Portal_User to create a new report.
9. IF the Portal_User JWT is missing, is expired, or does not identify a valid Portal_User, THEN THE Report_Builder SHALL NOT display any reports and SHALL display an error message indicating the session is invalid and re-authentication is required.
10. IF retrieval of reports from the Report_Store fails, THEN THE Report_Builder SHALL display an error message indicating the reports could not be loaded and SHALL provide a control to retry.
11. IF removal of a report fails after the Portal_User confirmed the Delete, THEN THE Report_Builder SHALL retain that report in the list and display an error message indicating the deletion did not complete.

### Requirement 2: Builder Canvas (Screen 02)

**User Story:** As a Portal_User, I want to assemble a report visually on a canvas, so that I can design a report without writing SQL.

#### Acceptance Criteria

1. THE Report_Builder SHALL display a searchable Data_Table_Palette listing each allow-listed Catalog table with its table name and its column count.
2. WHEN a Portal_User drags a table from the Data_Table_Palette onto the Flow_Canvas, THE Report_Builder SHALL open the Column_Picker for that table.
3. THE Report_Builder SHALL render each table on the Flow_Canvas as a node showing its selected columns and a summary displaying the count of selected columns and the count of remaining unselected columns for that table.
4. WHEN a Portal_User drags from one node's edge to another node, THE Report_Builder SHALL create a join between the two tables using the predicate defined in the Join_Manifest for that table pair.
5. WHILE two joined nodes are displayed, THE Report_Builder SHALL display a join line with a join-condition badge between them.
6. IF a Portal_User attempts to join two tables for which the Join_Manifest defines no predicate, THEN THE Report_Builder SHALL reject the join, leave the current Report_Design unchanged, and display a message indicating that the tables cannot be joined.
7. WHEN a Portal_User selects the remove control on a node title, THE Report_Builder SHALL remove that table and its joins from the Report_Design and update the Flow_Canvas.
8. WHEN a Portal_User edits the report name in the header to a value of 1 to 200 characters, THE Report_Builder SHALL update the report name in the current Report_Design.
9. THE Report_Builder SHALL provide Preview, Ask assistant, Run, and Save actions in the builder header.
10. WHEN a Portal_User selects Run, THE Report_Builder SHALL open the Run and history modal for the current report.
11. WHEN a Portal_User enters text in the Data_Table_Palette search field, THE Report_Builder SHALL display only the tables whose name contains the entered text using case-insensitive matching, and IF no table name matches, THEN THE Report_Builder SHALL display an empty-result message.
12. IF a Portal_User confirms the Column_Picker with zero columns selected, THEN THE Report_Builder SHALL reject the confirmation, keep the Column_Picker open, and display a message indicating that at least one column must be selected.
13. IF a Portal_User edits the report name to an empty value or a value exceeding 200 characters, THEN THE Report_Builder SHALL reject the change, preserve the previous report name, and display a message indicating the allowed report name length.

### Requirement 3: Column Selection (Screen 03)

**User Story:** As a Portal_User, I want to choose which columns a table contributes, so that my report includes only the data I need.

#### Acceptance Criteria

1. WHEN the Column_Picker opens for a table, THE Report_Builder SHALL list all allow-listed columns of that table from the Catalog, showing each column's name, its data type, and a key tag on columns that are join keys or primary keys.
2. WHEN the Column_Picker opens for a newly added table, THE Report_Builder SHALL pre-select the key columns (join key and primary key columns), leave all other columns unselected, and display the resulting "X of N selected" count.
3. WHEN a Portal_User selects "Select all" while no column filter is active, THE Report_Builder SHALL mark every column of that table as selected and update the "X of N selected" count.
4. WHEN a Portal_User selects "Select all" while a column filter is active, THE Report_Builder SHALL mark every currently displayed column as selected and update the "X of N selected" count.
5. WHEN a Portal_User toggles an individual column, THE Report_Builder SHALL update the selected state of only that column and update the "X of N selected" count.
6. WHEN a Portal_User enters text in the column filter, THE Report_Builder SHALL display only columns whose name contains the entered text as a case-insensitive substring, and WHEN the filter text is cleared THE Report_Builder SHALL display all columns again while preserving the current selection state.
7. WHEN a Portal_User confirms with "Add table" with at least one column selected, THE Report_Builder SHALL record the selected columns for that table in the Report_Design and place the node on the Flow_Canvas.
8. IF a Portal_User confirms with zero columns selected, THEN THE Report_Builder SHALL prevent confirmation, keep the Column_Picker open with its current list and selection state, and display a message indicating that at least one column is required.
9. WHEN the column filter matches no columns, THE Report_Builder SHALL display an empty-result message within the Column_Picker.
10. IF retrieval of the table's columns from the Catalog fails, THEN THE Report_Builder SHALL display an error message indicating the columns could not be loaded and provide a control to retry.

### Requirement 4: Assistant Drawer and Agent-Driven Editing (Screen 04)

**User Story:** As a Portal_User, I want to refine my report in plain language with an assistant, so that I can make changes without manipulating the canvas directly.

#### Acceptance Criteria

1. WHEN a Portal_User selects "Ask assistant", THE Report_Builder SHALL open the Assistant drawer within 1 second while keeping the Flow_Canvas and palette visible.
2. WHEN a Portal_User submits a natural-language message of 1 to 2000 characters, THE Report_Builder SHALL send the message together with the current Report_Design to the Assistant via the Report_API.
3. WHEN the Report_Builder receives an applied-change response from the Assistant, THE Report_Builder SHALL update the shared Report_Design and reflect the change on the Flow_Canvas within 2 seconds.
4. WHEN the Assistant applies a change, THE Assistant SHALL return a description of each change made and an applied-change summary.
5. THE Assistant SHALL read and write the same Report_Design structure that the Flow_Canvas edits.
6. IF a Portal_User request cannot be satisfied within the allow-listed Catalog and Join_Manifest, THEN THE Assistant SHALL decline the request, present a message explaining the specific limitation, and retain the current Report_Design without modification.
7. WHEN a Portal_User closes the Assistant drawer, THE Report_Builder SHALL return to full-width builder editing with the current Report_Design retained.
8. IF a Portal_User submits an empty, whitespace-only, or over-2000-character message, THEN THE Report_Builder SHALL reject the submission, present a message indicating the valid message length, and SHALL NOT send the message via the Report_API.
9. IF the Report_API does not respond within 30 seconds or returns an error, THEN THE Report_Builder SHALL present a message indicating the request failed and retain the current Report_Design without modification.

### Requirement 5: Report Preview (Screen 06)

**User Story:** As a Portal_User, I want a quick sample of my report's output, so that I can sanity-check the layout before running the full job.

#### Acceptance Criteria

1. WHEN a Portal_User selects Preview, THE Report_Builder SHALL display a dialog showing a sample of at most 100 result rows, presenting only the columns selected in the Report_Design in the same left-to-right order defined in the Report_Design.
2. WHEN the preview dialog is displayed, THE Report_Builder SHALL display a filter and sort summary strip listing every filter and sort rule currently defined in the Report_Design.
3. THE Report_Builder SHALL label the preview results as a bounded sample limited to a maximum of 100 rows.
4. WHEN a Portal_User selects Preview, THE Report_Builder SHALL NOT queue or start an asynchronous Run.
5. WHEN the preview is generated, THE Query_Generator SHALL produce a query bounded to a maximum of 100 returned rows, pinned to the Portal_User Authorised_Bryt_Numbers, and subject to the same verification applied to full runs.
6. WHILE a preview is being generated, THE Report_Builder SHALL display a progress indicator in the dialog.
7. WHEN a Portal_User selects Close or the dialog dismiss control, THE Report_Builder SHALL dismiss the preview dialog, leave the Report_Design unchanged, and return to the builder.
8. IF preview generation does not complete within 10 seconds, THEN THE Report_Builder SHALL stop the preview attempt and display a timeout error in the dialog, leaving the Report_Design unchanged.
9. IF preview generation fails, THEN THE Report_Builder SHALL display an error in the dialog, leave the Report_Design unchanged, and not queue or start an asynchronous Run.
10. IF the preview query returns zero rows, THEN THE Report_Builder SHALL display an empty-result indication while still showing the selected columns and the filter and sort summary strip.

### Requirement 6: Save Report (Screen 07)

**User Story:** As a Portal_User, I want to save my report design, so that I can reuse it later from My Reports.

#### Acceptance Criteria

1. WHEN a Portal_User selects Save, THE Report_Builder SHALL display a form containing a report name field accepting 1 to 100 characters, an optional description field accepting 0 to 500 characters, and the tables used shown as badges.
2. WHEN a Portal_User confirms the save with a report name of 1 to 100 characters after trimming whitespace, THE Report_Builder SHALL persist the serialised Report_Design to the Report_Store scoped to the effective Portal_User identity within 5 seconds.
3. IF a Portal_User confirms the save with an empty or whitespace-only name, THEN THE Report_Builder SHALL prevent the save, retain the entered form values, and display a message indicating a name is required.
4. IF a Portal_User confirms the save with a name exceeding 100 characters or a description exceeding 500 characters, THEN THE Report_Builder SHALL prevent the save, retain the entered form values, and display a message indicating which field exceeds its allowed length.
5. IF persisting the Report_Design fails, THEN THE Report_Builder SHALL prevent the save from completing, retain the entered Report_Design and form values, and display a message indicating the save failed.
6. WHEN a save completes successfully, THE Report_Builder SHALL make the saved report appear in the Portal_User My Reports list.
7. WHEN a Portal_User saves a Report_Design that already exists for the effective Portal_User identity, THE Report_Builder SHALL update the stored Report_Design in place rather than create a duplicate entry.

### Requirement 7: Run and History (Screen 05)

**User Story:** As a Portal_User, I want to run my report asynchronously and review its past runs, so that I can produce and retrieve report output over time.

#### Acceptance Criteria

1. WHEN a Portal_User selects "Run now", THE Report_Builder SHALL queue a new asynchronous Run via the Report_API and, within 3 seconds, display a new row at the top of the run history with Run_Status Queued.
2. THE Report_Builder SHALL display up to the 50 most-recent runs ordered most-recent-first by started time, showing for each run its run number, started time in the Portal_User's local time zone, trigger, Run_Status, row count, and per-run actions.
3. WHEN a Run reaches Complete status, THE Report_Builder SHALL offer a Download CSV action for that Run.
4. WHEN a Portal_User selects Download CSV for a completed Run, THE Report_Builder SHALL provide the CSV result object from the Result_Store for that Run.
5. WHERE a Run is in Failed status, THE Report_Builder SHALL display the error message truncated to 120 characters inline and SHALL display the full error message on hover.
6. WHERE a Run is in Queued or Running status, THE Report_Builder SHALL offer a Cancel action for that Run.
7. WHEN a Portal_User selects Cancel for a Queued or Running Run, THE Report_Builder SHALL request cancellation via the Report_API and update the Run_Status accordingly.
8. WHEN a Portal_User selects Refresh, THE Report_Builder SHALL retrieve and display the current Run_Status of the report's runs within 3 seconds.
9. IF queuing a new Run via the Report_API fails, THEN THE Report_Builder SHALL not add a new run row and SHALL display an error indicating the Run could not be started.
10. IF the CSV result object for a completed Run is unavailable in the Result_Store, THEN THE Report_Builder SHALL display an error indicating the result could not be retrieved.
11. IF a cancellation request fails, THEN THE Report_Builder SHALL retain the Run's current Run_Status and display an error indicating the cancellation did not complete.

### Requirement 8: Shared Report-Design Domain Model

**User Story:** As a Portal_User, I want the canvas and the assistant to edit one consistent design, so that visual and conversational edits stay in sync.

#### Acceptance Criteria

1. THE Report_Builder SHALL represent a report as a single Report_Design containing selected tables, selected columns per table, joins, filters, and sort order.
2. THE Report_Builder SHALL use the same Report_Design instance for both the Flow_Canvas editor and the Assistant, such that a change applied by either is observable to the other without conversion or duplication.
3. WHEN a Report_Design is serialised to its persistable form and then deserialised, THE Report_Builder SHALL produce a Report_Design in which the set of selected tables, the set of selected columns per table, the set of joins, the set of filters, and the ordered sort order are each identical to those of the original.
4. THE Report_Builder SHALL map the Report_Design to the flow-graph representation such that each node corresponds to exactly one selected table and each edge corresponds to exactly one join.
5. IF a Report_Design references a table or column not present in the allow-listed Catalog, THEN THE Report_Builder SHALL reject the Report_Design as invalid, indicating which table or column is not allow-listed, and leave any previously persisted Report_Design unchanged.
6. IF a Report_Design references a join not defined in the Join_Manifest, THEN THE Report_Builder SHALL reject the Report_Design as invalid, indicating which join is undefined, and leave any previously persisted Report_Design unchanged.

### Requirement 9: Agent-to-SQL Translation with Pre-Execution Validation

**User Story:** As a Portal_User, I want my design turned into a correct, safe query, so that runs produce accurate results without exposing unsafe SQL.

#### Acceptance Criteria

1. WHEN a Run or preview is requested, THE Query_Generator SHALL translate the current Report_Design into executable Athena SQL.
2. THE Query_Generator SHALL reference only tables and columns present in the allow-listed Catalog.
3. THE Query_Generator SHALL construct joins using only join predicates defined in the Join_Manifest.
4. WHEN query generation completes and prior to any execution, THE Assistant SHALL validate the generated query using a dry-run tool.
5. IF a dry-run validation reports an error, THEN THE Query_Generator SHALL prevent execution, retain the current Report_Design without modification, and surface a validation error indicating the reported failure.
6. WHEN query generation completes, THE Query_Generator SHALL pass the generated query to the Query_Verifier before any execution occurs.
7. IF the Report_Design references a table or column not present in the allow-listed Catalog, THEN THE Query_Generator SHALL prevent execution, retain the Report_Design unchanged, and surface a validation error identifying the disallowed table or column.
8. IF a join required by the Report_Design has no matching predicate in the Join_Manifest, THEN THE Query_Generator SHALL prevent execution, retain the Report_Design unchanged, and surface a validation error identifying the unsupported join.
9. IF a dry-run validation does not return within 30 seconds, THEN THE Assistant SHALL prevent execution and surface a validation error indicating the dry-run timed out.

### Requirement 10: Data Isolation by Authorised Bryt Numbers

**User Story:** As a Portal_User, I want every query restricted to the customer accounts I am authorised for, so that I can never see another customer's data.

#### Acceptance Criteria

1. WHEN the Report_API receives a request from a Portal_User, THE Report_API SHALL resolve the effective Portal_User identity server-side from the JWT claims (using the Admin_Override email when an Admin_Override is present, otherwise the user's email), and SHALL NOT read identity or bryt numbers from request headers, query parameters, or request body.
2. THE Report_API SHALL resolve the Authorised_Bryt_Numbers for the effective Portal_User by replicating the Customer Portal resolution logic (User_Customer_Mapping lookup, CustomerIds/CanAccessCustomer intersection, exclusion of hidden accounts, mapping accounts to bryt numbers).
3. IF the effective Portal_User has no Authorised_Bryt_Numbers, THEN THE Report_API SHALL deny data access, return no data records, and return an unauthorized response.
4. THE Report_API SHALL supply the Authorised_Bryt_Numbers to the Query_Generator and Assistant as Trusted_Context.
5. THE Query_Generator SHALL pin every generated query with a filter that restricts results to bryt numbers within the Authorised_Bryt_Numbers.
6. IF a Report_Design or request targets a specific Bryt_Number that is not a member of the Authorised_Bryt_Numbers, THEN THE Report_API SHALL deny the request and return no data records.
7. THE Report_Builder SHALL derive the bryt-number filter only from Trusted_Context and SHALL NOT derive it from Assistant output or Portal_User prompt content.
8. THE Report_Store, Run_Store, and Conversation_Store SHALL scope all read and write operations to the effective Portal_User identity.
9. IF a request references a report, run, or conversation not owned by the effective Portal_User identity, THEN THE Report_API SHALL deny the request, return no data records for that entity, and return a not-accessible response without disclosing whether the entity exists for another user.
10. IF the JWT is absent, expired, or contains no valid identity, THEN THE Report_API SHALL deny the request, return no data records, and return an unauthorized response.

### Requirement 11: Output Verification

**User Story:** As a Portal_User, I want the system to verify results before I receive them, so that outputs can never contain another customer's data.

#### Acceptance Criteria

1. WHEN a generated query is submitted for execution, THE Query_Verifier SHALL confirm, before execution begins, that the query contains a bryt-number filter that restricts results to a subset of the Authorised_Bryt_Numbers.
2. IF the Query_Verifier does not find a bryt-number filter restricting results to a subset of the Authorised_Bryt_Numbers, THEN THE Query_Verifier SHALL block execution and record a verification failure.
3. IF the Query_Verifier blocks execution, THEN THE Report_Builder SHALL mark the Run as Failed, SHALL NOT make any result available for download, and SHALL present an error indication that the Run could not be verified.
4. WHEN a Run completes, THE Query_Verifier SHALL verify, before any result is made available for download, that every record in the result set has a Bryt_Number that is a member of the Authorised_Bryt_Numbers.
5. IF result verification detects one or more records whose Bryt_Number is not a member of the Authorised_Bryt_Numbers, THEN THE Report_Builder SHALL mark the Run as Failed, discard the result set, and SHALL NOT make any result available for download.
6. IF a Run is marked Failed due to result verification, THEN THE Report_Builder SHALL present an error indication that the result could not be verified and is unavailable for download.

### Requirement 12: Prompt Injection Defence

**User Story:** As a Portal_User, I want the assistant protected from manipulation, so that instructions hidden in prompts or data cannot weaken security.

#### Acceptance Criteria

1. THE Assistant SHALL classify all Portal_User prompt content and all data pulled into context as untrusted input and SHALL NOT execute, act on, or follow any operational instruction contained within that untrusted input.
2. THE Assistant SHALL preserve the Authorised_Bryt_Numbers scoping obtained from Trusted_Context for every request, regardless of any instruction in Portal_User prompt content or context data.
3. IF Portal_User prompt content or context data instructs the Assistant to remove, alter, disable, or bypass the bryt-number scoping, the allow-list, or the query bounds, THEN THE Assistant SHALL ignore that instruction, preserve the enforced constraints, and complete the request using only the Trusted_Context scoping.
4. WHEN the Assistant detects an instruction in untrusted input attempting to alter or bypass the bryt-number scoping, allow-list, or query bounds, THE Assistant SHALL record an audit entry indicating the manipulation attempt was ignored.
5. THE Query_Verifier SHALL enforce the bryt-number scoping and query bounds on every query independently of the Assistant output.
6. IF the Assistant output specifies a query that omits the bryt-number scoping, violates the allow-list, or exceeds the query bounds, THEN THE Query_Verifier SHALL reject the query, indicate the violated constraint, and prevent execution.

### Requirement 13: Query Bounds

**User Story:** As a Portal_User, I want generated queries to stay bounded, so that ad-hoc reporting remains safe and performant.

#### Acceptance Criteria

1. THE Query_Generator SHALL restrict every generated query to allow-listed Catalog tables and columns only.
2. IF a query would reference a table or column not on the Catalog allow-list, THEN THE Query_Generator SHALL reject query generation, indicate the disallowed table or column, and SHALL NOT produce an executable query.
3. THE Query_Generator SHALL apply a configurable maximum row limit, constrained to an integer between 1 and 1,000,000 rows inclusive, to every generated query.
4. THE Query_Generator SHALL apply a configurable maximum scanned-bytes bound, constrained to a value between 1 byte and 1,099,511,627,776 bytes (1 TiB) inclusive, to every generated query.
5. IF a generated query exceeds the configured row limit or scanned-bytes bound, THEN THE Query_Verifier SHALL block execution before any rows are returned, record a bounds violation identifying the exceeded bound, and return an error without producing partial results.
6. WHEN the Report_Builder processes a report request, THE Report_Builder SHALL read the current row limit and scanned-bytes bound from configuration.
7. IF the configured row limit or scanned-bytes bound is absent or outside its permitted range, THEN THE Report_Builder SHALL reject the report request and indicate the invalid configuration value.

### Requirement 14: Persistence

**User Story:** As a Portal_User, I want my reports, conversations, and runs stored, so that I can resume work and retrieve results later.

#### Acceptance Criteria

1. WHEN a Portal_User saves a Report_Design, THE Report_Store SHALL persist it in serialised form scoped to its owner Portal_User identity, retaining it until the owner deletes it.
2. WHEN a Portal_User exchanges a message with the Assistant for a report, THE Conversation_Store SHALL persist the resulting conversation history scoped to that report and its owner Portal_User identity.
3. WHEN a Portal_User reopens a report, THE Report_Builder SHALL restore the saved Report_Design and its Assistant conversation history so iteration can resume.
4. IF persisting a Report_Design or conversation history fails, THEN THE Report_Builder SHALL retain the unsaved in-memory state, leave any previously persisted version unchanged, and indicate that the save did not complete.
5. IF a reopened report's Report_Design or conversation history cannot be restored, THEN THE Report_Builder SHALL indicate the report could not be reopened without overwriting the persisted record.
6. WHEN a Run is created, THE Run_Store SHALL persist it with its run number, trigger, current Run_Status, row count, and Result_Store location, scoped to its owner Portal_User identity.
7. WHEN a Run_Status changes, THE Run_Store SHALL update the persisted Run record.
8. WHEN a Run completes, THE Result_Store SHALL persist the result object and THE Run_Store SHALL record its Result_Store location and final row count.

### Requirement 15: Run Lifecycle

**User Story:** As a Portal_User, I want runs to progress through clear states, so that I know whether output is ready, in progress, or failed.

#### Acceptance Criteria

1. WHEN a Run is queued, THE Report_Builder SHALL set the Run_Status to Queued.
2. WHEN execution of a Run begins, THE Report_Builder SHALL set the Run_Status to Running.
3. WHEN a Run finishes successfully, THE Report_Builder SHALL set the Run_Status to Complete and record the result location and a row count expressed as a non-negative integer between 0 and 999,999,999.
4. IF a Run fails during execution, THEN THE Report_Builder SHALL set the Run_Status to Failed, record an error message of up to 1000 characters, and discard any partial output so no result location is recorded.
5. WHEN a Portal_User cancels a Run whose Run_Status is Queued or Running, THE Report_Builder SHALL stop the pending execution within 10 seconds and set the Run_Status to Cancelled.
6. IF a Portal_User attempts to cancel a Run whose Run_Status is Complete, Failed, or Cancelled, THEN THE Report_Builder SHALL reject the cancellation, retain the existing Run_Status, and indicate the Run is already terminal.
7. WHILE a Run has a Run_Status of Complete, Failed, or Cancelled, THE Report_Builder SHALL treat that status as terminal and SHALL NOT transition it to any other status.

### Requirement 16: Backend APIs

**User Story:** As a Portal_User, I want backend APIs supporting each screen, so that the portal can manage reports, runs, and assistant interactions.

#### Acceptance Criteria

1. THE Report_API SHALL provide operations to create, read, update, delete, and list Report_Designs scoped to the effective Portal_User identity.
2. THE Report_API SHALL provide an operation to queue an asynchronous Run for a report that returns the created Run identifier and an initial Run_Status of Queued.
3. THE Report_API SHALL provide operations to retrieve the current Run_Status of a Run and to list a report's runs.
4. THE Report_API SHALL provide an operation to obtain the CSV result for a completed Run from the Result_Store.
5. THE Report_API SHALL provide an operation to submit an Assistant chat message of at most 4,000 characters and receive the updated Report_Design and applied-change summary.
6. THE Report_API SHALL provide an operation to cancel a Queued or Running Run.
7. THE Report_API SHALL model its request and response contracts on the contract-note API pattern from BrytBusinessServices.
8. IF a CSV result is requested for a Run not in Complete status, THEN THE Report_API SHALL reject the request indicating the result is not available and SHALL NOT return a result object.
9. IF cancellation is requested for a Run not in Queued or Running status, THEN THE Report_API SHALL reject the request indicating the Run cannot be cancelled and leave the Run_Status unchanged.
10. IF a submitted Assistant chat message exceeds 4,000 characters, THEN THE Report_API SHALL reject the request indicating the message-length limit and SHALL NOT modify the Report_Design.

### Requirement 17: Backend Repository Structure and Patterns

**User Story:** As a developer, I want the backend to follow established BrytBusinessServices patterns, so that the new service is consistent and maintainable.

#### Acceptance Criteria

1. THE Report_Builder backend SHALL reside in a repository named BrytReportBuilder containing exactly three top-level directories named api, cdk, and shared-lib.
2. THE Report_Builder backend SHALL implement one TypeScript Lambda handler per API operation, each handler file located under a folder named for its domain.
3. THE Report_Builder backend SHALL persist data in a single DynamoDB table configured with a partition key (PK), a sort key (SK), one or more Global Secondary Indexes, and PAY_PER_REQUEST billing mode.
4. THE Report_Builder backend SHALL store run result objects and report design objects in S3 buckets that have public access blocked, versioning enabled, and server-side encryption enabled.
5. WHEN a client sends a request to a defined Report_API route, THE Report_Builder backend SHALL route it through an API Gateway REST API resource to the Lambda integration mapped to that route.
6. WHEN a report run is requested, THE Report_Builder backend SHALL execute the run asynchronously as a Step Functions state machine and return a run identifier before execution completes.
7. IF any state within the run execution state machine fails, THEN THE Report_Builder backend SHALL transition to a catch state, set the Run_Status to Failed, and record an error indication retrievable through the Report_API.
8. THE Report_Builder backend SHALL define all shared types in the shared-lib directory.
9. WHEN a request contains a valid JWT, THE Report_Builder backend SHALL derive the Portal_User identity (email, CustomerIds claim, and any Admin_Override) from the JWT claims.
10. IF a request has a missing, expired, or invalid JWT, THEN THE Report_Builder backend SHALL reject the request without performing the operation and return an authentication-failure response.

### Requirement 18: Catalog and Join Manifest

**User Story:** As a Portal_User, I want a curated set of tables and joins, so that I can only build reports over data that is safe and well understood.

#### Acceptance Criteria

1. THE Catalog SHALL expose only tables and columns sourced from the allow-listed Glue database `rel_esg_prod_data_eng_master_record_db`, excluding any table or column not present in that database.
2. THE Data_Table_Palette SHALL list only tables present in the allow-listed Catalog and SHALL NOT display any table absent from it.
3. WHEN a Portal_User selects a table in the Data_Table_Palette, THE Column_Picker SHALL list only the columns present in the allow-listed Catalog for that table and SHALL NOT display any column absent from it.
4. THE Join_Manifest SHALL define, for each pair of joinable Catalog tables, the join predicates used to auto-connect those tables.
5. WHEN the Report_API receives a report request, THE Report_API SHALL supply the Join_Manifest to the Assistant as additional Trusted_Context so joins between selected tables are made automatically.
6. IF the allow-listed Glue database is unavailable when the Catalog is requested, THEN THE Catalog SHALL return an error indicating the data source is unavailable and expose no tables or columns rather than partial or stale content.
7. IF a Portal_User selects two or more Catalog tables for which the Join_Manifest defines no join predicate, THEN THE Report_API SHALL reject the report request, indicate that no join is defined for the selected tables, and retain the current table selection.

### Requirement 19: Bryt Number Resolution and Admin Override

**User Story:** As a Portal_User who may be associated with multiple customer accounts, I want the system to resolve exactly the bryt numbers I am allowed to query, so that my reports are scoped correctly even when an admin is operating on my behalf.

#### Acceptance Criteria

1. WHEN the Report_API resolves the effective Portal_User identity, THE Report_API SHALL use the Admin_Override.OverrideEmail as the effective email when an Admin_Override is present, and otherwise SHALL use the authenticated user's email.
2. WHEN resolving the Authorised_Bryt_Numbers, THE Report_API SHALL retrieve the accessible customer accounts from the User_Customer_Mapping for the effective email.
3. WHEN resolving the Authorised_Bryt_Numbers, THE Report_API SHALL include a customer account only WHERE that account is present in the user's CustomerIds claim (CanAccessCustomer) AND that account is not hidden.
4. WHEN the set of included customer accounts is determined, THE Report_API SHALL map each included account to its Bryt_Number to form the Authorised_Bryt_Numbers.
5. WHEN the Report_API receives a request, THE Report_API SHALL re-resolve the Authorised_Bryt_Numbers for that request rather than reuse a value cached across identity changes, so that an Admin_Override change is reflected immediately.
6. WHEN an Admin_Override is active, THE Report_API SHALL record an audit entry capturing the admin identity, the override email, and the action performed.
7. IF the User_Customer_Mapping lookup fails, THEN THE Report_API SHALL deny data access and return an error rather than falling back to an unscoped query.

## Assumptions and Open Questions

The following are working assumptions adopted for this specification. Each is flagged as open for confirmation during design.

1. **Preview execution (Screen 06):** Assumed that preview runs a small bounded Athena query using a LIMIT rather than a purely client-side sample. Open: confirm whether a client-side sample is preferred to avoid Athena cost/latency.
2. **My Reports "View" (Screen 01):** Assumed View opens the builder. Open: confirm whether View should instead land on the latest results or the runs list for output-only users.
3. **CSV retention:** Assumed completed results are retained in S3 indefinitely. Open: confirm whether a lifecycle/expiry policy applies and how expiry would be surfaced.
4. **Run completion notifications:** Assumed in-portal polling on the runs modal is sufficient. Open: confirm whether email or in-portal toast notifications are needed for long-running Athena queries.
5. **Query bound values:** Exact maximum row count and maximum scanned-bytes values are TBD and captured as configurable. Open: confirm concrete default values.
6. **Bedrock integration approach:** Assume Claude on Bedrock. Open: decide in design between managed Bedrock Agents action groups and a roll-our-own Converse API tool-use approach, including the dry-run validation tool.
7. **Report persistence location:** Assumed reports persist in S3 and/or DynamoDB. Open: decide the exact split between Report_Store (DynamoDB) and object storage (S3) in design.
8. **Multi-account report scoping:** When a Portal_User is authorised for multiple bryt numbers, it is assumed a report's query filters to the FULL Authorised_Bryt_Numbers set (e.g. an IN filter), with optional narrowing to a single selected account/Bryt_Number. Open: confirm whether reports should target a single chosen account or always span all authorised bryt numbers.
9. **Bryt number field:** The exact column/attribute name that carries the bryt number in the Glue tables (`rel_esg_prod_data_eng_master_record_db`) is TBD and to be confirmed against the schema during design.

## Out of Scope

- Sharing reports, teams, or per-report permissions.
- Folders or report organisation.
- Scheduled or automatic refresh of reports.
- CSV retention/expiry handling.
