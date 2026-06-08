# Demo Resources — Teardown Tracker

All resources created for the Northedge demo. Remove after demo is complete.

## Account & Region

- Account: 922850913962
- Region: eu-west-1
- Profile: d55-sagemaker-demo

## Resources

### AWS Config Conformance Packs

| Name | ARN | Status |
|------|-----|--------|
| AI-ML-SageMaker-Security-Governance | arn:aws:config:eu-west-1:922850913962:conformance-pack/AI-ML-SageMaker-Security-Governance/conformance-pack-uday4bbox | Active |
| AI-ML-Supporting-Infrastructure | arn:aws:config:eu-west-1:922850913962:conformance-pack/AI-ML-Supporting-Infrastructure/conformance-pack-xiwvestde | Active |

### DataZone Project

| Name | ID | Profile | Status |
|------|------|---------|--------|
| ML Demo | 5spkm6uqcqyb6e | 3sdbic2ccn5r4m | Active (all 3 environments deployed) |

### MLflow Tracking Server

| Name | Project | Status |
|------|---------|--------|
| tracking-server-5spkm6uqcqyb6e... | ML Demo | Creating (via Unified Studio UI) |

### S3 Artefacts

| Path | Purpose |
|------|---------|
| s3://kpi-demo-data-922850913962-eu-west-1/mlflow-artifacts/ | MLflow artefact store |

### IAM Policy Additions

| Role | Policy Name | Reason |
|------|-------------|--------|
| D55-kpidemo-financials-dev-datazone-execution-role | MLflowTrackingServerPolicy | DataZone execution role lacked SageMaker MLflow permissions. Added `CreateMlflowTrackingServer`, `DescribeMlflowTrackingServer`, etc. + `iam:PassRole` for the SageMaker execution role. Without this, users got "User is not permitted to perform operation: CreateEnvironment" when trying to create an MLflow tracking server from Unified Studio UI. |

### DataZone Blueprint Configurations

| Blueprint | ID | Action |
|-----------|------|--------|
| MLExperiments | 6gm02axbwjor12 | Enabled for eu-west-1, added provisioning role + manage access role + regional parameters (VPC, subnets, S3, AZs) |
| MLflowApp | asdvextzvy4r12 | Enabled for eu-west-1 |

### Project Profile Update

| Profile | ID | Change |
|---------|------|--------|
| KPI Demo Project Profile | 3sdbic2ccn5r4m | Added MLExperiments environment (deployment order 2) |

## Teardown Commands

```bash
# Conformance packs
aws configservice delete-conformance-pack --conformance-pack-name "AI-ML-SageMaker-Security-Governance" --profile d55-sagemaker-demo --region eu-west-1
aws configservice delete-conformance-pack --conformance-pack-name "AI-ML-Supporting-Infrastructure" --profile d55-sagemaker-demo --region eu-west-1

# MLflow tracking server (if created via Unified Studio, delete from UI)
aws sagemaker delete-mlflow-tracking-server --tracking-server-name "tracking-server" --profile d55-sagemaker-demo --region eu-west-1

# MLflow artefacts
aws s3 rm s3://kpi-demo-data-922850913962-eu-west-1/mlflow-artifacts/ --recursive --profile d55-sagemaker-demo --region eu-west-1

# IAM policy added for MLflow
aws iam delete-role-policy --role-name D55-kpidemo-financials-dev-datazone-execution-role --policy-name MLflowTrackingServerPolicy --profile d55-sagemaker-demo --region eu-west-1
```
