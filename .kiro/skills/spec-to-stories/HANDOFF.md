# Handoff — Jira integration & MCP-config sharing

_Last updated: 2026-07-23. Purpose: let a fresh session resume without re-deriving context._

## Where we are (done — archived for lineage)

The **spec-to-stories** skill is built, tested and fully exercised:
- Engine + templates + tests in `.kiro/skills/spec-to-stories/` (`python -m pytest -q`
  → 11 passing).
- The contract-note decomposition is generated under
  `.kiro/specs/contract-note-template-management/decomposition/` (10 stories US-01..US-10,
  6 waves, all 21 parent requirements covered, `ok: true`).
- All 10 mini-specs (US-01..US-10) are authored and pass `getDiagnostics` with zero issues.
- Property-heading format rule is baked into `SKILL.md` (step 5) and
  `templates/story-design.md.tmpl`.

All of the above plus the earlier BRYT contract-note changes are **uncommitted** in the
working tree — that's the starting point for step 1 below.

---

## New plan

Four steps, roughly in order. 2 → 4 build on each other (Jira MCP must exist before the
Jira-export skill can push).

### Step 1 — Commit and push all current changes

Goal: get the working tree committed and pushed so nothing is at risk before we start the
new work.

- Review what's changed first (`git status`, `git diff --stat`) — this includes the whole
  spec-to-stories skill, the contract-note decomposition, and prior BRYT contract-note
  analysis edits.
- Watch for anything that shouldn't be committed: the skill has `.hypothesis/`,
  `.pytest_cache/`, `__pycache__/` (already gitignored in the bundle — confirm), and check
  the repo root `.gitignore`. Flag any file that looks like it holds secrets before staging.
- Per git-safety: push to a **new branch** (not main/master) with `-u`, and only commit
  because the user explicitly asked here.
- Suggested: a branch like `feature/spec-to-stories` (confirm name), one cohesive commit or
  a couple of logical commits (skill vs decomposition vs BRYT analysis).
- Open a PR if the user wants one (confirm remote host — likely GitHub `gh`).

### Step 2 — Configure the Atlassian Jira MCP server

Goal: a working MCP server that can read/write the user's Jira.

- Config lives in `.kiro/settings/mcp.json` (workspace) or `~/.kiro/settings/mcp.json`
  (user-level). Do NOT clobber existing config — merge/edit only.
- Decide which server: the official Atlassian remote MCP vs a community server
  (e.g. `mcp-atlassian`). Needs the Jira site URL, auth (API token / OAuth), and the
  user's account email. **Ask the user** which Jira (cloud/site URL) and how they want to
  authenticate; never hard-code a token into the repo — use env vars / the user config.
- After configuring, TEST by making a sample call (list projects / read an issue) rather
  than inspecting config — per the MCP guidance, only open config if a call fails.
- Record the final server name + tool names once confirmed working (the Jira-export skill
  in step 4 will call them).

### Step 3 — Skill: replicate my MCP setup onto another developer's Kiro workspace

Goal: a skill that takes the current machine's MCP configuration and gets a teammate's Kiro
workspace to the same config, safely.

- New skill dir, e.g. `.kiro/skills/share-mcp-config/` with `SKILL.md` + `USER-README.md`.
- It should: read the user + workspace `mcp.json`, produce a shareable, **secret-free**
  bundle (strip tokens/keys; replace with env-var placeholders + a `.env.example` and
  setup notes), and give the receiving dev a one-step way to apply it (merge into their
  own user/workspace config without overwriting unrelated servers).
- Respect config precedence (user < workspace1 < workspace2 …) and the two locations.
- Hard requirement: never emit real secrets into the shared artifact. Call out exactly
  which env vars/tokens the receiver must supply.
- Consider a small helper (python) to diff/merge two `mcp.json` files deterministically.

### Step 4 — Skill: push a spec-to-stories decomposition into Jira (epic → stories → sub-tasks)

Goal: a new skill, invoked by **spec-to-stories at the very end**, that turns a generated
decomposition into live Jira issues.

- New skill dir, e.g. `.kiro/skills/decomposition-to-jira/`.
- Input: a decomposition folder (`graph.yaml` + `stories/*/manifest.yaml`, and the existing
  `jira-import.csv`/`jira-import.json` the engine already emits).
- Mapping (already the convention in spec-to-stories):
  - parent spec → **Epic**
  - each story folder (US-xx) → **Story** under the epic
  - each story's `subtasks[]` → **Sub-task** under that story
  - dependency edges → **"blocks"** links (dst blocks src)
- Mechanism: call the **Atlassian Jira MCP** from step 2 to create issues (not CSV import),
  preserving idempotency where possible (don't duplicate on re-run — look up by a stable
  key/label first).
- Wire-in: add a final optional step to spec-to-stories `SKILL.md` that hands the
  decomposition off to this skill once `dec.ok` and the docs are authored.
- Return a summary: created epic key, story keys, sub-task keys, and the links made.

---

## Key conventions carried over (unchanged)

- Component ref syntax `kind:name`; one exporter per component.
- Edge semantics: `src depends-on dst` ⇒ dst first ⇒ "blocks" link dst→src in Jira.
- Decomposition output location: `.kiro/specs/<parent>/decomposition/`.
- Jira mapping: epic / story / sub-task / "blocks" (see step 4).
- Never write secrets into the repo or shared artifacts (steps 2–3).

## How to resume

Start with step 1 (commit + push) once the user confirms the branch name and whether they
want a PR. Steps 2→4 are sequential (Jira MCP before the Jira-push skill). Step 3 is
independent and can be done any time after step 2's config exists.
