#!/usr/bin/env bash
# Description: Validate MA control hub package split layout and secrets-based host defaults.
# Version: 2026.04.17.2
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

# 4) input_text host defaults must be secrets-based (never include tracked per-user files)
input_text_fragment="packages/ma_control_hub/input_text.inc"
[[ -f "$input_text_fragment" ]] || fail "missing fragment: $input_text_fragment"

grep -q 'initial:[[:space:]]*!secret[[:space:]]*spectra_ls_primary_tcp_host' "$input_text_fragment" \
  || fail "primary host default must use !secret spectra_ls_primary_tcp_host"
grep -q 'initial:[[:space:]]*!secret[[:space:]]*spectra_ls_room_tcp_host' "$input_text_fragment" \
  || fail "room host default must use !secret spectra_ls_room_tcp_host"

if grep -Eq 'spectra_ls_(primary|room)_tcp_host\.yaml' "$input_text_fragment"; then
  fail "input_text host defaults must not use include files"
fi

echo "PASS: ma_control_hub layout + secrets-based host defaults are valid"
