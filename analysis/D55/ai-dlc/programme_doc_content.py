"""
Content for the AI-DLC Programme Overview document.

A DOC dict of ordered blocks consumed by build_programme_doc.py. This is a
readable synthesis of programme-structure.md, the module docs, the schema, and
the Client Operating Manual TOC — for a quick read of the decisions made.

Body/bullet strings may contain inline HTML (<strong>, <em>).
"""

DOC = {
    "slug": "ai-dlc-programme-overview",
    "eyebrow": "AI-DLC",
    "title": "The AI-DLC Programme",
    "subtitle": "How the assessment workshop became a full service — structure, modules, and the decisions behind them.",
    "badge": "Programme Overview \u00b7 Draft for review",
    "date": "July 2026",
    "blocks": [
        {
            "type": "section",
            "heading": "What this is",
            "body": [
                "AI-DLC is a D55 service that helps mid-market engineering organisations actually get value from "
                "AI-assisted development — not a generic AI maturity assessment, but specifically <strong>how to use "
                "AI across the development lifecycle</strong>: tooling, specs, process, testing, governance, people, and ROI.",
                "This document captures a recent step up: the free assessment workshop we built is <strong>not the "
                "offering</strong> — it is the first step of a larger programme. What follows is the programme "
                "structure and the reasoning behind each decision, so it can be read quickly and reacted to.",
            ],
        },
        {
            "type": "callout",
            "heading": "The core reframe",
            "body": [
                "We were selling the diagnostic. We should be selling the <strong>transformation</strong>. A free "
                "one-hour diagnostic is a lead magnet, not a service. The value to a client is not \u201cyou found out "
                "where you stand\u201d — it is \u201cyou got to AI-native engineering, you can prove it with numbers, and "
                "you own the capability to keep going without us.\u201d",
            ],
        },
        {
            "type": "callout",
            "variant": "pitch",
            "heading": "The two-minute pitch",
            "body": [
                "\u201cWe assess where your engineering org really is with AI \u2014 free. We teach only the gaps that "
                "matter. Then we embed a hybrid team alongside your people, ship real work, and prove the ROI with "
                "hard numbers. Then we leave \u2014 and you keep the capability and the operating manual to run it "
                "yourselves.\u201d",
            ],
        },
        # --- The programme -------------------------------------------------
        {
            "type": "pipeline",
            "heading": "The programme: four phases",
            "pageBreak": True,
            "body": [
                "The assessment decides which phases and modules a given client actually needs. Not everyone does "
                "all of it — but where the gaps warrant it, the destination is <strong>Phase 2 (embed)</strong>, "
                "because that is where value is actually created.",
            ],
            "steps": [
                "Phase 0 \u2014 Assess (free)",
                "Phase 1 \u2014 Teach (modules)",
                "Phase 2 \u2014 Prove (embed)",
                "Phase 3 \u2014 Scale (roll out & exit)",
            ],
            "caption": "Throughout, the Client Operating Manual is written section by section — the asset the client keeps.",
        },
        {
            "type": "table",
            "heading": "What each phase does",
            "columns": ["Phase", "What happens", "Produces"],
            "rows": [
                ["0 \u2014 Assess",
                 "The 1-hour workshop we've built. 8 dimensions, current vs target, radar + gap analysis. Free.",
                 "The starting picture, and the decision on which modules/phases to recommend."],
                ["1 \u2014 Teach",
                 "Targeted workshops, chosen by the gaps. A prescription, not a fixed menu. Clustered into four modules.",
                 "The \u201chow you close each gap\u201d know-how, plus the middle sections of the manual."],
                ["2 \u2014 Prove",
                 "The 8-Week Prove-It made real: a <strong>hybrid</strong> team (D55 + their people) ships live work, metrics baselined from day one.",
                 "Shipped work, a proven metrics delta, and capability transferred into the team. The centre of gravity."],
                ["3 \u2014 Scale",
                 "Expand the proven pattern across teams. Hand over the completed manual. Reduce D55 presence.",
                 "An org running AI-native engineering on its own. The exit is a feature, not a bug."],
            ],
        },
        # --- Two runbooks --------------------------------------------------
        {
            "type": "cards",
            "heading": "Two runbooks (a deliberate distinction)",
            "intro": "\u201cRunbook\u201d was doing two jobs. Splitting it removed real confusion.",
            "cards": [
                {
                    "tag": "Internal",
                    "title": "D55 Delivery Playbook",
                    "body": [
                        "Our repeatable sequence for running an engagement: assess \u2192 teach \u2192 embed \u2192 roll out. "
                        "D55 IP. How a consultant knows what to do next. <strong>Never handed over.</strong>",
                    ],
                },
                {
                    "tag": "The kept asset",
                    "title": "Client Operating Manual",
                    "body": [
                        "The client's own playbook for AI-native engineering — their standards, tooling, guardrails, "
                        "metrics, ways of working. <strong>The artefact they own and run from after we leave.</strong>",
                    ],
                },
            ],
        },
        {
            "type": "callout",
            "heading": "How they relate",
            "body": [
                "Our Delivery Playbook <strong>drives</strong> the engagement; the engagement <strong>produces and "
                "populates</strong> the Client Operating Manual. Each phase we deliver writes another section of the "
                "client's manual. By the end it is complete and it is theirs.",
            ],
        },
        # --- The four modules ---------------------------------------------
        {
            "type": "table",
            "heading": "The four workshop modules",
            "pageBreak": True,
            "intro": "Eight assessment dimensions would make eight workshops — a bloated menu. Clustering them into "
                     "four modules keeps the service tight. Each maps to a chunk of the radar and writes one section "
                     "of the Client Operating Manual.",
            "columns": ["Module", "Covers (dimensions)", "Audience", "Writes"],
            "rows": [
                ["1. Leadership & the Investment Case",
                 "Leadership & Mandate \u00b7 Metrics & ROI", "Execs, sponsor, CFO/PE",
                 "\u00a71 Mandate & Measurement"],
                ["2. The AI-First Delivery Lifecycle",
                 "Tooling \u00b7 Specification & Design \u00b7 Delivery Process", "Engineering, POs/BAs",
                 "\u00a72 How We Build"],
                ["3. Shipping Safely",
                 "Testing & Quality \u00b7 Governance, Security & Compliance", "Eng leads, security, compliance",
                 "\u00a73 Shipping Safely"],
                ["4. People & Change",
                 "Team Adaptation & Skills (Four Fears, middle-layer, hybrid team model)", "Leadership, POs/BAs, HR",
                 "\u00a74 People & Operating Model"],
            ],
        },
        {
            "type": "callout",
            "heading": "Why the embed is a phase, not a module",
            "body": [
                "The hybrid embedded team is the destination the modules point toward — a team operating over a "
                "multi-month engagement, not a time-boxed workshop. Demoting it to a module would shrink the "
                "highest-value part of the service into a half-day slot. It stays Phase 2. <em>How</em> to run such "
                "a team is taught in Module 4; <em>doing</em> it is Phase 2.",
            ],
        },
        {
            "type": "section",
            "heading": "The hybrid embed, and the handover",
            "body": [
                "Phase 2 is <strong>not</strong> \u201cD55 comes and does the work.\u201d It is a deliberately hybrid "
                "team — D55 engineers plus the client's own people on one squad — because capability only transfers "
                "if their people are on the team, learning by doing. The handover is planned from day one: D55 "
                "presence tapers as the client takes over.",
                "The <strong>8-Week Prove-It</strong> (Assess wk 1\u20132, Prove wk 3\u20136, Translate wk 7\u20138) "
                "is the core proof cycle inside the embed — enough to baseline, ship, and demonstrate a metrics "
                "delta. A full embed typically runs longer as it tapers. Quote it as \u201c8-week proof, then taper.\u201d",
            ],
            "bullets": [
                "<strong>D55 + their people \u2192 handover</strong> — hybrid squad, client staff upskill in-flight, D55 exits leaving a self-sufficient team (preferred).",
                "<strong>D55-only \u2192 handover</strong> — where the client can't spare people up front; weaker capability transfer, so we steer toward the hybrid shape.",
            ],
        },
        # --- Value model --------------------------------------------------
        {
            "type": "cards",
            "heading": "How we drive maximum value for the client",
            "pageBreak": True,
            "intro": "The client doesn't want workshops or a runbook. They want three outcomes: ship faster, prove "
                     "it with numbers, and don't make a mess doing it. Five principles organise the service around those.",
            "cards": [
                {"title": "1. Value is created in the doing, not the assessing",
                 "body": ["Assessment and workshops are setup. The value lands when a hybrid team is shipping real "
                          "work with metrics baselined from day one. Get to shipped work fast and instrument it heavily."]},
                {"title": "2. Transfer capability, don't create dependency",
                 "body": ["The cleanest differentiator from a body-shop. We embed <em>and deliberately teach</em>, "
                          "leaving their people able to run it. Capability transfer is an explicit, measured deliverable — not a side effect."]},
                {"title": "3. De-risking is value, especially to the buyer",
                 "body": ["The CTO's real fear is a mess at 5x speed — insecure code, compliance exposure, EU AI Act. "
                          "\u201cYou can now go fast <em>safely</em>\u201d is what lets leadership authorise scaling at all."]},
                {"title": "4. Solve the problem they don't know they have",
                 "body": ["The middle-layer bottleneck is high-value because it's non-obvious. Surfacing and fixing it "
                          "makes us look like we've been somewhere they haven't."]},
                {"title": "5. Leave a flywheel",
                 "body": ["The end state is self-sustaining: metrics prove ROI \u2192 justifies investment \u2192 more "
                          "adoption \u2192 more metrics. The manual institutionalises it so it survives after we leave."]},
            ],
        },
        # --- Commercial ----------------------------------------------------
        {
            "type": "table",
            "heading": "Commercial shape (for discussion)",
            "intro": "Moving from \u00e0 la carte to a programme with a natural path. The existing component pricing "
                     "still stands — this packages it.",
            "columns": ["Tier", "Includes", "Rough shape"],
            "rows": [
                ["Assess", "Phase 0 only", "Free (the lead magnet)"],
                ["Assess + Teach", "Phase 0 + chosen modules", "Per module (~\u00a35\u201315k, priced by duration)"],
                ["Full programme", "Phase 0 \u2192 Teach \u2192 Embed \u2192 Scale", "Programme price; embed dominates (~\u00a315\u201325k/engineer/month)"],
            ],
        },
        {
            "type": "section",
            "heading": "Open decisions for Rhys",
            "body": ["A handful of calls are needed before this goes to a prospect. The structure above is designed to "
                     "make them concrete rather than open-ended."],
            "bullets": [
                "<strong>Does the free assessment stay free</strong>, or convert to paid discovery for serious prospects? (Changes the sales motion. Recommendation: start free to build trust and pipeline; add paid discovery once we have proof points.)",
                "<strong>Programme pricing</strong> — one price, or a committed path with stage gates the client can stop at?",
                "<strong>External name</strong> — \u201cAI-DLC\u201d works internally but not customer-facing (candidates already drafted).",
                "<strong>Manual format</strong> — generated branded document (reuses existing tooling) vs a living tool the client maintains.",
            ],
        },
        {
            "type": "callout",
            "heading": "Where this sits",
            "body": [
                "The programme structure, four modules, module schema, and Client Operating Manual outline are "
                "drafted and have passed a cold two-perspective critique (CTO 4/5, Marketing 3/5 \u2014 PASS). "
                "Remaining polish (an embed scoping one-pager, starter templates per module) is noted and authorable. "
                "The next real build is tooling: a skill that consumes the modules plus a client's assessment scores "
                "to generate a tailored write-up and populate their operating manual.",
            ],
        },
    ],
}
