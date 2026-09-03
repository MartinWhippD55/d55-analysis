---
name: review-pr
description: Fetch a GitHub Pull Request, perform an iterative code review, and produce a findings summary with a postable comment.
inclusion: manual
---

# Review PR

Fetches a GitHub Pull Request, performs an iterative code review, and produces a findings summary plus a polished PR comment.

This is a **hybrid skill**: a small **deterministic engine** renders the review comment (findings table, positives, verdict table) from structured findings so the format is always consistent and testable, and the **agent** does the reviewing (reading diffs, judging, writing findings). The engine never calls `gh` or GitHub.

## Self-sufficient bundle

```
.kiro/skills/review-pr/
  SKILL.md                 this file
  requirements.txt         hypothesis, pytest
  pytest.ini
  engine/
    comment.py             Finding / VerdictRow models + render_comment / render_findings_table
  templates/
    context.md.tmpl        PR context scaffold
    state.md.tmpl          loop-state tracker scaffold
    review-comment.md.tmpl  the canonical comment shape (reference)
  tests/
    test_comment.py        rendering, pipe-escaping, numbering, legends (incl. property-based)
```

Run the engine from the bundle root (`python -m pytest`, or `import engine.comment`).

## Usage

The user will provide either:
- A full GitHub PR URL (e.g., `https://github.com/owner/repo/pull/123`)
- A repo and PR number (e.g., `owner/repo #123`)

## Output Structure

All review artefacts are stored in a subfolder of `PRs/`:

```
PRs/<repo>-<number>/
├── context.md         # PR metadata, description, comments, file list
├── state.md           # Loop state tracker (for resume if interrupted)
├── summary.md         # Full findings and overall assessment (working notes)
└── review-comment.md  # Polished comment posted to the PR (findings + verdict tables)
```

Scaffold `context.md` and `state.md` from `templates/` in this folder.

## Steps

### Step 1: Fetch PR Context

1. Parse the repo and PR number from the user's input.

2. Use `gh` CLI to fetch PR metadata:
   ```bash
   gh pr view <number> --repo <owner/repo> --json title,body,author,state,baseRefName,headRefName,createdAt,updatedAt,additions,deletions,changedFiles,reviews,comments,labels,url
   ```

3. Fetch any review comments:
   ```bash
   gh api repos/<owner>/<repo>/pulls/<number>/comments --paginate --jq ".[] | {path: .path, body: .body, user: .user.login, line: .line}"
   ```

4. Write `PRs/<repo>-<number>/context.md` (from `templates/context.md.tmpl`) with:
   - PR metadata table (title, author, state, branches, stats, URL)
   - PR description (quoted)
   - Any existing comments/review feedback for context
   - A table of all changed files with their status (added/modified/removed) and lines changed

### Step 2: Cross-Reference Understanding

1. Read the PR description and comments to understand the intent.
2. Group the changed files by area/purpose.
3. Add a "Understanding" section to `context.md` that maps the stated intent to the file changes — identifying which files correspond to which described changes.
4. Flag any files that don't obviously map to the described intent (potential scope creep or undocumented changes).

### Step 3: Iterative File Review

1. Create `PRs/<repo>-<number>/state.md` (from `templates/state.md.tmpl`) to track progress:
   - List of all files to review
   - Current position in the list
   - Files completed
   - Issues found so far

2. For each file (or logical group of related files):
   - Fetch the file's patch/diff using:
     ```bash
     gh api repos/<owner>/<repo>/pulls/<number>/files --paginate --jq ".[] | select(.filename == \"<file>\") | .patch"
     ```
   - Review the diff for:
     - Bugs or logic errors
     - Security concerns
     - Performance issues
     - Missing error handling
     - Style/consistency issues
     - Potential edge cases
   - Record findings in `state.md`
   - Update the current position

3. If the diff is too large to fetch via API, note this and move on.

4. Prioritise reviewing:
   - Infrastructure / IaC changes (high blast radius)
   - Core business logic
   - Configuration files
   - Skip: lock files, generated files, trivial renames

### Step 4: Produce Summary

1. Write `PRs/<repo>-<number>/summary.md` with:
   - Overall assessment (approve / request changes / needs discussion)
   - Key findings grouped by severity (critical, warning, suggestion)
   - Positive observations (good patterns, well-structured code)
   - Questions for the author
   - A brief summary suitable for posting as a PR comment

### Step 5: Draft the PR Comment

Render `PRs/<repo>-<number>/review-comment.md` with the vendored engine, so the tables, numbering and legends are always well-formed (cell contents are pipe-escaped for you):

```python
import sys; sys.path.insert(0, ".kiro/skills/review-pr")
from engine.comment import Finding, VerdictRow, render_comment

md = render_comment(
    title="<feature / PR title>",
    summary="<one or two sentences: overall impression, blockers vs confirmations>",
    findings=[
        Finding("confirm", "`path/to/file`", "<what and why it matters>", "<what you'd like the author to do>"),
        Finding("non_blocking", "<area>", "<finding>", "<suggestion>"),
    ],
    positives=["<specific good pattern, with the concrete reason it's good>", "<another — be specific>"],
    verdict=[
        VerdictRow("Code quality", "good", "<one line>"),
        VerdictRow("Test coverage", "good", "<one line>"),
        VerdictRow("Blocking issues", "good", "None"),
        VerdictRow("Before merge", "confirm", "<the confirm-level findings by number>"),
        VerdictRow("Follow-ups", "non_blocking", "<the non-blocking findings by number>"),
        VerdictRow("Overall", "good", "<the bottom line>", bold=True),
    ],
)
open("PRs/<repo>-<number>/review-comment.md", "w", encoding="utf-8").write(md)
```

The engine renders the four parts (intro, **findings table**, **positives**, **verdict table**) using consistent emojis. `templates/review-comment.md.tmpl` shows the canonical shape for reference.

**Severity keys (findings table):**
| Key | Renders | Meaning |
|-----|---------|---------|
| `blocking` | 🔴 Blocking | Must be fixed before merge (bug, security, data loss). |
| `confirm` | 🟡 Confirm | Not necessarily wrong, but needs the author to confirm intent before merge. |
| `non_blocking` | 🔵 Non-blocking | Minor cleanup / suggestion that can land later. |
| `acknowledged` | ✅ Acknowledged | Raised, then confirmed as expected/intentional (keep it visible with a follow-up note). |

**Status keys (verdict table):** `good` → 🟢 · `confirm` → 🟡 · `problem` → 🔴.

Guidance:
- Reference findings by their table number in the verdict rows so the two line up.
- When the author confirms a 🟡 item during discussion, don't delete it — flip it to `acknowledged`, record the explanation, and note any planned follow-up. This preserves the review trail.
- Keep positives specific and evidence-based; avoid generic filler.
- Set the final `Overall` verdict row to match reality (🟢 good to merge / 🟡 changes requested / 🔴 do not merge).

### Step 6: Post (with approval)

1. Present the drafted comment to the user and ask before posting.
2. Post as a plain comment (does not change the PR's review state):
   ```bash
   gh pr comment <number> --repo <owner/repo> --body-file "PRs/<repo>-<number>/review-comment.md"
   ```
   Prefer `--body-file` over `--body` so tables and emojis render correctly.
3. To revise after posting (e.g. an item was confirmed), edit the file and update the
   same comment in place rather than posting a new one:
   ```bash
   gh pr comment <number> --repo <owner/repo> --edit-last --body-file "PRs/<repo>-<number>/review-comment.md"
   ```

## Verify

- `python -m pytest` in the bundle (engine correctness — rendering, pipe-escaping, numbering, legends).
- Before posting, eyeball the rendered `review-comment.md`: the findings are numbered, the verdict rows reference those numbers, and the tables render (no broken cells).

## Notes

- If interrupted mid-review, `state.md` allows resuming from where we left off.
- Group related files together for review (e.g., a handler + its tests) rather than reviewing in isolation.
- The diff API returns patches per-file which avoids the 20,000-line limit on full PR diffs.
- Be constructive in findings — focus on actionable feedback, not style nitpicks.
- Posting is **not** auto-approved — always confirm with the user first.
