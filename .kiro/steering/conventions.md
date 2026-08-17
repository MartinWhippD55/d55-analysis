---
inclusion: auto
---

# Repository Conventions

## Git

- **Branch model: work on `main`.** Commit and push directly to `main` — this repo does
  not use feature branches or PRs. (This intentionally overrides the default "push to a
  new branch" behaviour.)
- Only create commits when asked. Stage specific paths, not `git add .`.
- Never commit secrets. Credentials live only in `.kiro/settings/atlassian.env`
  (git-ignored).

## Where things live

- `analysis/<CLIENT>/<PROJECT>/<TASK>/` — analysis work (see `project-structure.md`).
- `.kiro/specs/<parent>/` — specs and their `decomposition/` (graph, jira-tree, stories).
- `.kiro/skills/<name>/` — reusable skills (each has a `SKILL.md`; most have tests).
- `.kiro/settings/` — `mcp.json` and `atlassian.env` (Jira credentials).

## Jira

- Writes go through the Atlassian MCP (`mcp_atlassian_jira_*`); sanity-check with a read
  before writing. Writes are not auto-approved.
- Decomposition → Jira is a defined pipeline — see `jira-pipeline.md` (loads when working
  under a `decomposition/`).
