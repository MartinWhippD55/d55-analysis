# Bryt Credential Rotation — GitHub Checklist

**Context:** Full endpoint / credential-chain compromise of a developer machine (Rhys). D55 manages Bryt's GitHub org and repositories. This checklist covers the **GitHub** side. See the companion **AWS** and **Cross-Cutting** checklists for the rest.

**Status legend:** `[ ]` to do · `[~]` in progress · `[x]` done · `[N/A]` not applicable

---

## How to use this checklist

- Work top-to-bottom. **Contain first, then rotate, then verify.**
- Each item has **Why → How to check → How to rotate → Verify**. Tick the box only after *Verify* passes.
- Where you see **📷 Evidence**, save a screenshot / command output into `security-incident/rotation-evidence/github/`.
- Commands assume the **GitHub CLI** (`gh`) authenticated as an org admin, and/or the org **Settings** UI. Set your org once:
  ```bash
  gh auth status
  ORG=Bryt   # replace with the real org login
  ```

## Before you start (prerequisites)

- [ ] **Admin access confirmed** to the org (owner role) and a break-glass owner account that is *not* Rhys.
- [ ] **Rotation ≠ history scrubbing.** This checklist rotates credentials. Purging leaked secrets (e.g. `ghp_…`, `AKIA…`) from git history is a separate activity (BFG / `git filter-repo`) tracked in the incident doc — do both.
- [ ] **Known leaked secret:** a GitHub PAT `ghp_…` was found in `BrytAdminPortal` CI/CD YAML history. Treat it as compromised regardless of scrubbing.
- [ ] **Repos of record:** `BrytAdminPortal`, `BrytDataEngineering` (confirm the full list — the identity may have had write to others).

---

## A. Contain Rhys's account first

- [ ] **A1. Revoke all sessions / sign out everywhere.** If the org uses SSO (SAML), revoke his IdP sessions too. Org → **Settings → Authentication security → SAML** → find user → *Revoke SSO*. Also have Rhys sign out of all devices in his account security settings.
- [ ] **A2. Reset his GitHub password and re-verify 2FA.** Remove existing 2FA methods and re-enroll.
- [ ] **A3. Temporarily suspend or reduce his org access** while rotating, if practical.

## B. Personal Access Tokens (PATs)

- [ ] **B1. Revoke the known leaked token** `ghp_…` and **all** of Rhys's PATs (classic + fine-grained). User settings → **Developer settings → Personal access tokens** (both *Tokens (classic)* and *Fine-grained tokens*).
  - As org owner you can see/audit PATs that access org resources: Org → **Settings → Personal access tokens → Active tokens**.
  ```bash
  # Fine-grained PATs with access to the org (owner view):
  gh api "/orgs/$ORG/personal-access-tokens" --paginate
  # Revoke a specific fine-grained PAT's org access:
  gh api -X DELETE "/orgs/$ORG/personal-access-tokens/{pat_id}"
  ```
  - 📷 Evidence: before/after token list.
- [ ] **B2. Audit every other member's PATs** for stale/over-scoped tokens while you're here.

## C. SSH keys & deploy keys

- [ ] **C1. Remove Rhys's user SSH keys** (user → Settings → SSH and GPG keys).
  ```bash
  gh api /user/keys            # (as the affected user) list
  gh api -X DELETE /user/keys/{key_id}
  ```
- [ ] **C2. Audit repo deploy keys** across all repos — remove unknown ones, rotate legitimate ones.
  ```bash
  for repo in BrytAdminPortal BrytDataEngineering; do
    echo "== $repo =="; gh api "/repos/$ORG/$repo/keys" --jq '.[] | {id,title,read_only,created_at}'
  done
  ```
  - 📷 Evidence: deploy-key list per repo.
- [ ] **C3. Rotate GPG/commit-signing keys** if Rhys used signing and the private key was on the machine.

## D. GitHub Actions secrets (high priority — common re-leak path)

- [ ] **D1. Rotate all repo-level Actions secrets** (they often hold AWS keys / deploy creds). Repo → **Settings → Secrets and variables → Actions**.
  ```bash
  gh api "/repos/$ORG/BrytAdminPortal/actions/secrets" --jq '.secrets[].name'
  gh secret set <NAME> --repo "$ORG/BrytAdminPortal"       # set new value
  ```
- [ ] **D2. Rotate org-level Actions secrets.** Org → Settings → Secrets and variables → Actions.
  ```bash
  gh api "/orgs/$ORG/actions/secrets" --jq '.secrets[].name'
  ```
- [ ] **D3. Rotate environment-level secrets** (per repo → Settings → Environments → each env → secrets).
  ```bash
  gh api "/repos/$ORG/<repo>/environments" --jq '.environments[].name'
  ```
- [ ] **D4. Rotate Dependabot secrets** (Settings → Secrets and variables → **Dependabot**) and **Codespaces** secrets.
- [ ] **D5. Prefer OIDC over stored cloud keys.** Where an Actions secret holds a long-lived AWS key, replace it with **OIDC federation** to an assumable role (see Cross-Cutting checklist). Less to rotate next time.

## E. Apps, OAuth & webhooks

- [ ] **E1. Review installed GitHub Apps** and their permissions; remove/rotate anything unexpected. Org → **Settings → GitHub Apps** / **Installed GitHub Apps**.
  ```bash
  gh api "/orgs/$ORG/installations" --jq '.installations[] | {app_slug,app_id}'
  ```
- [ ] **E2. Review OAuth app authorizations** (org → Settings → **Third-party access / OAuth app policy**). Revoke unknown grants.
- [ ] **E3. Rotate webhook secrets** (org and repo webhooks). Recreate the shared secret and update the receiver.
  ```bash
  gh api "/repos/$ORG/<repo>/hooks" --jq '.[] | {id,config_url:.config.url,active}'
  gh api "/orgs/$ORG/hooks" --jq '.[] | {id,config_url:.config.url,active}'
  ```
  - 📷 Evidence: webhook list per repo/org.

## F. Machine users, bots & registry tokens

- [ ] **F1. Rotate credentials for any machine/bot accounts** used by CI or automation.
- [ ] **F2. Rotate package/registry tokens** — GitHub Packages tokens, npm automation tokens, container registry creds. These may live as Actions secrets (see D) and/or on external systems.

## G. Persistence sweep (what an attacker may have planted)

- [ ] **G1. Review org membership & roles** for accounts added in the window.
  ```bash
  gh api "/orgs/$ORG/members" --paginate --jq '.[].login'
  gh api "/orgs/$ORG/outside_collaborators" --paginate --jq '.[].login'
  ```
- [ ] **G2. Review per-repo collaborators** for unexpected access.
  ```bash
  gh api "/repos/$ORG/<repo>/collaborators" --jq '.[] | {login,permissions}'
  ```
- [ ] **G3. New deploy keys / Apps / OAuth grants / webhooks** — covered in C & E; explicitly confirm none are attacker-planted.
- [ ] **G4. Changed CI workflows.** Review recent diffs to `.github/workflows/**` and any deploy YAML for injected steps.
- [ ] **G5. Audit log review.** Org → **Settings → Logs → Audit log**. Look for `oauth_authorization`, `personal_access_token`, `hook`, `protected_branch`, `repo` events and force-pushes in the window.
  ```bash
  gh api "/orgs/$ORG/audit-log?phrase=action:git.push&include=all" --paginate   # requires appropriate plan/scope
  ```
  - 📷 Evidence: filtered audit-log export.

## H. Repository protections (lock down during/after)

- [ ] **H1. Enforce branch protection / rulesets** on default + release branches: block force-push, require PR review + status checks. Org → **Settings → Repository → Rulesets**, or per repo → Settings → Branches.
  ```bash
  gh api "/repos/$ORG/<repo>/branches/main/protection" --jq '{required_pr:.required_pull_request_reviews,force_pushes:.allow_force_pushes}'
  ```
- [ ] **H2. Require signed commits** (addresses the impersonation/history-rewrite vector).
- [ ] **H3. Restrict who can edit Actions workflows** and enable **secret scanning + push protection** (Settings → Code security). Route alerts to a watched channel.

---

## Verification & sign-off

- [ ] Old `ghp_…` PAT returns `401` (e.g. `curl -sI -H "authorization: token ghp_..." https://api.github.com/user`).
- [ ] Rotated Actions secrets confirmed — a test pipeline run succeeds with the new values.
- [ ] No unexpected members, collaborators, deploy keys, Apps, OAuth grants, or webhooks remain.
- [ ] Secret scanning + push protection enabled; branch protection / signed commits enforced.
- [ ] Team notified to re-authenticate and **re-clone** (stale clones/forks/open PRs still carry old history & secrets).
- [ ] Evidence captured in `rotation-evidence/github/`.

| Field | Value |
|---|---|
| Operator | |
| Reviewer | |
| Date completed | |
| Exceptions / follow-ups | |
