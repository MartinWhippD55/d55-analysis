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

### Step 1 — Commit and push all current changes — DONE

Pushed to `main` (`243d172..d6277e7`) as four logical commits: (1) spec-to-stories skill,
(2) contract-note spec rework + 10-story decomposition, (3) BRYT contract-note analysis/
estimates/discussion notes, (4) ESG consolidated-update notes. Cache dirs stayed out via
the bundle `.gitignore`. Working tree clean.

### Step 2 — Configure the Atlassian Jira MCP server — DONE (verified)

Verified working: `jira_get_user_profile` returned Martin Whipp
(account_id `5c4b3c44cc3a1d3d8a2bc81b`) and `jira_get_all_projects` listed the instance.
Tool prefix is `mcp_atlassian_jira_*` (e.g. `jira_create_issue`, `jira_create_issue_link`,
`jira_get_project_issue_types`, `jira_link_to_epic`). Useful project keys: **BRYT** (Bryt)
for the real epic; **TEST** (Bryt MSP Project) as a safe sandbox for the step-4 skill.


Decisions: community **`mcp-atlassian`** server, **workspace** config
(`.kiro/settings/mcp.json`), Jira Cloud `https://d55ltd.atlassian.net`, user
`martin.whipp@d55.co.uk`.

What's set up:
- `uv`/`uvx` was not installed → installed via `pip install uv` (v0.11.31). It landed in
  the Store-Python Scripts dir and is **not on PATH**, so `mcp.json` uses the **full path**
  to `uvx.exe`
  (`...\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\LocalCache\local-packages\Python310\Scripts\uvx.exe`).
  `uvx mcp-atlassian --help` runs (installs 109 pkgs on first run) — server binary is good.
- `mcp.json` server entry `atlassian`: command = full uvx path, args =
  `mcp-atlassian --env-file <abs path to .kiro/settings/atlassian.env>`, env =
  `JIRA_URL` + `JIRA_USERNAME` (non-secret, tracked). `autoApprove: []` (writes not
  auto-approved yet — revisit for the step-4 skill).
- **Secret handling:** token goes in `.kiro/settings/atlassian.env` (created with a
  placeholder), which is git-ignored via a new rule `.kiro/settings/*.env`. Confirmed
  `git check-ignore` catches it. `mcp.json` stays secret-free and committable.

Outstanding to finish step 2 (needs the user):
1. Create a Jira API token at https://id.atlassian.com/manage-profile/security/api-tokens.
2. Paste it into `.kiro/settings/atlassian.env` (replace `REPLACE_WITH_YOUR_JIRA_API_TOKEN`).
3. Reconnect the `atlassian` server from the Kiro MCP panel (re-spawns and re-reads the
   env file — no full restart needed).
4. Then TEST with a live call (e.g. list Jira projects / get current user / read an issue).
   Record the working tool names for the step-4 skill.

Gotcha for step 3/4: the full `uvx.exe` path and the `--env-file` absolute path are
machine-specific — the config-sharing skill (step 3) must normalise these.

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
