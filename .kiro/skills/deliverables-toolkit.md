---
name: deliverables-toolkit
description: Shared foundation for the spec-to-deliverables suite — the reusable data-driven document-generator pattern, branding, verification method, and gotchas. Read this first.
inclusion: manual
---

# Deliverables Toolkit

Shared foundation for the `spec-to-deliverables` suite: the reusable document-generator pattern, branding approach, verification method, and the non-obvious gotchas learned building these documents. Every other child skill builds on this. The worked reference implementation is `analysis/BRYT/contract-note/` in this repo.

## The data-driven document pattern

Separate the **rendering engine** from the **content**:

- **Engine** (`build_walkthrough.py` in the reference): a generic renderer that takes a content dict (`DOC`) and produces branded, standalone HTML, then renders it to PDF. It knows nothing about any specific document.
- **Content modules** (`estimate_01.py`, `data_model.py`, …): one small Python file per document exposing a `DOC` dict of typed "blocks". Adding a new document = adding a content module, no engine changes.

The engine supports block types like: `section` (heading + prose + bullets), `table`, `screens` (annotated mockups with interactions + data notes), `diagram` (embedded image), CSS-rendered `layers` (architecture lanes) and `pipeline` (left-to-right steps), `callout`, and `entities` (data-model records with PK/SK badges + attribute tables). Reuse these rather than inventing markup per document.

### Rendering to PDF

- Build **standalone HTML** first (images embedded as base64 data URIs so the file is self-contained), then render to PDF with Playwright/Chromium.
- Use `page.pdf(print_background=True, prefer_css_page_size=True)` and control size/margins from CSS `@page` rules, not from the pdf() call. This is what makes Word-style margins repeat on every page.
- One-time setup: `pip install playwright` then `python -m playwright install chromium`.

## Branding

- Keep brand assets (logo, background, client logo) in one `assets/` folder and embed them as base64 so outputs are portable.
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
- **Self-contained HTML** must **inline** its runtime, not link a CDN. Tools like Redocly's `build-docs` still reference the runtime from a CDN — for a truly offline file, fetch the runtime once and embed it (see `openapi-html`).
- **Slide scaling**: to make fixed-size slides fill the viewport by default, use CSS `zoom` (via a tiny resize script), not `transform: scale`. `zoom` reserves layout space so slides still stack; `scale` leaves gaps/overlaps. Cap it (~1.9x) so it doesn't oversize on ultrawide screens.
- **Absolutely-positioned list markers** (custom chevron bullets) ride above the text baseline unless you pin them to the first-line box (`top` matching the item's padding, `line-height` matching the text). Verify by comparing computed `top`/`line-height`.
- **openpyxl rewrites xlsx binaries** even when values are unchanged. After any script that opens+saves a spreadsheet for testing, restore it from git to avoid needless binary churn in commits.
- **Commit messages via shell**: avoid escaped double-quotes in `-m` on Windows bash — they get split into pathspecs. Keep messages quote-free or use simple wording.

## Notes

- Prefer `fsWrite` + `fsAppend` for large generated files; keep individual writes modest.
- Point new work at the reference implementation for concrete code rather than duplicating it into the skill.
