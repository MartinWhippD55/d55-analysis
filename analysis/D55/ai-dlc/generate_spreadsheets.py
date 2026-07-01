"""Generate AI-DLC workshop spreadsheets (Value Proposition Canvas + Service Catalogue)."""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
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
    ws["B2"] = "D55 AI Development Lifecycle Assessment"
    ws["B2"].font = Font(name="Calibri", size=11, italic=True, color="64748B")

    # Row 4: Vertical / Sub-segment / Prospects
    row = 4
    for col, text in [("B", "Vertical Name"), ("D", "Sub-Segment"), ("F", "Prospective Customers")]:
        ws[f"{col}{row}"] = text
        ws[f"{col}{row}"].font = section_font
        ws[f"{col}{row}"].fill = section_fill

    ws["B5"] = "AI Adoption & Transformation"
    ws["D5"] = "Mid-market organisations (250-2000 employees) looking to adopt or scale AI"
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
            "No clear AI strategy \u2014 experimentation without business alignment",
            "Free AI-DLC Assessment: 1-hour structured workshop producing a radar chart of current vs target maturity across 8 dimensions",
            "Time to AI strategy: weeks \u2192 1 hour\nClarity of AI investment priorities",
        ),
        (
            "Tool sprawl \u2014 too many disconnected platforms, high onboarding time",
            "Platform consolidation advisory + prescriptive tooling workshops for dev teams",
            "Tools touched per week\nNew joiner productivity time\nPlatform maintenance burden",
        ),
        (
            "AI stays in notebooks \u2014 can't ship to production reliably",
            "MLOps implementation + CI/CD for models + observability",
            "Models in production\nDeployment frequency\nMTTR for model failures",
        ),
        (
            "No visibility of AI spend or ROI \u2014 CFO can't justify investment",
            "FinOps programme + per-project cost allocation + ROI measurement framework",
            "Cost per AI project\nROI per initiative\nBudget forecast accuracy",
        ),
        (
            "Governance gap \u2014 no policy, no compliance posture, EU AI Act exposure",
            "AI Governance framework + compliance posture review + region lockdown",
            "Audit readiness time\nPolicy coverage\nRegulatory risk score",
        ),
        (
            "Skills gap \u2014 dependent on heroes, no career path, can't recruit",
            "Embedded squads + training/upskilling + forward deployed engineers",
            "Bus factor\nTime to backfill\nInternal AI literacy rate",
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
            "Want AI to be a competitive differentiator, not just a cost play",
            "AI Strategy Workshop \u2192 Use Case Prioritisation \u2192 Business Case Development",
            "Revenue from AI-enabled products\nCompetitive win rate\nTime to market for AI features",
        ),
        (
            "Need to scale AI from 1-2 use cases to a portfolio",
            "Discovery & Strategy Session (DSD) producing a costed roadmap + runbook",
            "Active AI use cases\nPortfolio ROI\nReuse of platform/data assets",
        ),
        (
            "Want to embed AI literacy across the business, not just tech team",
            "AI Champions Programme + Change Management + Ceremony/Process changes",
            "Non-tech AI tool adoption\nIdeas submitted from frontline\nTraining completion rates",
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
        "\u2022 AWS Advanced Partner with AI/ML specialisation\n"
        "\u2022 Proven delivery across data platforms, MLOps, and GenAI\n"
        "\u2022 Forward deployed engineers who build AND upskill\n"
        "\u2022 Free assessment lowers barrier to engagement\n"
        "\u2022 Prescriptive runbooks \u2014 not just advice, but a playbook"
    )
    ws["D21"] = (
        "\u2022 EU AI Act compliance deadlines approaching\n"
        "\u2022 AI moving from experiment to board-level priority\n"
        "\u2022 Competitors adopting \u2014 window to differentiate closing\n"
        "\u2022 Cost pressure demands ROI visibility\n"
        "\u2022 Talent market means build-vs-buy decision is now"
    )
    ws["F21"] = (
        "\u2022 AWS SageMaker Unified Studio\n"
        "\u2022 Bedrock / GenAI\n"
        "\u2022 Glue / Athena / Lakehouse\n"
        "\u2022 MLOps (SageMaker Pipelines, CodePipeline)\n"
        "\u2022 QuickSight\n"
        "\u2022 Infrastructure as Code (CDK/Terraform)\n"
        "\u2022 Kiro / AI-assisted development"
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
        "Book an hour with us. We'll show you exactly where you are with AI, where you want to be, "
        "and what it takes to get there \u2014 for free. You leave with a radar chart, a gap analysis, "
        "and a clear roadmap. No commitment, just clarity. If you want us to help you execute, "
        "we've got workshops, embedded engineers, and runbooks ready to go."
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

    # Column widths
    ws.column_dimensions["A"].width = 3
    ws.column_dimensions["B"].width = 30
    ws.column_dimensions["C"].width = 80

    # Title
    ws.merge_cells("B1:C1")
    ws["B1"] = "AI-DLC Workshop \u2014 Service Catalogue"
    ws["B1"].font = Font(name="Calibri", size=16, bold=True)

    ws.merge_cells("B2:C2")
    ws["B2"] = "D55 AI Development Lifecycle Assessment & Delivery Services"
    ws["B2"].font = Font(name="Calibri", size=11, italic=True, color="64748B")

    # --- SERVICE: AI-DLC Assessment Workshop ---
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
        "A free, structured 1-hour assessment workshop that scores an organisation across 8 AI maturity "
        "dimensions (Strategy, Data, Tooling, Team, Governance, Delivery, Cost, Culture). "
        "Produces a radar chart showing current state vs target state, a gap analysis with recommended "
        "services, and an indicative runbook. The output drives further paid engagements."
    )
    ws[f"C{row}"].alignment = wrap

    row = 8
    ws[f"B{row}"] = "IDEAL CUSTOMER PROFILE"
    ws[f"B{row}"].font = subsection_font
    ws[f"C{row}"] = (
        "\u2022 Mid-market / SME (250\u20132000 employees)\n"
        "\u2022 Some AI experimentation but struggling to scale or show ROI\n"
        "\u2022 Leadership bought into AI but unclear on strategy or next steps\n"
        "\u2022 May have data platform but AI workloads not in production\n"
        "\u2022 Feeling pressure from competitors, regulation, or board\n"
        "\u2022 On AWS or open to AWS (for service delivery alignment)"
    )
    ws[f"C{row}"].alignment = wrap

    row = 10
    ws[f"B{row}"] = "CUSTOMER CHALLENGES"
    ws[f"B{row}"].font = subsection_font
    ws[f"C{row}"] = (
        "\u2022 No clear AI strategy tied to business outcomes\n"
        "\u2022 Tool and platform sprawl \u2014 high friction, long onboarding\n"
        "\u2022 AI work stuck in experimentation, not reaching production\n"
        "\u2022 No governance framework \u2014 EU AI Act exposure unknown\n"
        "\u2022 Can't quantify AI spend or demonstrate ROI to finance\n"
        "\u2022 Skills concentrated in individuals, no scalable capability\n"
        "\u2022 Culture not ready \u2014 AI seen as tech team's problem, not business-wide"
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
        ("AI Maturity", [
            "Have you started using AI in any capacity (even experimentation)?",
            "Is there executive sponsorship or budget for AI initiatives?",
            "Do you have data/ML practitioners on staff, or is it outsourced?",
        ]),
        ("Ambition & Urgency", [
            "Where does AI sit on the board agenda? Is there a deadline or trigger?",
            "Are competitors doing things with AI that worry you?",
            "Is there a compliance trigger (EU AI Act, sector regulation)?",
        ]),
        ("Scale & Complexity", [
            "How many people would be involved in or affected by AI adoption?",
            "How many data sources and systems are in play?",
            "What's your current cloud platform, and is that settled?",
        ]),
        ("Budget & Decision", [
            "Is there budget allocated for AI strategy or implementation work?",
            "Who makes the decision to engage external support?",
            "What does 'decided' look like for you, and by when?",
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
    ws[f"B{row}"] = "DISCOVERY QUESTIONS"
    ws[f"B{row}"].font = section_font
    ws[f"B{row}"].fill = section_fill
    ws[f"C{row}"] = "(Used during the workshop itself)"
    ws[f"C{row}"].font = section_font
    ws[f"C{row}"].fill = section_fill

    discovery = [
        ("Strategy & Alignment", [
            "Who owns AI in your organisation? Is there an executive sponsor?",
            "Can you point to a document linking AI initiatives to business outcomes?",
            "How are AI projects prioritised? What gets funded and why?",
            "If AI budgets were cut tomorrow, who'd fight for them?",
        ]),
        ("Data Readiness", [
            "Where does your data live today? How many systems for a full picture?",
            "Do you have a data catalogue? Do people actually use it?",
            "How long to produce a clean joined dataset across key entities?",
            "What's your biggest data quality pain point?",
        ]),
        ("Tooling & Platform", [
            "How many tools does a practitioner touch in a typical week?",
            "What's the journey from idea to production? How many hand-offs?",
            "If a new joiner started tomorrow, how long before productive?",
            "What's your biggest frustration with current tooling?",
        ]),
        ("Team & Capability", [
            "How many people on data/AI full-time vs second hat?",
            "When a senior leaves, what breaks? How long to backfill?",
            "Is there a training programme for AI? Who's been through it?",
            "If you could add three roles tomorrow, what and why?",
        ]),
        ("Governance & Compliance", [
            "Do you have an AI usage policy? Who enforces it?",
            "How do you document what a model does and what decisions it influences?",
            "Are you aware of EU AI Act implications for your use cases?",
            "If a regulator asked 'show me how this decision was made' \u2014 could you?",
        ]),
        ("Delivery & Operations", [
            "How many models in production? How did they get there?",
            "What happens when model performance degrades?",
            "What's the gap between experiments and what's shipping?",
            "'Deploy this by Friday' \u2014 realistic or laughable?",
        ]),
        ("Cost & Value", [
            "Do you know AI/data spend per team or project?",
            "Last time finance asked 'what are we getting?' \u2014 what was the answer?",
            "How do you decide to continue, scale, or kill an AI initiative?",
        ]),
        ("Culture & Adoption", [
            "How do non-technical staff feel about AI?",
            "Are there AI tools in use outside the data/tech team?",
            "If a frontline employee had an AI idea, who would they tell?",
        ]),
    ]

    row += 1
    for category, questions in discovery:
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
        "\u2022 Engagement model recommendation"
    )
    ws[f"C{row}"].alignment = wrap

    row += 1
    ws[f"B{row}"] = "Follow-on Services"
    ws[f"B{row}"].font = subsection_font
    ws[f"C{row}"] = (
        "1. Discovery & Strategy Session (DSD) \u2014 \u00a330\u201350k\n"
        "   Fully costed AI/data strategy + roadmap. Pure consultancy. 4\u20136 weeks.\n\n"
        "2. Prescriptive Workshops \u2014 \u00a35\u201315k per module\n"
        "   How to spec | Developer tooling | Compliance & governance | MLOps | "
        "Process & ceremonies | Data platform | Cost optimisation\n\n"
        "3. Embedded Team / FDEs \u2014 \u00a315\u201325k per engineer/month\n"
        "   Forward deployed engineers alongside customer team. Build + upskill.\n\n"
        "4. Runbook & Asset Delivery \u2014 from \u00a320k (or included with DSD)\n"
        "   Prescriptive step-by-step guide with decision points and options."
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
        "\u2022 Clarity in 1 hour \u2014 know exactly where you stand and what to do next\n"
        "\u2022 No upfront cost \u2014 assessment is free, you choose what (if anything) to buy\n"
        "\u2022 Visual gap analysis makes the case for investment to leadership\n"
        "\u2022 Roadmap is actionable \u2014 phased, prioritised, with clear deliverables\n"
        "\u2022 Flexible engagement \u2014 buy consultancy, workshops, or embedded people\n"
        "\u2022 Knowledge transfer built in \u2014 we upskill as we deliver\n"
        "\u2022 Prescriptive not theoretical \u2014 runbooks with specific steps, not just advice\n"
        "\u2022 AWS-native solutions with cost advantage over Snowflake/Databricks"
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
        "\u2022 CTO / VP Engineering / Head of Data (decision maker)\n"
        "\u2022 Senior data/ML engineer (technical reality check)\n"
        "\u2022 Someone from finance or ops (cost/value perspective)\n"
        "Optional: Product owner or business stakeholder"
    )
    ws[f"C{row}"].alignment = wrap

    row += 1
    ws[f"B{row}"] = "For Workshops"
    ws[f"B{row}"].font = subsection_font
    ws[f"C{row}"] = (
        "\u2022 Varies by module \u2014 dev tooling needs engineers, governance needs legal/compliance\n"
        "\u2022 Typically 4\u201310 people per workshop\n"
        "\u2022 Mix of doers and decision makers"
    )
    ws[f"C{row}"].alignment = wrap

    wb.save("analysis/D55/ai-dlc/spreadsheets/AI-DLC Service Catalogue.xlsx")
    print("Created: AI-DLC Service Catalogue.xlsx")


if __name__ == "__main__":
    create_value_proposition()
    create_service_catalogue()
