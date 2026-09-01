"""
Reusable walkthrough document generator for the BRYT Report Builder POC deliverables.

Stripped clone of `../../report-builder/deliverables/walkthroughs/build_walkthrough.py`.
The engine is content-agnostic: a content module (e.g. report_builder_poc.py)
exposes a DOC dict, this engine renders it into a branded, standalone HTML
document with embedded (base64) images, then Playwright renders the HTML to PDF.

Content model (DOC dict):
{
    "slug": "report-builder-poc",
    "title": "Report Builder",
    "subtitle": "Proof of Concept - Technical Walkthrough",
    "eyebrow": "Self-Service Reporting",   # cover eyebrow line (optional)
    "effort": "~6.8 developer days",         # cover badge (optional)
    "date": "August 2026",
    "blocks": [ <block>, ... ]
}

Block types: section, table, screens, diagram, callout, layers, pipeline, entities.

Usage:
    python analysis/BRYT/report-builder-poc/deliverables/walkthroughs/build_walkthrough.py report_builder_poc
"""
import base64
import html as html_mod
import importlib
import mimetypes
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # deliverables/
ASSETS = ROOT / "assets"
OUTPUTS = ROOT / "outputs"


def _b64_uri(path: Path) -> str:
    mime = mimetypes.guess_type(str(path))[0] or "image/png"
    data = base64.b64encode(path.read_bytes()).decode()
    return f"data:{mime};base64,{data}"


def esc(text: str) -> str:
    return html_mod.escape(str(text))


def _para_list(items):
    return "".join(f"<p>{esc(t)}</p>" for t in items or [])


def _bullets(items, cls="bullets"):
    if not items:
        return ""
    lis = "".join(f"<li>{esc(t)}</li>" for t in items)
    return f'<ul class="{cls}">{lis}</ul>'


def _resolve(path: str) -> Path:
    """Resolve an image path relative to the deliverables root."""
    p = Path(path)
    if p.is_absolute() and p.exists():
        return p
    candidate = (ROOT / path).resolve()
    if candidate.exists():
        return candidate
    return Path(path)


# ---------------------------------------------------------------------------
# Block renderers
# ---------------------------------------------------------------------------

def render_section(block):
    heading = f'<h2>{esc(block["heading"])}</h2>' if block.get("heading") else ""
    body = _para_list(block.get("body"))
    bullets = _bullets(block.get("bullets"))
    return f'<section class="block block-section">{heading}{body}{bullets}</section>'


def render_table(block):
    heading = f'<h2>{esc(block["heading"])}</h2>' if block.get("heading") else ""
    intro = _para_list([block["intro"]]) if block.get("intro") else ""
    cols = "".join(f"<th>{esc(c)}</th>" for c in block["columns"])
    rows = ""
    for row in block["rows"]:
        cells = "".join(f"<td>{esc(c)}</td>" for c in row)
        rows += f"<tr>{cells}</tr>"
    table = (
        f'<table class="data-table"><thead><tr>{cols}</tr></thead>'
        f"<tbody>{rows}</tbody></table>"
    )
    return f'<section class="block block-table">{heading}{intro}{table}</section>'


def render_diagram(block):
    heading = f'<h2>{esc(block["heading"])}</h2>' if block.get("heading") else ""
    body = _para_list(block.get("body"))
    uri = _b64_uri(_resolve(block["image"]))
    caption = f'<figcaption>{esc(block["caption"])}</figcaption>' if block.get("caption") else ""
    style = f' style="max-height:{block["maxHeight"]}mm"' if block.get("maxHeight") else ""
    return (
        f'<section class="block block-diagram">{heading}{body}'
        f'<figure class="diagram"><img src="{uri}" alt="diagram"{style}>{caption}</figure></section>'
    )


def render_callout(block):
    heading = f'<h3>{esc(block["heading"])}</h3>' if block.get("heading") else ""
    body = _para_list(block.get("body"))
    bullets = _bullets(block.get("bullets"))
    return f'<section class="block callout">{heading}{body}{bullets}</section>'


def render_screens(block):
    heading = f'<h2>{esc(block["heading"])}</h2>' if block.get("heading") else ""
    intro = _para_list([block["intro"]]) if block.get("intro") else ""
    cards = ""
    for scr in block["screens"]:
        uri = _b64_uri(_resolve(scr["image"]))
        body = _para_list(scr.get("body"))
        interactions = ""
        if scr.get("interactions"):
            interactions = (
                '<div class="col"><h4>Key interactions</h4>'
                f'{_bullets(scr["interactions"])}</div>'
            )
        data = ""
        if scr.get("data"):
            data = (
                '<div class="col"><h4>Behind the screen</h4>'
                f'{_bullets(scr["data"])}</div>'
            )
        detail = ""
        if interactions or data:
            detail = f'<div class="cols">{interactions}{data}</div>'
        cards += (
            '<div class="screen">'
            f'<h3>{esc(scr["title"])}</h3>'
            f'<figure class="shot"><img src="{uri}" alt="{esc(scr["title"])}"></figure>'
            f"{body}{detail}"
            "</div>"
        )
    return f'<section class="block block-screens">{heading}{intro}{cards}</section>'


def render_layers(block):
    """Layered architecture diagram: stacked lanes of boxes, arrow between lanes."""
    heading = f'<h2>{esc(block["heading"])}</h2>' if block.get("heading") else ""
    body = _para_list(block.get("body"))
    lanes_html = ""
    lanes = block["lanes"]
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
        f'<section class="block block-layers">{heading}{body}'
        f'<figure class="flow"><div class="layers">{lanes_html}</div>{caption}</figure></section>'
    )


def render_pipeline(block):
    """Left-to-right pipeline: sequence of steps connected by arrows."""
    heading = f'<h2>{esc(block["heading"])}</h2>' if block.get("heading") else ""
    body = _para_list(block.get("body"))
    steps = block["steps"]
    parts = []
    for i, step in enumerate(steps):
        parts.append(f'<div class="step">{esc(step)}</div>')
        if i < len(steps) - 1:
            parts.append('<div class="step-arrow">&#9654;</div>')
    caption = f'<figcaption>{esc(block["caption"])}</figcaption>' if block.get("caption") else ""
    return (
        f'<section class="block block-pipeline">{heading}{body}'
        f'<figure class="flow"><div class="pipeline">{"".join(parts)}</div>{caption}</figure></section>'
    )


def render_entities(block):
    """Entity/record definitions: key-pattern cards + attribute tables."""
    heading = f'<h2>{esc(block["heading"])}</h2>' if block.get("heading") else ""
    intro = _para_list([block["intro"]]) if block.get("intro") else ""
    table_label = ""
    if block.get("table"):
        table_label = f'<div class="table-name">Table: <code>{esc(block["table"])}</code></div>'

    cards = ""
    for ent in block["entities"]:
        keys = f'<span class="key"><span class="key-label">PK</span><code>{esc(ent["pk"])}</code></span>'
        if ent.get("sk"):
            keys += f'<span class="key"><span class="key-label">SK</span><code>{esc(ent["sk"])}</code></span>'
        note = f'<p class="entity-note">{esc(ent["note"])}</p>' if ent.get("note") else ""
        rows = ""
        for attr in ent["attributes"]:
            name, typ, desc = attr
            rows += (
                f'<tr><td><code>{esc(name)}</code></td>'
                f'<td class="type">{esc(typ)}</td><td>{esc(desc)}</td></tr>'
            )
        table = (
            '<table class="data-table attr-table">'
            '<thead><tr><th>Attribute</th><th>Type</th><th>Description</th></tr></thead>'
            f'<tbody>{rows}</tbody></table>'
        )
        cards += (
            '<div class="entity">'
            f'<h3>{esc(ent["name"])}</h3>'
            f'<div class="keys">{keys}</div>{note}{table}</div>'
        )

    return (
        f'<section class="block block-entities">{heading}{intro}{table_label}{cards}</section>'
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


# ---------------------------------------------------------------------------
# Stylesheet (print-oriented, D55 + Bryt branding)
# ---------------------------------------------------------------------------

def build_css(bg_uri: str) -> str:
    return f"""
/* Content pages: Word-style margins, repeated on every page */
@page {{ size: A4 portrait; margin: 24mm 22mm 22mm 22mm; }}
/* Cover page: full bleed */
@page cover {{ size: A4 portrait; margin: 0; }}

* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    font-family: 'Inter', 'Segoe UI', sans-serif;
    color: #23232f;
    font-size: 11pt;
    line-height: 1.65;
}}
h1, h2, h3, h4 {{ color: #1a0a3e; }}
p {{ margin: 0 0 10px; }}

/* Cover */
.cover {{
    page: cover;
    position: relative;
    width: 210mm;
    height: 297mm;
    background-image: url('{bg_uri}');
    background-size: cover;
    background-position: center;
    overflow: hidden;
    color: #fff;
    page-break-after: always;
}}
.cover::after {{
    content: '';
    position: absolute; inset: 0;
    background: linear-gradient(135deg, rgba(26,10,62,0.88) 0%, rgba(28,20,88,0.72) 50%, rgba(10,74,140,0.6) 100%);
}}
.cover > * {{ position: relative; z-index: 1; }}
.cover .logo {{ position: absolute; top: 30px; right: 34px; height: 50px; }}
.cover .bryt {{ position: absolute; bottom: 46px; right: 46px; height: 42px; }}
.cover .cover-inner {{ position: absolute; top: 40%; left: 52px; right: 52px; }}
.cover .eyebrow {{
    font-size: 13pt; font-weight: 300; letter-spacing: 2px;
    text-transform: uppercase; opacity: 0.8; margin-bottom: 14px;
}}
.cover h1 {{ color: #fff; font-size: 38pt; font-weight: 700; line-height: 1.1; max-width: 88%; }}
.cover .subtitle {{ font-size: 16pt; font-weight: 300; opacity: 0.85; margin-top: 16px; }}
.cover .effort {{
    display: inline-block; margin-top: 30px; padding: 9px 18px;
    background: rgba(93,173,226,0.25); border: 1px solid rgba(93,173,226,0.5);
    border-radius: 4px; font-size: 13pt; font-weight: 600; color: #d7ecfa;
}}
.cover .meta {{ position: absolute; bottom: 50px; left: 52px; }}
.cover .meta .org {{ font-size: 12pt; font-weight: 600; }}
.cover .meta .date {{ font-size: 10pt; opacity: 0.6; margin-top: 2px; }}

/* Content */
.content {{ padding-top: 2px; }}
.block {{ margin-bottom: 24px; }}
h2 {{
    font-size: 17pt; font-weight: 700; margin-bottom: 12px;
    padding-bottom: 7px; border-bottom: 2px solid #e2e2ee;
}}
h3 {{ font-size: 13pt; font-weight: 600; margin-bottom: 7px; }}
h4 {{ font-size: 9.5pt; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #0a4a8c; margin-bottom: 6px; }}

ul.bullets {{ list-style: none; margin: 6px 0; }}
ul.bullets li {{ position: relative; padding-left: 18px; margin-bottom: 6px; }}
ul.bullets li::before {{
    content: '\\203A'; position: absolute; left: 0; top: -1px;
    color: #5dade2; font-weight: bold; font-size: 13pt;
}}

/* Tables */
table.data-table {{ width: 100%; border-collapse: collapse; font-size: 10pt; margin-top: 8px; }}
table.data-table th {{
    background: #1a0a3e; color: #d7ecfa; text-align: left;
    padding: 8px 11px; font-size: 8.5pt; text-transform: uppercase; letter-spacing: 0.4px;
}}
table.data-table td {{ padding: 7px 11px; border-bottom: 1px solid #e6e6f0; vertical-align: top; }}
table.data-table tr:nth-child(even) td {{ background: #f6f6fb; }}

/* Diagrams */
figure.diagram {{ text-align: center; margin-top: 10px; page-break-inside: avoid; }}
figure.diagram img {{ max-width: 100%; max-height: 150mm; border: 1px solid #e2e2ee; border-radius: 4px; }}
figcaption {{ font-size: 8.5pt; color: #6a6a80; margin-top: 8px; font-style: italic; }}

/* Screens */
.screen {{ page-break-inside: avoid; margin-bottom: 26px; }}
figure.shot {{ margin: 8px 0 12px; }}
figure.shot img {{ width: 100%; border: 1px solid #d8d8e6; border-radius: 5px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
.cols {{ display: flex; gap: 26px; margin-top: 10px; }}
.cols .col {{ flex: 1; }}

/* Callout */
.callout {{
    background: #f0f6fc; border-left: 4px solid #5dade2;
    padding: 14px 18px; border-radius: 0 4px 4px 0;
}}
.callout h3 {{ color: #0a4a8c; }}

/* Flow diagrams (CSS-rendered) */
figure.flow {{ margin: 12px 0 6px; page-break-inside: avoid; }}
.layers {{ display: flex; flex-direction: column; gap: 4px; }}
.lane {{
    border: 1.5px solid #c9c9dc; border-radius: 6px; background: #f8f8fc;
    padding: 9px 11px 11px;
}}
.lane-label {{
    font-size: 8pt; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px;
    color: #0a4a8c; margin-bottom: 8px;
}}
.lane-nodes {{ display: flex; flex-wrap: wrap; gap: 8px; }}
.lane-nodes .node {{
    flex: 1; min-width: 110px; text-align: center;
    background: #fff; border: 1.5px solid #5dade2; border-radius: 5px;
    padding: 9px 6px; font-size: 8.5pt; font-weight: 600; color: #1a0a3e;
}}
.lane-arrow {{ text-align: center; color: #5dade2; font-size: 12pt; line-height: 1; margin: -1px 0; }}

.pipeline {{ display: flex; align-items: stretch; gap: 4px; }}
.pipeline .step {{
    flex: 1; text-align: center; background: #1a0a3e; color: #fff;
    border-radius: 5px; padding: 11px 6px; font-size: 8pt; font-weight: 600;
    display: flex; align-items: center; justify-content: center;
}}
.pipeline .step-arrow {{ color: #5dade2; font-size: 11pt; align-self: center; }}

/* Entity definitions */
.table-name {{ font-size: 10pt; color: #23232f; margin-bottom: 14px; }}
.table-name code {{ background: #1a0a3e; color: #d7ecfa; padding: 2px 8px; border-radius: 3px; font-size: 9.5pt; }}
.entity {{
    border: 1px solid #d8d8e6; border-radius: 6px; padding: 12px 14px;
    margin-bottom: 14px; page-break-inside: avoid; background: #fcfcfe;
}}
.entity h3 {{ margin-bottom: 8px; }}
.entity .keys {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 10px; }}
.entity .key {{
    display: inline-flex; align-items: stretch; border-radius: 4px; overflow: hidden;
    border: 1px solid #5dade2; font-size: 9pt;
}}
.entity .key-label {{
    background: #5dade2; color: #fff; font-weight: 700; padding: 3px 8px;
    display: flex; align-items: center;
}}
.entity .key code {{ padding: 3px 9px; color: #1a0a3e; background: #eaf4fb; display: flex; align-items: center; }}
.entity .entity-note {{ font-size: 9.5pt; color: #55556a; margin-bottom: 8px; }}
code {{ font-family: 'Consolas', 'Monaco', monospace; }}
table.attr-table {{ font-size: 9pt; }}
table.attr-table td code {{ font-size: 8.5pt; color: #0a4a8c; }}
table.attr-table td.type {{ color: #6a6a80; font-style: italic; white-space: nowrap; }}

.section-break {{ page-break-before: always; }}

/* Page-break control: keep headings with their content, avoid awkward splits */
h2, h3, h4 {{ break-after: avoid; page-break-after: avoid; }}
h2 + *, h3 + * {{ break-before: avoid; page-break-before: avoid; }}
figure.flow, figure.diagram, .callout, .block-layers, .block-pipeline {{
    break-inside: avoid; page-break-inside: avoid;
}}
table.data-table {{ break-inside: auto; }}
table.data-table tr {{ break-inside: avoid; page-break-inside: avoid; }}
table.data-table thead {{ display: table-header-group; }}
p, li {{ orphans: 2; widows: 2; }}

/* On-screen preview only: mimic paper with margins (does not affect print/PDF) */
@media screen {{
    body {{ background: #52526a; }}
    .cover {{ margin: 0 auto; box-shadow: 0 4px 24px rgba(0,0,0,0.4); }}
    .content {{
        width: 210mm; min-height: 297mm; margin: 24px auto; background: #fff;
        padding: 24mm 22mm; box-shadow: 0 4px 24px rgba(0,0,0,0.4);
    }}
}}
"""


# ---------------------------------------------------------------------------
# Page assembly
# ---------------------------------------------------------------------------

def build_html(doc: dict) -> str:
    logo_uri = _b64_uri(ASSETS / "d55-logo-white.png")
    bg_uri = _b64_uri(ASSETS / "D55_TEAMS_BACKGROUND_No_LOGO.jpg")
    bryt_uri = _b64_uri(ASSETS / "bryt-energy.png")

    blocks_html = ""
    for block in doc["blocks"]:
        renderer = RENDERERS.get(block["type"])
        if not renderer:
            raise ValueError(f"Unknown block type: {block['type']}")
        cls = " section-break" if block.get("pageBreak") else ""
        rendered = renderer(block)
        if cls:
            rendered = rendered.replace('class="block', f'class="block{cls}', 1)
        blocks_html += rendered

    effort_badge = f'<div class="effort">{esc(doc["effort"])}</div>' if doc.get("effort") else ""
    eyebrow = esc(doc.get("eyebrow", "Report Builder"))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{esc(doc['title'])}</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
{build_css(bg_uri)}
</style>
</head>
<body>
<div class="cover">
    <img src="{logo_uri}" class="logo" alt="D55">
    <img src="{bryt_uri}" class="bryt" alt="BRYT Energy">
    <div class="cover-inner">
        <div class="eyebrow">{eyebrow}</div>
        <h1>{esc(doc['title'])}</h1>
        <div class="subtitle">{esc(doc.get('subtitle', ''))}</div>
        {effort_badge}
    </div>
    <div class="meta">
        <div class="org">D55 Consulting</div>
        <div class="date">{esc(doc.get('date', 'August 2026'))}</div>
    </div>
</div>
<div class="content">
{blocks_html}
</div>
</body>
</html>"""


def render_pdf(html_path: Path, pdf_path: Path):
    """Render HTML to PDF via Playwright (Chromium)."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
        page.pdf(
            path=str(pdf_path),
            print_background=True,
            prefer_css_page_size=True,
        )
        browser.close()


def main():
    if len(sys.argv) < 2:
        print("Usage: python build_walkthrough.py <content_module> [--no-pdf]")
        sys.exit(1)

    module_name = sys.argv[1].replace(".py", "")
    make_pdf = "--no-pdf" not in sys.argv

    sys.path.insert(0, str(Path(__file__).parent))
    sys.path.insert(0, str(ROOT))  # so content modules can `import figures`
    content = importlib.import_module(module_name)
    doc = content.DOC

    html = build_html(doc)
    slug = doc.get("slug") or f"{doc.get('estimate', 'document')}-walkthrough"
    html_path = OUTPUTS / f"{slug}.html"
    html_path.write_text(html, encoding="utf-8")
    print(f"HTML written: {html_path}  ({len(html) / 1024:.0f} KB)")

    if make_pdf:
        pdf_path = OUTPUTS / f"{slug}.pdf"
        try:
            render_pdf(html_path, pdf_path)
            print(f"PDF written:  {pdf_path}")
        except Exception as exc:  # noqa: BLE001
            print(f"PDF render skipped ({exc}).")
            print("Install browser with: python -m playwright install chromium")


if __name__ == "__main__":
    main()
