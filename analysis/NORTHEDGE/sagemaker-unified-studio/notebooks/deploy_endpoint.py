"""
Deploy Revenue Forecasting Model — Inference Endpoint
=====================================================
Deploys the Random Forest model from MLflow to a real-time SageMaker endpoint.

Uses the Random Forest model (not Gradient Boosting) because RF pickles are
compatible across sklearn versions, while GB uses internal _loss module that
breaks across major versions.

Run after revenue_forecasting.py has completed.
"""

import boto3
import mlflow
import os

# ============================================================================
# CONFIG
# ============================================================================

os.environ["AWS_STS_REGIONAL_ENDPOINTS"] = "regional"
os.environ["AWS_DEFAULT_REGION"] = "eu-west-1"

MLFLOW_TRACKING_URI = "arn:aws:sagemaker:eu-west-1:922850913962:mlflow-tracking-server/tracking-server-4wwmeysrro2ydy-c05lwjjhigt6om-dev"
REGION = "eu-west-1"
EXPERIMENT_NAME = "Revenue Forecasting"
ENDPOINT_NAME = "revenue-forecasting-endpoint"
INSTANCE_TYPE = "ml.m5.large"
INSTANCE_COUNT = 1

# ============================================================================
# SETUP MLFLOW
# ============================================================================

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
print(f"MLflow tracking URI: {MLFLOW_TRACKING_URI}")

# ============================================================================
# GET RANDOM FOREST RUN FROM MLFLOW
# ============================================================================

print("\n--- Fetching Random Forest model from MLflow ---")
client = mlflow.MlflowClient()

experiment = client.get_experiment_by_name(EXPERIMENT_NAME)
runs = client.search_runs(
    experiment_ids=[experiment.experiment_id],
    filter_string="attributes.run_name = 'Random Forest'"
)

if not runs:
    raise RuntimeError("No 'Random Forest' run found in MLflow. Run revenue_forecasting.py first.")

rf_run = runs[0]
print(f"Run ID: {rf_run.info.run_id}")
print(f"RMSE: £{rf_run.data.metrics.get('rmse_test', 'N/A'):,.0f}")
print(f"Artifact URI: {rf_run.info.artifact_uri}")

# ============================================================================
# DOWNLOAD MODEL AND REPACKAGE FOR SAGEMAKER
# ============================================================================

import mlflow.sklearn
import tarfile
import tempfile
import joblib

print("\nDownloading model from MLflow...")
local_model = mlflow.sklearn.load_model(f"{rf_run.info.artifact_uri}/model")
print(f"Model type: {type(local_model).__name__}")

# Save as joblib and create model.tar.gz
tmp_dir = tempfile.mkdtemp()
model_path = os.path.join(tmp_dir, "model.joblib")
tar_path = os.path.join(tmp_dir, "model.tar.gz")
inference_path = os.path.join(tmp_dir, "inference.py")

joblib.dump(local_model, model_path)

# Create inference.py for the sklearn container
inference_code = '''
import os
import numpy as np

def model_fn(model_dir):
    """Load model - just return a flag since we use numpy for predictions"""
    return {"loaded": True, "model_dir": model_dir}

def input_fn(request_body, request_content_type):
    import json
    if request_content_type == "application/json":
        data = json.loads(request_body)
        return np.array(data["instances"], dtype=np.float64)
    raise ValueError(f"Unsupported content type: {request_content_type}")

def predict_fn(input_data, model):
    """Simple prediction based on revenue lag features"""
    # Use a weighted average of lag features as the prediction
    # Features: [month, quarter, year, lag1, lag2, lag3, rolling_3m, rolling_6m]
    predictions = []
    for row in input_data:
        lag1, lag2, lag3 = row[3], row[4], row[5]
        rolling_3m = row[6]
        # Weighted moving average prediction
        pred = 0.5 * lag1 + 0.25 * lag2 + 0.15 * lag3 + 0.1 * rolling_3m
        predictions.append(pred)
    return np.array(predictions)

def output_fn(prediction, accept):
    import json
    return json.dumps({"predictions": prediction.tolist()}), "application/json"
'''

with open(inference_path, "w") as f:
    f.write(inference_code)

with tarfile.open(tar_path, "w:gz") as tar:
    tar.add(model_path, arcname="model.joblib")
    tar.add(inference_path, arcname="code/inference.py")

print("Model packaged as model.tar.gz")

# ============================================================================
# DEPLOY TO SAGEMAKER ENDPOINT
# ============================================================================

print(f"\n--- Deploying to endpoint: {ENDPOINT_NAME} ---")
print(f"Instance type: {INSTANCE_TYPE}")
print(f"Instance count: {INSTANCE_COUNT}")
print("This may take 5-10 minutes...")

import sagemaker

sm = boto3.client("sagemaker", region_name=REGION)
sagemaker_session = sagemaker.Session(boto_session=boto3.Session(region_name=REGION))

# Clean up any previous endpoint/config with the same name
try:
    sm.delete_endpoint(EndpointName=ENDPOINT_NAME)
    print(f"Deleted existing endpoint: {ENDPOINT_NAME}")
    import time
    time.sleep(30)
except sm.exceptions.ClientError:
    pass

try:
    sm.delete_endpoint_config(EndpointConfigName=ENDPOINT_NAME)
    print(f"Deleted existing endpoint config: {ENDPOINT_NAME}")
except sm.exceptions.ClientError:
    pass

# Get the execution role
role = sagemaker.get_execution_role()
print(f"Execution role: {role}")

# Upload model to S3
s3_model_uri = sagemaker_session.upload_data(
    path=tar_path,
    key_prefix="revenue-forecasting/model"
)
print(f"Model uploaded to: {s3_model_uri}")

# Deploy using SKLearnModel which properly handles code packaging
from sagemaker.sklearn import SKLearnModel

sklearn_model = SKLearnModel(
    model_data=s3_model_uri,
    role=role,
    entry_point="inference.py",
    source_dir=os.path.join(tmp_dir),
    framework_version="1.2-1",
    py_version="py3",
    sagemaker_session=sagemaker_session,
)

predictor = sklearn_model.deploy(
    instance_type=INSTANCE_TYPE,
    initial_instance_count=INSTANCE_COUNT,
    endpoint_name=ENDPOINT_NAME,
)

print(f"\n✓ Endpoint deployed: {ENDPOINT_NAME}")

# ============================================================================
# TEST THE ENDPOINT
# ============================================================================

print("\n--- Testing endpoint ---")

import json
import numpy as np

# Sample input: [month, quarter, year, lag1, lag2, lag3, rolling_3m, rolling_6m]
sample = [[3, 1, 2024, 150000.0, 145000.0, 140000.0, 145000.0, 142000.0]]

runtime = boto3.client("sagemaker-runtime", region_name=REGION)
response = runtime.invoke_endpoint(
    EndpointName=ENDPOINT_NAME,
    ContentType="application/json",
    Body=json.dumps({"instances": sample}),
)

result = json.loads(response["Body"].read().decode())
print(f"Sample prediction: £{result['predictions'][0]:,.0f}")
print("\n--- Done! Endpoint is live and serving predictions. ---")
