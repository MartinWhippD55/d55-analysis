"""
Build a fully self-contained (offline) HTML rendering of an OpenAPI spec.

Inlines both the spec (as JSON) and the Redoc runtime so the output needs no
network access to view — just open it in a browser. The runtime is fetched once
and cached locally (gitignored); pass a cached copy to avoid any network call.

Usage:
    from engine.openapi_html import build_openapi_html
    build_openapi_html("deliverables/<spec>/api/api.yaml",
                       "deliverables/<spec>/api/api.html")
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path
from typing import Optional

REDOC_URL = "https://cdn.redocly.com/redoc/v2.5.3/bundles/redoc.standalone.js"


def ensure_runtime(cache_path, url: str = REDOC_URL) -> str:
    """Return the Redoc runtime JS, downloading + caching it if not present."""
    cache = Path(cache_path)
    if not cache.exists():
        urllib.request.urlretrieve(url, cache)
    return cache.read_text(encoding="utf-8")


def render_html(spec: dict, runtime_js: str) -> str:
    """Pure: assemble the self-contained HTML from a spec dict + runtime JS."""
    title = spec.get("info", {}).get("title", "API Reference")
    spec_json = json.dumps(spec)
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{title}</title>
  <style>body {{ margin: 0; padding: 0; }}</style>
</head>
<body>
  <div id="redoc"></div>
  <script>{runtime_js}</script>
  <script>
    var spec = {spec_json};
    Redoc.init(spec, {{ hideDownloadButton: false, expandResponses: "200,201" }}, document.getElementById("redoc"));
  </script>
</body>
</html>"""


def build_openapi_html(spec_yaml_path, output_path, runtime_cache: Optional[str] = None) -> Path:
    """Load a YAML spec and write a self-contained HTML reference beside it."""
    import yaml

    spec_path = Path(spec_yaml_path)
    out = Path(output_path)
    cache = Path(runtime_cache) if runtime_cache else spec_path.with_name("_redoc.js")
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    runtime = ensure_runtime(cache)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_html(spec, runtime), encoding="utf-8")
    return out
