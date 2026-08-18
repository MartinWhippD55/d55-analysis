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

## Service interaction

End-to-end runtime flow: the render pipeline (US-07) hands the contract PDF and `Contract_Metadata` to the Send Envelope Lambda (US-05), which looks up the contact (US-02), creates the envelope (US-03), and stores the record (US-04). DocuSign emails the customer for signature; the Connect callback hits the Webhook Lambda (US-06), which validates the HMAC, downloads the signed PDF, stores it in the signed bucket (US-01), uploads it to Salesforce, and updates status — routing declined/expired/failures to the reused error bucket (US-01). US-08 wires the `SendEnvelope` task and webhook route together.

See the attached `epic-service-interaction.png`, annotated with the delivering story (US-xx / SQP key) for each participant.

## What to ask Bryt for

External access and credentials this epic depends on Bryt (the client) to provide. None of it blocks initial development — the team can build against D55's own DocuSign developer (demo) account and a Salesforce dev org — but the client-provided sandboxes are needed for UAT, and a few items (JWT consent, DocuSign go-live) have lead time, so raise them early.

**Simon Farrimond or Stephen Perrins** are the people to check with internally about the Salesforce environment — they should know whether Bryt already has a sandbox and how to arrange access.

### DocuSign (US-03)

- Access to Bryt's DocuSign **sandbox/demo account** — either admin access so we create the app and keys, or the credential bundle created for us.
- A dedicated **system/service user** for the integration to impersonate (not a named person).
- The JWT credential bundle → Secrets Manager `{resourcePrefix}contract-note/docusign`: Integration Key, RSA private key, impersonated user GUID, account ID, auth server.
- **JWT admin consent** for the signature-impersonation scope (one-time, org-wide or per-user) — the most common first-call blocker.
- A **Connect HMAC key** created in their account, secret shared to us for webhook validation (US-06).
- **Production go-live** sponsorship — DocuSign requires ~20 successful demo API calls plus a review to promote the integration key to production.
- Confirm the eSignature plan has **API access** enabled.

### Salesforce (US-02)

- Access to Bryt's **Salesforce sandbox** — check internally with Simon Farrimond / Stephen Perrins whether one already exists, then arrange access.
- A **Connected App** for the OAuth client-credentials flow (consumer key + secret) → Secrets Manager `{resourcePrefix}contract-note/salesforce`, plus the instance URL and token URL.
- A dedicated **integration user** the Connected App runs as, with permission to query the customer record and create Files (ContentVersion / ContentDocumentLink).
- The **object/field mapping**: which object `customersalesforceref` resolves to, and where the signed PDF should be attached.

### Lead-time items to raise now

- DocuSign JWT consent grant and production go-live review (both gated, not instant).
- Whether the Salesforce sandbox is a full/partial-copy sandbox with representative contact data for UAT.
