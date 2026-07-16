---
inclusion: manual
---

# Markdown to PDF

Turn any Markdown file into a branded, standalone A4 PDF (D55 cover, logos,
typography, tables, callouts) with a single command. Free-standing: bundles its
own converter, brand assets, and a focused Markdown parser — no third-party
Markdown library needed. Reference example lives in `examples/`.

Related: `deliverables-toolkit` covers the block-authored document engine (hand
-written content modules). Use *this* skill when the source is already Markdown
and you just want it rendered to a branded PDF.

## Usage

```
python .kiro/skills/markdown-to-pdf/md_to_pdf.py <path-to.md> [options]
```

Options:

| Option | Effect |
|---|---|
| `--client-logo <key\|path>` | Co-brand the cover top-left. Bundled key (e.g. `esg`) or a path to a white PNG. |
| `--title / --subtitle / --eyebrow / --date / --confidential` | Override cover fields. |
| `--out <path>` | Output PDF path (default: alongside the source, same stem). The HTML is written next to the PDF. |
| `--no-pdf` | Write the standalone HTML only (skip the PDF render). |

Example:

```
python .kiro/skills/markdown-to-pdf/md_to_pdf.py analysis/ESG/report.md \
    --client-logo esg --eyebrow "Confidential Briefing"
```

## Front matter (optional)

A leading YAML block sets cover fields without CLI flags:

```markdown
---
title: My Document
subtitle: A short description
eyebrow: Confidential Briefing
confidential: Confidential — D55 internal
client_logo: esg
date: July 2026
---
```

Title precedence: `--title` > front matter `title` > first `# H1` in the body
(which is then removed from the content) > filename.

## Supported Markdown

Headings (`#`..`######`), paragraphs, unordered and ordered lists (single
level), GFM pipe tables, blockquotes (`>` → branded callout; a `**bold**`
lead-in becomes the callout heading), horizontal rules (`---`), fenced code
blocks, and inline `**bold**`, `*italic*`, `` `code` ``, `[links](url)`.

## Branding

- Bundled assets in `assets/`: `d55-logo-white.png` (cover, top-right),
  `d55-bg.jpg` (cover background), and `esg-logo-white.png` (an example client
  logo). All embedded as base64 so outputs are self-contained.
- Add more client logos by dropping a white PNG in `assets/` and registering a
  key in `CLIENT_LOGOS` in `md_to_pdf.py`, or just pass a path to `--client-logo`.
- Colours/typography match the D55 deliverables (navy `#1a0a3e`, accent
  `#5dade2`, Inter font). Content pages use Word-style margins via CSS `@page`.

## Verification (per deliverables-toolkit)

The agent cannot see images — measure, don't look:

1. Serve the output folder: `python -m http.server <port>` (background process).
2. Load the HTML with the browser tools and `browser_evaluate` to check: all
   images loaded (`naturalWidth > 0`), expected counts (tables, callouts,
   lists), cover title present, and `document.body.scrollWidth <= innerWidth`
   (no horizontal overflow).
3. Read the PDF back with `pypdf`: assert page count and A4 size (595×842pt),
   and scan for orphaned headings (a page whose last line is a heading).
4. Stop the server and clean up any temporary files.

## Gotchas

- **Fonts**: the Inter font is fetched from Google Fonts at render time
  (Playwright waits for `networkidle`, so the PDF embeds it). The HTML falls
  back to Segoe UI offline — acceptable for the PDF, which is the primary output.
- **Single-level lists**: nested lists are not parsed. Flatten or restructure
  if you need depth.
- **Tables need a separator row** (`---|---`) directly under the header, GFM
  style, or they render as paragraphs.
- **`openpyxl`/binary churn** doesn't apply here, but do restore or clean any
  temporary test outputs so generated HTML/PDF don't clutter commits (see the
  skill's `.gitignore`).
