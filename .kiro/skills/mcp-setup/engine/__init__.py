"""mcp-setup engine.

Deterministic helpers to reconcile a developer's Kiro MCP configuration with a
portable reference server set: load configs (tolerant of comments), diff, fill
per-machine/user placeholders, and merge missing servers non-destructively.

No network calls and no server installs — the agent drives prerequisites,
secrets, and reconnection; this module only does the config maths.
"""

from .config import (
    load_config,
    save_config,
    load_reference,
    server_names,
    missing_servers,
    diff,
    substitute,
    build_server_spec,
    unresolved_placeholders,
    merge_servers,
    find_runtime,
    default_workspace_config_path,
    default_user_config_path,
)

__all__ = [
    "load_config",
    "save_config",
    "load_reference",
    "server_names",
    "missing_servers",
    "diff",
    "substitute",
    "build_server_spec",
    "unresolved_placeholders",
    "merge_servers",
    "find_runtime",
    "default_workspace_config_path",
    "default_user_config_path",
]
