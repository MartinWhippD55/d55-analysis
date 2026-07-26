"""
Orchestrate inline image embedding into a Jira issue description (raw ADF).

Ties the pure ``adf`` module to the ``jira_client`` REST calls:

1. Ensure the image is attached to the issue (reuse an existing attachment with the
   same filename rather than uploading a duplicate — Jira does not dedupe by name).
2. Fetch the issue's current description as ADF (faithful; no markdown round-trip).
3. Insert an external ``media`` node pointing at the attachment's content URL, unless
   it is already embedded (idempotent).
4. PUT the updated ADF back.
5. Verify: confirm the media node persisted in the stored ADF, and (best-effort) that
   the rendered description contains an ``<img>`` rather than a broken placeholder.

Run as a module from the bundle root:

    python -m engine.embed SQP-4996 ../path/to/01-template-list.png \
        --heading "Design mockup" --alt "Template list screen"
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from . import adf


def _default_alt(file_path: str) -> str:
    """Derive readable alt text from a filename, e.g. '01-template-list.png'
    -> 'Template list'."""
    stem = Path(file_path).stem
    # drop a leading numeric ordering prefix like "01-"
    parts = stem.split("-", 1)
    if len(parts) == 2 and parts[0].isdigit():
        stem = parts[1]
    return stem.replace("-", " ").replace("_", " ").strip().capitalize()


def ensure_attachment(client, issue_key: str, file_path: str) -> tuple[str, str, bool]:
    """Return ``(filename, content_url, uploaded)`` for the image on the issue.

    Reuses an existing attachment with the same filename (returning its content URL and
    ``uploaded=False``); otherwise uploads and returns ``uploaded=True``.
    """
    filename = Path(file_path).name
    for att in client.list_attachments(issue_key):
        if att["filename"] == filename and att.get("content"):
            return filename, att["content"], False
    uploaded = client.upload_attachment(issue_key, file_path)
    content = uploaded.get("content") or client.attachment_content_url(uploaded["id"])
    return filename, content, True


def embed_image(
    client,
    issue_key: str,
    file_path: str,
    alt: Optional[str] = None,
    position: str = "bottom",
    heading: Optional[str] = None,
    verify: bool = True,
) -> dict:
    """Embed one image into ``issue_key``'s description. Returns a result dict."""
    filename, url, uploaded = ensure_attachment(client, issue_key, file_path)
    current = client.get_description_adf(issue_key)

    if adf.has_external_media(adf.normalize_doc(current), url):
        return {
            "issue": issue_key,
            "file": filename,
            "uploaded": uploaded,
            "embedded": False,
            "reason": "already embedded",
            "url": url,
        }

    new_doc, added = adf.embed_images(
        current,
        [{"url": url, "alt": alt or _default_alt(file_path)}],
        position=position,
        heading=heading,
    )
    client.set_description_adf(issue_key, new_doc)

    result = {
        "issue": issue_key,
        "file": filename,
        "uploaded": uploaded,
        "embedded": bool(added),
        "url": url,
    }
    if verify:
        persisted = adf.has_external_media(
            adf.normalize_doc(client.get_description_adf(issue_key)), url
        )
        html = client.rendered_description_html(issue_key)
        result["verified_adf"] = persisted
        result["verified_rendered_img"] = "<img" in html
    return result


def embed_images(
    client,
    issue_key: str,
    file_paths: list[str],
    alt: Optional[str] = None,
    position: str = "bottom",
    heading: Optional[str] = None,
    verify: bool = True,
) -> list[dict]:
    """Embed several images into one issue. ``alt`` (if given) applies only when there
    is a single image; otherwise alt text is derived per filename."""
    results = []
    for i, fp in enumerate(file_paths):
        this_alt = alt if (alt and len(file_paths) == 1) else None
        # only attach the heading on the first added image
        this_heading = heading if i == 0 else None
        results.append(
            embed_image(client, issue_key, fp, this_alt, position, this_heading, verify)
        )
    return results


def _main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="embed", description="Embed image(s) inline into a Jira issue description (raw ADF)."
    )
    parser.add_argument("issue_key", help="e.g. SQP-4996")
    parser.add_argument("images", nargs="+", help="path(s) to image file(s)")
    parser.add_argument("--alt", help="alt text (single image only; else derived from filename)")
    parser.add_argument("--position", choices=("bottom", "top"), default="bottom")
    parser.add_argument("--heading", help="optional heading inserted once above the image(s)")
    parser.add_argument("--no-verify", action="store_true", help="skip post-write verification")
    parser.add_argument(
        "--dry-run", action="store_true", help="report attach/embed decisions without writing"
    )
    args = parser.parse_args(argv)

    from .jira_client import JiraClient

    client = JiraClient.from_config()

    if args.dry_run:
        existing = {a["filename"] for a in client.list_attachments(args.issue_key)}
        doc = adf.normalize_doc(client.get_description_adf(args.issue_key))
        for fp in args.images:
            name = Path(fp).name
            attached = name in existing
            # can only know the embedded-url for already-attached files
            note = "reuse attachment" if attached else "would upload"
            print(f"[dry-run] {name}: {note}; would embed at {args.position}")
        return 0

    results = embed_images(
        client,
        args.issue_key,
        args.images,
        alt=args.alt,
        position=args.position,
        heading=args.heading,
        verify=not args.no_verify,
    )
    ok = True
    for r in results:
        status = (
            "embedded" if r["embedded"] else f"skipped ({r.get('reason', 'n/a')})"
        )
        verify_bits = ""
        if "verified_adf" in r:
            verify_bits = f" | adf={r['verified_adf']} img={r['verified_rendered_img']}"
            if not r["verified_adf"]:
                ok = False
        print(f"{r['issue']}  {r['file']:<28} {status}{verify_bits}")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(_main())
