# AI-DLC Workshop — Assessment Dimensions

These are the axes of the radar chart. Each dimension is scored on a 1–5 maturity scale for both **current state** and **desired state** (target within 12–18 months). The gap between the two drives the roadmap.

## Scoring Guidance for Facilitators

- **★ Must-ask questions** — always ask these. They're your minimum for a credible score.
- **Go-deeper questions** — use when conversation flows, score is ambiguous, or time allows.
- **Calibration examples** — provided per dimension. Use these to validate scoring: "that sounds like a Level 3 to me — does that resonate?"
- **When between levels** — score the lower. More credible to understate than overstate.
- **When split within a dimension** (e.g., Level 4 on data quality but Level 2 on catalogue) — score the dominant pattern and note the split in your write-up.
- **Let the prospect self-score first** — then validate or gently challenge. Their perception vs reality is valuable data.
- **Disagreement between attendees is gold** — don't resolve it, capture it. It reveals internal alignment gaps.

---

## 1. Strategy & Alignment

**What we're assessing:** Is AI adoption tied to business outcomes, or is it experimentation without direction?

| Score | Level | Description |
|-------|-------|-------------|
| 1 | Ad-hoc | No formal AI strategy. Pockets of interest but no executive sponsorship or budget. |
| 2 | Exploring | Leadership acknowledges AI opportunity. Some budget allocated but no clear OKRs or success criteria tied to AI. |
| 3 | Defined | AI strategy documented and linked to 2–3 business outcomes. Executive sponsor identified. Budget ring-fenced. |
| 4 | Integrated | AI initiatives are part of the business planning cycle. Portfolio of use cases prioritised by ROI. Regular board-level reporting. |
| 5 | Differentiating | AI is a core competitive advantage. Strategy is adaptive — continuously reprioritised based on outcomes. AI P&L visible. |

**Calibration examples:**
- Level 2: "Our CTO mentions AI in town halls but there's no written strategy or dedicated budget"
- Level 3: "We have an AI strategy doc linked to 3 business outcomes, a named sponsor, and a ring-fenced budget — but it's not yet part of the regular planning cycle"
- Level 4: "AI initiatives are prioritised alongside everything else in quarterly planning, with ROI-based scoring"

**Key workshop questions:**

★ Must-ask:
- Who owns AI in your organisation? Is there an executive sponsor?
- How are AI projects prioritised today? What gets funded, what doesn't, and why?
- If AI budgets were cut tomorrow, who would fight for them and with what evidence?

Go deeper (if time allows):
- Can you point to a document that links AI initiatives to specific business outcomes?
- When did the board last discuss AI? What was the conversation about?

---

## 2. Data Readiness

**What we're assessing:** Is the data foundation in place to support AI workloads at the ambition level?

| Score | Level | Description |
|-------|-------|-------------|
| 1 | Siloed | Data lives in disconnected systems. No catalogue, no lineage, no consistent quality standards. |
| 2 | Consolidating | Some centralisation effort underway (warehouse/lakehouse). Basic quality checks exist but coverage is patchy. |
| 3 | Governed | Central data platform with catalogue, lineage, and ownership. Quality monitored. Access controlled. Most analytical workloads served. |
| 4 | Optimised | Data products defined and SLA'd. Self-serve access for analysts and data scientists. Real-time and batch coexist. Feature stores emerging. |
| 5 | AI-Native | Data platform designed for AI workloads. Feature stores, vector stores, retrieval pipelines, and feedback loops are production-grade. Data flywheel spinning. |

**Calibration examples:**
- Level 2: "We have a Snowflake warehouse for BI but data quality is inconsistent and there's no formal catalogue"
- Level 3: "Central lakehouse with dbt transformations, basic data catalogue, defined ownership per domain"
- Level 4: "Self-serve data products with SLAs, real-time and batch coexist, feature store in early use"

**Key workshop questions:**

★ Must-ask:
- Where does your data live today? How many separate systems would we need to touch to get a full picture?
- If I asked for a clean, joined dataset across customers, transactions, and product — how long would that take to produce?
- What's your biggest data quality pain point right now?

Go deeper (if time allows):
- Do you have a data catalogue? Who maintains it? Do people actually use it?
- How do you handle PII and sensitive data access? Is it policy-driven or ad-hoc?
- Do you have legacy systems that would need migration or integration before AI workloads are viable?

---

## 3. Tooling & Platform

**What we're assessing:** Is there a coherent platform for building, deploying, and operating AI/ML workloads?

| Score | Level | Description |
|-------|-------|-------------|
| 1 | Fragmented | Individual tools chosen per project. No shared infrastructure. Notebooks on laptops. |
| 2 | Partial | Some shared tooling (e.g. a BI tool, a notebook server) but no end-to-end platform. Lots of hand-offs between environments. |
| 3 | Platform | A defined platform exists covering development, training, and deployment. Shared compute, shared storage, consistent access patterns. |
| 4 | Integrated | Platform covers the full lifecycle — experimentation through to production monitoring. CI/CD for models. Infrastructure as code. Self-serve provisioning. |
| 5 | Composable | Platform is modular and extensible. Teams can bring new tools without breaking governance. Multi-modal (SQL, Python, GenAI). One pane of glass for cost and governance. |

**Calibration examples:**
- Level 2: "We have a notebook server and a BI tool but devs manually copy models to production VMs"
- Level 3: "SageMaker Studio for ML work, shared S3 buckets, consistent IAM — but deployment is still scripted, not CI/CD"
- Level 4: "Full platform: SageMaker + CodePipeline + IaC, self-serve provisioning, new joiners productive in days"

**Key workshop questions:**

★ Must-ask:
- How many separate consoles, tools, or environments does a data/AI practitioner touch in a typical week?
- What's the journey from "I have an idea" to "it's running in production"? How long, how many hand-offs?
- If a new joiner started tomorrow, how long before they're productive on the platform?

Go deeper (if time allows):
- Who manages the infrastructure underneath your AI/data workloads? How much of their time goes to maintenance vs new work?
- What's your biggest frustration with the current tooling?
- Are your developers using AI-assisted development tools (Copilot, Claude, agentic IDEs)? What's been the experience?

---

## 4. Team & Capability

**What we're assessing:** Do they have the right people with the right skills, or are they dependent on heroes and contractors?

| Score | Level | Description |
|-------|-------|-------------|
| 1 | Absent | No dedicated AI/ML roles. Data work done by generalists or outsourced entirely. |
| 2 | Emerging | 1–2 data/ML specialists. Knowledge concentrated in individuals. No career path or training programme. |
| 3 | Functional | Defined data/AI team with clear roles (engineers, scientists, analysts). Some cross-training. Recruitment pipeline exists. |
| 4 | Scaled | Multiple squads with embedded AI capability. Internal training/upskilling programme. Knowledge sharing culture. Low bus-factor risk. |
| 5 | Pervasive | AI literacy across the business. Non-technical staff use AI tools daily. Centre of excellence feeds capability into product teams. Talent is a magnet, not a problem. |

**Calibration examples:**
- Level 2: "One data scientist who does everything — if she leaves, we're back to square one"
- Level 3: "Team of 6 (2 engineers, 2 scientists, 2 analysts) with defined roles and a grad pipeline"
- Level 4: "3 squads with embedded ML capability, internal training programme, knowledge sharing culture"

**Key workshop questions:**

★ Must-ask:
- How many people work on data and AI full-time? How many wear it as a second hat?
- When a senior data engineer leaves, what breaks? How long to backfill effectively?
- Who's the bottleneck in the team today? What are they spending their time on?

Go deeper (if time allows):
- Is there a training or upskilling programme for AI? Who's been through it?
- If you could add three roles tomorrow, what would they be and why?
- When devs adopted AI tooling and went faster, did coordination roles (POs, BAs, PMs) keep pace or become the constraint?

---

## 5. Governance, Risk & Compliance

**What we're assessing:** Are guardrails in place to use AI responsibly and securely? Covers policy, regulation, and the security posture specific to AI workloads.

| Score | Level | Description |
|-------|-------|-------------|
| 1 | Absent | No AI governance framework. No consideration of bias, explainability, security, or regulatory requirements. Data leakage risk from AI tools unmanaged. |
| 2 | Aware | Leadership aware of AI risks. Some ad-hoc review of models before deployment. No formal policy. AI tooling used without data loss prevention controls. |
| 3 | Defined | AI governance policy exists. Risk assessment for new AI use cases. Data privacy handled. Basic model documentation. AI tools approved and provisioned centrally. Workloads running in correct region. Access locked down. |
| 4 | Operationalised | Governance embedded in the development lifecycle. Model cards, bias testing, explainability tooling in use. Audit trail for decisions. EU AI Act posture understood. AI-specific security controls: prompt injection mitigation, output filtering, data classification for LLM context, supply chain risk for AI dependencies assessed. |
| 5 | Proactive | Continuous monitoring of deployed models for drift, fairness, and compliance. Automated guardrails (input validation, output filtering, confidence thresholds). Regulatory horizon scanning. Governance enables speed rather than blocking it. Red-teaming for adversarial AI risks. GenAI safety playbook in production. |

**Calibration examples:**
- Level 2: "We use ChatGPT but there's no policy on what data you can paste in"
- Level 3: "We have an AI policy, approved tools list, and data is classified — but governance is a gate, not embedded in the workflow"
- Level 4: "Every model has a model card, we've done our EU AI Act risk classification, and AI security is part of our threat model"

**Key workshop questions:**

★ Must-ask:
- Do you have an AI usage policy? Who wrote it, who enforces it, who's read it?
- Are you aware of the EU AI Act and its implications for your use cases? What's your current posture?
- If a regulator asked tomorrow "show me how this AI decision was made" — could you?

Go deeper (if time allows):
- When was the last time someone asked "should we be doing this?" about an AI use case? What happened?
- How do you document what a model does, what data it uses, and what decisions it influences?
- What controls exist around data leakage from AI tools? (e.g., can developers paste production data into ChatGPT/Copilot?)
- Have you assessed AI-specific security risks — prompt injection, model exfiltration, adversarial inputs?
- Are AI workloads running in the correct region? Is access locked down and auditable?
- What's your supply chain risk posture for AI dependencies (model providers, embedding APIs, third-party tools)?

---

## 6. Delivery & Operations

**What we're assessing:** Can they ship AI into production reliably, or does everything die in the notebook? Is the development lifecycle adapted for AI-first delivery?

| Score | Level | Description |
|-------|-------|-------------|
| 1 | Experimental | AI work stays in notebooks/POCs. Nothing in production. No MLOps. No consideration of how AI changes delivery process. |
| 2 | Manual | Some models in production but deployed manually. No CI/CD for models. Monitoring is "someone checks it." Traditional agile without adaptation. |
| 3 | Repeatable | Defined deployment process. Some automation (CI/CD for models, basic monitoring). Rollback possible but painful. Starting to recognise that specs matter more when implementation is fast. |
| 4 | Automated | Full MLOps pipeline — automated training, testing, deployment, monitoring. Model registry. A/B testing. Design-up-front discipline: more time in analysis/spec, contracts and integration points defined before implementation. AI-assisted delivery (agentic tooling against well-defined specs). |
| 5 | Continuous | Models retrain on fresh data automatically. Feedback loops from production to development. Canary deployments. Self-healing pipelines. AI-first lifecycle fully embedded: clarity of intent is the performance multiplier. Specs, contracts, and architectural decisions made upfront because garbage specs at 5x speed = garbage 5x faster. |

**Calibration examples:**
- Level 2: "We have one model in prod — someone SSHs into a box and runs a script to update it"
- Level 3: "We have a CI/CD pipeline for model training and a basic monitoring dashboard — but rollback is painful"
- Level 4: "Full MLOps: automated retraining, model registry, A/B testing, canary deploys. Design-up-front discipline means specs are the bottleneck, not implementation"

**Key workshop questions:**

★ Must-ask:
- How many AI/ML models do you have in production today? How did they get there?
- What's the gap between the AI experiments the team is running and what's actually shipping?
- How much time does your team spend in design/spec vs implementation? Has that ratio changed with AI tooling?

Go deeper (if time allows):
- What happens when a model's performance degrades? How do you know, and what do you do?
- Tell me about the last model that failed in production. What happened? How long to fix?
- If I asked "deploy this model to production by Friday" — is that realistic, or laughable?
- When devs go faster with AI assistance, where does the bottleneck shift to — specs? Reviews? Coordination?

---

## 7. Cost & Value Management

**What we're assessing:** Can they see what AI costs them and what value it's generating, or is it a black hole?

| Score | Level | Description |
|-------|-------|-------------|
| 1 | Invisible | AI/data spend is buried in a general IT bill. No visibility, no allocation, no ROI measurement. |
| 2 | Aggregated | Total AI/data spend is known at a high level. No per-project or per-team breakdown. ROI is anecdotal. |
| 3 | Allocated | Spend attributed to teams or projects. Budget owners identified. Some use cases have measured ROI. |
| 4 | Optimised | Active cost management — right-sizing, spot/savings plans, architecture choices driven by cost. ROI measured per initiative. Portfolio-level view. |
| 5 | Value-Driven | Investment decisions based on proven ROI data. Continuous optimisation. Clear link between spend and business outcomes. CFO is a partner, not a blocker. |

**Calibration examples:**
- Level 2: "We know roughly what we spend on SageMaker in total but can't split it by team or project"
- Level 3: "Spend tagged by team using AWS cost allocation tags. A few projects have ROI calculated."
- Level 4: "Active FinOps practice: savings plans in place, right-sizing reviews quarterly, ROI measured per initiative and reported to finance"

**Key workshop questions:**

★ Must-ask:
- Do you know what you spend on AI and data today? Per team? Per project?
- Last time finance asked "what are we getting for this AI investment?" — what was the answer?
- How do you decide whether to continue, scale, or kill an AI initiative?

Go deeper (if time allows):
- Are there workloads where you suspect spend is too high but can't prove it?
- What does the conversation with the CFO about AI investment look like today?
- AI tooling costs ~£150–200/seat/month for ~5x developer productivity — have you done this maths for your team size?

---

## 8. Culture & Adoption

**What we're assessing:** Is AI something the whole business embraces, or is it an ivory tower exercise? Have resistance patterns been identified and addressed?

**The Four Fears Framework** (diagnostic tool for this dimension):

| | Past/Present Leaning | Future Thinking |
|---|---|---|
| **Tasks-oriented** | Loss of Control (Controller) — "I can't manage what I can't understand" | Project Failure (Driver) — "This could go wrong and I'll be accountable" |
| **People-oriented** | Disruption to Hierarchy (Stabiliser) — "My position/authority is under threat" | Feeling Overshadowed (Influencer) — "If AI does the impressive stuff, what's my value?" |

**The reframe — AI addresses each fear when positioned correctly:**
- Controllers get more oversight and observability, not less
- Drivers get faster, cheaper failure — compressed risk
- Stabilisers who lean in become orchestrators — more valuable
- Influencers get amplified — AI handles grunt work, they get more stage

| Score | Level | Description |
|-------|-------|-------------|
| 1 | Resistant | Scepticism or fear of AI across the business. No visible use. "That's not for us." Resistance patterns undiagnosed. |
| 2 | Curious | Interest from pockets of the business. A few champions experimenting. No formal support. Resistance exists but isn't being addressed. |
| 3 | Supported | Leadership endorses AI adoption. Internal comms and training. Some business teams using AI tools. Resistance patterns identified (Four Fears diagnosed) but not yet systematically addressed. |
| 4 | Embedded | AI tools are part of daily workflows for multiple teams. Non-technical staff use AI confidently. Resistance addressed through tailored interventions per role/personality. Community of practice active. Middle layer (POs, BAs, PMs) actively adapting. |
| 5 | Transformative | AI fundamentally changes how the business operates. New business models enabled. Continuous innovation from the ground up. Organisation attracts talent because of AI culture. All fear patterns resolved — people see AI as amplifier, not threat. |

**Calibration examples:**
- Level 2: "A few engineers use Copilot but leadership hasn't acknowledged it and there's no policy"
- Level 3: "CEO did a town hall on AI, we rolled out Copilot licences, and a few business teams use ChatGPT for drafts — but resistance from middle management is visible"
- Level 4: "Multiple teams using AI daily, community of practice running, PO/BA/PM roles actively adapting their processes, resistance patterns identified and being addressed"

**Key workshop questions:**

★ Must-ask:
- How do non-technical staff feel about AI? Excited? Threatened? Indifferent?
- Where is resistance coming from? Which roles or personality types are pushing back?
- When devs adopted AI and went faster, did coordination roles (POs, BAs, PMs) keep pace or become a bottleneck?

Go deeper (if time allows):
- Are there AI tools in use outside of the data/tech team? Which ones? How did they get there?
- What internal communication has gone out about AI in the last 6 months?
- Is there a community of practice, a Slack channel, a lunch-and-learn series — anything that builds AI literacy?
- If a frontline employee had an idea for how AI could help their job, what would they do with it? Who would they tell?
- Has anyone left or been moved because they couldn't adapt? How was that handled?

**Four Fears diagnostic** (use during this dimension to diagnose resistance patterns — see facilitator's guide for details).

---

## Radar Chart

The output is an 8-axis radar chart with two overlays:

- **Blue (Current State):** Where the customer is today (scored 1–5 per dimension)
- **Green (Target State):** Where they want to be in 12–18 months

The gap between the two shapes is the opportunity. Each gap maps to D55 service offerings.

---

## Mapping Gaps to Services

| Dimension | Example D55 Services |
|-----------|---------------------|
| Strategy & Alignment | AI Strategy Workshop, Use Case Prioritisation, Business Case Development |
| Data Readiness | Data Platform Build, Data Quality Programme, Lakehouse Migration, Legacy Integration & Extraction |
| Tooling & Platform | SageMaker Unified Studio Deployment, Platform Engineering, Developer Productivity, AI Tooling Rollout |
| Team & Capability | Embedded Squads, Training & Upskilling, Recruitment Support, Forward Deployed Engineers |
| Governance, Risk & Compliance | AI Governance Framework, EU AI Act Readiness, AI Security Review, Region & Access Lockdown |
| Delivery & Operations | MLOps Implementation, CI/CD for Models, Observability & Monitoring, AI-First Delivery Lifecycle Workshop |
| Cost & Value Management | FinOps Programme, Cost Optimisation Review, ROI Measurement Framework |
| Culture & Adoption | AI Champions Programme, Change Management, AI Literacy Training, Four Fears Diagnostic & Intervention |
