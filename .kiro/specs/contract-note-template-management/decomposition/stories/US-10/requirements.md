# Requirements Document

**Story US-10 — Integration wiring & end-to-end validation**

> Mini-spec derived from parent spec **contract-note-template-management**.
> Delivers user story **US-10**. See `manifest.yaml` for the component
> exports/dependencies and `../../graph.yaml` for the full delivery graph.

## Introduction

This story wires everything together into a deployable whole: the CDK deployment that
grants IAM, connects the S3 input event to the render state machine, binds the API
Gateway routes to their Lambda handlers and configures CORS; the Admin Portal sidebar
navigation entry (Cognito-gated); and the end-to-end tests that prove a dropped XML
produces a PDF and an invalid XML produces an error record with no output.

It is the final wave-6 story. It depends on the deployable units from the API stories,
the render pipeline and the frontend navigation. It exports the deployment itself.

## Glossary

- **Render_State_Machine**: The Step Functions state machine (US-06) triggered by S3.
- **Admin_Portal**: The existing BrytAdminPortal Angular application.
- **Deployment**: The CDK-provisioned, wired-together stack for the whole feature.

## Delivered components

This story is responsible for creating and owning:

- `cdk-instance:deployment` — the wired CDK deployment (IAM, S3 trigger, API routes,
  CORS, portal navigation) plus end-to-end validation

## Dependencies

This story depends on components delivered by other stories (must be available first):

- `lambda:template-handlers` (from US-02) — template API handlers to bind
- `lambda:section-handlers` (from US-03) — section API handlers to bind
- `lambda:variant-publish-handlers` (from US-04) — publish/variant handlers to bind
- `lambda:rules-handlers` (from US-05) — rules API handlers to bind
- `state-machine:RenderStateMachine` (from US-06) — the pipeline to trigger from S3
- `frontend-component:Navigation` (from US-09) — the portal navigation to expose

## Requirements

### Requirement 1: Deployment wiring  _(parent: Requirements 14, 20)_

**User Story:** As a developer, I want all components deployed and wired, so that the
feature works as a whole.

#### Acceptance Criteria

1. THE CDK deployment SHALL grant each Lambda and the Render_State_Machine least-privilege
   IAM for DynamoDB and S3. _(parent 14.1, 20.4)_
2. THE deployment SHALL connect the S3 input event so an XML drop starts a
   Render_State_Machine execution. _(parent 14.1, 20.4)_
3. THE deployment SHALL bind the API Gateway routes to the correct Lambda handlers and
   configure CORS for the Admin Portal origin. _(parent 14.1)_

### Requirement 2: Portal navigation  _(parent: Requirement 15)_

**User Story:** As a Business_User, I want a portal sidebar entry for contract note
templates, so that I can reach the feature.

#### Acceptance Criteria

1. THE Admin_Portal sidebar SHALL include a menu item linking to the template list route.
   _(parent 15.1)_
2. THE menu item's visibility SHALL be gated by Cognito group membership. _(parent 15.1, 15.3)_

### Requirement 3: End-to-end validation  _(parent: Requirement 14)_

**User Story:** As a developer, I want end-to-end tests of the pipeline, so that I can
trust the feature works across service boundaries.

#### Acceptance Criteria

1. WHEN a valid XML is dropped into the input bucket, THE end-to-end test SHALL verify a
   PDF appears in the output bucket. _(parent 14.1, 14.3)_
2. WHEN an invalid XML is dropped, THE end-to-end test SHALL verify an error record is
   written to the error bucket and no output PDF is produced. _(parent 14.4)_
