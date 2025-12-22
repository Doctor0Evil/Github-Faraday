# GitHub-Faraday Profile Template

Use this one‑page profile to adopt the GitHub‑Faraday logical cage in any repo.

## Purpose
A lightweight profile that enforces workflow hygiene, runner isolation, and identity controls so code, data, and automation move through auditable, limited channels.

## Quick checklist

- [ ] GitHub Settings
  - [ ] Protected branches (main/release) with required review and status checks.
  - [ ] Enforce signed commits on protected branches.
  - [ ] Restrict Actions to org allowlist where possible.

- [ ] Required Workflows
  - [ ] `ci` (basic build/test) with `permissions: contents: read`.
  - [ ] `workflow-lint` must run on push/PR and be a required status check.
  - [ ] Deploy workflows gated by `environments` + manual approvals.

- [ ] Runners
  - [ ] Sensitive jobs use self‑hosted runners in isolated network segments.
  - [ ] Runners publish a DID identity and do not contain private keys in repo.

- [ ] Verification
  - [ ] All workflows pass `workflow-lint`.
  - [ ] Protected branches enforce status checks and required reviewers.

Copy this into your `SECURITY.md` or repo README when adopting the profile.