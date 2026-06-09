# Demo Notes — Sagemaker Unified Studio

Talking points and walkthrough notes for the Northedge demo.

## MLflow Experiment Tracking

**Narrative:** "We trained three models with different configurations, logged them all automatically, and can instantly compare performance to pick the winner — Gradient Boosting with RMSE of £31k."

**Walkthrough:**

1. Show the notebook — quick scroll through feature engineering, model training cells
2. Open MLflow UI → Experiments → "Revenue Forecasting"
3. Tick all 3 runs → Compare → show params and metrics side-by-side
4. Highlight: Gradient Boosting won, it's already registered in the Model Registry
5. Click into a run → show logged params, metrics, prediction plot artifact, model signature

**Key points to land:**
- Zero infrastructure to set up (tracking server provisioned by the platform)
- Every experiment is reproducible — params, code version, data version all tracked
- Model registry gives you a single source of truth for production-ready models
- Compare runs in seconds, not spreadsheets

## Model Registry

**Narrative:** "The best model is automatically registered with full lineage — we know exactly which experiment, which data, and which parameters produced it."

**Walkthrough:**

1. MLflow UI → Models tab → `revenue-forecasting-model`
2. Show version history, linked run, model signature (input/output schema)
3. Point out tags: `data_version: kpi-gold-v1`, `author: D55`

## Remaining Demo Areas (TODO)

- Inference endpoints — deploy registered model as real-time endpoint
- ML pipelines — chain: data prep → train → evaluate → register → deploy
- Generative AI (Playground / AI Apps) — Bedrock model access
