#!/bin/sh
# POSIX-compatible workflow linter for GitHub-Faraday

set -eu

FAILED=0
TMPDIR="/tmp/github-faraday-lint-$$"
mkdir -p "$TMPDIR"

# helper: check whether a nearby context contains a marker
check_nearby() {
  file="$1"; lineno="$2"; marker="$3"; range=3
  start=$(( lineno - range )); [ "$start" -lt 1 ] && start=1
  end=$(( lineno + range ))
  sed -n "${start},${end}p" "$file" | grep -F -- "$marker" >/dev/null 2>&1
}

for f in .github/workflows/*.yml .github/workflows/*.yaml; do
  [ -f "$f" ] || continue

  # 1) pull_request_target check — require nearby '# faraday-reviewed'
  grep -n "pull_request_target" "$f" | cut -d: -f1 | while IFS= read -r ln; do
    if ! check_nearby "$f" "$ln" "# faraday-reviewed"; then
      echo "ERROR: $f:$ln: uses 'pull_request_target' but missing nearby '# faraday-reviewed' comment"
      FAILED=1
    fi
  done

  # 2) unpinned third-party actions
  grep -n "uses:" "$f" > "$TMPDIR/uses.$$" 2>/dev/null || true
  if [ -f "$TMPDIR/uses.$$" ]; then
    while IFS= read -r line; do
      lineno=$(echo "$line" | cut -d: -f1)
      usepart=$(echo "$line" | sed -n "s/^[0-9]*://;s/^[[:space:]]*uses:[[:space:]]*//p" | tr -d '"' | tr -d "'")
      # extract owner
      owner=$(echo "$usepart" | cut -d/ -f1)

      # If pinned with full 40-hex SHA, allow
      if echo "$usepart" | grep -Eq "@[0-9a-f]{40}$"; then
        continue
      fi

      # If using tags like @vN, @main, @master, @latest -> must be actions/* or github/*
      if echo "$usepart" | grep -Eq "@(v[0-9]+|main|master|latest)"; then
        case "$owner" in
          actions|github)
            ;;
          *)
            echo "ERROR: $f:$lineno: unpinned third-party action '$usepart' - pin to a full commit SHA"
            FAILED=1
            ;;
        esac
      fi

      # If using a version that is not a full SHA and not allowed above, flag it
      if echo "$usepart" | grep -Eq "@.+" && ! echo "$usepart" | grep -Eq "@[0-9a-f]{40}$|@(v[0-9]+|main|master|latest)"; then
        echo "ERROR: $f:$lineno: action '$usepart' uses non-SHA pin (consider full SHA)"
        FAILED=1
      fi
    done < "$TMPDIR/uses.$$"
  fi

  # 3) curl/wget piped to sh or bash
  grep -nE "curl .*\|.*(sh|bash)" "$f" >/dev/null 2>&1 || grep -nE "wget .*\|.*(sh|bash)" "$f" >/dev/null 2>&1
  if [ $? -eq 0 ]; then
    grep -nE "curl .*\|.*(sh|bash)|wget .*\|.*(sh|bash)" "$f" || true
    echo "ERROR: $f: contains curl/wget piped to shell - avoid remote scripts"
    FAILED=1
  fi

  # 4) id-token: write or permissions: write-all require nearby '# justified'
  grep -n "id-token:[[:space:]]*write\|permissions:[[:space:]]*write-all" "$f" | cut -d: -f1 | while IFS= read -r ln; do
    if ! check_nearby "$f" "$ln" "# justified"; then
      echo "ERROR: $f:$ln: sets id-token/write permissions without nearby '# justified' comment"
      FAILED=1
    fi
  done

  # 5) Warning-only: look for comments that opt-out of signed-commit or workflow protection
  if grep -nE "signed-commit|disable-signed-commit|disable-workflow-protection|workflow-protection: false" "$f" >/dev/null 2>&1; then
    echo "WARN: $f: contains comments/patterns that indicate signed-commit or workflow-protection may be disabled. Enforce via GitHub rulesets/branch protection rather than comments."
  fi

done

rm -rf "$TMPDIR"

if [ "$FAILED" -eq 1 ]; then
  echo "One or more workflow lint checks failed"
  exit 1
fi

echo "OK: No lint violations found"