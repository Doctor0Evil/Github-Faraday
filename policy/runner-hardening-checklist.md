# Runner Hardening Checklist

## GitHub-hosted runners

- [ ] Use GitHub-hosted runners for low‑privilege, ephemeral jobs (build/test) only.
- [ ] Do not store secrets on the runner; pass only scoped, short‑lived tokens via job `permissions` or OIDC.
- [ ] Minimize `permissions` scope at the job level and avoid exposing `id-token`/write unless justified.

## Self-hosted runners

- [ ] Use a dedicated, minimal OS image with only required tooling preinstalled.
- [ ] Run the runner under a non‑privileged account; avoid running as root or Administrator.
- [ ] Enable automatic security updates or scheduled patching and auditing of installed packages.
- [ ] Restrict which repositories and branches can use each runner via labels and repo associations.
- [ ] Place runners in an isolated network segment; enforce egress allowlists (artifact stores, package registries, and required service endpoints only).
- [ ] Centralize runner logs to a secure log collector and monitor for anomalies (unexpected commands, high egress, repeated failures).
- [ ] Use hardware or VM attestation where possible; consider using HSM or cloud KMS for key storage.

## DID / Web5 Identity Integration

- [ ] Assign each runner a public DID (example below) used as its public identity; publish DID document to your DID resolver or org documentation.
- [ ] Example runner DID (sample only): `did:ion:EiD8J2b3K8k9Q8x9L7m2n4p1q5r6s7t8u9v0w1x2y3z4A5B6C7D8E9F0`
- [ ] Store private signing keys only on the runner host or in a secure external HSM/secret manager; never commit private keys to the repository.
- [ ] Expose the public DID as a non‑secret env var (e.g., `DID_IDENTITY`) to workflows; use the private key via secure local mount or vault during signing operations.
- [ ] Audit DID usage: log signing operations and verify that verification keys in DID docs match runner metadata.

---

Notes:
- Use `step-security/harden-runner` or similar tools as examples for image hardening and egress policy enforcement.
- The DID approach provides a consistent, decentralized identity layer for runners without embedding secrets into workflows.