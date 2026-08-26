# Review Summary — PR #462: Contract Note Templates Admin UI

**Overall assessment: Needs discussion / minor changes before merge.**

The feature is high quality — strongly typed, well-tested (24 spec files), consistent
service layer, and clean component lifecycle management. Nothing looks broken. The items
below are mostly about a couple of config/coupling risks and a fragile third-party hack
that are worth resolving or consciously accepting before this lands on `dev`.

---

## Warnings (worth resolving before merge)

### W1 — `ContractNotesApiURL` points at a raw `/ci/` API Gateway stage
`portal/src/environments/environment.ts` (which has `production: true`) adds:
```
ContractNotesApiURL: "https://rks666jjq2.execute-api.eu-west-2.amazonaws.com/ci/"
```
Every other URL in this file uses a branded, environment-appropriate host
(e.g. `admin-api-dev.brytenergy.co.uk`). This one is a raw execute-api URL on a `/ci/`
stage, which reads like a CI/test endpoint left in by accident. Please confirm this is
the intended endpoint for whatever environment this file is deployed to (and that a
custom domain / correct stage isn't expected).

### W2 — `isDevPlaceholderRule` magic sentinel in rules-config
`rules-config.component.ts` treats a rule of literally `EQUALS field="test" value="test"`
as "no rule" and replaces it with an empty editor. This couples the UI to a backend
seeding/placeholder behaviour, and would silently discard a legitimate rule that happens
to compare a field named `test` to `test`. Preferable for the backend to return an empty
body / 404 for "no rule" rather than the UI pattern-matching a sentinel.

### W3 — pdfme "bleed" mechanism is fragile against upstream changes
Two coupled hacks support editing artwork outside page bounds:
- `scripts/patch-pdfme-ui.mjs` string-patches `node_modules/@pdfme/ui/dist/index.js` on
  `postinstall`. With caret ranges (`^6.1.12`) a minor/patch bump can change that source
  and the patch will throw (fail-loud, which is good, but it blocks builds).
- `pdfme-designer.element.ts` scrapes pdfme's Ant Design DOM, reading input labels
  (`x`/`y`/`width`/`height`) to capture bleed positions. This breaks *silently* if pdfme
  changes its DOM structure or localises those labels.

Suggest pinning `@pdfme/*` to exact versions (drop the `^`), and/or adopting
`patch-package` for a more standard, reviewable patch. Consider a small guard/test around
the DOM-scraping so a future pdfme upgrade fails loudly rather than quietly.

---

## Suggestions (non-blocking)

- **S1 — Confirm server-side authz.** The `ContractNoteGroupGuardService` and
  `*appVisibleToGroups` are client-side UI gating only (as the PR description implies).
  Ensure the Contract Notes API independently enforces the `CONTRACT_NOTE_ADMINS` group —
  the guard can be bypassed in the browser.
- **S2 — Dead route config.** `contract-note.routes.ts` sets
  `data: { requiredGroup: CONTRACT_NOTE_ADMIN_GROUP }`, but the guard ignores it and
  hardcodes the constant. Either read `route.data['requiredGroup']` or drop the data.
- **S3 — Two different "unauthorised" destinations.** The outer route in
  `app-routing.module.ts` uses `AuthGuardService` with `redirectTo: 'not-authorized'`,
  while the child module guard redirects to `/contract-notes/access-denied`. Confirm the
  double gating and the differing destinations are intentional.
- **S4 — Rule values are always strings.** `coerceValue` trims to a string, so
  `LESS_THAN` / `MORE_THAN` comparisons are sent as strings even though the model allows
  `number`. If the backend doesn't coerce, numeric comparisons risk lexicographic
  ordering (`"10" < "9"`). Confirm typing expectations.
- **S5 — `postinstall` wipes the whole `.angular` cache** on every install, which slows
  every fresh install / CI run. Consider scoping or gating this.
- **S6 — package-lock (+2714).** Worth a quick sanity check that the added transitive
  footprint is all pdfme-related and expected.

---

## Positives

- Strongly typed domain models: `readonly` throughout, discriminated unions for the
  specification tree (`AndOrNode | NotNode | ComparisonNode | InNode`).
- Thin, consistent, predictable service layer over the REST API.
- Excellent subscription hygiene — `Subscription` aggregation with `unsubscribe()` in
  `ngOnDestroy` across every component; dialog `afterClosed()` subs tracked too.
- Optimistic section reordering with rollback and clear user feedback on failure.
- Safe PDF preview popup handling: window opened synchronously (dodges popup blocker),
  `opener` nulled, `noopener` fallback, `objectURL` revoked after use.
- pdfme wrapped as a self-contained web component with a clean test seam
  (`setPdfmeDesignerLoaderForTesting`) and robust loading/teardown/error states.
- Strong, feature-wide test coverage (24 `.spec.ts` files).

---

## Suggested PR comment

> Reviewed — really solid work overall: strongly typed models, clean service layer,
> great subscription hygiene, and strong test coverage. A few things to confirm before
> merge:
>
> 1. **`ContractNotesApiURL`** in `environment.ts` points at a raw
>    `...execute-api.../ci/` stage while everything else uses branded hosts — is `/ci/`
>    the intended endpoint here?
> 2. **`isDevPlaceholderRule`** pattern-matches a literal `test == test` rule as "no
>    rule". Could the backend return empty/404 instead so the UI doesn't have to guess?
> 3. **pdfme bleed hack**: the `postinstall` patch of `@pdfme/ui/dist` plus the DOM
>    label-scraping in `pdfme-designer.element.ts` are fragile against pdfme upgrades.
>    Suggest pinning `@pdfme/*` to exact versions (and/or `patch-package`).
>
> Non-blocking: confirm the API enforces the `CONTRACT_NOTE_ADMINS` group server-side;
> `requiredGroup` route data is currently unused; rule values are always sent as strings
> (fine for EQUALS/IN, check LESS_THAN/MORE_THAN); and `postinstall` clears the whole
> `.angular` cache on every install.
