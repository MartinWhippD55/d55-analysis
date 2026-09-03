"""
Data-driven branded HTML slide deck (16:9, auto-scaling, self-contained).

Build a deck from a ``deck`` dict rather than hand-writing slides. Figures come
from ``engine.figures`` (the caller interpolates them into slide content), so the
deck stays in sync with the spreadsheet. Images embed as base64; the output opens
offline in any browser and auto-scales to fill the viewport width.

Deck model:
    {
        "title": str,                # title-slide headline
        "subtitle": str?,            # title-slide sub-headline
        "org": str?, "date": str?,   # title-slide footer (else BrandConfig)
        "slides": [ <slide>, ... ],  # content/table slides after the title slide
    }

Slide types:
    {"type": "table",   "heading": str, "columns": [str], "rows": [[cell]]}  # last row = total (styled)
    {"type": "content", "heading": str, "hero": str?, "bullets": [str], "note": str?}

Bullet strings are treated as author-authored trusted HTML (so ``<strong>`` and
entities like ``&rarr;`` render), matching the content-module convention. Headings
and hero figures are escaped.

Usage:
    from engine.presentation import write_deck
    write_deck(deck, "deliverables/<spec>/outputs/presentation.html", brand)
"""
from __future__ import annotations

import html as html_mod
from pathlib import Path
from typing import Optional

from .brand import BrandConfig, b64_uri, rgba


def _esc(text) -> str:
    return html_mod.escape(str(text))


def _deck_css(brand: BrandConfig) -> str:
    primary, accent, deep = brand.primary, brand.accent, brand.deep
    return f"""
@import url('{brand.google_font_url}');
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: {brand.font_family}; background: #0d0d1a; padding: 24px; }}
.slide {{ width: 960px; height: 540px; margin: 0 auto 40px; border-radius: 6px; overflow: hidden;
    position: relative; box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    background: linear-gradient(135deg, {primary} 0%, {deep} 100%);
    color: #fff; padding: 48px 56px; display: flex; flex-direction: column; }}
.slide .logo {{ position: absolute; top: 24px; right: 28px; height: 36px; }}
.slide-number {{ position: absolute; bottom: 16px; right: 24px; font-size: 11px; color: rgba(255,255,255,0.35); }}
.slide-title {{ background-size: cover; background-position: center; justify-content: center; }}
.slide-title::after {{ content: ''; position: absolute; inset: 0;
    background: linear-gradient(135deg, {rgba(primary,0.8)} 0%, {rgba(deep,0.6)} 50%, {rgba(deep,0.5)} 100%); z-index: 0; }}
.slide-title > * {{ position: relative; z-index: 1; }}
.slide-title .logo {{ position: absolute; top: 24px; right: 28px; height: 44px; z-index: 1; }}
.slide-title h1 {{ font-size: 44px; font-weight: 700; line-height: 1.15; margin-bottom: 16px; max-width: 60%; }}
.slide-title h2 {{ font-size: 18px; font-weight: 300; opacity: 0.8; }}
.slide-title .presenter {{ position: absolute; bottom: 48px; left: 56px; z-index: 1; }}
.slide-title .presenter .name {{ font-size: 16px; font-weight: 600; }}
.slide-title .presenter .role {{ font-size: 13px; opacity: 0.6; margin-top: 2px; }}
.slide-title .client-logo {{ position: absolute; bottom: 40px; right: 56px; height: 40px; z-index: 1; }}
.slide-content h2, .slide-table h2 {{ font-size: 20px; font-weight: 700; margin-bottom: 20px;
    padding-bottom: 10px; border-bottom: 2px solid rgba(255,255,255,0.2); }}
.slide-content .hero-figure {{ font-size: 38px; font-weight: 700; color: {accent}; margin-bottom: 20px; }}
.slide-content ul {{ list-style: none; flex: 1; }}
.slide-content ul li {{ font-size: 14px; color: rgba(255,255,255,0.85); padding: 5px 0 5px 20px;
    position: relative; line-height: 1.6; }}
.slide-content ul li::before {{ content: "\\203A"; position: absolute; left: 0; top: 5px; color: {accent};
    font-weight: bold; font-size: 16px; line-height: 22px; }}
.slide-content .note {{ font-size: 11px; color: rgba(255,255,255,0.45); margin-top: auto;
    padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.1); }}
table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
table th {{ background: rgba(255,255,255,0.1); color: {accent}; padding: 10px 14px; text-align: left;
    font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }}
table td {{ padding: 10px 14px; border-bottom: 1px solid rgba(255,255,255,0.08); color: rgba(255,255,255,0.85); }}
table tr:last-child td {{ font-weight: 700; color: {accent}; border-top: 2px solid {rgba(accent,0.3)}; border-bottom: none; }}
"""


_AUTOSCALE = """
<script>
(function () {
    var SLIDE_WIDTH = 960, MAX_ZOOM = 1.9, PADDING = 48;
    function fit() {
        var avail = document.documentElement.clientWidth - PADDING;
        var zoom = Math.min(avail / SLIDE_WIDTH, MAX_ZOOM);
        if (zoom < 0.5) zoom = 0.5;
        document.body.style.zoom = zoom;
    }
    window.addEventListener('resize', fit);
    fit();
})();
</script>
"""


def _title_slide(deck, brand, logo, client, bg_style, num, total) -> str:
    org = deck.get("org") or brand.org_name
    date = deck.get("date") or brand.date or ""
    subtitle = f'<h2>{_esc(deck["subtitle"])}</h2>' if deck.get("subtitle") else ""
    return (
        f'<div class="slide slide-title"{bg_style}>{logo}{client}'
        f'<h1>{_esc(deck["title"])}</h1>{subtitle}'
        f'<div class="presenter"><div class="name">{_esc(org)}</div>'
        f'<div class="role">{_esc(date)}</div></div>'
        f'<span class="slide-number">{num} / {total}</span></div>'
    )


def _table_slide(slide, logo, num, total) -> str:
    cols = "".join(f"<th>{_esc(c)}</th>" for c in slide["columns"])
    rows = ""
    for row in slide["rows"]:
        rows += "<tr>" + "".join(f"<td>{_esc(c)}</td>" for c in row) + "</tr>"
    return (
        f'<div class="slide slide-table">{logo}<h2>{_esc(slide["heading"])}</h2>'
        f"<table><thead><tr>{cols}</tr></thead><tbody>{rows}</tbody></table>"
        f'<span class="slide-number">{num} / {total}</span></div>'
    )


def _content_slide(slide, logo, num, total) -> str:
    hero = f'<div class="hero-figure">{_esc(slide["hero"])}</div>' if slide.get("hero") else ""
    # bullets are trusted author HTML (content-module convention)
    lis = "".join(f"<li>{b}</li>" for b in slide.get("bullets", []))
    note = f'<div class="note">{slide["note"]}</div>' if slide.get("note") else ""
    return (
        f'<div class="slide slide-content">{logo}<h2>{_esc(slide["heading"])}</h2>{hero}'
        f"<ul>{lis}</ul>{note}"
        f'<span class="slide-number">{num} / {total}</span></div>'
    )


def build_deck_html(deck: dict, brand: Optional[BrandConfig] = None) -> str:
    """Render a deck dict into a self-contained, auto-scaling HTML string."""
    brand = brand or BrandConfig()
    logo = f'<img src="{b64_uri(brand.logo_path)}" class="logo" alt="logo">' \
        if brand.logo_path and Path(brand.logo_path).exists() else ""
    client = f'<img src="{b64_uri(brand.client_logo_path)}" class="client-logo" alt="client">' \
        if brand.client_logo_path and Path(brand.client_logo_path).exists() else ""
    bg_style = f' style="background-image:url(\'{b64_uri(brand.background_path)}\')"' \
        if brand.background_path and Path(brand.background_path).exists() else ""

    total = 1 + len(deck.get("slides", []))
    parts = [_title_slide(deck, brand, logo, client, bg_style, 1, total)]
    for i, slide in enumerate(deck.get("slides", []), 2):
        if slide["type"] == "table":
            parts.append(_table_slide(slide, logo, i, total))
        elif slide["type"] == "content":
            parts.append(_content_slide(slide, logo, i, total))
        else:
            raise ValueError(f"Unknown slide type: {slide['type']}")

    body = "\n".join(parts)
    return (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"UTF-8\">\n"
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        f"<title>{_esc(deck['title'])}</title>\n<style>{_deck_css(brand)}</style>\n"
        f"</head>\n<body>\n{body}\n{_AUTOSCALE}\n</body>\n</html>"
    )


def write_deck(deck: dict, output_path, brand: Optional[BrandConfig] = None) -> Path:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_deck_html(deck, brand), encoding="utf-8")
    return out
