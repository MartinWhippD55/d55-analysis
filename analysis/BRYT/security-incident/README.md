# Bryt Security Incident — Working Notes

Living overview of the Bryt endpoint/credential-chain compromise work: what's happened, what's in this folder, and what's next. Companion to the detailed HTML docs.

_Last updated: 16 Sep 2026._

---

## Background

A developer machine (Rhys) was compromised via a social-engineering lure — a fake "consultancy" supplied a malicious repo that executed on local setup and harvested the machine's credential chain. History on at least two repos (`BrytAdminPortal`, `BrytDataEngineering`) is believed to have been rewritten to inject malware. Because a persistent endpoint compromise held the full credential chain, the working assumption is that **everything that identity could reach is potentially compromised**. Bryt and D55 have agreed to **rotate everything**. D55 manages both Bryt's GitHub org and their AWS accounts.

Full detail lives in `incident-and-hardening.html`.

## What we've done so far

1. **Documented the incident & hardening plan** — `incident-and-hardening.html` (initial access, findings, response plan, hardening, Identity Center model, detection, exposed-key tracker).
2. **Built a read-only AWS activity audit** to answer "did the compromised identity do anything anomalous?":
   - `audit-aws.ps1` — read-only collector (CloudTrail, IAM, GuardDuty, EC2) across all profiles/regions.
   - Ran it against **all 12 `bryt-inv-*` accounts** over the last 30 days, matching Rhys' SSO identity.
   - **Result: no anomalous activity.** Every action traces to Rhys' UK IP (`86.183.104.170`) + AWS service ranges; no persistence/evasion/exfil, no new IAM users/keys, no GuardDuty findings. The only mutations were his own incident-response actions (SSM jump-box rotation; Identity Center password/session work). Written up in `audit.html`.
   - Secondary finding: a **GuardDuty coverage gap** (no detector in regions checked).
3. **Wrote three rotation checklists** for the "rotate everything" effort — `rotation-checklist-aws.md`, `rotation-checklist-github.md`, `rotation-checklist-cross-cutting.md` — developer-runnable, with how-to-check commands and evidence markers.

## Files in this folder

| File | What it is | In git? |
|---|---|---|
| `incident-and-hardening.html` | Main incident + hardening document | ✅ |
| `audit.html` | AWS activity-audit report (findings, scope, method) | ✅ |
| `audit-aws.ps1` | Read-only AWS audit collector | ✅ |
| `check-windows.ps1` | Endpoint triage script (the lure/loader sweep) | ✅ |
| `rotation-checklist-aws.md` | AWS rotation checklist | ✅ |
| `rotation-checklist-github.md` | GitHub rotation checklist | ✅ |
| `rotation-checklist-cross-cutting.md` | Cross-cutting rotation checklist | ✅ |
| `README.md` | This file | ✅ |
| `pem.xlsx` | Exposed-key tracker source | 🔒 local only (gitignored) |
| `prof.xlsx` | AWS profiles list | 🔒 local only (gitignored) |
| `aws-audit-<timestamp>/` | Raw audit output (CloudTrail, IPs, credential reports) | 🔒 local only (gitignored) |
| `win-check-<host>-<timestamp>/` | Endpoint triage output | 🔒 local only (gitignored) |

Sensitive/machine-generated output is kept local via `.gitignore`.

---

## Next steps

### 1. Walk through the AWS rotation checklist and close gaps _(next session)_

- Go through `rotation-checklist-aws.md` section by section **iteratively**, discussing each item and identifying anything missing for Bryt's actual setup.
- Likely gap areas to probe: services not yet enumerated (e.g. API Gateway keys, CloudFront signing, SES/SMTP, ECR/registry creds), the `d55-sagemaker-demo` account (`922850913962`) that isn't in the `bryt-inv-*` profiles, and confirming which secrets have live consumers before rotating.
- Refine the checklist as we go; the same review can then be applied to the GitHub and cross-cutting checklists.

### 2. Use the profile list to perform a sweep

- Use the `bryt-inv-*` profiles (read-only) to **sweep current state** and turn the checklist into a concrete "rotate these" worklist — e.g. enumerate Secrets Manager secrets, SSM SecureStrings, IAM users/access keys (credential reports), EC2 key pairs, and Identity Center permission-set assignments across all accounts.
- Note: the `bryt-inv-*` profiles are **read-only** — good for discovery, but the rotations themselves need admin/deployer access.
- Fold `prof.xlsx` in if it maps personas/permission sets to accounts.

### 3. Other follow-ups carried from the audit

- **Confirm `86.183.104.170` is Rhys' IP** — the "clean" verdict rests on this.
- **Confirm the 15–16 Sep mutating actions** were all intended incident response.
- **Extend the window past 90 days** using the org CloudTrail + Athena already set up in `logarchive` (`503561448641`); pin the malware-landing date.
- **Check S3 data events** for object-level exfil from the DMS output buckets (only visible if data events are captured).
- **Confirm / enable GuardDuty** org-wide and re-verify the "no detector" result isn't a read-role permission artifact.
- **Extend `audit-aws.ps1` with ACM issuance-abuse events** — add `ImportCertificate`, `RequestCertificate`, `ExportCertificate` (and ACM Private CA issuance, e.g. `IssueCertificate`) to the high-signal event list so the audit surfaces any certificate abuse by the compromised identity in the window. Complements the read-only imported-cert inventory (`sweep-acm-imported.ps1`): the inventory finds certs whose private key originated outside AWS; the CloudTrail signal catches issuance/export abuse for managed certs whose keys ACM never exposes.

## Open questions

- Is `86.183.104.170` Rhys' known IP?
- Were the 15–16 Sep mutating actions all intended IR?
- Confirmed malware-landing date (to set the true, likely >30-day, window)?
- Are S3 data events captured anywhere for object-level exfil coverage?
- Full list of repos/accounts the compromised identity could reach (beyond the two repos and the `bryt-inv-*` accounts)?
