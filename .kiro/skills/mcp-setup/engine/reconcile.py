"""Dry-run reconciliation plan: what would be added to bring a dev inline.

CLI:
    python -m engine.reconcile [--workspace <dir>] [--reference <path>]

Prints, per reference server, whether it is already present (in the workspace or
user config) or missing, plus the runtime and whether its launcher is on PATH and
what placeholders/secrets a missing server still needs. Read-only — writes nothing.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from .config import (
    load_config, load_reference, missing_servers, server_names,
    find_runtime, build_server_spec, unresolved_placeholders,
    default_workspace_config_path, default_user_config_path,
)

_DEFAULT_REFERENCE = Path(__file__).resolve().parent.parent / "reference" / "mcp.reference.json"


def build_plan(reference: dict, workspace_cfg: dict, user_cfg: dict) -> list[dict]:
    """Per-server plan entries (pure): action, runtime, launcher, needs."""
    have = server_names(workspace_cfg) | server_names(user_cfg)
    plan = []
    for name, entry in reference["servers"].items():
        runtime = entry.get("runtime", "")
        launcher = find_runtime(runtime)
        spec = build_server_spec(entry, {})   # no values -> placeholders remain
        secrets = entry.get("secrets", {}).get("env_file_keys", [])
        plan.append({
            "name": name,
            "action": "present" if name in have else "add",
            "runtime": runtime,
            "launcher_on_path": bool(launcher),
            "launcher_path": launcher,
            "needs_placeholders": unresolved_placeholders(spec),
            "needs_secrets": secrets,
            "notes": entry.get("notes", ""),
        })
    return plan


def format_plan(plan: list[dict]) -> str:
    lines = ["MCP reconciliation plan", "=" * 40]
    for e in plan:
        mark = "already present" if e["action"] == "present" else "MISSING -> add"
        lines.append(f"- {e['name']}: {mark}")
        lines.append(f"    runtime: {e['runtime']}  launcher on PATH: {'yes' if e['launcher_on_path'] else 'NO'}")
        if e["action"] == "add":
            if e["needs_placeholders"]:
                lines.append(f"    needs values: {', '.join(e['needs_placeholders'])}")
            if e["needs_secrets"]:
                lines.append(f"    needs secrets (env-file): {', '.join(e['needs_secrets'])}")
        if not e["launcher_on_path"]:
            lines.append(f"    ! install the {e['runtime']} runtime first (launcher not found)")
    missing = [e["name"] for e in plan if e["action"] == "add"]
    lines.append("")
    lines.append(f"{len(missing)} to add: {', '.join(missing) if missing else '(none — already in sync)'}")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Dry-run MCP reconciliation plan (read-only).")
    ap.add_argument("--workspace", default=".", help="workspace root (default: cwd)")
    ap.add_argument("--reference", default=str(_DEFAULT_REFERENCE), help="reference config path")
    args = ap.parse_args(argv)

    reference = load_reference(args.reference)
    workspace_cfg = load_config(default_workspace_config_path(args.workspace))
    user_cfg = load_config(default_user_config_path())
    plan = build_plan(reference, workspace_cfg, user_cfg)
    print(format_plan(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
