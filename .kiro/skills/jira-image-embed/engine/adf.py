"""
Pure Atlassian Document Format (ADF) manipulation for inline image embedding.

Why this exists
---------------
The Atlassian Jira MCP writes descriptions as *markdown*, which it converts to ADF.
That path cannot embed an image inline: a markdown image reference to an attachment
filename is stored as an image node pointing at a bare path, which Jira Cloud never
resolves (attachments are served from signed media URLs), so it renders as a broken
placeholder. To embed an image you must write the description as **raw ADF** with a
``media`` node.

This module is the *pure, no-network heart* of the jira-image-embed skill. It builds
the ADF ``mediaSingle`` node and inserts it into an existing description document,
non-destructively and idempotently. All network I/O (fetch the current ADF, upload the
attachment, PUT the new ADF) lives in ``jira_client.py``; this module never touches
Jira and is fully unit-testable in isolation.

Embedding strategy
------------------
Following the language-agnostic recipe recommended by the Atlassian developer
community, images are embedded as an **external media node** pointing at the
attachment's REST content URL (``.../rest/api/3/attachment/content/{id}``). Because
that URL is on the same Jira host, a signed-in viewer's browser is already
authenticated and renders it, and we avoid the media-services UUID flow (and the
grey-placeholder bug that path is prone to).
"""
from __future__ import annotations

import copy
from typing import Iterable, Optional

# ADF layouts valid on a mediaSingle node.
VALID_LAYOUTS = ("center", "wide", "full-width", "align-start", "align-end")

DEFAULT_LAYOUT = "center"


def empty_doc() -> dict:
    """Return a minimal, valid empty ADF document."""
    return {"version": 1, "type": "doc", "content": []}


def normalize_doc(description) -> dict:
    """Coerce a Jira ``description`` field value into a valid ADF doc dict.

    - ``None`` / empty  -> a fresh empty doc.
    - an ADF dict (``type == "doc"``) -> a deep copy (so callers never mutate the
      value they were handed).
    - a plain string (legacy/wiki description) -> a doc with a single paragraph
      carrying that text, so existing content is preserved rather than dropped.
    """
    if description is None or description == "":
        return empty_doc()
    if isinstance(description, dict) and description.get("type") == "doc":
        doc = copy.deepcopy(description)
        doc.setdefault("version", 1)
        doc.setdefault("content", [])
        return doc
    if isinstance(description, str):
        return {
            "version": 1,
            "type": "doc",
            "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": description}]}
            ],
        }
    raise TypeError(f"unsupported description type: {type(description)!r}")


def external_media_single(
    url: str,
    alt: Optional[str] = None,
    layout: str = DEFAULT_LAYOUT,
    width: Optional[int] = None,
    height: Optional[int] = None,
) -> dict:
    """Build a ``mediaSingle`` block wrapping an external ``media`` node for ``url``.

    ``width``/``height`` are optional pixel hints; ``alt`` becomes the media node's
    alt text. ``layout`` must be one of ``VALID_LAYOUTS`` (defaults to ``center``).
    """
    if layout not in VALID_LAYOUTS:
        raise ValueError(f"invalid layout {layout!r}; expected one of {VALID_LAYOUTS}")

    media_attrs: dict = {"type": "external", "url": url}
    if alt:
        media_attrs["alt"] = alt
    if width is not None:
        media_attrs["width"] = width
    if height is not None:
        media_attrs["height"] = height

    single_attrs: dict = {"layout": layout}
    if width is not None:
        single_attrs["width"] = width

    return {
        "type": "mediaSingle",
        "attrs": single_attrs,
        "content": [{"type": "media", "attrs": media_attrs}],
    }


def heading_node(text: str, level: int = 3) -> dict:
    """Build an ADF heading node."""
    return {
        "type": "heading",
        "attrs": {"level": level},
        "content": [{"type": "text", "text": text}],
    }


def _iter_external_media_urls(doc: dict) -> Iterable[str]:
    """Yield the url of every external media node already in ``doc`` (top level)."""
    for block in doc.get("content", []):
        if block.get("type") != "mediaSingle":
            continue
        for child in block.get("content", []):
            attrs = child.get("attrs", {})
            if child.get("type") == "media" and attrs.get("type") == "external":
                url = attrs.get("url")
                if url:
                    yield url


def has_external_media(doc: dict, url: str) -> bool:
    """Return True if ``doc`` already embeds an external media node for ``url``."""
    return url in set(_iter_external_media_urls(doc))


def _has_heading(doc: dict, text: str) -> bool:
    for block in doc.get("content", []):
        if block.get("type") == "heading":
            inner = "".join(
                c.get("text", "") for c in block.get("content", []) if c.get("type") == "text"
            )
            if inner == text:
                return True
    return False


def embed_images(
    description,
    images: list[dict],
    position: str = "bottom",
    heading: Optional[str] = None,
) -> tuple[dict, list[str]]:
    """Return ``(new_doc, added_urls)`` with the given images embedded in ``description``.

    ``description`` is any value the Jira ``description`` field can hold (None, an ADF
    dict, or a string); it is normalized and never mutated. ``images`` is a list of
    dicts with keys: ``url`` (required), optional ``alt``, ``layout``, ``width``,
    ``height``.

    Idempotency: an image whose ``url`` is already embedded is skipped, so re-running
    against the same issue (with the same attachment, hence the same content URL) adds
    nothing. If ``heading`` is given, the heading block is added once — only when at
    least one image is actually being added and the heading is not already present.

    ``position`` is ``"bottom"`` (append, default) or ``"top"`` (prepend). Pure.
    """
    if position not in ("bottom", "top"):
        raise ValueError(f"invalid position {position!r}; expected 'bottom' or 'top'")

    doc = normalize_doc(description)

    new_blocks: list[dict] = []
    added_urls: list[str] = []
    for img in images:
        url = img["url"]
        if has_external_media(doc, url) or url in added_urls:
            continue  # already embedded — idempotent skip
        new_blocks.append(
            external_media_single(
                url,
                alt=img.get("alt"),
                layout=img.get("layout", DEFAULT_LAYOUT),
                width=img.get("width"),
                height=img.get("height"),
            )
        )
        added_urls.append(url)

    if not new_blocks:
        return doc, []  # nothing to do

    if heading and not _has_heading(doc, heading):
        new_blocks.insert(0, heading_node(heading))

    if position == "top":
        doc["content"] = new_blocks + doc["content"]
    else:
        doc["content"] = doc["content"] + new_blocks

    return doc, added_urls
