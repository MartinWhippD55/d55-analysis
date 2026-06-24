# D55 Background Context

## Key Points

- The workstream involves a very large amount of change with near-impossible deadlines
- D55 communicated upfront that AI would be leveraged to meet timelines
- Gareth (ESG) stated at the in-person kick-off that the target should be "good enough, not perfection"
- D55 is currently on track for delivery, even with a late-coming scope increase
- The PR Preparation Jira tickets (UBT-15591 etc.) are intentional — raised to track developers reviewing and addressing feedback on long-lived feature branches *before* requesting ESG review
- D55 developers are also self-testing and raising defects against their own work (transparency, not incompetence)
- Long-lived feature branches were ESG's decision — this inherently delays the review burden to the end rather than spreading it across trunk-based commits
- D55 acknowledges ESG review burden but sees it as somewhat unavoidable given the branching strategy chosen

## Additional Context

### "Good enough" agreement
- Gareth stated at in-person kick-off that target should be "good enough, not perfection"
- Not documented anywhere — keep in back pocket, not a primary argument

### Scope increase
- Original deadline: July release
- Once D55 reached dev-complete on original scope, an additional initiative plus reporting work was pulled forward into the same release
- No timeline relief given for the increased scope

### Defects
- Metrics to follow — need to understand how many are pre-release vs post-release

### Comparison to in-house (MHHS vs Instalment Plans)
- Not a like-for-like comparison — likely anecdotal
- D55's PR preparation tickets were created specifically to address this gap

### Martin's role
- Martin = Jonathan (D55 lead), overseeing the squads
- Single point of contact for feedback from ESG leads (Alex, Damian)

### Review turnaround
- ESG feedback has been fast — D55 appreciates Damian's effort and hard work here

### Team composition
- 9 D55 developers, mostly senior
- Developers are reviewing work from a technical correctness standpoint
- Style alignment with ESG codebase is acknowledged as a gap — happy to address
- Distinction: technical correctness vs codebase style conformance — devs focused on former, ESG expecting latter

## D55's Position
- Transparent about AI use (communicated upfront)
- Transparent about defects (self-raising)
- Transparent about rework (dedicated Jira tickets for PR prep)
- On track for delivery despite scope creep and late scope additions
- Working within constraints set by ESG (branching strategy, timelines, scope)
- Acknowledge style issues but distinguish from functional/technical issues
- Appreciate ESG review effort, particularly Damian's

## Response Strategy

### Audience
- Gareth and Darren (ESG)

### Tone
- Conciliatory and collaborative
- Not conceding wrongdoing
- Framing: large workstreams compressed into tight timelines create pressure and frustration on all sides
- Defects are a normal part of SDLC — there shouldn't be an expectation of zero defects

### Key arguments
- The issues raised largely relate to already-merged workstreams (Instalment Plans, Financial Management) — actions have already been taken
- PR Preparation tickets demonstrate D55 proactively addressing feedback before it reaches ESG reviewers
- Self-raised defects show transparency, not failure
- Timeline pressure + scope creep + long-lived branches = concentrated review burden at the end
- Style vs correctness distinction — acknowledge gap, propose concrete action

### Actions to propose
- Adopt Alex's suggestion: extend CLAUDE.md rulesets to codify ESG patterns/style for AI tooling and automated PR review
- This addresses "style conformance" issues at source, earlier in the process
- Frame as collaborative improvement, not admission of fault

### Things NOT to concede
- That D55 has been negligent or careless
- That AI use is inappropriate (it was communicated upfront)
- That defect rates are abnormal given the scope/timeline/pressure

### Waiting on
- ~~Defect metrics (pre-merge vs post-merge breakdown)~~ — RECEIVED (see find-bugs folder)

## Defect Analysis (from find-bugs snapshot 2026-06-24)

### Headlines
| Codename | Total | Closed | Open | % Closed |
|---|---:|---:|---:|---:|
| IP (Instalment Plans) | 69 | 69 | 0 | 100% |
| DBT (Debt Management) | 58 | 54 | 4 | 93% |
| **Combined** | **127** | **123** | **4** | **97%** |

### Origin breakdown (DEV_TEST vs SYSTEM_TEST)
| Codename | DEV_TEST | SYSTEM_TEST |
|---|---:|---:|
| IP | 44 | 25 |
| DBT | 32 | 26 |
| **Combined** | **76** | **51** |

**DEV_TEST** = found internally by D55 developers / peer review (self-raised)
**SYSTEM_TEST** = found by ESG's formal test pass (Gary Cannon, Mike Sanusi, Stacie Cohen, Rebecca Bakewell)

### Key takeaways for the response

1. **60% of all defects (76/127) were self-identified by D55** (DEV_TEST origin). This directly counters the narrative that D55 aren't reviewing their own work — they're finding and raising more defects than ESG's testers are.

2. **97% closure rate** — only 4 defects remain open, and those are actively in progress. This isn't a team ignoring feedback.

3. **IP is 100% closed** — the workstream Darren used as a comparison point (Instalment Plans) is fully resolved.

4. **The open DBT defects** are all peer-review or design-review items (Rebecca's feedback), actively being worked. Not abandoned.

5. **Reporter data is telling**: martin.whipp (you) raised 11 defects. D55's own devs (Alex Johnson: 10, Graeme.Stow: 10, Martin Wetz-Gill: 6, James Ots: 18, paul.martin: 18) account for the bulk. ESG's system testers (Gary: 23, Mike: 26) found 49 between them — less than D55 found internally.

### Narrative for response
The data tells a different story to the one implied in the emails. D55 developers ARE reviewing their work — evidenced by 76 self-raised defects out of 127 total. The team is finding bugs, raising them transparently, and closing them at a 97% rate. The defects ESG's system testers find (51) represent genuine test-phase discoveries, which is the system working as intended.

### Why Martin took the lead on feedback
- To expedite addressing ESG feedback as quickly as possible
- To align code to ESG standards/best practices wherever possible
- D55 recognised the burden on Damian and Alex — the PR Preparation user story and sub-tasks were created specifically to distribute that initial review burden across the squad (not just Martin)
- Happy to remove/delete those Jira tickets if they're perceived as inflating throughput — that was never the intent
- They exist purely for task coordination across the squad

### SDLC Process (actual)
1. Developer writes code (with AI assistance)
2. Raise PR and address automated feedback
3. Internal peer review within D55, prior to merge into feature/debt/main
4. Self-testing, raising defects and addressing with fixes
5. System test of initiative
6. PR preparation tasks (introduced as part of debt epic, to address concerns from previous workstreams)
7. PR submitted for ESG review
8. Feedback addressed
9. Merge to main

### Proactive actions taken
- **review-pr skill**: Built a manual skill (run via Copilot/Claude) with rulesets distilled from previous PR feedback and ESG's documented Confluence coding standards. Developers run it, collaborate with the agent on output, and address feedback while maintaining human oversight. Not automated — requires deliberate developer engagement.
- **Comms-Hub refactor**: Proactively worked with Damian on the rules engine refactor. Initial design was SOLID-orthodox (35 classes, CC 90-110). Collaboratively refactored to tree-walking evaluator (3 classes, CC 85-95, net -969 LOC). Contract changed during this work requiring additional code changes and retesting — D55 absorbed this collaboratively.
- **Interactive documentation**: Documented complex areas (Debt System initiative) with interactive diagrams explaining inner workings for BA and product owner. Cross-referenced code areas and testable assets. BA was delighted with the output.
- **Test seed data**: Created Titanium-Test-Data repository with seed data scenarios enabling developers and testers to quickly iterate on feature testing.

### Delivery status
- On track for July release
- Dependent on ESG PR review to merge changes to main
- Doing everything possible to front-load preparation before ESG review

### Comms-Hub Rules Engine (evidence of collaboration)
- Initial design: ~35 classes, SOLID-orthodox, CC 90-110
- Refactor (with Damian): 3 classes, CC 85-95, -969 LOC net
- Both designs pass per-method complexity budgets
- D55 proposed technically sound design, then willingly refactored to align with ESG's preference for simplicity
- This directly counters the "not listening to feedback" narrative
