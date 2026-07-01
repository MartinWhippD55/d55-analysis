"""Generate AI-DLC workshop spreadsheets (Value Proposition Canvas + Service Catalogue).

Focus: AI in the Development Lifecycle — how to use AI for engineering, not general AI maturity.
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter


def create_value_proposition():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "AI-DLC Value Proposition"

    # Styles
    section_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    section_fill = PatternFill(start_color="334155", end_color="334155", fill_type="solid")
    wrap = Alignment(wrap_text=True, vertical="top")

    # Column widths
    for i, w in enumerate([5, 40, 5, 40, 5, 40], 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    # Title
    ws.merge_cells("B1:F1")
    ws["B1"] = "AI-DLC Workshop \u2014 Value Proposition Canvas"
    ws["B1"].font = Font(name="Calibri", size=16, bold=True)

    ws.merge_cells("B2:F2")
    ws["B2"] = "How to use AI in the Development Lifecycle \u2014 D55 Service Offering"
    ws["B2"].font = Font(name="Calibri", size=11, italic=True, color="64748B")

    # Row 4: Vertical / Sub-segment / Prospects
    row = 4
    for col, text in [("B", "Vertical Name"), ("D", "Sub-Segment"), ("F", "Prospective Customers")]:
        ws[f"{col}{row}"] = text
        ws[f"{col}{row}"].font = section_font
        ws[f"{col}{row}"].fill = section_fill

    ws["B5"] = "AI-Assisted Engineering"
    ws["D5"] = (
        "Mid-market engineering orgs (20-200 devs) who want to adopt AI-assisted "
        "development but are struggling with adoption, process change, or proving ROI"
    )
    ws["F5"] = "(List target customers here)"
    for c in ["B5", "D5", "F5"]:
        ws[c].alignment = wrap

    # Section: Pain Points
    row = 7
    for col, text in [("B", "Customer Pain Points"), ("D", "Our Value Proposition"), ("F", "Metrics We Impact")]:
        ws[f"{col}{row}"] = text
        ws[f"{col}{row}"].font = section_font
        ws[f"{col}{row}"].fill = section_fill

    pains = [
        (
            "Bought Copilot licences but adoption is patchy \u2014 some devs love it, others ignore it",
            "AI Tooling Rollout: standard configuration, shared skills/playbooks, MCP server setup, "
            "onboarding programme that gets every developer effective quickly",
            "% daily active users\nOnboarding time (days \u2192 hours)\nDeveloper satisfaction score",
        ),
        (
            "Devs are faster but output quality is inconsistent \u2014 garbage specs at 5x speed",
            "AI-First Delivery Lifecycle Workshop: teach teams to spec for AI-first delivery. "
            "More time in design, contracts/APIs upfront, specs that AI can consume",
            "Rework rate\nDefect density\nSpec-to-delivery ratio\nTime in design vs build",
        ),
        (
            "POs/BAs/PMs can't keep up \u2014 they've become the bottleneck now devs go 3-5x faster",
            "Process Redesign + Role Redefinition: adapt ceremonies, redefine coordination roles, "
            "introduce AI-assisted spec writing and prioritisation for the 'middle layer'",
            "Lead time (ticket \u2192 production)\nPR review wait time\nSprint predictability",
        ),
        (
            "Can't prove ROI to the board/PE \u2014 'it feels faster' but no hard numbers",
            "Measurement Framework + ROI Dashboard: define metrics, establish baseline, "
            "track before/after, package the investment case for finance/board/PE",
            "Cycle time\nDeployment frequency\nCost per feature\nOutput per \u00a3 of eng cost",
        ),
        (
            "Governance gap \u2014 devs pasting prod data into AI tools, no policy, no audit trail",
            "AI Usage Policy + DLP Implementation: approved tool list, enterprise agreements, "
            "correct region, code provenance tracking, EU AI Act classification",
            "Policy compliance rate\nData leakage incidents\nAudit readiness time",
        ),
        (
            "Resistance from senior engineers and coordination roles \u2014 adoption stalling",
            "Four Fears Diagnostic + Upskilling Programme: diagnose resistance patterns, "
            "tailor interventions per role, redefine value of coordination roles in AI-first world",
            "Adoption rate across roles\nRetention of key staff\nTime to productivity for new joiners",
        ),
    ]

    for i, (pain, vp, metrics) in enumerate(pains):
        r = row + 1 + i
        ws[f"B{r}"] = pain
        ws[f"D{r}"] = vp
        ws[f"F{r}"] = metrics
        for c in [f"B{r}", f"D{r}", f"F{r}"]:
            ws[c].alignment = wrap

    # Section: Transformation & Growth
    row = 15
    for col, text in [("B", "Customer Transformation & Growth"), ("D", "Our Value Proposition"), ("F", "Metrics We Impact")]:
        ws[f"{col}{row}"] = text
        ws[f"{col}{row}"].font = section_font
        ws[f"{col}{row}"].fill = section_fill

    transforms = [
        (
            "Want engineering to be a competitive advantage \u2014 not just a cost centre",
            "8-Week Prove-It Model: embed D55 engineers in a squad, apply AI-first delivery "
            "on real work, demonstrate 3-5x improvement with metrics, produce rollout playbook",
            "Output per engineer (before/after)\nRelease cadence\nValuation multiple (PE angle)",
        ),
        (
            "Need to scale AI-assisted development from one team to the whole org",
            "Discovery & Strategy Session: produce a costed roadmap for org-wide rollout. "
            "Identify blockers per team. Phase the transition. Build internal champions.",
            "% teams at Level 3+\nOrg-wide productivity gain\nRollout velocity (teams/quarter)",
        ),
        (
            "Want to attract and retain top engineering talent with AI-native ways of working",
            "AI-Native Engineering Culture: standard tooling, shared knowledge bases, "
            "community of practice, continuous skill evolution, public-facing AI engineering brand",
            "Offer acceptance rate\nAttrition rate\nGlassdoor/employer brand metrics",
        ),
    ]

    for i, (growth, vp, metrics) in enumerate(transforms):
        r = row + 1 + i
        ws[f"B{r}"] = growth
        ws[f"D{r}"] = vp
        ws[f"F{r}"] = metrics
        for c in [f"B{r}", f"D{r}", f"F{r}"]:
            ws[c].alignment = wrap

    # Section: Why Us / Why Now
    row = 20
    for col, text in [("B", "WHY D55?"), ("D", "WHY NOW?"), ("F", "TECHNOLOGIES")]:
        ws[f"{col}{row}"] = text
        ws[f"{col}{row}"].font = section_font
        ws[f"{col}{row}"].fill = section_fill

    ws["B21"] = (
        "\u2022 We've actually shipped with AI-native teams at scale \u2014 not theory\n"
        "\u2022 We know what breaks when AI works (middle-layer bottleneck, spec quality, process)\n"
        "\u2022 Forward deployed engineers who build AND upskill \u2014 not a permanent dependency\n"
        "\u2022 8-week prove-it model with metrics from day one\n"
        "\u2022 Free assessment lowers barrier \u2014 you see value before you spend"
    )
    ws["D21"] = (
        "\u2022 AI developer tooling is mature enough to deliver 3-5x now (not 'soon')\n"
        "\u2022 Cost is trivial: ~\u00a3200/seat/month for 3-5x productivity\n"
        "\u2022 Competitors are adopting \u2014 delay is the real cost\n"
        "\u2022 EU AI Act compliance deadlines approaching\n"
        "\u2022 PE/board pressure for engineering efficiency gains"
    )
    ws["F21"] = (
        "\u2022 GitHub Copilot / Amazon CodeWhisperer / Amazon Q\n"
        "\u2022 Claude / Anthropic (agentic development)\n"
        "\u2022 Kiro / Cursor / agentic IDEs\n"
        "\u2022 MCP Servers (Jira, GitHub, DB integrations)\n"
        "\u2022 Playwright MCP (automated regression)\n"
        "\u2022 AWS CodePipeline / CI/CD\n"
        "\u2022 Infrastructure as Code (CDK/Terraform)"
    )
    for c in ["B21", "D21", "F21"]:
        ws[c].alignment = wrap

    # Elevator Pitch
    row = 24
    ws.merge_cells(f"B{row}:F{row}")
    ws[f"B{row}"] = "ELEVATOR PITCH"
    ws[f"B{row}"].font = section_font
    ws[f"B{row}"].fill = section_fill

    ws.merge_cells("B25:F25")
    ws["B25"] = (
        "Your developers have AI tools. But are they actually faster? Is the process adapted? "
        "Can you prove it? Book an hour with us \u2014 we'll assess your AI-assisted development "
        "readiness across 8 dimensions, show you where the gaps are, and tell you exactly what "
        "it takes to close them. Free. One hour. A radar chart and roadmap you can take to your board."
    )
    ws["B25"].alignment = wrap
    ws["B25"].font = Font(name="Calibri", size=11, italic=True)

    wb.save("analysis/D55/ai-dlc/spreadsheets/AI-DLC Value Proposition Canvas.xlsx")
    print("Created: AI-DLC Value Proposition Canvas.xlsx")


def create_service_catalogue():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "AI-DLC Service Catalogue"

    # Styles
    section_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    subsection_font = Font(name="Calibri", size=10, bold=True)
    section_fill = PatternFill(start_color="334155", end_color="334155", fill_type="solid")
    wrap = Alignment(wrap_text=True, vertical="top")

    ws.column_dimensions["A"].width = 3
    ws.column_dimensions["B"].width = 30
    ws.column_dimensions["C"].width = 80

    # Title
    ws.merge_cells("B1:C1")
    ws["B1"] = "AI-DLC Workshop \u2014 Service Catalogue"
    ws["B1"].font = Font(name="Calibri", size=16, bold=True)

    ws.merge_cells("B2:C2")
    ws["B2"] = "AI in the Development Lifecycle \u2014 Assessment & Delivery Services"
    ws["B2"].font = Font(name="Calibri", size=11, italic=True, color="64748B")

    row = 4
    ws[f"B{row}"] = "SERVICE NAME"
    ws[f"B{row}"].font = section_font
    ws[f"B{row}"].fill = section_fill
    ws[f"C{row}"] = "AI-DLC Assessment Workshop"
    ws[f"C{row}"].font = section_font
    ws[f"C{row}"].fill = section_fill

    row = 6
    ws[f"B{row}"] = "SERVICE DESCRIPTION"
    ws[f"B{row}"].font = subsection_font
    ws[f"C{row}"] = (
        "A free, structured 1-hour assessment that scores an engineering organisation across 8 "
        "dimensions of AI-assisted development readiness: Leadership & Mandate, Developer Tooling, "
        "Specification & Design, Delivery Process, Testing & Quality, Governance & Security, "
        "Team Adaptation, and Metrics & ROI. Produces a radar chart, gap analysis, and indicative "
        "roadmap. The output drives further paid engagements."
    )
    ws[f"C{row}"].alignment = wrap

    row = 8
    ws[f"B{row}"] = "IDEAL CUSTOMER PROFILE"
    ws[f"B{row}"].font = subsection_font
    ws[f"C{row}"] = (
        "\u2022 Mid-market engineering org (20\u2013200 developers)\n"
        "\u2022 On AWS (or committed to AWS)\n"
        "\u2022 Have purchased or are considering AI dev tooling (Copilot, Claude, etc.)\n"
        "\u2022 Struggling with: patchy adoption, can't prove ROI, process hasn't adapted, "
        "or resistance from parts of the team\n"
        "\u2022 Executive sponsor exists (CTO/VP Eng) who wants this to work\n"
        "\u2022 PE-backed or board-level pressure for engineering efficiency preferred"
    )
    ws[f"C{row}"].alignment = wrap

    row = 10
    ws[f"B{row}"] = "CUSTOMER CHALLENGES"
    ws[f"B{row}"].font = subsection_font
    ws[f"C{row}"] = (
        "\u2022 Bought licences but adoption is patchy \u2014 ROI unclear\n"
        "\u2022 Devs faster but quality inconsistent \u2014 specs haven't adapted\n"
        "\u2022 POs/BAs/PMs becoming bottlenecks \u2014 process unchanged\n"
        "\u2022 No governance \u2014 data leaking into AI tools, no audit trail\n"
        "\u2022 Resistance from seniors or coordination roles \u2014 adoption stalling\n"
        "\u2022 Can't quantify the gain \u2014 'it feels faster' but no numbers for the board"
    )
    ws[f"C{row}"].alignment = wrap

    # Qualifying Questions
    row = 12
    ws[f"B{row}"] = "QUALIFYING QUESTIONS"
    ws[f"B{row}"].font = section_font
    ws[f"B{row}"].fill = section_fill
    ws[f"C{row}"] = ""
    ws[f"C{row}"].fill = section_fill

    qualifying = [
        ("Tooling Status", [
            "Are developers currently using AI-assisted coding tools? Which ones?",
            "How long have they been in use? Enterprise or individual licences?",
            "What percentage of developers are actively using them?",
        ]),
        ("Adoption & Pain", [
            "What's working well? What's not?",
            "Have you seen productivity improvements? Can you quantify them?",
            "Is there resistance? From whom?",
        ]),
        ("Mandate & Budget", [
            "Is there executive sponsorship for AI-assisted development specifically?",
            "Is there budget for consulting/implementation support?",
            "What does 'success' look like for you in 12 months?",
        ]),
        ("Disqualifiers", [
            "Fewer than 20 engineers \u2192 too small for embedded model",
            "Not on AWS and no plans to move \u2192 our delivery is AWS-native",
            "No executive sponsor AND no budget \u2192 can't act on the output",
            "Already engaged with another consultancy on same scope \u2192 redirect",
        ]),
    ]

    row = 13
    for category, questions in qualifying:
        ws[f"B{row}"] = category
        ws[f"B{row}"].font = subsection_font
        ws[f"C{row}"] = "\n".join(f"\u2022 {q}" for q in questions)
        ws[f"C{row}"].alignment = wrap
        row += 1

    # Discovery Questions
    row += 1
    ws[f"B{row}"] = "WORKSHOP DIMENSIONS"
    ws[f"B{row}"].font = section_font
    ws[f"B{row}"].fill = section_fill
    ws[f"C{row}"] = "(8 dimensions assessed during the 1-hour session)"
    ws[f"C{row}"].font = section_font
    ws[f"C{row}"].fill = section_fill

    dimensions = [
        ("1. Leadership & Mandate", [
            "Who sponsors AI-assisted development? Optional, encouraged, or mandated?",
            "Has the investment case been made to finance/board?",
        ]),
        ("2. Developer Tooling & Adoption", [
            "What tools are in use? What % use daily? Standard config or ad-hoc?",
            "Gap between best adopter and least engaged?",
        ]),
        ("3. Specification & Design", [
            "Time in design vs implementation \u2014 has the ratio changed?",
            "Are specs written for AI consumption? Contracts defined upfront?",
        ]),
        ("4. Delivery Process & Ceremonies", [
            "Have ceremonies adapted? Where are the new bottlenecks?",
            "Can POs/BAs keep pace with developer velocity?",
        ]),
        ("5. Testing & Quality", [
            "How is AI-generated code validated? Same bar as human code?",
            "Automated regression? Human-in-the-loop at integration points?",
        ]),
        ("6. Governance, Security & Compliance", [
            "AI usage policy? DLP controls? Enterprise agreements?",
            "Code provenance tracking? EU AI Act classification?",
        ]),
        ("7. Team Adaptation & Skills", [
            "Where is resistance? Which roles? (Use Four Fears to diagnose)",
            "Training programme? Middle layer adapting or bottlenecking?",
        ]),
        ("8. Metrics & ROI", [
            "What evidence exists? Cycle time, PRs, deploys, defects?",
            "Can you make the case to the CFO/board in \u00a3 terms?",
        ]),
    ]

    row += 1
    for category, questions in dimensions:
        ws[f"B{row}"] = category
        ws[f"B{row}"].font = subsection_font
        ws[f"C{row}"] = "\n".join(f"\u2022 {q}" for q in questions)
        ws[f"C{row}"].alignment = wrap
        row += 1

    # Service Deliverables
    row += 1
    ws[f"B{row}"] = "SERVICE DELIVERABLES"
    ws[f"B{row}"].font = section_font
    ws[f"B{row}"].fill = section_fill
    ws[f"C{row}"] = ""
    ws[f"C{row}"].fill = section_fill

    row += 1
    ws[f"B{row}"] = "Assessment Output (Free)"
    ws[f"B{row}"].font = subsection_font
    ws[f"C{row}"] = (
        "\u2022 8-dimension radar chart (current vs target state)\n"
        "\u2022 Gap analysis with severity scoring\n"
        "\u2022 Recommended services mapped to each gap\n"
        "\u2022 Indicative runbook (phased by priority)\n"
        "\u2022 Engagement model recommendation\n"
        "\u2022 Written summary with direct quotes and narrative (within 48 hours)"
    )
    ws[f"C{row}"].alignment = wrap

    row += 1
    ws[f"B{row}"] = "Follow-on Services"
    ws[f"B{row}"].font = subsection_font
    ws[f"C{row}"] = (
        "1. Discovery & Strategy Session \u2014 \u00a330\u201350k\n"
        "   Costed roadmap for org-wide AI-assisted development rollout. 4\u20136 weeks.\n\n"
        "2. Prescriptive Workshops \u2014 \u00a35\u201315k per module\n"
        "   Modules: AI-First Delivery Lifecycle | Developer Tooling Setup | Governance & DLP | "
        "Process & Ceremonies | Testing Strategy | Metrics & ROI | Four Fears (Team Change)\n\n"
        "3. Embedded Team / 8-Week Prove-It \u2014 \u00a315\u201325k per engineer/month\n"
        "   Weeks 1\u20132: Assess codebase, tooling, adoption barriers\n"
        "   Weeks 3\u20136: Embed in squad, apply AI-first delivery, track metrics\n"
        "   Weeks 7\u20138: Demonstrate improvement, produce playbooks, rollout plan\n"
        "   D55 embeds, proves, then enables. Not a permanent dependency.\n\n"
        "4. Runbook & Asset Delivery \u2014 from \u00a320k (or included with Discovery)\n"
        "   Prescriptive step-by-step playbook: standard configs, skills files, process changes, "
        "role definitions, measurement framework. The asset your team follows after we leave."
    )
    ws[f"C{row}"].alignment = wrap

    # Benefits
    row += 2
    ws[f"B{row}"] = "BENEFITS TO CUSTOMER"
    ws[f"B{row}"].font = section_font
    ws[f"B{row}"].fill = section_fill
    ws[f"C{row}"] = ""
    ws[f"C{row}"].fill = section_fill

    row += 1
    ws[f"C{row}"] = (
        "\u2022 Clarity in 1 hour \u2014 know exactly where you stand with AI-assisted development\n"
        "\u2022 No upfront cost \u2014 assessment is free, choose what (if anything) to buy\n"
        "\u2022 Proven economics: ~\u00a3200/seat/month delivers ~3-5x developer productivity\n"
        "  For 50 engineers: ~\u00a3120k/year for output equivalent to 150-250 engineers\n"
        "\u2022 8-week prove-it: see results with real metrics before committing to scale\n"
        "\u2022 Not a permanent dependency \u2014 we produce playbooks and leave\n"
        "\u2022 Process adapted, not just tools deployed \u2014 the second-order effects handled\n"
        "\u2022 Resistance diagnosed and addressed \u2014 not ignored until it blocks adoption\n"
        "\u2022 The real cost is delay, not investment"
    )
    ws[f"C{row}"].alignment = wrap

    # Who needs to be in the room
    row += 2
    ws[f"B{row}"] = "WHO WE NEED IN THE ROOM"
    ws[f"B{row}"].font = section_font
    ws[f"B{row}"].fill = section_fill
    ws[f"C{row}"] = ""
    ws[f"C{row}"].fill = section_fill

    row += 1
    ws[f"B{row}"] = "For the Assessment"
    ws[f"B{row}"].font = subsection_font
    ws[f"C{row}"] = (
        "\u2022 CTO / VP Engineering (decision maker, mandate perspective)\n"
        "\u2022 Engineering Manager or Tech Lead (ground-truth on tooling and adoption)\n"
        "\u2022 A Product Owner or Delivery Lead (process and coordination perspective)\n"
        "3\u20134 people. Enough to score honestly, few enough for real conversation."
    )
    ws[f"C{row}"].alignment = wrap

    row += 1
    ws[f"B{row}"] = "For Workshops"
    ws[f"B{row}"].font = subsection_font
    ws[f"C{row}"] = (
        "\u2022 AI-First Delivery Lifecycle: Engineering leads + POs + Scrum Masters\n"
        "\u2022 Developer Tooling: Senior engineers, tech leads (hands-on)\n"
        "\u2022 Governance & DLP: CTO + security + compliance\n"
        "\u2022 Four Fears / Team Change: Leadership + HR + people who'll champion or block\n"
        "\u2022 Metrics & ROI: Engineering leads + Finance\n\n"
        "Typically 4\u201310 people per workshop.\n"
        "Key learning: include POs/BAs/PMs early \u2014 they become the bottleneck "
        "when devs go faster and need to adapt too."
    )
    ws[f"C{row}"].alignment = wrap

    # Key Frameworks
    row += 2
    ws[f"B{row}"] = "KEY FRAMEWORKS"
    ws[f"B{row}"].font = section_font
    ws[f"B{row}"].fill = section_fill
    ws[f"C{row}"] = "(Proven in delivery \u2014 core IP of this offering)"
    ws[f"C{row}"].font = section_font
    ws[f"C{row}"].fill = section_fill

    row += 1
    ws[f"B{row}"] = "AI-First Delivery Lifecycle"
    ws[f"B{row}"].font = subsection_font
    ws[f"C{row}"] = (
        "When implementation goes 5x faster, clarity of intent becomes the bottleneck.\n\n"
        "The lifecycle shifts toward design-up-front (NOT waterfall):\n"
        "1. Analysis & Design \u2014 more time here. Clear, structured specs.\n"
        "2. Contracts & Integration Points \u2014 defined before build.\n"
        "3. Implementation \u2014 devs with agentic tooling against well-defined specs.\n"
        "4. Testing \u2014 human-in-the-loop + automated regression.\n"
        "5. Documentation \u2014 AI-generated assets.\n\n"
        "Garbage specs at 5x speed = garbage 5x faster.\n"
        "Design discipline is the multiplier on the multiplier."
    )
    ws[f"C{row}"].alignment = wrap

    row += 1
    ws[f"B{row}"] = "Four Fears Framework"
    ws[f"B{row}"].font = subsection_font
    ws[f"C{row}"] = (
        "Diagnostic for AI adoption resistance:\n\n"
        "\u2022 Controller: 'I can't manage what I can't understand' \u2192 "
        "AI gives MORE oversight, not less\n"
        "\u2022 Driver: 'This could go wrong' \u2192 "
        "AI compresses feedback loops, fail faster and cheaper\n"
        "\u2022 Stabiliser: 'My position is threatened' \u2192 "
        "Orchestrators of AI become MORE valuable\n"
        "\u2022 Influencer: 'What's my value if AI does the work?' \u2192 "
        "AI handles grunt work, you get more stage\n\n"
        "Common pattern: POs/BAs/PMs are Controllers + Stabilisers."
    )
    ws[f"C{row}"].alignment = wrap

    row += 1
    ws[f"B{row}"] = "Middle-Layer Bottleneck"
    ws[f"B{row}"].font = subsection_font
    ws[f"C{row}"] = (
        "When devs go 3-5x faster:\n"
        "\u2022 POs can't write specs fast enough\n"
        "\u2022 BAs can't break down requirements at pace\n"
        "\u2022 PMs can't coordinate the new velocity\n\n"
        "They become the constraint. Address by:\n"
        "\u2022 AI-assisted spec writing for POs\n"
        "\u2022 Structured templates that reduce ambiguity\n"
        "\u2022 1-on-1 coaching and training\n"
        "\u2022 Process redesign (continuous flow, not batch sprints)"
    )
    ws[f"C{row}"].alignment = wrap

    row += 1
    ws[f"B{row}"] = "8-Week Prove-It Model"
    ws[f"B{row}"].font = subsection_font
    ws[f"C{row}"] = (
        "Default shape for embedded engagements:\n\n"
        "Weeks 1\u20132: ASSESS\n"
        "\u2022 Assess codebase, tooling, adoption barriers\n"
        "\u2022 Diagnose resistance patterns (Four Fears)\n"
        "\u2022 Identify quick wins\n\n"
        "Weeks 3\u20136: PROVE\n"
        "\u2022 Embed in a squad, apply AI-first delivery on real work\n"
        "\u2022 Track metrics from day one\n\n"
        "Weeks 7\u20138: TRANSLATE\n"
        "\u2022 Demonstrate improvement with hard numbers\n"
        "\u2022 Produce reusable playbooks and configs\n"
        "\u2022 Deliver rollout plan for other squads\n\n"
        "One squad proves it. That squad becomes the reference to pull others forward."
    )
    ws[f"C{row}"].alignment = wrap

    row += 1
    ws[f"B{row}"] = "The Economics"
    ws[f"B{row}"].font = subsection_font
    ws[f"C{row}"] = (
        "\u2022 AI dev tooling: ~\u00a3150\u2013200/seat/month\n"
        "\u2022 Observed productivity gain: 3\u20135x\n"
        "\u2022 For 50 engineers: ~\u00a3120k/year for output of 150\u2013250 engineers\n"
        "\u2022 The real cost is DELAY, not investment\n\n"
        "PE/CFO framing: AI-native engineering = valuation multiplier at exit.\n"
        "Output per \u00a3 of engineering cost is the metric that matters."
    )
    ws[f"C{row}"].alignment = wrap

    wb.save("analysis/D55/ai-dlc/spreadsheets/AI-DLC Service Catalogue.xlsx")
    print("Created: AI-DLC Service Catalogue.xlsx")


if __name__ == "__main__":
    create_value_proposition()
    create_service_catalogue()
