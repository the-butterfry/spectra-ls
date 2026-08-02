<!-- Description: End-user overview for the Spectra L/S Home Assistant + ESPHome system. -->
<!-- Version: 2026.08.01.6 -->
<!-- Last updated: 2026-08-01 -->

# Spectra L/S

**⚠️ State of project (reviewed 2026-08-01): Public beta. It works today, but it still changes quickly. If you want "set it once and never touch it," wait for a stable milestone.**

## What is Spectra L/S?

Spectra L/S is a **physical control board for Home Assistant**.

Think of it like a **home DJ mixer for music + lights**:

- turn a knob for volume,
- press a button for playback,
- switch rooms/targets quickly,
- see what’s happening on the OLED.

It exists to make home control feel instant and tactile, instead of app-heavy and slow.

## What you can do with it today

- Control playback (play/pause, next, volume)
- Control room lighting
- Switch targets/rooms with physical controls
- See live context/status on the onboard OLED
- Route actions through Home Assistant services and automations

## Who this is for right now

- You already run Home Assistant (or are comfortable learning it)
- You want a premium physical interface for audio + home control
- You’re okay with a beta product that still evolves quickly

## What this is not (yet)

- Not a mass-market plug-and-play consumer product yet
- Not frozen/stable enterprise software yet
- Not "no-maintenance forever" if you follow `main`

## Complete hardware list (current)

### Main Spectra L/S unit (active build)

- **ESP32-S3 dev board** (`esp32-s3-devkitc-1` in active firmware)
- **RP2040 board** for physical input capture (buttons/encoders/pots)
- **I2C OLED display** (SSD1306 128x64, SSD1309-compatible, address `0x3C`)

### Audio endpoint hardware (what Spectra controls)

- **WiiM devices**
- **Arylic / LinkPlay-class devices** (TCP control, port `8899`)

### Optional remote lane (active project, additive)

- **ESP32-S3 remote node**
- Current target board: **ESP32-S3-DEVKIT-LIPO**
- Encoder + buttons (play/pause, next-track flow)

### Maintainer note

- When hardware changes, update this list **in the same change set** as the hardware/firmware change.
- Also add the hardware-list update note to `docs/CHANGELOG.md` in that same slice.

Home Assistant ties these hardware pieces together so physical actions map cleanly to your home.

Inspired by premium physical control products like [Condesa Electronics — Carmen SE](https://condesaelectronics.com/) and [Varia Instruments — RDM series](https://www.varia-instruments.com/), Spectra L/S brings that tactile philosophy to Home Assistant.

## Works with the Audio Ecosystem You Already Have

- Music Assistant players
- Home Assistant media players
- WiiM-based rooms
- Arylic/LinkPlay-class endpoints
- Sendspin-class endpoints (roadmap target)
- AirPlay / Apple TV style sources
- Plex sessions/players (optional)

## What’s being built now

- A polished in-app Home Assistant control center
- Better onboarding/setup flow for real homes with different device layouts
- Stronger playback and metadata reliability across mixed audio ecosystems
- Faster and cleaner input-to-action response from physical controls

If you want the deep implementation/roadmap details, see:

- `docs/roadmap/v-next-NOTES.md`
- `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`
- `docs/architecture/`

## Compatibility baseline (verified vs expected)

This section reflects an evidence-first compatibility audit against current upstream release notes plus local code-surface checks. It is intentionally conservative:

- **Verified up to (audit baseline):**
  - Home Assistant Core: **2026.6.4**
  - Home Assistant OS: **18.0**
  - ESPHome: **2026.6.2**
  - ESPHome add-on: **2026.6.2**
  - ESPHome Device Builder backend: **1.0.12**
  - ESPHome Device Builder frontend: **0.1.174**

- **What “verified” means in this context:**
  - Upstream changelog/release deltas were reviewed and compared to current Spectra runtime + component contract surfaces.
  - No blocking incompatibilities were identified in the current static code/config surface.

- **Expected (pending live soak confirmation):**
  - Build/deploy/runtime behavior remains expected-compatible on the versions above, but should still be confirmed with live compile + runtime validation evidence for each environment.

- **Known watch items:**
  - BLE scanning default changes in HA/ESPHome may affect operational behavior on `bluetooth_proxy` nodes; treat as an operational tuning watchpoint.
  - Compatibility statements here are contract-surface/audit based, not a blanket guarantee for every custom deployment topology.

## Spectra LS Remote (new additive lane)

- A new standalone ESPHome node (`spectra-ls-remote`) is being introduced as a **movable coffee-table control box**.
- Current input model is encoder-first: rotary volume step control + encoder center-press play/pause + dedicated momentary next-track button.
- Power direction is battery-aware by design (final target board: ESP32-S3-DEVKIT-LIPO with charging + deep-sleep + battery telemetry).
- Communication direction is BLE-bridge-primary for low wake overhead, with Wi-Fi retained as secondary OTA/service lane.
- Scope/progress source of truth: `docs/program/SPECTRA-LS-REMOTE-SCOPE-PROGRESS.md`.
- Separate local operations helpers:
  - build: `bin/esphome_spectra_remote_build_local.sh`
  - upload: `bin/esphome_spectra_remote_upload_local.sh`

## Documentation

Start here for setup, operations, and development workflow:

- [`docs/README.md`](docs/README.md)

Common entry points:

- Setup placeholders: [`docs/setup/SPECTRA-HA-CONFIG-PLACEHOLDERS.md`](docs/setup/SPECTRA-HA-CONFIG-PLACEHOLDERS.md)
- Latest project changes: [`docs/CHANGELOG.md`](docs/CHANGELOG.md)
- Parallel Amped integration entrypoint (additive, current runtime preserved): [`esphome/spectra_ls_system_amped_combined.yaml`](esphome/spectra_ls_system_amped_combined.yaml)
- Developer onboarding/runbook: [`docs/developer/DEVELOPER-INSTRUCTIONS.md`](docs/developer/DEVELOPER-INSTRUCTIONS.md)
- WLED palette room E2E test runbook: [`docs/testing/raw/wled_palette_room_e2e_runbook.md`](docs/testing/raw/wled_palette_room_e2e_runbook.md)

Need current execution status? Use [`docs/roadmap/v-next-NOTES.md`](docs/roadmap/v-next-NOTES.md).

Need migration mechanics and slice evidence? Use:

- [`docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`](docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md)
- [`docs/testing/raw/`](docs/testing/raw/)

Need wiki navigation? Start at [`docs/wiki/Home.md`](docs/wiki/Home.md).

## Reader journey (start in 60 seconds)

- **I want to install and run Spectra** → [`docs/wiki/Install-on-Your-Own-HA.md`](docs/wiki/Install-on-Your-Own-HA.md)
- **I already installed and need setup/deploy verification** → [`docs/wiki/User-Setup-Deploy-and-HA-Integration.md`](docs/wiki/User-Setup-Deploy-and-HA-Integration.md)
- **Something broke and I need the right bug path** → [`docs/wiki/Welcome-README-and-Bug-Workflow.md`](docs/wiki/Welcome-README-and-Bug-Workflow.md)
- **I’m contributing code/docs** → [`docs/wiki/Contributing-Workflow.md`](docs/wiki/Contributing-Workflow.md)
