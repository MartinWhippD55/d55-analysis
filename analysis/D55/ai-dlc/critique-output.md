# AI-DLC Workshop Offering — Cold Critique

*Evaluated: 2026-07-02*
*Assets reviewed: context.md, dimensions.md, workshop.html, generate_spreadsheets.py, facilitator-guide.md, intake-form.md, critique-prompt.md*

---

## Perspective 1: CTO / Technical Director

### Credibility & Depth

**What's strong:**

- The 8 dimensions cover the right ground. Strategy, Data, Tooling, Team, Governance, Delivery, Cost, Culture — this is a complete picture of AI organisational readiness. I'd struggle to point to a dimension that's missing.
- The maturity rubrics are genuinely well-calibrated. Each level is distinct and defensible. The calibration examples per dimension are a smart addition — they give the facilitator anchor points and make scoring conversations concrete rather than abstract.
- The "AI-First Delivery Lifecycle" framing is the most original thing here. The insight that when implementation speed goes 5x, clarity of intent becomes the bottleneck — that's not something you'll find in generic maturity assessments. It gives D55 a distinctive technical point of view.
- The Four Fears framework in Culture & Adoption is differentiated. Most consultancies treat culture as a checkbox. This gives the facilitator a diagnostic tool with actionable reframes.
- Scoring guidance ("when between levels, score the lower", "disagreement is gold", "let them self-score first") shows genuine facilitation maturity.

**What's missing or thin:**

- The questions are well-prioritised (★ must-ask vs go-deeper) but there are still 5-8 questions per dimension. In a ~5.5 minute window per dimension, a facilitator might panic about coverage. The facilitator guide helps here, but the dimensions.md could be tighter about "you only need 2-3 per dimension in practice."
- No worked example of a completed assessment. A single fictional walk-through (e.g., "Here's what it looked like when we ran this with a 500-person fintech") would massively accelerate facilitator confidence. This is a gap that requires external action (running a real session or fabricating a credible example), so noting it rather than penalising.
- The gap-to-service mapping is comprehensive but lacks specificity on what each service actually delivers. "AI Governance Framework" as a service tag is fine for a radar chart output, but the facilitator needs to know what that means in practice if a prospect asks "what does that look like?" The service catalogue spreadsheet helps here, but it's in a separate asset and not all services are fleshed out.

**Client Engagement:**

- **Would I hand this to a senior consultant and say "run it next week"?** Almost. The facilitator guide is excellent — the timing breakdown, facilitation tips, scoring mechanics, and post-session template are all there. What's missing is a dry-run script or a "your first 3 sessions" confidence-building plan. But the materials themselves are ready.
- **Does the gap-to-service mapping feel forced?** No — it's the natural output of a gap analysis. The phrasing ("recommended services") rather than ("what we'll sell you") is correct. The facilitator guide's instruction to not sell during the assessment and save it for the close is critical and well-placed.
- **The 8-week prove-it model** — this is well-structured (Assess/Prove/Translate). It's specific enough to scope: you know the phases, the duration, the activities, the outputs. A prospect could say "yes" to this. The pricing (£15-25k/engineer/month) gives enough range. This is credible.
- **Qualifying/disqualification** — the intake form + disqualification criteria in the facilitator guide are solid. "No exec sponsor AND no budget", "fewer than 20 engineers", "not on AWS" — these are clear and will save time. Good.

**Technical Direction:**

- This is opinionated where it matters. The AI-First Delivery Lifecycle is a point of view, not a generic assessment. The economics section (£150-200/seat/month for 5x) gives the facilitator ammunition for a specific conversation.
- AWS depth is appropriately present but not overwhelming. The service catalogue references SageMaker, Bedrock, Glue/Athena, CDK — that's enough to establish credibility without alienating multi-cloud prospects who might consider AWS.
- **Blind spots:** Security gets good coverage within Governance (prompt injection, data leakage, region lockdown). Networking is not explicitly called out but is arguably covered under "Platform." Legacy integration is mentioned in Data Readiness's go-deeper questions and in the service mapping. No major technical blind spot.

**What would make me proud to put D55's name on this:**

- D55 branding on the HTML tool (noted as TODO in context.md — visual polish only)
- One page of opinionated technical positions: "We believe X about data platforms, Y about MLOps, Z about GenAI in production." Right now the assessment is diagnostic; it doesn't yet show what D55's *answer* is. The service catalogue gets close but reads as a product list, not a philosophy.

### CTO Verdict

The intellectual framework is strong. The dimensions are credible, the questions are sharp, the facilitation guidance is practical, and the engagement models are specific enough to sell. A technically sophisticated buyer would respect this.

---

## Perspective 2: Marketing Director

### Positioning & Messaging

**What's strong:**

- The elevator pitch in the value proposition canvas is actually usable: "Book an hour with us. We'll show you exactly where you are with AI, where you want to be, and what it takes to get there — for free." That's a clear, compelling CTA.
- The radar chart concept is visually strong. A gap analysis visualised as a spider chart is immediately understandable — even to non-technical buyers. This is the hero image for marketing.
- The "free assessment" commercial hook is correct for this market. CTOs/CDOs will give an hour for a structured output. It doesn't cheapen the offering — it de-risks it.

**What's missing or weak:**

- **"AI-DLC" as a name is terrible for marketing.** It's an internal acronym. A non-technical buyer (or even a CTO) won't know what "DLC" means (Development Lifecycle? Downloadable Content? It's ambiguous). This needs a customer-facing name. Something like "AI Readiness Assessment" or "AI Maturity Diagnostic" — plain, searchable, self-explanatory. "AI-DLC" can remain as an internal project code but should never appear in customer-facing materials.
- **Differentiation from other AI maturity assessments:** The Four Fears framework and the AI-First Delivery Lifecycle are genuinely differentiating, but they're buried deep in the dimensions and facilitator guide. Marketing needs these surfaced as headline differentiators: "Not another maturity assessment — this one diagnoses why your people resist AI and what to do about it."
- **The one-liner isn't quite there.** The elevator pitch is good but long. A true one-liner would be: "Find out where you stand with AI — and what it'll take to close the gap. One hour. Free." Or: "The AI assessment that shows you the gap, the roadmap, and the cost. In one hour."

**Content & Collateral:**

- **Can I build a landing page from this?** Yes. The value proposition canvas gives me: headline, subhead, pain points, benefits, CTA. The radar chart gives me a hero visual. The engagement models give me a "what happens next" section.
- **LinkedIn carousel?** Yes — the 8 dimensions are a natural 8-slide carousel with one slide per dimension showing the 1→5 scale.
- **Email nurture?** Yes — each dimension could be a standalone email: "Is your data ready for AI? Here's how to tell."
- **Webinar outline?** Yes — "The 8 things holding your AI strategy back" practically writes itself.
- **What's missing for all of the above:** designed visual assets (not a marketing-materials gap in the document, just a production step), and a customer-facing name.

**Proof Points & Claims:**

- The "£150-200/seat/month for 5x productivity" claim is specific and powerful but unsourced. For marketing, I need either: a) a named case study, b) industry research citation, or c) "based on our delivery experience across N engagements." This requires external action (gathering evidence), so noting rather than penalising.
- "Output equivalent to 200+ engineers from a 50-person team" — this is a bold claim. It works in a sales conversation with caveats; it's risky in written marketing without evidence. Not a document fix — needs real data.

**Target Audience & Funnel:**

- **ICP is defined** (mid-market, 250-2000 employees, some AI experimentation, AWS or open to it). I can build a LinkedIn audience from this. I can build an ABM list from this.
- **Job titles are clear** from the "who we need in the room" section: CTO, VP Engineering, Head of Data, CDO. Plus the triggers (board pressure, competitor movement, EU AI Act, PE expectation) give me targeting hooks.
- **Conversion path is obvious:** Content → Book Assessment → Attend → Receive Write-up → Buy Services. The intake form is the booking gate. Clean funnel.
- **Social proof / case studies:** Zero. This is entirely theoretical as presented. Not fixable in the documents — requires running real sessions and collecting outcomes. Noted but not penalised.

**Content Calendar Potential:**

Tons of thought leadership hiding here:
- "The Four Fears of AI Adoption (and how to address each one)"
- "When developers go 5x faster, who becomes the bottleneck?"
- "Garbage specs at 5x speed = garbage 5x faster: the case for design-up-front in the AI era"
- "The EU AI Act is coming — here's what your AI governance gap looks like"
- "What does Level 5 data readiness actually look like?"
- "The 8-week prove-it model: how we embed, demonstrate, then step back"

That's 6+ months of content from what's already written.

**What would I need to launch:**

1. A customer-facing name (not "AI-DLC")
2. A designed radar chart visual for marketing materials (a screenshot of the HTML tool, or a styled mock-up)
3. One case study or "early results" example (requires running the first real session)
4. A landing page built from the value proposition canvas content

Items 1 and 2 are achievable within the documents/assets. Items 3 and 4 require external action.

### Marketing Director Verdict

There's a surprisingly complete marketing toolkit buried in what looks like an internal technical document. The pain points, benefits, ICP, elevator pitch, and content angles are all here. The main document-level gap is the naming problem ("AI-DLC" won't work externally) and surfacing the differentiators (Four Fears, AI-First Delivery Lifecycle) into headline-level positioning rather than leaving them buried in facilitation details.

---

## Scores & Verdict

### CTO Readiness: 4/5

**Single most important remaining gap:** A worked example (completed assessment for a fictional but credible prospect) that a facilitator can study before their first session. This accelerates confidence from "I've read the guide" to "I can see what good looks like."

*Note: The missing D55 branding on the HTML tool, real case studies, and opinionated technical positions doc would push this to 5/5 but require design work or external action, not document changes.*

### Marketing Readiness: 3/5

**Single most important remaining gap:** The customer-facing name. "AI-DLC" cannot go on a landing page, a LinkedIn post, or a sales deck. Everything else (messaging, ICP, content angles, funnel design) flows from having a name that communicates value to a buyer who doesn't know what a "Development Lifecycle" is. This is fixable in 10 minutes with a decision.

*Note: The lack of case studies, designed visual assets, and a live landing page would move this higher but require external action beyond document work.*

### Verdict: PASS

Both scores meet the threshold (CTO ≥ 4/5, Marketing ≥ 3/5).

**Top 3 improvements (in priority order for document-level polish):**

1. **Rename for external use.** Drop "AI-DLC" from anything customer-facing. Adopt a plain-language name (e.g., "AI Readiness Assessment", "AI Maturity Diagnostic", or similar). Keep AI-DLC as the internal project code.

2. **Add a worked example.** Create one fictional-but-realistic completed assessment (a "Level 2-3 average" mid-market company) showing the radar chart output, the gap analysis narrative, and the follow-up email. Include it as an appendix to the facilitator guide.

3. **Surface differentiators into a one-page positioning doc.** Pull the Four Fears framework, the AI-First Delivery Lifecycle thesis ("clarity of intent is the multiplier on the multiplier"), and the middle-layer bottleneck insight into a standalone page that marketing can use as source material for all collateral. These are the things that make this NOT just another maturity assessment — but right now you have to read 3000+ words of facilitation guidance to find them.
