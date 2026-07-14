<!-- Description: Scope, progress tracking, and execution baseline for the Spectra LS Remote standalone ESPHome project. -->
<!-- Version: 2026.07.04.3 -->
<!-- Last updated: 2026-07-04 -->

# Spectra LS Remote — Scope and Progress

## Objective

Create a new standalone ESPHome module named **Spectra LS Remote** focused on one job:

- **Single rotary encoder volume control**
- **Encoder center-press for play/pause**
- **One momentary button for next-track**

This is a new device lane and does not replace existing Spectra L/S runtime/component control-plane behavior.

Product posture: a compact, elegant **movable coffee-table control box** (not a strict handheld remote), independent from the fixed Spectra L/S main unit.

## Product definition (authoritative)

### In scope

- New ESPHome node identity: `spectra-ls-remote`
- One rotary encoder input for volume step intent
- One center-press button input for play/pause intent
- One discrete momentary button input for next-track intent
- Home Assistant integration for:
  - volume step operations
  - play/pause operations from encoder center-press
  - next-track action from momentary button (capability-gated)
- Battery-capable hardware baseline with deep sleep support
- Battery SoC telemetry via divider-based ADC measurement
- BLE-bridge-primary communication posture for low wake overhead

### Out of scope (for initial release)

- Display/OLED, menus, EQ, and transport controls beyond next-track
- Multi-room target-selection UI/logic
- Legacy control-board migration work
- Mute as a first-class MVP action (deferred unless reintroduced)

## Hardware strategy

### Development hardware (current)

- **ESP32-S3 test module** (existing available board)

### Final hardware target

- **ESP32-S3-DEVKIT-LIPO**
  - integrated charging path
  - battery-friendly deep sleep support
  - dedicated battery voltage divider path for SoC telemetry

### Input hardware

- Rotary encoder with detents
- Encoder integrated center-press (or separate push switch mapped to center action)
- Momentary push switch (toggle-form-factor acceptable; electrically momentary)

## Behavior contract

### Encoder volume path

- Read encoder detent direction and convert to bounded volume step actions
- Support optional acceleration curve (larger step at higher turn rate)
- Acceleration policy (active): slow detents use low step gain, fast detents use higher step gain
- HA helper control (active): acceleration enable/disable can be toggled live via `input_boolean.spectra_ls_remote_volume_acceleration` without reflashing
- Apply send-rate guard to avoid command storming

### Encoder center-press path

- Use digital edge from center-press input
- **Press action:** `media_player.media_play_pause` on effective target

### Next-track momentary path

- Use discrete GPIO digital edge from momentary switch
- Execute next-track only when all guardrails pass:
  - control handoff is ready (target/host resolved)
  - active target/source is transport-capable for next-track
  - source is not passthrough-input posture (`optical`, `line-in`, `aux`, `coax`, `hdmi`, `arc`)
- Apply debounce + cooldown to prevent burst spam

> Contract rule: next-track button is intent-only; fail-closed no-op is valid on unsupported source/target states.

### Communication path posture

- **Primary:** BLE to nearby always-on ESP bridge, bridge forwards to HA control contracts
- **Secondary:** Wi-Fi/API lane retained for bring-up, diagnostics, OTA, and fallback

> Contract rule: BLE-bridge path is preferred for battery-sensitive interaction loops; Wi-Fi path remains a serviceability/fallback lane.

## Battery + power model (baseline)

### Required

- LiPo charging support on final board
- Battery voltage read channel through divider
- SoC estimate surface exported to Home Assistant
- Interrupt-driven wake from encoder/button activity

### Deep sleep posture (phase-gated)

- Phase 1 (bring-up): wake-locked for rapid tuning and signal verification
- Phase 2 (battery tuning): add idle timeout + wake behavior validation
- Phase 3 (release candidate): optimize sleep intervals and wake latency trade-off

### Playback-aware awake guard (active)

- Remote deep-sleep entry is now suppressed while HA now-playing state is `playing`.
- Existing idle timeout and quiet-hours/daytime sleep policies remain in place.
- This preserves remote responsiveness during active listening sessions while still allowing aggressive battery savings when playback is idle/stopped.

### Expanded sleep profile (active)

- Post-playback linger hold: after playback leaves `playing`, remote stays awake for a bounded linger window before idle-sleep eligibility.
- Passthrough wake-lock: passthrough source postures (`optical`, `line-in`, `aux`, `coax`, `hdmi`, `arc`) suppress deep sleep while active.
- Night/day idle policy: quiet-hours uses a shorter idle threshold (more aggressive sleep), daytime uses a longer idle threshold (more forgiving wake behavior).

### Placeholder devboard no-battery mode (current)

- Development profile supports placeholder ESP32-S3 boards with **no battery installed**.
- Runtime contract for this mode:
  - `remote_has_battery=false`
  - battery telemetry surfaces are suppressed (`NaN` output) instead of exposing floating ADC noise
  - deep sleep entry is blocked regardless of idle timeout settings
- This mode is bring-up-safe and does not alter final battery-capable product contract.

### Temporary forced target mode (current bring-up)

- For current operator stabilization, remote control actions can be forced to a fixed media-player target.
- Active temporary target: `media_player.spectra_ls_2` (real Spectra host lane).
- Purpose: bypass transient HA control-hub target drift while TV/video/Plex contexts are active.
- This is a temporary bring-up override and should be reverted to dynamic target resolution after control-hub stabilization.

## ESPHome + HA integration plan

### Operational flow (separate remote config)

- Remote node runs from dedicated config: `esphome/spectra_ls_remote.yaml`
- Remote local staged build helper: `bin/esphome_spectra_remote_build_local.sh`
- Remote local staged upload helper: `bin/esphome_spectra_remote_upload_local.sh`
- Main system operational flow remains unchanged (`spectra_ls_system` helpers stay isolated)

### ESPHome entities (minimum)

- `sensor.remote_encoder_position` (internal/diagnostic)
- `binary_sensor.remote_encoder_press`
- `binary_sensor.remote_next_track_button`
- `sensor.remote_battery_voltage`
- `sensor.remote_battery_soc`

### HA contract actions

- Volume step service path (`media_player.volume_up` / `media_player.volume_down` or bounded step-set)
- Play/pause service path (`media_player.media_play_pause`) from center-press
- Next-track service path (`media_player.media_next_track`) when guardrails pass

## Milestones and status

- [ ] **M0 — Requirements lock**
  - Confirm target media player contract and entity surface
  - Confirm encoder electrical spec and switch pin map
  - Confirm BLE bridge payload contract for remote input events

- [ ] **M1 — Bench wiring + signal sanity**
  - Verify clean encoder detent decoding (CW/CCW)
  - Verify center-press and next button edges (debounced)
  - Verify bridge reachability and wake latency

- [ ] **M2 — ESPHome bring-up (`spectra-ls-remote`)**
  - New node compiles and connects
  - HA surfaces visible

- [ ] **M3 — Control behavior validation**
  - Encoder controls volume deterministically
  - Center-press controls play/pause deterministically
  - Next-track button triggers deterministic action on supported transport targets

- [ ] **M4 — Battery telemetry + deep sleep tuning**
  - Voltage + SoC validated across charge states
  - Sleep/wake profile validated for movable coffee-table usage

- [ ] **M5 — Hardware freeze and release checklist**
  - Final board migration to ESP32-S3-DEVKIT-LIPO
  - Documented acceptance test pass

## Progress log

### 2026-06-12

- Project charter created.
- Scope pivoted to encoder + center-press + momentary next-track behavior.
- Hardware direction locked: test on ESP32-S3 now, final on ESP32-S3-DEVKIT-LIPO.
- Battery-support requirement captured as first-class deliverable.
- Communication direction refined: BLE bridge primary, Wi-Fi fallback/service lane.
- Separate remote staged build/upload helper flow added for isolated operations parity.

### 2026-06-13

- Added explicit no-battery devboard safety posture to runtime/docs contracts (`remote_has_battery=false` defaults for placeholder board bring-up).
- Suppressed batteryless telemetry publish noise (no repeated `NaN` state updates in no-battery mode).
- Added unresolved-target handling improvements for remote controls: helper-target fallback to now-playing entity plus warning-rate throttling for high-frequency encoder movement.
- Added temporary forced-target override for remote action routing to `media_player.spectra_ls_2` (real Spectra control host lane).
- Corrected encoder direction by swapping default A/B pin mapping for current test hardware.

### 2026-07-04

- Added playback-aware sleep suppression: remote no longer enters deep sleep while HA now-playing contract reports `playing`.
- Sleep policy remains idle-timeout-driven outside active playback windows.
- Added adaptive detent-speed volume gain (slow/fast step policy) with live HA helper toggle (`input_boolean.spectra_ls_remote_volume_acceleration`).
- Expanded sleep behavior with playback-stop linger hold, passthrough-source wake-lock, and quiet-hours/daytime idle-threshold split.
- Live telemetry-guided responsiveness retune: increased slow/fast step gains and widened fast-turn detection window; modestly tightened encoder gate timings so practical real-world turns map to stronger volume movement.

## Decisions log

- **D-001 (superseded 2026-06-12):** Prior click-off mute contract removed from MVP in favor of encoder-center play/pause.
- **D-002 (2026-06-12):** New independent ESPHome node `spectra-ls-remote`.
- **D-003 (2026-06-12):** Final hardware baseline is ESP32-S3-DEVKIT-LIPO with charger + deep sleep + battery divider path.
- **D-004 (2026-06-12):** Add one momentary button for next-track; execute only under control-hub readiness + capability gates.
- **D-005 (2026-06-12):** Use encoder center-press for play/pause and treat volume=0 as sufficient quiet posture for MVP (no dedicated mute control).
- **D-006 (2026-06-12):** Primary comms target is BLE→bridge with Wi-Fi retained as fallback/OTA lane.

## Risks and mitigations

- **R1: Analog jitter near endpoints**
  - Mitigation: replaced by encoder detent decode and debounce validation.
- **R2: Switch bounce causing mute flapping**
  - Mitigation: hardware pull config + software debounce window for center/next buttons.
- **R3: Battery SoC inaccuracy from raw voltage-only estimate**
  - Mitigation: calibrated curve/table by chemistry and load profile.
- **R4: Deep-sleep wake latency degrades perceived responsiveness**
  - Mitigation: phase-gated sleep tuning with operator-driven latency targets.
- **R5: Next-track no-op confusion on passthrough/unsupported targets**
  - Mitigation: explicit guardrails + optional operator telemetry reason (`unsupported_source_or_target`).
- **R6: Bridge dependency creates single-point control-path failure**
  - Mitigation: keep Wi-Fi fallback lane and health telemetry for bridge availability.

## Definition of done (initial release)

- New node `spectra-ls-remote` compiles and connects reliably.
- Encoder volume behavior is stable, debounced, and rate-limited.
- Center-press play/pause behavior is deterministic.
- Next-track button behavior is deterministic on supported targets and fail-closed on unsupported postures.
- Battery voltage + SoC surfaces are available in HA.
- Deep sleep behavior is documented and validated for movable coffee-table use.
