# PR #520: sqp-4808 Data Orchestration Rework

## Metadata

| Field | Value |
|---|---|
| URL | https://github.com/d55ltd/BrytDataEngineering/pull/520 |
| Author | StephenPerrinsD55 |
| State | OPEN |
| Base | `dev-esg` ← `sqp-4808` |
| Created | 2026-05-13 09:31 UTC |
| Stats | +16,824 / -10,464 across 186 files |

## Description

> This PR
> - completely reworks data orchestration
> - explodes master-record json blobs into separate columns (but keeps the blobs for compatibility with downstream consumers)
>
> It's big. There's an architecture diagram, there are a few moving parts. Talk to Stephen if it's opaque

## Comments

### MartinWhippD55 (2026-05-13 10:09 UTC)

> Additional context from SP on what's been done as part of this PR:
>
> - glue jobs for CS, Phidex and SF all parameterized
> - cut Ensek out of orchestration
> - partition tracking via S3 events, with some nuance for "stuff arriving within the same hour but after an orchestration run"
> - orchestration only runs what it needs to run
> - master record only kicks off if dependencies updated
> - exploded out the data json in master record into separate columns, but kept it to avoid downstream updates and full table rewrites
> - crawlers run once a week to pick up schema updates, if there are any then there's a lambda that reacts to the table update and marks the last week's partitions as unprocessed so they get re-merged into staging
>
> you may also find queries/partition-activity-results.csv interesting (the result of a 15 minute runtime athena query)

## Changed Files

| # | File | Status | +/- |
|---|---|---|---|
| 1 | `.kiro/specs/crawler-schema-change-reprocessing/.config.kiro` | added | +1/-0 |
| 2 | `.kiro/specs/crawler-schema-change-reprocessing/design.md` | added | +517/-0 |
| 3 | `.kiro/specs/crawler-schema-change-reprocessing/requirements.md` | added | +131/-0 |
| 4 | `.kiro/specs/crawler-schema-change-reprocessing/tasks.md` | added | +174/-0 |
| 5 | `.kiro/specs/data-orchestration-refactor/.config.kiro` | added | +1/-0 |
| 6 | `.kiro/specs/data-orchestration-refactor/design.md` | added | +612/-0 |
| 7 | `.kiro/specs/data-orchestration-refactor/requirements.md` | added | +111/-0 |
| 8 | `.kiro/specs/data-orchestration-refactor/tasks.md` | added | +239/-0 |
| 9 | `.kiro/specs/master-record-schema-explosion/.config.kiro` | added | +1/-0 |
| 10 | `.kiro/specs/master-record-schema-explosion/design.md` | added | +630/-0 |
| 11 | `.kiro/specs/master-record-schema-explosion/requirements.md` | added | +141/-0 |
| 12 | `.kiro/specs/master-record-schema-explosion/tasks.md` | added | +185/-0 |
| 13 | `.kiro/steering/project-conventions.md` | added | +7/-0 |
| 14 | `cdk/jest.config.js` | added | +8/-0 |
| 15 | `cdk/lib/config/dependency-map.json` | added | +108/-0 |
| 16 | `cdk/lib/config/dependency-map.test.ts` | added | +284/-0 |
| 17 | `cdk/lib/config/dependency-map.ts` | added | +112/-0 |
| 18 | `cdk/lib/config/table-config.test.ts` | added | +76/-0 |
| 19 | `cdk/lib/config/table-config.ts` | added | +97/-0 |
| 20 | `cdk/lib/config/tables/centrestage.json` | added | +57/-0 |
| 21 | `cdk/lib/config/tables/phidex.json` | added | +34/-0 |
| 22 | `cdk/lib/resources/data-orchestration/data-orchestration.ts` | added | +417/-0 |
| 23 | `cdk/lib/resources/dms/centrestage.ts` | modified | +7/-62 |
| 24 | `cdk/lib/resources/dms/phidex.ts` | modified | +11/-51 |
| 25 | `cdk/lib/resources/dynamodb/partition-tracker.ts` | added | +46/-0 |
| 26 | `cdk/lib/resources/event-bridge/schema-change-rule.ts` | added | +45/-0 |
| 27 | `cdk/lib/resources/glue/etl/cdc-staging-generic.ts` | added | +282/-0 |
| 28 | `cdk/lib/resources/glue/etl/cdc-staging-jira.ts` | added | +221/-0 |
| 29 | `cdk/lib/resources/glue/etl/cdc-staging.ts` | removed | +0/-779 |
| 30 | `cdk/lib/resources/glue/etl/jobs.ts` | modified | +6/-4 |
| 31 | `cdk/lib/resources/glue/etl/lake-formation.ts` | modified | +9/-8 |
| 32 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-bryt/payment.py` | removed | +0/-101 |
| 33 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-bryt/refund.py` | removed | +0/-101 |
| 34 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-bryt/staging.py` | added | +245/-0 |
| 35 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/afmse-meter-register-reading.py` | removed | +0/-99 |
| 36 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/afmse-meter-register.py` | removed | +0/-99 |
| 37 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/afmse-meter.py` | removed | +0/-99 |
| 38 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/afmse-mpan.py` | removed | +0/-99 |
| 39 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/billing-wide.py` | removed | +0/-107 |
| 40 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/bol-xread-out-01-active-import-profile-data.py` | removed | +0/-102 |
| 41 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/bol-xread-out-01-meter.py` | removed | +0/-101 |
| 42 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/dcc-bol-device.py` | removed | +0/-99 |
| 43 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/meter_mhhs.py` | removed | +0/-99 |
| 44 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/meter_register_reading_mhhs.py` | removed | +0/-99 |
| 45 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/mpan_mhhs.py` | removed | +0/-99 |
| 46 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/staging.py` | added | +270/-0 |
| 47 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-address.py` | removed | +0/-99 |
| 48 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-allocation.py` | removed | +0/-99 |
| 49 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-constant-customer-supply-status.py` | removed | +0/-99 |
| 50 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-constant-payment-method.py` | removed | +0/-99 |
| 51 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-constant-payment-status.py` | removed | +0/-99 |
| 52 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-constant-refund-method.py` | removed | +0/-99 |
| 53 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-constant-tpr.py` | removed | +0/-99 |
| 54 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-contract.py` | removed | +0/-99 |
| 55 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-customer-contact.py` | removed | +0/-99 |
| 56 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-customer-note-attachment.py` | removed | +0/-99 |
| 57 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-customer-note-history.py` | removed | +0/-99 |
| 58 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-customer-note.py` | removed | +0/-99 |
| 59 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-customer-supply.py` | removed | +0/-99 |
| 60 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-customer.py` | removed | +0/-99 |
| 61 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-document-data.py` | removed | +0/-99 |
| 62 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-generated-document.py` | removed | +0/-99 |
| 63 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-invoice-billing-header-raw-data.py` | removed | +0/-99 |
| 64 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-invoice-billing-raw-data.py` | removed | +0/-99 |
| 65 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-invoice-crm-data.py` | removed | +0/-99 |
| 66 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-invoice-detail-note.py` | removed | +0/-99 |
| 67 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-invoice-detail.py` | removed | +0/-99 |
| 68 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-lookup-measurement-class.py` | removed | +0/-99 |
| 69 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-lookup-meter-type.py` | removed | +0/-99 |
| 70 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-lookup-profile-class.py` | removed | +0/-99 |
| 71 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-meter-electricity.py` | removed | +0/-99 |
| 72 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-meter.py` | removed | +0/-99 |
| 73 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-mpan-billing-raw-data.py` | removed | +0/-99 |
| 74 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-payment-association-map.py` | removed | +0/-99 |
| 75 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-payment-crm-data.py` | removed | +0/-99 |
| 76 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-payment.py` | removed | +0/-110 |
| 77 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-refund-association-map.py` | removed | +0/-99 |
| 78 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-refund.py` | removed | +0/-99 |
| 79 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-register-electricity.py` | removed | +0/-99 |
| 80 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-register.py` | removed | +0/-99 |
| 81 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-site-billing-raw-data.py` | removed | +0/-99 |
| 82 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-site-crm-data.py` | removed | +0/-99 |
| 83 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-site.py` | removed | +0/-99 |
| 84 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-supply-contact.py` | removed | +0/-99 |
| 85 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-supply-contract.py` | removed | +0/-99 |
| 86 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-supply-electricity.py` | removed | +0/-145 |
| 87 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-supply-registration-history.py` | removed | +0/-99 |
| 88 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium-supply.py` | removed | +0/-99 |
| 89 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium_contact.py` | removed | +0/-99 |
| 90 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-centrestage/titanium_sitecontact.py` | removed | +0/-99 |
| 91 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-ensek/readings.py` | removed | +0/-76 |
| 92 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-ensek/registers.py` | removed | +0/-76 |
| 93 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-ensek/staging.py` | added | +241/-0 |
| 94 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-jira/issue-type.py` | modified | +0/-2 |
| 95 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-jira/issue.py` | modified | +0/-2 |
| 96 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-jira/project-category.py` | modified | +0/-2 |
| 97 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-jira/project-type.py` | modified | +1/-3 |
| 98 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-jira/project.py` | modified | +0/-2 |
| 99 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-jira/user.py` | modified | +2/-4 |
| 100 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-jira/workflow-status-category.py` | modified | +4/-18 |
| 101 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-jira/workflow-status.py` | modified | +4/-18 |
| 102 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-phidex/billing-contract-document.py` | removed | +0/-99 |
| 103 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-phidex/billing-contract-meter.py` | removed | +0/-99 |
| 104 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-phidex/billing-contract-mpan-line.py` | removed | +0/-99 |
| 105 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-phidex/billing-contract-mpan-rate.py` | removed | +0/-102 |
| 106 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-phidex/billing-contract-mpan-read.py` | removed | +0/-99 |
| 107 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-phidex/billing-contract-mpan-volume.py` | removed | +0/-100 |
| 108 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-phidex/billing-contract-mpan.py` | removed | +0/-101 |
| 109 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-phidex/billing-contract-register.py` | removed | +0/-99 |
| 110 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-phidex/billing-contract-site.py` | removed | +0/-99 |
| 111 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-phidex/billing-contract.py` | removed | +0/-99 |
| 112 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-phidex/billing-customer.py` | removed | +0/-99 |
| 113 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-phidex/billing-group.py` | removed | +0/-99 |
| 114 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-phidex/billing-invoice-document.py` | removed | +0/-109 |
| 115 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-phidex/billing-invoice-error.py` | removed | +0/-99 |
| 116 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-phidex/billing-invoice-line.py` | removed | +0/-99 |
| 117 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-phidex/billing-invoice-mpan.py` | removed | +0/-99 |
| 118 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-phidex/billing-invoice-site.py` | removed | +0/-99 |
| 119 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-phidex/billing-invoice-vat.py` | removed | +0/-99 |
| 120 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-phidex/billing-invoice.py` | removed | +0/-99 |
| 121 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-phidex/billing-product-charge.py` | removed | +0/-99 |
| 122 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-phidex/billing-product-section.py` | removed | +0/-99 |
| 123 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-phidex/billing-product-timeband-group.py` | removed | +0/-99 |
| 124 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-phidex/billing-product.py` | removed | +0/-99 |
| 125 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-phidex/billing-run-group.py` | removed | +0/-99 |
| 126 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-phidex/billing-trade-group.py` | removed | +0/-109 |
| 127 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-phidex/process-queue.py` | removed | +0/-99 |
| 128 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-phidex/project-customer.py` | removed | +0/-99 |
| 129 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-phidex/project-document.py` | removed | +0/-99 |
| 130 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-phidex/project-mpan.py` | removed | +0/-99 |
| 131 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-phidex/project-site.py` | removed | +0/-99 |
| 132 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-phidex/project-unit-rate.py` | removed | +0/-99 |
| 133 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-phidex/project.py` | removed | +0/-99 |
| 134 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-phidex/staging.py` | added | +229/-0 |
| 135 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-salesforce/account.py` | removed | +0/-106 |
| 136 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-salesforce/case.py` | removed | +0/-77 |
| 137 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-salesforce/emailmessage.py` | removed | +0/-77 |
| 138 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-salesforce/loa-shell.py` | removed | +0/-107 |
| 139 | `cdk/lib/resources/glue/etl/scripts/cdc-staging-salesforce/staging.py` | added | +254/-0 |
| 140 | `cdk/lib/resources/glue/etl/scripts/master-consumption-record/consumption-activity-v3.py` | modified | +0/-5 |
| 141 | `cdk/lib/resources/glue/etl/scripts/master-consumption-record/sm-consumption-activity-v3.py` | modified | +1/-6 |
| 142 | `cdk/lib/resources/glue/etl/scripts/master-customer-record/account-activity-v3.py` | modified | +133/-28 |
| 143 | `cdk/lib/resources/glue/etl/scripts/master-customer-record/case-activity.py` | modified | +91/-2 |
| 144 | `cdk/lib/resources/glue/etl/scripts/master-customer-record/loa-activity-v3.py` | modified | +50/-5 |
| 145 | `cdk/lib/resources/glue/etl/scripts/master-financial-record/allocated-payment-refund-activity-v3.py` | modified | +81/-2 |
| 146 | `cdk/lib/resources/glue/etl/scripts/master-financial-record/invoice-activity-v3.py` | modified | +72/-2 |
| 147 | `cdk/lib/resources/glue/etl/scripts/master-financial-record/migrated-invoice-activity-v3.py` | modified | +81/-2 |
| 148 | `cdk/lib/resources/glue/etl/scripts/master-financial-record/migrated-payment-activity-v3.py` | modified | +81/-2 |
| 149 | `cdk/lib/resources/glue/etl/scripts/master-financial-record/migrated-refund-activity-v3.py` | modified | +81/-2 |
| 150 | `cdk/lib/resources/glue/etl/scripts/master-financial-record/statement-of-account-activity.py` | modified | +236/-19 |
| 151 | `cdk/lib/resources/glue/etl/scripts/master-meter-read-record/historic-meter-read-activity-v3.py` | modified | +53/-2 |
| 152 | `cdk/lib/resources/glue/etl/scripts/master-meter-read-record/meter-read-activity-v3.py` | modified | +61/-2 |
| 153 | `cdk/lib/resources/lambda/partition-tracker-lambda.ts` | added | +92/-0 |
| 154 | `cdk/lib/resources/lambda/schema-change-lambda.ts` | added | +122/-0 |
| 155 | `cdk/lib/resources/orchestration/data-orchestration-trigger.ts` | removed | +0/-182 |
| 156 | `cdk/lib/resources/orchestration/data-orchestration.ts` | removed | +0/-350 |
| 157 | `cdk/lib/resources/sqs/partition-event-queue.ts` | added | +51/-0 |
| 158 | `cdk/lib/resources/sqs/schema-change-queue.ts` | added | +66/-0 |
| 159 | `cdk/lib/resources/step-functions/master-record-sf.ts` | added | +231/-0 |
| 160 | `cdk/lib/resources/step-functions/orchestrator-sf.ts` | added | +316/-0 |
| 161 | `cdk/lib/resources/step-functions/source-system-sf.ts` | added | +290/-0 |
| 162 | `cdk/lib/stacks/data-orchestration-stack.ts` | removed | +0/-27 |
| 163 | `cdk/lib/stacks/etl-stack.ts` | modified | +4/-2 |
| 164 | `cdk/lib/stacks/new-data-orchestration-stack.ts` | added | +29/-0 |
| 165 | `cdk/lib/stages/application-stage.ts` | modified | +8/-2 |
| 166 | `docs/data-orchestration-architecture.md` | added | +143/-0 |
| 167 | `lambdas/crawler-schema-change/index.ts` | added | +185/-0 |
| 168 | `lambdas/crawler-schema-change/loop-prevention.ts` | added | +77/-0 |
| 169 | `lambdas/crawler-schema-change/package-lock.json` | added | +3265/-0 |
| 170 | `lambdas/crawler-schema-change/package.json` | added | +26/-0 |
| 171 | `lambdas/crawler-schema-change/partition-reset.ts` | added | +161/-0 |
| 172 | `lambdas/crawler-schema-change/schema-compare.ts` | added | +30/-0 |
| 173 | `lambdas/crawler-schema-change/schema-detection.ts` | added | +126/-0 |
| 174 | `lambdas/crawler-schema-change/tsconfig.json` | added | +12/-0 |
| 175 | `lambdas/partition-tracker/index.test.ts` | added | +103/-0 |
| 176 | `lambdas/partition-tracker/index.ts` | added | +173/-0 |
| 177 | `lambdas/partition-tracker/orchestrator-handler.test.ts` | added | +218/-0 |
| 178 | `lambdas/partition-tracker/orchestrator-handler.ts` | added | +121/-0 |
| 179 | `lambdas/partition-tracker/package-lock.json` | added | +3467/-0 |
| 180 | `lambdas/partition-tracker/package.json` | added | +25/-0 |
| 181 | `lambdas/partition-tracker/partition-utils.test.ts` | added | +159/-0 |
| 182 | `lambdas/partition-tracker/partition-utils.ts` | added | +130/-0 |
| 183 | `lambdas/partition-tracker/step-function-handler.ts` | added | +100/-0 |
| 184 | `lambdas/partition-tracker/tsconfig.json` | added | +12/-0 |
| 185 | `queries/partition-activity-analysis.sql` | added | +196/-0 |
| 186 | `queries/partition-activity-results.csv` | added | +86/-0 |

## Understanding — Intent vs File Changes

Based on the PR description and comments, this PR delivers 7 major changes. Here's how they map to the file changes:

### 1. "Completely reworks data orchestration"
**Files:** `cdk/lib/resources/data-orchestration/data-orchestration.ts`, `cdk/lib/resources/step-functions/orchestrator-sf.ts`, `cdk/lib/resources/step-functions/source-system-sf.ts`, `cdk/lib/resources/step-functions/master-record-sf.ts`, `cdk/lib/config/dependency-map.*`, `docs/data-orchestration-architecture.md`

Replaces the monolithic parallel step function with a dependency-aware orchestrator that splits into source-system and master-record sub-flows.

### 2. "Glue jobs for CS, Phidex and SF all parameterized"
**Files:** ~80 individual table scripts removed (centrestage, phidex, salesforce, bryt, ensek), replaced by 5 new `staging.py` scripts (one per source system) + `cdk/lib/resources/glue/etl/cdc-staging-generic.ts`

Consolidates ~80 per-table scripts into parameterized generic scripts driven by configuration.

### 3. "Cut Ensek out of orchestration"
**Files:** `cdc-staging-ensek/readings.py` (removed), `cdc-staging-ensek/registers.py` (removed), `cdc-staging-ensek/staging.py` (added — likely a standalone version)

### 4. "Partition tracking via S3 events"
**Files:** `cdk/lib/resources/dynamodb/partition-tracker.ts`, `cdk/lib/resources/lambda/partition-tracker-lambda.ts`, `cdk/lib/resources/sqs/partition-event-queue.ts`, `lambdas/partition-tracker/*` (index.ts, orchestrator-handler.ts, partition-utils.ts, step-function-handler.ts + tests)

New event-driven partition tracking system using S3 events → SQS → Lambda → DynamoDB.

### 5. "Orchestration only runs what it needs to run / master record only kicks off if dependencies updated"
**Files:** `cdk/lib/config/dependency-map.json`, `cdk/lib/config/dependency-map.ts`, `cdk/lib/config/dependency-map.test.ts`, `cdk/lib/config/table-config.ts`, `cdk/lib/config/tables/centrestage.json`, `cdk/lib/config/tables/phidex.json`, `lambdas/partition-tracker/orchestrator-handler.ts`

Dependency map defines which master records depend on which staging tables. Orchestrator checks partition tracker to determine what's changed.

### 6. "Exploded out the data json in master record into separate columns"
**Files:** `cdk/lib/resources/glue/etl/scripts/master-*-record/*.py` (11 modified files — account-activity-v3, invoice-activity-v3, meter-read-activity-v3, etc.)

Master record scripts updated to extract JSON blob fields into individual columns.

### 7. "Crawlers run once a week, lambda reacts to schema changes"
**Files:** `cdk/lib/resources/event-bridge/schema-change-rule.ts`, `cdk/lib/resources/lambda/schema-change-lambda.ts`, `cdk/lib/resources/sqs/schema-change-queue.ts`, `lambdas/crawler-schema-change/*` (index.ts, schema-detection.ts, schema-compare.ts, partition-reset.ts, loop-prevention.ts)

New schema change detection pipeline: crawler detects changes → EventBridge → SQS → Lambda → marks partitions for reprocessing.

### Unmapped / Supporting Files
- `.kiro/specs/*` — Kiro spec documents for the 3 workstreams (design docs, not runtime code)
- `.kiro/steering/project-conventions.md` — project conventions
- `cdk/jest.config.js` — test config
- `cdk/lib/resources/dms/centrestage.ts`, `phidex.ts` — minor DMS config changes
- `cdk/lib/resources/glue/etl/jobs.ts`, `lake-formation.ts` — minor adjustments
- `queries/partition-activity-analysis.sql`, `partition-activity-results.csv` — analysis artefacts
- `lambdas/*/package-lock.json` — dependency locks (skip for review)
