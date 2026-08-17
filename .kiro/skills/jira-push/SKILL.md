---
name: jira-push
description: Push a reviewed jira-tree mirror to live Jira — epic, stories, sub-tasks, and blocks-links — idempotently via the Atlassian MCP. Stage 4 of the spec-to-Jira pipeline.
inclusion: manual
---

# Jira Push

Take a reviewed, enriched **Jira tree** (the editable markdown mirror produced by the
**jira-tree** skill) and create the matching issues in **live Jira** — an Epic, a
Story per user story, a Sub-task per sub-task, and the cross-story "blocks" links.
Idempotent: re-running never duplicates anything.

This is the final step of the pipeline:

```
spec-to-stories → decomposition-to-jira → jira-tree → jira-push
(decompose)        (build jira-plan.json) (edit an        (push the reviewed
                                           editable mirror) tree to live Jira)
```

Like its siblings this is a **hybrid skill**: a small **deterministic engine** turns
the loaded tree into an ordered, idempotent *push plan* and reconciles it against what
already exists in Jira; the **agent** executes that plan by calling the Atlassian Jira
MCP (look up first, then create), because only the agent can make MCP calls. The
engine never touches Jira.

Why a separate skill from jira-tree? **jira-tree** owns authoring — generate, enrich,
validate the mirror. **jira-push** owns delivery — plan, reconcile and execute the
push. Splitting them keeps each focused and lets the push logic (ordering, reuse/skip
reconciliation) be unit-tested without a tree generator or a live Jira.

## Self-sufficient bundle

```
.kiro/skills/jira-push/
  SKILL.md                 this file
  USER-README.md           user-facing guide
  requirements.txt         pyyaml, hypothesis, pytest
  engine/
    push.py                build_push_plan, attach_specs, reconcile,
                           validate_plan, summarize_plan, load_tree_view,
                           build_key_map, substitute_keys,
                           plan_description_updates, render_placeholder_doc
  tests/
    test_push.py           mapping, ordering, idempotency (reconcile),
                           validation, determinism (property-based),
                           key substitution + placeholder map
```

Run the engine from the bundle root (`python -m pytest`, or import `engine.push`).
`load_tree_view` reuses the sibling **jira-tree** engine to read a tree from disk, so
the tree format has a single source of truth.

## The mapping

| Tree | Jira |
|------|------|
| `epic.md` | Epic |
| `<US-xx>/story.md` | Story under the epic |
| `<US-xx>/<US-xx-n>.md` | Sub-task under that story |
| `_links.md` entry `outward -> inward` | "Blocks" link: **outward blocks inward** (outward ships first) |

**Frontmatter = Jira fields, markdown body = the issue description.** The body is
pushed verbatim as the description, so all your local enrichment lands in Jira.

**Idempotency** is by stable identity label, carried straight through from the tree:
epic `s2s-<parent>-epic`, story `s2s-<parent>-US-01`, sub-task `s2s-<parent>-US-01-1`,
plus the set label `s2s-<parent>` on everything. Links dedupe by their
`(outward, inward)` story pair. A push searches identity labels first and reuses
matches, so re-running is safe. This matches `decomposition-to-jira` and `jira-tree`
exactly.

## Prerequisites

- A **validated Jira tree** on disk at
  `.kiro/specs/<parent>/decomposition/jira-tree/` (produced and enriched by
  **jira-tree**). If it doesn't exist, run **jira-tree** first.
- The **Atlassian Jira MCP** connected (tool prefix `mcp_atlassian_jira_*`).
  Sanity-check with a read call (`jira_get_user_profile martin.whipp@d55.co.uk`)
  before writing anything. If disconnected, ensure `.kiro/settings/atlassian.env`
  holds a valid token and reconnect the `atlassian` server from the Kiro MCP panel.
- A **target project key**. Ask the user. Trial against **`TEST`** (Bryt MSP Project)
  before any real project (e.g. **`BRYT`**), and only on explicit confirmation.

## Steps

### 1. Load and validate the tree, then build the push plan

```python
from engine.push import load_tree_view, build_push_plan, validate_plan, summarize_plan, reconcile

tree, tree_problems = load_tree_view(".kiro/specs/<parent>/decomposition/jira-tree")
assert not tree_problems, tree_problems          # jira-tree's own validation must be clean

plan = build_push_plan(tree)
assert not validate_plan(plan), validate_plan(plan)   # plan-structure invariants
print(summarize_plan(reconcile(plan)))                # dry summary (nothing found yet)
```

`plan.issues` is ordered **epic → (story, its sub-tasks) → …** and `plan.links` holds
the blocks-links. Every action starts as `create`. `validate_plan` guarantees the epic
is first, parents precede children, identity refs are unique, and link endpoints are
known stories. **Do not push a plan with problems.**

> Optional soft check: run **jira-tree**'s `find_placeholders(tree)` — pushing bodies
> that still contain `TODO` markers into Jira is rarely intended. Surface the count.

Show the summary + target project to the user and get a go-ahead (writes are **not**
auto-approved).

> **Optional — attach each story's mini-spec (opt-in, off by default).** If the user
> wants the authoritative mini-spec files on each story issue, call `attach_specs`:
>
> ```python
> from engine.push import attach_specs
> plan = attach_specs(plan, ".kiro/specs/<parent>/decomposition/stories")
> #                          ^ sibling of jira-tree/; each US-xx/ has requirements.md,
> #                            design.md, tasks.md
> ```
>
> This adds an `AttachmentAction` per existing spec file to each **story** action
> (epics and sub-tasks are never given attachments). Only do this when asked — it is a
> **traceability aid, not the source of truth**: the attached files are what the story
> body was derived from and can drift from it (see `jira-tree`'s `reconcile.md`). The
> repo/git copy remains canonical.

### 2. Confirm the target project and issue types

- Confirm the project key with the user (sandbox `TEST` first).
- Discover issue types with `jira_get_project_issue_types <PROJECT>`. On some
  team-managed projects this returns empty — if so, fall back to the standard names
  `Epic` / `Story` / `Sub-task`, or inspect an existing issue for the exact sub-task
  type name (some instances use `Subtask`). Adapt the `issue_type` you pass.

### 3. Discover what already exists (reconcile)

Search Jira for everything carrying this push's set label, so a re-run reuses instead
of duplicating:

- `jira_search` with `jql = project = <PROJECT> AND labels = "<plan.set_label>"`.
  Collect the identity label(s) on each returned issue and its Jira key into a map
  `existing_key = {identity_label -> jira_key}`.
- Gather existing links: for stories already present, read their issue links
  (`jira_get_issue <key> include=... ` or the links section) and collect the
  `(outward_key, inward_key)` pairs already linked.
- **If attachment mode is on:** for each story already present, read its existing
  attachment filenames (`jira_get_issue <key> fields="attachment"`) into
  `existing_attachments = {story_key -> {filename, ...}}`, so already-uploaded specs
  are skipped.

Then reconcile:

```python
plan = reconcile(
    plan,
    existing_labels=set(existing_key),          # identity labels already in Jira
    existing_links=existing_link_pairs,          # {(outward_key, inward_key), ...}
    existing_attachments=existing_attachments,   # {story_key -> {filename}}; omit if not attaching
)
print(summarize_plan(plan))   # issues create/reuse, links create/skip, attachments upload/skip
```

Every issue action is now `create` or `reuse`; every link is `create` or `skip`; every
attachment is `create` (upload) or `skip`.

### 4. Execute the issue actions in order

Walk `plan.issues` **in list order** (epic first, each story before its sub-tasks):

- **`reuse`** — the issue exists; take its key from `existing_key[action.ref]` and
  record it in a `key_of = {identity_label -> jira_key}` map. Create nothing.
- **`create`** — call `jira_create_issue`:
  - **Epic**: `issue_type = action.issue_type` (`"Epic"`),
    `summary = action.summary`, `description = action.description`,
    `additional_fields = {"labels": action.labels}`.
  - **Story**: `issue_type = action.issue_type`, `summary`, `description`,
    `additional_fields = {"labels": action.labels, "epic_link": key_of[action.parent_ref]}`.
    If the instance rejects `epic_link`, fall back to
    `jira_link_to_epic(storyKey, epicKey)`. If `action.estimate_days` is set and the
    project has a Story Points field you can add it; **skip rather than guessing** the
    field id.
  - **Sub-task**: `issue_type = "Sub-task"`, `summary`, `description`,
    `additional_fields = {"parent": key_of[action.parent_ref], "labels": action.labels}`.
  - Record the new key in `key_of[action.ref]`.
- **Attachments (if any):** after a story exists (created or reused), upload each
  `action.attachments` entry whose `op == "create"` via
  `jira_update_issue(<storyKey>, attachments=[att.source_path, ...])`. Entries marked
  `skip` are already on the issue — do nothing. Uploading the same filename twice
  creates a duplicate in Jira, so **only upload `create` entries** — this is why the
  reconcile in step 3 reads existing attachment filenames.

`action.parent_ref` is the parent's **identity label**; resolve it through `key_of`
(populated as you go — the ordering guarantees the parent was handled first).

### 5. Execute the link actions

For each `link` in `plan.links` with `op == "create"`: resolve `link.outward` and
`link.inward` story keys to Jira keys (via `key_of` and the story `ref`s, or the
`existing_key` map), then
`jira_create_issue_link(link_type="Blocks", outward_issue_key=<key(outward)>,
inward_issue_key=<key(inward)>)`. Semantics: **outward blocks inward** — the
dependency ships first. Links marked `skip` already exist; do nothing.

### 6. Rewrite cross-references to real Jira keys (placeholder → key)

The tree bodies refer to each other by **tree key** — "blocked by US-03", "the render
pipeline (US-06)", "variant rules (US-04-3)". Pushed verbatim (step 4) those stay as
`US-xx` strings in Jira instead of the real, clickable issue keys. Once every issue
exists you know the mapping, so rewrite the descriptions and push them again.

You already hold `key_of = {identity_label -> jira_key}` from steps 3–4 (the
`existing_key` map plus every key you created). Turn it into a tree-key map, snapshot
it to disk, and build the update actions:

```python
from engine.push import (
    build_key_map, plan_description_updates, render_placeholder_doc,
)

key_map = build_key_map(key_of, plan.set_label)   # {US-04 -> JIRA-KEY, US-04-2 -> ...}

# snapshot the correlation next to the tree (human + machine readable); handy to
# review, and lets a later run reload the map without re-querying Jira.
open(f"{tree_dir}/_placeholders.md", "w", encoding="utf-8").write(
    render_placeholder_doc(plan, key_of, project_key=PROJECT)
)

updates = plan_description_updates(plan, key_map, key_of)
```

`substitute_keys` (used inside) only rewrites whole-token references and refuses to
touch a `US-xx` that is flanked by a word char or hyphen — so identity labels printed
in a body (`…-US-04`) survive intact and `US-04` inside `US-04-2` is never partially
rewritten (longer keys win). It is idempotent: re-running over already-rewritten text
is a no-op because `JIRA-KEY` doesn't match the `US-<n>` shape.

Then push **only the changed** descriptions:

```python
for u in updates:
    if u.changed:
        # jira_update_issue(u.jira_key, fields={"description": u.description})
        ...
```

Skipping `changed == False` keeps the pass a no-op on a tree with no cross-references
and avoids needless writes. This step is optional but recommended when the bodies
cross-reference each other.

> **Placeholder-first variant (up-front keys).** Instead of pushing full bodies then
> rewriting, you can create **thin placeholder issues** in step 4 (summary + labels
> only), write `_placeholders.md`, then run this rewrite so the *first* real
> description already carries live keys — one create pass, one update pass. The engine
> is the same; only the ordering differs. Either way `_placeholders.md` is a scratch
> correlation, safe to delete once descriptions are finalised.

### 7. Return a summary

Report: the target project, the epic key, the story keys (`US-xx → JIRA-KEY`),
sub-tasks created vs reused, links created vs skipped, descriptions rewritten (if the
cross-reference pass ran), and (if attachment mode was on) spec files uploaded vs
skipped. Note anything reused/skipped as already present. Do **not** print secrets.

## Verify

- `python -m pytest` in the bundle (engine correctness — mapping, ordering,
  reconcile idempotency, validation, determinism).
- `load_tree_view` must return `[]` problems and `validate_plan(plan)` must be `[]`
  before any push.
- After a push, spot-check in Jira (or `jira_get_issue <epicKey>`,
  `jira_search labels = "<set_label>"`) that the epic, stories and sub-tasks exist,
  descriptions match the edited bodies, stories link to the epic, and blocks-links
  point dependency → dependent.
- **Re-run the whole skill against the same project** and confirm `summarize_plan`
  after reconcile shows all `reuse`/`skip` and nothing new is created (idempotency).

## Format note

Jira stores descriptions as ADF/wiki markup, not markdown. The Atlassian MCP converts
the markdown body on create, so headings, lists and tables render; mermaid blocks and
exotic markdown may not. The tree is a human-review mirror, not a byte-for-byte Jira
export.

## Hard rules

- **Read before write.** Sanity-check the MCP with a read call, and always search by
  identity label before creating — never create blind. Reconcile first.
- **Validate before push.** A tree with `load_tree_view` problems, or a plan with
  `validate_plan` problems, must not be pushed.
- **Sandbox first.** Trial against `TEST`; only touch a real project (e.g. `BRYT`) on
  explicit user confirmation. Writes are not auto-approved.
- **Idempotent.** Identity labels (issues), `(outward, inward)` pairs (links) and
  filenames (attachments) are the dedupe keys; re-running must not duplicate issues,
  links or attachments. Jira does not dedupe attachments by name — only upload
  `create` entries after reconciling against existing filenames.
- **Attachments are opt-in.** Only attach mini-specs when the user asks. They are a
  traceability aid that can drift from the reviewed description; the repo copy is
  canonical.
- **Never emit secrets.** The Jira token lives only in `.kiro/settings/atlassian.env`
  (git-ignored). Nothing this skill writes or prints may contain it.
- **Faithful.** One epic, one story per `US-xx`, one sub-task per sub-task, one
  blocks-link per edge — no more, no less. Push the tree as reviewed; don't invent
  content at push time.
