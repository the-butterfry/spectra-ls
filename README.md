<!-- Description: Human-readable overview and deployment guide for the Spectra Level / Source (Spectra L/S) Home Assistant + ESPHome system. -->
<!-- Version: 2026.04.17.25 -->
<!-- Last updated: 2026-04-17 -->

# Spectra Level / Source

**⚠️ State of project (published 2026-04-16): Active heavy development on `main`. Not currently recommended for fresh production installations unless you are comfortable with frequent updates and occasional migration adjustments.**

[Home Assistant](https://www.home-assistant.io/) unifies and automates devices and routines across your home; Spectra Level / Source (Spectra L/S) brings that power back into your hands as an intelligent physical control surface. With tactile knobs, smooth sliders, physical switches, dedicated buttons, and rotary dials, direct analog inputs drive Volume and Physical 3-Band EQ control for everything from everyday listening to a home dance party.

This is the point: Spectra L/S lets you run your home audio and lighting like an instrument, not an app screen. Hit Play/Pause, jump Next/Back, shape tone, move brightness, and switch rooms in seconds from the coffee table while the OLED keeps every move clear and immediate.

Behind the scenes, Home Assistant manages room logic, helpers, and automation flow, while ESPHome drives the OLED UI and real-time control behavior. In v-next, multiple switches and dials expand functionality while keeping the interface simple and clear, and the screen stays responsive to inputs with visual menu feedback as you navigate. If Home Assistant already knows a smart light or sound target, Spectra L/S can discover it and interact automatically, including direct tuning/control workflows from the hardware interface.

On `main`, project direction follows `esphome/spectra_ls_system/v-next-NOTES.md`: hardware-first UX, menu as fallback, deterministic controls, and scalable room/target handling.

## Hardware Reference (Current + Recommended)

### MCUs

- **[ESP32-S3](https://www.espressif.com/en/products/socs/esp32-s3)** (`[esp32-s3-devkitc-1](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/index.html)`): OLED/UI rendering, Home Assistant API integration, network control paths.
- **[RP2040](https://www.raspberrypi.com/products/rp2040/) ([CircuitPython](https://circuitpython.org/))**: physical input scanning and event publishing upstream.

### Inputs (Switches, Buttons, Knobs, Sliders, Dials)

- Direct Lighting Brightness / Hue / Saturation control over whole rooms or individual lights.
- Fast room switching from hardware, so you can move control from one space to another instantly.
- One-touch transport controls for audio: Play/Pause, Next, and Back/Previous on the active target.
- Real-time Physical 3-Band EQ + volume shaping to dial in the vibe without leaving the couch.

#### What these controls actually do (real-world examples)

- **Transport command cluster**: dedicated hardware buttons drive full playback control — **Play/Pause**, **Next**, and **Back/Previous** — on the active audio target without hunting through phone menus.
- **Room-quick lighting flow**: tap Room Select to cycle spaces, then move the lighting slider to set brightness for that room/target immediately; Spectra L/S syncs the selection back to Home Assistant helpers.
- **Physical 3-Band EQ shaping**: bass, mid, and treble analog controls let you dial a calmer background mix or push a brighter, punchier profile for party mode in real time.
- **Source + target control from hardware**: source toggle and target selectors keep control on-device so you can jump between zones and sources with instant OLED feedback.

#### v-next crossfade / balance slider (planned feature)

- **Multi-room mode**: the slider will shift volume balance between rooms (for example, pull energy toward the living room while easing the kitchen/bedroom).
- **Single-room mode**: the same slider will switch to left/right speaker balance for precise stereo placement in one room.

- **[PCF8575](https://www.nxp.com/products/interfaces/ic-spi-i3c-interface-devices/general-purpose-i-o-gpio/remote-16-bit-i-o-expander-for-ic-bus:PCF8575)** digital expander (active at `0x20`; optional expansion at `0x21`) for button/switch inputs.
- **[Seesaw](https://learn.adafruit.com/adafruit-seesaw-atsamd09-breakout/overview) rotary encoders** (menu + lighting encoders).
- **[ADS1015](https://www.ti.com/product/ADS1015)** analog ADC for high-resolution knobs/pots (Volume, Physical 3-Band EQ, lighting slider).
- **RP2040 internal ADC** for EQ mid channel.
- **[ADS7830](https://www.ti.com/product/ADS7830)** (recommended expansion, `0x49`) for additional low-resolution selector/switch channels.
- v-next analog control surface emphasis: direct analog Volume + Physical 3-Band EQ with additional switches/dials for expanded control coverage.

### Control Interfaces

- **[Home Assistant API](https://www.home-assistant.io/integrations/api/)** (`api:` in ESPHome) for entity state and helper orchestration.
- **Wi-Fi/TCP control** to [Arylic](https://developer.arylic.com/httpapi/)/[Linkplay](https://linkplay.com/)/[WiiM](https://www.wiimhome.com/)-class endpoints (primary real-time audio control path).
- **RP2040 ↔ ESP32 UART** event transport for hardware controls.
- **I2C buses** for OLED and local input peripherals (PCF8575 / Seesaw / ADC devices).

### Digital Audio Ingest + Final DAC Path

Spectra Level / Source (Spectra L/S) is designed for real-world use right where you live: place it on the coffee table and treat it as your home digital-to-analog control hub. From the couch or desk, you get tactile control over sources, routing, and playback without living inside phone apps. Under the hood, it still maintains a controlled end-to-end path for signal quality, timing stability, and conversion transparency.

Spectra L/S also supports whole-home multi-speaker playback with tight room-to-room synchronization, so one tap can keep every room locked to the same track and timing. You can also split zones for independent playback when needed, including routing supported audio-input sources into grouped multi-room streaming.

- HDMI input from an ARC-capable source is supported in the source chain.
- ARC digital audio is split/extracted and routed into the final output conversion stage.
- Audio-side streaming/control capabilities (from UP2STREAM HD DAC product data): dual-band Wi-Fi, AirPlay 2, Spotify Connect, TIDAL Connect, and aptX HD Bluetooth 5.0.
- Final DAC stage: **[ESS ES9038Q2M](https://www.esstech.com/products-overview/es9038q2m/)** (`ESS 9038Q2M DAC`).
- Conversion target capability: **192kHz / 24-bit**.
- Board class: no-amp streaming DAC/preamp module.
- Supports: `FLAC`, `MP3`, `AAC`, `AAC+`, `ALAC`, `APE`, `WAV`.

#### HD DAC Capability Cutsheet

- **Wireless Capability**: AirPlay 2, Spotify Connect, TIDAL Connect, Wi-Fi, Bluetooth with aptX HD, DLNA, UPnP.
- **Multi-room**: AirPlay 2 multi-room grouping, synchronized same-audio playback across rooms, and different songs in different rooms.
- **Music Service**: Spotify, Apple Music, Amazon Music, Tidal, Qobuz HD, TuneIn, Internet Radio, BBC Radio, Napster, iHeart Radio, Radio Paradise.
- **Local Music Source**: phone storage, NAS, USB stick.

### Recommended Screen

- **I2C OLED, [SSD1306](https://www.solomon-systech.com/product/ssd1306/) 128x64 mode** (configured `oled_model: "SSD1306 128x64"`, typical address `0x3C`).
- SSD1309-compatible modules are supported when driven in SSD1306 mode in current configs.

## What It Feels Like to Use Spectra L/S

- **Instant physical control**: adjust sound and lights in real time from dedicated controls, not nested app screens.
- **Room-aware operation**: jump between rooms quickly and control the right targets without reconfiguring every step.
- **Always-clear feedback**: the OLED keeps navigation and active actions visible, so you always know what you’re controlling.
- **Reliable day-to-day flow**: physical actions stay responsive even when the smart-home stack is busy in the background.

## Why People Love This Form Factor

- It turns whole-home control into a tactile experience you can use by feel.
- It keeps “party mode” and “wind-down mode” one move away.
- It reduces phone dependence for common actions like transport, room lighting, and tone shaping.
- It makes shared spaces easier: anyone can walk up, understand it, and use it fast.

## System Test Overview (Dev Tools Templates)

Use `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` as the standard system-test playbook in Home Assistant Developer Tools → Template. The templates are layered so you can move from broad health to precise command-effect verification quickly:

- **Template 1 — Overall Health Check**: verifies package/helper/runtime integrity and sentinel entities.
- **Template 2 — Audio Control Path Probe**: validates target → host → meta → now-playing routing consistency.
- **Template 3 — Command Readiness Probe**: confirms writable control surfaces and transport prerequisites.
- **Template 4 — Command Effect Verification**: before/after snapshot for `number.set_value` validation on a chosen control entity.
- **Template 5 — One-Screen Smoke Test**: fast go/no-go rollup across the four layers above.

Recommended flow: run 1 → 2 → 3 after deploy, then use 4 for specific action checks and 5 for quick regression smoke tests.

## Works with the Audio Ecosystem You Already Have

- Music Assistant players
- Home Assistant media players
- WiiM-based rooms
- Arylic/LinkPlay-class endpoints
- AirPlay / Apple TV style sources
- Plex sessions/players (optional)

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

0. If you are integrating into an existing Home Assistant install, merge the placeholder lines from `SPECTRA-HA-CONFIG-PLACEHOLDERS.md` into your local `configuration.yaml`.
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
