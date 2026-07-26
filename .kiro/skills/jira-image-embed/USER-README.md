# Jira Image Embed — user guide

Put images **inside** a Jira issue description, not just in the Attachments panel.
Built for dropping design mockups onto the tickets that implement them.

## Why it exists

The normal Jira tooling we use writes descriptions as markdown, and markdown can't
embed an attachment inline on Jira Cloud — it shows up as a broken image. This skill
writes the description as raw ADF (Atlassian's document format) with a proper image
node, which renders correctly. It also reads the existing description first and only
adds the image, so nothing else in the ticket is disturbed.

## What it does

Given an issue and one or more image files, it:

1. Attaches each image (reusing an existing attachment of the same name — no duplicates).
2. Embeds it inline in the description via an ADF image node pointing at the attachment.
3. Verifies the image actually persisted and renders (not a broken placeholder).

## Safe by default

- **Idempotent** — re-running doesn't duplicate the attachment or the embed.
- **Non-destructive** — it inserts into the existing description; it doesn't rewrite it.
- **Verified** — every embed is checked against the stored ADF and the rendered HTML.
- **No secrets** — the Jira token stays in `.kiro/settings/atlassian.env` (git-ignored).

## Using it

From the bundle root (`.kiro/skills/jira-image-embed`):

```
pip install -r requirements.txt
python -m pytest                     # engine correctness

# embed one mockup, with a heading, at the bottom of the description
python -m engine.embed SQP-4996 path/to/01-template-list.png --heading "Design mockup"

# preview without writing
python -m engine.embed SQP-4996 path/to/01-template-list.png --dry-run
```

Each line of output ends with `adf=True img=True` when the embed persisted and renders.

## Worth knowing

- Embedded mockups are a **snapshot** — they can drift from the build over time. The
  repo copy stays the source of truth.
- Only frontend tickets have mockups; backend tickets get none.
- If you ever see `img=False`, Jira may have hit its known inline-image bug for that
  write — re-check the ticket before relying on it.
