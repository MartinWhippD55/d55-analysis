# Jira Tree — user guide

Review and enrich your Jira issues **as local markdown files** before they hit Jira,
then push them when you're happy. It's the editable middle step between the machine
plan (`jira-plan.json`) and live Jira.

## What it does

Given a spec's `jira-plan.json`, it writes a folder that mirrors the Jira hierarchy:

```
jira-tree/
  epic.md            # the Epic
  _links.md          # the "blocks" links between stories
  US-01/
    story.md         # the Story
    US-01-1.md       # a Sub-task
    ...
  US-02/ … US-10/
```

Each file has **frontmatter** (the Jira fields: title, labels, parent, etc.) and a
**markdown body** that becomes the Jira **description**. You edit the bodies to make
the descriptions genuinely useful, review them like any other code change, and then
Kiro pushes the whole tree to Jira.

## Why bother (vs pushing the plan straight to Jira)

The raw plan has thin descriptions and none at all on sub-tasks. The tree gives you a
place to write proper descriptions — with full diff/PR review — before anything is
created. Nothing lands in Jira until you say so.

## Safe by default

- **Your edits are never lost.** Regenerating the tree skips files that already exist,
  and loading reads your edited body verbatim.
- **Validated before push.** Kiro checks the tree is internally consistent (labels
  unique, links resolve, parents match) and refuses to push a broken tree.
- **Idempotent.** Every issue carries a stable label (`s2s-<spec>-US-01`, …). Re-running
  finds and reuses existing issues instead of duplicating them.
- **Sandbox first.** Trials against the `TEST` project before touching a real one like
  `BRYT`, and asks first.
- **No secrets.** The Jira token stays in `.kiro/settings/atlassian.env` (git-ignored).

## Using it

1. Make sure `jira-plan.json` exists for your spec (the **decomposition-to-jira** skill
   produces it; run that first if needed).
2. Ask Kiro to generate the Jira tree. Edit the markdown bodies to enrich descriptions.
3. When you're happy, tell Kiro the target project (start with `TEST`) and ask it to
   push. It validates, creates the epic/stories/sub-tasks/links, and reports the keys.

## Running the engine

From the bundle root:

```
pip install -r requirements.txt      # pyyaml, hypothesis, pytest
python -m pytest                     # engine correctness (round-trip, validation, …)
```

The engine only renders/parses/validates the tree — Kiro makes the actual Jira calls
through the MCP.

## Re-running / cleaning up

Re-running against the same project is safe (idempotent). If you trialled in `TEST` and
want to start over, delete the issues tagged with the set label — search Jira for
`labels = "s2s-<spec>"` — then push again.

## How it fits with the other skills

```
spec-to-stories  →  decomposition-to-jira  →  jira-tree
(decompose a       (build jira-plan.json,     (render an editable mirror,
 spec into          push plan to Jira)          enrich descriptions, then push)
 stories/waves)
```

Use **decomposition-to-jira** when you just want the plan in Jira. Use **jira-tree**
when you want to review and improve the issue descriptions first.
