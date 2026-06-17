# D55 Demo Environment - Cost Savings Analysis

**Account:** 922850913962 (`d55-demo`)  
**Region:** eu-west-1  
**Period analysed:** 1–15 June 2026

## Current Monthly Burn (projected from half-month)

| Service | Cost (half-month) | Projected/month | Notes |
|---------|-------------------|-----------------|-------|
| QuickSight | $326 | ~$652 | Enterprise edition, 7 admin users |
| SageMaker | $252 | ~$504 | 21 domains + 1 real-time endpoint (ml.m5.large) |
| VPC | $209 | ~$418 | 1 NAT GW + 23 Interface VPC Endpoints across 2 VPCs |
| Kiro | $93 | ~$186 | IDE usage |
| EC2 + EC2-Other | $56 | ~$113 | 1 stopped t3.medium + NAT/EIP charges |
| RDS | $25 | ~$50 | Aurora PostgreSQL Serverless v2 (northwind-1, 0.5–18 ACU) |
| AWS Config | $7 | ~$14 | Config rule evaluations |
| CloudTrail | $3 | ~$6 | — |
| Other (Inspector, Glue, KMS, etc.) | ~$7 | ~$14 | — |
| **Total projected** | **~$978** | **~$1,957/month** | |

## Top Savings Opportunities

### 1. QuickSight Enterprise — ~$652/month potential savings

You have 7 users all at ADMIN role on Enterprise edition. For a demo environment:

- **Option A: Downgrade to Standard edition** — No paginated reports, no row-level security, but significantly cheaper reader sessions. However, you can't downgrade an existing subscription; you'd need to unsubscribe and re-subscribe.
- **Option B: Reduce to 1 admin user** — Enterprise is $18/author/month + $250 SPICE capacity. With 7 authors that's $126/month just for authors, but your $326/half-month suggests Q or session-based pricing is in play.
- **Option C: Delete the subscription entirely between demos** — Dashboards can be rebuilt from IaC/templates. This is the nuclear option but saves the most.

**Recommendation:** If the dashboards are only needed during demos, export the dashboard definitions (CloudFormation/CDK), delete the QS subscription, and recreate ahead of demos.

### 2. SageMaker Real-Time Endpoint — ~$140/month savings

`revenue-forecasting-endpoint` is running an `ml.m5.large` 24/7. This costs about $0.134/hr = $97/month minimum.

**Action:** Delete the endpoint between demos. Redeploy from the model artifact when needed (takes ~5-10 minutes):
```bash
aws sagemaker delete-endpoint --endpoint-name revenue-forecasting-endpoint --profile d55-demo --region eu-west-1
```

### 3. VPC Interface Endpoints — ~$240/month savings

You have **23 Interface VPC Endpoints** across 2 VPCs. Each costs ~$0.01/hr/AZ = ~$7.20/month minimum per endpoint (single AZ). That's roughly $166–$240/month just for endpoints.

Many of these exist for SageMaker Unified Studio. If the studio isn't in active use between demos:

**Action:** Delete the VPC endpoints from the `D55-kpidemo-financials-dev-vpc` (14 endpoints) when not demoing. Recreate via IaC before demos.

### 4. NAT Gateway — ~$45/month savings

`q-nat` (nat-0bf1ad11d21e6620e) in the Control Tower VPC costs ~$32/month fixed + data processing.

**Action:** Delete when not in use. Only needed if resources in private subnets need internet access during the demo.

### 5. SageMaker Unified Studio Domains — potential cost contributor

You have **21 SageMaker domains**, most from Feb–June 2026. While domains themselves are free when idle, they create supporting infrastructure (VPC endpoints, EFS mounts, etc.) that does cost money.

**Action:** Delete old/unused domains. Keep only the 1-2 needed for the next demo:
- Most recent: `d-zdz0ggin0nzp` (8 Jun) and `d-pugfkzzucaoo` (8 Jun)
- Consider deleting everything from April and earlier

### 6. Unattached Elastic IP — ~$3.60/month

`eipalloc-08196e973ee0c9fb6` (34.249.28.17) is not associated with anything.

**Action:** Release it immediately:
```bash
aws ec2 release-address --allocation-id eipalloc-08196e973ee0c9fb6 --profile d55-demo --region eu-west-1
```

### 7. Aurora Serverless v2 — keep but verify min ACU

`northwind-1` scales 0.5–18 ACU. At idle it's 0.5 ACU = ~$0.065/hr = $47/month. This is reasonable for a demo DB that needs quick startup.

**Action:** Could stop the cluster between demos (`aws rds stop-db-cluster`), but it auto-restarts after 7 days. Good for weekly demos; less useful for longer gaps.

## Quick Win Summary

| Action | Monthly Saving | Effort | Reversibility |
|--------|---------------|--------|---------------|
| Delete SageMaker endpoint | ~$97 | Low (1 CLI command) | Easy redeploy |
| Release unassociated EIP | ~$4 | Trivial | New IP on recreate |
| Delete NAT Gateway when idle | ~$45 | Low | Recreate + update routes |
| Delete VPC endpoints (dev VPC) | ~$100–170 | Medium (IaC needed for restore) | IaC redeploy |
| Clean up old SageMaker domains | Indirect (reduces VPC endpoint need) | Medium | — |
| Stop Aurora cluster | ~$47 | Low (auto-restarts after 7d) | Auto |
| Rationalise QuickSight | ~$300–650 | High (re-subscribe workflow) | Dashboards from templates |

**Conservative quick wins (low effort):** ~$190/month  
**Aggressive teardown (all of the above):** ~$800–1,000/month
