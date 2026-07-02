"""
Content for the Estimate 5 walkthrough: Comparison Audit.

Draws on:
  - .kiro/specs/contract-note-comparison-audit/{requirements,design,tasks}.md
  - analysis/BRYT/contract-note/open-questions.md (Estimate 5 items 9-11)

Note: Estimate 5 is a headless, developer-operated Step Function tool with no
Admin Portal UI, so there are no screen mockups. CSS-rendered flow diagrams
carry the visual load.
"""

DOC = {
    "estimate": "5",
    "title": "Comparison Audit",
    "subtitle": "Estimate 5 - Technical Walkthrough",
    "effort": "~12.4 developer days (incl. prompt iteration)",
    "date": "July 2026",
    "blocks": [
        # ---------------------------------------------------------------
        {
            "type": "section",
            "heading": "Background",
            "body": [
                "BRYT suspects that some contract note PDFs may be edited by hand after they are rendered but "
                "before they reach the customer, sidestepping the controlled template system. Because the edit "
                "happens outside any system, there is currently no way to know whether it is occurring or how "
                "often.",
                "Estimate 5 is an audit tool that answers that question. For a batch of contract notes it "
                "retrieves the original rendered PDF and the version that was actually emailed to the customer, "
                "compares the two with AWS Bedrock, and reports any differences it finds.",
                "This is a developer-operated analytical tool, not a customer- or business-facing product. It "
                "runs ad-hoc (for example monthly) over a list of references and produces results that are "
                "queried with Athena and delivered to BRYT as a spreadsheet.",
            ],
        },
        {
            "type": "callout",
            "heading": "How it differs from the other estimates",
            "body": [
                "Estimates 1-4 build the production system. Estimate 5 is a separate investigative tool that "
                "runs alongside it. There is no UI and no live integration, just a batch pipeline a developer "
                "triggers when an audit is needed.",
            ],
        },
        # ---------------------------------------------------------------
        {
            "type": "section",
            "heading": "How it works",
            "pageBreak": True,
            "body": [
                "A developer supplies a list of contract note references (up to 500 per run). A Step Function "
                "iterates the list, and for each reference it does three things: finds the original rendered "
                "PDF in S3, finds the sent PDF by searching the Outlook mailbox via the Microsoft Graph API, "
                "and, if both are available, asks Bedrock to compare them.",
                "The comparison result, identical or not, and if not, what changed, is written to S3 as a "
                "finding. A run-level summary tracks how many matched, mismatched, or errored. Once the run "
                "finishes, the findings are queried with Athena and turned into a spreadsheet for BRYT.",
                "The two documents come from deliberately different places: the original from the system's own "
                "S3 output, and the sent version from the actual email, because the email is the source of "
                "truth for what the customer really received.",
            ],
        },
        {
            "type": "pipeline",
            "heading": "Per-record comparison flow",
            "steps": [
                "Fetch original PDF (S3)",
                "Find sent email (Graph API)",
                "Extract sent PDF attachment",
                "Compare with Bedrock",
                "Store finding (S3)",
                "Update run summary",
            ],
            "caption": "If either PDF is missing, an error finding is recorded and the run continues to the next record.",
        },
        {
            "type": "pipeline",
            "heading": "Run lifecycle",
            "steps": [
                "Developer supplies references",
                "Step Function iterates (max 5 at a time)",
                "Findings written to S3",
                "Query with Athena",
                "Deliver spreadsheet to BRYT",
            ],
            "caption": "Concurrency is capped at 5 to stay within Graph API rate limits.",
        },
        # ---------------------------------------------------------------
        {
            "type": "layers",
            "heading": "System architecture",
            "pageBreak": True,
            "body": [
                "A Step Function orchestrates a handful of small Lambdas, each responsible for one step. The "
                "two PDFs are sourced from S3 and Outlook respectively, compared by Bedrock, and the findings "
                "land back in S3 where Athena can query them.",
            ],
            "lanes": [
                {"label": "Trigger",
                 "nodes": ["Developer - batch of references", "Step Function (Map, concurrency 5)"]},
                {"label": "Per-record Lambdas",
                 "nodes": ["fetch-original (S3)", "fetch-sent (Graph API)", "invoke-bedrock", "store-finding"]},
                {"label": "External services",
                 "nodes": ["Microsoft Graph API - Outlook", "AWS Bedrock (Claude)"]},
                {"label": "Results",
                 "nodes": ["S3 - findings (date-partitioned)", "Athena - query", "Spreadsheet for BRYT"]},
            ],
            "caption": "A developer-operated batch tool; nothing here runs in the live contract note path.",
        },
        {
            "type": "table",
            "heading": "Key design decisions",
            "intro": "The design favours proven, low-overhead building blocks that suit an ad-hoc analytical tool.",
            "columns": ["Decision", "Choice", "Why"],
            "rows": [
                ["Orchestration", "Step Functions with a Map state",
                 "Built-in iteration, retries, and error handling; a proven pattern"],
                ["Original PDF source", "S3 (existing output bucket)",
                 "The rendered original is already stored there by the current system"],
                ["Sent PDF source", "Microsoft Graph API (Outlook search)",
                 "The sent email is the source of truth for what the customer actually received"],
                ["Comparison engine", "AWS Bedrock (Claude)",
                 "Compares documents textually and visually, and can describe nuanced differences"],
                ["Results storage", "S3 JSON, date-partitioned",
                 "Directly queryable via Athena; no database or ETL needed"],
                ["Prompt management", "SSM Parameter Store, versioned",
                 "The comparison prompt can be refined without redeploying; each finding records the version used"],
                ["Operating model", "Developer-operated, ad-hoc batches",
                 "Not a production system; monthly runs with manual analysis and reporting"],
            ],
        },
        # ---------------------------------------------------------------
        {
            "type": "section",
            "heading": "The comparison itself",
            "pageBreak": True,
            "body": [
                "For each contract note where both PDFs are in hand, Bedrock is given the two documents and a "
                "prompt asking whether they are identical and, if not, to describe each difference with its "
                "location and severity. The response is stored as a structured finding: a match/mismatch "
                "verdict, a list of differences, and a one-line summary.",
                "Getting this right is mostly a prompt-engineering exercise. The prompt lives in Parameter "
                "Store rather than in code so it can be tuned quickly, and each finding records which prompt "
                "version produced it. The estimate explicitly budgets for several iteration cycles, running a "
                "batch, reviewing the signal-to-noise with BRYT, and refining, until the output reliably flags "
                "meaningful edits without drowning them in noise.",
            ],
        },
        {
            "type": "table",
            "heading": "What a finding records",
            "intro": "Each finding is one JSON record per contract note, written to S3 and queryable in Athena.",
            "columns": ["Field", "Holds"],
            "rows": [
                ["Offer reference / document ID", "Which contract note this finding is for"],
                ["Run ID & timestamp", "Which batch produced it and when"],
                ["Status", "match, mismatch, or error"],
                ["Original & sent PDF keys", "Where each source document was found (sent key only if located)"],
                ["Comparison result", "Bedrock's verdict: identical flag, list of differences, summary"],
                ["Prompt version", "Which prompt version produced the result (for traceability)"],
                ["Error message", "Populated when a step could not complete"],
            ],
        },
        {
            "type": "table",
            "heading": "How the edge cases are handled",
            "columns": ["Situation", "Behaviour"],
            "rows": [
                ["Original PDF not in S3", "Record 'error: original not found'; continue to next record"],
                ["No matching sent email", "Record 'error: email not found'; continue"],
                ["Multiple matching emails", "Use the most recent; log a warning"],
                ["Email has no PDF attachment", "Record an error finding; continue"],
                ["Bedrock call fails", "Retry once, then record 'error: comparison failed'; continue"],
                ["Bedrock reply unparseable", "Store the raw response and flag it for manual review"],
            ],
        },
        # ---------------------------------------------------------------
        {
            "type": "table",
            "heading": "Open questions",
            "pageBreak": True,
            "intro": "This estimate has a hard external dependency on Microsoft 365 access. These need BRYT confirmation before work can complete.",
            "columns": ["#", "Question", "Why it matters"],
            "rows": [
                ["9", "Can BRYT provide an Azure AD app registration with Mail.Read (or Mail.ReadBasic) for the Graph API?",
                 "This is the critical dependency, without it the sent PDFs cannot be retrieved and the tool cannot function."],
                ["10", "Which mailbox(es) are contract notes sent from?",
                 "Determines which mailbox the search runs against, could be one shared mailbox or several users."],
                ["11", "How do we correlate a sent email to a specific contract note?",
                 "Assumption: the subject line or attachment filename contains the offer reference (e.g. OP-56412). Needs confirmation."],
            ],
        },
        {
            "type": "callout",
            "heading": "Critical dependency",
            "body": [
                "Question 9 is a blocker rather than a detail. The whole tool depends on read access to the "
                "mailbox where contract notes are sent, which requires BRYT's M365 admin to grant the "
                "permission. It is worth securing this early, as everything else is downstream of it.",
            ],
        },
        # ---------------------------------------------------------------
        {
            "type": "table",
            "heading": "Delivery breakdown",
            "intro": "Estimate 5 is ~12.4 days. Unlike the others, a large share is prompt iteration and analysis rather than pure build.",
            "columns": ["Area", "Scope"],
            "rows": [
                ["Infrastructure", "Step Function, the six Lambdas, results S3 bucket, Secrets Manager, SSM prompt parameter, IAM, Athena/Glue table"],
                ["Graph API integration", "OAuth client-credentials auth, mailbox search, PDF attachment extraction"],
                ["Bedrock integration", "Initial comparison prompt, model invocation, structured response parsing"],
                ["Prompt iteration", "3-5 cycles of running batches, reviewing output with BRYT, and refining the prompt"],
                ["Analysis & reporting", "Athena queries for common patterns, producing the spreadsheet report for BRYT"],
                ["Buffer", "Graph API limitations and Bedrock output tuning"],
            ],
        },
        {
            "type": "callout",
            "heading": "A note on effort",
            "body": [
                "This estimate is less predictable than the others because its value depends on comparison "
                "quality, which is reached through iteration rather than a fixed build. The figure includes "
                "that iteration and a buffer for the Graph API and Bedrock tuning; the underlying spec notes a "
                "wider 13-20 day range depending on how many refinement cycles BRYT wants.",
            ],
        },
    ],
}
