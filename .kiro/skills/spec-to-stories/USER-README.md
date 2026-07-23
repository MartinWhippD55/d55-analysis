# Spec to Stories — user guide

Turn a spec (`.kiro/specs/<name>/`) into a set of mini-specs — one per user story —
with a dependency graph, a parallelisable implementation order, and a Jira import.
Each mini-spec is a self-contained Kiro spec a developer can pull into their own
workspace.

## What you get

Written to `.kiro/specs/<parent>/decomposition/`:

| Output | What it is |
|--------|-----------|
| `graph.yaml` | Component registry (component → owning story), dependency edges, waves, issues |
| `jira-import.csv` | Jira CSV importer file: an Epic, a Story per user story, Sub-tasks, and "blocks" links from the dependency edges |
| `jira-import.json` | The same, as JSON, for scripted creation via the Jira REST API |
| `README.md` | Human summary: the wave plan, a mermaid dependency graph, and a story table |
| `stories/<id>/` | A self-contained mini-spec (`manifest.yaml` + `requirements.md` + `design.md` + `tasks.md`) |

## How it decides the order

Each story declares the **components** it creates (`exports`) and needs
(`dependsOn`). A component is `kind:name` (e.g. `data-table:Templates`,
`api-endpoint:GET /templates`, `frontend-screen:TemplateList`, `cdk-construct:RenderStateMachine`).
The engine links each dependency to the story that exports it, checks for problems
(dangling dependencies, two stories owning one component, cycles), then topologically
sorts the stories into **waves** — stories in the same wave are independent and can
be built in parallel.

## Running the engine

From the bundle root:

```
pip install -r requirements.txt      # pyyaml, hypothesis, pytest
python -m pytest                     # engine correctness (unit + property tests)
```

The agent uses the engine (`engine/build_outputs.build_outputs(...)`) after grouping
the parent spec into stories; see `SKILL.md` for the full workflow.

## Pulling a story into a developer workspace

Copy `stories/<id>/` into your `.kiro/specs/`. It has `requirements.md`,
`design.md`, `tasks.md` (a valid Kiro spec) plus `manifest.yaml` telling you which
components it owns, which it consumes, and — via `../../graph.yaml` — which stories
must be delivered first.

## Pushing to Jira

Import `jira-import.csv` via Jira's external-system CSV importer: map `Issue Type`,
`Summary`, `Epic Link`, `Parent Id` (for sub-tasks), `Labels`, `Story Points`, and
build issue links from the `Blocks` column. Or drive the REST API from
`jira-import.json`.
