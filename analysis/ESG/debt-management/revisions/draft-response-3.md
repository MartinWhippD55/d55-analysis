# Draft Response v3 — To Gareth & Darren

---

Hi Gareth, Darren,

Thank you for documenting this. We want to address the points raised directly.

## Our process

D55's delivery process on this workstream:

1. Developer writes code (AI-assisted, as communicated upfront)
2. PR raised → automated feedback addressed
3. Internal D55 peer review before merge to feature branch
4. Developer self-testing — defects raised and fixed transparently
5. System test per initiative
6. PR preparation — developers review against ESG standards before requesting ESG review
7. ESG review → feedback addressed → merge to main

This is not "prompting and merging." There are multiple review gates before work reaches your team.

## The data

| | Total defects | Self-raised by D55 | Found by ESG testers | % Closed |
|---|---:|---:|---:|---:|
| IP | 69 | 44 | 25 | 100% |
| DBT | 58 | 32 | 26 | 93% |
| **Combined** | **127** | **76 (60%)** | **51 (40%)** | **97%** |

60% of all defects were found and raised by D55 ourselves. The team is testing its own work. A 97% closure rate across 127 defects on a 19-initiative workstream delivered under compressed timelines is not a team that's disengaged.

## What we've done proactively

- **review-pr skill** — rulesets distilled from previous ESG PR feedback and your documented Confluence standards. Developers run this manually via Copilot/Claude before requesting ESG review. Ready to translate into CLAUDE.md per repository as Alex suggested.
- **PR preparation tickets** — distributing the burden of addressing feedback across the squad before it reaches Damian and Alex. Not throughput inflation — coordination. Happy to remove/reclassify if preferred.
- **Collaborative refactor with Damian** — rules engine reworked from 35 classes to 3 (net -969 LOC), working directly with Damian. Contract changed mid-work requiring retesting; absorbed without complaint.
- **Interactive documentation** — diagrams explaining system workflow for BA and product owner, cross-referencing code and test assets.
- **Titanium-Test-Data repository** — seed data scenarios enabling faster test iteration for everyone.

## Addressing specifics

**"16 components for a dialog"** — Actual count is 11 components for a recursive tree editor (AND/OR/NOT rule DSL). This is standard React composition for tree-shaped UIs — not over-engineering. Damian correctly identified 4 that should wrap existing primitives; these are being addressed. That's review working as intended.

**"Removing Lombok / coding in own style"** — Acknowledged. This is a style alignment gap, not a correctness issue. Our review-pr skill and CLAUDE.md adoption address this directly.

**"Editing unrelated components"** — We'll ensure PR preparation explicitly checks for unrelated changes going forward.

## Context that matters

- This workstream covers 19 initiatives with near-impossible deadlines. Additional scope was pulled forward after we reached dev-complete on the original plan — no timeline relief given.
- Long-lived feature branches (ESG's decision) concentrate review burden at merge time rather than spreading it across trunk-based commits. That's what's being felt now.
- We are on track for July delivery, but need continued PR review from ESG to merge to main.
- Many of the issues raised relate to already-merged workstreams (IP, Financial Management). Actions have been taken; the output of those actions is what's now in flight.

## Commitment

Every D55 developer on this workstream has gone above and beyond — working late and weekends to hit these deadlines. We've addressed feedback comprehensively, including style and nitpick items. Previous feedback has also recognised good quality in our output.

Our goal is to deliver good code, on time, that you're happy with. Damian and Alex's input is making the output better and we value the collaboration.

**Actions:**
1. CLAUDE.md adoption — translating review-pr rulesets into each repository
2. Explicit unrelated-change checks in PR preparation
3. Address Damian's 4 reuse items in the rule editor before merge
4. Continue self-testing and transparent defect raising

Happy to discuss further on a call.

Jonathan
