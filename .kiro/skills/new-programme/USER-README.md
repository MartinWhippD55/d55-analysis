# New Programme — User Guide

A practical guide to running the **New Programme** skill. For the internal design and
engine reference, see `SKILL.md`.

## What it does

Authors a complete, repeatable D55 service *programme* from an idea (and optionally a
client's assessment scores):

- `programme.yaml` manifest (single source of truth)
- assessment dimensions with 1–5 maturity rubrics + questions
- a schema-conformant module library
- per-module branded HTML + PDF deliverables
- an internal Delivery Playbook runbook (spreadsheet)
- a client assessment questionnaire (spreadsheet)
- an interactive radar questionnaire (`workshop.html`)
- an elevator-pitch deck

A six-persona critique loop (CEO, CTO, Marketing, Client C-Suite, Client Middle-Mgmt,
Client Technical) refines each artefact before a human "Happy?" gate.

## Before you start

- **Python + Chromium.** Install the bundle dependencies once:
  ```
  python -m pip install -r requirements.txt
  python -m playwright install chromium
  ```
  (Chromium is only needed for PDF rendering and output verification.)
- **The skill is `inclusion: manual`.** Reference it with `#new-programme` in chat (or
  tell Kiro to use the New Programme skill) so `SKILL.md` is pulled into context.

## Two modes

- **Template mode** — author the canonical, reusable catalog entry (all candidate
  modules, generic content). This is the default; you clone it per client later.
- **Client-instance mode** — a per-engagement clone scoped to one client's assessment
  scores; only the recommended modules get client-specific framing. Never mutates the
  template.

## The flow

Four stages, each critiqued artefact refined by the critique loop *before* its human gate:

1. **Scope & Frame** — programme context (Phase A) → assessment dimensions (Phase B)
2. **Build Modules** — author each in-scope module (Phase D), gate per module
3. **Generate Assets** — per-module HTML+PDF, spreadsheets, interactive questionnaire
   (Phase G), elevator pitch (Phase H)
4. **Verify & Ship** — verify every output, then assemble the client bundle (excludes `internal/`)

At each gate you get the refined artefact plus a critique summary. Answer **No** to
re-refine with your steer, **Yes** to advance.

## Output layout

Default output root is `programmes/<slug>/`:

```
programmes/<slug>/
  programme.yaml, context.md, dimensions.md,
  client-operating-manual-toc.md, working-assumptions.md
  modules/module-{id}-{slug}/{module.md, assets/}
  internal/     Delivery Playbook + critique/ logs   (never shipped)
  client/       questionnaire.xlsx, workshop.html, elevator-pitch.*  (client-facing)
  assets/brand/
  clients/<client-slug>/   per-engagement clones (same layout)
```

The internal Delivery Playbook and critique logs live under `internal/` and are
excluded from the client-facing bundle.

## First run — author the AI-DLC programme (template mode)

The hand-built AI-DLC programme under `analysis/D55/ai-dlc/` is the reference. This run
reconstructs it *through the skill*. Paste this into a fresh Kiro chat:

```
Use the #new-programme skill to author the "AI Development Lifecycle" programme in TEMPLATE mode.

Source material: analysis/D55/ai-dlc/ is the hand-built reference. Use it as the
content source — copy the substance (dimensions, rubrics, questions, module content,
positioning) from:
  - context.md, positioning.md            -> programme context (Phase A)
  - dimensions.md                          -> the 8 assessment dimensions, 1-5 rubrics,
                                             calibration, must-ask/go-deeper questions (Phase B)
  - modules/MODULE-SCHEMA.md + modules/*/module.md -> the 4 modules (Phase D)
  - client-operating-manual-toc.md         -> the manual TOC / manual_section join keys
  - workshop.html, generate_spreadsheets.py -> reference for the interactive tool + spreadsheets

Output root: programmes/ai-dlc/  (bundle default layout: programme.yaml, docs, modules/,
internal/, client/, assets/brand/). Do NOT modify anything under analysis/.

Run it through the skill's four stages with the six-persona critique loop before each
human gate:
  1. Scope & Frame  — context (Phase A) then dimensions (Phase B)
  2. Build Modules  — author each module (Phase D), gate per module
  3. Generate Assets — per-module HTML+PDF, internal Delivery Playbook, client
     assessment questionnaire, interactive workshop.html (Phase G), elevator pitch (Phase H)
  4. Verify & Ship  — verify every output, then note the client bundle (excludes internal/)

Rules to hold to:
  - Validate join keys after scaffolding and hard-stop on any violation.
  - Keep the Delivery Playbook and critique logs under internal/ only.
  - Self-contained outputs (base64, no CDN); the workshop's client-side recommendation
    must match recommend_modules.
  - Capture any pricing/naming/commercial decisions in working-assumptions.md rather
    than inventing them.

Pause at each human "Happy?" gate and show me the refined artefact plus the critique
summary before advancing. Start with Phase A (context) and wait for my go-ahead.
```

## Variant — a client instance

To produce a client-scoped engagement instead, open with this (adjust the scores):

```
Use the #new-programme skill in CLIENT-INSTANCE mode for a client called "Acme".
Assessment scores (current/target, 1-5): Leadership & Mandate 2/4, Developer Tooling
& Adoption 3/5, Specification & Design Process 2/4, Delivery Process & Ceremonies 3/4,
Testing & Quality Assurance 2/4, Governance, Security & Compliance 1/4, Team Adaptation
& Skills 2/3, Metrics & ROI 1/4. Clone from the ai-dlc template and only populate the
recommended modules; write to programmes/ai-dlc/clients/acme/.
```

## Try the bundled example (no chat needed)

The bundle ships a trimmed 2-dimension / 2-module worked example. To generate it end-to-end:

```
python -c "from engine.build_example import build_example; from pathlib import Path; build_example(Path('programmes'), make_pdf=True)"
```

Run from the bundle root (`.kiro/skills/new-programme/`). Outputs land in
`programmes/example/`. Pass an `Assessment` to `build_example(...)` to exercise
client-instance scoping.

## Running the tests

```
python -m pytest tests/ -q
```

Browser/PDF tests skip automatically if Chromium isn't installed. The portability check
copies the bundle outside the repo and runs the example there.

## Notes & working assumptions

- Copy the *patterns* from `analysis/D55/ai-dlc/`, not necessarily the prose verbatim.
- These defaults are working assumptions to confirm with Rhys/Jonathan (the skill records
  provisional decisions in `working-assumptions.md` rather than inventing them): the
  `programmes/<slug>/` output root, the `internal/`/`client/` split, and any
  commercial / pricing / external-naming decisions.

## Troubleshooting

- **PDFs not generated / verification skipped** — Chromium isn't installed:
  `python -m playwright install chromium`.
- **Join-key hard stop** — a module's `dimensions_covered` or `manual_section` doesn't
  match the manifest/TOC exactly. Fix the offending string (exact match) and re-run.
- **Interactive questionnaire recommends differently than the build** — it shouldn't;
  both use the same logic. If you see drift, it's a bug — the parity test guards it.
