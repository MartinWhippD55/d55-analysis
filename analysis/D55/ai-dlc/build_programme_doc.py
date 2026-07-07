"""
AI-DLC programme overview document build.

Thin caller of the reusable engine (programme_engine.py): supplies the D55/AI-DLC
brand config and the content module, and invokes the build. All rendering logic
lives in the engine — this file is just wiring, the worked example for the
`new-programme` skill.

Usage:
    python build_programme_doc.py            # HTML + PDF
    python build_programme_doc.py --no-pdf   # HTML only
"""
import importlib
import sys
from pathlib import Path

from programme_engine import BrandConfig, build

ROOT = Path(__file__).resolve().parent  # analysis/D55/ai-dlc

D55_AIDLC = BrandConfig(
    logo=ROOT / "assets" / "logo" / "D55_LOGO_WHITE (2).png",
    background=ROOT / "assets" / "backgrounds" / "D55_TEAMS_BACKGROUND_No_LOGO.jpg",
    output_dir=ROOT / "outputs",
    org_name="D55",
)


def main():
    make_pdf = "--no-pdf" not in sys.argv
    sys.path.insert(0, str(ROOT))
    content = importlib.import_module("programme_doc_content")
    build(content.DOC, D55_AIDLC, make_pdf=make_pdf)


if __name__ == "__main__":
    main()
