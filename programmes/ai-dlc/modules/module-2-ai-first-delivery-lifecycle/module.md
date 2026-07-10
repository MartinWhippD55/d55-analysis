---
module_id: 2
title: The AI-First Delivery Lifecycle
dimensions_covered:
- Developer Tooling & Adoption
- Specification & Design Process
- Delivery Process & Ceremonies
trigger:
  recommend_when_current_at_or_below: 3
  include_when_gap_at_or_above: 2
  prioritise_when_gap_at_or_above: 2
audience:
- Engineering leads
- Developers
- Product Owners / BAs
- Delivery / Scrum leads
duration: 1–2 days (can split into tooling / specs / process)
format: Hands-on working sessions
manual_section: 2. How We Build
sets_up_embed: true
d55_ip:
- AI-First Delivery Lifecycle ("garbage specs at 5x = garbage 5x faster")
- Middle-Layer Bottleneck
---

# Module 2 — The AI-First Delivery Lifecycle

## Objective
Reshape how the team actually works day to day so AI speed turns into real throughput instead of faster mess. Cover the three linked shifts: developers using AI tools effectively, specs written up-front for both humans and AI, and delivery ceremonies adapted to the new velocity.

## Why it matters (client outcome)
This is the core "how we work now" module. Tools alone don't deliver — the process around them has to change. When implementation goes 5x, clarity of intent becomes the multiplier and the old sprint cadence starts to crack. This module fixes all three at once because they only work together.

## Who's in the room
Developers and eng leads (tooling + specs), Product Owners and BAs (specs + the middle-layer shift), and delivery/scrum leads (ceremonies). Cross-role by design — the point is they adapt together.

## Inputs (from assessment)
- Current vs target on Developer Tooling, Specification & Design, Delivery Process
- Intake context: current toolset, sprint model, where the bottleneck sits now
- Any shared configs / MCP setup already in place

## Session flow

The module runs across three tracks that can be delivered as one intensive day or,
preferably, two days (Track A in the morning of day 1; Tracks B and C across the
rest). Each role attends the tracks relevant to them — see the attendance guide
below — so the whole team isn't pulled off the floor for two full days.

1. **The core insight** *(all)* — "garbage specs at 5x speed = garbage 5x faster." Where does clarity of intent break today?

**Track A — Tooling** *(developers, eng leads)*
2. **Tooling that works** — move from "licences provisioned" to "embedded in daily flow": shared configs, skills, MCP connections to their systems.

**Track B — Specs** *(developers, eng leads, POs, BAs)*
3. **Specs as first-class artefacts** — design-up-front, contracts and integration points defined before build, specs written to be consumed by AI.
4. **The middle-layer bottleneck** — surface it: when devs go faster, POs/BAs become the constraint. Redefine those roles as spec owners.

**Track C — Ceremonies** *(delivery / scrum leads, eng leads)*
5. **Adapting ceremonies** — sprint cadence, PR review (AI-assisted first pass, different bar for AI code), continuous flow vs batch.

6. **Put it together** *(all)* — walk one real piece of work through the adapted lifecycle end to end.

**Attendance guide (so it's feasible mid-delivery):**

| Role | Track A (Tooling) | Track B (Specs) | Track C (Ceremonies) |
|------|:---:|:---:|:---:|
| Developers / eng leads | ● | ● | ○ |
| Product Owners / BAs | — | ● | ○ |
| Delivery / scrum leads | — | ○ | ● |

*(● required · ○ optional · — not needed. Steps 1 and 6 are whole-group.)*

## Deliverables (what they leave with)
- A standard AI tooling configuration — the minimum viable config: IDE + AI assistant, a shared skills/config set, MCP connections to their systems (Jira/GitHub/etc.), and agreed PR-review settings for AI-generated code
- A spec template written for human + AI consumption
- A redesigned delivery cadence and PR-review approach
- A named plan for the middle-layer role shift

## Writes to Client Operating Manual
Section: 2. How We Build
Section 2 — How We Build: tooling standards, the spec template, the adapted delivery process and ceremonies, and the coordination-role definitions.

## How it sets up the embed
The embed squad works inside this adapted lifecycle from day one — using the tooling standard, the spec template, and the new cadence. This module makes the embed productive immediately instead of the team relearning process while D55 is on the clock.
