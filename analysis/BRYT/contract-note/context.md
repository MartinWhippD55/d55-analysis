# BRYT Contract Note - Project Context

## What is this?

A rework of the BRYT Energy contract note system. BRYT is an energy supplier; contract notes are the PDF documents produced when a customer signs up to an energy contract. The current system is developer-dependent and inflexible — the goal is to make it self-service for business users.

## The 5 Estimates

Each estimate is an independently-specced piece of work. They build on each other sequentially:

| # | Name | Folder | What it does |
|---|------|--------|--------------|
| 1 | PDF / T&Cs Rework | `1-pdf-me/` | Template management UI + pdf-me editor + rules engine + render pipeline. Replaces the current SVG/HTML renderer. |
| 2 | DocuSign Integration | `2-docusign/` | Take the rendered PDF from Est 1, send to DocuSign for e-signature, email to customer, store signed copy back in Salesforce. |
| 3 | Training & Templates | `3-training/` | Training budget, new templates, changing existing templates, new data sources. Operational enablement. |
| 4 | Bespoke Contracts | `4-bespoke-contract/` | Handle bespoke/custom contracts with unique T&Cs, auditing, avoid manual PDF editing. |
| 5 | System Comparison | `5-comparison/` | Compare current system output vs new system output. Regression/validation testing. |

## Existing Systems

### Admin Portal (BrytAdminPortal)
- Angular frontend + AWS Lambda backend + CDK infrastructure
- Auth: Cognito with role-based groups
- Hosts: CMS, communications, contact management, market papers, optimisation modules
- **This is where all new UI screens live**

### Contract Note V2 (BrytContractNote/contract-note-v2)
- Current pipeline being replaced by Estimate 1
- Step Functions: S3 XML drop → xml-to-json (enrichment) → CreateHtml (.NET SVG engine) → html-to-pdf → S3 output
- Triggered by XML files arriving in S3 (from upstream systems like Phidex/Ensek)
- Heavy enrichment logic: pricing calculations, MPAN processing, address building, charge types, pass-through handling

### PDF PoC (PDF-PoC)
- Proof of concept using @pdfme/generator + pdf-lib
- Proved: pdf-me works for Bryt's needs, Designer can be embedded, sections can be stitched
- Known limitations: expressions need templating engine, page breaks with tables need section approach

## Key Decisions Made in Estimate 1

1. **Templates = ordered sections** — each template is composed of multiple sections, rendered independently and stitched together with pdf-lib
2. **Shared sections** — reusable across templates (header, footer, T&Cs). T&Cs are just shared sections positioned at the end, not a special upload mechanism
3. **Specification pattern for rules** — JSON tree with AND/OR/NOT logical operators and EQUALS/LESS_THAN/MORE_THAN/IN comparison leaf nodes. First-match-wins evaluation against template priority order.
4. **pdf-me Designer via Web Component** — React component wrapped as a custom element, embedded in Angular via modal
5. **DynamoDB single-table** — templates, sections, shared sections, rules all in one table with PK/SK patterns
6. **Render pipeline = single Lambda** — replaces the current multi-step Step Function approach

## Estimate 2 - DocuSign (Raw Notes)

From initial brief:
- Contract note produced (by Estimate 1's render pipeline)
- Take PDF out to DocuSign
- Email to customer
- When signed, store the signed contract and attach to Salesforce account

### Key Questions Still to Explore:
- Does BRYT already have a DocuSign account/API credentials?
- What Salesforce objects does the signed contract attach to? (Account? Opportunity? Custom object?)
- Is the email sent by DocuSign directly, or does BRYT want to control the email template/branding?
- What triggers the DocuSign flow? Automatic after PDF render, or manual approval step?
- How do we handle signing status tracking? (Sent, viewed, signed, declined, expired)
- Where does the signed PDF get stored in AWS before/alongside Salesforce?
- Are there multiple signatories? (Customer + Bryt + TPI in some cases based on the current system)

## Key Identifiers

- **BrytNumber** = `customerreference` field in the contract data payload (e.g., "BRYT002618"). Unique customer identifier shared across BRYT's external services (Salesforce, Ensek, etc.). Used as the join key for data source enrichment.
- **customersalesforceref** = Salesforce record reference for the customer (e.g., "432"). Used for DocuSign flow (Estimate 2) to look up contact details and attach signed documents.

## Reference Repos

Available at `reference-repos/` (gitignored, local only):
- `BrytAdminPortal/` — Angular portal + Lambda APIs + CDK
- `BrytContractNote/` — current pipeline (contract-note-v2)
- `PDF-PoC/` — pdf-me proof of concept
- `BrytBusinessServices/` — business services API + CDK + shared lib (TypeScript monorepo)

## Working Style

- Specs follow the .kiro/specs structure (requirements → design → tasks)
- Wireframe mockups as HTML (Architects Daughter font, sketchy style) + PNG screenshots
- Progress tracked in `analysis/BRYT/contract-note/progress.md`
- We work through estimates sequentially, one at a time
