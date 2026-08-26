# PR #462 — Contract Note Templates Admin UI

## Metadata

| Field | Value |
|-------|-------|
| Title | sqp-4962 |
| Author | Jabez Souttar (Bezll) |
| State | OPEN |
| Base | `dev` |
| Head | `sqp-4962` |
| Created | 2026-08-26 |
| Files changed | 71 |
| Additions | 11,964 |
| Deletions | 166 |
| URL | https://github.com/d55ltd/BrytAdminPortal/pull/462 |

## Description

Adds the admin portal UI for managing contract note templates and shared sections.

Includes:
- Contract note template list and edit screens
- Section designer integration using pdfme
- Shared section library and picker
- Section version history, publish/revert flow, and linked template handling
- Conditional section variants and rule configuration UI
- Template preview PDF action
- Section copy flow with custom naming
- Bundled Noto Sans fonts for in-state rendering
- Contract note route protection via Cognito group guard

The contract notes area is gated behind the intended Cognito group assignment for admin users.
Shared sections are treated as reusable loose templates: pulled into a template then iterated independently.

## Existing Review Feedback

None — no comments, no reviews at time of fetch.

## Changed Files by Area

### Build / dependencies
| File | Status | +/- |
|------|--------|-----|
| portal/package.json | modified | +14/-4 |
| portal/package-lock.json | modified | +2714/-160 |
| portal/scripts/patch-pdfme-ui.mjs | added | +47 |

### Routing / access control
| File | Status | +/- |
|------|--------|-----|
| portal/src/app/app-routing.module.ts | modified | +10/-1 |
| portal/src/app/components/contract-notes/contract-note.module.ts | added | +72 |
| portal/src/app/components/contract-notes/contract-note.routes.ts | added | +53 |
| portal/src/app/components/contract-notes/contract-note.routes.spec.ts | added | +45 |
| portal/src/app/components/contract-notes/contract-note-group-guard.service.ts | added | +42 |
| portal/src/app/components/contract-notes/contract-note-group-guard.service.spec.ts | added | +72 |
| portal/src/app/components/contract-notes/access-denied/access-denied.component.ts | added | +8 |
| portal/src/app/components/contract-notes/access-denied/access-denied.component.html | added | +7 |
| portal/src/app/components/home/home.component.html | modified | +13/-1 |
| portal/src/environments/environment.ts | modified | +1 |

### Services
| File | Status | +/- |
|------|--------|-----|
| services/template.service.ts | added | +74 |
| services/template.service.spec.ts | added | +167 |
| services/section.service.ts | added | +134 |
| services/section.service.spec.ts | added | +100 |
| services/rules.service.ts | added | +28 |
| services/rules.service.spec.ts | added | +64 |

### Models
| File | Status | +/- |
|------|--------|-----|
| models/contract-note.models.ts | added | +194 |

### Components (major)
| File | Status | +/- |
|------|--------|-----|
| template-edit/template-edit.component.ts | added | +760 |
| template-edit/template-edit.component.spec.ts | added | +522 |
| template-list/template-list.component.ts | added | +183 |
| rules-config/rules-config.component.ts | added | +805 |
| shared-sections/shared-sections.component.ts | added | +295 |
| section-version-history/section-version-history.component.ts | added | +245 |
| section-editor/section-editor.component.ts | added | +213 |
| section-variants/section-variants.component.ts | added | +196 |
| section-publish/section-publish.component.ts | added | +145 |
| shared-section-picker/shared-section-picker.component.ts | added | +42 |
| copy-section-dialog/copy-section-dialog.component.ts | added | +44 |
| example-contract-data/example-contract-data.component.ts | added | +55 |
| navigation/contract-note-navigation.component.ts | added | +27 |

### pdfme web component
| File | Status | +/- |
|------|--------|-----|
| web-components/pdfme-designer/pdfme-designer.element.ts | added | +569 |
| web-components/pdfme-designer/pdfme-designer.element.spec.ts | added | +432 |
| web-components/pdfme-designer/index.ts | added | +1 |

### Assets
| File | Status | +/- |
|------|--------|-----|
| assets/contract-notes/example-contract-data.json | added | +62 |
| assets/contract-notes/fonts/noto-sans-latin-400-normal.woff2 | added | binary |
| assets/contract-notes/fonts/noto-sans-latin-700-normal.woff2 | added | binary |

(Plus HTML/SASS templates for each component — reviewed alongside their `.ts`.)
