"""
Regenerate all Report Builder POC deliverables from their sources.

Run this after editing estimate figures in the POC spreadsheet (Task Detail tab)
or the POC tasks.md - it rebuilds every generated artifact so figures and content
stay in sync everywhere.

Stripped clone of `../../report-builder/deliverables/regenerate_all.py`. The POC
set is intentionally lean: the estimate spreadsheet, the figures check, the
summary presentation, and the technical walkthrough. The full feature's
data-model PDF and OpenAPI reference are NOT part of the POC deliverables.

Steps, in order:
  1. Estimate spreadsheet   - regenerated from the POC spec tasks.md
  2. Estimate figures check - reports the current per-phase figures
  3. Summary presentation   - standalone auto-scaling HTML deck
  4. Technical walkthrough  - branded HTML + PDF

Usage:
    python analysis/BRYT/report-builder-poc/deliverables/regenerate_all.py
    python analysis/BRYT/report-builder-poc/deliverables/regenerate_all.py --no-pdf        # skip PDF rendering
    python analysis/BRYT/report-builder-poc/deliverables/regenerate_all.py --no-estimates  # keep manual spreadsheet edits
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent          # deliverables/
REPO = ROOT.parents[4]                            # workspace root
WALK = ROOT / "walkthroughs" / "build_walkthrough.py"

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

    # 4. Technical walkthrough (HTML + PDF)
    walk_args = [rel(WALK), "report_builder_poc"]
    if NO_PDF:
        walk_args.append("--no-pdf")
    results.append(("walkthrough", run("Technical walkthrough", walk_args)))

    print("\n" + "=" * 60)
    print("POC REGENERATION SUMMARY")
    print("=" * 60)
    for name, ok in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    failed = [n for n, ok in results if not ok]
    if failed:
        print(f"\n{len(failed)} step(s) failed: {', '.join(failed)}")
        sys.exit(1)
    print("\nAll POC deliverables regenerated successfully.")


if __name__ == "__main__":
    main()
