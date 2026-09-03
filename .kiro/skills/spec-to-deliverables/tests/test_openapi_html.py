"""Tests for the self-contained OpenAPI HTML assembly (pure render)."""
import re

from engine.openapi_html import render_html


SPEC = {
    "openapi": "3.1.0",
    "info": {"title": "My API", "version": "1.0.0"},
    "paths": {"/ping": {"get": {"responses": {"200": {"description": "ok"}}}}},
}
RUNTIME = "/* redoc runtime */ var Redoc = { init: function(){} };"


def test_title_and_spec_inlined():
    html = render_html(SPEC, RUNTIME)
    assert "<title>My API</title>" in html
    assert '"openapi": "3.1.0"' in html or '"openapi":"3.1.0"' in html
    assert "Redoc.init(spec" in html


def test_runtime_inlined():
    html = render_html(SPEC, RUNTIME)
    assert "redoc runtime" in html


def test_no_external_script_or_style_refs():
    html = render_html(SPEC, RUNTIME)
    # No external runtime/style references — everything is inlined.
    assert not re.search(r'src\s*=\s*"https?://', html)
    assert not re.search(r'href\s*=\s*"https?://', html)


def test_missing_title_falls_back():
    html = render_html({"paths": {}}, RUNTIME)
    assert "<title>API Reference</title>" in html
