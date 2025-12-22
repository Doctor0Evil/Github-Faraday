# openEMS minimal model (2.4 / 5 GHz)

This directory holds a minimal, low‑dependency skeleton for an openEMS-based model to evaluate a small PEC box at 2.4 GHz (Wi‑Fi band) and 5 GHz.

Goal: provide a script skeleton that can be extended to run openEMS simulations on provisioned runners or inside a builder container.

Requirements (when you run simulations):
- Python 3.10+
- openEMS (python bindings) or rfems (optional; script falls back to placeholder)
- numpy, scipy

Contents:
- `simulate_box.py` — tries to import `rfems`/`pyopenems` and run a simulation; if not installed, writes a safe placeholder JSON report.
- `Dockerfile` — a minimal container image that provides Python + numerical deps. Add openEMS/rfems install steps for full capability.
- `docker-run.sh` — helper to build and run the container locally.
- `openems-ci.yml` — workflow (manual `workflow_dispatch`) that runs the simulation on labeled provisioned runners, plus an optional container-based dispatch (guarded by workflow input).

Quick local usage (Docker):

```sh
# build image and run placeholder simulation
sh openems/docker-run.sh

# you should see JSON reports in openems/
```

CI usage notes:
- The workflow is manual. To run an actual openEMS simulation in CI you have two choices:
  1. Provision self-hosted runners with openEMS installed and run `openems-ci.yml`.
  2. Extend the Dockerfile to install openEMS toolchain and use the container-based job by triggering the workflow with `use_container: true` (see `.github/workflows/openems-ci.yml`).

If you'd like, I can prepare a fuller Docker image spec that builds openEMS from source (this requires more build time and native deps).

## CI Smoke Test

A lightweight smoke test runs on `ubuntu-latest` and verifies the placeholder path works when FDTD libraries are absent. The smoke test executes:

```sh
python openems/simulate_box.py --frequency-ghz 2.4 --output openems_results.json --preset xr-headset
```

Expected artifact (`openems_results.json`): a JSON object containing keys:
- `mode`: should be `"placeholder"`
- `frequency_ghz`: numeric frequency in GHz (e.g., `2.4`)
- `timestamp`: an ISO‑8601 UTC timestamp
- `note`: a short string explaining this is a placeholder run
- `sweep`: an array of objects `{"freq_mhz": .., "attenuation_db": ..}` representing a small frequency sweep

The smoke test also installs `matplotlib` and will generate an example attenuation graph (PNG) next to the outputs when plotting is available. CI asserts `mode == "placeholder"` and that `openems_results.json` exists; additional checks may assert the CSV and PNG outputs are produced.

## Presets, devices, and example graphs

`simulate_box.py` supports `--preset` values that influence placeholder attenuation modeling:

- `xr-headset` — default centered at **2.4 GHz**, deeper notch (example).
- `xr-headset-5` — centered at **5.0 GHz** for 5 GHz headset bands.
- `ble` — centered near **2.402 GHz** (BLE channel), narrow notch.
- `generic` — balanced placeholder profile.

It also supports `--device` to run device-specific presets across their supported bands. Supported example devices:

- `oculus-quest-2` — bands: 2.4 GHz, 5.0 GHz (preset: `xr-headset`)
- `pico-neo-3` — bands: 2.4 GHz, 5.0 GHz (preset: `xr-headset`)
- `meta-quest-pro` — bands: 2.4 GHz, 5.0 GHz (preset: `xr-headset-5`)
- `htc-vive` — bands: 5.0 GHz (preset: `xr-headset-5`)
- `ble-headset` — band: 2.402 GHz (preset: `ble`)

Example usage to produce a CSV + PNG for a device band:

```sh
python openems/simulate_box.py --device oculus-quest-2
# produces oculus-quest-2_2400MHz_results.json, oculus-quest-2_2400MHz_results.csv, and a PNG (if matplotlib installed)
```

These placeholder outputs are intended for quick CI checks and visualization; replace with real openEMS outputs when running on provisioned simulation runners.

## Local acceptance test

To reproduce CI acceptance failures locally, run one of these checks on a machine with Docker or with a local openEMS install:

- Bare-metal / dev host acceptance test:

```sh
sh openems/acceptance_test.sh
```

- Containerized acceptance test (after building `xr-openems-full:latest`):

```sh
docker run --rm xr-openems-full:latest /work/openems/acceptance_test.sh
```

A successful test indicates at least one of `openems`, `openems-smoke`, or the Octave openEMS binding is available inside the runtime. A non-zero exit indicates missing runtime components to address.