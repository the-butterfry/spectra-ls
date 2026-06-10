<!-- Description: Detailed wiring, layout, bus, and event-contract protocol for Spectra LS hardware and RP/ESP integration. -->
<!-- Version: 2026.06.09.1 -->
<!-- Last updated: 2026-06-09 -->

# Spectra L/S Wiring + Layout Protocol (Detailed)

This is the detailed protocol reference for wiring/layout decisions, event mapping, and RP→ESP integration guardrails.

## Purpose

Use this document to keep hardware wiring, logical channel mapping, and runtime protocol behavior synchronized.

- Summary/legend view: [`docs/circuitpy/RP-LEGEND.md`](../circuitpy/RP-LEGEND.md)
- Runtime architecture map: [`docs/architecture/CODEBASE-RUNTIME-ARCHITECTURE.md`](../architecture/CODEBASE-RUNTIME-ARCHITECTURE.md)
- v-next behavior contracts: [`docs/roadmap/v-next-NOTES.md`](../roadmap/v-next-NOTES.md)

## Topology ownership model

## Bus ownership boundaries

- **RP2040 owns physical input capture** and emits canonical hardware events upstream.
- **ESP32-S3 owns UI/menu/render orchestration** and control dispatch.
- **HA package layer owns target/meta/routing resolution** surfaces consumed by ESPHome runtime.

Do not duplicate ownership across layers.

## Wiring domains and protocols

### 1) Digital input domain (PCF8575 class)

Protocol requirements:

1. Every digital input must map to a stable logical role.
2. Logical role must map to a stable event ID contract.
3. Role changes require changelog + contract note.

### 2) Encoder domain (Seesaw class)

Protocol requirements:

1. Delta signal and press signal remain separate identities.
2. Directionality policy must be centralized (single inversion point only).
3. Menu and lighting encoders cannot share ambiguous semantic mappings.

Reference paths:

- [`esphome/spectra_ls_system/components/sls_menu_nav.h`](../../esphome/spectra_ls_system/components/sls_menu_nav.h)
- [`esphome/spectra_ls_system/packages/spectra-ls-ui.yaml`](../../esphome/spectra_ls_system/packages/spectra-ls-ui.yaml)

### 3) Analog domain (ADS1015/internal ADC class)

Protocol requirements:

1. Channel maps must be explicitly documented and versioned.
2. Calibration/application logic remains in RP runtime modules.
3. Analog-to-event conversion must preserve range semantics at edges.

Reference paths:

- [`esphome/circuitpy/sls_analog.py`](../../esphome/circuitpy/sls_analog.py)
- [`esphome/circuitpy/sls_calibration.py`](../../esphome/circuitpy/sls_calibration.py)
- [`esphome/circuitpy/sls_calibration_runtime.py`](../../esphome/circuitpy/sls_calibration_runtime.py)

### 4) RP→ESP transport domain (UART framing)

Protocol requirements:

1. Packet type and event ID semantics are treated as API contracts.
2. Framing updates require explicit migration notes and dual-side validation.
3. Parser tolerance should not silently reinterpret semantic IDs.

Reference paths:

- [`esphome/circuitpy/sls_protocol.py`](../../esphome/circuitpy/sls_protocol.py)
- [`esphome/spectra_ls_system/components/rp2040_uart`](../../esphome/spectra_ls_system/components/rp2040_uart)
- [`esphome/spectra_ls_system/packages/spectra-ls-hardware.yaml`](../../esphome/spectra_ls_system/packages/spectra-ls-hardware.yaml)

## Layout protocol (physical controls)

## Control grouping rules

- Group by user intent first (navigation, lighting, audio, mode selectors).
- Keep frequently paired actions physically adjacent.
- Avoid multi-purpose controls that require hidden mode memory.

## Labeling rules

- Physical labels and logical role names must align exactly.
- If a role changes, update both label reference docs and event maps.

## Expansion rules

- Expansion channels are allowed only when:
  1. bus addressing is collision-checked,
  2. event ID ranges are conflict-checked,
  3. diagnostics templates are updated.

## Control alignment findings (2026-06-09 sweep)

These are active documentation/contract watch-items for upcoming analog expansion:

1. **Mirrored mode-nav overlaps on shared physical buttons**

- RP emits mode-nav IDs (`122/123/124`) by mirroring `next/back/select` in addition to canonical button IDs.
- In `hardware_mode_system_meta`, this can create dual semantic effects if base handlers and mode handlers are both active.
- Expansion rule: when introducing new mode classes or analog-triggered mode transitions, explicitly gate shared-button semantics by mode.

1. **Meta-select button contract requires explicit RP emit validation**

- ESP runtime expects `${meta_select_button_id}` (`40`) for `RP Meta Select`.
- RP mirror mapping currently documents canonical button IDs from `BUTTON_EVENT_IDS` plus mode-nav mirrors.
- Expansion rule: treat `40` as provisional until RP-side emit path is explicitly confirmed in source and hardware validation.

1. **Selector detents 2/3 are reserved but behavior-collapsed today**

- Substitutions define `hardware_mode_audio_targets=2` and `hardware_mode_audio_transport=3`.
- Active runtime mode application currently provides distinct branches for `0/1/4` and falls through to general audio/default behavior otherwise.
- Expansion rule: do not assign user-facing unique analog roles to detents 2/3 without implementing and validating distinct runtime branches.

## Hyperlinked component detail index

### Runtime and protocol

- Runtime architecture baseline: [`docs/architecture/CODEBASE-RUNTIME-ARCHITECTURE.md`](../architecture/CODEBASE-RUNTIME-ARCHITECTURE.md)
- Control-hub architecture baseline: [`docs/architecture/CONTROL-HUB-ARCHITECTURE.md`](../architecture/CONTROL-HUB-ARCHITECTURE.md)
- v-next roadmap contracts: [`docs/roadmap/v-next-NOTES.md`](../roadmap/v-next-NOTES.md)

### Firmware + runtime files

- RP legend + ownership map: [`docs/circuitpy/RP-LEGEND.md`](../circuitpy/RP-LEGEND.md)
- RP transport component: [`esphome/spectra_ls_system/components/rp2040_uart`](../../esphome/spectra_ls_system/components/rp2040_uart)
- Hardware ingest package: [`esphome/spectra_ls_system/packages/spectra-ls-hardware.yaml`](../../esphome/spectra_ls_system/packages/spectra-ls-hardware.yaml)
- UI package: [`esphome/spectra_ls_system/packages/spectra-ls-ui.yaml`](../../esphome/spectra_ls_system/packages/spectra-ls-ui.yaml)
- Lighting package: [`esphome/spectra_ls_system/packages/spectra-ls-lighting.yaml`](../../esphome/spectra_ls_system/packages/spectra-ls-lighting.yaml)
- Audio TCP package: [`esphome/spectra_ls_system/packages/spectra-ls-audio-tcp.yaml`](../../esphome/spectra_ls_system/packages/spectra-ls-audio-tcp.yaml)

### External component references

- [PCF8575](https://www.nxp.com/products/interfaces/ic-spi-i3c-interface-devices/general-purpose-i-o-gpio/remote-16-bit-i-o-expander-for-ic-bus:PCF8575)
- [Seesaw](https://learn.adafruit.com/adafruit-seesaw-atsamd09-breakout/overview)
- [ADS1015](https://www.ti.com/product/ADS1015)
- [ADS7830](https://www.ti.com/product/ADS7830)
- [ESP32-S3](https://www.espressif.com/en/products/socs/esp32-s3)
- [RP2040](https://www.raspberrypi.com/products/rp2040/)

## Change protocol (required)

When wiring/layout/event contracts change:

1. Update this file ([`docs/hardware/WIRING-LAYOUT-PROTOCOL.md`](./WIRING-LAYOUT-PROTOCOL.md)).
2. Update [`docs/circuitpy/RP-LEGEND.md`](../circuitpy/RP-LEGEND.md) summary links/contracts.
3. Update affected architecture/roadmap docs as needed.
4. Update [`docs/CHANGELOG.md`](../CHANGELOG.md).
5. Record whether `README.md` parity is required or no material change.

## Acceptance checklist

- [ ] Wiring/layout intent and ownership are unambiguous.
- [ ] Event IDs/channels have no collisions.
- [ ] RP capture and ESP ingest paths are both updated and verified.
- [ ] Diagnostics templates cover new/changed pathways.
- [ ] Changelog + parity docs updated in same change set.
