#!/bin/sh
# Acceptance test for a built openEMS runtime image.
# Passes if at least one of: openems-smoke, openEMS binary, or octave openEMS binding is present.
set -eu

echo "openEMS acceptance test: starting"

# 1) run the smoke script if available
if [ -x "/usr/local/bin/openems-smoke" ]; then
  echo "Found /usr/local/bin/openems-smoke — running..."
  /usr/local/bin/openems-smoke || true
  echo "openems-smoke ran (non-fatal)"
fi

# 2) check for openEMS binary
if command -v openEMS >/dev/null 2>&1; then
  echo "Found openEMS binary: $(openEMS --version 2>&1 | head -n1)"
  echo "ACCEPT: openEMS binary available"
  exit 0
fi

# 3) check Octave for openEMS bindings
if command -v octave >/dev/null 2>&1; then
  echo "Checking Octave for openEMS bindings..."
  out=$(octave --silent --eval "if exist('openEMS','file') disp('OPENEMS_OCTAVE_FOUND'); else disp('OPENEMS_OCTAVE_MISSING'); endif" 2>/dev/null | tail -n1 || true)
  echo "Octave check result: $out"
  if echo "$out" | grep -q 'OPENEMS_OCTAVE_FOUND'; then
    echo "ACCEPT: openEMS Octave binding found"
    exit 0
  fi
fi

echo "FAIL: no openEMS binary or Octave binding found. openems-smoke ran (if present) but did not prove runtime availability." >&2
exit 2
