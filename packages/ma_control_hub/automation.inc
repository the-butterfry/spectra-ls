# Description: MA control hub automations for startup sync, target selection, and override lifecycle.
# Version: 2026.04.21.3
# Last updated: 2026-04-21
# HUB MUST-READ: Contract parser methodology.
# - For complex attributes (`rooms`, `candidates_json`, etc.), prefer native sequence/mapping values first.
# - Only parse string JSON when trimmed payload starts with `[` or `{` and is not unknown/unavailable/none/''.
# - Never assume attribute payloads are string-only.
# - Some readers may still be unpatched; if you touch or find one, patch it to this dual-mode contract in the same change.

- id: ma_update_target_options_start
  alias: "MA: Update target options (startup)"
  trigger:
    - platform: homeassistant
      event: start
    - platform: state
      entity_id: sensor.ma_players
    - platform: time_pattern
      minutes: "/5"
  action:
    - choose:
        - conditions: "{{ trigger.platform == 'homeassistant' }}"
          sequence:
            - delay: "00:01:00"
    - choose:
        - conditions:
            - condition: template
              value_template: "{{ states.sensor.spectra_ls_rooms_raw is not none }}"
          sequence:
            - service: homeassistant.update_entity
              data:
                entity_id: sensor.spectra_ls_rooms_raw
    - service: script.turn_on
      data:
        entity_id: script.ma_update_target_options
    - service: script.turn_on
      data:
        entity_id: script.ma_auto_select

- id: ma_auto_select_loop
  alias: "MA: Auto select active target"
  trigger:
    - platform: state
      entity_id: sensor.ma_players
    - platform: state
      entity_id: input_select.ma_active_target
    - platform: event
      event_type: state_changed
  condition:
    - condition: template
      value_template: >-
        {% if trigger.platform != 'event' %}
          true
        {% else %}
          {% set ent = trigger.event.data.entity_id if trigger.event.data is defined else '' %}
          {% set watched = (state_attr('input_select.ma_active_target','options') or []) %}
          {{ ent in watched }}
        {% endif %}
    - condition: template
      value_template: >-
        {% set count = states('sensor.ma_players') %}
        {{ count not in ['unknown','unavailable',''] and (count | int(0)) > 0 }}
    - condition: state
      entity_id: input_boolean.ma_override_active
      state: "off"
  action:
    - service: script.turn_on
      data:
        entity_id: script.ma_auto_select

- id: ma_track_last_valid_target
  alias: "MA: Track last valid target"
  trigger:
    - platform: state
      entity_id: input_select.ma_active_target
  condition:
    - condition: template
      value_template: >-
        {% set t = states('input_select.ma_active_target') %}
        {{ t not in ['none','unknown','unavailable',''] and states[t] is not none }}
  action:
    - service: input_text.set_value
      data:
        entity_id: input_text.ma_last_valid_target
        value: "{{ states('input_select.ma_active_target') }}"

- id: ma_lock_target_on_ambiguous_select
  alias: "MA: Lock target on ambiguous select"
  trigger:
    - platform: state
      entity_id: input_select.ma_active_target
  condition:
    - condition: state
      entity_id: binary_sensor.ma_control_ambiguous
      state: "on"
    - condition: template
      value_template: >-
        {% set t = states('input_select.ma_active_target') %}
        {{ t not in ['none','unknown','unavailable',''] and states[t] is not none }}
  action:
    - service: input_boolean.turn_on
      data:
        entity_id: input_boolean.ma_override_active

- id: ma_clear_lock_on_meta_stale
  alias: "MA: Clear lock when meta stale"
  trigger:
    - platform: state
      entity_id: binary_sensor.ma_meta_stale
      to: "on"
      for: "00:00:05"
  condition:
    - condition: state
      entity_id: input_boolean.ma_override_active
      state: "on"
  action:
    - service: input_boolean.turn_off
      data:
        entity_id: input_boolean.ma_override_active
    - service: script.turn_on
      data:
        entity_id: script.ma_auto_select

- id: ma_restore_last_valid_target
  alias: "MA: Restore last valid target"
  trigger:
    - platform: homeassistant
      event: start
  action:
    - delay: "00:00:10"
    - choose:
        - conditions: >-
            {% set current = states('input_select.ma_active_target') %}
            {% set last = states('input_text.ma_last_valid_target') %}
            {% set options = state_attr('input_select.ma_active_target','options') or [] %}
            {{ current in ['none','unknown','unavailable',''] and last not in ['none','unknown','unavailable',''] and last in options }}
          sequence:
            - service: input_select.select_option
              data:
                entity_id: input_select.ma_active_target
                option: "{{ states('input_text.ma_last_valid_target') }}"

- id: ma_feedback_no_control_capable_hosts
  alias: "MA: Feedback no control-capable hosts"
  trigger:
    - platform: state
      entity_id: binary_sensor.ma_no_control_capable_hosts
      to: "on"
      for: "00:00:15"
    - platform: state
      entity_id: binary_sensor.ma_no_control_capable_hosts
      to: "off"
  action:
    - choose:
        - conditions: "{{ trigger.to_state is not none and trigger.to_state.state == 'on' }}"
          sequence:
            - service: persistent_notification.create
              data:
                notification_id: spectra_ls_no_control_capable_hosts
                title: "Spectra L/S: No control-capable hosts"
                message: >-
                  Active target: {{ states('input_select.ma_active_target') }}\n
                  Control path: {{ states('sensor.ma_active_control_path') }}\n
                  Control capable: {{ states('binary_sensor.ma_active_control_capable') }}\n
                  Control hosts: {{ states('sensor.ma_control_hosts') if states('sensor.ma_control_hosts') not in ['','none','unknown','unavailable'] else 'none' }}\n
                  Reason: {{ state_attr('binary_sensor.ma_no_control_capable_hosts','reason') | default('unknown', true) }}\n
                  Suggested action: confirm active target eligibility and rerun MA target/options refresh.
        - conditions: "{{ trigger.to_state is not none and trigger.to_state.state == 'off' }}"
          sequence:
            - service: persistent_notification.dismiss
              data:
                notification_id: spectra_ls_no_control_capable_hosts
