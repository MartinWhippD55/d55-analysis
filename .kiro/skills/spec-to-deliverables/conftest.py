"""Ensure the bundle root is importable so tests can `import engine.*`.

Running `python -m pytest` from the bundle root already puts the root on
sys.path; this makes it robust regardless of how pytest is invoked.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
