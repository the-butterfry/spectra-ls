<!-- Description: Control-plane architecture reference for Spectra L/S integration-first operation. -->
<!-- Version: 2026.08.01.1 -->
<!-- Last updated: 2026-08-01 -->

# Control Plane Architecture

## Purpose

Describe the active control-plane contracts for Spectra L/S with integration-owned authority and runtime consumers bound to integration surfaces.

## Active ownership model

- Authority owner: `custom_components/spectra_ls`
- Runtime role: consume integration-published contracts and execute device I/O paths
- Control center services: `spectra_ls.execute_control_center_input`, `spectra_ls.set_control_center_settings`
- Validation services: `spectra_ls.validate_contracts`, `spectra_ls.dump_route_trace`, `spectra_ls.validate_scheduler`

## Core contract surfaces

- Active target: `sensor.component_active_target`
- Control host(s):
  - `sensor.component_control_host`
  - `sensor.component_control_hosts`
  - `sensor.component_control_port`
- Now-playing:
  - `sensor.component_now_playing_entity`
  - `sensor.component_now_playing_state`
  - `sensor.component_now_playing_title`
  - `sensor.component_now_playing_artist`
  - `sensor.component_now_playing_source`
  - `sensor.component_now_playing_freshness_age`
  - `binary_sensor.component_now_playing_display_allowed`

## Runtime consumption rules

- Runtime routing and metadata reads must bind to component contract entities.
- Host resolution is discovery-first and fail-closed.
- No install-specific target IP defaults in tracked product logic.
- Active-path validation should use component diagnostics packets and route traces.

## Operational verification

Use these proofs for control-plane health checks:

- `sensor.shadow_active_target` packet freshness + contract validity
- `route_trace` decision + active target coherence
- Scheduler verdict and cutover gate readiness
- ESP handoff + OLED status telemetry consistency

## Documentation parity rule

When control-plane behavior or ownership changes:

1. Update this architecture document.
2. Update `docs/CHANGELOG.md`.
3. Update roadmap status in `docs/roadmap/v-next-NOTES.md`.
4. Update user-facing docs when operator behavior changes.
