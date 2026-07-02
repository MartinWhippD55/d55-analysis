"""
Build a fully self-contained HTML rendering of the OpenAPI spec.

Inlines both the spec (as JSON) and the Redoc runtime so the output needs no
network access to view - just open it in a browser.

The Redoc runtime is fetched once and cached locally as `_redoc.js` (gitignored).
If it is missing, this script downloads it.

Usage:
    python analysis/BRYT/contract-note/api/build_html.py
"""
import json
import urllib.request
from pathlib import Path

import yaml

HERE = Path(__file__).parent
SPEC = HERE / "contract-note-api.yaml"
RUNTIME = HERE / "_redoc.js"
OUTPUT = HERE / "contract-note-api.html"
REDOC_URL = "https://cdn.redocly.com/redoc/v2.5.3/bundles/redoc.standalone.js"


def ensure_runtime() -> str:
    if not RUNTIME.exists():
        print(f"Downloading Redoc runtime from {REDOC_URL} ...")
        urllib.request.urlretrieve(REDOC_URL, RUNTIME)
    return RUNTIME.read_text(encoding="utf-8")


def main():
    spec = yaml.safe_load(SPEC.read_text(encoding="utf-8"))
    spec_json = json.dumps(spec)
    runtime = ensure_runtime()
    title = spec.get("info", {}).get("title", "API Reference")

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{title}</title>
  <style>body {{ margin: 0; padding: 0; }}</style>
</head>
<body>
  <div id="redoc"></div>
  <script>{runtime}</script>
  <script>
    var spec = {spec_json};
    Redoc.init(spec, {{ hideDownloadButton: false, expandResponses: "200,201" }}, document.getElementById("redoc"));
  </script>
</body>
</html>"""

    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Self-contained HTML written: {OUTPUT}  ({len(html) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
