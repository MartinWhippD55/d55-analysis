# Glue Job Inventory — run-titanium-jobs stage

Total jobs: 94

## Source Database Locations

| Source Database | Location |
|---|---|
| `rel-esg-prod-data-eng-bryt-db` | `unknown` |
| `rel-esg-prod-data-eng-centrestage-db` | `unknown` |
| `rel-esg-prod-data-eng-ensek-db` | `unknown` |
| `rel-esg-prod-data-eng-phidex-db` | `unknown` |
| `rel-esg-prod-data-eng-salesforce-db` | `unknown` |

## Job Details

| # | Job Name | Source DB | Staging DB | Warehouse | Workers |
|---|---|---|---|---|---|
| 1 | `phidex-billing-contract-mpan-volume` | `rel-esg-prod-data-eng-phidex-db` | `rel_esg_prod_data_eng_phidex_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 5x G.8X |
| 2 | `phidex-billing-contract-mpan` | `rel-esg-prod-data-eng-phidex-db` | `rel_esg_prod_data_eng_phidex_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 3 | `phidex-billing-customer` | `rel-esg-prod-data-eng-phidex-db` | `rel_esg_prod_data_eng_phidex_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 4 | `phidex-billing-group` | `rel-esg-prod-data-eng-phidex-db` | `rel_esg_prod_data_eng_phidex_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 5 | `centerstage-titanium-customer` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 6 | `centerstage-titanium-customer-supply` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 7 | `centerstage-titanium-constant-customer-supply-status` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 8 | `centerstage-titanium-constant-payment-method` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 9 | `centerstage-titanium-constant-payment-status` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 10 | `centerstage-titanium-constant-refund-method` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 11 | `centerstage-titanium-supply` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 12 | `centerstage-titanium-supply-electricity` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 13 | `centerstage-titanium-lookup-profile-class` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 14 | `centerstage-titanium-lookup-measurement-class` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 15 | `centerstage-titanium-site` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 16 | `centerstage-titanium-address` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 17 | `centerstage-titanium-meter` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 18 | `centerstage-titanium-meter-electricity` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 19 | `centerstage-titanium-lookup-meter-type` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 20 | `centerstage-titanium-register` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 21 | `centerstage-titanium-register-electricity` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 22 | `centerstage-titanium-constant-tpr` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 23 | `centerstage-titanium-supply-contract` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 24 | `centerstage-titanium-contract` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 25 | `centerstage-titanium-invoice-billing-raw-data` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 26 | `centerstage-titanium-invoice-crm-data` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 27 | `centerstage-titanium-document-data` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 28 | `centerstage-titanium-generated-document` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 29 | `centerstage-titanium-mpan-billing-raw-data` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 30 | `centerstage-titanium-payment-association-map` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 31 | `centerstage-titanium-payment` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 32 | `centerstage-titanium-refund-association-map` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 33 | `centerstage-titanium-refund` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 34 | `centerstage-titanium-allocation` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 35 | `centerstage-titanium-invoice-detail` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 36 | `centerstage-titanium-payment-crm-data` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 37 | `centerstage-titanium-site-billing-raw-data` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 38 | `centerstage-titanium-site-crm-data` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 39 | `centerstage-titanium-invoice-billing-header-raw-data` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 40 | `centerstage-titanium-invoice-detail-note` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 41 | `centerstage-titanium-customer-note` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 42 | `centerstage-titanium-customer-note-history` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 43 | `centerstage-titanium-customer-note-attachment` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 44 | `centerstage-afmse-meter-register-reading` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 45 | `centerstage-afmse-meter-register` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 46 | `centerstage-afmse-meter` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 47 | `centerstage-afmse-mpan` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 48 | `centerstage-bol-xread-out-01-active-import-profile-data` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 49 | `centerstage-bol-xread-out-01-meter` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 50 | `centerstage-dcc-bol-device` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 51 | `centerstage-billing-wide` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 52 | `salesforce-account` | `rel-esg-prod-data-eng-salesforce-db` | `rel_esg_prod_data_eng_salesforce_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 53 | `salesforce-loa-shell` | `rel-esg-prod-data-eng-salesforce-db` | `rel_esg_prod_data_eng_salesforce_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 54 | `bryt-payment` | `rel-esg-prod-data-eng-bryt-db` | `rel_esg_prod_data_eng_bryt_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 55 | `bryt-refund` | `rel-esg-prod-data-eng-bryt-db` | `rel_esg_prod_data_eng_bryt_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 56 | `ensek-readings` | `rel-esg-prod-data-eng-ensek-db` | `rel_esg_prod_data_eng_ensek_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 57 | `ensek-registers` | `rel-esg-prod-data-eng-ensek-db` | `rel_esg_prod_data_eng_ensek_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 58 | `phidex-billing-contract-site` | `rel-esg-prod-data-eng-phidex-db` | `rel_esg_prod_data_eng_phidex_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 59 | `centerstage-meter_register_reading_mhhs` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 60 | `centerstage-mpan_mhhs` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 61 | `centerstage-meter_mhhs` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 62 | `centerstage-titanium_contact` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 63 | `centerstage-titanium_sitecontact` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 64 | `phidex-billing-contract-document` | `rel-esg-prod-data-eng-phidex-db` | `rel_esg_prod_data_eng_phidex_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 65 | `phidex-billing-contract-meter` | `rel-esg-prod-data-eng-phidex-db` | `rel_esg_prod_data_eng_phidex_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 66 | `phidex-billing-contract-mpan-line` | `rel-esg-prod-data-eng-phidex-db` | `rel_esg_prod_data_eng_phidex_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 67 | `phidex-billing-contract-mpan-rate` | `rel-esg-prod-data-eng-phidex-db` | `rel_esg_prod_data_eng_phidex_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 4x G.4X |
| 68 | `phidex-billing-contract-mpan-read` | `rel-esg-prod-data-eng-phidex-db` | `rel_esg_prod_data_eng_phidex_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 69 | `phidex-billing-contract-register` | `rel-esg-prod-data-eng-phidex-db` | `rel_esg_prod_data_eng_phidex_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 70 | `phidex-billing-invoice` | `rel-esg-prod-data-eng-phidex-db` | `rel_esg_prod_data_eng_phidex_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 71 | `phidex-billing-invoice-document` | `rel-esg-prod-data-eng-phidex-db` | `rel_esg_prod_data_eng_phidex_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 72 | `phidex-billing-invoice-error` | `rel-esg-prod-data-eng-phidex-db` | `rel_esg_prod_data_eng_phidex_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 4x G.4X |
| 73 | `phidex-billing-invoice-line` | `rel-esg-prod-data-eng-phidex-db` | `rel_esg_prod_data_eng_phidex_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 74 | `phidex-billing-invoice-mpan` | `rel-esg-prod-data-eng-phidex-db` | `rel_esg_prod_data_eng_phidex_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 75 | `phidex-billing-invoice-site` | `rel-esg-prod-data-eng-phidex-db` | `rel_esg_prod_data_eng_phidex_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 76 | `phidex-billing-invoice-vat` | `rel-esg-prod-data-eng-phidex-db` | `rel_esg_prod_data_eng_phidex_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 77 | `phidex-billing-product` | `rel-esg-prod-data-eng-phidex-db` | `rel_esg_prod_data_eng_phidex_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 78 | `phidex-billing-product-charge` | `rel-esg-prod-data-eng-phidex-db` | `rel_esg_prod_data_eng_phidex_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 79 | `phidex-billing-product-section` | `rel-esg-prod-data-eng-phidex-db` | `rel_esg_prod_data_eng_phidex_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 80 | `phidex-billing-product-timeband-group` | `rel-esg-prod-data-eng-phidex-db` | `rel_esg_prod_data_eng_phidex_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 81 | `phidex-billing-run-group` | `rel-esg-prod-data-eng-phidex-db` | `rel_esg_prod_data_eng_phidex_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 82 | `phidex-billing-trade-group` | `rel-esg-prod-data-eng-phidex-db` | `rel_esg_prod_data_eng_phidex_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 83 | `phidex-process-queue` | `rel-esg-prod-data-eng-phidex-db` | `rel_esg_prod_data_eng_phidex_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 84 | `phidex-project` | `rel-esg-prod-data-eng-phidex-db` | `rel_esg_prod_data_eng_phidex_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 85 | `phidex-project-customer` | `rel-esg-prod-data-eng-phidex-db` | `rel_esg_prod_data_eng_phidex_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 86 | `phidex-project-document` | `rel-esg-prod-data-eng-phidex-db` | `rel_esg_prod_data_eng_phidex_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 4x G.4X |
| 87 | `phidex-project-mpan` | `rel-esg-prod-data-eng-phidex-db` | `rel_esg_prod_data_eng_phidex_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 88 | `phidex-project-site` | `rel-esg-prod-data-eng-phidex-db` | `rel_esg_prod_data_eng_phidex_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 89 | `phidex-project-unit-rate` | `rel-esg-prod-data-eng-phidex-db` | `rel_esg_prod_data_eng_phidex_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 4x G.4X |
| 90 | `centerstage-titanium-supply-contact` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 91 | `centerstage-titanium-customer-contact` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 92 | `centerstage-titanium-supply-registration-history` | `rel-esg-prod-data-eng-centrestage-db` | `rel_esg_prod_data_eng_centrestage_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 93 | `phidex-billing-contract` | `rel-esg-prod-data-eng-phidex-db` | `rel_esg_prod_data_eng_phidex_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 2x G.1X |
| 94 | `salesforce-case` | `rel-esg-prod-data-eng-salesforce-db` | `rel_esg_prod_data_eng_salesforce_cdc_staging_db` | `s3://rel-esg-prod-data-eng-cdc-staging/` | 4x G.4X |
