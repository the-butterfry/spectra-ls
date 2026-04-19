<!-- Description: Feature inventory and phased rebuild plan for dst_tuya_ac package. -->
<!-- Version: 2026.04.18.1 -->
<!-- Last updated: 2026-04-18 -->

# DST + Tuya AC — Legacy Feature Inventory

This file catalogs what existed in `dst_tuya_ac.yaml` before the reset-to-baseline rebuild.

## Existing feature surface (pre-reset)

### Control surfaces

- Template switches for AC mode control:
  - `switch.ac_cooler`
  - `switch.ac_fan`
  - `switch.ac_dryer`
- Template fan wrapper:
  - `fan.ac_fan` with preset forwarding (`low/high/auto/strong`)
- DST climate entity:
  - `climate.room_dst` (`dual_smart_thermostat`)

### Policy + decision layer

- `sensor.ac_target_mode` decision sensor (away/pause/manual/fan-policy/schedule logic)
- `sensor.ac_control_reason` reason trace surface
- `binary_sensor.ac_schedule_cool_request`
- `binary_sensor.ac_warm_rising_policy_active`
- `binary_sensor.ac_fan_policy_active`
- `binary_sensor.ac_manual_override_active`
- `binary_sensor.ac_pause_active`

### Diagnostics + trend layer

- `sensor.ac_tuya_hvac_action`
- Statistics source + derived trend sensors:
  - `sensor.dst_room_temp_change_1h_raw`
  - `sensor.dst_room_temp_change_1h`
  - `sensor.dst_room_temp_rate_1h`
  - `sensor.dst_room_temp_trend_1h_summary`
  - `binary_sensor.dst_room_temp_rising_1h`

### Scripts

- Manual hold lifecycle:
  - `script.dst_set_manual_override_24h`
  - `script.dst_clear_manual_override`
- Device action scripts:
  - `script.dst_ac_set_cool`
  - `script.dst_apply_fan_only_low`
  - `script.dst_ac_set_fan`
  - `script.dst_ac_set_dry`
  - `script.dst_ac_turn_off`
- Preset bridge scripts:
  - `script.dst_preset_home`
  - `script.dst_preset_away`

### Automations

- Pause button → 10h hold (`dst_pause_automation_10h`)
- Manual hold set/clear from thermostat mode change (`dst_manual_hold_on_hvac_change`)
- Preset mode bridge (`dst_on_preset_mode_changed`)
- Outdoor cool + room satisfied auto-clear manual hold (`dst_clear_manual_override_on_outdoor_cool`)

### Helpers / frontend support

- `input_datetime.ac_manual_override_until`
- `input_datetime.ac_pause_until`
- `input_boolean.ac_away_lock`
- `input_boolean.ac_fan_override`
- `input_button.ac_pause_10h`
- `homeassistant.customize` entries for switch/fan presentation

---

## Rebuild approach (right-way phased path)

## Phase 0 (now): stable baseline only

- Keep package minimal:
  - one DST climate + minimal mode scripts/switch bridge
  - no policy overlays
  - no scheduler/reconciler automations
  - no manual hold logic
- Goal: verify Tuya + DST coexistence without fighting control loops.

## Phase 1: observability only (no control side effects)

- Re-add read-only diagnostics (`ac_tuya_hvac_action`, basic reason sensor).
- No mode-forcing automations.

## Phase 2: single policy feature at a time

- Add one feature, verify for at least one cycle/daypart, then proceed.
- Candidate order:
  1) manual override hold,
  2) pause window,
  3) schedule cool request,
  4) warm+rising fan policy.

## Phase 3: optional UX helpers

- Preset bridges, helper labels, and convenience entities after control path is proven stable.

## Validation gate per phase

- Confirm DST mode transitions do not flap.
- Confirm Tuya app direct control still works and stays on.
- Confirm no duplicate conflicting automation writes for the same action window.
