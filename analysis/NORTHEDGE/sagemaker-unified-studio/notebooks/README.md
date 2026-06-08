# Revenue Forecasting Notebook

## Files

- `revenue_forecasting.py` — Full script version, ready to run as a Python file or paste into a notebook
- Copy into a SageMaker Unified Studio notebook environment to execute

## Prerequisites

In the notebook environment, install:
```python
%pip install mlflow scikit-learn pandas matplotlib pyarrow
```

## How to Run

1. Open SageMaker Unified Studio → navigate to the appropriate project
2. Create a new notebook (JupyterLab)
3. Copy the contents of `revenue_forecasting.py` into cells
4. Run all cells
5. Open MLflow UI from the Unified Studio sidebar to view experiments

## MLflow Tracking Server

- Name: d55-revenue-forecasting
- URL: https://t-ngg2umhnzhpq.eu-west-1.experiments.sagemaker.aws
- Artefact store: s3://kpi-demo-data-922850913962-eu-west-1/mlflow-artifacts/

## What the Demo Shows

1. Four models trained on the same data, all logged to MLflow
2. Model comparison in the MLflow UI (metrics, params, artefacts side-by-side)
3. Best model automatically registered in the Model Registry
4. Full audit trail: who trained what, when, with which parameters and data
