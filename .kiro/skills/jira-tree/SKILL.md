---
inclusion: manual
---

# Jira Tree

Turn a spec-to-stories decomposition into an **editable filesystem mirror** of the
Jira issue hierarchy — an `epic.md`, a `story.md` per user story, a file per
sub-task, and a `_links.md` of the cross-story "blocks" links — then **iterate on the
content locally** and **push it to Jira** once you're happy.

This is the review-and-enrich step between `jira-plan.json` and live Jira.
`decomposition-to-jira` pushes the auto-generated plan straight to Jira with thin
descriptions; **jira-tree** inserts a human-editable surface first: each issue's
markdown body *is* its Jira description, so you can enrich, diff and review it in a PR
before anything lands.

Like its siblings this is a **hybrid skill**: a small **deterministic engine** renders
/ parses / validates the tree; the **agent** pushes the parsed tree to Jira via the
Atlassian MCP (look up first, then create). The engine never touches Jira.

## Self-sufficient bundle

```
.kiro/skills/jira-tree/
  SKILL.md                 this file
  USER-README.md           user-facing guide
  requirements.txt         pyyaml, hypothesis, pytest
  engine/
    tree.py                build_tree_from_plan, write_tree, load_tree,
                           validate_tree, find_placeholders, summarize, load_plan
  templates/
    epic.md.tmpl           canonical Epic description shape + house style
    story.md.tmpl          canonical Story description shape + house style
    subtask.md.tmpl        canonical Sub-task description shape + house style
  tests/
    test_tree.py           seed mapping, round-trip, non-destructive write,
                           validation, placeholders, determinism (property-based)
```

Run the engine from the bundle root (`python -m pytest`, or import `engine.tree`).

## Where the tree lives

Default location, alongside the decomposition it mirrors:

```
.kiro/specs/<parent>/decomposition/jira-tree/
  epic.md            _links.md          README.md
  US-01/ story.md + <US-01-n>.md ...    US-02/ ...
```

Folder nesting *is* the parent/child hierarchy: epic at root, each story a folder,
sub-tasks leaf files inside it. Sub-tasks are named by key (`US-01-1.md`) so they sort
naturally.

## The mapping

| Tree | Jira |
|------|------|
| `epic.md` | Epic |
| `<US-xx>/story.md` | Story under the epic |
| `<US-xx>/<US-xx-n>.md` | Sub-task under that story |
| `_links.md` entry `outward -> inward` | "Blocks" link: **outward blocks inward** (outward ships first) |

**Frontmatter = Jira fields, body = description.** Frontmatter carries `issue_type`,
`summary`, `identity_label`, `labels`, and (per type) `parent`/`parent_epic`,
`requirements`/`covers_requirements`, `estimate_days`, `wave`, `depends_on`, `blocks`,
`optional`. The markdown **body** is the issue description, read verbatim on load.

**Idempotency** is by stable identity label, copied straight through from the plan:
epic `s2s-<parent>-epic`, story `s2s-<parent>-US-01`, sub-task `s2s-<parent>-US-01-1`,
plus the set label `s2s-<parent>` on everything. A push searches the identity label
before creating, so re-running never duplicates. This matches `decomposition-to-jira`
exactly.

## Description templates & house style

Each issue type has a canonical description shape in `templates/*.md.tmpl`.
`build_tree_from_plan` **seeds bodies in these shapes** and leaves clearly-marked
`TODO` placeholders where content must be enriched. The templates are the reference
an author or sub-agent targets.

**House style — clear and easy to read (borrowed from ultra-terse writing, minus the
persona):**

- Lead with substance. No preamble, no hedging, no "this task involves…".
- Short sentences and bullets. Spell things out; do not invent abbreviations.
- Keep code, API names, CLI commands and error strings **verbatim**.
- Expand where order or ambiguity matters — never compress a multi-step sequence into
  a fragment that could be misread.

**Per type:**

- **Epic** — Goal · Background · Scope · Delivery-plan table · Story index · Definition
  of done. The delivery plan and story index are seeded from the plan (we have all
  stories + waves); goal/background/scope are placeholders.
- **Story** — user-story line → Description → Delivers → **Acceptance criteria in
  Given/When/Then** → Dependencies (named `US-xx — summary`) → Traceability. User
  story, dependencies and traceability are seeded; description, delivers and AC are
  placeholders.
- **Sub-task** — greppable **What / Why / Done-when** bullets, then a **Suggested
  approach** code fence (a small, honest starting point a developer can run with:
  handler stub, CDK snippet, request/response JSON, component mock). `What` and
  requirement refs are seeded; `Why`, `Done-when` and the snippet are placeholders.
  An API response shape here should match the OpenAPI spec, and a component mock should
  match its backing endpoint — mismatches surface gaps in the parent spec.

### Optional: enrich with a sub-agent

After seeding, an optional sub-agent pass can fill the placeholders — most usefully the
sub-task **Suggested approach** snippets and story **acceptance criteria** — by reading
the spec's `design.md`/`requirements.md`, any OpenAPI spec, and (if pointed at one) an
associated code repository. Have it replace `TODO` markers only, preserve frontmatter
and identity labels, and flag any cross-reference mismatch (e.g. a mock whose shape
disagrees with the OpenAPI response) as a candidate spec gap. Re-run `validate_tree`
and `find_placeholders` afterwards.

## Prerequisites

- A `jira-plan.json` for the spec (produced by **decomposition-to-jira**'s
  `build_plan`/`write_plan`) at `.kiro/specs/<parent>/decomposition/jira-plan.json`.
  If it doesn't exist, run **decomposition-to-jira** step 1 first.
- For the push: the **Atlassian Jira MCP** connected (tool prefix
  `mcp_atlassian_jira_*`). Sanity-check with a read call
  (`jira_get_user_profile martin.whipp@d55.co.uk`) before writing anything. If
  disconnected, ensure `.kiro/settings/atlassian.env` holds a valid token and
  reconnect the `atlassian` server from the Kiro MCP panel.
- A **target project key**. Ask the user. Trial against **`TEST`** (Bryt MSP Project)
  before any real project (e.g. **`BRYT`**), and only on explicit confirmation.

## Steps

### 1. Generate the tree from the plan (deterministic, non-destructive)

```python
from engine.tree import load_plan, build_tree_from_plan, write_tree, summarize
plan = load_plan(".kiro/specs/<parent>/decomposition/jira-plan.json")
tree = build_tree_from_plan(plan)
written = write_tree(tree, ".kiro/specs/<parent>/decomposition/jira-tree")  # overwrite=False
print(summarize(tree), f"— wrote {len(written)} new files")
```

`write_tree` **skips files that already exist** (`overwrite=False` default), so
regenerating never clobbers hand-edited descriptions. Only pass `overwrite=True` to
deliberately reset a file to its seeded content.

### 2. Iterate locally

Enrich the markdown **bodies** to the house style above — replace every `TODO`
placeholder (acceptance criteria, delivers, suggested-code snippets, notes). Leave
frontmatter and identity labels intact. Optionally run the **sub-agent enrichment**
pass to draft the snippets and criteria. Commit and review in a PR like any other file
— this is the whole point of the tree.

### 3. Load and validate before pushing

```python
from engine.tree import load_tree, validate_tree, find_placeholders, summarize
tree = load_tree(".kiro/specs/<parent>/decomposition/jira-tree")
problems = validate_tree(tree)
assert not problems, problems
todos = find_placeholders(tree)   # soft check: any un-enriched TODO placeholders
print(summarize(tree), f"— {len(todos)} issues still have TODO placeholders")
```

`validate_tree` returns `[]` when the tree is internally consistent. It flags: missing
/ malformed / duplicate identity labels; a story whose `parent_epic` doesn't match the
epic; `blocks`/`depends_on`/link endpoints that don't resolve to a known story;
sub-task `parent` mismatches; `optional` flag vs `optional` label disagreements; and
any disagreement between `_links.md` and the per-story `blocks:` frontmatter. **Do not
push a tree with problems** — fix them first.

`find_placeholders` is a **soft** check — it lists issues whose body still has a `TODO`.
It doesn't block a push, but surface the count to the user: pushing placeholder text
into Jira is rarely intended. Show the summary + placeholder count + target project and
get a go-ahead (writes are **not** auto-approved).

### 4. Confirm the target project and issue types

- Confirm the project key with the user (sandbox `TEST` first).
- Discover issue types with `jira_get_project_issue_types <PROJECT>`. On some
  team-managed projects this returns empty — if so, fall back to the standard names
  `Epic` / `Story` / `Sub-task`, or inspect an existing issue for the exact sub-task
  type name (some instances use `Subtask`). Adapt the `issue_type` you pass.

### 5. Create (or reuse) the Epic

- Search first: `jira_search` with
  `jql = project = <PROJECT> AND labels = "<tree.epic.identity_label>"`.
- Reuse the key if a match exists; otherwise `jira_create_issue` with
  `issue_type = "Epic"`, `summary = tree.epic.summary`,
  `description = tree.epic.description` (the markdown body),
  `additional_fields = {"labels": tree.epic.labels}`.
- Record the epic key.

### 6. Create (or reuse) each Story, then its Sub-tasks

Process `tree.stories` in order (wave/topological). For each story:

1. Search `jql = project = <PROJECT> AND labels = "<story.identity_label>"`. Reuse if
   found; else `jira_create_issue` with `issue_type = story.issue_type`,
   `summary = story.summary`, `description = story.description`,
   `additional_fields = {"labels": story.labels, "epic_link": "<epicKey>"}`. If the
   instance rejects `epic_link`, fall back to `jira_link_to_epic(storyKey, epicKey)`.
   If `story.estimate_days` is set and the project has a Story Points field you can
   add it; skip rather than guessing the field id.
2. For each `subtask` in `story.subtasks`: search by `subtask.identity_label`; reuse
   or `jira_create_issue` with `issue_type = "Sub-task"`, `summary = subtask.summary`,
   `description = subtask.description`, `additional_fields = {"parent": "<storyKey>",
   "labels": subtask.labels}`.
3. Keep a map `{story_key -> jira_key}` (and sub-task keys) as you go.

### 7. Make the dependency links

For each `link` in `tree.links` (all `Blocks`): resolve `link.outward` and
`link.inward` to Jira keys from step 6, then `jira_create_issue_link(link_type=
"Blocks", outward_issue_key=<key(outward)>, inward_issue_key=<key(inward)>)`.
Semantics: **outward blocks inward** — the dependency ships first. Skip a link that
already exists (re-fetch the issue's links if unsure) to stay idempotent.

### 8. Return a summary

Report the target project, the epic key, the story keys (key → Jira key), sub-tasks
created vs reused, and links made. Note anything skipped as already present. Do **not**
print secrets.

## Verify

- `python -m pytest` in the bundle (engine correctness — seed mapping, round-trip,
  non-destructive write, validation, placeholders, determinism).
- `load_tree` then `validate_tree` on the real tree must return `[]` before a push;
  `find_placeholders` should ideally be empty (or the remaining `TODO`s are intended).
- After a push, spot-check in Jira (or `jira_get_issue <epicKey>`,
  `jira_search labels = "<set_label>"`) that the epic, stories and sub-tasks exist,
  descriptions match the edited bodies, stories link to the epic, and blocks-links
  point dependency → dependent.
- Re-run against the same project and confirm nothing is duplicated (idempotency).

## Format note

Jira stores descriptions as ADF/wiki markup, not markdown. The Atlassian MCP converts
the markdown body on create, so headings, lists and tables render; mermaid blocks and
exotic markdown may not. The tree is a human-review mirror, not a byte-for-byte Jira
export.

## Hard rules

- **Round-trip safe.** `load_tree` reads the body verbatim as the description; edits
  are never lost. `write_tree` is non-destructive by default — never clobber edits.
- **Validate before push.** A tree with `validate_tree` problems must not be pushed.
- **Read before write.** Sanity-check the MCP with a read call, and always search by
  identity label before creating — never create blind.
- **Sandbox first.** Trial against `TEST`; only touch a real project on explicit
  user confirmation.
- **Idempotent.** Identity labels are the dedupe key; re-running must not duplicate
  issues or links.
- **Never emit secrets.** The Jira token lives only in `.kiro/settings/atlassian.env`
  (git-ignored). Nothing this skill writes or prints may contain it.
- **Faithful.** One epic, one story per `US-xx`, one sub-task per sub-task, one
  blocks-link per edge — no more, no less.
