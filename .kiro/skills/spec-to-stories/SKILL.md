---
inclusion: manual
---

# Spec to Stories

Decompose a spec we built together (`requirements.md` / `design.md` / `tasks.md`,
e.g. under `.kiro/specs/<name>/`) into a set of **mini-specs** — one per user
story — that together deliver the whole spec, wired into a component dependency
graph, topologically ordered into implementation waves, and exported for Jira.

Each mini-spec is a **self-contained Kiro spec**: a developer can copy its folder
into their own `.kiro/specs/` and implement it in isolation, knowing exactly which
components it owns, which it consumes, and which stories must land first.

This is a hybrid skill: a small **deterministic engine** does the graph maths
(build, validate, topological sort, wave layering, Jira export) and the **agent**
does the authoring (reading the parent spec, grouping work into stories, writing
each mini-spec). Read `deliverables-toolkit` only if you also want to produce
client-facing PDFs afterwards — this skill is about developer-facing delivery.

## Self-sufficient bundle

```
.kiro/skills/spec-to-stories/
  SKILL.md                 this file
  requirements.txt         pyyaml, hypothesis, pytest
  engine/
    models.py              Component, Story, SubTask, Edge, Issue, Decomposition
    graph.py               build_decomposition, topological_order, partition_waves, detect_cycles
    manifest.py            read/write per-story manifest.yaml + graph.yaml
    jira_export.py         Jira CSV + JSON (epic / stories / sub-tasks / blocks links)
    build_outputs.py       write graph.yaml, jira-import.*, README.md, per-story manifests
  templates/               manifest + story requirements/design/tasks skeletons
  tests/                   graph engine unit + property tests
```

Run the engine from the bundle root (`python -m pytest`, or import `engine.*`).

## The component model

A **Component** is a unit of software identified by `kind:name`. Recognised kinds
(extensible; use `other` as a fallback):

`data-table`, `gsi`, `s3-bucket`, `api-endpoint`, `lambda`, `state-machine`,
`cdk-construct`, `cdk-stack`, `cdk-instance`, `frontend-component`,
`frontend-screen`, `web-component`, `service`, `type`, `shared-lib`, `other`.

Each **Story** (user story = one mini-spec):
- **exports** the components it creates and owns, and
- **depends on** components another story exports.

An edge `src --depends-on--> dst` means `dst` must be implemented before `src`.
From the edges the engine produces a topological order and **waves** (stories in
the same wave are independent and can run in parallel — the same idea as the wave
blocks in our `tasks.md` files).

## Steps

### 1. Read the parent spec

Read `requirements.md`, `design.md`, `tasks.md`. Inventory the **components** the
design defines:
- Data models / DynamoDB records / tables and GSIs → `data-table:` / `gsi:`
- API endpoint tables → `api-endpoint:METHOD /path` (and `lambda:` handlers)
- Frontend component/service diagrams → `frontend-component:` / `service:`
- Screens / landing pages → `frontend-screen:`
- CDK / infrastructure → `cdk-construct:` / `cdk-stack:` / `state-machine:` / `s3-bucket:`
- Shared types / libraries → `type:` / `shared-lib:`

Build a flat **component registry** first; it is the vocabulary everything else
references. Note the parent requirement ids (for coverage checking).

### 2. Group work into user stories

Slice the spec into vertical, independently valuable stories. Good heuristics:
- Prefer a thin vertical (table + endpoint + screen for one capability) over a
  horizontal layer, where the graph allows — it ships value sooner.
- Keep cross-cutting foundations (shared types, base infra, the state machine
  shell) as their own early story that many others depend on.
- One story should own each component (exactly one exporter). If two stories want
  to own the same component, that's a seam to split or a foundation to extract.

For each story assign: `id` (US-01…), `title`, `userStory`, `coversRequirements`,
`exports`, `dependsOn`, and `subtasks` (lifted from the parent `tasks.md`).

### 3. Build the graph and validate

Construct `Story` objects and call `engine.graph.build_decomposition(parent, stories,
all_requirement_ids=...)`. Inspect the result:
- `dec.ok` must be `True` before generating. Blocking issues:
  - **dangling-dependency** — a `dependsOn` no story exports (fix the ref or add an exporter)
  - **duplicate-exporter** — two stories export the same component (reassign ownership)
  - **self-dependency** — a story depends on what it exports (remove it)
  - **cycle** — mutual dependency (break it: extract a shared `type:`/`shared-lib:`
    story, or invert one direction)
- **uncovered-requirement** is a warning: every parent requirement should be
  covered by at least one story — add coverage or justify the omission.

Iterate on the story grouping until `dec.ok` and coverage is complete.

### 4. Generate the outputs

Call `engine.build_outputs.build_outputs(parent, stories, out_dir, all_requirement_ids)`.
Recommended `out_dir`: `.kiro/specs/<parent>/decomposition/`. It writes:
- `graph.yaml` — component registry, edges, waves, issues
- `jira-import.csv` / `jira-import.json` — epic + stories + sub-tasks + blocks links
- `README.md` — wave plan + a mermaid dependency graph + a story table
- `stories/<id>/manifest.yaml` — the machine manifest per story

### 5. Author each mini-spec (the part only you can do)

For every story folder, write the three spec files from `templates/`:
- `requirements.md` — the covered acceptance criteria, copied/adapted from the
  parent (EARS preserved), each annotated with its parent requirement id.
- `design.md` — the slice of the parent design for this story's components, plus a
  **Touch points** section naming the seams with other stories (the human form of
  the graph edges).
- `tasks.md` — the sub-tasks for this story's components (with parent requirement
  ids), plus the Task Dependency Graph + waves block, and an **Upstream story
  dependencies** list.

Keep it faithful to the parent spec — lift content, don't invent. Mark any inferred
detail as an assumption.

**Format is enforced.** For each story folder to pass Kiro's spec-format checks (so a
developer can pull it straight in), the files MUST have these exact sections (the
templates already include them):
- `requirements.md`: top heading exactly `# Requirements Document`; sections
  `## Introduction`, `## Glossary`, `## Requirements`.
- `design.md`: `## Overview`, `## Architecture`, `## Components and Interfaces`,
  `## Data Models` (required) plus `## Correctness Properties`, `## Error Handling`,
  `## Testing Strategy` (recommended). Under `## Correctness Properties`, each
  property MUST be a `### Property N: Title` heading where **N is a plain integer**
  (no suffixes like `15A`) followed by `**Validates: Requirements X.Y**`. Reuse the
  parent property numbers a story validates. If the section is present it MUST have at
  least one such heading — so for a story with no natural parent property (e.g. pure
  frontend wiring), either **drop the section** or add one **story-local property that
  continues the parent's numbering** (parent had 1–N → use N+1, N+2 …). Do not invent
  a duplicate of an existing parent number.
- `tasks.md`: a `## Task Dependency Graph` with BOTH a mermaid graph and a JSON
  `waves` block, plus `## Overview` and `## Notes`.

### 6. Verify

- Run `python -m pytest` in the bundle (engine correctness).
- Run `getDiagnostics` on every generated `stories/*/{requirements,design,tasks}.md`
  so each mini-spec passes the Kiro spec-format checks (each `tasks.md` needs the
  Task Dependency Graph + JSON waves block — the template includes them).
- Sanity-check the graph: the wave count and edges in `README.md` match the design's
  intent; no story is stranded; totals of covered requirements == parent requirements.

### 7. (Optional) Push to Jira

Once `dec.ok` and the mini-specs are authored and verified, you can create the live
Jira issues (epic → stories → sub-tasks → "blocks" links) directly instead of
importing the CSV by hand. Hand the decomposition folder off to the
**`decomposition-to-jira`** skill (`.kiro/skills/decomposition-to-jira/SKILL.md`):
it builds a deterministic, idempotent plan from `graph.yaml` + the manifests and
creates the issues via the Atlassian Jira MCP (trialling against the `TEST` project
first). This step is optional and only runs on request.

## Correctness properties (engine)

The engine is covered by property tests in `tests/test_graph.py`:
- **P1** every dependency resolves to exactly one exporting story (else an issue)
- **P2** topological order respects every edge (`dst` before `src`)
- **P3** wave integrity: no intra-wave dependency; `wave = 1 + max(dep waves)`
- **P4** cycles are detected and block generation (no waves emitted)
- **P5** determinism: same input → identical edges, order and waves
- **P6** uncovered parent requirements are reported

## Hard rules

- **One exporter per component.** Ownership is singular; shared things become their
  own foundation story that others depend on.
- **`dec.ok` gates generation.** Never write mini-specs while blocking issues exist.
- **Mini-specs stay valid Kiro specs.** Each story folder must pass spec-format
  diagnostics so a developer can pull it straight into their workspace.
- **Faithful decomposition.** Every parent requirement is covered by some story and
  every design component is exported by exactly one story — the union of mini-specs
  must equal the parent spec, no more, no less.
- **Deterministic + traceable.** Keep story ids stable; annotate copied content with
  parent requirement/property numbers so nothing loses its lineage.
