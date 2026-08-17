# Requirements Document

**Story US-08 — Integration wiring & deployment**

> Mini-spec derived from parent spec **contract-note-docusign-integration**.
> Delivers user story **US-08**. See `manifest.yaml` for the component
> exports/dependencies and `../../graph.yaml` for the full delivery graph.

## Introduction

This story assembles the pipeline: it wires the `DocuSignPipeline` construct into
`ContractNoteStack`, appends the `SendEnvelope` task to the render state machine after
`writeOutput` (with its own DocuSign-specific catch and retry/timeout), binds the webhook
route to the Webhook Lambda, sets environment variables, and finalises least-privilege IAM.

It is the final wave-4 story, depending on the two handlers (US-05 send, US-06 webhook) and
the Estimate 1 metadata passthrough (US-07). It is the point at which the pieces become a
running, deployable pipeline.

## Glossary

- **SendEnvelope task**: The `LambdaInvoke` task appended to the render state machine after
  `WriteOutput`, invoking the send Lambda.
- **DocuSign-specific catch**: A catch on the `SendEnvelope` task routing to a DocuSign
  failure handler (not the render `handleFailure`), so a send failure does not fail the
  render or discard the PDF.
- **ContractNoteStack**: The Estimate 1 CDK stack the DocuSign construct is wired into.

## Delivered components

This story is responsible for creating and owning:

- `cdk-instance:deployment` — the wired, deployable pipeline (construct in the stack,
  `SendEnvelope` task + catch, webhook route binding, env vars, IAM)

## Dependencies

This story depends on components delivered by other stories (must be available first):

- `lambda:send-envelope` (from US-05) — invoked by the `SendEnvelope` task
- `lambda:webhook` (from US-06) — bound to the webhook route
- `api-endpoint:POST /docusign-webhook` (from US-06) — the route being connected
- `state-machine:render-metadata-passthrough` (from US-07) — supplies the Contract_Metadata
  the `SendEnvelope` task passes to the send Lambda

## Requirements

### Requirement 1: SendEnvelope task wiring with isolated failure handling  _(parent: Requirement 1)_

**User Story:** As a system operator, I want signing wired into the render pipeline without
letting e-signature failures fail the render.

#### Acceptance Criteria

1. THE render state machine SHALL invoke the send Lambda via a `SendEnvelope`
   `LambdaInvoke` task appended after `WriteOutput`, passing the render output location and
   Contract_Metadata in the state payload. _(parent 1.1)_
2. THE `SendEnvelope` task SHALL have its own catch routing to a DocuSign-specific failure
   handler (not the render `handleFailure`), so the render execution stays successful and
   the produced PDF is retained. _(parent 1.4)_
3. THE `SendEnvelope` task SHALL have its own retry/timeout so it does not consume the
   render execution's budget. _(parent 1.4)_

### Requirement 2: Webhook route and deployment  _(parent: Requirements 6, 11)_

**User Story:** As a system operator, I want the whole pipeline deployed via CDK following
the repo conventions.

#### Acceptance Criteria

1. THE API Gateway `POST /docusign-webhook` route SHALL be connected to the Webhook Lambda. _(parent 6.1)_
2. THE Lambda functions SHALL have least-privilege IAM permissions for the DynamoDB table,
   the signed-documents and reused error buckets, and the Secrets Manager secrets they
   require. _(parent 11.6)_
3. THE Lambda environment variables (table name, bucket names, webhook URL, secret ARNs)
   SHALL follow the `NodejsFunction` environment pattern used by `RenderPipeline`, and the
   construct SHALL be wired into `ContractNoteStack`. _(parent 11.3)_
