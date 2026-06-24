# Draft Response v2 — To Gareth & Darren

---

Hi Gareth, Darren,

Thank you for documenting these concerns. We take code quality seriously and want to address the points raised with both context and evidence.

## The SDLC process we follow

Before addressing specific points, it's worth setting out the process D55 follows on this workstream, because some of the feedback suggests we're bypassing review entirely — which is not the case.

1. Developer writes code (with AI assistance, as communicated upfront)
2. PR raised against `feature/debt/main`; automated feedback addressed
3. Internal D55 peer review prior to merge into the feature branch
4. Developer self-testing — defects raised and fixed transparently
5. System testing of each initiative
6. PR preparation tasks — developers review their own work against ESG's standards and address known issues before requesting ESG review
7. PR submitted for ESG review
8. ESG feedback addressed
9. Merge to main

This is not "prompting and merging." There are multiple review gates, and the data bears that out.

## The defect data tells a different story

Across Instalment Plans and Debt Management combined:

| | Total | Closed | Open | % Closed |
|---|---:|---:|---:|---:|
| IP | 69 | 69 | 0 | **100%** |
| DBT | 58 | 54 | 4 | **93%** |
| **Combined** | **127** | **123** | **4** | **97%** |

Of those 127 defects, **76 (60%) were found and raised by D55 developers themselves** during internal dev testing and peer review. ESG's system testers identified 51. The team is actively testing its own work, finding issues, raising them transparently, and closing them.

The 4 remaining open items are all actively in progress — peer-review and design-review feedback items being worked right now.

Defects are a normal and expected part of the SDLC. For a workstream of this size — 19 initiatives across two codenames, delivered under compressed timelines with a late-coming scope increase — a 97% closure rate with 60% self-identification demonstrates a team that is engaged, not negligent.

## Proactive actions we've taken

We haven't waited for feedback to act. Based on concerns raised during earlier workstreams (Instalment Plans, Financial Management), we've taken the following proactive steps:

**PR Review Skills**
We've built a `review-pr` skill with rulesets distilled from previous ESG PR feedback and ESG's documented Confluence coding standards. Developers run this manually against their own code using Copilot or Claude, collaborate with the agent on discovered issues, and address as much feedback as possible — while maintaining human oversight on context-sensitive decisions. This is not automated rubber-stamping; it requires deliberate developer engagement.

These rulesets are ready to be translated into documentation referenced from a CLAUDE.md in each relevant repository (as Alex has suggested), which will surface issues during automated PR review as early as possible.

**PR Preparation Tickets (UBT-15591)**
The dedicated Jira tickets were created specifically to distribute the burden of addressing review feedback across the squad rather than routing everything through Martin, Damian and Alex alone. The intent is coordination, not throughput inflation — we're happy to remove or reclassify these if they're creating a misleading impression.

**Collaborative refactoring with Damian**
On the Communications-Hub rules engine, our initial design followed a SOLID Specification-pattern approach (~35 classes, cyclomatic complexity 90-110). We worked directly with Damian to refactor this into a simplified tree-walking evaluator (3 classes, CC 85-95, net -969 lines of code). The contract changed during this work requiring additional code changes and retesting, which we absorbed collaboratively. This is not a team that ignores feedback — it's a team that actively seeks the best outcome.

**Interactive documentation**
We've documented complex areas of the system (particularly the Debt System initiative) with interactive diagrams explaining inner workings for the BA and product owner. These cross-reference areas of the code and assets usable during system test. The BA described the output as excellent.

**Test seed data**
We created the Titanium-Test-Data repository with seed data scenarios enabling developers and testers to iterate quickly on feature testing. This has been invaluable for both sides.

## Addressing the specific concerns

### "16 components for a single dialog"

The actual count is 11 React components, not 16. The modal is a recursive tree editor over a rule DSL (AND/OR/NOT composites, each leaf carrying a path/operator/value triple where input shape varies by operator). This is exactly the use case where component recursion is the correct approach — the alternative would be a single 1,200+ LOC monolith that would be substantially harder to read, test, and maintain.

Of those 11 components, Damian correctly identified 4 that reinvent existing BFE primitives (formik-select, formik-autocomplete, dialog footer pattern). These are being addressed. That's a healthy review outcome — not evidence of a broken process.

### "Removing Lombok annotations and coding in their own style"

We acknowledge this is a gap in codebase style alignment. Our developers review for technical correctness — does the code work, is it logically sound, are edge cases handled? Alignment with ESG's internal conventions (Lombok usage, specific patterns, component reuse) is a separate concern, and one that is harder to catch without codified reference material.

The review-pr skill and the proposed CLAUDE.md adoption directly address this. We want to catch these issues earlier, and we're investing in the tooling to do so.

### "Editing components not related to Debt"

We'll investigate the specific instances raised. In some cases, changes to shared components are a genuine requirement of the feature (e.g. extending a shared utility to support a new use case). In other cases, AI tooling can introduce unintended scope creep if not carefully reviewed. We'll ensure our PR preparation process explicitly checks for unrelated changes.

### "40K lines of front-end code, 50K lines in the Debt Service"

This workstream covers 19 initiatives across Debt Management and Instalment Plans — a substantial volume of genuinely new functionality including a recursive rule editor, a full debt path configuration UI, account management, system workflow, and payment settlement. We'd welcome a discussion about what the expected line count should be for this scope, but absolute numbers without that context can be misleading.

## The branching strategy creates concentrated review burden

The decision to use long-lived feature branches (rather than trunk-based development) was ESG's, made to reduce operational burden during development. The trade-off is that review burden concentrates at the point of merge rather than being spread across smaller incremental commits. What we're experiencing now is that trade-off materialising — not a failure of process.

## On delivery

We are on track for the July release. This includes absorbing a scope increase (additional initiatives pulled forward after we reached dev-complete on the original scope) without timeline relief.

To maintain this trajectory, we need continued PR review from ESG to merge changes to main. We're doing everything we can — through the PR preparation process, the review-pr skill, and self-testing — to ensure that when work reaches ESG reviewers, it's as clean as possible and focused on the more nuanced issues their expertise catches.

## Commitment

Previous feedback has also highlighted good quality in our output — this workstream is not uniformly problematic. Every one of the D55 developers has gone above and beyond, working late and weekends to meet these deadlines. We've addressed feedback comprehensively, including style and nitpick items, because our goal is to deliver good code, on time, that you're happy with.

We intend to keep working closely with Damian and Alex — their input is making the output better, and we value the collaboration.

**Concrete actions:**
1. Adopt CLAUDE.md rulesets in each repository, translating our existing review-pr skill rules into documentation that AI tooling and automated review can consume
2. Continue the PR preparation process — addressing known issues before ESG review
3. Explicitly check for unrelated component changes as part of PR preparation
4. Address the 4 reuse opportunities Damian identified in the rule editor before merge

Happy to discuss any of this further on a call.

Thanks,
Jonathan
