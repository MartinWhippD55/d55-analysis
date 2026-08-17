# Handoff — push the DocuSign decomposition to Jira

_Last updated: 2026-08-17. Purpose: let a fresh session run the final pipeline step
(**jira-push**) for the `contract-note-docusign-integration` decomposition without
re-deriving context._

## TL;DR

Everything local is **done and verified**. The only remaining step is the **live Jira
push**, which is **gated on explicit user go-ahead** and must trial against the **`TEST`**
sandbox first (writes are NOT auto-approved). Follow `.kiro/skills/jira-push/SKILL.md`.

## Pipeline state

```
spec-to-stories ✅ → decomposition-to-jira ✅ → jira-tree ✅ → jira-push ⬜ (this handoff)
```

- **spec-to-stories** — 8 stories, 4 waves, `ok: true`, all 12 parent requirements
  covered. 24 mini-spec files under `stories/US-01..US-08/` pass `getDiagnostics` clean.
  Reviewed and approved by the user.
- **decomposition-to-jira** — `jira-plan.json` built: **1 epic, 8 stories, 25 sub-tasks,
  14 blocks-links**. Link direction verified (outward=dependency ships first, blocks inward).
- **jira-tree** — editable mirror at `decomposition/jira-tree/` (35 files), fully enriched
  (Given/When/Then AC, delivers, sub-task What/Why/Done-when + grounded code snippets).
  `validate_tree` → `[]`; `find_placeholders` → `0`.
- Engine test suites all passing at last run: spec-to-stories 11, decomposition-to-jira 7,
  jira-tree 14. Re-run jira-push's suite (should be 25) before pushing.

## Artifacts (all under `.kiro/specs/contract-note-docusign-integration/decomposition/`)

- `graph.yaml`, `README.md` — the decomposition + wave plan + mermaid graph
- `jira-plan.json` — the idempotent plan (source for the tree)
- `jira-import.csv` / `jira-import.json` — raw CSV/JSON export (not needed for the push)
- `stories/US-01..US-08/{manifest,requirements,design,tasks}.md` — the mini-specs
- `jira-tree/` — the reviewed mirror to push: `epic.md`, `US-xx/story.md`,
  `US-xx/US-xx-n.md`, `_links.md`

## The stories & waves (for a sanity read)

| Wave | Stories |
|------|---------|
| 1 | US-01 (foundation), US-07 (Estimate 1 metadata surfacing — cross-team / Jabez) |
| 2 | US-02 (Salesforce client), US-03 (DocuSign client), US-04 (metadata service) |
| 3 | US-05 (Send Envelope Lambda), US-06 (Webhook Lambda) |
| 4 | US-08 (integration wiring & deployment) |

## Identity labels (idempotency keys — carried through unchanged)

- Set label on everything: `s2s-contract-note-docusign-integration`
- Epic: `s2s-contract-note-docusign-integration-epic`
- Story: `s2s-contract-note-docusign-integration-US-01` … `-US-08`
- Sub-task: `s2s-contract-note-docusign-integration-US-01-1` …

A push searches these labels first and reuses matches, so re-running never duplicates.

## How a fresh session should resume

1. **Read** `.kiro/skills/jira-push/SKILL.md` (manual-inclusion skill) and this file.
2. **Sanity-check the MCP with a read** before any write:
   `jira_get_user_profile martin.whipp@d55.co.uk`. If disconnected, ensure
   `.kiro/settings/atlassian.env` holds a valid token (git-ignored — never print it) and
   reconnect the `atlassian` server from the Kiro MCP panel.
3. **Confirm the target project with the user.** Trial against **`TEST`** (Bryt MSP
   Project) first; only touch a real project (e.g. `BRYT`) on explicit confirmation.
4. **Load + validate + plan** (engine, no Jira writes yet):
   ```python
   from engine.push import load_tree_view, build_push_plan, validate_plan, summarize_plan, reconcile
   tree, probs = load_tree_view(".kiro/specs/contract-note-docusign-integration/decomposition/jira-tree")
   assert not probs, probs
   plan = build_push_plan(tree)
   assert not validate_plan(plan), validate_plan(plan)
   print(summarize_plan(reconcile(plan)))   # dry summary — show the user, get go-ahead
   ```
5. **Confirm issue types.** `jira_get_project_issue_types TEST` has historically returned
   `[]` (team-managed / permissions). If so, fall back to the standard names
   `Epic` / `Story` / `Sub-task`, or inspect an existing issue for the exact sub-task type
   name (some instances use `Subtask`).
6. **Reconcile against what exists** (search `labels = "s2s-contract-note-docusign-integration"`),
   then **execute** epic → each story then its sub-tasks → links, per the SKILL steps 3–5.
7. **Rewrite cross-references** (SKILL step 6): bodies mention sibling stories as `US-xx`;
   after all issues exist, rewrite descriptions to real Jira keys and write
   `jira-tree/_placeholders.md`. Optional but recommended.
8. **Verify + prove idempotency**: spot-check in Jira, then re-run the whole skill and
   confirm `summarize_plan` shows all `reuse`/`skip` — nothing new created.

## Open decisions for the user (relay before pushing)

- **Target = `TEST` sandbox** for the trial? (recommended first). Real project after a
  clean trial + idempotency re-run.
- **Attach mini-specs to stories?** Off by default. `attach_specs(plan, ".../stories")`
  adds each story's `requirements/design/tasks.md` as attachments. Opt-in only — it's a
  traceability aid that can drift; the repo copy stays canonical.
- **SQP cleanup (unrelated):** the Estimate 1 trial left issues under label
  `s2s-contract-note-template-management` — a *different* label, so **no collision** with
  this push. Clean up only if the user asks.

## Gotchas / notes

- Writes are **not** auto-approved (`autoApprove: []` in `mcp.json`); every create needs
  user approval.
- Never emit the Jira token; it lives only in `.kiro/settings/atlassian.env`.
- Cosmetic: bare `US-02`-style text in a description gets auto-linked by Jira to a
  non-existent `/browse/US-02`. The step-6 cross-reference rewrite replaces these with
  real keys; harmless if left.
- **Nothing is committed yet.** The entire `decomposition/` folder (mini-specs + tree +
  plan) is **untracked on `main`**. Consider committing it before/after the push so the
  reviewed tree is captured in git.
