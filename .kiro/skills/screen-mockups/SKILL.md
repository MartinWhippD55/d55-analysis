---
name: screen-mockups
description: Turn a prompt, design doc, or spec into a set of hand-drawn-style UI wireframes, one per screen.
inclusion: manual
---

# Screen Mockups

Turn a **prompt** — a description of an app, a design doc, a spec, or just a
list of screens — into a set of **hand-drawn-style UI wireframes**: one
self-contained HTML file per screen, each screenshotted to a PNG, all indexed
from a `screen-mockups.md`. The deliberately sketchy look keeps reviewers on
layout and flow rather than pixels and brand.

Self-contained: this skill bundles its own style kit, an HTML skeleton, and a
screenshot helper. It has no external dependencies beyond Playwright.

## Inputs (what to provide when invoking)

1. **A source of screen content** — any of: a written prompt describing the
   screens, a product/feature description, a design doc, or a spec. The skill
   infers the screen list from it.
2. **An output folder** — where `screen-mockups.md` + `mockups/` should be
   written.
3. *(optional)* The exact screens and their order, a viewport width, or specific
   sample data to show. If omitted, these are inferred and defaults used.

## When to use

- You want low-fidelity wireframes to validate layout, structure, and
  interactions with stakeholders — fast, throwaway, "layout only".
- Not for branded, pixel-perfect comps or print-ready documents.

## Output layout

```
<output-folder>/
  screen-mockups.md          # index: intro + screenshot table + per-screen notes
  mockups/
    wireframe.css            # the style kit (copied from this skill's assets/)
    01-<screen>.html         # one wireframe per screen; links wireframe.css
    01-<screen>.png          # its screenshot
    02-<screen>.html
    02-<screen>.png
    ...
```

Number files `01-`, `02-`, … in the order a user encounters them; keep slugs
short (`template-list`, `section-editor`).

## Steps

### Step 1: Derive the screen list

From the prompt/design, list the distinct screens and modals a user moves
through. For each, capture: purpose (one line), **layout** (panels/regions and
their contents), and **key interactions** (what buttons/handles/drag affordances
do). Confirm the list with the user if the prompt is thin.

### Step 2: Author one HTML wireframe per screen

- Copy `assets/wireframe.css` into the output `mockups/` folder and `<link>` it
  from each HTML (simplest), **or** inline its contents into each file for fully
  standalone artefacts.
- Start from `assets/template.html`. Apply the style kit consistently so the set
  reads as one family. Add per-screen tweaks (field positions, widths) in a
  small local `<style>`.
- Populate with **realistic sample data** drawn from the domain in the prompt —
  never lorem ipsum. Real names make reviewers engage with the actual content.
- Use the kit's building blocks rather than inventing markup: `.container` frame,
  `.header`/`.footer` bars, `.btn`/`.btn-sm`, `table` + `.chip` + `.drag-handle`,
  `.badge`, `.left-panel`/`.right-panel` splits, `.form-group`, and for modals
  `body.modal-mode` + `.modal` + `.canvas`/`.field-box`.

### Step 3: Screenshot each to PNG

```
python .kiro/skills/screen-mockups/shoot.py <output>/mockups --width 1200 --check
```

This renders every `*.html` in the folder at a fixed viewport width and writes a
full-page PNG next to each (same stem). `--check` also verifies the DOM (see
Step 5). One-time setup: `pip install playwright && python -m playwright install chromium`.

### Step 4: Index in `screen-mockups.md`

Write the markdown index: a short intro, a table linking each PNG, then one
section per screen with its **Layout** and **Key interactions** bullets from
Step 1. This is the human-readable deliverable.

### Step 5: Verify

`shoot.py --check` asserts, per screen: the sketch font is applied, no horizontal
overflow (`scrollWidth <= innerWidth`), no broken images, and the
`.wireframe-label` is present. It exits non-zero if any screen has issues. Then
confirm every PNG exists with non-zero size and every link in `screen-mockups.md`
resolves. (The agent can't see images — rely on these measurements, not on
looking at the PNG.)

## The wireframe style kit (`assets/wireframe.css`)

The signature look, so you know what the classes give you:

- **Font**: Architects Daughter (Google Fonts), falling back to Comic Sans /
  cursive — the hand-drawn "not final" feel.
- **Palette**: black-on-white only. Text `#333`, muted `#888`/`#aaa`, subtle
  fills `#f9f9f9`/`#fafafa`. No brand colours.
- **Frame**: `.container` = `2px solid #333` + `border-radius: 6px` + a tiny
  `rotate(-0.3deg)` sketched tilt.
- **Dividers**: inner separators are **dashed** (`#aaa`); strong section edges
  (header/footer) are **solid** `2px #333`.
- **Buttons**: `.btn` (primary, `2px` border) and `.btn-sm` (secondary, `1.5px`).
- **Fidelity signal**: `.wireframe-label` fixed top-right on every screen.
- **Chips & handles**: circular numbered `.chip`; `⋮⋮` (`&#x22EE;&#x22EE;`)
  `.drag-handle` for reorderable rows; small `.badge` tags.
- **Layouts**: `.content` flex with `.left-panel` (fixed width, dashed right
  border) + `.right-panel { flex: 1 }`.
- **Modals**: `body.modal-mode` dims the backdrop and centres a `.modal`; a
  labelled `.canvas` holds dashed `.field-box` placeholders for draggable items.

## Gotchas

- **Consistent width, full-page**: capture full-page and hold one viewport width
  across all screens (`shoot.py` does both), or the set looks mismatched. Very
  wide screens embedded in a portrait doc read as tiny letterboxed strips — crop
  or scale before embedding.
- **Keep it obviously sketchy**: the font + tilt + "WIREFRAME" label are the
  point. If it looks polished, stakeholders debate colours instead of flow.
- **Icons**: prefer HTML entities (`&#x22EE;`, `+`) and plain words over emoji —
  they render consistently in the sketch font.
- **Self-contained files**: only the Google font is remote; inline the CSS (or
  ship `wireframe.css` alongside) so a file opens offline in any browser.
- **Throwaway artefacts**: gitignore the PNGs if they're large/regenerable and
  clean up any stray screenshots (see this skill's `.gitignore`).
