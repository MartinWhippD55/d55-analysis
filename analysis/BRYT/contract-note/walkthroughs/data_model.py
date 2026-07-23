"""
Content for the Data Model walkthrough - the DynamoDB tables across all estimates.

Draws on the data-model sections of:
  - .kiro/specs/contract-note-template-management/design.md      (Est 1)
  - .kiro/specs/contract-note-data-source-extensibility/design.md (Est 3b)
  - .kiro/specs/contract-note-docusign-integration/design.md      (Est 2)
  - .kiro/specs/contract-note-bespoke-contracts/design.md         (Est 4)

Uses the "entities" block to render each record with its PK/SK pattern and
attribute table, plus GSIs.
"""

DOC = {
    "estimate": "data-model",
    "slug": "data-model",
    "title": "Data Model",
    "subtitle": "DynamoDB Table & Record Reference",
    "effort": "Estimates 1-4",
    "date": "July 2026",
    "blocks": [
        # ---------------------------------------------------------------
        {
            "type": "section",
            "heading": "Overview",
            "body": [
                "This document describes the DynamoDB data model behind the contract note rework. It is a "
                "companion to the estimate walkthroughs and the API specification, giving the concrete record "
                "shapes, key patterns, and indexes the implementation will use.",
                "The design follows a single-table pattern per bounded area. The bulk of the system, templates, "
                "sections, shared sections, rules, versions, data source attachments, and bespoke contracts, "
                "lives in one ContractNoteTemplates table, distinguished by partition key (PK) and sort key "
                "(SK) patterns. DocuSign envelope tracking sits in its own DocuSignEnvelopes table.",
                "Larger blobs are kept out of DynamoDB: pdf-me section layouts (schema JSON) and rendered PDFs "
                "live in S3, referenced from the records by their S3 key.",
            ],
        },
        {
            "type": "callout",
            "heading": "Reading the key patterns",
            "body": [
                "Values in braces are substituted at runtime, e.g. TEMPLATE#{templateId} becomes "
                "TEMPLATE#4f3c... . Records that share a partition key (a template and its sections, versions, "
                "rule, and change log) are stored together and retrieved with a single query, which is the "
                "core idea behind single-table design.",
            ],
        },
        {
            "type": "table",
            "heading": "Tables at a glance",
            "columns": ["Table", "Estimates", "Holds"],
            "rows": [
                ["ContractNoteTemplates", "1, 3b, 4",
                 "Templates, sections, shared sections, rules, version history, change log, data source attachments, and all bespoke records"],
                ["DocuSignEnvelopes", "2",
                 "One record per DocuSign envelope, for status tracking and traceability"],
            ],
        },
        # ---------------------------------------------------------------
        # ESTIMATE 1
        # ---------------------------------------------------------------
        {
            "type": "entities",
            "heading": "Estimate 1 - Templates & Sections",
            "pageBreak": True,
            "intro": "The core template records. Everything owned by a template shares the TEMPLATE#{templateId} partition, so a single query returns the template with its sections, rule, and change log.",
            "table": "ContractNoteTemplates",
            "entities": [
                {
                    "name": "Template",
                    "pk": "TEMPLATE#{templateId}",
                    "sk": "METADATA",
                    "attributes": [
                        ["templateId", "String", "UUID"],
                        ["name", "String", "Template display name (unique)"],
                        ["description", "String", "Template description"],
                        ["priority", "Number", "Evaluation priority (1 = highest)"],
                        ["sectionCount", "Number", "Denormalised count of sections"],
                        ["createdAt", "String", "ISO 8601 timestamp"],
                        ["updatedAt", "String", "ISO 8601 timestamp"],
                        ["createdBy", "String", "Cognito username"],
                    ],
                },
                {
                    "name": "Section (template-owned)",
                    "pk": "TEMPLATE#{templateId}",
                    "sk": "SECTION#{sortOrder}#{sectionId}",
                    "note": "The sort order is baked into the SK so sections return already ordered.",
                    "attributes": [
                        ["sectionId", "String", "UUID"],
                        ["name", "String", "Section display name"],
                        ["sortOrder", "Number", "Position within the template"],
                        ["isShared", "Boolean", "Whether this references a shared section"],
                        ["sharedSectionId", "String", "(optional) Reference to a shared section"],
                        ["schemaS3Key", "String", "S3 key for the schema JSON (default variant)"],
                        ["pinnedVersionId", "String", "(optional) Version this reference resolves to at render time; else latest"],
                        ["createdAt", "String", "ISO 8601 timestamp"],
                        ["updatedAt", "String", "ISO 8601 timestamp"],
                    ],
                },
                {
                    "name": "Section Variant",
                    "pk": "SECTION#{sectionId}",
                    "sk": "VARIANT#{variantOrder}#{variantId}",
                    "note": "Ordered variants within a section; the render pipeline picks the first whose rule matches, else the default.",
                    "attributes": [
                        ["variantId", "String", "UUID"],
                        ["name", "String", "Variant display name"],
                        ["variantOrder", "Number", "Evaluation order (first match wins)"],
                        ["isDefault", "Boolean", "Fallback when no variant rule matches"],
                        ["schemaS3Key", "String", "S3 key for this variant's schema JSON"],
                        ["specification", "Map", "(optional) Variant rule; absent for the default variant"],
                        ["createdAt / updatedAt", "String", "ISO 8601 timestamps"],
                    ],
                },
                {
                    "name": "Rule",
                    "pk": "TEMPLATE#{templateId}",
                    "sk": "RULE",
                    "note": "The specification tree that selects this template (see the Estimate 1 walkthrough).",
                    "attributes": [
                        ["specification", "Map", "JSON specification tree"],
                        ["updatedAt", "String", "ISO 8601 timestamp"],
                        ["updatedBy", "String", "Cognito username"],
                    ],
                },
                {
                    "name": "Template Change Log",
                    "pk": "TEMPLATE#{templateId}",
                    "sk": "CHANGELOG#{timestamp}",
                    "attributes": [
                        ["changeType", "String", "section-added, section-removed, section-reordered, metadata-updated, rule-updated"],
                        ["description", "String", "Human-readable description of the change"],
                        ["createdAt", "String", "ISO 8601 timestamp"],
                        ["createdBy", "String", "Cognito username"],
                    ],
                },
            ],
            "gsi": [
                {"name": "PriorityIndex", "pk": "ALL_TEMPLATES (constant)", "sk": "priority (Number)",
                 "enables": "Query all templates ordered by priority in a single call"},
            ],
        },
        {
            "type": "entities",
            "heading": "Estimate 1 - Shared Sections & Versions",
            "pageBreak": True,
            "intro": "Reusable sections live under their own partition and are linked to templates by reference records. Section edits are versioned rather than overwritten, and a chosen version is published to linked templates explicitly.",
            "table": "ContractNoteTemplates",
            "entities": [
                {
                    "name": "Shared Section",
                    "pk": "SHARED_SECTION#{sectionId}",
                    "sk": "METADATA",
                    "attributes": [
                        ["sectionId", "String", "UUID"],
                        ["name", "String", "Section display name"],
                        ["isTermsAndConditions", "Boolean", "Whether this is a T&C section"],
                        ["schemaS3Key", "String", "S3 key for the schema JSON"],
                        ["createdAt", "String", "ISO 8601 timestamp"],
                        ["updatedAt", "String", "ISO 8601 timestamp"],
                        ["createdBy", "String", "Cognito username"],
                    ],
                },
                {
                    "name": "Shared Section Reference",
                    "pk": "SHARED_SECTION#{sectionId}",
                    "sk": "REF#{templateId}",
                    "note": "One per template using the shared section; tracks references and the version each template is pinned to.",
                    "attributes": [
                        ["templateId", "String", "Template using this shared section"],
                        ["templateName", "String", "Denormalised for display"],
                        ["pinnedVersionId", "String", "Version this template resolves to (updated by a publish action)"],
                    ],
                },
                {
                    "name": "Section Version",
                    "pk": "SECTION_VERSION#{sectionId}#{variantId}",
                    "sk": "VERSION#{timestamp}",
                    "note": "Every schema save appends a version (per variant); nothing is overwritten, enabling history, revert, and publish.",
                    "attributes": [
                        ["versionId", "String", "UUID"],
                        ["sectionId", "String", "Section this version belongs to"],
                        ["variantId", "String", "Variant this version belongs to ('default' if no variants)"],
                        ["schemaS3Key", "String", "S3 key for this version's schema JSON"],
                        ["createdAt", "String", "ISO 8601 timestamp"],
                        ["createdBy", "String", "Cognito username"],
                        ["description", "String", "(optional) Change description"],
                    ],
                },
            ],
        },
        # ---------------------------------------------------------------
        # ESTIMATE 3b
        # ---------------------------------------------------------------
        {
            "type": "entities",
            "heading": "Estimate 3b - Data Source Attachments",
            "pageBreak": True,
            "intro": "Data source extensibility adds two record types to the same table. No new table is needed. Attachments hang off the template; dependencies hang off the shared section.",
            "table": "ContractNoteTemplates",
            "entities": [
                {
                    "name": "Template Data Source",
                    "pk": "TEMPLATE#{templateId}",
                    "sk": "DATASOURCE#{database}#{tableName}",
                    "note": "Marks a Glue table as attached to a template; its columns become available as fields.",
                    "attributes": [
                        ["database", "String", "Glue database name"],
                        ["tableName", "String", "Glue table name"],
                        ["displayName", "String", "User-friendly name (defaults to table name)"],
                        ["attachedAt", "String", "ISO 8601 timestamp"],
                        ["attachedBy", "String", "Cognito username"],
                    ],
                },
                {
                    "name": "Shared Section Dependency",
                    "pk": "SHARED_SECTION#{sectionId}",
                    "sk": "DATASOURCE_DEP#{database}#{tableName}",
                    "note": "Auto-tracked from the data source fields a shared section uses; drives the missing-dependency prompt.",
                    "attributes": [
                        ["database", "String", "Glue database name"],
                        ["tableName", "String", "Glue table name"],
                    ],
                },
            ],
        },
        # ---------------------------------------------------------------
        # ESTIMATE 4
        # ---------------------------------------------------------------
        {
            "type": "entities",
            "heading": "Estimate 4 - Bespoke Contracts",
            "pageBreak": True,
            "intro": "Bespoke records mirror the template pattern but under a BESPOKE#{bespokeId} partition, keeping one-off documents fully isolated from standard templates. A pending record is written first by the pipeline skip.",
            "table": "ContractNoteTemplates",
            "entities": [
                {
                    "name": "Pending Bespoke Request",
                    "pk": "BESPOKE_PENDING#{brytNumber}",
                    "sk": "OFFER#{offerReference}",
                    "note": "Written by the render pipeline when it skips a bespoke-flagged customer.",
                    "attributes": [
                        ["brytNumber", "String", "Customer BrytNumber"],
                        ["offerReference", "String", "Offer reference from the contract data"],
                        ["customerName", "String", "Customer name"],
                        ["contractDataS3Key", "String", "S3 key of the original contract JSON"],
                        ["receivedAt", "String", "ISO 8601 timestamp when received"],
                        ["status", "String", "pending"],
                    ],
                },
                {
                    "name": "Bespoke Contract Note",
                    "pk": "BESPOKE#{bespokeId}",
                    "sk": "METADATA",
                    "attributes": [
                        ["bespokeId", "String", "UUID"],
                        ["brytNumber", "String", "Customer BrytNumber"],
                        ["offerReference", "String", "Offer reference"],
                        ["customerName", "String", "Customer name"],
                        ["contractDataS3Key", "String", "S3 key of the contract JSON"],
                        ["clonedFromTemplateId", "String", "(optional) Template ID if cloned"],
                        ["status", "String", "draft, rendering, rendered, failed"],
                        ["currentRenderS3Key", "String", "(optional) S3 key of latest rendered PDF"],
                        ["currentRenderVersion", "Number", "Current render version number"],
                        ["docusignEnvelopeId", "String", "(optional) Envelope ID if sent"],
                        ["docusignStatus", "String", "(optional) sent, completed, declined, expired"],
                        ["createdAt / updatedAt", "String", "ISO 8601 timestamps"],
                        ["createdBy / updatedBy", "String", "Cognito usernames"],
                    ],
                },
                {
                    "name": "Bespoke Section",
                    "pk": "BESPOKE#{bespokeId}",
                    "sk": "SECTION#{sortOrder}#{sectionId}",
                    "note": "Same shape as a template section; independent copies when cloned from a template.",
                    "attributes": [
                        ["sectionId", "String", "UUID"],
                        ["name", "String", "Section display name"],
                        ["sortOrder", "Number", "Position within the bespoke contract"],
                        ["isShared", "Boolean", "Whether this references a shared section"],
                        ["sharedSectionId", "String", "(optional) Reference to a shared section"],
                        ["schemaS3Key", "String", "S3 key for the schema JSON"],
                        ["versionNumber", "Number", "Current version number"],
                        ["createdAt / updatedAt", "String", "ISO 8601 timestamps"],
                    ],
                },
                {
                    "name": "Bespoke Render History",
                    "pk": "BESPOKE#{bespokeId}",
                    "sk": "RENDER#{version}",
                    "note": "Append-only; one per on-demand render.",
                    "attributes": [
                        ["version", "Number", "Render version number"],
                        ["pdfS3Key", "String", "S3 key of the rendered PDF"],
                        ["renderedAt", "String", "ISO 8601 timestamp"],
                        ["renderedBy", "String", "Cognito username"],
                        ["status", "String", "success, failed"],
                        ["errorMessage", "String", "(optional) Error details if failed"],
                    ],
                },
            ],
        },
        # ---------------------------------------------------------------
        # ESTIMATE 2
        # ---------------------------------------------------------------
        {
            "type": "entities",
            "heading": "Estimate 2 - DocuSign Envelopes",
            "pageBreak": True,
            "intro": "DocuSign tracking uses a separate table. One record per envelope, looked up by envelope ID during webhook processing and by Salesforce reference for debugging.",
            "table": "DocuSignEnvelopes",
            "entities": [
                {
                    "name": "Envelope",
                    "pk": "ENVELOPE#{envelopeId}",
                    "sk": "METADATA",
                    "attributes": [
                        ["envelopeId", "String", "DocuSign envelope ID"],
                        ["salesforceRef", "String", "Customer Salesforce reference"],
                        ["contractNoteS3Key", "String", "S3 key of the original contract note PDF"],
                        ["customerEmail", "String", "Email the envelope was sent to"],
                        ["customerName", "String", "Customer name on the envelope"],
                        ["status", "String", "sent, delivered, completed, declined, expired"],
                        ["signedPdfS3Key", "String", "(optional) S3 key of signed PDF once downloaded"],
                        ["createdAt", "String", "ISO 8601 timestamp of creation"],
                        ["updatedAt", "String", "ISO 8601 timestamp of last status update"],
                        ["errorMessage", "String", "(optional) Error / decline reason"],
                    ],
                },
            ],
            "gsi": [
                {"name": "SalesforceRefIndex", "pk": "salesforceRef", "sk": "createdAt",
                 "enables": "Query all envelopes for a given customer (for debugging)"},
            ],
        },
        # ---------------------------------------------------------------
        {
            "type": "section",
            "heading": "What lives in S3 (not DynamoDB)",
            "body": [
                "Two kinds of larger data are deliberately kept in S3 and referenced from DynamoDB by key: the "
                "pdf-me section layouts (schema JSON, one object per section and per version), and the rendered "
                "and signed PDFs. This keeps DynamoDB items small and cheap to query while letting the bulkier "
                "content sit in cost-effective object storage.",
            ],
            "bullets": [
                "Schema JSON - referenced by schemaS3Key on sections, shared sections, and section versions",
                "Rendered contract note PDFs - the render pipeline output (Estimate 1)",
                "Signed PDFs - stored after DocuSign completion (Estimate 2), keyed by Salesforce ref + envelope ID",
                "Bespoke render PDFs - referenced by pdfS3Key on render history records (Estimate 4)",
                "Original contract JSON - stored for bespoke customers, referenced by contractDataS3Key",
            ],
        },
        {
            "type": "callout",
            "heading": "A note on scope",
            "body": [
                "These record shapes come from the estimate design documents and are intended to convey intent "
                "and structure. Exact attribute names, optionality, and any additional GSIs may be refined "
                "during implementation without changing the overall approach.",
            ],
        },
    ],
}
