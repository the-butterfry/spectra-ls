<!-- Description: Human-readable overview and deployment guide for the Spectra LS Home Assistant + ESPHome system. -->
<!-- Version: 2026.04.16.4 -->
<!-- Last updated: 2026-04-16 -->

# Spectra LS System

Home Assistant unifies and automates devices and routines across your home; Spectra LS brings that power back into your hands as an intelligent physical control surface. With tactile knobs, smooth sliders, physical switches, dedicated buttons, and rotary dials, you can control whole-home music and lighting by touch instead of living inside phone apps.

Behind the scenes, Home Assistant manages room logic, helpers, and automation flow, while ESPHome drives the OLED UI and real-time control behavior. Input hardware feeds clean control events into that stack, so transport, source selection, volume, EQ, lighting target selection, and lighting adjustments stay quick and natural even when upstream state updates are briefly noisy.

On `main`, project direction follows `esphome/spectra_ls_system/v-next-NOTES.md`: hardware-first UX, menu as fallback, deterministic controls, and scalable room/target handling.

## System Interaction (Moderate Detail)

- **Home Assistant (`/mnt/homeassistant`)**
  - Owns automations, templates, helper entities, and package-level orchestration.
  - Exposes canonical state and control helpers consumed by ESPHome.
- **ESPHome (ESP32-S3)**
  - `main`: `esphome/spectra_ls_system.yaml` + `esphome/spectra_ls_system/`
  - `menu-only`: `esphome/control-board-esp32-tcp.yaml` + `esphome/control-py/`
  - Handles OLED rendering, API integration, and TCP control execution.
- **RP2040 (CircuitPython)**
  - Live source of truth: `CIRCUITPY/`
  - Repo mirror: `esphome/circuitpy/`
  - Reads hardware inputs and emits event stream consumed by ESPHome.

## Key Feature Points

- Stable dual-branch operations (`main` + `menu-only`) with worktree-safe workflow.
- Shared-contract parity gate for RP2040 protocol, control API, and helper/entity contracts.
- TCP-only audio control path (no UART control path unless explicitly enabled).
- Hardware-first UX: encoder/button/pot interactions remain responsive during HA update noise.
- Diagnostic/log cadence hardening to reduce publish spam and improve readability.

## Audio Clients / Player Types Spectra LS Interacts With

- **Music Assistant players** (`media_player` entities) for normalized multi-source metadata and active target context.
- **Home Assistant media players** (generic `media_player.*`) for cross-integration state/transport interoperability.
- **WiiM Audio integration players** for transport-oriented control paths in supported rooms.
- **Arylic / LinkPlay TCP endpoints** for direct low-latency control (volume, EQ, source, transport fallback).
- **AirPlay / Apple TV style sources** detected through HA/MA metadata and source-app attributes.
- **Plex sessions/players** (optional) for now-playing enrichment and local-session filtering logic.

## Deployment Guide (Detailed)

### 1) Choose target branch and workspace

1. Use `main` for spectra_ls_system development and deployment validation.
2. Use `menu-only` only for stabilized v2/control-py releases.
3. Confirm you are working from authoritative path: `/mnt/homeassistant`.

### 2) Pull latest and verify branch health

1. Pull latest changes for the branch.
2. Confirm required entrypoint exists:
   - `main`: `esphome/spectra_ls_system.yaml`
   - `menu-only`: `esphome/control-board-esp32-tcp.yaml`
3. If a shared contract changed, complete `.github/SHARED-CONTRACT-CHECKLIST.md` before deploy.

### 3) Validate ESPHome configuration

1. Validate the target entrypoint config before flashing.
2. Ensure secrets are provided via `secrets.yaml` (never commit real secrets).
3. Confirm package/include paths resolve correctly for the selected branch.

### 4) Flash / update ESP32-S3 firmware

1. Build and upload the selected ESPHome target.
2. Confirm API connection to Home Assistant after reboot.
3. Confirm OLED boot and menu rendering are healthy.

### 5) Deploy RP2040 firmware (when changed)

1. Update live `CIRCUITPY/` files first.
2. Mirror the same change into `esphome/circuitpy/` in the repo.
3. Reboot RP2040 and verify event stream is active.
4. If mirror sync is deferred, log the exact delta before closing work.

### 6) Reload Home Assistant and package state

1. Reload YAML configuration or restart Home Assistant as needed.
2. Reload affected template/automation helpers.
3. Verify key entity availability (target selectors, now-playing, control host helpers).

### 7) Post-deploy verification checklist

- Hardware controls operate without repeated prompt flapping.
- Audio control actions route to expected room/target.
- Now-playing metadata and source labels render correctly.
- Diagnostic entities update at expected cadence (no high-frequency spam).
- No errors in ESPHome logs or Home Assistant logs related to missing helpers/packages.

### 8) Rollback procedure (recommended)

1. Keep previous known-good ESPHome binary/config reference per branch.
2. If deployment regresses behavior, redeploy prior known-good branch/commit.
3. Restore previous HA package set if helper contracts changed unexpectedly.
4. Record rollback reason and follow-up action in `CHANGELOG.md`.
