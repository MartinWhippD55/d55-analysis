"""
Revenue Forecasting — MLflow Experiment
========================================
Trains multiple models on KPI sales transaction data, logs experiments to MLflow,
compares performance, and registers the best model.

Designed to run in SageMaker Unified Studio notebook environment.

Prerequisites (run in a cell before this script):
    %pip install scikit-learn==1.2.2 mlflow sagemaker-mlflow pandas matplotlib pyarrow
    # Then restart the kernel
"""

import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

# ============================================================================
# CONFIG
# ============================================================================

S3_DATA_PATH = "s3://kpi-demo-data-922850913962-eu-west-1/kpi-gold/finance/gold_sales_transactions/gold_sales_transactions.parquet"
EXPERIMENT_NAME = "Revenue Forecasting"
MLFLOW_TRACKING_URI = "arn:aws:sagemaker:eu-west-1:922850913962:mlflow-tracking-server/tracking-server-4wwmeysrro2ydy-c05lwjjhigt6om-dev"

# ============================================================================
# SETUP MLFLOW
# ============================================================================

import os
os.environ["AWS_STS_REGIONAL_ENDPOINTS"] = "regional"
os.environ["AWS_DEFAULT_REGION"] = "eu-west-1"

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment(EXPERIMENT_NAME)

print(f"MLflow tracking URI: {MLFLOW_TRACKING_URI}")
print(f"Experiment: {EXPERIMENT_NAME}")

# ============================================================================
# LOAD & PREPARE DATA
# ============================================================================

print("\n--- Loading data ---")
df = pd.read_parquet(S3_DATA_PATH)
print(f"Raw data shape: {df.shape}")
print(f"Products: {df['product'].unique().tolist()}")
print(f"Date range: {df['date'].min()} to {df['date'].max()}")

# Aggregate monthly total revenue across all products
df['date'] = pd.to_datetime(df['date'])
monthly_revenue = df.groupby('date')['total_revenue'].sum().reset_index()
monthly_revenue = monthly_revenue.sort_values('date').reset_index(drop=True)

print(f"\nMonthly revenue data: {monthly_revenue.shape[0]} months")
print(monthly_revenue.head())

# ============================================================================
# FEATURE ENGINEERING
# ============================================================================

print("\n--- Feature engineering ---")

monthly_revenue['month'] = monthly_revenue['date'].dt.month
monthly_revenue['quarter'] = monthly_revenue['date'].dt.quarter
monthly_revenue['year'] = monthly_revenue['date'].dt.year
monthly_revenue['month_index'] = range(len(monthly_revenue))

# Lag features
monthly_revenue['revenue_lag1'] = monthly_revenue['total_revenue'].shift(1)
monthly_revenue['revenue_lag2'] = monthly_revenue['total_revenue'].shift(2)
monthly_revenue['revenue_lag3'] = monthly_revenue['total_revenue'].shift(3)

# Rolling features
monthly_revenue['revenue_rolling_3m'] = monthly_revenue['total_revenue'].rolling(3).mean()
monthly_revenue['revenue_rolling_6m'] = monthly_revenue['total_revenue'].rolling(6).mean()

# Drop rows with NaN from lag/rolling
monthly_revenue = monthly_revenue.dropna().reset_index(drop=True)

feature_cols = ['month', 'quarter', 'year',
                'revenue_lag1', 'revenue_lag2', 'revenue_lag3',
                'revenue_rolling_3m', 'revenue_rolling_6m']
target_col = 'total_revenue'

print(f"Features: {feature_cols}")
print(f"Final dataset: {monthly_revenue.shape[0]} rows")

# ============================================================================
# TRAIN/TEST SPLIT
# ============================================================================

# Use 2023 as train, 2024 as test (time-based split)
train = monthly_revenue[monthly_revenue['year'] == 2023]
test = monthly_revenue[monthly_revenue['year'] == 2024]

X_train = train[feature_cols]
y_train = train[target_col]
X_test = test[feature_cols]
y_test = test[target_col]

print(f"\nTrain: {len(X_train)} months (2023)")
print(f"Test: {len(X_test)} months (2024)")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_mape(y_true, y_pred):
    """Mean Absolute Percentage Error"""
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100


def log_prediction_plot(y_test, y_pred, model_name, test_dates):
    """Create and log predictions vs actuals chart"""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(test_dates, y_test.values, 'b-o', label='Actual', linewidth=2)
    ax.plot(test_dates, y_pred, 'r--o', label='Predicted', linewidth=2)
    ax.set_title(f'{model_name} — Predictions vs Actuals (2024)')
    ax.set_xlabel('Date')
    ax.set_ylabel('Total Revenue')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    plot_path = f"/tmp/{model_name.lower().replace(' ', '_')}_predictions.png"
    fig.savefig(plot_path, dpi=100)
    plt.close()
    return plot_path


def train_and_log_model(model, model_name, params, X_train, y_train, X_test, y_test, test_dates):
    """Train a model, evaluate, and log everything to MLflow"""

    with mlflow.start_run(run_name=model_name):
        # Log parameters
        mlflow.log_params(params)
        mlflow.set_tag("model_type", model_name)
        mlflow.set_tag("data_version", "kpi-gold-v1")
        mlflow.set_tag("author", "D55")

        # Train
        model.fit(X_train, y_train)

        # Predict
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)

        # Calculate metrics
        metrics = {
            "rmse_train": np.sqrt(mean_squared_error(y_train, y_pred_train)),
            "rmse_test": np.sqrt(mean_squared_error(y_test, y_pred_test)),
            "mae_test": mean_absolute_error(y_test, y_pred_test),
            "r2_test": r2_score(y_test, y_pred_test),
            "mape_test": calculate_mape(y_test, y_pred_test),
        }

        # Log metrics
        mlflow.log_metrics(metrics)

        # Log prediction plot
        plot_path = log_prediction_plot(y_test, y_pred_test, model_name, test_dates)
        mlflow.log_artifact(plot_path, "plots")

        # Log the model
        mlflow.sklearn.log_model(model, "model", input_example=X_train.iloc[:1])

        # Print results
        print(f"\n{'='*60}")
        print(f"  {model_name}")
        print(f"{'='*60}")
        print(f"  RMSE (test):  £{metrics['rmse_test']:,.0f}")
        print(f"  MAE (test):   £{metrics['mae_test']:,.0f}")
        print(f"  R² (test):    {metrics['r2_test']:.4f}")
        print(f"  MAPE (test):  {metrics['mape_test']:.1f}%")

        return metrics


# ============================================================================
# TRAIN MODELS
# ============================================================================

test_dates = test['date']
results = {}

# --- Model 1: Random Forest ---
print("\n\n--- Training models ---")

rf_params = {"n_estimators": 100, "max_depth": 5, "random_state": 42}
results['Random Forest'] = train_and_log_model(
    model=RandomForestRegressor(**rf_params),
    model_name="Random Forest",
    params={**rf_params, "model_type": "random_forest", "features": len(feature_cols)},
    X_train=X_train, y_train=y_train,
    X_test=X_test, y_test=y_test,
    test_dates=test_dates
)

# --- Model 2: Gradient Boosting (XGBoost-like) ---
gb_params = {"n_estimators": 200, "max_depth": 4, "learning_rate": 0.1, "random_state": 42}
results['Gradient Boosting'] = train_and_log_model(
    model=GradientBoostingRegressor(**gb_params),
    model_name="Gradient Boosting",
    params={**gb_params, "model_type": "gradient_boosting", "features": len(feature_cols)},
    X_train=X_train, y_train=y_train,
    X_test=X_test, y_test=y_test,
    test_dates=test_dates
)

# --- Model 3: Tuned Gradient Boosting ---
gb_tuned_params = {"n_estimators": 500, "max_depth": 3, "learning_rate": 0.05,
                   "subsample": 0.8, "random_state": 42}
results['Gradient Boosting (Tuned)'] = train_and_log_model(
    model=GradientBoostingRegressor(**gb_tuned_params),
    model_name="Gradient Boosting (Tuned)",
    params={**gb_tuned_params, "model_type": "gradient_boosting_tuned", "features": len(feature_cols)},
    X_train=X_train, y_train=y_train,
    X_test=X_test, y_test=y_test,
    test_dates=test_dates
)

# ============================================================================
# SUMMARY & MODEL COMPARISON
# ============================================================================

print("\n\n" + "="*70)
print("  MODEL COMPARISON SUMMARY")
print("="*70)
print(f"{'Model':<30} {'RMSE':>10} {'MAE':>10} {'R²':>8} {'MAPE':>8}")
print("-"*70)

best_model_name = None
best_rmse = float('inf')

for name, metrics in results.items():
    print(f"{name:<30} £{metrics['rmse_test']:>8,.0f} £{metrics['mae_test']:>8,.0f} {metrics['r2_test']:>7.4f} {metrics['mape_test']:>6.1f}%")
    if metrics['rmse_test'] < best_rmse:
        best_rmse = metrics['rmse_test']
        best_model_name = name

print("-"*70)
print(f"\n✓ Best model: {best_model_name} (RMSE: £{best_rmse:,.0f})")

# ============================================================================
# REGISTER BEST MODEL
# ============================================================================

print(f"\n--- Registering best model: {best_model_name} ---")

# Find the run for the best model
runs = mlflow.search_runs(filter_string=f"tags.model_type = '{best_model_name}'")
if runs.empty:
    # Fallback: search by run name
    experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
    runs = mlflow.search_runs(
        experiment_ids=[experiment.experiment_id],
        filter_string=f"attributes.run_name = '{best_model_name}'"
    )

if not runs.empty:
    best_run_id = runs.iloc[0]['run_id']
    model_uri = f"runs:/{best_run_id}/model"

    # Register the model
    model_details = mlflow.register_model(
        model_uri=model_uri,
        name="revenue-forecasting-model"
    )
    print(f"✓ Model registered: {model_details.name} v{model_details.version}")
    print(f"  Run ID: {best_run_id}")
    print(f"  Model URI: {model_uri}")
else:
    print("⚠ Could not find best run to register. Register manually from MLflow UI.")

print("\n--- Done! Check the MLflow UI to compare experiments. ---")
