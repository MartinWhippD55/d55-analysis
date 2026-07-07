---
inclusion: manual
---

# New Programme

Author a repeatable D55 **service programme** — a multi-phase offering built around an assessment, a set of workshop modules, an embedded delivery phase, and a client-owned operating manual. Given a client's assessment scores and context, this skill recommends which modules are needed, scaffolds the module structure, iterates on content with the user, and generates the client-facing assets (assessment write-up, operating manual, pitch deck).

This is the **orchestrator** skill. It decides what to produce and delegates rendering to focused steps. The worked reference implementation is `analysis/D55/ai-dlc/` — the AI-DLC programme this pattern was extracted from. Read it for concrete examples of every artefact this skill produces.

Read `deliverables-toolkit` first — this skill reuses its rendering/branding/verification patterns. The reusable render engine is `analysis/D55/ai-dlc/programme_engine.py` (config-driven: pass a `BrandConfig` + content dict to `build()`); `analysis/D55/ai-dlc/build_programme_doc.py` is a worked thin-caller example.

## Core concepts

A programme has:
- **Dimensions** — the axes an assessment scores (current vs target). See `analysis/D55/ai-dlc/dimensions.md`.
- **Modules** — workshop clusters of dimensions, each with machine-parseable frontmatter. Contract: `analysis/D55/ai-dlc/modules/MODULE-SCHEMA.md`.
- **Two runbooks** — the internal **Delivery Playbook** (never handed over) and the **Client Operating Manual** (the kept asset, populated across the programme). See `analysis/D55/ai-dlc/client-operating-manual-toc.md`.
- **Phases** — Assess → Teach → Prove (embed) → Scale.

The join keys that make it tooling-consumable: a module's `dimensions_covered` must match dimension names exactly, and its `manual_section` must match a manual TOC section title exactly.

## Steps

### Step 1: Ask questions (recursive scoping)

Establish scope before generating anything. **Lead with data, not an open interview:**

1. Take the client's assessment scores (current + target per dimension). If none exist, ask for them or run/point to the assessment first.
2. Apply each module's `trigger` logic (from `MODULE-SCHEMA.md`) to *recommend* which modules are in scope — recommended, critical, or high-priority. Present the recommendation with the reasoning ("weak on governance → Shipping Safely is critical").
3. Confirm or adjust with the user. Only ask open questions where the scores are ambiguous or context is missing (client size, sector, regulated?, AWS?, people available for a hybrid embed).
4. Loop until scope is agreed: which modules, whether the embed is in play, any client-specific framing.

Capture any provisional decisions in a working-assumptions register (see `analysis/D55/ai-dlc/working-assumptions.md` for the format) so they can be reviewed later.

### Step 2: Create the module folder structure

Scaffold only the in-scope modules, to the schema:

```
modules/module-{id}-{slug}/
  module.md      (frontmatter to MODULE-SCHEMA.md + the standard body sections)
  assets/        (empty until Step 4)
```

Validate the join keys as you write: `dimensions_covered` against the dimension list, `manual_section` against the manual TOC.

### Step 3: Iterate on module content (human-in-the-loop loop)

For each in-scope module:
1. Draft the `module.md` body (Objective, Why it matters, Who's in the room, Inputs, Session flow, Deliverables, Writes to manual, How it sets up the embed).
2. **Request user review — Happy? (Y/N).** If N, revise and re-present. Do not advance to the next module until the current one is agreed.

This establishes ground-truth per module rather than generating everything then reworking.

### Step 4: Generate assets (per module)

Once content is agreed, produce the starter artefacts each module promises (its "deliverables"): e.g. an investment-case one-pager, a spec template, an AI usage policy, a diagnostic worksheet, a governance checklist, and slides. Render branded via `programme_engine.build()` with the programme's `BrandConfig`. Output into each module's `assets/`.

### Step 5: Generate the radar assessment write-up

Produce the tailored assessment document from the scores: current-vs-target radar narrative, the gaps ranked, and which modules/phases each points to. This becomes Section 0 of the Client Operating Manual.

### Step 6: Generate the elevator-pitch presentation

Produce a branded exec deck summarising the programme for this client. Reuse the `summary-presentation` skill. Keep it exec-level: the 2-minute narrative, the phase path, the value principles, and the recommended next step.

### Step 7: Verify

Per `deliverables-toolkit`: serve locally, measure the DOM (images loaded, expected block counts, no overflow), check PDFs for page count and orphaned headings. Clean up temporary servers/screenshots.

## Output modes

- **Template mode** — the reusable D55 offering (all modules, generic content). This is the canonical library.
- **Client-instance mode** — a per-engagement folder cloned from the template, scoped to one client's scores and populated with their specifics.

Default: maintain the template, and clone it per client rather than editing the template in place.

## Notes

- Point new work at the `analysis/D55/ai-dlc/` reference for concrete examples — copy the **patterns**, not the prose.
- Keep the module schema and manual TOC as the single source of structure; if they change, regenerate rather than hand-editing outputs.
- Mark any inferred or provisional decision clearly (working-assumptions register) so it can be confirmed later.
- This skill builds real software (the generators). A Kiro spec is an appropriate vehicle when implementing the engine generalisation.
