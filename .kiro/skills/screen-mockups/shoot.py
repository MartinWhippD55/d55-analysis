#!/usr/bin/env python3
"""Screenshot HTML wireframes to PNGs, and (optionally) verify they rendered.

Generic, repo-agnostic. Give it a directory of *.html (or explicit files);
it renders each at a fixed viewport width and writes a full-page PNG next to
it (same stem). Keeping the width identical across screens is what makes a set
of mockups read as one family.

Usage:
    python shoot.py <dir-or-html...> [--width 1200] [--out DIR] [--check]

Examples:
    python shoot.py ./mockups
    python shoot.py ./mockups/01-list.html ./mockups/02-edit.html --width 1280
    python shoot.py ./mockups --check          # screenshot + sanity-check DOM

Setup (one time):
    pip install playwright
    python -m playwright install chromium
"""
import argparse
import glob
import sys
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit(
        "Playwright not installed. Run:\n"
        "  pip install playwright\n"
        "  python -m playwright install chromium"
    )


def collect(inputs):
    files = []
    for item in inputs:
        p = Path(item)
        if p.is_dir():
            files.extend(sorted(p.glob("*.html")))
        elif p.is_file():
            files.append(p)
        else:
            files.extend(Path(m) for m in sorted(glob.glob(item)))
    # de-dupe, preserve order
    seen, out = set(), []
    for f in files:
        r = f.resolve()
        if r not in seen:
            seen.add(r)
            out.append(f)
    return out


# DOM sanity check: font applied + no horizontal overflow + some content.
CHECK_JS = """
() => {
    const overflow = document.body.scrollWidth - window.innerWidth;
    const font = getComputedStyle(document.body).fontFamily;
    const imgs = Array.from(document.images);
    return {
        overflow,
        fontOk: /Architects Daughter|Comic Sans|cursive/i.test(font),
        elements: document.querySelectorAll('*').length,
        buttons: document.querySelectorAll('button, .btn, .btn-sm').length,
        brokenImages: imgs.filter(i => i.naturalWidth === 0).length,
        hasLabel: !!document.querySelector('.wireframe-label'),
    };
}
"""


def main():
    ap = argparse.ArgumentParser(description="Screenshot HTML wireframes to PNGs.")
    ap.add_argument("inputs", nargs="+", help="Directory, HTML files, or globs.")
    ap.add_argument("--width", type=int, default=1200, help="Viewport width (default 1200).")
    ap.add_argument("--out", help="Output directory (default: alongside each HTML).")
    ap.add_argument("--check", action="store_true", help="Also verify the DOM rendered sanely.")
    args = ap.parse_args()

    files = collect(args.inputs)
    if not files:
        sys.exit("No HTML files found for the given inputs.")

    out_dir = Path(args.out) if args.out else None
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)

    problems = 0
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": args.width, "height": 900})
        for html in files:
            png = (out_dir or html.parent) / (html.stem + ".png")
            page.goto(html.resolve().as_uri(), wait_until="networkidle")
            page.screenshot(path=str(png), full_page=True)
            line = f"  {html.name} -> {png.name}"
            if args.check:
                r = page.evaluate(CHECK_JS)
                issues = []
                if r["overflow"] > 1:
                    issues.append(f"h-overflow {r['overflow']}px")
                if not r["fontOk"]:
                    issues.append("sketch font not applied")
                if r["brokenImages"]:
                    issues.append(f"{r['brokenImages']} broken image(s)")
                if not r["hasLabel"]:
                    issues.append("missing .wireframe-label")
                if issues:
                    problems += 1
                    line += "  [!] " + "; ".join(issues)
                else:
                    line += f"  [ok] {r['elements']} els, {r['buttons']} buttons"
            print(line)
        browser.close()

    print(f"\nDone: {len(files)} screen(s).")
    if args.check and problems:
        sys.exit(f"{problems} screen(s) had issues.")


if __name__ == "__main__":
    main()
