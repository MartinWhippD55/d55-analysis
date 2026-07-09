# Requirements Document

*New Programme Skill (Service Catalog)*

## Introduction

The **New Programme** skill is a Kiro orchestrator skill that authors a complete, repeatable D55 service *programme* for the Service Catalog. From a programme idea (and optionally a client's assessment scores) it produces the full asset set: assessment dimensions, a module library, per-module branded assets, an internal runbook spreadsheet, an assessment questionnaire spreadsheet, an interactive questionnaire (radar chart + recommended modules), and an elevator-pitch deck. Quality is driven by a six-persona automated critique loop that refines artefacts before each human review gate.

These requirements are derived from `design.md` (design-first workflow) and remain traceable to it. Where the design left a matter open (notably commercial/pricing questions and the asset folder structure), the requirement records a working assumption and flags it for confirmation rather than silently deciding high-impact commercial policy.

---

## Glossary

- **Programme** — a repeatable, multi-phase D55 service offering (Assess → Teach → Prove → Scale) built around a free assessment.
- **Template mode** — authoring the canonical, reusable catalog entry for a programme (all candidate modules, generic content).
- **Client-instance mode** — a per-engagement clone of a template, scoped to one client's assessment scores.
- **Manifest** — `programme.yaml`, the single machine-readable source of truth for a programme (identity, brand, dimensions, modules).
- **Dimension** — an axis the assessment scores (current vs target, 1–5); the radar chart axes.
- **Module** — a workshop/deliverable cluster covering one or more dimensions, defined by a schema-conformant `module.md`.
- **Join key** — an exact-match link between artefacts (dimension names ↔ `dimensions_covered`; manual TOC titles ↔ `manual_section`; dimension names ↔ scores).
- **Critique loop** — the automated, bounded refinement of an artefact by the six personas before a human gate.
- **Persona** — one of six critique viewpoints: CEO (Jonathan), CTO (Rhys), Marketing, Client C-Suite, Client Middle-Management, Client Technical.
- **Internal assets** — artefacts D55 keeps and never ships (e.g. the Delivery Playbook runbook).
- **Client-facing assets** — artefacts handed to the client (Operating Manual, assessment questionnaire, interactive questionnaire, elevator pitch).
- **Bundle** — a self-contained skill directory that vendors everything it needs to run when copied elsewhere.

---

## Requirements

### Requirement 1: Author a programme end-to-end in two modes

**User Story:** As a D55 consultant, I want to author a whole service programme from an idea, in either template or client-instance mode, so that I can add a reusable catalog entry or produce a client-scoped engagement without hand-building every artefact.

#### Acceptance Criteria
1. WHEN the skill is invoked THEN it SHALL require a mode of either `template` or `client-instance` before generating any artefacts.
2. WHEN mode is `client-instance` THEN the skill SHALL require (or prompt for) a client's assessment scores, or a pointer to run the assessment first.
3. WHEN mode is `template` THEN the skill SHALL produce the canonical programme with all candidate modules and generic content.
4. WHEN a programme run completes THEN the skill SHALL have produced: the manifest, dimensions, a module library, per-module assets, the internal runbook spreadsheet, the assessment questionnaire spreadsheet, the interactive questionnaire, and the elevator-pitch deck.
5. IF a required input is missing or ambiguous THEN the skill SHALL ask a clarifying question rather than inventing high-impact content, recording any provisional decision in a working-assumptions register.

### Requirement 2: Manifest as single source of truth with join-key validation

**User Story:** As a maintainer, I want every artefact driven from one machine-readable manifest with validated join keys, so that the docs, spreadsheets, and interactive tool never drift apart.

#### Acceptance Criteria
1. WHEN a programme is scaffolded THEN the skill SHALL create a `programme.yaml` manifest capturing programme identity, brand config, dimensions, and modules.
2. WHEN modules and dimensions exist THEN the skill SHALL validate that every module `dimensions_covered` entry matches a manifest dimension name exactly.
3. WHEN modules and the manual TOC exist THEN the skill SHALL validate that every module `manual_section` matches a manual TOC section title exactly.
4. WHEN `trigger.critical_dimensions` are present THEN the skill SHALL validate they are a subset of that module's `dimensions_covered`.
5. IF any join-key validation fails THEN the skill SHALL hard-stop before asset generation and route the specific violations back for correction, and SHALL NOT emit drifted outputs. *(Validates Property 1.)*

### Requirement 3: Phased flow with human review gates

**User Story:** As a consultant, I want the build organised into stages with a human "Happy?" gate at key points, so that I stay in control and only review refined drafts.

#### Acceptance Criteria
1. WHEN authoring proceeds THEN the skill SHALL follow the four stages: Scope & Frame, Build Modules, Generate Assets, Verify & Ship.
2. WHEN the context, dimensions, module-content, and pitch artefacts reach the end of their automated critique loop THEN the skill SHALL present the refined artefact plus a critique summary at a human review gate.
3. WHEN the user answers "No" at a gate THEN the skill SHALL incorporate their steer and re-refine before advancing.
4. WHEN the user answers "Yes" at a gate THEN the skill SHALL advance to the next stage.
5. WHEN the module loop runs THEN the skill SHALL apply the gate per in-scope module before generating that module's assets.

### Requirement 4: Six-persona critique loop that always terminates

**User Story:** As a D55 stakeholder, I want each major artefact critiqued from six internal and external perspectives in a bounded refinement loop, so that quality is high and the loop can never run forever.

#### Acceptance Criteria
1. WHEN an artefact enters the critique loop THEN the skill SHALL invoke the relevant personas from: CEO (Jonathan), CTO (Rhys), Marketing, Client C-Suite, Client Middle-Management, Client Technical.
2. WHEN selecting personas for an artefact THEN the skill SHALL use the persona→artefact relevance matrix, and only primary personas SHALL gate that artefact.
3. WHEN personas return results THEN the skill SHALL aggregate them, dedupe overlapping findings, rank by severity × persona weight × cross-persona frequency, and split findings into *addressable-now* and *parked*.
4. WHEN scoring THEN parked items (needing a person or decision) SHALL NOT count against an artefact's score. *(Validates Property 9.)*
5. WHEN a round completes THEN the skill SHALL decide PASS (primary thresholds met, zero blockers), ITERATE (apply top addressable findings and re-run), or ESCALATE.
6. WHEN the maximum iteration cap is reached OR the addressable backlog stops shrinking THEN the skill SHALL ESCALATE (stop and surface open items at the human gate) rather than continue. *(Validates Properties 7, 8.)*
7. WHEN aggregating identical findings from multiple personas THEN the skill SHALL collapse them to one ranked backlog item deterministically. *(Validates Property 10.)*
8. WHEN a round completes THEN the skill SHALL append per-persona scores, backlog delta, and the decision to an auditable critique log.

### Requirement 5: Assessment dimensions and rubrics

**User Story:** As a consultant, I want the programme's assessment dimensions defined with maturity rubrics and tiered questions, so that the assessment is credible and repeatable.

#### Acceptance Criteria
1. WHEN scoping a programme THEN the skill SHALL define the assessment dimensions (radar axes) with 1–5 maturity rubrics and calibration examples.
2. WHEN authoring questions THEN the skill SHALL tier them into must-ask and go-deeper per dimension.
3. WHEN dimensions are defined THEN each dimension name SHALL be usable as the join key for module `dimensions_covered` and for assessment scores.

### Requirement 6: Module library conformant to the schema

**User Story:** As a maintainer, I want each module authored to the module schema, so that tooling can consume modules reliably.

#### Acceptance Criteria
1. WHEN scaffolding modules THEN the skill SHALL create one folder per in-scope module at `modules/module-{id}-{slug}/` with a `module.md` and an `assets/` folder.
2. WHEN authoring a `module.md` THEN it SHALL include schema-conformant frontmatter (module_id, title, dimensions_covered, trigger, audience, duration, format, manual_section, sets_up_embed, optional d55_ip) and the standard body sections.
3. WHEN a module is authored THEN the skill SHALL validate its join keys before proceeding.
4. WHEN in client-instance mode THEN only in-scope modules (per the recommendation logic) SHALL be populated with client-specific framing.

### Requirement 7: Recommendation logic (assessment scores to modules)

**User Story:** As a consultant, I want modules recommended from a client's scores using the module trigger rules, so that the client sees exactly the modules their gaps warrant.

#### Acceptance Criteria
1. WHEN scores are supplied THEN the skill SHALL compute, per module, whether it is included and at what level (standard, high, critical) using the MODULE-SCHEMA trigger logic.
2. WHEN a covered dimension's current score is at/below `recommend_when_current_at_or_below` OR the gap is at/above `include_when_gap_at_or_above` THEN the module SHALL be included.
3. WHEN a listed critical dimension's current score is at/below `critical_when_current_at_or_below` THEN the module SHALL always be included and flagged critical. *(Validates Property 5.)*
4. WHEN a module is included AND a covered dimension's gap is at/above `prioritise_when_gap_at_or_above` THEN it SHALL be flagged high priority; the reported level SHALL be the highest triggered (critical > high > standard). *(Validates Property 4.)*
5. WHEN a covered dimension's current is lowered or its target raised THEN a previously recommended module SHALL never be dropped from the recommended set. *(Validates Property 3.)*
6. WHEN scores are validated THEN every dimension SHALL be scored exactly once, each current/target within 1–5. *(Validates Property 2.)*

### Requirement 8: Per-module assets (branded HTML + PDF + starter templates)

**User Story:** As a consultant, I want each module's deliverables rendered as branded HTML and PDF plus starter templates, so that any consultant can run the module.

#### Acceptance Criteria
1. WHEN a module's content is agreed THEN the skill SHALL generate the module's promised deliverables into that module's `assets/` folder.
2. WHEN rendering THEN the skill SHALL produce branded HTML and a matching A4 PDF per deliverable using the programme's brand config.
3. WHEN HTML is produced THEN it SHALL embed its images/runtime as base64 (self-contained, no CDN links). *(Validates Property 12.)*

### Requirement 9: Internal runbook spreadsheet (Delivery Playbook)

**User Story:** As D55 delivery, I want an internal runbook spreadsheet describing what happens at each stage, so that we deliver the programme consistently.

#### Acceptance Criteria
1. WHEN generating spreadsheets THEN the skill SHALL produce an internal Delivery Playbook spreadsheet covering stages, activities, owners, inputs/outputs, and decision points.
2. WHEN the Delivery Playbook is produced THEN it SHALL be stored as an internal-only asset (see Requirement 12) and SHALL NOT be placed among client-facing deliverables.

### Requirement 10: Assessment questionnaire spreadsheet

**User Story:** As a facilitator, I want a questionnaire spreadsheet of the questions to ask per dimension, so that I can run or reference the assessment offline.

#### Acceptance Criteria
1. WHEN generating spreadsheets THEN the skill SHALL produce an assessment questionnaire spreadsheet with the questions per dimension and the 1–5 scoring scale.
2. WHEN the questionnaire spreadsheet is produced THEN its dimensions SHALL match the manifest dimension names exactly.

### Requirement 11: Interactive questionnaire (radar + recommendations)

**User Story:** As a prospect or facilitator, I want an interactive questionnaire that scores current vs target, draws a radar chart, and recommends modules, so that the free assessment produces an immediate, tailored output.

#### Acceptance Criteria
1. WHEN the interactive questionnaire is generated THEN it SHALL let a user score each dimension current vs target (1–5) and render a radar chart of the gap.
2. WHEN scores are entered THEN it SHALL recommend modules and next steps using the same trigger logic as the build-time recommendation.
3. WHEN the client-side recommendation is computed THEN it SHALL match the build-time `recommend_modules()` output for identical scores. *(Validates Property 6.)*
4. WHEN the interactive questionnaire is delivered THEN it SHALL be a self-contained HTML file (assets/runtime embedded, no external dependencies). *(Validates Property 12.)*

### Requirement 12: Asset output folder structure and internal/client separation

**User Story:** As a maintainer, I want a clear, predictable output folder structure that separates internal from client-facing assets and keeps client instances isolated from the template, so that assets are easy to find and we never hand a client the internal runbook by accident.

#### Acceptance Criteria
1. WHEN a programme is produced THEN its assets SHALL be written under a configurable output root, defaulting to `programmes/<programme-slug>/` (the AI-DLC reference at `analysis/D55/ai-dlc/` remaining as the exemplar); the output root SHALL be a parameter, never a hard-coded absolute path.
2. WHEN a template-mode programme is written THEN it SHALL use this layout:
   - `programme.yaml`, `context.md`, `dimensions.md`, `client-operating-manual-toc.md`, `working-assumptions.md`
   - `modules/module-{id}-{slug}/{module.md, assets/}`
   - `internal/` — internal-only assets (the Delivery Playbook runbook spreadsheet, `critique/` logs)
   - `client/` — client-facing deliverables (Operating Manual, `assessment-questionnaire.xlsx`, `workshop.html` interactive questionnaire, `elevator-pitch.*`)
   - `assets/brand/` — brand assets
3. WHEN any internal-only asset is generated THEN it SHALL be written under `internal/` and SHALL NOT be written under `client/` or a module's client-facing `assets/`.
4. WHEN a client-facing bundle is assembled for delivery THEN the skill SHALL exclude everything under `internal/`.
5. WHEN mode is `client-instance` THEN the clone SHALL be written under `programmes/<programme-slug>/clients/<client-slug>/` using the same internal/client layout.
6. WHEN a client-instance build runs THEN it SHALL NOT modify any file in the template library. *(Validates Property 11.)*
7. WHEN naming outputs THEN the skill SHALL use stable slug-based names consistent with the manifest.
8. NOTE: this structure firms up the directory-layout question left open in the design; the internal/client split and the default output root are working assumptions to confirm with Rhys before first real use.

### Requirement 13: Elevator-pitch presentation

**User Story:** As marketing/sales, I want a branded exec elevator-pitch deck for the free assessment offer, so that we can open conversations with prospects.

#### Acceptance Criteria
1. WHEN assets are generated THEN the skill SHALL produce a branded elevator-pitch presentation summarising the programme (the 2-minute narrative, the stage path, value, recommended next step).
2. WHEN in client-instance mode THEN the pitch SHALL be tailored to that client's gap profile.
3. WHEN the pitch is produced THEN it SHALL be a client-facing asset stored under `client/`.

### Requirement 14: Self-sufficient, portable skill bundle

**User Story:** As a maintainer, I want the skill and its sub-skills packaged as self-contained bundles, so that I can zip a skill (or the set) into another repo and it just works.

#### Acceptance Criteria
1. WHEN the skill is packaged THEN its bundle directory SHALL vendor everything it needs: engine code, module schema, persona rubrics, brand assets, templates, and a trimmed worked example, plus a bundle-local `requirements.txt`.
2. WHEN the skill resolves any path THEN it SHALL resolve relative to the bundle, never relative to the repo root or `analysis/`, and SHALL contain no hard-coded absolute paths.
3. WHEN a bundle is copied to a location outside the repo and run on its bundled example THEN it SHALL produce outputs successfully, with no file/asset load resolving into `analysis/`, the repo root, or an absolute path. *(Validates Property 13.)*
4. WHEN two skills need the same engine THEN each SHALL vendor its own copy (or ship together as one skill-set) rather than referencing a shared file elsewhere.

### Requirement 15: Output verification

**User Story:** As a consultant, I want every output verified before the programme is declared ready, so that I never ship a broken asset.

#### Acceptance Criteria
1. WHEN outputs are produced THEN the skill SHALL verify rendered HTML by measuring the DOM (images loaded, expected block/section counts, no horizontal overflow).
2. WHEN PDFs are produced THEN the skill SHALL verify page count, page size, and the absence of orphaned headings.
3. WHEN spreadsheets are produced THEN the skill SHALL verify expected sheets/rows exist.
4. IF any verification check fails THEN the skill SHALL fix and regenerate the affected asset and re-verify before declaring the programme ready.
5. WHEN verification finishes THEN the skill SHALL clean up any temporary servers, screenshots, and check scripts.

---

## Open questions carried from design (need confirmation)

1. **First-build scope** — generalise the whole engine now, or ship the critique-loop + manifest against AI-DLC first, then generalise. Working assumption: AI-DLC first.
2. **Critique cost/latency** — cap iterations and make panel membership per-phase configurable (working assumption in Requirement 4).
3. **Runbook spreadsheet columns** — confirm the exact columns for the Delivery Playbook (Requirement 9).
4. **Interactive questionnaire hosting** — self-contained HTML only for now (Requirement 11); hosted/booking version out of scope.
5. **Output root + internal/client split** — confirm `programmes/<slug>/` default and the `internal/` vs `client/` split (Requirement 12).
6. **Commercial/pricing policy and external programme name** — not decided by the skill; captured as working assumptions for Rhys/Jonathan.
