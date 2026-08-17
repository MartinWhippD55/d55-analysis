"""Render the service-interaction diagram HTML to a high-res PNG.

Uses headless Chromium at 2x device scale so the image stays crisp when the
branded PDF downscales it to page width.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
HTML = HERE / "service-diagram.html"
OUT = HERE / "service-diagram.png"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_context(device_scale_factor=2).new_page()
        page.goto(HTML.as_uri(), wait_until="networkidle")
        el = page.query_selector("#diagram")
        el.screenshot(path=str(OUT))
        browser.close()
    print(f"Diagram PNG written: {OUT}")


if __name__ == "__main__":
    main()
