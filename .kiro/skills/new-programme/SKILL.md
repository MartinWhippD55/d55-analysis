---
inclusion: manual
---

# New Programme (Service Catalog Orchestrator)

> **Placeholder** — the full orchestrator instructions are authored in Task 16.3.
> This file currently documents the bundle's purpose and structure so the skill
> is discoverable while the engine is built out.

## What this skill does

The **New Programme** skill authors a complete, repeatable D55 service *programme*
for the Service Catalog. From a programme idea (and optionally a client's
assessment scores) it produces the full asset set:

- the `programme.yaml` manifest (single source of truth),
- assessment dimensions with 1–5 maturity rubrics,
- a schema-conformant module library,
- per-module branded HTML + PDF deliverables,
- an internal Delivery Playbook runbook spreadsheet,
- an assessment questionnaire spreadsheet,
- an interactive questionnaire (radar chart + recommended modules), and
- an elevator-pitch deck.

Quality is driven by a **six-persona automated critique loop** (CEO, CTO,
Marketing, Client C-Suite, Client Middle-Management, Client Technical) that
refines each artefact before a human review gate.

The skill runs in two modes: **template** (author the canonical, reusable catalog
entry) and **client-instance** (a per-engagement clone scoped to one client's
assessment scores).

## Self-sufficient bundle

This skill is a **self-contained bundle**. Everything it needs is vendored inside
this directory and all paths resolve relative to the bundle root
(`Path(__file__).parent`) — never relative to the repo root or `analysis/`, and
never via hard-coded absolute paths (see `engine/paths.py`).

```
.kiro/skills/new-programme/
  SKILL.md              # this file (orchestrator instructions)
  requirements.txt      # bundle-local Python dependencies
  engine/               # vendored, self-contained engine + path helper
  templates/            # manifest / module / dimensions skeletons
  personas/             # the six critique rubrics
  assets/brand/         # default D55 brand assets (overridable per programme)
  examples/             # a trimmed worked example (patterns, not full prose)
```

## Status

Scaffold only (Task 1). The engine, templates, personas, brand assets, and
worked example are populated by subsequent tasks; the full orchestration
instructions land in Task 16.3.
