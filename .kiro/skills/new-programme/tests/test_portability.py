"""Bundle portability check (Task 17, Property 13).

Copies the whole bundle to a temp dir *outside* the repo and runs it end-to-end
on the bundled example — in a fresh subprocess whose only import path is the
copied bundle and whose cwd is the temp dir. Asserts outputs are produced and no
path resolves into ``analysis/``, the repo root, or an absolute repo path.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BUNDLE = Path(__file__).resolve().parent.parent          # .../.kiro/skills/new-programme
REPO_ROOT = BUNDLE.parents[2]                            # .../d55-analysis

_IGNORE = shutil.ignore_patterns("__pycache__", ".pytest_cache", ".hypothesis", "output", "*.pyc")


def test_bundle_runs_end_to_end_outside_the_repo(tmp_path):
    # A workspace entirely outside the repo tree.
    work = Path(tempfile.mkdtemp(prefix="np-portability-"))
    try:
        copied = work / "new-programme"
        shutil.copytree(BUNDLE, copied, ignore=_IGNORE)
        out_root = work / "out"

        # Fresh interpreter: only the copied bundle on sys.path, cwd in the temp dir.
        # Any reach-back into analysis/ (relative) or the repo would fail here.
        script = (
            "import sys; sys.path.insert(0, r'{copied}')\n"
            "from engine.build_example import build_example\n"
            "layout = build_example(r'{out}', make_pdf=False)\n"
            "print('ROOT=' + str(layout.root))\n"
        ).format(copied=copied, out=out_root)

        env = dict(os.environ)
        env.pop("PYTHONPATH", None)                       # don't leak the repo onto the path
        proc = subprocess.run(
            [sys.executable, "-c", script],
            cwd=work, env=env, capture_output=True, text=True,
        )
        assert proc.returncode == 0, f"run failed:\nSTDOUT:{proc.stdout}\nSTDERR:{proc.stderr}"

        programme = out_root / "example"
        # Outputs produced.
        assert (programme / "programme.yaml").exists()
        assert (programme / "client" / "workshop.html").exists()
        assert (programme / "client" / "elevator-pitch.html").exists()
        assert (programme / "client" / "assessment-questionnaire.xlsx").exists()
        assert any((programme / "internal").glob("*.xlsx"))
        assert any((programme / "modules" / "module-1-leadership-and-investment-case" / "assets").glob("*.html"))

        # Property 13: no produced text output leaks the repo root or an analysis/ path.
        repo_str = str(REPO_ROOT)
        offenders = []
        for p in programme.rglob("*"):
            if p.suffix.lower() in {".html", ".md", ".yaml", ".yml"} and p.is_file():
                text = p.read_text(encoding="utf-8", errors="ignore")
                if repo_str in text or "/analysis/" in text or "\\analysis\\" in text:
                    offenders.append(p.name)
        assert not offenders, f"outputs leaked a repo/analysis path: {offenders}"

        # And the outputs live entirely under the external work dir (no absolute repo paths).
        assert str(work) in str(programme.resolve())
    finally:
        shutil.rmtree(work, ignore_errors=True)
