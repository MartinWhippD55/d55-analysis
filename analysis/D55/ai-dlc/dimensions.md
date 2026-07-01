# AI-DLC Workshop — Assessment Dimensions

These are the axes of the radar chart. Each dimension assesses a specific aspect of **AI-enabled engineering readiness** — how effectively the organisation uses AI within its development lifecycle. This is not a general "AI maturity" assessment. The use case IS AI for development.

## Scoring Guidance for Facilitators

- **★ Must-ask questions** — always ask these. They're your minimum for a credible score.
- **Go-deeper questions** — use when conversation flows, score is ambiguous, or time allows.
- **Calibration examples** — provided per dimension. Use these to validate scoring: "that sounds like a Level 3 to me — does that resonate?"
- **When between levels** — score the lower. More credible to understate than overstate.
- **When split within a dimension** (e.g., Level 4 on one sub-aspect but Level 2 on another) — score the dominant pattern and note the split in your write-up.
- **Let the prospect self-score first** — then validate or gently challenge. Their perception vs reality is valuable data.
- **Disagreement between attendees is gold** — don't resolve it, capture it. It reveals internal alignment gaps.

---

## 1. Leadership & Mandate

**What we're assessing:** Is there executive sponsorship and organisational commitment to AI-assisted development, or are developers going rogue with tools?

| Score | Level | Description |
|-------|-------|-------------|
| 1 | Absent | No leadership acknowledgement of AI-assisted development. Developers may be using tools on their own with no mandate or budget. |
| 2 | Aware | Leadership knows developers are experimenting with AI tooling. No formal position, no budget, no policy — just awareness. |
| 3 | Endorsed | Executive sponsor identified. Budget allocated for AI dev tooling. Organisational position: "we want this." But adoption is still optional/organic. |
| 4 | Mandated | AI-assisted development is the expected way of working. Tooling provided and supported. KPIs exist. Investment case proven for at least one team. |
| 5 | Strategic | AI-native engineering is a stated competitive advantage. Board-level visibility. Actively marketed to talent. Continuous investment in tooling and process evolution. |

**Calibration examples:**
- Level 2: "A few devs use Copilot on personal accounts. CTO knows but hasn't taken a position."
- Level 3: "CTO bought enterprise Copilot licences last quarter. Everyone's encouraged to use it but there's no measurement."
- Level 4: "AI tooling is standard for all engineers. We track productivity metrics. The investment case has been presented to the board."

**Key workshop questions:**

★ Must-ask:
- Who made the decision to adopt AI dev tooling? Is there an executive sponsor?
- Is AI-assisted development optional, encouraged, or mandated?
- Has the investment case for AI tooling been made to finance/board?

Go deeper:
- If AI tooling budgets were cut tomorrow, who would fight for them?
- How does the board/PE see AI-assisted development — cost play, velocity play, or valuation play?
- Is AI-native engineering part of your talent/recruitment messaging?

---

## 2. Developer Tooling & Adoption

**What we're assessing:** Are developers actually using AI tools effectively, or are licences gathering dust?

| Score | Level | Description |
|-------|-------|-------------|
| 1 | None | No AI developer tooling in use. No Copilot, no Claude, no agentic IDEs. |
| 2 | Experimenting | Some developers using AI tools ad-hoc (free tiers, personal accounts). No consistency, no shared configuration, no support. |
| 3 | Provisioned | Enterprise licences deployed. Most developers have access to AI-assisted coding tools. Some using effectively, others barely touching them. |
| 4 | Effective | AI tooling embedded in daily workflow for the majority. Shared configurations, skills/playbooks, and MCP servers in use. Developers report meaningful productivity improvement. |
| 5 | Advanced | Agentic workflows standard. Developers working with AI on specs, not just code generation. Custom tooling (MCP servers, skills, knowledge bases) tuned to the codebase. AI is a pair-programming partner, not just autocomplete. |

**Calibration examples:**
- Level 2: "Maybe 30% of devs use Copilot. Some love it, some ignore it. No shared setup."
- Level 3: "Everyone has Copilot Enterprise. Usage is patchy — some teams use it heavily, others barely."
- Level 4: "Standard IDE setup includes Copilot + Claude. We have shared skills files and MCP connections to Jira/GitHub. Devs say they can't imagine going back."

**Key workshop questions:**

★ Must-ask:
- What AI developer tools are in use today? (Copilot, Claude, Cursor, Kiro, other?)
- What percentage of developers use them daily vs occasionally vs never?
- Do developers report meaningful productivity gains? Can they quantify?

Go deeper:
- Is there a standard configuration/setup that new joiners get, or does everyone roll their own?
- Are there shared skills, playbooks, or MCP servers that connect AI tools to your systems (Jira, GitHub, databases)?
- What's the gap between your best AI-assisted developer and your least engaged? What explains it?
- How long does onboarding take with AI tooling vs without?

---

## 3. Specification & Design Process

**What we're assessing:** Has the organisation recognised that when implementation goes 5x faster, the bottleneck shifts to clarity of intent — and adapted accordingly?

| Score | Level | Description |
|-------|-------|-------------|
| 1 | Traditional | No change to specification process despite AI tooling. Requirements are vague, verbal, or buried in Jira tickets. |
| 2 | Recognising | Some awareness that "AI needs better specs" but no systematic change. Individual developers compensating by writing their own specs before prompting. |
| 3 | Adapting | Formal recognition that design-up-front matters more. Spec templates exist. Integration points and contracts defined before implementation. Some teams investing more time in analysis. |
| 4 | Disciplined | AI-first delivery lifecycle in operation: more time in analysis/design, less in implementation. Specs are written to be consumed by both humans and AI. Contracts and APIs defined upfront. Architectural decisions documented before build. |
| 5 | Optimised | Specs are first-class engineering artefacts. AI assists in spec generation from requirements. Continuous feedback loop: poor specs caught early by AI-generated test failures. Spec quality directly correlated with output quality — and measured. |

**Calibration examples:**
- Level 2: "Our best devs write detailed prompts before they start. Most don't — they just tab-complete."
- Level 3: "We introduced spec templates last quarter. Teams that use them ship faster. Not everyone uses them yet."
- Level 4: "Every piece of work starts with a spec and contract review. AI tools work against those specs. We've seen quality go up and rework go down."

**Key workshop questions:**

★ Must-ask:
- How much time does the team spend in design/specification vs implementation? Has that ratio changed since adopting AI tooling?
- When a developer starts a piece of work, what do they start with? A Jira ticket? A spec? A conversation?
- Has the quality of output changed since AI adoption — for better or worse?

Go deeper:
- "Garbage specs at 5x speed = garbage 5x faster." Does that resonate?
- Are integration points and APIs defined before implementation starts, or discovered during?
- Who writes the specs? Has that role changed?
- Are specs written in a way that AI tools can consume them (structured, unambiguous)?

---

## 4. Delivery Process & Ceremonies

**What we're assessing:** Have sprints, standups, reviews, and ways of working adapted to the new velocity — or is the process unchanged and becoming a bottleneck?

| Score | Level | Description |
|-------|-------|-------------|
| 1 | Unchanged | Same agile ceremonies, same cadence, same roles — despite developers being 3-5x faster. Process hasn't noticed the change. |
| 2 | Straining | Cracks appearing. Sprint capacity calculations wrong. Stories completed faster than POs can write them. PR review queues growing. Coordination roles feeling pressure. |
| 3 | Adjusting | Some conscious adaptation. Sprint length may have shortened. Review processes streamlined. Some ceremony changes. But ad-hoc, not systematic. |
| 4 | Redesigned | Delivery process deliberately reshaped for AI-assisted development. Faster cycles. Continuous flow replacing batch sprints. PR review adapted (AI-assisted review, different standards for AI-generated code). Coordination roles redefined. |
| 5 | Continuous | Near-continuous delivery. Ceremonies minimal and focused on alignment, not status. AI handles routine coordination (auto-generated specs from requirements, auto-linked PRs, auto-updated boards). Humans focus on decisions, not process. |

**Calibration examples:**
- Level 2: "Devs finish stories in 2 days but wait 3 days for review. POs are writing the next sprint's tickets while the current one's still running."
- Level 3: "We moved to 1-week sprints and added mid-sprint reviews. PR reviews are faster now — we use an AI review agent for first pass."
- Level 4: "We've ditched fixed sprints for continuous flow. AI generates draft specs from epics. Human reviews focus on intent and edge cases, not boilerplate."

**Key workshop questions:**

★ Must-ask:
- Have your ceremonies or delivery cadence changed since AI tooling adoption?
- Where are the bottlenecks now? (If devs are faster, what's the new constraint?)
- How long does a PR sit in review? Has that changed?

Go deeper:
- Are POs/BAs able to keep up with the demand for well-specified work?
- Has sprint velocity metrics become meaningless now that output per developer has changed?
- Are you using AI for any coordination tasks (review, linking, status updates)?
- What's your release cadence? Has it changed?

---

## 5. Testing & Quality Assurance

**What we're assessing:** Is testing adapted for AI-generated code — or is the test strategy the same as before?

| Score | Level | Description |
|-------|-------|-------------|
| 1 | Unchanged | Same manual testing approach as pre-AI. No AI-assisted test generation. No automated regression for AI-generated code. |
| 2 | Basic | AI tools generate some unit tests alongside code. Developer-driven, not systematic. No specific QA process for AI-generated code. |
| 3 | Integrated | AI-generated code has the same test coverage requirements as human code. Some automated regression (e.g., Playwright MCP for UI). Test data generation assisted by AI. |
| 4 | Comprehensive | AI-assisted testing integrated into CI/CD. Human-in-the-loop validation at integration points. Regression suites auto-maintained. Confidence in AI-generated code is evidence-based, not assumed. |
| 5 | Continuous | Full test automation with AI. Tests generated from specs automatically. Mutation testing and property-based testing standard. Quality gates differentiate between AI-generated and human code where needed. Feedback loop from production issues to test coverage. |

**Calibration examples:**
- Level 2: "Copilot writes unit tests if you ask. Some devs do, some don't. No policy."
- Level 3: "All code needs 80% coverage regardless of who (or what) wrote it. We use Playwright for regression on key flows."
- Level 4: "AI generates tests from our spec documents. CI won't pass without them. We have a human review gate before anything touches production."

**Key workshop questions:**

★ Must-ask:
- How do you validate AI-generated code? Is there a specific process?
- What's your automated test coverage? Has it changed since AI adoption?
- Do you trust AI-generated code the same as human-written code?

Go deeper:
- Are tests generated alongside code, or as a separate step?
- Who reviews AI-generated code before it merges? Same bar as human code?
- Have you seen new categories of bugs from AI-generated code?
- Is there human-in-the-loop validation at integration points?

---

## 6. Governance, Security & Compliance

**What we're assessing:** Are AI development tools used safely — or is sensitive data leaking into prompts, code generated without audit trail, and compliance unaddressed?

| Score | Level | Description |
|-------|-------|-------------|
| 1 | Unmanaged | No policy on AI tool usage. Developers pasting production data into ChatGPT. No audit trail on AI-generated code. No consideration of IP, data leakage, or compliance. |
| 2 | Aware | Leadership knows there are risks. Informal guidance ("don't paste customer data"). No formal policy, no technical controls, no audit. |
| 3 | Controlled | AI usage policy exists and is communicated. Approved tool list. Enterprise agreements in place (data not used for training). Workloads in correct region. Basic access controls. |
| 4 | Enforced | Technical controls in place: DLP for AI tools, approved model endpoints, audit trail on AI-generated code. Code provenance tracked. EU AI Act classification done (if applicable). Regular compliance reviews. |
| 5 | Embedded | Governance is automated and frictionless. Real-time DLP, automatic code provenance, compliance-as-code. Security red-teaming includes AI-specific threats (prompt injection, model exfiltration). Governance enables speed rather than blocking it. |

**Calibration examples:**
- Level 2: "We told people not to paste customer data into ChatGPT. No idea if they listened."
- Level 3: "Enterprise Copilot agreement in place — data excluded from training. Policy published. Tools run in EU region."
- Level 4: "DLP prevents sensitive data reaching AI tools. All AI-generated code flagged in git. Quarterly compliance review covers AI usage."

**Key workshop questions:**

★ Must-ask:
- Do you have a policy on what data can and can't be used with AI tools?
- Are your AI tools running on enterprise agreements with data protection guarantees?
- Can you trace which code was AI-generated vs human-written?

Go deeper:
- If a regulator asked "how do you govern AI in your development process" — what would you show them?
- Are there DLP controls preventing sensitive data from reaching AI tool endpoints?
- Have you classified your AI usage under EU AI Act risk categories?
- What's your supply chain risk posture for AI dependencies (model providers, APIs)?

---

## 7. Team Adaptation & Skills

**What we're assessing:** Are people adapting to AI-assisted development — or are coordination roles becoming bottlenecks and resistance patterns blocking adoption?

| Score | Level | Description |
|-------|-------|-------------|
| 1 | Resistant | Significant resistance to AI tooling. Senior engineers feel undermined. Coordination roles threatened. No training or support. |
| 2 | Mixed | Some enthusiastic adopters, some holdouts. No formal training. Knowledge concentrated in champions. Middle layer (POs/BAs/PMs) starting to feel pressure but not adapting. |
| 3 | Training | Formal training/upskilling programme exists. Resistance patterns identified. Some coordination roles actively adapting (e.g., POs learning to write better specs). Champions supported. |
| 4 | Adapted | Majority of team working effectively with AI. Coordination roles redefined (POs as spec owners, BAs as prompt engineers for requirements). Resistance addressed through tailored interventions. New joiners onboarded with AI-first from day one. |
| 5 | Native | AI-assisted development is the culture, not a change programme. Team attracts talent because of AI-native ways of working. Continuous skill evolution. Everyone — not just developers — uses AI in their role. |

**Calibration examples:**
- Level 2: "Our best devs love it. Some seniors refuse. POs are complaining they can't write tickets fast enough."
- Level 3: "We ran a workshop on AI-assisted development. Most engineers engaged. POs are starting to write structured specs. Still some holdouts."
- Level 4: "Everyone uses AI daily. POs write specs in a format AI can consume. New joiners are productive in days, not weeks. The senior who was resistant left — the rest adapted."

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

**Key workshop questions:**

★ Must-ask:
- Where is resistance coming from? Which roles or personality types push back?
- When devs went faster, did coordination roles (POs, BAs, PMs) keep pace or become the bottleneck?
- Is there a training/upskilling programme specifically for AI-assisted development?

Go deeper:
- Who's your biggest AI champion? Who's your biggest blocker? What's the difference?
- Has anyone left or been moved because they couldn't adapt?
- How long does it take a new joiner to become productive with AI tooling?
- Are non-engineering roles (POs, QA, BA) using AI in their work too?

---

## 8. Metrics & ROI

**What we're assessing:** Can you prove AI-assisted development is working — with numbers, not vibes?

| Score | Level | Description |
|-------|-------|-------------|
| 1 | Unmeasured | No metrics on AI-assisted development impact. "It feels faster" but no evidence. |
| 2 | Anecdotal | Individual testimonials. Some developers say "I'm 3x faster." No systematic measurement. Cannot make the case to finance. |
| 3 | Tracked | Key metrics tracked: deployment frequency, cycle time, PR throughput, defect rate. Before/after comparison available. Investment case can be articulated. |
| 4 | Proven | ROI quantified and reported. Cost per feature known. Productivity per £ of engineering spend measured. The case is made to finance/board/PE with hard data. |
| 5 | Optimised | Continuous measurement drives continuous improvement. Metrics inform tooling choices, process changes, and investment decisions. Output per £ of engineering cost is a primary KPI. AI tooling ROI is a competitive/valuation talking point. |

**Calibration examples:**
- Level 2: "A few devs say they're much faster. My gut says it's working. I can't prove it to the CFO."
- Level 3: "We track cycle time, PRs/week, and deployment frequency. All improved ~40% since AI tooling rollout. I can show a before/after."
- Level 4: "We know it costs £200/seat/month and delivers approximately 3-5x productivity. For our 50 engineers, that's £120k/year for output we'd otherwise need 150-250 engineers to achieve. The board has seen this."

**Key workshop questions:**

★ Must-ask:
- How do you know AI-assisted development is working? What evidence do you have?
- If the CFO asked "what are we getting for the AI tooling spend?" — what would you say?
- What metrics do you track? (Cycle time, deployment frequency, PRs, defect rate, etc.)

Go deeper:
- Have you quantified the ROI in £ terms?
- Do you measure individual or team productivity? Both?
- What would it take to make the case for doubling the investment?
- Is "output per £ of engineering cost" something your board/PE tracks?

---

## Radar Chart

The output is an 8-axis radar chart with two overlays:

- **Blue (Current State):** Where the organisation is today (scored 1–5 per dimension)
- **Cyan (Target State):** Where they want to be in 12–18 months

The gap between the two shapes is the opportunity. Each gap maps to D55 service offerings.

---

## Mapping Gaps to Services

| Dimension | Example D55 Services |
|-----------|---------------------|
| Leadership & Mandate | AI-First Strategy Workshop, Investment Case Development, Board Presentation Support |
| Developer Tooling & Adoption | AI Tooling Rollout, Standard Configuration Build, MCP Server Setup, Knowledgebase Creation |
| Specification & Design | AI-First Delivery Lifecycle Workshop, Spec Template Development, Contract-First Design Coaching |
| Delivery Process & Ceremonies | Process Redesign Workshop, Ceremony Adaptation, Continuous Flow Implementation |
| Testing & Quality | Test Automation Strategy, AI-Assisted QA Setup, Playwright Regression Implementation |
| Governance, Security & Compliance | AI Usage Policy, DLP Implementation, EU AI Act Classification, Code Provenance Tooling |
| Team Adaptation & Skills | Four Fears Diagnostic & Intervention, Upskilling Programme, Role Redefinition Coaching |
| Metrics & ROI | Measurement Framework Setup, ROI Dashboard, Investment Case Packaging |
