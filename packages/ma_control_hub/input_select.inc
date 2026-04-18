# Description: MA control hub select helpers for active target routing.
# Version: 2026.04.17.1
# Last updated: 2026-04-17
# HUB MUST-READ: Contract parser methodology.
# - For complex attributes (`rooms`, `candidates_json`, etc.), prefer native sequence/mapping values first.
# - Only parse string JSON when trimmed payload starts with `[` or `{` and is not unknown/unavailable/none/''.
# - Never assume attribute payloads are string-only.
# - Some readers may still be unpatched; if you touch or find one, patch it to this dual-mode contract in the same change.

ma_active_target:
  name: MA Active Target
  options:
    - none
  initial: none
