---
name: deliverables-toolkit
description: Shared foundation for the spec-to-deliverables suite — the reusable data-driven document-generator pattern, branding, verification method, and gotchas. Read this first.
inclusion: manual
---

# Deliverables Toolkit

Shared foundation for the `spec-to-deliverables` suite: the reusable document-generator pattern, branding approach, verification method, and the non-obvious gotchas learned building these documents. Every other child skill in this folder builds on this.

## Where things live

The **engine is vendored in this skill** (`engine/`) — you don't rebuild it. What you author per spec is the *content* (small Python modules exposing `DOC`/`deck` dicts) plus branding, written under the run's **`<deliverables-dir>`** — by default `deliverables/<spec>/` at the repo root (the parent `SKILL.md` sets this). A typical layout:

```
.kiro/skills/spec-to-deliverables/engine/   the render engine (shared, tested — import it)

deliverables/<spec>/
  figures.py               shared figures module (thin: calls engine.figures.load_figures)
  <document>.py            one content module per document (DOC dict of blocks)
  <deck>.py                the presentation content (deck dict)
  regenerate_all.py        runs every generator in order
  assets/                  brand + client logos, backgrounds, cropped mockups (base64-embedded)
  outputs/                 rendered HTML + PDF + xlsx
```

Keep each spec's deliverables inside its own `<deliverables-dir>` so specs never collide and the set stays portable. Content modules add the bundle root to `sys.path` (or the caller does) so they can `import engine.*` and `import figures`.

> **Optional worked example.** A complete, already-built instance of this pattern lives at `analysis/BRYT/contract-note/` **in this repo, if present** — read its `walkthroughs/*.py` content modules for concrete `DOC` examples. It predates the vendored engine (it carried its own copy), so treat it as a *content* reference; the code of record is `engine/` here.

## The data-driven document pattern

Separate the **rendering engine** (vendored, generic) from the **content** (per spec):

- **Engine** — `engine/walkthrough.py` renders a `DOC` dict into branded, standalone HTML then PDF; `engine/presentation.py` renders a `deck` dict into a slide deck; `engine/figures.py` / `engine/estimates.py` handle the spreadsheet; `engine/openapi_html.py` the API reference. All brand-configurable via `engine/brand.py::BrandConfig`. None of it is spec-specific.
- **Content modules** (`estimate_01.py`, `data_model.py`, …): one small Python file per document exposing a `DOC` dict of typed "blocks". Adding a new document = adding a content module, no engine changes.

Supported block types (see `engine/walkthrough.py` docstring for the exact schema): `section` (heading + prose + bullets), `table`, `screens` (annotated mockups with interactions + data notes), `diagram` (embedded image), CSS-rendered `layers` (architecture lanes) and `pipeline` (left-to-right steps), `callout`, and `entities` (data-model records with PK/SK badges + attribute tables). Any block may carry `"pageBreak": True`. Reuse these rather than inventing markup.

### Using the engine

```python
import sys; sys.path.insert(0, ".kiro/skills/spec-to-deliverables")  # so `import engine` resolves
from engine.walkthrough import build_document
from engine.brand import BrandConfig

brand = BrandConfig.from_assets_dir("deliverables/<spec>/assets", eyebrow="My Programme", date="July 2026")
build_document(DOC, out_dir="deliverables/<spec>/outputs", brand=brand,
               base_dir="deliverables/<spec>")   # base_dir resolves relative image paths
```

`build_document` writes `<slug>.html` and (unless `make_pdf=False`) `<slug>.pdf`. Assets are optional — if a logo/background path is missing the cover falls back to the brand gradient, so nothing hard-depends on a particular file.

### Rendering to PDF

- The engine builds **standalone HTML** first (images embedded as base64 so the file is self-contained), then renders to PDF with Playwright/Chromium.
- It uses `page.pdf(print_background=True, prefer_css_page_size=True)` and controls size/margins from CSS `@page` rules (not the pdf() call) — this is what makes Word-style margins repeat on every page.
- One-time setup: `pip install -r .kiro/skills/spec-to-deliverables/requirements.txt` then `python -m playwright install chromium`.

### Verify the engine

Run `python -m pytest` from the bundle root before relying on it — the engine has unit + property tests for block rendering, figures maths, estimate parsing, deck assembly, and the OpenAPI HTML.

## Branding

- Keep brand assets (logo, background, client logo) in the run's `<deliverables-dir>/assets/` folder and embed them as base64 so outputs are portable.
- Cover page: full-bleed background with a gradient overlay; content pages: white with generous margins (~24mm top, 22mm sides) for a document feel.
- Use CSS named pages so the cover can be margin-free while content pages have margins.

## Verification method (important — the agent cannot view images directly)

To check a rendered document actually looks right:

1. Serve the output folder over localhost: `python -m http.server <port>` (use `controlPwshProcess` to run it in the background; stop it when done).
2. Navigate to the HTML with the Playwright browser tools.
3. **Measure the DOM programmatically** with `browser_evaluate` — this is the reliable signal. Check: all images loaded (`naturalWidth > 0`), expected counts (screens, tables, diagram lanes, entity cards), the cover background applied, and `document.body.scrollWidth <= innerWidth` (no horizontal overflow).
4. For PDFs, read them back with `pypdf`: assert the page count and page size (A4 = 595×842pt), and detect **orphaned headings** by checking whether any page's last text line is a known heading.
5. Screenshots can be captured but cannot be inspected inline — rely on measurement, not on looking.
6. Clean up temporary check scripts and screenshots afterwards.

## Gotchas (hard-won — save yourself the rediscovery)

- **Page breaks**: without control, headings orphan at page bottoms. Add `break-after: avoid` on headings, `break-before: avoid` on the element after a heading, and `break-inside: avoid` on cards, callouts, diagrams, and table rows. Verify with the orphan check above.
- **Excalidraw MCP** renders diagrams but does **not** save a PNG to disk. For embeddable diagrams, prefer **CSS-rendered** diagrams (the `layers`/`pipeline` block types) — they print cleanly, stay on-brand, and need no external files.
- **Wide screenshots**: mockups captured at full window width (e.g. 1920×889) read as small letterboxed strips in a portrait doc. Crop them to the relevant area before embedding; the engine scales to content width automatically so aspect ratio is preserved.
- **Self-contained HTML** must **inline** its runtime, not link a CDN. Tools like Redocly's `build-docs` still reference the runtime from a CDN — for a truly offline file, fetch the runtime once and embed it (see `openapi-html.md`).
- **Slide scaling**: to make fixed-size slides fill the viewport by default, use CSS `zoom` (via a tiny resize script), not `transform: scale`. `zoom` reserves layout space so slides still stack; `scale` leaves gaps/overlaps. Cap it (~1.9x) so it doesn't oversize on ultrawide screens.
- **Absolutely-positioned list markers** (custom chevron bullets) ride above the text baseline unless you pin them to the first-line box (`top` matching the item's padding, `line-height` matching the text). Verify by comparing computed `top`/`line-height`.
- **openpyxl rewrites xlsx binaries** even when values are unchanged. After any script that opens+saves a spreadsheet for testing, restore it from git to avoid needless binary churn in commits.
- **Commit messages via shell**: avoid escaped double-quotes in `-m` on Windows bash — they get split into pathspecs. Keep messages quote-free or use simple wording.

## Notes

- Prefer `fsWrite` + `fsAppend` for large generated files; keep individual writes modest.
- Build the engine once per `<deliverables-dir>` and reuse it across every document for that spec; copy **patterns** from any example rather than duplicating prose.
