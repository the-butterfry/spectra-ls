<!-- Description: Operator-facing control-surface reference for Spectra inputs, buttons, sliders/pots, encoders, expanders, and event path. -->
<!-- Version: 2026.08.01.3 -->
<!-- Last updated: 2026-08-01 -->

# Control Surface Inputs, Buttons, Sliders, and Expanders

This is the hardware/input map you use when buttons or knobs do the wrong thing.

Quick links:

- Wiring protocol: [`docs/hardware/WIRING-LAYOUT-PROTOCOL.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/hardware/WIRING-LAYOUT-PROTOCOL.md)
- RP legend: [`docs/circuitpy/RP-LEGEND.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/circuitpy/RP-LEGEND.md)
- RP source config: [`esphome/circuitpy/sls_config.py`](https://github.com/the-butterfry/spectra-ls/blob/main/esphome/circuitpy/sls_config.py)
- RP runtime input code: [`esphome/circuitpy/code.py`](https://github.com/the-butterfry/spectra-ls/blob/main/esphome/circuitpy/code.py)

## Signal path (30-second mental model)

1. Physical control changes
2. RP2040 reads it
3. RP2040 emits event packet
4. ESPHome `rp2040_uart` ingests packet
5. HA/runtime/component logic applies behavior

## Digital buttons (PCF8575)

Canonical map from [`esphome/circuitpy/sls_config.py`](https://github.com/the-butterfry/spectra-ls/blob/main/esphome/circuitpy/sls_config.py):

| Button | PCF pin | Event ID |
| --- | ---: | ---: |
| room | 0 | 31 |
| source | 1 | 35 |
| back | 2 | 36 |
| home | 3 | _(reserved/no mapped event in current config)_ |
| prev | 4 | 34 |
| play | 5 | 32 |
| next | 6 | 33 |
| mute | 7 | 22 |
| select | 8 | 37 |

## Selector and mode controls

- **Mode selector event**: `120`
- **Control-class selector event**: `121`
- **Mode navigation events**:
  - next item: `122`
  - previous item: `123`
  - confirm: `124`

Selector pin contracts are defined in [`esphome/circuitpy/sls_config.py`](https://github.com/the-butterfry/spectra-ls/blob/main/esphome/circuitpy/sls_config.py):

- mode selector pins: `9..13` (one-hot)
- control class pins: `14..15` (mapped combinations)

## Rotary encoders (Seesaw)

Current map from [`esphome/circuitpy/code.py`](https://github.com/the-butterfry/spectra-ls/blob/main/esphome/circuitpy/code.py):

| Encoder | I2C address | Delta event ID | Press event ID |
| --- | ---: | ---: | ---: |
| menu | `0x36` | 2 | 21 |
| lighting | `0x37` | 1 | 20 |

## Sliders and pots (analog)

Current map from [`esphome/circuitpy/code.py`](https://github.com/the-butterfry/spectra-ls/blob/main/esphome/circuitpy/code.py):

| Control | Source | Channel/Pin | Event ID |
| --- | --- | --- | ---: |
| lighting slider | external ADC | ADS channel 1 | 101 |
| volume pot | external ADC | ADS channel 2 | 102 |
| EQ bass pot | external ADC | ADS channel 0 | 104 |
| EQ mid pot | internal ADC | `board.A0` | 105 |
| EQ treble pot | external ADC | ADS channel 3 | 106 |

## I2C addresses quick reference

- PCF8575 addresses (digital inputs): `0x20`, `0x21`
- Seesaw encoder addresses: `0x36`, `0x37`
- External ADS1015 ADC address: `0x48`

## Troubleshooting quick checks

| Symptom | First check | Next action |
| --- | --- | --- |
| Button press does nothing | Event ID map for that button | Confirm packet appears in RP/ESP logs and route mapping consumes it |
| Encoder rotates backward or jumps | Encoder address + delta event map | Verify Seesaw address wiring and event mapping in `code.py` |
| Slider behavior is noisy/stuck | ADS/internal ADC channel mapping | Validate channel-to-event mapping and analog calibration |

## Source-of-truth files

- RP event/pin map: [`esphome/circuitpy/sls_config.py`](https://github.com/the-butterfry/spectra-ls/blob/main/esphome/circuitpy/sls_config.py)
- RP runtime input config: [`esphome/circuitpy/code.py`](https://github.com/the-butterfry/spectra-ls/blob/main/esphome/circuitpy/code.py)
- Detailed wiring protocol: [`docs/hardware/WIRING-LAYOUT-PROTOCOL.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/hardware/WIRING-LAYOUT-PROTOCOL.md)
- RP legend + ownership: [`docs/circuitpy/RP-LEGEND.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/circuitpy/RP-LEGEND.md)
- Runtime architecture map: [`docs/architecture/CODEBASE-RUNTIME-ARCHITECTURE.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/architecture/CODEBASE-RUNTIME-ARCHITECTURE.md)

## Change discipline

When input mappings or event IDs change:

1. Update RP source-of-truth files.
2. Update wiring/legend docs.
3. Update this wiki page.
4. Record contract deltas in [`docs/CHANGELOG.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/CHANGELOG.md).
