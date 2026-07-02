# Contract Note - API Specification

OpenAPI 3.1 specification for the BRYT Contract Note Admin Portal API.

## Files

| File | Description |
|------|-------------|
| `contract-note-api.yaml` | OpenAPI 3.1 spec. 26 paths, 38 operations, 35 schemas. |
| `contract-note-api.html` | Fully self-contained Redoc rendering — spec and runtime both inlined, no network needed. Just open it in a browser. |
| `build_html.py` | Regenerates the standalone HTML from the YAML (inlines the Redoc runtime + spec). |

## Scope

The spec documents the REST surface hosted behind the BrytAdminPortal API Gateway:

- **Estimate 1 - Template Management** — templates, sections, shared sections, selection rules, section version history, change log
- **Estimate 3b - Data Source Extensibility** — data source discovery and template attachment
- **Estimate 4 - Bespoke Contracts** — bespoke note CRUD, on-demand render, render history, manual DocuSign trigger
- **Estimate 2 - DocuSign** — the single public `POST /docusign-webhook` callback (HMAC-validated). The rest of Estimate 2 is event-driven (S3 + Lambda-to-Lambda), not a REST surface.

**Estimate 5 (Comparison Audit)** is intentionally excluded — it is a Step Function invoked with a JSON payload, not an HTTP API. Its input/finding shapes are documented in the walkthrough instead.

## Derivation and assumptions

Paths, methods, and most schemas are taken directly from the `.kiro/specs` design documents (endpoint tables + TypeScript interfaces). Where the specs describe behaviour in prose rather than concrete request/response bodies, reasonable shapes were inferred and marked with `ASSUMPTION:` in the spec descriptions. These should be confirmed with BRYT:

- A standard JSON error envelope (`Error` / `ValidationError`) is used for all non-2xx responses.
- Authentication is a Cognito-issued JWT bearer token, with access gated by Cognito group membership. The webhook uses HMAC instead.
- List endpoints are unpaginated in this phase (only the bespoke list has a `status` filter).
- The bespoke contract-data reference endpoint returns fields grouped by category.

## Validate

```
pip install openapi-spec-validator pyyaml
python -c "from openapi_spec_validator import validate_spec; import yaml; from pathlib import Path; validate_spec(yaml.safe_load(Path('analysis/BRYT/contract-note/api/contract-note-api.yaml').read_text(encoding='utf-8'))); print('valid')"
```

## View

The easiest option is to open `contract-note-api.html` directly in any browser — it is fully self-contained (spec + Redoc runtime inlined) and needs no server or internet connection.

To regenerate that HTML after editing the YAML:

```
pip install pyyaml
python analysis/BRYT/contract-note/api/build_html.py
```

The builder downloads the Redoc runtime once (cached locally as `_redoc.js`, gitignored) and inlines it along with the spec.

Alternatively, paste the YAML into [editor.swagger.io](https://editor.swagger.io), or preview with Redocly:

```
npx @redocly/cli preview-docs analysis/BRYT/contract-note/api/contract-note-api.yaml
```
