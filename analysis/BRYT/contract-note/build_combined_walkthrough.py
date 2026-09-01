"""
Combine the outstanding-estimate walkthrough PDFs (Estimates 2-5) into a single
PDF for easy sharing.

Merges the per-estimate walkthrough PDFs that already live in outputs/ (produced
by walkthroughs/build_walkthrough.py) in order, adding a top-level bookmark per
estimate so the combined document is navigable.

This does not regenerate the source walkthroughs - run regenerate_all.py first
if any of them are stale.

Usage:
    python analysis/BRYT/contract-note/build_combined_walkthrough.py
"""
from pathlib import Path

from pypdf import PdfWriter

ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT / "outputs"

# Ordered (source filename, bookmark label) for the outstanding estimates.
PARTS = [
    ("estimate-2-walkthrough.pdf", "Estimate 2 - DocuSign Integration"),
    ("estimate-3-walkthrough.pdf", "Estimate 3 - Training & Data Sources"),
    ("estimate-4-walkthrough.pdf", "Estimate 4 - Bespoke Contracts"),
    ("estimate-5-walkthrough.pdf", "Estimate 5 - System Comparison"),
]

OUTPUT_NAME = "estimates-2-5-combined-walkthrough.pdf"


def main():
    missing = [name for name, _ in PARTS if not (OUTPUTS / name).exists()]
    if missing:
        print("Missing source walkthrough PDF(s): " + ", ".join(missing))
        print("Run: python analysis/BRYT/contract-note/regenerate_all.py")
        raise SystemExit(1)

    writer = PdfWriter()
    for name, label in PARTS:
        src = OUTPUTS / name
        writer.append(str(src), outline_item=label)
        print(f"  + {name}  ->  bookmark '{label}'")

    out_path = OUTPUTS / OUTPUT_NAME
    with out_path.open("wb") as fh:
        writer.write(fh)
    writer.close()

    size_kb = out_path.stat().st_size / 1024
    print(f"\nCombined PDF written: {out_path}  ({size_kb:.0f} KB)")


if __name__ == "__main__":
    main()
