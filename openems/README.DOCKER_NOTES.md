# Notes on building a full openEMS image

Building a container that includes a working openEMS toolchain typically requires:

- Installing the openEMS native binaries (may require compiling from source).
- Installing MATLAB/Octave toolchain and/or the necessary dependencies for the Python bindings.
- Verifying system-level libs: libx11, libfftw3, gfortran, etc.

## Quick Docker commands

To build and run the current (minimal) image locally:

```sh
docker build -t xr-openems-box openems
docker run --rm -v "$PWD":/workspace -w /workspace xr-openems-box python openems/simulate_box.py --frequency-ghz 2.4 --output openems_results.json
```

Notes:
- The base image currently includes Python and numeric deps only (numpy/scipy/matplotlib). The placeholder simulation path requires only the Python standard library but the smoke test installs `matplotlib` at runtime; building a fuller image with native openEMS would include more native libs.
- Adding the full openEMS compilation will significantly increase build time and image size and should be limited to dedicated runners or a cached build pipeline.

## References / examples

- tclin0122/openEMS_docker (example Dockerfile)
- Maskset guide: "A guide to FDTD simulation with openEMS" (setup notes)

I prepared a fuller Dockerfile that builds openEMS from source and installs the Python bindings. See `openems/Dockerfile.openems` and the helper script `openems/build-openems.sh`.

**Build tips / recommended environment:**

- Use a builder host with at least **8 CPU cores**, **32 GB RAM**, and **50+ GB disk** for comfort (smaller may work but builds will be slower and may fail on resource limits).
- Consider using Docker Buildx with a local cache or a remote cache to speed repetitive builds and avoid long rebuilds.
- Prefer running the build on a dedicated self-hosted runner or a powerful local machine; building on GitHub-hosted runners is not recommended due to time limits and quota.

**Example build (local):**

```sh
# on a machine with Docker installed
sh openems/build-openems.sh
```

**Example buildx (with cache)**

```sh
docker buildx create --use --name buildx0
docker buildx build --progress=plain --tag xr-openems-full:latest --file openems/Dockerfile.openems --cache-to=type=local,dest=/tmp/buildcache --cache-from=type=local,src=/tmp/buildcache .
```

Be prepared for a long build; inspect logs and increase memory where necessary.

## Acceptance test

After building the full image, run the built-in acceptance test to verify runtime availability:

```sh
# inside the built image (example)
docker run --rm xr-openems-full:latest /work/openems/acceptance_test.sh
```

The acceptance test passes if at least one of the following is true:
- The helper `/usr/local/bin/openems-smoke` is present and runnable
- The `openEMS` binary is present in PATH and responds
- The Octave `openEMS` bindings are available (Octave can `exist('openEMS','file')`)

If the acceptance test fails, inspect the builder logs and verify missing libraries, Octave bindings, or path issues. If you want, I can iterate on the Dockerfile to address any specific failure you encounter.

**CI artifacts:** the build workflow uploads acceptance logs and outputs as an artifact named `openems-acceptance` so you can retrieve logs and JSON output even when the job fails. The docker build logs are now captured to `openems/artifacts/docker_build.log` and uploaded as part of the artifact.

## Troubleshooting build and acceptance failures

- Check the Docker build logs for errors about missing system packages or libraries (e.g., FFTW, Qt, Octave headers); map missing headers to the corresponding `-dev` package to install (e.g., `libfftw3-dev`, `libx11-dev`).
- If `make` or `cmake` fails with missing headers, inspect the failing command and install the package that provides the header (e.g., `libgsl-dev`, `liblapack-dev`).
- Verify runtime artifacts are present in the image: `docker run --rm <image> which openEMS || which openems-smoke` and inspect `/usr/local/bin` for smoke helpers.
- Check Octave bindings by running: `docker run --rm <image> octave --eval "disp(exist('openEMS','file'))"` to verify binding availability.
- Confirm `openems/acceptance_test.sh` is executable and available at `/work/openems/acceptance_test.sh` inside the container (`ls -l /work/openems/acceptance_test.sh`).
- Rebuild with `--no-cache` if base images or earlier build steps changed (stale cache can mask changes): `docker build --no-cache -f openems/Dockerfile.openems -t xr-openems-full:latest .`.
- If builds fail on memory or CPU limits, increase available resources (more RAM, add swap) or reduce parallelism (lower `-j` value in `make`).
- Check for network/clone errors (git clone, pip install) which may indicate a blocked registry/proxy; retry in a network-enabled environment or mirror dependencies.
- If you get stuck, save and share the full Docker build log (use `--progress=plain` or redirect output to a file) and I can help triage specific failures.
