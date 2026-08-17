"""Render every ``*.mmd`` in a directory to a high-resolution PNG.

Mermaid is loaded from CDN into a headless Chromium page (Playwright) and each diagram
is sized to its intrinsic ``viewBox`` before screenshotting, so the PNG is full-detail
rather than capped to a container width (a bug we hit the first time round). Jira Cloud
does not render mermaid in descriptions, so these PNGs are what the embed step attaches.

CLI:
    python -m engine.render <diagrams_dir>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

MERMAID_CDN = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs"

_PAGE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', 'Inter', sans-serif; background: #ffffff; }}
  #diagram {{ display: inline-block; padding: 24px 28px; background: #ffffff; }}
  #diagram svg {{ display: block; }}
</style></head>
<body>
  <div id="diagram"><pre class="mermaid">{graph}</pre></div>
  <script type="module">
    import mermaid from '{cdn}';
    mermaid.initialize({{ startOnLoad: false, theme: 'default',
      flowchart: {{ htmlLabels: true, curve: 'basis' }} }});
    window.__done = false;
    try {{
      await mermaid.run({{ querySelector: '.mermaid' }});
      const svg = document.querySelector('#diagram svg');
      if (svg) {{
        const vb = svg.viewBox.baseVal;
        svg.style.maxWidth = 'none';
        svg.setAttribute('width', vb.width);
        svg.setAttribute('height', vb.height);
      }}
      window.__ok = !!svg;
    }} catch (e) {{ window.__err = String(e); }}
    window.__done = true;
  </script>
</body></html>"""


def render_dir(diagrams_dir: str | Path) -> list[str]:
    """Render every ``*.mmd`` in ``diagrams_dir`` to a sibling ``.png``. Returns names."""
    from playwright.sync_api import sync_playwright

    here = Path(diagrams_dir)
    sources = sorted(here.glob("*.mmd"))
    if not sources:
        return []

    rendered: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_context(device_scale_factor=2).new_page()
        try:
            for mmd in sources:
                graph = mmd.read_text(encoding="utf-8")
                html_path = mmd.with_suffix(".render.html")
                html_path.write_text(_PAGE.format(graph=graph, cdn=MERMAID_CDN), encoding="utf-8")
                page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
                page.wait_for_function("window.__done === true", timeout=30000)
                err = page.evaluate("window.__err || null")
                if err:
                    raise RuntimeError(f"mermaid failed for {mmd.name}: {err}")
                page.wait_for_timeout(300)
                png = mmd.with_suffix(".png")
                page.query_selector("#diagram").screenshot(path=str(png))
                html_path.unlink(missing_ok=True)
                rendered.append(png.name)
        finally:
            browser.close()
    return rendered


def _main(argv=None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print("usage: python -m engine.render <diagrams_dir>")
        return 2
    rendered = render_dir(args[0])
    print(json.dumps({"rendered": rendered}, indent=2))
    return 0 if rendered else 1


if __name__ == "__main__":
    sys.exit(_main())
