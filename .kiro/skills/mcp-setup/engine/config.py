"""MCP config load / diff / merge / placeholder substitution (pure + small IO).

The functions that only transform data (``diff``, ``substitute``,
``build_server_spec``, ``merge_servers``, ``missing_servers``,
``unresolved_placeholders``) are pure and fully tested. ``load_config`` /
``save_config`` do file IO; ``find_runtime`` probes PATH.
"""
from __future__ import annotations

import copy
import json
import re
import shutil
from pathlib import Path
from typing import Optional

_PLACEHOLDER_RE = re.compile(r"\{\{(\w+)\}\}")
_LINE_COMMENT_RE = re.compile(r"(?m)^\s*//.*$")
_BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)

# Runtime -> the executable that must be on PATH to launch such a server.
_RUNTIME_COMMAND = {
    "node": "npx",
    "python-uvx": "uvx",
}


def default_workspace_config_path(workspace) -> Path:
    return Path(workspace) / ".kiro" / "settings" / "mcp.json"


def default_user_config_path() -> Path:
    return Path.home() / ".kiro" / "settings" / "mcp.json"


def _strip_comments(text: str) -> str:
    """Best-effort strip of // and /* */ comments so JSONC configs still parse."""
    text = _BLOCK_COMMENT_RE.sub("", text)
    text = _LINE_COMMENT_RE.sub("", text)
    return text


def load_config(path) -> dict:
    """Load an mcp.json. Returns ``{"mcpServers": {}}`` if the file is absent/empty."""
    p = Path(path)
    if not p.exists():
        return {"mcpServers": {}}
    raw = p.read_text(encoding="utf-8").strip()
    if not raw:
        return {"mcpServers": {}}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = json.loads(_strip_comments(raw))
    if not isinstance(data, dict):
        raise ValueError(f"{p} is not a JSON object")
    data.setdefault("mcpServers", {})
    return data


def save_config(path, config: dict) -> None:
    """Write an mcp.json with stable 2-space formatting and a trailing newline."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")


def load_reference(path) -> dict:
    data = json.loads(_strip_comments(Path(path).read_text(encoding="utf-8")))
    if "servers" not in data or not isinstance(data["servers"], dict):
        raise ValueError("reference config must have a 'servers' object")
    return data


def server_names(config: dict) -> set:
    return set((config or {}).get("mcpServers", {}).keys())


def missing_servers(reference: dict, *configs: dict) -> list[str]:
    """Reference server names absent from *every* provided config (workspace + user).

    Order follows the reference's declaration order for stable output.
    """
    have = set()
    for cfg in configs:
        have |= server_names(cfg)
    return [name for name in reference["servers"] if name not in have]


def diff(reference: dict, target: dict) -> dict:
    """Compare a single target config to the reference."""
    ref_names = list(reference["servers"].keys())
    have = server_names(target)
    return {
        "missing": [n for n in ref_names if n not in have],
        "present": [n for n in ref_names if n in have],
        "extra": sorted(have - set(ref_names)),
    }


def substitute(obj, values: dict):
    """Recursively replace ``{{key}}`` tokens in strings using ``values``.

    Unknown tokens are left intact so ``unresolved_placeholders`` can report them.
    """
    if isinstance(obj, str):
        def repl(m):
            key = m.group(1)
            return str(values[key]) if key in values else m.group(0)
        return _PLACEHOLDER_RE.sub(repl, obj)
    if isinstance(obj, list):
        return [substitute(v, values) for v in obj]
    if isinstance(obj, dict):
        return {k: substitute(v, values) for k, v in obj.items()}
    return obj


def build_server_spec(reference_entry: dict, values: Optional[dict] = None) -> dict:
    """Return the concrete mcp.json spec for a reference server, placeholders filled.

    ``values`` may include a special ``command`` key to override the resolved
    launcher path (e.g. an absolute uvx path); otherwise the reference command
    (``npx`` / ``uvx``) is kept.
    """
    values = dict(values or {})
    # Fold in reference defaults (e.g. JIRA_URL) without overriding explicit values.
    for k, v in (reference_entry.get("defaults") or {}).items():
        values.setdefault(k, v)
    spec = substitute(copy.deepcopy(reference_entry["spec"]), values)
    if values.get("command"):
        spec["command"] = values["command"]
    return spec


def unresolved_placeholders(obj) -> list[str]:
    """Return the sorted unique ``{{key}}`` names still present anywhere in obj."""
    found = set()

    def walk(o):
        if isinstance(o, str):
            found.update(_PLACEHOLDER_RE.findall(o))
        elif isinstance(o, list):
            for v in o:
                walk(v)
        elif isinstance(o, dict):
            for v in o.values():
                walk(v)

    walk(obj)
    return sorted(found)


def merge_servers(target: dict, new_servers: dict, overwrite: bool = False):
    """Non-destructively add servers to a config.

    Returns ``(merged_config, added, skipped)``. Existing servers are preserved
    (and their autoApprove/customisations untouched) unless ``overwrite=True``.
    The input ``target`` is not mutated.
    """
    merged = copy.deepcopy(target) if target else {"mcpServers": {}}
    merged.setdefault("mcpServers", {})
    added, skipped = [], []
    for name, spec in new_servers.items():
        if name in merged["mcpServers"] and not overwrite:
            skipped.append(name)
            continue
        merged["mcpServers"][name] = copy.deepcopy(spec)
        added.append(name)
    return merged, added, skipped


def find_runtime(runtime: str) -> Optional[str]:
    """Resolve the launcher executable for a runtime on PATH, or None if missing."""
    cmd = _RUNTIME_COMMAND.get(runtime)
    if not cmd:
        return None
    return shutil.which(cmd)
