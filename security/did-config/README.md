# DID / Web5 Config (example)

This directory shows a minimal pattern for using a public DID identity for CI and runners.

- Public DID documents are non‑secret and can be referenced from workflows via a non‑secret env var `DID_IDENTITY`.
- Private signing keys must remain off‑repo (OS keyring, external HSM, or secret manager).
- Example env usage (do not commit your real DID as a secret):

```yaml
env:
  DID_IDENTITY: "did:ion:EiD8J2b3K8k9Q8x9L7m2n4p1q5r6s7t8u9v0w1x2y3z4A5B6C7D8E9F0"
```

Workflows should use the DID only as a public pointer to verification keys and logging identity; signing operations should retrieve private keys from a secure store at runtime.