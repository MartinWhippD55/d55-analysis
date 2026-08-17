"""US-xx -> live Jira key rewrite, driven by ``jira-tree/_placeholders.md``.

When jira-push creates the issues it writes a ``_placeholders.md`` whose front-matter
``key_map`` correlates each tree key (``US-01``, ``US-04-2``, the epic parent slug) to
its real Jira key (``SQP-5046`` …). Diagram labels and the enrichment prose are
authored with tree keys; before pushing to Jira we rewrite them to the live keys so
they render as clickable references — matching what jira-push does to the bodies.

Learnings baked in (see SKILL.md gotchas):
- Only rewrite **whole** ``US-0x`` / ``US-0x-n`` tokens.
- **Never** rewrite the ``US-xx`` inside an identity label (``s2s-<parent>-US-01``) or
  any other dashed identifier: negative lookbehind on a preceding hyphen / word char.
- **Never** rewrite a token that is actually a diagram filename (``US-01.png`` /
  ``US-01.mmd``): negative lookahead on the extension.
- Idempotent: a already-substituted ``SQP-1234`` never matches the ``US-`` shape.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

# Match a whole US-xx / US-xx-n token that is NOT:
#  - a suffix of a longer dashed identifier / identity label (lookbehind on [-\w]),
#  - a diagram filename US-xx.png / US-xx.mmd (lookahead on the extension),
#  - glued to a trailing word char or hyphen.
_TOKEN = re.compile(r"(?<![-\w])US-\d{2}(?:-\d+)?(?!\.(?:png|mmd)\b)(?![\w-])")
_BASE = "https://d55ltd.atlassian.net/browse"


def load_key_map(placeholders_path: str | Path) -> dict[str, str]:
    """Return the ``{tree_key -> jira_key}`` map from a ``_placeholders.md`` file.

    The map lives in the YAML front-matter under ``key_map``. Missing file or map
    yields an empty dict (callers then simply do no rewriting).
    """
    text = Path(placeholders_path).read_text(encoding="utf-8")
    fm = _front_matter(text)
    return dict((fm or {}).get("key_map", {}) or {})


def _front_matter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    return yaml.safe_load(text[3:end]) or {}


def remap(text: str, key_map: dict[str, str], base_url: str = _BASE) -> str:
    """Rewrite whole ``US-xx`` tokens in ``text`` to ``[SQP-nnnn](url)`` markdown links.

    Tokens absent from ``key_map`` (e.g. a sub-task key when only story keys are
    supplied) are left untouched. Identity labels and diagram filenames are protected
    by the token pattern.
    """
    def _sub(m: re.Match) -> str:
        tok = m.group(0)
        key = key_map.get(tok)
        if not key:
            return tok
        return f"[{key}]({base_url}/{key})"

    return _TOKEN.sub(_sub, text)
