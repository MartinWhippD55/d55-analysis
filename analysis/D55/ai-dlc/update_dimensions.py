"""Replace the dimensions array in workshop.html with the new AI-DLC focused version."""

NEW_DIMENSIONS = '''const dimensions = [
    {
        id: "leadership",
        title: "Leadership & Mandate",
        description: "Is there executive sponsorship for AI-assisted development, or are developers going rogue with tools?",
        levels: [
            "Absent \\u2014 No leadership acknowledgement of AI-assisted development",
            "Aware \\u2014 Leadership knows devs are experimenting, no formal position or budget",
            "Endorsed \\u2014 Executive sponsor, budget allocated, adoption encouraged but optional",
            "Mandated \\u2014 AI-assisted dev is the expected way of working, KPIs exist, investment proven",
            "Strategic \\u2014 AI-native engineering is a stated competitive advantage, board visibility"
        ],
        questions: [
            "Who made the decision to adopt AI dev tooling? Is there an executive sponsor?",
            "Is AI-assisted development optional, encouraged, or mandated?",
            "Has the investment case been made to finance/board?",
            "How does the board/PE see AI-assisted development \\u2014 cost play, velocity play, or valuation play?",
            "Is AI-native engineering part of your talent/recruitment messaging?"
        ],
        services: ["AI-First Strategy Workshop", "Investment Case Development", "Board Presentation Support"]
    },
    {
        id: "tooling",
        title: "Developer Tooling & Adoption",
        description: "Are developers actually using AI tools effectively, or are licences gathering dust?",
        levels: [
            "None \\u2014 No AI developer tooling in use",
            "Experimenting \\u2014 Some devs using ad-hoc, no consistency or support",
            "Provisioned \\u2014 Enterprise licences deployed, usage patchy across teams",
            "Effective \\u2014 AI embedded in daily workflow, shared configs and skills, meaningful productivity gain",
            "Advanced \\u2014 Agentic workflows standard, custom MCP servers, AI is a pair-programming partner"
        ],
        questions: [
            "What AI developer tools are in use? (Copilot, Claude, Cursor, Kiro?)",
            "What percentage of developers use them daily vs occasionally vs never?",
            "Do developers report meaningful productivity gains? Can they quantify?",
            "Is there a standard configuration new joiners get, or everyone rolls their own?",
            "Are there shared skills/playbooks or MCP connections to your systems (Jira, GitHub, DBs)?",
            "What\\u2019s the gap between your best AI-assisted dev and your least engaged?"
        ],
        services: ["AI Tooling Rollout", "Standard Configuration Build", "MCP Server Setup", "Knowledgebase Creation"]
    },
    {
        id: "specs",
        title: "Specification & Design",
        description: "When implementation goes 5x faster, the bottleneck shifts to clarity of intent. Has the org adapted?",
        levels: [
            "Traditional \\u2014 No change to specs despite AI tooling. Requirements vague or verbal.",
            "Recognising \\u2014 Awareness that AI needs better specs, but no systematic change",
            "Adapting \\u2014 Spec templates exist, contracts defined before build, some teams investing more in analysis",
            "Disciplined \\u2014 AI-first lifecycle: more time in design, less in build. Specs consumed by humans AND AI",
            "Optimised \\u2014 Specs are first-class artefacts. AI assists spec generation. Quality measured and correlated to output"
        ],
        questions: [
            "How much time in design/spec vs implementation? Has that ratio changed since AI tooling?",
            "When a dev starts work, what do they start with \\u2014 a Jira ticket, a spec, or a conversation?",
            "Has output quality changed since AI adoption \\u2014 better or worse?",
            "\\u2018Garbage specs at 5x speed = garbage 5x faster\\u2019 \\u2014 does that resonate?",
            "Are integration points and APIs defined before implementation, or discovered during?",
            "Are specs written in a way AI tools can consume them?"
        ],
        services: ["AI-First Delivery Lifecycle Workshop", "Spec Template Development", "Contract-First Design Coaching"]
    },
    {
        id: "process",
        title: "Delivery Process & Ceremonies",
        description: "Have sprints, standups, and ways of working adapted to the new velocity \\u2014 or is the process the bottleneck?",
        levels: [
            "Unchanged \\u2014 Same ceremonies, same cadence, same roles despite devs being 3-5x faster",
            "Straining \\u2014 Cracks appearing. Stories done faster than POs write them. Review queues growing.",
            "Adjusting \\u2014 Some conscious adaptation. Shorter sprints, streamlined reviews. But ad-hoc.",
            "Redesigned \\u2014 Process deliberately reshaped. Faster cycles. AI-assisted review. Coordination roles redefined.",
            "Continuous \\u2014 Near-continuous delivery. Ceremonies minimal. AI handles routine coordination."
        ],
        questions: [
            "Have your ceremonies or delivery cadence changed since AI tooling adoption?",
            "Where are the bottlenecks now? If devs are faster, what\\u2019s the new constraint?",
            "How long does a PR sit in review? Has that changed?",
            "Are POs/BAs able to keep pace with demand for well-specified work?",
            "Are you using AI for any coordination tasks (review, linking, status)?",
            "What\\u2019s your release cadence? Has it changed?"
        ],
        services: ["Process Redesign Workshop", "Ceremony Adaptation", "Continuous Flow Implementation"]
    },
    {
        id: "testing",
        title: "Testing & Quality",
        description: "Is testing adapted for AI-generated code \\u2014 or is the test strategy unchanged?",
        levels: [
            "Unchanged \\u2014 Same manual testing as pre-AI. No AI-assisted test generation.",
            "Basic \\u2014 AI generates some unit tests alongside code. Not systematic.",
            "Integrated \\u2014 AI code has same coverage requirements. Automated regression. AI-assisted test data.",
            "Comprehensive \\u2014 AI testing in CI/CD. Human-in-the-loop at integration points. Evidence-based confidence.",
            "Continuous \\u2014 Tests from specs automatically. Mutation testing standard. Feedback from prod to coverage."
        ],
        questions: [
            "How do you validate AI-generated code? Is there a specific process?",
            "What\\u2019s your automated test coverage? Has it changed since AI adoption?",
            "Do you trust AI-generated code the same as human-written?",
            "Are tests generated alongside code, or separately?",
            "Have you seen new categories of bugs from AI-generated code?",
            "Is there human-in-the-loop validation at integration points?"
        ],
        services: ["Test Automation Strategy", "AI-Assisted QA Setup", "Playwright Regression Implementation"]
    },
    {
        id: "governance",
        title: "Governance, Security & Compliance",
        description: "Are AI development tools used safely \\u2014 or is sensitive data leaking into prompts with no audit trail?",
        levels: [
            "Unmanaged \\u2014 No policy. Devs pasting prod data into ChatGPT. No audit trail.",
            "Aware \\u2014 Informal guidance exists. No technical controls.",
            "Controlled \\u2014 AI policy exists. Approved tool list. Enterprise agreements. Correct region.",
            "Enforced \\u2014 DLP in place. Code provenance tracked. EU AI Act classification done.",
            "Embedded \\u2014 Governance automated and frictionless. Real-time DLP. Compliance-as-code."
        ],
        questions: [
            "Do you have a policy on what data can/can\\u2019t be used with AI tools?",
            "Are your AI tools on enterprise agreements with data protection guarantees?",
            "Can you trace which code was AI-generated vs human-written?",
            "If a regulator asked \\u2018how do you govern AI in your dev process\\u2019 \\u2014 what would you show?",
            "Are there DLP controls preventing sensitive data reaching AI endpoints?",
            "What\\u2019s your supply chain risk posture for AI dependencies?"
        ],
        services: ["AI Usage Policy", "DLP Implementation", "EU AI Act Classification", "Code Provenance Tooling"]
    },
    {
        id: "team",
        title: "Team Adaptation & Skills",
        description: "Are people adapting \\u2014 or are coordination roles becoming bottlenecks and resistance blocking adoption?",
        levels: [
            "Resistant \\u2014 Significant resistance. Senior engineers undermined. Coordination roles threatened.",
            "Mixed \\u2014 Some enthusiasts, some holdouts. No training. Middle layer feeling pressure.",
            "Training \\u2014 Formal upskilling programme. Resistance identified. Some coordination roles adapting.",
            "Adapted \\u2014 Majority effective with AI. Coordination roles redefined. New joiners AI-first from day one.",
            "Native \\u2014 AI-assisted dev is the culture. Attracts talent. Everyone uses AI in their role."
        ],
        questions: [
            "Where is resistance coming from? Which roles or personality types push back?",
            "When devs went faster, did POs/BAs/PMs keep pace or become the bottleneck?",
            "Is there a training programme specifically for AI-assisted development?",
            "Who\\u2019s your biggest AI champion? Who\\u2019s your biggest blocker?",
            "Has anyone left or been moved because they couldn\\u2019t adapt?",
            "How long for a new joiner to become productive with AI tooling?"
        ],
        services: ["Four Fears Diagnostic & Intervention", "Upskilling Programme", "Role Redefinition Coaching"]
    },
    {
        id: "metrics",
        title: "Metrics & ROI",
        description: "Can you prove AI-assisted development is working \\u2014 with numbers, not vibes?",
        levels: [
            "Unmeasured \\u2014 No metrics on impact. \\u2018It feels faster\\u2019 but no evidence.",
            "Anecdotal \\u2014 Individual testimonials. Cannot make the case to finance.",
            "Tracked \\u2014 Key metrics tracked (cycle time, PRs, deploys, defects). Before/after available.",
            "Proven \\u2014 ROI quantified. Cost per feature known. Productivity per \\u00a3 measured. Case made to board.",
            "Optimised \\u2014 Continuous measurement drives improvement. Output per \\u00a3 is a primary KPI."
        ],
        questions: [
            "How do you know AI-assisted development is working? What evidence?",
            "If the CFO asked \\u2018what are we getting for AI tooling spend?\\u2019 \\u2014 what would you say?",
            "What metrics do you track? (Cycle time, deploys, PRs, defects?)",
            "Have you quantified the ROI in \\u00a3 terms?",
            "What would it take to make the case for doubling the investment?",
            "Is \\u2018output per \\u00a3 of engineering cost\\u2019 something your board/PE tracks?"
        ],
        services: ["Measurement Framework Setup", "ROI Dashboard", "Investment Case Packaging"]
    }
];'''

with open('analysis/D55/ai-dlc/workshop.html', 'r', encoding='utf-8') as f:
    html = f.read()

start_marker = 'const dimensions = ['
end_marker = '\n// State'

start_idx = html.index(start_marker)
end_idx = html.index(end_marker)

html = html[:start_idx] + NEW_DIMENSIONS + html[end_idx:]

with open('analysis/D55/ai-dlc/workshop.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done - dimensions replaced in workshop.html")
