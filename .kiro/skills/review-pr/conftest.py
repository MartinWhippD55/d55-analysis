"""Ensure the bundle root is importable so tests can `import engine.*`."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
