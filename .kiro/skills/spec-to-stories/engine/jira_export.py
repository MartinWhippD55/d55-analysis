"""
Jira export for spec-to-stories.

Produces a CSV suitable for Jira's external-system CSV importer, plus a JSON
form for scripted creation via the Jira REST API.

Mapping:
  - Parent spec        -> Epic
  - Each user story    -> Story  (linked to the Epic)
  - Each sub-task      -> Sub-task (child of its Story)
  - Dependency edges   -> "blocks" links (dst blocks src: dst must ship first)

The CSV is emitted with a stable column set. Jira's importer lets you map these
columns to fields and to build issue links from the Blocks column on import.
Issue keys are synthetic (the story id / sub-task id) so links resolve within
the same import.
"""
from __future__ import annotations

import csv
import io
import json
from collections import defaultdict

from .models import Decomposition


CSV_COLUMNS = [
    "Issue Type",
    "Issue Id",
    "Summary",
    "Description",
    "Epic Name",
    "Epic Link",
    "Parent Id",
    "Labels",
    "Story Points",
    "Blocks",
    "Requirements",
]


def _epic_name(dec: Decomposition) -> str:
    return dec.parent_spec


def to_rows(dec: Decomposition) -> list[dict]:
    """Flatten the decomposition into Jira issue rows (epic, stories, sub-tasks)."""
    epic_name = _epic_name(dec)
    epic_id = f"EPIC-{dec.parent_spec}"

    # dst blocks src (dst must be done first)
    blocks: dict[str, list[str]] = defaultdict(list)
    for e in dec.edges:
        blocks[e.dst].append(e.src)

    rows: list[dict] = []
    rows.append(
        {
            "Issue Type": "Epic",
            "Issue Id": epic_id,
            "Summary": f"{dec.parent_spec} (delivery)",
            "Description": f"Umbrella epic decomposed from spec '{dec.parent_spec}'.",
            "Epic Name": epic_name,
            "Epic Link": "",
            "Parent Id": "",
            "Labels": "",
            "Story Points": "",
            "Blocks": "",
            "Requirements": "",
        }
    )

    for story in dec.stories:
        rows.append(
            {
                "Issue Type": story.jira.issue_type or "Story",
                "Issue Id": story.id,
                "Summary": story.title,
                "Description": story.user_story,
                "Epic Name": "",
                "Epic Link": epic_name,
                "Parent Id": "",
                "Labels": " ".join(story.jira.labels),
                "Story Points": "" if story.jira.estimate_days is None else story.jira.estimate_days,
                "Blocks": ",".join(sorted(blocks.get(story.id, []))),
                "Requirements": ",".join(story.covers_requirements),
            }
        )
        for t in story.subtasks:
            rows.append(
                {
                    "Issue Type": "Sub-task",
                    "Issue Id": t.id,
                    "Summary": t.title,
                    "Description": "",
                    "Epic Name": "",
                    "Epic Link": "",
                    "Parent Id": story.id,
                    "Labels": "optional" if t.optional else "",
                    "Story Points": "",
                    "Blocks": "",
                    "Requirements": ",".join(t.requirements),
                }
            )
    return rows


def to_csv(dec: Decomposition) -> str:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=CSV_COLUMNS)
    writer.writeheader()
    for row in to_rows(dec):
        writer.writerow(row)
    return buf.getvalue()


def to_json(dec: Decomposition) -> str:
    return json.dumps(to_rows(dec), indent=2)


def write_csv(dec: Decomposition, path: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(to_csv(dec))


def write_json(dec: Decomposition, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(to_json(dec))
