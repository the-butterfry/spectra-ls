ma_update_target_options:
  mode: restart
  sequence:
    - variables:
        rooms: >-
          {% set rooms_raw = state_attr('sensor.spectra_ls_rooms_raw','rooms') %}
          {% if rooms_raw is string %}
            {% set raw_l = rooms_raw | lower %}
            {% set raw_trim = rooms_raw | trim %}
            {% if raw_l in ['unknown','unavailable','none',''] %}
              {{ [] }}
            {% elif raw_trim.startswith('[') or raw_trim.startswith('{') %}
              {{ rooms_raw | from_json }}
            {% else %}
              {{ [] }}
            {% endif %}
          {% else %}
            {{ rooms_raw or [] }}
          {% endif %}
        known_targets: >-
          {% set ns = namespace(list=[]) %}
          {% for r in rooms %}
            {% if r.entity is defined and r.entity not in ['','unknown','unavailable'] and states[r.entity] is not none %}
              {% set ns.list = ns.list + [r.entity] %}
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
          {{ (['none'] + known_targets + extra) | unique | list }}
        default_option: >-
          {% set last_ok = last_valid not in ['none','unknown','unavailable',''] and last_valid in known_targets %}
          {{ (current if current_norm not in ['none','unknown','unavailable',''] else (last_valid if last_ok else (known_targets[0] if (known_targets | length) > 0 else 'none'))) }}
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
    - choose:
        - conditions: "{{ pick_ready }}"
          sequence:
            - service: input_select.select_option
              data:
                entity_id: input_select.ma_active_target
                option: "{{ pick }}"
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
