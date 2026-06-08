# Security & Governance for AI — AWS Services

## The Story for Rhys

For a regulated HR/payroll company operating across multiple countries, you need three things:

1. **Preventive controls** — Config rules ensuring AI infrastructure is secure and compliant before anything runs
2. **Detective controls** — CloudTrail showing who used what AI, when
3. **Content auditing** — Model invocation logging proving what the AI said was appropriate and accurate

AWS gives all three out of the box. We just configure and demonstrate it.

---

## AWS Config — AI/ML Conformance Packs

AWS provides purpose-built conformance packs for AI governance. These deploy as a single bundle and continuously evaluate compliance, flagging non-compliant resources automatically.

### Amazon SageMaker AI Security & Governance

- Pre-built Config rules checking: endpoint encryption, network isolation, private VPCs, encrypted training volumes
- Continuously assesses SageMaker resources against security baseline

### Amazon Bedrock Security & Governance

- Rules for Bedrock-specific resources: guardrails configured, model access properly scoped, invocation logs enabled
- Deploy alongside supporting infrastructure pack

### AI/ML Security & Governance Supporting Infrastructure

- Baseline rules for underlying compute, storage, and networking that AI workloads run on
- Covers any AI workload (AI, ML, generative AI, agentic AI)

### How It Works

- Deploy conformance pack → Config rules continuously evaluate
- Non-compliant resources flagged in dashboard
- Can trigger automatic remediation or notifications
- Deployable across an entire AWS Organization for multi-account governance

---

## CloudTrail — AI Audit Trail

### Layer 1: Standard CloudTrail

- Logs every API call: who invoked which model, when, from where
- Good for access auditing
- Doesn't capture what was asked/answered (just that an invocation happened)

### Layer 2: Bedrock Model Invocation Logging

- Captures full request and response payloads (prompts + completions)
- Logs to S3 or CloudWatch Logs
- Disabled by default — must be explicitly enabled
- For HR/payroll: can audit exactly what AI said to an employee about their rights, and prove it was accurate
- EU AI Act readiness: traceability of AI decisions

---

## Additional Services

### Amazon Bedrock Guardrails

- Proactive content filtering before responses reach users
- Block specific topics, detect PII, enforce responsible AI policies
- For HR: "AI must not give legal advice for jurisdictions it hasn't been validated for"
- Configurable per use case / per model

### AWS Audit Manager

- Automated evidence collection for compliance frameworks (SOC2, GDPR, ISO 27001)
- Has specific controls for AI workloads
- Generates audit-ready reports

### SageMaker Model Cards & Model Registry

- Documented model metadata: intended use, limitations, bias assessments
- Version tracking — which model is deployed where
- The "responsible AI" paper trail regulators want
- Required for EU AI Act high-risk AI systems

### Amazon Bedrock Model Evaluation

- Automated evaluation of model outputs for accuracy, toxicity, bias
- For HR: bias in AI-driven decisions (hiring, performance, pay recommendations) is a massive regulatory risk
- Can run offline evals against test datasets

---

## Relevance to Cezanne / Northedge

| Concern | AWS Service | What It Does |
|---------|-------------|--------------|
| "Who used the AI and when?" | CloudTrail | Full API audit trail |
| "What did the AI say?" | Bedrock Invocation Logging | Prompt + response capture |
| "Is our AI infrastructure secure?" | Config Conformance Packs | Continuous compliance checks |
| "Is the AI biased or inappropriate?" | Bedrock Guardrails + Model Eval | Content filtering + bias testing |
| "Can we prove compliance to auditors?" | Audit Manager + Model Cards | Evidence collection + documentation |
| "Do different countries need different rules?" | Guardrails (per-use-case) | Jurisdiction-specific policies |

---

## Demo Potential

- Deploy the AI/ML conformance pack and show the compliance dashboard
- Enable model invocation logging and show a sample audit trail
- Configure Bedrock Guardrails with HR-specific content policies
- Show Audit Manager generating a compliance report covering AI usage

These are relatively quick to set up and visually impressive in a demo context.

---

## Deployed (June 2026)

### AI-ML-SageMaker-Security-Governance (15 rules)
- Status: CREATE_COMPLETE
- Findings: 2 non-compliant SageMaker domains not in VPC (`d-9f4j4baxru0d`, `d-b9ygwkxeyxmm`)
- Console: Config → Conformance packs → AI-ML-SageMaker-Security-Governance

### AI-ML-Supporting-Infrastructure (16 rules)
- Status: CREATE_COMPLETE
- Findings: 40+ non-compliant resources (S3 buckets without SSL policies, CloudWatch log groups without encryption, VPC without flow logs, unencrypted EBS volume, KMS key without rotation)
- Console: Config → Conformance packs → AI-ML-Supporting-Infrastructure

### AI-ML-Bedrock-Security-Governance
- Status: FAILED — Bedrock Config rule identifiers not available in eu-west-1 yet
- Revisit when AWS rolls these out to the region

### Console URL
`https://eu-west-1.console.aws.amazon.com/config/home?region=eu-west-1#/conformance-packs`
