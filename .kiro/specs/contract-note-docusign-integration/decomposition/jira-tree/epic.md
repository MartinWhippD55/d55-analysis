---
issue_type: Epic
summary: contract-note-docusign-integration (delivery)
epic_name: contract-note-docusign-integration
identity_label: s2s-contract-note-docusign-integration-epic
set_label: s2s-contract-note-docusign-integration
labels:
- s2s-contract-note-docusign-integration
- s2s-contract-note-docusign-integration-epic
---

## Goal

Deliver Estimate 2 of the Bryt Energy Contract Note Rework: a fully automated, headless
DocuSign e-signature pipeline. It takes the rendered contract note PDF from Estimate 1,
sends it to the customer for electronic signature via DocuSign, and stores the signed
copy back in S3 and Salesforce — with no Admin Portal UI and no manual intervention.

## Background

Decomposed from spec `contract-note-docusign-integration` by spec-to-stories. Estimate 1
produced the render pipeline that generates contract note PDFs; today those PDFs still
have to be sent for signature and filed by hand. This epic closes that loop. It is
delivered inside the `BrytBusinessServices` monorepo (api / cdk / shared-lib), following
the conventions Estimate 1's backend established.

## Scope

- In scope: the stories and waves below — DocuSign JWT auth + envelope creation, a
  greenfield Salesforce client (lookup + signed-doc upload), a `docusign-envelopes`
  metadata table, the send and webhook Lambdas, the reused error bucket, and the
  `SendEnvelope` task appended to Estimate 1's render state machine.
- Out of scope: an Admin Portal UI; the `voided` envelope status; any change to
  Estimate 1's render logic beyond surfacing the customer reference (US-07 /
  Requirement 12, coordinated with Jabez).

## Delivery plan

| Wave | Stories |
|------|---------|
| 1 | US-01, US-07 |
| 2 | US-02, US-03, US-04 |
| 3 | US-05, US-06 |
| 4 | US-08 |

## Stories

| Story | Summary |
|-------|---------|
| US-01 | Foundation: DocuSign pipeline infra, shared types & utilities |
| US-02 | Salesforce integration client (greenfield) |
| US-03 | DocuSign integration client |
| US-04 | Envelope metadata service |
| US-05 | Send Envelope Lambda |
| US-06 | Webhook Lambda (completion + declined/expired) |
| US-07 | Estimate 1 metadata surfacing (Requirement 12) |
| US-08 | Integration wiring & deployment |

## Definition of done

- All 8 stories delivered.
- Parent requirements covered: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12.
