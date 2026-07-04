<!-- Description: Universal entity-resolution plan for replacing install-specific entity IDs with contract-first resolver surfaces. -->
<!-- Version: 2026.06.22.1 -->
<!-- Last updated: 2026-06-22 -->

# Universal Entity Resolution Plan

## Goal

Remove install-specific entity dependencies from active Spectra logic by routing all runtime controls and diagnostics through discovery-first contract surfaces.

## Canonical resolver surfaces (already present)

- Player/target resolver chain:
  - `input_select.ma_active_target`
  - `sensor.ma_active_target`
  - `sensor.component_control_host`
  - `sensor.component_control_hosts`
  - `sensor.component_control_port`
- Lighting resolver chain:
  - `sensor.control_board_eligible_light_catalog` (`items_json`)
  - `input_select.control_board_room`
  - `input_select.control_board_target`
  - `sensor.control_board_target_entity_id`
- Metadata/now-playing resolver chain:
  - `sensor.component_now_playing_entity`
  - `sensor.component_now_playing_title`
  - `sensor.component_now_playing_source`
  - `binary_sensor.component_now_playing_display_allowed`

## Universal alternatives put in place in this slice

- Added reusable dynamic light action scripts in `packages/spectra_ls_lighting_hub.yaml`:
  - `script.control_board_room_lights_on`
  - `script.control_board_room_lights_off`
- Behavior:
  - Resolve entities from `sensor.control_board_eligible_light_catalog` at execution time.
  - Scope to selected room (`input_select.control_board_room`) when set.
  - Avoid any fixed light entity names in script logic.

## Policy scope clarification

- Local/operator Lovelace fixture files are not treated as active product-logic contracts for hardcode CI:
  - `esphome/spectra_ls_system/spectra_ls_ha_view.yaml`
  - `esphome/spectra_ls_system/spectra_ls_ha_view.json`
- Product logic remains enforced in:
  - `packages/**`
  - `esphome/spectra_ls_system/**` (excluding archived/fixture paths)
  - `custom_components/spectra_ls/**`

## Next migration slices

1. Migrate control-board view actions to resolver scripts (`control_board_room_lights_on/off`) instead of explicit light lists.
2. Introduce optional dynamic cards (catalog-driven) for room/target display in operator dashboards.
3. Keep CI focused on contract-bearing paths; continue reducing true install-specific literals in active runtime/component code.
