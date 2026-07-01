# AI-DLC Workshop — Service Offering

## Background

Following discussions with Rhys (2026-07-01), D55 wants to develop an AI-DLC (AI Development Lifecycle) workshop as a service offering. The workshop is a free initial assessment that identifies where a company currently sits with AI adoption, where they want to be, and produces a roadmap to get them there. The output drives further paid engagements.

This builds on earlier work done for the NORTHEDGE ai-forum (see `analysis/NORTHEDGE/ai-forum/`), but is broader in scope — not tied to a single prospect but designed as a repeatable D55 offering.

## Concept

- **Focus:** How to use AI within the development lifecycle — NOT general AI maturity or AI product use cases. The use case IS AI-assisted development.
- **Format:** ~1 hour session with a prospective customer
- **Input:** Structured fact-finding questions across 8 dimensions of AI-enabled engineering readiness
- **Output:** Radar chart showing current maturity vs desired state, plus a roadmap/runbook of what needs to happen to close the gap
- **Commercial model:** Workshop is free; the roadmap output naturally identifies paid service opportunities (consulting, implementation, embedded engineers)

## How It Drives Revenue

The radar chart creates a visual gap analysis. Each gap maps to a D55 service offering. The customer leaves with a clear picture of where they are, where they want to be, and what it'll cost to get there — with D55 positioned as the partner to deliver it.

## Reference Materials

Two example spreadsheets from Rhys sit in `./spreadsheets/`:

1. **Developer Productivity Value Proposition 1.xlsx** — A Value Proposition Canvas template. Structured around:
   - Customer pain points → our value prop → metrics impacted
   - Customer transformation/growth initiatives → our value prop → metrics impacted
   - Customer BAU activities → our value prop → metrics impacted
   - Why us / Why now / Technologies used
   - Elevator pitch

2. **Sagemaker_Unified_Studio_Service_Catalogue (1).xlsx** — A fully worked Service Catalogue entry for "Managed SageMaker Unified Studio and QuickSight". Includes:
   - Service name and description
   - Ideal customer profile
   - Customer challenges addressed (with sourced claims)
   - Qualifying questions (cloud strategy, current stack, team capability, workload mix, scale, cost/FinOps, governance, timeline)
   - Discovery questions (pain/friction, workflow, team, cost visibility, governance, ML/AI maturity, past attempts, success criteria, decision dynamics, risks)
   - Information capture template reference
   - Service deliverables
   - Quantified customer benefits

## What We Want to Build

We'll adapt and extend the patterns from both spreadsheets into an AI-DLC workshop framework:

1. **Assessment dimensions** — The axes of the radar chart. These represent the key areas we assess (e.g. strategy alignment, tooling maturity, team capability, governance, cost visibility, AI/ML adoption depth, etc.)

2. **Workshop questions** — Structured questions per dimension that score the customer on a maturity scale (current state) and capture their ambition (desired state)

3. **Radar chart output** — Visual gap analysis across all dimensions

4. **Roadmap/runbook template** — For each gap identified, what the journey looks like and what D55 services map to it

5. **Service catalogue entries** — Each roadmap item maps back to a D55 service offering (following the pattern in the SUS spreadsheet)

## Service / Engagement Models

The radar chart gap analysis drives a recommendation into one (or more) of these engagement models:

### 1. Discovery & Strategy Session (DSD)
- Defines what needs to be done
- Output asset is a data/AI strategy document — the roadmap, prioritised and costed
- "You buy this off us for £30–50k, this is what you get"
- Pure consultancy

### 2. Prescriptive Guidance & Workshops
- Targeted workshops across gap areas
- Teach them: how to spec, tooling for devs, compliance (correct region, locked down), changes to ceremonies, changes to process
- Customer chooses modules, we deliver
- ~£5–15k per workshop
- Who do we need at these workshops? (TBD per module)

### 3. Embedded Team / Forward Deployed Engineers
- We put a team in
- Forward deployed engineer(s) working alongside their people
- "You get x people for n months"
- Scope defined by gap analysis — what needs to be done, how many people, etc.
- ~£15–25k per engineer/month

### 4. Runbook & Asset Delivery
- Build a runbook that tells them how to get from current → target
- Runbook is the asset — prescriptive guidance with choices at decision points
- Step-by-step, with options ("offer choices")
- Included with Discovery, or standalone from £20k

## Open Questions

- What workshops specifically? (Need to define the catalogue)
- Who needs to attend each workshop? (Personas per module)
- How do we price the embedded model flexibly? (Team size × duration)
- Do we productise the runbook as a standalone thing?
- How does the free assessment → paid engagement handoff work commercially?

## Next Steps

- [x] Define the assessment dimensions (radar chart axes) → `dimensions.md`
- [x] Draft workshop questions per dimension → `dimensions.md`
- [x] Define the maturity scoring model → `dimensions.md`
- [x] Map dimensions to D55 service offerings → `dimensions.md`
- [x] Design the radar chart output format → `workshop.html`
- [x] Create interactive assessment tool → `workshop.html`
- [ ] Iterate on engagement model pricing/packaging with Rhys
- [ ] Define workshop catalogue (modules, content, attendees)
- [ ] Refine runbook template structure
- [ ] Add D55 branding to the HTML tool
- [ ] Consider: PDF export of results?

## Decisions & Notes

| Date | Decision/Note | Who |
|------|--------------|-----|
| 2026-07-01 | Initial concept agreed — free workshop, radar chart output, drives paid services | Rhys + Martin |
| 2026-07-01 | Use SUS service catalogue and value prop canvas as structural examples | Rhys |
| 2026-07-01 | Engagement models: DSD (pure consultancy, ~£50k), Workshops (modular, ~£5-15k each), Embedded team (FDEs, per engineer/month), Runbook asset | Rhys + Martin |
| 2026-07-01 | Rhys feedback: the use case IS AI DLC — not general AI maturity, not AI product use cases. It's specifically "how do we use AI for development?" Dimensions reshaped accordingly. | Rhys |
