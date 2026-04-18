# Description: Music Assistant control hub scripts (target options, auto-select, control helpers).
# Version: 2026.04.17.8
# Last updated: 2026-04-17
# Update version/date whenever you change this file.
# HUB MUST-READ: Contract parser methodology.
# - For complex attributes (`rooms`, `candidates_json`, etc.), prefer native sequence/mapping values first.
# - Only parse string JSON when trimmed payload starts with `[` or `{` and is not unknown/unavailable/none/''.
# - Never assume attribute payloads are string-only.
# - Some readers may still be unpatched; if you touch or find one, patch it to this dual-mode contract in the same change.

ma_update_target_options:
  mode: restart
  sequence:
    - variables:
        rooms: >-
          {% set rooms_raw = state_attr('sensor.spectra_ls_rooms_raw','rooms') %}
          {% if rooms_raw is sequence and rooms_raw is not string and rooms_raw is not mapping %}
            {{ rooms_raw }}
          {% elif rooms_raw is mapping %}
            {% set mapped = (rooms_raw.rooms if rooms_raw.rooms is defined else (rooms_raw.result if rooms_raw.result is defined else [])) %}
            {% if mapped is sequence and mapped is not string and mapped is not mapping %}
              {{ mapped }}
            {% else %}
              {{ [] }}
            {% endif %}
          {% elif rooms_raw is string %}
            {% set raw_trim = rooms_raw | trim %}
            {% set raw_trim_l = raw_trim | lower %}
            {% if raw_trim_l not in ['unknown','unavailable','none',''] and (raw_trim.startswith('[') or raw_trim.startswith('{')) %}
              {% set parsed = rooms_raw | from_json %}
              {% if parsed is sequence and parsed is not string and parsed is not mapping %}
                {{ parsed }}
              {% elif parsed is mapping %}
                {% set mapped = (parsed.rooms if parsed.rooms is defined else (parsed.result if parsed.result is defined else [])) %}
                {% if mapped is sequence and mapped is not string and mapped is not mapping %}
                  {{ mapped }}
                {% else %}
                  {{ [] }}
                {% endif %}
              {% else %}
                {{ [] }}
              {% endif %}
            {% else %}
              {{ [] }}
            {% endif %}
          {% else %}
            {{ [] }}
          {% endif %}
        known_targets: >-
          {% set ns = namespace(list=[]) %}
          {% for r in rooms %}
            {% if r.entity is defined and r.entity not in ['','unknown','unavailable'] and states[r.entity] is not none %}
              {% set ns.list = ns.list + [r.entity] %}
            {% endif %}
          {% endfor %}
          {{ ns.list }}
        discovered_targets: >-
          {% set players = state_attr('sensor.ma_players','result') or [] %}
          {% set ns = namespace(list=[]) %}
          {% for p in players %}
            {% set ent = (p.entity_id if p.entity_id is defined else '') %}
            {% set ip = (state_attr(ent,'ip_address') if ent not in ['','none','unknown','unavailable'] else '') or (p.ip_address if p.ip_address is defined else '') %}
            {% set model = (state_attr(ent,'device_model') if ent not in ['','none','unknown','unavailable'] else '') or '' %}
            {% set manufacturer = (state_attr(ent,'manufacturer') if ent not in ['','none','unknown','unavailable'] else '') or '' %}
            {% set purpose = (state_attr(ent,'integration_purpose') if ent not in ['','none','unknown','unavailable'] else '') or '' %}
            {% set ma_ok = (state_attr(ent,'music_assistant_compatible') if ent not in ['','none','unknown','unavailable'] else none) %}
            {% set cap_hint = (state_attr(ent,'control_capable') if ent not in ['','none','unknown','unavailable'] else '') %}
            {% set cap_l = (cap_hint | string | lower) %}
            {% set hint = (model ~ ' ' ~ manufacturer ~ ' ' ~ purpose ~ ' ' ~ ent) | lower %}
            {% set is_linkplay = ('arylic' in hint) or ('linkplay' in hint) or ('up2stream' in hint) %}
            {% set control_path = 'linkplay_tcp' if (ip not in ['','none','unknown','unavailable','None', none] and ((ma_ok is true) or is_linkplay)) else 'other' %}
            {% set control_capable = (cap_l in ['1','true','yes','on']) if cap_l not in ['','none','unknown','unavailable'] else (control_path == 'linkplay_tcp') %}
            {% if ent not in ['','none','unknown','unavailable']
                  and (ent | regex_match('^media_player\\.'))
                  and states[ent] is not none
                  and control_path == 'linkplay_tcp'
                  and control_capable %}
              {% set ns.list = ns.list + [ent] %}
            {% endif %}
          {% endfor %}
          {{ ns.list }}
        detected_receiver: >-
          {{ states('sensor.ma_detected_receiver_entity') }}
        detected_valid: >-
          {% set dr = states('sensor.ma_detected_receiver_entity') %}
          {{ dr not in ['none','unknown','unavailable',''] and states[dr] is not none }}
        current: >-
          {{ states('input_select.ma_active_target') }}
        last_valid: >-
          {{ states('input_text.ma_last_valid_target') }}
        current_norm: >-
          {{ (current | lower) if current is not none else '' }}
        current_is_none: >-
          {{ current_norm in ['none','unknown','unavailable',''] }}
        final_options: >-
          {% set extra = ([current] if (current_norm not in ['none','unknown','unavailable',''] and current not in known_targets) else []) %}
          {{ (['none'] + known_targets + discovered_targets + extra) | unique | list }}
        default_option: >-
          {% set selectable = (known_targets + discovered_targets) | unique | list %}
          {% set last_ok = last_valid not in ['none','unknown','unavailable',''] and last_valid in selectable %}
          {{ (current if current_norm not in ['none','unknown','unavailable',''] else (last_valid if last_ok else (selectable[0] if (selectable | length) > 0 else 'none'))) }}
    - service: input_select.set_options
      data:
        entity_id: input_select.ma_active_target
        options: "{{ final_options }}"
    - choose:
        - conditions: "{{ current_is_none or current not in final_options }}"
          sequence:
            - service: input_select.select_option
              data:
                entity_id: input_select.ma_active_target
                option: "{{ default_option }}"

ma_cycle_target:
  mode: restart
  sequence:
    - service: input_boolean.turn_on
      data:
        entity_id: input_boolean.ma_override_active
    - variables:
        options: "{{ state_attr('input_select.ma_active_target','options') or [] }}"
        current: "{{ states('input_select.ma_active_target') }}"
    - choose:
        - conditions: "{{ options | length > 0 }}"
          sequence:
            - variables:
                idx: "{{ options.index(current) if current in options else -1 }}"
                next: "{{ options[(idx + 1) % (options | length)] }}"
            - service: input_select.select_option
              data:
                entity_id: input_select.ma_active_target
                option: "{{ next }}"

ma_auto_select:
  mode: restart
  sequence:
    - variables:
        override_on: "{{ is_state('input_boolean.ma_override_active','on') }}"
        current: "{{ states('input_select.ma_active_target') }}"
        current_state: >-
          {% if current.startswith('media_player.') and states[current] is not none %}
            {{ states(current) | lower }}
          {% else %}
            {{ '' }}
          {% endif %}
        detected: "{{ states('sensor.ma_detected_receiver_entity') }}"
        detected_state: >-
          {% if detected.startswith('media_player.') and states[detected] is not none %}
            {{ states(detected) | lower }}
          {% else %}
            {{ '' }}
          {% endif %}
        detected_playing: >-
          {{ detected_state == 'playing' }}
        current_invalid: >-
          {{ current in ['none','unknown','unavailable',''] or states[current] is none or current_state in ['','unknown','unavailable'] }}
        current_playing: >-
          {{ current not in ['none','unknown','unavailable',''] and current_state == 'playing' }}
        current_active: >-
          {{ current not in ['none','unknown','unavailable',''] and current_state in ['playing','paused'] }}
        idle_threshold: "{{ states('input_number.ma_auto_idle_s') | float(45) }}"
        current_idle_s: >-
          {% if current in ['none','unknown','unavailable',''] or states[current] is none %}
            999999
          {% else %}
            {{ (as_timestamp(now()) - as_timestamp(states[current].last_changed)) | float(0) }}
          {% endif %}
        current_idle_long: "{{ current_idle_s >= idle_threshold }}"
    - choose:
        - conditions: "{{ current_playing }}"
          sequence:
            - stop: "Auto-select skipped (current target playing)."
        - conditions: "{{ override_on and current_playing }}"
          sequence:
            - stop: "Manual override active (current target playing)."
        - conditions: "{{ override_on and not current_active }}"
          sequence:
            - service: input_boolean.turn_off
              data:
                entity_id: input_boolean.ma_override_active
        - conditions: "{{ not current_active and not current_idle_long and not detected_playing }}"
          sequence:
            - stop: "Auto-select delayed (current target not idle long enough)."
    - variables:
        allowed_players: >-
          {{ state_attr('input_select.ma_active_target','options') or [] }}
        players: >-
          {% set ids = (allowed_players | select('match','^media_player\\.') | list) %}
          {% set ns = namespace(list=[]) %}
          {% for e in ids %}
            {% if states[e] is not none %}
              {% set st = states(e) %}
              {% if st not in ['unknown','unavailable',''] %}
                {% set ns.list = ns.list + [e] %}
              {% endif %}
            {% endif %}
          {% endfor %}
          {{ ns.list }}
        pick: "{{ states('sensor.ma_detected_receiver_entity') }}"
        pick_state: >-
          {% if pick not in ['','none','unknown','unavailable'] and states[pick] is not none %}
            {{ states(pick) | lower }}
          {% else %}
            {{ '' }}
          {% endif %}
        pick_ready: >-
          {{ pick not in ['','none','unknown','unavailable'] and pick in (state_attr('input_select.ma_active_target','options') or []) and pick_state not in ['','unknown','unavailable'] }}
        first_active_allowed: >-
          {% set opts = (state_attr('input_select.ma_active_target','options') or []) %}
          {% set ns = namespace(ent='') %}
          {% for e in opts %}
            {% if ns.ent == '' and e is string and e.startswith('media_player.') and states[e] is not none %}
              {% set st = states(e) | lower %}
              {% if st in ['playing','paused'] %}
                {% set ns.ent = e %}
              {% endif %}
            {% endif %}
          {% endfor %}
          {{ ns.ent }}
    - choose:
        - conditions: "{{ pick_ready }}"
          sequence:
            - service: input_select.select_option
              data:
                entity_id: input_select.ma_active_target
                option: "{{ pick }}"
        - conditions: "{{ first_active_allowed not in ['', 'none', 'unknown', 'unavailable'] }}"
          sequence:
            - service: input_select.select_option
              data:
                entity_id: input_select.ma_active_target
                option: "{{ first_active_allowed }}"
        - conditions: "{{ not pick_ready }}"
          sequence:
            - stop: "Auto-select skipped (no active playing target)."

ma_set_volume:
  mode: restart
  fields:
    volume:
      description: "Volume 0..1"
      example: 0.35
  sequence:
    - stop: "MA volume set disabled (read-only)."


ma_set_balance:
  mode: restart
  fields:
    balance:
      description: "Balance -1..1"
      example: -0.3
  sequence:
    - stop: "MA balance disabled (read-only volume)."
