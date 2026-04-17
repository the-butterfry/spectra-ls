<!-- Description: RP2040 firmware module legend and ownership map for Spectra LS. -->
<!-- Version: 2026.04.17.2 -->
<!-- Last updated: 2026-04-17 -->

# RP2040 Firmware Legend (Spectra LS)

This document is the authoritative module map for RP firmware in `CIRCUITPY` and mirror `esphome/circuitpy`.

## Source-of-truth + sync rule

- Live runtime source: `CIRCUITPY/`.
- Repository mirror: `esphome/circuitpy/`.
- Any RP firmware change must update both in the same change set.

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

### `sls_protocol.py`

- UART packet wire format + buffered writer.
- No hardware scan/decoder behavior.
- Packet framing changes require explicit protocol review.

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

## Guardrails for edits

- Keep packet IDs/types stable unless explicitly approved.
- Prefer reusable helper functions over duplicated edge/log code.
- Keep hot loop lean: avoid unnecessary allocations/lookups.
- Do not move responsibilities across files without updating this legend.
