<!-- Description: v-next implementation notes for Spectra LS System hardware-first control plan and migration policy. -->
<!-- Version: 2026.04.17.3 -->
<!-- Last updated: 2026-04-17 -->

# v-next NOTES — Hardware-First Control Plan (Implementation Guide)

> Scope: Hardware-driven UX redesign for Spectra LS Control Board v2.
> Audience: Implementation agent working across RP2040 CircuitPython + ESPHome packages + HA helpers.
> Status: Draft plan. Update as decisions solidify.

## Naming Strategy + Deferred Full Cleanup (Entity/Helper IDs)

### Current contract policy (active now)

- File/package naming in active includes should use `spectra-ls-*`.
- Legacy runtime helper/entity IDs (`control_board_*`) remain in place where already deployed.
- This is intentional for operational stability while `spectra_ls_system` reaches full completion.

### Why cleanup is deferred

- Existing Home Assistant artifacts depend on deployed IDs (dashboards/cards, scripts/automations, template sensors, recorder/history/statistics continuity, and external references/service payloads).
- Mid-stream global ID renames carry high outage/regression risk.

### Forward naming rule (effective now)

- For all **new** artifacts, use Spectra naming.
- Files/packages: `spectra-ls-*`.
- Helpers/entities: `spectra_ls_*`.
- Docs/comments: avoid introducing new `control_board_*` names except compatibility references.

### Completion trigger gates (do not run cleanup before all pass)

1. `spectra_ls_system` is functionally complete/stable.
2. Validation templates 1–12 pass consistently in normal operations.
3. No open contract-level MA routing/selector refactors remain.
4. A controlled maintenance window is scheduled.

### Full cleanup execution blueprint (future)

- **Inventory:** build full old→new ID map (`control_board_*` → `spectra_ls_*`) and enumerate all reference paths.
- **Compatibility phase:** introduce `spectra_ls_*` surfaces, mirror/bridge old and new, keep legacy IDs live during burn-in.
- **Validation phase:** verify both legacy + new surfaces PASS before cutover.
- **Cutover phase:** flip all references to `spectra_ls_*`, then retire compatibility shims after sustained PASS windows.
- **Cleanup phase:** remove legacy definitions and preserve migration mapping in docs/changelog.

### Migration-day guardrails

- No ad hoc one-file renames for helper/entity IDs.
- Keep changes atomic per domain (audio, lighting, UI, hardware, MA hub).
- Require rollback path (snapshot + tested restore steps).
- Treat missing helper/script sentinels as blocker.

### Read-depth guidance for future sessions

- Skim-safe default: read this section header/policy only.
- Deep-read required only when explicitly starting migration.
- Migration start trigger phrase: **"start full naming cleanup"**.

## Goals (what success looks like)

1. **Hardware-first UX**: physical selectors + momentaries drive modes/targets; OLED follows hardware state.
2. **Menu is fallback**: menu encoder remains functional, but hardware changes reassert control.
3. **Generalizable**: works for installs with 1–N rooms and multiple audio targets.
4. **Deterministic**: hardware switch positions always map to clear actions, no ambiguous prompts.

## Pathing + Naming Safety Guardrails (Do Not Skip)

### Authoritative edit targets for `spectra_ls_system`

- Path context rule: edit files from host paths (`/mnt/homeassistant/...`), but when writing ESPHome include literals use container paths (`/config/...`).

- ESPHome entrypoint: `/mnt/homeassistant/esphome/spectra_ls_system.yaml`
- Spectra packages only:
  - `/mnt/homeassistant/esphome/spectra_ls_system/packages/spectra-ls-system.yaml`
  - `/mnt/homeassistant/esphome/spectra_ls_system/packages/spectra-ls-hardware.yaml`
  - `/mnt/homeassistant/esphome/spectra_ls_system/packages/spectra-ls-ui.yaml`
  - `/mnt/homeassistant/esphome/spectra_ls_system/packages/spectra-ls-lighting.yaml`
  - `/mnt/homeassistant/esphome/spectra_ls_system/packages/spectra-ls-audio-tcp.yaml`
  - `/mnt/homeassistant/esphome/spectra_ls_system/packages/spectra-ls-diagnostics.yaml`
- RP2040 source-of-truth:
  - live: `/media/cory/CIRCUITPY/code.py`
  - mirror: `/mnt/homeassistant/esphome/circuitpy/code.py`

### Out-of-scope paths for this track (unless explicitly requested)

- `/mnt/homeassistant/esphome/control-py/**` (stabilized v2 line)
- `/mnt/homeassistant/esphome/control-py/previous/**` (archived)
- `/mnt/homeassistant/esphome/spectra_ls_system/NOTES-control-board-2.md` (archived/frozen)

### Naming execution rule

- New files/packages/helpers use Spectra naming (`spectra-ls-*`, `spectra_ls_*`).
- Legacy `control_board_*` runtime IDs remain until dedicated cleanup trigger.
- Never mix ad hoc renames with behavior changes in one patch set.

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

### Execution Phases (commit-scoped)

1. **Phase A — Path-safe scaffolding + event contract reservation**
   - Confirm all target files are in `spectra_ls_system` and `CIRCUITPY` + mirror only.
   - Reserve/record event IDs and mode enum contract in this file.
   - Commit scope: notes + non-behavioral scaffolding only.

#### Phase A Start Checklist (must pass before Phase B)

- [ ] **A1: Path authority check**
  - Planned edit targets must resolve only to `/mnt/homeassistant/esphome/spectra_ls_system.yaml`, `/mnt/homeassistant/esphome/spectra_ls_system/packages/spectra-ls-*.yaml`, `/media/cory/CIRCUITPY/code.py`, and `/mnt/homeassistant/esphome/circuitpy/code.py`.
  - Planned edit targets must exclude `/mnt/homeassistant/esphome/control-py/**` and `/mnt/homeassistant/esphome/control-py/previous/**`.

- [ ] **A2: Include wiring check**
  - Verify `spectra_ls_system.yaml` includes only active `spectra-ls-*` package files.
  - Verify include target existence for every referenced package path.

- [ ] **A3: RP2040 parity pre-check**
  - Confirm live and mirror firmware files are identical before changes.
  - If drift exists, reconcile parity first and document source-of-truth decision.

- [ ] **A4: Event contract reservation**
  - Reserve event ID window for new selector/switch/momentary features.
  - Add an event contract table in this file with columns: `event_id`, `producer`, `consumer`, `notes`.
  - Mark any existing IDs that must not be repurposed.

- [ ] **A5: Ownership map**
  - Document owner files for each concern: RP2040 scan/debounce/emit, ESPHome event ingest/state, UI/menu override/render state, and HA helper routing.

- [ ] **A6: Safety gates**
  - Define “no-go” conditions (e.g., missing package include target, RP2040 live/mirror mismatch, unresolved legacy path ambiguity).
  - Define rollback actions and restore commands before functional edits.

- [ ] **A7: Validation gates for phase transition**
  - Define minimum validation set required to move to Phase B/C.
  - Include expected PASS/WARN behavior for templates and what blocks advancement.

- [ ] **A8: Commit boundary**
  - Keep Phase A commit doc-only (notes + optional changelog pointer) with no behavioral code changes.
  - Push Phase A commit before opening Phase B implementation work.

1. **Phase B — RP2040 input capture**
   - Implement selector/switch/momentary scan + debounce + edge-trigger emit.
   - Update both live `CIRCUITPY` and repo mirror in same change set.
   - Commit scope: RP2040 only (plus notes/changelog as needed).

1. **Phase C — ESPHome mode/state wiring**
   - Wire incoming events into `spectra-ls-hardware.yaml` + `spectra-ls-ui.yaml`.
   - Add `hardware_mode`, menu override clearing, and deterministic route state updates.
   - Commit scope: spectra package files only.

1. **Phase D — HA helper/routing integration**
   - Bind mode transitions to existing helper contracts (`ma_active_target`, room/target selectors).
   - Add only required helper surfaces; avoid broad helper churn.
   - Commit scope: minimal helper/automation updates.

1. **Phase E — Validation + hardening**
   - Run validation templates and confirm pass/warn deltas.
   - Address race/flood/stale-state issues before proceeding.
   - Commit scope: fixes + docs + changelog.

1. **Phase F — Deferred naming cleanup (future trigger only)**
   - Execute only after all trigger gates in naming section are satisfied.
   - Perform compatibility/cutover/cleanup sequence as documented above.

### Phase 1 — RP2040 CircuitPython (input scanning)

**Files**:
- `/media/cory/CIRCUITPY/code.py` (authoritative live firmware)
- `/mnt/homeassistant/esphome/circuitpy/code.py` (required mirror sync in same change set)

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
   - Document in this file (`v-next-NOTES.md`) and `CHANGELOG.md` when applied

5. **Edge-triggered events**
   - Only send on change to prevent flooding
   - Debounce using existing Debouncer

---

### Phase 2 — ESPHome (ESP32-S3)

**Files**:
- `/config/esphome/spectra_ls_system/packages/spectra-ls-hardware.yaml`
- `/config/esphome/spectra_ls_system/packages/spectra-ls-ui.yaml`
- `/config/esphome/spectra_ls_system/packages/spectra-ls-system.yaml` (if shared routing state is needed)

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
- All mappings documented in `v-next-NOTES.md` + `CHANGELOG.md` when implemented.

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
