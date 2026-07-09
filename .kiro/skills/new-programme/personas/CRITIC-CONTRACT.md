# Critic Invocation Contract

How the orchestrator invokes the six critique personas and consumes their results.
This binds the persona rubric files in this folder to the aggregation logic in
`engine/critique.py`.

## Which personas run for which phase

Per the persona → artefact relevance matrix (`engine/critique.py::RELEVANCE_MATRIX`):

| Phase | Artefact | Primary (●● — gates) | Contributing (●) | Light (○) |
|-------|----------|----------------------|------------------|-----------|
| A | Context / positioning | CEO, Marketing, C-Suite | CTO | Mid-Mgmt, Tech |
| B | Dimensions / questions | CTO, Mid-Mgmt, Tech | C-Suite | CEO, Marketing |
| D | Module content | CTO, Mid-Mgmt, Tech | CEO, Marketing, C-Suite | — |
| G | Interactive questionnaire | Marketing, C-Suite | CEO, CTO, Mid-Mgmt, Tech | — |
| H | Elevator pitch | CEO, Marketing, C-Suite | CTO | Mid-Mgmt, Tech |

- `personas_for(phase)` returns primary + contributing (the critics to invoke).
- Only **primary** personas gate the artefact (`primary_thresholds(phase)`):
  internal primary ≥ 4/5, external primary ≥ 3/5.

## Input to each critic sub-agent (`engine/personas.py::CriticInput`)

- `persona` — the persona id (e.g. `d55_cto`).
- `phase` — `A | B | D | G | H`.
- `artefact_paths` — the file(s) the critic must read.
- `programme_context` — short programme framing (positioning, ICP).
- `rubric` — the persona rubric text, loaded from `personas/<persona>.md`.
- `scoring_guidance` — score addressable-in-document quality only (1..5); park
  anything needing a person or a decision, with an owner, and never let a parked
  item reduce the score.

Build one with `CriticInput.build(persona, phase, artefact_paths, programme_context)`,
which loads the rubric from the bundle.

## Output from each critic (`engine/models.py`)

A `CritiqueResult`:
- `phase`, `persona`, `score` (1..5, addressable items only), `verdict`
  (`PASS`/`ITERATE`), `summary`.
- `findings`: a list of `Finding`, each with `severity`
  (`blocker`/`major`/`minor`/`nit`), `disposition` (`addressable`/`parked`),
  `target`, `issue`, `suggestion`, optional `owner` (for parked), and optional
  `dedupe_key` (a normalised signature so the same issue from multiple personas
  collapses to one backlog item).

## Aggregation

The orchestrator collects one `CritiqueResult` per invoked persona and calls
`engine/critique.py::aggregate(results, phase, iteration)` to produce a ranked,
deduped backlog and a `passed` verdict, then `should_continue(history)` to decide
PASS / ITERATE / ESCALATE (max 3 iterations; stall detection). Each round is logged
via `write_critique_log(...)` under `internal/critique/`.
