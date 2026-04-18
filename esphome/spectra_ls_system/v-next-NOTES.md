<!-- Description: v-next implementation notes for Spectra LS System hardware-first control plan and migration policy. -->
<!-- Version: 2026.04.17.14 -->
<!-- Last updated: 2026-04-17 -->

# v-next NOTES — Hardware-First Control Plan (Implementation Guide)

> Scope: Hardware-driven UX redesign for Spectra LS Control Board v2.
> Audience: Implementation agent working across RP2040 CircuitPython + ESPHome packages + HA helpers.
> Status: Draft plan. Update as decisions solidify.

## Latest Contract Update (Lighting)

- Lighting room/target helper surfaces now follow a **catalog-first** contract in HA package logic:
  - Build eligible lights from `states.light` + `area_id(...)`.
  - Resolve room options, target options, target entity mapping, and room state helpers from that shared catalog.
- Intent: eliminate drift and intermittent `All`-only target regressions caused by duplicated direct `area_entities(...)` scan logic across multiple templates.

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
5. **Crossfade/Balance slider mode (v-next)**: one slider surface with mode-aware behavior — room-to-room balance in multi-room mode, and left/right speaker balance in single-room mode.

## v-next Feature Requirement — Crossfade / Balance Slider

This is a required top-line feature for v-next.

- In **multi-room mode**, the slider controls **volume balance between rooms** (crossfade-style weighting), not just a global absolute level.
- In **single-room mode**, the slider controls **left/right speaker balance** for that room.
- Mode-to-slider behavior must be explicit on OLED so users always know whether they are balancing rooms or balancing speakers.

Implementation notes (planning contract):

- Add a normalized slider value domain (for example `-100..100`) for directional balance semantics.
- Multi-room balance path should map slider direction into weighted per-room gain adjustments with clamping and rate limiting.
- Single-room balance path should map slider direction into stereo L/R balance (or equivalent device-supported control path).
- Keep fallback behavior safe: if a target path does not support balance controls, hold current mix and expose a clear UI/status notice.

## HDMI ARC Ingest + Final DAC Path (Active Hardware Note)

- Spectra Level / Source should be treated as a **fully integrated high-fidelity system path** (ingest + routing + conversion), not a DAC-only feature claim.
- ES9038Q2M capability is framed as the final conversion stage in a broader source-to-output architecture optimized for signal integrity and deterministic control routing.

- Source path includes **HDMI input from an ARC-capable source**.
- ARC digital audio is split/extracted and carried as the digital program feed into the final conversion stage.
- Final output conversion target is the **ESS ES9038Q2M DAC** (`ESS 9038Q2M`).
- Output capability target for this path: **192kHz / 24-bit**.
- Expected codec/file compatibility on the digital playback chain:
  - `FLAC`
  - `MP3`
  - `AAC`
  - `AAC+`
  - `ALAC`
  - `APE`
  - `WAV`

Implementation guidance:

- Treat ARC ingest as part of source-path selection/routing validation (same deterministic control-path rules as other sources).
- Keep this note in sync with README hardware reference to avoid drift in published hardware capabilities.

## MA/HA Discovery + Control Routing Contract (Active)

- Discovery-first is the baseline: newly discovered compatible players should appear without requiring static per-site host mapping edits.
- Static/manual host mapping remains as a safety fallback only and should be **disabled by default** to keep no-override testing honest.
- Every discovered/selected target must be classified into a control routing class before command send:
  - `linkplay_tcp` (supported now)
  - `other` (placeholder for future code paths)
- Override entries should carry full routing metadata to match discovery data quality:
  - `hardware_family` (example: `linkplay`)
  - `control_path` (example: `linkplay_tcp`)
  - `control_capable` (boolean; can receive direct hardware controls like POT/EQ)
  - `capabilities` (optional list for control feature matrix)
- Command dispatch must follow control class, not just host presence, so unsupported classes are visible but not incorrectly routed.

## Control-Path + Hardware-Family Roadmap (As-Wired + Next)

### Current wiring snapshot (implemented)

- Discovery-first target onboarding is active via MA player data and HA entity attributes.
- Manual/static fallback routing is opt-in and defaults off via `input_boolean.ma_control_fallback_enabled`.
- Active target routing surfaces:
  - `sensor.ma_active_control_path`
  - `binary_sensor.ma_active_control_capable`
  - `sensor.ma_control_hosts`
- Override metadata contract is wired in `packages/spectra_ls_setup.yaml` room entries and extra JSON:
  - `hardware_family`
  - `control_path`
  - `control_capable`
  - `capabilities`
- Currently supported dispatch path:
  - `linkplay_tcp` (control-capable targets only)
- Non-supported path behavior:
  - tagged as `other`
  - visible for diagnostics/selection context
  - intentionally not routed for direct control sends

### Family/codepath roadmap

1. **Phase R1 — LinkPlay hardening (now)**
    - Keep `linkplay_tcp` as the only routed path.
    - Expand `capabilities` usage from informational to enforced feature gates (for example EQ, source cycle, transport subfeatures).

2. **Phase R2 — Additional family onboarding**
    - Add first non-LinkPlay family tag under `hardware_family`.
    - Introduce dedicated `control_path` value for that family (do not reuse `linkplay_tcp`).
    - Route only after a family-specific command adapter exists.

3. **Phase R3 — Capability matrix routing**
    - Move from boolean `control_capable` to per-feature capability routing decisions using `capabilities`.
    - Gate each direct hardware command type by both `control_path` and required capability.

4. **Phase R4 — Unified adapter contract**
    - Standardize a per-family adapter interface so new paths plug into the same decision layer.
    - Maintain discovery-first default and fallback-off policy across all families.

### No-go guardrails for future families

- Do not route a new `control_path` until:
  - host/endpoint resolution is deterministic,
  - command semantics are validated for that family,
  - `control_capable`/`capabilities` mappings are explicitly defined.

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

- [x] **A1: Path authority check**
  - Planned edit targets must resolve only to `/mnt/homeassistant/esphome/spectra_ls_system.yaml`, `/mnt/homeassistant/esphome/spectra_ls_system/packages/spectra-ls-*.yaml`, `/media/cory/CIRCUITPY/code.py`, and `/mnt/homeassistant/esphome/circuitpy/code.py`.
  - Planned edit targets must exclude `/mnt/homeassistant/esphome/control-py/**` and `/mnt/homeassistant/esphome/control-py/previous/**`.

- [x] **A2: Include wiring check**
  - Verify `spectra_ls_system.yaml` includes only active `spectra-ls-*` package files.
  - Verify include target existence for every referenced package path.

- [x] **A3: RP2040 parity pre-check**
  - Confirm live and mirror firmware files are identical before changes.
  - If drift exists, reconcile parity first and document source-of-truth decision.

- [x] **A4: Event contract reservation**
  - Reserve event ID window for new selector/switch/momentary features.
  - Add an event contract table in this file with columns: `event_id`, `producer`, `consumer`, `notes`.
  - Mark any existing IDs that must not be repurposed.

- [x] **A5: Ownership map**
  - Document owner files for each concern: RP2040 scan/debounce/emit, ESPHome event ingest/state, UI/menu override/render state, and HA helper routing.

- [x] **A6: Safety gates**
  - Define “no-go” conditions (e.g., missing package include target, RP2040 live/mirror mismatch, unresolved legacy path ambiguity).
  - Define rollback actions and restore commands before functional edits.

- [x] **A7: Validation gates for phase transition**
  - Define minimum validation set required to move to Phase B/C.
  - Include expected PASS/WARN behavior for templates and what blocks advancement.

- [ ] **A8: Commit boundary**
  - Keep Phase A commit doc-only (notes + optional changelog pointer) with no behavioral code changes.
  - Push Phase A commit before opening Phase B implementation work.

#### Phase A Verification Snapshot (2026-04-17)

- A1 verified: authoritative target files exist only in `spectra_ls_system` + RP2040 live/mirror paths.
- A2 verified: `spectra_ls_system.yaml` package includes point to active `spectra-ls-*` files with valid include targets.
- A3 verified: RP2040 live/mirror parity is clean.
- RP2040 live SHA256 (`/media/cory/CIRCUITPY/code.py`): `41b9b828bf43556e982d8c035d2ef4fad8589f794ee45dbc3cf79b19736bd647`
- RP2040 mirror SHA256 (`/mnt/homeassistant/esphome/circuitpy/code.py`): `41b9b828bf43556e982d8c035d2ef4fad8589f794ee45dbc3cf79b19736bd647`

#### Event Contract Reservation (Phase A)

Existing event IDs in use (do not repurpose):

- Debug: `0`
- Buttons: `20`, `21`, `22`, `31`–`37`
- Analog controls: `101`, `102`, `104`, `105`, `106`

Reserved window for v-next selector/switch/momentary contract: `120`–`129`

| event_id | producer | consumer | notes |
| --- | --- | --- | --- |
| 120 | RP2040 `code.py` | ESPHome `spectra-ls-hardware.yaml` + `spectra-ls-ui.yaml` | `mode_selector_index` (0–4), edge/event-on-change |
| 121 | RP2040 `code.py` | ESPHome `spectra-ls-hardware.yaml` | `control_class_index` (0–2), edge/event-on-change |
| 122 | RP2040 `code.py` | ESPHome `spectra-ls-ui.yaml` | `mode_next_item` momentary press |
| 123 | RP2040 `code.py` | ESPHome `spectra-ls-ui.yaml` | `mode_prev_item` momentary press |
| 124 | RP2040 `code.py` | ESPHome `spectra-ls-ui.yaml` | `mode_confirm` momentary press |
| 125–129 | Reserved | Reserved | keep unassigned for follow-on controls/long-press variants |

#### Ownership Map (Phase A)

- RP2040 scan/debounce/emit owner:

  - live: `/media/cory/CIRCUITPY/code.py`
  - mirror: `/mnt/homeassistant/esphome/circuitpy/code.py`
- ESPHome event ingest/state owner:

  - `/mnt/homeassistant/esphome/spectra_ls_system/packages/spectra-ls-hardware.yaml`
  - `/mnt/homeassistant/esphome/spectra_ls_system/packages/spectra-ls-system.yaml`
- UI/menu override/render owner:

  - `/mnt/homeassistant/esphome/spectra_ls_system/packages/spectra-ls-ui.yaml`
  - `/mnt/homeassistant/esphome/spectra_ls_system/packages/spectra-ls-peripherals.yaml`
- HA helper/routing owner:

  - `/mnt/homeassistant/packages/ma_control_hub.yaml`
  - `/mnt/homeassistant/packages/ma_control_hub/*.inc`

#### Safety Gates (Phase A)

No-Go conditions before Phase B:

- Any missing include target from `spectra_ls_system.yaml` package map.
- RP2040 live/mirror checksum mismatch.
- Planned edits touching `/mnt/homeassistant/esphome/control-py/**` without explicit request.
- Undefined/overlapping event IDs with existing active IDs.

Rollback baseline and commands (doc-only Phase A / pre-Phase B prep):

- Baseline commit on `main`: `a504d36`
- Full repo rollback to baseline:

  - `cd /mnt/homeassistant && git reset --hard a504d36`
- RP2040 mirror-to-live firmware restore (if live diverges unintentionally):

  - `cp /mnt/homeassistant/esphome/circuitpy/code.py /media/cory/CIRCUITPY/code.py`

#### Validation Gates (A → B/C)

Minimum required PASS set before entering Phase B/C implementation:

- Include map sanity:

  - `spectra_ls_system.yaml` references only existing `spectra-ls-*` packages.
- RP2040 parity sanity:

  - live + mirror `code.py` checksum match at handoff.
- Event contract sanity:

  - no collision between reserved window `120`–`129` and active event IDs.

Expected WARN/PASS interpretation:

- WARN allowed: non-blocking runtime helper naming drift (`control_board_*`) under deferred cleanup policy.
- BLOCKER/No-Go: include target missing, checksum mismatch, event ID collision, or edits outside Phase A scope.

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

### Future Cleanup / Tuning Backlog — Host Inventory + Overrides (Productization)

- [ ] Replace ad hoc host defaults with a single product-scoped host inventory model (canonical source), rather than split per-user root files.
- [ ] Define canonical naming for inventory artifact(s): avoid user/site names; prefer product namespace (e.g., `spectra_ls_host_inventory`).
- [ ] Design host inventory schema to include richer metadata, not just IP:
   - stable device key / logical role (`primary`, `room`, etc.)
   - transport capabilities (TCP/HTTP/UPnP)
   - friendly label(s)
   - optional MAC and firmware/version hints
   - override precedence fields (auto-discovered vs user-pinned)
- [ ] Add a generation path (auto-discovery + synthesis) that can produce/refresh inventory defaults without committing user-specific data.
- [ ] Add a user override layer (manual corrections/augmentations) with explicit merge precedence over discovered values.
- [ ] Ensure generated/override artifacts are local-only by default (ignored in git), while repository keeps only universal templates/examples.
- [ ] Update MA control hub helper wiring to read from canonical inventory surfaces (or derived helpers) instead of hard-coded per-install includes.
- [ ] Add validation checks/scripts for schema integrity and required keys (fail fast on malformed inventory).
- [ ] Add migration notes for existing installs that currently depend on `spectra_ls_primary_tcp_host` / `spectra_ls_room_tcp_host` keys.

Current state note (2026-04-17):

- Root `spectra_ls_primary_tcp_host.yaml` and `spectra_ls_room_tcp_host.yaml` are local-only and untracked from GitHub.
- Active `ma_control_hub` host defaults are secrets-based via `!secret spectra_ls_primary_tcp_host` and `!secret spectra_ls_room_tcp_host`.
- This backlog item is the planned path to evolve from simple host keys to a universal product-grade host inventory/override model.

Phase progression note (2026-04-17 update):

- **Phase B event fidelity fix applied**: RP2040 now emits selector/control-class (`120`, `121`) as `TYPE_ANALOG` packets so index values (0–4 / 0–2) are preserved end-to-end instead of collapsing to boolean button state.
- **Phase C ingest wired (initial)**: `spectra-ls-hardware.yaml` now consumes `120`–`124`, updates global `hardware_mode`/`control_class`, and applies deterministic mode-to-UI routing with menu override clear-on-hardware-change behavior.
- Mode-nav mirrored events (`122`–`124`) are currently scoped to hardware mode 4 (System/Meta) to avoid transport/menu double-trigger conflicts while preserving existing button behavior in other modes.
- **Virtual harness added (temporary diagnostics path)**: `spectra-ls-diagnostics.yaml` now exposes virtual mode/control injectors plus mode-nav test buttons and a one-shot battery script. These invoke shared handler scripts in `spectra-ls-hardware.yaml`, allowing HA-side flow validation without touching RP2040 wiring while preserving a single behavior path.
