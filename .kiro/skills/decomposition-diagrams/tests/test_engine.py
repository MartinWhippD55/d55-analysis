"""Pure-engine tests: graph queries, baseline mermaid, and the US-xx -> key rewrite."""
from hypothesis import given, strategies as st

from engine.graph import graph_from_dict
from engine import mermaid
from engine.keymap import remap


GRAPH = {
    "parentSpec": "demo-spec",
    "stories": ["US-01", "US-02", "US-05"],
    "components": {
        "shared-lib:types": "US-01",
        "service:client": "US-02",
        "lambda:worker": "US-05",
    },
    "edges": [
        {"from": "US-02", "to": "US-01", "via": ["shared-lib:types"]},
        {"from": "US-05", "to": "US-01", "via": ["shared-lib:types"]},
        {"from": "US-05", "to": "US-02", "via": ["service:client"]},
    ],
}

KEY_MAP = {"US-01": "SQP-100", "US-02": "SQP-101", "US-05": "SQP-104", "demo-spec": "SQP-99"}


# -- graph model -------------------------------------------------------------- #

def test_delivers_is_sorted_and_scoped():
    g = graph_from_dict(GRAPH)
    assert g.delivers("US-01") == ["shared-lib:types"]
    assert g.delivers("US-05") == ["lambda:worker"]


def test_consumers_is_reverse_of_depends_on():
    g = graph_from_dict(GRAPH)
    # US-01 is depended on by US-02 and US-05 -> those are its consumers
    assert sorted(e.frm for e in g.consumers("US-01")) == ["US-02", "US-05"]
    # US-01 itself depends on nothing
    assert g.depends_on("US-01") == []
    # US-05 depends on US-01 and US-02
    assert sorted(e.to for e in g.depends_on("US-05")) == ["US-01", "US-02"]


# -- baseline mermaid --------------------------------------------------------- #

def test_story_diagram_shows_delivered_components_and_consumer_keys():
    g = graph_from_dict(GRAPH)
    out = mermaid.build_story_diagram(g, "US-01", key_map=KEY_MAP)
    assert "flowchart LR" in out
    assert "shared-lib:types" in out          # what it builds
    assert "SQP-101" in out and "SQP-104" in out  # consumers, by live key
    assert "US-01 / SQP-100 builds" in out


def test_story_diagram_shows_upstream_dependencies():
    g = graph_from_dict(GRAPH)
    out = mermaid.build_story_diagram(g, "US-05", key_map=KEY_MAP)
    assert "SQP-100" in out and "SQP-101" in out  # feeds in from US-01 and US-02
    assert "service:client" in out                # via label


def test_epic_overview_is_valid_baseline_with_todo_banner():
    g = graph_from_dict(GRAPH)
    out = mermaid.build_epic_overview(g, epic_key="SQP-99", key_map=KEY_MAP)
    assert out.startswith("%%")
    assert "TODO(agent)" in out
    assert "flowchart LR" in out
    # every story gets a subgraph
    for s in ("US-01", "US-02", "US-05"):
        assert s in out


def test_story_diagram_is_deterministic():
    g = graph_from_dict(GRAPH)
    a = mermaid.build_story_diagram(g, "US-01", key_map=KEY_MAP)
    b = mermaid.build_story_diagram(g, "US-01", key_map=KEY_MAP)
    assert a == b


# -- key remap ---------------------------------------------------------------- #

def test_remap_rewrites_known_tokens_to_links():
    assert remap("built on US-01", KEY_MAP) == "built on [SQP-100](https://d55ltd.atlassian.net/browse/SQP-100)"


def test_remap_leaves_unknown_tokens_untouched():
    assert remap("see US-09", KEY_MAP) == "see US-09"


def test_remap_protects_identity_labels():
    text = "label `s2s-demo-spec-US-01` stays"
    assert remap(text, KEY_MAP) == text


def test_remap_protects_diagram_filenames():
    assert remap("See attached `US-01.png`", KEY_MAP) == "See attached `US-01.png`"
    assert remap("source US-02.mmd", KEY_MAP) == "source US-02.mmd"


def test_remap_is_idempotent():
    once = remap("built on US-01 and US-02", KEY_MAP)
    twice = remap(once, KEY_MAP)
    assert once == twice


@given(st.integers(min_value=1, max_value=8))
def test_remap_idempotent_property(n):
    key_map = {f"US-0{n}": f"SQP-{100 + n}"}
    text = f"depends on US-0{n} heavily"
    once = remap(text, key_map)
    assert remap(once, key_map) == once
    assert f"SQP-{100 + n}" in once
