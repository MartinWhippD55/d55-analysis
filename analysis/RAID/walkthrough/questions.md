# Raid / Venatrix — Questions & Areas to Investigate

Split into: (A) what to send Dom in advance, and (B) things for us to dig into / decide.

---

## A. To send Dom ahead of the call

Frame these as "areas we'd like the walkthrough to cover" so their team can prep.

### Codebase & architecture
- [ ] High-level architecture of Venatrix — how the Svelte/Vite frontend, TypeScript, and
      Python/LangGraph backend fit together.
- [ ] The LangGraph agent design: what graphs/nodes/tools exist, what a typical "agent
      run" looks like end to end.
- [ ] Where the boundaries are between components (services, repos, deployables).
- [ ] Current repo layout, build, and local dev setup (feeds the onboarding docs deliverable).

### Observability (primary focus)
- [ ] What agent metrics matter most to them today (latency, token/cost, tool calls,
      success/failure, human-in-the-loop steps, etc.).
- [ ] What they capture today vs. what's missing — any existing logging/telemetry.
- [ ] Who consumes the metrics and for what decisions (product impact, cost, debugging)?
- [ ] Any existing "central database" or is that greenfield?

### Hosting & infra
- [ ] Current hosting/deployment setup for Venatrix (if any) and pain points.
- [ ] Existing AWS footprint, accounts, and any org/landing-zone conventions to respect.
- [ ] Current CI/CD, IaC (Terraform/CDK/other?), and secret management approach.
- [ ] Environments they need (dev/test/staging/prod?) and any compliance constraints.

### Data & security
- [ ] Data residency requirements in detail (UK/EU? specific regions?).
- [ ] Sensitivity/classification of agent inputs, outputs, and logs (any PII, client
      pentest data, findings?).
- [ ] Constraints on third-party/SaaS observability tools given they are a security firm.

### Logistics
- [ ] Will we get read access to the repo(s) before or during the call?
- [ ] Recording allowed? Who owns follow-up actions?

---

## B. For us to investigate / decide (internal)

### Observability approach
- [ ] LangGraph-native options: LangSmith vs. self-hosted tracing vs. OpenTelemetry.
      Trade-offs given "AWS-first / data residency" and a security-conscious client.
- [ ] Metric schema / data model for an "agent run" (run id, graph, node timings, token
      counts, cost, status, errors, trace links).
- [ ] Central DB choice on AWS (RDS/Postgres vs. Timestream vs. OpenSearch vs. Athena over
      S3) — weigh query patterns, cost, and simplicity.
- [ ] How to instrument LangGraph runs with minimal code intrusion (callbacks/handlers).

### Hosting recommendation
- [ ] IaC tool recommendation (Terraform vs. AWS CDK) — match their existing skills.
- [ ] Reference architecture: compute for Python agents (ECS Fargate / Lambda / App Runner?),
      frontend hosting (S3+CloudFront / Amplify?), HA & auto-scaling.
- [ ] Secret & config management (AWS Secrets Manager / SSM Parameter Store).
- [ ] CI/CD design (GitHub Actions vs. CodePipeline) and env-promotion flow.
- [ ] Cost controls & alerting (AWS Budgets, anomaly detection, per-env tagging).

### Log storage
- [ ] AWS-first design: CloudWatch Logs vs. S3 + Athena vs. OpenSearch; retention tiers.
- [ ] When (if ever) a non-AWS alternative clears the "significant benefit" bar.

### Deliverables framing
- [ ] Draft outline for the onboarding/setup docs for new engineers.
- [ ] Decide what a lean v1 looks like vs. what's "build upon later."

---

## Answered

_(none yet — populate after the walkthrough)_
