# Description: MA control hub REST command wrappers for MA API requests.
# Version: 2026.04.17.1
# Last updated: 2026-04-17
# HUB MUST-READ: Contract parser methodology.
# - For complex attributes (`rooms`, `candidates_json`, etc.), prefer native sequence/mapping values first.
# - Only parse string JSON when trimmed payload starts with `[` or `{` and is not unknown/unavailable/none/''.
# - Never assume attribute payloads are string-only.
# - Some readers may still be unpatched; if you touch or find one, patch it to this dual-mode contract in the same change.

ma_api_command:
  url: "{{ states('sensor.ma_api_url') }}"
  method: POST
  headers:
    Content-Type: "application/json"
    # NOTE: ma_ll_token should include the 'Bearer ' prefix.
    # Example in secrets.yaml: ma_ll_token: "Bearer <TOKEN>"
    Authorization: !secret ma_ll_token
  payload: "{{ payload }}"
  content_type: "application/json"
