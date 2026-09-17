# Bryt Credential Rotation — AWS Checklist

**Context:** Full endpoint / credential-chain compromise of a developer machine (Rhys). Bryt and D55 have agreed to rotate everything. This checklist covers the **AWS** side. See the companion **GitHub** and **Cross-Cutting** checklists for the rest.

**Status legend:** `[ ]` to do · `[~]` in progress · `[x]` done · `[N/A]` not applicable

---

## How to use this checklist

- Work top-to-bottom. The ordering matters: **contain first, then rotate, then verify.**
- Each item has **Why → How to check → How to rotate → Verify**. Tick the box only after the *Verify* step passes.
- Capture evidence as you go. Where you see **📷 Evidence**, save a screenshot or command output into `security-incident/rotation-evidence/aws/` for the incident record.
- Two people where possible: one operator, one reviewer — especially for destructive steps.

## Before you start (prerequisites)

- [ ] **Access level.** The read-only `bryt-inv-*` profiles used for the audit are **not** sufficient to rotate. Use your normal admin / deployer access. Commands below show `--profile <admin-PROFILE>` as a placeholder.
- [ ] **Break-glass path confirmed.** Before touching SSO/admin, confirm you have a working fallback: root login + hardware MFA for the management account, or a second known-good Identity Center admin. Do not proceed without this.
- [ ] **Containment done first.** Rhys's IdP/SSO sessions and GitHub sessions are already revoked (see Response Plan / GitHub checklist). Rotating before containment lets a live attacker session re-harvest the new secrets.
- [ ] **Consumer map to hand.** For every shared secret (DB creds, deploy creds), know what reads it so you can update consumers in step and avoid breaking prod.
- [ ] **Rotate against the full window**, not just the last 30 days — pin the malware-landing date if known.

### Accounts in scope

| Account | ID | Notes |
|---|---|---|
| audit | 597088050142 | Security / audit tooling |
| sage | 548046216771 | SageMaker workloads |
| portal2 | 922022259560 | Admin portal / networking |
| phidex | 313047251060 | Jump box + Logic Monitor (incident asset) |
| dev | 783535217689 | Development |
| logarchive | 503561448641 | Central CloudTrail S3 + Athena |
| logging | 569981240471 | Landing-zone logging |
| prod | 837413265725 | Production data platform |
| sagemaker | 624909705724 | SageMaker / DataZone (incident asset) |
| test | 286557183581 | Test |
| uat | 562148325844 | UAT |
| users | 425713683394 | Identity Center / SSO |
| d55-sagemaker-demo | 922850913962 | **Not** in `bryt-inv-*` profiles — confirm coverage |

> **Note on human AWS access:** access is via **Identity Center (SSO) / short-lived STS** — the audit found no long-lived IAM access keys for Rhys. So the priority is the **IdP/SSO identity**, the **secrets stored inside the accounts**, and the **leaked git-history secrets** — not human key rotation.

---

## A. Identity Center / SSO

- [ ] **A1. Identify the identity source.** Console → IAM Identity Center → **Settings** → *Identity source*. Note whether it's the built-in directory or an external IdP (Entra ID / Okta). Rotation of Rhys's password/MFA happens wherever the identity source lives.
  - 📷 Evidence: screenshot of the Identity source panel.
- [ ] **A2. Reset Rhys's password** in the identity source (Identity Center directory, or Entra/Okta admin).
- [ ] **A3. Re-enroll MFA.** Remove existing MFA devices for Rhys and require re-registration. Console → Identity Center → Users → *rhys.jacob* → **Multi-factor authentication**.
  - Why: a stolen session or device could have registered attacker MFA.
- [ ] **A4. Revoke active SSO sessions** (these survive a password reset). Console → Identity Center → Users → *rhys.jacob* → **Delete active sessions** / *Sign out*. Also lower session duration: Identity Center → Permission sets → each set → *Session duration* (e.g. 1–6h).
- [ ] **A5. Review permission-set assignments for anomalies.** Look for assignments/permission sets that shouldn't exist.
  ```bash
  # List Identity Center instance + permission sets (run against the IC account admin profile)
  aws sso-admin list-instances --profile <admin-users>
  aws sso-admin list-permission-sets --instance-arn <ic-instance-arn> --profile <admin-users>
  # For each permission set, list account assignments
  aws sso-admin list-account-assignments --instance-arn <ic-instance-arn> \
      --account-id <account-id> --permission-set-arn <ps-arn> --profile <admin-users>
  ```
  - 📷 Evidence: the assignment list.
- [ ] **A6. SAML signing certificate.** The exposed cert was public-only (low risk, per Key Tracker), but rotating it is good hygiene: Identity Center → application → **Actions → Edit configuration → IdP certificate → Generate new**. Coordinate with the SP.

## B. The leaked long-lived IAM key + org-wide key sweep

- [ ] **B1. Deactivate `AKIA4TNB…` first, then delete** (deactivate is reversible; keep briefly in case of break).
  ```bash
  aws iam update-access-key --access-key-id AKIA4TNB... --status Inactive --user-name <user> --profile <admin>
  # After confirming nothing breaks:
  aws iam delete-access-key --access-key-id AKIA4TNB... --user-name <user> --profile <admin>
  ```
- [ ] **B2. Check its usage in CloudTrail before deleting** (was it used by the attacker?). Query the org trail via Athena in logarchive (503561448641), or:
  ```bash
  aws cloudtrail lookup-events --lookup-attributes AttributeKey=AccessKeyId,AttributeValue=AKIA4TNB... \
      --profile <admin> --region eu-west-2
  ```
  - 📷 Evidence: usage result.
- [ ] **B3. Org-wide IAM key sweep.** For **every** account, generate a credential report and rotate/disable any long-lived access keys (especially on service/CI IAM users).
  ```bash
  aws iam generate-credential-report --profile <admin-ACCT>
  aws iam get-credential-report --query Content --output text --profile <admin-ACCT> | \
      # (base64-decode to CSV; inspect access_key_1/2_active, last_used, last_rotated)
  ```
  - Rotate: create a new key → update the consumer → deactivate old → verify → delete old (overlap window avoids downtime).

## C. IAM roles & trust policies

- [ ] **C1. Review trust policies** on privileged roles, especially the CDK deploy roles (`cdk-hnb659fds-*`) and anything assumable from CI. Look for unexpected principals or new external IDs.
  ```bash
  aws iam list-roles --profile <admin-ACCT> --query "Roles[].RoleName"
  aws iam get-role --role-name <role> --profile <admin-ACCT> --query "Role.AssumeRolePolicyDocument"
  ```
- [ ] **C2. Rotate external IDs** where used in cross-account trust (treat as a shared secret).
- [ ] **C3. Look for role backdoors** — roles created in the compromise window with broad trust (e.g. `sts:AssumeRole` from `*`).

## D. Secrets Manager (highest cascade risk)

- [ ] **D1. Enumerate secrets in every account.**
  ```bash
  aws secretsmanager list-secrets --profile <admin-ACCT> \
      --query "SecretList[].{Name:Name,LastChanged:LastChangedDate,RotationEnabled:RotationEnabled}" --output table
  ```
- [ ] **D2. Rotate the DMS credentials** called out in the incident: `centrestage` and `phidex`. Rotate the **value in Secrets Manager _and_ the actual DB user password**, then confirm DMS still connects.
- [ ] **D3. Rotate all other stored secrets** (API keys, SMTP, third-party tokens). For each: change it at the source system → update the Secrets Manager value → restart/redeploy consumers → verify.
  ```bash
  aws secretsmanager put-secret-value --secret-id <name> --secret-string '<new>' --profile <admin-ACCT>
  ```
  - Why the cascade matters: a DB password in Secrets Manager is read by apps, DMS, and jobs — update the DB and every consumer together or use an overlap.
- [ ] **D4. Enable automatic rotation** where supported, so this is easier next time.

## E. SSM Parameter Store

- [ ] **E1. Find `SecureString` parameters and rotate their values.**
  ```bash
  aws ssm describe-parameters --parameter-filters "Key=Type,Values=SecureString" --profile <admin-ACCT>
  ```
- [ ] **E2. Update consumers** (Lambda env, ECS task defs, EC2 bootstrap) that read them.

## F. Databases (RDS / Aurora / Redshift / DMS endpoints)

- [ ] **F1. Rotate master + application DB users** for each cluster. Prefer changing the password in the DB, then updating Secrets Manager (see D).
  ```bash
  aws rds describe-db-instances --profile <admin-ACCT> --query "DBInstances[].DBInstanceIdentifier"
  aws redshift describe-clusters --profile <admin-ACCT> --query "Clusters[].ClusterIdentifier"
  ```
- [ ] **F2. Rotate DMS endpoint credentials** (tie to the `centrestage`/`phidex` secrets in D2).
- [ ] **F3. Review DB users for unexpected accounts** created in the window.

## G. EC2 key pairs (per `pem.xlsx` tracker)

- [ ] **G1. For each exposed key pair still in service**, remember: **deleting the key-pair record does NOT rotate access** on a running instance. You must replace `authorized_keys` (Linux) or rotate the local admin password (Windows), or reimage.
  ```bash
  aws ec2 describe-key-pairs --profile <admin-ACCT> --region <region> \
      --query "KeyPairs[].{Name:KeyName,Id:KeyPairId,Created:CreateTime}" --output table
  ```
- [ ] **G2. Prefer moving to SSM Session Manager** (keyless) and removing the key pair entirely.
- [ ] **G3. Reconcile against the Key Tracker** in `incident-and-hardening.html` — mark each key remediated.

## H. Cognito (the user-migration code touched this)

- [ ] **H1. Rotate app-client secrets** for any confidential clients. Console → Cognito → User pool → **App integration → App clients** → *Edit → generate new secret* (or recreate the client).
- [ ] **H2. Review user pool** for rogue users/admins created in the window; force password resets / global sign-out if warranted.

## I. KMS & certificates

- [ ] **I1. Review KMS key policies and grants** for unexpected principals (data was decrypted during the incident — that's expected for the investigation, but confirm no new grants).
  ```bash
  aws kms list-grants --key-id <id> --profile <admin-ACCT>
  ```
- [ ] **I2. Enable automatic key rotation** on CMKs where off.
- [ ] **I3. Rotate any private keys / certs** stored in ACM-imported certs, or app keystores.

## J. Root account hygiene (per account)

- [ ] **J1. Confirm root has no access keys**, has hardware MFA, and a strong unique password.
- [ ] **J2. Reset root password + MFA** for any account where root credentials could conceivably have been exposed.

## K. Persistence sweep (do alongside rotation)

- [ ] **K1. New IAM users / roles / access keys / login profiles** created in the window (see the audit's high-signal list).
- [ ] **K2. New Identity Center permission sets or assignments.**
- [ ] **K3. Logging still intact** — CloudTrail not stopped/deleted, GuardDuty detectors present (note: audit found a GuardDuty coverage gap — confirm and enable).
- [ ] **K4. No unexpected cross-account trust or resource-sharing (RAM) grants.**

---

## Verification & sign-off

- [ ] Old `AKIA4TNB…` returns `AccessDenied` / no longer usable (check CloudTrail).
- [ ] Rotated DB / app / DMS credentials confirmed working (services healthy, pipelines green).
- [ ] Re-run the activity audit (`audit-aws.ps1`) — no new anomalies.
- [ ] Optional: plant an AWS honeytoken key and confirm any use alarms.
- [ ] Evidence captured in `rotation-evidence/aws/`.

| Field | Value |
|---|---|
| Operator | |
| Reviewer | |
| Date completed | |
| Exceptions / follow-ups | |
