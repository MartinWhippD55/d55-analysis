---
name: decomposition-to-jira
description: Build an ordered, idempotent jira-plan.json (epic, stories, sub-tasks, blocks-links) from a spec-to-stories decomposition. Stage 2 of the spec-to-Jira pipeline.
inclusion: manual
---

# Decomposition to Jira

Take a decomposition produced by the **spec-to-stories** skill and create the
matching issues in Jira — an **Epic** for the parent spec, a **Story** for each
user story, a **Sub-task** for each sub-task, and **"blocks"** links from the
dependency edges. Runs against a live Jira via the Atlassian MCP.

This is a hybrid skill: a small **deterministic engine** turns the decomposition
into an idempotent creation *plan*; the **agent** executes that plan by calling the
Atlassian Jira MCP (look up first, then create), because only the agent can make
the MCP calls. The engine never touches Jira.

## Self-sufficient bundle

```
.kiro/skills/decomposition-to-jira/
  SKILL.md                 this file
  USER-README.md           user-facing guide
  requirements.txt         pyyaml, hypothesis, pytest
  engine/
    plan.py                load_decomposition, build_plan, write_plan, summarize
  tests/
    test_plan.py           mapping + idempotency-label + determinism tests
```

Run the engine from the bundle root (`python -m pytest`, or import `engine.plan`).

## Prerequisites

- A finished decomposition with `dec.ok: true`, i.e. a folder
  `.kiro/specs/<parent>/decomposition/` containing `graph.yaml` and
  `stories/*/manifest.yaml`. If it does not exist, run **spec-to-stories** first.
- The **Atlassian Jira MCP** connected (tool prefix `mcp_atlassian_jira_*`). Sanity
  check with a read call, e.g. `jira_get_user_profile martin.whipp@d55.co.uk`, before
  writing anything. If disconnected, ensure `.kiro/settings/atlassian.env` holds a
  valid token and reconnect the `atlassian` server from the Kiro MCP panel.
- A **target project key**. Ask the user. Use **`TEST`** (Bryt MSP Project) as the
  safe sandbox for trial runs; only use a real project (e.g. **`BRYT`**) once a trial
  looks right and the user confirms.

## The mapping

| Decomposition | Jira |
|---------------|------|
| parent spec | Epic |
| story `US-xx` | Story under the epic |
| story `subtasks[]` | Sub-task under that story |
| edge `from: src, to: dst` | "Blocks" link: **dst blocks src** (dst ships first) |

**Idempotency** is by stable label. Every planned issue carries an identity label
derived from the parent spec + id: the epic is `s2s-<parent>-epic`, a story is
`s2s-<parent>-US-01`, a sub-task is `s2s-<parent>-US-01-1`. Every issue also gets the
set label `s2s-<parent>`. Before creating an issue, search for its identity label; if
it already exists, reuse the key instead of creating a duplicate. Re-running is safe.

## Steps

### 1. Build the plan (deterministic)

```python
from engine.plan import build_plan, write_plan, summarize
plan = build_plan(".kiro/specs/<parent>/decomposition")
write_plan(plan, ".kiro/specs/<parent>/decomposition/jira-plan.json")
print(summarize(plan))
```

`plan` has `epic`, `stories` (each with `subtasks`), `links`, `waves`, and a
`set_label`. Show the summary and the target project to the user and get a
go-ahead before writing to Jira (writes are **not** auto-approved).

### 2. Confirm the target project and issue types

- Confirm the project key with the user.
- Discover issue types with `jira_get_project_issue_types <PROJECT>`. Note: on some
  team-managed projects this returns empty — if so, fall back to the standard names
  `Epic`, `Story`, `Sub-task`, or inspect an existing issue in the project to learn
  the exact sub-task type name (some instances use `Subtask`). Adapt the
  `issue_type` you pass accordingly.

### 3. Create (or reuse) the Epic

- Search first: `jira_search` with
  `jql = project = <PROJECT> AND labels = "<plan.epic.identity_label>"`.
- If a match exists, reuse its key. Otherwise `jira_create_issue` with
  `issue_type = "Epic"`, `summary = plan.epic.summary`, `description =
  plan.epic.description`, `additional_fields = {"labels": plan.epic.labels}` (Epic
  Name is set from the summary/name on instances that require it).
- Record the epic key.

### 4. Create (or reuse) each Story, then its Sub-tasks

Process stories in `plan.stories` order (it follows the wave/topological order):

1. Search `jql = project = <PROJECT> AND labels = "<story.identity_label>"`.
   Reuse the key if found; else `jira_create_issue` with `issue_type =
   story.issue_type`, `summary = story.summary`, `description = story.description`,
   `additional_fields = {"labels": story.labels, "epic_link": "<epicKey>"}`. If the
   instance rejects `epic_link`, fall back to `jira_link_to_epic(storyKey, epicKey)`.
   If `story.estimate_days` is set and the project has a Story Points field, you may
   add it to `additional_fields`; skip if unknown rather than guessing the field id.
2. For each `subtask` in `story.subtasks`: search by `subtask.identity_label`; reuse
   or `jira_create_issue` with `issue_type = "Sub-task"`, `summary =
   subtask.summary`, `additional_fields = {"parent": "<storyKey>", "labels":
   subtask.labels}`.
3. Keep a map `{story_id -> jira_key}` (and sub-task keys) as you go.

### 5. Make the dependency links

For each `link` in `plan.links` (all are `Blocks`): resolve `link.outward` and
`link.inward` to their Jira keys from step 4, then
`jira_create_issue_link(link_type="Blocks", outward_issue_key=<key(outward)>,
inward_issue_key=<key(inward)>)`. Semantics: **outward blocks inward** — the
dependency (`outward` / edge `to`) blocks the dependent (`inward` / edge `from`).
Skip a link if it already exists (re-fetch the issue's links if unsure) to stay
idempotent.

### 6. Return a summary

Report: the target project, the epic key, the story keys (id → key), the count of
sub-tasks created vs reused, and the links made. Note anything skipped as already
present. Do **not** print secrets.

## Verify

- `python -m pytest` in the bundle (engine correctness — mapping, labels, determinism).
- After a run, spot-check in Jira (or via `jira_get_issue <epicKey>`,
  `jira_search labels = "<set_label>"`) that the epic, stories and sub-tasks exist,
  are linked to the epic, and the blocks-links point dependency → dependent.
- Re-run against the same project and confirm nothing is duplicated (idempotency).

## Hard rules

- **Read before write.** Always sanity-check the MCP with a read call, and always
  search by identity label before creating — never create blind.
- **Sandbox first.** Trial against `TEST` before any real project; only touch a real
  project (e.g. `BRYT`) on explicit user confirmation.
- **Idempotent.** Identity labels are the dedupe key; re-running must not duplicate
  issues or links.
- **Never emit secrets.** The Jira token lives only in `.kiro/settings/atlassian.env`
  (git-ignored). Nothing this skill writes or prints may contain it.
- **Faithful to the decomposition.** One epic, one story per `US-xx`, one sub-task per
  sub-task, one blocks-link per edge — no more, no less.
