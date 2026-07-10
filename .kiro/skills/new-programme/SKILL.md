---
inclusion: manual
---

# New Programme (Service Catalog Orchestrator)

Author a complete, repeatable D55 service **programme** for the Service Catalog.
From a programme idea (and optionally a client's assessment scores) this skill
produces the full asset set — manifest, assessment dimensions, a module library,
per-module branded HTML+PDF, an internal Delivery Playbook, an assessment
questionnaire, an interactive radar questionnaire, and an elevator-pitch deck —
refined by a six-persona critique loop before each human review gate.

This is the **orchestrator**. It decides what to produce and delegates rendering
to the vendored engine. The worked reference is `analysis/D55/ai-dlc/` — read it
for concrete examples of each artefact; copy the **patterns**, not the prose.

## Self-sufficient bundle

Everything this skill needs is vendored here and all paths resolve relative to
the bundle root via `engine/paths.py` — never the repo root, `analysis/`, or an
absolute path. Dependencies are in `requirements.txt` (`openpyxl`, `playwright`,
`pypdf`, `hypothesis`, `pyyaml`); a Python interpreter + Chromium is assumed.

```
.kiro/skills/new-programme/
  SKILL.md              this file
  requirements.txt      bundle-local dependencies
  engine/               vendored engine (see below)
  templates/            manifest / module / dimensions / TOC / questionnaire / pitch skeletons
  personas/             the six critique rubrics + CRITIC-CONTRACT.md
  assets/brand/         default D55 logo + background (overridable)
  tests/                the bundle's own test suite
```

### Engine modules

| Module | Responsibility |
|--------|----------------|
| `paths.py` | Bundle-relative path resolution (portability). |
| `programme_engine.py` | Branded, self-contained HTML + A4 PDF render engine (`BrandConfig`, `build`). |
| `models.py` | Core dataclasses (`Assessment`, `Recommendation`, critique models, `ContractViolation`). |
| `manifest.py` | Load/write `programme.yaml`, parse frontmatter/TOC, `validate_join_keys` (hard stop). |
| `recommend.py` | **The single** `recommend_modules` + `validate_assessment` (build-time and questionnaire share it). |
| `critique.py` | `aggregate`, `should_continue` (PASS/ITERATE/ESCALATE), relevance matrix, thresholds, log writer. |
| `personas.py` | Persona metadata, rubric loading, `CriticInput` invocation contract. |
| `layout.py` | Output layout, modes, internal/client separation, `client_bundle`, client cloning. |
| `scaffold.py` | Instantiate templates + validate join keys. |
| `authoring.py` | Author `dimensions.md` and `module.md` content; client-instance scoping. |
| `module_assets.py` | Render per-module deliverables (branded HTML+PDF starter templates). |
| `spreadsheets.py` | Internal Delivery Playbook + client assessment questionnaire. |
| `questionnaire.py` | Manifest-driven interactive radar questionnaire (parity with `recommend.py`). |
| `pitch.py` | Elevator-pitch deck (gap-tailored in client-instance mode). |
| `verify.py` | Verify HTML (DOM), PDF (pypdf), xlsx (openpyxl); local server cleanup. |
| `orchestrator.py` | Stages, critique loop, human gates, mode handling, working-assumptions register. |

## Modes

- **Template mode** — author the canonical, reusable catalog entry (all candidate
  modules, generic content). Default: maintain the template; clone per client.
- **Client-instance mode** — a per-engagement clone scoped to one client's
  assessment scores. Requires the scores (or run the assessment first); only the
  recommended modules get client-specific framing. Never mutates the template.

`orchestrator.prepare_run` enforces the required inputs and validates the
assessment (1–5 bijection over the manifest dimensions) before anything is built.

## The four stages

Follow `engine/orchestrator.STAGES`:

1. **Scope & Frame** — establish context (Phase A) and dimensions (Phase B).
2. **Build Modules** — author each in-scope module (Phase D), with a gate per module.
3. **Generate Assets** — per-module assets, spreadsheets, interactive questionnaire
   (Phase G), elevator pitch (Phase H).
4. **Verify & Ship** — verify every output; assemble the client bundle.

Each critiqued artefact (phases A, B, D, G, H) runs the autonomous critique loop
*before* its human "Happy?" gate.

## The critique loop (before every gate)

Use `run_phase_with_gate(phase, critique_fn, gate_fn, apply_fixes_fn, revise_fn)`:

1. **Critique** — invoke the relevant personas for the phase
   (`critique.personas_for`; only primary personas gate — see
   `personas/CRITIC-CONTRACT.md`). Each critic returns a `CritiqueResult`.
2. **Aggregate** — `critique.aggregate` dedupes, ranks, splits addressable vs
   parked, and applies the gate (no open blocker; internal primary ≥4, external
   primary ≥3).
3. **Decide** — `critique.should_continue`: PASS → human gate; ITERATE → apply the
   top-K addressable findings via the producer and re-critique; ESCALATE (cap of 3
   or a stalled backlog) → stop and surface open items. Every round is logged to
   `internal/critique/critique-<phase>-<iter>.md`.
4. **Human gate** — present the refined artefact + a critique summary. "No" → take
   the steer and re-refine; "Yes" → advance. Parked items accumulate in
   `working-assumptions.md`.

## Steps

1. **Choose mode** and, for client-instance, take the scores. Call `prepare_run`.
2. **Scaffold** the programme with `scaffold.scaffold_programme` (manifest + docs +
   module skeletons); it validates join keys and hard-stops on drift.
3. **Author dimensions** (`authoring.author_dimensions`) → gate (Phase B).
4. **Author modules** (`authoring.author_modules`; client-instance authors only
   recommended modules) → per-module gate (Phase D).
5. **Generate assets**: `module_assets.generate_module_assets`,
   `spreadsheets.generate_delivery_playbook` (internal),
   `spreadsheets.generate_questionnaire_spreadsheet` (client),
   `questionnaire.generate_questionnaire` (Phase G),
   `pitch.generate_pitch` (Phase H).
6. **Verify** every output with `verify.py`; regenerate any asset that fails and
   re-verify; clean up temp servers.
7. **Ship**: assemble the client bundle with `layout.client_bundle` (excludes
   `internal/`). Write the working-assumptions register (`orchestrator.finalize`).

## Hard rules

- **One recommendation implementation.** `recommend.recommend_modules` is shared by
  build-time scoping and the interactive questionnaire (parity, Property 6). Do not
  fork it.
- **Join keys are a hard stop.** Never generate assets while `validate_join_keys`
  reports violations.
- **Internal vs client separation is structural.** The Delivery Playbook and
  critique logs live under `internal/` and must never land under `client/`.
- **Self-contained outputs.** Embed images as base64; no CDN links (Property 12).
- **Portability.** Resolve everything via `paths.py`; never reach into `analysis/`,
  the repo root, or an absolute path.
- **Capture provisional decisions** in the working-assumptions register rather than
  inventing high-impact (commercial/naming/pricing) content.
