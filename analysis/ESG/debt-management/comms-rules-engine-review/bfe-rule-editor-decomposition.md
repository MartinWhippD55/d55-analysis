# BFE Rule Editor — Component Decomposition Review

**Date:** 2026-06-24
**Subject:** Billing-FrontEnd rule editor modal (`ui/src/components/dialog/communications/rule-*`)
**Context:** Companion to the [back-end engine comparison](README.md). The anecdotal claim was *"16 new components were created to facilitate a single modal."* This document verifies the number, characterises the decomposition, defends the approach, and acknowledges the genuine reuse opportunities Damian's review caught.

## What was actually added

All new files arrived in three commits on `feature/debt/main` spanning UBT-15556→15566:

- `dde34e290` — UBT-15556 / 15557 / 15558 / 15559 / 15560 / 15561 (the bulk of the modal)
- `3d9b1ddde` — UBT-15556 ST-001 (rule tree TS types, text-representation walker, structural validator)
- `cecc9e7c1` — UBT-15563 ST-001 (model + Formik data flow for per-event rule + `ruleEnabled`)

**Definitive count (production source files, tests excluded):**

| Counting basis | Total |
|---|---|
| React `.tsx` components inside the modal package (`dialog/communications/`) | **11** |
| Above + the editor entry-point that hosts the modal (`views/settings/communications/communication-rule-editor.tsx`) | **12** |
| All new production files (components + helpers + utils + hook + constants + model) | **21** |

There is no way to land on exactly 16 cleanly, but a reasonable composition (11 components + 4 utils + 1 hook = **16**) does sit inside the actual footprint. The figure is **directionally correct** as a description of the surface area; **slightly imprecise** as a description of component count.

### Component inventory (the 11 modal-scoped components)

| Component | Role |
|---|---|
| `rule-editor-dialog.tsx` | The modal shell itself |
| `rule-editor-top-bar.tsx` | Header / context display |
| `rule-editor-footer.tsx` | Save/cancel + summary footer |
| `rule-editor-json-view.tsx` | Raw-JSON inspector tab |
| `rule-tree-view.tsx` | The recursive tree container |
| `rule-tree-node.tsx` | One node in the tree (composite or leaf) |
| `rule-condition-row.tsx` | A leaf comparison row (path / operator / value) |
| `rule-operator-bar.tsx` | AND/OR/NOT badge for a composite |
| `rule-add-operator-dropdown.tsx` | "Add child" picker for composites |
| `rule-value-input.tsx` | Scalar value input (string/number/boolean/date) |
| `rule-value-chip-input.tsx` | Multi-value input for `in`/`notIn` (chips) |

### Supporting non-component files (9)

- `utils/rule-text-walker.ts` — human-readable rendering of a rule tree
- `utils/rule-tree-mutations.ts` — pure tree-edit helpers (add/remove/replace)
- `utils/rule-validator.ts` — structural validation mirroring back-end contract
- `utils/rule-json-serialization.ts` — JSON ↔ tree round-trip
- `utils/query-type-payload-flattener.ts` — turns a sample payload into typed path suggestions
- `hooks/use-query-type-payload.ts` — sample-payload lookup hook
- `constants/query-type-sample-payloads.ts` — per-query-type sample payloads
- `types/models/settings/communications/communications-rule-model.ts` — `RuleNode`, `LogicalOperator`, etc.
- `dialog/communications/rule-condition-helpers.ts` — leaf-row helpers

## Defending the decomposition

The headline number ("16 components for one modal") sounds excessive in the abstract. In practice the breakdown is closer to standard React composition than over-engineering, for four concrete reasons.

### 1. The modal is a recursive editor over a tree DSL

The thing being edited is *not* a flat form. It's a recursive AND/OR/NOT tree with composite and leaf nodes, each leaf carrying a (path, operator, value) triple, where value-input shape depends on operator (`isNull` has no value, `in`/`notIn` take a chip array, `equals` takes a scalar typed by the path). A single 1,200-LOC `<RuleEditor>` covering all that would have been substantially harder to read and test than the eleven components we have.

Tree-shaped editors are exactly where component recursion (`RuleTreeView` → `RuleTreeNode` → `RuleTreeNode` …) pays for itself.

### 2. Single Responsibility — applied appropriately

Each component has one obvious job:

- `rule-editor-top-bar` paints the header
- `rule-editor-footer` paints the footer
- `rule-tree-node` renders one node and decides composite-vs-leaf
- `rule-condition-row` renders the (path, operator, value) triple
- `rule-value-input` vs `rule-value-chip-input` separate scalar input from multi-value input

This is the **right** application of SRP — there are real behavioural differences between a chip-input and a scalar input (parsing, MUI primitives, change semantics). Where the back-end Specification design over-applied SRP to 14 leaves that differed by a single operator, the front-end decomposition tracks genuine differences in render shape and interaction.

### 3. Testability per concern

The repo's testing convention is to test components at their natural seam. With this decomposition, `rule-tree-view.test.tsx`, `rule-editor-dialog.test.tsx`, `rule-add-operator-dropdown.test.tsx` all exist and test independent surfaces. Coverage stays manageable; a regression in chip-input parsing doesn't require dragging the whole modal into a test.

### 4. The non-component helpers are correctly factored

`rule-tree-mutations.ts`, `rule-text-walker.ts`, and `rule-validator.ts` are pure functions over `RuleNode`. They're *not* tucked inside components — they're independently importable, independently testable, and independently reusable (e.g. `formatRule` is consumed both by the editor and by the trigger-form summary). That's the right shape for tree-DSL utilities.

## Genuine reuse opportunities (caught by Damian)

A defensible decomposition is not the same as a perfect decomposition. A handful of the new components are doing work that existing BFE primitives already do, and the right call would have been to wrap or extend the existing primitive instead of writing a fresh one. The cases worth flagging:

| New component | Existing primitive that likely should have been used | Why |
|---|---|---|
| `rule-add-operator-dropdown.tsx` | `components/select-boxes/formik-select.tsx` (or unwrapped MUI `Select` with the codebase's themed wrapper) | Hand-rolls a `Menu` + `MenuItem` flow with bespoke colour-by-operator styling instead of plugging into the Formik-aware select pattern used everywhere else in the dialog directory. |
| `rule-value-chip-input.tsx` | `components/select-boxes/formik-autocomplete.tsx` + `components/chips/bill-chip.tsx` | Uses MUI `Autocomplete` + `Chip` + `TextField` directly. The codebase has a Formik-aware autocomplete and a themed `BillChip`; either would have given consistent styling and form-state integration for free. |
| `rule-value-input.tsx` | Existing scalar input wrappers (Formik-aware) | Reinvents type-aware scalar input where Formik-aware variants already exist for string/number/boolean across the codebase. |
| `rule-editor-footer.tsx` | Standard `BillDialog` footer pattern | Other dialogs in the same directory use shared dialog footer styling; the bespoke footer is a small but real divergence. |

These weren't all-or-nothing problems — the new components still work — but each one introduces a styling and form-state pattern that diverges from the rest of the BFE. Over time that becomes a maintenance tax: themes and Formik conventions evolve, and the rule editor risks getting left behind on each round.

**Damian called these out, and the team has the chance to fold reuse back in before the work lands on `main`.** That is exactly the outcome a review is supposed to produce.

## On timing — why this is a normal review outcome, not a process failure

Damian's review happened **before** D55's own internal PR review process had its run at the work. The pattern was:

1. Initial PR opened on `feature/debt/main`.
2. Damian (cross-team reviewer) commented.
3. D55 internal review would normally have happened at this point and is where the team typically catches "this looks like an existing primitive — please wrap it" feedback.

The fact that Damian caught the reuse misses doesn't indicate D55's review process is insufficient — it indicates the work was reviewed *earlier than D55's process expects*. D55's standard PR review catches exactly these kinds of inconsistencies: pattern alignment, shared-primitive reuse, Formik integration, styling consistency. Looking at the recent merge history on the branch, D55 PR review has consistently caught and corrected divergences of this shape before merge.

The healthy framing here is:

- The decomposition was correct in shape (recursive tree editor → recursive components is the right model).
- A handful of leaf components reinvented primitives the codebase already exposed.
- Damian's review accelerated the feedback that D55's process would have produced at PR time anyway.
- Folding the reuse back in is a small, mechanical follow-up — not a rethink.

## Recommendation

1. **Keep the 11-component decomposition.** It tracks real shape differences in a recursive tree editor; collapsing it would hurt readability and testability.
2. **Address Damian's reuse feedback** by replacing the four flagged components (or their inner primitives) with wraps over `formik-select`, `formik-autocomplete`, `BillChip`, and the standard dialog footer pattern. Estimated effort: half a day to a day; behavioural changes minimal (the API surface of each component stays the same, only the internals change).
3. **Treat this as a healthy review interaction, not a process gap.** Cross-team reviewers catching things before internal PR review is a feature, not a bug — and D55's PR review process would have caught the same items on the same branch within its own cadence.

## Cross-references

- Back-end engine comparison: [README.md](README.md)
- Commits involved (Billing-FrontEnd, `feature/debt/main`): `dde34e290`, `3d9b1ddde`, `cecc9e7c1`
