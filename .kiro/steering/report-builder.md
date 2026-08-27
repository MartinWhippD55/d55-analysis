---
inclusion: fileMatch
fileMatchPattern: '**/report-builder/**'
---

# Report Builder — start here

When working on the **Report Builder** feature, the entry point is the session
handoff, not the individual files:

**Read [`analysis/BRYT/report-builder/session.md`](../../analysis/BRYT/report-builder/session.md) first.**

It holds the current status, where every document lives, the key facts and
constraints (bryt-number scoping, Glue catalog, Join_Manifest, Bedrock decision,
the new `BrytReportBuilder` repo), and a "how to work a session" loop.

## Loop

1. Read `session.md` to learn what's done and the **next action**.
2. Open [`analysis/BRYT/report-builder/plan.md`](../../analysis/BRYT/report-builder/plan.md)
   and find the first `[ ]` / `[~]` task — that is what to do next.
3. As you work: mark tasks `[~]` (in progress) → `[x]` (done), or `[!]` if blocked.
4. Before ending: update the **Status** block in `session.md` and add any
   decisions to the **Decision log** in `plan.md`.

## Source of truth

- Scope & flow: `analysis/BRYT/report-builder/overview.md` + `screen-mockups.md`
- Requirements (approved, EARS): `.kiro/specs/report-builder/requirements.md`
- Design: `.kiro/specs/report-builder/design.md` _(written in Phase 0.6)_
- Backend reference pattern: `reference-repos/BrytBusinessServices` (contract-note)

Do not re-derive settled decisions — they are recorded in `session.md`.
