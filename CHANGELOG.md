<!-- Description: Repository changelog for Home Assistant + ESPHome work. -->
<!-- Version: 2026.04.16.12 -->
<!-- Last updated: 2026-04-16 -->

# Changelog

## 2026-04-16

- ESPHome: Phase 1 rename step on tracked main path — rename active diagnostics package to `spectra-ls-diagnostics.yaml` and repoint `esphome/control-board-esp32-tcp.yaml` include.
- Docs: README description now calls out room/lighting/audio auto-discovery and minimal user configuration expectations.
- Repo/Docs: Stop tracking root `configuration.yaml`; switch to placeholder-based integration via `SPECTRA-HA-CONFIG-PLACEHOLDERS.md` for adding Spectra-specific lines into an existing Home Assistant config.
- Docs: Add bold README project-state banner (active heavy development + publish date) and a current hardware reference section covering MCUs, expanders, control interfaces, and recommended OLED screen profile.
- Docs: Declare `esphome/spectra_ls_system/v-next-NOTES.md` as the `main` branch direction source and require `README.md` alignment to that hardware-first roadmap.
- Docs: Update README elevator pitch to plain-English whole-home audio + lighting focus and add explicit audio clients/player types section (Music Assistant, HA media_player, WiiM integration, Arylic/LinkPlay, AirPlay/Apple TV, Plex optional).
- Docs: Rewrite README project-intent intro to emphasize whole-home audio + lighting control and simplify system interaction language.
- Docs: Add mandatory shared-contract go/no-go checklist (`.github/SHARED-CONTRACT-CHECKLIST.md`) and wire it into branch runbook + Copilot directives.
- Docs: Add top-level repository `README.md` with project intent, architecture interaction summary, key features, and detailed deploy instructions.
- ESPHome: Reduce diagnostics and control-number publish cadence to 30s (`EQ Low/Mid/High`, `Arylic Volume Set`, `OLED Contrast`, heap/PSRAM diagnostics) and simplify CPU reporting to a single `CPU Usage` sensor (disable per-core sensors and top-task logs).
- ESPHome: Reduce number state publish spam by throttling template number update intervals (`EQ Low/Mid/High`, `Arylic Volume Set`) from 500ms to 5s and `OLED Contrast` from 1s to 10s.
- ESPHome: Canonicalize secrets structure to `esphome/secrets.yaml` and remove duplicate per-project `secrets.yaml` under `esphome/spectra_ls_system/`.
- Repo: Add tracked `esphome/secrets.example.yaml` template while keeping real secret files ignored.
- Repo: Establish concurrent dual-branch operations with dedicated `menu-only` worktree under `.worktrees/menu-only`.
- Docs: Add filesystem safety gate to prevent destructive live-path moves/deletes without reversible snapshot and verification.
- Repo: Tighten HA tracking scope to Spectra project docs/packages/ESPHome paths and stop tracking generic HA root runtime files.

## 2026-04-15

- Repo: Enforce RP2040 source-of-truth policy (live `CIRCUITPY/` + single repo mirror `esphome/circuitpy/`) and remove stale duplicate `boot.py`/`code.py` copies from other ESPHome paths.
- Docs: Tighten Copilot instructions for senior/public-product standards, latest HA/ESPHome API diligence, and mandatory dual-sync RP2040 edits (live `CIRCUITPY/` + `esphome/circuitpy/`).
- Repo: Migrate to top-level `/mnt/homeassistant` Git root and import `esphome` history under `esphome/` with preserved commit history.
- Repo: Track core HA root files on `main` (`configuration.yaml`, `automations.yaml`, `scripts.yaml`, `scenes.yaml`, and `packages/`).
- Docs: Add dual-branch shared-contract merge gate (`main` + `menu-only`) with required paired update or explicit divergence note.

## 2026-04-14

- HA: Explicitly enable the template integration to ensure package template sensors load.
- HA: Explicitly enable the command_line integration for Spectra LS HW status polling.
- HA: Remove unsupported from_json default parameter in Spectra LS rooms template to ensure sensor loads.
- HA: Reduce false control-target ambiguity when now-playing clearly matches the active target.
- ESPHome: Add v.next self-contained `spectra_ls_system/` project and repoint `spectra_ls_system.yaml` to use it (substitutions, packages, components, and assets).
- ESPHome: Rename v.next peripherals file to `spectra-ls-peripherals.yaml` (drop legacy naming).

## 2026-04-13

- ESPHome: Repoint Control Board v2 entrypoint to control-py-scoped substitutions and components so the config is self-contained when duplicating control-py.
- ESPHome: Consolidate control-board dependencies into control-py (components and fonts), keeping root entrypoint in place.
- ESPHome: Fix rp2040_uart header path after moving components into control-py.
- ESPHome: Use MA active sensors directly for now-playing metadata to restore artist/source fields.
- HA: Add unified now-playing meta resolver with normalized scoring across MA/HA sources.
- HA: Harden meta resolver Plex allowlist defaults and debug candidate output handling.
- HA: Split ma_control_hub into logical include files for maintainability.
- HA: Gate kitchen meta override behind MA meta confidence so strong detections win.
- HA: Prefer active meta when it is playing/paused or fresh to avoid stale now-playing selection.
- HA: Use media_player is_playing/is_paused/play_state attributes to determine active meta and reduce stale picks.
- ESPHome: Add animated boot splash for Spectra L \ S lettering.
- Docs: Update Copilot instructions to avoid editing rings peripherals file.
- ESPHome: Add audio control gate logging + fallback to ma_control_host when ma_control_hosts is empty (volume/EQ TCP sends).
- ESPHome: Keep last valid control host(s) when active target is valid (avoid transient clears on HA flaps).
- ESPHome: Apply manual_ip from substitutions so Control Board stays on the IoT subnet.
- ESPHome: Temporarily pin `wifi.use_address` to 192.168.30.246 for Control Board v2 (OTA/API target only).
- ESPHome: Switch Control Board v2 Wi-Fi secrets to non-IoT keys and remove temporary use_address pin.
- Repo: Restore tracking of `esphome/circuitpy/` (authoritative RP2040 firmware mirror), while ignoring `control-py/previous/circuitpy/`.
- Repo: Track HA packages `packages/dst_tuya_ac.yaml` and `packages/ma_control_hub.yaml`.

## 2026-04-12

- HA: DST manual override now sticks until the room reaches the target temperature, and Tuya cool setpoint defaults 2°F below the DST target when turning on AC.
- HA: DST auto-off now respects manual override window to prevent premature shutdown.
- HA: DST now uses bedroom enviro temperature/humidity sensors with faster updates.
- HA: DST now reasserts Tuya cool mode while DST is cooling, without forcing preset changes during manual override.
- HA: Fix tuya_unsupported_sensors config flow await error and set DST automation/script modes to avoid “Already running” warnings.
- ESPHome: Stop forced HA update_entity calls for MA control host sensors to avoid template AssertionError spam.
- HA: Prefer active target for now-playing entity when target is playing with metadata to avoid stale AirPlay meta on OLED.
- ESPHome: Add control-target prompt grace window around playback/ambiguity transitions to prevent popups during track switches.
- ESPHome: Add Gear menu (Meta Select + Control Select) and manual Control Target prompt entry.
- ESPHome: Label control-target popup “Control Targets”.
- RP2040/Docs: Add dedicated Select button on PCF8575 (event 37) and mirror select input to menus.
- ESPHome: Harden control-target prompt parsing (escaped JSON), add prompt cancel/empty handling, and align menu activation index.
- ESPHome: Debounce control-target prompts, add Control Target popup label, and hold last valid TCP hosts during transient HA updates.
- ESPHome: Reduce Control Target popup highlight top overlap (2px padding).
- HA/ESPHome: Harden lighting target label → entity mapping and debounce slider brightness sends to avoid bursts.
- ESPHome: Lighting slider no longer pushes brightness while in menu mode; brightness mode auto-exits after inactivity and on menu entry.
- ESPHome: Deduplicate lighting HS/color apply logic (shared script).
- ESPHome: Remove unused lighting HS wrapper script (use shared apply path).
- ESPHome: Add control-target prompt cooldown to avoid repeated prompts on volume touches when hosts/ambiguity are unstable.
- ESPHome: Keep control-target selection sticky until the play/control source changes; suppress re-prompts while locked.
- ESPHome: Apply sticky control-target lock guard across EQ/volume audio control paths.
- ESPHome: Keep sticky control-target lock from clearing on empty/unknown source keys (only clear on confirmed source change).
- ESPHome: Ignore invalid control host updates while sticky lock is active to prevent prompt flapping.
- ESPHome: Adopt first valid source key into sticky lock to prevent initial lock drop.
- ESPHome: Fix EQ pot rounding so full range reaches -10..10.
- ESPHome: Block control-target prompt immediately on selection to avoid double-press.
- ESPHome: Centralize control-target prompt gating and keep lock sticky until user explicitly reopens the selector.
- Docs: Added detailed plan for ADS7830 + 5‑position control‑target rotary switch reorg (no implementation yet).

## 2026-04-07

- HA: Refactored MA meta/control hub for dynamic meta detection, receiver matching, overrides, and low‑confidence handling.
- HA: Meta candidates now filtered to active (playing/paused) sources and respect Plex allow‑lists plus legacy local session filter.
- HA: Added MA/HA labeling for meta candidates (`MA:` / `HA:`) to disambiguate origins.
- HA: Active target options now include the detected receiver when not already present.
- HA: Added universal TV/HDMI → Spectra auto‑switch package (`spectra_ls_tv_source_auto.yaml`).
- ESPHome: Added Meta menu (low‑confidence chooser) and HA override calls for manual selection.
- ESPHome: Meta menu header renamed to “Meta Player”.
- ESPHome: Suppressed EQ overlay during boot to avoid brief EQ flash.
- ESPHome: UI render path no longer mutates menu timing; last input timestamp now initialized at boot.
- ESPHome: Moved stale `control-board-peripherals.yaml` to `previous/` to keep it out of active builds.
- ESPHome: Tightened now-playing gating so stale metadata doesn’t revive the screen when nothing is playing.
- Docs: Updated control‑board notes to use “Meta player” terminology for override behavior.

## 2026-04-09

- HA: MA Active Friendly now prefers host-mapped/target entity (removes meta-driven label flips).
- ESPHome: Volume pot now mirrors EQ handling (interval/settle/jump deferral + 50ms deferred send loop).

## 2026-04-10

- ESPHome: Centralized Control Board v2 substitutions into `substitutions.yaml` and updated control-board configs to include it.
- ESPHome: Adjusted splash screen layout (bottom-justified subtitle) and reduced splash font sizes to fit OLED.
- ESPHome: Restored `presence.yaml` to its standalone substitutions (kept separate project unchanged).
- ESPHome: Removed HA volume fallback in OLED render path (TCP volume only).
- ESPHome: Nudged splash title down 5px for improved vertical balance.
- ESPHome: Suppressed EQ overlay immediately after splash unless EQ changes post-splash.
- ESPHome: Fixed splash EQ gating compile error (avoid id() shadowing).
- ESPHome: Updated boot splash stages (Stage 1: SPECTRA + "L \ S"; Stage 2: "Level \ Source"; SPECTRA hides after 1s in Stage 2).
- ESPHome: Added missing `eq_overlay_ignore_until_ms` global for display state gating.
- ESPHome: Fixed duplicate `now` declarations in audio TCP lambdas that caused build failures.
- Repo: Added workspace-level Copilot instructions for Home Assistant + ESPHome guidance.
- Repo: Expanded Copilot instructions with additional directives and reference links.
- Repo: Documented CIRCUITPY RP2040 firmware paths in Copilot instructions references.
- Docs: Corrected Control Board v2 notes (RP2040 hardware, TCP-only control path, and ADC channel mapping) and added explicit update gate.
- HA: Treat AirPlay/Apple TV sources as control-target ambiguous to force prompt selection.
- HA: Harden MA selection templates (guard room JSON parsing; define primary Spectra entity in now-playing templates).
- ESPHome: Treat AirPlay/Apple TV sources as ambiguous locally and clear stale control hosts on invalid updates to ensure popup triggers.
- HA: Add Apple TV entity allowlist for ambiguity (ensures prompt even when app/source is non-AirPlay).
- ESPHome: Reset control target prompt after popup expiry so repeated hardware interactions re-trigger the prompt.
- ESPHome: Keep control target prompt visible until ambiguity clears (no timeout when selection required).
- ESPHome: Trigger target prompt immediately when ambiguity turns on (no waiting for hardware input).
- ESPHome/HA: Add control-target selection list wiring (entities + menu selection via encoder).
- HA: Autodetect receiver now prefers a playing room entity from `spectra_ls_rooms_raw` before heuristic scoring.
- HA: Auto-select bypasses idle delay when a detected receiver is actively playing.
- HA: Added UART-over-TCP hardware play-state polling across rooms (`spectra_ls_hw_status`) using `PINFGET`.
- HA: Detected receiver now prefers hardware playing entity when available.
- HA: HW status polling is now on-demand (now-playing triggers + 15s active refresh) instead of constant 5s polling.
- HA: HW polling now treats AirPlay as playing when progress advances (mode-based + cached deltas).
- Docs: Updated Control Board v2 wiring/input ID map to match current ESPHome button/encoder/analog IDs.
- Docs: Updated RP2040 PCF8575 pin map and button list to match current CircuitPython firmware.
- Docs: Reordered control-py notes to surface pin maps near the top and refreshed deploy steps for current firmware.
- Docs: Re-read and refreshed control-board-2 notes with current TCP control path and reality check.
- ESPHome: Added debug logging for progress-bar drops and HA position/duration updates to trace meta gating.
- Hybrid: Move position smoothing to ESPHome (local timer between HA updates) and keep HA position sensors lightweight.
- Cleanup: Remove temporary HA/meta progress debug logging after hybrid stabilization.
- ESPHome: Decouple progress bar source from meta slots (prefer HA progress when active; fall back to arylic).
- ESPHome: CPU usage component refactor (single-source header, logging controls + tag) and diagnostic logging toggle.
- Audit: Confirmed `control-board-peripherals-no-rings.yaml` in `esphome/control-py/` is complete (not empty).
- ESPHome: Fix control-target prompt rendering and selection handling in UI/menu paths.
- HA/ESPHome: Remove Apple TV ambiguity detection (AirPlay-only prompt).

## 2026-04-11

- ESPHome: Fix OLED interval lambda missing time base (`now`) compilation error.
- ESPHome: Fix control-target prompt encoder navigation (use labels list for count).
- ESPHome: Use menu encoder center press as Select input.
- RP2040/Docs: Remove bass/treble encoder references (EQ is pot-only).
- ESPHome: Auto-dismiss control-target prompt once control hosts are valid and ambiguity clears; track manual prompts to avoid auto-close.
- HA: DST auto-cool raises setpoint to 74°F after 11pm for late-night comfort.
- HA: DST auto-cool fan scaling now uses low/high/strong only (no auto).
- HA: DST now uses bedroom temp/humidity sensors as primary controllers.
- HA: DST presets simplified to Home/Away; Away disables automations and turns HVAC off.
- HA: Add manual override window + 10-hour pause controls for DST automations.

## 2026-04-06

- ESPHome/RP2040: removed calibration UI/autocal/tracking flows; RP2040 continues to apply `/calibration.json`.
- ESPHome: simplified menu to Lighting/Audio only; TCP audio package is authoritative (non-TCP marked legacy).
- Docs: consolidated to a single control-board-2 notes file.
- ESPHome: EQ display now renders 3-band vertical bars (L/M/H) to match the three physical EQ pots.
- ESPHome: EQ overlay layout refined (slimmer rows, adjusted label spacing/positioning).
- RP2040: EQ pots now snap near edges to guarantee full min/max sweep.
- RP2040: enabled EQ pot auto-capture (tracking) to save min/max to `/calibration.json`.
- ESPHome: EQ bars no longer render fully filled at 0; draw outline with center fill only.
- ESPHome: fixed EQ endpoint rounding so 0% maps to full negative dB (no truncation).
- ESPHome: stabilized Now Playing against brief HA/meta dropouts (no blanking flicker).
- ESPHome: EQ overlay bars thickened (3px slider tick, taller container).
- ESPHome: volume pot pickup/catch to prevent HA/MA volume replay overriding the knob.
- ESPHome: extended Now Playing hold window to avoid periodic blanking when HA state flaps.
- HA: MA auto-select now ignores missing media_player entities to avoid forced update failures.
- HA: delay MA target refresh on startup and skip auto-select until MA players are available.
- ESPHome: Settings menu brightness slider now points at OLED contrast control.
- HA: auto-select can switch immediately on boot/invalid target while retaining debounce for normal changes.
- HA: Control Board view now targets live MA selector and OLED contrast entity.
- ESPHome: expose OLED contrast number to HA for brightness control.
- HA: MA auto-select now reacts to player/target changes and polls faster to cut startup lag.
- RP2040: add idle noise gate for volume pot to prevent phantom volume drift.
- HA: persist and restore last valid MA target to prevent target loss and volume dropouts.
- RP2040: require multiple consistent volume pot readings before sending changes.
- ESPHome/HA: volume controls are now read-only (ignore HA/MA volume writes; hide HA slider).
- ESPHome: removed volume pot catch/hold logic (input handling is RP2040-only).
- HA: disabled MA balance volume writes to keep volume read-only.
- HA: added volume_set watcher to log and notify any HA volume writes to MA targets.
- HA: volume_set watcher now logs HA context (user_id/parent_id/origin) for faster source tracing.
- HA: paused MA auto-select time-pattern loop to stop 5s focus flapping during volume debug.
- HA: auto-select no longer switches away when current target is active (reduces target churn).
- HA: auto-select action now uses script.turn_on to fix unknown action error.
- HA: added watcher for MA volume state changes (with context) to trace non-HA volume shifts.
- HA: now-playing/meta entity pinned to active target to prevent cross-room stale metadata.
- HA: now-playing entity selection prefers the player with real metadata and most recent updates (reduces AirPlay/Spectra blanks).
- HA: MA Active Title now falls back to Now Playing Title/Source/Friendly to avoid OLED blanks when MA metadata is empty.
- HA: Spectra LS meta entity now matches its playback entity to keep MA Active metadata populated.
- HA: Replaced AirPlay-specific meta heuristics with dynamic meta detection and receiver matching.
- HA: Refactored meta/control architecture with dynamic meta detection, receiver detection, meta override, and low-confidence indicator; removed debug volume watcher automations.

## 2026-03-25

- ESPHome: Added EQ full-screen slider view (9-band, 75% adjacent) and mirrored it to both `control-board-peripherals-no-rings.yaml` and `control-board-peripherals.yaml`.
- ESPHome: Added MA control host fallback (`sensor.ma_control_host`) when `ma_control_hosts` is empty; refreshes both sensors periodically.
- ESPHome: Arylic TCP send coalescing to reduce burst flooding while keeping pot responsiveness (latest payload wins, skip immediate duplicates).

## 2026-03-24

- HA: Split MA control hub into focused package files for maintainability.
- ESPHome: Increased Arylic TCP timeout and added ADS read safeguards/recovery in RP2040 input path.
- ESPHome: Added EQ screen overlay features and display state improvements to prevent Now Playing blanking.
