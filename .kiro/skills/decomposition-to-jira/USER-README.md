# Decomposition to Jira — user guide

Push a **spec-to-stories** decomposition into Jira as live issues: an Epic for the
spec, a Story per user story, a Sub-task per sub-task, and "blocks" links from the
dependency graph. Uses the Atlassian Jira MCP, so it creates real issues rather than
a CSV you import by hand.

## What it does

Given `.kiro/specs/<parent>/decomposition/` (from spec-to-stories):

| Decomposition | Becomes in Jira |
|---------------|-----------------|
| parent spec | Epic |
| story `US-xx` | Story under the epic |
| each sub-task | Sub-task under that story |
| dependency edge | "Blocks" link (the upstream story blocks the downstream one) |

## Safe by default

- **Reads before it writes.** It checks the MCP is connected and looks up existing
  issues before creating anything.
- **Idempotent.** Every issue is tagged with a stable label (`s2s-<parent>-US-01`,
  etc.). Re-running finds those labels and reuses the issues instead of making
  duplicates.
- **Sandbox first.** It trials against the `TEST` project (Bryt MSP Project) before
  touching a real project like `BRYT`, and asks before doing so.
- **No secrets.** The Jira API token stays in `.kiro/settings/atlassian.env` (which is
  git-ignored). Nothing the skill writes or prints contains it.

## Using it

1. Make sure you have a decomposition with `ok: true` (run spec-to-stories if not).
2. Tell Kiro the target Jira project key (start with `TEST`).
3. Kiro builds a plan, shows you a summary (how many issues and links), and creates
   them once you confirm. It reports the epic key, story keys, and links made.

## Running the engine

From the bundle root:

```
pip install -r requirements.txt      # pyyaml, hypothesis, pytest
python -m pytest                     # planner correctness (mapping, labels, determinism)
```

The planner (`engine/plan.py`) only builds the deterministic plan — Kiro makes the
actual Jira calls through the MCP.

## Re-running / cleaning up

Re-running against the same project is safe (idempotent). If you trialled in `TEST`
and want to start over, delete the issues tagged with the set label — search Jira for
`labels = "s2s-<parent>"` — then run again.
