# Description: Music Assistant control hub scripts (target options, auto-select, control helpers).
# Version: 2026.04.28.6
# Last updated: 2026-04-28
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
          {% set rooms_raw = state_attr('sensor.spectra_ls_rooms_json','rooms_json') | default([], true) %}
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
              {% set parsed = raw_trim | from_json %}
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
        excluded_targets: >-
          {{ (label_entities('no-spectra') + label_entities('no_spectra')) | unique | list }}
        known_targets: >-
          {% set ns = namespace(list=[]) %}
          {% for r in rooms %}
            {% if r.entity is defined and r.entity not in ['','unknown','unavailable'] and states[r.entity] is not none and r.entity not in excluded_targets %}
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
                  and ent not in excluded_targets
              and ip not in ['','none','unknown','unavailable','None', none] %}
              {% set ns.list = ns.list + [ent] %}
            {% endif %}
          {% endfor %}
          {{ ns.list }}
        discovered_live_targets: >-
          {% set ns = namespace(list=[]) %}
          {% for s in states.media_player %}
            {% set ent = s.entity_id %}
            {% set ip = state_attr(ent,'ip_address') %}
            {% set control_capable_attr = state_attr(ent,'control_capable') %}
            {% set control_path = (state_attr(ent,'control_path') | string | lower) %}
            {% set model = (state_attr(ent,'device_model') | string | lower) %}
            {% set manufacturer = (state_attr(ent,'manufacturer') | string | lower) %}
            {% set purpose = (state_attr(ent,'integration_purpose') | string | lower) %}
            {% set hint = (ent ~ ' ' ~ model ~ ' ' ~ manufacturer ~ ' ' ~ purpose) | lower %}
            {% set hint_supported = ('wiim' in hint) or ('linkplay' in hint) or ('arylic' in hint) or ('up2stream' in hint) %}
            {% set control_capable = control_capable_attr in [true, 'true', 'True', '1', 1, 'yes', 'on'] %}
            {% set control_path_ok = control_path in ['linkplay_tcp'] %}
            {% if ent not in ['','none','unknown','unavailable']
                  and states[ent] is not none
                  and ent not in excluded_targets
                  and ip not in ['','none','unknown','unavailable','None', none]
                  and (control_capable or control_path_ok or hint_supported) %}
              {% set ns.list = ns.list + [ent] %}
            {% endif %}
          {% endfor %}
          {{ ns.list }}
        detected_candidate: >-
          {% set dr = states('sensor.ma_detected_receiver_entity') %}
          {% if dr not in ['','none','unknown','unavailable'] and (dr | regex_match('^media_player\.')) and states[dr] is not none and dr not in excluded_targets %}
            {{ dr }}
          {% else %}
            {{ '' }}
          {% endif %}
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
        current_excluded: >-
          {{ current not in ['none','unknown','unavailable',''] and current in excluded_targets }}
        final_options: >-
          {% set extra = ([current] if (current_norm not in ['none','unknown','unavailable',''] and current not in known_targets and current not in excluded_targets) else []) %}
          {% set detected_extra = ([detected_candidate] if detected_candidate not in ['','none','unknown','unavailable'] else []) %}
          {{ (['none'] + known_targets + discovered_targets + discovered_live_targets + detected_extra + extra) | unique | list }}
        default_option: >-
          {% set selectable = (known_targets + discovered_targets + discovered_live_targets + ([detected_candidate] if detected_candidate not in ['','none','unknown','unavailable'] else [])) | unique | list %}
          {% set last_ok = last_valid not in ['none','unknown','unavailable',''] and last_valid in selectable %}
          {{ (current if (current_norm not in ['none','unknown','unavailable',''] and (not current_excluded) and current in selectable) else (last_valid if last_ok else (selectable[0] if (selectable | length) > 0 else 'none'))) }}
    - service: input_select.set_options
      data:
        entity_id: input_select.ma_active_target
        options: "{{ final_options }}"
    - choose:
        - conditions: "{{ detected_candidate not in ['','none','unknown','unavailable'] and detected_candidate not in (state_attr('input_select.ma_active_target','options') or []) }}"
          sequence:
            - service: input_select.set_options
              data:
                entity_id: input_select.ma_active_target
                options:
                  - none
                  - "{{ detected_candidate }}"
    - choose:
        - conditions: "{{ current_is_none or current not in (state_attr('input_select.ma_active_target','options') or []) }}"
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


ma_send_metadata_to_providers:
  mode: restart
  fields:
    reason:
      description: "Optional audit reason for metadata provider refresh dispatch."
      example: "step3_validation_refresh"
    force_refresh:
      description: "If true, request provider-side force refresh (default true)."
      example: true
  sequence:
    - variables:
        reason_text: "{{ reason | default('manual_dispatch', true) }}"
        force_refresh_bool: >-
          {% if force_refresh is not defined %}
            {{ true }}
          {% elif force_refresh is sameas true %}
            {{ true }}
          {% elif force_refresh is sameas false %}
            {{ false }}
          {% elif force_refresh is number %}
            {{ (force_refresh | int(0)) != 0 }}
          {% elif force_refresh is string %}
            {% set fr = force_refresh | trim | lower %}
            {{ fr in ['1','true','yes','on'] }}
          {% else %}
            {{ true }}
          {% endif %}
        np_fields_raw: "{{ state_attr('sensor.now_playing_entity','player_fields_json') | default('', true) }}"
        np_fields: >-
          {% if np_fields_raw is mapping %}
            {{ np_fields_raw }}
          {% elif np_fields_raw is string %}
            {% set raw_trim = np_fields_raw | trim %}
            {% set raw_trim_l = raw_trim | lower %}
            {% if raw_trim_l not in ['unknown','unavailable','none',''] and raw_trim.startswith('{') %}
              {{ raw_trim | from_json }}
            {% else %}
              {{ {} }}
            {% endif %}
          {% else %}
            {{ {} }}
          {% endif %}
        ap_json_raw: "{{ state_attr('sensor.ma_active_player_id_resolved','player_json') | default('', true) }}"
        ap_json: >-
          {% if ap_json_raw is mapping %}
            {{ ap_json_raw }}
          {% elif ap_json_raw is string %}
            {% set raw_trim = ap_json_raw | trim %}
            {% set raw_trim_l = raw_trim | lower %}
            {% if raw_trim_l not in ['unknown','unavailable','none',''] and raw_trim.startswith('{') %}
              {{ raw_trim | from_json }}
            {% else %}
              {{ {} }}
            {% endif %}
          {% else %}
            {{ {} }}
          {% endif %}
        item_uri: >-
          {% set pf_uri = (np_fields.ma_uri if np_fields is mapping and np_fields.ma_uri is defined else '') | string %}
          {% set ap_uri = (ap_json.current_media.uri if ap_json is mapping and ap_json.current_media is defined and ap_json.current_media is mapping and ap_json.current_media.uri is defined else '') | string %}
          {% set np_entity = states('sensor.now_playing_entity') %}
          {% set np_media_id = (state_attr(np_entity, 'media_content_id') if np_entity not in ['none','unknown','unavailable',''] and states[np_entity] is not none else '') | string %}
          {% set cand = pf_uri if pf_uri | trim not in ['','none','unknown','unavailable'] else (ap_uri if ap_uri | trim not in ['','none','unknown','unavailable'] else np_media_id) %}
          {{ cand | trim }}
        item_uri_l: "{{ item_uri | lower }}"
        item_uri_is_valid: >-
          {{ item_uri_l not in ['','none','unknown','unavailable'] and (':' in item_uri) }}
        payload_json: >-
          {{ {
                'message_id': 'spectra_meta_refresh_' ~ (as_timestamp(now()) | int),
                'command': 'metadata/update_metadata',
                'args': {
                  'item': item_uri,
                  'force_refresh': force_refresh_bool,
                  'reason': reason_text
                }
             } | tojson }}
    - choose:
        - conditions: "{{ not item_uri_is_valid }}"
          sequence:
            - service: input_text.set_value
              data:
                entity_id: input_text.ma_metadata_provider_last_status
                value: "skipped_invalid_uri"
            - service: input_text.set_value
              data:
                entity_id: input_text.ma_metadata_provider_last_response
                value: "No valid MA item URI resolved"
            - service: input_text.set_value
              data:
                entity_id: input_text.ma_metadata_provider_last_providers
                value: "no_dispatch_invalid_uri"
            - service: input_text.set_value
              data:
                entity_id: input_text.ma_metadata_provider_last_item_uri
                value: "{{ item_uri }}"
            - service: input_text.set_value
              data:
                entity_id: input_text.ma_metadata_provider_last_reason
                value: "{{ reason_text }}"
            - service: input_text.set_value
              data:
                entity_id: input_text.ma_metadata_provider_last_updated_at
                value: "{{ now() }}"
            - stop: >-
                Metadata provider refresh skipped: no valid MA item URI resolved
                (candidate='{{ item_uri }}').
    - service: rest_command.ma_api_command
      data:
        payload: "{{ payload_json }}"
      response_variable: ma_metadata_refresh_response
    - variables:
        response_status: >-
          {{ (ma_metadata_refresh_response.status if ma_metadata_refresh_response is mapping and ma_metadata_refresh_response.status is defined else 0) | int(0) }}
        response_content_raw: >-
          {% if ma_metadata_refresh_response is mapping and ma_metadata_refresh_response.content is defined %}
            {{ ma_metadata_refresh_response.content }}
          {% else %}
            {{ {} }}
          {% endif %}
        response_content_map: >-
          {% if response_content_raw is mapping %}
            {{ response_content_raw }}
          {% elif response_content_raw is sequence and response_content_raw is not string and response_content_raw is not mapping %}
            {% if (response_content_raw | count) > 0 and response_content_raw[0] is mapping %}
              {{ response_content_raw[0] }}
            {% else %}
              {{ {} }}
            {% endif %}
          {% elif response_content_raw is string %}
            {% set raw_trim = response_content_raw | trim %}
            {% set raw_trim_l = raw_trim | lower %}
            {% if raw_trim_l not in ['unknown','unavailable','none',''] and (raw_trim.startswith('{') or raw_trim.startswith('[')) %}
              {% set parsed = raw_trim | from_json %}
              {% if parsed is mapping %}
                {{ parsed }}
              {% elif parsed is sequence and parsed is not string and parsed is not mapping and (parsed | count) > 0 and parsed[0] is mapping %}
                {{ parsed[0] }}
              {% else %}
                {{ {} }}
              {% endif %}
            {% else %}
              {{ {} }}
            {% endif %}
          {% else %}
            {{ {} }}
          {% endif %}
        provider_rows: >-
          {% if response_content_map is mapping and response_content_map.providers is defined and response_content_map.providers is sequence and response_content_map.providers is not string %}
            {{ response_content_map.providers }}
          {% elif response_content_map is mapping and response_content_map.provider_results is defined and response_content_map.provider_results is sequence and response_content_map.provider_results is not string %}
            {{ response_content_map.provider_results }}
          {% elif response_content_map is mapping and response_content_map.results is defined and response_content_map.results is sequence and response_content_map.results is not string %}
            {{ response_content_map.results }}
          {% else %}
            {{ [] }}
          {% endif %}
        provider_summary: >-
          {% set ns = namespace(list=[]) %}
          {% for p in provider_rows %}
            {% set pname = '' %}
            {% set pstatus = '' %}
            {% if p is mapping %}
              {% set pname = (
                p.provider if p.provider is defined else (
                p.provider_name if p.provider_name is defined else (
                p.name if p.name is defined else (
                p.provider_id if p.provider_id is defined else 'provider')))) | string %}
              {% set pstatus = (
                p.status if p.status is defined else (
                p.result if p.result is defined else (
                p.state if p.state is defined else (
                p.error if p.error is defined else 'ok')))) | string %}
            {% elif p is string %}
              {% set pname = p %}
              {% set pstatus = 'ok' %}
            {% endif %}
            {% set pname = pname | trim %}
            {% set pstatus = pstatus | trim %}
            {% if pname == '' %}{% set pname = 'provider' %}{% endif %}
            {% if pstatus == '' %}{% set pstatus = 'ok' %}{% endif %}
            {% if (ns.list | length) < 6 %}
              {% set ns.list = ns.list + [pname ~ ':' ~ pstatus] %}
            {% endif %}
          {% endfor %}
          {% if ns.list | length > 0 %}
            {{ ns.list | join('; ') }}
          {% elif response_status >= 400 %}
            {{ 'request_error_' ~ response_status }}
          {% else %}
            {{ 'no_provider_rows_in_response' }}
          {% endif %}
        provider_summary_compact: "{{ (provider_summary | string)[:250] }}"
        response_raw: >-
          {% if ma_metadata_refresh_response is mapping and ma_metadata_refresh_response.content is defined %}
            {{ ma_metadata_refresh_response.content | tojson }}
          {% elif ma_metadata_refresh_response is mapping %}
            {{ ma_metadata_refresh_response | tojson }}
          {% else %}
            {{ ma_metadata_refresh_response | string }}
          {% endif %}
        response_compact: "{{ (response_raw | string)[:250] }}"
        status_text: >-
          {{ ('error_' ~ response_status) if response_status >= 400 else ('ok_' ~ (response_status if response_status > 0 else 200)) }}
    - service: input_text.set_value
      data:
        entity_id: input_text.ma_metadata_provider_last_status
        value: "{{ status_text }}"
    - service: input_text.set_value
      data:
        entity_id: input_text.ma_metadata_provider_last_response
        value: "{{ response_compact }}"
    - service: input_text.set_value
      data:
        entity_id: input_text.ma_metadata_provider_last_providers
        value: "{{ provider_summary_compact }}"
    - service: input_text.set_value
      data:
        entity_id: input_text.ma_metadata_provider_last_item_uri
        value: "{{ item_uri }}"
    - service: input_text.set_value
      data:
        entity_id: input_text.ma_metadata_provider_last_reason
        value: "{{ reason_text }}"
    - service: input_text.set_value
      data:
        entity_id: input_text.ma_metadata_provider_last_updated_at
        value: "{{ now() }}"
    - choose:
        - conditions: >-
            {{ ma_metadata_refresh_response is mapping and
               ma_metadata_refresh_response.status is defined and
               (ma_metadata_refresh_response.status | int(0)) >= 400 }}
          sequence:
            - stop: >-
                Metadata provider refresh failed (status={{ ma_metadata_refresh_response.status }}).
    - stop: >-
        Metadata provider refresh dispatched for item='{{ item_uri }}'
        (reason='{{ reason_text }}').
