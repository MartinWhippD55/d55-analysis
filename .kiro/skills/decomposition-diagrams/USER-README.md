# Decomposition Diagrams — user guide

Add architecture diagrams to a decomposition's Jira issues: a small "what it builds /
where it's used" diagram on each story, and a service-interaction diagram on the epic —
each one **embedded inline at the top of the Jira description**, not just dropped in the
attachments panel.

Run it as the optional last step, after the issues have been pushed:

```
spec-to-stories → decomposition-to-jira → jira-tree → jira-push → decomposition-diagrams
```

## What it does

1. **Generates** baseline mermaid diagrams from `graph.yaml` — the per-story ones are
   accurate (components a story delivers, and the stories that consume it); the epic one
   is an overview you refine into the real runtime flow.
2. **Renders** them to crisp PNGs.
3. **Enriches** each Jira description with a short Architecture / Service-interaction
   section (mirrored into the editable tree first) and **embeds the diagram inline** at
   the top under an "Overview" heading — via the `jira-image-embed` skill, because
   markdown can't embed images on Jira Cloud.

## Why it's split from jira-push

`jira-push` owns creating the issues. This skill owns the optional visual polish on top,
so the push stays focused and the diagram/embed logic can be tested and re-run on its
own. It's safe to skip entirely.

## Using it

From the bundle root (`.kiro/skills/decomposition-diagrams`):

```
pip install -r requirements.txt
python -m pytest                                              # engine correctness

# 1. generate baseline .mmd from the decomposition
python -m engine.generate ../../specs/<parent>/decomposition

# 2. (agent) refine the epic diagram into the real runtime flow, tweak stories

# 3. render every .mmd -> .png
python -m engine.render ../../specs/<parent>/decomposition/diagrams

# 4. enrich descriptions (prose via MCP) then embed each PNG at the top:
#    from ../jira-image-embed:
python -m engine.embed <ISSUE_KEY> <diagrams>/<US-xx>.png --position top --heading "Overview"
```

Each embed prints `adf=True img=True` when the image persisted and renders.

## Safe by default

- **Idempotent** — attachments dedupe by filename, embeds by image URL; re-running adds
  nothing.
- **Non-destructive** — diagrams are inserted into the existing description; prose lands
  in the tree mirror first (the repo copy stays canonical).
- **Verified** — every embed is checked against the stored ADF and the rendered HTML.
- **No secrets** — the Jira token stays in `.kiro/settings/atlassian.env` (git-ignored).

## Worth knowing

- The epic's `graph.yaml` describes *build dependencies*, not the *runtime* sequence, so
  the epic diagram always needs a human pass to become the real service-interaction flow.
- Embedded diagrams are a **snapshot** — they can drift from the build. The `.mmd`
  sources in the repo are the source of truth; commit them alongside the PNGs.
- If an embed ever shows `img=False`, Jira may have hit its known inline-image bug for
  that write — re-check the ticket before relying on it.
