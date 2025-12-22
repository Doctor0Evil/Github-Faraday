#!/bin/bash
# Build the full openEMS Docker image locally (long-running)
set -euo pipefail
IMAGE_NAME=xr-openems-full:latest
DOCKERFILE=openems/Dockerfile.openems

ARTIFACT_DIR=openems/artifacts
mkdir -p "$ARTIFACT_DIR"

echo "Building full openEMS image: $IMAGE_NAME (this may take a long time)..."

# Capture build output to an artifact log
if docker build -f "$DOCKERFILE" -t "$IMAGE_NAME" . 2>&1 | tee "$ARTIFACT_DIR/docker_build.log"; then
  echo "Build complete: $IMAGE_NAME"
else
  echo "Build failed; see $ARTIFACT_DIR/docker_build.log for details"
  exit 1
fi

echo "Run smoke test: docker run --rm -v \"$(pwd)/openems:/work\" $IMAGE_NAME /usr/local/bin/openems-smoke"
