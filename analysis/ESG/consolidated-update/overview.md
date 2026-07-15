# Current State Overview — for Jonathan / Lynsey (ESG)

*Prepared ahead of the 9am Thursday meeting. Pitched at product/outcome level, not technical detail. Purpose: give Jonathan a clear, evidence-backed picture and a constructive line to take.*

---

## TL;DR (the one-minute version)

- D55 delivered four major workstreams — Financial Management, Instalment Plans, Debt Config, Debt Management — **on time, to very tight deadlines**, running our own squads and process.
- The next tranche (**16 initiatives**) is now being run under a **new operating model**: D55 developers embedded into an ESG squad, ESG leads owning design and decisions, D55's design-first process removed.
- Under that model, **pace has dropped materially**. Current gut-feel estimates point to a **~end-September** finish against an **end-July** target — for a body of work **smaller than Debt Management**, which we delivered in ~2 months with 9 developers.
- The single variable that changed is **the process**, not the people. The fastest route back to pace is to **reinstate design-first, then AI-accelerate from it** — the method that produced our previous results.
- The strategic opportunity: ESG want to learn how we break work down for AI. We're **in the process of productising exactly that**. Route it into a value-adding engagement rather than giving it away piecemeal.

---

## 1. Current State

### Delivered (D55-led, design-first process)
| Workstream | Outcome |
|---|---|
| Financial Management | Delivered on time |
| Instalment Plans | Delivered on time |
| Debt Config | Delivered on time |
| Debt Management | Delivered ~2 months, 9 developers, larger scope than the current tranche |

Delivery quality held up under scrutiny: on the Debt/IP defect review, **127 defects, 97% closed, ~60% self-raised by D55** before ESG testing — evidence of a team reviewing and testing its own work.

### In flight (new ESG-integrated model)
- **16 initiatives** in scope. Currently at **business-requirements level only** — overlapping, not scoped into technical design or implementation.
- **Refinement only just completed** — half of July already gone.
- Estimate basis has changed: **gut-feel / finger-in-the-air**, no technical design underpinning it.

### What changed operationally
- D55 developers **embedded into an ESG squad**; ESG leads own the big-ticket initiatives and increasingly own the process.
- **D55's design-first process removed** — no upfront technical design, no user-story/subtask decomposition, no Monte Carlo forecast.
- **Autonomy removed** — design and delivery decisions now sit with ESG leads.
- Each developer **owns their own design** for their assigned initiative → weak coordination across overlapping initiatives, integration rework late.

---

## 2. Internal Team

**Team running the current 16 initiatives: 5 developers (3 D55 + 2 ESG).**

- **2 ESG developers** own the main big-ticket initiatives and are taking on more of the overall process.
- **3 D55 developers** actively embedded, with reduced scope to make meaningful design/architecture impact.
- **3 further D55 developers** waiting on workstreams that start end of next week.
- **2 further D55 developers** working on less involved areas of the codebase.

Observation to convey (calmly, not as a grievance): the current setup **under-uses D55's strengths**. Our value was never interchangeable coding capacity — it was the delivery *system* (design-first + AI acceleration) that produced the earlier results. Embedded as individual contributors under someone else's process, that advantage is switched off.

---

## 3. Deadlines: Expected vs Realistic

| | |
|---|---|
| **Expected (as indicated by ESG)** | End of July |
| **Realistic (current trajectory)** | ~End of September |

### How the realistic estimate builds up
- **~178 dev-days** estimated across the 16 initiatives (gut-feel, no design).
- Team of 5 → **~35–36 dev-days ≈ ~7 dev-weeks of pure build**, *if* perfectly parallel with zero rework.
- That excludes: **testing, defect-fixing, and merging feature-branch PRs into main** — a non-trivial tail on every prior workstream.
- With refinement only just finished mid-July and no technical design to parallelise cleanly, the honest landing point is **end of September**.

### The contrast that makes the point (use this)
> Debt Management was **larger**, and we delivered it in **~2 months with 9 developers** under our design-first process.
> This tranche is **smaller**, yet forecast at **~2+ months with 5 developers** (effectively 3 D55) under the new process.
> **Same-or-worse duration for less scope. The only variable that changed is the process.**

### Estimate-confidence caveat (important, honest)
Previously we forecast dates from a technical design → user stories → subtasks → **Monte Carlo simulation**. Those forecasts were defensible. The current numbers are **gut-feel without a design**, so their confidence interval is wide. We should be clear that we can't stand behind a precise date under an estimation approach that isn't ours.

---

## 4. Key Challenges

All of these trace back to **one root cause: the switch away from design-first.**

1. **No upfront technical design.** This is the big one. It removes the artefact that (a) makes AI acceleration possible and (b) lets us forecast reliably.
2. **Sequential refinement dependency.** Work now waits on individual refinement sessions rather than being decomposed once, upfront.
3. **Gut-feel estimates + side discussions on ambiguity.** Ambiguity is resolved ad hoc mid-flight instead of being designed out early.
4. **Fragmented design ownership.** Each dev owning their own initiative design → communication overhead and **rework where overlapping initiatives must integrate**.
5. **No comparable metrics.** Because we're not using our decomposition, we can't produce the like-for-like throughput data we normally would — which itself obscures the pace drop.
6. **Autonomy removed.** Decision latency: D55 can't move at its own pace when every meaningful call routes through ESG leads.

**The AI angle that matters most** (and it's D55's own published insight): when developers go 5x with AI, the bottleneck moves from *building* to *specifying*. *"No design specs at 5x speed = failure."* The current model has increased AI pressure on delivery while **removing the specification/design step that makes AI pay off** — so the constraint has moved to the middle layer (design, coordination, refinement), exactly where we're now seeing the slowdown.

---

## 5. Our Plan to Bring It In Sooner (if allowed)

The fastest path is not "more people" or vaguely "more AI." It's restoring the conditions that produced our earlier pace.

1. **Reinstate design-first.** Produce a technical design across the 16 initiatives up front, resolving the overlaps once. This is the enabler for everything else.
2. **AI-accelerate from the design.** With a clean design and defined contracts/integration points, large sections can be one-shot with Claude/Copilot — this is where the throughput multiplier actually lives.
3. **Phase the delivery.** Carving into delivery phases (already on ESG's agenda) plays directly to decomposition — sequence by dependency, ship value earlier.
4. **Align accountability with control.** We're happy to be measured on delivery where we own the levers that drive it. Under a shared-ownership model, timescale accountability is genuinely shared.
5. **Right-size the team to the work, post-design.** Adding developers *before* the work is designed and decomposed adds coordination overhead and rework, not speed. Design first, then scale the team to the shape of the work.

### Responding to Jen's agenda (reduce timescales: more resource / AI / phasing)
- **More resource:** won't help linearly on undesigned, overlapping work — risks worsening integration rework. Design first, then add people to a decomposed backlog.
- **Use of AI:** the real lever — *but it requires the upfront design.* This is the honest case for reinstating design-first.
- **Phasing:** yes, supportive — it aligns with how we decompose.

---

## 6. How to Play the Conversation with Lynsey

*Strategic framing — Jonathan's call, offered as counsel.*

- **Listen first.** Lynsey is product/outcome-focused and more senior than the day-to-day delivery politics. Open by understanding *her* pain points and what she's trying to achieve. Let her define success before we position.
- **Partner, not defence.** Avoid leading with "the timescales aren't our responsibility." It's true in fairness terms, but framed that way it invites "then we'll take it fully in-house." Instead: *"align accountability with control"* and pivot to value.
- **Anchor on the contrast, not the complaint.** "Smaller scope, same duration, only the process changed" is fair, factual, and lands without blaming individuals.
- **Move up the value stack.** D55's value is the delivery *system*, not interchangeable dev capacity. As embedded individuals we're commoditised and easy to offboard; as the people who bring the 5x method we're not.
- **Turn the "teach us your AI method" request into an opportunity.** Rowena wants Huw to show ESG devs how we break work down with AI. We're **in the process of productising this** (the AI-DLC programme: assessment, workshops, embedded prove-it, runbook). Offer it as a **structured enablement engagement** rather than free osmosis. This protects the method, secures future work, strengthens the relationship, and directly answers the "use of AI" question — a genuine win-win.
- **Be measured on the "how."** Share the *principle* (design-first unlocks AI acceleration) freely — it strengthens our case. Keep the *detailed reusable playbook* as the commercial asset it is.
- **Jonathan's real goal:** reinforce the relationship and secure future work. Every point above should serve that, not win a delivery-process argument.

---

## Open Questions / To Confirm Before the Meeting

- Is end-of-July a hard ESG commitment to a customer, or an internal target? (Changes how we frame the gap.)
- What is Lynsey's own top priority — a date, a cost, a capability transfer, or de-risking? (Listen for this.)
- How explicit do we want to be about the handover signals (Jen's resourcing, Rowena's comments) — name it, or let Lynsey lead there?
- Appetite to formally propose the AI-DLC enablement engagement, or plant the seed only?
