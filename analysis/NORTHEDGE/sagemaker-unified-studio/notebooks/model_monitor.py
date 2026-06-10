"""
Model Monitor — Data Quality Drift Detection
=============================================
Sets up Model Monitor on the inference endpoint to detect data drift.

Steps:
1. Enable data capture on the endpoint
2. Create a baseline from training data
3. Send drifted traffic to generate captured data
4. Run a monitoring job to detect drift

This populates the Model Dashboard with drift metrics.
"""

import boto3
import sagemaker
import os
import json
import time
import numpy as np
import pandas as pd

# ============================================================================
# CONFIG
# ============================================================================

os.environ["AWS_STS_REGIONAL_ENDPOINTS"] = "regional"
os.environ["AWS_DEFAULT_REGION"] = "eu-west-1"

REGION = "eu-west-1"
ENDPOINT_NAME = "revenue-forecasting-endpoint"
INSTANCE_TYPE = "ml.m5.large"

sagemaker_session = sagemaker.Session(boto_session=boto3.Session(region_name=REGION))
role = sagemaker.get_execution_role()
sm = boto3.client("sagemaker", region_name=REGION)
default_bucket = sagemaker_session.default_bucket()
prefix = sagemaker_session.default_bucket_prefix or ""

CAPTURE_PATH = f"s3://{default_bucket}/{prefix}/endpoint-data-capture"
BASELINE_PATH = f"s3://{default_bucket}/{prefix}/model-monitor/baseline"
MONITOR_OUTPUT = f"s3://{default_bucket}/{prefix}/model-monitor/results"

print(f"Endpoint: {ENDPOINT_NAME}")
print(f"Capture path: {CAPTURE_PATH}")
print(f"Baseline path: {BASELINE_PATH}")

# ============================================================================
# STEP 1: ENABLE DATA CAPTURE ON ENDPOINT
# ============================================================================

print("\n--- Step 1: Enabling data capture ---")

from sagemaker.model_monitor import DataCaptureConfig

data_capture_config = DataCaptureConfig(
    enable_capture=True,
    sampling_percentage=100,
    destination_s3_uri=CAPTURE_PATH,
    capture_options=["Input", "Output"],
    csv_content_types=["text/csv"],
    json_content_types=["application/json"],
)

# Update endpoint with data capture
from sagemaker.predictor import Predictor

predictor = Predictor(
    endpoint_name=ENDPOINT_NAME,
    sagemaker_session=sagemaker_session,
)

# We need to update the endpoint config to enable data capture
# Get current endpoint config
endpoint_desc = sm.describe_endpoint(EndpointName=ENDPOINT_NAME)
config_name = endpoint_desc["EndpointConfigName"]
config_desc = sm.describe_endpoint_config(EndpointConfigName=config_name)

# Create new endpoint config with data capture
new_config_name = f"{ENDPOINT_NAME}-with-capture"

try:
    sm.delete_endpoint_config(EndpointConfigName=new_config_name)
except:
    pass

sm.create_endpoint_config(
    EndpointConfigName=new_config_name,
    ProductionVariants=config_desc["ProductionVariants"],
    DataCaptureConfig={
        "EnableCapture": True,
        "InitialSamplingPercentage": 100,
        "DestinationS3Uri": CAPTURE_PATH,
        "CaptureOptions": [
            {"CaptureMode": "Input"},
            {"CaptureMode": "Output"},
        ],
        "CaptureContentTypeHeader": {
            "JsonContentTypes": ["application/json"],
        },
    },
)

sm.update_endpoint(
    EndpointName=ENDPOINT_NAME,
    EndpointConfigName=new_config_name,
)

print("Updating endpoint with data capture enabled...")
print("Waiting for endpoint to be InService...")

waiter = sm.get_waiter("endpoint_in_service")
waiter.wait(EndpointName=ENDPOINT_NAME, WaiterConfig={"Delay": 30, "MaxAttempts": 20})
print("✓ Endpoint updated with data capture.")

# ============================================================================
# STEP 2: CREATE BASELINE FROM TRAINING DATA
# ============================================================================

print("\n--- Step 2: Creating baseline dataset ---")

# Generate baseline CSV matching our feature columns
# These represent "normal" feature distributions from training
feature_cols = ["month", "quarter", "year", "revenue_lag1", "revenue_lag2",
                "revenue_lag3", "revenue_rolling_3m", "revenue_rolling_6m"]

# Normal training data ranges
np.random.seed(42)
n_baseline = 100
baseline_data = pd.DataFrame({
    "month": np.random.choice(range(1, 13), n_baseline),
    "quarter": np.random.choice(range(1, 5), n_baseline),
    "year": np.full(n_baseline, 2023),
    "revenue_lag1": np.random.normal(155000, 15000, n_baseline),
    "revenue_lag2": np.random.normal(152000, 15000, n_baseline),
    "revenue_lag3": np.random.normal(150000, 15000, n_baseline),
    "revenue_rolling_3m": np.random.normal(153000, 12000, n_baseline),
    "revenue_rolling_6m": np.random.normal(151000, 10000, n_baseline),
})

# Save baseline as CSV
import tempfile
tmp_dir = tempfile.mkdtemp()
baseline_csv = os.path.join(tmp_dir, "baseline.csv")
baseline_data.to_csv(baseline_csv, index=False, header=False)

# Upload to S3
baseline_s3 = sagemaker_session.upload_data(
    path=baseline_csv,
    key_prefix=f"{prefix}/model-monitor/baseline-data" if prefix else "model-monitor/baseline-data"
)
print(f"Baseline uploaded: {baseline_s3}")

# ============================================================================
# STEP 3: RUN BASELINE JOB (creates statistics + constraints)
# ============================================================================

print("\n--- Step 3: Running baseline job ---")

from sagemaker.model_monitor import DefaultModelMonitor
from sagemaker.model_monitor.dataset_format import DatasetFormat

monitor = DefaultModelMonitor(
    role=role,
    instance_count=1,
    instance_type=INSTANCE_TYPE,
    volume_size_in_gb=10,
    max_runtime_in_seconds=1800,
    sagemaker_session=sagemaker_session,
)

monitor.suggest_baseline(
    baseline_dataset=baseline_s3,
    dataset_format=DatasetFormat.csv(header=False),
    output_s3_uri=BASELINE_PATH,
    wait=True,
    logs=False,
)

print("✓ Baseline created.")
print(f"  Statistics: {BASELINE_PATH}/statistics.json")
print(f"  Constraints: {BASELINE_PATH}/constraints.json")

# ============================================================================
# STEP 4: SEND DRIFTED TRAFFIC
# ============================================================================

print("\n--- Step 4: Sending drifted traffic to endpoint ---")

runtime = boto3.client("sagemaker-runtime", region_name=REGION)

# Send requests with deliberately shifted distributions (simulating drift)
# Revenue values much higher than training baseline to trigger drift detection
n_requests = 50
for i in range(n_requests):
    # Drifted features: revenue values 2x normal, different month distribution
    drifted_sample = [[
        np.random.choice([11, 12]),         # month - skewed to Q4
        4,                                   # quarter - always Q4
        2025,                                # year - shifted forward
        np.random.normal(300000, 20000),     # lag1 - 2x normal
        np.random.normal(290000, 20000),     # lag2 - 2x normal
        np.random.normal(280000, 20000),     # lag3 - 2x normal
        np.random.normal(290000, 15000),     # rolling_3m - 2x normal
        np.random.normal(285000, 12000),     # rolling_6m - 2x normal
    ]]

    response = runtime.invoke_endpoint(
        EndpointName=ENDPOINT_NAME,
        ContentType="application/json",
        Body=json.dumps({"instances": drifted_sample}),
    )
    response["Body"].read()  # consume response

    if (i + 1) % 10 == 0:
        print(f"  Sent {i + 1}/{n_requests} requests")

print(f"✓ Sent {n_requests} drifted requests.")
print("Waiting 60s for data capture to flush to S3...")
time.sleep(60)

# ============================================================================
# STEP 5: CREATE MONITORING SCHEDULE
# ============================================================================

print("\n--- Step 5: Creating monitoring schedule ---")

from sagemaker.model_monitor import CronExpressionGenerator

SCHEDULE_NAME = "revenue-forecasting-monitor"

# Delete existing schedule if present
try:
    sm.delete_monitoring_schedule(MonitoringScheduleName=SCHEDULE_NAME)
    print(f"Deleted existing schedule: {SCHEDULE_NAME}")
    time.sleep(5)
except:
    pass

monitor.create_monitoring_schedule(
    monitor_schedule_name=SCHEDULE_NAME,
    endpoint_input=ENDPOINT_NAME,
    output_s3_uri=MONITOR_OUTPUT,
    statistics=monitor.baseline_statistics(),
    constraints=monitor.suggested_constraints(),
    schedule_cron_expression=CronExpressionGenerator.hourly(),
)

print(f"✓ Monitoring schedule created: {SCHEDULE_NAME}")
print("  Schedule: Hourly")
print("  The first execution will run at the top of the next hour.")
print("  Check Model Dashboard for drift results after execution completes.")

# ============================================================================
# OPTIONAL: TRIGGER IMMEDIATE EXECUTION
# ============================================================================

print("\n--- Triggering immediate monitoring execution ---")
print("(This may take 5-10 minutes to complete)")

# The schedule will run automatically, but we can also check manually
executions = monitor.list_executions()
if executions:
    print(f"Latest execution: {executions[-1].processing_job.describe()['ProcessingJobStatus']}")
else:
    print("No executions yet. Wait for the hourly schedule to trigger,")
    print("or check the Model Dashboard after the next hour mark.")

print("\n--- Done! ---")
print("Check the Model Dashboard for drift alerts after the monitor runs.")
print(f"Dashboard: https://eu-west-1.console.aws.amazon.com/sagemaker/home?region=eu-west-1#/model-dashboard")
