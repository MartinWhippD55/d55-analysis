# AI-DLC Workshop — Iterative Improvement Process

## How This Works

This is a self-improving loop. Maximum 3 iterations, stopping early if the critique comes back clean.

Each iteration:
1. **Critique** — invoke a sub-agent using `critique-prompt.md` against the current assets
2. **Triage** — separate issues into "addressable now" (can fix in the files) vs "requires external action" (needs people, clients, or decisions)
3. **Fix** — address all "addressable now" issues across the assets
4. **Re-critique** — invoke again to verify improvements landed

"Clean" means: CTO readiness ≥ 4/5 AND Marketing readiness ≥ 3/5 on addressable items only. External dependencies (case studies, real pilots, design resources) are parked — they can't be fixed by editing documents.

---

## Scope of "Addressable Now"

Things we CAN fix in iteration:
- Missing content in dimensions, questions, rubrics
- Structural gaps (facilitator's guide, intake form, scoring calibration)
- Naming and messaging clarity
- Security/technical blind spots in the dimensions
- AWS-specific depth where it's missing
- Reducing question count / adding "must-ask" vs "go deeper" tiers
- Disqualification criteria
- One-pager / collateral content (text only, no design)
- Improving the workshop HTML tool

Things we CANNOT fix (parking lot):
- Real case studies / proof points from actual delivery
- Named client testimonials
- Visual design assets (designer needed)
- Landing page build (needs hosting, forms, design)
- Booking mechanism
- Pricing decisions that need Rhys/leadership sign-off
- Running pilot assessments

---

## Iteration Prompt (for the sub-agent)

Use this exact prompt when invoking the critique sub-agent:

```
You are performing a cold critique of a service offering called "AI-DLC Workshop" by D55 (a cloud consultancy). You have no background context — evaluate the assets as delivered.

Read these files:
1. analysis/D55/ai-dlc/context.md
2. analysis/D55/ai-dlc/dimensions.md
3. analysis/D55/ai-dlc/workshop.html
4. analysis/D55/ai-dlc/generate_spreadsheets.py
5. analysis/D55/ai-dlc/critique-prompt.md

Follow the instructions in critique-prompt.md exactly. Perform the critique from BOTH perspectives (CTO and Marketing Director).

IMPORTANT — Scoring guidance:
- Only score based on what's addressable in the documents themselves.
- If an issue requires external action (real case studies, design work, live pilots), note it but do NOT let it reduce the readiness score.
- A score of 4/5 means "ready to use with a real prospect with minor polish needed."
- A score of 5/5 means "confidently client-ready."

At the end, provide:
1. CTO readiness score (1-5) with the single most important remaining gap
2. Marketing readiness score (1-5) with the single most important remaining gap
3. A verdict: PASS (both scores ≥ 4/5 for CTO, ≥ 3/5 for Marketing) or ITERATE (with the top 3 fixes needed)

Write your output to: analysis/D55/ai-dlc/critique-output.md (overwrite previous)
```

---

## Process for the Orchestrator (Kiro)

```
iteration = 0
max_iterations = 3

while iteration < max_iterations:
    iteration += 1
    
    # Step 1: Invoke critique sub-agent
    run critique using prompt above
    
    # Step 2: Read critique-output.md
    check verdict: PASS or ITERATE
    
    if PASS:
        commit and push
        report: "Clean after {iteration} iteration(s)"
        stop
    
    if ITERATE:
        # Step 3: Read the top 3 fixes
        # Step 4: Implement fixes across assets
        # Step 5: Regenerate spreadsheets if generator was changed
        # Step 6: Continue to next iteration

if iteration == max_iterations and not PASS:
    commit and push current state
    report: "Reached max iterations. Remaining gaps: [list from last critique]"
```

---

## Parking Lot (External Actions Required)

Track items here that come out of critiques but can't be addressed in-file:

| Item | Owner | Status |
|------|-------|--------|
| Run 2-3 pilot assessments | Rhys + Delivery | Not started |
| Choose external-facing name (not "AI-DLC") | Rhys + Martin | Not started |
| Get radar chart mocked up by designer | Marketing/Design | Not started |
| Build landing page | Marketing | Not started |
| Source/qualify 5x productivity claim | Martin | Not started |
| Identify 2-3 target industries | Rhys + Sales | Not started |
| Assign a "face" for the offering (content, events) | Rhys | Not started |
