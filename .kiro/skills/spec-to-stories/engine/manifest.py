"""
Manifest I/O for spec-to-stories.

Each generated mini-spec folder carries a `manifest.yaml` describing the story's
exports, dependencies, requirement coverage and Jira metadata. The decomposition
root carries a `graph.yaml` describing the whole set: the component registry
(component -> exporting story), the resolved edges, the wave ordering and any
issues.

Kiro treats `manifest.yaml` as ordinary metadata, so a developer can copy a
story folder straight into their own `.kiro/specs/` and it remains a valid spec.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from .models import (
    Component,
    Decomposition,
    JiraMeta,
    Story,
    SubTask,
)


def story_from_dict(d: dict) -> Story:
    return Story(
        id=str(d["id"]),
        title=d.get("title", ""),
        user_story=d.get("userStory", d.get("user_story", "")),
        covers_requirements=[str(r) for r in d.get("coversRequirements", d.get("covers_requirements", []))],
        exports=[Component.parse(r) for r in d.get("exports", [])],
        depends_on=[Component.parse(r) for r in d.get("dependsOn", d.get("depends_on", []))],
        subtasks=[
            SubTask(
                id=str(t["id"]),
                title=t.get("title", ""),
                requirements=[str(r) for r in t.get("requirements", [])],
                optional=bool(t.get("optional", False)),
            )
            for t in d.get("subtasks", [])
        ],
        jira=_jira_from_dict(d.get("jira", {})),
    )


def _jira_from_dict(d: dict) -> JiraMeta:
    return JiraMeta(
        issue_type=d.get("issueType", d.get("issue_type", "Story")),
        epic=d.get("epic"),
        labels=list(d.get("labels", [])),
        estimate_days=d.get("estimateDays", d.get("estimate_days")),
    )


def story_to_dict(s: Story) -> dict:
    out: dict = {
        "id": s.id,
        "title": s.title,
        "userStory": s.user_story,
        "coversRequirements": list(s.covers_requirements),
        "exports": [c.ref for c in s.exports],
        "dependsOn": [c.ref for c in s.depends_on],
    }
    if s.subtasks:
        out["subtasks"] = [
            {"id": t.id, "title": t.title, "requirements": t.requirements, "optional": t.optional}
            for t in s.subtasks
        ]
    jira: dict = {"issueType": s.jira.issue_type}
    if s.jira.epic:
        jira["epic"] = s.jira.epic
    if s.jira.labels:
        jira["labels"] = s.jira.labels
    if s.jira.estimate_days is not None:
        jira["estimateDays"] = s.jira.estimate_days
    out["jira"] = jira
    return out


def load_story_manifest(path: str | Path) -> Story:
    with open(path, "r", encoding="utf-8") as f:
        return story_from_dict(yaml.safe_load(f))


def write_story_manifest(story: Story, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(story_to_dict(story), f, sort_keys=False, allow_unicode=True)


def load_stories(root: str | Path) -> list[Story]:
    """Load every `stories/*/manifest.yaml` under a decomposition root."""
    root = Path(root)
    stories: list[Story] = []
    for manifest in sorted(root.glob("stories/*/manifest.yaml")):
        stories.append(load_story_manifest(manifest))
    return stories


def decomposition_to_dict(dec: Decomposition) -> dict:
    index: dict[str, str] = {}
    for s in dec.stories:
        for c in s.exports:
            index[c.ref] = s.id
    return {
        "parentSpec": dec.parent_spec,
        "stories": [s.id for s in dec.stories],
        "components": dict(sorted(index.items())),
        "edges": [
            {"from": e.src, "to": e.dst, "via": e.via} for e in dec.edges
        ],
        "waves": [
            {"wave": i + 1, "stories": members} for i, members in enumerate(dec.waves)
        ],
        "issues": [
            {"kind": i.kind, "detail": i.detail, "stories": i.stories, "components": i.components}
            for i in dec.issues
        ],
        "ok": dec.ok,
    }


def write_graph(dec: Decomposition, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(decomposition_to_dict(dec), f, sort_keys=False, allow_unicode=True)
