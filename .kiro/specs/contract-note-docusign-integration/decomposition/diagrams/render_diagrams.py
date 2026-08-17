"""Render every .mmd in this folder to a high-res PNG.

Mermaid is loaded from CDN into a headless Chromium page (device_scale_factor=2),
matching the repo's existing diagram tooling
(analysis/BRYT/contract-note/diagram/render_diagram.py). Jira Cloud does not
render mermaid in descriptions, so these PNGs are what gets attached to issues.

    python .kiro/specs/contract-note-docusign-integration/decomposition/diagrams/render_diagrams.py
"""
from pathlib import Path
import json

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
MERMAID_CDN = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs"

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', 'Inter', sans-serif; background: #ffffff; }}
  #diagram {{ display: inline-block; padding: 24px 28px; background: #ffffff; }}
  #diagram svg {{ display: block; }}
</style>
</head>
<body>
  <div id="diagram"><pre class="mermaid">{graph}</pre></div>
  <script type="module">
    import mermaid from '{cdn}';
    mermaid.initialize({{ startOnLoad: false, theme: 'default', flowchart: {{ htmlLabels: true, curve: 'basis' }} }});
    window.__done = false;
    try {{
      await mermaid.run({{ querySelector: '.mermaid' }});
      // Size the SVG to its intrinsic viewBox so it renders full-resolution
      // instead of being capped to the container width.
      const svg = document.querySelector('#diagram svg');
      if (svg) {{
        const vb = svg.viewBox.baseVal;
        svg.style.maxWidth = 'none';
        svg.setAttribute('width', vb.width);
        svg.setAttribute('height', vb.height);
      }}
      window.__ok = !!svg;
    }} catch (e) {{
      window.__err = String(e);
    }}
    window.__done = true;
  </script>
</body>
</html>"""


def main():
    sources = sorted(HERE.glob("*.mmd"))
    if not sources:
        print("No .mmd sources found.")
        return

    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(device_scale_factor=2)
        page = ctx.new_page()
        for mmd in sources:
            graph = mmd.read_text(encoding="utf-8")
            html = PAGE.format(graph=graph, cdn=MERMAID_CDN)
            html_path = mmd.with_suffix(".render.html")
            html_path.write_text(html, encoding="utf-8")
            page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
            page.wait_for_function("window.__done === true", timeout=30000)
            err = page.evaluate("window.__err || null")
            if err:
                raise RuntimeError(f"mermaid failed for {mmd.name}: {err}")
            page.wait_for_timeout(300)
            png_path = mmd.with_suffix(".png")
            page.query_selector("#diagram").screenshot(path=str(png_path))
            html_path.unlink(missing_ok=True)
            results.append(png_path.name)
            print(f"rendered {mmd.name} -> {png_path.name}")
        browser.close()
    print(json.dumps({"rendered": results}, indent=2))


if __name__ == "__main__":
    main()
