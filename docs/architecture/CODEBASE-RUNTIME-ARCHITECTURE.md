<!-- Description: Retroactive architecture and feature documentation for the active Spectra LS ESPHome runtime codebase. -->
<!-- Version: 2026.04.29.7 -->
<!-- Last updated: 2026-04-29 -->

# Spectra LS Runtime Architecture (Retroactive Baseline)

## Purpose

This document captures the **current active runtime architecture** for `esphome/spectra_ls_system` so future changes can be made against a stable, explicit baseline.

Entry point: `esphome/spectra_ls_system.yaml`

## Active include graph (source of truth)

- `substitutions.yaml`
- `spectra-ls-peripherals.yaml`
- `packages/spectra-ls-hardware.yaml`
- `packages/spectra-ls-ui.yaml`
- `packages/spectra-ls-system.yaml`
- `packages/spectra-ls-diagnostics.yaml`
- `packages/spectra-ls-audio-tcp.yaml`
- `packages/spectra-ls-lighting.yaml`

C++ local components:

- `components/arylic_tcp.h`
- `components/sls_oled_text_layout.h`
- `components/sls_menu_nav.h`
- `components/rp2040_uart`
- `components/cpu_usage`

## Runtime domains

### 1) Boot + platform domain

Owned in `spectra_ls_system.yaml`:

- ESP32-S3 + ESP-IDF setup
- Wi-Fi/API/OTA/web server
- build flags for Arylic TCP transport tuning
- on-boot sequencing:
  - target options refresh
  - splash/contrast init
  - lighting sync
  - menu/display state init

### 2) Shared-state domain

Owned in `packages/spectra-ls-system.yaml`:

- cross-package globals (menu/display/audio/meta/lighting/control-target state)
- cadence loops (heartbeat, HTTP poll hooks, screensaver watchdog)
- calibration/state bookkeeping
- base scripts (`note_user_input`, `note_menu_input`, calibration flow, status logging)
- exported ESP status text sensors include transport-safe OLED diagnostics (`esp_oled_status`) with ASCII-sanitized + bounded payloads to avoid malformed UTF-8/protobuf decode failures during telemetry updates
- ESP status text telemetry cadence is intentionally bounded at 30s for operator log clarity (`esp_control_handoff_status`, `esp_control_target`, `esp_oled_status`, `arylic_http_scheme`, `arylic_http_transport`) to avoid repeated unchanged logs
- ESP emits a dedicated 30s HA-contract metadata summary line (`ha_meta`) sourced from HA-authoritative surfaces (`ha_audio_media_class`, `ha_audio_display_allowed`, `ha_audio_state`, `ha_audio_source`, `ha_audio_app`, `ha_audio_title`) so operators can distinguish HA policy state from transport-native Arylic status lines
- `ha_meta` field provenance is now single-contract for state/source/app/title: ESP binds these to `sensor.now_playing_state`, `sensor.now_playing_source`, `sensor.now_playing_app`, and `sensor.now_playing_title` (via substitutions), preventing mixed MA-active vs now-playing cross-field context in periodic metadata logs
- `ha_meta` title rendering is fail-closed for policy coherence: title is blanked when `display_allowed=false` or media class is non-display (`none/unknown/unavailable`) to prevent stale MA title carryover in hidden-display contexts

### 3) Hardware ingest domain

Owned in `packages/spectra-ls-hardware.yaml`:

- UART transport and RP2040 hub
- reserved hardware-mode/control-class streams (`120`, `121`)
- mode nav button events (`122`–`124`)
- mode-to-screen/menu routing scripts

### 4) UI/menu domain

Owned in `packages/spectra-ls-ui.yaml` + `spectra-ls-peripherals.yaml`:

- menu state machine and menu action handlers
- encoder and button menu navigation
- dynamic options parsing for room/target/meta/control-target prompts
- display renderer (splash, menu, now-playing, EQ, lighting, blank)
- display-state decision script (`compute_display_state`)

### 5) Audio control domain (TCP-only)

Owned in `packages/spectra-ls-audio-tcp.yaml`:

- transport controls (play/pause/next/prev/source/meta select)
- volume + EQ ingest from RP2040 analog/encoder
- guarded send paths via `arylic_tcp` (prompt/host gating)
- active-playback volume unblock: volume paths may proceed during prompt state when playback is active and hosts are resolvable (still fail-closed when hosts are unresolved)
- host/port intake from HA (`sensor.ma_control_hosts`, `sensor.ma_control_port`)
- now-playing/meta resolver feed inputs
- control-target prompt lifecycle

### 6) Lighting control domain

Owned in `packages/spectra-ls-lighting.yaml`:

- room/target selection and sync with HA helpers
- slider/encoder mapping to brightness/hue/sat
- debounced light script calls (`script.control_board_set_light_dynamic`)
- toggle actions (room/selected target)
- menu-hold and resume behavior for lighting-adjust flows

### 7) Diagnostics domain

Owned in `packages/spectra-ls-diagnostics.yaml`:

- OLED contrast diagnostics and control number
- CPU/heap/PSRAM diagnostics
- CPU periodic stats logging emits every 30s for lightweight runtime health sampling during active troubleshooting
- virtual input battery harness for mode/control-path validation

## External contracts consumed by runtime

Primary HA helper/sensor contracts (via substitutions + package usage):

- target/route: `input_select.ma_active_target`, `sensor.ma_control_hosts`, `sensor.ma_control_host`, `sensor.ma_control_port`
- metadata: `sensor.ma_active_title`, `sensor.ma_active_artist`, `sensor.ma_active_album`, `sensor.ma_active_app`, `sensor.ma_active_source`, `sensor.ma_active_state`, `sensor.ma_active_duration`, `sensor.ma_active_position`, `sensor.ma_active_volume`
- candidate/override: `sensor.ma_meta_candidates`, `binary_sensor.ma_meta_low_confidence`, `input_boolean.ma_meta_override_active`, `input_text.ma_meta_override_entity`
- lighting helpers: `input_select.control_board_room`, `input_select.control_board_target`, and dynamic catalog sensors

## Feature map (user-visible)

- Hardware-first room/target/audio control surface
- OLED menu + now-playing + EQ + lighting rendering
- Audio transport via MA-selected target host(s) over Linkplay TCP
- Prompted control-target selection under ambiguity
- Dynamic lighting room/target routing with direct slider apply
- Virtual input diagnostics for mode/class/event sanity checks

## Known active constraints

- Runtime still depends on legacy helper naming (`control_board_*`) in several HA contracts.
- Direct audio routing currently supports `linkplay_tcp` path only.
- Some docs/files in this folder are archival/reference and not runtime-included (see dead-path matrix).

## Change discipline for future slices

When runtime behavior changes, update this file in the same change set with:

1. domain impact (which of the 7 domains changed),
2. contract deltas (added/removed/renamed helpers/entities),
3. migration note if legacy compatibility is affected.
