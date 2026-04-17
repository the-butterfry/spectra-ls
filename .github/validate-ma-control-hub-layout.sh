#!/usr/bin/env bash
# Description: Validate MA control hub package split layout and required host include files.
# Version: 2026.04.17.1
# Last updated: 2026-04-17

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

echo "[check] validating ma_control_hub package layout"

# 1) No split YAML fragments should exist in packages/ma_control_hub
mapfile -t split_yaml < <(find packages/ma_control_hub -maxdepth 1 -type f -name '*.yaml' | sort)
if [[ ${#split_yaml[@]} -gt 0 ]]; then
  printf 'Found invalid split YAML fragments:\n' >&2
  printf '  - %s\n' "${split_yaml[@]}" >&2
  fail "packages/ma_control_hub must contain only .inc fragments"
fi

# 2) Required .inc fragments must exist
required_inc=(
  automation.inc
  input_boolean.inc
  input_number.inc
  input_select.inc
  input_text.inc
  rest.inc
  rest_command.inc
  script.inc
  template.inc
)

for f in "${required_inc[@]}"; do
  [[ -f "packages/ma_control_hub/$f" ]] || fail "missing required fragment: packages/ma_control_hub/$f"
  [[ -s "packages/ma_control_hub/$f" ]] || fail "empty fragment: packages/ma_control_hub/$f"
done

# 3) Aggregate package file must reference .inc fragments only
[[ -f "packages/ma_control_hub.yaml" ]] || fail "missing aggregate package: packages/ma_control_hub.yaml"
if grep -Eq 'ma_control_hub/.*\.yaml' packages/ma_control_hub.yaml; then
  fail "packages/ma_control_hub.yaml references .yaml fragment(s); expected .inc only"
fi

# 4) Required include-root host files must exist with IPv4-like scalar values
host_files=(
  spectra_ls_primary_tcp_host.yaml
  spectra_ls_room_tcp_host.yaml
)

for f in "${host_files[@]}"; do
  [[ -f "$f" ]] || fail "missing host include file: /config/$f"
  v="$(grep -v '^#' "$f" | tr -d '[:space:]')"
  [[ -n "$v" ]] || fail "host include file empty: /config/$f"
  [[ "$v" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]] || fail "host include is not IPv4-like in /config/$f: $v"
done

echo "PASS: ma_control_hub layout + host includes are valid"
