"""
Regenerate all Report Builder deliverables from their sources.

Run this after editing estimate figures in the spreadsheet (Task Detail tab),
the OpenAPI YAML, or any walkthrough content module - it rebuilds every
generated artifact so figures and content stay in sync everywhere.

Steps, in order:
  1. Estimate spreadsheet   - regenerated from the spec tasks.md
  2. Estimate figures check - reports the current per-phase figures
  3. Summary presentation   - standalone auto-scaling HTML deck
  4. Walkthrough + data model -> HTML + PDF
  5. Self-contained API reference HTML

Usage:
    python analysis/BRYT/report-builder/deliverables/regenerate_all.py
    python analysis/BRYT/report-builder/deliverables/regenerate_all.py --no-pdf
    python analysis/BRYT/report-builder/deliverables/regenerate_all.py --no-estimates  # keep manual spreadsheet edits
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent          # deliverables/
REPO = ROOT.parents[3]                           # workspace root
WALK = ROOT / "walkthroughs" / "build_walkthrough.py"

WALKTHROUGHS = ["report_builder", "report_builder_no_estimates", "data_model"]

PY = sys.executable
NO_PDF = "--no-pdf" in sys.argv
NO_ESTIMATES = "--no-estimates" in sys.argv


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

    # 1. Regenerate the estimate spreadsheet from tasks.md (unless preserving edits)
    if not NO_ESTIMATES:
        results.append(("estimates-spreadsheet",
                        run("Estimate spreadsheet", [rel(ROOT / "generate_estimates.py")])))

    # 2. Figures snapshot (validates the spreadsheet is readable)
    results.append(("figures", run("Estimate figures", [rel(ROOT / "figures.py")])))

    # 3. Summary presentation
    results.append(("presentation-html",
                    run("Summary presentation", [rel(ROOT / "build_standalone_html.py")])))

    # 4. Walkthroughs + data model
    for module in WALKTHROUGHS:
        args = [rel(WALK), module]
        if NO_PDF:
            args.append("--no-pdf")
        results.append((module, run(f"Walkthrough: {module}", args)))

    # 5. API reference HTML
    results.append(("api-html",
                    run("API reference HTML", [rel(ROOT / "api" / "build_html.py")])))

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
