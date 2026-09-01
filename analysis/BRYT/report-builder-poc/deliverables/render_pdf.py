"""
Render the standalone POC summary presentation (outputs/presentation-preview.html)
to a landscape PDF, one 16:9 slide per page.

The deck is HTML-first (see build_standalone_html.py); this is a thin Playwright
renderer so the deck can also be shared as a PDF. Print CSS is injected to pin
each .slide to a single page and to neutralise the on-screen auto-zoom script.

Usage:
    python analysis/BRYT/report-builder-poc/deliverables/render_pdf.py

Requires: playwright + a Chromium build
    pip install playwright
    python -m playwright install chromium
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
HTML = HERE / "outputs" / "presentation-preview.html"
PDF = HERE / "outputs" / "presentation-preview.pdf"

# One slide == one landscape page. Slides are authored at 960x540 CSS px.
PRINT_CSS = """
@page { size: 960px 540px; margin: 0; }
html, body { zoom: 1 !important; padding: 0 !important; margin: 0 !important; background: #fff !important; }
.slide {
    margin: 0 !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    page-break-after: always;
    break-after: page;
}
.slide:last-of-type { page-break-after: auto; break-after: auto; }
"""


def main():
    if not HTML.exists():
        raise SystemExit(f"Deck not found: {HTML}\nRun build_standalone_html.py first.")

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(HTML.resolve().as_uri(), wait_until="networkidle")
        page.add_style_tag(content=PRINT_CSS)
        page.emulate_media(media="print")
        page.pdf(
            path=str(PDF),
            print_background=True,
            prefer_css_page_size=True,
        )
        browser.close()

    print(f"PDF written: {PDF}  ({PDF.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
