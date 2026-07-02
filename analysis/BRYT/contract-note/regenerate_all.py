"""
Regenerate all contract note deliverables from their sources.

Run this after editing estimate figures in the spreadsheet (Task Detail tab)
or updating any content module - it rebuilds every generated artifact so the
figures and content stay in sync everywhere.

Steps, in order:
  1. Estimate figures check  - reports the current per-estimate figures
  2. Standalone HTML presentation
  3. Estimate walkthroughs (1-5) + data model  -> HTML + PDF
  4. Self-contained API reference HTML

Not included (by request): the .pptx presentation. Regenerate it separately
with `python analysis/BRYT/contract-note/generate_presentation.py` if needed.

Usage:
    python analysis/BRYT/contract-note/regenerate_all.py
    python analysis/BRYT/contract-note/regenerate_all.py --no-pdf   # skip PDF rendering
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]  # workspace root (analysis/BRYT/contract-note -> repo)
WALK = ROOT / "walkthroughs" / "build_walkthrough.py"

WALKTHROUGHS = [
    "estimate_01",
    "estimate_02",
    "estimate_03",
    "estimate_04",
    "estimate_05",
    "data_model",
]

PY = sys.executable
NO_PDF = "--no-pdf" in sys.argv


def run(label: str, args: list[str]) -> bool:
    print(f"\n=== {label} ===")
    result = subprocess.run([PY, *args], cwd=str(REPO))
    ok = result.returncode == 0
    print(f"--- {label}: {'OK' if ok else 'FAILED (exit %d)' % result.returncode} ---")
    return ok


def rel(p: Path) -> str:
    return str(p.relative_to(REPO))


def main():
    results: list[tuple[str, bool]] = []

    # 1. Figures snapshot (also validates the spreadsheet is readable)
    results.append(("figures", run("Estimate figures", [rel(ROOT / "figures.py")])))

    # 2. Standalone HTML presentation
    results.append(("presentation-html",
                    run("Standalone HTML presentation", [rel(ROOT / "build_standalone_html.py")])))

    # 3. Walkthroughs + data model
    for module in WALKTHROUGHS:
        args = [rel(WALK), module]
        if NO_PDF:
            args.append("--no-pdf")
        results.append((module, run(f"Walkthrough: {module}", args)))

    # 4. API reference HTML
    results.append(("api-html",
                    run("API reference HTML", [rel(ROOT / "api" / "build_html.py")])))

    # Summary
    print("\n" + "=" * 60)
    print("REGENERATION SUMMARY")
    print("=" * 60)
    for name, ok in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    failed = [n for n, ok in results if not ok]
    if failed:
        print(f"\n{len(failed)} step(s) failed: {', '.join(failed)}")
        sys.exit(1)
    print("\nAll deliverables regenerated successfully.")


if __name__ == "__main__":
    main()
