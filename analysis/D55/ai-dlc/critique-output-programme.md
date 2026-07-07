# AI-DLC Programme Layer — Critique

*Cold critique of the new programme layer (Phase 0→3, two-runbook split, 4 modules, schema, Client Operating Manual TOC). Assessed on its own merits. The original assessment workshop is treated as already-passed and out of scope.*

*Date: cold review of the programme-structure layer.*

---

## Perspective 1: CTO / Delivery Director

### Does the 4-phase programme sequence sensibly?
Yes. Assess → Teach → Prove → Scale is the right spine and reads like something a delivery org would actually run. The logic that "the assessment decides what the rest looks like" is the correct organising idea, and making Phase 2 (embed) the explicit centre of gravity is a good, honest call — it puts the money and the value in the same place. Framing the exit as a feature rather than an afterthought is a genuine differentiator and it's baked into the structure, not bolted on.

**But there's an unenforced-dependency problem.** Phase 1 is explicitly "only the modules the gaps call for" — a prescription, not a menu. Yet Phase 2 (embed) has hard prerequisites that live *inside* those modules:
- The metrics scorecard that Phase 2 "baselines from day one" is produced by **Module 1**.
- The guardrails that let embedded work reach production are produced by **Module 3**.
- The hybrid operating model that *is the embed's team structure* is produced by **Module 4**.

So a client who scores well on Leadership (Module 1 not triggered) but proceeds to embed has no defined source for the scorecard the embed depends on. The programme narrative assumes modules feed the embed, but the module-selection logic can skip the very modules the embed needs. Right now nothing reconciles "skip modules you don't need" with "embed requires outputs from Modules 1/3/4." **Fix:** either mark the embed prerequisites explicitly (e.g. "if going to Phase 2, Modules 1, 3, 4 outputs are required inputs — deliver a compressed version if not triggered as a full workshop") or add a pre-embed checklist that captures those artefacts regardless of which modules ran.

### Is the clustering of 8 dimensions into 4 modules sound?
Mostly sound, and clearly better than eight standalone workshops. Three of the four clusters are clean:
- **Module 2 (Tooling + Specs + Ceremonies)** is the strongest grouping — those three genuinely only work together, and the doc says so.
- **Module 3 (Testing + Governance)** as "Shipping Safely" is a coherent, sellable frame.
- **Module 1 (Leadership + Metrics)** as "the investment case and the scorecard" is tight.

The one that's carrying strain is **Module 4**. It bundles a single assessment dimension (Team Adaptation & Skills) with a large extra payload — "how to structure and run a hybrid AI-native team," i.e. the operating model that Phase 2 embodies. That's arguably the most important content in the whole programme (it's what makes handover real), and it's tucked into a one-dimension module as a fifth agenda item. Two consequences:
1. Module 4 is the only module mapped to a single dimension, so its trigger only fires off one score — yet it carries embed-critical content.
2. The operating-model content will get squeezed in a 1-day session that also has to run the Four Fears diagnostic, the middle-layer role shift, and upskilling.

It's not *wrong*, but the hybrid-team operating model probably deserves to be pulled out as its own named deliverable (even if delivered within Module 4) rather than being the tail of the people module.

### Is the two-runbook split clear and useful?
Yes — this is the cleanest part of the new layer. "D55 Delivery Playbook (internal, never handed over)" vs "Client Operating Manual (the kept asset)" resolves a real terminology collision and the relationship ("our playbook drives the engagement; the engagement writes their manual, section by section") is genuinely useful and correct. The TOC then makes it concrete by naming which phase/module writes each section.

One gap: **the Delivery Playbook is named but not authored anywhere.** The four phases are effectively its spine, so it exists implicitly, but there's no `delivery-playbook.md`. For internal consistency and onboarding a new consultant, that document should exist as more than the marketing-facing phase descriptions.

### Are the modules deliverable? Could you hand `module-*.md` to a senior consultant and have them run it?
A **senior consultant who already knows the D55 IP** could run these — objective, audience, inputs, session flow, deliverables and the embed linkage are all present and consistent. That's a solid, repeatable structure. But it is **not yet turnkey**, and the gaps are specific:

1. **No delivery templates ship with the modules.** Every module promises tangible artefacts "drafted in the room" — a one-page investment case, a spec template, an AI usage policy, a Four Fears diagnostic output, a governance checklist. None of these template artefacts are included. The consultant has to build them live or from memory. Since the whole value story is "you leave with real artefacts, not promises," the *absence* of starter templates is the single biggest deliverability gap. (The Four Fears instrument at least exists in `dimensions.md`, but it's not referenced from the module or packaged with it.)
2. **No per-step timings.** Module-level durations are given (half day, 1–2 days) but the numbered session flows have no time-boxes. A 1–2 day range for Module 2 is a 100% variance — fine as a planning hint, not enough to actually run the day.
3. **No "what to send ahead / pre-reqs" per module.** Phase 0 has an intake form; the modules have none.
4. **`assets/` folders are specified but empty.** The schema anticipates slides/exercises/handouts; none exist yet.

None of these require external dependencies to fix — they're authorable now — so they inform the score without capping it, but item 1 is what stands between "a senior can run it" and "any consultant can run it."

### Is the hybrid-embed (Phase 2) credible and specified enough to scope/price?
Credible in concept — the "hybrid by design, handover planned from day one, presence tapers" framing is exactly right and the two shapes (D55+client → handover vs D55-only → handover) are a sensible articulation. **But it is under-specified for scoping or pricing**, and it's the phase that most needs to be specified because it's the largest revenue line and the stated centre of gravity. Missing:
- **Team size / ratio.** No guidance on squad size or the D55:client-people ratio that makes the hybrid shape work.
- **Duration is internally contradictory.** The doc says Phase 2 "is a team structure operating over **months**, not a workshop," but also that it's "the 8-Week Prove-It model, made real." `HANDOVER.md` defines 8-Week Prove-It concretely (Assess wk 1–2, Prove wk 3–6, Translate wk 7–8). Eight weeks is not "months." Is the embed an 8-week proof or a multi-month engagement? This needs reconciling — it directly changes the price.
- **No taper schedule.** "Presence deliberately tapers" is asserted but not shaped (e.g. week-by-week D55 headcount ramp-down), so it can't be costed.
- **No exit / success criteria.** What has to be true for D55 to roll off? "Capability transferred" is named as a deliverable but not defined as a measurable gate.

Per-engineer/month pricing gives a *rate*, but without team size, duration, and taper you can't produce a *quote*. **Fix:** add a one-page embed scoping template (squad shape, ratio, duration model, taper, exit criteria) — this was already flagged as a polish item in `HANDOVER.md` and it's the highest-leverage one.

### Is the MODULE-SCHEMA / trigger logic coherent enough for a tool to consume?
Largely yes — this is impressively disciplined for a draft. The join keys are real and they check out: every module's `dimensions_covered` matches `dimensions.md` exactly, and every `manual_section` matches a title in the Client Operating Manual TOC exactly. A tool could glob `modules/*/module.md` and join on those keys today. That's the right foundation. Remaining gaps and ambiguities:

1. **The `critical` gate is module-scoped but the intent is dimension-scoped.** Module 3's comment says "Governance is a hard gate," and `critical_when_current_at_or_below: 2` is set. But the reference logic applies critical "for each dimension it covers" — Module 3 also covers Testing & Quality. So a client with strong governance (4) but weak testing (2) would be flagged **critical** on the basis of testing, which contradicts the stated intent. A consuming tool can't tell governance from testing here. **Fix:** move `trigger` (at least the critical threshold) to per-dimension, or add a `critical_dimensions` list naming which dimension(s) the hard gate applies to.

2. **Target scores barely influence *inclusion*.** Inclusion is driven almost entirely by `recommend_when_current_at_or_below` (current-state only). The gap `(target − current)` only sets *priority*, never inclusion. Consequence: a client at current 4 / target 5 across the board — clear ambition, real gaps — triggers **no modules at all**. That quietly undercuts the "current vs target roadmap" story the whole assessment is built on. Decide deliberately: is the programme only for the currently-weak, or should a large target gap pull a module in even from a decent base? State it either way.

3. **Inconsistent `recommend_when_current_at_or_below` across modules, with no rationale.** Module 1 recommends at ≤2; Modules 2/3/4 at ≤3. Maybe deliberate (leadership gaps are common, so a higher bar), but nothing explains it. A future maintainer/tool author will read this as a possible typo. Add a one-line rationale per threshold.

4. **Filename-casing inconsistency in the contract.** `MODULE-SCHEMA.md` refers to the TOC as both `CLIENT-OPERATING-MANUAL-TOC.md` (in the field description and the example) while the actual file is `client-operating-manual-toc.md`. Trivial for a human, breaks a case-sensitive tool. Pin one canonical casing.

5. **Priority-without-inclusion edge case is unstated.** The logic never explicitly says priority only applies to included modules. Given the current 1–5 scoring it can't actually produce a high-priority-but-excluded module, but a tool author would want that stated rather than inferred.

### Does the Client Operating Manual TOC map cleanly to what the phases produce?
Yes — cleanly. Section 0 ← Phase 0, Sections 1–4 ← Modules 1–4, Section 5 ← Phase 2 embed, Section 6 ← Phase 3. The "populated by / when" table makes the fill-order explicit and the section titles are the exact `manual_section` join targets. This is the most finished piece after the two-runbook split. The only open item (manual format: document vs living tool) is correctly parked as a Rhys decision and doesn't block anything.

---

## Perspective 2: Marketing / Commercial Director

### Does "going up a level" make this more sellable?
Net yes, for the buyer that matters. A free one-hour diagnostic is a lead magnet, not a service — the reframe correctly turns "eight things you could buy" into "one transformation with a clear destination," which is a better decision for an exec to make and a bigger one for D55 to win. The single-transformation framing is the right move.

The friction it adds is real but manageable: the curious, low-commitment prospect who'd have happily taken a free hour now sees the free hour as the front door to a programme. That's fine **as long as the free assessment still delivers standalone value** (it does — it produces Section 0 of their manual and a radar they keep). The risk is tone: if the assessment feels like a sales funnel rather than a genuine diagnostic, you lose the very trust that made the free workshop work. Keep Phase 0 honestly useful on its own.

### Is the value-to-client argument (5 principles) compelling and distinct from body-shop staff-aug?
This is the strongest part of the whole layer. The five principles are genuinely differentiated and they're the antidote to "you're just expensive contractors":
- "Value is created in the doing" — puts proof, not paper, at the centre.
- "Transfer capability, don't create dependency" + "the exit is a feature" — this is the clean, defensible line against body-shops, and it's structural (the hybrid squad, the kept manual), not a slogan.
- "De-risking is value to the buyer" — speaks directly to the CTO's actual fear.
- "Solve the problem they don't know they have" (middle-layer bottleneck) — makes D55 look like it's been somewhere the client hasn't.

These are distinct, credible, and hard for a staff-aug shop to copy. Keep them.

### Is the commercial shape coherent? Pricing/packaging risks?
The ladder (free → per-module → full programme) is coherent and maps to the existing à la carte pricing, so nothing is invented. Two risks:

1. **A big step in the value ladder.** The jump from "free" to a programme dominated by £15–25k/engineer/month embed is large, with per-module (£5–15k) as the only bridge. That's a wide gap to walk a nervous buyer across. The per-module tier is doing a lot of load-bearing work as the "try before you commit" rung — make sure it's genuinely positioned that way.

2. **Price doesn't track effort across modules.** Modules sit in one ~£5–15k band, but Module 1 is a half-day exec session and Module 2 is a 1–2 day hands-on build. Same band, very different cost-to-deliver and value. Either differentiate module pricing or make the band's spread explicitly reflect duration.

### Does "free assessment as front of a programme sale" hold up, or create a discount-anchoring problem?
It holds up but the anchoring risk is live and currently **unresolved**. The doc deserves credit for naming it explicitly ("does free stay free once it's the front of a programme sale?") — but naming it isn't answering it. "Free" anchors the relationship at zero, which can make the first paid step feel like a cliff, and can subtly devalue the IP being given away. The two credible resolutions (keep it a genuine free lead magnet with standalone value / OR convert serious prospects to a paid deeper discovery) point in different commercial directions and need a decision before this goes to a prospect, because the answer changes the sales motion.

### Is there a 2-minute exec story a salesperson could tell?
The *ingredients* are all here, but there is **no assembled elevator pitch in the programme doc** — a salesperson has to synthesise it from five principles and a phase diagram. That's a gap, because the whole point of "going up a level" is a single clean narrative. The story is right there and easy to write:

> "We assess where your engineering org really is with AI — free. We teach only the gaps that matter. Then we embed a hybrid team alongside your people, ship real work, and prove the ROI with hard numbers. Then we leave — and you keep the capability and the operating manual to run it yourselves."

That's tellable in under a minute and it's implicit across the doc. It just needs to be written down once, explicitly, as *the* pitch. (The external programme name is still open — flagged in `positioning.md` — which is a real launch dependency but a noted external item, so it doesn't reduce the score here.)

---

## Consistency check against background (context.md / dimensions.md / HANDOVER.md)
- **Join keys are clean:** all `dimensions_covered` values match `dimensions.md` headings exactly; all `manual_section` values match the TOC titles exactly. Good.
- **Phase numbering drift:** `HANDOVER.md` and `context.md` describe the assessment as "Phase 1" (1-indexed, phases 1–4); the new doc uses "Phase 0" (0-indexed, phases 0–3). The new doc lists "update context.md and HANDOVER.md" as a next step, so this is acknowledged — but until done, anyone reading the older docs will be off by one.
- **8-week vs months tension** (noted above) sits between the new Phase 2 description and the `HANDOVER.md` 8-Week Prove-It definition. Reconcile.
- **Empty `assets/` folders** are specified by the schema but not yet populated — consistent with "content first, then skills," so expected, not a defect.

---

## Scores & Verdict

### CTO / Delivery Director readiness: **4 / 5**
Ready to take to Rhys and use to shape a real client conversation with minor polish. The spine, the two-runbook split, the clustering, and the schema join keys are sound and internally consistent.
**Single most important remaining gap:** Phase 2 (embed) — the largest-revenue, centre-of-gravity phase — is under-specified for scoping and pricing (no team size/ratio, an unresolved 8-week-vs-months duration contradiction, no taper schedule, no exit/success criteria). You can quote a rate but not a job.

### Marketing / Commercial readiness: **3 / 5**
Rich, distinct, and self-aware, with the strongest differentiation (5 principles + exit-as-feature) already nailed. Needs packaging work before it's launch-ready.
**Single most important remaining gap:** there is no single written programme value proposition / elevator pitch — a salesperson has to assemble it from five principles — and the "does free stay free?" anchoring question is named but not decided. Both are in-doc fixes.

### Verdict: **PASS**
(CTO 4/5 ≥ 4 AND Marketing 3/5 ≥ 3.)

Top 3 fixes to move toward "confidently ready" (recommended polish, not blockers):

1. **Specify the embed for scoping (CTO).** Add a one-page Phase 2 scoping template: squad shape and D55:client ratio, a resolved duration model (reconcile "8-Week Prove-It" vs "operating over months"), a week-by-week taper, and explicit exit/capability-transfer criteria. This turns the biggest revenue line from a rate into a quotable engagement.

2. **Ship starter templates with the modules + fix the two trigger ambiguities (CTO).** Package the promised artefacts as skeleton templates (investment-case one-pager, spec template, AI usage policy, Four Fears output, governance checklist) so any consultant — not just an IP-fluent senior — can run a module. In the same pass, make the `critical` gate dimension-scoped (so governance triggers it, not testing) and decide/state whether a large target-gap alone can pull a module in (target scores currently don't drive inclusion). Also pin the TOC filename casing.

3. **Write the pitch and decide the free-anchoring question (Marketing).** Commit the 2-minute exec narrative to the programme doc as *the* elevator pitch, and make the call on whether the assessment stays free or converts to paid discovery for serious prospects — the sales motion depends on it.
