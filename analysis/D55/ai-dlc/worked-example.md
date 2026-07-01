# AI-DLC Assessment — Worked Example

*Fictional but realistic. Based on composite patterns from mid-market organisations. Use this to understand what a completed assessment looks like — the flow, the scoring rationale, the output, and the follow-up.*

---

## The Prospect: "Heron Financial"

- **Industry:** Financial services (lending platform)
- **Size:** ~600 employees, 80 engineers
- **Cloud:** AWS (3 years), modest Redshift + Lambda estate
- **Trigger:** New CTO hired 4 months ago; PE sponsor (Clearwater Capital) pushing for AI-enabled underwriting to improve unit economics before a 2027 exit
- **AI today:** 2 data scientists running experiments in notebooks; one credit scoring model in production (deployed manually 18 months ago, never retrained)

---

## Pre-Session Intake (Received 48 Hours Before)

| Question | Response |
|----------|----------|
| Employees | ~600 |
| Engineers | 80 (60 backend, 12 frontend, 5 data, 3 platform) |
| Cloud | AWS |
| AI adoption self-assessment | "Experimenting — a few POCs or pilots" |
| Trigger | "PE sponsor wants AI-driven underwriting improvements. New CTO mandate." |
| Biggest frustration | "Data science team builds things that never make it to production. Engineering won't touch their code." |
| Budget | "Yes — approved and ring-fenced (£500k for 12 months)" |
| Good outcome | "Leave with a clear picture of what we need to do first, second, third — and how much help we need." |
| In the room | Sarah Chen (CTO, 4 months in), Marcus Webb (Head of Data, 2 years), James Okafor (VP Engineering, 5 years) |

**Facilitator notes before session:** Good fit. Clear trigger (PE pressure + new CTO). Budget confirmed. Mix of perspectives in the room (new leader + incumbent veterans = potential tension). Watch for Controller/Stabiliser dynamics between Sarah (new, change-driving) and James (incumbent, may feel threatened).

---

## The Session

### Opening (0–5 min)

Introductions. Explained the format: "We'll walk through 8 dimensions of AI maturity. For each one, I'll ask a couple of questions, we'll discuss, and then score where you are today and where you'd like to be in 12–18 months. At the end, you'll see a radar chart showing the gaps. Takes about an hour."

Sarah: "Perfect. I've been here 4 months and I still don't have a clear picture of where we actually are versus where the board thinks we are."

*(Note: this framing — "the board thinks X, reality is Y" — is common. The assessment gives the CTO ammunition to have an honest conversation with the board.)*

---

### Dimension Scores

#### 1. Strategy & Alignment — Current: 2, Target: 4

**Key exchange:**
- Facilitator: "Who owns AI in your organisation?"
- Sarah: "Technically me, as of 4 months ago. Before that, nobody formally. Marcus's team was doing 'AI stuff' but it wasn't linked to any business outcome."
- Marcus: "That's fair. We had ideas but no mandate or budget until Sarah arrived."
- Facilitator: "Can you point to a document linking AI initiatives to business outcomes?"
- Sarah: "I've drafted one. It's not approved yet. The board wants 'AI-driven underwriting' but hasn't defined what success looks like."

**Scoring rationale:** Level 2 — leadership acknowledges the opportunity, budget exists, but no clear OKRs or documented strategy yet. Sarah is building this but it's not landed. Target of 4 (AI in planning cycle, prioritised by ROI) is realistic for 12-18 months given the PE pressure and budget.

---

#### 2. Data Readiness — Current: 2, Target: 4

**Key exchange:**
- Facilitator: "If I asked for a clean, joined dataset across customers, applications, and repayment history — how long?"
- Marcus: "Honestly? Two to three weeks. It's spread across Redshift, a legacy Oracle DB, and some CSVs that ops teams maintain in SharePoint."
- James: "And the Oracle system is the one nobody wants to touch."
- Facilitator: "Do you have a data catalogue?"
- Marcus: "We have a Confluence page that's 18 months out of date. Does that count?" *(laughs)*

**Scoring rationale:** Level 2 — some centralisation (Redshift) but coverage is patchy, no catalogue, legacy systems in play. Target of 4 is ambitious but achievable with investment (self-serve data products, proper catalogue, quality monitoring).

**Notable:** Legacy Oracle system flagged as integration challenge. This will need extraction/migration or API wrapping before AI workloads are viable at scale.

---

#### 3. Tooling & Platform — Current: 1, Target: 3

**Key exchange:**
- Facilitator: "How many separate tools does a data practitioner touch in a typical week?"
- Marcus: "My team? Jupyter on their laptops, Redshift via DBeaver, AWS console for S3, and then they email James's team when something needs deploying." *(James winces)*
- Facilitator: "If a new joiner started tomorrow, how long before they're productive?"
- Marcus: "On the data side? Weeks. They need access to 6 different systems and half the tribal knowledge is in people's heads."

**Scoring rationale:** Level 1 — fragmented, individual tools, notebooks on laptops, no shared platform. Target of 3 (defined platform covering dev, training, deployment) is realistic and would be transformative for them.

---

#### 4. Team & Capability — Current: 3, Target: 4

**Key exchange:**
- Facilitator: "Who's the bottleneck today?"
- James: "Marcus's team builds models. My team won't deploy them because they're unstructured Python scripts with no tests, no CI, no monitoring. We're stuck in the middle."
- Sarah: "And I've got 80 engineers who could be 5x more productive with AI tooling but nobody's rolled it out."
- Facilitator: "Is there a training programme for AI?"
- James: "No. A few people have done Coursera courses on their own time."

**Scoring rationale:** Level 3 — defined team with clear roles (data engineers, scientists, platform), some cross-training exists. But knowledge is concentrated and there's no upskilling programme. Target of 4 (multiple squads with embedded AI, internal training, low bus-factor) is a natural next step.

**Notable:** The tension between Marcus's team and James's team is a classic "data science vs engineering" divide. This is a delivery & process problem, not a people problem.

---

#### 5. Governance, Risk & Compliance — Current: 2, Target: 4

**Key exchange:**
- Facilitator: "Do you have an AI usage policy?"
- Sarah: "No. Some engineers use ChatGPT. I don't know what data they paste into it."
- Facilitator: "Are you aware of the EU AI Act implications? You're a lending platform — credit scoring is high-risk."
- Sarah: "...yes. That's on my list. We haven't done the classification yet."
- James: "Our credit model is basically a black box. If the FCA asked how a decision was made, we'd struggle."

**Scoring rationale:** Level 2 — leadership aware of risks, ad-hoc review exists (the credit model was "reviewed" once), but no formal policy, no data loss prevention for AI tools, no regulatory classification. Target of 4 given they're in financial services with a high-risk use case (credit decisioning) and regulatory pressure.

**Notable:** This is a potential urgent priority. Financial services + credit scoring + EU AI Act = they need governance before they scale, not after.

---

#### 6. Delivery & Operations — Current: 2, Target: 4

**Key exchange:**
- Facilitator: "How many models in production? How did they get there?"
- Marcus: "One. The credit model. I deployed it 18 months ago by SSHing into a box and running a script. It hasn't been retrained since."
- Facilitator: "What happens if its performance degrades?"
- Marcus: "We'd probably find out from complaints, if I'm honest."
- Facilitator: "How much time does the team spend in design/spec vs implementation?"
- James: "Almost none in spec. Engineers pick up tickets and start coding. With 80 devs that's... a lot of uncoordinated output."

**Scoring rationale:** Level 2 — one model in production deployed manually, no MLOps, no CI/CD for models, no monitoring. Target of 4 (full MLOps pipeline, design-up-front discipline, AI-assisted delivery) is where they need to be.

**Notable:** The "no time in spec" comment + 80 engineers = massive opportunity for AI-First Delivery Lifecycle intervention. If they adopt AI tooling without fixing spec discipline first, they'll produce garbage faster.

---

#### 7. Cost & Value Management — Current: 2, Target: 3

**Key exchange:**
- Facilitator: "Do you know what you spend on AI/data per team or project?"
- Sarah: "I know the total AWS bill. I can't split it by team, let alone by AI initiative."
- Facilitator: "Last time finance asked what they're getting for the AI investment?"
- Sarah: "They haven't yet — the budget was only approved 2 months ago. But they will. Clearwater will want to see ROI within 6 months."

**Scoring rationale:** Level 2 — total spend known at high level, no per-project allocation, ROI is "TBD." Target of 3 is realistic and necessary (spend attributed to projects, budget owners identified, some measured ROI) given PE pressure for ROI visibility.

---

#### 8. Culture & Adoption — Current: 2, Target: 4

**Key exchange:**
- Facilitator: "How do non-technical staff feel about AI?"
- Sarah: "Mixed. The exec team is excited. Middle management is nervous."
- Facilitator: "Where specifically is resistance coming from?"
- James: "Honestly? The POs and BAs are worried. If developers go faster, what's their role?"
- Sarah: "And some of the senior engineers feel like AI tooling undermines their expertise. 'I didn't need Copilot to get where I am.'"

**Four Fears diagnosis:**
- POs/BAs: Stabiliser pattern (hierarchy disruption) + Controller pattern (loss of oversight)
- Senior engineers: Influencer pattern (feeling overshadowed by tools)

**Scoring rationale:** Level 2 — pockets of interest (exec level), champions exist (Sarah), but resistance is present and unaddressed. Target of 4 (AI in daily workflows, resistance addressed, middle layer adapting) requires deliberate intervention.

---

## The Radar Chart

```
                    Strategy (2→4)
                         |
    Culture (2→4)        |        Data (2→4)
          \              |              /
           \             |             /
            \            |            /
  Cost (2→3) --------- [centre] --------- Tooling (1→3)
            /            |            \
           /             |             \
          /              |              \
   Delivery (2→4)       |       Team (3→4)
                         |
                  Governance (2→4)
```

**Visual impression:** Almost all dimensions at Level 1-2 current, targeting 3-4. Uniform gap pattern = systematic underinvestment, not a single weak spot. Tooling is the lowest (1) and the most foundational blocker.

---

## Live Results Reaction

Sarah: "That looks about right. Tooling at 1 — yeah, that's painful to see but it's true."

James: "I'm surprised Team came out at 3. I thought we'd be lower."

Facilitator: "You have clear roles, defined team structure, and a recruitment pipeline. The gap is in cross-training and embedded AI capability — that's what takes you from 3 to 4."

Marcus: "Governance scares me the most. We're a lender. If the FCA comes knocking..."

Facilitator: "That's exactly the right instinct. Given your sector, governance isn't just a nice-to-have — it's potentially a blocker on scaling anything else."

---

## Closing & Engagement Recommendation

**Total gap score: 17** (across 8 dimensions)
**Max single gap: 3** (Strategy, Governance, Delivery)
**Recommendation: Embedded Team** (total gap ≥ 16 triggers this recommendation)

**What was said in the room:**

Facilitator: "Based on the gaps, there are a few ways we can help. Given the breadth — you've got material gaps in 7 out of 8 dimensions — and the PE timeline, I'd suggest we start with an 8-week embedded engagement. Two engineers alongside your team for 8 weeks: assess, prove, translate. You'd see measurable results within 6 weeks and have a playbook for the rest of the org by week 8."

Sarah: "What does that look like commercially?"

Facilitator: "Two engineers for 8 weeks at our standard rate. I'll include options in the write-up — including a lighter-touch alternative if you want to start smaller."

Sarah: "Send me the write-up. I'll share it with Clearwater."

---

## Follow-Up Email (Sent 36 Hours Later)

---

**Subject: Your AI Maturity Assessment — Summary & Next Steps**

Hi Sarah, Marcus, James,

Thanks for the conversation on Tuesday. Genuinely useful session — you've clearly got a strong foundation (team, budget, executive mandate) but some critical gaps that need closing before you can scale AI safely. Here's the summary.

**Your Radar:**

[Radar chart image attached]

**Key findings:**

- **Governance (2→4):** Your most urgent gap given financial services regulation. Credit scoring is a high-risk use case under EU AI Act. You need a governance framework and AI security posture *before* you scale, not after. The current state (no policy, no model documentation, no DLP controls on AI tools) is a regulatory risk.

- **Tooling & Platform (1→3):** Your most foundational blocker. Until data practitioners have a shared platform (not notebooks on laptops), everything else is fighting gravity. This is also the fastest win — platform setup is a solved problem.

- **Delivery & Operations (2→4):** The credit model deployed manually 18 months ago with no monitoring tells the whole story. Combined with 80 engineers spending almost no time in spec, there's a massive opportunity: AI-First Delivery Lifecycle (more time in design, AI-assisted implementation against clear specs) could transform your output quality and velocity simultaneously.

**What we heard:**

- "Data science builds things that never make it to production. Engineering won't touch their code." — this is a process/platform problem, not a people problem. Solvable.
- "If the FCA asked how a decision was made, we'd struggle." — needs to be fixed urgently.
- "POs and BAs are worried. If devs go faster, what's their role?" — classic middle-layer bottleneck. Addressable through deliberate role evolution and our Four Fears intervention.

**Recommended next steps:**

1. **Primary: 8-Week Embedded Engagement (2 FDEs)**
   - Weeks 1-2: Assess your codebase, platform gaps, and adoption barriers in detail
   - Weeks 3-6: Embed in one squad, stand up a basic MLOps pipeline, apply AI-first delivery on a real piece of work, track metrics
   - Weeks 7-8: Demonstrate improvement with numbers, produce your playbook, deliver rollout plan
   - Investment: £40-50k per engineer for 8 weeks (~£80-100k total for the pair)
   - Output: measurable proof + reusable assets + rollout plan for remaining squads

2. **Alternative: Targeted Workshops (lighter touch)**
   - AI Governance Framework workshop (urgent — 1 day, get your policy and EU AI Act classification in place)
   - AI-First Delivery Lifecycle workshop (1 day — teach your 80 engineers how to spec for AI-assisted development)
   - Investment: £10-15k per workshop
   - Trade-off: faster start, but doesn't solve the platform or MLOps gap directly

3. **Self-serve option:**
   - Use the radar chart to prioritise internally. Start with Governance (it's regulatory) and Tooling (it's foundational). Your team can begin both with the calibration examples as a guide. Happy to be a sounding board without a formal engagement.

No pressure on any of these — the assessment is yours regardless. Happy to jump on a call this week or next to discuss, or just keep it as a reference for your own planning.

Best,
[Facilitator name]
D55

---

## Facilitator Debrief Notes

**What went well:**
- Sarah is a clear champion. She used the session to build alignment with James and Marcus — smart.
- The Four Fears diagnosis landed well during Culture. James visibly nodded when "middle layer bottleneck" was mentioned.
- The governance urgency (FCA + EU AI Act + credit scoring) created genuine concern. This is the emotional hook for the follow-up.

**What to watch:**
- James may be a Stabiliser. He's been VP Eng for 5 years. A new CTO + external consultancy could feel threatening. Handle with care — frame D55 as augmenting his team, not replacing his judgment.
- The "5 years with no retrained model" situation could become a blame conversation. Keep it forward-looking.
- Clearwater (PE) will want metrics fast. The 8-week model with "metrics from week 3" is the right pitch for them.

**Conversion probability:** High (70%+). Budget exists, trigger is real, champion is the decision-maker, PE pressure creates urgency. Follow up within 5 days.
