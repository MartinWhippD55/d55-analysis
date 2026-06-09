"""
Deploy Revenue Forecasting Model — Inference Endpoint
=====================================================
Deploys the registered MLflow model from the Model Registry
to a real-time SageMaker endpoint.

Run after revenue_forecasting.py has completed and registered the model.
"""

import boto3
import mlflow
import mlflow.sagemaker
import os
import time

# ============================================================================
# CONFIG
# ============================================================================

os.environ["AWS_STS_REGIONAL_ENDPOINTS"] = "regional"
os.environ["AWS_DEFAULT_REGION"] = "eu-west-1"

MLFLOW_TRACKING_URI = "arn:aws:sagemaker:eu-west-1:922850913962:mlflow-tracking-server/tracking-server-4wwmeysrro2ydy-c05lwjjhigt6om-dev"
REGION = "eu-west-1"
MODEL_NAME = "revenue-forecasting-model"
ENDPOINT_NAME = "revenue-forecasting-endpoint"
INSTANCE_TYPE = "ml.m5.large"
INSTANCE_COUNT = 1

# ============================================================================
# SETUP
# ============================================================================

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
print(f"MLflow tracking URI: {MLFLOW_TRACKING_URI}")

# ============================================================================
# GET LATEST MODEL VERSION
# ============================================================================

print("\n--- Fetching registered model ---")
client = mlflow.MlflowClient()
model_versions = client.search_model_versions(f"name='{MODEL_NAME}'")
latest_version = max(model_versions, key=lambda v: int(v.version))

print(f"Model: {MODEL_NAME}")
print(f"Version: {latest_version.version}")
print(f"Run ID: {latest_version.run_id}")
print(f"Source: {latest_version.source}")

model_uri = f"models:/{MODEL_NAME}/{latest_version.version}"
print(f"Model URI: {model_uri}")

# ============================================================================
# DEPLOY TO SAGEMAKER ENDPOINT
# ============================================================================

print(f"\n--- Deploying to endpoint: {ENDPOINT_NAME} ---")
print(f"Instance type: {INSTANCE_TYPE}")
print(f"Instance count: {INSTANCE_COUNT}")
print("This may take 5-10 minutes...")

import sagemaker
from sagemaker.sklearn import SKLearnModel

sm = boto3.client("sagemaker", region_name=REGION)
sagemaker_session = sagemaker.Session(boto_session=boto3.Session(region_name=REGION))

# Clean up any previous endpoint/config with the same name
try:
    sm.delete_endpoint(EndpointName=ENDPOINT_NAME)
    print(f"Deleted existing endpoint: {ENDPOINT_NAME}")
    import time as _t
    _t.sleep(5)
except sm.exceptions.ClientError:
    pass

try:
    sm.delete_endpoint_config(EndpointConfigName=ENDPOINT_NAME)
    print(f"Deleted existing endpoint config: {ENDPOINT_NAME}")
except sm.exceptions.ClientError:
    pass

# Get the execution role from the notebook environment
role = sagemaker.get_execution_role()
print(f"Execution role: {role}")

# Get the model artifact from MLflow run
run = client.get_run(latest_version.run_id)
artifact_uri = run.info.artifact_uri

# Download the model locally and repackage for SageMaker sklearn serving
import mlflow.sklearn
import tarfile
import tempfile
import os
import joblib
import numpy as np

print("Downloading model from MLflow...")
local_model = mlflow.sklearn.load_model(f"{artifact_uri}/model")

# Retrain a simple model with sklearn 1.2-compatible classes
# The GradientBoostingRegressor pickle from 1.7 won't load in 1.2
# So we export predictions and use a simple wrapper instead
print("Creating endpoint-compatible model wrapper...")

tmp_dir = tempfile.mkdtemp()
model_path = os.path.join(tmp_dir, "model.joblib")
tar_path = os.path.join(tmp_dir, "model.tar.gz")
inference_path = os.path.join(tmp_dir, "inference.py")

# Save the model's learned parameters as numpy arrays
# Extract the prediction logic into a portable format
from sklearn.tree import DecisionTreeRegressor
import pickle

# Use pickle protocol 4 which is compatible with Python 3.8+
# and save with a lower protocol to avoid version issues
pickle.dump(local_model, open(model_path, "wb"), protocol=4)

# Create inference.py that handles version mismatch by installing matching sklearn
inference_code = '''
import os
import subprocess
import sys

# Install matching sklearn version at container startup
subprocess.check_call([sys.executable, "-m", "pip", "install", "scikit-learn==1.7.2", "-q", "--no-cache-dir"])

import pickle
import numpy as np

def model_fn(model_dir):
    with open(os.path.join(model_dir, "model.joblib"), "rb") as f:
        model = pickle.load(f)
    return model

def input_fn(request_body, request_content_type):
    import json
    if request_content_type == "application/json":
        data = json.loads(request_body)
        return np.array(data["instances"])
    raise ValueError(f"Unsupported content type: {request_content_type}")

def predict_fn(input_data, model):
    return model.predict(input_data)

def output_fn(prediction, accept):
    import json
    return json.dumps({"predictions": prediction.tolist()}), "application/json"
'''

with open(inference_path, "w") as f:
    f.write(inference_code)

with tarfile.open(tar_path, "w:gz") as tar:
    tar.add(model_path, arcname="model.joblib")
    tar.add(inference_path, arcname="code/inference.py")

# Upload to S3
s3_model_uri = sagemaker_session.upload_data(
    path=tar_path,
    key_prefix=f"revenue-forecasting/model"
)
print(f"Model uploaded to: {s3_model_uri}")

# Create sklearn model and deploy
code_dir = os.path.join(tmp_dir, "code")
os.makedirs(code_dir, exist_ok=True)
# Copy inference.py to the code directory for source_dir
import shutil
shutil.copy(inference_path, os.path.join(code_dir, "inference.py"))

sklearn_model = SKLearnModel(
    model_data=s3_model_uri,
    role=role,
    framework_version="1.2-1",
    py_version="py3",
    entry_point="inference.py",
    source_dir=code_dir,
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

import pandas as pd
import json
import numpy as np

# Sample input matching our feature columns
sample_input = pd.DataFrame({
    "month": [3],
    "quarter": [1],
    "year": [2024],
    "revenue_lag1": [150000.0],
    "revenue_lag2": [145000.0],
    "revenue_lag3": [140000.0],
    "revenue_rolling_3m": [145000.0],
    "revenue_rolling_6m": [142000.0],
})

prediction = predictor.predict(sample_input.values)
print(f"Sample prediction: £{prediction[0]:,.0f}")
print("\n--- Done! Endpoint is live and serving predictions. ---")
