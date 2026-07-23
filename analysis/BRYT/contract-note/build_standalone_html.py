"""
Build standalone HTML presentation with embedded base64 images.

Estimate figures are read from the shared `figures` module (single source of
truth: the estimates spreadsheet), not hardcoded.
"""
import base64
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import figures as F  # noqa: E402

# Encode assets
with open('analysis/BRYT/contract-note/assets/d55-logo-white.png', 'rb') as f:
    logo_b64 = base64.b64encode(f.read()).decode()

with open('analysis/BRYT/contract-note/assets/D55_TEAMS_BACKGROUND_No_LOGO.jpg', 'rb') as f:
    bg_b64 = base64.b64encode(f.read()).decode()

with open('analysis/BRYT/contract-note/assets/bryt-energy.png', 'rb') as f:
    bryt_b64 = base64.b64encode(f.read()).decode()

logo_uri = f"data:image/png;base64,{logo_b64}"
bg_uri = f"data:image/jpeg;base64,{bg_b64}"
bryt_uri = f"data:image/png;base64,{bryt_b64}"

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BRYT Contract Note Rework - Estimates</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; background: #0d0d1a; padding: 24px; }}
        .slide {{
            width: 960px;
            height: 540px;
            margin: 0 auto 40px;
            border-radius: 6px;
            overflow: hidden;
            position: relative;
            box-shadow: 0 8px 32px rgba(0,0,0,0.4);
            background: linear-gradient(135deg, #1a0a3e 0%, #1c1458 30%, #1e2a6e 70%, #0a4a8c 100%);
            color: white;
            padding: 48px 56px;
            display: flex;
            flex-direction: column;
        }}
        .slide .logo {{
            position: absolute;
            top: 24px;
            right: 28px;
            height: 36px;
        }}
        .slide-number {{
            position: absolute;
            bottom: 16px;
            right: 24px;
            font-size: 11px;
            color: rgba(255,255,255,0.35);
        }}

        /* Title slide */
        .slide-title {{
            background-image: url('{bg_uri}');
            background-size: cover;
            background-position: center;
            justify-content: center;
            padding-left: 56px;
        }}
        .slide-title::after {{
            content: '';
            position: absolute;
            inset: 0;
            background: linear-gradient(135deg, rgba(26,10,62,0.8) 0%, rgba(28,20,88,0.6) 50%, rgba(10,74,140,0.5) 100%);
            z-index: 0;
        }}
        .slide-title > * {{ position: relative; z-index: 1; }}
        .slide-title .slide-number {{ position: absolute; bottom: 16px; right: 24px; z-index: 1; }}
        .slide-title .logo {{ position: absolute; top: 24px; right: 28px; height: 44px; z-index: 1; }}
        .slide-title h1 {{
            font-size: 44px;
            font-weight: 700;
            line-height: 1.15;
            margin-bottom: 16px;
            max-width: 55%;
        }}
        .slide-title h2 {{
            font-size: 18px;
            font-weight: 300;
            opacity: 0.8;
        }}
        .slide-title .presenter {{
            position: absolute;
            bottom: 48px;
            left: 56px;
            z-index: 1;
        }}
        .slide-title .presenter .name {{ font-size: 16px; font-weight: 600; }}
        .slide-title .presenter .role {{ font-size: 13px; opacity: 0.6; margin-top: 2px; }}
        .slide-title .bryt-logo {{
            position: absolute;
            bottom: 40px;
            right: 56px;
            height: 40px;
            z-index: 1;
        }}

        /* Content slides */
        .slide-content h2 {{
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(255,255,255,0.2);
        }}
        .slide-content .hero-figure {{
            font-size: 38px;
            font-weight: 700;
            color: #5dade2;
            margin-bottom: 20px;
        }}
        .slide-content ul {{
            list-style: none;
            flex: 1;
        }}
        .slide-content ul li {{
            font-size: 14px;
            color: rgba(255,255,255,0.85);
            padding: 5px 0;
            padding-left: 20px;
            position: relative;
            line-height: 1.6;
        }}
        .slide-content ul li::before {{
            content: "\\203A";
            position: absolute;
            left: 0;
            top: 5px;
            color: #5dade2;
            font-weight: bold;
            font-size: 16px;
            line-height: 22px;
        }}
        .slide-content .note {{
            font-size: 11px;
            color: rgba(255,255,255,0.45);
            margin-top: auto;
            padding-top: 12px;
            border-top: 1px solid rgba(255,255,255,0.1);
        }}

        /* Table slide */
        .slide-table h2 {{
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(255,255,255,0.2);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        table th {{
            background: rgba(255,255,255,0.1);
            color: #5dade2;
            padding: 10px 14px;
            text-align: left;
            font-weight: 600;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        table td {{
            padding: 10px 14px;
            border-bottom: 1px solid rgba(255,255,255,0.08);
            color: rgba(255,255,255,0.85);
        }}
        table tr:last-child td {{
            font-weight: 700;
            color: #5dade2;
            border-top: 2px solid rgba(93,173,226,0.3);
            border-bottom: none;
        }}
    </style>
</head>
<body>

<!-- SLIDE 1: Title -->
<div class="slide slide-title">
    <img src="{logo_uri}" class="logo" alt="D55">
    <img src="{bryt_uri}" class="bryt-logo" alt="BRYT Energy">
    <h1>Contract Note Rework</h1>
    <h2>Estimate Playback</h2>
    <div class="presenter">
        <div class="name">D55 Consulting</div>
        <div class="role">July 2026</div>
    </div>
    <span class="slide-number">1 / 8</span>
</div>

<!-- SLIDE 2: Summary Table -->
<div class="slide slide-table">
    <img src="{logo_uri}" class="logo" alt="D55">
    <h2>Estimate Summary</h2>
    <table>
        <thead>
            <tr>
                <th>Estimate</th>
                <th>Required (days)</th>
                <th>Total (days)</th>
            </tr>
        </thead>
        <tbody>
            <tr><td>1. PDF / Template Management</td><td>{F.fmt(F.FIGURES['est1'].required)}</td><td>{F.fmt(F.FIGURES['est1'].total)}</td></tr>
            <tr><td>2. DocuSign Integration</td><td>{F.fmt(F.FIGURES['est2'].required)}</td><td>{F.fmt(F.FIGURES['est2'].total)}</td></tr>
            <tr><td>3a. Training &amp; Enablement</td><td>{F.fmt(F.FIGURES['est3a'].required)}</td><td>{F.fmt(F.FIGURES['est3a'].total)}</td></tr>
            <tr><td>3b. Data Source Extensibility</td><td>{F.fmt(F.FIGURES['est3b'].required)}</td><td>{F.fmt(F.FIGURES['est3b'].total)}</td></tr>
            <tr><td>4. Bespoke Contracts</td><td>{F.fmt(F.FIGURES['est4'].required)}</td><td>{F.fmt(F.FIGURES['est4'].total)}</td></tr>
            <tr><td>5. Comparison Audit</td><td>{F.fmt(F.FIGURES['est5'].required)}</td><td>{F.fmt(F.FIGURES['est5'].total)}</td></tr>
            <tr><td>TOTAL</td><td>{F.fmt(F.grand_total().required)}</td><td>{F.fmt(F.grand_total().total)}</td></tr>
        </tbody>
    </table>
    <span class="slide-number">2 / 8</span>
</div>

<!-- SLIDE 3: Est 1 -->
<div class="slide slide-content">
    <img src="{logo_uri}" class="logo" alt="D55">
    <h2>Est 1: PDF / Template Management</h2>
    <div class="hero-figure">~{F.fmt(F.FIGURES['est1'].total)} days</div>
    <ul>
        <li>Self-service template editor replacing the current developer-dependent pipeline</li>
        <li>Visual section editor (pdf-me) embedded in the Admin Portal</li>
        <li>Rules engine for template selection and per-section variants (first-match-wins)</li>
        <li>Shared sections for headers, footers, T&amp;Cs</li>
        <li>Render pipeline: Step Functions, per-section render + PDF stitch</li>
        <li>Version history with revert, plus publish-to-linked-templates</li>
    </ul>
    <span class="slide-number">3 / 8</span>
</div>

<!-- SLIDE 4: Est 2 -->
<div class="slide slide-content">
    <img src="{logo_uri}" class="logo" alt="D55">
    <h2>Est 2: DocuSign Integration</h2>
    <div class="hero-figure">~{F.fmt(F.FIGURES['est2'].total)} days</div>
    <ul>
        <li>Automated e-signature: PDF rendered &rarr; sent for signing &rarr; signed copy to Salesforce</li>
        <li>S3 trigger fires when contract note PDF is generated</li>
        <li>Customer details fetched from Salesforce (via BrytNumber)</li>
        <li>DocuSign envelope created + signing email sent automatically</li>
        <li>Webhook receives completion &rarr; stores signed PDF in S3 + Salesforce</li>
    </ul>
    <span class="slide-number">4 / 8</span>
</div>

<!-- SLIDE 5: Est 3 -->
<div class="slide slide-content">
    <img src="{logo_uri}" class="logo" alt="D55">
    <h2>Est 3: Training &amp; Data Sources</h2>
    <div class="hero-figure">~{F.fmt(F.FIGURES['est3'].total)} days</div>
    <ul>
        <li><strong style="color:#5dade2">3a. Training &amp; Enablement ({F.fmt(F.FIGURES['est3a'].total)} days):</strong> Quick-start guide, how-to guides, field reference, rules cheat sheet</li>
        <li><strong style="color:#5dade2">3b. Data Source Extensibility ({F.fmt(F.FIGURES['est3b'].total)} days):</strong></li>
        <li>Subscribe data sources in SageMaker Unified Studio &rarr; auto-discovered via Glue</li>
        <li>Attached to templates, enriched at render time via Athena (keyed on BrytNumber)</li>
        <li>Fields appear in the section editor for drag-and-drop use</li>
    </ul>
    <div class="note">3a and 3b can be prioritised independently</div>
    <span class="slide-number">5 / 8</span>
</div>

<!-- SLIDE 6: Est 4 -->
<div class="slide slide-content">
    <img src="{logo_uri}" class="logo" alt="D55">
    <h2>Est 4: Bespoke Contracts</h2>
    <div class="hero-figure">~{F.fmt(F.FIGURES['est4'].total)} days</div>
    <ul>
        <li>One-off contract notes for VIP/non-standard customers</li>
        <li>Pipeline skips bespoke-flagged customers automatically</li>
        <li>Users create bespoke contracts (clone from template or from scratch)</li>
        <li>Same section editor + shared sections as standard templates</li>
        <li>On-demand render + manual DocuSign trigger</li>
        <li>Full version and render history per document</li>
    </ul>
    <span class="slide-number">6 / 8</span>
</div>

<!-- SLIDE 7: Est 5 -->
<div class="slide slide-content">
    <img src="{logo_uri}" class="logo" alt="D55">
    <h2>Est 5: Comparison Audit</h2>
    <div class="hero-figure">~{F.fmt(F.FIGURES['est5'].total)} days</div>
    <ul>
        <li>Detect PDF tampering: compare rendered original vs what was actually sent</li>
        <li>Step Function batch pipeline (ad-hoc, e.g. monthly)</li>
        <li>Fetches sent PDFs from Outlook via Microsoft Graph API</li>
        <li>AI comparison via AWS Bedrock (identifies differences)</li>
        <li>Results queryable via Athena, delivered as spreadsheet</li>
    </ul>
    <div class="note">Dependency: Requires M365 admin to grant Graph API access</div>
    <span class="slide-number">7 / 8</span>
</div>

<!-- SLIDE 8: Next Steps -->
<div class="slide slide-content">
    <img src="{logo_uri}" class="logo" alt="D55">
    <h2>Next Steps</h2>
    <div class="hero-figure">~{F.fmt(F.grand_total().total)} developer days total</div>
    <ul>
        <li>Resolve open questions (11 items for client confirmation)</li>
        <li>Prioritise delivery order (estimates are sequential by default)</li>
        <li>Confirm optional scope (testing tasks &mdash; recommended but deferrable)</li>
        <li>Begin implementation from Estimate 1</li>
    </ul>
    <div class="note">Detailed specs, wireframes, and task breakdowns available on request for each estimate.</div>
    <span class="slide-number">8 / 8</span>
</div>

<script>
    // Auto-scale slides to fill the viewport width (preserving 16:9),
    // reproducing a comfortable zoom by default. Capped so it stays sensible
    // on very wide screens.
    (function () {{
        var SLIDE_WIDTH = 960;
        var MAX_ZOOM = 1.9;
        var PADDING = 48; // 24px each side (matches body padding * 2)
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

output_path = 'analysis/BRYT/contract-note/outputs/presentation-preview.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Standalone HTML saved: {output_path}")
print(f"File size: {len(html) / 1024:.0f} KB")
