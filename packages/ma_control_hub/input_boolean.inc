# Description: MA control hub boolean toggles for manual override and routing behavior.
# Version: 2026.04.17.2
# Last updated: 2026-04-17
# HUB MUST-READ: Contract parser methodology.
# - For complex attributes (`rooms`, `candidates_json`, etc.), prefer native sequence/mapping values first.
# - Only parse string JSON when trimmed payload starts with `[` or `{` and is not unknown/unavailable/none/''.
# - Never assume attribute payloads are string-only.
# - Some readers may still be unpatched; if you touch or find one, patch it to this dual-mode contract in the same change.

ma_override_active:
  name: MA Manual Override Active
  initial: false
ma_meta_override_active:
  name: MA Meta Override Active
  initial: false
ma_control_fallback_enabled:
  name: MA Control Fallback Enabled
  initial: false
