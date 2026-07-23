# Reconcile — candidate spec gaps

Flagged during the jira-tree enrichment pass (2026-07-23). Each item is a
cross-reference mismatch or missing detail found while filling issue descriptions from
the story mini-specs and the parent spec (`../../design.md`, `../../requirements.md`).

Where the two disagreed, the tree body was written to match the **parent design** (or
the story mini-spec where noted); the specs themselves were **left unchanged**. Resolve
each at the source, then regenerate/re-enrich the affected issue if needed.

## Open placeholders (intentional `TODO (spec gap)`)

These two `TODO` markers were left deliberately because the spec is silent — they are
the only remaining placeholders in the tree.

- **US-08-1 — Cognito group name.** The exact required Cognito group is not stated
  anywhere. Requirement 15 only says "appropriate Cognito group membership". The guard
  uses a placeholder constant `'contract-note-admins'`. **Needed:** the real group name.
- **US-03-5 — change-log route.** The parent design's Section API endpoint table has no
  dedicated HTTP path for `list-template-changelog`, though the manifest exports it as
  `api-endpoint:template-changelog`. **Needed:** confirm the route (or confirm the change
  log is only returned embedded per template).

## Cross-reference mismatches

- **US-06 wave mismatch.** The story frontmatter and the epic delivery-plan table place
  US-06 in **wave 2**, but its mini-spec (`design.md`/`requirements.md`/`tasks.md`)
  describes it as a **wave-4** story. This originates in `jira-plan.json` / the
  decomposition, so fix it at the source if wave 4 is correct (also affects the epic's
  Delivery-plan table and US-06 `story.md` frontmatter `wave`).
- **US-06-8 requirements coverage.** Sub-task frontmatter `requirements` lists
  11, 12, 13, 14, 19, 20 but its test scope includes Property 34 (pinned-version
  resolution), which the design maps to Requirement 18.6. Consider adding `18`.
- **US-02 get-template response shape.** Parent design (around line 190) says
  `GET /contract-note-templates/{id}` "Returns template with section list"; the US-02
  mini-spec says metadata only (404 if absent). Body filled to the **mini-spec**
  (metadata only). Reconcile whether get-template should embed a section list.
- **US-02 property→requirement annotation.** Parent design annotates Property 8 →
  Requirement 4.3, while the US-02 mini-spec annotates Property 8 → 4.2 and Property 9 →
  4.3. Traceability cleanup only; not body-affecting.
- **US-01 rules route grouping.** The US-01 mini-spec implies a sections-level `rules`
  route; the parent design places the rule under the template path
  (`GET`/`PUT /contract-note-templates/{id}/rule`). CDK snippet written to match the
  **parent design** (`templateId.addResource('rule')`). Confirm the intended grouping so
  US-05 attaches handlers to the path US-01 provisions.
- **US-04 publish changeType.** Publishing records a change-log entry per affected
  template (req 18.4), but the Template Change Log Record `changeType` enum
  (`section-added`, `section-removed`, `section-reordered`, `metadata-updated`,
  `rule-updated`) has no publish value. **Suggested:** add e.g. `section-published`.
- **US-04 / response envelopes.** The design pins item shapes (`SectionReference`;
  validation errors with node paths) but not the enclosing response/error envelope.
  Bodies match the pinned item shapes; wrappers are illustrative. Only a gap if the team
  wants envelope consistency across the API.
- **US-08-2 linked-templates operation.** The US-08 mini-spec lists SectionService
  responsibilities but does not name the `get-linked-templates` operation; the parent
  design does (`GET /contract-note-sections/{id}/linked-templates`, US-04).
  `getLinkedTemplates` was included to match the parent design. Confirm the mini-spec's
  service description should mention it.
- **US-09-8 test requirement coverage.** Sub-task frontmatter `requirements` lists
  1, 10, 18, 19, but the testing strategy calls for SectionEditorComponent
  lifecycle/event tests (Requirement 7), which is absent from the list.

## Naming drift (align terminology)

- **State machine:** `RenderStateMachine` (US-10 mini-spec) vs `render-contract-note` /
  "Render State Machine" (parent design). Bodies use `RenderStateMachine`.
- **Shared-sections screen:** `SharedSectionsComponent` (+ `SharedSectionDetailComponent`)
  in the design vs `frontend-screen:SharedSectionsLibrary` in the manifest/requirements.
  Same screen, two names.
