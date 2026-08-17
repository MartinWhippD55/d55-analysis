---
inclusion: fileMatch
fileMatchPattern: '**/decomposition/**'
---

# Decomposition → Jira Pipeline (overview)

Turning a spec into live, enriched Jira issues is a chain of skills. This is a map only
— **each skill's `SKILL.md` is the source of truth** for how to run it.

```
spec-to-stories → decomposition-to-jira → jira-tree → jira-push → [decomposition-diagrams]
```

| Stage | Skill | Does |
|-------|-------|------|
| 1 | `.kiro/skills/spec-to-stories/` | Decompose a spec into stories/sub-tasks (`graph.yaml`, mini-specs). |
| 2 | `.kiro/skills/decomposition-to-jira/` | Build the ordered, idempotent `jira-plan.json`. |
| 3 | `.kiro/skills/jira-tree/` | Render an editable markdown mirror; enrich the descriptions. |
| 4 | `.kiro/skills/jira-push/` | Push the reviewed tree to live Jira (epic, stories, sub-tasks, links). |
| 5 (optional) | `.kiro/skills/decomposition-diagrams/` | Generate + inline-embed architecture diagrams on the issues. |

Supporting: `.kiro/skills/jira-image-embed/` — embeds an image inline in a Jira Cloud
description via raw ADF (the MCP's markdown path can't). Used by stage 5.

## Cross-skill gotchas

- **Markdown can't embed images on Jira Cloud** — use `jira-image-embed` (raw-ADF media
  node), not a markdown/`!file!` reference.
- **Push prose before embedding** — an MCP description update replaces the body and wipes
  any embedded media node.
- **Idempotent throughout** — issues dedupe by identity label, links by `(outward,
  inward)`, attachments by filename, embeds by media URL. Re-running adds nothing.
