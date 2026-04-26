# Description: MA control hub REST sensors for MA player snapshots.
# Version: 2026.04.23.2
# Last updated: 2026-04-23
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
  # NOTE: REST sensor payload is treated as literal JSON by HA REST integration.
  # Do not place Jinja block templates here (`{% ... %}`), or MA receives invalid JSON.
  payload: '{"command": "players/all", "args": {"details": true}}'
  scan_interval: 15
  sensor:
    - name: MA Active Player
      value_template: >-
        {% set rows = (value_json.result if value_json is defined and value_json.result is defined else (value_json if value_json is defined and value_json is sequence else [])) %}
        {% set pid = states('sensor.ma_active_player_id_resolved') %}
        {% set pid_short = (pid.split('.')[-1] if pid not in ['','none','unknown','unavailable'] else '') %}
        {% set ns = namespace(found='') %}
        {% for p in rows %}
          {% set p_pid = (p.player_id if p is mapping and p.player_id is defined else '') %}
          {% set p_ent = (p.entity_id if p is mapping and p.entity_id is defined else '') %}
          {% if ns.found == '' and pid not in ['','none','unknown','unavailable'] and (p_pid == pid or p_pid == pid_short or p_ent == pid or p_ent == ('media_player.' ~ pid_short)) %}
            {% set ns.found = (p_pid if p_pid not in ['','none','unknown','unavailable'] else p_ent) %}
          {% endif %}
        {% endfor %}
        {{ ns.found }}
      json_attributes:
        - player_id
        - current_media
        - streamdetails
        - active_source
        - app_name
        - playback_state
        - state
        - result
