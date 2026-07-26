"""
Tests for the pure ADF embedding core. No network, no Jira — just document shaping,
idempotency and non-mutation.
"""
import copy
import os
import sys

import pytest
from hypothesis import given
from hypothesis import strategies as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import adf  # noqa: E402


# --------------------------------------------------------------------------- #
# normalize_doc
# --------------------------------------------------------------------------- #
def test_normalize_none_gives_empty_doc():
    assert adf.normalize_doc(None) == {"version": 1, "type": "doc", "content": []}
    assert adf.normalize_doc("") == {"version": 1, "type": "doc", "content": []}


def test_normalize_existing_doc_is_deep_copied():
    src = {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": []}]}
    out = adf.normalize_doc(src)
    out["content"].append({"type": "rule"})
    assert len(src["content"]) == 1  # original untouched


def test_normalize_string_becomes_paragraph():
    out = adf.normalize_doc("legacy text")
    assert out["content"][0]["type"] == "paragraph"
    assert out["content"][0]["content"][0]["text"] == "legacy text"


def test_normalize_rejects_unsupported_type():
    with pytest.raises(TypeError):
        adf.normalize_doc(12345)


# --------------------------------------------------------------------------- #
# external_media_single
# --------------------------------------------------------------------------- #
def test_external_media_single_shape():
    node = adf.external_media_single("https://x/att/1", alt="Screen", width=800)
    assert node["type"] == "mediaSingle"
    assert node["attrs"]["layout"] == "center"
    assert node["attrs"]["width"] == 800
    media = node["content"][0]
    assert media["type"] == "media"
    assert media["attrs"] == {"type": "external", "url": "https://x/att/1", "alt": "Screen", "width": 800}


def test_external_media_single_minimal():
    node = adf.external_media_single("https://x/att/2")
    assert node["content"][0]["attrs"] == {"type": "external", "url": "https://x/att/2"}


def test_external_media_single_invalid_layout():
    with pytest.raises(ValueError):
        adf.external_media_single("https://x/att/3", layout="sideways")


# --------------------------------------------------------------------------- #
# has_external_media
# --------------------------------------------------------------------------- #
def test_has_external_media_detects_url():
    doc, _ = adf.embed_images(None, [{"url": "https://x/att/9"}])
    assert adf.has_external_media(doc, "https://x/att/9")
    assert not adf.has_external_media(doc, "https://x/att/other")


# --------------------------------------------------------------------------- #
# embed_images — add / position / heading
# --------------------------------------------------------------------------- #
def test_embed_appends_at_bottom_by_default():
    start = {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": []}]}
    doc, added = adf.embed_images(start, [{"url": "https://x/att/1"}])
    assert added == ["https://x/att/1"]
    assert doc["content"][0]["type"] == "paragraph"     # existing content first
    assert doc["content"][-1]["type"] == "mediaSingle"  # image appended


def test_embed_prepends_at_top():
    start = {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": []}]}
    doc, _ = adf.embed_images(start, [{"url": "https://x/att/1"}], position="top")
    assert doc["content"][0]["type"] == "mediaSingle"
    assert doc["content"][-1]["type"] == "paragraph"


def test_embed_adds_heading_once():
    doc, _ = adf.embed_images(None, [{"url": "https://x/att/1"}], heading="Design mockup")
    headings = [b for b in doc["content"] if b["type"] == "heading"]
    assert len(headings) == 1
    assert headings[0]["content"][0]["text"] == "Design mockup"


def test_embed_multiple_images_dedupes_within_call():
    doc, added = adf.embed_images(
        None, [{"url": "https://x/att/1"}, {"url": "https://x/att/1"}, {"url": "https://x/att/2"}]
    )
    assert added == ["https://x/att/1", "https://x/att/2"]
    medias = [b for b in doc["content"] if b["type"] == "mediaSingle"]
    assert len(medias) == 2


def test_embed_is_non_mutating():
    start = {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": []}]}
    snapshot = copy.deepcopy(start)
    adf.embed_images(start, [{"url": "https://x/att/1"}])
    assert start == snapshot  # input untouched


def test_embed_invalid_position():
    with pytest.raises(ValueError):
        adf.embed_images(None, [{"url": "https://x/att/1"}], position="middle")


# --------------------------------------------------------------------------- #
# Idempotency
# --------------------------------------------------------------------------- #
def test_embed_same_url_twice_is_noop_second_time():
    doc1, added1 = adf.embed_images(None, [{"url": "https://x/att/1"}])
    doc2, added2 = adf.embed_images(doc1, [{"url": "https://x/att/1"}])
    assert added1 == ["https://x/att/1"]
    assert added2 == []                 # nothing added on the second pass
    assert doc2 == doc1                 # document unchanged


def test_embed_heading_not_duplicated_on_rerun():
    doc1, _ = adf.embed_images(None, [{"url": "https://x/att/1"}], heading="Design mockup")
    # a *new* image on a re-run should not add a second heading
    doc2, added = adf.embed_images(doc1, [{"url": "https://x/att/2"}], heading="Design mockup")
    assert added == ["https://x/att/2"]
    assert len([b for b in doc2["content"] if b["type"] == "heading"]) == 1


# --------------------------------------------------------------------------- #
# Property-based: any set of urls embeds once and re-embedding is stable
# --------------------------------------------------------------------------- #
@given(
    urls=st.lists(
        st.builds(lambda n: f"https://x/att/{n}", st.integers(min_value=1, max_value=50)),
        min_size=1,
        max_size=15,
    )
)
def test_property_embedding_is_idempotent(urls):
    images = [{"url": u} for u in urls]
    doc1, _ = adf.embed_images(None, images)
    doc2, added2 = adf.embed_images(doc1, images)  # re-embed the same set
    assert added2 == []
    assert doc2 == doc1
    # one media node per distinct url
    distinct = list(dict.fromkeys(urls))
    medias = [b for b in doc1["content"] if b["type"] == "mediaSingle"]
    assert len(medias) == len(distinct)
