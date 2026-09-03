"""
Print-oriented stylesheet for the walkthrough engine, parameterised by BrandConfig.

Kept in its own module so ``walkthrough.py`` stays focused on structure. Colours,
font and the cover background all come from the brand config; if no background
image is set the cover falls back to the brand gradient.
"""
from __future__ import annotations

from .brand import BrandConfig, b64_uri, rgba


def build_css(brand: BrandConfig) -> str:
    primary, accent, deep, text = brand.primary, brand.accent, brand.deep, brand.text
    font = brand.font_family

    # Cover background: image (under a brand-gradient overlay) or plain gradient.
    if brand.background_path and brand.background_path.exists():
        cover_bg = f"background-image: url('{b64_uri(brand.background_path)}'); background-size: cover; background-position: center;"
        overlay = (
            f"content: ''; position: absolute; inset: 0; background: linear-gradient(135deg, "
            f"{rgba(primary, 0.88)} 0%, {rgba(deep, 0.72)} 50%, {rgba(deep, 0.6)} 100%);"
        )
    else:
        cover_bg = f"background: linear-gradient(135deg, {primary} 0%, {deep} 100%);"
        overlay = "content: none;"

    return f"""
@page {{ size: A4 portrait; margin: 24mm 22mm 22mm 22mm; }}
@page cover {{ size: A4 portrait; margin: 0; }}

* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: {font}; color: {text}; font-size: 11pt; line-height: 1.65; }}
h1, h2, h3, h4 {{ color: {primary}; }}
p {{ margin: 0 0 10px; }}

/* Cover */
.cover {{
    page: cover; position: relative; width: 210mm; height: 297mm;
    {cover_bg}
    overflow: hidden; color: #fff; page-break-after: always;
}}
.cover::after {{ {overlay} }}
.cover > * {{ position: relative; z-index: 1; }}
.cover .logo {{ position: absolute; top: 30px; right: 34px; height: 50px; }}
.cover .client-logo {{ position: absolute; bottom: 46px; right: 46px; height: 42px; }}
.cover .cover-inner {{ position: absolute; top: 40%; left: 52px; right: 52px; }}
.cover .eyebrow {{
    font-size: 13pt; font-weight: 300; letter-spacing: 2px;
    text-transform: uppercase; opacity: 0.8; margin-bottom: 14px;
}}
.cover h1 {{ color: #fff; font-size: 38pt; font-weight: 700; line-height: 1.1; max-width: 88%; }}
.cover .subtitle {{ font-size: 16pt; font-weight: 300; opacity: 0.85; margin-top: 16px; }}
.cover .effort {{
    display: inline-block; margin-top: 30px; padding: 9px 18px;
    background: {rgba(accent, 0.25)}; border: 1px solid {rgba(accent, 0.5)};
    border-radius: 4px; font-size: 13pt; font-weight: 600; color: #d7ecfa;
}}
.cover .meta {{ position: absolute; bottom: 50px; left: 52px; }}
.cover .meta .org {{ font-size: 12pt; font-weight: 600; }}
.cover .meta .date {{ font-size: 10pt; opacity: 0.6; margin-top: 2px; }}

/* Content */
.content {{ padding-top: 2px; }}
.block {{ margin-bottom: 24px; }}
h2 {{ font-size: 17pt; font-weight: 700; margin-bottom: 12px; padding-bottom: 7px; border-bottom: 2px solid #e2e2ee; }}
h3 {{ font-size: 13pt; font-weight: 600; margin-bottom: 7px; }}
h4 {{ font-size: 9.5pt; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: {deep}; margin-bottom: 6px; }}

ul.bullets {{ list-style: none; margin: 6px 0; }}
ul.bullets li {{ position: relative; padding-left: 18px; margin-bottom: 6px; }}
ul.bullets li::before {{ content: '\\203A'; position: absolute; left: 0; top: -1px; color: {accent}; font-weight: bold; font-size: 13pt; }}

/* Tables */
table.data-table {{ width: 100%; border-collapse: collapse; font-size: 10pt; margin-top: 8px; }}
table.data-table th {{ background: {primary}; color: #d7ecfa; text-align: left; padding: 8px 11px; font-size: 8.5pt; text-transform: uppercase; letter-spacing: 0.4px; }}
table.data-table td {{ padding: 7px 11px; border-bottom: 1px solid #e6e6f0; vertical-align: top; }}
table.data-table tr:nth-child(even) td {{ background: #f6f6fb; }}

/* Diagrams */
figure.diagram {{ text-align: center; margin-top: 10px; page-break-inside: avoid; }}
figure.diagram img {{ max-width: 100%; max-height: 150mm; border: 1px solid #e2e2ee; border-radius: 4px; }}
figcaption {{ font-size: 8.5pt; color: #6a6a80; margin-top: 8px; font-style: italic; }}

/* Screens */
.screen {{ page-break-inside: avoid; margin-bottom: 26px; }}
figure.shot {{ margin: 8px 0 12px; }}
figure.shot img {{ width: 100%; border: 1px solid #d8d8e6; border-radius: 5px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
.cols {{ display: flex; gap: 26px; margin-top: 10px; }}
.cols .col {{ flex: 1; }}

/* Callout */
.callout {{ background: #f0f6fc; border-left: 4px solid {accent}; padding: 14px 18px; border-radius: 0 4px 4px 0; }}
.callout h3 {{ color: {deep}; }}

/* Flow diagrams (CSS-rendered) */
figure.flow {{ margin: 12px 0 6px; page-break-inside: avoid; }}
.layers {{ display: flex; flex-direction: column; gap: 4px; }}
.lane {{ border: 1.5px solid #c9c9dc; border-radius: 6px; background: #f8f8fc; padding: 9px 11px 11px; }}
.lane-label {{ font-size: 8pt; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; color: {deep}; margin-bottom: 8px; }}
.lane-nodes {{ display: flex; flex-wrap: wrap; gap: 8px; }}
.lane-nodes .node {{ flex: 1; min-width: 110px; text-align: center; background: #fff; border: 1.5px solid {accent}; border-radius: 5px; padding: 9px 6px; font-size: 8.5pt; font-weight: 600; color: {primary}; }}
.lane-arrow {{ text-align: center; color: {accent}; font-size: 12pt; line-height: 1; margin: -1px 0; }}

.pipeline {{ display: flex; align-items: stretch; gap: 4px; }}
.pipeline .step {{ flex: 1; text-align: center; background: {primary}; color: #fff; border-radius: 5px; padding: 11px 6px; font-size: 8pt; font-weight: 600; display: flex; align-items: center; justify-content: center; }}
.pipeline .step-arrow {{ color: {accent}; font-size: 11pt; align-self: center; }}

/* Entity (record) definitions */
.table-name {{ font-size: 10pt; color: {text}; margin-bottom: 14px; }}
.table-name code {{ background: {primary}; color: #d7ecfa; padding: 2px 8px; border-radius: 3px; font-size: 9.5pt; }}
.entity {{ border: 1px solid #d8d8e6; border-radius: 6px; padding: 12px 14px; margin-bottom: 14px; page-break-inside: avoid; background: #fcfcfe; }}
.entity h3 {{ margin-bottom: 8px; }}
.entity .keys {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 10px; }}
.entity .key {{ display: inline-flex; align-items: stretch; border-radius: 4px; overflow: hidden; border: 1px solid {accent}; font-size: 9pt; }}
.entity .key-label {{ background: {accent}; color: #fff; font-weight: 700; padding: 3px 8px; display: flex; align-items: center; }}
.entity .key code {{ padding: 3px 9px; color: {primary}; background: #eaf4fb; display: flex; align-items: center; }}
.entity .entity-note {{ font-size: 9.5pt; color: #55556a; margin-bottom: 8px; }}
code {{ font-family: 'Consolas', 'Monaco', monospace; }}
table.attr-table {{ font-size: 9pt; }}
table.attr-table td code {{ font-size: 8.5pt; color: {deep}; }}
table.attr-table td.type {{ color: #6a6a80; font-style: italic; white-space: nowrap; }}
.gsi-block {{ margin-top: 6px; page-break-inside: avoid; }}
.gsi-block table code {{ font-size: 8.5pt; color: {deep}; }}

.section-break {{ page-break-before: always; }}

/* Page-break control */
h2, h3, h4 {{ break-after: avoid; page-break-after: avoid; }}
h2 + *, h3 + * {{ break-before: avoid; page-break-before: avoid; }}
figure.flow, figure.diagram, .callout, .block-layers, .block-pipeline {{ break-inside: avoid; page-break-inside: avoid; }}
table.data-table {{ break-inside: auto; }}
table.data-table tr {{ break-inside: avoid; page-break-inside: avoid; }}
table.data-table thead {{ display: table-header-group; }}
p, li {{ orphans: 2; widows: 2; }}

/* On-screen preview only */
@media screen {{
    body {{ background: #52526a; }}
    .cover {{ margin: 0 auto; box-shadow: 0 4px 24px rgba(0,0,0,0.4); }}
    .content {{ width: 210mm; min-height: 297mm; margin: 24px auto; background: #fff; padding: 24mm 22mm; box-shadow: 0 4px 24px rgba(0,0,0,0.4); }}
}}
"""
