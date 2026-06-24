# Email 1 - From Darren (ESG)

## Original Email

Hi both, I caught up with Alex and Damian recently on some of the concerns they've raised in particular over the quality of code produced by D55. It appears the main issue is D55 developers are using AI to generate code, and it's not being reviewed by humans. A good step would be to enforce that they actually review the code that the AI is generating, because it's clear this is not happening despite being requested multiple times. Damian in particular is getting quite frustrated at repeating himself.

We are working closely with Martin when issues are identified, and Martin generally addresses these concerns and issues with the D55 development team. But, while these issues get resolved, it takes additional development time from both our side and D55, and then the issues happen again on the next feature. This shouldn't really be on Martin, this should be on the developers themselves to address, especially when it's pointed out on a PR.

Here is a summary of some of the issues Damian raised recently:

- Large volumes of code being generated for relatively small pieces of functionality
- Repeated deviations from agreed development standards and testing practices despite previous feedback
- Existing reusable components and patterns are being ignored and reimplemented unnecessarily
- Technical debt is being introduced into new services rather than taking the opportunity to improve and modernise designs
- Leads identify obvious issues within minutes of a review that should have been identified during the D55 peer review
- Liquibase skills added for front-end changes
- Features are requiring repeated rework before reaching an acceptable standard

For comparison, we have a MHHS feature (PR#2925) that was running just as long as the Instalment Plans feature (PR#2907). Yet the MHHS work delivered internally had 2-3 issues, whereas the Instalment Plans had 80 issues, over 300 component changes and took a week of back and forth between Martin and Damian to get to a standard that could be released.

In the recent Debt Management work, there is so much generated code that is really of poor quality. There are 40K lines of front-end code, and 50K lines in the Debt Service, where the D55 developers are editing components not even related to Debt. Damian has flagged how we implement unit tests and API mocks, yet they are still not following our processes. They are changing tests that have nothing to do with Debt, Damian requested that they don't touch components that aren't related to the area they are developing in, yet every time the code is pushed it involves changes to components not related. This is evidence of AI use that is not being reviewed by humans. It looks like they are relying on AI and not even looking at what it's producing.

A particular concern for Damian was with D55 using 16 components for a single dialog, introducing 'dialog footers' when we already have reusable dialogs in other areas of the system they can copy from. Considering D55 have done a lot of front-end work, this again is obvious they are prompting and merging without keeping the code consistent.

Alex reviewed the Debt Service after Damian asked for a second opinion and he confirmed within minutes he could immediately see concerns. We use Lombok annotations and hashCode methods, however D55 have decided to implement code in completely their own style. The more Alex looked into the code, the more it confused him. It looks like they removed the Lombok annotations and exposed the generated code. Alex has said we can address some of these issues by creating a CLAUDE.md file to make it very clear what developers (and AI) should be doing and the patterns they need to follow, but the reality is they really should be reviewing the code themselves before merging code in.

A point Alex made that is a concern is D55 have been given a greenfield project in Debt Management Service, that would have been an opportunity to start fresh and create a clean service that would be clear of technical debt, instead they've copied existing services and not attempted to improve it. There's also some very questionable code in there that Alex feels a large portion will require rewriting in its current state (it's still in draft though so this may change).

The crux of the situation is if they are using AI, then they need to review the code that AI generates. There is too many clear examples where they clearly have not reviewed what they have pushed in to our codebase and it's causing frustration among the team.

Some specific examples:

**Debt Management - Frontend - PR#3038**
- Why are we adding debt path, liquibase skills, docker file changes? .idea workspace?
- Adding reset mocks, changing location of API mocks
- Mocking http client, editing tests and components not related to Debt
- FileService mock, brokers, switch, test field, autocomplete, custom table, time picker
- getGroupReference - functions for a state?
- vi.mock("src/components/forms/form-render") - what is the point of testing if you are mocking the components output? What happens if form render logic changes, the component breaks but you've mocked it so you will never know
- No idea why Liquibase skills added in front-end or changing components that aren't even part of Debt Management, mocking components in tests instead of testing the functionality - all of these things point to AI especially when you review the code and realise nobody would ever code that themselves when you consider we have 3000+ tests, and this is the odd one out.

**UBT-15556 - PR#3047**
- Frontend with 4K lines changed
- Reinventing things like 'dialog footers'

**UBT-15517 - Generic Comms - PR#141**
- Hub 2.6K lines, 71 files
- Invasive, poor quality

**PR#3057 (Damian's refactor)**
- Damian refactoring the Hub after D55 had merged their code in
- Hub 1.1K lines, 21 files
- Much cleaner and consistent with codebase

I hope this helps to clear some of the challenges we are facing up. We are actively working closely with Martin, but again this should be something the rest of the D55 developers are following, rather than repeating the same issues that have been addressed previously.

Thank you, Darren

---

## Summary

Darren has caught up with Alex and Damian (ESG tech leads) regarding concerns over D55 code quality. The core complaint: D55 developers are using AI to generate code and not reviewing it before pushing to PRs.

## Key Issues Raised

### Process Failures
- Code is not being human-reviewed despite repeated requests
- Martin is acting as intermediary to resolve issues, but responsibility should sit with D55 developers
- Same issues recur on every new feature despite prior feedback
- Features require repeated rework before reaching acceptable standard

### Code Quality Concerns
- Large volumes of code for small functionality (40K lines frontend, 50K lines Debt Service)
- Deviations from agreed development standards and testing practices
- Existing reusable components/patterns ignored and reimplemented (e.g. 16 components for a single dialog, new "dialog footers" when reusable dialogs already exist)
- Technical debt introduced into new greenfield service instead of starting clean
- Lombok annotations removed and generated code exposed
- Inconsistent coding style vs established codebase

### Specific Evidence of Unreviewed AI Output
- Editing components unrelated to Debt Management
- Liquibase skills added in frontend changes
- .idea workspace files committed
- Mocking HTTP client and editing unrelated tests
- Mocking component output in tests (defeating the purpose of testing)
- Docker file changes in unrelated PRs

### Comparison Point
- Internal MHHS feature (PR#2925): 2-3 issues
- D55 Instalment Plans (PR#2907): 80 issues, 300+ component changes, week of back-and-forth

## PRs Referenced
- [PR#3038](https://github.com/Utiligroup/Billing-FrontEnd/pull/3038) - Debt Management Frontend
- [PR#3047](https://github.com/Utiligroup/Billing-FrontEnd/pull/3047) - UBT-15556, 4K lines changed
- [PR#141](https://github.com/Utiligroup/Communications-Hub/pull/141) - UBT-15517 Generic Comms, 2.6K lines, 71 files
- [PR#3057](https://github.com/Utiligroup/Billing-FrontEnd/pull/3057) - Damian's refactor post-D55 merge (1.1K lines, 21 files, much cleaner)

## Actions Mentioned
- Alex suggested creating a CLAUDE.md file to make patterns/standards explicit for AI tooling
- ESG working closely with Martin to address issues as they arise
- Darren's position: developers themselves need to review AI output before merging

## Tone
Frustrated but professional. Clear escalation intent. Well-evidenced with specific examples and comparisons.

---

## Initial Thoughts (D55 Perspective)

### What's clear
- The evidence is specific, comparative, and well-documented — this isn't vague complaints
- The MHHS vs Instalment Plans comparison (2-3 issues vs 80 issues) is particularly strong evidence of a quality gap
- The unrelated file changes (Liquibase in frontend, .idea files, unrelated component edits) are classic hallmarks of unchecked AI-generated output
- Damian's refactor (PR#3057: 1.1K lines, 21 files) vs the original D55 output (PR#141: 2.6K lines, 71 files) tells its own story

### Questions to consider for response
- What is D55's contractual obligation around code quality and peer review standards?
- Is this a training/capability gap, or a care/effort gap? The repeated nature suggests the latter
- Martin being the sole point of accountability on D55's side is a structural problem — one person can't fix a team culture issue
- The CLAUDE.md suggestion from Alex is pragmatic but is also an admission that verbal/PR feedback isn't working

### Things to be careful about in response
- "Using AI" isn't inherently the problem — not reviewing output is. The response should acknowledge AI use is fine but unreviewed AI output is not
- Need to separate the technical issues (which are fixable) from the process/culture issues (which are harder)
- Darren is being diplomatic but the subtext is: this is costing ESG real time and money in rework
- The frustration from Alex and Damian is building — there's a retention/morale risk if this isn't addressed
