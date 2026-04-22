<!-- Description: Operator-facing control-surface reference for Spectra inputs, buttons, sliders/pots, encoders, expanders, and event path. -->
<!-- Version: 2026.04.22.1 -->
<!-- Last updated: 2026-04-22 -->

# Control Surface Inputs, Buttons, Sliders, and Expanders

This page is the practical “where are all the controls?” index.

Quick links:

- Wiring protocol: `docs/hardware/WIRING-LAYOUT-PROTOCOL.md`
- RP legend: `docs/circuitpy/RP-LEGEND.md`
- RP source config: `esphome/circuitpy/sls_config.py`
- RP runtime input code: `esphome/circuitpy/code.py`

## Hardware input stack at a glance

- **RP2040** captures physical inputs.
- **PCF8575** expanders provide digital button/selector inputs.
- **Seesaw encoders** provide rotary delta + press events.
- **ADS1015 + internal ADC** provide analog slider/pot values.
- **UART transport** carries RP events to ESPHome runtime.

## Digital buttons (PCF8575 path)

Current canonical button pin map from `esphome/circuitpy/sls_config.py`:

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

## Selectors and mode/class controls (PCF8575 path)

- **Mode selector event**: `120`
- **Control-class selector event**: `121`
- **Mode navigation events**:
  - next item: `122`
  - previous item: `123`
  - confirm: `124`

Selector pin contracts are defined in `esphome/circuitpy/sls_config.py`:

- mode selector pins: `9..13` (one-hot)
- control class pins: `14..15` (mapped combinations)

## Rotary encoders (Seesaw path)

Current encoder map from `esphome/circuitpy/code.py`:

| Encoder | I2C address | Delta event ID | Press event ID |
| --- | ---: | ---: | ---: |
| menu | `0x36` | 2 | 21 |
| lighting | `0x37` | 1 | 20 |

## Sliders and pots (analog path)

Current analog input map from `esphome/circuitpy/code.py`:

| Control | Source | Channel/Pin | Event ID |
| --- | --- | --- | ---: |
| lighting slider | external ADC | ADS channel 1 | 101 |
| volume pot | external ADC | ADS channel 2 | 102 |
| EQ bass pot | external ADC | ADS channel 0 | 104 |
| EQ mid pot | internal ADC | `board.A0` | 105 |
| EQ treble pot | external ADC | ADS channel 3 | 106 |

## Expanders and buses

- PCF8575 addresses (digital inputs): `0x20`, `0x21`
- Seesaw encoder addresses: `0x36`, `0x37`
- External ADS1015 ADC address: `0x48`

## Event path (end-to-end)

1. Physical input changes at control surface.
2. RP2040 reads digital/encoder/analog values.
3. RP normalizes and emits event packets.
4. ESPHome runtime ingests packets via `rp2040_uart`.
5. UI/audio/lighting/runtime packages apply behavior in HA context.

## Source-of-truth files

- RP event/pin map: `esphome/circuitpy/sls_config.py`
- RP runtime input config: `esphome/circuitpy/code.py`
- Detailed wiring protocol: `docs/hardware/WIRING-LAYOUT-PROTOCOL.md`
- RP legend + ownership: `docs/circuitpy/RP-LEGEND.md`
- Runtime architecture map: `docs/architecture/CODEBASE-RUNTIME-ARCHITECTURE.md`

## Change discipline

When input mappings or event IDs change:

1. Update RP source-of-truth files.
2. Update wiring/legend docs.
3. Update this wiki page.
4. Record contract deltas in `docs/CHANGELOG.md`.
