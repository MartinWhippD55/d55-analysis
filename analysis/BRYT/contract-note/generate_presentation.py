"""
Generate BRYT Contract Note Rework presentation using D55 template.
Slim exec-level deck: 8 slides total.

Estimate figures are read from the shared `figures` module (single source of
truth: the estimates spreadsheet), not hardcoded.
"""
import sys
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

sys.path.insert(0, str(Path(__file__).resolve().parent))
import figures as F  # noqa: E402

# Load D55 template
template_path = 'analysis/D55/ai-dlc/assets/powerpoint/D55_Deck_Visual_NO ANIMATION Template (1).pptx'
prs = Presentation(template_path)

# Remove all existing slides
while len(prs.slides) > 0:
    rId = prs.slides._sldIdLst[0].rId
    prs.part.drop_rel(rId)
    del prs.slides._sldIdLst[0]

# Helpers
def add_slide(layout_idx):
    return prs.slides.add_slide(prs.slide_layouts[layout_idx])

def clear_placeholders(slide):
    for ph in slide.placeholders:
        ph.text_frame.clear()

def set_text(text_frame, text, size=18, bold=False, color=None, alignment=PP_ALIGN.LEFT):
    text_frame.clear()
    p = text_frame.paragraphs[0]
    p.alignment = alignment
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    if color:
        run.font.color.rgb = color

def add_body_lines(text_frame, lines, size=13):
    text_frame.clear()
    for i, line in enumerate(lines):
        p = text_frame.paragraphs[0] if i == 0 else text_frame.add_paragraph()
        run = p.add_run()
        run.text = line
        run.font.size = Pt(size)
        if line.startswith("~") or line.startswith("Estimate:") or line.startswith("Total:"):
            run.font.bold = True
            run.font.size = Pt(size + 2)

# ============================================================
# SLIDE 1: Title
# ============================================================
slide = add_slide(0)  # 1_Title
clear_placeholders(slide)
for ph in slide.placeholders:
    if ph.placeholder_format.idx == 0:
        set_text(ph.text_frame, "Contract Note Rework", size=32, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF))
    elif ph.placeholder_format.idx == 1:
        set_text(ph.text_frame, "Estimate Playback", size=18, color=RGBColor(0xFF, 0xFF, 0xFF))

# ============================================================
# SLIDE 2: Summary Table
# ============================================================
slide = add_slide(17)  # Table SLIDE
clear_placeholders(slide)
for ph in slide.placeholders:
    if ph.placeholder_format.idx == 0:
        set_text(ph.text_frame, "Estimate Summary", size=24, bold=True)

rows, cols = 8, 3
left, top, width, height = Inches(1.0), Inches(2.0), Inches(8.0), Inches(3.2)
table_shape = slide.shapes.add_table(rows, cols, left, top, width, height)
table = table_shape.table

table.columns[0].width = Inches(4.5)
table.columns[1].width = Inches(1.8)
table.columns[2].width = Inches(1.7)

# Headers
for col_idx, h in enumerate(['Estimate', 'Days (req)', 'Days (total)']):
    cell = table.cell(0, col_idx)
    cell.text = h
    for p in cell.text_frame.paragraphs:
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    cell.fill.solid()
    cell.fill.fore_color.rgb = RGBColor(0x1F, 0x4E, 0x79)

_gt = F.grand_total()
data = [
    ('1. PDF / Template Management', F.fmt(F.FIGURES['est1'].required), F.fmt(F.FIGURES['est1'].total)),
    ('2. DocuSign Integration', F.fmt(F.FIGURES['est2'].required), F.fmt(F.FIGURES['est2'].total)),
    ('3a. Training & Enablement', F.fmt(F.FIGURES['est3a'].required), F.fmt(F.FIGURES['est3a'].total)),
    ('3b. Data Source Extensibility', F.fmt(F.FIGURES['est3b'].required), F.fmt(F.FIGURES['est3b'].total)),
    ('4. Bespoke Contracts', F.fmt(F.FIGURES['est4'].required), F.fmt(F.FIGURES['est4'].total)),
    ('5. Comparison Audit', F.fmt(F.FIGURES['est5'].required), F.fmt(F.FIGURES['est5'].total)),
    ('TOTAL', F.fmt(_gt.required), F.fmt(_gt.total)),
]

for row_idx, row_data in enumerate(data, 1):
    for col_idx, val in enumerate(row_data):
        cell = table.cell(row_idx, col_idx)
        cell.text = val
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(11)
            if row_idx == len(data):
                p.font.bold = True

# ============================================================
# SLIDE 3: Est 1
# ============================================================
slide = add_slide(3)  # 1_Content
clear_placeholders(slide)
for ph in slide.placeholders:
    if ph.placeholder_format.idx == 0:
        set_text(ph.text_frame, "Est 1: PDF / Template Management", size=22, bold=True)
    elif ph.placeholder_format.idx == 1:
        add_body_lines(ph.text_frame, [
            f"~{F.fmt(F.FIGURES['est1'].total)} days",
            "",
            "Self-service template editor replacing the current developer-dependent pipeline.",
            "",
            "Visual section editor (pdf-me) embedded in the Admin Portal",
            "Rules engine for automated template selection (first-match-wins)",
            "Shared sections for headers, footers, T&Cs",
            "Render pipeline: section render + PDF stitch (Lambda)",
            "Version history with revert on all sections",
        ])

# ============================================================
# SLIDE 4: Est 2
# ============================================================
slide = add_slide(3)
clear_placeholders(slide)
for ph in slide.placeholders:
    if ph.placeholder_format.idx == 0:
        set_text(ph.text_frame, "Est 2: DocuSign Integration", size=22, bold=True)
    elif ph.placeholder_format.idx == 1:
        add_body_lines(ph.text_frame, [
            f"~{F.fmt(F.FIGURES['est2'].total)} days",
            "",
            "Automated e-signature: PDF rendered > sent for signing > signed copy to Salesforce.",
            "",
            "S3 trigger fires when contract note PDF is generated",
            "Customer details fetched from Salesforce (via BrytNumber)",
            "DocuSign envelope created + signing email sent automatically",
            "Webhook receives completion > stores signed PDF in S3 + Salesforce",
        ])

# ============================================================
# SLIDE 5: Est 3
# ============================================================
slide = add_slide(3)
clear_placeholders(slide)
for ph in slide.placeholders:
    if ph.placeholder_format.idx == 0:
        set_text(ph.text_frame, "Est 3: Training & Data Sources", size=22, bold=True)
    elif ph.placeholder_format.idx == 1:
        add_body_lines(ph.text_frame, [
            f"~{F.fmt(F.FIGURES['est3'].total)} days ({F.fmt(F.FIGURES['est3a'].total)} + {F.fmt(F.FIGURES['est3b'].total)})",
            "",
            f"3a. Training & Enablement ({F.fmt(F.FIGURES['est3a'].total)} days)",
            "Quick-start guide, how-to guides, field reference, cheat sheets",
            "",
            f"3b. Data Source Extensibility ({F.fmt(F.FIGURES['est3b'].total)} days)",
            "Subscribe data sources in SageMaker Unified Studio",
            "Auto-discovered via Glue Catalog, attached to templates",
            "Athena enrichment at render time (keyed on BrytNumber)",
            "Fields appear in the section editor for drag-and-drop use",
        ])

# ============================================================
# SLIDE 6: Est 4
# ============================================================
slide = add_slide(3)
clear_placeholders(slide)
for ph in slide.placeholders:
    if ph.placeholder_format.idx == 0:
        set_text(ph.text_frame, "Est 4: Bespoke Contracts", size=22, bold=True)
    elif ph.placeholder_format.idx == 1:
        add_body_lines(ph.text_frame, [
            f"~{F.fmt(F.FIGURES['est4'].total)} days",
            "",
            "One-off contract notes for VIP/non-standard customers.",
            "",
            "Pipeline skips bespoke-flagged customers automatically",
            "Users create bespoke contracts (clone from template or scratch)",
            "Same section editor + shared sections as standard templates",
            "On-demand render (Save & Render) + manual DocuSign trigger",
            "Full version history and render history per document",
        ])

# ============================================================
# SLIDE 7: Est 5
# ============================================================
slide = add_slide(3)
clear_placeholders(slide)
for ph in slide.placeholders:
    if ph.placeholder_format.idx == 0:
        set_text(ph.text_frame, "Est 5: Comparison Audit", size=22, bold=True)
    elif ph.placeholder_format.idx == 1:
        add_body_lines(ph.text_frame, [
            f"~{F.fmt(F.FIGURES['est5'].total)} days",
            "",
            "Detect PDF tampering: compare rendered original vs what was actually sent.",
            "",
            "Step Function batch pipeline (ad-hoc, e.g. monthly)",
            "Fetches sent PDFs from Outlook via Microsoft Graph API",
            "AI comparison via AWS Bedrock (identifies differences)",
            "Results queryable via Athena, delivered as spreadsheet",
            "",
            "Dependency: Requires M365 admin to grant Graph API access",
        ])

# ============================================================
# SLIDE 8: Next Steps
# ============================================================
slide = add_slide(3)
clear_placeholders(slide)
for ph in slide.placeholders:
    if ph.placeholder_format.idx == 0:
        set_text(ph.text_frame, "Next Steps", size=22, bold=True)
    elif ph.placeholder_format.idx == 1:
        add_body_lines(ph.text_frame, [
            f"Total: ~{F.fmt(F.grand_total().total)} developer days",
            "",
            "Resolve open questions (11 items for client confirmation)",
            "Prioritise delivery order (estimates are sequential by default)",
            "Confirm optional scope (testing tasks, recommended)",
            "Begin implementation from Estimate 1",
            "",
            "Detailed specs, wireframes, and task breakdowns available",
            "on request for each estimate.",
        ])

# Save
output_path = 'analysis/BRYT/contract-note/outputs/BRYT Contract Note Rework - Estimates.pptx'
prs.save(output_path)
print(f"Presentation saved: {output_path}")
print(f"Slides: {len(prs.slides)}")
