# GitHub Actions Policy

A concise, enforceable checklist for `xr-security-lab` to apply GitHub‑Faraday controls.

## Organization

- [ ] Enable GitHub Actions at the org level and maintain an allowlist of approved actions (prefer GitHub‑maintained and vetted Marketplace actions).
- [ ] Set organization policy to restrict Actions usage to the allowlist for all repos.
- [ ] Default `GITHUB_TOKEN` org policy to least privilege; require explicit permission grants per job.

## Repositories

- [ ] Protect `main` and any release branches: require status checks, required reviewers, and signed commits.
- [ ] Require PRs and protect changes to `.github/workflows/**` so workflow file changes cannot be merged without review and passing checks.
- [ ] Require `workflow-lint` and primary `ci` checks as required status checks before merge.

## Workflows

- [ ] Default workflow YAML must set `permissions: contents: read` at the workflow level unless a documented justification exists.
- [ ] Pin third‑party actions to a full commit SHA; only allow `actions/*` and `github/*` org actions to use short tags when justified.
- [ ] Avoid `pull_request_target` except in narrow, documented cases; require `# faraday-reviewed` comment when used and additional review controls.
- [ ] Do not run untrusted code with elevated tokens (never run high‑priv jobs from forked PRs without gating/approval).

## Runners

- [ ] Self‑hosted runners must be registered to a limited, allowlisted set of repos only.
- [ ] Use isolated network segments for self‑hosted runners; enforce strict egress allowlists to artifact/package stores and other approved endpoints.
- [ ] Require image hardening and least‑software policy on runner hosts; apply automatic patching and hardening profiles.

## Secrets & Environments

- [ ] Use `environments` with required reviewers for any job that deploys to production or accesses high‑value secrets.
- [ ] Prefer OIDC and short‑lived credentials for cloud access; avoid long‑lived static secrets in repo settings.
- [ ] Scope secrets to the narrowest environment and rotation schedule; audit secret usage and access history.

## Monitoring & Meta-CI

- [ ] Run `workflow-lint` on push & PRs; protect branches to require a passing `workflow-lint` check.
- [ ] Monitor workflow telemetry for anomalies (rate of runs, unusual triggers, repeated failures); quarantine workflows that show suspicious patterns.
- [ ] Review third‑party Actions usage and update allowlist periodically (monthly or on new security advisories).

## Governance

- [ ] Prefer signed commits for maintainers on protected branches; consider enabling "Require signed commits" where contributor experience permits (weigh trade‑offs with contributor friction).
- [ ] Limit write access to `.github/workflows/**` to a small, trusted maintainer group; avoid allowing broad write access or drive‑by workflow edits.
- [ ] Document the workflow ownership policy in the repo `CONTRIBUTING.md` and require explicit approvals for any workflow-authoring PRs.
- [ ] Note: enforcing signed commits for all contributors can increase onboarding friction; a pragmatic pattern is to require signed commits for maintainers and CI-affecting merges, while logging unsigned contributions for review.

---

This policy is a baseline; specific repos can adopt a stricter subset (e.g., deploy pipelines handling neural/XR data should default to self‑hosted, offline runners with manual approvals).