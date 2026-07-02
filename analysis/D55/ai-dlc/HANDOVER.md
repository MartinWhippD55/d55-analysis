# AI-DLC — Session Handover & Next Steps

*Last updated: 2026-07-02*

---

## What This Is

AI-DLC (AI Development Lifecycle) is a D55 service offering designed to help mid-market engineering organisations adopt AI-assisted development effectively. The core proposition: "Your developers have AI tools — but are they actually faster? Has the process adapted? Can you prove it?"

This is NOT a general AI maturity assessment. It's specifically about **how to use AI in the development lifecycle** — tooling, specs, process, testing, governance, team adaptation, and ROI measurement.

---

## What's Been Built

### Assets (all in `analysis/D55/ai-dlc/`)

| File | Purpose |
|------|---------|
| `workshop.html` | Interactive assessment tool. 8 dimensions, score current vs target, renders radar chart + gap analysis + engagement recommendations. D55-branded, self-contained (logo embedded as base64). Includes validation (must select scores before advancing) and fade animations. |
| `dimensions.md` | The 8 assessment dimensions with maturity rubrics (1-5), calibration examples, must-ask vs go-deeper question tiering, and scoring guidance for facilitators. |
| `facilitator-guide.md` | How to run the workshop: timing, pacing, facilitation tips, scoring mechanics, Four Fears quick-reference, results narrative template, follow-up email template, disqualification criteria. |
| `intake-form.md` | Pre-session questionnaire (11 questions, ~5 min for prospect). Sent 48 hours before to qualify and prep. |
| `worked-example.md` | Fictional but realistic completed assessment ("Heron Financial" — PE-backed lender, 80 engineers). Full walk-through: intake, scoring rationale, Four Fears diagnosis, results reaction, follow-up email, debrief notes. |
| `positioning.md` | Marketing source material: one-liner candidates, differentiators (Four Fears, AI-First Delivery Lifecycle, Middle-Layer Bottleneck, 8-Week Prove-It), ICP, content calendar, conversion path. External name not yet decided. |
| `context.md` | Project context, decisions log, engagement models, open questions. |
| `generate_spreadsheets.py` | Generates the two .xlsx files below. Run with `python generate_spreadsheets.py`. |
| `spreadsheets/AI-DLC Value Proposition Canvas.xlsx` | Pain points → value props → metrics. Engineering-focused. |
| `spreadsheets/AI-DLC Service Catalogue.xlsx` | Full service entry: ICP, qualifying questions, dimensions, deliverables, pricing, benefits, attendees, key frameworks. |
| `critique-prompt.md` | Structured prompt for critiquing assets from CTO and Marketing Director perspectives. |
| `critique-output.md` | Latest critique result (PASS: CTO 4/5, Marketing 3/5). |
| `iterate-prompt.md` | Documents the self-improving critique loop process. |
| `assets/` | D55 brand assets (logos, backgrounds, PowerPoint template). |

### The 8 Dimensions (current)

1. **Leadership & Mandate** — executive sponsorship for AI-assisted dev
2. **Developer Tooling & Adoption** — are devs actually using AI tools effectively
3. **Specification & Design** — has the org adapted to design-up-front when build is 5x faster
4. **Delivery Process & Ceremonies** — have sprints/standups/reviews adapted
5. **Testing & Quality** — is testing adapted for AI-generated code
6. **Governance, Security & Compliance** — policy, DLP, audit trail, EU AI Act
7. **Team Adaptation & Skills** — resistance patterns, middle-layer bottleneck, upskilling
8. **Metrics & ROI** — can you prove it's working with numbers

### Key Frameworks (D55 IP)

- **Four Fears Framework** — diagnostic for AI adoption resistance (Controller, Driver, Stabiliser, Influencer). Each has a specific reframe.
- **AI-First Delivery Lifecycle** — "garbage specs at 5x speed = garbage 5x faster." Clarity of intent is the performance multiplier.
- **Middle-Layer Bottleneck** — when devs go 3-5x faster, POs/BAs/PMs become the constraint.
- **8-Week Prove-It Model** — Assess (weeks 1-2), Prove (weeks 3-6), Translate (weeks 7-8).
- **The Economics** — ~£200/seat/month for 3-5x productivity. The real cost is delay.

### Quality Status

- Passed CTO critique at 4/5 (ready to use with a real prospect)
- Passed Marketing critique at 3/5 (rich IP, needs external name and designed assets to launch)
- Workshop HTML tested: validation works, radar chart renders correctly, animations smooth

---

## Latest Feedback from Rhys (2026-07-02)

**The service needs to go up a level.**

The assessment workshop we've built is Phase 1 of a larger AI-DLC programme — not the whole offering. The hierarchy should be:

```
AI-DLC (the full service/programme)
├── Phase 1: Assessment Workshop (what we've built — the free diagnostic)
├── Phase 2: Workshop Modules (one per gap dimension — teach them)
├── Phase 3: Embedded Prove-It (8-week model — do it with them)
├── Phase 4: Rollout & Scale (expand across the org)
└── Output: Runbook (the asset they keep — their operating manual for AI-native engineering)
```

The free assessment populates the runbook. The workshops and embedded phases deliver against it. The customer keeps the runbook as the operating manual.

---

## Next Steps (Priority Order)

### 1. Define the full AI-DLC programme structure
- What are the phases?
- What does each phase contain?
- How do they sequence?
- What's the commercial model at the programme level (vs à la carte)?

### 2. Design the workshop modules (Phase 2)
Each dimension gap likely maps to a deliverable workshop:
- AI-First Delivery Lifecycle Workshop (Specs & Design)
- Developer Tooling Setup Workshop
- Process & Ceremonies Redesign Workshop
- Testing Strategy for AI-Generated Code Workshop
- Governance & DLP Workshop
- Four Fears / Team Adaptation Workshop
- Metrics & ROI Workshop
- Leadership & Investment Case Workshop

For each: define objectives, attendees, duration, deliverables, and how it connects to the runbook.

### 3. Define the runbook structure
The runbook is the programme spine. What does it look like?
- Does the assessment auto-populate a runbook template?
- What sections does it have?
- What's the format (document? interactive tool? Notion-style?)
- What does "the asset they keep" actually look like?

### 4. Decide the external name
"AI-DLC" works internally but doesn't communicate value externally. Candidates in `positioning.md`. Needs a Rhys decision.

### 5. Programme-level pricing
Move from à la carte to programme pricing:
- What does the whole programme cost?
- Are there tiers? (Assessment only → Assessment + Workshops → Full programme with embedded)
- How does the "free assessment" fit into a programme sale?

### 6. Remaining polish items (from last critique)
- 8-week prove-it scoping template (one-pager for consultants to scope follow-on)
- Static radar chart screenshot for marketing hero image
- Update worked example to reference the programme framing
- Run first real assessment to generate a proof point

---

## Decisions Still Needed (Rhys)

| Decision | Context |
|----------|---------|
| External name | "AI-DLC" doesn't work customer-facing. Candidates in positioning.md. |
| Programme pricing model | À la carte vs tiered packages vs full programme price |
| Target industries | ICP is "mid-market, 20-200 devs, AWS" — do we narrow to specific sectors? |
| Who's the face? | Who presents this externally (LinkedIn, events, workshops)? |
| First pilot prospect | Who do we run the assessment with first to get a real proof point? |

---

## How to Continue This Work

1. Read `context.md` for full background and decision log
2. Read this file for current state and next steps
3. The critique loop (`iterate-prompt.md` + `critique-prompt.md`) can be used to validate changes — invoke a sub-agent with the critique prompt, fix issues, re-run until PASS
4. All assets are in git on `main` branch at `github.com/MartinWhippD55/d55-analysis`
5. Workshop HTML can be tested by running `python -m http.server 8901` from the `analysis/D55/ai-dlc` directory
6. Spreadsheets can be regenerated with `python generate_spreadsheets.py`
