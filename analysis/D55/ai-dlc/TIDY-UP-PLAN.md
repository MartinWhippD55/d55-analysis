# AI-DLC — Tidy-Up & Consolidation Plan

*Created 2026-07-07. The intent for turning this working folder into a clean, canonical version — and building the authoring skill that does it. Deferred until content firms up and Rhys has reviewed; captured now so it isn't lost.*

---

## The problem this solves

This folder is organised by **topic** (programme, modules, schema, assumptions, critique, embed scoping), which is right for a design phase. But it's not yet organised by **"what happens when."** A newcomer can read everything and understand the shape, but couldn't glance at it and know the running order or what's blocked on what. Some docs (`HANDOVER.md`, `context.md`) still describe the pre-programme framing.

Two distinct needs:
1. **The Delivery Playbook** — the sequenced "what and when" view (the internal runbook). Named but not yet authored; the four phases are its spine.
2. **Consolidation** — a clean, canonical version of the whole thing with a clear "start here" entry point, stale docs reconciled.

## The idea: consolidate via a skill, not by hand

Rather than a one-off manual reorganise, build a **`new-programme` skill** that reads this working folder as source material and emits a clean version into a **new, separate folder**. This makes consolidation repeatable and doubles as the reusable authoring tool for *future* programmes (this AI-DLC folder becomes the worked reference implementation, the way BRYT is for the deliverables skills).

Working source (this folder, messy, full of thinking) → **skill** → clean canonical programme (new folder).

---

## Proposed skill flow

Based on the sketched design:

```
new-programme (skill)
   │
   ├── 1. Ask questions            ← interactive; recursively refine scope
   │      (loops until clear)         how many modules? which dimensions? client context?
   │
   ├── 2. Create module folder structure
   │
   ├── 3. Loop modules:
   │        Iterate on module content ──▶ Request user review (Happy? Y/N)
   │              ▲                                    │ N
   │              └────────────────────────────────────┘
   │                                                   │ Y
   ├── 4. Loop modules:
   │        Generate assets            ← per-module slides/handouts/templates
   │
   ├── 5. Generate radar assessment    ← the assessment write-up from scores
   │
   └── 6. Generate elevator pitch presentation
```

### Step notes

- **Ask questions (recursive):** lead with the assessment radar + the trigger logic in `MODULE-SCHEMA.md` to *recommend* which modules are needed, then confirm/adjust with the user. Not an open-ended interview — score-driven, per the earlier design principle.
- **Create module folder structure:** scaffold `module-{id}-{slug}/module.md` (+ `assets/`) to the schema, only for the modules in scope.
- **Iterate on module content + review loop:** human-in-the-loop gate per module before moving on. Matches how we establish ground-truth as we go.
- **Generate assets:** the starter templates (investment-case one-pager, spec template, AI usage policy, Four Fears sheet, governance checklist) + slides. Reuses/generalises the `build_programme_doc.py` engine.
- **Generate radar assessment:** the tailored assessment write-up (the parked assessment→runbook capability).
- **Generate elevator pitch presentation:** repurposes the existing `summary-presentation` skill.

### Relationship to existing skills

- Generalise `build_programme_doc.py` into the shared rendering engine (like `deliverables-toolkit`).
- Reuse `summary-presentation` for the pitch deck.
- The `new-programme` skill becomes the **orchestrator** (like `spec-to-deliverables`), delegating to render/asset/presentation steps.

---

## Consolidation deliverables (what the clean folder contains)

1. **`delivery-playbook.md`** — the authored internal runbook: phases in order, triggers, inputs, RACI, exit criteria per phase. The map through the reference docs.
2. **Top-level `README.md`** — "start here": what this is, read order, what's canonical vs archived.
3. **Reconciled reference docs** — programme structure, modules, schema, manual TOC, embed scoping — canonical versions, consistent phase numbering (0–3 throughout).
4. **Archive** — `HANDOVER.md`, `context.md`, critique outputs, working-assumptions moved to an `archive/` or `_working/` area so the clean folder isn't cluttered with process history.

---

## Sequencing / prerequisites

**Decision (2026-07-07):** Rhys review will not come soon, so we are **proceeding on the working assumptions** (WA-1…WA-6) as ground-truth. The Rhys-review gate is lifted; assumptions remain flagged 🟡 for later review but do not block work. The best way to firm up lean content is to run the process against it and fix what breaks.

**Order:**
1. ✅ Write the `new-programme` skill definition — `.kiro/skills/new-programme.md`.
2. Generalise `build_programme_doc.py` → a reusable engine (separate engine from ai-dlc-specific content/branding config). Foundation for the skill; not throwaway regardless of content changes.
3. Build `new-programme` skill steps incrementally (scaffold → content loop → assets → assessment → pitch), refining the skill doc as we learn.
4. Run it against this folder to emit the clean canonical version (new folder).
5. Author `delivery-playbook.md` + README as part of the clean output.

---

## Open questions for later

- Does the skill emit into a per-client folder (each engagement gets its own programme instance) or a canonical template folder (the reusable D55 offering)? Likely **both**: a template it clones per client.
- Is a Kiro **spec** the right vehicle to build the skill itself? (It's real software — probably yes, when we start.)
- Where does the clean folder live — replace this one, or sit alongside as `ai-dlc-programme/` with this as `_working/`?
