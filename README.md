<!-- Description: Human-readable overview and deployment guide for the Spectra LS Home Assistant + ESPHome system. -->
<!-- Version: 2026.04.16.1 -->
<!-- Last updated: 2026-04-16 -->

# Spectra LS System

Spectra LS is a dual-MCU control and display system for whole-home audio, built around Home Assistant, ESPHome, and Music Assistant. The ESP32-S3 runs the OLED UI, Home Assistant state sync, and TCP-based audio control, while an RP2040 scans physical inputs (buttons, encoders, and pots) and publishes normalized events upstream. The goal is a resilient, low-latency hardware UX that stays stable under Home Assistant state churn and network jitter, while keeping branch-safe delivery for both active development (`main`) and stabilized control-path operation (`menu-only`).

At runtime, Home Assistant package logic resolves active room/source context and now-playing metadata, ESPHome renders and mediates user interactions, and the RP2040 provides deterministic local input capture. Key features include source-aware control targeting, menu-driven hardware control surfaces, resilient fallback handling for temporary data gaps, and branch parity controls for shared contracts (protocol/API/helper entity behavior) to avoid drift between operational branches.

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
