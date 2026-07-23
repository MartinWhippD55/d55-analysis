# Handoff — Jira integration & MCP-config sharing

_Last updated: 2026-07-23 (step 4 skill built). Purpose: let a fresh session resume without re-deriving context._

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

All of the above (plus the earlier BRYT contract-note changes and the Jira MCP config) is
now **committed and pushed to `main`** — see steps 1–2 below.

---

## Outstanding at a glance

- ✅ **Step 1** — commit + push all work (done, on `main`).
- ✅ **Step 2** — Atlassian Jira MCP configured + verified live (done).
- ⬜ **Step 3** — `share-mcp-config` skill (not started).
- 🟡 **Step 4** — `decomposition-to-jira` skill: **built, tested, wired in** (planner
  `engine/plan.py`, 7 passing tests, `SKILL.md` + `USER-README.md`, and an optional
  step 7 added to spec-to-stories `SKILL.md`). `jira-plan.json` generated for the
  contract-note decomposition (1 epic, 10 stories, 44 sub-tasks, 19 blocks-links).
  **Not yet run against live Jira** — a trial push to `TEST` is pending user go-ahead
  (writes are not auto-approved). Not yet committed.

Steps 3 and the live step-4 trial are independent. Suggested next: **run the step-4
trial against `TEST`** (then commit), or start **step 3**.

## New plan

Four steps. 2 → 4 build on each other (Jira MCP must exist before the Jira-export skill
can push); step 3 is independent.

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

Setup (committed on `main`, secret-safe):
- Community **`mcp-atlassian`** server, **workspace** config `.kiro/settings/mcp.json`,
  Jira Cloud `https://d55ltd.atlassian.net`, user `martin.whipp@d55.co.uk`.
- `uv`/`uvx` was missing → installed via `pip install uv` (v0.11.31). It landed in the
  Store-Python Scripts dir and is **not on PATH**, so `mcp.json` uses the **full path** to
  `uvx.exe`
  (`...\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\LocalCache\local-packages\Python310\Scripts\uvx.exe`).
- `mcp.json` `atlassian` entry: command = full uvx path, args =
  `mcp-atlassian --env-file <abs path to .kiro/settings/atlassian.env>`, env =
  `JIRA_URL` + `JIRA_USERNAME` (non-secret, tracked). `autoApprove: []` — **writes are not
  auto-approved**; revisit when the step-4 skill starts creating issues.
- **Secret handling:** the API token lives ONLY in `.kiro/settings/atlassian.env`,
  git-ignored via `.kiro/settings/*.env` (verified with `git check-ignore`; confirmed the
  file is not tracked). `mcp.json` stays secret-free.

Gotcha for steps 3/4: the full `uvx.exe` path and the `--env-file` absolute path are
machine-specific — the step-3 config-sharing skill must normalise these, and the step-4
skill should not assume them.

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

### Step 4 — Skill: push a spec-to-stories decomposition into Jira (epic → stories → sub-tasks) — BUILT (live trial pending)

A new skill `.kiro/skills/decomposition-to-jira/` turns a decomposition into live Jira
issues. What's done:

- **Engine** `engine/plan.py`: `build_plan(decomposition_dir)` reads `graph.yaml` +
  `stories/*/manifest.yaml` and returns a deterministic, idempotent `JiraPlan`
  (epic / stories / sub-tasks / "blocks" links). `write_plan` + `summarize` helpers.
  Pure — makes no Jira calls.
- **Idempotency by stable label:** epic `s2s-<parent>-epic`, story
  `s2s-<parent>-US-01`, sub-task `s2s-<parent>-US-01-1`, plus set label
  `s2s-<parent>` on everything. The agent searches the identity label before creating.
- **Link direction:** edge `from: src, to: dst` ⇒ `Blocks` link with
  `outward=dst` (ships first) `inward=src` — "outward blocks inward".
- **Tests** `tests/test_plan.py`: mapping, label validity/uniqueness, determinism,
  and a property that every edge → exactly one correctly-directed link. `python -m
  pytest` → 7 passing.
- **Docs:** `SKILL.md` (agent workflow: sanity-check MCP → build plan → confirm
  project/issue types → create/reuse epic → stories → sub-tasks → links → summary)
  and `USER-README.md`.
- **Wired in:** spec-to-stories `SKILL.md` now has an optional **step 7** handing the
  decomposition off to this skill.
- **Generated** `.kiro/specs/contract-note-template-management/decomposition/jira-plan.json`
  (1 epic, 10 stories, 44 sub-tasks, 19 blocks-links).

Still to do:
- **Pick a target project/board for the live trial** (see "Jira project/board recon"
  below) — open question, user will decide tomorrow.
- **Live trial** against the chosen project — NOT yet run; writes aren't
  auto-approved, needs user go-ahead. Then verify + re-run for idempotency.
- **Gotcha found:** `jira_get_project_issue_types` returned `[]` for both `TEST` and
  `BRYT` (likely team-managed / permission). The skill's step 2 already handles this:
  fall back to standard type names (`Epic`/`Story`/`Sub-task`) or inspect an existing
  issue for the exact sub-task type name.

### Jira project/board recon (2026-07-23) — where to run the step-4 trial

Investigated which project/board should receive the trial push. Findings:

- **`TEST` (Bryt MSP Project)** — the intended sandbox. **Empty** (0 issues) and
  `jira_get_project_issue_types` returns `[]`. Unverified whether it accepts
  Epic/Story/Sub-task. Safe, but must confirm types before use.
- **`BRYT` (Bryt)** — the real delivery project. **No agile board** is exposed via the
  API and it returns no issue types → almost certainly **team-managed (next-gen)**.
  Would need a real BRYT issue read to confirm its type names.
- **`BRT` (Bryt Support)** — company-managed **support/break-fix** queue (board id 84,
  kanban). Only **Task** and **Bug** types, driven by "Bryt Energy"-reported tickets.
  **Not suitable** — no Story/Sub-task.
- **`SQP` (Squad Phoenix)** — backs the **`SO board`** (id 101, kanban, ~3,757 issues).
  Company-managed, active dev board using **Story / Task / Bug** with a full workflow.
  This is the one place confirmed to support `Story` as a real type — but it's a live,
  busy project, so any trial issues would sit among real work (they'd carry the
  `s2s-<parent>` labels, so easy to find and delete).
- All 16 accessible agile boards are **kanban**; there are no scrum boards on the
  instance.

Decision for tomorrow: choose between `TEST` (verify types first), `SQP` (proven types,
but live — label + clean up), or reading a `BRYT` issue to see if Bryt itself works.
Whichever is chosen, verify issue types before creating anything.

---

## Key conventions carried over (unchanged)

- Component ref syntax `kind:name`; one exporter per component.
- Edge semantics: `src depends-on dst` ⇒ dst first ⇒ "blocks" link dst→src in Jira.
- Decomposition output location: `.kiro/specs/<parent>/decomposition/`.
- Jira mapping: epic / story / sub-task / "blocks" (see step 4).
- Never write secrets into the repo or shared artifacts (steps 2–3).

## How to resume

Steps 1 and 2 are done and pushed to `main`. The step-4 **skill is built, wired and
committed** (see above); it has not been run against live Jira. The open question is
**which project/board to trial against** (see "Jira project/board recon") — the user
will decide tomorrow. Pick up by either:

- **Finishing step 4:** confirm the target project with the user, sanity-check the MCP
  is live (`jira_get_user_profile martin.whipp@d55.co.uk`), verify that project's issue
  types, then follow `.kiro/skills/decomposition-to-jira/SKILL.md` to push the generated
  `jira-plan.json`, verify + re-run for idempotency. If the MCP is disconnected, ensure
  `.kiro/settings/atlassian.env` still holds a valid token and reconnect the `atlassian`
  server from the Kiro MCP panel.
- **Starting step 3** (`share-mcp-config`) — independent of the above.
