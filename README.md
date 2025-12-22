# GitHub-Faraday

GitHub-Faraday is a "logical Faraday cage" pattern for GitHub Actions: a set of policies, workflows, runner guidelines, DID identity patterns, and meta‑CI that harden CI/CD automation to reduce covert channels, exfiltration, and workflow abuse for XR/BCI/smart-city stacks.

## Getting Started

Follow these steps to bootstrap the `xr-security-lab/github-faraday` profile:

- [ ] Create repository `xr-security-lab/github-faraday` and push this skeleton.
- [ ] Enable branch protection on `main` and require `CI` and `Workflow Lint` as required status checks.
- [ ] Configure protection for changes under `.github/workflows/**` to require PR review and checks.
- [ ] Restrict self-hosted runners to trusted repos and configure egress allowlists per `policy/runner-hardening-checklist.md`.
- [ ] Set `DID_IDENTITY` as a non-secret repository or org variable to your DID for CI jobs (e.g., `did:ion:EiD8J2...`).
- [ ] Run a test PR to confirm `ci` and `workflow-lint` both pass.
- [ ] Run the openEMS full-image build + acceptance test at least once on a provisioned runner and confirm it passes.

## Legal and Ethical Notes

- Neural and XR telemetry is highly sensitive; require **explicit informed consent**, data minimization, encryption, and purpose limitation when collecting or processing such data.
- Do **not** implement RF jamming or unlawful interference — focus on measurement, shielding, and access controls.
- For research involving humans, follow relevant human-subject protections and applicable neural privacy laws/regulations.

---

## openEMS Track

The repository includes an *openEMS* track to prototype physical Faraday box simulations tied to reproducible CI:

- `openems/` contains:
  - `simulate_box.py` — a placeholder-capable script that writes `openems_results.json` when real FDTD libraries are absent.
  - `Dockerfile` and `openems/README.DOCKER_NOTES.md` for building a minimal image (add openEMS build steps only on dedicated runners).
  - `openems-ci.yml` — includes a fast smoke test that runs on `ubuntu-latest` and heavier jobs gated to self-hosted `openems` runners or a container build.
- `openems-build-image.yml` — manual build workflow to construct a full `xr-openems-full` image and run `acceptance_test.sh` inside it (must be run on a self-hosted builder with sufficient resources).
Next options:
- Integrate full openEMS stack into the Docker image on dedicated hardware (long build).
- Add 5 GHz and BLE presets and corresponding result tags.
- Define simple attenuation reporting and mapping for an XR headset box model.

---

See `policy/` for the GitHub‑Faraday policy checklist and `security/did-config/` for DID examples.