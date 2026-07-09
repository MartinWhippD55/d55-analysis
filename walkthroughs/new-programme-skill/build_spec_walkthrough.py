"""
Build a branded, standalone HTML + A4 PDF walkthrough of the New Programme skill spec.

Reuses the block renderers, CSS, and PDF renderer from the existing walkthrough
engine (analysis/BRYT/contract-note/walkthroughs/build_walkthrough.py), but with
D55-only branding (this is an internal spec, no external client logo).

Usage:
    python walkthroughs/new-programme-skill/build_spec_walkthrough.py [--no-pdf]
"""
import base64
import importlib.util
import mimetypes
import sys
from pathlib import Path

# Workspace root = two parents up from this file (walkthroughs/new-programme-skill/x.py)
WS = Path(__file__).resolve().parents[2]
ENGINE = WS / "analysis/BRYT/contract-note/walkthroughs/build_walkthrough.py"
LOGO = WS / "analysis/D55/ai-dlc/assets/logo/D55_LOGO_WHITE (2).png"
BG = WS / "analysis/D55/ai-dlc/assets/backgrounds/D55_TEAMS_BACKGROUND_No_LOGO.jpg"
OUT = Path(__file__).resolve().parent

# --- import the existing engine as a module to reuse its renderers ---------
spec = importlib.util.spec_from_file_location("wt_engine", ENGINE)
eng = importlib.util.module_from_spec(spec)
spec.loader.exec_module(eng)


def _b64_uri(path: Path) -> str:
    mime = mimetypes.guess_type(str(path))[0] or "image/png"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def build_html_d55(doc: dict) -> str:
    """D55-branded page assembly (adapted from engine.build_html, no client logo)."""
    logo_uri = _b64_uri(LOGO)
    bg_uri = _b64_uri(BG)

    blocks_html = ""
    for block in doc["blocks"]:
        renderer = eng.RENDERERS.get(block["type"])
        if not renderer:
            raise ValueError(f"Unknown block type: {block['type']}")
        rendered = renderer(block)
        if block.get("pageBreak"):
            rendered = rendered.replace('class="block', 'class="block section-break', 1)
        blocks_html += rendered

    effort = f'<div class="effort">{eng.esc(doc["effort"])}</div>' if doc.get("effort") else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{eng.esc(doc['title'])}</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
{eng.build_css(bg_uri)}
</style>
</head>
<body>
<div class="cover">
    <img src="{logo_uri}" class="logo" alt="D55">
    <div class="cover-inner">
        <div class="eyebrow">Service Catalog</div>
        <h1>{eng.esc(doc['title'])}</h1>
        <div class="subtitle">{eng.esc(doc.get('subtitle', ''))}</div>
        {effort}
    </div>
    <div class="meta">
        <div class="org">D55 Consulting</div>
        <div class="date">{eng.esc(doc.get('date', 'July 2026'))}</div>
    </div>
</div>
<div class="content">
{blocks_html}
</div>
</body>
</html>"""


def main():
    make_pdf = "--no-pdf" not in sys.argv
    from spec_walkthrough_content import DOC

    html = build_html_d55(DOC)
    slug = DOC.get("slug", "new-programme-skill-walkthrough")
    html_path = OUT / f"{slug}.html"
    html_path.write_text(html, encoding="utf-8")
    print(f"HTML written: {html_path}  ({len(html) / 1024:.0f} KB)")

    if make_pdf:
        pdf_path = OUT / f"{slug}.pdf"
        try:
            eng.render_pdf(html_path, pdf_path)
            print(f"PDF written:  {pdf_path}")
        except Exception as exc:  # noqa: BLE001
            print(f"PDF render skipped ({exc}).")
            print("Install browser with: python -m playwright install chromium")


if __name__ == "__main__":
    sys.path.insert(0, str(OUT))
    main()
