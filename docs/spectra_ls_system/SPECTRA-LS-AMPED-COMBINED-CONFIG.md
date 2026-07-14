<!-- Description: Extensive operator/developer guide for the parallel Spectra + Amped combined ESPHome config lane. -->
<!-- Version: 2026.07.04.2 -->
<!-- Last updated: 2026-07-04 -->

# Spectra LS Amped Combined Config Guide

This page documents the new **parallel combined ESPHome lane**:

- Entrypoint: `esphome/spectra_ls_system_amped_combined.yaml`
- Bridge overlay: `esphome/spectra_ls_system/packages/spectra-ls-amped-bridge.yaml`

The goal is to run a phased Amped integration track **without replacing** the current baseline runtime.

## Why this config exists

The project now maintains two lanes in parallel:

1. **Current baseline runtime** (stable compatibility lane)
   - `esphome/spectra_ls_system.yaml`
2. **Combined Amped track** (additive migration lane)
   - `esphome/spectra_ls_system_amped_combined.yaml`

This keeps development reversible and lets you validate hardware/backend assumptions safely.

## Design posture and guarantees

The combined lane is intentionally conservative:

- It imports the full current baseline runtime as-is.
- It overlays only a small bridge package for profile control and phased behavior toggles.
- It uses a separate node identity (`spectra-ls-system-amped`) to avoid accidentally clobbering the main node.
- It does **not** force immediate ownership or route-path cutover.

## File map

- `esphome/spectra_ls_system_amped_combined.yaml`
  - parallel entrypoint
  - profile marker substitution (`combined_profile_name`)
  - imports baseline + bridge package
- `esphome/spectra_ls_system/packages/spectra-ls-amped-bridge.yaml`
  - backend profile selector
  - bridge-mode boolean state
  - apply script + profile-status text sensor

## Pin map for Amped + HiFi ESP32 Plus S3

Canonical wiring reference for this combined lane:

- `docs/hardware/AMPED-HIFI-ESP32-PLUS-S3-PIN-MAP.md`

Important in this phase:

- `amped_dock` is currently a backend/profile mode switch.
- It does not currently redefine ESP32 GPIO assignment.
- Active pin contracts remain those from `esphome/spectra_ls_system/substitutions.yaml`.

## Backend profile contract

The combined bridge package currently exposes two profile modes:

- `spectra_arylic`
- `amped_dock`

Behavior today:

- `spectra_arylic` = baseline-compatible posture
- `amped_dock` = phased bridge posture (hook enabled, no forced deep replacement)

This is intentional: profile switching is available now, while hard hardware-path cutover remains a controlled follow-up slice.

## How to use this lane

1. Keep `esphome/spectra_ls_system.yaml` untouched as your baseline lane.
2. Build/deploy from `esphome/spectra_ls_system_amped_combined.yaml` only when testing the combined lane.
3. Validate route/control/OLED behavior independently before any migration decisions.

## Validation checklist (combined lane)

Minimum pass criteria:

- config compiles cleanly
- OTA/build target identity is `spectra-ls-system-amped`
- HA entities register without schema errors
- profile selector flips between `spectra_arylic` and `amped_dock`
- status sensor reflects selected profile

Recommended additional checks:

- room/target options still populate
- control-host feed remains deterministic
- no regression in OLED state transitions
- no degradation in RP2040 input/menu responsiveness

## Rollback and safety

Rollback is immediate by design:

- Stop using the combined entrypoint.
- Continue with baseline `esphome/spectra_ls_system.yaml`.

Because this lane is additive and identity-isolated, rollback does not require path surgery.

## What this guide is not

This page does **not** declare a full Amped hardware pin-map cutover complete.

It documents the current parallel integration foundation so future Amped slices can be executed with clear boundaries, predictable diagnostics, and changelog traceability.

## Related references

- Main changelog: `docs/CHANGELOG.md`
- ESP-specific changelog: `esphome/CHANGELOG.md`
- Baseline runtime entrypoint: `esphome/spectra_ls_system.yaml`
- Combined entrypoint: `esphome/spectra_ls_system_amped_combined.yaml`
