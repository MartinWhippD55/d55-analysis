---
name: mcp-setup
description: Bring a developer's Kiro MCP setup in line with the D55 reference — install prerequisites, add any missing MCP servers non-destructively, wire per-user secrets, and verify each connects.
inclusion: manual
---

# MCP Setup

Reconcile a developer's Kiro **MCP** configuration with the D55 reference server
set: detect which servers they're missing, add **only those** (never clobbering
their existing servers or `autoApprove` customisations), localise the
machine/user/secret bits, and verify each server connects.

Use it to onboard a new developer, or to extend an existing setup with servers
they don't yet have. It is **additive and idempotent** — re-running only fills gaps.

This is a **hybrid skill**: a deterministic **engine** does the config maths
(load, diff, placeholder-fill, non-destructive merge) and the **agent** drives
the interactive parts only it can do — installing prerequisites, prompting for
per-user values and secrets, and reconnecting servers.

## Self-sufficient bundle

```
.kiro/skills/mcp-setup/
  SKILL.md                 this file
  requirements.txt         hypothesis, pytest (engine is stdlib-only at runtime)
  pytest.ini
  reference/
    mcp.reference.json     the portable D55 server set (placeholders for machine/user/secret)
  engine/
    config.py              load / diff / substitute / merge / find_runtime
    reconcile.py           dry-run plan (CLI: python -m engine.reconcile)
  tests/
    test_config.py         load, diff, merge (non-destructive), substitution (incl. property-based)
```

Run the engine from the bundle root (`python -m pytest`, or `import engine.config`).

## The reference server set

`reference/mcp.reference.json` is the source of truth for *which* servers a D55
dev should have and *how* to launch them portably. Today:

| Server | Runtime | Launcher | Notes |
|--------|---------|----------|-------|
| `playwright` | node | `npx` | Headless browser + screenshots (deliverables verification, screen-mockups). |
| `excalidraw` | node | `npx` | Excalidraw diagram rendering. |
| `atlassian` | python | `uvx` | Jira via `mcp-atlassian`; needs a per-user token + email. |

Each entry carries the mcp.json `spec` plus metadata: `runtime`, `{{placeholders}}`
for per-machine/user fields, `defaults` (e.g. the shared `JIRA_URL`), `secrets`
(which keys live in the git-ignored env-file), and a `verify_tool`. **Machine
paths, emails and tokens are never baked into the reference** — they're resolved
per developer at setup time.

To add a server to the D55 baseline for everyone, add it to this reference file
(with placeholders for anything machine/user/secret-specific) and re-run the skill.

## Config locations & precedence

Kiro merges MCP configs with precedence **user < workspace** (workspace wins):

- **Workspace**: `<workspace>/.kiro/settings/mcp.json`
- **User (global)**: `~/.kiro/settings/mcp.json`

A server the dev already has at **either** level is *not* missing. New servers are
added to the **workspace** config by default (project-scoped); offer the user
config only if they want the server available across all their workspaces.

## Steps

### 1. Verify the engine, then produce a dry-run plan

```
python -m pytest                       # from the bundle root
python -m engine.reconcile --workspace <target-workspace>
```

The plan lists, per reference server: **present** vs **MISSING → add**, its
runtime, whether the launcher (`npx`/`uvx`) is **on PATH**, and — for missing
servers — the placeholder values and secrets still needed. Nothing is written.
Show this plan to the developer before changing anything.

### 2. Ensure prerequisites (per runtime of the missing servers)

Only what the missing servers need:

- **node servers** (`playwright`, `excalidraw`) need **Node.js** (ships `npx`).
  Check `node --version` and `npx --version`. If absent, install Node.js LTS
  (nvm, the official installer, or the platform package manager). `npx` fetches
  `@latest` on first launch — no separate install per server.
- **python-uvx servers** (`atlassian`) need **uv** (ships `uvx`). Check
  `uvx --version`. If absent, install uv (see https://docs.astral.sh/uv/getting-started/installation/,
  e.g. `pip install uv` or the platform installer). There is no `uvx install` —
  `uvx mcp-atlassian` downloads and runs on demand.

If the plan shows a launcher **not on PATH** but the runtime *is* installed
(common on Windows for `uvx`), resolve its absolute path (`where uvx` /
`which uvx`) and use that as the server `command` in step 4 — this mirrors how an
absolute launcher path ends up in a working config.

### 3. Gather per-user values and secrets (for each missing server)

From the plan's `needs values` / `needs secrets`:

- **Placeholders** (e.g. `atlassian`): `env_file` (default
  `<workspace>/.kiro/settings/atlassian.env`), `JIRA_USERNAME` (their D55 email).
  `JIRA_URL` has a team default (`https://d55ltd.atlassian.net`) — confirm or override.
- **Secrets** go **only** in the env-file, never in `mcp.json`. For `atlassian`,
  create `<env_file>` containing `JIRA_API_TOKEN=<token>` (a token from
  https://id.atlassian.com/manage-profile/security/api-tokens). The repo's
  `.gitignore` already ignores `.kiro/settings/*.env`; confirm the env-file is
  ignored before writing. **Never print or commit the token.**

### 4. Build specs and merge non-destructively

Use the engine to fill placeholders and add only missing servers, preserving
everything the developer already has:

```python
import sys; sys.path.insert(0, ".kiro/skills/mcp-setup")
from engine.config import (
    load_config, save_config, load_reference, missing_servers,
    build_server_spec, unresolved_placeholders, merge_servers,
    default_workspace_config_path, default_user_config_path,
)

ref = load_reference(".kiro/skills/mcp-setup/reference/mcp.reference.json")
ws_path = default_workspace_config_path("<workspace>")
ws = load_config(ws_path)
user = load_config(default_user_config_path())

new_specs = {}
for name in missing_servers(ref, ws, user):
    entry = ref["servers"][name]
    values = {   # gathered in step 3; include "command" if you resolved an absolute launcher path
        # "env_file": "<workspace>/.kiro/settings/atlassian.env",
        # "JIRA_USERNAME": "jane.doe@d55.co.uk",
        # "command": r"C:\path\to\uvx.exe",   # only if uvx not on PATH
    }
    spec = build_server_spec(entry, values)
    remaining = unresolved_placeholders(spec)
    assert not remaining, f"{name} still needs: {remaining}"   # don't write a half-filled spec
    new_specs[name] = spec

merged, added, skipped = merge_servers(ws, new_specs)   # non-destructive; existing servers untouched
save_config(ws_path, merged)
print("added:", added, "already present:", skipped)
```

`merge_servers` never overwrites an existing server (or its `autoApprove`) unless
you pass `overwrite=True`. `save_config` writes stable 2-space JSON.

### 5. Reconnect and verify

- In Kiro, reconnect the affected servers from the **MCP Server** view (or search
  the command palette for **MCP**) — no full restart needed. Servers also
  reconnect on config change.
- Verify each newly added server with its **read-only** `verify_tool` from the
  reference (e.g. `atlassian` → `jira_get_user_profile <email>`; `playwright` →
  `browser_navigate`; `excalidraw` → `create-excalidraw-diagram`). A clean read
  confirms the launcher, config and (for atlassian) the token all work.
- If a server fails: check the launcher path, the env-file path/contents (token
  present, not empty), and that the runtime is installed. Re-run the dry-run plan
  to reconfirm state.

## Verify

- `python -m pytest` in the bundle (engine correctness — load, diff, merge
  idempotency/non-destructiveness, substitution, no-secret-in-spec).
- After applying, re-run `python -m engine.reconcile` and confirm **0 to add**
  (idempotency), then confirm each server answers a read-only call in Kiro.

## Hard rules

- **Additive & non-destructive.** Only add missing servers; never remove or
  overwrite a developer's existing servers or `autoApprove` lists (no `overwrite`
  unless the user explicitly asks).
- **Idempotent.** Re-running adds nothing when already in sync.
- **Secrets only in the env-file.** Tokens live in the git-ignored
  `.kiro/settings/*.env`, never in `mcp.json`, never printed, never committed.
- **No cross-machine paths.** Resolve launchers on the target's PATH (or its own
  absolute path); never copy another machine's absolute `uvx`/`npx` path, email,
  or token.
- **Confirm before writing.** Show the plan and get a go-ahead; config writes and
  reconnects are not auto-approved.
