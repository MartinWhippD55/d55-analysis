# Draft Response (Final)

---

Hi Gareth, Darren,

Thank you for raising these concerns. I want to cut to the heart of this.

## The real issue

We are delivering 19 initiatives under near-impossible deadlines, with a late scope increase absorbed without timeline relief. That volume of change, compressed into this window, creates pain on all sides: for your reviewers, for our developers, and for the relationship. We feel that too.

But the pain doesn't mean the process is broken.

## Three things that need saying

1. We are reviewing our code.

Every line is manually reviewed before it reaches your team. Nothing is thrown over the fence. 60% of all defects (76 out of 127) were found and raised by D55 ourselves. We're catching more issues than your system testers. That is not a team blindly merging AI output.

2. ESG's conventions aren't written down.

The style divergences being flagged (Lombok, dialog patterns, component reuse) are real. But they live in people's heads and past PRs, not in codified documentation. We can't consistently hit a target we can't see. The CLAUDE.md approach Alex suggested fixes this, and we've already built the rulesets to populate it. We'll adopt this immediately.

3. The expectations are contradictory.

At kick-off we agreed: pragmatism over perfection, AI to accelerate, reuse existing patterns. We've since been told to align with the existing codebase (which we did), and simultaneously criticised for not modernising it. We can't be asked to follow existing patterns and also be criticised for not departing from them. We need one clear standard.

## What we've done

- Built PR review skills encoding your standards, ready to become CLAUDE.md
- Self-tested and raised 76 defects transparently
- Refactored the rules engine collaboratively with Damian (35 classes to 3, -969 LOC)
- Created documentation, diagrams, and test seed data to help everyone move faster
- Created PR preparation tickets to spread the review burden across our squad before it reaches yours
- Every developer has worked late and weekends to hit this deadline

It's also worth noting that some of the feedback referenced in these emails came before D55's own internal review process had run. Our PR preparation stage would have caught the same issues. Where ESG reviewers have engaged early, that's accelerated the feedback loop, which is a positive. But it shouldn't be read as evidence that our process is absent.

## What we need

- A codified style standard (CLAUDE.md), and we'll help build it
- Consistent expectations on ticket management (we were told separate tickets weren't wanted, now consolidated tickets are questioned)
- Continued PR review from ESG to merge to main. We're on track for July but can't stay there without it

## Bottom line

The volume and timeline created this friction, not negligence, not carelessness, and not a lack of review. We care about this code. The data proves it. Let's fix the structural issues (codified standards, clear expectations) so we're not having this conversation again on the next workstream.

## Next Steps

1. CLAUDE.md adoption in each repository, translating our existing review-pr rulesets
2. Align on a single ticket management standard. Your call, we'll follow it consistently.
3. Address the 4 reuse items Damian identified in the rule editor before merge
4. Continue collaborative working with Damian and Alex through the final merge to main

Happy to discuss on a call.

Jonathan
