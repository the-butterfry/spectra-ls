# Description: MA control hub REST sensors for MA player snapshots.
# Version: 2026.04.17.1
# Last updated: 2026-04-17
# HUB MUST-READ: Contract parser methodology.
# - For complex attributes (`rooms`, `candidates_json`, etc.), prefer native sequence/mapping values first.
# - Only parse string JSON when trimmed payload starts with `[` or `{` and is not unknown/unavailable/none/''.
# - Never assume attribute payloads are string-only.
# - Some readers may still be unpatched; if you touch or find one, patch it to this dual-mode contract in the same change.

- resource_template: "{{ states('sensor.ma_api_url') }}"
  method: POST
  headers:
    Content-Type: "application/json"
    # NOTE: ma_ll_token should include the 'Bearer ' prefix.
    # Example in secrets.yaml: ma_ll_token: "Bearer <TOKEN>"
    Authorization: !secret ma_ll_token
  payload: '{"command": "players/all", "args": {"details": true}}'
  scan_interval: 60
  sensor:
    - name: MA Players
      value_template: >-
        {% if value_json is defined and value_json.result is defined %}
          {{ value_json.result | length }}
        {% elif value_json is defined and value_json is iterable %}
          {{ value_json | length }}
        {% else %}
          0
        {% endif %}
      json_attributes:
        - result
- resource_template: "{{ states('sensor.ma_api_url') }}"
  method: POST
  headers:
    Content-Type: "application/json"
    # NOTE: ma_ll_token should include the 'Bearer ' prefix.
    # Example in secrets.yaml: ma_ll_token: "Bearer <TOKEN>"
    Authorization: !secret ma_ll_token
  payload: >-
    {"command": "players/get", "args": {"player_id": "{{ states('sensor.ma_active_player_id_resolved') }}"}}
  scan_interval: 15
  sensor:
    - name: MA Active Player
      value_template: >-
        {% if value_json is defined and value_json.player_id is defined %}
          {{ value_json.player_id }}
        {% elif value_json is defined and value_json.result is defined and value_json.result.player_id is defined %}
          {{ value_json.result.player_id }}
        {% else %}
          {{ '' }}
        {% endif %}
      json_attributes:
        - player_id
        - current_media
        - streamdetails
        - active_source
        - app_name
        - playback_state
        - state
        - result
