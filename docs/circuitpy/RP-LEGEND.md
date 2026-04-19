<!-- Description: RP2040 firmware module legend, wiring/layout protocol, and component-link map for Spectra LS. -->
<!-- Version: 2026.04.19.1 -->
<!-- Last updated: 2026-04-19 -->

# RP2040 Firmware Legend (Spectra LS)

This document is the authoritative RP2040 module map plus wiring/layout protocol index for firmware in `CIRCUITPY` and mirror `esphome/circuitpy`.

## Quick links to fine details

- Wiring/layout protocol (deep detail): [`docs/hardware/WIRING-LAYOUT-PROTOCOL.md`](../hardware/WIRING-LAYOUT-PROTOCOL.md)
- Runtime architecture baseline: [`docs/architecture/CODEBASE-RUNTIME-ARCHITECTURE.md`](../architecture/CODEBASE-RUNTIME-ARCHITECTURE.md)
- Control-hub architecture baseline: [`docs/architecture/CONTROL-HUB-ARCHITECTURE.md`](../architecture/CONTROL-HUB-ARCHITECTURE.md)
- v-next control contracts: [`docs/roadmap/v-next-NOTES.md`](../roadmap/v-next-NOTES.md)

### Component-level references

- RP transport component: [`esphome/spectra_ls_system/components/rp2040_uart`](../../esphome/spectra_ls_system/components/rp2040_uart)
- OLED text layout helper: [`esphome/spectra_ls_system/components/sls_oled_text_layout.h`](../../esphome/spectra_ls_system/components/sls_oled_text_layout.h)
- Shared menu navigation helper: [`esphome/spectra_ls_system/components/sls_menu_nav.h`](../../esphome/spectra_ls_system/components/sls_menu_nav.h)
- Hardware ingest package: [`esphome/spectra_ls_system/packages/spectra-ls-hardware.yaml`](../../esphome/spectra_ls_system/packages/spectra-ls-hardware.yaml)
- UI package: [`esphome/spectra_ls_system/packages/spectra-ls-ui.yaml`](../../esphome/spectra_ls_system/packages/spectra-ls-ui.yaml)

## Source-of-truth + sync rule

- Live runtime source: `CIRCUITPY/`.
- Repository mirror: `esphome/circuitpy/`.
- Any RP firmware change must update both in the same change set.

## Wiring/layout protocol summary (directive)

1. **Single-bus ownership:** one owner per hardware bus segment; no duplicate bus-role definitions across modules.
2. **Stable event contract:** input wiring changes must preserve event ID semantics unless a migration note is published in `docs/CHANGELOG.md`.
3. **Deterministic mode routing:** selector and control-class wiring must map to explicit runtime branches in hardware mode scripts.
4. **Guarded expansion:** new expanders/channels are allowed only with updated channel map, collision checks, and diagnostics template updates.
5. **Parity update required:** any wiring/layout protocol edit must update both this legend and `docs/hardware/WIRING-LAYOUT-PROTOCOL.md` in the same change set.

For full protocol details, constraints, and acceptance gates, use:

- [`docs/hardware/WIRING-LAYOUT-PROTOCOL.md`](../hardware/WIRING-LAYOUT-PROTOCOL.md)

## File ownership contract

### `boot.py`

- USB/runtime boot toggles only.
- No input scanning, no protocol logic, no calibration logic.

### `code.py`

- Main orchestrator only.
- Hardware init (I2C devices, ADC setup, encoder setup).
- Main loop ordering and high-level flow control.
- Delegates details to `sls_*` modules.

### `sls_config.py`

- Constants + event/pin maps only.
- No hardware calls.
- No mutable runtime state.

Contains the canonical event/channel/pin identity map. Any logical rewiring must be reflected here first.

### `sls_protocol.py`

- UART packet wire format + buffered writer.
- No hardware scan/decoder behavior.
- Packet framing changes require explicit protocol review.

Wire-contract anchor for RP→ESP packet semantics.

### `sls_inputs_pcf.py`

- PCF8575 input setup and selector decode helpers.
- No UART emission and no protocol policy.

### `sls_analog.py`

- Analog math/helpers only (read/scale/name helpers).
- No calibration persistence or trigger state.

### `sls_calibration.py`

- Calibration load/save/apply utility functions.
- No hardware reads and no loop orchestration.

### `sls_calibration_runtime.py`

- Autocalibration/tracking runtime state machine.
- Consumes sampled values + time from `code.py`.
- No direct hardware reads and no packet emission.

## Runtime pipeline (RP -> ESP)

1. Acquire hardware input (buttons/encoders/analog) in `code.py`.
2. Normalize/decode via `sls_inputs_pcf.py` and `sls_analog.py`.
3. Resolve calibration/runtime state via `sls_calibration.py` + `sls_calibration_runtime.py`.
4. Emit framed events via `sls_protocol.py`.

## Wiring change acceptance checklist

- [ ] Bus topology impact documented in `docs/hardware/WIRING-LAYOUT-PROTOCOL.md`.
- [ ] Event/channel map updates documented in `sls_config.py` notes and changelog.
- [ ] RP + ESP ingest parity verified (`rp2040_uart` decode + hardware package handlers).
- [ ] Diagnostics template coverage updated (if new event IDs/channels are introduced).
- [ ] No ambiguity in selector/control-class path behavior after reboot.

## Guardrails for edits

- Keep packet IDs/types stable unless explicitly approved.
- Prefer reusable helper functions over duplicated edge/log code.
- Keep hot loop lean: avoid unnecessary allocations/lookups.
- Do not move responsibilities across files without updating this legend.
