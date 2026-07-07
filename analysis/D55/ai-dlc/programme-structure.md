# AI-DLC — Full Programme Structure

*Draft for Rhys. Created 2026-07-07. Builds on the 2026-07-02 feedback that "the service needs to go up a level."*

*Nothing in the existing assets is removed. This doc sits above them: it defines the full service, and reframes the assessment workshop as the first step of it.*

---

## The Core Reframe

We have been selling the diagnostic. We should be selling the transformation.

The assessment workshop is not the offering — it is step one of the offering. On its own, a free one-hour diagnostic is a lead magnet, not a service. The value to a customer is not "you found out where you stand." It is "you got from where you were to AI-native engineering, you can prove it with numbers, and you own the capability to keep going without us."

The whole service is **AI-DLC**. The assessment is how it starts.

This also fixes the commercial problem. À la carte workshops are easy to decline one at a time. A programme with a clear outcome is a single, larger decision — and a better one for the client.

### The 2-minute pitch (the one story)

> "We assess where your engineering org really is with AI — free. We teach only the gaps that matter. Then we embed a hybrid team alongside your people, ship real work, and prove the ROI with hard numbers. Then we leave — and you keep the capability and the operating manual to run it yourselves."

That's the whole programme in five sentences: Assess → Teach → Prove → Scale, with "we leave, you keep it" as the differentiator. Everything below expands on it.

---

## Two Runbooks (resolving the terminology)

We have been using one word — "runbook" — for two different things. They need separate names.

### 1. The D55 Delivery Playbook (internal)

Our repeatable sequence for running an AI-DLC engagement: assess → teach where needed → embed and prove → roll out. This is D55 IP. It is how we deliver consistently across clients and how a new consultant knows what to do next. The assessment is the first step because **it decides what the rest of the sequence looks like for that specific client.**

Audience: D55. Never handed over.

*(Not yet authored as its own doc — the four phases below are effectively its spine. A standalone `delivery-playbook.md` for consultant onboarding is a follow-up once the structure is agreed.)*

### 2. The Client Operating Manual (the kept asset)

The client's own playbook for AI-native engineering — what good looks like *for them*: their standards, their tooling setup, their guardrails, their metrics baseline, their ways of working. This is the artefact they walk away owning and operating from after we leave.

Audience: the client. This is a core part of the value we hand over.

**How they relate:** our Delivery Playbook drives the engagement; the engagement produces and populates the Client Operating Manual. Each phase we deliver writes another section of the client's manual. By the end, it is complete and it is theirs.

*(Naming: "Client Operating Manual" is a working label — open to a better name. It's the thing Rhys called "the asset they keep.")*

---

## The Programme: Four Phases

```
AI-DLC (the full service)
│
├── Phase 0 — Assess        Free. The workshop we've built. Decides the path.
├── Phase 1 — Teach         Workshop modules, only the ones the gaps call for.
├── Phase 2 — Prove         Embed a D55 team. Ship real work. Baseline metrics.
└── Phase 3 — Scale         Roll out across the org. Hand over the manual. We exit.
│
└── Throughout: the Client Operating Manual is written, section by section.
```

The assessment radar decides which phases and modules a given client actually needs. Not everyone does all of it — but the destination we're steering toward, when the gaps warrant it, is **Phase 2 (embed)**, because that's where the value is actually created.

### Phase 0 — Assess (free)
- **What:** the existing 1-hour workshop. 8 dimensions, current vs target, radar + gap analysis.
- **Produces:** the first section of the Client Operating Manual — "where you are, where you want to be." And, internally, the decision on which modules/phases to recommend.
- **Already built.** No change needed beyond framing it as step one.

### Phase 1 — Teach (workshop modules)
- **What:** targeted workshops, chosen by the gaps the assessment surfaced. Not a fixed menu — a prescription.
- **Produces:** the "how you close each gap" sections of the manual, plus the client's people knowing how to do it.
- Clustered into **four modules** (below) so the service feels tight, not like a list of eight things.

### Phase 2 — Prove (embed a hybrid team)
- **What:** the 8-Week Prove-It model, made real. This is **not** "D55 comes and does the work." It's a deliberately **hybrid team** — D55 engineers + the client's own people on the same squad — shipping live work together, with metrics baselined from day one.
- **Why hybrid by design:** capability only transfers if their people are *on* the team, learning by doing, not watching from the side. The hybrid structure is what makes the handover real rather than a document dump.
- **The handover is planned from day one, not bolted on at the end.** D55 presence deliberately tapers as the client's people take on more, so that when we roll off they can keep going. Two shapes depending on the client:
  - **D55 + their people → handover:** hybrid squad, client staff upskill in-flight, D55 exits leaving a self-sufficient team.
  - **D55-only → handover:** where the client can't spare people up front, D55 delivers and hands over to a receiving team at completion (weaker capability transfer — we steer clients toward the hybrid shape where possible).
- **Produces:** shipped work, a proven metrics delta, and — critically — capability transferred into the client's team.
- **This is the centre of gravity of the whole service** and its largest revenue component (~£15–25k/engineer/month). Teaching sets it up; proving is where the value lands. It is a team structure operating over a multi-month engagement — which is why it's a phase, not a workshop.
- **Duration model:** the **8-Week Prove-It** (Assess wk 1–2, Prove wk 3–6, Translate wk 7–8) is the *core proof cycle* inside Phase 2 — the minimum to baseline, ship, and demonstrate a metrics delta. A full embed typically runs longer (proof cycle + taper as capability transfers), so quote it as "8-week proof cycle, with an embed that tapers over the following weeks/months as your people take over." The 8 weeks is the committed proof; the taper is scoped per client.
- **Embed prerequisites (resolves the "skip modules you don't need" tension):** the embed depends on outputs that Modules 1, 3 and 4 produce — the metrics scorecard (M1), the shipping guardrails (M3), and the hybrid operating model (M4). If a client's assessment didn't trigger one of those as a full workshop, its output is still a **required pre-embed input** — captured as a compressed working session rather than skipped. See the pre-embed checklist note below.

### Phase 3 — Scale (roll out and exit)
- **What:** expand the proven pattern across other teams. Hand over the completed Client Operating Manual. Deliberately reduce our presence.
- **Produces:** an org running AI-native engineering on its own, with the manual as its operating spine.
- **The exit is a feature, not a bug.** "We enable, then leave" is our differentiator from body-shops.

---

## The Four Workshop Modules (clustering the 8 dimensions)

Eight workshops would look bloated. Four modules map cleanly onto the assessment and feel like a coherent programme.

| Module | Dimensions it covers | Audience | Purpose |
|--------|---------------------|----------|---------|
| **1. Leadership & the Investment Case** | Leadership & Mandate · Metrics & ROI | Execs, sponsor, CFO/PE | The business case and how we'll measure it. Sets the mandate and the scorecard. |
| **2. The AI-First Delivery Lifecycle** | Developer Tooling · Specification & Design · Delivery Process & Ceremonies | Engineering, POs/BAs | The core "how we actually work now" module. Tooling, specs-up-front, adapted ceremonies. |
| **3. Shipping Safely** | Testing & Quality · Governance, Security & Compliance | Eng leads, security, compliance | Going fast without blowing up. Test strategy for AI code, DLP, audit trail, EU AI Act. |
| **4. People & Change** | Team Adaptation & Skills (incl. Four Fears + middle-layer) | Leadership, POs/BAs/PMs, HR | The human side. Diagnose resistance, redefine coordination roles, upskill, **and how to structure/run a hybrid AI-native team** (the operating model that Phase 2 embodies and hands over). |

Each module maps to a chunk of the radar and writes the corresponding section of the Client Operating Manual. The assessment scores tell you which modules a given client needs — a client strong on tooling but weak on governance might do Module 3 only before going to embed.

---

## How We Drive Maximum Value for the Client

Rhys's key point. The client doesn't want workshops or a runbook — they want three outcomes: **ship faster, prove it with numbers, don't make a mess doing it.** Five principles for organising the service around those outcomes:

**1. Value is created in the doing, not the assessing.** Assessment and workshops are setup. The real value lands in Phase 2 when a D55 team is embedded and shipping real work with their people, metrics baselined from day one. Get to shipped work fast and instrument it heavily — the metrics justify everything after.

**2. Transfer capability, don't create dependency.** The biggest long-term value and our cleanest differentiator. A body-shop leaves nothing behind; we embed *and deliberately teach* — pairing, the Client Operating Manual, leaving their people able to run it. That capability compounds after we go. Make capability transfer an explicit, measured deliverable — not a side effect.

**3. De-risking is value, especially to the buyer.** The CTO's real fear is making a mess at 5x speed — insecure code, compliance exposure, EU AI Act. "You can now go fast *safely*" is worth as much as the speed itself, and it's what lets leadership authorise scaling at all.

**4. Solve the problem they don't know they have.** The middle-layer bottleneck is high-value precisely because it's non-obvious. Surfacing it in the assessment and fixing it in delivery makes us look like we've been somewhere they haven't.

**5. Leave a flywheel.** End state should be self-sustaining: metrics prove ROI → justifies more investment → more adoption → more metrics. The Client Operating Manual institutionalises it so it survives after we leave.

---

## Commercial Shape (for discussion, not decided)

Moving from à la carte to a programme with a natural path. Existing à la carte pricing (from `context.md`) still stands as the components — this just packages them.

| Tier | What's included | Rough shape |
|------|-----------------|-------------|
| **Assess** | Phase 0 only | Free (the lead magnet) |
| **Assess + Teach** | Phase 0 + chosen modules | Per module (~£5–15k each, per existing pricing) |
| **Full programme** | Phase 0 → Teach → Embed → Scale | Programme price; embed dominates (~£15–25k/engineer/month) |

Two notes on the shape:
- **Module pricing should track effort, not sit in one flat band.** Module 1 is a half-day exec session; Module 2 is a 1–2 day hands-on build. Same ~£5–15k band, very different cost-to-deliver — so price within the band by duration rather than charging the same for all four.
- **The per-module tier is the load-bearing bridge** from free to the embed. It's a wide jump from £0 to a £15–25k/engineer/month programme, so position modules explicitly as the low-risk "try us before you commit" rung.

Open commercial questions for Rhys:
- **Does "free assessment" stay free, or convert to paid discovery for serious prospects?** This needs a decision — it changes the sales motion. The anchoring risk is real: "free" anchors the relationship at zero and can make the first paid step feel like a cliff. Two credible answers: (a) keep it a genuine free lead magnet that delivers standalone value (Section 0 of their manual + a radar they keep), backfilling proof from early sessions; or (b) keep a free *taster* but convert qualified prospects to a paid deeper discovery before the programme. Recommendation: start with (a) to build trust and pipeline, move to (b) once we have proof points and demand. **Rhys call.**
- Is the programme sold as one price, or as a committed path with stage gates the client can stop at?
- How do we price capability transfer so it's valued, not seen as "you charging us to leave"?

---

## What This Doesn't Change

- Everything already built stays. The assessment workshop, dimensions, facilitator guide, intake form, worked example, positioning, spreadsheets — all intact and all still correct.
- The 8 dimensions stay as the assessment axes. The four modules are a *delivery* clustering, not a change to how we assess.
- The D55 IP frameworks (Four Fears, AI-First Delivery Lifecycle, Middle-Layer Bottleneck, 8-Week Prove-It, the Economics) all carry through unchanged.

---

## Future Tooling Vision (parked)

The assessment tool (`workshop.html`) is real software and the natural place this heads. The vision: a D55 **skill** that consumes the structured module library plus a client's assessment scores, and generates two things automatically — a tailored assessment write-up and a populated Client Operating Manual (the runbook).

```
Assessment scores (from workshop.html)
        +
Module library (structured docs — see /modules)
        ↓
   [D55 skill]
        ↓
Tailored assessment write-up  +  populated Client Operating Manual
```

Implication for how we write the modules **now**: each module doc carries machine-parseable metadata (dimensions covered, score-gap trigger thresholds, deliverables, which manual section it writes) so the future skill has clean inputs and we don't retrofit. This is genuine software — a Kiro spec would fit when we build it.

**Foundations now in place for this** (so skills can be built against a stable target, not a moving one):
- `modules/MODULE-SCHEMA.md` — the frontmatter contract every module follows, including the score→recommendation trigger logic.
- `client-operating-manual-toc.md` — the runbook spine each module writes into.
- `modules/module-*/module.md` — the four modules, structured to the schema.

**Planned skills** (build order — content first, then skills):
1. *module-to-presentation* — repurposes the existing `summary-presentation` / `deliverables-toolkit` skills to turn a `module.md` into a branded deck. Cheapest first build (mostly reuse).
2. *module authoring* — assessment-aware: leads with radar scores + trigger logic to recommend which modules a client needs, discusses to confirm, and scaffolds the folders.
3. *assessment→runbook* — consumes scores + module library → tailored write-up + populated Client Operating Manual.

Skills 2 and 3 overlap (both consume scores + module library) and may merge into one "AI-DLC engine" skill under an orchestrator like the existing `spec-to-deliverables`. Parked until module content and manual structure are validated with Rhys.

---

## Open Questions / Decisions for Rhys

1. **The two-runbook split** — does separating "D55 Delivery Playbook" (internal) from "Client Operating Manual" (kept asset) match how you're thinking about it?
2. **Four-module clustering** — right grouping, or would you split/merge differently?
3. **Embed as the destination** — agree Phase 2 is the centre of gravity and where we steer clients when gaps warrant?
4. **Programme pricing** — one price vs stage-gated path (see commercial questions above).
5. **Naming** — "Client Operating Manual" as the kept asset; and the still-open external name for AI-DLC itself (candidates in `positioning.md`).

---

## Suggested Next Steps

Done:
- ✅ Four modules fleshed out (`modules/module-*/module.md`) to the schema.
- ✅ Client Operating Manual TOC defined (`client-operating-manual-toc.md`).
- ✅ Module schema authored with trigger logic (`modules/MODULE-SCHEMA.md`).
- ✅ Critique loop run (CTO 4/5, Marketing 3/5 — PASS). See `critique-output-programme.md`.

Remaining polish (authorable now, from the critique — all recommended, none blocking):
1. **Phase 2 embed scoping template** — one-pager: squad shape + D55:client ratio, the duration model (now reconciled above), week-by-week taper, and explicit exit/capability-transfer criteria. Highest-leverage item: turns the biggest revenue line from a rate into a quotable job.
2. **Starter templates per module** — skeleton artefacts (investment-case one-pager, spec template, AI usage policy, Four Fears output sheet, governance checklist) so any consultant can run a module, not just an IP-fluent senior. These would live in each module's `assets/`.
3. **Pre-embed checklist** — captures the M1/M3/M4 prerequisite outputs even when those modules weren't run as full workshops.
4. **Standalone `delivery-playbook.md`** — the internal spine, for consultant onboarding.

Needs Rhys / decisions:
5. React to the structure (esp. the two-runbook split and the four modules).
6. The free-vs-paid-discovery anchoring decision (see commercial section).
7. Update `context.md` decision log and `HANDOVER.md` to reflect the agreed structure — including reconciling phase numbering (this doc uses Phase 0–3; older docs use Phase 1–4).
