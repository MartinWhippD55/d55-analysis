"""
Markdown -> branded PDF converter (D55).

Free-standing: takes a Markdown file (by path), converts it to a branded,
standalone HTML document (assets embedded as base64), then renders A4 PDF via
Playwright. No third-party Markdown library required — a focused converter
handles the constructs used in our docs.

Supported Markdown:
  - Headings  # .. ######
  - Paragraphs
  - Unordered lists (-, *, +) and ordered lists (1.)  (single level)
  - GFM pipe tables (header row + --- separator + body rows)
  - Blockquotes ( > ... )  -> rendered as branded callouts
  - Horizontal rules (---, ***, ___) -> section dividers
  - Fenced code blocks (``` ... ```)
  - Inline: **bold**, *italic* / _italic_, `code`, [text](url)
  - Optional YAML front matter: title, subtitle, eyebrow, date, confidential,
    client_logo (a bundled key like "esg", or a path to a white PNG logo)

Usage:
  python .kiro/skills/markdown-to-pdf/md_to_pdf.py <path-to.md> [options]

Options:
  --client-logo <key|path>  Co-brand: bundled key (e.g. "esg") or a PNG path.
  --title / --subtitle / --eyebrow / --date / --confidential  Override cover.
  --out <path>              Output PDF path (default: alongside source, .pdf).
  --no-pdf                  Write HTML only (skip PDF render).
"""
import argparse
import base64
import html as html_mod
import mimetypes
import re
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent
ASSETS = SKILL_DIR / "assets"

# Bundled client logos by key (extend as needed).
CLIENT_LOGOS = {
    "esg": ASSETS / "esg-logo-white.png",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def b64_uri(path: Path) -> str:
    mime = mimetypes.guess_type(str(path))[0] or "image/png"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def esc(text: str) -> str:
    return html_mod.escape(text)


# ---------------------------------------------------------------------------
# Front matter
# ---------------------------------------------------------------------------

def split_front_matter(text: str):
    """Return (meta_dict, body). Parses a leading --- ... --- YAML block."""
    if not text.startswith("---"):
        return {}, text
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.DOTALL)
    if not m:
        return {}, text
    raw, body = m.group(1), m.group(2)
    meta = {}
    try:
        import yaml  # present in this environment
        meta = yaml.safe_load(raw) or {}
    except Exception:
        for line in raw.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, body


# ---------------------------------------------------------------------------
# Inline formatting
# ---------------------------------------------------------------------------

_CODE_TOKEN = "\x00CODE{}\x00"


def inline(text: str) -> str:
    """Escape HTML then apply inline markdown. Code spans are protected first."""
    codes = []

    def _stash(m):
        codes.append(m.group(1))
        return _CODE_TOKEN.format(len(codes) - 1)

    text = re.sub(r"`([^`]+)`", _stash, text)
    text = esc(text)
    # links [text](url)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)\s]+)\)",
        lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>',
        text,
    )
    # bold then italic
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"(?<!_)_([^_\n]+)_(?!_)", r"<em>\1</em>", text)
    # restore code spans
    for i, c in enumerate(codes):
        text = text.replace(_CODE_TOKEN.format(i), f"<code>{esc(c)}</code>")
    return text


# ---------------------------------------------------------------------------
# Block-level parsing
# ---------------------------------------------------------------------------

def _is_table_sep(line: str) -> bool:
    return bool(re.match(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+\|?\s*$", line))


def _split_row(line: str):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def render_table(header, rows):
    ths = "".join(f"<th>{inline(c)}</th>" for c in header)
    body = ""
    for r in rows:
        cells = "".join(f"<td>{inline(c)}</td>" for c in r)
        body += f"<tr>{cells}</tr>"
    return (
        f'<table class="data-table"><thead><tr>{ths}</tr></thead>'
        f"<tbody>{body}</tbody></table>"
    )


def render_callout(lines):
    """Blockquote -> callout. A leading **bold** line becomes the heading."""
    inner = ""
    if lines and re.match(r"^\*\*.+\*\*", lines[0]):
        m = re.match(r"^\*\*(.+?)\*\*[:：]?\s*(.*)$", lines[0])
        inner += f"<h3>{inline(m.group(1))}</h3>"
        rest = m.group(2).strip()
        remaining = ([rest] if rest else []) + lines[1:]
    else:
        remaining = lines
    para = " ".join(remaining).strip()
    if para:
        inner += f"<p>{inline(para)}</p>"
    return f'<section class="callout">{inner}</section>'


def markdown_to_html(md: str) -> str:
    lines = md.replace("\r\n", "\n").split("\n")
    out = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # blank
        if not stripped:
            i += 1
            continue

        # fenced code
        if stripped.startswith("```"):
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1  # closing fence
            code = esc("\n".join(buf))
            out.append(f'<pre class="code"><code>{code}</code></pre>')
            continue

        # horizontal rule / divider
        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", stripped):
            out.append('<hr class="divider">')
            i += 1
            continue

        # heading
        h = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if h:
            level = len(h.group(1))
            out.append(f"<h{level}>{inline(h.group(2).strip())}</h{level}>")
            i += 1
            continue

        # table (current line has a pipe and next line is a separator)
        if "|" in line and i + 1 < n and _is_table_sep(lines[i + 1]):
            header = _split_row(line)
            i += 2
            rows = []
            while i < n and "|" in lines[i] and lines[i].strip():
                rows.append(_split_row(lines[i]))
                i += 1
            out.append(render_table(header, rows))
            continue

        # blockquote
        if stripped.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            buf = [b for b in buf if b.strip()]
            out.append(render_callout(buf))
            continue

        # unordered list
        if re.match(r"^\s*[-*+]\s+", line):
            items = []
            while i < n and re.match(r"^\s*[-*+]\s+", lines[i]):
                items.append(re.sub(r"^\s*[-*+]\s+", "", lines[i]).strip())
                i += 1
            lis = "".join(f"<li>{inline(t)}</li>" for t in items)
            out.append(f'<ul class="bullets">{lis}</ul>')
            continue

        # ordered list
        if re.match(r"^\s*\d+\.\s+", line):
            items = []
            while i < n and re.match(r"^\s*\d+\.\s+", lines[i]):
                items.append(re.sub(r"^\s*\d+\.\s+", "", lines[i]).strip())
                i += 1
            lis = "".join(f"<li>{inline(t)}</li>" for t in items)
            out.append(f"<ol>{lis}</ol>")
            continue

        # paragraph (gather until blank or block starter)
        buf = []
        while i < n and lines[i].strip() and not (
            lines[i].strip().startswith(("#", ">", "```"))
            or re.match(r"^\s*[-*+]\s+", lines[i])
            or re.match(r"^\s*\d+\.\s+", lines[i])
            or re.match(r"^(-{3,}|\*{3,}|_{3,})$", lines[i].strip())
        ):
            buf.append(lines[i].strip())
            i += 1
        out.append(f"<p>{inline(' '.join(buf))}</p>")

    return "\n".join(out)


# ---------------------------------------------------------------------------
# Branded template
# ---------------------------------------------------------------------------

def build_css(bg_uri: str) -> str:
    return f"""
@page {{ size: A4 portrait; margin: 22mm 20mm 20mm 20mm; }}
@page cover {{ size: A4 portrait; margin: 0; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Inter','Segoe UI',sans-serif; color: #23232f; font-size: 10.5pt; line-height: 1.6; }}
h1,h2,h3,h4,h5,h6 {{ color: #1a0a3e; }}
p {{ margin: 0 0 9px; }}

.cover {{
    page: cover; position: relative; width: 210mm; height: 297mm;
    background-image: url('{bg_uri}'); background-size: cover; background-position: center;
    overflow: hidden; color: #fff; page-break-after: always;
}}
.cover::after {{ content:''; position:absolute; inset:0;
    background: linear-gradient(135deg, rgba(26,10,62,0.9) 0%, rgba(28,20,88,0.74) 50%, rgba(10,74,140,0.62) 100%); }}
.cover > * {{ position: relative; z-index: 1; }}
.cover .logo {{ position: absolute; top: 30px; right: 34px; height: 46px; }}
.cover .client-logo {{ position: absolute; top: 24px; left: 34px; height: 58px; }}
.cover .cover-inner {{ position: absolute; top: 38%; left: 52px; right: 52px; }}
.cover .eyebrow {{ font-size: 12pt; font-weight: 300; letter-spacing: 2px; text-transform: uppercase; opacity: 0.82; margin-bottom: 14px; }}
.cover h1 {{ color: #fff; font-size: 34pt; font-weight: 700; line-height: 1.12; max-width: 90%; border: none; padding: 0; }}
.cover .subtitle {{ font-size: 15pt; font-weight: 300; opacity: 0.85; margin-top: 16px; max-width: 82%; }}
.cover .confidential {{ display: inline-block; margin-top: 26px; padding: 8px 16px;
    background: rgba(93,173,226,0.22); border: 1px solid rgba(93,173,226,0.5); border-radius: 4px;
    font-size: 11pt; font-weight: 600; color: #d7ecfa; letter-spacing: 0.5px; }}
.cover .meta {{ position: absolute; bottom: 48px; left: 52px; }}
.cover .meta .org {{ font-size: 12pt; font-weight: 600; }}
.cover .meta .date {{ font-size: 10pt; opacity: 0.62; margin-top: 2px; }}

.content h1 {{ font-size: 20pt; font-weight: 700; margin: 4px 0 12px; padding-bottom: 7px; border-bottom: 2px solid #e2e2ee; }}
.content h2 {{ font-size: 16pt; font-weight: 700; margin: 18px 0 11px; padding-bottom: 6px; border-bottom: 2px solid #e2e2ee; }}
.content h3 {{ font-size: 12.5pt; font-weight: 600; margin: 14px 0 6px; }}
.content h4 {{ font-size: 10.5pt; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #0a4a8c; margin: 12px 0 6px; }}

ul.bullets, ol {{ margin: 6px 0 10px; padding-left: 0; }}
ul.bullets {{ list-style: none; }}
ul.bullets li {{ position: relative; padding-left: 18px; margin-bottom: 5px; }}
ul.bullets li::before {{ content: '\\203A'; position: absolute; left: 0; top: -1px; color: #5dade2; font-weight: bold; font-size: 13pt; }}
ol {{ padding-left: 20px; }}
ol li {{ margin-bottom: 5px; }}

table.data-table {{ width: 100%; border-collapse: collapse; font-size: 9.5pt; margin: 8px 0 12px; }}
table.data-table th {{ background: #1a0a3e; color: #d7ecfa; text-align: left; padding: 7px 10px; font-size: 8pt; text-transform: uppercase; letter-spacing: 0.4px; }}
table.data-table td {{ padding: 6px 10px; border-bottom: 1px solid #e6e6f0; vertical-align: top; }}
table.data-table tr:nth-child(even) td {{ background: #f6f6fb; }}

.callout {{ background: #f0f6fc; border-left: 4px solid #5dade2; padding: 13px 17px; border-radius: 0 4px 4px 0; margin: 10px 0 14px; }}
.callout h3 {{ color: #0a4a8c; margin-bottom: 6px; }}

pre.code {{ background: #1a0a3e; color: #e7edf5; padding: 12px 14px; border-radius: 5px; font-size: 8.5pt; overflow-x: auto; margin: 8px 0 12px; }}
pre.code code {{ font-family: 'Consolas','Monaco',monospace; }}
code {{ font-family: 'Consolas','Monaco',monospace; background: #eef0f6; color: #0a4a8c; padding: 1px 4px; border-radius: 3px; font-size: 9pt; }}
pre.code code {{ background: none; color: inherit; padding: 0; }}
a {{ color: #0a4a8c; text-decoration: none; }}
hr.divider {{ border: none; border-top: 1px solid #e2e2ee; margin: 16px 0; }}

/* Page-break control */
h1,h2,h3,h4 {{ break-after: avoid; page-break-after: avoid; }}
h1+*,h2+*,h3+*,h4+* {{ break-before: avoid; page-break-before: avoid; }}
.callout, pre.code {{ break-inside: avoid; page-break-inside: avoid; }}
table.data-table tr {{ break-inside: avoid; page-break-inside: avoid; }}
table.data-table thead {{ display: table-header-group; }}
p, li {{ orphans: 2; widows: 2; }}

@media screen {{
    body {{ background: #52526a; }}
    .cover {{ margin: 0 auto; box-shadow: 0 4px 24px rgba(0,0,0,0.4); }}
    .content {{ width: 210mm; min-height: 297mm; margin: 24px auto; background: #fff; padding: 22mm 20mm; box-shadow: 0 4px 24px rgba(0,0,0,0.4); }}
}}
"""


def build_html(meta: dict, body_html: str) -> str:
    logo_uri = b64_uri(ASSETS / "d55-logo-white.png")
    bg_uri = b64_uri(ASSETS / "d55-bg.jpg")

    client_logo_uri = None
    cl = meta.get("client_logo")
    if cl:
        p = CLIENT_LOGOS.get(str(cl).lower()) or Path(cl)
        if p and Path(p).exists():
            client_logo_uri = b64_uri(Path(p))

    eyebrow = f'<div class="eyebrow">{esc(meta["eyebrow"])}</div>' if meta.get("eyebrow") else ""
    subtitle = f'<div class="subtitle">{esc(meta["subtitle"])}</div>' if meta.get("subtitle") else ""
    confidential = f'<div class="confidential">{esc(meta["confidential"])}</div>' if meta.get("confidential") else ""
    client_img = f'<img src="{client_logo_uri}" class="client-logo" alt="client">' if client_logo_uri else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{esc(meta.get('title',''))}</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
{build_css(bg_uri)}
</style>
</head>
<body>
<div class="cover">
    <img src="{logo_uri}" class="logo" alt="D55">
    {client_img}
    <div class="cover-inner">
        {eyebrow}
        <h1>{esc(meta.get('title',''))}</h1>
        {subtitle}
        {confidential}
    </div>
    <div class="meta">
        <div class="org">{esc(meta.get('org','D55'))}</div>
        <div class="date">{esc(meta.get('date','')) }</div>
    </div>
</div>
<div class="content">
{body_html}
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
    ap = argparse.ArgumentParser(description="Convert a Markdown file to a branded D55 PDF.")
    ap.add_argument("source", help="Path to the Markdown file (relative to CWD).")
    ap.add_argument("--client-logo", help="Bundled key (e.g. 'esg') or path to a white PNG logo.")
    ap.add_argument("--title")
    ap.add_argument("--subtitle")
    ap.add_argument("--eyebrow")
    ap.add_argument("--date")
    ap.add_argument("--confidential")
    ap.add_argument("--out", help="Output PDF path (default: alongside source).")
    ap.add_argument("--no-pdf", action="store_true")
    args = ap.parse_args()

    src = Path(args.source)
    if not src.exists():
        raise SystemExit(f"Markdown file not found: {src}")

    meta, body = split_front_matter(src.read_text(encoding="utf-8"))

    # Title: CLI > front matter > first H1 (consumed) > filename stem.
    if not meta.get("title"):
        m = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
        if m:
            meta["title"] = m.group(1).strip()
            body = body[: m.start()] + body[m.end():]
        else:
            meta["title"] = src.stem.replace("-", " ").replace("_", " ").title()

    # CLI overrides
    for key in ("title", "subtitle", "eyebrow", "date", "confidential"):
        val = getattr(args, key)
        if val:
            meta[key] = val
    if args.client_logo:
        meta["client_logo"] = args.client_logo
    if not meta.get("date"):
        from datetime import date
        meta["date"] = date.today().strftime("%B %Y")

    body_html = markdown_to_html(body)
    html = build_html(meta, body_html)

    out_pdf = Path(args.out) if args.out else src.with_suffix(".pdf")
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    html_path = out_pdf.with_suffix(".html")
    html_path.write_text(html, encoding="utf-8")
    print(f"HTML written: {html_path}  ({len(html)/1024:.0f} KB)")

    if not args.no_pdf:
        try:
            render_pdf(html_path, out_pdf)
            print(f"PDF written:  {out_pdf}")
        except Exception as exc:  # noqa: BLE001
            print(f"PDF render skipped ({exc}).")
            print("Install browser with: python -m playwright install chromium")


if __name__ == "__main__":
    main()
