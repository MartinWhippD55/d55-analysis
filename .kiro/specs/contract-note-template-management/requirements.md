# Requirements Document

## Introduction

This document specifies the requirements for Estimate 1 of the Bryt Energy Contract Note Rework project. The system enables business users to manage PDF rendering templates for contract notes through the existing BrytAdminPortal, replacing the current developer-dependent SVG/HTML pipeline with a visual template management approach powered by pdf-me.

The solution covers template CRUD operations, a visual section editor, shared/reusable sections (including T&Cs), a rules engine for automated template selection, and a render pipeline that generates PDFs by rendering sections independently and stitching them together.

## Glossary

- **Admin_Portal**: The existing BrytAdminPortal Angular application used by Bryt Energy internal staff for administration tasks
- **Template**: A contract note PDF template composed of multiple ordered sections, with an associated selection rule
- **Section**: An independently editable portion of a template, defined as a pdf-me schema JSON structure containing positioned fields
- **Shared_Section**: A section marked as reusable across multiple templates (e.g., headers, footers, T&Cs)
- **Terms_And_Conditions_Document**: A Shared_Section designated as Terms and Conditions, managed through the same Section_Editor as other sections, and positioned as the final section(s) of a template
- **Section_Editor**: The embedded pdf-me visual designer component used to configure section layout and field placement
- **Template_List**: The ordered table of templates in the Admin Portal, where ordering determines rule evaluation priority
- **Rules_Engine**: The specification-pattern-based system for automated template selection, using a tree of logical and comparison operators
- **Specification**: A JSON-serialised rule tree composed of logical operators (AND, OR, NOT) and leaf comparison operators (EQUALS, LESS_THAN, MORE_THAN, IN)
- **Render_Pipeline**: The automated process that renders each section independently using @pdfme/generator and stitches the results using pdf-lib
- **Schema_JSON**: The pdf-me template definition containing a schemas array (one entry per page) with positioned field definitions including type, position, dimensions, and font
- **Business_User**: An authenticated Admin Portal user with appropriate Cognito group membership to manage contract note templates

## Requirements

### Requirement 1: Template Listing

**User Story:** As a Business_User, I want to view all contract note templates in an ordered list, so that I can understand which templates exist and their evaluation priority.

#### Acceptance Criteria

1. WHEN a Business_User navigates to the template management screen, THE Admin_Portal SHALL display all templates in a table ordered by evaluation priority
2. THE Admin_Portal SHALL display the template name, description, number of sections, and current priority order for each template in the Template_List
3. WHEN no templates exist, THE Admin_Portal SHALL display an empty state message indicating no templates have been configured

### Requirement 2: Template Creation

**User Story:** As a Business_User, I want to create new contract note templates, so that I can define new document layouts for different contract types.

#### Acceptance Criteria

1. WHEN a Business_User submits a valid template creation form, THE Admin_Portal SHALL create a new template with the provided name and description
2. THE Admin_Portal SHALL assign the newly created template to the lowest priority position in the Template_List
3. IF a Business_User submits a template creation form with a duplicate name, THEN THE Admin_Portal SHALL display a validation error indicating the name is already in use
4. IF a Business_User submits a template creation form with missing required fields, THEN THE Admin_Portal SHALL display validation errors for each missing field

### Requirement 3: Template Editing

**User Story:** As a Business_User, I want to edit existing templates, so that I can update template metadata and manage section composition.

#### Acceptance Criteria

1. WHEN a Business_User selects a template for editing, THE Admin_Portal SHALL display the template details form pre-populated with current values
2. WHEN a Business_User saves changes to a template, THE Admin_Portal SHALL persist the updated name and description
3. THE Admin_Portal SHALL display the list of sections belonging to the template in their configured order

### Requirement 4: Template Deletion

**User Story:** As a Business_User, I want to delete templates that are no longer needed, so that the template list remains current.

#### Acceptance Criteria

1. WHEN a Business_User requests deletion of a template, THE Admin_Portal SHALL prompt for confirmation before proceeding
2. WHEN a Business_User confirms template deletion, THE Admin_Portal SHALL remove the template and re-order remaining templates to maintain contiguous priority ordering
3. THE Admin_Portal SHALL not delete Shared_Sections when a template referencing them is deleted

### Requirement 5: Template Priority Ordering

**User Story:** As a Business_User, I want to reorder templates in the list, so that I can control which template rules are evaluated first during automated processing.

#### Acceptance Criteria

1. WHEN a Business_User changes the priority order of a template, THE Admin_Portal SHALL update the evaluation order of all affected templates
2. THE Admin_Portal SHALL persist the updated priority ordering across sessions
3. THE Render_Pipeline SHALL evaluate template rules in the order defined by the Template_List priority

### Requirement 6: Section Creation and Management

**User Story:** As a Business_User, I want to add, remove, and reorder sections within a template, so that I can compose the contract note document structure.

#### Acceptance Criteria

1. WHEN a Business_User adds a new section to a template, THE Admin_Portal SHALL create the section and append it to the end of the template's section list
2. WHEN a Business_User removes a section from a template, THE Admin_Portal SHALL remove the section association and re-order remaining sections
3. WHEN a Business_User reorders sections within a template, THE Admin_Portal SHALL persist the new section order
4. WHEN a Business_User adds a Shared_Section to a template, THE Admin_Portal SHALL create a reference to the shared section without duplicating its definition
5. THE Admin_Portal SHALL allow a Business_User to attach a Terms_And_Conditions_Document as the final section(s) of a template

### Requirement 7: Section Editor Integration

**User Story:** As a Business_User, I want to visually edit section layouts using the pdf-me designer, so that I can configure field placement without developer assistance.

#### Acceptance Criteria

1. WHEN a Business_User opens a section for editing, THE Admin_Portal SHALL display the Section_Editor in a modal window with the current section Schema_JSON loaded
2. THE Section_Editor SHALL support text, multiVariableText, and table schema types for field configuration
3. WHEN a Business_User saves changes in the Section_Editor, THE Admin_Portal SHALL persist the updated Schema_JSON for that section
4. THE Section_Editor SHALL allow configuration of field position (x, y coordinates), dimensions (width, height), font settings, and alignment for each field
5. IF the Section_Editor fails to load, THEN THE Admin_Portal SHALL display an error message and provide an option to retry

### Requirement 8: Shared Section Management

**User Story:** As a Business_User, I want to create and manage shared sections, so that common elements like headers and footers are reusable across templates.

#### Acceptance Criteria

1. WHEN a Business_User marks a section as shared, THE Admin_Portal SHALL make that section available for selection in all templates
2. WHEN a Business_User edits a Shared_Section, THE Admin_Portal SHALL apply the changes to all templates referencing that section
3. THE Admin_Portal SHALL display which templates reference a given Shared_Section
4. IF a Business_User attempts to delete a Shared_Section that is referenced by one or more templates, THEN THE Admin_Portal SHALL display a warning listing the affected templates and require confirmation

### Requirement 9: Terms and Conditions as Shared Sections

**User Story:** As a Business_User, I want to manage Terms and Conditions as shared sections, so that T&Cs can be reused across templates and positioned as the final section(s) of a contract note.

#### Acceptance Criteria

1. WHEN a Business_User creates a Shared_Section designated as Terms_And_Conditions, THE Admin_Portal SHALL make it available for attachment to any template
2. WHEN a Business_User attaches a Terms_And_Conditions_Document to a template, THE Admin_Portal SHALL position it as the final section(s) after all other sections
3. THE Admin_Portal SHALL allow a Business_User to edit Terms_And_Conditions sections using the same Section_Editor as other Shared_Sections
4. THE Admin_Portal SHALL allow multiple Terms_And_Conditions shared sections to exist, so that different contract types can reference different T&Cs

### Requirement 10: Rules Engine Configuration

**User Story:** As a Business_User, I want to configure selection rules for each template, so that the automated process can select the correct template based on contract data.

#### Acceptance Criteria

1. WHEN a Business_User opens the rules configuration for a template, THE Admin_Portal SHALL display the current Specification tree in an editable UI
2. THE Admin_Portal SHALL support logical operators AND, OR, and NOT for combining conditions in the Specification tree
3. THE Admin_Portal SHALL support comparison operators EQUALS, LESS_THAN, MORE_THAN, and IN as leaf nodes in the Specification tree
4. THE Admin_Portal SHALL serialise the configured Specification as a JSON tree structure with leftOperand and rightOperand for AND/OR nodes, a single operand for NOT nodes, and comparison values for leaf nodes
5. WHEN a Business_User saves a Specification, THE Admin_Portal SHALL validate the tree structure is well-formed before persisting
6. IF a Business_User saves a Specification with an incomplete tree (missing operands or comparison values), THEN THE Admin_Portal SHALL display validation errors indicating the incomplete nodes

### Requirement 11: Rules Engine Evaluation

**User Story:** As a Business_User, I want the automated pipeline to select the correct template using the configured rules, so that contract notes are generated with the appropriate layout.

#### Acceptance Criteria

1. WHEN contract data arrives for processing, THE Render_Pipeline SHALL evaluate template Specifications in Template_List priority order
2. WHEN a template's Specification evaluates to true against the contract data, THE Render_Pipeline SHALL select that template for rendering and stop evaluation
3. IF no template Specification matches the contract data, THEN THE Render_Pipeline SHALL log an error indicating no matching template was found
4. THE Render_Pipeline SHALL evaluate EQUALS by comparing a data field value to the specified value
5. THE Render_Pipeline SHALL evaluate IN by checking if a data field value exists within the specified set of values
6. THE Render_Pipeline SHALL evaluate LESS_THAN and MORE_THAN by numeric comparison of a data field value against the specified threshold

### Requirement 12: Section Rendering

**User Story:** As a Business_User, I want each template section to be rendered independently, so that sections with dynamic content (like tables spanning multiple pages) are handled correctly.

#### Acceptance Criteria

1. WHEN the Render_Pipeline processes a template, THE Render_Pipeline SHALL render each section independently using @pdfme/generator with the section's Schema_JSON and contract data
2. THE Render_Pipeline SHALL supply the configured font and plugin options (text, multiVariableText, table) to @pdfme/generator for each section render
3. IF a section render fails, THEN THE Render_Pipeline SHALL log the error with section identifier and template context, and halt processing for that contract note

### Requirement 13: PDF Stitching

**User Story:** As a Business_User, I want rendered sections to be combined into a single PDF document, so that the final contract note is a complete, cohesive document.

#### Acceptance Criteria

1. WHEN all sections of a template have been rendered successfully, THE Render_Pipeline SHALL stitch the rendered section PDFs together in section order using pdf-lib
2. THE Render_Pipeline SHALL include the Terms_And_Conditions_Document pages as the final pages in the stitched output
3. WHEN stitching is complete, THE Render_Pipeline SHALL write the final PDF to the configured S3 output location

### Requirement 14: S3-Triggered Processing

**User Story:** As a Business_User, I want the pipeline to trigger automatically when contract data arrives in S3, so that contract notes are generated without manual intervention.

#### Acceptance Criteria

1. WHEN an XML file is dropped into the configured S3 input bucket, THE Render_Pipeline SHALL initiate the contract note generation process
2. THE Render_Pipeline SHALL parse the XML input into a JSON data structure for use in template rendering
3. WHEN rendering completes successfully, THE Render_Pipeline SHALL write the output PDF to the configured S3 output bucket
4. IF processing fails at any stage, THEN THE Render_Pipeline SHALL log the failure with contextual details and not write a partial output to the S3 output bucket

### Requirement 15: Authentication and Authorisation

**User Story:** As a Business_User, I want template management to be restricted to authorised users, so that only appropriate staff can modify contract note templates.

#### Acceptance Criteria

1. THE Admin_Portal SHALL restrict access to template management screens to authenticated users with the appropriate Cognito group membership
2. WHEN an unauthenticated user attempts to access template management, THE Admin_Portal SHALL redirect to the login flow
3. WHEN an authenticated user without the required group membership attempts to access template management, THE Admin_Portal SHALL display an access denied message

### Requirement 16: Section Version History

**User Story:** As a Business_User, I want to view and revert to previous versions of a section's design, so that I can undo mistakes or compare changes over time.

#### Acceptance Criteria

1. WHEN a Business_User saves changes to a section in the Section_Editor, THE Admin_Portal SHALL create a new version of the section's Schema_JSON rather than overwriting the previous version
2. THE Admin_Portal SHALL display a version history for each section, showing version number, timestamp, and the user who made the change
3. WHEN a Business_User selects a previous version from the history, THE Admin_Portal SHALL display a preview or allow the user to open it in the Section_Editor as read-only
4. WHEN a Business_User confirms reverting to a previous version, THE Admin_Portal SHALL create a new version with the content of the selected historical version (rather than deleting intermediate versions)
5. THE Admin_Portal SHALL retain all versions indefinitely (no automatic purging)

### Requirement 17: Template Version History

**User Story:** As a Business_User, I want to view the change history of a template's configuration (sections added/removed/reordered, metadata changes), so that I can understand what changed and when.

#### Acceptance Criteria

1. WHEN a Business_User modifies a template (adds/removes/reorders sections, changes name/description), THE Admin_Portal SHALL record a change event with timestamp, user, and description of what changed
2. THE Admin_Portal SHALL display a change log for each template, showing the chronological list of changes
3. THE change log SHALL be accessible from the template edit screen
