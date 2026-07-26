---
inclusion: manual
---

# Jira Image Embed

Embed one or more images **inline** in a Jira Cloud issue description — visible in the
description body, not just the Attachments panel. Idempotent: re-running never
duplicates the attachment or the embed.

## Why this is a separate skill (and not the Atlassian MCP)

The Atlassian Jira MCP writes descriptions as **markdown**, which it converts to ADF.
That path *cannot* embed an image: a markdown image reference to an attachment filename
becomes an image node pointing at a bare path, and Jira Cloud only serves attachments
from signed media URLs — so it renders as a broken placeholder (confirmed empirically).

True inline embedding needs the description written as **raw ADF** with a `media`
node. No MCP tool does that, so this skill talks to the Jira REST API directly. As a
bonus, the raw GET→insert→PUT flow is *more* faithful than the markdown route: it reads
the existing description ADF and only inserts a node, so nothing else is reformatted.

## Approach — external media node

Following the language-agnostic recipe recommended by the Atlassian developer
community, an image is embedded as an **external** `media` node whose `url` is the
attachment's REST content URL (`.../rest/api/3/attachment/content/{id}`):

```json
{ "type": "mediaSingle", "attrs": { "layout": "center" },
  "content": [ { "type": "media", "attrs": { "type": "external", "url": "<attachment content url>", "alt": "…" } } ] }
```

Because that URL is on the same Jira host, a signed-in viewer's browser is already
authenticated and renders it. This avoids the media-services UUID flow and the
grey-placeholder bug (`JRACLOUD-97869`) that the "proper" `type: file` path is prone
to. We still **verify** every write (see below), because that bug exists.

## Self-sufficient bundle

```
.kiro/skills/jira-image-embed/
  SKILL.md              this file
  USER-README.md        user-facing guide
  requirements.txt      requests, hypothesis, pytest
  engine/
    adf.py              PURE: build/insert media nodes, idempotency, non-mutating
    jira_client.py      thin authed REST client (config load, get/list/upload/put/rendered)
    embed.py            orchestration + CLI (python -m engine.embed)
  tests/
    test_adf.py         pure ADF tests (shape, position, heading, idempotency, property-based)
```

`adf.py` makes no network calls and is fully unit-tested. `jira_client.py` is the only
part that touches Jira.

## Prerequisites

- **Credentials**, read from the same source as the `atlassian` MCP server:
  `JIRA_API_TOKEN` from `.kiro/settings/atlassian.env` (git-ignored), and `JIRA_URL` /
  `JIRA_USERNAME` from `atlassian.env` or the `atlassian` server's `env` block in
  `.kiro/settings/mcp.json`. Any may be overridden by a real environment variable.
- `pip install -r requirements.txt` (needs `requests`).
- A **target issue key** and local **image path(s)**.

## Steps

### 1. Verify the engine

```
python -m pytest      # from the bundle root
```

### 2. Embed

From the bundle root:

```
python -m engine.embed <ISSUE_KEY> <image_path> [<image_path> ...] \
    [--heading "Design mockup"] [--alt "…"] [--position bottom|top] [--no-verify] [--dry-run]
```

- Reuses an existing attachment with the same filename (no duplicate upload); otherwise
  uploads it, then embeds the external media node.
- `--position` defaults to `bottom` (append). `--heading` inserts one heading above the
  image(s), only if not already present. `--alt` applies to a single image; for several,
  alt text is derived from each filename.
- `--dry-run` reports the attach/embed decision per file without writing.

### 3. Confirm

The CLI prints per image, e.g. `SQP-4996  01-template-list.png  embedded | adf=True img=True`:

- `adf=True` — the media node persisted in the stored description ADF (Jira didn't strip it).
- `img=True` — the server-rendered description contains an `<img>` (not a broken placeholder).

Both true = success. If `adf=False`, the instance rejected external media; if `img=False`,
suspect the grey-placeholder bug — inspect `renderedFields` before trusting the result.

## Typical use: design mockups on frontend tickets

Attach each screen mockup to the ticket that builds it (by the `NN-name.png` convention),
e.g. `01-template-list.png` → the Template List sub-task. Embed the full set on the
parent screens story or the epic as an at-a-glance overview. Only frontend tickets have
mockups; backend tickets get none. Label them as **design mockups** — they are a
snapshot that can drift from the build; the repo copy stays canonical.

## Hard rules

- **Read before write.** The flow GETs the current ADF and inserts into it — it never
  blindly overwrites a description.
- **Idempotent.** Attachments dedupe by filename; embeds dedupe by media URL. Re-running
  adds nothing. (Jira does not dedupe attachments by name — always reuse, never blind-upload.)
- **Verify every write.** External media embedding has a known Jira bug; always check
  `adf` + rendered `<img>` (the CLI does this unless `--no-verify`).
- **Sandbox / confirm.** Trial on a throwaway issue before bulk-embedding across a real
  project; writes are not auto-approved.
- **Never emit secrets.** The token lives only in `.kiro/settings/atlassian.env`
  (git-ignored) and is used only in the `Authorization` header — never logged or printed.
- **Faithful.** One media node per image, inserted into the real ADF; existing content is
  preserved untouched.
