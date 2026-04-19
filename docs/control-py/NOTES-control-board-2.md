# Control Board v2 (control-board-2) Notes

These notes are the **authoritative v2 design doc**. They supersede all prior v1/v2 notes in `previous/`.

## Documentation gate (must close before done)

- [ ] Update `docs/CHANGELOG.md` for any functional change.
- [ ] Update this notes file if behavior or architecture changed.
- [ ] Call out any deferred doc updates explicitly before ending a session.

## Setup / reproduction notes (new HA + MA)

### Setup goal

Deploy the HA packages, reload, point Spectra L/S to HA, and go — with no YAML edits beyond required secrets and device‑specific networking.

### Step‑by‑step (fresh HA + MA)

1. **Install Music Assistant (MA)**

    - Add the MA integration in Home Assistant.
    - Confirm `sensor.ma_players` is populated.

1. **Add required secrets**

    - In `spectra_ls_secrets.yaml` set:
      - `ma_server_url`
      - `ma_ll_token` (include the `Bearer` prefix)
    - Copy those values into **Home Assistant** `secrets.yaml`.

1. **Drop in HA packages** (copy into `/config/packages/`)

    - Required: `ma_control_hub.yaml`, `spectra_ls_lighting_hub.yaml`, `spectra_ls_scripts.yaml`.
    - Optional: `spectra_ls_tv_source_auto.yaml` (universal HDMI/TV → Spectra input auto-switch).
    - Optional: any Plex or media filters you want.

1. **Reload Home Assistant**

    - Use HA UI → Settings → System → Restart, or reload template/script/automation if preferred.
    - Confirm new helpers exist:
      - `input_select.control_board_room`
      - `input_select.control_board_target`
      - `input_select.ma_active_target`
      - `input_text.spectra_ls_target_primary_entity`
      - `input_text.spectra_ls_target_primary_tcp_host`
      - `input_text.spectra_ls_target_room_entity`
      - `input_text.spectra_ls_target_room_tcp_host`

1. **Verify dynamic lighting discovery**

    - Ensure your light entities are assigned to **Areas** in HA.
    - Confirm sensors update:
      - `sensor.control_board_room_options`
      - `sensor.control_board_target_options`
      - `sensor.control_board_room_area_id`
      - `sensor.control_board_target_entity_id`

1. **Configure MA target mapping (HA UI)**

    - Defaults are now prefilled for the always‑present Spectra LS:
      - `input_text.spectra_ls_target_primary_entity` → `media_player.spectra_ls` (WiiM transport)
      - `input_text.spectra_ls_target_primary_meta_entity` → `media_player.spectra_ls_2` (MA metadata)
    - Update those defaults **only if your entity IDs differ**.
    - Set these `input_text` values if you have additional devices:
      - `input_text.spectra_ls_target_primary_tcp_host` → **Spectra LS** TCP host IP
      - `input_text.spectra_ls_target_room_entity` → **Room (optional)** MA media_player entity
      - `input_text.spectra_ls_target_room_tcp_host` → **Room (optional)** TCP host IP
    - TCP port is fixed at **8899** for LinkPlay/WiiM/Up2Stream devices.
    - Optional (metadata override):
      - `input_text.spectra_ls_target_primary_meta_entity`
      - `input_text.spectra_ls_target_room_meta_entity`

1. **Configure ESPHome device substitutions**

    - Wi‑Fi + static IP (device‑specific). Use `wifi_ssid` / `wifi_password` secrets for the Control Board v2.
    - Leave lighting room/target labels as fallbacks only.

1. **Flash ESPHome (ESP32‑S3)**

    - Build and upload `control-board-esp32-tcp.yaml`.
    - Confirm ESPHome connects to HA API.

1. **Flash RP2040 firmware (CircuitPython)**

    - Copy `control-py/code.py` to `CIRCUITPY/`.
    - Copy `control-py/lib/` to `CIRCUITPY/lib/` (PCF8575, debouncer, ticks, seesaw, ADS1015 if used).
    - Preserve `/calibration.json` if present.
    - Reboot the RP2040 and confirm UART events are flowing.

1. **Confirm control paths**

    - Validate `input_select.ma_active_target` updates.
    - Ensure `sensor.ma_control_hosts` and `sensor.ma_control_port` have values.
    - Room and target lists should match HA Areas + lights.
    - Brightness, hue, saturation should affect the selected room/target.

### Common pitfalls

- **Rooms empty**: no lights assigned to HA Areas.
- **Targets empty**: selected Area has no `light.*` entities.
- **MA metadata missing**: `ma_ll_token` not set or MA not reachable.
- **No lighting control**: `script.control_board_set_light_dynamic` missing or renamed.

### Minimal required edits (by design)

- `spectra_ls_secrets.yaml`: MA URL + token
- `secrets.yaml`: include Spectra LS secrets
- ESPHome substitutions: Wi‑Fi + IPs
- HA input_texts: MA target entity IDs + TCP hosts/ports
- RP2040 firmware: copy `control-py/code.py` + `control-py/lib/` to `CIRCUITPY/`

## Pin maps (current firmware, 2026-04-10)

### System pinout + signal map (v2, RP2040 Feather)

```text
  Inputs + analog (RP2040 Feather)              UI + Wi‑Fi (ESP32‑S3)
┌──────────────────────────────┐         ┌──────────────────────────────┐
│  PCF8575 (buttons) +          │         │  OLED SSD1306/1309 (I2C)      │
│  Seesaw encoders (I2C)        │         │  GPIO8 = SDA, GPIO9 = SCL     │
│      ▲                         │         │                              │
│      │ I2C (SDA/SCL)           │         │  LED rings (RMT)              │
│  RP2040 Feather                │         │  Hue ring: GPIO13             │
│  A0/A1 = sliders (ADC)         │         │  Audio ring: GPIO14           │
│  (ADS1015 optional on I2C)     │         │                              │
│      │ UART (115200)           │         │  Arylic UART: GPIO15/16       │
└──────┴───────────────┬────────┘         │  RP2040 UART: GPIO17/18       │
                │                  └──────────────────────────────┘
                └──────────────►  ESP32‑S3 (HA/UI)
```

### ESP32‑S3 pins (control‑board‑esp32-tcp.yaml)

- **OLED I2C**: `GPIO8` (SDA), `GPIO9` (SCL)
- **RP2040 UART**: `GPIO17` (TX → RP2040 RX), `GPIO18` (RX ← RP2040 TX)
- **Arylic UART**: `GPIO15` (TX), `GPIO16` (RX)
- **Hue ring**: `GPIO13`
- **Audio ring**: `GPIO14`

### RP2040 Feather pins (CircuitPython)

- **I2C (inputs)**: `board.SDA`, `board.SCL` (STEMMA QT) → PCF8575 + seesaw + ADS1015
- **UART to ESP32‑S3**: `board.TX`, `board.RX`
- **Analog inputs**: `A0` used for EQ mid (0–3.3V); `A1` spare
- **External ADC (optional)**: ADS1015 on same I2C bus (`0x48`)

### RP2040 I2C devices + addresses

- **PCF8575**: first detected in `[0x20, 0x21]` (buttons only)
- **Seesaw encoders**: Menu `0x36`, Lighting `0x37`
- **ADS1015** (external ADC): `0x48`

### PCF8575 button map (current)

> Only **one** PCF8575 is used; the first address found wins. The second expander is currently unused.

- **P0**: Room select → event **31**
- **P1**: Source toggle → event **35**
- **P2**: Back (long‑press = Home) → event **36**
- **P3**: Home (autocal trigger only; **no UART event**)
- **P4**: Prev → event **34**
- **P5**: Play/Pause → event **32**
- **P6**: Next → event **33**
- **P7**: Mute → event **22**
- **P8**: Select → event **37**
- **P9–P15**: spare

### Seesaw encoders (current)

- **Menu encoder**: address `0x36`, delta **2**, press **21**
- **Lighting encoder**: address `0x37`, delta **1**, press **20**

### Analog inputs (current)

- **ADS1015 ch0** → `eq_bass_pot` (event **104**)
- **ADS1015 ch1** → `lighting_slider` (event **101**)
- **ADS1015 ch2** → `volume_pot` (event **102**)
- **ADS1015 ch3** → `eq_treble_pot` (event **106**)
- **RP2040 A0** → `eq_mid_pot` (event **105**)

### Planned ADC + control-target switch reorg (design proposal)

> **No firmware changes yet.** This is a hardware + firmware plan for when parts arrive.

#### Goals

- **Eliminate control‑target ambiguity** by adding a physical 5‑position selector (Auto + 4 fixed targets).
- **Preserve high‑resolution feel** on volume/EQ.
- **Use low‑resolution ADC** for low‑precision inputs (rotary switch ladder, optional extra sliders).

#### Hardware proposal (two‑ADC topology)

- **Keep ADS1015** (12‑bit) for high‑resolution controls:
  - `eq_bass_pot`
  - `eq_treble_pot`
  - `volume_pot`
  - (optional spare channel)
- **Add ADS7830** (8‑bit, 8‑ch) for low‑resolution inputs:
  - **Control‑target rotary switch** via **resistor ladder** into one ADS7830 channel.
  - Potential expansion: additional sliders, buttons‑as‑analog, test pads.
- **Keep RP2040 internal ADC** for **lighting slider** (or EQ mid if desired) to avoid jitter and keep a stable source.

#### Alternate hardware option (single‑ADC topology)

If we want fewer parts:

- **Replace ADS1015 with ADS7830** and move *all* external analog inputs to ADS7830.
- **Trade‑off:** 8‑bit stepping on volume/EQ (acceptable, but less smooth).
- **Recommendation:** only consider this if part count/cost is more important than feel.

#### Rotary switch details

- **Switch:** 1P5T detented rotary (break‑before‑make).
- **Positions:**
  - **0 = Auto** (use HA/MA auto selection)
  - **1–4 = Fixed targets** (four control devices)
- **Wiring (ladder):**
  - Common to ADS7830 channel.
  - Each throw through a distinct resistor to GND.
  - ADS7830 VIN = 3.3V (use as reference).
- **ADC thresholds:** map 5 stable voltage windows to 5 positions; include a dead‑band between windows.

#### Proposed analog channel map (two‑ADC)

- **ADS1015 @ 0x48**
  - ch0 → `eq_bass_pot` (event 104)
  - ch1 → `volume_pot` (event 102)
  - ch2 → `eq_treble_pot` (event 106)
  - ch3 → spare (future)
- **RP2040 internal**
  - A0 → `lighting_slider` (event 101) **or** `eq_mid_pot` (event 105)
  - A1 → spare
- **ADS7830 @ 0x48/0x49** (address configurable; avoid conflict with ADS1015)
  - A0 → `control_target_switch` (new analog event)
  - A1–A7 → reserved

#### I2C address planning

- ADS1015 default: **0x48**
- ADS7830 default: **0x48**
- **Action:** set **ADS7830 to 0x49** (AD0 closed) to avoid address conflict.

#### Firmware changes required (RP2040 / CircuitPython)

1. **Add ADS7830 support** (library + detection)
   - Add `adafruit_ads7830/` + `adafruit_bus_device/` to `CIRCUITPY/lib`.
   - Update I2C scan to detect **both** ADS1015 and ADS7830.

2. **Multi‑ADC read loop**
   - ADS1015 continues feeding high‑res pots (volume/EQ).
   - ADS7830 provides low‑res inputs (switch ladder, extras).
   - Normalize ADS7830 values to 0–65535 scale (library already does this).

3. **Rotary switch interpretation**
   - Add a new analog channel definition (e.g. `control_target_switch`).
   - Implement **threshold mapping** (5 buckets) with hysteresis.
   - Debounce position changes (e.g., require N consecutive samples).

4. **UART event mapping**
   - Assign a **new analog event ID** for the switch (e.g., 110).
   - Send value as a **position index** (0–4) or as scaled analog value (ESPHome maps).

5. **Calibration / persistence**
   - Switch ladder does **not** need calibration file entries.
   - If ADS1015 channels move, update `/calibration.json` mapping names accordingly.

#### ESPHome changes required (ESP32‑S3)

1. **Add new analog sensor** for switch position (event ID TBD).
2. **Map position to control‑target selection**:
   - **Auto** (0): clear manual lock and allow HA auto‑select.
   - **Positions 1–4**: set `input_select.ma_active_target` to fixed entities.
3. **Force sticky lock** whenever switch is non‑Auto.
4. **Ignore ambiguity prompts** when switch is fixed.

#### HA changes required

- Add a **fixed list** of 4 control targets (entities) for the switch positions.
- Document the mapping in HA helpers or substitutions.

#### Risks / mitigations

- **ADC stepping visible**: use ADS1015 for volume/EQ to keep smoothness.
- **Address conflict**: ensure ADS7830 address != ADS1015.
- **Rotary noise / bounce**: use hysteresis + sample confirmation.
- **Switch vs HA drift**: treat switch as authoritative; HA UI changes only affect Auto.

#### Validation checklist (when parts arrive)

- Verify ADS1015 + ADS7830 coexist on I2C.
- Confirm switch positions map cleanly with no flapping.
- Confirm fixed positions **never** show control‑target prompt.
- Confirm Auto behaves like today (prompts only if ambiguous).

### UART event ID summary (ESP32‑S3 facing)

#### Encoder deltas (Type `0x03`)

- Lighting: **1**
- Menu: **2**

#### Encoder presses (Type `0x01`)

- Lighting: **20**
- Menu: **21** (Select)

#### Buttons (Type `0x01`)

- Room: **31**
- Source: **35**
- Back: **36**
- Prev: **34**
- Play/Pause: **32**
- Next: **33**
- Mute: **22**
- Select: **37**

#### Analog (Type `0x02`)

- Lighting slider: **101**
- Volume pot: **102**
- EQ bass: **104**
- EQ mid: **105**
- EQ treble: **106**

### CircuitPython library requirements

Copy these into `CIRCUITPY/lib` on the Feather RP2040:

- **Required**: `adafruit_pcf8575.mpy`, `adafruit_debouncer.mpy`, `adafruit_ticks.mpy`
- **Required (encoders)**: `adafruit_seesaw.mpy` + `adafruit_seesaw/`
- **Required if ADS1015 is used**: `adafruit_ads1x15/` and `adafruit_bus_device/`

> The repo has these under `control-py/lib/`. If `CIRCUITPY` isn’t mounted, stage them later.

## Change log

### 2026-04-12

- HA: DST manual override now sticks until the room reaches target temperature; Tuya cool setpoint defaults 2°F below DST target on manual start.
- HA: DST auto-off now respects manual override window to prevent premature shutdown.
- HA: DST now uses bedroom enviro temperature/humidity sensors with faster updates.
- HA: DST now reasserts Tuya cool mode while DST is cooling, without forcing preset changes during manual override.
- HA: Fix tuya_unsupported_sensors config flow await error and set DST automation/script modes to avoid “Already running” warnings.

### 2026-04-06

- **Calibration UI removal**: no user-facing calibration UI; autocal is disabled but EQ calibration tracking persists via `/calibration.json`.
- **Menu simplification**: removed Settings/Calibration menus (top-level is Lighting/Audio only).
- **Audio packages**: TCP package is authoritative; non-TCP audio package is legacy/stale.

### 2026-04-07

- **UI cleanup**: render path no longer writes `last_input_ms`; initialization happens at boot.
- **Build hygiene**: `control-board-peripherals.yaml` moved to `previous/` (stale, no longer in active builds).
- **Now‑playing gating**: stale metadata no longer revives the screen when nothing is playing.

### 2026-03-27

- **MA hardware-only flow**: removed slot-based metadata stack; now-playing uses **MA active sensors** only.
- **Target routing**: MA `input_select.ma_active_target` now directly drives TCP host selection.
- **HA polling**: ESPHome refreshes only the **active MA target** (no slot entity refreshes).
- **Docs refresh**: updated design notes to reflect MA-active + TCP-only control paths.

### 2026-03-28

- **Dynamic lighting hub**: room/target options, room/target on-state, and HS color now derive from HA Areas + light entities (drop-in package).
- **Menu label**: Lighting adjust menu renamed from “Toggles” → “Lighting Values”.
- **Brightness slider UX**: moving the lighting slider exits menu mode so the room list no longer flashes when adjusting brightness.

### 2026-03-06

- **Now-playing layout**: title band height increased (+4 px); artist line pushed down for legibility.
- **Track font**: now-playing title font increased by 1 px.
- **Album/artist lines**: album renders on its own line (mid font), artist renders below with a tight inverted background (2 px horizontal padding).
- **Artist block**: shifted down 6 px; top padding removed and bottom padding increased.
- **Album scroll mask**: album text is masked near the volume area with a 2 px left buffer.
- **Volume UI**: numeric value removed; vertical meter moved down.
- **OCR-B scroll tuning**: increased scroll gap, sped up scroll, and widened char width estimates to prevent overlap.
- **Display refresh**: now-playing display refresh set to 250 ms for smoother scrolling.
- **Build fix**: added default `now_playing_mid_font_size` and `font_mid` in peripherals packages to avoid undefined substitution/ID errors.
- **Pill removed**: source pill hidden in now-playing view.
- **Volume display**: switched to a **vertical slider** with a **numeric value underneath** (right-aligned).
- **Volume scaling**: UI now shows **1–11**, mapped to **0–90% actual**; **11 = 90%**.
- **Max volume limiter**: enforced across UI set, encoder delta, and direct set volume paths.
- **Audio ring**: now respects the max volume cap for LED fill.
- **Metadata refresh**: HA update interval set to **3s** (no MA direct API calls from ESPHome).
- **Progress bar**: removed predictive position extrapolation; now relies on HA position updates only.
- **Stale metadata mitigation**: when playback reaches track end and metadata stalls, ESPHome forces a HA `update_entity` refresh (cooldown guarded).
- **Observation**: now-playing metadata appeared stale until MA restart; after MA reboot, HA updates resumed.

### 2026-03-08

- **RP2040 input MCU**: migrating from XIAO RP2040 to **Adafruit Feather RP2040**.
- **Analog strategy**: prefer **internal ADC** (A0/A1) for sliders; **ADS1015 optional** fallback/expansion path retained.
- **ADC mode**: RP2040 firmware can **auto-detect ADS1015** on I2C and fall back to internal ADC when absent.
- **Pinout**: added visual system pin/map summary at top of this document.
- **Feather conversion**: CircuitPython uses `board.SDA/SCL`, `board.TX/RX`, and `board.A0–A3` (no XIAO‑specific pins).

## Current build state (as of 2026-03-27)

- **Fonts**: OCR-A for UI and splash.
- **Now-playing UI**:
  - Inverted title band (height = title font + 6 px).
  - Title font size **10**; artist line pushed down (title font + 9 px).
  - Album line uses mid-size font (**9**) between title and artist sizes.
  - Source pill hidden.
  - Progress bar at bottom; shown only when duration/position are valid.
  - Volume displayed as **vertical slider + numeric 1–11**, right-aligned.
  - Artist line is inverted only around the text (2 px horizontal padding).
- **Volume model**:
  - `audio_max_volume_pct` default **90**.
  - UI scale `audio_ui_min=1`, `audio_ui_max=11`.
  - Max cap enforced in `arylic_set_volume`, `arylic_volume_delta`, and `arylic_volume_set`.
  - Audio ring brightness uses capped volume for LED fill.
- **Metadata source**: Music Assistant **active sensors** (`sensor.ma_active_*`); ESPHome refreshes only the **active MA target**.
- **Progress tracking**: no predictive extrapolation; position is whatever HA last reported.
- **Meta timestamps**: ESPHome tracks last metadata update and triggers a refresh if position stalls at track end.
- **Rings**: build currently includes `control-board-peripherals-no-rings.yaml` (rings disabled build).
- **Known behavior**: If MA/HA metadata stalls, ESPHome will display stale data until HA resumes updates.

## ESPHome config snapshot (current, 2026-03-22)

> Source: `/config/esphome/control-board-esp32-tcp.yaml` + `/config/esphome/control-py/*`

### Topology

- **Main ESPHome file**: `control-board-esp32-tcp.yaml`
- **Packages included**:
  - `control-board-peripherals-no-rings.yaml` (OLED-only, no LED rings)
  - `control-board-peripherals.yaml` is **legacy/stale** and **not used** in current builds.
  - `packages/control-board-hardware.yaml`
  - `packages/control-board-ui.yaml`
  - `packages/control-board-system.yaml`
  - `packages/control-board-diagnostics.yaml`
  - `packages/control-board-audio-tcp.yaml`
  - `packages/control-board-audio.yaml` is **legacy/stale**; **TCP is authoritative**.
  - `packages/control-board-lighting.yaml`
- **Substitutions**: `control-board-esp32-tcp.yaml` now includes `/config/esphome/control-py/substitutions.yaml` for Control Board v2.
- **Wi-Fi**: uses `manual_ip` from substitutions (`static_ip`, `gateway`, `subnet`, `dns1`, `dns2`).
- **Wi-Fi**: `wifi.use_address` can be temporarily pinned for OTA/API targeting when an IP is in transition.
- **Components path**: `external_components` points to `/config/esphome/control-py/components` (cpu_usage + rp2040_uart).

### Audio control + metadata

- **TCP control**: `arylic_tcp_host` + `arylic_tcp_port` (primary); `volume_tcp_only: true`.
- **Host fallback + logging**: volume/EQ TCP sends fall back to `sensor.ma_control_host` when `sensor.ma_control_hosts` is empty, with gate/deny logging to expose prompt/host/ambiguity blocks.
- **Host stability**: invalid host updates no longer clear last-good hosts while a valid MA active target is present.
- **HTTP status polling** is **disabled by default** (`arylic_http_enabled: false`); can be enabled for `getPlayerStatus` polling.
- **MA hardware targets**: MA `input_select.ma_active_target` chooses **Living Room WiiM** or **Spectra LS**.
- **Meta player override**: `meta_select_button_id` cycles MA target; popup + auto-reset timers. (No dedicated RP2040 button is wired for this in the current firmware.)

### UI / display state machine

- **Display states**: Splash → Boot Menu → Menu → Now Playing → Lighting → Screensaver → Blank.
- **Now Playing** pulls from HA + Arylic meta (with activity + staleness gating).
- **Progress bar** uses HA position/duration only; no extrapolation.
- **Screensaver** activates after `screensaver_idle_ms`, with `screensaver_update_ms` render cadence.

### Menu architecture

- **Top-level tiles**: Lighting / Audio / Gear.
- **No Settings/Calibration menu** in the current v2 build.
- **Menu encoder** (RP2040 delta id 2) drives navigation; **select/confirm** uses menu encoder press (id 21) **and** Select button (id 37), and **back** uses the back button (id 36).
- **Control Targets prompt**: back cancels the prompt; empty lists auto-cancel with a brief popup.
- **Control Target popup**: uses a dedicated “Control Target” header and prompt debounce to avoid repeat popups during HA host updates.
- **Prompt auto-dismiss**: once control hosts are valid and ambiguity clears, the prompt closes unless it was opened manually from the Gear menu.
- **Prompt cooldown**: volume/encoder-triggered prompts set a short cooldown to avoid repeated popups while hosts/ambiguity settle.
- **Sticky target lock**: suppresses control-target prompts once a target is chosen; lock remains until the selector is explicitly reopened, and invalid host updates are ignored while locked.
- **Prompt highlight**: top padding reduced by 2px to prevent header overlap.

### Calibration

- Calibration UI has been **removed** (no user flow; autocal disabled).
- RP2040 applies `/calibration.json` at boot and can update it via EQ calibration tracking.

### Audio control (TCP package)

- **Active package**: `packages/control-board-audio-tcp.yaml` (TCP-only transport).
- **Control host(s)**: resolved via HA (`sensor.ma_control_hosts` + `sensor.ma_control_port`).
- **Multi-host dispatch**: `arylic_tcp` sends to a CSV list of hosts; per-command fan-out.
- **Volume pot path**: raw pot values mapped to % and throttled by `volume_pot_send_interval_ms`, with deferred send queueing.
- **MA metadata**: uses only MA active sensors (`sensor.ma_active_*`) for title/artist/album/app/source/state/position.
- **Meta override**: `meta_select_button_id` cycles MA target via HA service. (No dedicated RP2040 button is wired for this in the current firmware.)

### Lighting control (package)

- **Lighting encoder**: delta events adjust hue/sat or brightness depending on mode; press toggles hue/sat or exits brightness.
- **Brightness slider**: analog `sensor_id: 101` drives brightness and can also control menu selection during menu mode; **no HA brightness push while menus are active**.
- **Brightness mode auto-exit**: brightness mode clears after slider inactivity or when entering menus.
- **Target mapping**: target labels are normalized for matching to entity IDs to avoid silent mismatches.
- **Slider debounce**: brightness slider sends are debounced to a single update after movement settles.
- **Room/target selection**: driven by input_selects and synced both ways (options sourced dynamically from HA Areas).
- **HA calls**: `light.turn_on/off` or custom script for hs/brightness updates; target entity/area IDs are resolved dynamically in HA.

### Diagnostics helpers

- **OLED contrast**: runtime slider + applied raw value + debug text sensor.
- **Test buttons**: e.g., `Arylic Test Volume 20`.

### Custom components (ESPHome)

- **`rp2040_uart`**: UART packet parser for RP2040 binary events (0xAA55 header, 10‑byte frames); routes button/analog/encoder events to sensors.
- **`arylic_uart`**: UART parser for Arylic serial protocol (`STA`, `VOL`, `MUT`, `BAS`, `TRE`, `SRC`, `TIT`, `ART`, `ALB`, `PLA`).
- **`arylic_tcp`**: TCP passthrough wrapper with queue + worker task, non‑blocking connect/send, and multi‑host fan‑out helpers.

### Home Assistant package (Plex local filter)

- `packages/plex_local_filter.yaml` builds **local‑only** now‑playing sensors by filtering Plex sessions.
- Uses subnet allowlist + denylist and exposes `plex_now_playing_local` only when a local session is detected.

## System overview (v2)

- **Main MCU**: ESP32-S3 N16R8 Gold Edition Development Board (16MB Flash, 8MB PSRAM, Lonely Binary)
- **Input MCU**: Adafruit Feather RP2040, dedicated input scanner
- **MCU split**:
  - **RP2040** handles **all input devices** over **I2C** using Adafruit CircuitPython drivers and forwards events over **UART**.
  - **ESP32-S3** handles **UI, menus, Wi‑Fi/HA**, display rendering, and overall system logic.

## v2 intent (experience)

- **Button‑first UX**: core actions should be possible without diving into menus.
- **Menus are secondary**: use for deeper settings/options only.
- **No ambient strip**: removed entirely in v2.
- **LED feedback** is focused on **audio volume** and **lighting hue/saturation** (encoder ring).
- **Audio screensaver** behavior should match v1 (see below).

## Setup & web settings UI (future)

### Dashboard goals

- Provide a **simple, guided setup wizard** so a non‑technical user can configure the Spectra without editing YAML.
- Keep the **primary experience dead‑simple**, with optional **advanced** steps hidden behind an “expert” toggle.

### Proposed wizard flow (v1)

1. **Wi‑Fi provisioning** — use ESPHome provisioning (captive portal / Improv).
1. **Home Assistant link** — connect to HA via ESPHome API (pairing flow).
1. **Select MA target** — set `input_select.ma_active_target` (Living Room WiiM or Spectra LS).
1. **Hardware toggles** — rings enabled/disabled, UART device presence.
1. **Display tuning** — screensaver idle time, scroll speed, font sizes (advanced).
1. **Save + test** — persist settings and show a “Now Playing” preview.

### Runtime‑configurable vs build‑time settings

**Runtime (can change without reflash):**

- `ha_audio_player` / `_2` / `_3`
- Screensaver timings (idle/update)
- Scroll speed / gap
- Display modes (screensaver on/off, audio focus)
- Volume source preference (UART vs HA) when both are available

**Build‑time (requires rebuild):**

- GPIO pins, UART pins
- OLED model/address
- LED ring counts / chipset
- ESP32 board type / framework settings

### How settings are passed to the ESP

**Yes — settings can be sent to the ESP at runtime.**

Implementation approach (ESPHome‑native):

- Expose **editable entities** using `number`, `select`, `text`, and `switch` components.
- Use `set_action` to update **globals** and apply changes live.
- Persist values with `globals` using `restore_value: yes` (stored in flash).

UI surfaces:

- **ESPHome web_server** provides a simple built‑in UI for editing those entities.
- **Home Assistant** can act as the primary UI (dashboard cards / config panel).
- A dedicated **setup web app** can write to those entities via HA REST API or ESPHome native API.

### Persistence + safety

- Use `restore_value` for configuration globals to survive reboots.
- Avoid frequent writes to flash (rate‑limit changes; save on “Done”).
- Store a **last known good** configuration snapshot for rollback.

## Home Assistant dashboard (post‑setup)

### Dashboard goal

- Provide a **clean, non‑technical dashboard** for day‑to‑day tuning after the wizard applies initial settings.
- Provide a **clean, non‑technical dashboard** for day‑to‑day tuning after the wizard applies initial settings.
- Keep a separate **advanced** view for power users.

### Spectra LS Settings view (recommended)

Create a dedicated Lovelace view named **Spectra LS – Settings** with an **Entities** card
containing the key helpers so you never need to edit YAML:

- `input_text.spectra_ls_target_primary_entity`
- `input_text.spectra_ls_target_primary_meta_entity`
- `input_text.spectra_ls_target_primary_tcp_host`
- `input_text.spectra_ls_target_room_entity`
- `input_text.spectra_ls_target_room_meta_entity`
- `input_text.spectra_ls_target_room_tcp_host`
- `input_select.ma_active_target`

This provides a modern “settings page” experience while keeping the config HA‑native and
easy to maintain.

### Recommended dashboard sections

- **Status** — now‑playing title/artist/source/state (from `sensor.ma_active_*`), connection state (Wi‑Fi, HA API connected).
- **Audio controls** — volume slider (UART when available, HA fallback otherwise), mute toggle, source selector (BT/NET/etc) when UART is present.
- **Display & screensaver** — screensaver idle time, scroll speed/gap, font sizes (advanced only).
- **Lighting linkage** — room + target selectors (input_selects), brightness slider.
- **Advanced** — MA target selection (`input_select.ma_active_target`), rings enabled/disabled, UART presence toggle.

### Suggested entity mapping

- **Input select:** `input_select.ma_active_target`
- **Sensors:** `sensor.ma_active_title`, `sensor.ma_active_artist`, `sensor.ma_active_album`, `sensor.ma_active_app`, `sensor.ma_active_source`, `sensor.ma_active_state`, `sensor.ma_active_position`, `sensor.ma_active_duration`, `sensor.ma_active_volume`
- **Numbers:** `screensaver_idle_ms`, `screensaver_update_ms`, `scroll_speed_ms`, `scroll_gap_px`, `now_playing_font_size`, `now_playing_small_font_size`
- **Switches:** Rings enabled, UART present

### Notes

- The dashboard should be **optional**; the device must still be usable with defaults.
- The wizard should set **safe defaults** so the dashboard is never required for a basic setup.

## Outstanding items (quick list)

- Finalize **LED ring counts/pins** (audio + hue).
- Finalize **menu/selection model** (menu encoder navigation + select/back behavior).
- Simplify **lighting adjust menu**: remove **Brightness** from Hue/Sat menus (slider-only), and define the **light selection → slider** flow with minimal nesting.
- Confirm **HA helpers** (room/target input_select + room groups).
- Confirm **scan/debounce** values (leave library defaults unless needed).

## Home Assistant helpers (recommended)

### Music Assistant (hardware targets + active metadata)

- **Active target selector**: `input_select.ma_active_target` (must contain only the **two hardware devices**).
- **Active metadata sensors**: `sensor.ma_active_*` (title/artist/album/app/source/state/position/duration/volume).
- **Control hosts**: `sensor.ma_control_hosts`, `sensor.ma_control_host`, `sensor.ma_control_port` (resolved in HA).
- The ESPHome device **does not** read arbitrary `media_player.*` entities directly anymore.

### Input selects

- `input_select.control_board_room`
- `input_select.control_board_target`

#### Room options (in order)

- Living Room
- Dining Room
- Kitchen
- Bedroom

#### Target options (shared list)

- All
- Star
- Tube
- Reading
- Chandelier
- Polaroid Clock

### Room groups (dynamic membership)

- `light.living_room_group`
- `light.dining_room_group`
- `light.kitchen_group`
- `light.bedroom_group`

## Tunable configuration (build‑time)

- **Preferred location**: a separate config file read at build time.
- **Fallback**: main YAML/Python config if a separate file is not used.
- The list below is the single, organized set of tunables to surface.

### Input + timing

- `ENCODER_TRANSITIONS_PER_DETENT` (default **2**): quadrature transitions per detent (hardware‑specific).
- `ENCODER_STEPS_PER_DETENT` (default **1**): how many delta steps are emitted for each physical click of the encoder.
- `ENCODER_RATE_LIMIT_HZ` (default **2**): max encoder updates per second per control (volume/bass/treble).
- `BACK_LONG_PRESS_MS` (default **1000**): press duration that triggers **Home**.
- `INPUT_SCAN_INTERVAL_MS` (default **library‑recommended**): keep the library’s default for smoothness; tune only if needed.
- `DEBOUNCE_MS` (default **library‑recommended**): keep the library’s default for smoothness; tune only if needed.
- `ANALOG_REPORT_DELTA` (default **64**): minimum ADS1015 change before sending a new value.
- `ANALOG_REPORT_INTERVAL_MS` (default **30**): minimum time between analog reports.

### Audio polling + screensaver

- `AUDIO_POLL_INTERVAL_MS` (default **30000**): warm poll interval for audio state.
- `AUDIO_WAKE_WINDOW_MS` (default **10000**): active window after audio activity.
- `SCREENSAVER_IDLE_MS` (default **30000**): idle time before Now Playing screensaver.
- `SCREENSAVER_UPDATE_MS` (default **1000**): metadata/render refresh cadence.
- `NOW_PLAYING_FONT_SIZE` (default **11**): readable title font (Roboto, v1 baseline).
- `NOW_PLAYING_SMALL_FONT_SIZE` (default **8**): sub‑line font for artist/album.
- `SCROLL_SPEED_MS` (default **200**): Now Playing scroll speed.
- `SCROLL_GAP_PX` (default **12**): gap between scrolling repeats.

### Build-time package toggle (rings)

- Toggle the package include in `control-board-esp32.yaml`:
  - `control-board-peripherals.yaml` (rings enabled)
  - `control-board-peripherals-no-rings.yaml` (rings disabled)

### LED rings

- `HUE_RING_TYPE` (default **WS2812**)
- `HUE_RING_LED_COUNT` (default **8**)
- `HUE_RING_IDLE_BRIGHTNESS` (default **10%**)
- `HUE_RING_ACTIVE_BRIGHTNESS` (default **80%**)
- `HUE_RING_SLEEP_MS` (default **15000**): time after last activity to fully dim/off.
- `HUE_RING_UPDATE_HZ` (**TBD**)
- `AUDIO_RING_TYPE` (default **WS2812**)
- `AUDIO_RING_LED_COUNT` (default **8**)
- `AUDIO_RING_IDLE_BRIGHTNESS` (default **10%**)
- `AUDIO_RING_ACTIVE_BRIGHTNESS` (default **80%**)
- `AUDIO_RING_SLEEP_MS` (default **15000**): time after last activity to fully dim/off.
- `AUDIO_RING_UPDATE_HZ` (**TBD**)

### UART (audio)

- `UART_BAUD` (default **115200**)

## Hardware layout (recommended)

### Core controls

- **Encoders**
  - **Lighting encoder**: turn = Hue/Saturation, press = toggle Hue ↔ Saturation
  - **Main/Menu encoder**: screen/menu navigation + select/confirm
- **Pots + sliders**
  - **Volume pot**: always‑active volume
  - **EQ pots**: bass / mid / treble
  - **Lighting brightness slider**: HSB brightness (slider = B)

### Buttons (hard‑wired)

- **Room select**: single button cycles rooms (screen shows current room)
- **Audio transport**: Play/Pause, Next, Prev
- **Audio source**: single toggle (Wi‑Fi ↔ Bluetooth)
- **Mute**
- **Back** (long‑press = Home)
- **Home** (autocal trigger only; no UART event)

### Optional

- Small OLED per section (or split screen) for clear context
- LED ring around audio knob for volume feedback
- LED ring around lighting encoder for Hue/Saturation feedback
- Capacitive touch strip for quick dimming (optional)

## Hardware list (v2)

### Core electronics

- **Main MCU**: ESP32-S3 N16R8 Gold Edition Dev Board (16MB Flash / 8MB PSRAM)
- **Input MCU**: Adafruit Feather RP2040
- **Power**: 5V rail + 3.3V regulation (exact regulator TBD)
- **UART link**: RP2040 ↔ ESP32-S3 (event packets only)

### I2C buses (two independent buses)

- **RP2040 I2C (inputs only)**
  - **PCF8575** (16‑bit GPIO expander) — first detected from `0x20/0x21` (buttons only)
  - **ADS1015** (12‑bit ADC) — optional (external ADC)
  - **Seesaw** (STEMMA QT encoders) — 2 devices (Menu + Lighting)
  - 4.7 kΩ pull‑ups to 3.3 V required if modules lack them
- **ESP32‑S3 I2C (UI only)**
  - **OLED**: SSD1306/SSD1309 128×64 I2C (single screen)
  - Address, pins, and bus speed are unchanged from v1 implementation

### Inputs

- **Lighting encoder** → Seesaw (`0x37`, encoder + press)
- **Main/Menu encoder** → Seesaw (`0x36`, encoder + press)
- **Lighting brightness slider** (10k potentiometer) → ADS1015 channel 1
- **Volume pot** (10k potentiometer) → ADS1015 channel 2
- **EQ pots** → ADS1015 channels 0 (bass) + 3 (treble) + RP2040 A0 (mid)
- **Buttons** (all hard‑wired to PCF8575)
  - Room select (cycle)
  - Audio transport: Play/Pause, Next, Prev
  - Audio source toggle (Wi‑Fi ↔ Bluetooth)
  - Mute
  - Back (long‑press = Home)
  - Home (autocal trigger only; no UART event)

### Lighting outputs / feedback

- **Status RGB LED** (addressable)
- **Audio LED ring** for volume feedback (size TBD)
- **Hue/Sat LED ring** around lighting encoder (size TBD)

### Optional inputs / sensors

- Capacitive touch strip (quick dimming)
- Any room sensors (future)

## Safer menu system (guard‑rails)

- **Two top‑level modes only**: Lighting | Audio
- **Screen focus follows activity** (audio/lighting interaction switches the screen to that side)
- **Buttons are primary** for rooms/transport/source/mute; menus are secondary.
- **No auto‑arming** on menu entry
- **Pickup logic always required** for sliders/knobs
- **Persistent Back** everywhere; **Home via Back long‑press**
- **Explicit state banners** (e.g., “Audio Controls Active”)
- **Audio menu items**: Source, Now Playing (screensaver), Options
- **Lighting menu items**: Room list (populated from HA), Presets, H/S control, Brightness

## UART event contract (RP2040 → ESP32‑S3)

- **Events only**; ESP32‑S3 owns state and UI.
- Packet format remains 10 bytes:
  - Header: `0xAA 0x55`
  - Type: `0x01` button, `0x02` analog, `0x03` encoder delta
  - ID: 0–255
  - Timestamp: 32‑bit big‑endian ms
  - Value: 16‑bit big‑endian
    - **Button**: `0` = release, `1` = press
    - **Analog**: 0–65535
    - **Encoder delta**: signed 16‑bit (two’s complement), **+1/‑1 per detent**

### UART event notes

- RP2040 handles debounce + quadrature decoding and emits **delta steps** only.
- ESP32‑S3 never processes A/B edges directly.
- Long‑press behavior is derived on ESP32‑S3 using timestamps.
- **Implementation note**: current `code.py` emits **binary UART packets** (v2 format).

## CircuitPython firmware (RP2040) — current behavior (as of 2026-04-10)

> Source: `/media/cory/CIRCUITPY/code.py`, `/media/cory/CIRCUITPY/boot.py`, `/media/cory/CIRCUITPY/settings.toml`.

### Boot behavior

- `boot.py` enables both USB serial **console + data** (`usb_cdc.enable(console=True, data=True)`).
- No USB mass‑storage remount logic in `boot.py`.

### Input topology (current wiring expectations)

- **I2C bus**: `board.SCL` / `board.SDA` (single bus for PCF8575 + seesaw + ADS1015).
- **PCF8575**: first detected address from `[0x20, 0x21]` (single expander used for buttons).
- **Seesaw encoders** (I2C STEMMA QT):
  - Menu: `0x36` → delta id **2**, press id **21**
  - Lighting: `0x37` → delta id **1**, press id **20**
- **Buttons via PCF8575** (bit → logical name → event id):
  - P0 room → **31**
  - P1 source → **35**
  - P2 back → **36**
  - P3 home → **no UART event** (autocal trigger only)
  - P4 prev → **34**
  - P5 play → **32**
  - P6 next → **33**
  - P7 mute → **22**

### Analog inputs (current configuration)

- **ADC mode**: `ADC_MODE = "external"` (expects ADS1015 at `0x48`).
- **External ADS1015 channels**:
  - ch0 → `eq_bass_pot` (event **104**)
  - ch1 → `lighting_slider` (event **101**)
  - ch2 → `volume_pot` (event **102**)
  - ch3 → `eq_treble_pot` (event **106**)
- **Internal ADC**:
  - `board.A0` → `eq_mid_pot` (event **105**)
- **Output mode**: `percent` (0–100). Default scale for external ADC is **0–26367** raw.
- **Analog filters**: median window (3), EMA (slow/fast), min raw delta = 2, min output delta = 2, send interval = 20 ms.
- **Snap‑to‑edge**: lighting slider snaps to 0%/100% within 2% by name.

### Calibration status

- Calibration uses `/calibration.json`.
- Autocal is **disabled** by default.
- **Calibration tracking is enabled** for EQ pots and can update `/calibration.json` when enough samples are collected.

### UART packet format (RP2040 → ESP32‑S3)

- Packet length = **10 bytes**: `0xAA 0x55` + type + id + timestamp(4) + value(2).
- Types:
  - `0x01` = button
  - `0x02` = analog
  - `0x03` = encoder delta
  - `0xF0` = debug (suppressed if `DEBUG_GLOBAL = False`)
- Encoder deltas use `ENCODER_TRANSITIONS_PER_DETENT = 1`, `ENCODER_STEPS_PER_DETENT = 1`.

### Debugging behavior

- Global debug on UART + serial is **enabled** (`DEBUG_GLOBAL = True`, `DEBUG_UART = True`).
- Periodic debug packets every **1000 ms** unless idle suppress triggers.
- Analog debug prints enabled; button debug prints disabled by default.

### Settings file

- `/media/cory/CIRCUITPY/settings.toml` is currently **empty**.

## Audio polling, wakeup, and LED ring behavior

- **ESP32‑S3 owns the LED ring** (only device with HA/Wi‑Fi context).
- **Hardware audio control** is **TCP-only** (custom `arylic_tcp`), routed by MA active target.
- **Now‑playing metadata** is **always read from MA active sensors** (`sensor.ma_active_*`).
- Do **not** rely on UART metadata; MA sensors are the source of truth.
- **Warm polling**: ESP32‑S3 periodically polls audio state so volume is always ready to render.
  - Default **volume poll interval**: **30 seconds** (make tunable at top‑level config).
  - Polling mechanism should be **generic/extensible** for additional entities later.
- **Audio‑active wakeup**: enter active mode when any of the following occur:
  - Any audio button/encoder event
  - Audio playing state is true
  - Audio menu/screen is focused
  - Recent audio activity within a **10s** wake window (tunable)
- **Sleep behavior**: when lighting is active and none of the audio‑active conditions are true, audio polling can stay at the idle rate.
- **Immediate sync on audio actions**: any audio transport action (Next/Prev/Play/Pause/Mute) should **trigger a volume refresh** so the ring always reflects the true state.

### LED ring brightness states (defaults, tunable)

- **Idle glow** while audio controls are active: **10%** brightness (constant, no pulsing).
- **Active interaction** (changing volume): **80%** brightness (TBD, tune later).

### Volume pot + ring sync

- On **first interaction**, request current volume and **render ring to true volume**.
- Pot changes apply relative to the **current ring position** (no jumps).
- If a volume read fails, **fallback to last known volume** and continue at idle glow (no pulsing).

## Hue/Saturation LED ring behavior (lighting encoder)

- **Hardware**: WS2812 ring around the lighting encoder (LED count TBD, tunable).
- **Activation**: ring is active only when the lighting encoder is in **Hue** or **Saturation** mode.
- **Hue mode**:
  - Ring displays a **full color wheel** with the **leading edge** representing the **current hue**.
  - On activation, the ring should **snap to the light’s current hue** (from HA state).
  - Encoder delta steps rotate the wheel; each step updates ring + light hue.
- **Saturation mode (default behavior)**:
  - Ring shows the **current hue** with **brightness/intensity mapped to saturation** (0% = white/off, 100% = full hue).
  - Encoder deltas adjust saturation and immediately update the ring + light.
- **Pickup logic** still applies before changes are sent.

## Lighting screen behavior

- **No Hue/Sat bar** on screen (the ring is the visual indicator).
- Screen should show **Selected Light/Room** + **Mode** (Hue or Saturation).
- **Brightness slider** should show a **bar graph + %** while moving and should **exit menus** on adjustment.
- **Presets** should display a short toast/label on change.

## Audio screensaver (v1 parity)

- If **audio is playing** and **idle time > SCREENSAVER_IDLE_MS** (default **30s**), switch to **Now Playing** screensaver.
- Show title/artist (scrolling) and transport icons (Play/Pause/Next/Prev).
- **Progress bar** is driven by MA active sensors (`sensor.ma_active_duration`, `sensor.ma_active_position`). If any are missing, the bar is hidden.
- Volume is represented by the **LED ring**; no dedicated volume screen.
- Update metadata/rendering on a 1s cadence (tunable).
- Any user input exits screensaver and restores the last focused mode.
- If **nothing is playing**, **turn screen off** after idle; wake on input.

## Metadata strategy (best effort)

- **Control path** is **TCP-only** (custom `arylic_tcp`), routed by MA active target.
- **Now‑playing metadata** is **always read from MA active sensors** (`sensor.ma_active_*`).
- If metadata is missing, display **source + playback state** and keep last known title/artist if available.
- If source is **AirPlay** and metadata is missing, show **“TV”** as the status label.
- ESPHome treats **AirPlay** sources as **ambiguous** locally to force the hardware target prompt.
- HA can also force ambiguity by listing Apple TV entities in `input_text.ma_ambiguous_entities` (comma-separated).
- The target prompt stays visible until ambiguity clears (selection resolves); it does not time out while active.
- When ambiguity flips on and no sticky lock is active, ESPHome raises the prompt immediately (no hardware interaction required).

## Input inventory (current)

Use **Pin maps (current firmware)** above as the single source of truth. All older draft maps and placeholder wiring tables have been removed to prevent conflicts.

## Notes / open questions

- Confirm final input ID map for PCF8575 bit indices (buttons only) **after parts/pre‑assembly/testing**.
- Confirm ADS1015 channel allocation and scaling ranges per slider.
- Confirm OLED address and ESP32‑S3 I2C pin assignment (reuse v1).
- Confirm audio polling defaults (30s idle interval, 10s wake window) and ensure they remain tunable.

## Open items / closure checklist

- [ ] Confirm **encoder detent resolution** (default 1 step per detent) and any acceleration curve.
- [ ] Use **library‑recommended** scan interval + debounce timing unless tuning is needed.
- [ ] Finalize **PCF8575 pin map** (expander #, bit index per input) and confirm whether `0x21` will be used.
- [ ] Finalize **ADS1015 scaling** (min/max voltage, inversion, dead‑zone, mapping to 0–65535).
- [ ] Specify **LED ring LED counts** (audio + hue), **data pins**, and **update rate/curve**.
- [ ] Document **UART `STA;` response format + units** and confirm parsing against Arylic UART API.
- [ ] Confirm **UART source list** and which sources are valid for the chosen module (per Arylic UART API).
- [ ] Define **room/preset selection model** (button vs menu sync) in a dedicated deep‑dive before coding.

## Handoff checklist for implementer

### Audio control path (TCP + MA active target) — current

- **Volume/EQ control**: **direct TCP** via custom `arylic_tcp` (no UART, no HA volume_set).
- **Transport actions**: **through integration** (HA services to MA active target).
- **Target resolution**: HA publishes `sensor.ma_control_hosts`/`sensor.ma_control_port` for the active target.
- **Rate limiting**: encoder updates capped at **2 updates/sec** (tunable).
- **Polling**: use periodic HA refresh of the **active MA target** for progress/metadata integrity.

### Legacy UART notes (not used in current build)

- **Reference**: [Arylic UART API](https://developer.arylic.com/uartapi/#uart-api)
- Keep for future UART builds; do **not** assume UART control in the current TCP-only firmware.

### Volume pot + LED ring

- **No slider**. Volume pot + LED ring only.
- On first interaction, **query current volume** and snap ring to true value.
- Pot changes apply relative to synced volume (no jumps).
- Immediate volume refresh after transport actions.

### Polling

- Warm polling for volume and audio state every **30s** (tunable).
- Wake mode for **10s** after audio activity (tunable).
- Keep polling framework **extensible** for more entities later.

### MA/HA usage

- Use **HA (`ha_audio_player`) for all now‑playing metadata** (title/artist/album/source/app/state).
- Multi‑client environment is expected (AirPlay/BT/Wi‑Fi/MA); metadata may be missing or stale.
- Do **not** use MA/HA for core transport/volume/mute actions.

## Detailed Arylic UART API integration (legacy / optional)

- **Reference**: [Arylic UART API](https://developer.arylic.com/uartapi/#uart-api) (source of truth; **no guessing**).

### UART transport basics

- **Legacy control path** kept for reference; current firmware is **TCP-only**.
- **Port settings**: `115200 8N1`, no flow control.
- **Framing**: each message must end with `;`.
- **Message form**: `CMD[:param];`
- **Asynchronous updates**: device may send state updates without a request; the host must parse and update cache.

### Core UART commands we will use

#### Status / sync

- **STA;** — status summary.
  - **Format**: `STA:{source},{mute},{volume},{treble},{bass},{net},{internet},{playing},{led},{upgrading}`
  - **Example**: `STA:NET,0,33,-2,0,1,1,1,1,0`
  - **Units/ranges**:
    - `volume`: 0–100
    - `treble` / `bass`: -10..10 (dB)

#### Transport

- **POP;** — play/pause toggle
- **NXT;** — next track
- **PRE;** — previous track
- **SRC:{source};** — set input source
  - **Valid sources** (module‑dependent):
    - `NET` (network)
    - `BT` (bluetooth)
    - `USBDAC` (USB DAC)
    - `LINE-IN` (line‑in)
    - `OPT` (optical)
    - `COAX` (coaxial)
    - `LINE-IN2` (extra line‑in)
    - `OPT2` (extra optical)
    - `COAX2` (extra coaxial)
    - `HDMI` (HDMI ARC)
  - Prefer querying supported sources via UART when available (see `LST` in Arylic UART API).

#### Audio controls

- **VOL:<0-100>;** — set volume
- **MUT:1;** / **MUT:0;** — mute/unmute
- **BAS:<-10..10>;** — set bass (dB)
- **TRE:<-10..10>;** — set treble (dB)

### UART polling and flood control

- **Warm state**: periodically query `STA;` to refresh cached audio state when idle.
- **Audio‑active wake**: when any audio input occurs, allow more frequent `STA;` polls for the wake window.
- **Encoder rate‑limit**: cap tone/volume updates to **2 per second**; accumulate deltas between sends.
- **Error handling**: if UART parse fails, keep last known state and retry on next poll.
