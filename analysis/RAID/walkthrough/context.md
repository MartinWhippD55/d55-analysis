# Raid / Venatrix — Code Walkthrough Prep

## Meeting

- **What:** Code walkthrough and deeper dive into **Venatrix**, hosted by Dominika ("Dom").
- **When:** Thursday.
- **Who (their side):** Dom (organising), plus whoever Jonathan / Rhys forward to.
- **Who (our side):** Rhys (our CTO) + engagement team.
- **Ask from Dom:** Send specific questions, topics, or areas we'd like covered *in advance*
  so their team can prepare and we maximise the time.

> Action: we should send a short list of prepared topics/questions before the call.
> See `questions.md`.

## The client — CovertSwarm ("Raid" is our internal codename)

- Dom's email is on `covertswarm.com`.
- **CovertSwarm** is an offensive-security company: continuous, subscription-based
  penetration testing under a "Constant Cyber Attack" methodology (attacking clients'
  attack surface before real adversaries do).
- Founded 2020 by Anders Reeves; backed by Beech Tree Private Equity; CREST and CBEST
  accredited; operations in UK and North America.
- They run an **Offensive Operations Center (OOC)** platform for asset discovery, passive
  vulnerability enumeration, and threat alerting.
- Source: CovertSwarm public site (rephrased for licensing compliance) —
  https://www.covertswarm.com/about

> Implication: a security-first client. They will care a lot about how logs, secrets,
> and agent data are handled, where data resides, and the security posture of anything
> we recommend. Expect a high bar on IaC, secret management, and least-privilege.

## Venatrix — what we know

Venatrix appears to be an internal agentic platform. From Rhys's overview:

- **Stack:** LangGraph (agent orchestration), Python, TypeScript, Svelte, Vite.
- CompanyX (us) provides **embedded engineering support**, focused on lean, efficient
  solutions.

## Engagement overview (from Rhys)

Primary focus: **observability and logging** — capturing agent run metrics in a central
database for analysis and impact visibility. We also advise on **central hosting**.
Application and log data stay in **AWS for data residency** unless an alternative offers
significant speed, simplicity, or cost advantages.

## Deliverables & outcomes

1. **Agent Run Observability** — capture and store agent metrics in a central database
   for analysis and visibility.
2. **Hosting Recommendation** — a lean central hosting strategy, AWS-first for data
   residency, including:
   - Multiple environments (test & production)
   - Auto-scaling and high availability
   - Secure secret & configuration management
   - Disposable infrastructure via infrastructure-as-code
   - CI/CD pipelines (at minimum deploy to environments; extensible later)
   - Controls & alerting for AWS account spend
3. **Log Storage Architecture** — AWS-first log and metric storage; evaluate alternatives
   only for clear speed, simplicity, or cost benefit.
4. **Documentation** — supporting docs for the above, plus onboarding/setup docs for new
   engineers on the codebase.

## Status

- Prep folder created; notes started. No code access yet — walkthrough is Thursday.
