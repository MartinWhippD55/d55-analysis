# Jira Push — user guide

Push your reviewed **Jira tree** into live Jira — the epic, stories, sub-tasks and
their "blocks" links — in one go, safely and without duplicates. It's the last step
after you've enriched the descriptions with **jira-tree**.

## What it does

Given the `jira-tree/` folder for a spec (the editable markdown mirror), it:

1. Loads and validates the tree.
2. Builds an ordered **push plan** — epic first, then each story with its sub-tasks,
   then the links.
3. Checks what already exists in Jira and **reconciles** — anything already there is
   reused/skipped, not recreated.
4. Creates the missing issues and links, and reports every key.

Your enriched markdown bodies become the Jira **descriptions**, so all the work you
put into the tree lands in Jira.

## How it fits with the other skills

```
spec-to-stories  →  decomposition-to-jira  →  jira-tree      →  jira-push
(decompose a        (build jira-plan.json)     (edit an           (push the reviewed
 spec into                                      editable mirror,    tree to live Jira)
 stories/waves)                                 enrich descriptions)
```

- **decomposition-to-jira** — push the raw machine plan straight to Jira (thin
  descriptions). Fastest path, no review.
- **jira-tree** — render an editable mirror and improve the descriptions first.
- **jira-push** — take that reviewed mirror and create it in Jira. Use this once the
  tree reads the way you want.

## Safe by default

- **Idempotent.** Every issue carries a stable label (`s2s-<spec>-US-01`, …) and every
  link is matched by its story pair. Re-running finds and reuses what's already there
  instead of duplicating.
- **Validated before push.** Refuses to push a tree or plan that isn't internally
  consistent (labels unique, parents before children, links resolve).
- **Sandbox first.** Trials against the `TEST` project before touching a real one like
  `BRYT`, and asks first. Writes are never auto-approved.
- **No secrets.** The Jira token stays in `.kiro/settings/atlassian.env` (git-ignored).

## Using it

1. Make sure the `jira-tree/` folder exists and is enriched the way you want (run
   **jira-tree** first if not).
2. Make sure the Atlassian Jira MCP is connected.
3. Tell Kiro the target project (start with `TEST`) and ask it to push. It validates,
   shows you a plan summary, and — once you confirm — creates the epic, stories,
   sub-tasks and links, then reports the keys.
4. Want to be sure it's safe to re-run? Ask Kiro to run it again — the summary should
   show everything as *reuse*/*skip* and create nothing new.

### Optional: attach the mini-specs to each story

If you want each story issue to carry its authoritative mini-spec (`requirements.md`,
`design.md`, `tasks.md` from `decomposition/stories/US-xx/`), ask Kiro to **attach the
specs** when pushing. It's **off by default** and deduped by filename, so re-running
won't pile up duplicates.

Worth knowing: the attached files are the *source* the story description was derived
from, so they can drift from the description over time — the repo copy stays the source
of truth. Use it when people working in Jira need the full spec without repo access.

## Running the engine

From the bundle root:

```
pip install -r requirements.txt      # pyyaml, hypothesis, pytest
python -m pytest                     # engine correctness (planning, reconcile, validation)
```

The engine only plans and reconciles — Kiro makes the actual Jira calls through the
MCP.

## Cleaning up a trial

If you trialled in `TEST` and want to start over, delete the issues tagged with the set
label — search Jira for `labels = "s2s-<spec>"` — then push again.
