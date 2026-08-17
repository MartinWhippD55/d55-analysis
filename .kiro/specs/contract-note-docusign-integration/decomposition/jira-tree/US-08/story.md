---
issue_type: Story
key: US-08
summary: Integration wiring & deployment
parent_epic: contract-note-docusign-integration
identity_label: s2s-contract-note-docusign-integration-US-08
labels:
- s2s-contract-note-docusign-integration
- s2s-contract-note-docusign-integration-US-08
- infra
- integration
estimate_days: 1.5
covers_requirements:
- '1'
- '6'
- '11'
wave: 4
depends_on:
- US-05
- US-06
- US-07
blocks: []
---

As a system operator, I want the DocuSign construct wired into the stack, the SendEnvelope task appended to the render state machine with its own catch, and the webhook route connected, so that the whole pipeline deploys and runs end to end.

## Description

The final wave-4 assembly story. It wires the `DocuSignPipeline` construct into
`ContractNoteStack`, appends the `SendEnvelope` `LambdaInvoke` task to the render state
machine after `WriteOutput`, binds the webhook route to the Webhook Lambda, sets the Lambda
environment variables, and finalises least-privilege IAM. No new runtime component is
introduced — this is the point where the parts built in US-05 (send Lambda), US-06 (webhook
Lambda + route) and US-07 (Contract_Metadata passthrough) become a running, deployable
pipeline. It depends on US-05, US-06 and US-07 being complete.

## Delivers

- `cdk-instance:deployment` — the wired, deployable pipeline: the `DocuSignPipeline`
  construct in `ContractNoteStack`, the `SendEnvelope` task with its own catch and
  retry/timeout, the webhook route binding, env vars, and least-privilege IAM.

## Acceptance criteria

- **Given** the render state machine, **when** it is defined, **then** a `SendEnvelope`
  `LambdaInvoke` task is appended after `WriteOutput`, passing the render output location and
  Contract_Metadata to the send Lambda.
- **Given** the `SendEnvelope` task, **when** it fails, **then** its own DocuSign-specific
  catch routes the failure to a DocuSign failure handler (not the render `handleFailure`),
  so the render execution stays successful and the produced PDF is retained.
- **Given** the `SendEnvelope` task, **when** it runs, **then** it uses its own retry and
  timeout so it does not consume the render execution's budget.
- **Given** the API Gateway, **when** the stack is deployed, **then** the
  `POST /docusign-webhook` route is connected to the Webhook Lambda.
- **Given** the Lambda functions, **when** IAM is finalised, **then** each has
  least-privilege permissions for the DynamoDB table, the signed-documents and reused error
  buckets, and the Secrets Manager secrets it requires.
- **Given** the Lambda environment variables (table name, bucket names, webhook URL, secret
  ARNs), **when** they are configured, **then** they follow the `NodejsFunction` environment
  pattern used by `RenderPipeline` and the construct is wired into `ContractNoteStack`.

## Dependencies

- US-05 — Send Envelope Lambda
- US-06 — Webhook Lambda (completion + declined/expired)
- US-07 — Estimate 1 metadata surfacing (Requirement 12)

## Traceability

Covers parent requirements: 1, 6, 11 · `s2s-contract-note-docusign-integration-US-08`
