"""
Self-contained briefing document generator (D55-branded).

Adapted from the deliverables-toolkit walkthrough engine
(analysis/BRYT/contract-note/walkthroughs/build_walkthrough.py), but standalone
and D55-branded — no client co-branding, since this is a D55-prepared internal
briefing ahead of the ESG / Lynsey meeting.

Content lives in `briefing_content.py` as a DOC dict of typed blocks.

Block types: section, table, callout, pipeline, layers.

Usage:
    python build_briefing.py            # HTML + PDF
    python build_briefing.py --no-pdf   # HTML only
"""
import base64
import html as html_mod
import importlib
import mimetypes
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
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


def render_callout(block):
    heading = f'<h3>{esc(block["heading"])}</h3>' if block.get("heading") else ""
    body = _para_list(block.get("body"))
    bullets = _bullets(block.get("bullets"))
    return f'<section class="block callout">{heading}{body}{bullets}</section>'


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
    return (
        f'<section class="block block-pipeline">{heading}{body}'
        f'<figure class="flow"><div class="pipeline">{"".join(parts)}</div>{caption}</figure></section>'
    )


def render_layers(block):
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


RENDERERS = {
    "section": render_section,
    "table": render_table,
    "callout": render_callout,
    "pipeline": render_pipeline,
    "layers": render_layers,
}


# ---------------------------------------------------------------------------
# Stylesheet (print-oriented, D55 branding)
# ---------------------------------------------------------------------------

def build_css(bg_uri: str) -> str:
    return f"""
@page {{ size: A4 portrait; margin: 22mm 20mm 20mm 20mm; }}
@page cover {{ size: A4 portrait; margin: 0; }}

* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    font-family: 'Inter', 'Segoe UI', sans-serif;
    color: #23232f; font-size: 10.5pt; line-height: 1.6;
}}
h1, h2, h3, h4 {{ color: #1a0a3e; }}
p {{ margin: 0 0 9px; }}

/* Cover */
.cover {{
    page: cover; position: relative; width: 210mm; height: 297mm;
    background-image: url('{bg_uri}'); background-size: cover; background-position: center;
    overflow: hidden; color: #fff; page-break-after: always;
}}
.cover::after {{
    content: ''; position: absolute; inset: 0;
    background: linear-gradient(135deg, rgba(26,10,62,0.9) 0%, rgba(28,20,88,0.74) 50%, rgba(10,74,140,0.62) 100%);
}}
.cover > * {{ position: relative; z-index: 1; }}
.cover .logo {{ position: absolute; top: 30px; right: 34px; height: 46px; }}
.cover .client-logo {{ position: absolute; top: 32px; left: 34px; height: 40px; }}
.cover .cover-inner {{ position: absolute; top: 38%; left: 52px; right: 52px; }}
.cover .eyebrow {{
    font-size: 12pt; font-weight: 300; letter-spacing: 2px;
    text-transform: uppercase; opacity: 0.82; margin-bottom: 14px;
}}
.cover h1 {{ color: #fff; font-size: 34pt; font-weight: 700; line-height: 1.12; max-width: 90%; }}
.cover .subtitle {{ font-size: 15pt; font-weight: 300; opacity: 0.85; margin-top: 16px; max-width: 82%; }}
.cover .confidential {{
    display: inline-block; margin-top: 26px; padding: 8px 16px;
    background: rgba(93,173,226,0.22); border: 1px solid rgba(93,173,226,0.5);
    border-radius: 4px; font-size: 11pt; font-weight: 600; color: #d7ecfa;
    letter-spacing: 0.5px;
}}
.cover .meta {{ position: absolute; bottom: 48px; left: 52px; }}
.cover .meta .org {{ font-size: 12pt; font-weight: 600; }}
.cover .meta .date {{ font-size: 10pt; opacity: 0.62; margin-top: 2px; }}

/* Content */
.content {{ padding-top: 2px; }}
.block {{ margin-bottom: 20px; }}
h2 {{
    font-size: 16pt; font-weight: 700; margin-bottom: 11px;
    padding-bottom: 6px; border-bottom: 2px solid #e2e2ee;
}}
h3 {{ font-size: 12.5pt; font-weight: 600; margin-bottom: 6px; }}

ul.bullets {{ list-style: none; margin: 6px 0; }}
ul.bullets li {{ position: relative; padding-left: 18px; margin-bottom: 5px; }}
ul.bullets li::before {{
    content: '\\203A'; position: absolute; left: 0; top: -1px;
    color: #5dade2; font-weight: bold; font-size: 13pt;
}}

/* Tables */
table.data-table {{ width: 100%; border-collapse: collapse; font-size: 9.5pt; margin-top: 8px; }}
table.data-table th {{
    background: #1a0a3e; color: #d7ecfa; text-align: left;
    padding: 7px 10px; font-size: 8pt; text-transform: uppercase; letter-spacing: 0.4px;
}}
table.data-table td {{ padding: 6px 10px; border-bottom: 1px solid #e6e6f0; vertical-align: top; }}
table.data-table tr:nth-child(even) td {{ background: #f6f6fb; }}

figcaption {{ font-size: 8.5pt; color: #6a6a80; margin-top: 8px; font-style: italic; }}

/* Callout */
.callout {{
    background: #f0f6fc; border-left: 4px solid #5dade2;
    padding: 13px 17px; border-radius: 0 4px 4px 0;
}}
.callout h3 {{ color: #0a4a8c; }}

/* Flow diagrams (CSS-rendered) */
figure.flow {{ margin: 12px 0 6px; page-break-inside: avoid; }}
.pipeline {{ display: flex; align-items: stretch; gap: 4px; }}
.pipeline .step {{
    flex: 1; text-align: center; background: #1a0a3e; color: #fff;
    border-radius: 5px; padding: 10px 6px; font-size: 8pt; font-weight: 600;
    display: flex; align-items: center; justify-content: center;
}}
.pipeline .step-arrow {{ color: #5dade2; font-size: 11pt; align-self: center; }}

.layers {{ display: flex; flex-direction: column; gap: 4px; }}
.lane {{ border: 1.5px solid #c9c9dc; border-radius: 6px; background: #f8f8fc; padding: 9px 11px 11px; }}
.lane-label {{
    font-size: 8pt; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px;
    color: #0a4a8c; margin-bottom: 8px;
}}
.lane-nodes {{ display: flex; flex-wrap: wrap; gap: 8px; }}
.lane-nodes .node {{
    flex: 1; min-width: 110px; text-align: center; background: #fff;
    border: 1.5px solid #5dade2; border-radius: 5px; padding: 9px 6px;
    font-size: 8.5pt; font-weight: 600; color: #1a0a3e;
}}
.lane-arrow {{ text-align: center; color: #5dade2; font-size: 12pt; line-height: 1; margin: -1px 0; }}

.section-break {{ page-break-before: always; }}

/* Page-break control */
h2, h3, h4 {{ break-after: avoid; page-break-after: avoid; }}
h2 + *, h3 + * {{ break-before: avoid; page-break-before: avoid; }}
figure.flow, .callout, .block-layers, .block-pipeline {{ break-inside: avoid; page-break-inside: avoid; }}
table.data-table {{ break-inside: auto; }}
table.data-table tr {{ break-inside: avoid; page-break-inside: avoid; }}
table.data-table thead {{ display: table-header-group; }}
p, li {{ orphans: 2; widows: 2; }}

@media screen {{
    body {{ background: #52526a; }}
    .cover {{ margin: 0 auto; box-shadow: 0 4px 24px rgba(0,0,0,0.4); }}
    .content {{
        width: 210mm; min-height: 297mm; margin: 24px auto; background: #fff;
        padding: 22mm 20mm; box-shadow: 0 4px 24px rgba(0,0,0,0.4);
    }}
}}
"""


# ---------------------------------------------------------------------------
# Page assembly
# ---------------------------------------------------------------------------

def build_html(doc: dict) -> str:
    logo_uri = _b64_uri(ASSETS / "d55-logo-white.png")
    bg_uri = _b64_uri(ASSETS / "d55-bg.jpg")
    client_logo_path = ASSETS / "esg-logo-white.png"
    client_logo_uri = _b64_uri(client_logo_path) if client_logo_path.exists() else None

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

    confidential = (
        f'<div class="confidential">{esc(doc["confidential"])}</div>'
        if doc.get("confidential") else ""
    )

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
    {f'<img src="{client_logo_uri}" class="client-logo" alt="ESG">' if client_logo_uri else ''}
    <div class="cover-inner">
        <div class="eyebrow">{esc(doc.get('eyebrow', ''))}</div>
        <h1>{esc(doc['title'])}</h1>
        <div class="subtitle">{esc(doc.get('subtitle', ''))}</div>
        {confidential}
    </div>
    <div class="meta">
        <div class="org">D55</div>
        <div class="date">{esc(doc.get('date', 'July 2026'))}</div>
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
        page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
        page.pdf(path=str(pdf_path), print_background=True, prefer_css_page_size=True)
        browser.close()


def main():
    make_pdf = "--no-pdf" not in sys.argv
    sys.path.insert(0, str(ROOT))
    content = importlib.import_module("briefing_content")
    doc = content.DOC

    OUTPUTS.mkdir(exist_ok=True)
    html = build_html(doc)
    slug = doc.get("slug", "briefing")
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
