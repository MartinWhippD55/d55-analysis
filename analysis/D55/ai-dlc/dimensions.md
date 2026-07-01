# AI-DLC Workshop — Assessment Dimensions

These are the axes of the radar chart. Each dimension is scored on a 1–5 maturity scale for both **current state** and **desired state** (target within 12–18 months). The gap between the two drives the roadmap.

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

**Key workshop questions:**
- Who owns AI in your organisation? Is there an executive sponsor?
- Can you point to a document that links AI initiatives to specific business outcomes?
- How are AI projects prioritised today? What gets funded, what doesn't, and why?
- When did the board last discuss AI? What was the conversation about?
- If AI budgets were cut tomorrow, who would fight for them and with what evidence?

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

**Key workshop questions:**
- Where does your data live today? How many separate systems would we need to touch to get a full picture?
- Do you have a data catalogue? Who maintains it? Do people actually use it?
- If I asked for a clean, joined dataset across customers, transactions, and product — how long would that take to produce?
- What's your biggest data quality pain point right now?
- How do you handle PII and sensitive data access? Is it policy-driven or ad-hoc?

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

**Key workshop questions:**
- How many separate consoles, tools, or environments does a data/AI practitioner touch in a typical week?
- What's the journey from "I have an idea" to "it's running in production"? How long, how many hand-offs?
- Who manages the infrastructure underneath your AI/data workloads? How much of their time goes to maintenance vs new work?
- If a new joiner started tomorrow, how long before they're productive on the platform?
- What's your biggest frustration with the current tooling?

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

**Key workshop questions:**
- How many people work on data and AI full-time? How many wear it as a second hat?
- When a senior data engineer leaves, what breaks? How long to backfill effectively?
- Who's the bottleneck in the team today? What are they spending their time on?
- Is there a training or upskilling programme for AI? Who's been through it?
- If you could add three roles tomorrow, what would they be and why?

---

## 5. Governance, Risk & Compliance

**What we're assessing:** Are guardrails in place to use AI responsibly, or is it the wild west?

| Score | Level | Description |
|-------|-------|-------------|
| 1 | Absent | No AI governance framework. No consideration of bias, explainability, or regulatory requirements. |
| 2 | Aware | Leadership aware of AI risks. Some ad-hoc review of models before deployment. No formal policy. |
| 3 | Defined | AI governance policy exists. Risk assessment for new AI use cases. Data privacy handled. Basic model documentation. |
| 4 | Operationalised | Governance embedded in the development lifecycle. Model cards, bias testing, explainability tooling in use. Audit trail for decisions. EU AI Act posture understood. |
| 5 | Proactive | Continuous monitoring of deployed models for drift, fairness, and compliance. Automated guardrails. Regulatory horizon scanning. Governance enables speed rather than blocking it. |

**Key workshop questions:**
- Do you have an AI usage policy? Who wrote it, who enforces it, who's read it?
- When was the last time someone asked "should we be doing this?" about an AI use case? What happened?
- How do you document what a model does, what data it uses, and what decisions it influences?
- Are you aware of the EU AI Act and its implications for your use cases? What's your current posture?
- If a regulator asked tomorrow "show me how this AI decision was made" — could you?

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

**Key workshop questions:**
- How many AI/ML models do you have in production today? How did they get there?
- What happens when a model's performance degrades? How do you know, and what do you do?
- Tell me about the last model that failed in production. What happened? How long to fix?
- What's the gap between the AI experiments the team is running and what's actually shipping?
- If I asked "deploy this model to production by Friday" — is that realistic, or laughable?
- How much time does your team spend in design and specification vs implementation? Has that ratio changed with AI tooling?
- When devs go faster with AI assistance, where does the bottleneck shift to? (Specs? Reviews? Coordination?)

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

**Key workshop questions:**
- Do you know what you spend on AI and data today? Per team? Per project?
- Last time finance asked "what are we getting for this AI investment?" — what was the answer?
- Are there workloads where you suspect spend is too high but can't prove it?
- How do you decide whether to continue, scale, or kill an AI initiative?
- What does the conversation with the CFO about AI investment look like today?

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

**Key workshop questions:**
- How do non-technical staff feel about AI? Excited? Threatened? Indifferent?
- Are there AI tools in use outside of the data/tech team? Which ones? How did they get there?
- What internal communication has gone out about AI in the last 6 months?
- Is there a community of practice, a Slack channel, a lunch-and-learn series — anything that builds AI literacy?
- If a frontline employee had an idea for how AI could help their job, what would they do with it? Who would they tell?
- Where is the resistance coming from? Which roles or personality types are pushing back? (Use Four Fears to diagnose)
- When devs adopted AI tooling and went faster, did coordination roles (POs, BAs, PMs) keep pace or become a bottleneck?
- Has anyone left or been moved because they couldn't adapt? How was that handled?

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
| Data Readiness | Data Platform Build, Data Quality Programme, Lakehouse Migration |
| Tooling & Platform | SageMaker Unified Studio Deployment, Platform Engineering, Developer Productivity |
| Team & Capability | Embedded Squads, Training & Upskilling, Recruitment Support |
| Governance, Risk & Compliance | AI Governance Framework, EU AI Act Readiness, Model Risk Assessment |
| Delivery & Operations | MLOps Implementation, CI/CD for Models, Observability & Monitoring, AI-First Delivery Lifecycle Workshop |
| Cost & Value Management | FinOps Programme, Cost Optimisation Review, ROI Measurement Framework |
| Culture & Adoption | AI Champions Programme, Change Management, AI Literacy Training, Four Fears Diagnostic & Intervention |
