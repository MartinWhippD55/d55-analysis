"""
Reusable branded-document engine for D55 programmes.

Config-driven: given a BrandConfig (assets, colours, output dir) and a content
dict (DOC of ordered blocks), renders a branded, standalone HTML document
(images embedded as base64) and optionally renders it to A4 PDF via Playwright.

This is the generic engine — it knows nothing about any specific programme.
Callers supply branding and content. See build_programme_doc.py for a worked use.

Block types: section, table, callout, pipeline, layers, cards.
"""
from __future__ import annotations

import base64
import html as html_mod
import mimetypes
from dataclasses import dataclass, field
from pathlib import Path


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

@dataclass
class BrandConfig:
    """Branding + output configuration for a document build."""
    logo: Path
    background: Path
    output_dir: Path
    org_name: str = "D55"
    # Palette (sensible D55 defaults; override per brand)
    ink: str = "#1a0a3e"
    accent: str = "#5dade2"
    accent_dark: str = "#0a4a8c"
    gradient: str = ("linear-gradient(135deg, rgba(26,10,62,0.90) 0%, "
                     "rgba(28,20,88,0.74) 50%, rgba(10,74,140,0.6) 100%)")
    font_import: str = ("https://fonts.googleapis.com/css2?"
                        "family=Inter:wght@300;400;600;700&display=swap")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def b64_uri(path: Path) -> str:
    mime = mimetypes.guess_type(str(path))[0] or "image/png"
    data = base64.b64encode(Path(path).read_bytes()).decode()
    return f"data:{mime};base64,{data}"


def esc(text) -> str:
    return html_mod.escape(str(text))


def _para_list(items):
    return "".join(f"<p>{t}</p>" for t in items or [])


def _bullets(items, cls="bullets"):
    if not items:
        return ""
    lis = "".join(f"<li>{t}</li>" for t in items)
    return f'<ul class="{cls}">{lis}</ul>'


# ---------------------------------------------------------------------------
# Block renderers (body/bullet strings may contain inline HTML)
# ---------------------------------------------------------------------------

def render_section(block):
    heading = f'<h2>{esc(block["heading"])}</h2>' if block.get("heading") else ""
    return (f'<section class="block block-section">{heading}'
            f'{_para_list(block.get("body"))}{_bullets(block.get("bullets"))}</section>')


def render_table(block):
    heading = f'<h2>{esc(block["heading"])}</h2>' if block.get("heading") else ""
    intro = f'<p>{block["intro"]}</p>' if block.get("intro") else ""
    cols = "".join(f"<th>{esc(c)}</th>" for c in block["columns"])
    rows = "".join(
        "<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>"
        for row in block["rows"]
    )
    table = (f'<table class="data-table"><thead><tr>{cols}</tr></thead>'
             f"<tbody>{rows}</tbody></table>")
    return f'<section class="block block-table">{heading}{intro}{table}</section>'


def render_callout(block):
    heading = f'<h3>{esc(block["heading"])}</h3>' if block.get("heading") else ""
    return (f'<section class="block callout">{heading}'
            f'{_para_list(block.get("body"))}{_bullets(block.get("bullets"))}</section>')


def render_pipeline(block):
    heading = f'<h2>{esc(block["heading"])}</h2>' if block.get("heading") else ""
    body = _para_list(block.get("body"))
    steps = block["steps"]
    parts = []
    for i, step in enumerate(steps):
        parts.append(f'<div class="step">{esc(step)}</div>')
        if i < len(steps) - 1:
            parts.append('<div class="step-arrow">&#9654;</div>')
    caption = f'<figcaption>{esc(block["caption"])}</figcaption>' if block.get("caption") else ""
    return (f'<section class="block block-pipeline">{heading}{body}'
            f'<figure class="flow"><div class="pipeline">{"".join(parts)}</div>{caption}</figure></section>')


def render_layers(block):
    heading = f'<h2>{esc(block["heading"])}</h2>' if block.get("heading") else ""
    body = _para_list(block.get("body"))
    lanes_html = ""
    lanes = block["lanes"]
    for i, lane in enumerate(lanes):
        nodes = "".join(f'<div class="node">{esc(n)}</div>' for n in lane["nodes"])
        lanes_html += (f'<div class="lane"><div class="lane-label">{esc(lane["label"])}</div>'
                       f'<div class="lane-nodes">{nodes}</div></div>')
        if i < len(lanes) - 1:
            lanes_html += '<div class="lane-arrow">&#9660;</div>'
    caption = f'<figcaption>{esc(block["caption"])}</figcaption>' if block.get("caption") else ""
    return (f'<section class="block block-layers">{heading}{body}'
            f'<figure class="flow"><div class="layers">{lanes_html}</div>{caption}</figure></section>')


def render_cards(block):
    heading = f'<h2>{esc(block["heading"])}</h2>' if block.get("heading") else ""
    intro = f'<p>{block["intro"]}</p>' if block.get("intro") else ""
    cards = ""
    for card in block["cards"]:
        tag = f'<span class="card-tag">{esc(card["tag"])}</span>' if card.get("tag") else ""
        title = f'<h3>{esc(card["title"])}</h3>' if card.get("title") else ""
        cards += (f'<div class="card">{tag}{title}'
                  f'{_para_list(card.get("body"))}{_bullets(card.get("bullets"))}</div>')
    return f'<section class="block block-cards">{heading}{intro}<div class="cards">{cards}</div></section>'


RENDERERS = {
    "section": render_section,
    "table": render_table,
    "callout": render_callout,
    "pipeline": render_pipeline,
    "layers": render_layers,
    "cards": render_cards,
}


# ---------------------------------------------------------------------------
# Stylesheet (config-driven; print-oriented)
# ---------------------------------------------------------------------------

def build_css(cfg: BrandConfig, bg_uri: str) -> str:
    return f"""
@page {{ size: A4 portrait; margin: 22mm 20mm 20mm 20mm; }}
@page cover {{ size: A4 portrait; margin: 0; }}

* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Inter', 'Segoe UI', sans-serif; color: #23232f; font-size: 11pt; line-height: 1.6; }}
h1, h2, h3, h4 {{ color: {cfg.ink}; }}
p {{ margin: 0 0 10px; }}
strong {{ color: {cfg.ink}; }}

.cover {{
    page: cover; position: relative; width: 210mm; height: 297mm;
    background-image: url('{bg_uri}'); background-size: cover; background-position: center;
    overflow: hidden; color: #fff; page-break-after: always;
}}
.cover::after {{ content: ''; position: absolute; inset: 0; background: {cfg.gradient}; }}
.cover > * {{ position: relative; z-index: 1; }}
.cover .logo {{ position: absolute; top: 32px; right: 36px; height: 46px; }}
.cover .cover-inner {{ position: absolute; top: 36%; left: 52px; right: 52px; }}
.cover .eyebrow {{ font-size: 13pt; font-weight: 300; letter-spacing: 2px; text-transform: uppercase; opacity: 0.82; margin-bottom: 14px; }}
.cover h1 {{ color: #fff; font-size: 40pt; font-weight: 700; line-height: 1.08; max-width: 90%; }}
.cover .subtitle {{ font-size: 15pt; font-weight: 300; opacity: 0.88; margin-top: 18px; max-width: 80%; }}
.cover .badge {{
    display: inline-block; margin-top: 28px; padding: 9px 18px;
    background: rgba(93,173,226,0.25); border: 1px solid rgba(93,173,226,0.5);
    border-radius: 4px; font-size: 12pt; font-weight: 600; color: #d7ecfa;
}}
.cover .meta {{ position: absolute; bottom: 50px; left: 52px; }}
.cover .meta .org {{ font-size: 12pt; font-weight: 600; }}
.cover .meta .date {{ font-size: 10pt; opacity: 0.62; margin-top: 2px; }}

.content {{ padding-top: 2px; }}
.block {{ margin-bottom: 22px; }}
h2 {{ font-size: 17pt; font-weight: 700; margin-bottom: 12px; padding-bottom: 7px; border-bottom: 2px solid #e2e2ee; }}
h3 {{ font-size: 12.5pt; font-weight: 600; margin-bottom: 7px; }}

ul.bullets {{ list-style: none; margin: 6px 0; }}
ul.bullets li {{ position: relative; padding-left: 18px; margin-bottom: 6px; }}
ul.bullets li::before {{ content: '\\203A'; position: absolute; left: 0; top: -1px; color: {cfg.accent}; font-weight: bold; font-size: 13pt; line-height: 1.6; }}

table.data-table {{ width: 100%; border-collapse: collapse; font-size: 9.5pt; margin-top: 8px; }}
table.data-table th {{ background: {cfg.ink}; color: #d7ecfa; text-align: left; padding: 8px 10px; font-size: 8.5pt; text-transform: uppercase; letter-spacing: 0.4px; }}
table.data-table td {{ padding: 7px 10px; border-bottom: 1px solid #e6e6f0; vertical-align: top; }}
table.data-table tr:nth-child(even) td {{ background: #f6f6fb; }}

.callout {{ background: #f0f6fc; border-left: 4px solid {cfg.accent}; padding: 14px 18px; border-radius: 0 4px 4px 0; }}
.callout h3 {{ color: {cfg.accent_dark}; }}
.callout.pitch {{ background: #f4f0fb; border-left-color: #6b4ea8; }}
.callout.pitch p {{ font-size: 12.5pt; font-style: italic; color: #2e1a5e; }}

figure.flow {{ margin: 12px 0 6px; page-break-inside: avoid; }}
figcaption {{ font-size: 8.5pt; color: #6a6a80; margin-top: 8px; font-style: italic; }}
.layers {{ display: flex; flex-direction: column; gap: 4px; }}
.lane {{ border: 1.5px solid #c9c9dc; border-radius: 6px; background: #f8f8fc; padding: 9px 11px 11px; }}
.lane-label {{ font-size: 8pt; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; color: {cfg.accent_dark}; margin-bottom: 8px; }}
.lane-nodes {{ display: flex; flex-wrap: wrap; gap: 8px; }}
.lane-nodes .node {{ flex: 1; min-width: 110px; text-align: center; background: #fff; border: 1.5px solid {cfg.accent}; border-radius: 5px; padding: 9px 6px; font-size: 8.5pt; font-weight: 600; color: {cfg.ink}; }}
.lane-arrow {{ text-align: center; color: {cfg.accent}; font-size: 12pt; line-height: 1; margin: -1px 0; }}
.pipeline {{ display: flex; align-items: stretch; gap: 4px; }}
.pipeline .step {{ flex: 1; text-align: center; background: {cfg.ink}; color: #fff; border-radius: 5px; padding: 11px 6px; font-size: 8pt; font-weight: 600; display: flex; align-items: center; justify-content: center; }}
.pipeline .step-arrow {{ color: {cfg.accent}; font-size: 11pt; align-self: center; }}

.cards {{ display: flex; flex-direction: column; gap: 12px; }}
.card {{ border: 1px solid #d8d8e6; border-left: 4px solid {cfg.accent}; border-radius: 0 6px 6px 0; padding: 13px 16px; background: #fcfcfe; page-break-inside: avoid; }}
.card h3 {{ margin-bottom: 6px; }}
.card-tag {{ display: inline-block; background: {cfg.ink}; color: #d7ecfa; font-size: 8pt; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; padding: 3px 9px; border-radius: 3px; margin-bottom: 8px; }}

.section-break {{ page-break-before: always; }}

h2, h3, h4 {{ break-after: avoid; page-break-after: avoid; }}
h2 + *, h3 + * {{ break-before: avoid; page-break-before: avoid; }}
figure.flow, .callout, .block-layers, .block-pipeline, .card {{ break-inside: avoid; page-break-inside: avoid; }}
table.data-table {{ break-inside: auto; }}
table.data-table tr {{ break-inside: avoid; page-break-inside: avoid; }}
table.data-table thead {{ display: table-header-group; }}
p, li {{ orphans: 2; widows: 2; }}

@media screen {{
    body {{ background: #52526a; }}
    .cover {{ margin: 0 auto; box-shadow: 0 4px 24px rgba(0,0,0,0.4); }}
    .content {{ width: 210mm; min-height: 297mm; margin: 24px auto; background: #fff; padding: 22mm 20mm; box-shadow: 0 4px 24px rgba(0,0,0,0.4); }}
}}
"""


def build_html(doc: dict, cfg: BrandConfig) -> str:
    logo_uri = b64_uri(cfg.logo)
    bg_uri = b64_uri(cfg.background)

    blocks_html = ""
    for block in doc["blocks"]:
        renderer = RENDERERS.get(block["type"])
        if not renderer:
            raise ValueError(f"Unknown block type: {block['type']}")
        rendered = renderer(block)
        if block.get("variant"):
            rendered = rendered.replace('class="block ', f'class="block {block["variant"]} ', 1)
        if block.get("pageBreak"):
            rendered = rendered.replace('class="block', 'class="block section-break', 1)
        blocks_html += rendered

    badge = f'<div class="badge">{esc(doc["badge"])}</div>' if doc.get("badge") else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{esc(doc['title'])}</title>
<style>
@import url('{cfg.font_import}');
{build_css(cfg, bg_uri)}
</style>
</head>
<body>
<div class="cover">
    <img src="{logo_uri}" class="logo" alt="{esc(cfg.org_name)}">
    <div class="cover-inner">
        <div class="eyebrow">{esc(doc.get('eyebrow', ''))}</div>
        <h1>{esc(doc['title'])}</h1>
        <div class="subtitle">{esc(doc.get('subtitle', ''))}</div>
        {badge}
    </div>
    <div class="meta">
        <div class="org">{esc(cfg.org_name)}</div>
        <div class="date">{esc(doc.get('date', ''))}</div>
    </div>
</div>
<div class="content">
{blocks_html}
</div>
</body>
</html>"""


def render_pdf(html_path: Path, pdf_path: Path):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(Path(html_path).resolve().as_uri(), wait_until="networkidle")
        page.pdf(path=str(pdf_path), print_background=True, prefer_css_page_size=True)
        browser.close()


def build(doc: dict, cfg: BrandConfig, make_pdf: bool = True) -> Path:
    """Render a content dict to branded HTML (+ optional PDF). Returns the HTML path."""
    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    slug = doc.get("slug", "document")
    html = build_html(doc, cfg)
    html_path = cfg.output_dir / f"{slug}.html"
    html_path.write_text(html, encoding="utf-8")
    print(f"HTML written: {html_path}  ({len(html) / 1024:.0f} KB)")

    if make_pdf:
        pdf_path = cfg.output_dir / f"{slug}.pdf"
        try:
            render_pdf(html_path, pdf_path)
            print(f"PDF written:  {pdf_path}")
        except Exception as exc:  # noqa: BLE001
            print(f"PDF render skipped ({exc}).")
            print("Install browser with: python -m playwright install chromium")
    return html_path
