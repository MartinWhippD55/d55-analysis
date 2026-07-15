"""
Content module for the ESG delivery briefing PDF.

Mirrors analysis/ESG/consolidated-update/overview.md, distilled into typed
blocks for the build_briefing.py engine. Pitched at product/outcome level for
the Lynsey meeting. Edit here, then re-run: python build_briefing.py
"""

DOC = {
    "slug": "esg-delivery-briefing",
    "eyebrow": "ESG Delivery — Confidential Briefing",
    "title": "Current State & Path to Faster Delivery",
    "subtitle": "Prepared for Jonathan ahead of the meeting with Lynsey",
    "confidential": "Confidential — D55 internal briefing",
    "date": "July 2026",
    "blocks": [
        # ---------------------------------------------------------------
        {
            "type": "callout",
            "heading": "In one minute",
            "bullets": [
                "D55 delivered four major workstreams — Financial Management, Instalment Plans, "
                "Debt Config, Debt Management — on time, to tight deadlines, running our own process.",
                "The next tranche (16 initiatives) is now run under a new model: D55 developers "
                "embedded into an ESG squad, ESG leads owning design and decisions, our design-first "
                "process removed.",
                "Under that model, pace has dropped. Current gut-feel estimates point to ~end-September "
                "against an end-July target — for work smaller than Debt Management, which we delivered "
                "in ~2 months with 9 developers.",
                "The variable that changed is the process, not the people. The fastest route back to "
                "pace is to reinstate design-first, then AI-accelerate from it.",
                "Opportunity: ESG want to learn how we break work down for AI. We're in the process of "
                "productising exactly that — route it into a value-adding engagement rather than giving "
                "it away piecemeal.",
            ],
        },
        # ---------------------------------------------------------------
        {
            "type": "section",
            "heading": "1. Current State",
            "body": [
                "D55 has delivered four major workstreams to date, each on time and under tight "
                "deadlines, running our own squads and design-first process.",
            ],
        },
        {
            "type": "table",
            "intro": "Delivered (D55-led, design-first process):",
            "columns": ["Workstream", "Outcome"],
            "rows": [
                ["Financial Management", "Delivered on time"],
                ["Instalment Plans", "Delivered on time"],
                ["Debt Config", "Delivered on time"],
                ["Debt Management", "~2 months, 9 developers — larger scope than the current tranche"],
            ],
        },
        {
            "type": "section",
            "body": [
                "Delivery quality held up under scrutiny: on the Debt/IP defect review, 127 defects, "
                "97% closed, and ~60% self-raised by D55 before ESG testing — a team reviewing and "
                "testing its own work.",
            ],
            "bullets": [
                "In flight: 16 initiatives, currently at business-requirements level only — "
                "overlapping, not yet scoped into technical design.",
                "Refinement only just completed, with half of July already gone.",
                "Estimate basis has changed to gut-feel, with no technical design underpinning it.",
            ],
        },
        {
            "type": "section",
            "heading": "What changed operationally",
            "bullets": [
                "D55 developers embedded into an ESG squad; ESG leads own the big-ticket initiatives "
                "and increasingly the overall process.",
                "D55's design-first process removed — no upfront technical design, no story/subtask "
                "decomposition, no Monte Carlo forecast.",
                "Autonomy removed — design and delivery decisions now sit with ESG leads.",
                "Each developer owns their own initiative design → weak coordination across overlapping "
                "initiatives and integration rework late in the cycle.",
            ],
        },
        # ---------------------------------------------------------------
        {
            "type": "section",
            "heading": "2. Internal Team",
            "body": [
                "The team running the current 16 initiatives is 5 developers: 3 from D55 and 2 from ESG.",
            ],
            "bullets": [
                "2 ESG developers own the main big-ticket initiatives and are taking on more of the process.",
                "3 D55 developers actively embedded, with reduced scope to make meaningful design impact.",
                "3 further D55 developers waiting on workstreams that start end of next week.",
                "2 further D55 developers working on less involved areas of the codebase.",
            ],
        },
        {
            "type": "callout",
            "heading": "The point to land (calmly)",
            "body": [
                "The current setup under-uses D55's strengths. Our value was never interchangeable "
                "coding capacity — it was the delivery system (design-first plus AI acceleration) that "
                "produced the earlier results. Embedded as individual contributors under another "
                "process, that advantage is switched off.",
            ],
        },
        # ---------------------------------------------------------------
        {
            "type": "table",
            "heading": "3. Deadlines: Expected vs Realistic",
            "pageBreak": True,
            "columns": ["", "Timeline"],
            "rows": [
                ["Expected (as indicated by ESG)", "End of July"],
                ["Realistic (current trajectory)", "~End of September"],
            ],
        },
        {
            "type": "section",
            "heading": "How the realistic estimate builds up",
            "bullets": [
                "~178 dev-days estimated across the 16 initiatives (gut-feel, no design).",
                "Team of 5 → ~35–36 dev-days ≈ ~7 dev-weeks of pure build, if perfectly parallel with "
                "zero rework.",
                "Excludes testing, defect-fixing, and merging feature-branch PRs into main — a "
                "non-trivial tail on every prior workstream.",
                "With refinement only just finished mid-July and no design to parallelise cleanly, the "
                "honest landing point is end of September.",
            ],
        },
        {
            "type": "callout",
            "heading": "The contrast that makes the point",
            "body": [
                "Debt Management was larger, delivered in ~2 months with 9 developers under our "
                "design-first process. This tranche is smaller, yet forecast at ~2+ months with 5 "
                "developers (effectively 3 D55) under the new process.",
                "Same-or-worse duration for less scope. The only variable that changed is the process.",
            ],
        },
        {
            "type": "section",
            "heading": "A note on estimate confidence",
            "body": [
                "Previously we forecast dates from technical design → user stories → subtasks → Monte "
                "Carlo simulation. Those forecasts were defensible. The current numbers are gut-feel "
                "without a design, so their confidence interval is wide. We cannot stand behind a "
                "precise date under an estimation approach that isn't ours.",
            ],
        },
        # ---------------------------------------------------------------
        {
            "type": "section",
            "heading": "4. Key Challenges",
            "body": [
                "All of these trace back to one root cause: the switch away from design-first.",
            ],
            "bullets": [
                "No upfront technical design — removes the artefact that makes AI acceleration possible "
                "and reliable forecasting achievable.",
                "Sequential refinement dependency — work waits on individual sessions rather than being "
                "decomposed once, upfront.",
                "Gut-feel estimates and ad-hoc ambiguity resolution mid-flight, rather than designed out early.",
                "Fragmented design ownership — per-developer initiative design drives communication "
                "overhead and integration rework.",
                "No comparable metrics — without our decomposition we can't produce the like-for-like "
                "throughput data that would evidence the pace drop.",
                "Autonomy removed — decision latency when every meaningful call routes through ESG leads.",
            ],
        },
        {
            "type": "callout",
            "heading": "The AI angle that matters most (D55's own published insight)",
            "body": [
                "When developers go 5x with AI, the bottleneck moves from building to specifying — "
                "\"no design specs at 5x speed = failure.\" The current model has increased AI "
                "pressure on delivery while removing the design step that makes AI pay off, so the "
                "constraint has moved to the middle layer (design, coordination, refinement) — exactly "
                "where the slowdown is showing.",
            ],
        },
        # ---------------------------------------------------------------
        {
            "type": "section",
            "heading": "5. Our Plan to Bring It In Sooner",
            "body": [
                "The fastest path is not \"more people\" or vaguely \"more AI.\" It is restoring the "
                "conditions that produced our earlier pace.",
            ],
        },
        {
            "type": "pipeline",
            "steps": [
                "Reinstate design-first",
                "AI-accelerate from the design",
                "Phase the delivery",
                "Align accountability with control",
                "Right-size the team post-design",
            ],
            "caption": "The sequence matters: design first is the enabler for everything downstream.",
        },
        {
            "type": "section",
            "bullets": [
                "Reinstate design-first: a technical design across the 16 initiatives up front, "
                "resolving the overlaps once. This enables everything else.",
                "AI-accelerate from the design: with clean design and defined contracts, large sections "
                "can be one-shot with Claude/Copilot — where the throughput multiplier actually lives.",
                "Phase the delivery: carving into phases (already on ESG's agenda) plays to "
                "decomposition — sequence by dependency, ship value earlier.",
                "Align accountability with control: happy to be measured on delivery where we own the "
                "levers; under shared ownership, timescale accountability is genuinely shared.",
                "Right-size the team post-design: adding developers before the work is decomposed adds "
                "overhead and rework, not speed. Design first, then scale to the shape of the work.",
            ],
        },
        {
            "type": "table",
            "heading": "Responding to the \"reduce timescales\" options",
            "intro": "ESG's agenda raises three levers. Our honest position on each:",
            "columns": ["Option", "D55 position"],
            "rows": [
                ["More resource",
                 "Won't help linearly on undesigned, overlapping work — risks worsening integration "
                 "rework. Design first, then add people to a decomposed backlog."],
                ["Use of AI",
                 "The real lever — but it requires the upfront design. This is the honest case for "
                 "reinstating design-first."],
                ["Phasing",
                 "Supportive — it aligns with how we decompose."],
            ],
        },
        # ---------------------------------------------------------------
        {
            "type": "section",
            "heading": "6. How to Play the Conversation with Lynsey",
            "pageBreak": True,
            "body": [
                "Strategic framing — Jonathan's call, offered as counsel.",
            ],
            "bullets": [
                "Listen first. Lynsey is product/outcome-focused and more senior than the day-to-day "
                "delivery politics. Understand her pain points and goals before positioning.",
                "Partner, not defence. Avoid leading with \"the timescales aren't our responsibility\" — "
                "true in fairness terms, but it invites \"then we'll take it fully in-house.\" Frame as "
                "\"align accountability with control\" and pivot to value.",
                "Anchor on the contrast, not the complaint: \"smaller scope, same duration, only the "
                "process changed\" is fair, factual, and lands without blaming individuals.",
                "Move up the value stack. As embedded individuals we are commoditised and easy to "
                "offboard; as the people who bring the 5x method we are not.",
                "Turn \"teach us your AI method\" into an opportunity. We're in the process of "
                "productising this (the AI-DLC programme). Offer it as a structured enablement "
                "engagement — protects the "
                "method, secures future work, strengthens the relationship, answers the AI question.",
                "Be measured on the \"how.\" Share the principle (design-first unlocks AI) freely; keep "
                "the detailed reusable playbook as the commercial asset it is.",
                "Jonathan's real goal: reinforce the relationship and secure future work. Every point "
                "should serve that, not win a delivery-process argument.",
            ],
        },
        {
            "type": "section",
            "heading": "Open questions to confirm before the meeting",
            "bullets": [
                "Is end-of-July a hard ESG commitment to a customer, or an internal target?",
                "What is Lynsey's own top priority — a date, a cost, a capability transfer, or de-risking?",
                "How explicit do we want to be about the handover signals — name it, or let Lynsey lead there?",
                "Appetite to formally propose the AI-DLC enablement engagement, or plant the seed only?",
            ],
        },
    ],
}
