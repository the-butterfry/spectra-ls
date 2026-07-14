<!-- Description: Canonical pin map for Spectra parallel Amped lane and HiFi ESP32 Plus S3 wiring profile. -->
<!-- Version: 2026.07.04.2 -->
<!-- Last updated: 2026-07-04 -->

# Amped + HiFi ESP32 Plus S3 Pin Map

This document defines the canonical pin map for the current parallel combined lane:

- `esphome/spectra_ls_system_amped_combined.yaml`
- `esphome/spectra_ls_system/packages/spectra-ls-amped-bridge.yaml`

## Scope and contract

In the current implementation, the `amped_dock` profile is a backend/profile behavior switch and **not** a separate GPIO remap.

That means:

- Amped lane and HiFi ESP32 Plus S3 lane use the same active ESP pin contract in this slice.
- Active combined configs are **no-rings**; ring data pins are intentionally excluded from this map.
- If a board-specific remap is introduced later, this file must be version-bumped and updated in the same slice as firmware/substitution changes.

## ESP32-S3 pin map (Amped + HiFi profile)

| Function | ESP32-S3 Pin | Amped Lane | HiFi ESP32 Plus S3 Lane | Notes |
| --- | --- | --- | --- | --- |
| OLED I2C SDA | `GPIO8` | same | same | `oled_sda_pin` |
| OLED I2C SCL | `GPIO9` | same | same | `oled_scl_pin` |
| RP2040 UART TX (ESP -> RP) | `GPIO17` | same | same | `rp2040_uart_tx` |
| RP2040 UART RX (ESP <- RP) | `GPIO18` | same | same | `rp2040_uart_rx` |
| Arylic/HiFi UART TX (ESP -> DAC/amp) | `GPIO15` | same | same | active UART control path pin |
| Arylic/HiFi UART RX (ESP <- DAC/amp) | `GPIO16` | same | same | active UART telemetry path pin |

## RP2040 interconnect and input map (shared)

| Domain | RP2040 Side | Contract |
| --- | --- | --- |
| ESP bridge UART | `board.TX` / `board.RX` | RP -> ESP event transport |
| Input I2C bus | `board.SDA` / `board.SCL` | PCF8575 + Seesaw + ADS1015 |
| Internal analog | `A0` (active), `A1` (spare) | EQ mid + expansion |

## I2C devices and addresses (shared)

| Device | Address | Role |
| --- | --- | --- |
| PCF8575 | `0x20` or `0x21` | button expander (first detected wins) |
| Seesaw menu encoder | `0x36` | menu delta/press |
| Seesaw lighting encoder | `0x37` | lighting delta/press |
| ADS1015 | `0x48` | analog controls |

## Source-of-truth files

- ESP substitutions pin contract: `esphome/spectra_ls_system/substitutions.yaml`
- Hardware ingest package: `esphome/spectra_ls_system/packages/spectra-ls-hardware.yaml`
- Current control-board notes: `docs/notes/NOTES-control-board-2.md`
- Wiring protocol baseline: `docs/hardware/WIRING-LAYOUT-PROTOCOL.md`

## Change control requirements

If any pin assignment changes:

1. Update this file.
2. Update `docs/hardware/WIRING-LAYOUT-PROTOCOL.md`.
3. Update `docs/notes/NOTES-control-board-2.md` if operator-facing mapping changes.
4. Update `docs/CHANGELOG.md` and `esphome/CHANGELOG.md` in the same change set.
