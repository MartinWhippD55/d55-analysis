---
issue_type: Epic
summary: contract-note-template-management (delivery)
epic_name: contract-note-template-management
identity_label: s2s-contract-note-template-management-epic
set_label: s2s-contract-note-template-management
labels:
- s2s-contract-note-template-management
- s2s-contract-note-template-management-epic
---

## Goal

Let Bryt Energy business users manage the PDF rendering templates for contract notes themselves, through the existing BrytAdminPortal — template CRUD, a visual section editor, shared/reusable sections (including T&Cs), a rules engine for automated template selection, and a render pipeline that renders sections independently and stitches them into a PDF. This is Estimate 1 of the Bryt Energy Contract Note Rework project.

## Background

Decomposed from spec `contract-note-template-management` by spec-to-stories. Today, contract note templates are produced through a developer-dependent SVG/HTML pipeline: every template or layout change is a code change. This epic replaces that with a visual, business-user-owned template management approach powered by pdf-me, removing developers from the loop for routine template edits.

## Scope

- In scope: the stories and waves below — template CRUD, section and shared-section editing, section version history and publishing, section variants, the template-selection rules engine, the Step Functions render pipeline, the pdf-me designer web component, the Angular admin screens, and the integration wiring with end-to-end validation.
- Out of scope: migrating or re-authoring existing contract note content into the new system; decommissioning the legacy SVG/HTML pipeline; changes to the contract data (XML) source or upstream systems that feed the render pipeline; and any Admin Portal capability outside contract note template management.

## Delivery plan

| Wave | Stories |
|------|---------|
| 1 | US-01, US-07 |
| 2 | US-02, US-03, US-05, US-06 |
| 3 | US-04 |
| 4 | US-08 |
| 5 | US-09 |
| 6 | US-10 |

## Stories

| Story | Summary | Est (days) |
|-------|---------|------------|
| US-01 | Foundation: infrastructure & shared types | 2.5 |
| US-02 | Template CRUD API | 1.5 |
| US-03 | Section, shared-section, version history & change log API | 2.0 |
| US-04 | Section version publishing & variants API | 1.0 |
| US-05 | Template selection rules API | 0.5 |
| US-06 | Render pipeline (Step Functions) | 3.0 |
| US-07 | pdf-me Designer web component | 1.0 |
| US-08 | Angular module, routing & services | 1.0 |
| US-09 | Angular screens & components | 3.0 |
| US-10 | Integration wiring & end-to-end validation | 1.0 |

_Total estimate: 16.5 days (excludes optional test sub-tasks)._

## Definition of done

- All 10 stories delivered.
- Parent requirements covered: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21.
