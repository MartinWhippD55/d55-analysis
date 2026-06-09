"""
Submit Training Job — SageMaker Managed Training
=================================================
Submits the revenue forecasting training as a SageMaker Training Job.
This runs on dedicated compute, shows up in the Training Jobs UI,
and logs results to MLflow.

Run this from the notebook after the MLflow setup cell.
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
INSTANCE_TYPE = "ml.m5.large"
JOB_NAME_PREFIX = "revenue-forecasting"

# ============================================================================
# SETUP
# ============================================================================

sagemaker_session = sagemaker.Session(boto_session=boto3.Session(region_name=REGION))
role = sagemaker.get_execution_role()
print(f"Execution role: {role}")
print(f"S3 data: {S3_DATA_PATH}")

# ============================================================================
# CREATE TRAINING SCRIPT
# ============================================================================

import tempfile

tmp_dir = tempfile.mkdtemp()
script_path = os.path.join(tmp_dir, "train.py")

training_script = '''
import argparse
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings("ignore")

def calculate_mape(y_true, y_pred):
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args, _ = parser.parse_known_args()

    # Load data from the input channel
    input_dir = os.environ.get("SM_CHANNEL_TRAINING", "/opt/ml/input/data/training")
    print(f"Loading data from: {input_dir}")

    # Find parquet files
    parquet_files = [f for f in os.listdir(input_dir) if f.endswith(".parquet")]
    df = pd.read_parquet(os.path.join(input_dir, parquet_files[0]))
    print(f"Raw data shape: {df.shape}")

    # Feature engineering
    df["date"] = pd.to_datetime(df["date"])
    monthly_revenue = df.groupby("date")["total_revenue"].sum().reset_index()
    monthly_revenue = monthly_revenue.sort_values("date").reset_index(drop=True)

    monthly_revenue["month"] = monthly_revenue["date"].dt.month
    monthly_revenue["quarter"] = monthly_revenue["date"].dt.quarter
    monthly_revenue["year"] = monthly_revenue["date"].dt.year
    monthly_revenue["revenue_lag1"] = monthly_revenue["total_revenue"].shift(1)
    monthly_revenue["revenue_lag2"] = monthly_revenue["total_revenue"].shift(2)
    monthly_revenue["revenue_lag3"] = monthly_revenue["total_revenue"].shift(3)
    monthly_revenue["revenue_rolling_3m"] = monthly_revenue["total_revenue"].rolling(3).mean()
    monthly_revenue["revenue_rolling_6m"] = monthly_revenue["total_revenue"].rolling(6).mean()
    monthly_revenue = monthly_revenue.dropna().reset_index(drop=True)

    feature_cols = ["month", "quarter", "year",
                    "revenue_lag1", "revenue_lag2", "revenue_lag3",
                    "revenue_rolling_3m", "revenue_rolling_6m"]

    train = monthly_revenue[monthly_revenue["year"] == 2023]
    test = monthly_revenue[monthly_revenue["year"] == 2024]

    X_train = train[feature_cols]
    y_train = train["total_revenue"]
    X_test = test[feature_cols]
    y_test = test["total_revenue"]

    print(f"Train: {len(X_train)} months, Test: {len(X_test)} months")

    # Train models
    models = {
        "Random Forest": (RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42),
                         {"n_estimators": 100, "max_depth": 5, "random_state": 42}),
        "Gradient Boosting": (GradientBoostingRegressor(n_estimators=200, max_depth=4, learning_rate=0.1, random_state=42),
                             {"n_estimators": 200, "max_depth": 4, "learning_rate": 0.1, "random_state": 42}),
        "Gradient Boosting (Tuned)": (GradientBoostingRegressor(n_estimators=500, max_depth=3, learning_rate=0.05, subsample=0.8, random_state=42),
                                     {"n_estimators": 500, "max_depth": 3, "learning_rate": 0.05, "subsample": 0.8, "random_state": 42}),
    }

    best_rmse = float("inf")
    best_model_name = None

    for name, (model, params) in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        mape = calculate_mape(y_test, y_pred)

        print(f"{name}: RMSE=£{rmse:,.0f}, MAE=£{mae:,.0f}, R²={r2:.4f}, MAPE={mape:.1f}%")

        if rmse < best_rmse:
            best_rmse = rmse
            best_model_name = name

    print(f"\\nBest model: {best_model_name} (RMSE: £{best_rmse:,.0f})")

    # Save model artifact
    model_dir = os.environ.get("SM_MODEL_DIR", "/opt/ml/model")
    import joblib
    joblib.dump(models[best_model_name][0], os.path.join(model_dir, "model.joblib"))
    print(f"Model saved to {model_dir}")
'''

with open(script_path, "w") as f:
    f.write(training_script)

print(f"Training script written to: {script_path}")

# ============================================================================
# SUBMIT TRAINING JOB
# ============================================================================

from sagemaker.sklearn import SKLearn

print(f"\n--- Submitting training job ---")
print(f"Instance type: {INSTANCE_TYPE}")

estimator = SKLearn(
    entry_point="train.py",
    source_dir=tmp_dir,
    role=role,
    instance_type=INSTANCE_TYPE,
    instance_count=1,
    framework_version="1.2-1",
    py_version="py3",
    base_job_name=JOB_NAME_PREFIX,
    sagemaker_session=sagemaker_session,
)

estimator.fit({"training": S3_DATA_PATH}, wait=True, logs="All")

print(f"\n✓ Training job completed: {estimator.latest_training_job.name}")
print(f"Model artifact: {estimator.model_data}")
