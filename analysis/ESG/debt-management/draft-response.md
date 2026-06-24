# Draft Response - To Gareth & Darren

---

Hi Gareth, Darren,

Thank you both for taking the time to document this in detail — it's appreciated and we want to address the points raised constructively.

First, I want to acknowledge the frustration. This has been a large body of work delivered under significant time pressure, and that creates friction on all sides. The feedback from Damian and Alex has been invaluable, and I want to recognise how much effort they've put into reviewing what are inevitably large PRs given the scope of work.

I'd like to share some context on what we're seeing from our side, and the actions we've already taken and are taking to improve things.

## On code review and AI use

We were upfront at the outset that AI tooling would be leveraged to meet the timelines on this workstream — the scope and deadlines required it. However, I want to be clear: our developers are reviewing the code. The data supports this.

Of the 127 defects raised across Instalment Plans and Debt Management, 76 (60%) were identified and raised by D55 developers themselves during internal dev testing and peer review. ESG's system testers identified 51. This isn't a team blindly merging AI output — it's a team actively testing, identifying issues, and raising them transparently.

As of today, 97% of those defects are closed. Instalment Plans is at 100% closure. The 4 remaining open items in Debt Management are all actively in progress.

## On the PR Preparation tickets (UBT-15591)

These were created deliberately to address exactly the concerns raised. We recognised the burden on Damian and Alex, and rather than routing all feedback through Martin, Damian and Alex, we created sub-tasks to distribute the work of addressing PR feedback across the squad before requesting ESG review.

The intent is coordination, not throughput inflation. We're happy to remove or close these tickets if they're creating a misleading impression — that was never the purpose.

## On style and consistency

I want to draw a distinction between functional correctness and codebase style conformance. Our developers review for technical correctness — does the code work, is it logically sound, are the edge cases handled? The feedback from Damian around patterns, reusable components, Lombok usage, and dialog structure is about alignment with ESG's established conventions.

This is a valid gap and we accept it. When you have 9 developers working at pace on a codebase they haven't built from scratch, there will be divergence from established internal patterns — particularly ones that aren't formally documented.

To that end, we're supportive of Alex's suggestion to extend the CLAUDE.md rulesets. This will codify ESG's patterns and standards in a way that both developers and AI tooling can consume, catching style issues earlier in the process. We'd like to take this as a collaborative action — we can work with Alex and Damian to populate it with the conventions they'd like enforced.

## On defect counts

Defects are a normal part of the SDLC, particularly on a workstream of this size delivered to these timelines. The comparison to in-house features is understandable, but I'd note these are not like-for-like — the Debt Management and Instalment Plans work represents a substantial volume of new functionality delivered under compressed deadlines with a late-coming scope increase (additional initiatives pulled forward into the July release after we reached dev-complete on the original scope).

The important thing is that defects are being found, addressed, and closed — and the majority are being caught before they reach ESG's formal test pass.

## On the long-lived feature branches

The decision to use long-lived feature branches (rather than trunk-based development) was made to reduce operational burden during development. The trade-off is that review burden concentrates at the point of merge rather than being spread across smaller incremental PRs. This is what we're seeing now — and it's a consequence of the branching strategy rather than a failure of process.

## Actions

1. **CLAUDE.md rulesets** — We'll work with Alex and Damian to codify ESG conventions and patterns into the automated review tooling. This addresses the style alignment concerns at source.
2. **PR Preparation tickets** — Happy to close/remove these if they're perceived as inflating throughput. Alternatively, we can reclassify them to make their purpose clearer.
3. **Continued self-testing** — We'll continue the practice of developers testing their own work and raising defects transparently.

We're committed to getting this right and delivering quality work. It's worth noting that previous feedback has also highlighted good quality in our output — this isn't a team that's consistently missing the mark. Every one of the D55 developers has gone above and beyond on this workstream, working late to meet these deadlines. We've addressed as much feedback as we can, including style and nitpick items, because the goal is to deliver good code, on time, that you're happy with.

Let's keep working closely with Damian and Alex — their input is making the output better.

Happy to discuss any of this further on a call if useful.

Thanks,
Jonathan
