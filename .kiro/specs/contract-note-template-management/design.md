# Design Document: Contract Note Template Management

## Overview

This design covers Estimate 1 of the Bryt Energy Contract Note Rework: a template management system within the existing BrytAdminPortal that replaces the current developer-dependent SVG/HTML pipeline with a visual, business-user-managed approach using pdf-me.

The system introduces:
1. An Angular module in the Admin Portal for CRUD operations on templates, sections, and shared sections
2. A rules engine UI for configuring specification-pattern-based template selection
3. An embedded pdf-me Designer (React component via Web Component wrapper) for visual section editing
4. A serverless render pipeline, orchestrated by an AWS Step Functions state machine, that evaluates rules, selects a section variant per section, renders sections with @pdfme/generator, and stitches PDFs with pdf-lib
5. DynamoDB for template/section/variant metadata and S3 for schema JSON storage

The architecture maintains the existing S3-triggered pipeline entry point but replaces the internal rendering mechanism entirely.

### Scope changes since the initial estimate

This design was extended after the client playback of Estimate 1. Three changes are folded in:

1. **Section version publishing (Requirement 18)** — shared/linked section edits no longer propagate implicitly. Each template's section reference now resolves to a *pinned version*, and a new *publish* action pushes a chosen version to the linked templates (all or a selected subset).
2. **Section variants with rules (Requirement 19)** — a section can hold multiple layout variants, each guarded by a rule reusing the existing specification engine. At render time the first matching variant is rendered, with a default fallback.
3. **Step Functions orchestration (Requirement 20)** — the render pipeline moves from a single Lambda to a Step Functions state machine with a per-section map state. This isolates and retries section work (now more involved because of variant selection) and improves observability for multi-section documents.

Landing/list pages (Template List, Shared Sections Library) were already part of the design as full-page screens; Requirement 21 makes the page-vs-modal distinction explicit and adds a variants list to the template edit page.

## Architecture

### High-Level System Architecture

```mermaid
graph TB
    subgraph Admin Portal - Angular
        TL[Template List Screen]
        TE[Template Edit Screen]
        RC[Rules Configuration Screen]
        SE[Section Editor Modal - pdf-me Designer]
        SL[Shared Sections Library]
    end

    subgraph Admin Portal API - Lambda + API Gateway
        TAPI[Template API]
        SAPI[Section API]
        RAPI[Rules API]
    end

    subgraph Storage
        DDB[(DynamoDB - Metadata)]
        S3S[S3 - Schema JSON]
    end

    subgraph Render Pipeline - Step Functions
        S3IN[S3 Input Bucket - XML]
        SFN[Render State Machine]
        PARSE[Parse XML - Lambda]
        SELECT[Select Template - Lambda]
        MAP[Map state: per section]
        RENDERSEC[Select Variant + Render Section - Lambda]
        STITCH[Stitch PDF - Lambda]
        S3OUT[S3 Output Bucket - PDF]
        S3ERR[S3 Error Bucket]
    end

    TL --> TAPI
    TE --> TAPI
    TE --> SAPI
    RC --> RAPI
    SE --> SAPI
    SL --> SAPI

    TAPI --> DDB
    SAPI --> DDB
    SAPI --> S3S
    RAPI --> DDB

    S3IN -->|S3 Event| SFN
    SFN --> PARSE
    PARSE --> SELECT
    SELECT --> MAP
    MAP --> RENDERSEC
    RENDERSEC --> STITCH
    SELECT --> DDB
    RENDERSEC --> DDB
    RENDERSEC --> S3S
    STITCH --> S3OUT
    SFN --> S3ERR
```

### Key Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| pdf-me Designer embedding | Web Component wrapper around React | Avoids Angular-React bridge library overhead; isolates React dependency; standard web platform approach |
| Template metadata storage | DynamoDB | Matches existing Admin Portal pattern; supports fast ordered queries via GSI |
| Schema JSON storage | S3 | Schema JSON can be large; S3 is cost-effective for blob storage; decouples metadata from content |
| Render pipeline | Step Functions state machine with a per-section Map state | Section rendering now includes per-section variant rule evaluation and can fan out over many sections; a state machine isolates and retries each section, handles large multi-section documents beyond a single Lambda's limits, and gives per-section observability. (Supersedes the initial single-Lambda decision.) |
| Rules engine | Server-side evaluation in render steps | Rules (template selection and variant selection) evaluate against runtime contract data; no client-side evaluation needed |
| Section version resolution | Pinned version per template reference | Templates resolve a specific section version rather than "latest", so a new version only goes live via an explicit publish action |
| Section variants | Ordered variants, each with a rule + default fallback | Reuses the specification engine; lets one section slot render alternatives without multiplying whole templates |
| Section stitching | pdf-lib | Already proven in PoC; lightweight; handles page concatenation well |
| Priority ordering | Explicit `priority` integer field | Simple to reorder; DynamoDB GSI on priority enables ordered scan |

### Deployment Architecture

The solution deploys as:
- New Angular module within existing Admin Portal (same CloudFront + S3 hosting)
- New Lambda functions behind existing API Gateway
- New DynamoDB table for template/section metadata
- New S3 bucket for schema JSON definitions
- Modified render pipeline Lambda replacing the CreateHtml + html-to-pdf steps

## Components and Interfaces

### Frontend Components (Angular)

```mermaid
graph TD
    subgraph ContractNoteModule
        TLC[TemplateListComponent]
        TEC[TemplateEditComponent]
        RCC[RulesConfigComponent]
        SEC[SectionEditorComponent - Web Component host]
        SSC[SharedSectionsComponent]
        SSTD[SharedSectionDetailComponent]
    end

    subgraph Services
        TS[TemplateService]
        SS[SectionService]
        RS[RulesService]
    end

    TLC --> TS
    TEC --> TS
    TEC --> SS
    RCC --> RS
    SEC --> SS
    SSC --> SS
    SSTD --> SS
```

#### TemplateListComponent
- Displays ordered table of templates (name, description, section count, priority)
- Drag-and-drop or up/down buttons for reordering
- Actions: Create, Edit, Delete, Configure Rules
- Empty state when no templates exist

#### TemplateEditComponent
- Form for template name and description
- Section list showing ordered sections with add/remove/reorder
- Ability to add new section, add existing shared section, or attach T&Cs
- Section click opens SectionEditorComponent modal
- For sections with variants, an inline list of variants (name, rule summary, default badge) rendered on the page (not only in a modal), with add/reorder/edit-rule actions
- A "pinned version" indicator per section showing whether an update is available

#### RulesConfigComponent
- Visual tree editor for specification pattern
- Node types: AND, OR, NOT (logical), EQUALS, LESS_THAN, MORE_THAN, IN (comparison)
- Add/remove nodes, configure leaf values (field name, operator, value)
- Validation before save (well-formed tree check)

#### SectionEditorComponent
- Hosts the pdf-me Designer React component via a custom Web Component (`<pdfme-designer>`)
- Receives schema JSON on open, emits updated schema JSON on save
- Modal presentation with save/cancel actions

#### SharedSectionsComponent
- List of all shared sections with name, type (standard/T&C), and reference count
- Detail panel showing which templates reference a shared section
- Create/edit/delete actions with referencing-template warnings

#### SectionPublishComponent
- Launched from the version history for a section
- Lists the templates linked to the section, each showing its current pinned version and whether an update is available
- Lets the user publish a chosen version (defaulting to latest) to all linked templates
- Confirms the change and reports the templates updated

#### SectionVariantsComponent
- Manages the ordered variants within a section (add, reorder, set default, delete)
- Each variant links to the SectionEditorComponent for its layout and to the RulesConfigComponent for its Variant_Rule
- Reuses the same rule editor and validation as template selection rules

### Backend API (Lambda Functions)

#### Template API (`lambdas-rest-api/contract-note-templates/`)

| Method | Path | Handler | Description |
|--------|------|---------|-------------|
| GET | /contract-note-templates | list-templates | Returns all templates ordered by priority |
| POST | /contract-note-templates | create-template | Creates template at lowest priority |
| GET | /contract-note-templates/{id} | get-template | Returns template with section list |
| PUT | /contract-note-templates/{id} | update-template | Updates name/description |
| DELETE | /contract-note-templates/{id} | delete-template | Deletes template, reorders remaining |
| PUT | /contract-note-templates/reorder | reorder-templates | Batch update priority order |

#### Section API (`lambdas-rest-api/contract-note-sections/`)

| Method | Path | Handler | Description |
|--------|------|---------|-------------|
| GET | /contract-note-templates/{id}/sections | list-sections | Returns sections for template in order |
| POST | /contract-note-templates/{id}/sections | add-section | Adds section to template |
| DELETE | /contract-note-templates/{id}/sections/{sectionId} | remove-section | Removes section from template |
| PUT | /contract-note-templates/{id}/sections/reorder | reorder-sections | Reorders sections within template |
| GET | /contract-note-sections/{id}/schema | get-section-schema | Returns schema JSON from S3 |
| PUT | /contract-note-sections/{id}/schema | save-section-schema | Saves schema JSON to S3 |
| GET | /contract-note-sections/{id}/versions | list-section-versions | Returns version history for a section |
| GET | /contract-note-sections/{id}/versions/{versionId} | get-section-version | Returns a specific historical version's schema |
| POST | /contract-note-sections/{id}/versions/{versionId}/revert | revert-section-version | Creates a new version from a historical version |
| GET | /contract-note-sections/{id}/linked-templates | get-linked-templates | Returns templates linked to a section with their pinned version + whether an update is available |
| POST | /contract-note-sections/{id}/versions/{versionId}/publish | publish-section-version | Updates the pinned version of all linked templates to the chosen version |
| GET | /contract-note-sections/{id}/variants | list-section-variants | Returns the section's variants in evaluation order |
| POST | /contract-note-sections/{id}/variants | add-section-variant | Adds a variant to the section |
| PUT | /contract-note-sections/{id}/variants/reorder | reorder-section-variants | Reorders variant evaluation order |
| PUT | /contract-note-sections/{id}/variants/{variantId} | update-section-variant | Updates variant metadata (name, isDefault) |
| DELETE | /contract-note-sections/{id}/variants/{variantId} | delete-section-variant | Removes a variant |
| GET | /contract-note-sections/{id}/variants/{variantId}/rule | get-variant-rule | Returns the variant's specification |
| PUT | /contract-note-sections/{id}/variants/{variantId}/rule | save-variant-rule | Validates and saves the variant's specification |
| GET | /contract-note-sections/shared | list-shared-sections | Lists all shared sections |
| POST | /contract-note-sections/shared | create-shared-section | Creates a new shared section |
| PUT | /contract-note-sections/shared/{id} | update-shared-section | Updates shared section metadata |
| DELETE | /contract-note-sections/shared/{id} | delete-shared-section | Deletes shared section (with ref check) |
| GET | /contract-note-sections/shared/{id}/references | get-shared-section-refs | Returns templates referencing this section |

#### Rules API (`lambdas-rest-api/contract-note-rules/`)

| Method | Path | Handler | Description |
|--------|------|---------|-------------|
| GET | /contract-note-templates/{id}/rule | get-rule | Returns specification JSON for template |
| PUT | /contract-note-templates/{id}/rule | save-rule | Validates and saves specification JSON |

### Render Pipeline (Step Functions State Machine)

The `render-contract-note` state machine replaces the existing CreateHtml + html-to-pdf steps. It is triggered by the S3 input event (via EventBridge / S3 notification) and coordinates a set of small single-purpose Lambdas:

```
Input: S3 object key for the dropped XML
States:
  1. ParseInput (Lambda)      - parse XML to JSON contract data
  2. SelectTemplate (Lambda)  - fetch templates ordered by priority; evaluate each
                                specification against contract data; first match wins
  3. RenderSections (Map)     - for each section of the matched template, in parallel:
         a. resolve the section reference's Pinned_Version
         b. if the section has variants, evaluate each Variant_Rule in order and
            select the first match (else the default variant)
         c. fetch that variant version's schema JSON from S3
         d. render the section via @pdfme/generator -> section PDF
  4. Stitch (Lambda)          - concatenate section PDFs in order via pdf-lib
  5. WriteOutput (Lambda)     - write final PDF to the output S3 bucket
Catch (any state):
     HandleFailure (Lambda)   - write an error record to the error bucket; no partial output
Output: Stitched PDF in S3
```

The Map state processes sections independently with per-section retry, so a transient failure rendering one section does not require re-running the whole document, and documents with many sections are not bound by a single Lambda's execution time or memory.

### Web Component: pdfme-designer

A thin Web Component wrapper that:
1. Loads the React pdf-me Designer component
2. Accepts `schema-json` attribute (or property) for initial state
3. Dispatches `schema-save` CustomEvent with updated schema JSON
4. Handles lifecycle (mount/unmount React root on connectedCallback/disconnectedCallback)

Built as a separate bundle (React + pdf-me Designer), loaded on-demand when the section editor modal opens.


## Data Models

### DynamoDB Table: `ContractNoteTemplates`

Single-table design with PK/SK pattern.

#### Template Record

| Attribute | Type | Description |
|-----------|------|-------------|
| PK | String | `TEMPLATE#{templateId}` |
| SK | String | `METADATA` |
| templateId | String | UUID |
| name | String | Template display name (unique) |
| description | String | Template description |
| priority | Number | Evaluation priority (1 = highest) |
| sectionCount | Number | Denormalised count of sections |
| createdAt | String | ISO 8601 timestamp |
| updatedAt | String | ISO 8601 timestamp |
| createdBy | String | Cognito username |

#### Section Record (template-owned)

| Attribute | Type | Description |
|-----------|------|-------------|
| PK | String | `TEMPLATE#{templateId}` |
| SK | String | `SECTION#{sortOrder}#{sectionId}` |
| sectionId | String | UUID |
| name | String | Section display name |
| sortOrder | Number | Position within template |
| isShared | Boolean | Whether this references a shared section |
| sharedSectionId | String | (optional) Reference to shared section |
| schemaS3Key | String | S3 key for schema JSON (default variant, when no variants defined) |
| pinnedVersionId | String | (optional) The section version this reference resolves to at render time; when absent, resolves to latest |
| createdAt | String | ISO 8601 timestamp |
| updatedAt | String | ISO 8601 timestamp |

#### Shared Section Record

| Attribute | Type | Description |
|-----------|------|-------------|
| PK | String | `SHARED_SECTION#{sectionId}` |
| SK | String | `METADATA` |
| sectionId | String | UUID |
| name | String | Section display name |
| isTermsAndConditions | Boolean | Whether this is a T&C section |
| schemaS3Key | String | S3 key for schema JSON |
| createdAt | String | ISO 8601 timestamp |
| updatedAt | String | ISO 8601 timestamp |
| createdBy | String | Cognito username |

#### Shared Section Reference Record

| Attribute | Type | Description |
|-----------|------|-------------|
| PK | String | `SHARED_SECTION#{sectionId}` |
| SK | String | `REF#{templateId}` |
| templateId | String | Template using this shared section |
| templateName | String | Denormalised for display |
| pinnedVersionId | String | The section version this template currently resolves to (updated by a publish action) |

#### Section Variant Record

| Attribute | Type | Description |
|-----------|------|-------------|
| PK | String | `SECTION#{sectionId}` |
| SK | String | `VARIANT#{variantOrder}#{variantId}` |
| variantId | String | UUID |
| name | String | Variant display name |
| variantOrder | Number | Evaluation order within the section (first match wins) |
| isDefault | Boolean | Whether this variant is the fallback when no rule matches |
| schemaS3Key | String | S3 key for this variant's current schema JSON |
| specification | Map | (optional) Variant_Rule specification tree; absent for the default variant |
| createdAt | String | ISO 8601 timestamp |
| updatedAt | String | ISO 8601 timestamp |

Variants have their own version history: Section Version records are keyed by `{sectionId}#{variantId}` so each variant is versioned independently. A section with no Section Variant records behaves as a single implicit variant using the section's own `schemaS3Key` (backwards compatible).

#### Section Version Record

| Attribute | Type | Description |
|-----------|------|-------------|
| PK | String | `SECTION_VERSION#{sectionId}#{variantId}` |
| SK | String | `VERSION#{timestamp}` |
| versionId | String | UUID |
| sectionId | String | Section this version belongs to |
| variantId | String | Variant this version belongs to (`default` for sections without variants) |
| schemaS3Key | String | S3 key for this version's schema JSON |
| createdAt | String | ISO 8601 timestamp |
| createdBy | String | Cognito username |
| description | String | (optional) Change description |

#### Template Change Log Record

| Attribute | Type | Description |
|-----------|------|-------------|
| PK | String | `TEMPLATE#{templateId}` |
| SK | String | `CHANGELOG#{timestamp}` |
| changeType | String | section-added, section-removed, section-reordered, metadata-updated, rule-updated |
| description | String | Human-readable description of the change |
| createdAt | String | ISO 8601 timestamp |
| createdBy | String | Cognito username |

#### Rule Record

| Attribute | Type | Description |
|-----------|------|-------------|
| PK | String | `TEMPLATE#{templateId}` |
| SK | String | `RULE` |
| specification | Map | JSON specification tree (see below) |
| updatedAt | String | ISO 8601 timestamp |
| updatedBy | String | Cognito username |

#### GSI: PriorityIndex

| Key | Attribute |
|-----|-----------|
| GSI PK | `ALL_TEMPLATES` (constant) |
| GSI SK | `priority` (Number) |

Enables: Query all templates ordered by priority in a single query.

### Specification Tree JSON Structure

```json
{
  "type": "AND",
  "leftOperand": {
    "type": "EQUALS",
    "field": "offer.producttype",
    "value": "Fixed"
  },
  "rightOperand": {
    "type": "OR",
    "leftOperand": {
      "type": "IN",
      "field": "offer.region",
      "values": ["North", "South"]
    },
    "rightOperand": {
      "type": "MORE_THAN",
      "field": "offer.mpancount",
      "value": 5
    }
  }
}
```

Node types:
- **AND/OR**: `{ type, leftOperand, rightOperand }` — binary logical
- **NOT**: `{ type, operand }` — unary logical
- **EQUALS**: `{ type, field, value }` — exact match
- **LESS_THAN/MORE_THAN**: `{ type, field, value }` — numeric comparison
- **IN**: `{ type, field, values }` — set membership

### S3 Schema JSON Structure

Stored at `s3://{schema-bucket}/{sectionId}/schema.json`:

```json
{
  "schemas": [
    [
      {
        "name": "customerName",
        "type": "text",
        "position": { "x": 20, "y": 50 },
        "width": 150,
        "height": 12,
        "fontSize": 10,
        "fontName": "NotoSans",
        "alignment": "left"
      },
      {
        "name": "propertyTable",
        "type": "table",
        "position": { "x": 10, "y": 100 },
        "width": 190,
        "height": 400
      }
    ]
  ]
}
```

Each entry in the `schemas` array represents one page of the section. Fields within a page define the pdf-me schema elements.

### TypeScript Interfaces

```typescript
// Specification Tree
type LogicalOperator = 'AND' | 'OR' | 'NOT';
type ComparisonOperator = 'EQUALS' | 'LESS_THAN' | 'MORE_THAN' | 'IN';

interface AndOrNode {
  type: 'AND' | 'OR';
  leftOperand: SpecificationNode;
  rightOperand: SpecificationNode;
}

interface NotNode {
  type: 'NOT';
  operand: SpecificationNode;
}

interface ComparisonNode {
  type: 'EQUALS' | 'LESS_THAN' | 'MORE_THAN';
  field: string;
  value: string | number;
}

interface InNode {
  type: 'IN';
  field: string;
  values: (string | number)[];
}

type SpecificationNode = AndOrNode | NotNode | ComparisonNode | InNode;

// Template
interface Template {
  templateId: string;
  name: string;
  description: string;
  priority: number;
  sectionCount: number;
  createdAt: string;
  updatedAt: string;
  createdBy: string;
}

// Section
interface Section {
  sectionId: string;
  name: string;
  sortOrder: number;
  isShared: boolean;
  sharedSectionId?: string;
  schemaS3Key: string;
  pinnedVersionId?: string; // version this reference resolves to at render time
}

// Section Variant
interface SectionVariant {
  variantId: string;
  name: string;
  variantOrder: number;   // evaluation order; first match wins
  isDefault: boolean;     // fallback when no rule matches
  schemaS3Key: string;
  specification?: SpecificationNode; // Variant_Rule; absent for the default variant
}

// A template's link to a section, with the version it currently resolves to
interface SectionReference {
  templateId: string;
  templateName: string;
  pinnedVersionId: string;
  updateAvailable: boolean; // pinned version is older than the section's latest
}

// Shared Section
interface SharedSection {
  sectionId: string;
  name: string;
  isTermsAndConditions: boolean;
  schemaS3Key: string;
  referenceCount?: number;
}
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Template listing returns priority-ordered results

*For any* set of templates stored in the system, listing all templates SHALL return them sorted by priority in ascending order (lowest priority number first).

**Validates: Requirements 1.1, 1.2**

### Property 2: Template creation round-trip

*For any* valid template name and description, creating a template and then fetching it by ID SHALL return the same name and description that were provided.

**Validates: Requirements 2.1**

### Property 3: New templates get lowest priority

*For any* existing set of N templates, creating a new template SHALL assign it priority N+1 (appended to end).

**Validates: Requirements 2.2**

### Property 4: Duplicate name rejection

*For any* template name that already exists in the system, attempting to create a new template with that same name SHALL fail with a validation error.

**Validates: Requirements 2.3**

### Property 5: Required field validation

*For any* template creation request with one or more missing required fields, the system SHALL return validation errors identifying exactly the missing fields.

**Validates: Requirements 2.4**

### Property 6: Template update round-trip

*For any* existing template and valid updated name/description, saving the update and then fetching the template SHALL return the new values.

**Validates: Requirements 3.1, 3.2**

### Property 7: Sections returned in sort order

*For any* template with sections, fetching the template's sections SHALL return them ordered by sortOrder ascending.

**Validates: Requirements 3.3**

### Property 8: Template deletion maintains contiguous priority

*For any* set of N templates with contiguous priorities 1..N, deleting one template SHALL result in the remaining N-1 templates having contiguous priorities 1..N-1.

**Validates: Requirements 4.2**

### Property 9: Shared sections survive template deletion

*For any* template that references shared sections, deleting that template SHALL not affect the existence or content of those shared sections.

**Validates: Requirements 4.3**

### Property 10: Priority reorder produces contiguous ordering

*For any* valid reorder operation on templates, the resulting priorities SHALL be contiguous integers starting from 1, and the relative order SHALL match the requested order.

**Validates: Requirements 5.1, 5.2**

### Property 11: Section addition appends to end

*For any* template with N sections, adding a new section SHALL result in N+1 sections where the new section has the highest sortOrder.

**Validates: Requirements 6.1**

### Property 12: Section removal maintains contiguous order

*For any* template with N sections, removing one section SHALL result in N-1 sections with contiguous sortOrder values.

**Validates: Requirements 6.2**

### Property 13: Shared section reference (no duplication)

*For any* shared section added to a template, the section record SHALL contain a reference (sharedSectionId) to the shared section and SHALL use the shared section's schemaS3Key rather than creating a copy.

**Validates: Requirements 6.4**

### Property 14: T&C sections positioned at end

*For any* template with both regular sections and T&C sections, all T&C sections SHALL have a sortOrder greater than all non-T&C sections.

**Validates: Requirements 6.5, 9.2**

### Property 15: Schema JSON save/load round-trip

*For any* valid schema JSON, saving it for a section and then loading it SHALL return an equivalent JSON structure.

**Validates: Requirements 7.1, 7.3**

### Property 16: Shared section visibility

*For any* section marked as shared (including T&C sections), it SHALL appear in the shared sections listing available to all templates.

**Validates: Requirements 8.1, 9.1, 9.4**

### Property 17: Shared section edit propagation

*For any* shared section referenced by multiple templates, updating the shared section's schema SHALL be reflected when loading the schema for any of those templates' sections.

**Validates: Requirements 8.2**

### Property 18: Shared section reference tracking

*For any* shared section, querying its references SHALL return exactly the set of templates that include it.

**Validates: Requirements 8.3**

### Property 19: Referenced shared section deletion protection

*For any* shared section that is referenced by one or more templates, deletion SHALL be blocked (or require explicit force) and the response SHALL list the referencing templates.

**Validates: Requirements 8.4**

### Property 20: Specification tree serialization round-trip

*For any* valid specification tree (composed of AND, OR, NOT, EQUALS, LESS_THAN, MORE_THAN, IN nodes), serializing to JSON and deserializing SHALL produce an equivalent tree.

**Validates: Requirements 10.2, 10.3, 10.4**

### Property 21: Specification validation rejects malformed trees

*For any* specification tree that is structurally incomplete (AND/OR missing operands, comparison nodes missing field or value), validation SHALL fail and identify the incomplete nodes.

**Validates: Requirements 10.5**

### Property 22: First-match-wins template selection

*For any* ordered set of templates with specifications, and any contract data, the render pipeline SHALL select the template with the lowest priority number whose specification evaluates to true, and no other.

**Validates: Requirements 5.3, 11.1, 11.2**

### Property 23: Specification operator evaluation correctness

*For any* contract data object and specification leaf node: EQUALS returns true iff field equals value; IN returns true iff field value is in the values set; LESS_THAN returns true iff field value < threshold; MORE_THAN returns true iff field value > threshold.

**Validates: Requirements 11.4, 11.5, 11.6**

### Property 24: Independent section rendering produces valid PDF

*For any* section with a valid schema JSON and complete input data, rendering the section with @pdfme/generator SHALL produce a non-empty valid PDF buffer.

**Validates: Requirements 12.1**

### Property 25: PDF stitching preserves page count

*For any* list of valid PDF buffers, stitching them together in order using pdf-lib SHALL produce a single PDF whose total page count equals the sum of the individual PDFs' page counts.

**Validates: Requirements 13.1, 13.2**

### Property 26: XML-to-JSON parsing produces valid data structure

*For any* valid contract XML input, parsing SHALL produce a JSON object containing all the fields present in the XML.

**Validates: Requirements 14.2**

### Property 27: Pipeline failure produces no output

*For any* contract note processing that fails at any stage, the output S3 bucket SHALL NOT contain a file for that contract note.

**Validates: Requirements 14.4**

### Property 28: Section save creates a new version

*For any* section save operation, the system SHALL create a new version record and preserve the previous version's schema JSON. The version count SHALL increase by exactly 1.

**Validates: Requirements 16.1, 16.5**

### Property 29: Section version revert creates new version (not destructive)

*For any* revert operation to a historical version V, the system SHALL create a new version N+1 with the content of version V, and all intermediate versions SHALL remain accessible.

**Validates: Requirements 16.4**

### Property 30: Template change log records all modifications

*For any* template modification (section add/remove/reorder, metadata update, rule change), the system SHALL record a change log entry with timestamp and user.

**Validates: Requirements 17.1, 17.2**

### Property 31: New section version does not change pinned versions

*For any* section referenced by one or more templates, creating a new section version SHALL leave every linked template's pinnedVersionId unchanged until a publish action is performed.

**Validates: Requirements 8.2, 18.2**

### Property 32: Publish updates all linked templates

*For any* publish of version V for a section, every template linked to that section SHALL have pinnedVersionId = V afterwards.

**Validates: Requirements 18.3, 18.4**

### Property 33: Update-available flag correctness

*For any* linked template, the update-available flag SHALL be true if and only if its pinnedVersionId is older than the section's latest version.

**Validates: Requirements 18.5**

### Property 34: Render resolves the pinned version

*For any* section render, the schema JSON used SHALL be the one belonging to the template reference's pinnedVersionId (not necessarily the latest version).

**Validates: Requirements 18.6**

### Property 35: Variant first-match-wins with default fallback

*For any* section with ordered variants and any contract data, the render SHALL select the first variant (in variant order) whose Variant_Rule evaluates to true; if none match, it SHALL select the designated default variant.

**Validates: Requirements 19.4, 19.5**

### Property 36: Section with no variants preserves single-variant behaviour

*For any* section with no variant records defined, rendering SHALL use the section's own schema (implicit single variant), identical to pre-variant behaviour.

**Validates: Requirements 19.8**

### Property 37: No-match with no default halts

*For any* section that has variants, no matching variant, and no designated default, the render pipeline SHALL log an error and produce no output PDF.

**Validates: Requirements 19.6**

### Property 38: Per-section failure isolation and no partial output

*For any* render run where a section-level Map state fails after its configured retries, the state machine SHALL route to the failure state and the output bucket SHALL NOT contain a PDF for that contract note.

**Validates: Requirements 20.2, 20.3**

## Error Handling

### Frontend Error Handling

| Scenario | Handling |
|----------|----------|
| API request failure (network) | Display toast notification with retry option; preserve form state |
| Validation errors (400) | Highlight invalid fields; display field-level error messages |
| Unauthorized (401) | Redirect to login flow via existing auth guard mechanism |
| Forbidden (403) | Display access denied message |
| Not found (404) | Display "template not found" message; redirect to list |
| Server error (500) | Display generic error toast; log to console; offer retry |
| Section Editor fails to load | Display error state in modal with retry button |
| Drag-and-drop reorder fails | Revert to previous order; display error notification |

### Backend Error Handling

| Scenario | Handling | HTTP Status |
|----------|----------|-------------|
| Missing required fields | Return field-level validation errors | 400 |
| Duplicate template name | Return specific duplicate error | 409 |
| Template not found | Return not found error | 404 |
| Shared section has references (on delete) | Return reference list | 409 |
| Malformed specification tree | Return validation errors with node paths | 400 |
| DynamoDB write failure | Log error, return 500 | 500 |
| S3 read/write failure | Log error, return 500 | 500 |
| Invalid schema JSON format | Return validation error | 400 |

### Render Pipeline Error Handling

| Scenario | Handling |
|----------|----------|
| No matching template | Log error with contract data summary to error bucket; halt |
| Section schema fetch fails (S3) | Log error with section ID and template ID; halt; write to error bucket |
| Section render fails (pdf-me) | Log error with section ID, template ID, and pdf-me error; halt; write to error bucket |
| PDF stitching fails (pdf-lib) | Log error with template ID; halt; write to error bucket |
| XML parse failure | Log error with filename; write to error bucket |
| Output S3 write failure | Log error; write to error bucket |

All pipeline errors write a JSON error record to the error S3 bucket containing:
```json
{
  "timestamp": "ISO-8601",
  "inputFile": "s3://input-bucket/filename.xml",
  "stage": "template-selection|section-render|stitching|output-write",
  "templateId": "uuid (if known)",
  "sectionId": "uuid (if applicable)",
  "error": "error message",
  "context": {}
}
```

## Testing Strategy

### Unit Testing

Framework: Jest (existing in both Admin Portal and Lambda projects)

Unit tests cover:
- **Specification tree validation** — specific valid/invalid tree structures
- **Specification evaluation** — specific contract data + rule combinations
- **Template priority management** — reorder/delete/create priority logic
- **Section ordering logic** — add/remove/reorder sort order management
- **Schema JSON validation** — format validation edge cases
- **XML-to-JSON transformation** — specific XML inputs and expected outputs
- **API request/response mapping** — handler input parsing and output formatting

### Property-Based Testing

Library: **fast-check** (TypeScript property-based testing library)

Configuration:
- Minimum 100 iterations per property test
- Custom arbitraries for specification trees, templates, sections, and contract data

Each property test is tagged with:
```
// Feature: contract-note-template-management, Property {N}: {property title}
```

Property tests implement the Correctness Properties defined above. Key generators needed:

1. **Specification tree generator** — produces random valid/invalid specification trees of varying depth
2. **Template generator** — produces random templates with names, descriptions, priorities
3. **Section generator** — produces random sections with sort orders and schema references
4. **Contract data generator** — produces random contract data objects with typed fields
5. **Schema JSON generator** — produces random valid pdf-me schema structures

### Integration Testing

- **API integration tests** — test Lambda handlers against DynamoDB Local and S3 (localstack)
- **Pipeline integration tests** — end-to-end: drop XML → verify PDF output in S3
- **Frontend E2E tests** — Protractor/Cypress tests for critical user flows (template CRUD, section editing, rule configuration)

### Test Organisation

```
lambdas-rest-api/contract-note-templates/tests/
  unit/
    template-service.spec.ts
    priority-manager.spec.ts
  property/
    template-priority.property.spec.ts
    specification-evaluation.property.spec.ts
    specification-serialization.property.spec.ts

lambdas-rest-api/contract-note-sections/tests/
  unit/
    section-service.spec.ts
    schema-validator.spec.ts
  property/
    section-ordering.property.spec.ts
    schema-roundtrip.property.spec.ts

render-pipeline/tests/
  unit/
    xml-parser.spec.ts
    section-renderer.spec.ts
    pdf-stitcher.spec.ts
  property/
    specification-evaluation.property.spec.ts
    pdf-stitching.property.spec.ts
    pipeline-error-handling.property.spec.ts

portal/src/app/components/contract-notes/tests/
  unit/
    template-list.component.spec.ts
    rules-config.component.spec.ts
  property/
    specification-tree-validation.property.spec.ts
```

### What Property Tests Cover vs Unit Tests

- **Property tests**: Universal invariants (ordering, round-trips, evaluation correctness, structural preservation)
- **Unit tests**: Specific examples (known XML input → expected JSON, specific rule tree → specific match result), edge cases (empty lists, single-node trees), error conditions (missing fields, malformed input)
- **Integration tests**: End-to-end flows across service boundaries (API → DynamoDB → S3, S3 trigger → pipeline → output)
