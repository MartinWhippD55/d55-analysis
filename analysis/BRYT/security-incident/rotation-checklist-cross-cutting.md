# Bryt Credential Rotation — Cross-Cutting Checklist

**Context:** Full endpoint / credential-chain compromise of a developer machine (Rhys). Bryt and D55 have agreed to rotate everything. This checklist covers the parts that **span AWS and GitHub** or sit outside both — process, CI/CD, third-party services, and verification. Use it alongside the **AWS** and **GitHub** checklists.

**Status legend:** `[ ]` to do · `[~]` in progress · `[x]` done · `[N/A]` not applicable

---

## How to use this checklist

- This is the **wrapper**: it sequences the whole rotation and catches the things that fall between AWS and GitHub.
- Where you see **📷 Evidence**, save into `security-incident/rotation-evidence/cross-cutting/`.
- Do **A (sequence & containment)** before diving into the AWS/GitHub checklists; do **F (verification)** after.

---

## A. Sequence & containment (do this first)

- [ ] **A1. Contain the identity before rotating.** Revoke Rhys's IdP/SSO sessions (AWS Identity Center) and GitHub sessions/tokens *first*. Rotating while an attacker holds a live session just leaks the new secrets to them.
- [ ] **A2. Preserve break-glass.** Confirm a working fallback admin path on both sides (AWS root + hardware MFA; a GitHub org owner that isn't Rhys) before touching privileged access.
- [ ] **A3. Preserve evidence before anything destructive.** `git clone --mirror` the affected repos offline; note malicious commit SHAs; snapshot/AMI any instances being rebuilt. (History rewrite and endpoint rebuild are separate activities in the incident doc.)
- [ ] **A4. Agree the window.** Rotate against the **full** compromise window, not just 30 days — pin the malware-landing date if known.

## B. Inventory (you can't rotate what you can't see)

- [ ] **B1. Consolidated secret scan over full git history**, all repos, to produce one authoritative "rotate these" list.
  ```bash
  # Example with gitleaks (run per repo, over full history)
  gitleaks detect --source . --log-opts="--all" --report-path gitleaks-<repo>.json
  # or trufflehog
  trufflehog git file://. --json > trufflehog-<repo>.json
  ```
  - 📷 Evidence: the consolidated findings list.
- [ ] **B2. AWS credential reports** for all 12 accounts (see AWS checklist B3) — the standing-key inventory.
- [ ] **B3. GitHub token/key/secret inventory** (see GitHub checklist B–F) — PATs, deploy keys, Actions/Dependabot/Codespaces secrets, Apps, webhooks.
- [ ] **B4. Build a consumer map.** For each shared secret, list what reads it (pipelines, services, DBs, jobs) so rotation updates consumers in step and doesn't break prod.

## C. CI/CD — where AWS and GitHub meet

- [ ] **C1. GitHub Actions → AWS.** Any Actions secret holding a long-lived AWS access key is the classic re-leak path. Rotate the key (AWS checklist B) **and** the Actions secret (GitHub checklist D), then confirm the pipeline works.
- [ ] **C2. Move to OIDC federation.** Replace stored AWS keys in Actions with `aws-actions/configure-aws-credentials` + an IAM OIDC role scoped per environment. Removes the standing secret entirely.
  - Why here: this is the single highest-leverage change to reduce what has to be rotated next time.
- [ ] **C3. Self-hosted runners.** If any exist, rotate their registration tokens and check for tampering; prefer ephemeral runners.
- [ ] **C4. Deployment identities.** Confirm deploys assume the `cdk-*` roles via OIDC/short-lived creds, not stored keys.

## D. Third-party / SaaS reachable from the endpoint or stored secrets

The compromised machine (and the secrets it held) could reach services beyond AWS/GitHub. Rotate credentials / revoke sessions for each in use:

- [ ] **D1. Package registries** — npm, PyPI, Docker Hub, GitHub Packages (automation tokens).
- [ ] **D2. Observability / ops** — Datadog, PagerDuty, Sentry, LogicMonitor (in use per incident assets).
- [ ] **D3. Comms** — Slack tokens/webhooks, email/SMTP credentials.
- [ ] **D4. IaC / delivery** — Terraform Cloud, any deploy tooling tokens.
- [ ] **D5. Anything in the developer's browser/keychain** — SaaS admin logins saved on the machine; force password resets + session revocation where those could grant access to Bryt systems.
- [ ] **D6. VPN / remote access** credentials and certificates.

## E. Endpoint & people

- [ ] **E1. Rebuild Rhys's endpoint** from known-good media before issuing fresh credentials (per incident Response Plan). Never reissue onto the compromised machine.
- [ ] **E2. Issue fresh credentials to Rhys** only on the rebuilt machine.
- [ ] **E3. Team comms.** Everyone re-authenticates and **re-clones** repos (stale clones/forks/open PRs still carry old history & secrets). Brief the team blamelessly on the lure.

## F. Verification & closure

- [ ] **F1. Old credentials fail.** Spot-check: deactivated AWS key → `AccessDenied` in CloudTrail; leaked `ghp_…` → `401`; rotated DB/app creds prove out.
- [ ] **F2. Services healthy.** Pipelines green, apps up, DMS connects, scheduled jobs run.
- [ ] **F3. Re-run the AWS activity audit** (`audit-aws.ps1`) — no new anomalies.
- [ ] **F4. Re-scan repos** post-rotation/scrub — confirm secrets gone and push protection blocks re-entry.
- [ ] **F5. Plant canary tokens** (endpoint, repo, S3, Secrets Manager) so any future use of "stolen" creds alarms — highest-ROI detection.
- [ ] **F6. Close detection gaps** surfaced by the audit — enable GuardDuty org-wide; stream GitHub audit log + CloudTrail to a watched channel.
- [ ] **F7. Evidence archived** across `rotation-evidence/{aws,github,cross-cutting}/`.

---

## Rotation order at a glance

1. **Contain** identity (SSO + GitHub sessions/tokens) — Cross-Cutting A, GitHub A.
2. **Inventory** — Cross-Cutting B.
3. **Rotate**, grouped, updating consumers in step:
   - Leaked specific secrets first (`AKIA4TNB…`, `ghp_…`).
   - AWS: Identity Center → IAM keys → Secrets Manager/SSM → DBs → key pairs → Cognito/KMS → root.
   - GitHub: PATs → SSH/deploy keys → Actions/Dependabot/Codespaces secrets → Apps/OAuth/webhooks → registry tokens.
   - CI/CD crossover — move to OIDC.
   - Third-party / SaaS.
4. **Persistence sweep** — AWS K, GitHub G.
5. **Rebuild endpoint & reissue** — Cross-Cutting E.
6. **Verify & close** — Cross-Cutting F.

| Field | Value |
|---|---|
| Operator | |
| Reviewer | |
| Date completed | |
| Exceptions / follow-ups | |
