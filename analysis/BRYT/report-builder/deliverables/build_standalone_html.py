"""
Build the standalone Report Builder summary presentation (HTML) with embedded
base64 images.

Estimate figures are read from the shared `figures` module (single source of
truth: the estimates spreadsheet), not hardcoded. The deck auto-scales to fill
the viewport width (16:9, capped) via a small resize script using CSS `zoom`.

Usage:
    python analysis/BRYT/report-builder/deliverables/build_standalone_html.py
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

# Slide definitions: (title, headline figure key or None, bullets, note)
CONTENT_SLIDES = [
    ("Phase 1: Repo & shared-lib foundations", "phase1", [
        "New <strong>BrytReportBuilder</strong> repo (api/, cdk/, shared-lib/), mirroring BrytBusinessServices",
        "Shared-lib domain types: Report_Design, Catalog, GeneratedQuery, Run",
        "Join_Manifest promoted into shared-lib as a typed, read-only model",
        "Shared HTTP + identity helpers",
    ], "Foundation for everything that follows"),
    ("Phase 2: Security spine", "phase2", [
        "<strong>validateDesign</strong> - allow-listed tables/columns, manifest joins only",
        "Server-side identity &rarr; authorised bryt numbers resolution",
        "<strong>Query_Generator</strong> - pins every table from trusted context; via-mpan CTE + date window",
        "<strong>Query_Verifier</strong> - independent pre-exec + result-set checks",
        "Serialise round-trip + spine property tests",
    ], "Built and tested before any query can execute"),
    ("Phase 3: CDK foundation", "phase3", [
        "Single DynamoDB table (PK/SK + name and run-recency GSIs)",
        "Versioned, encrypted, private S3 buckets (design snapshots + Result_Store)",
        "API Gateway REST tree + JWT authorizer",
        "Per-environment execution role: IAM + Lake Formation grants",
        "Athena workgroup with a bytes-scanned backstop",
    ], "dev and prod are separate accounts with separate grants"),
    ("Phase 4: Catalog + Reports CRUD", "phase4", [
        "Fail-closed Catalog service: curated allow-list intersected with Glue",
        "Read-only Join_Manifest endpoint",
        "Owner-scoped Reports create / read / update / delete / list",
        "Versioned S3 design snapshot on every save",
    ], None),
    ("Phase 5: Assistant + query generation", "phase5", [
        "Bedrock <strong>Converse</strong> tool-use loop in a Lambda (not managed Agents)",
        "Report_Design mutation tools, each through validateDesign",
        "Forced <strong>validate_query</strong> (Athena EXPLAIN) before finalising a change",
        "Conversation persistence per report + owner",
        "Prompt-injection defence + audit logging of ignored attempts",
    ], "The model is untrusted-by-design; the verifier is the boundary"),
    ("Phase 6: Run pipeline + preview + download", "phase6", [
        "Step Functions: generate &rarr; verify &rarr; execute &rarr; write CSV &rarr; finalise (catch on every state)",
        "Run queue / status / list APIs (up to 50 most-recent)",
        "Cancel API + terminal-state protection",
        "CSV download via short-lived pre-signed URL",
        "Synchronous bounded preview (no run queued)",
    ], None),
    ("Phase 7: Frontend (Angular Portal extension)", "phase7", [
        "Flow-canvas library spike (ngx-xyflow vs f-flow)",
        "Shared client Report_Design + pure graph mapping (canvas &harr; assistant in sync)",
        "The seven screens: My Reports, Builder, Column picker, Assistant, Run &amp; history, Preview, Save",
        "Client-side validation mirrored for UX; the server re-validates authoritatively",
    ], "The client never sends identity or bryt numbers"),
    ("Phase 8: Hardening, tests, deploy", "phase8", [
        "Security suite: cross-tenant isolation, injection, bounds, verifier independence",
        "Observability: logging, tracing, alarms on verification failures",
        "CI/CD pipeline for BrytReportBuilder",
        "End-to-end walkthrough against a dev stage + sign-off",
    ], "Asserts the 13 correctness properties end-to-end"),
]

TOTAL_SLIDES = 2 + len(CONTENT_SLIDES) + 1  # title + summary + phases + next steps


def slide_number(n):
    return f'<span class="slide-number">{n} / {TOTAL_SLIDES}</span>'


# --- Summary table rows ------------------------------------------------------
summary_rows = ""
for k in F.phase_keys():
    fig = f(k)
    label = fig.name  # 'Phase N: ...'
    summary_rows += (
        f"<tr><td>{label}</td><td>{F.fmt(fig.required)}</td><td>{F.fmt(fig.total)}</td></tr>"
    )
summary_rows += (
    f"<tr><td>TOTAL</td><td>{F.fmt(gt.required)}</td><td>{F.fmt(gt.total)}</td></tr>"
)

# --- Content slides ----------------------------------------------------------
content_html = ""
n = 3
for title, key, bullets, note in CONTENT_SLIDES:
    hero = f'<div class="hero-figure">~{F.fmt(f(key).total)} days</div>' if key else ""
    lis = "".join(f"<li>{b}</li>" for b in bullets)
    note_html = f'<div class="note">{note}</div>' if note else ""
    content_html += f"""
<div class="slide slide-content">
    <img src="{logo_uri}" class="logo" alt="D55">
    <h2>{title}</h2>
    {hero}
    <ul>{lis}</ul>
    {note_html}
    {slide_number(n)}
</div>"""
    n += 1

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BRYT Report Builder - Estimate Playback</title>
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
    <h2>Self-Service Reporting &mdash; Estimate Playback</h2>
    <div class="presenter">
        <div class="name">D55 Consulting</div>
        <div class="role">August 2026</div>
    </div>
    {slide_number(1)}
</div>

<!-- SLIDE 2: Summary Table -->
<div class="slide slide-table">
    <img src="{logo_uri}" class="logo" alt="D55">
    <h2>Estimate Summary</h2>
    <table>
        <thead>
            <tr><th>Phase</th><th>Required (days)</th><th>Total (days)</th></tr>
        </thead>
        <tbody>
            {summary_rows}
        </tbody>
    </table>
    {slide_number(2)}
</div>

{content_html}

<!-- FINAL SLIDE: Next Steps -->
<div class="slide slide-content">
    <img src="{logo_uri}" class="logo" alt="D55">
    <h2>Next Steps</h2>
    <div class="hero-figure">~{F.fmt(gt.total)} developer days total</div>
    <ul>
        <li>Confirm the working assumptions carried from Phase 0.5 (preview, bounds, retention, allow-list)</li>
        <li>Confirm optional scope (property, integration, and security tests &mdash; recommended but deferrable)</li>
        <li>Resolve the one deferral: prod value-verification of the mpan mapping (needs a scoped Lake Formation grant)</li>
        <li>Begin implementation from Phase 1; build and test the security spine before any execution path</li>
    </ul>
    <div class="note">Design, requirements, 38-task plan, walkthrough, data model, and API reference available alongside this deck.</div>
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

OUTPUT.write_text(html, encoding="utf-8")
print(f"Standalone HTML saved: {OUTPUT}")
print(f"File size: {len(html) / 1024:.0f} KB  ({TOTAL_SLIDES} slides)")
