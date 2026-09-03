"""Tests for the MCP config load / diff / merge / substitution engine."""
import json
from pathlib import Path

import pytest
from hypothesis import given, strategies as st

from engine.config import (
    load_config, save_config, load_reference, missing_servers, diff, substitute,
    build_server_spec, unresolved_placeholders, merge_servers, find_runtime,
)

REFERENCE = Path(__file__).resolve().parent.parent / "reference" / "mcp.reference.json"


# --- load / save ----------------------------------------------------------

def test_load_missing_returns_empty_skeleton(tmp_path):
    cfg = load_config(tmp_path / "nope.json")
    assert cfg == {"mcpServers": {}}


def test_load_strips_comments(tmp_path):
    p = tmp_path / "mcp.json"
    p.write_text('{\n  // a comment\n  "mcpServers": {"a": {"command": "npx"}}\n}', encoding="utf-8")
    cfg = load_config(p)
    assert "a" in cfg["mcpServers"]


def test_save_round_trip(tmp_path):
    p = tmp_path / "sub" / "mcp.json"
    save_config(p, {"mcpServers": {"x": {"command": "npx"}}})
    assert load_config(p)["mcpServers"]["x"]["command"] == "npx"


# --- diff / missing -------------------------------------------------------

def _ref():
    return {"servers": {"a": {"spec": {}}, "b": {"spec": {}}, "c": {"spec": {}}}}


def test_diff_partitions_present_missing_extra():
    target = {"mcpServers": {"a": {}, "z": {}}}
    d = diff(_ref(), target)
    assert d["present"] == ["a"]
    assert d["missing"] == ["b", "c"]
    assert d["extra"] == ["z"]


def test_missing_servers_across_workspace_and_user():
    ws = {"mcpServers": {"a": {}}}
    user = {"mcpServers": {"b": {}}}
    # a in workspace, b in user -> only c missing from both
    assert missing_servers(_ref(), ws, user) == ["c"]


def test_missing_preserves_reference_order():
    assert missing_servers(_ref(), {"mcpServers": {}}) == ["a", "b", "c"]


# --- substitution ---------------------------------------------------------

def test_substitute_recurses_dicts_and_lists():
    obj = {"args": ["--env", "{{env_file}}"], "env": {"URL": "{{JIRA_URL}}"}}
    out = substitute(obj, {"env_file": "/p/x.env", "JIRA_URL": "https://e.example"})
    assert out["args"][1] == "/p/x.env"
    assert out["env"]["URL"] == "https://e.example"


def test_substitute_leaves_unknown_tokens():
    assert substitute("{{a}}-{{b}}", {"a": "1"}) == "1-{{b}}"


def test_unresolved_placeholders_finds_all():
    obj = {"a": "{{x}}", "b": ["{{y}}", "plain"], "c": {"d": "{{x}}"}}
    assert unresolved_placeholders(obj) == ["x", "y"]


# --- build_server_spec ----------------------------------------------------

def test_build_spec_applies_defaults_and_values():
    entry = {
        "spec": {"command": "uvx", "args": ["--env-file", "{{env_file}}"],
                 "env": {"JIRA_URL": "{{JIRA_URL}}", "JIRA_USERNAME": "{{JIRA_USERNAME}}"}},
        "defaults": {"JIRA_URL": "https://d55ltd.atlassian.net"},
    }
    spec = build_server_spec(entry, {"env_file": "/w/.kiro/settings/atlassian.env",
                                     "JIRA_USERNAME": "jane@d55.co.uk"})
    assert spec["env"]["JIRA_URL"] == "https://d55ltd.atlassian.net"   # from defaults
    assert spec["env"]["JIRA_USERNAME"] == "jane@d55.co.uk"
    assert spec["args"][1] == "/w/.kiro/settings/atlassian.env"
    assert unresolved_placeholders(spec) == []


def test_build_spec_command_override():
    entry = {"spec": {"command": "uvx", "args": []}}
    spec = build_server_spec(entry, {"command": "C:/tools/uvx.exe"})
    assert spec["command"] == "C:/tools/uvx.exe"


def test_explicit_value_beats_default():
    entry = {"spec": {"env": {"JIRA_URL": "{{JIRA_URL}}"}}, "defaults": {"JIRA_URL": "https://d55ltd.atlassian.net"}}
    spec = build_server_spec(entry, {"JIRA_URL": "https://other.atlassian.net"})
    assert spec["env"]["JIRA_URL"] == "https://other.atlassian.net"


# --- merge ----------------------------------------------------------------

def test_merge_is_non_destructive_by_default():
    target = {"mcpServers": {"a": {"command": "keep", "autoApprove": ["x"]}}}
    merged, added, skipped = merge_servers(target, {"a": {"command": "new"}, "b": {"command": "npx"}})
    assert added == ["b"]
    assert skipped == ["a"]
    assert merged["mcpServers"]["a"]["command"] == "keep"          # untouched
    assert merged["mcpServers"]["a"]["autoApprove"] == ["x"]        # customisation preserved
    assert merged["mcpServers"]["b"]["command"] == "npx"


def test_merge_overwrite():
    target = {"mcpServers": {"a": {"command": "keep"}}}
    merged, added, skipped = merge_servers(target, {"a": {"command": "new"}}, overwrite=True)
    assert added == ["a"] and skipped == []
    assert merged["mcpServers"]["a"]["command"] == "new"


def test_merge_does_not_mutate_input():
    target = {"mcpServers": {"a": {"command": "keep"}}}
    merge_servers(target, {"b": {"command": "npx"}})
    assert set(target["mcpServers"]) == {"a"}   # original unchanged


def test_merge_into_empty_config():
    merged, added, skipped = merge_servers({"mcpServers": {}}, {"a": {"command": "npx"}})
    assert added == ["a"]


# --- runtime probe --------------------------------------------------------

def test_find_runtime_unknown_returns_none():
    assert find_runtime("does-not-exist") is None


# --- against the real reference ------------------------------------------

def test_reference_loads_and_has_expected_servers():
    ref = load_reference(REFERENCE)
    assert set(ref["servers"]) == {"playwright", "excalidraw", "atlassian"}


def test_reference_specs_build_and_atlassian_needs_user_values():
    ref = load_reference(REFERENCE)
    # node servers have no placeholders
    for name in ("playwright", "excalidraw"):
        assert unresolved_placeholders(build_server_spec(ref["servers"][name], {})) == []
    # atlassian, with only defaults applied, still needs env_file + JIRA_USERNAME
    spec = build_server_spec(ref["servers"]["atlassian"], {})
    assert set(unresolved_placeholders(spec)) == {"env_file", "JIRA_USERNAME"}


def test_reference_atlassian_token_is_not_in_spec():
    # The secret must never live in the mcp.json spec — only the env-file.
    ref = load_reference(REFERENCE)
    spec = build_server_spec(ref["servers"]["atlassian"],
                             {"env_file": "/w/atlassian.env", "JIRA_USERNAME": "jane@d55.co.uk"})
    assert "JIRA_API_TOKEN" not in json.dumps(spec)


@given(st.dictionaries(st.text(min_size=1, max_size=6), st.fixed_dictionaries({"command": st.text(max_size=5)}), max_size=5))
def test_merge_adds_all_absent_names(new_servers):
    merged, added, skipped = merge_servers({"mcpServers": {}}, new_servers)
    assert set(added) == set(new_servers)
    assert set(merged["mcpServers"]) == set(new_servers)
