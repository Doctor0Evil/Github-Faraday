# Minimal container for running openEMS simulations (placeholder-capable)
# NOTE: This Dockerfile intentionally includes only light deps for the
# placeholder path. To build a full openEMS environment, add native build
# steps (compilation, dependencies) — see README.DOCKER_NOTES.md for guidance.

FROM python:3.10-slim

# Keep image lean: placeholder simulation needs only the standard library.
# Optionally install numpy/scipy for richer post-processing.
RUN pip install --no-cache-dir numpy scipy matplotlib

WORKDIR /work
COPY . /work

# If you later need to build openEMS from source, add steps like:
# RUN apt-get update && apt-get install -y build-essential gfortran libfftw3-dev libx11-dev
# RUN git clone https://github.com/thliebig/openEMS-Project.git && cd openEMS-Project && make ...

CMD ["python3", "openems/simulate_box.py"]
