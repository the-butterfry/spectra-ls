# Control Board v2 Baseline Architecture (v2.0)

**Scope:** Current production baseline on ESPHome 2026.03.21.x. This document freezes the *existing* architecture, behaviors, and known ownership conflicts for reference during the v3 refactor.

**Goal of v2:** A multi-input control board that merges Arylic + HA/MA metadata into a single OLED UI + input experience, with menus and lighting control sharing the same UX surface.

---

## System Overview

**Hardware:** ESP32-S3 + RP2040 (UART input hub)

**Primary subsystems:**
- **Audio/Meta** (Arylic TCP/HTTP + HA/MA metadata)
- **UI/Display** (OLED state machine + menu inputs)
- **Lighting** (HA light targets with local selectors)
- **System** (shared globals + intervals + logging)

**Primary files:**
- `control-board-peripherals-no-rings.yaml` — OLED display logic, now-playing pipeline, menu rendering
- `packages/control-board-system.yaml` — globals, intervals, log/status, input bookkeeping
- `packages/control-board-audio.yaml` — audio I/O, HA/MA metadata, Arylic control + pot/encoder behavior
- `packages/control-board-ui.yaml` — menu inputs, encoder navigation, UI helper sensors

---

## v2 Execution Model (Current)

### Data Flow (as implemented)
1. **Inputs** (RP2040 UART): buttons, encoders, analog pots → update globals (menu, input timing, lighting, audio)
2. **Metadata**: HA/MA + Arylic TCP/HTTP → update caches + last_meta timestamps
3. **Display**: OLED lambda computes playing state, selects meta, manages screen state, renders UI
4. **Intervals**: system intervals also update `screensaver_active` based on audio + idle state

### Compute vs Render (Current)
- **Compute and render are mixed** in the OLED lambda:
  - playback predicate (`playing`) derived from multiple sources
  - meta selection occurs in render path
  - UI state transitions happen inside render

---

## Shared State (Ownership Conflicts)

### Conflicting writers
| Shared Global | Current Writers | Notes |
|---|---|---|
| `screensaver_active` | OLED display lambda + `control-board-system.yaml` interval + `note_user_input` | Multiple owners; divergence occurs during playback/idle logic. |
| `screen_mode` | OLED lambda + UI scripts + audio scripts | Competing writes based on menu/audio/lights. |
| `menu_active` | OLED lambda + UI scripts + audio scripts | Render path forces menu changes. |
| `last_input_ms` | UI scripts + audio input flows | Mixed semantics (input vs screen wake). |
| `playing` predicate | OLED lambda + system log (Arylic only) | UI and logs disagree on “playing”. |

### Consequence
- “Now Playing” can blank or yield to screensaver even when audio is active.
- Status logging reports `play=0` while UI considers playing.

---

## v2 Playback Predicate (Current)

**Locations:**
- OLED lambda in `control-board-peripherals-no-rings.yaml`
- System interval in `control-board-system.yaml` (screensaver logic)
- Status logger in `control-board-system.yaml` (Arylic only)

**Sources used:**
- HA media player states (6 slots)
- Arylic play states (TCP/HTTP + left/right)
- Meta recency timestamps

---

## v2 Display Flow (Current)

**Display states:**
- Splash → Boot Menu → Menu → Now Playing → Lighting → Screensaver → Blank

**Decision order (current):**
- Boot menu if within boot window
- Menu if active
- Now Playing if screen_mode==1 and playing or audio_wake
- Lighting if screen_mode==0 and lighting-active
- Screensaver if idle threshold exceeded
- Blank otherwise

**Note:** screensaver is also set elsewhere and not fully owned by the display state machine.

---

## v2 Meta Selection (Current)

Meta selection is computed in OLED render path using:
- Slot active detection (state active + recency + duration/position sanity)
- Priority rules (playing → state active → meta freshness)
- Optional override via meta select

This works but is **tightly coupled to render**, making testing and reuse difficult.

---

## v2 Invariants (Must Preserve)

- Existing grace windows and timing constants are respected:
  - `meta_playing_grace_ms`, `meta_stale_ms`, `meta_pos_stall_ms`, `screensaver_idle_ms`, etc.
- Menu navigation is unchanged; calibration UI is removed (RP2040 still applies `/calibration.json`).
- Audio controls continue to function (volume/encoders). 
- HA/MA inputs remain the authoritative source of metadata when present.

---

## v2 Known Pain Points (Architectural)

- **Multiple writers** to the same display-related globals.
- **Render path side-effects** (state transitions inside OLED lambda).
- **Distributed playback predicate** (UI vs logs vs screensaver mismatch).
- **Meta selection and rendering tightly coupled**.

---

## v2 Summary

This baseline is stable but structurally fragile. The v3 refactor will preserve visible behavior while **centralizing ownership**, **separating compute from render**, and **making playback intent authoritative** across UI/logging/screensaver logic.
