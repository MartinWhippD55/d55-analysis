"""
Content for the Estimate 4 walkthrough: Bespoke Contracts.

Draws on:
  - .kiro/specs/contract-note-bespoke-contracts/{requirements,design,tasks}.md
  - analysis/BRYT/contract-note/4-bespoke-contract/mockups/{01-bespoke-list,02-bespoke-editor}.png
"""

MOCKUPS = "4-bespoke-contract/mockups"

DOC = {
    "estimate": "4",
    "title": "Bespoke Contracts",
    "subtitle": "Estimate 4 - Technical Walkthrough",
    "effort": "~7.8 developer days (4.8 required + testing)",
    "date": "July 2026",
    "blocks": [
        # ---------------------------------------------------------------
        {
            "type": "section",
            "heading": "Background",
            "body": [
                "Not every customer fits the standard mould. Some need non-standard terms, a different pricing "
                "presentation, or VIP treatment, cases where the automated template-matching from Estimate 1 "
                "is not the right tool. Today these are handled by manually editing a PDF, which is slow, "
                "error-prone, and leaves no audit trail.",
                "Estimate 4 gives business users a proper way to produce these one-off documents. A customer is "
                "flagged as bespoke on their Salesforce record; when their contract data arrives, the automated "
                "pipeline skips them and instead records that a bespoke contract is pending. A user then "
                "composes, renders, and sends that document manually through a dedicated area of the Admin "
                "Portal, using the same section editor they already know from Estimate 1.",
            ],
        },
        {
            "type": "callout",
            "heading": "Built almost entirely from reuse",
            "body": [
                "This estimate is deliberately thin on new machinery. It reuses Estimate 1's section editor, "
                "shared sections, and render-and-stitch pipeline, and Estimate 2's DocuSign envelope logic. "
                "The new parts are the pipeline skip, the bespoke list and editor screens, on-demand rendering, "
                "and render history.",
            ],
        },
        # ---------------------------------------------------------------
        {
            "type": "section",
            "heading": "How it works",
            "pageBreak": True,
            "body": [
                "The journey starts in the automated pipeline. Before rendering, the pipeline checks the "
                "customer's bespoke flag in Salesforce. If it is set, the pipeline skips rendering entirely, "
                "produces no PDF, does not trigger DocuSign, and writes a pending record so the work surfaces "
                "in the Admin Portal.",
                "From there it is a manual, user-driven flow. A user picks up the pending request and creates a "
                "bespoke contract note, either cloning an existing template as a starting point or beginning "
                "from a blank document. They compose it in the same section editor as standard templates, with "
                "the customer's actual contract data shown alongside for reference.",
                "When ready, the user renders on demand to produce the PDF, reviewing and re-rendering as "
                "needed, with every render kept in history. Once happy, they send it for signature with a "
                "single button that reuses the Estimate 2 DocuSign flow.",
            ],
        },
        {
            "type": "pipeline",
            "heading": "End-to-end journey",
            "steps": [
                "Bespoke flag set in Salesforce",
                "Pipeline skips, writes pending record",
                "User creates bespoke (clone or blank)",
                "Edit sections + review data",
                "Save & render on demand",
                "Send via DocuSign",
            ],
            "caption": "The automated pipeline steps aside; a person drives the rest through the Admin Portal.",
        },
        {
            "type": "callout",
            "heading": "The skip is fail-safe",
            "body": [
                "If Salesforce cannot be reached to check the flag, the pipeline proceeds with standard "
                "rendering rather than blocking. A missed bespoke flag is recoverable; a customer receiving no "
                "contract note at all is not.",
            ],
        },
        # ---------------------------------------------------------------
        {
            "type": "table",
            "heading": "Key design decisions",
            "pageBreak": True,
            "intro": "The decisions centre on isolation (bespoke edits must never touch standard templates) and reuse (don't rebuild what Estimates 1 and 2 already do).",
            "columns": ["Decision", "Choice", "Why"],
            "rows": [
                ["Bespoke flag source", "A field on the Salesforce customer record",
                 "Single source of truth for customer data; no duplicated configuration"],
                ["Cloned sections", "Independent copies, not template references",
                 "Bespoke edits must not affect standard templates, and vice versa; full isolation"],
                ["Render mechanism", "Reuse the Estimate 1 render Lambda, invoked on demand",
                 "Same section-render-and-stitch logic; no duplicate rendering code"],
                ["DocuSign", "Reuse Estimate 2's envelope logic, triggered manually",
                 "Identical signing flow, just started by a button instead of automatically"],
                ["Contract data", "Stored alongside the bespoke record",
                 "Available both for the reference panel and for resolving fields at render time"],
                ["Version history", "Same pattern as standard sections (Estimate 1)",
                 "Consistent experience; reuses the existing version records"],
            ],
        },
        # ---------------------------------------------------------------
        {
            "type": "screens",
            "heading": "Screen-by-screen walkthrough",
            "intro": "Two screens make up the bespoke experience. Both build on patterns from the Estimate 1 template editor.",
            "screens": [
                {
                    "image": f"{MOCKUPS}/01-bespoke-list.png",
                    "title": "1. Bespoke Contract Notes list",
                    "body": [
                        "The entry point. A filterable table of every bespoke contract note and its status. "
                        "Pending requests, customers who arrived via the pipeline skip, are highlighted so they "
                        "get picked up.",
                    ],
                    "interactions": [
                        "Filter by status (pending, draft, rendered, failed)",
                        "Pending rows offer a Create Bespoke action",
                        "Edit opens the bespoke editor",
                        "Download PDF appears once a note has been rendered",
                        "Send via DocuSign appears on rendered notes",
                    ],
                    "data": [
                        "Pending rows come from records the pipeline wrote when it skipped a customer",
                        "Each note shows customer, BrytNumber, offer reference, status, dates, and the user on it",
                        "Status reflects the latest render and DocuSign state",
                        "No per-user locking in this phase; any authorised user can edit any note",
                    ],
                },
                {
                    "image": f"{MOCKUPS}/02-bespoke-editor.png",
                    "title": "2. Bespoke Editor",
                    "body": [
                        "Where the document is composed. The section management is the same as the Estimate 1 "
                        "template editor, with two additions: a contract data reference panel and a render "
                        "history panel.",
                    ],
                    "interactions": [
                        "Add, remove, reorder, and edit sections in the pdf-me designer",
                        "Add shared sections (headers, footers, T&Cs) from the existing library",
                        "The reference panel shows the customer's actual field values while editing",
                        "Save & Render produces the PDF on demand; re-render after edits",
                        "Send via DocuSign appears once rendered",
                    ],
                    "data": [
                        "Sections live under the bespoke note, as independent copies if cloned",
                        "The reference panel reads the stored contract JSON, grouped and searchable",
                        "Each render appends a version to the render history (append-only)",
                        "Section edits carry version history, same as standard templates",
                    ],
                },
            ],
        },
        # ---------------------------------------------------------------
        {
            "type": "section",
            "heading": "On-demand rendering and history",
            "pageBreak": True,
            "body": [
                "Unlike the automated pipeline, bespoke notes render when the user asks. Save & Render resolves "
                "the note's sections, invokes the same render-and-stitch logic as the standard pipeline (this "
                "time synchronously) using the customer's stored contract data, and writes the resulting PDF to "
                "S3.",
                "Every render is preserved. Each one appends a new version to the render history, with the "
                "timestamp, the user who triggered it, and a link to that PDF, so a user can always retrieve an "
                "earlier version. The current version is clearly marked, and it is the one used when the note "
                "is sent for signature.",
            ],
        },
        {
            "type": "table",
            "heading": "Status lifecycle",
            "intro": "A bespoke note moves through a small set of states as it is worked on.",
            "columns": ["Status", "Meaning"],
            "rows": [
                ["pending", "The pipeline skipped this customer; awaiting someone to pick it up"],
                ["draft", "A bespoke note has been created and is being composed"],
                ["rendering", "A render is in progress"],
                ["rendered", "A PDF has been produced and is ready to download or send"],
                ["failed", "The last render failed; the error is recorded for the user to see"],
            ],
        },
        {
            "type": "section",
            "heading": "Sending for signature",
            "body": [
                "Once a note is rendered, a Send via DocuSign button appears. It reuses Estimate 2's flow "
                "wholesale: it looks up the customer's contact details in Salesforce, creates a DocuSign "
                "envelope around the latest rendered PDF, and stores the envelope so its status (sent, "
                "completed, declined, expired) shows against the note. Completion is handled by the same "
                "Estimate 2 webhook, so a signed bespoke contract lands in S3 and Salesforce exactly like a "
                "standard one.",
            ],
        },
        # ---------------------------------------------------------------
        {
            "type": "table",
            "heading": "What we store",
            "pageBreak": True,
            "intro": "Bespoke records follow the same single-table pattern as Estimate 1, keyed under the bespoke note rather than a template.",
            "columns": ["Record", "Holds"],
            "rows": [
                ["Pending bespoke", "Written by the pipeline skip: BrytNumber, offer reference, customer name, contract data location"],
                ["Bespoke contract note", "The note's metadata: customer, status, current render, DocuSign envelope + status, who created/updated it"],
                ["Bespoke section", "Each section's name, order, shared reference, schema location, and version, independent of any template"],
                ["Render history", "One row per render: version, PDF location, timestamp, user, success/failure"],
            ],
        },
        {
            "type": "table",
            "heading": "Delivery breakdown",
            "intro": "Estimate 4 is ~4.8 required days plus optional testing, ~7.8 days in total. Much of the effort is wiring together existing capabilities.",
            "columns": ["Area", "Scope"],
            "rows": [
                ["Pipeline skip", "Salesforce bespoke-flag check (fail-safe), pending record creation, contract data stored for later"],
                ["Bespoke API", "List, create (clone or blank), get, update, delete, section management, contract-data endpoint"],
                ["On-demand render", "Synchronous render handler, render history, download links"],
                ["Manual DocuSign", "Send handler reusing Estimate 2 envelope logic; envelope status on the note"],
                ["Bespoke module (Angular)", "List screen, editor, contract-data reference panel, render history, creation/clone dialog"],
                ["Integration", "CDK routes, IAM, synchronous render invocation, portal navigation, end-to-end validation"],
            ],
        },
        {
            "type": "callout",
            "heading": "Testing note",
            "body": [
                "The build is designed around 7 correctness properties (no automated output for flagged "
                "customers, pending-record creation, clone isolation, valid on-demand render, append-only "
                "history, and correct-PDF signing). Property-based and integration tests are optional in the "
                "plan and can be deferred for a faster MVP, but are recommended given bespoke notes are "
                "customer-facing contracts.",
            ],
        },
    ],
}
