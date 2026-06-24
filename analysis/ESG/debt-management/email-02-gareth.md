# Email 2 - From Gareth (ESG)

## Original Email

Hi Jonathan,

As discussed on the call, defect count on recent D55 features has been high, when compared to other similar sized features that have been delivered in-house.

Below is an extract of the notes my Test Manager has provided. Also, here's a handful of examples where we're seeing multiple defects raised on one ticket:
- [UBT-15264] Defect: Debt Load Screen and Stage Steppers - peer review feedback (Rebecca)
- [UBT-15136] Defect: Debt Events and Communications - peer review feedback (Rebecca)

Bizarrely, there's also an issue been raised purely for PR Reviews - [UBT-15591] Debt Management - Pull Request Preparation. This has two dozen sub-tasks raised under it; I'm all for close tracking of work to be done, but this one feels like it should naturally be picked up as part of the SDLC process. It also means D55 throughput will be higher than expected, as you're recording task completion on minimal tasks.

Thanks,
Gareth

### 🏆 Debt Management (~70 issues — largest area)

The biggest cluster by far, covering debt paths, debt controls, stage steppers, debt notes, debt log, and account management suspensions.

**Debt Path Configuration** – can't edit/add/deactivate paths, layout misaligned, debt markers defaulting incorrectly
- UBT-15232, UBT-15305, UBT-15409

**Debt Controls** – status indicator labels wrong, can't edit in-flight controls, history count incorrect
- UBT-15451, UBT-15457, UBT-15511

**Stage Stepper / Debt Load Screen** – Group/Site dropdown not populated, stage status logic, manual suspension cache issues
- UBT-15146, UBT-15264, UBT-15352

**Debt Notes** – filtering, read tracking, last edited date, delete option, layout
- UBT-15258, UBT-15275, UBT-15460

**Debt Log** – CSV export only exports active page, audit table, event publisher implementation
- UBT-15299, UBT-15177, UBT-15459

**Account Management Suspensions** – race conditions, save button enabled incorrectly, API allows empty suspensions
- UBT-15233, UBT-15235, UBT-15283

### 💳 Instalment Plans & Payment Settlement (~43 issues)

Second largest cluster — view plan, DDI, BACS, ringfenced invoices, collection dates.

**IP creation bugs** – remaining balance set to 0, first/last collection dates not saved, weekends not configured
- UBT-15274, UBT-15430, UBT-15417

**Ringfenced invoices** – allocation rows, exclusion from automated strategies, warning icon missing
- UBT-15143, UBT-15144, UBT-15278

**DDI / BACS** – can't create DDI where PTX not active PSP, CollectionProfile errors, DD status not updating
- UBT-15254, UBT-15255, UBT-15357

**View Plan UI** – contacts tab missing primary contact, approval/signed agreement logic, stacked transactions
- UBT-15182, UBT-15485, UBT-15624

Thanks,
Gareth

---

## Summary

Gareth (likely delivery/project lead at ESG) is providing hard defect data to back up the concerns Darren raised qualitatively. This email adds quantitative weight to the argument.

### Key Points

- **~70 defects** in Debt Management alone — the largest cluster
- **~43 defects** in Instalment Plans & Payment Settlement
- **~113 total defects** across these two D55-delivered feature areas
- Defect count is described as "high" compared to similar-sized in-house features
- Multiple defects being raised per ticket (evidence of insufficient testing before handover)
- A dedicated Jira ticket (UBT-15591) created just for "PR Preparation" with two dozen sub-tasks — Gareth flags this as:
  - Work that should be natural SDLC activity, not separately tracked
  - Inflating D55's apparent throughput by logging minimal tasks as completions

### Nature of Defects

The defects aren't edge cases — they're core functionality failures:
- Can't edit/add/deactivate paths
- Dropdowns not populated
- Race conditions
- CSV export only exports current page
- Save buttons enabled when they shouldn't be
- API accepting empty data

These suggest features were delivered without basic functional testing.

---

## Initial Thoughts (D55 Perspective)

### What this adds to the picture
- Darren's email was qualitative (code quality, AI concerns, process). Gareth's is quantitative (113+ defects, specific Jira tickets). Together they build a strong case.
- The defects are not subtle — "can't edit", "dropdown not populated", "remaining balance set to 0" — these would be caught by even basic manual testing
- The PR Preparation ticket (UBT-15591) with 24 sub-tasks is an interesting detail. It suggests D55 may be gaming velocity/throughput metrics by breaking remediation work into many small trackable items

### Concerns for D55's position
- 113+ defects across two feature areas is hard to defend regardless of the AI angle
- The nature of the defects (basic functionality broken) undermines any argument about "different standards" — these are objectively broken features
- The throughput inflation point from Gareth is a separate but related credibility issue

### Things to consider for response
- Are these defects found in QA before release, or post-release? (Matters for severity of the argument)
- What's the contractual agreement around defect rates / acceptance criteria?
- Is there a defined "definition of done" that D55 should be meeting before handover to ESG QA?
- The PR Preparation ticket needs addressing — is D55 genuinely tracking rework, or padding numbers?
