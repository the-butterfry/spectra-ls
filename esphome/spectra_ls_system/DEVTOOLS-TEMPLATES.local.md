<!-- Description: Copy/paste Home Assistant Dev Tools template diagnostics for Spectra LS System. -->
<!-- Version: 2026.04.16.11 -->
<!-- Last updated: 2026-04-16 -->

# Spectra LS System — Dev Tools Template Validation

> Tracked diagnostics guide for repeatable Spectra LS system validation.  
> Use each template by copying into **Home Assistant → Developer Tools → Template**.

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

{% set room_attr = state_attr('sensor.spectra_ls_rooms_raw','rooms') %}
{% set rooms = [] %}
{% if room_attr is sequence and room_attr is not string %}
  {% set rooms = room_attr %}
{% elif room_attr is string %}
  {% set raw_l = room_attr | lower %}
  {% set raw_trim = room_attr | trim %}
  {% if raw_l not in ['','none','unknown','unavailable'] and (raw_trim.startswith('[') or raw_trim.startswith('{')) %}
    {% set rooms = room_attr | from_json %}
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

{% set ns = namespace(writable=[], available=[], unavailable=[], eq=[], eq_ready=[], volume=[], volume_ready=[], diagnostics=[]) %}

{# Find writable number entities likely tied to audio control #}
{% for n in states.number %}
  {% set eid = n.entity_id %}
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
{% set expected_value = 3.0 %}

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

{% set expected_in_range = true %}
{% if probe_min is not none and expected_value < (probe_min | float(expected_value)) %}
  {% set expected_in_range = false %}
{% endif %}
{% if probe_max is not none and expected_value > (probe_max | float(expected_value)) %}
  {% set expected_in_range = false %}
{% endif %}

{% set delta = (probe_numeric - expected_value) | abs if probe_has_numeric else none %}
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
- Expected value: **{{ expected_value }}**
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
{% set expected_value = 3.0 %}

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
{% set c = namespace(writable=[], available=[]) %}
{% for n in states.number %}
  {% set eid = n.entity_id %}
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
{% endfor %}
{% set layer_c_ok = host_ok and (c.available | length) > 0 %}

{# Layer D: Effect snapshot check against expected value #}
{% set probe_exists = states[probe_entity] is not none %}
{% set probe_state = states(probe_entity) if probe_exists else 'missing' %}
{% set probe_numeric = (probe_state | float(none)) if probe_state not in ['missing','unknown','unavailable','none',''] else none %}
{% set p_min = state_attr(probe_entity,'min') if probe_exists else none %}
{% set p_max = state_attr(probe_entity,'max') if probe_exists else none %}
{% set p_step = state_attr(probe_entity,'step') if probe_exists else none %}
{% set in_range = true %}
{% if p_min is not none and expected_value < (p_min | float(expected_value)) %}{% set in_range = false %}{% endif %}
{% if p_max is not none and expected_value > (p_max | float(expected_value)) %}{% set in_range = false %}{% endif %}
{% set d = ((probe_numeric - expected_value) | abs) if probe_numeric is not none else none %}
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
| D | Command effect snapshot (`{{ probe_entity }}`≈`{{ expected_value }}`) | **{{ 'PASS' if layer_d_ok else 'WARN' }}** |

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

{% set verdict = 'PASS' %}
{% if (ns.missing | length) > 0 %}
  {% set verdict = 'FAIL' %}
{% elif (ns.unavailable | length) > 0 or not room_sel_ok or not target_sel_ok %}
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

## 9) Rename Step Validation — UI Package (Post-Reload)

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
