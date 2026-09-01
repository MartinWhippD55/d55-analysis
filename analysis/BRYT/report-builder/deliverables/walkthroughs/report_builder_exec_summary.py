"""
Content for the Report Builder EXECUTIVE SUMMARY.

A short (~2-3 page) plain-language brief for a business/exec audience. It sits
alongside the full technical walkthrough (report_builder.py), which is kept
intact for the developer.

Same build engine, branding, and single-source-of-truth figures as the other
deliverables: effort numbers are pulled from the shared `figures` module (the
estimates spreadsheet) and are never hardcoded, so a spreadsheet edit +
regenerate propagates here too.

Build:
    python analysis/BRYT/report-builder/deliverables/walkthroughs/build_walkthrough.py report_builder_exec_summary
"""
import figures as F

MOCKUPS = "../mockups"

gt = F.grand_total()


# Compact per-phase table: plain-language phase name + core vs total days.
_PHASE_PLAIN = {
    "phase1": "Foundations (new codebase, shared building blocks)",
    "phase2": "Data-privacy engine (the safety core)",
    "phase3": "Cloud environment set-up",
    "phase4": "Report storage and the data catalogue",
    "phase5": "Plain-language assistant",
    "phase6": "Running reports and downloading results",
    "phase7": "The on-screen experience (portal screens)",
    "phase8": "Hardening, testing and go-live",
}


def _phase_rows():
    rows = []
    for k in F.phase_keys():
        fig = F.FIGURES[k]
        rows.append([_PHASE_PLAIN.get(k, fig.name), f"{F.fmt(fig.required)}", f"{F.fmt(fig.total)}"])
    rows.append(["Total", f"{F.fmt(gt.required)}", f"{F.fmt(gt.total)}"])
    return rows


DOC = {
    "slug": "report-builder-exec-summary",
    "title": "Report Builder",
    "subtitle": "Executive Summary",
    "eyebrow": "Self-Service Reporting",
    "effort": f"~{F.fmt(gt.required)} days core build  ·  ~{F.fmt(gt.total)} days fully tested",
    "date": "September 2026",
    "blocks": [
        # --- What it is -------------------------------------------------
        {
            "type": "section",
            "heading": "What we're building",
            "body": [
                "The Report Builder lets your customers pull their own reports from their data, without "
                "waiting on a developer and without writing any code. It is added straight into the existing "
                "Customer Portal they already sign in to.",
                "A customer picks the information they want on screen, and can simply ask for what they need "
                "in plain English. Behind the scenes we turn that into a query, run it, and give them the "
                "results back as a spreadsheet (CSV) they can download.",
            ],
        },
        {
            "type": "callout",
            "heading": "In a sentence",
            "body": [
                "Self-service reporting that customers drive themselves, with the guarantee that each customer "
                "only ever sees their own data.",
            ],
        },
        {
            "type": "diagram",
            "image": f"{MOCKUPS}/02-builder-canvas.png",
            "maxHeight": 82,
            "caption": "The customer drags the data they want onto the canvas and connects it up, or simply "
                       "asks the built-in assistant to adjust the report - no query language to learn.",
        },
        {
            "type": "section",
            "heading": "Why it matters",
            "bullets": [
                "Customers self-serve the reports they need, reducing ad-hoc data requests on your team.",
                "No SQL, no engineering involvement, and no new tool to learn - it lives in the portal they already use.",
                "Every report is locked to the signed-in customer's own accounts, checked independently before results are ever shown.",
                "Built on the same proven patterns and AWS foundations as your existing services.",
            ],
        },
        # --- The estimate (the headline question) -----------------------
        {
            "type": "table",
            "heading": "The estimate, and the 15 days",
            "intro": f"The core build - everything needed to ship the feature - is about {F.fmt(gt.required)} "
                     f"developer days. That is the figure quoted previously and it has not changed. A further "
                     f"~{F.fmt(gt.optional)} days of optional testing and hardening can be added for full "
                     f"assurance, taking the fully-tested total to about {F.fmt(gt.total)} days.",
            "columns": ["", "Developer days"],
            "rows": [
                ["Core build (required to ship)", f"~{F.fmt(gt.required)}"],
                ["Optional testing & hardening (recommended, can be deferred)", f"~{F.fmt(gt.optional)}"],
                ["Fully-tested total", f"~{F.fmt(gt.total)}"],
            ],
        },
        {
            "type": "callout",
            "heading": "What the optional testing buys",
            "body": [
                "The optional days are spent proving the data-privacy guarantee holds under every condition: "
                "automated checks that no customer can ever see another's data, that reports stay within safe "
                "limits, and that results are independently verified before anyone can download them. It is "
                "strongly recommended for a feature that handles customers' own data - and it is the main "
                "lever if you would prefer a faster, lighter first release.",
            ],
        },
        {
            "type": "table",
            "heading": "Where the effort goes",
            "pageBreak": True,
            "intro": "The work is grouped into eight stages. The data-privacy engine is built and proven before "
                     "anything is allowed to run a query. Day figures are indicative, derived from the detailed "
                     "task plan.",
            "columns": ["Stage", "Core (days)", "With testing (days)"],
            "rows": _phase_rows(),
        },
        {
            "type": "section",
            "heading": "What we need to proceed",
            "bullets": [
                "Confirm whether the optional testing is in or out of the first release.",
                "Confirm a small number of working assumptions carried from the design phase (report retention, query limits, the initial set of data tables).",
                "One environment access grant to finish verifying a data mapping in production.",
                "Green light to start the build, beginning with the foundations and the data-privacy engine.",
            ],
        },
        {
            "type": "callout",
            "heading": "More detail on request",
            "body": [
                "A full technical walkthrough, data model, and API reference sit alongside this summary for the "
                "development team. This page is the business-level view.",
            ],
        },
    ],
}
