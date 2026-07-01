# AI-DLC Workshop Offering — Critique Output

*Cold critique performed against all delivered assets. No prior context assumed.*

---

## Perspective 1: CTO / Technical Director

### Credibility & Depth

**What's strong:**

- The 8 dimensions are well-chosen for the narrow "AI in the development lifecycle" scope. They avoid the trap of becoming a generic AI maturity model. Every dimension maps directly to something an engineering leader would recognise as a real operational concern when rolling out AI-assisted development. The inclusion of "Specification & Design" and "Delivery Process & Ceremonies" as distinct dimensions is a differentiator — most assessments skip the second-order effects of velocity improvement.
- The maturity rubrics are defensible. The 5-level progression for each dimension tells a coherent story of increasing maturity, and the calibration examples give enough texture that a facilitator won't be left guessing. A technically sophisticated CTO could challenge these and find substance behind them.
- The "Four Fears" framework embedded in the Team Adaptation dimension is a genuine differentiator. It gives the facilitator a diagnostic model for human resistance that goes beyond "change management" platitudes.
- The worked example (Heron Financial) is excellent. It demonstrates exactly what a completed session looks like, how to score, how to handle room dynamics, and what the follow-up email looks like. This is the single most useful asset for making the offering repeatable.

**What's missing or weak:**

- The dimensions are heavily weighted toward organisational/process concerns. There's no dedicated dimension for **codebase readiness** — how the existing codebase interacts with AI tooling (monorepo vs polyrepo, documentation quality, test coverage baseline, code complexity, technical debt). A Level 5 organisation with a terrible codebase will still struggle. This is the one dimension a technically sophisticated buyer would expect.
- The scoring is self-reported/facilitator-validated, which is correct for a 1-hour session — but there's no mention of objective validation signals. Even a brief "what would we look for to validate this score?" column per dimension would strengthen credibility.
- The workshop questions mix "must-ask" and "go-deeper" well, but the question count per dimension (5-6 questions) is ambitious for a ~5.5-minute-per-dimension pacing. The facilitator guide addresses this, but the dimensions.md itself doesn't make the time constraint prominent enough at point-of-use.

**Verdict on dimensions:** Solid for the scoped use case. The engineering-focused framing holds up. One missing dimension (codebase readiness) is the most obvious gap a CTO buyer would identify.

---

### Client Engagement

**What's strong:**

- The facilitator guide is genuinely good. The pacing guidance, "don't sell during assessment" instruction, Four Fears quick-reference, and scoring-in-the-room protocol would let a competent senior consultant run this next week. The results narrative template and follow-up email structure remove guesswork from post-session delivery.
- The disqualification criteria are sharp and specific: <20 engineers, no budget, not on AWS, already engaged elsewhere. This prevents the free hour being wasted on bad-fit prospects.
- The intake form is lightweight (5 minutes) and captures the signals that matter for qualification and session prep.
- The gap-to-service mapping feels natural because it flows from the assessment output rather than being shoehorned in. The engagement models section in the HTML tool presents options without hard-selling — the "based on your gaps" framing keeps it consultative.

**What's missing or weak:**

- The 8-week prove-it model is described at positioning level but not at delivery level. There's no scoping framework — what constitutes a "squad" for embedding? What's the minimum viable codebase for the prove phase? What metrics are committed to by week 3? A consultant asked to scope and price this would still need to improvise.
- The handoff from "free assessment done" to "paid engagement starts" isn't formalised. The worked example shows a good follow-up email, but there's no commercial proposal template, no SOW skeleton, no pricing calculator. The facilitator has to write a bespoke proposal every time.
- No "what to do if the session goes badly" guidance. What if the prospect is hostile? What if they score themselves all 5s? What if they refuse to self-score? These are edge cases but they happen.

---

### Technical Direction

**What's strong:**

- The offering is opinionated where it matters: "garbage specs at 5x speed = garbage 5x faster" is a strong, defensible position that gives the conversation direction. The AI-First Delivery Lifecycle framing (more time in design, less in build) is technically sound and currently under-discussed in market.
- The middle-layer bottleneck insight (POs/BAs becoming the constraint when devs go 5x) is genuinely differentiated. Most consultancies haven't articulated this yet because they haven't shipped with AI-native teams at scale.

**What's weak:**

- The offering is platform-agnostic in a way that might undermine D55's AWS credibility. There's no AWS-specific depth anywhere in the dimensions — no mention of CodeWhisperer, Amazon Q, Bedrock, SageMaker, or how AWS-native tooling choices affect the maturity scoring. Given the disqualification criterion is "not on AWS," the assessment should at least reference AWS-specific guidance at higher maturity levels.
- Integration with legacy systems, migration patterns, and networking/security architecture are not addressed. The governance dimension touches security but from a policy/DLP angle, not a technical implementation angle. For a prospect with a complex AWS estate, the assessment could feel disconnected from their infrastructure reality.

---

### Overall Assessment

**Readiness: 4/5**

This is usable with a real prospect next week, with minor facilitator briefing. The combination of dimensions.md + facilitator-guide.md + worked-example.md + workshop.html creates a complete delivery package. The quality of thinking is high, the scoping is tight, and the worked example removes most ambiguity about "what does good look like."

**Single most important remaining gap:** The 8-week prove-it model lacks delivery-level specification — a senior consultant can run the assessment but would struggle to scope and price the follow-up engagement without improvising. A one-page "8-week engagement scoping template" (what we assess, what we prove, what we translate, minimum commitments from the customer, pricing model) would close this gap.

---

## Perspective 2: Marketing Director

### Positioning & Messaging

**What's strong:**

- The positioning.md file is a genuinely useful marketing source document. The one-liners are strong — "One hour. Eight dimensions. A clear AI roadmap — free" is ready to use. The four differentiators (Four Fears, AI-First Delivery Lifecycle, Middle-Layer Bottleneck, 8-Week Prove-It) are distinct and each yields a content angle.
- The "garbage specs at 5x speed" hook is immediately compelling. It's counterintuitive, it's quotable, and it positions D55 as having seen the future (and the problems) before their prospects have.
- The economics hook (£200/seat for 5x productivity) is simple enough for a LinkedIn post and strong enough for a CFO conversation.

**What's missing or weak:**

- The external name hasn't been decided. "AI-DLC" is an internal codename that communicates nothing to a buyer. The name candidates in positioning.md are reasonable but no decision is made. Marketing can't launch without a name. **Recommendation:** "AI Readiness Radar" — it ties to the artifact (radar chart), is memorable, and immediately communicates the output format. The slight playfulness is a feature for content marketing, and the word "Readiness" avoids the "maturity" trap.
- The differentiation from generic "AI maturity assessments" is well-articulated internally but not distilled into a single, external-facing positioning statement. The four differentiators need a unifying message: something like "We don't assess whether you've adopted AI. We diagnose what breaks when you do — and fix it."
- No visual assets exist. The radar chart concept is visually compelling as a hero image, but there's no sample radar chart image, no branded mockup, no "before" example to use in marketing materials. The HTML tool generates one dynamically, but marketing needs a static, polished example.

---

### Content & Collateral

**What's strong:**

- There's easily enough material here for: a landing page, a 1-pager, a LinkedIn carousel series, a webinar, and a 6-8 week content calendar. The positioning.md even provides the content calendar structure with specific topics, hooks, and formats.
- The Four Fears framework is a natural carousel/infographic. Four slides, four personality types, four reframes. That's social content that writes itself.
- The worked example would make an excellent anonymised case study or webinar walkthrough.

**What's missing or weak:**

- No real case studies or social proof. Everything is theoretical or based on a fictional composite. The "5x productivity" claim cites "D55 delivery experience" but names no customers, no dates, no specifics. A technically sophisticated CTO will notice. This is noted as a limitation but doesn't reduce readiness for marketing launch — you can launch with the framework and backfill proof points from early sessions.
- No designed assets. No PDF template, no slide deck, no branded radar chart, no landing page mockup. The content is all in markdown and raw HTML. Marketing needs a designer before they can launch. (Again — this is external action, noted but not scored.)
- The conversion path is clear (content → landing page → intake form → session → follow-up → proposal) but there's no landing page copy written, no intake form hosted anywhere, and no CRM integration specified.

---

### Target Audience & Funnel

**What's strong:**

- The ICP is specific and targetable: CTO/VP Eng at mid-market (250-2000 employees), 20+ engineers, on AWS, with some AI experimentation. You could build a LinkedIn Ads audience or ABM list from this today.
- Trigger events are well-defined (new CTO, PE pressure, competitor adoption, EU AI Act, cost pressure). These map to intent signals that sales/marketing can monitor.
- The job titles for targeting are clear: CTO, VP Engineering, Head of Data. Secondary audiences (PE ops, CFO, HR) are identified with their respective angles.

**What's missing or weak:**

- No proof that this ICP exists in sufficient volume for D55's pipeline needs. How many companies in the UK fit this profile? Is this a 200-company universe or a 2000-company universe? That determines whether this is an ABM play or a content marketing play.
- The "free assessment" framing is correctly identified as a potential risk — it could cheapen the offering. The positioning.md doesn't resolve this. **Recommendation:** Frame it as "complimentary" not "free," and emphasise the output value ("you'll leave with a £X deliverable"). The radar chart + written narrative is easily worth £5-10k if it were billed. Make that implicit.

---

### Gaps

**What's needed from delivery team:**

1. A decided external name (one of the candidates in positioning.md)
2. A static, polished radar chart example image for marketing use
3. One real anonymised engagement to reference (even "a mid-market lender" from the first session)
4. Confirmation of the 5x productivity claim with any supporting data (even internal D55 metrics)

**Content calendar:** Yes, it's hiding in here. The positioning.md provides 8 weeks of topics. Combined with the depth in dimensions.md, you could run 3-6 months of content before repeating.

---

### Overall Assessment

**Readiness: 3/5**

The strategic positioning, messaging framework, ICP, content calendar, and conversion path are all in place. What's missing is execution-layer marketing assets (landing page, designed collateral, hosted intake form) and a decided external name. These are all producible from what's here — the source material is rich enough. The gap is between "internal strategy doc" and "live campaign."

**Single most important remaining gap:** No decided external name. Marketing cannot write a landing page headline, register a URL, create social content, or brief a designer until the offering has a name. Pick one. Ship.

---

## Verdict

| Perspective | Score | Threshold | Result |
|-------------|-------|-----------|--------|
| CTO | 4/5 | ≥ 4/5 | ✅ PASS |
| Marketing | 3/5 | ≥ 3/5 | ✅ PASS |

### **PASS**

Both scores meet their respective thresholds. The offering is ready to use with a real prospect (CTO perspective) and has sufficient strategic material to begin marketing execution (Marketing perspective).

---

## Top 3 Improvements (In Priority Order)

These would elevate both scores:

1. **Decide the external name.** Pick "AI Readiness Radar" or equivalent. This unblocks all marketing execution and gives the offering an identity beyond internal codenames.

2. **Create an 8-week prove-it scoping template.** One page: what's assessed, what's proved, what's translated, minimum customer commitments, pricing bands. This closes the CTO's biggest gap (ability to scope and price the follow-up) and gives marketing a concrete deliverable to reference.

3. **Generate a polished static radar chart example.** Screenshot the HTML tool with the Heron Financial scores populated. This becomes the hero image for the landing page, the visual hook in LinkedIn content, and the "here's what you'll get" proof point in the conversion funnel.
