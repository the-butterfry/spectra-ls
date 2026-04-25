# Description: MA control hub command-line discovery sensors.
# Version: 2026.04.25.1
# Last updated: 2026-04-25
# HUB MUST-READ: Contract parser methodology.
# - For complex attributes (`rooms`, `candidates_json`, etc.), prefer native sequence/mapping values first.
# - Only parse string JSON when trimmed payload starts with `[` or `{` and is not unknown/unavailable/none/''.
# - Never assume attribute payloads are string-only.
# - Some readers may still be unpatched; if you touch or find one, patch it to this dual-mode contract in the same change.

- sensor:
    name: MA PyWiiM Discovery
    command: >-
      /bin/sh -c 'if command -v wiim-discover >/dev/null 2>&1; then
      wiim-discover --output json --ssdp-timeout 5;
      elif [ -f /config/bin/pywiim_discover_targets.py ]; then
      python3 /config/bin/pywiim_discover_targets.py --ssdp-timeout 5;
      else
      printf "{\"count\":0,\"devices\":[],\"status\":\"missing\"}";
      fi'
    value_template: >-
      {{ value_json.count if value_json is defined and value_json.count is defined else 0 }}
    json_attributes:
      - count
      - devices
      - validate
      - ssdp_timeout
      - status
      - error
    scan_interval: 300
