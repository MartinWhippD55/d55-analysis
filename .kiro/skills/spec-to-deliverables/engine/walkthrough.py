"""
Block-based branded document engine (standalone HTML + A4 PDF).

A content module supplies a ``DOC`` dict; this engine renders it into a branded,
fully self-contained HTML document (images embedded as base64), then Playwright
renders the HTML to PDF. The engine knows nothing about any specific document —
add a document by writing a new content module, no engine changes.

Content model (DOC dict):
    {
        "title": str,                 # cover title (required)
        "subtitle": str?,             # cover subtitle
        "eyebrow": str?,              # cover kicker (else BrandConfig.eyebrow)
        "effort": str?,               # cover badge, e.g. "~13.5 developer days"
        "date": str?,                 # cover date (else BrandConfig.date)
        "slug": str?,                 # output filename stem (else slugified title)
        "blocks": [ <block>, ... ],
    }

Block types:
    {"type": "section",  "heading": str?, "body": [str], "bullets": [str]}
    {"type": "table",    "heading": str?, "intro": str?, "columns": [str], "rows": [[str]]}
    {"type": "screens",  "heading": str?, "intro": str?, "screens": [
        {"image": path, "title": str, "body": [str]?, "interactions": [str]?, "data": [str]?}]}
    {"type": "diagram",  "heading": str?, "image": path, "caption": str?, "body": [str]?, "maxHeight": int?}
    {"type": "callout",  "heading": str?, "body": [str]?, "bullets": [str]?}
    {"type": "layers",   "heading": str?, "body": [str]?, "caption": str?,
        "lanes": [{"label": str, "nodes": [str]}]}
    {"type": "pipeline", "heading": str?, "body": [str]?, "caption": str?, "steps": [str]}
    {"type": "entities", "heading": str?, "intro": str?, "table": str?,
        "entities": [{"name": str, "pk": str, "sk": str?, "note": str?,
                      "attributes": [[name, type, desc], ...]}],
        "gsi": [{"name": str, "pk": str, "sk": str?, "enables": str?}]?}

Any block may carry ``"pageBreak": True`` to start a new page before it.

Usage (as a library):
    from engine.walkthrough import build_html, render_pdf
    from engine.brand import BrandConfig
    html = build_html(DOC, BrandConfig.from_assets_dir("deliverables/<spec>/assets"))
"""
from __future__ import annotations

import html as html_mod
import re
from pathlib import Path
from typing import Optional

from .brand import BrandConfig, b64_uri
from .css import build_css


def esc(text) -> str:
    return html_mod.escape(str(text))


def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")
    return s or "document"


def _para_list(items) -> str:
    return "".join(f"<p>{esc(t)}</p>" for t in items or [])


def _bullets(items, cls="bullets") -> str:
    if not items:
        return ""
    lis = "".join(f"<li>{esc(t)}</li>" for t in items)
    return f'<ul class="{cls}">{lis}</ul>'


def _resolve_image(path, base_dir: Optional[Path]) -> Path:
    """Resolve an image path: absolute, else relative to base_dir, else as-is."""
    p = Path(path)
    if p.is_absolute() and p.exists():
        return p
    if base_dir is not None:
        candidate = Path(base_dir) / path
        if candidate.exists():
            return candidate
    return p


# ---------------------------------------------------------------------------
# Block renderers. Each takes (block, ctx) where ctx carries base_dir.
# ---------------------------------------------------------------------------

def _heading(block, tag="h2") -> str:
    return f"<{tag}>{esc(block['heading'])}</{tag}>" if block.get("heading") else ""


def render_section(block, ctx) -> str:
    return (
        '<section class="block block-section">'
        f"{_heading(block)}{_para_list(block.get('body'))}{_bullets(block.get('bullets'))}"
        "</section>"
    )


def render_table(block, ctx) -> str:
    intro = _para_list([block["intro"]]) if block.get("intro") else ""
    cols = "".join(f"<th>{esc(c)}</th>" for c in block["columns"])
    rows = ""
    for row in block["rows"]:
        rows += "<tr>" + "".join(f"<td>{esc(c)}</td>" for c in row) + "</tr>"
    table = (
        f'<table class="data-table"><thead><tr>{cols}</tr></thead>'
        f"<tbody>{rows}</tbody></table>"
    )
    return f'<section class="block block-table">{_heading(block)}{intro}{table}</section>'


def render_diagram(block, ctx) -> str:
    uri = b64_uri(_resolve_image(block["image"], ctx["base_dir"]))
    caption = f'<figcaption>{esc(block["caption"])}</figcaption>' if block.get("caption") else ""
    style = f' style="max-height:{block["maxHeight"]}mm"' if block.get("maxHeight") else ""
    return (
        f'<section class="block block-diagram">{_heading(block)}{_para_list(block.get("body"))}'
        f'<figure class="diagram"><img src="{uri}" alt="diagram"{style}>{caption}</figure></section>'
    )


def render_callout(block, ctx) -> str:
    return (
        '<section class="block callout">'
        f"{_heading(block, 'h3')}{_para_list(block.get('body'))}{_bullets(block.get('bullets'))}"
        "</section>"
    )


def render_screens(block, ctx) -> str:
    intro = _para_list([block["intro"]]) if block.get("intro") else ""
    cards = ""
    for scr in block["screens"]:
        uri = b64_uri(_resolve_image(scr["image"], ctx["base_dir"]))
        interactions = (
            f'<div class="col"><h4>Key interactions</h4>{_bullets(scr["interactions"])}</div>'
            if scr.get("interactions") else ""
        )
        data = (
            f'<div class="col"><h4>Behind the screen</h4>{_bullets(scr["data"])}</div>'
            if scr.get("data") else ""
        )
        detail = f'<div class="cols">{interactions}{data}</div>' if (interactions or data) else ""
        cards += (
            '<div class="screen">'
            f'<h3>{esc(scr["title"])}</h3>'
            f'<figure class="shot"><img src="{uri}" alt="{esc(scr["title"])}"></figure>'
            f"{_para_list(scr.get('body'))}{detail}</div>"
        )
    return f'<section class="block block-screens">{_heading(block)}{intro}{cards}</section>'


def render_layers(block, ctx) -> str:
    lanes = block["lanes"]
    lanes_html = ""
    for i, lane in enumerate(lanes):
        nodes = "".join(f'<div class="node">{esc(n)}</div>' for n in lane["nodes"])
        lanes_html += (
            f'<div class="lane"><div class="lane-label">{esc(lane["label"])}</div>'
            f'<div class="lane-nodes">{nodes}</div></div>'
        )
        if i < len(lanes) - 1:
            lanes_html += '<div class="lane-arrow">&#9660;</div>'
    caption = f'<figcaption>{esc(block["caption"])}</figcaption>' if block.get("caption") else ""
    return (
        f'<section class="block block-layers">{_heading(block)}{_para_list(block.get("body"))}'
        f'<figure class="flow"><div class="layers">{lanes_html}</div>{caption}</figure></section>'
    )


def render_pipeline(block, ctx) -> str:
    steps = block["steps"]
    parts = []
    for i, step in enumerate(steps):
        parts.append(f'<div class="step">{esc(step)}</div>')
        if i < len(steps) - 1:
            parts.append('<div class="step-arrow">&#9654;</div>')
    caption = f'<figcaption>{esc(block["caption"])}</figcaption>' if block.get("caption") else ""
    return (
        f'<section class="block block-pipeline">{_heading(block)}{_para_list(block.get("body"))}'
        f'<figure class="flow"><div class="pipeline">{"".join(parts)}</div>{caption}</figure></section>'
    )


def render_entities(block, ctx) -> str:
    intro = _para_list([block["intro"]]) if block.get("intro") else ""
    table_label = (
        f'<div class="table-name">Table: <code>{esc(block["table"])}</code></div>'
        if block.get("table") else ""
    )
    cards = ""
    for ent in block["entities"]:
        keys = f'<span class="key"><span class="key-label">PK</span><code>{esc(ent["pk"])}</code></span>'
        if ent.get("sk"):
            keys += f'<span class="key"><span class="key-label">SK</span><code>{esc(ent["sk"])}</code></span>'
        note = f'<p class="entity-note">{esc(ent["note"])}</p>' if ent.get("note") else ""
        rows = ""
        for name, typ, desc in ent["attributes"]:
            rows += (
                f'<tr><td><code>{esc(name)}</code></td>'
                f'<td class="type">{esc(typ)}</td><td>{esc(desc)}</td></tr>'
            )
        table = (
            '<table class="data-table attr-table">'
            "<thead><tr><th>Attribute</th><th>Type</th><th>Description</th></tr></thead>"
            f"<tbody>{rows}</tbody></table>"
        )
        cards += (
            f'<div class="entity"><h3>{esc(ent["name"])}</h3>'
            f'<div class="keys">{keys}</div>{note}{table}</div>'
        )
    gsi_html = ""
    if block.get("gsi"):
        grows = ""
        for g in block["gsi"]:
            grows += (
                f'<tr><td>{esc(g["name"])}</td>'
                f'<td><code>{esc(g["pk"])}</code></td>'
                f'<td><code>{esc(g.get("sk", "-"))}</code></td>'
                f'<td>{esc(g.get("enables", ""))}</td></tr>'
            )
        gsi_html = (
            '<div class="gsi-block"><h3>Global Secondary Indexes</h3>'
            '<table class="data-table"><thead><tr>'
            "<th>Index</th><th>GSI PK</th><th>GSI SK</th><th>Enables</th>"
            f"</tr></thead><tbody>{grows}</tbody></table></div>"
        )
    return (
        f'<section class="block block-entities">{_heading(block)}{intro}{table_label}'
        f"{cards}{gsi_html}</section>"
    )


RENDERERS = {
    "section": render_section,
    "table": render_table,
    "diagram": render_diagram,
    "callout": render_callout,
    "screens": render_screens,
    "layers": render_layers,
    "pipeline": render_pipeline,
    "entities": render_entities,
}


def _maybe_img(path: Optional[Path], cls: str, alt: str) -> str:
    if path and Path(path).exists():
        return f'<img src="{b64_uri(Path(path))}" class="{cls}" alt="{esc(alt)}">'
    return ""


def build_html(doc: dict, brand: Optional[BrandConfig] = None, base_dir=None) -> str:
    """Render a DOC dict into a branded, self-contained HTML string.

    ``base_dir`` (default: cwd) is where relative image paths in the DOC resolve.
    """
    brand = brand or BrandConfig()
    base_dir = Path(base_dir) if base_dir is not None else None
    ctx = {"base_dir": base_dir}

    blocks_html = ""
    for block in doc["blocks"]:
        renderer = RENDERERS.get(block["type"])
        if not renderer:
            raise ValueError(f"Unknown block type: {block['type']}")
        rendered = renderer(block, ctx)
        if block.get("pageBreak"):
            rendered = rendered.replace('class="block', 'class="block section-break', 1)
        blocks_html += rendered

    eyebrow = doc.get("eyebrow", brand.eyebrow)
    eyebrow_html = f'<div class="eyebrow">{esc(eyebrow)}</div>' if eyebrow else ""
    subtitle_html = f'<div class="subtitle">{esc(doc["subtitle"])}</div>' if doc.get("subtitle") else ""
    effort_html = f'<div class="effort">{esc(doc["effort"])}</div>' if doc.get("effort") else ""
    date = doc.get("date") or brand.date or ""

    logo_html = _maybe_img(brand.logo_path, "logo", brand.org_name)
    client_html = _maybe_img(brand.client_logo_path, "client-logo", "client")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{esc(doc['title'])}</title>
<style>
@import url('{brand.google_font_url}');
{build_css(brand)}
</style>
</head>
<body>
<div class="cover">
    {logo_html}
    {client_html}
    <div class="cover-inner">
        {eyebrow_html}
        <h1>{esc(doc['title'])}</h1>
        {subtitle_html}
        {effort_html}
    </div>
    <div class="meta">
        <div class="org">{esc(brand.org_name)}</div>
        <div class="date">{esc(date)}</div>
    </div>
</div>
<div class="content">
{blocks_html}
</div>
</body>
</html>"""


def render_pdf(html_path, pdf_path) -> None:
    """Render an HTML file to PDF via Playwright (Chromium)."""
    from playwright.sync_api import sync_playwright

    html_path, pdf_path = Path(html_path), Path(pdf_path)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
        page.pdf(path=str(pdf_path), print_background=True, prefer_css_page_size=True)
        browser.close()


def build_document(doc: dict, out_dir, brand: Optional[BrandConfig] = None,
                   base_dir=None, make_pdf: bool = True) -> dict:
    """Write ``<out_dir>/<slug>.html`` (+ ``.pdf``) for a DOC. Returns paths written."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = doc.get("slug") or slugify(doc["title"])
    html = build_html(doc, brand=brand, base_dir=base_dir)
    html_path = out_dir / f"{slug}.html"
    html_path.write_text(html, encoding="utf-8")
    result = {"html": html_path, "pdf": None}
    if make_pdf:
        pdf_path = out_dir / f"{slug}.pdf"
        render_pdf(html_path, pdf_path)
        result["pdf"] = pdf_path
    return result
