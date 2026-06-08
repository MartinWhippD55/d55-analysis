# Session Notes — 8 June 2026

## Context

D55 is a consultancy. Rhys (CTO) is preparing for a meeting with Northedge (PE house) who back Cezanne (HR/payroll SaaS company). Northedge are unhappy with Cezanne's pace and cost, and have moved the CTO out. D55's angle is to show we can help them adopt AI to become more productive.

There are two workstreams here:

1. **AI Forum prep** (`analysis/NORTHEDGE/ai-forum/`) — talking points, frameworks, and a PowerPoint deck for the Northedge meeting. This is largely complete (see `focus.md` for the full brief).

2. **Sagemaker Unified Studio demos** (`analysis/NORTHEDGE/sagemaker-unified-studio/`) — building working demo content to showcase capabilities. Rhys wants demos across the AI/ML menu items in Unified Studio (MLflow, Models, Training Jobs, Inference Endpoints, ML Pipelines) and the Generative AI section (Playground, AI Apps).

## What We've Done

### Security & Governance (Complete)
- Deployed 2 AWS Config conformance packs (SageMaker + Supporting Infrastructure)
- Both active and producing findings (2 non-compliant domains, 40+ infra issues)
- Demo-ready via Config console: `https://eu-west-1.console.aws.amazon.com/config/home?region=eu-west-1#/conformance-packs`

### MLflow Setup (In Progress)
- Enabled MLExperiments blueprint at domain level (with provisioning roles + regional params)
- Updated project profile to include MLExperiments environment
- Created new project "ML Demo" (ID: `5spkm6uqcqyb6e`) — all 3 environments deployed successfully
- MLflow tracking server is **creating** within the project (takes 10-15 mins)
- Added Martin + Rhys as project owners
- Revenue forecasting notebook written and ready to run (`notebooks/revenue_forecasting.py`)

## What to Do When Picking Up Tomorrow

### 1. Check MLflow Tracking Server Status
- Go to Unified Studio → "ML Demo" project → Compute → MLflow tab
- Should show status "Active" with an "Open" link
- Click Open to confirm MLflow UI is accessible

### 2. Run the Revenue Forecasting Notebook
- In "ML Demo" project, open a notebook (Spaces → JupyterLab)
- Copy contents of `notebooks/revenue_forecasting.py` into cells
- May need to update the `MLFLOW_TRACKING_URI` — in Unified Studio notebooks it should auto-connect, so try removing the explicit `mlflow.set_tracking_uri()` line first
- Install deps: `%pip install mlflow scikit-learn pandas matplotlib pyarrow`
- Run all cells
- Verify experiments appear in MLflow UI

### 3. Demo Walkthrough
- MLflow UI: show 4 model runs, compare metrics side-by-side
- Model Registry: show the registered best model
- This covers: MLflow, Models, Training jobs (within notebook)

### 4. Remaining Demo Areas (Not Started)
- **Inference endpoints** — deploy the registered model as a real-time endpoint
- **ML pipelines** — chain data prep → train → evaluate → register → deploy
- **Generative AI (Playground / AI apps)** — needs Bedrock model access check
- **Partner AI apps** — low priority

## Key Details

- AWS Profile: `d55-sagemaker-demo`
- Account: `922850913962`
- Region: `eu-west-1`
- Domain: `dzd-6vhyd0ynnh742e`
- Portal: `https://dzd-6vhyd0ynnh742e.sagemaker.eu-west-1.on.aws`
- Project "ML Demo": `5spkm6uqcqyb6e`

## Issues Encountered & Fixed

1. MLExperiments blueprint wasn't enabled → enabled via `put-environment-blueprint-configuration`
2. Blueprint missing provisioning role + regional params → added to match Tooling blueprint config
3. DataZone execution role missing MLflow permissions → added `MLflowTrackingServerPolicy` inline policy to `D55-kpidemo-financials-dev-datazone-execution-role`
4. Existing projects don't pick up new environments (ON_CREATE mode) → had to create new project "ML Demo"
5. Bedrock Config rules not available in eu-west-1 → parked for now
6. The "RDD - Finance v2" project cannot use MLflow — it was created before MLExperiments was in the profile. Only the new "ML Demo" project has it.

## Related Files

- `focus.md` in `ai-forum/` — the full talking points brief for Rhys
- `security-governance.md` — documenting the Config/CloudTrail/Governance angle
- `mlflow.md` — the plan for the MLflow demo (data, models, steps)
- `notebooks/revenue_forecasting.py` — the actual notebook script to run
- `resources.md` — all AWS resources created + teardown commands
- `conformance-packs/` — the YAML templates deployed to AWS Config
