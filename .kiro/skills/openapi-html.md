---
inclusion: manual
---

# OpenAPI HTML

Where a spec defines an API surface, produce an OpenAPI 3.1 YAML plus a **fully self-contained** HTML reference (spec + rendering runtime both inlined, opens offline in any browser). Reference: `analysis/BRYT/contract-note/api/` (`contract-note-api.yaml`, `build_html.py`).

Read `deliverables-toolkit` first.

## Steps

### Step 1: Derive the spec

1. From the design docs, pull the endpoint tables (method, path, purpose) and the TypeScript/interface definitions (→ component schemas).
2. Write an OpenAPI 3.1 YAML: `paths` grouped by `tags`, reusable `components` (schemas, parameters, responses, security schemes).
3. Where the design describes behaviour in prose rather than concrete request/response bodies, infer reasonable shapes and mark each with `ASSUMPTION:` in the description so the client can confirm.
4. Model a standard error envelope, a security scheme (e.g. bearer/Cognito), and any recurring responses (401/403/404/409/validation) once and `$ref` them.
5. Combine related specs into one document where they share a gateway; keep genuinely separate surfaces (e.g. a public webhook) as their own tagged section with its own security scheme.

### Step 2: Handle recursive / oneOf schemas

Tools cannot auto-generate examples for recursive `oneOf` schemas and fall back to `"string"` placeholders. Add an explicit `example` (a realistic nested payload) to the recursive schema **and** to each node type, so the rendered docs show real payloads.

### Step 3: Validate

Validate with `openapi-spec-validator` (`pip install openapi-spec-validator`). Also confirm every local `$ref` resolves and count paths/operations/schemas as a sanity check.

### Step 4: Build the self-contained HTML

The key gotcha: Redocly's `build-docs` still links its runtime from a CDN, so that output is **not** offline. Instead, write a small `build_html.py` that:

1. Loads the YAML and inlines it as a JSON object in the page.
2. Downloads the Redoc standalone runtime once (cache it locally, gitignored) and inlines it in a `<script>`.
3. Initialises Redoc against the inlined spec.

Result: one HTML file with **zero external references**.

### Step 5: Verify

Serve on localhost, load in the browser, and confirm: title correct, operation count matches, zero parse errors, and — crucially — grep the file for external `src=`/`href=` http refs (should be none). Spot-check that a recursive-schema endpoint shows a real nested example, not `"string"`.

## Notes

- Exclude from the offline check the cosmetic `example.com` placeholders that Redoc emits; only script/style/runtime refs matter.
- Keep an `api/README.md` documenting scope, assumptions, and how to validate/regenerate.
