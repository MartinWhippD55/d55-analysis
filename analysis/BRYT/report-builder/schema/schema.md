# Glue schema — `rel_esg_prod_data_eng_master_record_db`

> Raw source: `glue-tables-raw.json` (`aws glue get-tables`, profile `bryt-proddy` → account 837413265725, region eu-west-2).
> Generated for Task 0.1. Database created 2025-11-26. 13 tables.

| Table | Columns | Partition keys |
|---|---|---|
| `account_activity` | 25 | - |
| `case_activity` | 16 | - |
| `consumption_activity` | 30 | - |
| `consumption_activity_view_test` | 33 | - |
| `ecoes_activity` | 67 | - |
| `financial_activity` | 25 | - |
| `jira_changelog_activity` | 12 | - |
| `jira_issue_activity` | 249 | - |
| `loa_activity` | 20 | - |
| `meter_reading_activity` | 20 | - |
| `sm_consumption_activity` | 12 | - |
| `statement_of_account_activity` | 26 | - |
| `supply_activity` | 9 | - |


## `account_activity`

- Location: `s3://rel-esg-prod-data-eng-master-record/rel_esg_prod_data_eng_master_record_db.db/account_activity`
- Format: ``

| # | Column | Type | Comment |
|---|---|---|---|
| 1 | `activity_name` | `string` |  |
| 2 | `activity_version` | `int` |  |
| 3 | `created_date_time` | `string` |  |
| 4 | `is_deleted` | `boolean` |  |
| 5 | `bryt_number` | `string` |  |
| 6 | `account_id` | `string` |  |
| 7 | `data` | `string` |  |
| 8 | `checksum` | `string` |  |
| 9 | `account_status` | `string` |  |
| 10 | `customer_id` | `string` |  |
| 11 | `company_name` | `string` |  |
| 12 | `primary_contact_first_name` | `string` |  |
| 13 | `primary_contact_last_name` | `string` |  |
| 14 | `primary_contact_telephone` | `string` |  |
| 15 | `primary_contact_email` | `string` |  |
| 16 | `address_line1` | `string` |  |
| 17 | `address_line2` | `string` |  |
| 18 | `address_line3` | `string` |  |
| 19 | `post_code` | `string` |  |
| 20 | `account_type` | `string` |  |
| 21 | `customer_supply` | `array<struct<customer_supply_id:string,supply_effective_from:string,supply_effective_to:string,supply_status:string,supply:array<struct<supply_id:string,mpan:string,profile_class:string,measurement_class:string,site_id:string,site_name:string,address_line1:string,address_line2:string,address_line3:string,town:string,post_code:string,meters:array<struct<meter_id:string,meter_serial_number:string,installed_date:string,removed_date:string,meter_type:string,registers:array<struct<register_id:string,number_of_digits:string,tpr:string,register_reference:string,non_settlement_functionality_code:string>>>>>>>>` |  |
| 22 | `supply_contracts` | `array<struct<supply_id:string,contract_id:string,start_date:string,end_date:string,product_name:string,contract_name:string,contract_reference:string>>` |  |
| 23 | `contacts` | `array<struct<contact_type:string,contact_id:string,email_address:string,first_name:string,last_name:string,site_id:string,supply_id:string,contact_level:string>>` |  |
| 24 | `billing_groups` | `array<struct<billing_group_id:string,billing_group_reference:string,billing_customer_id:string,pricing_customer_id:string,billing_group_name:string,billing_group_status:string,customer_reference:string>>` |  |
| 25 | `customer_is_deleted` | `boolean` |  |

## `case_activity`

- Location: `s3://rel-esg-prod-data-eng-master-record/rel_esg_prod_data_eng_master_record_db.db/case_activity`
- Format: ``

| # | Column | Type | Comment |
|---|---|---|---|
| 1 | `activity_name` | `string` |  |
| 2 | `activity_version` | `int` |  |
| 3 | `created_date_time` | `string` |  |
| 4 | `is_deleted` | `boolean` |  |
| 5 | `id` | `string` |  |
| 6 | `bryt_number` | `string` |  |
| 7 | `account_id` | `string` |  |
| 8 | `data` | `string` |  |
| 9 | `checksum` | `string` |  |
| 10 | `case_number` | `string` |  |
| 11 | `case_created` | `string` |  |
| 12 | `subject` | `string` |  |
| 13 | `description` | `string` |  |
| 14 | `category` | `string` |  |
| 15 | `sub_category` | `string` |  |
| 16 | `last_modified_date` | `string` |  |

## `consumption_activity`

- Location: `s3://rel-esg-prod-data-eng-master-record/rel_esg_prod_data_eng_master_record_db.db/consumption_activity`
- Format: ``

| # | Column | Type | Comment |
|---|---|---|---|
| 1 | `year` | `int` |  |
| 2 | `month` | `int` |  |
| 3 | `day` | `int` |  |
| 4 | `date` | `date` |  |
| 5 | `source` | `string` |  |
| 6 | `billing_contract_mpan_volume_id` | `bigint` |  |
| 7 | `billing_period` | `int` |  |
| 8 | `billing_contract_mpan_id` | `int` |  |
| 9 | `consumption_msp` | `decimal(24,15)` |  |
| 10 | `consumption_gsp` | `decimal(24,15)` |  |
| 11 | `consumption_nbp` | `decimal(24,15)` |  |
| 12 | `consumption_ai` | `decimal(24,15)` |  |
| 13 | `consumption_ae` | `decimal(24,15)` |  |
| 14 | `consumption_ri` | `decimal(24,15)` |  |
| 15 | `consumption_re` | `decimal(24,15)` |  |
| 16 | `actual_estimated_ai` | `string` |  |
| 17 | `actual_estimated_ae` | `string` |  |
| 18 | `actual_estimated_ri` | `string` |  |
| 19 | `actual_estimated_re` | `string` |  |
| 20 | `creation_time_ai` | `timestamp` |  |
| 21 | `creation_time_ae` | `timestamp` |  |
| 22 | `creation_time_ri` | `timestamp` |  |
| 23 | `creation_time_re` | `timestamp` |  |
| 24 | `mpan` | `string` |  |
| 25 | `aa` | `decimal(18,2)` |  |
| 26 | `eac` | `decimal(18,2)` |  |
| 27 | `profile_coefficient` | `decimal(18,14)` |  |
| 28 | `llf` | `decimal(5,3)` |  |
| 29 | `transmission_loss_multiplier` | `decimal(18,9)` |  |
| 30 | `checksum` | `string` |  |

## `consumption_activity_view_test`

- Location: `s3://rel-esg-prod-data-eng-master-record/rel_esg_prod_data_eng_master_record_db.db/consumption_activity_view_test`
- Format: ``

| # | Column | Type | Comment |
|---|---|---|---|
| 1 | `year` | `int` |  |
| 2 | `month` | `int` |  |
| 3 | `day` | `int` |  |
| 4 | `date` | `date` |  |
| 5 | `source` | `string` |  |
| 6 | `billing_contract_mpan_volume_id` | `bigint` |  |
| 7 | `billing_period` | `int` |  |
| 8 | `billing_contract_mpan_id` | `int` |  |
| 9 | `consumption_msp` | `decimal(24,15)` |  |
| 10 | `consumption_gsp` | `decimal(24,15)` |  |
| 11 | `consumption_nbp` | `decimal(24,15)` |  |
| 12 | `calculated_consumption_msp` | `decimal(24,15)` |  |
| 13 | `calculated_consumption_gsp` | `decimal(24,15)` |  |
| 14 | `calculated_consumption_nbp` | `decimal(24,15)` |  |
| 15 | `consumption_ai` | `decimal(24,15)` |  |
| 16 | `consumption_ae` | `decimal(24,15)` |  |
| 17 | `consumption_ri` | `decimal(24,15)` |  |
| 18 | `consumption_re` | `decimal(24,15)` |  |
| 19 | `actual_estimated_ai` | `string` |  |
| 20 | `actual_estimated_ae` | `string` |  |
| 21 | `actual_estimated_ri` | `string` |  |
| 22 | `actual_estimated_re` | `string` |  |
| 23 | `creation_time_ai` | `timestamp` |  |
| 24 | `creation_time_ae` | `timestamp` |  |
| 25 | `creation_time_ri` | `timestamp` |  |
| 26 | `creation_time_re` | `timestamp` |  |
| 27 | `mpan` | `string` |  |
| 28 | `aa` | `decimal(18,2)` |  |
| 29 | `eac` | `decimal(18,2)` |  |
| 30 | `profilecoefficient` | `decimal(18,14)` |  |
| 31 | `linelossfactor` | `decimal(5,3)` |  |
| 32 | `transmissionlossmultiplier` | `decimal(18,9)` |  |
| 33 | `checksum` | `string` |  |

## `ecoes_activity`

- Location: `s3://rel-esg-prod-data-eng-master-record/rel_esg_prod_data_eng_master_record_db.db/ecoes_activity`
- Format: ``

| # | Column | Type | Comment |
|---|---|---|---|
| 1 | `queried_mpan` | `string` |  |
| 2 | `mpan_core` | `string` |  |
| 3 | `address_line_1` | `string` |  |
| 4 | `address_line_2` | `string` |  |
| 5 | `address_line_3` | `string` |  |
| 6 | `address_line_4` | `string` |  |
| 7 | `address_line_5` | `string` |  |
| 8 | `address_line_6` | `string` |  |
| 9 | `address_line_7` | `string` |  |
| 10 | `address_line_8` | `string` |  |
| 11 | `address_line_9` | `string` |  |
| 12 | `postcode` | `string` |  |
| 13 | `trading_status` | `string` |  |
| 14 | `trading_status_efd` | `string` |  |
| 15 | `gsp_group_id` | `string` |  |
| 16 | `gsp_group_efd` | `string` |  |
| 17 | `measurement_class` | `string` |  |
| 18 | `measurement_class_efd` | `string` |  |
| 19 | `profile_class` | `string` |  |
| 20 | `profile_class_efd` | `string` |  |
| 21 | `standard_settlement_configuration` | `string` |  |
| 22 | `standard_settlement_configuration_efd` | `string` |  |
| 23 | `meter_timeswitch_class` | `string` |  |
| 24 | `meter_timeswitch_class_efd` | `string` |  |
| 25 | `line_loss_factor` | `string` |  |
| 26 | `line_loss_factor_efd` | `string` |  |
| 27 | `energisation_status` | `string` |  |
| 28 | `energisation_status_efd` | `string` |  |
| 29 | `data_aggregator_mpid` | `string` |  |
| 30 | `data_aggregator_efd` | `string` |  |
| 31 | `data_collector_mpid` | `string` |  |
| 32 | `data_collector_efd` | `string` |  |
| 33 | `metering_service_mpid` | `string` |  |
| 34 | `metering_service_efd` | `string` |  |
| 35 | `supplier_mpid` | `string` |  |
| 36 | `supplier_efd` | `string` |  |
| 37 | `green_deal_in_effect` | `string` |  |
| 38 | `smso_mpid` | `string` |  |
| 39 | `smso_efd` | `string` |  |
| 40 | `dcc_service_flag` | `string` |  |
| 41 | `dcc_service_flag_efd` | `string` |  |
| 42 | `ihd_status` | `string` |  |
| 43 | `ihd_status_efd` | `string` |  |
| 44 | `smets_version` | `string` |  |
| 45 | `rmp_state` | `string` |  |
| 46 | `rmp_state_efd` | `string` |  |
| 47 | `domestic_premises_indicator` | `string` |  |
| 48 | `metered_indicator` | `string` |  |
| 49 | `connection_type` | `string` |  |
| 50 | `market_segment_indicator` | `string` |  |
| 51 | `mhhs_indicator` | `string` |  |
| 52 | `energy_direction` | `string` |  |
| 53 | `energy_direction_etd` | `string` |  |
| 54 | `relationship_status_indicator` | `string` |  |
| 55 | `execution_id` | `string` |  |
| 56 | `record_source` | `string` |  |
| 57 | `created_datetime` | `string` |  |
| 58 | `meter_serial_number` | `string` |  |
| 59 | `meter_install_date` | `string` |  |
| 60 | `meter_type` | `string` |  |
| 61 | `map_mpid` | `string` |  |
| 62 | `primary_mpan` | `string` |  |
| 63 | `secondary_mpan` | `string` |  |
| 64 | `primary_mpan_mhhs_indicator` | `string` |  |
| 65 | `secondary_mpan_mhhs_indicator` | `string` |  |
| 66 | `master_record_created_datetime` | `string` |  |
| 67 | `checksum` | `string` |  |

## `financial_activity`

- Location: `s3://rel-esg-prod-data-eng-master-record/rel_esg_prod_data_eng_master_record_db.db/financial_activity`
- Format: ``

| # | Column | Type | Comment |
|---|---|---|---|
| 1 | `activity_name` | `string` |  |
| 2 | `activity_version` | `int` |  |
| 3 | `created_date_time` | `string` |  |
| 4 | `is_deleted` | `boolean` |  |
| 5 | `id` | `int` |  |
| 6 | `bryt_number` | `string` |  |
| 7 | `transaction_type` | `string` |  |
| 8 | `mpan` | `string` |  |
| 9 | `is_migrated` | `boolean` |  |
| 10 | `data` | `string` |  |
| 11 | `checksum` | `string` |  |
| 12 | `customer_id` | `string` |  |
| 13 | `amount` | `string` |  |
| 14 | `date` | `string` |  |
| 15 | `created_date` | `string` |  |
| 16 | `billing_group_id` | `string` |  |
| 17 | `site_id` | `string` |  |
| 18 | `supply_id` | `string` |  |
| 19 | `ensek_statement_id` | `string` |  |
| 20 | `is_hh_metering` | `boolean` |  |
| 21 | `billing_start_date` | `string` |  |
| 22 | `billing_end_date` | `string` |  |
| 23 | `billing_run_group_id` | `string` |  |
| 24 | `meter_type` | `string` |  |
| 25 | `documents` | `array<struct<document_data_id:string,document_id:string,document_path:string,document_type:string>>` |  |

## `jira_changelog_activity`

- Location: `s3://rel-esg-prod-data-eng-master-record/rel_esg_prod_data_eng_master_record_db.db/jira_changelog_activity`
- Format: ``

| # | Column | Type | Comment |
|---|---|---|---|
| 1 | `issue_key` | `string` |  |
| 2 | `changelog_id` | `string` |  |
| 3 | `author_account_id` | `string` |  |
| 4 | `author_display_name` | `string` |  |
| 5 | `created` | `string` |  |
| 6 | `field` | `string` |  |
| 7 | `fieldtype` | `string` |  |
| 8 | `from_value` | `string` |  |
| 9 | `from_string` | `string` |  |
| 10 | `to_value` | `string` |  |
| 11 | `to_string` | `string` |  |
| 12 | `processed_at` | `string` |  |

## `jira_issue_activity`

- Location: `s3://rel-esg-prod-data-eng-master-record/rel_esg_prod_data_eng_master_record_db.db/jira_issue_activity`
- Format: ``

| # | Column | Type | Comment |
|---|---|---|---|
| 1 | `id` | `string` |  |
| 2 | `summary` | `string` |  |
| 3 | `project_key` | `string` |  |
| 4 | `project_name` | `string` |  |
| 5 | `issue_type` | `string` |  |
| 6 | `status` | `string` |  |
| 7 | `status_category` | `string` |  |
| 8 | `priority` | `string` |  |
| 9 | `assignee` | `string` |  |
| 10 | `reporter` | `string` |  |
| 11 | `creator` | `string` |  |
| 12 | `created` | `string` |  |
| 13 | `updated` | `string` |  |
| 14 | `status_category_changed` | `string` |  |
| 15 | `time_spent_seconds` | `bigint` |  |
| 16 | `aggregate_time_spent_seconds` | `bigint` |  |
| 17 | `progress_percent` | `int` |  |
| 18 | `aggregate_progress_percent` | `int` |  |
| 19 | `votes` | `int` |  |
| 20 | `watchers` | `int` |  |
| 21 | `sprint_id` | `bigint` |  |
| 22 | `sprint_name` | `string` |  |
| 23 | `sprint_state` | `string` |  |
| 24 | `sprint_board_id` | `bigint` |  |
| 25 | `sprint_start_date` | `string` |  |
| 26 | `sprint_end_date` | `string` |  |
| 27 | `sprint_complete_date` | `string` |  |
| 28 | `linked_issue_1_relationship` | `string` |  |
| 29 | `linked_issue_1_key` | `string` |  |
| 30 | `linked_issue_1_summary` | `string` |  |
| 31 | `linked_issue_1_status` | `string` |  |
| 32 | `linked_issue_1_status_category` | `string` |  |
| 33 | `linked_issue_1_priority` | `string` |  |
| 34 | `linked_issue_1_issue_type` | `string` |  |
| 35 | `linked_issue_2_relationship` | `string` |  |
| 36 | `linked_issue_2_key` | `string` |  |
| 37 | `linked_issue_2_summary` | `string` |  |
| 38 | `linked_issue_2_status` | `string` |  |
| 39 | `linked_issue_2_status_category` | `string` |  |
| 40 | `linked_issue_2_priority` | `string` |  |
| 41 | `linked_issue_2_issue_type` | `string` |  |
| 42 | `description` | `string` |  |
| 43 | `user_story` | `string` |  |
| 44 | `test_cases` | `string` |  |
| 45 | `team_10001` | `string` |  |
| 46 | `organizations` | `string` |  |
| 47 | `approvers` | `string` |  |
| 48 | `impact` | `string` |  |
| 49 | `change_type_10005` | `string` |  |
| 50 | `change_risk` | `string` |  |
| 51 | `change_reason` | `string` |  |
| 52 | `actual_start` | `string` |  |
| 53 | `actual_end` | `string` |  |
| 54 | `request_type` | `string` |  |
| 55 | `epic_name` | `string` |  |
| 56 | `epic_status` | `string` |  |
| 57 | `epic_color` | `string` |  |
| 58 | `epic_link` | `string` |  |
| 59 | `start_date` | `string` |  |
| 60 | `story_point_estimate` | `string` |  |
| 61 | `issue_color` | `string` |  |
| 62 | `rank` | `string` |  |
| 63 | `sprint` | `string` |  |
| 64 | `flagged` | `string` |  |
| 65 | `target_start` | `string` |  |
| 66 | `target_end` | `string` |  |
| 67 | `chart_date_of_first_response` | `string` |  |
| 68 | `chart_time_in_status` | `string` |  |
| 69 | `approvals` | `string` |  |
| 70 | `request_participants` | `string` |  |
| 71 | `satisfaction` | `string` |  |
| 72 | `satisfaction_date` | `string` |  |
| 73 | `approver_groups` | `string` |  |
| 74 | `affected_services` | `string` |  |
| 75 | `time_to_resolution` | `string` |  |
| 76 | `time_to_first_response` | `string` |  |
| 77 | `request_language` | `string` |  |
| 78 | `story_points` | `string` |  |
| 79 | `responders` | `string` |  |
| 80 | `sub_category` | `string` |  |
| 81 | `work_category` | `string` |  |
| 82 | `3rd_party_completion_date` | `string` |  |
| 83 | `date_submitted_to_3rd_party` | `string` |  |
| 84 | `allocated_to` | `string` |  |
| 85 | `status_10047` | `string` |  |
| 86 | `requirement_id` | `string` |  |
| 87 | `external_reference` | `string` |  |
| 88 | `raised_via` | `string` |  |
| 89 | `whats_the_problem_we_are_solving` | `string` |  |
| 90 | `how_are_we_solving_the_problem` | `string` |  |
| 91 | `scope` | `string` |  |
| 92 | `urgency` | `string` |  |
| 93 | `pending_reason` | `string` |  |
| 94 | `product_categorization` | `string` |  |
| 95 | `operational_categorization` | `string` |  |
| 96 | `affected_hardware` | `string` |  |
| 97 | `severity_10059` | `string` |  |
| 98 | `source` | `string` |  |
| 99 | `implementation_plan` | `string` |  |
| 100 | `backout_plan` | `string` |  |
| 101 | `test_plan` | `string` |  |
| 102 | `planned_start` | `string` |  |
| 103 | `planned_end` | `string` |  |
| 104 | `investigation_reason` | `string` |  |
| 105 | `root_cause` | `string` |  |
| 106 | `workaround` | `string` |  |
| 107 | `major_incident` | `string` |  |
| 108 | `time_to_close_after_resolution_10070` | `string` |  |
| 109 | `time_to_review_normal_change` | `string` |  |
| 110 | `time_to_close_after_resolution` | `string` |  |
| 111 | `open_forms` | `string` |  |
| 112 | `submitted_forms` | `string` |  |
| 113 | `locked_forms` | `string` |  |
| 114 | `total_forms` | `string` |  |
| 115 | `end_date` | `string` |  |
| 116 | `baseline_start_date` | `string` |  |
| 117 | `baseline_end_date` | `string` |  |
| 118 | `task_progress` | `string` |  |
| 119 | `size` | `string` |  |
| 120 | `category` | `string` |  |
| 121 | `potential_benefits` | `string` |  |
| 122 | `potential_improvement_required` | `string` |  |
| 123 | `process` | `string` |  |
| 124 | `reported_by` | `string` |  |
| 125 | `do_we_have_access_to_the_data` | `string` |  |
| 126 | `which_resource_is_needed` | `string` |  |
| 127 | `new_report` | `string` |  |
| 128 | `name_of_existing_report` | `string` |  |
| 129 | `will_there_be_personal_data_potentially_being_processed` | `string` |  |
| 130 | `is_data_being_processed_in_any_of_the_three_types_of_processing_below` | `string` |  |
| 131 | `will_this_change_implement_new_technological_or_organisational_solutions` | `string` |  |
| 132 | `dipa_score` | `string` |  |
| 133 | `project_manager` | `string` |  |
| 134 | `requirement_id_10119` | `string` |  |
| 135 | `contract_id` | `string` |  |
| 136 | `last_reviewed_date` | `string` |  |
| 137 | `current_status` | `string` |  |
| 138 | `original_status` | `string` |  |
| 139 | `probability` | `string` |  |
| 140 | `severity` | `string` |  |
| 141 | `strategy` | `string` |  |
| 142 | `risk_score` | `string` |  |
| 143 | `business_owner` | `string` |  |
| 144 | `review_date` | `string` |  |
| 145 | `business_area` | `string` |  |
| 146 | `system_area` | `string` |  |
| 147 | `work_type` | `string` |  |
| 148 | `tshirt_size` | `string` |  |
| 149 | `project_overview_key` | `string` |  |
| 150 | `project_overview_status` | `string` |  |
| 151 | `external_party` | `string` |  |
| 152 | `area` | `string` |  |
| 153 | `user_story_10138` | `string` |  |
| 154 | `tdd` | `string` |  |
| 155 | `moscow_rating` | `string` |  |
| 156 | `additional_information` | `string` |  |
| 157 | `dependencies` | `string` |  |
| 158 | `task_category` | `string` |  |
| 159 | `date_decision_made` | `string` |  |
| 160 | `decision_made_by` | `string` |  |
| 161 | `made_via` | `string` |  |
| 162 | `requires_it_testing` | `string` |  |
| 163 | `mitigation` | `string` |  |
| 164 | `external_assignee` | `string` |  |
| 165 | `work_phase_type` | `string` |  |
| 166 | `anticipated_number_of_hours` | `string` |  |
| 167 | `recreation_steps` | `string` |  |
| 168 | `actual_results` | `string` |  |
| 169 | `expected_results` | `string` |  |
| 170 | `reproduction_environment` | `string` |  |
| 171 | `example_id` | `string` |  |
| 172 | `bug_allocation` | `string` |  |
| 173 | `design` | `string` |  |
| 174 | `parent_story` | `string` |  |
| 175 | `internal_reference` | `string` |  |
| 176 | `project` | `string` |  |
| 177 | `sentiment` | `string` |  |
| 178 | `goals` | `string` |  |
| 179 | `actions` | `string` |  |
| 180 | `issue_strategy` | `string` |  |
| 181 | `bug_type` | `string` |  |
| 182 | `link` | `string` |  |
| 183 | `environment` | `string` |  |
| 184 | `does_this_impact_all_customers` | `string` |  |
| 185 | `department` | `string` |  |
| 186 | `reason_for_change_request` | `string` |  |
| 187 | `soft__intangible_benefits` | `string` |  |
| 188 | `risk_of_not_implementing_change` | `string` |  |
| 189 | `name_of_user_who_made_change_request` | `string` |  |
| 190 | `benefits` | `string` |  |
| 191 | `bryt_systems` | `string` |  |
| 192 | `other_system` | `string` |  |
| 193 | `risk_categories` | `string` |  |
| 194 | `focus_areas` | `string` |  |
| 195 | `description_of_change_request` | `string` |  |
| 196 | `raised_by` | `string` |  |
| 197 | `date_raised` | `string` |  |
| 198 | `change_type` | `string` |  |
| 199 | `other_specify` | `string` |  |
| 200 | `systems_impacted` | `string` |  |
| 201 | `date_required` | `string` |  |
| 202 | `strategic_alignment` | `string` |  |
| 203 | `tangible_benefits` | `string` |  |
| 204 | `intangible_benefits` | `string` |  |
| 205 | `evidence_links` | `string` |  |
| 206 | `evidence_folder` | `string` |  |
| 207 | `sponsor` | `string` |  |
| 208 | `project_or_change` | `string` |  |
| 209 | `assessed_date` | `string` |  |
| 210 | `date_added_to_backlog` | `string` |  |
| 211 | `date_planning_commenced` | `string` |  |
| 212 | `build_commenced_date` | `string` |  |
| 213 | `date_release_commenced` | `string` |  |
| 214 | `go_live_date` | `string` |  |
| 215 | `benefit_realisation_to_start` | `string` |  |
| 216 | `project_closure` | `string` |  |
| 217 | `ideal_go_live_date` | `string` |  |
| 218 | `monthly_commentary` | `string` |  |
| 219 | `reporting_stage` | `string` |  |
| 220 | `requirement_source` | `string` |  |
| 221 | `date_fault_occurred` | `string` |  |
| 222 | `example` | `string` |  |
| 223 | `resolution` | `string` |  |
| 224 | `type` | `string` |  |
| 225 | `hard__tangible_benefits` | `string` |  |
| 226 | `date_resolved` | `string` |  |
| 227 | `lesson_learnt_category` | `string` |  |
| 228 | `previous_risk_score` | `string` |  |
| 229 | `acceptance_criteria` | `string` |  |
| 230 | `allocation` | `string` |  |
| 231 | `known_data_source` | `string` |  |
| 232 | `budget` | `string` |  |
| 233 | `development_type` | `string` |  |
| 234 | `team` | `string` |  |
| 235 | `frequency_priority` | `string` |  |
| 236 | `aa_test` | `string` |  |
| 237 | `agentsessions` | `string` |  |
| 238 | `chart_date_of_first_response_10024` | `string` |  |
| 239 | `chart_time_in_status_10025` | `string` |  |
| 240 | `issue_colour` | `string` |  |
| 241 | `key` | `string` |  |
| 242 | `requirement_id_10048` | `string` |  |
| 243 | `story_points_10038` | `string` |  |
| 244 | `task_mode` | `string` |  |
| 245 | `time_remaining` | `string` |  |
| 246 | `vulnerability` | `string` |  |
| 247 | `work_item_created_forms` | `string` |  |
| 248 | `agent_sessions` | `string` |  |
| 249 | `example_2` | `string` |  |

## `loa_activity`

- Location: `s3://rel-esg-prod-data-eng-master-record/rel_esg_prod_data_eng_master_record_db.db/loa_activity`
- Format: ``

| # | Column | Type | Comment |
|---|---|---|---|
| 1 | `activity_name` | `string` |  |
| 2 | `activity_version` | `int` |  |
| 3 | `created_date_time` | `string` |  |
| 4 | `is_deleted` | `boolean` |  |
| 5 | `id` | `string` |  |
| 6 | `customer_bryt_number` | `string` |  |
| 7 | `customer_account_id` | `string` |  |
| 8 | `tpi_bryt_number` | `string` |  |
| 9 | `tpi_account_id` | `string` |  |
| 10 | `data` | `string` |  |
| 11 | `checksum` | `string` |  |
| 12 | `from_date` | `string` |  |
| 13 | `to_date` | `string` |  |
| 14 | `loa_status` | `string` |  |
| 15 | `has_l1_permissions` | `boolean` |  |
| 16 | `has_l2_permissions` | `boolean` |  |
| 17 | `last_modified_date` | `string` |  |
| 18 | `last_modified_by` | `string` |  |
| 19 | `customer_account_name` | `string` |  |
| 20 | `tpi_account_name` | `string` |  |

## `meter_reading_activity`

- Location: `s3://rel-esg-prod-data-eng-master-record/rel_esg_prod_data_eng_master_record_db.db/meter_reading_activity`
- Format: ``

| # | Column | Type | Comment |
|---|---|---|---|
| 1 | `activity_name` | `string` |  |
| 2 | `activity_version` | `int` |  |
| 3 | `is_deleted` | `boolean` |  |
| 4 | `source` | `string` |  |
| 5 | `ensek_register_id` | `int` |  |
| 6 | `meter_point_number` | `bigint` |  |
| 7 | `meter_serial_number` | `string` |  |
| 8 | `register_reference` | `string` |  |
| 9 | `reading_date` | `timestamp` |  |
| 10 | `id` | `bigint` |  |
| 11 | `data` | `string` |  |
| 12 | `checksum` | `string` |  |
| 13 | `mpan` | `string` |  |
| 14 | `register_id` | `string` |  |
| 15 | `meter_point_id` | `string` |  |
| 16 | `reading_value` | `string` |  |
| 17 | `created_date` | `string` |  |
| 18 | `reading_type` | `string` |  |
| 19 | `reading_source` | `string` |  |
| 20 | `reading_status` | `string` |  |

## `sm_consumption_activity`

- Location: `s3://rel-esg-prod-data-eng-master-record/rel_esg_prod_data_eng_master_record_db.db/sm_consumption_activity`
- Format: ``

| # | Column | Type | Comment |
|---|---|---|---|
| 1 | `activity_name` | `string` |  |
| 2 | `activity_version` | `int` |  |
| 3 | `created_date_time` | `timestamp` |  |
| 4 | `is_deleted` | `boolean` |  |
| 5 | `mpan` | `string` |  |
| 6 | `meter_serial_number` | `string` |  |
| 7 | `meter_register_type` | `string` |  |
| 8 | `date_time` | `timestamp` |  |
| 9 | `date_only` | `date` |  |
| 10 | `id` | `string` |  |
| 11 | `primaryvalue` | `decimal(19,4)` |  |
| 12 | `checksum` | `string` |  |

## `statement_of_account_activity`

- Location: `s3://rel-esg-prod-data-eng-master-record/rel_esg_prod_data_eng_master_record_db.db/statement_of_account_activity`
- Format: ``

| # | Column | Type | Comment |
|---|---|---|---|
| 1 | `activity_name` | `string` |  |
| 2 | `activity_version` | `int` |  |
| 3 | `created_date_time` | `string` |  |
| 4 | `is_deleted` | `boolean` |  |
| 5 | `id` | `string` |  |
| 6 | `bryt_number` | `string` |  |
| 7 | `transaction_type` | `string` |  |
| 8 | `mpan` | `string` |  |
| 9 | `is_migrated` | `boolean` |  |
| 10 | `data` | `string` |  |
| 11 | `checksum` | `string` |  |
| 12 | `invoice_id` | `string` |  |
| 13 | `payment_refund_id` | `string` |  |
| 14 | `external_reference` | `string` |  |
| 15 | `legacy_invoice_reference` | `string` |  |
| 16 | `customer_id` | `string` |  |
| 17 | `account_number` | `string` |  |
| 18 | `account_type` | `string` |  |
| 19 | `billing_group_reference` | `string` |  |
| 20 | `billing_site_reference` | `string` |  |
| 21 | `date` | `string` |  |
| 22 | `created_date` | `string` |  |
| 23 | `method` | `string` |  |
| 24 | `debit_amount` | `decimal(15,2)` |  |
| 25 | `credit_amount` | `decimal(15,2)` |  |
| 26 | `signed_amount` | `decimal(15,2)` |  |

## `supply_activity`

- Location: `s3://rel-esg-prod-data-eng-master-record/rel_esg_prod_data_eng_master_record_db.db/supply_activity`
- Format: ``

| # | Column | Type | Comment |
|---|---|---|---|
| 1 | `activity_name` | `string` |  |
| 2 | `activity_version` | `int` |  |
| 3 | `created_date_time` | `string` |  |
| 4 | `bryt_number` | `string` |  |
| 5 | `customer_id` | `int` |  |
| 6 | `customer_is_deleted` | `boolean` |  |
| 7 | `supplies` | `array<struct<supply_id:int,customer_supply_id:int,mpan:string,site_id:int,promotional_status:int,supply_start_date:date,supply_end_date:date,afms_status:int,registration_date:date,cot_id:string,outgoing_customer_id:string,outgoing_bryt_number:string,move_out_date:string,incoming_customer_id:string,incoming_bryt_number:string,move_in_date:string,cot_undone_date:string,supply_is_deleted:boolean,customer_supply_is_deleted:boolean,supply_registration_is_deleted:boolean,afms_status_last_updated:string,has_been_cotted:boolean>>` |  |
| 8 | `data` | `string` |  |
| 9 | `checksum` | `string` |  |
