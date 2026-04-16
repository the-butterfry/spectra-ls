# v-next NOTES — Hardware-First Control Plan (Implementation Guide)

> Scope: Hardware-driven UX redesign for Spectra LS Control Board v2.
> Audience: Implementation agent working across RP2040 CircuitPython + ESPHome packages + HA helpers.
> Status: Draft plan. Update as decisions solidify.

## Goals (what success looks like)

1. **Hardware-first UX**: physical selectors + momentaries drive modes/targets; OLED follows hardware state.
2. **Menu is fallback**: menu encoder remains functional, but hardware changes reassert control.
3. **Generalizable**: works for installs with 1–N rooms and multiple audio targets.
4. **Deterministic**: hardware switch positions always map to clear actions, no ambiguous prompts.

## Current Input Inventory (baseline)

### Digital (PCF8575 @ 0x20)
- P0 `room` → event 31
- P1 `source` → event 35
- P2 `back` → event 36
- P3 `home` → no event (autocal trigger only)
- P4 `prev` → event 34
- P5 `play` → event 32
- P6 `next` → event 33
- P7 `mute` → event 22
- P8 `select` → event 37
- **Spare**: P9–P15 (7 inputs)

### Encoders (Seesaw)
- Menu encoder: delta id 2, press id 21
- Lighting encoder: delta id 1, press id 20

### Analog (ADS1015 + internal ADC)
- ADS1015 ch0: eq_bass_pot → 104
- ADS1015 ch1: lighting_slider → 101
- ADS1015 ch2: volume_pot → 102
- ADS1015 ch3: eq_treble_pot → 106
- RP2040 A0: eq_mid_pot → 105
- **Spare**: RP2040 A1

### Expansion allowed
- Add I2C expanders/ADCs as needed (PCF8575 @ 0x21, ADS7830 @ 0x49 recommended).

---

## Proposed Hardware Model (Mode + Target + Action)

### 5-way selector = **Mode Selector**
Suggested mapping (generalizable across installs):

1. **Lighting Rooms**
   - Momentary: cycle room list
   - Encoder: brightness or hue/sat (depending on sub-mode)

2. **Lighting Targets**
   - Momentary: cycle target list within selected room
   - Encoder: adjust selected target (brightness or hue/sat)

3. **Audio Targets**
   - Momentary: cycle hardware audio targets (MA/HA list)
   - Encoder: volume (always)

4. **Audio Transport**
   - Momentary: play/pause, prev/next
   - Encoder: volume (always)

5. **System / Meta**
   - Momentary: cycle meta source or control-target prompt
   - Encoder: meta select or diagnostic/utility

### 3-way switch = **Audio Control Class**
- **Auto**: HA/MA logic chooses target
- **Primary Hardware**: local Spectra LS (or primary device)
- **Room Hardware**: optional room device

### Momentary buttons
- **Primary momentary**: “Next” within mode
- **Secondary momentary**: “Back/Reverse” or “Confirm”
- Long-press on Back remains Home

---

## Implementation Plan (Agent Instructions)

### Phase 1 — RP2040 CircuitPython (input scanning)

**Files**: `/media/cory/CIRCUITPY/code.py` (and control-py copy)

1. **Add selector input**
   - Choose one:
     - **Resistor ladder** on ADS7830 (recommended)
     - Discrete GPIOs on PCF8575 (uses 5 pins)
   - If ladder:
     - Add ADS7830 driver + detection
     - Add analog channel `mode_selector` with hysteresis
     - Map 5 ADC bands → positions 0–4
     - Emit event `MODE_SELECTOR_ID` as **position index** (0–4)

2. **Add 3-way control-class switch**
   - Prefer discrete pins on PCF8575
   - Emit event `CONTROL_CLASS_ID` as 0–2

3. **Add momentary inputs**
   - Assign spare PCF pins
   - Emit button events for `next_mode_item`, `prev_mode_item`, `confirm`

4. **Event ID assignments**
   - Pick new IDs in an unused range (e.g., 120–129)
   - Document in this file and in NOTES-control-board-2.md

5. **Edge-triggered events**
   - Only send on change to prevent flooding
   - Debounce using existing Debouncer

---

### Phase 2 — ESPHome (ESP32-S3)

**Files**:
- `/config/esphome/control-py/packages/control-board-hardware.yaml`
- `/config/esphome/control-py/packages/control-board-ui.yaml`

1. **Add sensors / binary_sensors for new events**
   - `mode_selector` (0–4)
   - `control_class` (0–2)
   - momentary events

2. **Add global “hardware_mode” state**
   - Enum values 0–4 (match selector)
   - Stored in globals; updated on mode selector event

3. **OLED behavior**
   - When selector changes: swap screen to mode-specific layout
   - Show current mode + target at top

4. **Menu override behavior**
   - Menu encoder activity sets `menu_override_active = true`
   - Any hardware selector change clears override
   - OLED returns to hardware mode view

5. **Control routing**
   - Lighting modes: drive `input_select.control_board_room/target`
   - Audio targets: drive `input_select.ma_active_target` or target helper
   - System/meta: trigger meta override or target prompt

---

### Phase 3 — Home Assistant helpers

1. **Audio targets**
   - Use `input_select.ma_active_target` for actual targets
   - Add `input_text` helpers if you want labels per selector position

2. **Lighting targets**
   - Ensure `sensor.control_board_room_options` and `sensor.control_board_target_options` are valid

---

## Wiring / Hardware Choices

### Recommended 5-way selector approach
- **Resistor ladder** into ADS7830 channel
- ADS7830 @ **0x49** to avoid ADS1015 conflict
- Use deadbands between thresholds to avoid chatter

### Alternate approach
- Discrete 5 pins on PCF8575 (P9–P13)
- Requires more GPIO, but simpler firmware

---

## Acceptance Criteria

- Changing selector positions updates OLED within 100–200ms.
- Hardware mode always overrides menu when selector changes.
- Audio target switch positions never show “control target prompt.”
- No event flooding from selector or 3-way switch.
- All mappings documented in NOTES-control-board-2.md + CHANGELOG when implemented.

---

## Next Decisions (required before coding)

1. **Selector implementation**: ladder + ADS7830 vs discrete pins
2. **Final mode list**: confirm 5 positions
3. **Event ID allocation**: reserve IDs and document
4. **HA helper mapping**: labels for targets and rooms

---

## Working Notes (update as we go)

- Menu encoder remains fallback; hardware selector reasserts state.
- Expansion via ADS7830/PCF8575 is allowed.
- Ensure selector states map cleanly to HA target lists across multi-room installs.
