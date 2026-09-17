# BrytAdminPortal — Git History Secret Findings

**Context:** Part of the Bryt endpoint/credential-chain compromise work (see `README.md`, `incident-and-hardening.html`). This document records secrets found committed to the `BrytAdminPortal` git history, whether/where they were removed, and the exact commands to purge them from history.

**Method:** Read-only inspection of a full clone (`reference-repos/BrytAdminPortal`, 1906 commits, 2020-06 → 2026-08) using `git log -G/-S` pickaxe, `git show`, and `git grep` against `HEAD` and `origin/dev`. No secret values are reproduced in full here — only the leading identifier prefixes needed to correlate.

_Last updated: 17 Sep 2026._

> **⚠️ Rotation ≠ scrubbing.** Every secret below must be treated as **compromised and rotated** regardless of history rewriting (a clone, fork, or open PR may still carry it). Purging history removes the artefact; it does **not** undo the exposure. Do both. Rotation is tracked in `rotation-checklist-github.md` / `rotation-checklist-aws.md`.

---

## Summary

| # | Secret | Files | Committed | Removed from tree | Exposure |
|---|---|---|---|---|---|
| 1 | GitHub PAT `ghp_fQekuT…` | `cd/branch-stack.yml`, `cd/branch-dual-env-stack.yml`, `auth/pipeline.yml` | 2021-06-21 (Whippy), 2021-11-16 (Peter Job) | 2025-04-03 (Simon, restructure) | ~3.8 yrs in tree; still in history |
| 2 | AWS key `AKIA4TNB…` | `apis/auth/src/auth-command.ts` (+ compiled `.js`) | 2020-06-19 (Peter Job) | 2020-06-24 (Peter Job, "remove access key") | ~5 days in tree; ~6 yrs in history |
| 3 | AWS key `AKIA5NLG…` | `apis/account/src/handlers/getQuicksightUrl.ts` | 2022-11-10 (simon) | 2025-04-03 (Simon, restructure) | ~2.4 yrs in tree; ~3.9 yrs in history |
| 4 | Password literals (×4) | `apis/auth/src/commands/UserEmailCommand.ts`, `auth/resources/UserMigration.js` → `…/cognito-user-migration/index.ts` | 2020-07-02 (Peter Job), 2020-07-10 (Whippy) | 2025-04-03 (Simon, restructure) | 1–6 yrs in history |

**Current tip is clean:** `git grep` for `AKIA[0-9A-Z]{16}` and `ghp_[A-Za-z0-9]{20,}` returns nothing on `HEAD` or `origin/dev`. All four findings remain recoverable in history until scrubbed.

---

## Detailed findings

### 1. GitHub Personal Access Token — `ghp_fQekuT…`

| Event | Commit | Date | Author | Message |
|---|---|---|---|---|
| Introduced | `475b94d67935683601ad389ccb7a262d71416b62` | 2021-06-21 | Whippy | Updating auth token |
| Re-added / spread | `5543a9df0f382beafcf3e3bd98225abac0e556d1` | 2021-11-16 | Peter Job | create new develop ci environment |
| Removed (files deleted) | `e47e8a4db7935092fc40c946fbe6453a9957a961` | 2025-04-03 | Simon | Restructure (#298) |

- Paths: `auth/pipeline.yml`, `cd/branch-dual-env-stack.yml`, `cd/branch-stack.yml`.
- The 2025-04-03 restructure deleted all three YAMLs, so it is absent from the current tree — but the blob is fully recoverable from history.

### 2. AWS access key — `AKIA4TNB…`

| Event | Commit | Date | Author | Message |
|---|---|---|---|---|
| Introduced | `a84ed6c36658fffcbf3fa4d3e10b8fa0ed488971` | 2020-06-19 | Peter Job | fix tsc and deploy |
| Present | `34224225181d0ae295d3b3c5833f1d73ce70a8ee` | 2020-06-19 | Peter Job | fix typescript build |
| Removed | `c1b1f441546dc5ca35f20a7c06bb2373d3258ca5` | 2020-06-24 | Peter Job | remove access key |

- Path: `apis/auth/src/auth-command.ts` (and its compiled `apis/auth/src/auth-command.js`).
- Removed from the working tree quickly (~5 days) but the key lives on in the 2020-06-19..24 commits (~6 years in history).

### 3. AWS access key — `AKIA5NLG…`

| Event | Commit | Date | Author | Message |
|---|---|---|---|---|
| Introduced | `5244b0cefbdd65213f3eb0faeefa83fbfc65388d` | 2022-11-10 | simon | quicksight |
| Edited (same day) | `b9f8db95c6fc47490e403f1ae13235fef6fa971b` | 2022-11-10 | simon | quicksight |
| Edited (same day) | `8496618b3a3bb8d4cdaf9c532a9d03d671c72fbc` | 2022-11-10 | simon | quicksight |
| File deleted | `e47e8a4db7935092fc40c946fbe6453a9957a961` | 2025-04-03 | Simon | Restructure (#298) |

- Path: `apis/account/src/handlers/getQuicksightUrl.ts`.
- No dedicated "remove key" commit — it persisted until the file was deleted in the 2025-04-03 restructure.

### 4. Password literals (×4)

These are hardcoded / template password strings a generic-secret scanner (e.g. gitleaks "generic password") flags. Lower severity than the live keys above, but still credential material in history.

| Event | Commit | Date | Author | Message | Note |
|---|---|---|---|---|---|
| `UserEmailCommand.ts` added | `6a8ed9aaff353c3429735342a357142a2056c00e` | 2020-07-02 | Peter Job | cognito signup | `…password '${request.temporaryPassword}'…` in TextBody + HtmlBody |
| `UserMigration.js` added | `5c94adb3b861571b1fa58d404bc5d40487e51493` | 2020-07-10 | Whippy | Adding migration function to auth pipeline | hardcoded sentinel `password: '~'` in `legacyLookupUser` |
| Removed | `e47e8a4db7935092fc40c946fbe6453a9957a961` | 2025-04-03 | Simon | Restructure (#298) | restructure deleted the legacy auth files |

- Paths: `apis/auth/src/commands/UserEmailCommand.ts`; `auth/resources/UserMigration.js` (later the migration logic moved to `auth/cognito-user-migration/index.ts` → `lambdas-cognito/cognito-user-migration/index.ts`).

> **Attribution / date caveat.** The incident tracker lists a `2024-12-17 (simon)` migration literal under `cognito-user-migration/index.ts`. In this clone that TS file only appears from `5614277c` (2025-01-09, Simon); the actual 2020 literal lives in the older `UserMigration.js`. The README notes this repo's history is *believed to have been rewritten*, so this clone may not be byte-identical to whatever produced the original tracker — expect minor date/author drift.

---

## Purging the secrets from history

> **Do these on a coordinated, admin-run pass — history rewrite is destructive and changes every downstream commit SHA.**
> - **Contain + rotate first** (revoke the PAT, disable the AWS keys). Scrubbing is slow; rotation is what actually closes exposure.
> - Rewriting history **breaks all existing clones, forks, and open PRs**. Everyone must **re-clone** afterwards; open PRs should be closed/recreated.
> - Take a **mirror backup** before rewriting: `git clone --mirror git@github.com:<ORG>/BrytAdminPortal.git BrytAdminPortal-backup.git`.
> - Coordinate with `rotation-checklist-github.md` (branch protection may need temporarily relaxing to force-push, then re-enabled; enable **secret scanning + push protection** afterwards).

### Option A — `git filter-repo` (recommended)

[`git filter-repo`](https://github.com/newren/git-filter-repo) is the tool the Git project recommends over `filter-branch`/BFG. Install via `pip install git-filter-repo` (needs Python 3).

Work on a **fresh mirror clone** (filter-repo refuses to run on a non-fresh clone by design):

```bash
# 1. Fresh mirror
git clone --mirror git@github.com:<ORG>/BrytAdminPortal.git
cd BrytAdminPortal.git

# 2a. Purge whole files that only ever held secrets / build output
git filter-repo --invert-paths \
  --path apis/auth/src/auth-command.ts \
  --path apis/auth/src/auth-command.js \
  --path apis/account/src/handlers/getQuicksightUrl.ts \
  --path cd/branch-stack.yml \
  --path cd/branch-dual-env-stack.yml \
  --path auth/pipeline.yml \
  --path auth/resources/UserMigration.js \
  --path apis/auth/src/commands/UserEmailCommand.ts

# 2b. Redact secret values that may also appear in OTHER files (belt-and-braces).
#     Put the literal strings in replacements.txt (NOT committed anywhere).
#     Format: one per line — literal==>REDACTED  (or use regex:/.../ )
#       ghp_fQekuT<...full token...>==>REDACTED-GH-PAT
#       AKIA4TNB<...full key...>==>REDACTED-AWS-KEY
#       AKIA5NLG<...full key...>==>REDACTED-AWS-KEY
git filter-repo --replace-text replacements.txt

# 3. Re-push the rewritten history (force). This overwrites the remote.
git push --force --mirror git@github.com:<ORG>/BrytAdminPortal.git
```

Notes:
- `--invert-paths --path …` removes those paths from **every** commit. Use `--path-glob` for patterns (e.g. `--path-glob 'apis/auth/src/auth-command.*'`).
- `--replace-text` rewrites blob **contents** so the values are scrubbed even where they were pasted into READMEs, `.env` examples, compiled `.js`, etc. Prefer this for the actual key/token strings.
- Delete `replacements.txt` afterwards; it contains the raw secrets.

### Option B — BFG Repo-Cleaner

[BFG](https://rtyley.github.io/bfg-repo-cleaner/) is simpler for the common "delete files / replace strings" case (Java required).

```bash
git clone --mirror git@github.com:<ORG>/BrytAdminPortal.git
# Remove files by name (matches anywhere in the tree/history):
java -jar bfg.jar --delete-files "{auth-command.ts,auth-command.js,getQuicksightUrl.ts,branch-stack.yml,branch-dual-env-stack.yml,pipeline.yml,UserMigration.js,UserEmailCommand.ts}" BrytAdminPortal.git

# Replace secret literals with ***REMOVED*** (passwords.txt: one literal per line):
java -jar bfg.jar --replace-text passwords.txt BrytAdminPortal.git

cd BrytAdminPortal.git
git reflog expire --expire=now --all && git gc --prune=now --aggressive
git push --force
```

Notes:
- BFG **protects `HEAD`** by default — it won't touch the files as they exist on your latest commit. Since the current tip is already clean of these secrets, that's fine; if a secret were still on `HEAD` you'd remove it with a normal commit first.
- `--delete-files` matches by **filename**, not path — good here because the target filenames are distinctive. Delete `passwords.txt` afterwards.

### After either option

1. **Rotate** every secret (if not already done) — see the GitHub/AWS rotation checklists.
2. Have the whole team **re-clone**; delete stale forks; close/recreate open PRs.
3. Enable **GitHub secret scanning + push protection** and **branch protection / required signed commits** so this can't recur silently.
4. Verify: `git grep -nE 'AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,}' $(git rev-list --all)` returns nothing on the rewritten mirror.
