"""Pytest configuration for the New Programme bundle tests.

Puts the bundle root on ``sys.path`` so tests can ``import engine.*`` regardless
of where pytest is invoked from. The bundle directory name is dashed
(``new-programme``) and thus not importable as a package, so we import the
``engine`` package directly by anchoring on the bundle root.
"""
from __future__ import annotations

import sys
from pathlib import Path

BUNDLE_ROOT = Path(__file__).resolve().parent.parent
if str(BUNDLE_ROOT) not in sys.path:
    sys.path.insert(0, str(BUNDLE_ROOT))
