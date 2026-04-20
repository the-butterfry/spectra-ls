<!-- Description: Copy/paste Home Assistant Dev Tools template diagnostics for Spectra LS System. -->
<!-- Version: 2026.04.19.28 -->
<!-- Last updated: 2026-04-19 -->

# Spectra LS System — Dev Tools Template Validation

> Tracked diagnostics guide for repeatable Spectra LS system validation.  
> Use each template by copying into **Home Assistant → Developer Tools → Template**.

## Copy/Paste Quick Path (Raw Templates)

- If markdown code fences are annoying, use raw Jinja files (no backticks) under:
  - `docs/testing/raw/`
- Current raw templates:
  - `docs/testing/raw/p2_registry_router_verification.jinja`
  - `docs/testing/raw/p2_negative_case_regression.jinja`
  - `docs/testing/raw/p3_s01_guarded_write_validation.jinja`
  - `docs/testing/raw/p3_s02_selection_handoff_validation.jinja`
  - `docs/testing/raw/p3_s01_s02_soak_protocol.md`
  - `docs/testing/raw/p3_s01_s02_closure_gate_check.jinja`

## 1) Overall Spectra LS Health Check (Comprehensive)

```jinja
{# =========================
  Spectra LS Comprehensive Health Check
  Paste into HA Developer Tools -> Template
  ========================= #}

{% set critical_helpers = [
  'input_select.ma_active_target',
  'input_boolean.ma_override_active',
  'input_boolean.ma_meta_override_active',
  'input_number.ma_meta_confidence_min',
  'input_number.ma_meta_stale_s',
  'input_text.ma_server_url',
  'input_text.ma_last_valid_target'
] %}

{% set critical_runtime = [
  'sensor.spectra_ls_rooms_raw',
  'sensor.ma_control_hosts',
  'sensor.ma_control_host',
  'sensor.ma_active_target_by_host',
  'sensor.ma_active_meta_entity',
  'sensor.now_playing_entity',
  'sensor.now_playing_title',
  'sensor.now_playing_state'
] %}

{% set package_entity_sentinels = [
  'script.ma_update_target_options',
  'script.ma_auto_select',
  'script.ma_set_volume',
  'script.ma_set_balance',
  'sensor.ma_api_url'
] %}

{% set automation_id_sentinels = [
  'ma_update_target_options_start',
  'ma_auto_select_loop',
  'ma_track_last_valid_target'
] %}

{% set ns = namespace(total=0, ok=0, missing=[], unavailable=[], rows=[]) %}

{% for eid in critical_helpers %}
  {% set ns.total = ns.total + 1 %}
  {% set exists = states[eid] is not none %}
  {% set state = states(eid) if exists else 'missing' %}
  {% if exists %}
    {% set ns.ok = ns.ok + 1 %}
  {% else %}
    {% set ns.missing = ns.missing + [eid] %}
  {% endif %}
  {% set ns.rows = ns.rows + [{'tier':'helper','entity':eid,'exists':exists,'state':state}] %}
{% endfor %}

{% for eid in critical_runtime %}
  {% set ns.total = ns.total + 1 %}
  {% set exists = states[eid] is not none %}
  {% set state = states(eid) if exists else 'missing' %}
  {% if exists %}
    {% if state in ['unknown','unavailable'] %}
      {% set ns.unavailable = ns.unavailable + [eid] %}
    {% else %}
      {% set ns.ok = ns.ok + 1 %}
    {% endif %}
  {% else %}
    {% set ns.missing = ns.missing + [eid] %}
  {% endif %}
  {% set ns.rows = ns.rows + [{'tier':'runtime','entity':eid,'exists':exists,'state':state}] %}
{% endfor %}

{% for eid in package_entity_sentinels %}
  {% set ns.total = ns.total + 1 %}
  {% set exists = states[eid] is not none %}
  {% set state = states(eid) if exists else 'missing' %}
  {% if exists %}
    {% set ns.ok = ns.ok + 1 %}
  {% else %}
    {% set ns.missing = ns.missing + [eid] %}
  {% endif %}
  {% set ns.rows = ns.rows + [{'tier':'package-sentinel','entity':eid,'exists':exists,'state':state}] %}
{% endfor %}

{% for aid in automation_id_sentinels %}
  {% set ns.total = ns.total + 1 %}
  {% set probe = namespace(found=false, match='') %}
  {% for a in states.automation %}
    {% set current_id = (a.attributes.id if a.attributes is defined and a.attributes.id is defined else '') %}
    {% if current_id == aid %}
      {% set probe.found = true %}
      {% set probe.match = a.entity_id %}
    {% endif %}
  {% endfor %}
  {% if probe.found %}
    {% set ns.ok = ns.ok + 1 %}
  {% else %}
    {% set ns.missing = ns.missing + ['automation_id:' ~ aid] %}
  {% endif %}
  {% set ns.rows = ns.rows + [{'tier':'package-sentinel-id','entity':'automation_id:' ~ aid,'exists':probe.found,'state':(probe.match if probe.found else 'missing')}] %}
{% endfor %}

{% set target = states('input_select.ma_active_target') %}
{% set target_exists = target not in ['unknown','unavailable','none',''] and states[target] is not none %}
{% set target_options = state_attr('input_select.ma_active_target','options') or [] %}

{% set rooms_attr = state_attr('sensor.spectra_ls_rooms_raw','rooms') %}
{% set rooms_attr_type = 'none' %}
{% if rooms_attr is mapping %}
  {% set rooms_attr_type = 'mapping' %}
{% elif rooms_attr is sequence and rooms_attr is not string %}
  {% set rooms_attr_type = 'list' %}
{% elif rooms_attr is string %}
  {% set rooms_attr_type = 'string' %}
{% endif %}

{% set health = 'PASS' %}
{% if (ns.missing | length) > 0 %}
  {% set health = 'FAIL' %}
{% elif (ns.unavailable | length) > 0 %}
  {% set health = 'WARN' %}
{% endif %}

### Spectra LS Health Summary
- Result: **{{ health }}**
- Timestamp: **{{ now() }}**
- Checked entities: **{{ ns.total }}**
- OK: **{{ ns.ok }}**
- Missing: **{{ ns.missing | length }}**
- Unknown/Unavailable runtime: **{{ ns.unavailable | length }}**

### Key runtime wiring
- `input_select.ma_active_target`: **{{ target }}**
- Active target exists in state machine: **{{ target_exists }}**
- Active target options count: **{{ target_options | length }}**
- `sensor.spectra_ls_rooms_raw` rooms attr type: **{{ rooms_attr_type }}**
- `sensor.ma_control_host`: **{{ states('sensor.ma_control_host') }}**
- `sensor.ma_control_hosts`: **{{ states('sensor.ma_control_hosts') }}**
- `sensor.now_playing_entity`: **{{ states('sensor.now_playing_entity') }}**
- `sensor.now_playing_title`: **{{ states('sensor.now_playing_title') }}**
- `sensor.now_playing_state`: **{{ states('sensor.now_playing_state') }}**

### Missing entities (must fix)
{% if (ns.missing | length) == 0 %}
- none
{% else %}
{% for eid in ns.missing %}
- {{ eid }}
{% endfor %}
{% endif %}

### Runtime entities with unknown/unavailable (investigate)
{% if (ns.unavailable | length) == 0 %}
- none
{% else %}
{% for eid in ns.unavailable %}
- {{ eid }}
{% endfor %}
{% endif %}

### Detailed check table
| Tier | Entity | Exists | State |
|---|---|---:|---|
{% for row in ns.rows %}
| {{ row.tier }} | `{{ row.entity }}` | {{ row.exists }} | {{ row.state }} |
{% endfor %}

### Notes
- `rest_command.*` does not expose a normal state entity, so this template verifies package health via sentinels (`sensor.ma_api_url`, scripts).
- Automation health is checked by `automation.attributes.id` (stable), not alias/entity slug names (which can vary).
- If helpers/scripts are missing here, package loading is still broken.
```

## Maintenance Notes

- Add new templates below this section as diagnostics evolve.
- Keep templates copy-paste ready (no extra markdown inside code blocks).
- Update version metadata in this file each time you add/change templates.

## 1A) Iteration Workbench — Combined Checks (1→4 in One Paste)

```jinja
{# =========================
  Spectra LS Iteration Workbench (Combined 1→4)
  Purpose: single paste for iterative check/code/check cycles
  Includes: Health + Path + Readiness + Effect
  ========================= #}

{# Optional probe inputs for effect section #}
{% set probe_entity = 'number.control_board_v2_arylic_volume_set' %}
{% set probe_action_value = none %}

{# Common sentinels #}
{% set invalid = ['','none','unknown','unavailable'] %}

{# -------------------------
   A) Core health subset
   ------------------------- #}
{% set health_entities = [
  'input_select.ma_active_target',
  'sensor.spectra_ls_rooms_raw',
  'sensor.ma_control_host',
  'sensor.ma_control_hosts',
  'sensor.ma_active_target_by_host',
  'sensor.ma_active_meta_entity',
  'sensor.now_playing_entity',
  'sensor.now_playing_state',
  'sensor.now_playing_title',
  'sensor.ma_api_url',
  'script.ma_update_target_options',
  'script.ma_auto_select',
  'script.ma_set_volume',
  'script.ma_set_balance'
] %}

{% set h = namespace(missing=[], unavailable=[]) %}
{% for eid in health_entities %}
  {% if states[eid] is none %}
    {% set h.missing = h.missing + [eid] %}
  {% else %}
    {% set st = states(eid) %}
    {% if st in ['unknown','unavailable'] %}
      {% set h.unavailable = h.unavailable + [eid] %}
    {% endif %}
  {% endif %}
{% endfor %}
{% set health_ok = (h.missing | length) == 0 and (h.unavailable | length) == 0 %}

{# -------------------------
   B) Path probe subset
   ------------------------- #}
{% set target = states('input_select.ma_active_target') %}
{% set target_options = state_attr('input_select.ma_active_target','options') or [] %}
{% set target_ok = target not in invalid and target in target_options and states[target] is not none %}

{% set host = states('sensor.ma_control_host') %}
{% set host_ok = host not in invalid %}

{% set by_host = states('sensor.ma_active_target_by_host') %}
{% set by_host_ok = by_host not in invalid and states[by_host] is not none %}

{% set meta = states('sensor.ma_active_meta_entity') %}
{% set meta_ok = meta not in invalid and states[meta] is not none %}
{% set meta_state = states(meta) if meta_ok else 'missing' %}
{% set meta_title = (state_attr(meta,'media_title') if meta_ok else '') | default('', true) %}
{% set meta_artist = (state_attr(meta,'media_artist') if meta_ok else '') | default('', true) %}
{% set meta_source = (state_attr(meta,'source') if meta_ok else '') | default('', true) %}

{% set np = states('sensor.now_playing_entity') %}
{% set np_ok = np not in invalid and states[np] is not none %}
{% set np_state = states('sensor.now_playing_state') %}
{% set np_title = states('sensor.now_playing_title') %}

{% set room_attr = state_attr('sensor.spectra_ls_rooms_json','rooms_json') %}
{% set rooms = [] %}
{% if room_attr is sequence and room_attr is not string and room_attr is not mapping %}
  {% set rooms = room_attr %}
{% elif room_attr is mapping %}
  {% set mapped = (room_attr.rooms if room_attr.rooms is defined else (room_attr.result if room_attr.result is defined else [])) %}
  {% if mapped is sequence and mapped is not string and mapped is not mapping %}
    {% set rooms = mapped %}
  {% endif %}
{% elif room_attr is string %}
  {% set raw_trim = room_attr | trim %}
  {% set raw_trim_l = raw_trim | lower %}
  {% if raw_trim_l not in invalid and (raw_trim.startswith('[') or raw_trim.startswith('{')) %}
    {% set parsed = raw_trim | from_json %}
    {% if parsed is sequence and parsed is not string and parsed is not mapping %}
      {% set rooms = parsed %}
    {% elif parsed is mapping %}
      {% set mapped = (parsed.rooms if parsed.rooms is defined else (parsed.result if parsed.result is defined else [])) %}
      {% if mapped is sequence and mapped is not string and mapped is not mapping %}
        {% set rooms = mapped %}
      {% endif %}
    {% endif %}
  {% endif %}
{% endif %}

{% set p = namespace(room_match=false, host_match=false, mapped_host='', mapped_meta='') %}
{% for r in rooms %}
  {% set ent = (r.entity if r is not none and r.entity is defined else '') %}
  {% if ent == target %}
    {% set p.room_match = true %}
    {% set p.mapped_host = (r.tcp_host if r is not none and r.tcp_host is defined else '') %}
    {% set p.mapped_meta = (r.meta if r is not none and r.meta is defined else '') %}
    {% if p.mapped_host == host and host not in invalid %}
      {% set p.host_match = true %}
    {% endif %}
  {% endif %}
{% endfor %}

{% set path_score = 0 %}
{% if target_ok %}{% set path_score = path_score + 1 %}{% endif %}
{% if host_ok %}{% set path_score = path_score + 1 %}{% endif %}
{% if by_host_ok %}{% set path_score = path_score + 1 %}{% endif %}
{% if meta_ok %}{% set path_score = path_score + 1 %}{% endif %}
{% if np_ok %}{% set path_score = path_score + 1 %}{% endif %}
{% if p.room_match %}{% set path_score = path_score + 1 %}{% endif %}
{% if p.host_match %}{% set path_score = path_score + 1 %}{% endif %}

{% set path_result = 'PASS' %}
{% if path_score < 5 %}
  {% set path_result = 'FAIL' %}
{% elif path_score < 7 %}
  {% set path_result = 'WARN' %}
{% endif %}

{# -------------------------
   C) Command readiness
   ------------------------- #}
{% set api_url = states('sensor.ma_api_url') %}
{% set api_ok = api_url not in invalid and '/api' in api_url %}
{% set control_ambiguous = is_state('binary_sensor.ma_control_ambiguous','on') %}
{% set override_on = is_state('input_boolean.ma_override_active','on') %}
{% set readiness_number_candidates = [
  'number.control_board_v2_arylic_volume_set',
  'number.control_board_v2_eq_low',
  'number.control_board_v2_eq_mid',
  'number.control_board_v2_eq_high',
  'number.control_board_audio_volume'
] %}

{% set c = namespace(writable=[], available=[], unavailable=[], eq=[], eq_ready=[], volume=[], volume_ready=[]) %}
{% for eid in readiness_number_candidates %}
  {% if states[eid] is not none %}
  {% set name_l = (state_attr(eid,'friendly_name') or eid) | lower %}
  {% set writable = state_attr(eid,'readonly') != true %}
  {% set st = states(eid) %}
  {% set audioish = (
      ('arylic' in eid) or ('eq' in eid) or ('volume' in eid) or
      ('arylic' in name_l) or ('equalizer' in name_l) or ('eq' in name_l) or ('volume' in name_l)
    ) %}
  {% if writable and audioish %}
    {% set c.writable = c.writable + [eid] %}
    {% if st in ['unknown','unavailable'] %}
      {% set c.unavailable = c.unavailable + [eid] %}
    {% else %}
      {% set c.available = c.available + [eid] %}
    {% endif %}
    {% if 'eq' in eid or 'equalizer' in name_l %}
      {% set c.eq = c.eq + [eid] %}
      {% if st not in ['unknown','unavailable'] %}
        {% set c.eq_ready = c.eq_ready + [eid] %}
      {% endif %}
    {% endif %}
    {% if 'volume' in eid or 'volume' in name_l %}
      {% set c.volume = c.volume + [eid] %}
      {% if st not in ['unknown','unavailable'] %}
        {% set c.volume_ready = c.volume_ready + [eid] %}
      {% endif %}
    {% endif %}
  {% endif %}
  {% endif %}
{% endfor %}

{% set readiness_score = 0 %}
{% if host_ok %}{% set readiness_score = readiness_score + 1 %}{% endif %}
{% if api_ok %}{% set readiness_score = readiness_score + 1 %}{% endif %}
{% if target_ok %}{% set readiness_score = readiness_score + 1 %}{% endif %}
{% if (c.available | length) > 0 %}{% set readiness_score = readiness_score + 1 %}{% endif %}
{% if (c.volume_ready | length) > 0 or (c.eq_ready | length) > 0 %}{% set readiness_score = readiness_score + 1 %}{% endif %}

{% set readiness_result = 'PASS' %}
{% if readiness_score < 3 %}
  {% set readiness_result = 'FAIL' %}
{% elif readiness_score < 5 %}
  {% set readiness_result = 'WARN' %}
{% endif %}

{% set vol_probe = (c.volume_ready[0] if (c.volume_ready | length) > 0 else (c.volume[0] if (c.volume | length) > 0 else (c.available[0] if (c.available | length) > 0 else (c.writable[0] if (c.writable | length) > 0 else '')))) %}
{% set eq_probe = (c.eq_ready[0] if (c.eq_ready | length) > 0 else (c.eq[0] if (c.eq | length) > 0 else '')) %}

{# -------------------------
   D) Effect snapshot
   ------------------------- #}
{% set probe_exists = states[probe_entity] is not none %}
{% set probe_state = states(probe_entity) if probe_exists else 'missing' %}
{% set probe_numeric = (probe_state | float(none)) if probe_state not in ['missing','unknown','unavailable','none',''] else none %}
{% set p_min = state_attr(probe_entity,'min') if probe_exists else none %}
{% set p_max = state_attr(probe_entity,'max') if probe_exists else none %}
{% set p_step = state_attr(probe_entity,'step') if probe_exists else none %}
{% set suggested_action_value = (p_min | float(0)) if p_min is not none else (probe_numeric if probe_numeric is not none else 0) %}
{% set expected_effect_value = (probe_action_value | float(suggested_action_value)) if probe_action_value is not none else suggested_action_value %}

{% set expected_in_range = true %}
{% if p_min is not none and expected_effect_value < (p_min | float(expected_effect_value)) %}
  {% set expected_in_range = false %}
{% endif %}
{% if p_max is not none and expected_effect_value > (p_max | float(expected_effect_value)) %}
  {% set expected_in_range = false %}
{% endif %}

{% set d = ((probe_numeric - expected_effect_value) | abs) if probe_numeric is not none else none %}
{% set tol = (p_step | float(0.5)) if p_step is not none else 0.5 %}
{% set effect_ok = probe_exists and probe_state not in ['unknown','unavailable'] and expected_in_range and (d is not none and d <= tol) %}

{% set effect_result = 'PASS' %}
{% if not probe_exists or probe_state in ['unknown','unavailable'] %}
  {% set effect_result = 'FAIL' %}
{% elif not expected_in_range or not effect_ok %}
  {% set effect_result = 'WARN' %}
{% endif %}

{# -------------------------
   Overall
   ------------------------- #}
{% set pass_count = (1 if health_ok else 0) + (1 if path_result == 'PASS' else 0) + (1 if readiness_result == 'PASS' else 0) + (1 if effect_result == 'PASS' else 0) %}
{% set overall = 'PASS' if pass_count == 4 else ('WARN' if pass_count >= 3 else 'FAIL') %}

### Spectra LS Iteration Workbench (1→4)
- Overall: **{{ overall }}**
- Timestamp: **{{ now() }}**
- PASS blocks: **{{ pass_count }}/4**

| Block | Status | Key metric |
|---|---|---|
| 1) Health | **{{ 'PASS' if health_ok else 'FAIL' }}** | missing={{ h.missing | length }}, unavailable={{ h.unavailable | length }} |
| 2) Path | **{{ path_result }}** | path_score={{ path_score }}/7 |
| 3) Readiness | **{{ readiness_result }}** | readiness_score={{ readiness_score }}/5 |
| 4) Effect | **{{ effect_result }}** | delta={{ (d | round(4)) if d is not none else 'n/a' }}, tol={{ tol }} |

### 1) Health details
- Missing count: **{{ h.missing | length }}**
- Unavailable count: **{{ h.unavailable | length }}**
{% if (h.missing | length) > 0 %}
Missing entities:
{% for eid in h.missing %}
- `{{ eid }}`
{% endfor %}
{% endif %}
{% if (h.unavailable | length) > 0 %}
Unavailable entities:
{% for eid in h.unavailable %}
- `{{ eid }}`
{% endfor %}
{% endif %}

### 2) Path details
- Target: **{{ target }}** (ok={{ target_ok }})
- Host: **{{ host }}** (ok={{ host_ok }})
- By-host: **{{ by_host }}** (ok={{ by_host_ok }})
- Meta: **{{ meta }}** (ok={{ meta_ok }})
- Now playing entity: **{{ np }}** (ok={{ np_ok }})
- Room map match: **{{ p.room_match }}**
- Host map match: **{{ p.host_match }}**
- Mapped host/meta: **{{ p.mapped_host if p.mapped_host not in ['',none] else 'n/a' }}** / **{{ p.mapped_meta if p.mapped_meta not in ['',none] else 'n/a' }}**
- Meta state/title/artist/source: **{{ meta_state }}** / **{{ meta_title }}** / **{{ meta_artist }}** / **{{ meta_source }}**
- NP state/title: **{{ np_state }}** / **{{ np_title }}**

### 3) Readiness details
- `sensor.ma_api_url`: **{{ api_url }}** (ok={{ api_ok }})
- `binary_sensor.ma_control_ambiguous`: **{{ control_ambiguous }}**
- `input_boolean.ma_override_active`: **{{ override_on }}**
- Writable audio entities: **{{ c.writable | length }}**
- Available writable entities: **{{ c.available | length }}**
- Volume-ready / EQ-ready: **{{ c.volume_ready | length }}** / **{{ c.eq_ready | length }}**

{% if vol_probe != '' %}
- Volume probe candidate:
  - Service: `number.set_value`
  - Data: `{"entity_id":"{{ vol_probe }}","value":{{ state_attr(vol_probe,'min') if state_attr(vol_probe,'min') is not none else 0 }}}`
{% else %}
- Volume probe candidate: **none found**
{% endif %}

{% if eq_probe != '' %}
- EQ probe candidate:
  - Service: `number.set_value`
  - Data: `{"entity_id":"{{ eq_probe }}","value":{{ state_attr(eq_probe,'min') if state_attr(eq_probe,'min') is not none else -10 }}}`
{% else %}
- EQ probe candidate: **none found**
{% endif %}

### 4) Effect details
- Probe: **{{ probe_entity }}** (exists={{ probe_exists }})
- Probe state/value: **{{ probe_state }}** / **{{ probe_numeric if probe_numeric is not none else 'n/a' }}**
- Probe min/max/step: **{{ p_min }} / {{ p_max }} / {{ p_step }}**
- Action value used for expectation: **{{ expected_effect_value }}**
- Expected in range: **{{ expected_in_range }}**
- Match expected (±step): **{{ effect_ok }}**

### Next action guidance
{% if overall == 'PASS' %}
- All core iteration checks are healthy. Proceed with next code slice.
{% elif not health_ok %}
- Fix health contract breaks first (missing/unavailable entities).
{% elif path_result != 'PASS' %}
- Resolve routing path mismatch before command tuning.
{% elif readiness_result != 'PASS' %}
- Restore writable command surfaces and host/API readiness.
{% else %}
- Re-run command effect with fresh before/after action and aligned `probe_action_value`.
{% endif %}
```

## 2) Audio Control Path Probe (Target → Host → Meta → Now Playing)

```jinja
{# =========================
  Spectra LS Audio Control Path Probe
  Paste into HA Developer Tools -> Template
  ========================= #}

{% set target = states('input_select.ma_active_target') %}
{% set target_options = state_attr('input_select.ma_active_target','options') or [] %}
{% set target_valid = target not in ['','none','unknown','unavailable'] and target in target_options and states[target] is not none %}

{% set control_host = states('sensor.ma_control_host') %}
{% set control_hosts = states('sensor.ma_control_hosts') %}
{% set host_valid = control_host not in ['','none','unknown','unavailable'] %}

{% set by_host = states('sensor.ma_active_target_by_host') %}
{% set by_host_valid = by_host not in ['','none','unknown','unavailable'] and states[by_host] is not none %}

{% set meta = states('sensor.ma_active_meta_entity') %}
{% set meta_valid = meta not in ['','none','unknown','unavailable'] and states[meta] is not none %}
{% set meta_state = states(meta) if meta_valid else 'missing' %}
{% set meta_title = (state_attr(meta,'media_title') if meta_valid else '') | default('', true) %}
{% set meta_artist = (state_attr(meta,'media_artist') if meta_valid else '') | default('', true) %}
{% set meta_source = (state_attr(meta,'source') if meta_valid else '') | default('', true) %}

{% set np = states('sensor.now_playing_entity') %}
{% set np_valid = np not in ['','none','unknown','unavailable'] and states[np] is not none %}
{% set np_state = states('sensor.now_playing_state') %}
{% set np_title = states('sensor.now_playing_title') %}

{% set room_attr = state_attr('sensor.spectra_ls_rooms_json','rooms_json') %}
{% set rooms = [] %}
{% if room_attr is sequence and room_attr is not string and room_attr is not mapping %}
  {% set rooms = room_attr %}
{% elif room_attr is mapping %}
  {% set mapped = (room_attr.rooms if room_attr.rooms is defined else (room_attr.result if room_attr.result is defined else [])) %}
  {% if mapped is sequence and mapped is not string and mapped is not mapping %}
    {% set rooms = mapped %}
  {% endif %}
{% elif room_attr is string %}
  {% set raw_trim = room_attr | trim %}
  {% set raw_trim_l = raw_trim | lower %}
  {% if raw_trim_l not in ['','none','unknown','unavailable'] and (raw_trim.startswith('[') or raw_trim.startswith('{')) %}
    {% set parsed = raw_trim | from_json %}
    {% if parsed is sequence and parsed is not string and parsed is not mapping %}
      {% set rooms = parsed %}
    {% elif parsed is mapping %}
      {% set mapped = (parsed.rooms if parsed.rooms is defined else (parsed.result if parsed.result is defined else [])) %}
      {% if mapped is sequence and mapped is not string and mapped is not mapping %}
        {% set rooms = mapped %}
      {% endif %}
    {% endif %}
  {% endif %}
{% endif %}

{% set ns = namespace(room_match=false, host_match=false, mapped_host='', mapped_meta='') %}
{% for r in rooms %}
  {% set ent = (r.entity if r is not none and r.entity is defined else '') %}
  {% if ent == target %}
    {% set ns.room_match = true %}
    {% set ns.mapped_host = (r.tcp_host if r is not none and r.tcp_host is defined else '') %}
    {% set ns.mapped_meta = (r.meta if r is not none and r.meta is defined else '') %}
    {% if ns.mapped_host == control_host and control_host not in ['','none','unknown','unavailable'] %}
      {% set ns.host_match = true %}
    {% endif %}
  {% endif %}
{% endfor %}

{% set path_score = 0 %}
{% if target_valid %}{% set path_score = path_score + 1 %}{% endif %}
{% if host_valid %}{% set path_score = path_score + 1 %}{% endif %}
{% if by_host_valid %}{% set path_score = path_score + 1 %}{% endif %}
{% if meta_valid %}{% set path_score = path_score + 1 %}{% endif %}
{% if np_valid %}{% set path_score = path_score + 1 %}{% endif %}
{% if ns.room_match %}{% set path_score = path_score + 1 %}{% endif %}
{% if ns.host_match %}{% set path_score = path_score + 1 %}{% endif %}

{% set verdict = 'PASS' %}
{% if path_score < 5 %}
  {% set verdict = 'FAIL' %}
{% elif path_score < 7 %}
  {% set verdict = 'WARN' %}
{% endif %}

### Audio Control Path Probe
- Result: **{{ verdict }}**
- Timestamp: **{{ now() }}**
- Path score: **{{ path_score }}/7**

### Target selection
- Target: **{{ target }}**
- Target valid and selectable: **{{ target_valid }}**
- Target options count: **{{ target_options | length }}**

### Host routing
- `sensor.ma_control_host`: **{{ control_host }}**
- `sensor.ma_control_hosts`: **{{ control_hosts }}**
- Host valid: **{{ host_valid }}**
- `sensor.ma_active_target_by_host`: **{{ by_host }}**
- Host→target entity valid: **{{ by_host_valid }}**

### Room map correlation
- Rooms map found target: **{{ ns.room_match }}**
- Mapped host for target: **{{ ns.mapped_host if ns.mapped_host not in ['',none] else 'n/a' }}**
- Control host matches room map: **{{ ns.host_match }}**
- Mapped meta for target: **{{ ns.mapped_meta if ns.mapped_meta not in ['',none] else 'n/a' }}**

### Meta + now playing
- `sensor.ma_active_meta_entity`: **{{ meta }}**
- Meta entity valid: **{{ meta_valid }}**
- Meta state: **{{ meta_state }}**
- Meta title: **{{ meta_title }}**
- Meta artist: **{{ meta_artist }}**
- Meta source: **{{ meta_source }}**
- `sensor.now_playing_entity`: **{{ np }}**
- Now playing entity valid: **{{ np_valid }}**
- `sensor.now_playing_state`: **{{ np_state }}**
- `sensor.now_playing_title`: **{{ np_title }}**

### Suggested next action
{% if not target_valid %}
- Target layer failing: run `script.ma_update_target_options`, then re-check options and selected target.
{% elif not host_valid %}
- Host layer failing: inspect `sensor.ma_control_hosts` + `sensor.spectra_ls_rooms_raw` mapping and room `tcp_host` values.
{% elif not ns.room_match %}
- Room map mismatch: selected target is not present in `sensor.spectra_ls_rooms_raw` rooms list.
{% elif not ns.host_match %}
- Host mismatch: target maps to a different `tcp_host` than `sensor.ma_control_host`.
{% elif not meta_valid %}
- Meta layer failing: inspect `sensor.ma_active_meta_entity` logic and confidence/stale thresholds.
{% elif not np_valid %}
- Now-playing layer failing: inspect `sensor.now_playing_entity` resolver path and source entity states.
{% else %}
- Path looks healthy; if control still fails, next probe should test command execution (volume/EQ service calls + TCP ack).
{% endif %}
```

## 3) Command Execution Readiness Probe (Writable Controls + Host Path)

```jinja
{# =========================
  Spectra LS Command Execution Readiness Probe
  Paste into HA Developer Tools -> Template
  ========================= #}

{% set host = states('sensor.ma_control_host') %}
{% set hosts = states('sensor.ma_control_hosts') %}
{% set host_ok = host not in ['','none','unknown','unavailable'] %}

{% set api_url = states('sensor.ma_api_url') %}
{% set api_ok = api_url not in ['','none','unknown','unavailable'] and '/api' in api_url %}

{% set target = states('input_select.ma_active_target') %}
{% set target_ok = target not in ['','none','unknown','unavailable'] and states[target] is not none %}

{% set control_ambiguous = is_state('binary_sensor.ma_control_ambiguous','on') %}
{% set override_on = is_state('input_boolean.ma_override_active','on') %}

{% set readiness_number_candidates = [
  'number.control_board_v2_arylic_volume_set',
  'number.control_board_v2_eq_low',
  'number.control_board_v2_eq_mid',
  'number.control_board_v2_eq_high',
  'number.control_board_audio_volume'
] %}

{% set ns = namespace(writable=[], available=[], unavailable=[], eq=[], eq_ready=[], volume=[], volume_ready=[], diagnostics=[]) %}

{# Find writable number entities likely tied to audio control #}
{% for eid in readiness_number_candidates %}
  {% if states[eid] is not none %}
  {% set name_l = (state_attr(eid,'friendly_name') or eid) | lower %}
  {% set writable = state_attr(eid,'readonly') != true %}
  {% set st = states(eid) %}
  {% set audioish = (
      ('arylic' in eid) or ('eq' in eid) or ('volume' in eid) or
      ('arylic' in name_l) or ('equalizer' in name_l) or ('eq' in name_l) or ('volume' in name_l)
    ) %}
  {% if writable and audioish %}
    {% set ns.writable = ns.writable + [eid] %}
    {% if st in ['unknown','unavailable'] %}
      {% set ns.unavailable = ns.unavailable + [eid] %}
    {% else %}
      {% set ns.available = ns.available + [eid] %}
    {% endif %}
    {% if 'eq' in eid or 'equalizer' in name_l %}
      {% set ns.eq = ns.eq + [eid] %}
      {% if st not in ['unknown','unavailable'] %}
        {% set ns.eq_ready = ns.eq_ready + [eid] %}
      {% endif %}
    {% endif %}
    {% if 'volume' in eid or 'volume' in name_l %}
      {% set ns.volume = ns.volume + [eid] %}
      {% if st not in ['unknown','unavailable'] %}
        {% set ns.volume_ready = ns.volume_ready + [eid] %}
      {% endif %}
    {% endif %}
  {% endif %}
  {% endif %}
{% endfor %}

{% set lane_score = 0 %}
{% if host_ok %}{% set lane_score = lane_score + 1 %}{% endif %}
{% if api_ok %}{% set lane_score = lane_score + 1 %}{% endif %}
{% if target_ok %}{% set lane_score = lane_score + 1 %}{% endif %}
{% if (ns.available | length) > 0 %}{% set lane_score = lane_score + 1 %}{% endif %}
{% if (ns.volume_ready | length) > 0 or (ns.eq_ready | length) > 0 %}{% set lane_score = lane_score + 1 %}{% endif %}

{% set verdict = 'PASS' %}
{% if lane_score < 3 %}
  {% set verdict = 'FAIL' %}
{% elif lane_score < 5 %}
  {% set verdict = 'WARN' %}
{% endif %}

### Command Execution Readiness
- Result: **{{ verdict }}**
- Timestamp: **{{ now() }}**
- Readiness score: **{{ lane_score }}/5**

### Transport + target prerequisites
- `sensor.ma_control_host`: **{{ host }}**
- `sensor.ma_control_hosts`: **{{ hosts }}**
- Host ready: **{{ host_ok }}**
- `sensor.ma_api_url`: **{{ api_url }}**
- API URL looks valid: **{{ api_ok }}**
- Active target: **{{ target }}**
- Active target valid: **{{ target_ok }}**
- `binary_sensor.ma_control_ambiguous`: **{{ control_ambiguous }}**
- `input_boolean.ma_override_active`: **{{ override_on }}**

### Writable command surfaces detected
- Total writable audio-ish number entities: **{{ ns.writable | length }}**
- Available writable entities: **{{ ns.available | length }}**
- Unavailable writable entities: **{{ ns.unavailable | length }}**
- Volume-like entities: **{{ ns.volume | length }}**
- EQ-like entities: **{{ ns.eq | length }}**

{% if (ns.unavailable | length) > 0 %}
Unavailable (informational):
{% for eid in ns.unavailable %}
- `{{ eid }}` (state={{ states(eid) }})
{% endfor %}
{% endif %}

{% if (ns.writable | length) == 0 %}
- none detected
{% else %}
{% for eid in ns.writable %}
- `{{ eid }}` (state={{ states(eid) }}, min={{ state_attr(eid,'min') }}, max={{ state_attr(eid,'max') }}, step={{ state_attr(eid,'step') }})
{% endfor %}
{% endif %}

### Manual service-call payloads (copy into Dev Tools → Actions)
{% set vol_probe = (ns.volume_ready[0] if (ns.volume_ready | length) > 0 else (ns.volume[0] if (ns.volume | length) > 0 else (ns.available[0] if (ns.available | length) > 0 else (ns.writable[0] if (ns.writable | length) > 0 else '')))) %}
{% set eq_probe = (ns.eq_ready[0] if (ns.eq_ready | length) > 0 else (ns.eq[0] if (ns.eq | length) > 0 else '')) %}

{% if vol_probe != '' %}
- Volume probe candidate:
  - Service: `number.set_value`
  - Data: `{"entity_id":"{{ vol_probe }}","value":{{ state_attr(vol_probe,'min') if state_attr(vol_probe,'min') is not none else 0 }}}`
{% else %}
- Volume probe candidate: **none found**
{% endif %}

{% if eq_probe != '' %}
- EQ probe candidate:
  - Service: `number.set_value`
  - Data: `{"entity_id":"{{ eq_probe }}","value":{{ state_attr(eq_probe,'min') if state_attr(eq_probe,'min') is not none else -10 }}}`
{% else %}
- EQ probe candidate: **none found**
{% endif %}

### Interpretation
{% if not host_ok %}
- Transport host is not ready. Fix host mapping first (`sensor.ma_control_host`).
{% elif (ns.available | length) == 0 %}
- No writable audio control entities discovered. Check ESPHome entity exposure for volume/EQ number controls.
{% elif control_ambiguous and not override_on %}
- Control path may be blocked by ambiguity. Choose/lock target, then re-run probe.
{% elif (ns.unavailable | length) > 0 %}
- Control lane is usable, but some writable entities are currently unavailable. Prefer probes from available entities above; investigate unavailable entries if they should be active.
{% else %}
- Readiness is good. If commands still appear ineffective, compare before/after value changes and check ESPHome logs for TCP send attempts.
{% endif %}
```

## 4) Command Effect Verification (Before/After Snapshot)

```jinja
{# =========================
  Spectra LS Command Effect Verification
  Paste into HA Developer Tools -> Template
  Workflow:
    1) Run this template (before snapshot)
    2) Run number.set_value action
    3) Run this template again (after snapshot)
  ========================= #}

{# Optional: change these two lines per test #}
{% set probe_entity = 'number.control_board_v2_arylic_volume_set' %}
{% set probe_action_value = none %}

{% set target = states('input_select.ma_active_target') %}
{% set host = states('sensor.ma_control_host') %}
{% set np = states('sensor.now_playing_entity') %}

{% set probe_exists = states[probe_entity] is not none %}
{% set probe_state_raw = states(probe_entity) if probe_exists else 'missing' %}
{% set probe_numeric = (probe_state_raw | float(none)) if probe_state_raw not in ['missing','unknown','unavailable','none',''] else none %}
{% set probe_has_numeric = probe_numeric is not none %}
{% set probe_min = state_attr(probe_entity,'min') if probe_exists else none %}
{% set probe_max = state_attr(probe_entity,'max') if probe_exists else none %}
{% set probe_step = state_attr(probe_entity,'step') if probe_exists else none %}
{% set probe_lc = as_timestamp(states[probe_entity].last_changed) if probe_exists else none %}
{% set probe_lu = as_timestamp(states[probe_entity].last_updated) if probe_exists else none %}
{% set now_ts = as_timestamp(now()) %}
{% set probe_age_s = (now_ts - probe_lu) if probe_lu is not none else none %}
{% set suggested_action_value = (probe_min | float(0)) if probe_min is not none else (probe_numeric if probe_numeric is not none else 0) %}
{% set expected_effect_value = (probe_action_value | float(suggested_action_value)) if probe_action_value is not none else suggested_action_value %}

{% set expected_in_range = true %}
{% if probe_min is not none and expected_effect_value < (probe_min | float(expected_effect_value)) %}
  {% set expected_in_range = false %}
{% endif %}
{% if probe_max is not none and expected_effect_value > (probe_max | float(expected_effect_value)) %}
  {% set expected_in_range = false %}
{% endif %}

{% set delta = (probe_numeric - expected_effect_value) | abs if probe_has_numeric else none %}
{% set step_tol = (probe_step | float(0.5)) if probe_step is not none else 0.5 %}
{% set matches_expected = (delta is not none and delta <= step_tol) %}

{% set target_valid = target not in ['','none','unknown','unavailable'] and states[target] is not none %}
{% set target_state = states(target) if target_valid else 'missing' %}
{% set target_volume = (state_attr(target,'volume_level') if target_valid else none) %}
{% set target_src = (state_attr(target,'source') if target_valid else '') | default('', true) %}
{% set target_app = (state_attr(target,'app_name') if target_valid else '') | default('', true) %}

{% set np_valid = np not in ['','none','unknown','unavailable'] and states[np] is not none %}
{% set np_state = states(np) if np_valid else 'missing' %}
{% set np_title = states('sensor.now_playing_title') %}

{% set verdict = 'PASS' %}
{% if not probe_exists or probe_state_raw in ['unknown','unavailable'] %}
  {% set verdict = 'FAIL' %}
{% elif not expected_in_range %}
  {% set verdict = 'WARN' %}
{% elif not matches_expected %}
  {% set verdict = 'WARN' %}
{% endif %}

### Command Effect Verification
- Result: **{{ verdict }}**
- Timestamp: **{{ now() }}**

### Probe setup
- Probe entity: **{{ probe_entity }}**
- Probe exists: **{{ probe_exists }}**
- Probe state: **{{ probe_state_raw }}**
- Probe numeric value: **{{ probe_numeric if probe_numeric is not none else 'n/a' }}**
- Probe min/max/step: **{{ probe_min }} / {{ probe_max }} / {{ probe_step }}**
- Probe last_changed: **{{ states[probe_entity].last_changed if probe_exists else 'n/a' }}**
- Probe last_updated: **{{ states[probe_entity].last_updated if probe_exists else 'n/a' }}**
- Probe update age (s): **{{ (probe_age_s | round(2)) if probe_age_s is not none else 'n/a' }}**

### Expectation check
- Action value used for expectation: **{{ expected_effect_value }}**
- Expected in allowed range: **{{ expected_in_range }}**
- Absolute delta from expected: **{{ (delta | round(4)) if delta is not none else 'n/a' }}**
- Match expected (±step): **{{ matches_expected }}**

### Runtime context
- `input_select.ma_active_target`: **{{ target }}**
- Target valid: **{{ target_valid }}**
- Target state: **{{ target_state }}**
- Target volume_level attr: **{{ target_volume if target_volume is not none else 'n/a' }}**
- Target source/app: **{{ target_src }} / {{ target_app }}**
- `sensor.ma_control_host`: **{{ host }}**
- `sensor.now_playing_entity`: **{{ np }}**
- Now playing valid/state/title: **{{ np_valid }} / {{ np_state }} / {{ np_title }}**

### Quick use
- Before snapshot: run this template and note probe value/time.
- Send action: `number.set_value` on `{{ probe_entity }}`.
- After snapshot: run template again; confirm probe value and `last_updated` moved.

### Interpretation
{% if not probe_exists %}
- Probe entity does not exist. Pick a valid entity from Template #3 available list.
{% elif probe_state_raw in ['unknown','unavailable'] %}
- Probe entity is unavailable; command effect cannot be verified from this entity.
{% elif not expected_in_range %}
- Expected value is outside entity limits; adjust to min/max range and retry.
{% elif matches_expected %}
- Command effect appears applied at entity layer.
{% else %}
- Command may not have applied (or still in flight). Re-run after 1–2s and verify ESPHome logs for send/ack path.
{% endif %}
```

## 5) One-Screen Smoke Test (Fast Go/No-Go)

```jinja
{# =========================
  Spectra LS One-Screen Smoke Test
  Purpose: fast summary from key layers (config, routing, readiness, effect)
  Paste into HA Developer Tools -> Template
  ========================= #}

{# Optional probe inputs for effect layer #}
{% set probe_entity = 'number.control_board_v2_arylic_volume_set' %}
{% set probe_action_value = none %}

{# Layer A: Core config/runtime integrity #}
{% set core_entities = [
  'input_select.ma_active_target',
  'sensor.spectra_ls_rooms_raw',
  'sensor.ma_control_host',
  'sensor.ma_control_hosts',
  'sensor.ma_active_target_by_host',
  'sensor.ma_active_meta_entity',
  'sensor.now_playing_entity',
  'sensor.now_playing_state',
  'sensor.now_playing_title',
  'sensor.ma_api_url'
] %}

{% set ns = namespace(missing=[], unavailable=[]) %}
{% for eid in core_entities %}
  {% if states[eid] is none %}
    {% set ns.missing = ns.missing + [eid] %}
  {% else %}
    {% set st = states(eid) %}
    {% if st in ['unknown','unavailable'] %}
      {% set ns.unavailable = ns.unavailable + [eid] %}
    {% endif %}
  {% endif %}
{% endfor %}
{% set layer_a_ok = (ns.missing | length) == 0 and (ns.unavailable | length) == 0 %}

{# Layer B: Routing path integrity #}
{% set target = states('input_select.ma_active_target') %}
{% set target_opts = state_attr('input_select.ma_active_target','options') or [] %}
{% set target_ok = target not in ['','none','unknown','unavailable'] and target in target_opts and states[target] is not none %}
{% set host = states('sensor.ma_control_host') %}
{% set host_ok = host not in ['','none','unknown','unavailable'] %}
{% set by_host = states('sensor.ma_active_target_by_host') %}
{% set by_host_ok = by_host not in ['','none','unknown','unavailable'] and states[by_host] is not none %}
{% set meta = states('sensor.ma_active_meta_entity') %}
{% set meta_ok = meta not in ['','none','unknown','unavailable'] and states[meta] is not none %}
{% set np = states('sensor.now_playing_entity') %}
{% set np_ok = np not in ['','none','unknown','unavailable'] and states[np] is not none %}
{% set layer_b_ok = target_ok and host_ok and by_host_ok and meta_ok and np_ok %}

{# Layer C: Command readiness (writable surface available) #}
{% set readiness_number_candidates = [
  'number.control_board_v2_arylic_volume_set',
  'number.control_board_v2_eq_low',
  'number.control_board_v2_eq_mid',
  'number.control_board_v2_eq_high',
  'number.control_board_audio_volume'
] %}
{% set c = namespace(writable=[], available=[]) %}
{% for eid in readiness_number_candidates %}
  {% if states[eid] is not none %}
  {% set name_l = (state_attr(eid,'friendly_name') or eid) | lower %}
  {% set writable = state_attr(eid,'readonly') != true %}
  {% set st = states(eid) %}
  {% set audioish = ('arylic' in eid) or ('eq' in eid) or ('volume' in eid) or ('arylic' in name_l) or ('equalizer' in name_l) or ('volume' in name_l) %}
  {% if writable and audioish %}
    {% set c.writable = c.writable + [eid] %}
    {% if st not in ['unknown','unavailable'] %}
      {% set c.available = c.available + [eid] %}
    {% endif %}
  {% endif %}
  {% endif %}
{% endfor %}
{% set layer_c_ok = host_ok and (c.available | length) > 0 %}

{# Layer D: Effect snapshot check against expected value #}
{% set probe_exists = states[probe_entity] is not none %}
{% set probe_state = states(probe_entity) if probe_exists else 'missing' %}
{% set probe_numeric = (probe_state | float(none)) if probe_state not in ['missing','unknown','unavailable','none',''] else none %}
{% set p_min = state_attr(probe_entity,'min') if probe_exists else none %}
{% set p_max = state_attr(probe_entity,'max') if probe_exists else none %}
{% set p_step = state_attr(probe_entity,'step') if probe_exists else none %}
{% set suggested_action_value = (p_min | float(0)) if p_min is not none else (probe_numeric if probe_numeric is not none else 0) %}
{% set expected_effect_value = (probe_action_value | float(suggested_action_value)) if probe_action_value is not none else suggested_action_value %}
{% set in_range = true %}
{% if p_min is not none and expected_effect_value < (p_min | float(expected_effect_value)) %}{% set in_range = false %}{% endif %}
{% if p_max is not none and expected_effect_value > (p_max | float(expected_effect_value)) %}{% set in_range = false %}{% endif %}
{% set d = ((probe_numeric - expected_effect_value) | abs) if probe_numeric is not none else none %}
{% set tol = (p_step | float(0.5)) if p_step is not none else 0.5 %}
{% set effect_ok = probe_exists and probe_state not in ['unknown','unavailable'] and in_range and (d is not none and d <= tol) %}
{% set layer_d_ok = effect_ok %}

{# Final roll-up #}
{% set pass_count = (1 if layer_a_ok else 0) + (1 if layer_b_ok else 0) + (1 if layer_c_ok else 0) + (1 if layer_d_ok else 0) %}
{% set overall = 'PASS' if pass_count == 4 else ('WARN' if pass_count >= 3 else 'FAIL') %}

### Spectra LS Smoke Test
- Overall: **{{ overall }}**
- Timestamp: **{{ now() }}**
- Layers passed: **{{ pass_count }}/4**

| Layer | Purpose | Status |
|---|---|---|
| A | Core config/runtime integrity | **{{ 'PASS' if layer_a_ok else 'FAIL' }}** |
| B | Routing path (target→host→meta→now-playing) | **{{ 'PASS' if layer_b_ok else 'FAIL' }}** |
| C | Command readiness (writable control surface) | **{{ 'PASS' if layer_c_ok else 'FAIL' }}** |
| D | Command effect snapshot (`{{ probe_entity }}`≈`{{ expected_effect_value }}`) | **{{ 'PASS' if layer_d_ok else 'WARN' }}** |

### Key signals
- Target: **{{ target }}** (valid={{ target_ok }})
- Host: **{{ host }}** (valid={{ host_ok }})
- By-host target: **{{ by_host }}** (valid={{ by_host_ok }})
- Meta: **{{ meta }}** (valid={{ meta_ok }})
- Now playing: **{{ np }}** (valid={{ np_ok }})
- Writable audio controls available: **{{ c.available | length }}** / total writable audio-ish **{{ c.writable | length }}**
- Probe state: **{{ probe_state }}** (delta={{ (d | round(4)) if d is not none else 'n/a' }}, tol={{ tol }})

### Diagnostics
{% if (ns.missing | length) > 0 %}
Missing core entities:
{% for eid in ns.missing %}
- {{ eid }}
{% endfor %}
{% endif %}

{% if (ns.unavailable | length) > 0 %}
Unavailable core entities:
{% for eid in ns.unavailable %}
- {{ eid }}
{% endfor %}
{% endif %}

### Next step guidance
{% if overall == 'PASS' %}
- System smoke test passed. Proceed with feature testing / UX validation.
{% elif not layer_a_ok %}
- Fix core missing/unavailable entities first (Template 1).
{% elif not layer_b_ok %}
- Debug routing mismatch (Template 2).
{% elif not layer_c_ok %}
- Restore writable control entities / host readiness (Template 3).
{% else %}
- Re-run before/after effect check with a fresh action (Template 4).
{% endif %}
```

## 6) Rename Step Validation — Lighting Package (Post-Reload)

```jinja
{# =========================
  Spectra Rename Step Validation (Lighting package rename)
  Run AFTER: HA reload/restart + ESPHome device online
  Purpose: confirm no contract regression in lighting/target helpers used by renamed package include.
  ========================= #}

{% set required = [
  'input_select.control_board_room',
  'input_select.control_board_target',
  'sensor.control_board_room_options',
  'sensor.control_board_target_options',
  'sensor.control_board_room_area_id',
  'sensor.control_board_target_entity_id',
  'sensor.control_board_room_hs',
  'sensor.control_board_target_hs',
  'binary_sensor.control_board_room_on',
  'binary_sensor.control_board_target_on',
  'sensor.ma_control_host',
  'input_select.ma_active_target'
] %}

{% set ns = namespace(missing=[], unavailable=[], ok=0, rows=[]) %}
{% for eid in required %}
  {% set exists = states[eid] is not none %}
  {% set st = states(eid) if exists else 'missing' %}
  {% if not exists %}
    {% set ns.missing = ns.missing + [eid] %}
  {% elif st in ['unknown','unavailable'] %}
    {% set ns.unavailable = ns.unavailable + [eid] %}
  {% else %}
    {% set ns.ok = ns.ok + 1 %}
  {% endif %}
  {% set ns.rows = ns.rows + [{'entity':eid,'exists':exists,'state':st}] %}
{% endfor %}

{% set room = states('input_select.control_board_room') %}
{% set target = states('input_select.control_board_target') %}
{% set room_opts = state_attr('input_select.control_board_room','options') or [] %}
{% set target_opts = state_attr('input_select.control_board_target','options') or [] %}
{% set room_sel_ok = room in room_opts if (room_opts | length) > 0 else false %}
{% set target_sel_ok = target in target_opts if (target_opts | length) > 0 else false %}
{% set room_opts_meaningful = (room_opts | reject('in', ['No Rooms','Unknown','none','unknown','unavailable','']) | list | length) > 0 %}
{% set target_opts_meaningful = (target_opts | reject('in', ['All','none','unknown','unavailable','']) | list | length) > 0 %}

{% set verdict = 'PASS' %}
{% if (ns.missing | length) > 0 %}
  {% set verdict = 'FAIL' %}
{% elif not room_opts_meaningful %}
  {% set verdict = 'FAIL' %}
{% elif (ns.unavailable | length) > 0 or not room_sel_ok or not target_sel_ok %}
  {% set verdict = 'WARN' %}
{% elif not target_opts_meaningful %}
  {% set verdict = 'WARN' %}
{% endif %}

### Rename Validation — Lighting Package
- Result: **{{ verdict }}**
- Timestamp: **{{ now() }}**
- Checked entities: **{{ required | length }}**
- OK: **{{ ns.ok }}**
- Missing: **{{ ns.missing | length }}**
- Unknown/Unavailable: **{{ ns.unavailable | length }}**

### Selector sanity
- `input_select.control_board_room`: **{{ room }}** (options={{ room_opts | length }}, selected_in_options={{ room_sel_ok }})
- `input_select.control_board_target`: **{{ target }}** (options={{ target_opts | length }}, selected_in_options={{ target_sel_ok }})
- Room options meaningful (not placeholders): **{{ room_opts_meaningful }}**
- Target options meaningful (beyond `All`): **{{ target_opts_meaningful }}**
- `sensor.ma_control_host`: **{{ states('sensor.ma_control_host') }}**
- `input_select.ma_active_target`: **{{ states('input_select.ma_active_target') }}**

### Missing entities
{% if (ns.missing | length) == 0 %}
- none
{% else %}
{% for eid in ns.missing %}
- {{ eid }}
{% endfor %}
{% endif %}

### Unknown/Unavailable entities
{% if (ns.unavailable | length) == 0 %}
- none
{% else %}
{% for eid in ns.unavailable %}
- {{ eid }}
{% endfor %}
{% endif %}

### Detailed table
| Entity | Exists | State |
|---|---:|---|
{% for row in ns.rows %}
| `{{ row.entity }}` | {{ row.exists }} | {{ row.state }} |
{% endfor %}

### Next action guidance
{% if verdict == 'PASS' %}
- Lighting rename step validated. Proceed to next rename slice.
{% elif (ns.missing | length) > 0 %}
- Missing helper/entity contracts detected. Fix package/helper load before next rename.
{% elif not room_opts_meaningful %}
- Room options are placeholder-only (`No Rooms`/`Unknown`). This is a real data-path failure, not a PASS. Fix room population source before continuing.
{% else %}
- Resolve unavailable/select-option mismatch first, then rerun this template.
{% endif %}
```

## 7) Rename Step Validation — Audio TCP Package (Post-Reload)

```jinja
{# =========================
  Spectra Rename Step Validation (Audio TCP package rename)
  Run AFTER: HA reload/restart + ESPHome device online
  Purpose: confirm no contract regression in audio command surfaces and routing helpers used by renamed package include.
  ========================= #}

{% set required = [
  'sensor.ma_control_host',
  'sensor.ma_control_hosts',
  'input_select.ma_active_target',
  'sensor.ma_active_target_by_host',
  'sensor.ma_active_meta_entity',
  'sensor.now_playing_entity',
  'sensor.now_playing_state',
  'sensor.now_playing_title',
  'number.control_board_v2_arylic_volume_set',
  'number.control_board_v2_eq_low',
  'number.control_board_v2_eq_mid',
  'number.control_board_v2_eq_high'
] %}

{% set ns = namespace(missing=[], unavailable=[], ok=0, rows=[]) %}
{% for eid in required %}
  {% set exists = states[eid] is not none %}
  {% set st = states(eid) if exists else 'missing' %}
  {% if not exists %}
    {% set ns.missing = ns.missing + [eid] %}
  {% elif st in ['unknown','unavailable'] %}
    {% set ns.unavailable = ns.unavailable + [eid] %}
  {% else %}
    {% set ns.ok = ns.ok + 1 %}
  {% endif %}
  {% set ns.rows = ns.rows + [{'entity':eid,'exists':exists,'state':st}] %}
{% endfor %}

{% set target = states('input_select.ma_active_target') %}
{% set target_opts = state_attr('input_select.ma_active_target','options') or [] %}
{% set target_sel_ok = target in target_opts if (target_opts | length) > 0 else false %}
{% set host = states('sensor.ma_control_host') %}
{% set host_ok = host not in ['','none','unknown','unavailable'] %}

{% set volume = states('number.control_board_v2_arylic_volume_set') %}
{% set eq_low = states('number.control_board_v2_eq_low') %}
{% set eq_mid = states('number.control_board_v2_eq_mid') %}
{% set eq_high = states('number.control_board_v2_eq_high') %}

{% set verdict = 'PASS' %}
{% if (ns.missing | length) > 0 %}
  {% set verdict = 'FAIL' %}
{% elif (ns.unavailable | length) > 0 or not target_sel_ok or not host_ok %}
  {% set verdict = 'WARN' %}
{% endif %}

### Rename Validation — Audio TCP Package
- Result: **{{ verdict }}**
- Timestamp: **{{ now() }}**
- Checked entities: **{{ required | length }}**
- OK: **{{ ns.ok }}**
- Missing: **{{ ns.missing | length }}**
- Unknown/Unavailable: **{{ ns.unavailable | length }}**

### Routing + selector sanity
- `input_select.ma_active_target`: **{{ target }}** (options={{ target_opts | length }}, selected_in_options={{ target_sel_ok }})
- `sensor.ma_control_host`: **{{ host }}** (valid={{ host_ok }})
- `sensor.ma_control_hosts`: **{{ states('sensor.ma_control_hosts') }}**
- `sensor.now_playing_entity`: **{{ states('sensor.now_playing_entity') }}**

### Audio command surfaces
- `number.control_board_v2_arylic_volume_set`: **{{ volume }}**
- `number.control_board_v2_eq_low`: **{{ eq_low }}**
- `number.control_board_v2_eq_mid`: **{{ eq_mid }}**
- `number.control_board_v2_eq_high`: **{{ eq_high }}**

### Missing entities
{% if (ns.missing | length) == 0 %}
- none
{% else %}
{% for eid in ns.missing %}
- {{ eid }}
{% endfor %}
{% endif %}

### Unknown/Unavailable entities
{% if (ns.unavailable | length) == 0 %}
- none
{% else %}
{% for eid in ns.unavailable %}
- {{ eid }}
{% endfor %}
{% endif %}

### Detailed table
| Entity | Exists | State |
|---|---:|---|
{% for row in ns.rows %}
| `{{ row.entity }}` | {{ row.exists }} | {{ row.state }} |
{% endfor %}

### Next action guidance
{% if verdict == 'PASS' %}
- Audio TCP rename step validated. Proceed to next rename slice.
{% elif (ns.missing | length) > 0 %}
- Missing audio/routing contracts detected. Restore package include/load before next rename.
{% else %}
- Resolve unavailable host/selector/number entities first, then rerun this template.
{% endif %}
```

## 8) Rename Step Validation — System Package (Post-Reload)

```jinja
{# =========================
  Spectra Rename Step Validation (System package rename)
  Run AFTER: HA reload/restart + ESPHome device online
  Purpose: confirm no contract regression in core routing/state surfaces used by renamed system package include.
  ========================= #}

{% set required = [
  'sensor.ma_control_host',
  'sensor.ma_control_hosts',
  'sensor.ma_api_url',
  'input_select.ma_active_target',
  'sensor.ma_active_target_by_host',
  'sensor.ma_active_meta_entity',
  'sensor.now_playing_entity',
  'sensor.now_playing_state',
  'sensor.now_playing_title',
  'number.control_board_v2_arylic_volume_set',
  'input_select.control_board_room',
  'input_select.control_board_target'
] %}

{% set ns = namespace(missing=[], unavailable=[], ok=0, rows=[]) %}
{% for eid in required %}
  {% set exists = states[eid] is not none %}
  {% set st = states(eid) if exists else 'missing' %}
  {% if not exists %}
    {% set ns.missing = ns.missing + [eid] %}
  {% elif st in ['unknown','unavailable'] %}
    {% set ns.unavailable = ns.unavailable + [eid] %}
  {% else %}
    {% set ns.ok = ns.ok + 1 %}
  {% endif %}
  {% set ns.rows = ns.rows + [{'entity':eid,'exists':exists,'state':st}] %}
{% endfor %}

{% set target = states('input_select.ma_active_target') %}
{% set target_opts = state_attr('input_select.ma_active_target','options') or [] %}
{% set target_sel_ok = target in target_opts if (target_opts | length) > 0 else false %}

{% set room = states('input_select.control_board_room') %}
{% set room_opts = state_attr('input_select.control_board_room','options') or [] %}
{% set room_sel_ok = room in room_opts if (room_opts | length) > 0 else false %}

{% set host = states('sensor.ma_control_host') %}
{% set host_ok = host not in ['','none','unknown','unavailable'] %}

{% set verdict = 'PASS' %}
{% if (ns.missing | length) > 0 %}
  {% set verdict = 'FAIL' %}
{% elif (ns.unavailable | length) > 0 or not target_sel_ok or not room_sel_ok or not host_ok %}
  {% set verdict = 'WARN' %}
{% endif %}

### Rename Validation — System Package
- Result: **{{ verdict }}**
- Timestamp: **{{ now() }}**
- Checked entities: **{{ required | length }}**
- OK: **{{ ns.ok }}**
- Missing: **{{ ns.missing | length }}**
- Unknown/Unavailable: **{{ ns.unavailable | length }}**

### Core routing sanity
- `sensor.ma_control_host`: **{{ host }}** (valid={{ host_ok }})
- `sensor.ma_control_hosts`: **{{ states('sensor.ma_control_hosts') }}**
- `input_select.ma_active_target`: **{{ target }}** (options={{ target_opts | length }}, selected_in_options={{ target_sel_ok }})
- `input_select.control_board_room`: **{{ room }}** (options={{ room_opts | length }}, selected_in_options={{ room_sel_ok }})
- `sensor.now_playing_entity`: **{{ states('sensor.now_playing_entity') }}**

### Missing entities
{% if (ns.missing | length) == 0 %}
- none
{% else %}
{% for eid in ns.missing %}
- {{ eid }}
{% endfor %}
{% endif %}

### Unknown/Unavailable entities
{% if (ns.unavailable | length) == 0 %}
- none
{% else %}
{% for eid in ns.unavailable %}
- {{ eid }}
{% endfor %}
{% endif %}

### Detailed table
| Entity | Exists | State |
|---|---:|---|
{% for row in ns.rows %}
| `{{ row.entity }}` | {{ row.exists }} | {{ row.state }} |
{% endfor %}

### Next action guidance
{% if verdict == 'PASS' %}
- System rename step validated. Proceed to next rename slice.
{% elif (ns.missing | length) > 0 %}
- Missing core contracts detected. Restore package include/load before next rename.
{% else %}
- Resolve unavailable/selector mismatch first, then rerun this template.
{% endif %}
```

## 9) Rename Step Validation — Peripherals Package (Post-Reload)

```jinja
{# =========================
  Spectra Rename Step Validation (Peripherals package rename)
  Run AFTER: HA reload/restart + ESPHome device online
  Purpose: confirm no contract regression in display/routing surfaces after renaming the active peripherals include.
  ========================= #}

{% set required = [
  'sensor.ma_control_host',
  'sensor.ma_control_hosts',
  'input_select.ma_active_target',
  'sensor.ma_active_target_by_host',
  'sensor.ma_active_meta_entity',
  'sensor.now_playing_entity',
  'sensor.now_playing_state',
  'sensor.now_playing_title',
  'input_select.control_board_room',
  'input_select.control_board_target',
  'number.control_board_v2_arylic_volume_set',
  'number.control_board_v2_eq_low',
  'number.control_board_v2_eq_mid',
  'number.control_board_v2_eq_high'
] %}

{% set ns = namespace(missing=[], unavailable=[], ok=0, rows=[]) %}
{% for eid in required %}
  {% set exists = states[eid] is not none %}
  {% set st = states(eid) if exists else 'missing' %}
  {% if not exists %}
    {% set ns.missing = ns.missing + [eid] %}
  {% elif st in ['unknown','unavailable'] %}
    {% set ns.unavailable = ns.unavailable + [eid] %}
  {% else %}
    {% set ns.ok = ns.ok + 1 %}
  {% endif %}
  {% set ns.rows = ns.rows + [{'entity':eid,'exists':exists,'state':st}] %}
{% endfor %}

{% set target = states('input_select.ma_active_target') %}
{% set target_opts = state_attr('input_select.ma_active_target','options') or [] %}
{% set target_sel_ok = target in target_opts if (target_opts | length) > 0 else false %}

{% set room = states('input_select.control_board_room') %}
{% set target_light = states('input_select.control_board_target') %}
{% set room_opts = state_attr('input_select.control_board_room','options') or [] %}
{% set target_light_opts = state_attr('input_select.control_board_target','options') or [] %}
{% set room_sel_ok = room in room_opts if (room_opts | length) > 0 else false %}
{% set target_light_sel_ok = target_light in target_light_opts if (target_light_opts | length) > 0 else false %}

{% set host = states('sensor.ma_control_host') %}
{% set host_ok = host not in ['','none','unknown','unavailable'] %}

{% set verdict = 'PASS' %}
{% if (ns.missing | length) > 0 %}
  {% set verdict = 'FAIL' %}
{% elif (ns.unavailable | length) > 0 or not target_sel_ok or not room_sel_ok or not target_light_sel_ok or not host_ok %}
  {% set verdict = 'WARN' %}
{% endif %}

### Rename Validation — Peripherals Package
- Result: **{{ verdict }}**
- Timestamp: **{{ now() }}**
- Checked entities: **{{ required | length }}**
- OK: **{{ ns.ok }}**
- Missing: **{{ ns.missing | length }}**
- Unknown/Unavailable: **{{ ns.unavailable | length }}**

### Display + routing sanity
- `sensor.ma_control_host`: **{{ host }}** (valid={{ host_ok }})
- `sensor.ma_control_hosts`: **{{ states('sensor.ma_control_hosts') }}**
- `input_select.ma_active_target`: **{{ target }}** (options={{ target_opts | length }}, selected_in_options={{ target_sel_ok }})
- `sensor.now_playing_entity`: **{{ states('sensor.now_playing_entity') }}**
- `sensor.now_playing_state`: **{{ states('sensor.now_playing_state') }}**
- `sensor.now_playing_title`: **{{ states('sensor.now_playing_title') }}**
- `input_select.control_board_room`: **{{ room }}** (options={{ room_opts | length }}, selected_in_options={{ room_sel_ok }})
- `input_select.control_board_target`: **{{ target_light }}** (options={{ target_light_opts | length }}, selected_in_options={{ target_light_sel_ok }})

### Missing entities
{% if (ns.missing | length) == 0 %}
- none
{% else %}
{% for eid in ns.missing %}
- {{ eid }}
{% endfor %}
{% endif %}

### Unknown/Unavailable entities
{% if (ns.unavailable | length) == 0 %}
- none
{% else %}
{% for eid in ns.unavailable %}
- {{ eid }}
{% endfor %}
{% endif %}

### Detailed table
| Entity | Exists | State |
|---|---:|---|
{% for row in ns.rows %}
| `{{ row.entity }}` | {{ row.exists }} | {{ row.state }} |
{% endfor %}

### Next action guidance
{% if verdict == 'PASS' %}
- Peripherals package rename step validated. Proceed to next rename slice.
{% elif (ns.missing | length) > 0 %}
- Missing display/routing contracts detected. Restore package include/load before next rename.
{% else %}
- Resolve unavailable/selector mismatch first, then rerun this template.
{% endif %}
```

## 10) Rename Step Validation — UI Package (Post-Reload)

```jinja
{# =========================
  Spectra Rename Step Validation (UI package rename)
  Run AFTER: HA reload/restart + ESPHome device online
  Purpose: confirm no contract regression in UI helper/selector surfaces used by renamed UI package include.
  ========================= #}

{% set required = [
  'input_select.control_board_room',
  'input_select.control_board_target',
  'sensor.control_board_room_options',
  'sensor.control_board_target_options',
  'sensor.control_board_room_area_id',
  'sensor.control_board_target_entity_id',
  'sensor.control_board_room_hs',
  'sensor.control_board_target_hs',
  'binary_sensor.control_board_room_on',
  'binary_sensor.control_board_target_on',
  'sensor.ma_control_host',
  'input_select.ma_active_target'
] %}

{% set ns = namespace(missing=[], unavailable=[], ok=0, rows=[]) %}
{% for eid in required %}
  {% set exists = states[eid] is not none %}
  {% set st = states(eid) if exists else 'missing' %}
  {% if not exists %}
    {% set ns.missing = ns.missing + [eid] %}
  {% elif st in ['unknown','unavailable'] %}
    {% set ns.unavailable = ns.unavailable + [eid] %}
  {% else %}
    {% set ns.ok = ns.ok + 1 %}
  {% endif %}
  {% set ns.rows = ns.rows + [{'entity':eid,'exists':exists,'state':st}] %}
{% endfor %}

{% set room = states('input_select.control_board_room') %}
{% set target = states('input_select.control_board_target') %}
{% set room_opts = state_attr('input_select.control_board_room','options') or [] %}
{% set target_opts = state_attr('input_select.control_board_target','options') or [] %}
{% set room_sel_ok = room in room_opts if (room_opts | length) > 0 else false %}
{% set target_sel_ok = target in target_opts if (target_opts | length) > 0 else false %}

{% set verdict = 'PASS' %}
{% if (ns.missing | length) > 0 %}
  {% set verdict = 'FAIL' %}
{% elif (ns.unavailable | length) > 0 or not room_sel_ok or not target_sel_ok %}
  {% set verdict = 'WARN' %}
{% endif %}

### Rename Validation — UI Package
- Result: **{{ verdict }}**
- Timestamp: **{{ now() }}**
- Checked entities: **{{ required | length }}**
- OK: **{{ ns.ok }}**
- Missing: **{{ ns.missing | length }}**
- Unknown/Unavailable: **{{ ns.unavailable | length }}**

### Selector sanity
- `input_select.control_board_room`: **{{ room }}** (options={{ room_opts | length }}, selected_in_options={{ room_sel_ok }})
- `input_select.control_board_target`: **{{ target }}** (options={{ target_opts | length }}, selected_in_options={{ target_sel_ok }})
- `sensor.ma_control_host`: **{{ states('sensor.ma_control_host') }}**
- `input_select.ma_active_target`: **{{ states('input_select.ma_active_target') }}**

### Missing entities
{% if (ns.missing | length) == 0 %}
- none
{% else %}
{% for eid in ns.missing %}
- {{ eid }}
{% endfor %}
{% endif %}

### Unknown/Unavailable entities
{% if (ns.unavailable | length) == 0 %}
- none
{% else %}
{% for eid in ns.unavailable %}
- {{ eid }}
{% endfor %}
{% endif %}

### Detailed table
| Entity | Exists | State |
|---|---:|---|
{% for row in ns.rows %}
| `{{ row.entity }}` | {{ row.exists }} | {{ row.state }} |
{% endfor %}

### Next action guidance
{% if verdict == 'PASS' %}
- UI rename step validated. Proceed to next rename slice.
{% elif (ns.missing | length) > 0 %}
- Missing UI helper contracts detected. Restore package include/load before next rename.
{% else %}
- Resolve unavailable/select-option mismatch first, then rerun this template.
{% endif %}
```

## 11) Rename Step Validation — Hardware Package (Post-Reload)

```jinja
{# =========================
  Spectra Rename Step Validation (Hardware package rename)
  Run AFTER: HA reload/restart + ESPHome device online
  Purpose: confirm no contract regression in control/selector surfaces that depend on renamed hardware package include.
  ========================= #}

{% set required = [
  'sensor.ma_control_host',
  'sensor.ma_control_hosts',
  'input_select.ma_active_target',
  'input_select.control_board_room',
  'input_select.control_board_target',
  'sensor.control_board_room_options',
  'sensor.control_board_target_options',
  'binary_sensor.control_board_room_on',
  'binary_sensor.control_board_target_on',
  'number.control_board_v2_arylic_volume_set',
  'number.control_board_v2_eq_low',
  'number.control_board_v2_eq_mid',
  'number.control_board_v2_eq_high'
] %}

{% set ns = namespace(missing=[], unavailable=[], ok=0, rows=[]) %}
{% for eid in required %}
  {% set exists = states[eid] is not none %}
  {% set st = states(eid) if exists else 'missing' %}
  {% if not exists %}
    {% set ns.missing = ns.missing + [eid] %}
  {% elif st in ['unknown','unavailable'] %}
    {% set ns.unavailable = ns.unavailable + [eid] %}
  {% else %}
    {% set ns.ok = ns.ok + 1 %}
  {% endif %}
  {% set ns.rows = ns.rows + [{'entity':eid,'exists':exists,'state':st}] %}
{% endfor %}

{% set room = states('input_select.control_board_room') %}
{% set target = states('input_select.control_board_target') %}
{% set room_opts = state_attr('input_select.control_board_room','options') or [] %}
{% set target_opts = state_attr('input_select.control_board_target','options') or [] %}
{% set room_sel_ok = room in room_opts if (room_opts | length) > 0 else false %}
{% set target_sel_ok = target in target_opts if (target_opts | length) > 0 else false %}

{% set host = states('sensor.ma_control_host') %}
{% set host_ok = host not in ['','none','unknown','unavailable'] %}

{% set verdict = 'PASS' %}
{% if (ns.missing | length) > 0 %}
  {% set verdict = 'FAIL' %}
{% elif (ns.unavailable | length) > 0 or not room_sel_ok or not target_sel_ok or not host_ok %}
  {% set verdict = 'WARN' %}
{% endif %}

### Rename Validation — Hardware Package
- Result: **{{ verdict }}**
- Timestamp: **{{ now() }}**
- Checked entities: **{{ required | length }}**
- OK: **{{ ns.ok }}**
- Missing: **{{ ns.missing | length }}**
- Unknown/Unavailable: **{{ ns.unavailable | length }}**

### Control + selector sanity
- `sensor.ma_control_host`: **{{ host }}** (valid={{ host_ok }})
- `sensor.ma_control_hosts`: **{{ states('sensor.ma_control_hosts') }}**
- `input_select.control_board_room`: **{{ room }}** (options={{ room_opts | length }}, selected_in_options={{ room_sel_ok }})
- `input_select.control_board_target`: **{{ target }}** (options={{ target_opts | length }}, selected_in_options={{ target_sel_ok }})
- `input_select.ma_active_target`: **{{ states('input_select.ma_active_target') }}**

### Missing entities
{% if (ns.missing | length) == 0 %}
- none
{% else %}
{% for eid in ns.missing %}
- {{ eid }}
{% endfor %}
{% endif %}

### Unknown/Unavailable entities
{% if (ns.unavailable | length) == 0 %}
- none
{% else %}
{% for eid in ns.unavailable %}
- {{ eid }}
{% endfor %}
{% endif %}

### Detailed table
| Entity | Exists | State |
|---|---:|---|
{% for row in ns.rows %}
| `{{ row.entity }}` | {{ row.exists }} | {{ row.state }} |
{% endfor %}

### Next action guidance
{% if verdict == 'PASS' %}
- Hardware rename step validated. Proceed to next rename slice.
{% elif (ns.missing | length) > 0 %}
- Missing hardware-dependent contracts detected. Restore package include/load before next rename.
{% else %}
- Resolve unavailable/selector mismatch first, then rerun this template.
{% endif %}
```

## 12) Package Loader Regression Check — `ma_control_hub` (Post-Reload)

```jinja
{# =========================
  MA Control Hub Package Loader Regression Check
  Run AFTER: HA restart or package reload
  Purpose: quickly detect the exact failure pattern caused by split fragment
           package-loader conflicts (missing helpers/scripts + invalid package init).
  ========================= #}

{% set helpers = [
  'input_boolean.ma_override_active',
  'input_boolean.ma_meta_override_active',
  'input_number.ma_balance',
  'input_number.ma_meta_confidence_min',
  'input_number.ma_meta_stale_s',
  'input_number.ma_pos_stall_s',
  'input_number.ma_end_tolerance_s',
  'input_number.ma_override_pause_s',
  'input_number.ma_auto_idle_s',
  'input_number.ma_auto_playing_s',
  'input_select.ma_active_target',
  'input_text.ma_ambiguous_entities',
  'input_text.ma_server_url',
  'input_text.ma_meta_override_entity',
  'input_text.ma_last_valid_target',
  'input_text.spectra_ls_target_primary_entity',
  'input_text.spectra_ls_target_primary_meta_entity',
  'input_text.spectra_ls_target_primary_tcp_host',
  'input_text.spectra_ls_target_room_entity',
  'input_text.spectra_ls_target_room_meta_entity',
  'input_text.spectra_ls_target_room_tcp_host'
] %}

{% set script_sentinels = [
  'script.ma_update_target_options',
  'script.ma_cycle_target',
  'script.ma_auto_select',
  'script.ma_set_volume',
  'script.ma_set_balance'
] %}

{% set template_sentinels = [
  'sensor.ma_api_url',
  'sensor.ma_control_host',
  'sensor.ma_control_hosts',
  'sensor.now_playing_entity'
] %}

{% set automation_ids = [
  'ma_update_target_options_start',
  'ma_auto_select_loop',
  'ma_track_last_valid_target'
] %}

{% set ns = namespace(total=0, ok=0, missing=[], unavailable=[], rows=[], autom_missing=[]) %}

{% for eid in helpers + script_sentinels + template_sentinels %}
  {% set ns.total = ns.total + 1 %}
  {% set exists = states[eid] is not none %}
  {% set st = states(eid) if exists else 'missing' %}
  {% if not exists %}
    {% set ns.missing = ns.missing + [eid] %}
  {% elif st in ['unknown','unavailable'] %}
    {% set ns.unavailable = ns.unavailable + [eid] %}
  {% else %}
    {% set ns.ok = ns.ok + 1 %}
  {% endif %}
  {% set ns.rows = ns.rows + [{'entity':eid,'exists':exists,'state':st}] %}
{% endfor %}

{% for aid in automation_ids %}
  {% set ns.total = ns.total + 1 %}
  {% set probe = namespace(found=false, match='') %}
  {% for a in states.automation %}
    {% set current_id = (a.attributes.id if a.attributes is defined and a.attributes.id is defined else '') %}
    {% if current_id == aid %}
      {% set probe.found = true %}
      {% set probe.match = a.entity_id %}
    {% endif %}
  {% endfor %}
  {% if probe.found %}
    {% set ns.ok = ns.ok + 1 %}
  {% else %}
    {% set ns.autom_missing = ns.autom_missing + [aid] %}
    {% set ns.missing = ns.missing + ['automation_id:' ~ aid] %}
  {% endif %}
{% endfor %}

{% set target_host = states('input_text.spectra_ls_target_primary_tcp_host') %}
{% set room_host = states('input_text.spectra_ls_target_room_tcp_host') %}
{% set ip_like_primary = target_host is string and (target_host | regex_match('^([0-9]{1,3}\\.){3}[0-9]{1,3}$')) %}
{% set ip_like_room = room_host is string and (room_host | regex_match('^([0-9]{1,3}\\.){3}[0-9]{1,3}$')) %}

{% set verdict = 'PASS' %}
{% if (ns.missing | length) > 0 %}
  {% set verdict = 'FAIL' %}
{% elif (ns.unavailable | length) > 0 or not ip_like_primary or not ip_like_room %}
  {% set verdict = 'WARN' %}
{% endif %}

### Package Loader Regression Check — `ma_control_hub`
- Result: **{{ verdict }}**
- Timestamp: **{{ now() }}**
- Checked signals: **{{ ns.total }}**
- OK: **{{ ns.ok }}**
- Missing: **{{ ns.missing | length }}**
- Unknown/Unavailable: **{{ ns.unavailable | length }}**

### Host include surfaces
- `input_text.spectra_ls_target_primary_tcp_host`: **{{ target_host }}** (ipv4_like={{ ip_like_primary }})
- `input_text.spectra_ls_target_room_tcp_host`: **{{ room_host }}** (ipv4_like={{ ip_like_room }})

### Missing entities/IDs
{% if (ns.missing | length) == 0 %}
- none
{% else %}
{% for e in ns.missing %}
- {{ e }}
{% endfor %}
{% endif %}

### Unknown/Unavailable entities
{% if (ns.unavailable | length) == 0 %}
- none
{% else %}
{% for e in ns.unavailable %}
- {{ e }}
{% endfor %}
{% endif %}

### Quick diagnosis
{% if verdict == 'PASS' %}
- `ma_control_hub` package surfaces look healthy.
{% elif (ns.missing | length) >= 8 %}
- Broad helper/script loss detected; this strongly suggests package-loader conflict or package init failure.
- Check repository guardrail script output and ensure only `.inc` fragments exist under `packages/ma_control_hub/`.
{% else %}
- Partial contract loss detected; inspect package reload logs and missing IDs above.
{% endif %}
```

## 17) Phase 2 Registry/Router Verification — Custom Component (`spectra_ls`)

- Raw copy/paste file (no markdown fences): `docs/testing/raw/p2_registry_router_verification.jinja`
- This raw template is the source of truth for Section 17 and includes:
  - entity-id auto-detection (`sensor.shadow_*` + `sensor.spectra_ls_shadow_*` fallback)
  - deep diagnostics checks (`registry`, `route_trace`, `contract_validation`)
  - snapshot freshness guard (`captured_at` age threshold)

## 18) Phase 2 Negative-Case Regression — Custom Component (`spectra_ls`)

- Raw copy/paste file (no markdown fences): `docs/testing/raw/p2_negative_case_regression.jinja`
- Use this after forcing a known-bad input condition (unsupported/missing target or invalid route context) to verify defer-path diagnostics are emitted as expected.

## 19) Phase 3-S01 Guarded Write Validation — Custom Component (`spectra_ls`)

- Raw copy/paste file (no markdown fences): `docs/testing/raw/p3_s01_guarded_write_validation.jinja`
- Use this to validate `set_write_authority` + `route_write_trial` outcomes and confirm guard-result semantics from `write_controls.last_attempt`.
- One-shot shortcut is available: run `spectra_ls.run_p3_s01_sequence` to execute authority set + rebuild + validate + route-trace + write-trial in one action call.

## 20) Phase 3-S02 Selection-Handoff Validation — Custom Component (`spectra_ls`)

- Raw copy/paste file (no markdown fences): `docs/testing/raw/p3_s02_selection_handoff_validation.jinja`
- Use this to validate selection-handoff readiness diagnostics (`selection_handoff_validation`) with helper/options + compatibility shim checks.
- One-shot shortcut is available: run `spectra_ls.run_p3_s02_sequence` to execute authority set + rebuild + validate + route-trace + optional write-trial + handoff validation in one action call.

## 21) Phase 3 Small Soak Protocol (S01 + S02) — Custom Component (`spectra_ls`)

- Operator runbook file: `docs/testing/raw/p3_s01_s02_soak_protocol.md`
- Use this after baseline S01/S02 PASS to perform compact multi-cycle target-switch soak evidence collection before graduating P3-S02 from Active/Pending.

## 22) Phase 3 Closure Gate Check (S01 + S02) — Custom Component (`spectra_ls`)

- Raw copy/paste file (no markdown fences): `docs/testing/raw/p3_s01_s02_closure_gate_check.jinja`
- Use this after soak collection to produce one deterministic closure verdict covering route/contract/parity/S01/S02 gates plus the distinct-target (or explicit single-capable waiver) decision.

<!-- EOF -->

## 13) Source Truth Test — Is HA Down or Is Control-Hub Path Broken?

```jinja
{# =========================
  Source Truth Test (HA vs Control-Hub Path)
  Run in: Developer Tools -> Template
  Purpose: answer "is HA inaccessible?" vs "source/control-hub path is degraded"
  ========================= #}

{% set core_ha_optional = [
  'sensor.time',
  'sun.sun'
] %}

{% set hub_contract = [
  'sensor.ma_api_url',
  'sensor.ma_control_host',
  'sensor.ma_control_hosts',
  'input_select.ma_active_target',
  'sensor.ma_active_target_by_host',
  'sensor.ma_active_meta_entity',
  'sensor.now_playing_entity',
  'sensor.now_playing_state',
  'sensor.now_playing_title',
  'sensor.control_board_room_options',
  'sensor.control_board_target_options',
  'input_select.control_board_room',
  'input_select.control_board_target'
] %}

{% set source_inputs = [
  'sensor.now_playing_state',
  'sensor.now_playing_title',
  'sensor.ma_active_meta_entity',
  'select.control_board_v2_arylic_source'
] %}

{% set ns = namespace(
  core_missing=[], core_bad=[],
  hub_missing=[], hub_bad=[],
  src_missing=[], src_bad=[],
  src_ok=[]
) %}

{% for eid in core_ha_optional %}
  {% if states[eid] is none %}
    {% set ns.core_missing = ns.core_missing + [eid] %}
  {% else %}
    {% set st = states(eid) %}
    {% if st in ['unknown','unavailable','none',''] %}
      {% set ns.core_bad = ns.core_bad + [eid] %}
    {% endif %}
  {% endif %}
{% endfor %}

{% for eid in hub_contract %}
  {% if states[eid] is none %}
    {% set ns.hub_missing = ns.hub_missing + [eid] %}
  {% else %}
    {% set st = states(eid) %}
    {% if st in ['unknown','unavailable','none',''] %}
      {% set ns.hub_bad = ns.hub_bad + [eid] %}
    {% endif %}
  {% endif %}
{% endfor %}

{% for eid in source_inputs %}
  {% if states[eid] is none %}
    {% set ns.src_missing = ns.src_missing + [eid] %}
  {% else %}
    {% set st = states(eid) %}
    {% if st in ['unknown','unavailable','none',''] %}
      {% set ns.src_bad = ns.src_bad + [eid] %}
    {% else %}
      {% set ns.src_ok = ns.src_ok + [eid] %}
    {% endif %}
  {% endif %}
{% endfor %}

{% set ha_entity_count = states | count %}
{% set room_opts = state_attr('input_select.control_board_room','options') or [] %}
{% set target_opts = state_attr('input_select.control_board_target','options') or [] %}
{% set active_target = states('input_select.ma_active_target') %}
{% set control_host = states('sensor.ma_control_host') %}

{% set core_optional_ok = (ns.core_missing | length + ns.core_bad | length) == 0 %}
{% set ha_core_ok = ha_entity_count > 50 %}
{% set hub_ok = (ns.hub_missing | length == 0) and (ns.hub_bad | length == 0) %}
{% set src_ok_any = (ns.src_ok | length) > 0 %}
{% set room_target_options_ok = (room_opts | length) > 0 and (target_opts | length) > 0 %}
{% set target_selected_ok = active_target not in ['none','unknown','unavailable',''] %}
{% set control_host_ok = control_host not in ['none','unknown','unavailable',''] %}

{% set verdict = 'PASS' %}
{% set conclusion = 'Hub/source path appears healthy.' %}

{% if not ha_core_ok %}
  {% set verdict = 'FAIL' %}
  {% set conclusion = 'Home Assistant core appears degraded (very low entity registry count).' %}
{% elif (ns.hub_missing | length) >= 5 %}
  {% set verdict = 'FAIL' %}
  {% set conclusion = 'Control-hub package contracts are missing (loader/init regression likely).' %}
{% elif (not room_target_options_ok) and (not control_host_ok) and (not target_selected_ok) %}
  {% set verdict = 'FAIL' %}
  {% set conclusion = 'Control-hub routing surfaces are empty after restart (upstream package/data path failure).' %}
{% elif (not src_ok_any) or (not control_host_ok) or (not target_selected_ok) %}
  {% set verdict = 'WARN' %}
  {% set conclusion = 'HA is reachable, but control-hub source/option pipeline is degraded.' %}
{% endif %}

### Source Truth Test — HA vs Control Hub
- Result: **{{ verdict }}**
- Timestamp: **{{ now() }}**
- Conclusion: **{{ conclusion }}**

### Quick state snapshot
- HA core healthy (entity-count heuristic): **{{ ha_core_ok }}**
- HA entity count: **{{ ha_entity_count }}**
- Optional core sentinels healthy (`sensor.time`, `sun.sun`): **{{ core_optional_ok }}**
- Control-hub contract healthy: **{{ hub_ok }}**
- Any usable source feed present: **{{ src_ok_any }}**
- Room/Target option lists non-empty: **{{ room_target_options_ok }}**

### Key values
- `input_select.ma_active_target`: **{{ active_target }}**
- `sensor.ma_control_host`: **{{ control_host }}**
- `input_select.control_board_room` options count: **{{ room_opts | length }}**
- `input_select.control_board_target` options count: **{{ target_opts | length }}**

### Missing / unhealthy signals
{% if (ns.core_missing | length + ns.core_bad | length + ns.hub_missing | length + ns.hub_bad | length + ns.src_missing | length + ns.src_bad | length) == 0 %}
- none
{% else %}
{% for e in ns.core_missing %}
- core missing: `{{ e }}`
{% endfor %}
{% for e in ns.core_bad %}
- core bad: `{{ e }}` (state={{ states(e) }})
{% endfor %}
{% for e in ns.hub_missing %}
- hub missing: `{{ e }}`
{% endfor %}
{% for e in ns.hub_bad %}
- hub bad: `{{ e }}` (state={{ states(e) }})
{% endfor %}
{% for e in ns.src_missing %}
- source missing: `{{ e }}`
{% endfor %}
{% for e in ns.src_bad %}
- source bad: `{{ e }}` (state={{ states(e) }})
{% endfor %}
{% endif %}

### Action guidance
{% if verdict == 'FAIL' and not ha_core_ok %}
- HA core likely degraded (entity registry unexpectedly small). Verify HA startup health/logs, then rerun.
{% elif verdict == 'FAIL' %}
- Control-hub package/data path likely failed. Run Template #12 and repair missing/bad hub contracts before ESP-side debugging.
{% elif verdict == 'WARN' %}
- HA is reachable; issue is source/contract flow. Check `sensor.control_board_room_options`, `sensor.control_board_target_options`, and active target/host mapping before blaming HA uptime.
{% else %}
- Path looks healthy. If OLED still reports bad source, inspect ESP logs for receive/staleness gating.
{% endif %}
```

## 14) Iteration Parser Contract Check — MA Control Hub (Dual-Mode + Mapping)

```jinja
{# =========================
  Iteration Parser Contract Check (MA Control Hub)
  Run AFTER each parser-modernization iteration.
  Purpose: prove complex payload readers tolerate sequence + mapping + guarded string JSON.
  ========================= #}

{% set rooms_raw = state_attr('sensor.spectra_ls_rooms_raw','rooms') %}
{% set candidates_raw = state_attr('sensor.ma_meta_resolver','candidates_json') | default([], true) %}

{% set rooms_type = 'none' %}
{% if rooms_raw is mapping %}
  {% set rooms_type = 'mapping' %}
{% elif rooms_raw is sequence and rooms_raw is not string %}
  {% set rooms_type = 'sequence' %}
{% elif rooms_raw is string %}
  {% set rooms_type = 'string' %}
{% endif %}

{% set candidates_type = 'none' %}
{% if candidates_raw is mapping %}
  {% set candidates_type = 'mapping' %}
{% elif candidates_raw is sequence and candidates_raw is not string %}
  {% set candidates_type = 'sequence' %}
{% elif candidates_raw is string %}
  {% set candidates_type = 'string' %}
{% endif %}

{% set ns = namespace(rooms=[], candidates=[]) %}

{# Normalize rooms using modernization contract #}
{% if rooms_raw is sequence and rooms_raw is not string and rooms_raw is not mapping %}
  {% set ns.rooms = rooms_raw %}
{% elif rooms_raw is mapping %}
  {% set mapped = (rooms_raw.rooms if rooms_raw.rooms is defined else (rooms_raw.result if rooms_raw.result is defined else [])) %}
  {% if mapped is sequence and mapped is not string and mapped is not mapping %}
    {% set ns.rooms = mapped %}
  {% endif %}
{% elif rooms_raw is string %}
  {% set raw_trim = rooms_raw | trim %}
  {% set raw_trim_l = raw_trim | lower %}
  {% if raw_trim_l not in ['unknown','unavailable','none',''] and (raw_trim.startswith('[') or raw_trim.startswith('{')) %}
    {% set parsed = rooms_raw | from_json %}
    {% if parsed is sequence and parsed is not string and parsed is not mapping %}
      {% set ns.rooms = parsed %}
    {% elif parsed is mapping %}
      {% set mapped = (parsed.rooms if parsed.rooms is defined else (parsed.result if parsed.result is defined else [])) %}
      {% if mapped is sequence and mapped is not string and mapped is not mapping %}
        {% set ns.rooms = mapped %}
      {% endif %}
    {% endif %}
  {% endif %}
{% endif %}

{# Normalize candidates using modernization contract #}
{% if candidates_raw is sequence and candidates_raw is not string and candidates_raw is not mapping %}
  {% set ns.candidates = candidates_raw %}
{% elif candidates_raw is mapping %}
  {% set mapped = (candidates_raw.candidates if candidates_raw.candidates is defined else (candidates_raw.result if candidates_raw.result is defined else [])) %}
  {% if mapped is sequence and mapped is not string and mapped is not mapping %}
    {% set ns.candidates = mapped %}
  {% endif %}
{% elif candidates_raw is string %}
  {% set raw_trim = candidates_raw | trim %}
  {% set raw_trim_l = raw_trim | lower %}
  {% if raw_trim_l not in ['unknown','unavailable','none',''] and (raw_trim.startswith('[') or raw_trim.startswith('{')) %}
    {% set parsed = candidates_raw | from_json %}
    {% if parsed is sequence and parsed is not string and parsed is not mapping %}
      {% set ns.candidates = parsed %}
    {% elif parsed is mapping %}
      {% set mapped = (parsed.candidates if parsed.candidates is defined else (parsed.result if parsed.result is defined else [])) %}
      {% if mapped is sequence and mapped is not string and mapped is not mapping %}
        {% set ns.candidates = mapped %}
      {% endif %}
    {% endif %}
  {% endif %}
{% endif %}

{% set room_entities = ns.rooms | selectattr('entity','defined') | map(attribute='entity') | list %}
{% set candidate_entities = ns.candidates | selectattr('entity','defined') | map(attribute='entity') | list %}

{% set has_core_surfaces =
  states['sensor.ma_control_hosts'] is not none and
  states['sensor.ma_control_host'] is not none and
  states['sensor.now_playing_entity'] is not none and
  states['sensor.ma_active_meta_entity'] is not none
%}

{% set verdict = 'PASS' %}
{% if not has_core_surfaces %}
  {% set verdict = 'FAIL' %}
{% elif (ns.rooms | length) == 0 and rooms_type in ['mapping','sequence','string'] %}
  {% set verdict = 'WARN' %}
{% elif (ns.candidates | length) == 0 and candidates_type in ['mapping','sequence','string'] %}
  {% set verdict = 'WARN' %}
{% endif %}

### Iteration Parser Contract Check — MA Control Hub
- Result: **{{ verdict }}**
- Timestamp: **{{ now() }}**

### Raw payload shape
- `rooms_raw` type: **{{ rooms_type }}**
- `candidates_json` type: **{{ candidates_type }}**

### Normalized payload outcomes
- Normalized rooms count: **{{ ns.rooms | length }}**
- Normalized candidates count: **{{ ns.candidates | length }}**
- Room entities (sample): **{{ (room_entities[:8] if (room_entities | length) > 0 else []) }}**
- Candidate entities (sample): **{{ (candidate_entities[:8] if (candidate_entities | length) > 0 else []) }}**

### Core contract surfaces
- `sensor.ma_control_hosts`: **{{ states('sensor.ma_control_hosts') }}**
- `sensor.ma_control_host`: **{{ states('sensor.ma_control_host') }}**
- `sensor.ma_active_meta_entity`: **{{ states('sensor.ma_active_meta_entity') }}**
- `sensor.now_playing_entity`: **{{ states('sensor.now_playing_entity') }}**

### Next action guidance
{% if verdict == 'PASS' %}
- Iteration passed: proceed to next modernization slice.
{% elif verdict == 'WARN' %}
- Parser accepted payload shape but normalized result is empty. Inspect upstream payload content for missing `rooms/result` or `candidates/result` keys.
{% else %}
- Core contract surface missing. Fix package/runtime load before continuing modernization.
{% endif %}
```

## 15) Iteration 2 Parser Guard Check — Trim + Sentinel Determinism

```jinja
{# =========================
  Iteration 2 Parser Guard Check
  Run AFTER trim-guard modernization.
  Purpose: verify whitespace/case-wrapped sentinel strings do not parse,
           while real JSON strings still parse to usable lists.
  ========================= #}

{% set rooms_raw = state_attr('sensor.spectra_ls_rooms_raw','rooms') %}
{% set candidates_raw = state_attr('sensor.ma_meta_resolver','candidates_json') | default([], true) %}

{% set ns = namespace(rooms=[], candidates=[]) %}

{# Rooms normalization (same contract as runtime readers) #}
{% if rooms_raw is sequence and rooms_raw is not string and rooms_raw is not mapping %}
  {% set ns.rooms = rooms_raw %}
{% elif rooms_raw is mapping %}
  {% set mapped = (rooms_raw.rooms if rooms_raw.rooms is defined else (rooms_raw.result if rooms_raw.result is defined else [])) %}
  {% if mapped is sequence and mapped is not string and mapped is not mapping %}
    {% set ns.rooms = mapped %}
  {% endif %}
{% elif rooms_raw is string %}
  {% set raw_trim = rooms_raw | trim %}
  {% set raw_trim_l = raw_trim | lower %}
  {% if raw_trim_l not in ['unknown','unavailable','none',''] and (raw_trim.startswith('[') or raw_trim.startswith('{')) %}
    {% set parsed = rooms_raw | from_json %}
    {% if parsed is sequence and parsed is not string and parsed is not mapping %}
      {% set ns.rooms = parsed %}
    {% elif parsed is mapping %}
      {% set mapped = (parsed.rooms if parsed.rooms is defined else (parsed.result if parsed.result is defined else [])) %}
      {% if mapped is sequence and mapped is not string and mapped is not mapping %}
        {% set ns.rooms = mapped %}
      {% endif %}
    {% endif %}
  {% endif %}
{% endif %}

{# Candidates normalization (same contract as runtime readers) #}
{% if candidates_raw is sequence and candidates_raw is not string and candidates_raw is not mapping %}
  {% set ns.candidates = candidates_raw %}
{% elif candidates_raw is mapping %}
  {% set mapped = (candidates_raw.candidates if candidates_raw.candidates is defined else (candidates_raw.result if candidates_raw.result is defined else [])) %}
  {% if mapped is sequence and mapped is not string and mapped is not mapping %}
    {% set ns.candidates = mapped %}
  {% endif %}
{% elif candidates_raw is string %}
  {% set raw_trim = candidates_raw | trim %}
  {% set raw_trim_l = raw_trim | lower %}
  {% if raw_trim_l not in ['unknown','unavailable','none',''] and (raw_trim.startswith('[') or raw_trim.startswith('{')) %}
    {% set parsed = candidates_raw | from_json %}
    {% if parsed is sequence and parsed is not string and parsed is not mapping %}
      {% set ns.candidates = parsed %}
    {% elif parsed is mapping %}
      {% set mapped = (parsed.candidates if parsed.candidates is defined else (parsed.result if parsed.result is defined else [])) %}
      {% if mapped is sequence and mapped is not string and mapped is not mapping %}
        {% set ns.candidates = mapped %}
      {% endif %}
    {% endif %}
  {% endif %}
{% endif %}

{# Sentinel simulation checks #}
{% set simulated_sentinels = [' unknown ', 'UNAVAILABLE', ' None ', '   '] %}
{% set sim = namespace(blocked=0,total=0) %}
{% for s in simulated_sentinels %}
  {% set sim.total = sim.total + 1 %}
  {% set s_trim = s | trim %}
  {% set s_trim_l = s_trim | lower %}
  {% if s_trim_l in ['unknown','unavailable','none',''] %}
    {% set sim.blocked = sim.blocked + 1 %}
  {% endif %}
{% endfor %}

{% set verdict = 'PASS' %}
{% if (ns.rooms | length) == 0 %}
  {% set verdict = 'WARN' %}
{% endif %}
{% if (sim.blocked != sim.total) %}
  {% set verdict = 'FAIL' %}
{% endif %}

### Iteration 2 Parser Guard Check — Trim + Sentinel Determinism
- Result: **{{ verdict }}**
- Timestamp: **{{ now() }}**

### Normalized runtime outcomes
- Normalized rooms count: **{{ ns.rooms | length }}**
- Normalized candidates count: **{{ ns.candidates | length }}**
- `sensor.ma_control_host`: **{{ states('sensor.ma_control_host') }}**
- `sensor.ma_active_meta_entity`: **{{ states('sensor.ma_active_meta_entity') }}**

### Sentinel trim/lower simulation
- Simulated sentinels checked: **{{ sim.total }}**
- Correctly blocked by trim+lower guard: **{{ sim.blocked }}**

### Guidance
{% if verdict == 'PASS' %}
- Guard determinism looks healthy. Proceed to next optimization slice.
{% elif verdict == 'WARN' %}
- Guard logic is active, but normalized runtime payload looks empty. Inspect upstream rooms/candidates payload content.
{% else %}
- Sentinel guard determinism failed. Re-check parser branches for trim+lower checks.
{% endif %}
```

## 16) Iteration 4 Diagnostics Chatter Check — Virtual Harness Cadence

```jinja
{# =========================
  Iteration 4 Diagnostics Chatter Check
  Purpose: verify reduced virtual diagnostics idle spam while preserving
           live interaction visibility.
  Run once idle, then interact with encoder/buttons/pots and run again.
  ========================= #}

{% set find = namespace(vm='', vc='', vb='', probe='') %}

{% for n in states.number %}
  {% set eid = n.entity_id | default('', true) %}
  {% set eid_l = eid | lower %}
  {% set fn = (n.attributes.friendly_name if n.attributes is defined and n.attributes.friendly_name is defined else '') | string %}
  {% set fn_l = fn | lower %}
  {% if find.vm == '' and ('virtual mode selector index' in fn_l or eid_l.endswith('_virtual_mode_selector_index')) %}
    {% set find.vm = eid %}
  {% endif %}
  {% if find.vc == '' and ('virtual control class index' in fn_l or eid_l.endswith('_virtual_control_class_index')) %}
    {% set find.vc = eid %}
  {% endif %}
  {% if find.probe == '' and ('arylic volume set' in fn_l or eid_l.endswith('_arylic_volume_set')) %}
    {% set find.probe = eid %}
  {% endif %}
{% endfor %}

{% for t in states.sensor %}
  {% set eid = t.entity_id | default('', true) %}
  {% set eid_l = eid | lower %}
  {% set fn = (t.attributes.friendly_name if t.attributes is defined and t.attributes.friendly_name is defined else '') | string %}
  {% set fn_l = fn | lower %}
  {% if find.vb == '' and ('virtual input battery status' in fn_l or eid_l.endswith('_virtual_input_battery_status')) %}
    {% set find.vb = eid %}
  {% endif %}
{% endfor %}

{% set vm = find.vm if find.vm != '' else 'number.control_board_v2_virtual_mode_selector_index' %}
{% set vc = find.vc if find.vc != '' else 'number.control_board_v2_virtual_control_class_index' %}
{% set vb = find.vb if find.vb != '' else 'sensor.spectra_ls_system_virtual_input_battery_status' %}
{% set probe = find.probe if find.probe != '' else 'number.control_board_v2_arylic_volume_set' %}

{% set vm_ok = vm != '' and states[vm] is not none %}
{% set vc_ok = vc != '' and states[vc] is not none %}
{% set vb_ok = vb != '' and states[vb] is not none %}
{% set probe_ok = states[probe] is not none %}

{% set vm_age = (as_timestamp(now()) - as_timestamp(states[vm].last_updated)) if vm_ok else none %}
{% set vc_age = (as_timestamp(now()) - as_timestamp(states[vc].last_updated)) if vc_ok else none %}
{% set vb_age = (as_timestamp(now()) - as_timestamp(states[vb].last_updated)) if vb_ok else none %}
{% set probe_age = (as_timestamp(now()) - as_timestamp(states[probe].last_updated)) if probe_ok else none %}

{% set recent_virtual_seen =
  (vm_ok and vm_age is not none and vm_age <= 60) or
  (vc_ok and vc_age is not none and vc_age <= 60) or
  (vb_ok and vb_age is not none and vb_age <= 90)
%}

{% set interaction_seen =
  (probe_ok and probe_age is not none and probe_age <= 30) or
  recent_virtual_seen
%}

{% set score = 0 %}
{% if vm_ok %}{% set score = score + 1 %}{% endif %}
{% if vc_ok %}{% set score = score + 1 %}{% endif %}
{% if vb_ok %}{% set score = score + 1 %}{% endif %}
{% if interaction_seen %}{% set score = score + 1 %}{% endif %}

{% set verdict = 'PASS' %}
{% if not (vm_ok and vc_ok and vb_ok) %}
  {% set verdict = 'FAIL' %}
{% elif not interaction_seen %}
  {% set verdict = 'WARN' %}
{% endif %}

### Iteration 4 Diagnostics Chatter Check
- Result: **{{ verdict }}**
- Timestamp: **{{ now() }}**
- Score: **{{ score }}/4**

### Virtual harness cadence probes
- `{{ vm }}` exists={{ vm_ok }}, age_s={{ (vm_age | round(2)) if vm_age is not none else 'n/a' }}
- `{{ vc }}` exists={{ vc_ok }}, age_s={{ (vc_age | round(2)) if vc_age is not none else 'n/a' }}
- `{{ vb }}` exists={{ vb_ok }}, age_s={{ (vb_age | round(2)) if vb_age is not none else 'n/a' }}

### Interaction visibility probe
- `{{ probe }}` exists={{ probe_ok }}, age_s={{ (probe_age | round(2)) if probe_age is not none else 'n/a' }}
- Recent virtual signal seen (mode/class/battery): **{{ recent_virtual_seen }}**
- Interaction observed in last 30s: **{{ interaction_seen }}**

### Guidance
{% if verdict == 'PASS' %}
- Cadence reduction is healthy: virtual diagnostics are quieter at idle and interaction signals remain visible.
{% elif not (vm_ok and vc_ok and vb_ok) %}
- One or more virtual diagnostics entities are missing. Validate ESPHome entity exposure first.
{% elif not interaction_seen %}
- Virtual entities exist, but no recent activity was detected on watched probes. Note: physical dials/encoders do not necessarily update virtual test entities; run `Run Virtual Input Battery` or change the virtual mode/class controls, then rerun.
{% else %}
- Cadence windows are outside expected bounds. Check diagnostics package update intervals and device connectivity.
{% endif %}
```

<!-- EOF -->