"""
Content for the Estimate 2 walkthrough: DocuSign Integration.

Draws on:
  - .kiro/specs/contract-note-docusign-integration/{requirements,design,tasks}.md
  - analysis/BRYT/contract-note/2-docusign/docusign-flow.png (technical sequence)
  - analysis/BRYT/contract-note/2-docusign/docusign-flow-simple.png (simplified)
  - analysis/BRYT/contract-note/open-questions.md (Estimate 2 items)

Note: Estimate 2 is a headless, event-driven pipeline with no Admin Portal UI,
so there are no screen mockups. The two flow diagrams carry the visual load.
"""

import figures as F

DOCUSIGN_DIR = "2-docusign"
_f = F.FIGURES["est2"]

DOC = {
    "estimate": "2",
    "title": "DocuSign Integration",
    "subtitle": "Estimate 2 - Technical Walkthrough",
    "effort": F.effort_line("est2"),
    "date": "July 2026",
    "blocks": [
        # ---------------------------------------------------------------
        {
            "type": "section",
            "heading": "Background",
            "body": [
                "Once a contract note PDF has been produced, it still needs to be signed by the customer. "
                "Today that final step is manual: someone has to send the document out, chase the signature, "
                "collect the signed copy, and file it against the customer's record.",
                "Estimate 2 automates that entire loop. When Estimate 1's render pipeline writes a finished "
                "PDF, this system automatically sends it to the customer for electronic signature via "
                "DocuSign, then retrieves the signed copy and attaches it to the customer's Salesforce record.",
                "It is a headless, event-driven pipeline. There is no new screen in the Admin Portal, the whole "
                "thing runs automatically from the moment a PDF lands. The only visible outcome for the "
                "business is a signed contract appearing against the customer in Salesforce.",
            ],
        },
        {
            "type": "callout",
            "heading": "Builds directly on Estimate 1",
            "body": [
                "This estimate is delivered inside BrytBusinessServices, the repository where Estimate 1's "
                "backend landed, and consumes the output of Estimate 1's render pipeline. That pipeline is a "
                "Step Functions state machine, so the trigger for this estimate is a new final step added to "
                "that state machine, right after the PDF is written. The step invokes the send process with "
                "the customer details already in hand, and has its own error handling so a signing hiccup "
                "never marks the render itself as failed or throws away the finished PDF.",
                "Estimate 1 also needs a small, real change: today it produces the PDF but does not carry the "
                "customer's Salesforce reference through to the output. That reference has to be surfaced "
                "(alongside the offer reference and customer name) so this pipeline knows who to send each "
                "contract note to. That work is coordinated with the Estimate 1 pipeline owner.",
            ],
        },
        # ---------------------------------------------------------------
        {
            "type": "section",
            "heading": "How it works",
            "pageBreak": True,
            "body": [
                "The system is two small Lambda functions with DocuSign and Salesforce either side of them.",
                "The first Lambda runs when a PDF is produced: it looks up the customer in Salesforce, "
                "authenticates to DocuSign, and creates a signing envelope, which prompts DocuSign to email "
                "the customer. The second Lambda runs when the customer finishes signing: DocuSign calls back "
                "over a webhook, and the Lambda downloads the signed PDF, stores it, and attaches it to "
                "Salesforce.",
                "In between those two moments, the customer signs at their own pace, so the flow is split into "
                "a send phase and a completion phase rather than one continuous run.",
            ],
        },
        {
            "type": "pipeline",
            "heading": "Send phase (automatic, on PDF creation)",
            "steps": [
                "PDF written by render pipeline",
                "SendEnvelope step fires",
                "Look up customer in Salesforce",
                "Authenticate to DocuSign",
                "Create + send envelope",
                "Store envelope metadata",
            ],
            "caption": "DocuSign emails the signing request to the customer as soon as the envelope is sent.",
        },
        {
            "type": "pipeline",
            "heading": "Completion phase (triggered when the customer signs)",
            "steps": [
                "Customer signs",
                "DocuSign webhook fires",
                "Validate HMAC signature",
                "Download signed PDF",
                "Store in S3",
                "Attach to Salesforce",
            ],
            "caption": "A declined or expired envelope instead writes a notification record for operational follow-up.",
        },
        {
            "type": "diagram",
            "heading": "End-to-end sequence",
            "body": [
                "The full exchange between the render pipeline, the two Lambdas, DocuSign, the customer, and "
                "Salesforce. The top half is the send phase; the bottom half is the completion phase that runs "
                "after the customer signs.",
            ],
            "image": f"{DOCUSIGN_DIR}/docusign-flow.png",
            "caption": "Technical sequence diagram: PDF creation through to signed document stored in Salesforce.",
        },
        {
            "type": "diagram",
            "heading": "Simplified flow",
            "body": [
                "The same journey told for a non-technical audience, useful for explaining the process to "
                "stakeholders who care about the outcome rather than the mechanics.",
            ],
            "image": f"{DOCUSIGN_DIR}/docusign-flow-simple.png",
            "caption": "Stakeholder-friendly view of the signing journey.",
        },
        # ---------------------------------------------------------------
        {
            "type": "table",
            "heading": "Key design decisions",
            "pageBreak": True,
            "intro": "A handful of choices keep the pipeline automated, secure, and consistent with existing BRYT patterns.",
            "columns": ["Decision", "Choice", "Why"],
            "rows": [
                ["DocuSign authentication", "JWT Grant (server-to-server)",
                 "No human login needed; the token can be cached and refreshed for a fully automated pipeline"],
                ["Trigger", "New final step on the render state machine",
                 "Runs right after the PDF is written, with the customer details already in the payload; its own error handling keeps signing failures from failing the render"],
                ["Status notifications", "DocuSign Connect webhook (per-envelope)",
                 "Real-time updates instead of polling; per-envelope config avoids account-level admin setup"],
                ["Signed document storage", "S3 and Salesforce",
                 "S3 as the durable system of record; Salesforce for day-to-day business access"],
                ["Salesforce integration", "OAuth client, built fresh",
                 "No Salesforce API client exists in the landed code to reuse, so this is new (not a reuse) work"],
                ["Resilience", "Exponential backoff, 3 attempts",
                 "DocuSign and Salesforce calls can fail transiently; retries avoid losing a signed document"],
                ["Webhook security", "HMAC signature validation",
                 "The endpoint must be public for DocuSign to reach it, so every request is verified as genuine"],
            ],
        },
        # ---------------------------------------------------------------
        {
            "type": "section",
            "heading": "The two Lambdas in detail",
            "body": [
                "Send Envelope Lambda. Invoked by the render pipeline's final step with the customer's "
                "Salesforce reference already in the payload, it queries Salesforce for their name and email, "
                "authenticates to DocuSign, then creates an envelope containing the PDF with a signature field "
                "and the customer as the sole signer. Setting the envelope to sent makes DocuSign email the "
                "customer immediately. It records the envelope details in DynamoDB for traceability, and skips "
                "cleanly if an envelope already exists for that PDF so a retry can never double-send.",
                "Webhook Lambda. Exposed via a public API Gateway endpoint, it receives DocuSign's callbacks. "
                "Every request is HMAC-validated first. On a completed event it downloads the signed PDF, "
                "stores it in S3, attaches it to the Salesforce record, and updates the status. On a declined "
                "or expired event it records the status and writes a notification for follow-up.",
            ],
        },
        {
            "type": "table",
            "heading": "External integrations",
            "intro": "The pipeline talks to two external services. Both authenticate with credentials held in AWS Secrets Manager.",
            "columns": ["Service", "What we call it for", "Key operations"],
            "rows": [
                ["DocuSign eSignature API", "Sending documents for signature and retrieving signed copies",
                 "JWT auth; create + send envelope; download combined signed document"],
                ["Salesforce REST API", "Finding the customer and filing the signed contract",
                 "OAuth; query contact by reference; upload file (ContentVersion); link to record"],
            ],
        },
        # ---------------------------------------------------------------
        {
            "type": "table",
            "heading": "What we track",
            "pageBreak": True,
            "intro": "A single DynamoDB table records one row per envelope, for debugging and traceability. There is no user-facing status screen in this phase.",
            "columns": ["Field", "Holds"],
            "rows": [
                ["Envelope ID", "DocuSign's identifier for the signing envelope (the primary key)"],
                ["Salesforce reference", "Links back to the customer record (also a lookup index)"],
                ["Contract note S3 key", "The original PDF that was sent"],
                ["Customer name & email", "Who the envelope was sent to"],
                ["Status", "sent, completed, declined, or expired"],
                ["Signed PDF S3 key", "Where the signed copy landed, once complete"],
                ["Timestamps & error/decline reason", "When it was created and last updated, plus any failure detail"],
            ],
        },
        {
            "type": "section",
            "heading": "Error handling and resilience",
            "body": [
                "Because this pipeline produces legally significant documents, it fails safe. Any failure in the "
                "send phase (missing metadata, customer not found, no email on file, DocuSign or Salesforce "
                "errors) is logged to a shared error bucket and halts before an envelope is created, so nothing "
                "is half-sent.",
                "In the completion phase, the two external calls that matter most, downloading the signed PDF "
                "and uploading it to Salesforce, each retry up to three times with exponential backoff. If they "
                "still fail, an error record is written for manual investigation, and the signed PDF is always "
                "safe in S3 regardless.",
            ],
        },
        # ---------------------------------------------------------------
        {
            "type": "table",
            "heading": "Open questions",
            "pageBreak": True,
            "intro": "This estimate carries assumptions that need BRYT confirmation. Each has a working assumption so delivery can proceed, but they should be resolved before or during implementation.",
            "columns": ["#", "Question", "Working assumption"],
            "rows": [
                ["1", "Are there multi-party signing scenarios (BRYT rep, TPI), or always just the customer?",
                 "Single signatory (customer only). Multi-party would affect envelope routing and signing order."],
                ["2", "Does BRYT have an existing DocuSign account?",
                 "Starting from scratch, new account, API credentials, and sandbox needed. No evidence found in AWS."],
                ["3", "Is DocuSign's standard branded email acceptable, or is full control needed?",
                 "DocuSign sends the signing email directly, with BRYT branding configured in DocuSign settings."],
                ["4", "Is an Admin Portal UI needed for envelope status tracking?",
                 "No UI this phase. Metadata is stored for debugging; the signed PDF in Salesforce is the visible outcome."],
                ["5", "What Salesforce object does the customer reference map to, and is it queryable via the REST API?",
                 "Resolved at implementation time. Now more significant: with no existing Salesforce client, we confirm the object and that a REST/OAuth integration is available before build."],
                ["6", "Are voided envelopes, resend, and reminders out of scope?",
                 "Out of scope. We handle completed, declined, and expired only. Retry/resend can come in a later phase."],
            ],
        },
        # ---------------------------------------------------------------
        {
            "type": "table",
            "heading": "Delivery breakdown",
            "intro": f"Estimate 2 is ~{F.fmt(_f.required)} required days plus optional testing, ~{F.fmt(_f.total)} days in total. Work is grouped as follows.",
            "columns": ["Area", "Scope"],
            "rows": [
                ["Infrastructure & utilities", "Envelope metadata table + GSI, signed-docs S3 bucket, API Gateway webhook route, Secrets Manager, IAM, retry + error-record utilities (reusing Estimate 1's error bucket) as a CDK construct in BrytBusinessServices"],
                ["Salesforce client (new)", "OAuth auth, customer contact lookup, signed document upload (ContentVersion + link) — built fresh, no existing client to reuse"],
                ["DocuSign client", "JWT auth, envelope creation + send, signed document download, HMAC webhook validation"],
                ["Metadata service", "DynamoDB create / get / update / query-by-reference for envelope records"],
                ["Send Envelope Lambda", "Trigger handling, metadata extraction, and orchestration of the send phase"],
                ["Webhook Lambda", "HMAC validation, completion flow, declined/expired notification flow"],
                ["Estimate 1 change", "Surface the customer Salesforce reference through the render state machine to the PDF output, and add the trigger hook"],
                ["Integration", "CDK wiring into the contract-note stack, trigger wiring, end-to-end validation"],
            ],
        },
        {
            "type": "callout",
            "heading": "Testing note",
            "body": [
                "The build is designed around 10 correctness properties (trigger-to-envelope correlation, "
                "webhook validation, completion produces a signed PDF in both S3 and Salesforce, and fail-safe "
                "behaviour). Property-based and integration tests are marked optional in the plan and can be "
                "deferred for a faster MVP, but they are strongly recommended given the pipeline handles signed "
                "contracts.",
            ],
        },
    ],
}
