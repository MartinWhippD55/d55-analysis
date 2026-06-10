"""
ML Pipeline — SageMaker Pipelines
==================================
Creates and executes a SageMaker Pipeline with 3 steps:
  1. Processing: Feature engineering on raw sales data
  2. Training: Train a Random Forest model
  3. Register: Register the model in SageMaker Model Registry

Shows up in Unified Studio under "ML Pipelines" with visual DAG.
"""

import boto3
import sagemaker
import os

# ============================================================================
# CONFIG
# ============================================================================

os.environ["AWS_STS_REGIONAL_ENDPOINTS"] = "regional"
os.environ["AWS_DEFAULT_REGION"] = "eu-west-1"

REGION = "eu-west-1"
S3_DATA_PATH = "s3://kpi-demo-data-922850913962-eu-west-1/kpi-gold/finance/gold_sales_transactions/"
PIPELINE_NAME = "revenue-forecasting-pipeline"
INSTANCE_TYPE = "ml.m5.large"
MODEL_PACKAGE_GROUP = "revenue-forecasting-models"

# ============================================================================
# SETUP
# ============================================================================

sagemaker_session = sagemaker.Session(boto_session=boto3.Session(region_name=REGION))
role = sagemaker.get_execution_role()
default_bucket = sagemaker_session.default_bucket()

print(f"Role: {role}")
print(f"Bucket: {default_bucket}")
print(f"Pipeline: {PIPELINE_NAME}")

# ============================================================================
# STEP 1: PROCESSING — Feature Engineering
# ============================================================================

import tempfile

tmp_dir = tempfile.mkdtemp()

# Write the processing script
processing_script = '''
import os
import pandas as pd
import numpy as np

if __name__ == "__main__":
    input_dir = "/opt/ml/processing/input"
    output_dir = "/opt/ml/processing/output"
    os.makedirs(output_dir, exist_ok=True)

    # Load data
    parquet_files = [f for f in os.listdir(input_dir) if f.endswith(".parquet")]
    df = pd.read_parquet(os.path.join(input_dir, parquet_files[0]))
    print(f"Raw data: {df.shape}")

    # Feature engineering
    df["date"] = pd.to_datetime(df["date"])
    monthly = df.groupby("date")["total_revenue"].sum().reset_index()
    monthly = monthly.sort_values("date").reset_index(drop=True)

    monthly["month"] = monthly["date"].dt.month
    monthly["quarter"] = monthly["date"].dt.quarter
    monthly["year"] = monthly["date"].dt.year
    monthly["revenue_lag1"] = monthly["total_revenue"].shift(1)
    monthly["revenue_lag2"] = monthly["total_revenue"].shift(2)
    monthly["revenue_lag3"] = monthly["total_revenue"].shift(3)
    monthly["revenue_rolling_3m"] = monthly["total_revenue"].rolling(3).mean()
    monthly["revenue_rolling_6m"] = monthly["total_revenue"].rolling(6).mean()
    monthly = monthly.dropna().reset_index(drop=True)

    # Split: 2023 train, 2024 test
    train = monthly[monthly["year"] == 2023].drop(columns=["date"])
    test = monthly[monthly["year"] == 2024].drop(columns=["date"])

    train.to_csv(os.path.join(output_dir, "train.csv"), index=False)
    test.to_csv(os.path.join(output_dir, "test.csv"), index=False)
    print(f"Train: {len(train)} rows, Test: {len(test)} rows")
    print("Processing complete.")
'''

with open(os.path.join(tmp_dir, "processing.py"), "w") as f:
    f.write(processing_script)

# Write the training script
training_script = '''
import os
import argparse
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-estimators", type=int, default=100)
    parser.add_argument("--max-depth", type=int, default=5)
    args, _ = parser.parse_known_args()

    # Load processed data
    input_dir = os.environ.get("SM_CHANNEL_TRAIN", "/opt/ml/input/data/train")
    train = pd.read_csv(os.path.join(input_dir, "train.csv"))
    test = pd.read_csv(os.path.join(input_dir, "test.csv"))

    feature_cols = ["month", "quarter", "year",
                    "revenue_lag1", "revenue_lag2", "revenue_lag3",
                    "revenue_rolling_3m", "revenue_rolling_6m"]

    X_train = train[feature_cols]
    y_train = train["total_revenue"]
    X_test = test[feature_cols]
    y_test = test["total_revenue"]

    # Train
    model = RandomForestRegressor(
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        random_state=42
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    print(f"RMSE: £{rmse:,.0f}")
    print(f"R²: {r2:.4f}")

    # Save model
    model_dir = os.environ.get("SM_MODEL_DIR", "/opt/ml/model")
    joblib.dump(model, os.path.join(model_dir, "model.joblib"))
    print(f"Model saved to {model_dir}")
'''

with open(os.path.join(tmp_dir, "train.py"), "w") as f:
    f.write(training_script)

print("Scripts written.")

# ============================================================================
# DEFINE PIPELINE STEPS
# ============================================================================

from sagemaker.sklearn.processing import SKLearnProcessor
from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker.sklearn import SKLearn
from sagemaker.workflow.steps import ProcessingStep, TrainingStep
from sagemaker.workflow.step_collections import RegisterModel
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.inputs import TrainingInput

print("\n--- Defining pipeline steps ---")

# Step 1: Processing
sklearn_processor = SKLearnProcessor(
    framework_version="1.2-1",
    role=role,
    instance_type=INSTANCE_TYPE,
    instance_count=1,
    sagemaker_session=sagemaker_session,
)

processing_step = ProcessingStep(
    name="FeatureEngineering",
    processor=sklearn_processor,
    code=os.path.join(tmp_dir, "processing.py"),
    inputs=[
        ProcessingInput(
            source=S3_DATA_PATH,
            destination="/opt/ml/processing/input",
        )
    ],
    outputs=[
        ProcessingOutput(
            output_name="processed",
            source="/opt/ml/processing/output",
        )
    ],
)

# Step 2: Training
sklearn_estimator = SKLearn(
    entry_point="train.py",
    source_dir=tmp_dir,
    role=role,
    instance_type=INSTANCE_TYPE,
    instance_count=1,
    framework_version="1.2-1",
    py_version="py3",
    sagemaker_session=sagemaker_session,
    hyperparameters={
        "n-estimators": 100,
        "max-depth": 5,
    },
)

training_step = TrainingStep(
    name="TrainModel",
    estimator=sklearn_estimator,
    inputs={
        "train": TrainingInput(
            s3_data=processing_step.properties.ProcessingOutputConfig.Outputs["processed"].S3Output.S3Uri,
            content_type="text/csv",
        )
    },
)

# Step 3: Register Model
register_step = RegisterModel(
    name="RegisterModel",
    estimator=sklearn_estimator,
    model_data=training_step.properties.ModelArtifacts.S3ModelArtifacts,
    content_types=["application/json"],
    response_types=["application/json"],
    inference_instances=[INSTANCE_TYPE],
    transform_instances=[INSTANCE_TYPE],
    model_package_group_name=MODEL_PACKAGE_GROUP,
)

print("Pipeline steps defined: FeatureEngineering → TrainModel → RegisterModel")

# ============================================================================
# CREATE AND EXECUTE PIPELINE
# ============================================================================

pipeline = Pipeline(
    name=PIPELINE_NAME,
    steps=[processing_step, training_step, register_step],
    sagemaker_session=sagemaker_session,
)

print(f"\n--- Creating pipeline: {PIPELINE_NAME} ---")
pipeline.upsert(role_arn=role)
print("Pipeline created/updated.")

print("\n--- Starting pipeline execution ---")
execution = pipeline.start()
print(f"Execution ARN: {execution.arn}")
print("Pipeline is running. Check Unified Studio → ML Pipelines for progress.")

# Optionally wait for completion (takes ~10 mins)
# execution.wait()
# print(f"Execution status: {execution.describe()['PipelineExecutionStatus']}")
