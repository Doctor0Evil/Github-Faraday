#!/bin/sh
# Build and run the openEMS container locally. Mounts current directory for outputs.
set -eu
IMAGE=github-faraday-openems:local

echo "Building image $IMAGE..."
docker build -t "$IMAGE" openems

echo "Running container and executing simulate_box.py..."
docker run --rm -v "$(pwd)/openems:/work" "$IMAGE"

echo "Simulation run complete. Check openems/ for output files."