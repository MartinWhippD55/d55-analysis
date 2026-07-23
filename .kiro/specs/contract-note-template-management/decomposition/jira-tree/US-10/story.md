---
issue_type: Story
key: US-10
summary: Integration wiring & end-to-end validation
parent_epic: contract-note-template-management
identity_label: s2s-contract-note-template-management-US-10
labels:
- s2s-contract-note-template-management
- s2s-contract-note-template-management-US-10
- infra
- integration
estimate_days: 1.0
covers_requirements:
- '14'
- '15'
- '20'
wave: 6
depends_on:
- US-02
- US-03
- US-04
- US-05
- US-06
- US-09
blocks: []
---

As a developer, I want all components deployed and wired (IAM, S3 trigger, API Gateway, portal navigation) with end-to-end tests, so that the feature works as a whole.

## Description

This is the terminal wave-6 integration story. It builds no new functionality; it provisions the CDK deployment that ties everything together and proves the assembled feature works. Specifically it grants least-privilege IAM to each Lambda and the render state machine, wires the S3 input-bucket event to start a render execution, binds API Gateway routes to their Lambda handlers and configures CORS for the Admin Portal origin, and adds the Cognito-gated portal sidebar entry that links to the template list.

It sits over the outputs of every other story and is the terminal node of the delivery graph — nothing depends on it. Completing it means the whole parent spec is delivered. It consumes `lambda:template-handlers` (US-02), `lambda:section-handlers` (US-03), `lambda:variant-publish-handlers` (US-04) and `lambda:rules-handlers` (US-05) as API routes; starts `state-machine:RenderStateMachine` (US-06) from the S3 event; and surfaces `frontend-component:Navigation` (US-09) in the sidebar. It covers parent requirements 14 (S3-triggered processing), 15 (authentication and authorisation) and 20 (render orchestration).

## Delivers

- `cdk-instance:deployment` — the wired-together CDK stack for the whole feature: least-privilege IAM for every Lambda and the render state machine, the S3 input-event trigger, API Gateway route-to-handler bindings, CORS for the Admin Portal origin, and the Cognito-gated portal sidebar navigation entry.
- CDK synth/assertion tests covering the IAM grants, the S3 notification wiring, the route-to-handler bindings and the CORS configuration.
- End-to-end integration tests exercising the full pipeline: valid XML in produces a PDF in the output bucket; invalid XML in produces an error record in the error bucket and no output PDF (parent Property 27 / Property 38).

## Acceptance criteria

- **Given** the deployed stack, **when** it is synthesised/deployed, **then** each Lambda and the `RenderStateMachine` is granted least-privilege IAM for its required DynamoDB and S3 access, and misconfigured IAM fails the deployment fast rather than publishing a partially wired stack (parent 14.1, 20.4).
- **Given** the configured S3 input bucket, **when** an XML file is dropped into it, **then** the deployment's S3 notification / EventBridge wiring starts a `RenderStateMachine` execution (parent 14.1, 20.4).
- **Given** API Gateway, **when** the stack is deployed, **then** each route is bound to the correct Lambda handler (template, section, variant-publish and rules handlers) and CORS is configured for the Admin Portal origin so portal requests pass preflight (parent 14.1).
- **Given** the Admin Portal sidebar, **when** an authenticated user with the required Cognito group membership views it, **then** it shows a menu item linking to the template list route; the item's visibility is gated by Cognito group membership (parent 15.1, 15.3).
- **Given** a valid XML input, **when** it is dropped into the input bucket, **then** the end-to-end test verifies a PDF appears in the output bucket (parent 14.1, 14.3).
- **Given** an invalid XML input, **when** it is dropped into the input bucket, **then** the end-to-end test verifies an error record is written to the error bucket and no output PDF is produced (parent 14.4, Property 27).

## Dependencies

- US-02 — Template CRUD API
- US-03 — Section, shared-section, version history & change log API
- US-04 — Section version publishing & variants API
- US-05 — Template selection rules API
- US-06 — Render pipeline (Step Functions)
- US-09 — Angular screens & components

## Traceability

Covers parent requirements: 14, 15, 20 · `s2s-contract-note-template-management-US-10`
