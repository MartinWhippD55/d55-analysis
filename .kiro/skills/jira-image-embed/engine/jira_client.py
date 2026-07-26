"""
Thin, authenticated Jira Cloud REST client for the jira-image-embed skill.

This is the *only* part of the skill that touches the network. It exists because the
Atlassian MCP cannot write a raw-ADF description (it only accepts markdown), and inline
image embedding requires raw ADF. Everything here is deliberately minimal: load the
same credentials the Atlassian MCP uses, then do the handful of REST calls the embed
flow needs. All ADF construction lives in the pure ``adf`` module.

Credentials
-----------
Read from the same source of truth as the ``atlassian`` MCP server (see
``.kiro/settings/mcp.json``):

- ``JIRA_API_TOKEN`` (secret) from ``.kiro/settings/atlassian.env`` (git-ignored).
- ``JIRA_URL`` and ``JIRA_USERNAME`` from ``atlassian.env`` if present, otherwise from
  the ``atlassian`` server's ``env`` block in ``mcp.json``.
- Any of the three may be overridden by a real environment variable.

The token is only ever placed in the ``Authorization`` header; it is never logged or
returned.
"""
from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Optional

import requests

# jira_client.py -> engine -> jira-image-embed -> skills -> .kiro -> <workspace root>
_KIRO_DIR = Path(__file__).resolve().parents[3]
_SETTINGS_DIR = _KIRO_DIR / "settings"
ENV_FILE = _SETTINGS_DIR / "atlassian.env"
MCP_JSON = _SETTINGS_DIR / "mcp.json"

REQUIRED = ("JIRA_URL", "JIRA_USERNAME", "JIRA_API_TOKEN")


def _parse_env_file(path: Path) -> dict[str, str]:
    """Parse a dotenv-style ``KEY=VALUE`` file. Missing file -> empty dict."""
    out: dict[str, str] = {}
    if not path.exists():
        return out
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        value = value.strip().strip('"').strip("'")
        out[key.strip()] = value
    return out


def _mcp_atlassian_env(path: Path) -> dict[str, str]:
    """Pull the ``atlassian`` server's inline ``env`` block from mcp.json (URL/user)."""
    if not path.exists():
        return {}
    try:
        cfg = json.loads(path.read_text(encoding="utf-8"))
        return dict(cfg["mcpServers"]["atlassian"].get("env", {}))
    except (json.JSONDecodeError, KeyError, TypeError):
        return {}


def load_config() -> dict:
    """Resolve ``{base_url, email, token}`` from env file + mcp.json + os.environ.

    Precedence (high to low): real environment variables, ``atlassian.env``, then the
    ``mcp.json`` atlassian ``env`` block. Raises ``RuntimeError`` naming any missing
    required key — never echoing values.
    """
    merged: dict[str, str] = {}
    merged.update(_mcp_atlassian_env(MCP_JSON))  # lowest precedence
    merged.update(_parse_env_file(ENV_FILE))
    for key in REQUIRED:  # highest precedence: the live environment
        if os.environ.get(key):
            merged[key] = os.environ[key]

    missing = [k for k in REQUIRED if not merged.get(k)]
    if missing:
        raise RuntimeError(
            "Missing Jira credential(s): "
            + ", ".join(missing)
            + f". Expected in {ENV_FILE} or the atlassian env block of {MCP_JSON}."
        )
    return {
        "base_url": merged["JIRA_URL"].rstrip("/"),
        "email": merged["JIRA_USERNAME"],
        "token": merged["JIRA_API_TOKEN"],
    }


class JiraClient:
    """Minimal Jira Cloud REST v3 client (Basic auth: email + API token)."""

    def __init__(self, base_url: str, email: str, token: str):
        self.base_url = base_url.rstrip("/")
        creds = base64.b64encode(f"{email}:{token}".encode()).decode()
        self._auth_header = f"Basic {creds}"
        self._session = requests.Session()
        self._session.headers.update(
            {"Authorization": self._auth_header, "Accept": "application/json"}
        )

    @classmethod
    def from_config(cls) -> "JiraClient":
        cfg = load_config()
        return cls(cfg["base_url"], cfg["email"], cfg["token"])

    # -- reads -------------------------------------------------------------- #
    def get_description_adf(self, issue_key: str):
        """Return the issue's description as an ADF dict (or None if empty)."""
        r = self._session.get(
            f"{self.base_url}/rest/api/3/issue/{issue_key}",
            params={"fields": "description"},
            timeout=30,
        )
        r.raise_for_status()
        return r.json().get("fields", {}).get("description")

    def list_attachments(self, issue_key: str) -> list[dict]:
        """Return the issue's attachments as ``[{filename, id, content}, ...]``."""
        r = self._session.get(
            f"{self.base_url}/rest/api/3/issue/{issue_key}",
            params={"fields": "attachment"},
            timeout=30,
        )
        r.raise_for_status()
        items = r.json().get("fields", {}).get("attachment") or []
        return [
            {"filename": a.get("filename"), "id": a.get("id"), "content": a.get("content")}
            for a in items
        ]

    def rendered_description_html(self, issue_key: str) -> str:
        """Return the server-rendered HTML of the description (for verification)."""
        r = self._session.get(
            f"{self.base_url}/rest/api/3/issue/{issue_key}",
            params={"fields": "description", "expand": "renderedFields"},
            timeout=30,
        )
        r.raise_for_status()
        return (r.json().get("renderedFields", {}) or {}).get("description") or ""

    # -- writes ------------------------------------------------------------- #
    def upload_attachment(self, issue_key: str, file_path: str) -> dict:
        """Upload a file as an attachment; return ``{filename, id, content}``."""
        path = Path(file_path)
        with path.open("rb") as fh:
            r = self._session.post(
                f"{self.base_url}/rest/api/3/issue/{issue_key}/attachments",
                headers={"X-Atlassian-Token": "no-check"},
                files={"file": (path.name, fh)},
                timeout=120,
            )
        r.raise_for_status()
        a = r.json()[0]
        return {"filename": a.get("filename"), "id": a.get("id"), "content": a.get("content")}

    def set_description_adf(self, issue_key: str, doc: dict) -> None:
        """PUT the description as raw ADF, preserving everything already in ``doc``."""
        r = self._session.put(
            f"{self.base_url}/rest/api/3/issue/{issue_key}",
            headers={"Content-Type": "application/json"},
            data=json.dumps({"fields": {"description": doc}}),
            timeout=60,
        )
        r.raise_for_status()

    def attachment_content_url(self, attachment_id: str) -> str:
        """The stable content URL used as the external media node's ``url``."""
        return f"{self.base_url}/rest/api/3/attachment/content/{attachment_id}"
