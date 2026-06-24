# Draft Response v2

---

Hi Gareth, Darren,

Thank you for documenting these concerns in detail. We take code quality seriously and want to address the points raised with both context and evidence.

## Our process: nothing is being thrown over the fence

We want to be unequivocal on this point: every piece of code D55 delivers has been manually reviewed by a developer before it reaches your team. Nothing is being thrown over the fence. Our delivery process on this workstream:

1. Developer writes code (AI-assisted, as communicated and agreed upfront)
2. PR raised against feature/debt/main; automated feedback addressed
3. Internal D55 peer review prior to merge into feature branch
4. Developer self-testing, defects raised and fixed transparently
5. System testing of each initiative
6. PR preparation: developers review their own work against ESG standards and address known issues before requesting ESG review
7. PR submitted for ESG review
8. ESG feedback addressed
9. Merge to main

There are multiple human review gates before work reaches your team. AI assists with generation; humans review, test, and take accountability for what's delivered.

## The defect data

Across Instalment Plans and Debt Management combined:

| | Total defects | Self-raised by D55 | Found by ESG testers | % Closed |
|---|---:|---:|---:|---:|
| IP | 69 | 44 | 25 | 100% |
| DBT | 58 | 32 | 26 | 93% |
| Combined | 127 | 76 (60%) | 51 (40%) | 97% |

60% of all defects were found and raised by D55 ourselves during internal dev testing and peer review. ESG's system testers identified 51. The team is actively testing its own work, finding issues, raising them transparently, and closing them. A 97% closure rate across 127 defects on a 19-initiative workstream delivered under compressed timelines is a team that is engaged, not negligent.

## What we agreed at kick-off

It's worth revisiting the principles we took away from the original kick-off sessions:

- Pragmatism and "good enough" over perfection, to ensure we deliver on time
- AI to accelerate delivery, communicated upfront and agreed as the approach to meet the timelines
- Reuse existing code where possible. We were not aware there was an expectation to refactor existing code. Where we've copied patterns from existing services, that was done in the spirit of reuse and consistency with what already exists in the codebase.

The current feedback suggests a standard closer to perfection than "good enough" is being applied. We're happy to meet whatever standard is required, but it needs to be consistent with what was agreed and with the timelines we're working to.

## Ticket management

We understand there's been feedback that ESG were too busy to have separate tickets raised for each defect, with a preference instead for single tickets covering multiple defects. We adopted that pattern as requested. We're happy to follow whichever approach you prefer (separate tickets per defect or consolidated tickets) but we need consistency so we know what standard to follow. The PR Preparation tickets (UBT-15591) were created to coordinate work across the squad, not to inflate throughput. Happy to remove or reclassify if preferred.

## Proactive actions we've taken

We haven't waited for feedback to act. Based on concerns raised during earlier workstreams, we've taken the following steps:

PR Review Skills

We built a review-pr skill with rulesets distilled from previous ESG PR feedback and your documented Confluence coding standards. Developers run this manually via Copilot/Claude before requesting ESG review, collaborate with the agent on discovered issues, and address feedback while maintaining human oversight on context-sensitive decisions. This is not automated rubber-stamping; it requires deliberate developer engagement.

These rulesets are ready to be translated into documentation referenced from a CLAUDE.md in each relevant repository (as Alex suggested), surfacing issues during automated PR review as early as possible.

PR Preparation Tickets

Created to distribute the burden of addressing review feedback across the squad rather than routing everything through Martin, Damian and Alex. The intent is coordination, ensuring developers share the initial burden before work reaches ESG reviewers.

Collaborative refactoring with Damian

On the Communications-Hub rules engine, our initial design followed SOLID Specification-pattern principles (~35 classes, cyclomatic complexity 90-110). We worked directly with Damian to refactor this into a simplified tree-walking evaluator (3 classes, CC 85-95, net -969 lines of code). The contract changed during this work requiring additional code changes and retesting, which we absorbed collaboratively. This is not a team that ignores feedback.

Interactive documentation

Complex areas of the system (particularly the Debt System initiative) have been documented with interactive diagrams explaining inner workings for the BA and product owner, cross-referencing code and testable assets. The BA described the output as excellent.

Test seed data

We created the Titanium-Test-Data repository with seed data scenarios enabling developers and testers to iterate quickly on feature testing.

## Addressing the specific concerns

"16 components for a single dialog"

The actual count is 11 React components. The modal is a recursive tree editor over a rule DSL (AND/OR/NOT composites, each leaf carrying a path/operator/value triple where input shape varies by operator). This is standard React composition for tree-shaped UIs, and the alternative would be a single 1,200+ LOC monolith that would be harder to read, test, and maintain.

Of those 11 components, Damian correctly identified 4 that reinvent existing BFE primitives (formik-select, formik-autocomplete, dialog footer pattern). These are being addressed. However, it's worth noting that some of this feedback came before D55's own internal review process had run. Our PR preparation stage would have caught the same reuse issues. Damian's review accelerated the feedback, which is a positive, but it doesn't indicate a missing process.

"Removing Lombok annotations and coding in their own style"

We acknowledge this is a style alignment gap. Our developers review for technical correctness: does the code work, is it logically sound, are edge cases handled? Alignment with ESG's internal conventions (Lombok usage, specific patterns) is harder to catch without codified reference material. The review-pr skill and CLAUDE.md adoption directly address this.

"Editing components not related to Debt"

We'll ensure our PR preparation process explicitly checks for unrelated changes going forward.

"40K lines frontend / 50K lines Debt Service"

This workstream covers 19 initiatives, a substantial volume of genuinely new functionality including a recursive rule editor, full debt path configuration, account management, system workflow, and payment settlement. We'd welcome a discussion about expected proportions, but absolute line counts without scope context can be misleading.

"D55 have been given a greenfield project and copied existing services instead of improving"

We've been asked many times to align our approach with the existing codebase, which is what we did. Copying established patterns from existing services was done in the spirit of consistency and reuse. The suggestion that we should simultaneously have taken the opportunity to refactor and modernise contradicts that guidance. We can't be asked to align with existing patterns and also be criticised for not departing from them. We're happy to discuss the expectation going forward, but it needs to be one or the other.

## The branching strategy

Long-lived feature branches (ESG's decision) were chosen to reduce operational burden during development. The trade-off is that review burden concentrates at the point of merge rather than being spread across smaller trunk-based commits. What's being felt now is that trade-off materialising, not a failure of process.

## Delivery

We are on track for the July release. This includes absorbing a scope increase (additional initiatives pulled forward after we reached dev-complete on the original scope) without timeline relief.

To maintain this trajectory, we need continued PR review from ESG to merge changes to main. We're doing everything we can to ensure work reaching your reviewers is as clean as possible.

## Commitment

Every D55 developer on this workstream has gone above and beyond, working late and weekends to meet these deadlines. We've addressed feedback comprehensively, including style and nitpick items. Previous feedback has also recognised good quality in our output. We intend to deliver good code, on time, that you're happy with.

Damian and Alex's input is making the output better and we value that collaboration. Let's keep it going.

## Next Steps

1. CLAUDE.md adoption: translating review-pr rulesets into each repository for automated/AI-assisted review
2. Explicit unrelated-change checks in PR preparation
3. Address Damian's 4 reuse items in the rule editor before merge
4. Align on ticket management approach: happy to follow whichever pattern you prefer, consistently
5. Continue self-testing and transparent defect raising

Happy to discuss further on a call.

Jonathan
