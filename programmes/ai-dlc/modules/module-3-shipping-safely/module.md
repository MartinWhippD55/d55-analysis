---
module_id: 3
title: Shipping Safely
dimensions_covered:
- Testing & Quality Assurance
- Governance, Security & Compliance
trigger:
  recommend_when_current_at_or_below: 3
  include_when_gap_at_or_above: 2
  prioritise_when_gap_at_or_above: 2
  critical_dimensions:
  - Governance, Security & Compliance
  critical_when_current_at_or_below: 2
audience:
- Engineering leads
- QA / test leads
- Security
- Compliance / risk
duration: 1 day
format: Facilitated working session + policy drafting
manual_section: 3. Shipping Safely
sets_up_embed: true
d55_ip:
- Evidence-based confidence in AI-generated code
- Governance-enables-speed framing
---

# Module 3 — Shipping Safely

## Objective
Let the team go fast without blowing up. Adapt testing for AI-generated code and put governance, security and compliance controls in place so leadership can authorise scaling with confidence.

## Why it matters (client outcome)
The CTO's real fear isn't speed — it's making a mess at speed: insecure code, data leaking into prompts, no audit trail, EU AI Act exposure. "You can now go fast safely" is what lets leadership say yes to scaling. Governance here is an enabler, not a blocker.

## Who's in the room
Eng leads and QA/test leads (testing), security and compliance/risk (governance). Where the client is regulated (finance, health), compliance attendance is essential.

## Inputs (from assessment)
- Current vs target on Testing & Quality and Governance, Security & Compliance
- Intake context: regulated industry? existing DLP / policy? enterprise AI agreements? region?
- EU AI Act relevance (credit, hiring, pricing use cases)

## Session flow
1. **Trust, but verify** — how do you validate AI-generated code today? Same bar as human code?
2. **Testing adapted for AI code** — tests generated from specs, coverage gates, human-in-the-loop at integration points, regression (e.g. Playwright).
3. **The governance reality check** — what would you show a regulator? Where's sensitive data going?
4. **Controls that don't slow you down** — approved tools/endpoints, enterprise agreements (data not used for training), correct region, DLP, code provenance / audit trail.
5. **EU AI Act** — classify their AI usage under risk categories where applicable.
6. **Draft the policy** — leave with a real AI usage policy started, not a promise to write one.

## Deliverables (what they leave with)
- An AI usage policy (drafted in the room)
- A test strategy for AI-generated code (gates, coverage, review bar)
- A governance checklist: approved tools, region, DLP, provenance, audit
- EU AI Act classification (where applicable)

## Writes to Client Operating Manual
Section: 3. Shipping Safely
Section 3 — Shipping Safely: the AI usage policy, the test strategy for AI code, the governance/compliance controls, and the audit approach.

## How it sets up the embed
The embed squad ships production code — so the guardrails defined here are what let that shipped work actually go live. Without them, the embed proves speed but can't prove safe speed, and leadership won't authorise rollout.
