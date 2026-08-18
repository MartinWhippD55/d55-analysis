# Handoff — Stage 5 (decomposition-diagrams) for contract-note-data-source-extensibility

_Self-contained handoff so a fresh session can run the optional final pipeline stage
(architecture diagrams + inline Jira embeds) without re-deriving context._

## Where we are

The `contract-note-data-source-extensibility` spec (Estimate 3b) has been run through
the full local pipeline **and pushed live to Jira**:

- **spec-to-stories** → 8 stories (US-01..US-08), 6 waves, `graph.yaml` `ok: true`, all
  7 parent requirements covered; 24 mini-spec files under `stories/US-0x/`.
- **decomposition-to-jira** → `jira-plan.json`: 1 epic, 8 stories, 31 sub-tasks, 15
  blocks-links.
- **jira-tree** → enriched + validated mirror at `jira-tree/` (`validate_tree` → `[]`,
  `find_placeholders` → `0`).
- **jira-push** → pushed to **project `SQP`** (SO board). All 40 issues + 15 Blocks
  links created fresh; descriptions rewritten so `US-xx` cross-references point at live
  keys. Set label: `s2s-contract-note-data-source-extensibility`.

Everything above is committed to `main`.

## The only outstanding step = Stage 5: decomposition-diagrams (optional)

Follow `.kiro/skills/decomposition-diagrams/SKILL.md` — it is the source of truth. In
short: generate baseline mermaid from `graph.yaml`, **hand-author the epic
service-interaction diagram** (graph edges are build deps, not runtime flow), render to
PNG, add an `## Architecture` / `## Service interaction` prose section to each tree body
first, push the prose via the MCP (remap `US-xx` → live keys via `_placeholders.md`),
then **embed the PNGs via `jira-image-embed`** (raw-ADF media node — markdown can't embed
on Jira Cloud). **Push prose before embedding** (an MCP description write wipes a media
node). Then commit `diagrams/` (`.mmd` + `.png`) and the updated tree bodies.

## Live Jira key map (project SQP, epic SQP-5079)

The `tree-key -> Jira-key` map is also snapshotted in `jira-tree/_placeholders.md`
(what `keymap.load_key_map` reads).

| Story | Key | Sub-tasks (key) |
|-------|-----|-----------------|
| Epic  | SQP-5079 | — |
| US-01 Foundation: types, trust policy, Athena | SQP-5080 | US-01-1 SQP-5081, US-01-2 SQP-5082, US-01-3 SQP-5083 |
| US-02 Glue Data Catalog discovery client | SQP-5085 | US-02-1 SQP-5091, US-02-2 SQP-5092, US-02-3 SQP-5093 |
| US-03 Data Source API + routing | SQP-5086 | US-03-1 SQP-5100, US-03-2 SQP-5097, US-03-3 SQP-5098, US-03-4 SQP-5101, US-03-5 SQP-5102, US-03-6 SQP-5103, US-03-7 SQP-5104, US-03-8 SQP-5105, US-03-9 SQP-5106 |
| US-04 Data source dependency scanner | SQP-5084 | US-04-1 SQP-5088, US-04-2 SQP-5090, US-04-3 SQP-5089 |
| US-05 Render pipeline enrichment | SQP-5087 | US-05-1 SQP-5094, US-05-2 SQP-5095, US-05-3 SQP-5096, US-05-4 SQP-5099 |
| US-06 FE data sources panel | SQP-5108 | US-06-1 SQP-5115, US-06-2 SQP-5117, US-06-3 SQP-5116 |
| US-07 FE field browser + shared-section deps | SQP-5107 | US-07-1 SQP-5110, US-07-2 SQP-5112, US-07-3 SQP-5111, US-07-4 SQP-5113 |
| US-08 Integration wiring & e2e validation | SQP-5109 | US-08-1 SQP-5114, US-08-2 SQP-5118 |

## How to resume

1. MCP sanity check: `jira_get_user_profile martin.whipp@d55.co.uk`. If disconnected,
   ensure `.kiro/settings/atlassian.env` has a valid token and reconnect the
   `atlassian` server from the Kiro MCP panel.
2. `cd .kiro/skills/decomposition-diagrams` → `python -m pytest` (and
   `python -m pytest ../jira-image-embed`).
3. `python -m engine.generate .kiro/specs/contract-note-data-source-extensibility/decomposition`
4. Refine `diagrams/epic-service-interaction.mmd` by hand into the real runtime flow:
   `subscribe → Glue discovery (US-02) → attach via API (US-03) → reference fields in
   section editor (US-07) → at render time enrich via Athena (US-05) → enriched PDF`.
   Annotate each participant with its story + key.
5. `python -m engine.render .../decomposition/diagrams` and eyeball the PNGs (mermaid
   fails quietly with a bomb graphic).
6. Add prose sections to the tree bodies, push via MCP (remap keys), then embed PNGs via
   `jira-image-embed` (`--position top --heading "Overview"`). Prose first, embed second.
7. Verify each embed reports `adf=True img=True`; re-run to confirm idempotency; commit
   `diagrams/` + updated tree bodies.

## Gotchas (carried from the skill + prior runs)

- Markdown can't embed images on Jira Cloud — use `jira-image-embed` (raw-ADF media node).
- Push prose **before** embedding — an MCP description update wipes any media node.
- `graph.yaml` edges are **build** dependencies, not runtime flow — hand-author the epic
  diagram.
- Attachments don't dedupe by filename; `jira-image-embed` reuses by name — never
  blind-upload twice.
- Everything is idempotent by label / media URL; re-running adds nothing.
- SQP is a live, busy board — the `s2s-contract-note-data-source-extensibility` label is
  how you find (or clean up) exactly this push.
- US-03-1's Jira **summary** was shortened to fit Jira's 255-char limit; the full text
  lives in its description body (cosmetic only).
