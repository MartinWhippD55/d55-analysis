# MLflow Demo — Revenue Forecasting

## Objective

Demonstrate MLflow experiment tracking, model comparison, and model registry using existing KPI financial data in Sagemaker Unified Studio. This is the starting point that feeds into Models, Training Jobs, Inference Endpoints, and ML Pipelines.

## Data

- Source: `s3://kpi-demo-data-922850913962-eu-west-1/kpi-gold/finance/gold_sales_transactions/`
- Shape: 146 rows, monthly frequency (Jan 2023 – Dec 2024)
- Columns: date, product, quantity, unit_price, total_revenue
- Products: Cloud Analytics Suite, Data Integration Platform, ML Ops Toolkit, Real-Time Dashboard, Predictive Insights Engine, Compliance Automation

## Use Case

Revenue forecasting — predict next quarter's revenue by product. Simple enough to explain in a demo, relevant enough for a financial audience.

## Plan

### Step 1: MLflow Experiment Setup

- Create an MLflow experiment in Unified Studio called "Revenue Forecasting"
- This is where all training runs, metrics, and artefacts get logged

### Step 2: Data Preparation

- Load the gold_sales_transactions parquet from S3
- Aggregate to monthly total revenue (already structured this way)
- Split into train (2023) and test (2024) sets
- Feature engineering: month, quarter, lag features, rolling averages

### Step 3: Train Multiple Models (logged to MLflow)

Run 3-4 different approaches so we can show model comparison in the MLflow UI:

1. **Linear Regression** — baseline, simple
2. **Random Forest** — more complex, captures non-linearity
3. **XGBoost** — gradient boosting, likely best performer
4. (Optional) **Prophet** — Facebook's time series library, if available

For each run, log:
- Parameters (hyperparameters, feature set)
- Metrics (RMSE, MAE, R², MAPE)
- Artefacts (model file, feature importance plot, predictions vs actuals chart)
- Tags (model type, data version, author)

### Step 4: Compare Models in MLflow UI

- Show the experiment runs side-by-side
- Compare metrics across approaches
- Visualise parameter vs metric relationships
- This is the "demo moment" — show how easy it is to pick the best model

### Step 5: Register Best Model

- Register the winning model in the MLflow Model Registry
- Add model description, version notes
- Transition to "Staging" stage
- (Links into the Models menu item in Unified Studio)

## What This Demonstrates

| Capability | How It's Shown |
|---|---|
| Experiment tracking | Multiple runs logged with params, metrics, artefacts |
| Model comparison | Side-by-side view in MLflow UI |
| Reproducibility | Every run is versioned with full lineage |
| Model registry | Best model registered, versioned, staged |
| Governance | Clear audit trail of what was tried and why the best model was chosen |

## Next Steps (after MLflow demo is working)

- **Models** → Show the registered model with Model Cards
- **Training Jobs** → Run the training as a managed SageMaker job (not a notebook)
- **Inference Endpoints** → Deploy the registered model for real-time predictions
- **ML Pipelines** → Chain data prep → train → evaluate → register → deploy

## Prerequisites

- MLflow tracking server enabled in the Unified Studio domain
- Notebook environment with access to the S3 data bucket
- Python packages: pandas, scikit-learn, xgboost, mlflow, matplotlib

## Implementation

Notebook will be created at: TBD (within the Unified Studio project)
Local development version: `analysis/NORTHEDGE/sagemaker-unified-studio/notebooks/revenue-forecasting.ipynb`
