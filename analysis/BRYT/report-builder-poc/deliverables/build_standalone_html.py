"""
Build the standalone Report Builder POC summary presentation (HTML) with embedded
base64 images.

Estimate figures are read from the shared `figures` module (single source of
truth: the POC estimates spreadsheet), not hardcoded. The deck auto-scales to
fill the viewport width (16:9, capped) via a small resize script using CSS `zoom`.

Stripped clone of `../../report-builder/deliverables/build_standalone_html.py`.
The story is the POC pitch: what the demo shows, what it costs to build, and the
explicit line between the POC and the full production build.

Usage:
    python analysis/BRYT/report-builder-poc/deliverables/build_standalone_html.py
"""
import base64
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import figures as F  # noqa: E402

ASSETS = HERE / "assets"
OUTPUT = HERE / "outputs" / "presentation-preview.html"


def b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode()


logo_uri = f"data:image/png;base64,{b64(ASSETS / 'd55-logo-white.png')}"
bg_uri = f"data:image/jpeg;base64,{b64(ASSETS / 'D55_TEAMS_BACKGROUND_No_LOGO.jpg')}"
bryt_uri = f"data:image/png;base64,{b64(ASSETS / 'bryt-energy.png')}"


def f(key):
    return F.FIGURES[key]


gt = F.grand_total()

# Fixed narrative slides (not tied to a phase figure).
# --- "What the POC shows" (kept) and "What we defer" (stripped) --------------
KEPT_SLIDE = ("What the POC shows the client", None, [
    "<strong>Builder canvas</strong> - drag tables from a palette, connect joins visually",
    "<strong>Column picker</strong> - choose exactly what each table contributes",
    "<strong>AI assistant</strong> - refine the report in plain language; the canvas updates live",
    "<strong>Preview</strong> - an instant sample of the output",
    "<strong>Run &amp; download</strong> - a real CSV result to finish on",
], "The demo proves the experience - the assistant is the star")

STRIPPED_SLIDE = ("What the POC deliberately defers", None, [
    "The whole <strong>governance &amp; security spine</strong> - per-customer isolation, output verifier, injection defence, query bounds",
    "Production infrastructure - Step Functions, DynamoDB single-table, versioned S3, IAM + Lake Formation, JWT auth",
    "Multi-tenant identity + admin override - the POC runs one demo user against one configured scope",
    "Run cancellation, deep history, presigned downloads, conversation persistence",
], "All of this lands in the full build on green-light - not a hardened POC")

# Phase slides: (title, phase-figure key, bullets, note)
PHASE_SLIDES = [
    ("Phase 1: Foundations", "phase1", [
        "Lightweight project scaffold (api/ + web/) - not the strict production repo layout",
        "Shared <strong>Report_Design</strong> domain types - same shapes as the full spec, so they carry forward",
        "Bring in the Join_Manifest + pick the minimal demo table set; define the single demo scope + fixed LIMIT",
    ], "The kept pieces seed the production build later"),
    ("Phase 2: Query generation + validation", "phase2", [
        "<strong>validateDesign</strong> - allow-listed tables/columns + manifest joins only (a correctness check, not a security gate)",
        "<strong>Query_Generator</strong> - design &rarr; Athena SQL, scoped to the demo scope, fixed LIMIT, bound parameters",
        "Report_Design serialise/deserialise round-trip",
    ], "No independent verifier - that is a full-build concern"),
    ("Phase 3: Backend services", "phase3", [
        "Catalog service - static / cached allow-list + Join_Manifest (no fail-closed governance)",
        "Reports CRUD against a simple store (one table or local JSON)",
        "<strong>Assistant</strong> - Bedrock Converse tool-use loop + Report_Design mutation tools",
        "Optional dry-run EXPLAIN polish (not a gate)",
    ], "The assistant is the centrepiece - prioritised over everything"),
    ("Phase 4: Run + preview + download", "phase4", [
        "Run handler: generate &rarr; Athena &rarr; CSV, polled to completion (no Step Functions)",
        "CSV download for a completed run",
        "Synchronous bounded preview (no run queued)",
    ], "Queued &rarr; Running &rarr; Complete / Failed - no Cancelled state"),
    ("Phase 5: Frontend (Angular Portal feature)", "phase5", [
        "Flow-canvas library spike (ngx-xyflow vs f-flow)",
        "Client Report_Design + pure graph mapping (canvas &harr; assistant in sync)",
        "The demo screens: My Reports, Builder, Column picker, Assistant drawer, Run, Preview, Save",
    ], "Simplified screens - single demo user, no auth"),
    ("Phase 6: Demo readiness", "phase6", [
        "Seed a couple of pre-built reports + demo data",
        "Script the &lsquo;ask the assistant&rsquo; moment so it lands reliably",
        "End-to-end run-through - smooth and repeatable in front of the client",
    ], "The rehearsal that makes the demo land"),
]

TOTAL_SLIDES = 3 + len(PHASE_SLIDES) + 1  # title + kept + stripped + phases + next steps


def slide_number(n):
    return f'<span class="slide-number">{n} / {TOTAL_SLIDES}</span>'


def content_slide(title, key, bullets, note, n):
    hero = f'<div class="hero-figure">~{F.fmt(f(key).total)} days</div>' if key else ""
    lis = "".join(f"<li>{b}</li>" for b in bullets)
    note_html = f'<div class="note">{note}</div>' if note else ""
    return f"""
<div class="slide slide-content">
    <img src="{logo_uri}" class="logo" alt="D55">
    <h2>{title}</h2>
    {hero}
    <ul>{lis}</ul>
    {note_html}
    {slide_number(n)}
</div>"""


# --- Summary table rows ------------------------------------------------------
summary_rows = ""
for k in F.phase_keys():
    fig = f(k)
    summary_rows += (
        f"<tr><td>{fig.name}</td><td>{F.fmt(fig.required)}</td><td>{F.fmt(fig.total)}</td></tr>"
    )
summary_rows += (
    f"<tr><td>TOTAL</td><td>{F.fmt(gt.required)}</td><td>{F.fmt(gt.total)}</td></tr>"
)

# --- Build slides ------------------------------------------------------------
# Slide 1 title, 2 kept, 3 stripped, 4 summary table, then phases, then next steps.
n = 2
kept_html = content_slide(*KEPT_SLIDE, n); n += 1
stripped_html = content_slide(*STRIPPED_SLIDE, n); n += 1
# summary table is slide n
summary_slide_no = n; n += 1
phase_html = ""
for title, key, bullets, note in PHASE_SLIDES:
    phase_html += content_slide(title, key, bullets, note, n)
    n += 1

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BRYT Report Builder POC - Estimate Playback</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; background: #0d0d1a; padding: 24px; }}
        .slide {{
            width: 960px; height: 540px; margin: 0 auto 40px;
            border-radius: 6px; overflow: hidden; position: relative;
            box-shadow: 0 8px 32px rgba(0,0,0,0.4);
            background: linear-gradient(135deg, #1a0a3e 0%, #1c1458 30%, #1e2a6e 70%, #0a4a8c 100%);
            color: white; padding: 48px 56px; display: flex; flex-direction: column;
        }}
        .slide .logo {{ position: absolute; top: 24px; right: 28px; height: 36px; }}
        .slide-number {{ position: absolute; bottom: 16px; right: 24px; font-size: 11px; color: rgba(255,255,255,0.35); }}

        /* Title slide */
        .slide-title {{
            background-image: url('{bg_uri}'); background-size: cover; background-position: center;
            justify-content: center; padding-left: 56px;
        }}
        .slide-title::after {{
            content: ''; position: absolute; inset: 0;
            background: linear-gradient(135deg, rgba(26,10,62,0.8) 0%, rgba(28,20,88,0.6) 50%, rgba(10,74,140,0.5) 100%);
            z-index: 0;
        }}
        .slide-title > * {{ position: relative; z-index: 1; }}
        .slide-title .slide-number {{ position: absolute; bottom: 16px; right: 24px; z-index: 1; }}
        .slide-title .logo {{ position: absolute; top: 24px; right: 28px; height: 44px; z-index: 1; }}
        .slide-title h1 {{ font-size: 44px; font-weight: 700; line-height: 1.15; margin-bottom: 16px; max-width: 62%; }}
        .slide-title h2 {{ font-size: 18px; font-weight: 300; opacity: 0.8; }}
        .slide-title .badge {{ display: inline-block; margin-top: 20px; padding: 6px 14px; border: 1px solid rgba(93,173,226,0.6); border-radius: 20px; font-size: 13px; color: #9fd0f0; }}
        .slide-title .presenter {{ position: absolute; bottom: 48px; left: 56px; z-index: 1; }}
        .slide-title .presenter .name {{ font-size: 16px; font-weight: 600; }}
        .slide-title .presenter .role {{ font-size: 13px; opacity: 0.6; margin-top: 2px; }}
        .slide-title .bryt-logo {{ position: absolute; bottom: 40px; right: 56px; height: 40px; z-index: 1; }}

        /* Content slides */
        .slide-content h2 {{ font-size: 20px; font-weight: 700; margin-bottom: 18px; padding-bottom: 10px; border-bottom: 2px solid rgba(255,255,255,0.2); }}
        .slide-content .hero-figure {{ font-size: 36px; font-weight: 700; color: #5dade2; margin-bottom: 16px; }}
        .slide-content ul {{ list-style: none; flex: 1; }}
        .slide-content ul li {{ font-size: 14px; color: rgba(255,255,255,0.85); padding: 5px 0; padding-left: 20px; position: relative; line-height: 1.55; }}
        .slide-content ul li::before {{ content: "\\203A"; position: absolute; left: 0; top: 5px; color: #5dade2; font-weight: bold; font-size: 16px; line-height: 22px; }}
        .slide-content .note {{ font-size: 11px; color: rgba(255,255,255,0.45); margin-top: auto; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.1); }}

        /* Table slide */
        .slide-table h2 {{ font-size: 20px; font-weight: 700; margin-bottom: 18px; padding-bottom: 10px; border-bottom: 2px solid rgba(255,255,255,0.2); }}
        table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
        table th {{ background: rgba(255,255,255,0.1); color: #5dade2; padding: 8px 14px; text-align: left; font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }}
        table td {{ padding: 7px 14px; border-bottom: 1px solid rgba(255,255,255,0.08); color: rgba(255,255,255,0.85); }}
        table tr:last-child td {{ font-weight: 700; color: #5dade2; border-top: 2px solid rgba(93,173,226,0.3); border-bottom: none; }}
    </style>
</head>
<body>

<!-- SLIDE 1: Title -->
<div class="slide slide-title">
    <img src="{logo_uri}" class="logo" alt="D55">
    <img src="{bryt_uri}" class="bryt-logo" alt="BRYT Energy">
    <h1>Report Builder</h1>
    <h2>Self-Service Reporting &mdash; Proof of Concept</h2>
    <div><span class="badge">Demo scope &mdash; not the production build</span></div>
    <div class="presenter">
        <div class="name">D55 Consulting</div>
        <div class="role">August 2026</div>
    </div>
    {slide_number(1)}
</div>

{kept_html}
{stripped_html}

<!-- Summary Table -->
<div class="slide slide-table">
    <img src="{logo_uri}" class="logo" alt="D55">
    <h2>POC Estimate Summary</h2>
    <table>
        <thead>
            <tr><th>Phase</th><th>Required (days)</th><th>Total (days)</th></tr>
        </thead>
        <tbody>
            {summary_rows}
        </tbody>
    </table>
    {slide_number(summary_slide_no)}
</div>

{phase_html}

<!-- FINAL SLIDE: Next Steps -->
<div class="slide slide-content">
    <img src="{logo_uri}" class="logo" alt="D55">
    <h2>Next Steps</h2>
    <div class="hero-figure">~{F.fmt(gt.total)} developer days for the POC</div>
    <ul>
        <li>Build the POC demo from Phase 1 - prioritise the assistant, the star of the demo</li>
        <li>Run against the dev twin (or a small fixture) as a single demo user / demo scope</li>
        <li>Showcase to the client; gather feedback on the experience</li>
        <li>On green-light, build the full production spec (with the security spine + infrastructure) - <strong>not</strong> a hardened POC</li>
    </ul>
    <div class="note">The full feature - requirements, design, 38-task plan, and its own estimate - lives alongside this POC in the report-builder spec.</div>
    {slide_number(TOTAL_SLIDES)}
</div>

<script>
    // Auto-scale slides to fill the viewport width (preserving 16:9). Uses CSS
    // `zoom` (reserves layout space so slides stack), capped for wide screens.
    (function () {{
        var SLIDE_WIDTH = 960, MAX_ZOOM = 1.9, PADDING = 48;
        function fit() {{
            var avail = document.documentElement.clientWidth - PADDING;
            var zoom = Math.min(avail / SLIDE_WIDTH, MAX_ZOOM);
            if (zoom < 0.5) zoom = 0.5;
            document.body.style.zoom = zoom;
        }}
        window.addEventListener('resize', fit);
        fit();
    }})();
</script>

</body>
</html>'''

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(html, encoding="utf-8")
print(f"Standalone HTML saved: {OUTPUT}")
print(f"File size: {len(html) / 1024:.0f} KB  ({TOTAL_SLIDES} slides)")
