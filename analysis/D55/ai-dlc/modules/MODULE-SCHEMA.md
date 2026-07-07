# Module Schema

*The contract every `module.md` frontmatter must follow. Skills that consume the module library (authoring, module-to-presentation, assessment→runbook) target this schema. Change it here first, then update the module docs.*

*Location convention: one folder per module at `modules/module-{id}-{slug}/module.md`, with an optional `assets/` folder alongside for slides, exercises, and handouts. Skills glob `modules/*/module.md`.*

---

## Frontmatter fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `module_id` | integer | yes | Stable numeric id (1–N). Orders modules and keys them for tooling. |
| `title` | string | yes | Human-readable module name. |
| `dimensions_covered` | list[string] | yes | Assessment dimension names this module addresses. **Must match `dimensions.md` names exactly** — this is the join key between assessment scores and modules. |
| `trigger` | object | yes | Rules for when to recommend this module from assessment scores. See below. |
| `audience` | list[string] | yes | Who should attend. |
| `duration` | string | yes | Time commitment (e.g. "Half day (3–4 hrs)"). |
| `format` | string | yes | Delivery format (e.g. "Facilitated exec session"). |
| `manual_section` | string | yes | Which Client Operating Manual section this module writes. **Must match a section title in `client-operating-manual-toc.md`** (exact lowercase filename). |
| `sets_up_embed` | boolean | yes | Whether this module directly prepares the Phase 2 embed. |
| `d55_ip` | list[string] | no | Named D55 frameworks used in the module. |

---

## The `trigger` object

Drives which modules a skill recommends from a client's radar scores. Scores are 1–5 (current and target) per dimension, per `dimensions.md`.

| Key | Type | Required | Meaning |
|-----|------|----------|---------|
| `recommend_when_current_at_or_below` | integer (1–5) | yes | Recommend the module if the current-state score on **any** covered dimension is ≤ this value. Include a one-line rationale comment where the threshold differs from other modules. |
| `include_when_gap_at_or_above` | integer (1–4) | yes | **Inclusion** trigger on ambition: pull the module in when (target − current) on any covered dimension is ≥ this value, *even from a strong base*. Ensures a client at current 4 / target 5 still gets a roadmap. |
| `prioritise_when_gap_at_or_above` | integer (1–4) | yes | Flag an included module **high priority** when (target − current) on any covered dimension is ≥ this value. |
| `critical_dimensions` | list[string] | no | Names the dimension(s) subject to a hard gate. Must be a subset of `dimensions_covered`. Use for gates like governance. |
| `critical_when_current_at_or_below` | integer (1–5) | no | With `critical_dimensions`: flag **critical** when the current score on a *listed* dimension ≤ this. Applies only to the named dimensions, not all covered ones. |

### Recommendation logic (reference for skills)

For each module, for each dimension it covers:
1. If `current <= recommend_when_current_at_or_below` → module is **included** (recommended).
2. If `(target - current) >= include_when_gap_at_or_above` → module is **included** (ambition-driven), regardless of how high the current score is.
3. If `critical_when_current_at_or_below` is set **and** the dimension is in `critical_dimensions` **and** `current <=` the threshold → module is **critical** (always include, overrides).
4. For an already-included module, if `(target - current) >= prioritise_when_gap_at_or_above` → mark **high priority**.

A module is included if step 1, 2, or 3 fires on any covered dimension. **Priority applies only to included modules** and is the highest level triggered: critical > high > standard. A module cannot be high-priority-but-excluded — if a priority condition fires, the module is included by definition.

---

## Body sections (after frontmatter)

Each `module.md` body follows this consistent structure so a presentation/runbook skill can map sections predictably:

1. **Objective** — the client outcome in 2–3 sentences.
2. **Why it matters (client outcome)** — the value framing.
3. **Who's in the room** — audience detail.
4. **Inputs (from assessment)** — what feeds the module.
5. **Session flow** — numbered agenda / exercises.
6. **Deliverables (what they leave with)** — bulleted tangible outputs.
7. **Writes to Client Operating Manual** — which section and what content.
8. **How it sets up the embed** — link to Phase 2.

---

## Example (Module 1 frontmatter)

```yaml
---
module_id: 1
title: Leadership & the Investment Case
dimensions_covered:
  - Leadership & Mandate
  - Metrics & ROI
trigger:
  recommend_when_current_at_or_below: 2  # leadership gaps common; only pull in when genuinely weak
  include_when_gap_at_or_above: 2
  prioritise_when_gap_at_or_above: 2
audience:
  - CEO / Managing Director
  - CTO / VP Engineering
  - CFO / Finance
  - PE / Board sponsor
duration: Half day (3–4 hrs)
format: Facilitated exec session
manual_section: "1. Mandate & Measurement"
sets_up_embed: true
d55_ip:
  - The Economics (£200/seat for 3–5x)
  - 8-Week Prove-It Model
---
```
