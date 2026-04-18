<!-- Description: Repository changelog for Home Assistant + ESPHome work. -->
<!-- Version: 2026.04.18.8 -->
<!-- Last updated: 2026-04-18 -->

# Changelog

## 2026-04-18

- ESPHome/Diagnostics Cleanup: Remove one-cycle `disp_diag` transition logger from `esphome/spectra_ls_system/spectra-ls-peripherals.yaml` after root-cause playback predicate hardening, reducing log noise without changing display-state behavior.

- ESPHome/HA Position Activity Debounce: In `esphome/spectra_ls_system/packages/spectra-ls-audio-tcp.yaml`, only refresh `ha_audio_pos_last_ms` when `ha_audio_position` actually moves (>=0.05s delta), preventing unchanged paused-position updates from being misread as active playback evidence.

- ESPHome/Now-Playing Idle-Recency Clamp (follow-up): Refine `playing_effective` in `esphome/spectra_ls_system/spectra-ls-peripherals.yaml` so Arylic/LR recency and activity windows only contribute when corresponding sources are non-idle, and only refresh `last_playing_true_ms` under active-source conditions. This prevents idle metadata timestamp churn from holding `play=1`/NP state with empty content.

- ESPHome/Now-Playing Evidence Gate Fix (diagnostic-driven): Use one-cycle `disp_diag` findings to harden `playing_effective` in `esphome/spectra_ls_system/spectra-ls-peripherals.yaml` so HA `state=playing` only refreshes playback-hold timestamps when recent HA playback evidence exists (recent meta or position updates). This prevents stale upstream `playing` flags from pinning the idle display on Now Playing with empty content.

- ESPHome/Display Diagnostics (One-Cycle Instrumentation): Add always-on, rate-limited transition logging in `esphome/spectra_ls_system/spectra-ls-peripherals.yaml` (`compute_display_state`) for `display_state`, `no_audio_activity`, `menu_active`, `lighting_active`, and `screen_mode` so stuck-idle branch selection can be traced from a single reboot cycle.

- ESPHome/Now-Playing Predicate Hardening: In `esphome/spectra_ls_system/spectra-ls-peripherals.yaml`, tighten `playing_effective` recovery so Arylic/LR recency no longer revives playback when source is idle, and make the clear-down condition depend on active-source/activity signals rather than raw recency timestamps. This prevents idle no-content systems from being pinned on the Now Playing screen.

- ESPHome/UI Display-State Routing Fix: In `esphome/spectra_ls_system/spectra-ls-peripherals.yaml`, update `compute_display_state` decision ordering so `no_audio_activity` resolves directly to `STATE_BLANK` when menu and lighting-activity windows are not active, preventing idle home/target text screens from persisting when nothing is playing.

- ESPHome/UI Idle Blanking Root-Cause Fix: In `esphome/spectra_ls_system/packages/spectra-ls-audio-tcp.yaml`, stop treating passive volume-pot polling as synthetic user activity by only updating `last_input_ms` when the mapped pot target actually changes; this prevents idle timers from being continuously reset by analog polling noise and allows proper blanking when nothing is playing.

## 2026-04-17

- ESPHome/UI Idle-Blank Safety Fix: In `esphome/spectra_ls_system/spectra-ls-peripherals.yaml`, change the unknown display-state fallback renderer to fail closed (blank screen) instead of drawing `${friendly_name}`/status text; in `packages/spectra-ls-system.yaml`, initialize `display_state` to blank by default so post-flash startup/compute race windows cannot surface the stale top-line `SPECTRA LS` header when nothing is playing.

- HA/MA Control-Hub Consolidation (template.inc, batch 11): Final 5+ dedupe sweep by adding shared scalar resolver attributes for now-playing (`resolved_position`, `resolved_duration`, `resolved_volume`, `resolved_friendly`) and MA-active (`resolved_duration`, `resolved_position`, `resolved_volume`) surfaces, then rewiring the corresponding sensors to consume shared attributes instead of repeating inline target/meta fallback blocks.

- HA/MA Control-Hub Consolidation (template.inc, batch 10): Execute a 5+ slice maintainability pass by (1) adding shared `resolved_app` on `sensor.ma_active_player_id_resolved` and rewiring `MA Active App`, and (2) normalizing remaining control-path `rooms_json` string parsing callsites to the dual-mode contract (trim+sentinel guard, `[`/`{` support, mapping extraction) across host/path/target/capability/ambiguity readers.

- HA/MA Control-Hub Dedupe (template.inc, batch 9): Add shared `resolved_artist` and `resolved_album` attributes on `sensor.now_playing_entity` and `sensor.ma_active_player_id_resolved`, then rewire `Now Playing Artist/Album` and `MA Active Artist/Album` sensors to consume those shared attributes; preserves existing fallback precedence while removing duplicated inline artist/album resolution blocks.

- HA/MA Control-Hub Dedupe (template.inc, batch 8): Add shared `resolved_title` attributes on `sensor.now_playing_entity` and `sensor.ma_active_player_id_resolved`, then rewire `Now Playing Title` and `MA Active Title` sensors to consume those shared attributes; preserves existing URL/queue suppression and fallback ordering while removing duplicated inline title-resolution blocks.

- HA/MA Control-Hub Dedupe (template.inc, batch 7): Add shared resolved source attributes on `sensor.now_playing_entity` and `sensor.ma_active_player_id_resolved` (candidate filtering + queue/placeholder guards + media_player friendly-name normalization), then rewire `Now Playing Source` and `MA Active Source` to consume those shared resolved values instead of duplicating inline candidate-reduction loops.

- HA/MA Control-Hub Dedupe (template.inc, batch 6): Add shared `player_json` + `player_fields_json` attributes on `sensor.now_playing_entity` and rewire `Now Playing Title/Artist/Album/Source/State` to consume the shared fields payload instead of repeating per-sensor MA player lookup loops; also align `packages/ma_control_hub/script.inc` string JSON guard to accept both `[` and `{` payload starts for mapping-compatible room parser behavior.

- HA/MA Control-Hub Dedupe (template.inc, batch 5): Add shared `player_fields_json` projection on `sensor.ma_active_player_id_resolved` and rewire `MA Active Title/Artist/Album/App/Source` to consume that shared payload instead of repeating per-sensor `player_json` parse/field extraction blocks; also normalize `packages/ma_control_hub/script.inc` room JSON string parse branch to use trimmed payload + sentinel guard consistency.

- DevTools + HA/MA Control-Hub Quality (batch 4): In `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` Iteration Workbench 1A and command-effect templates, replace manual `expected_value` dependency with action-aligned effect expectation (`expected_effect_value`) derived from a single probe action value input (with safe default to entity `min`) to eliminate false WARN deltas from mismatched expected/probe payloads; in `packages/ma_control_hub/template.inc`, add shared `player_json` lookup payload on `sensor.ma_active_player_id_resolved` and reuse it across `MA Active Title/Artist/Album/App/Source` to dedupe repeated `lookup_id/short_id/players/ns.p` loops without behavior drift.

- HA/MA Control-Hub Correctness + Quality (template.inc, batch 3): Fix high-risk self-reference in `sensor.spectra_ls_rooms_json` state parser to source room data from `sensor.spectra_ls_rooms_raw.rooms` (authoritative input) instead of self-reading `sensor.spectra_ls_rooms_json.rooms_json`; additionally normalize `MA Meta Resolver` guarded string parse to use `raw_trim | from_json`, switch `MA Detected Receiver Entity` to normalized `sensor.spectra_ls_rooms_json.rooms_json`, and remove dead locals (`_mp`, `appletv`) that were not consumed.

- HA/MA Control-Hub Code Quality (template.inc, batch 2): Continue parser-contract cleanup in `packages/ma_control_hub/template.inc` by (1) routing additional room consumers (`MA Detected Receiver Entity`, `MA Active Meta Entity`) to normalized `sensor.spectra_ls_rooms_json.rooms_json` payloads instead of re-reading raw rooms attributes, and (2) standardizing guarded string JSON parsing in touched branches to parse `raw_trim` values.

- HA/MA Control-Hub Code Quality (template.inc): Refactor `sensor.ma_meta_candidates` attribute derivation in `packages/ma_control_hub/template.inc` to use a shared parsed summary payload (`candidate_summary_json`) for entities/names/labels/scores/best-candidate outputs, reducing duplicated parser branches and improving maintainability; also normalize guarded JSON parse inputs to use trimmed payloads in touched parser branches.

- Docs/DevTools Batched Refactor (3 slices): Update `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` to (1) route Iteration Workbench 1A and Template #2 room-map parsing through normalized `sensor.spectra_ls_rooms_json.rooms_json` payloads instead of re-parsing `sensor.spectra_ls_rooms_raw` inline, and (2) replace broad `states.number` scans in Templates #3 and #5 with explicit Spectra audio control candidate lists to reduce listener noise and render churn.

- HA/MA Meta Candidates Refactor: Consolidate repeated candidate scan loops in `packages/ma_control_hub/template.inc` by introducing a shared candidate-row payload attribute for `sensor.ma_meta_candidates` and deriving summary attributes from that shared structure, reducing drift and repeated high-cost template passes.

- Docs/DevTools 1A Noise Reduction: Tune `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` Iteration Workbench (Template 1A) command-readiness scan to use a targeted audio-control number candidate list instead of broad `states.number` domain enumeration, reducing irrelevant listener wakeups while keeping expected Spectra control-surface probes intact.

- HA/MA Meta Candidates Dedupe: Reduce duplicated scoring loops in `packages/ma_control_hub/template.inc` by introducing a shared `best_candidate_json` attribute for `sensor.ma_meta_candidates` and routing `best_entity`/`best_score` through that shared payload.

- HA/MA Script Parser Unification: Update `packages/ma_control_hub/script.inc` (`ma_update_target_options`) to consume normalized `sensor.spectra_ls_rooms_json` payload (`rooms_json`) for room-target option derivation, aligning script-side parsing with template-side helper refactors and reducing contract drift.

- HA/MA Parser Helper Refactor: Reduce duplicated `rooms` parser blocks in `packages/ma_control_hub/template.inc` by routing key control-path sensors (`ma_control_hosts`, `ma_active_control_path`, `ma_control_targets` + attributes, `ma_active_target_by_host`, `ma_active_control_capable`, `ma_control_ambiguous`) through normalized `sensor.spectra_ls_rooms_json` payload ingestion.

- HA/MA Refactor (Meta Resolver): Reduce parser drift in `packages/ma_control_hub/template.inc` by introducing a shared `best_candidate_json` attribute in `sensor.ma_meta_resolver` and routing both `best_entity` and `best_score` through it instead of maintaining duplicate `candidates_json` parse/scan blocks.

- Docs/DevTools Iteration Workbench: Add a unified single-paste `1→4` diagnostics template (`1A`) to `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` that consolidates health, routing path, command readiness, and command-effect checks into one iterative operator workflow with compact roll-up status and inline probe payload suggestions.

- HA/Now-Playing Source Stability (ma_control_hub): Harden `packages/ma_control_hub/template.inc` source resolvers (`Now Playing Source`, `MA Active Source`) to select the first valid non-placeholder, non-queue candidate in deterministic order (with media_player entity-id friendly-name resolution and final friendly-name fallback), preventing intermittent blank `src` output while target/host/meta are otherwise healthy.

- ESPHome/Runtime Cleanup (Code-Side): Remove unreferenced high-frequency internal template sensors from `esphome/spectra_ls_system/packages/spectra-ls-lighting.yaml` (`lighting_hue_state`, `lighting_sat_state`, `lighting_brightness_state`, `selected_room_state`, `selected_target_state`) to eliminate unnecessary 500ms polling work with no behavioral contract impact.

- Docs/DevTools Phase-4 Template Modernization: Update `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` Template #2 and Template #14 to use the full dual-mode payload contract (native sequence/mapping + guarded string JSON parse) with trimmed lowercase sentinel checks (`raw_trim_l`) for deterministic parser behavior.

- Docs/DevTools Iteration-4 Accuracy Fix: Update `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` Template #16 to detect virtual battery status using HA `sensor`-domain entities (not `text_sensor` domain) and soften verdict semantics so idle/no-recent-probe activity reports `WARN` rather than hard `FAIL` when core virtual entities are present.

- Docs/DevTools Hotfix: Repair Jinja syntax corruption in `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` Template #16 (`Iteration 4 Diagnostics Chatter Check`) by removing stray `endif/endfor` mismatches and leaked lines from adjacent templates, restoring valid render behavior in HA Developer Tools.

- Docs/DevTools Diagnostics Hardening: Update `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` Iteration 4 chatter template virtual-entity discovery to tolerate prefixed `friendly_name` variants (substring match) and reorder tail templates into strict `13 → 14 → 15 → 16` numeric sequence for predictable navigation.

- Docs/DevTools Ordering: Reorder `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` template sections into strict numeric sequence so the tail block is now `13 → 14 → 15 → 16` (eliminates out-of-order `16/14/15/13` layout).

- Diagnostics/Template Fix (Iteration 4): Harden `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` Template #16 entity resolution to use `friendly_name` matching with explicit entity-id fallbacks, preventing false FAIL reports where virtual diagnostics exist but `name`-based lookup returns empty IDs.

- ESPHome/Diagnostics Iteration 4: Reduce virtual-input diagnostics chatter in `esphome/spectra_ls_system/packages/spectra-ls-diagnostics.yaml` by slowing passive publish cadence for virtual mode/control/status entities (no behavior-path changes), and add an Iteration 4 DT verification template in `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` focused on interaction visibility with lower idle spam.

- HA/MA Parser Guard Determinism (Iteration 2): Tighten complex-payload string parser guards in `packages/ma_control_hub/template.inc` and `packages/ma_control_hub/script.inc` to evaluate sentinel checks against trimmed lowercase payloads, reducing whitespace/case-induced drift while preserving dual-mode sequence/mapping behavior.

- HA/MA Full Parser Modernization (Iteration): Expand `packages/ma_control_hub/template.inc` rooms/candidate readers to fully honor the dual-mode contract across remaining call sites (native sequence, native mapping with canonical key extraction, and guarded string JSON parse) and add an iteration DT validation template in `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` to verify parser-shape compatibility after each modernization pass.

- HA/MA Contract Hardening: Update `packages/ma_control_hub/template.inc` and `packages/ma_control_hub/script.inc` rooms/candidate readers to a dual-mode parser contract (native sequence payloads accepted directly; string JSON payloads parsed only after trim+guard checks), preventing audio routing/meta/control surfaces from collapsing when Home Assistant exposes attribute payloads as non-string objects.

- HA/Lighting Native Payload Parse Fix: Update `packages/spectra_ls_lighting_hub.yaml` catalog consumers to accept both string JSON arrays and native sequence payloads from `items_json`, preventing false-empty parses when Home Assistant surfaces `state_attr(..., 'items_json')` as a non-string object.

- HA/Lighting JSON Parse Hardening: Make `packages/spectra_ls_lighting_hub.yaml` catalog/options JSON parsing whitespace-tolerant (`| trim` before `[` checks and parse) across template sensors and sync automations, preventing valid JSON payloads with leading newline/space from being treated as empty and collapsing selectors to `No Rooms` / `All`.

- HA/Lighting Catalog Fallback Hardening: Add area-registry (`areas()` + `area_entities()`) fallback population path inside `sensor.control_board_eligible_light_catalog` so room/target helper surfaces recover even when primary `states.light`/`area_id(...)` pass yields empty results. This prevents persistent `No Rooms`/`All` selector collapse after reload when catalog bootstrap is unexpectedly empty.

- HA/Lighting Catalog Payload Overflow Fix: Move `sensor.control_board_eligible_light_catalog` payload from sensor state into attribute-backed JSON (`items_json`) and switch dependent templates to read attribute-first with state fallback. This prevents long JSON truncation/parse collapse that manifested as `control_board_room_options = ["No Rooms"]` and `control_board_target_options = ["All"]` despite healthy entities.

- HA/Lighting Catalog-First Target Resolution Fix: Refactor `packages/spectra_ls_lighting_hub.yaml` room/target contract surfaces to resolve from a shared eligible-light catalog built from `states.light` + `area_id(...)`, then drive `room_options`, `target_options`, `room_area_id`, `target_entity_id`, `room_hs`, and `room_on` from that catalog. This removes dependence on direct per-template `area_entities(...)` scans and restores per-room target population where selectors previously degraded to `All`-only.

- HA/Lighting Area-Selection Scope Fix: Correct Jinja loop-scope behavior in `packages/spectra_ls_lighting_hub.yaml` by replacing plain `area_id_selected` loop assignments with `namespace(area_id=...)` in room-dependent target/HS/on templates. This restores per-room light discovery so populated rooms no longer show `All`-only targets.

- HA/Lighting Template Runtime Fix: Correct malformed Jinja block closures in `packages/spectra_ls_lighting_hub.yaml` (`Control Board Target Options` and `Control Board Target Entity ID`) where `endif` incorrectly closed `for ent in lights` loops; this was driving `sensor.control_board_room_options`/`target_options` contract dependents into `unavailable` and collapsing room UI back to static fallback labels.

- Diagnostics Hardening: Update `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` Template #6 (Lighting Rename Validation) to treat placeholder-only room options (`No Rooms`/`Unknown`) as **FAIL** and `All`-only target options as degraded (**WARN**), preventing false PASS reports when room population is actually broken.

- HA/Lighting Room Source-of-Truth Fix: Switch `packages/spectra_ls_lighting_hub.yaml` room/target derivation to HA area registry as primary contract (`areas()` + `area_entities()`), including `room_options`, `room_area_id`, `target_options`, `target_entity_id`, `room_hs`, and `room_on`, decoupling visible room population from eligible-light catalog filtering.

- HA/Lighting Fallback Policy Correction: Remove `Unassigned` all-lights fallback from `sensor.control_board_eligible_light_catalog` and switch empty room fallback to `No Rooms`; add placeholder-only guard in room sync to preserve existing concrete room options. This prevents repeated `Unassigned + Back` loops from masking real area contract issues.

- HA/Lighting Startup Stabilization: Remove transient availability gating from `sensor.control_board_eligible_light_catalog` and add anti-downgrade guard in room sync so `input_select.control_board_room` is not overwritten by `['Unassigned']` when concrete room options already exist; addresses recurring `Unassigned + Back` regressions after reload/boot churn.

- Hotfix: Correct `packages/spectra_ls_lighting_hub.yaml` Jinja block terminator in `sensor.control_board_eligible_light_catalog` (`endif` vs accidental `endfor`) to restore template loading; this unblocks room/target option generation that had been failing at HA config parse time.

- HA/Lighting Regression Correction: Restore `packages/spectra_ls_lighting_hub.yaml` eligible-light catalog to area-first discovery (`areas()` + `area_entities()`), with all-lights fallback only when area-derived results are empty; fixes unintended "Unassigned-only" room output introduced by prior all-lights-first refactor.

- MA Control Targets Boot Fallback: Harden `packages/ma_control_hub/template.inc` so `sensor.ma_control_targets` falls back to `input_select.ma_active_target` options when `sensor.spectra_ls_rooms_raw` is not yet populated at boot/reload, preventing blank control-target prompt/options during startup race windows.

- HA/Lighting Selectability Regression Fix: Update `packages/spectra_ls_lighting_hub.yaml` sync automations to stop preserving stale room/target option values in `input_select` options, and force-reset to valid parsed options when contracts repopulate; resolves "Select Control Target" lock state with no selectable targets.

- HA/Lighting Room Options Root-Cause Fix: Rework `sensor.control_board_eligible_light_catalog` in `packages/spectra_ls_lighting_hub.yaml` to derive candidates from all `light.*` entities (including unassigned-area lights) instead of area-only enumeration, preventing `['Unknown']` option collapse that forced ESP OLED room-menu fallback labels (`Room 1/2/3/4`).

- Diagnostics/Template Fix: Correct `Source Truth Test` false-negative behavior in `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` by replacing brittle core sentinel failure logic (`sensor.time`/`sun.sun`) with a core entity-count heuristic and by switching source probes to realistic exposed entities; prevents misleading "HA degraded" conclusions when control-hub contracts are the actual fault domain.

- HA/Lighting Control-Hub Recovery: Broaden `sensor.control_board_eligible_light_catalog` eligibility in `packages/spectra_ls_lighting_hub.yaml` to include on/off and legacy light entities (while still excluding speaker-like pseudo-lights), preventing false-empty room/target catalogs that caused ESP menus to fall back to generic room labels.

- ESPHome/Source Status UX Hardening: Normalize source placeholders and surface explicit fallback status (`HA not accessible`) in OLED source resolution when all source feeds are empty/unavailable, removing ambiguous blank/unknown source states.

- ESPHome/HA Option Intake Resilience: Add dual-source room/target option feeds (`input_select` attribute options + catalog sensors) and prefer non-empty parsed lists for OLED menu rendering and UI count refresh paths, preventing transient helper-state gaps from collapsing lighting menus to static fallback room labels.

- ESPHome/Now-Playing Architecture Hardening: Remove source-only activity from playback truth in `spectra-ls-peripherals.yaml` (no longer promotes passive source labels into active playback), tighten display hold to real playing/recent-playing signals, and clear source fallback caches when hold is inactive so idle state resolves to true blank.

- ESPHome/Option Parser Contract Hardening: Apply placeholder-value filtering (`unknown`, `unavailable`, `none`, `null`, `idle`) to duplicated dynamic option parsers in `spectra-ls-lighting.yaml` so HA transient states cannot contaminate room/target selector mapping paths.

- ESPHome/Lighting Menu Resilience Fix: Sanitize dynamic option parsing in `spectra-ls-peripherals.yaml` so placeholder HA values (`unknown`, `unavailable`, `none`, `null`, `idle`) are dropped instead of rendered as real menu entries; Lighting Rooms now correctly falls back to configured room labels when HA options are temporarily unavailable.

- ESPHome/OLED Idle-State Fix: Prevent stale source labels (for example `YOUTUBE`) from holding Now Playing when no active playback exists by tightening display-active gating to playing/recent-media signals and clearing source-fallback fields when media display hold is inactive.

- ESPHome/Display Contract Refactor: Move display-state IDs to shared substitutions and replace local enum literals in `spectra-ls-peripherals.yaml` state computation/render paths, keeping display mode semantics centralized and reusable across package evolution.

- ESPHome/Nav Constants Refactor: Add shared menu-count/fallback-count substitutions and replace active hardcoded menu counts/branch sizes in UI, hardware nav handlers, and OLED menu rendering paths to reduce cross-file drift and make menu evolution centrally tunable.

- HA/Lighting Architecture Refactor: Introduce a reusable `sensor.control_board_eligible_light_catalog` contract in `packages/spectra_ls_lighting_hub.yaml` and route room options, target options, room area resolution, target entity resolution, room HS, and room on/off state through that single eligibility source to prevent layered filtering drift.

- Workflow/Instruction Update: Extend `.github/copilot-instructions.md` with an explicit architecture-first directive for this workspace: treat bug reports as signals to improve reusable design and avoid "just make it work" patch layering.

- HA/Lighting Target Hygiene: Harden `packages/spectra_ls_lighting_hub.yaml` target derivation to exclude speaker-like pseudo-light entities (name/entity contains `speaker`) while retaining domain-light routing, preventing entries like `Kitchen speakers` from appearing in lighting target menus.

- HA/Lighting Contract Fix: Enforce strict light-only target options in `packages/spectra_ls_lighting_hub.yaml` by removing stale-current option carryover from target sync, preventing non-light entries (for example speaker labels) from persisting in `input_select.control_board_target`.

- ESPHome/UI UX Fix: Add direct one-click entry from non-menu lighting screen into Lighting Rooms menu in `spectra-ls-ui.yaml` so opening lighting menu no longer requires an extra select press.

- ESPHome/UI Navigation Fix: Eliminate boot-time ghost root-menu rendering that was visually presenting menu tiles without an active menu state, causing dead-end-feeling navigation and hidden menu semantics.

- ESPHome/UI Menu Fix: Force boot/root menu rendering to the icon-tile root level so fallback/boot states no longer show literal `Lighting / Audio / Gear` list text; those labels are internal root-category semantics behind icon navigation.

- ESPHome/UI Regression Fix: Remove implicit top-level menu re-entry after lighting-adjust hold and playback-stop transitions so the UI no longer auto-shows literal `Lighting / Audio / Gear` tiles unless the menu is explicitly opened by user input.

- ESPHome/UI Architecture: Replace hardcoded menu-level magic numbers in active lighting/UI control paths with named menu-level constants from substitutions to reduce transition fragility and improve v-next maintainability.

- ESPHome/Lighting Architecture: Centralize lighting value-adjust transition flow into a single script path (`start_lighting_value_adjust`) to eliminate duplicated menu-to-adjust state writes and reduce transition drift risk as v-next menu behavior expands.

- ESPHome/Lighting UX Flow: Rework lighting value adjustment behavior so Hue/Saturation (and lighting adjust paths) do not get pre-empted by active playback; after adjustment activity ends, UI returns to the same lighting menu context, holds for 5000ms, then gracefully transitions to Home (no active playback) or Now Playing (when active).

- ESPHome/Lighting Hardening: Make UI auto-routing hardware-mode-aware in `spectra-ls-ui.yaml` so audio-driven auto-flip behavior no longer overrides explicit lighting selector modes (`hardware_mode` 0/1), improving hardware-first determinism for v-next.

- ESPHome/Lighting Hardening: Add structural guardrails for v-next stability by removing hardcoded lighting hold timing (new substitution), sanitizing slider selection index handling in room/target menu contexts, and gating HA light service dispatch when neither target entity nor area routing is available.

- ESPHome/Lighting Audit Fix: Correct display-state gating so lighting render windows honor `hue_ring_active_until_ms` (not only brightness/audio windows), preventing Hue/Saturation lighting views from dropping back to the main/menu screen during active adjustments.

- ESPHome/Lighting Audit Fix: Harden slider input routing in `spectra-ls-lighting.yaml` so slider movement exits stale non-lighting menu states and applies as lighting input, while still preserving room/target selection behavior when explicitly in Room/Target menu levels.

- ESPHome/Lighting Audit Fix: Add a consistent temporary lighting hold window in `focus_lighting` so encoder/button/slider interactions all keep `screen_mode=0` long enough to prevent immediate auto-flip back to audio while playback is active.

- Docs/README: Tighten `Digital Audio Ingest + Final DAC Path` intro wording and add an explicit plain-language positioning line: “In plain terms: a DAC for your home.”

- Docs/README: Re-group Inputs feature copy into explicit **Lighting Controls** and **Audio Controls** blocks, and replace the awkward controls-example heading with a concise **Controls** section label for cleaner launch-page flow.

- Docs/README: Final editorial launch-page pass — enforce one-time `Spectra Level / Source (Spectra L/S)` introduction and use `Spectra L/S` thereafter, while tightening opening narrative flow for a cohesive front-to-back product voice.

- Docs/README: Rework non-spec sections into product-outcome language (what users feel and can do) by removing file-path/architecture-heavy prose from system interaction and feature sections; keep detailed technical capability data centered in specs/cutsheet areas.

- Docs/README: Replace implementation-heavy input inventory wording with outcome-focused product copy; explicitly call out direct lighting Brightness/Hue/Saturation control over rooms or individual lights and keep the Inputs section centered on what users can do (not internal mechanics).

- Docs/README + v-next NOTES: Add promotional hands-on input examples (including full transport controls: Play/Pause, Next, Back/Previous), strengthen product-forward copy tone, and add a formal v-next crossfade/balance slider requirement: in multi-room mode, slider shifts volume balance between rooms; in single-room mode, slider controls speaker balance.

- Docs/README: Replace dry input inventory copy with concrete control behavior notes for the lighting slider (brightness mapping + debounced sends), room switching (cycle + input_select sync), and the implemented multi-room transition/crossfade path via `script.control_board_set_light_dynamic` transition support.

- Docs/README: Add an explicit `HD DAC Capability Cutsheet` block (wireless stack, multi-room behavior, music-service list, and local-source support) and add plain-language whole-home multi-speaker synchronization copy (same-track room lock + independent room playback) without protocol-insider wording.

- Docs/README: Normalize shorthand usage to `Spectra L/S` (no standalone `L/S`), change EQ phrasing to `Physical 3-Band EQ`, move Seesaw under an explicit Inputs section, and expand physical-control listing to call out switches/buttons/knobs/sliders/dials.

- Docs/README: Add explicit direct analog-input control wording for Volume + 3-band EQ, document automatic Light/Sound interaction behavior when Home Assistant already knows targets, and include UP2STREAM HD DAC audio-side capability notes (dual-band Wi-Fi, AirPlay 2, Spotify Connect, TIDAL Connect, aptX HD Bluetooth 5.0, no-amp module class) sourced from published product metadata.

- Docs/README: Expand front-page intended-use messaging to explicitly call out direct analog control for Volume + 3-band EQ (bass/mid/treble), home dance-party usage, v-next multiple switches/dials expansion, and responsive screen/menu navigation feedback.

- Docs/README: Link `Home Assistant` at its first paragraph mention and de-link later duplicate `Home Assistant` link usage so external-linking follows first-mention-only style.

- Docs/README: Reframe the Digital Audio Ingest section around intended day-to-day use (coffee-table/home digital-to-analog control hub, couch/desk operation) and remove HDMI/ARC hyperlinking in that section while keeping capability statements intact.

- Docs/README: Remove the literal “audio nerd” phrasing in the Digital Audio Ingest + Final DAC Path section and replace the multi-bullet codec list with a single concise `Supports: FLAC, MP3, AAC, AAC+, ALAC, APE, WAV.` line.

- Docs/README: Set front-page title and first project mention to **Spectra Level / Source** (with immediate **L/S** shorthand), normalize remaining visible **Spectra LS** wording to **L/S**, and remove the dedicated external-links block including the dead `n4archive` reference in favor of inline linked hardware/ecosystem mentions.

- Docs/README: Convert front-page hardware/audio ecosystem mentions to inline manufacturer/project URLs (MCUs, input ICs, control interface ecosystems, HDMI/ARC reference, ESS ES9038Q2M, and OLED controller references) so readers can jump directly from each mention to its canonical project/vendor page.

- Docs/README: Normalize product naming in front-page audio section to introduce **Level / Source** once and use **L/S** shorthand thereafter while preserving published ARC/DAC capability details.

- Docs/README: Strengthen front-page hardware/audio positioning to describe Spectra Level / Source as a fully integrated high-fidelity source-to-output system (not a DAC-only claim), while retaining the explicit ARC ingest → ESS ES9038Q2M conversion path and published 192kHz/24-bit + codec capability references.

- Docs/Hardware Notes: Document HDMI ARC-capable source ingest path (HDMI input → ARC digital audio split/extract → final ESS ES9038Q2M DAC stage) including 192kHz/24-bit target capability and codec support references (`FLAC`, `MP3`, `AAC`, `AAC+`, `ALAC`, `APE`, `WAV`) in project notes/README.

- ESPHome/Diagnostics: Add a temporary virtual-input harness in `esphome/spectra_ls_system/packages/spectra-ls-diagnostics.yaml` with mode/control injectors, mode-nav test buttons, and a one-shot battery script so selector/control-class/menu flows can be validated in HA without physical RP2040 wiring changes.
- RP2040/Phase B: Fix v-next selector/control-class event fidelity by emitting IDs `120` and `121` as analog packets (index payload preserved) instead of button packets (boolean collapse), updated in both live `CIRCUITPY/code.py` and mirror `esphome/circuitpy/code.py`.
- ESPHome/Phase C: Add initial `120`–`124` event consumers in `esphome/spectra_ls_system/packages/spectra-ls-hardware.yaml` and new shared state globals in `packages/spectra-ls-system.yaml` (`hardware_mode`, `control_class`, `menu_override_active`) with deterministic mode routing and clear-on-hardware-change menu override behavior.

- Tooling/Build: Harden `bin/esphome_spectra_build_local.sh` + `bin/esphome_spectra_upload_local.sh` for fast iteration with incremental stage sync, stable local artifact copies, build summary output, optional forced clean stage, and upload helper auto-use of latest staged config.
- ESPHome/OTA: Migrate `esphome/spectra_ls_system.yaml` from legacy `web_server.ota: true` to OTA platform syntax (`ota: - platform: web_server`) for ESPHome 2026.4.0+ compatibility while preserving web UI upload support.
- Tooling/Build: Add local workstation automation scripts under `bin/` for one-command Spectra LS build kickoff (staging copy + path rewrite + compile artifact reporting) with optional OTA upload, so fast Ryzen-side builds avoid HA VM/Celeron compile bottlenecks without modifying tracked runtime YAML.
- ESPHome/Web UI: Enable `web_server` OTA exposure in `esphome/spectra_ls_system.yaml` (`web_server.ota: true`) so the built-in device web UI renders the firmware upload form (POST `/update`) for direct binary uploads.
- UI/Code Cleanup: Deduplicate OLED display lambda option parsing helpers in `esphome/spectra_ls_system/spectra-ls-peripherals.yaml` by reusing a single shared `trim_ascii`/`parse_options` implementation for both control-target prompt and dynamic options lists (no behavior change).
- UI/Code Cleanup: Remove redundant/unreachable second `STATE_NOW_PLAYING` render branch in `esphome/spectra_ls_system/spectra-ls-peripherals.yaml` display lambda and drop unused local state variable, reducing ambiguity in display-state flow.
- UI/Splash Stability: Fix startup splash sequence restart in `esphome/spectra_ls_system/spectra-ls-peripherals.yaml` by preventing delayed `on_boot` splash timer reinitialization after the display loop has already started splash timing.
- UI/Splash Readability: Keep the “SPECTRA” title line visible throughout splash stage 2 (subtitle reveal), removing the abrupt title disappearance while preserving existing splash timing.
- HA/MA Boot Auto-Select Fix: Update `packages/ma_control_hub/script.inc` so startup default target selection includes discovered targets (not only static room targets), preventing `none` from persisting when discoverable control-capable targets exist.
- HA/MA Startup UX: Add fallback auto-pick of first active (playing/paused) allowed target when detected receiver is not ready yet, reducing blank-screen/prompt-on-boot behavior while discovery data settles.
- Docs/Architecture Notes: Expand `esphome/spectra_ls_system/v-next-NOTES.md` with a dedicated control-path/hardware-family roadmap section, including current as-wired implementation snapshot and phased family/codepath expansion plan.
- HA/MA Override Schema: Extend room/target override contract to carry `hardware_family`, `control_path`, `control_capable`, and `capabilities` metadata so overrides can fully represent control routing intent for current and future device families.
- HA/MA Capability Routing: Gate control-host resolution on `control_capable` + routed `control_path` (currently `linkplay_tcp`) so direct POT adjustments are sent only to explicitly control-capable targets.
- HA/MA Routing Policy: Add discovery-first control-path routing in `packages/ma_control_hub/template.inc` with explicit per-target tagging (`linkplay_tcp` now, extensible for future non-LinkPlay paths) and expose active control path as a template sensor.
- HA/MA Fallback Safety: Add `input_boolean.ma_control_fallback_enabled` (default `off`) in `packages/ma_control_hub/input_boolean.inc` and gate static host override/fallback routing branches behind this tunable for clean no-override testing by default.
- HA/MA Target Discovery: Tighten discovered target inclusion in `packages/ma_control_hub/script.inc` to include only linkplay-compatible TCP targets by default, while preserving extensibility for future routing classes.
- Project Guidance: Update `.github/copilot-instructions.md` and `esphome/spectra_ls_system/v-next-NOTES.md` to codify discovery-first onboarding, default-off fallback policy, and per-device control-path decision requirements.
- HA/MA Auto-Discovery: Enhance `packages/ma_control_hub/script.inc` and `packages/ma_control_hub/template.inc` so MA-discovered players with valid entity IDs and IP addresses are treated as first-class targets/options and TCP host candidates, reducing dependency on static per-room host mappings for plug-in onboarding.
- HA/MA Routing: In `sensor.ma_control_hosts`, prefer active target entity `ip_address` when available before static fallback mappings, enabling zero-touch control host resolution for newly discovered compatible players.
- ESPHome/Config Hygiene: Clarify Arylic endpoint section in `esphome/spectra_ls_system/substitutions.yaml` to document HA runtime authority (`sensor.ma_control_hosts` / `sensor.ma_control_port`) and switch bootstrap endpoint defaults to neutral non-site-specific values instead of repo-pinned local hosts.
- ESPHome/Config Hygiene: Reorganize `esphome/spectra_ls_system/substitutions.yaml` tunables into distinct domain sections (system cadence, display/menu UI, audio UX/prompting, lighting UX, and control-loop/log cadence) to remove mixed random grouping and improve operator readability.
- Docs: Update `esphome/spectra_ls_system/SUBSTITUTIONS-TUNING-LEGEND.md` with a substitutions layout map so tuning guidance matches the new sectioned structure.
- ESPHome/Tuning Policy: Adopt B+ as default in `esphome/spectra_ls_system/substitutions.yaml` based on observed low-latency/high-quality network behavior with occasional jitter spikes; reserve B++ as DJ-candidate profile pending extended soak validation.
- ESPHome/Tuning Surface: Add next-batch substitution tunables for non-transport smoothing in `esphome/spectra_ls_system/substitutions.yaml` (control-target evaluation cadence, MA target sync interval, meta-cycle settle delay, input/log throttle intervals) and wire these into `packages/spectra-ls-audio-tcp.yaml` to remove hardcoded timing constants.
- Docs: Update `esphome/spectra_ls_system/SUBSTITUTIONS-TUNING-LEGEND.md` with network-quality guidance, B+ default positioning, and B++ DJ-candidate profile notes.
- ESPHome/Audio UX: Add reboot ambiguity grace handling in `esphome/spectra_ls_system/packages/spectra-ls-audio-tcp.yaml` so a valid MA target + control host can establish lock during early boot even when transient ambiguity sensors report true, preventing repeated post-reboot control-target prompts.
- ESPHome/Tuning: Apply a tighter B++ responsiveness profile in `esphome/spectra_ls_system/substitutions.yaml` (pot intervals/settle and Arylic TCP pacing/burst/worker tuning) for reduced perceived control lag while preserving transport stability margins.
- ESPHome/Substitutions: Prune non-spectra dead keys from `esphome/spectra_ls_system/substitutions.yaml` (legacy BLE presence + lighting-controller carryovers and other unreferenced runtime leftovers) and expand section comments into operator-oriented guidance (purpose, gains, risks, and tuning intent).
- ESPHome/Audio TCP: Add substitution-driven tunables for Arylic TCP worker/log behavior (queue length, worker stack/priority, and TX log throttle) and wire them through build flags into `components/arylic_tcp.h` so they can be tuned without C++ edits.
- ESPHome/Audio TCP: Wire Arylic TCP pacing constants to compile-time substitution-driven build flags from `esphome/spectra_ls_system/substitutions.yaml` (including newly exposed burst-guard knobs), so tuning values are actually applied without editing `arylic_tcp.h` defaults.
- Docs: Add `esphome/spectra_ls_system/SUBSTITUTIONS-TUNING-LEGEND.md` with baseline profile sets (Baseline/Safe/Performance/Aggressive), parameter descriptions, and staged test guidance for per-network tuning.
- ESPHome/Audio TCP: Consolidate duplicated script-level EQ gate/send logic by introducing shared `arylic_set_eq_channel` in `esphome/spectra_ls_system/packages/spectra-ls-audio-tcp.yaml`, with existing `arylic_set_bass/mid/treble` IDs retained as thin compatibility wrappers.
- ESPHome/Audio TCP: Consolidate duplicated EQ pot update/defer logic in `esphome/spectra_ls_system/packages/spectra-ls-audio-tcp.yaml` into a shared channel-aware script path to reduce repeated hot-path code while preserving per-channel behavior and deferred-send semantics.
- Docs: Update `README.md` with explicit external reference links (ESPHome, Home Assistant, Music Assistant, and Arylic/LinkPlay API references) for easier operator onboarding.
- ESPHome/Audio TCP: Add reversible Arylic TCP burst guard in `esphome/spectra_ls_system/components/arylic_tcp.h` to pace sustained command bursts per host/port via a short sliding-window delay (delay/coalesce behavior, no protocol changes) to reduce control-lane chatter while preserving responsiveness.
- ESPHome: Update `esphome/spectra_ls_system/substitutions.yaml` `friendly_name` to remove reserved URL path separator (`/`) and avoid 2026.7.0 validation failure.
- RP2040/Architecture: Pass 3B.1 removes dead legacy inline autocalibration/tracking functions and globals from `code.py` now that `sls_calibration_runtime.py` is authoritative, reducing monolith drift and keeping loop behavior manager-driven.
- RP2040/Docs+Architecture: Add per-file RP ownership/instruction contracts at top of all RP firmware source files (`boot.py`, `code.py`, `sls_*.py`) and add a detailed RP legend document on-device (`CIRCUITPY`) with mirrored repo copy; begin Pass 3B by extracting autocalibration/tracking state machine responsibilities toward a dedicated runtime module to reduce monolith drift risk.
- RP2040/Architecture: Pass 3 introduces reusable runtime helper functions for button-edge emit/log flow and precomputed analog channel profiles to reduce repeated hot-path lookups/branches while preserving packet format and behavioral semantics.
- RP2040/Architecture: Pass 2 modularization extracts analog/calibration helper functions from `code.py` into `sls_analog.py` and `sls_calibration.py` (live `CIRCUITPY` + repo mirror) while preserving runtime loop behavior and packet contract.
- RP2040/Architecture: Begin v-next-safe modularization of firmware by extracting config/protocol/input-decode helpers from monolithic `code.py` into dedicated modules in live `CIRCUITPY/` with synchronized mirror under `esphome/circuitpy/`; preserve existing packet contract and runtime behavior.
- RP2040/Phase B: Add hardware input-capture contract in `CIRCUITPY/code.py` + mirror `esphome/circuitpy/code.py` for v-next reserved events (`120`–`124`) including mode selector, control-class selector, and mode-navigation momentary event emits; preserve existing event IDs and behavior while adding parallel v-next event path.
- Productization: de-track `spectra_ls_primary_tcp_host.yaml` and `spectra_ls_room_tcp_host.yaml` from git/GitHub while keeping local files in place; host defaults now use secrets-based values and these per-user endpoint files are ignored to prevent personal config pollution.
- Docs/Policy: add explicit universal-product directive in `.github/copilot-instructions.md` forbidding tracked per-user host/IP config artifacts.
- Docs/Policy: Add a required pre-flight checklist to `.github/copilot-instructions.md` for any file move/delete operation; session must show backup path, planned `CHANGELOG.md` line, and restore command/path before execution.
- Docs/Policy: Strengthen `.github/copilot-instructions.md` with mandatory file move/delete governance — deletes now require non-repo backup + changelog entry + restore path, and moves/renames must be changelogged with source/destination paths.
- Repo/ESPHome: Rename `esphome/secrets.example.yaml` to `esphome/secrets.example` so the secrets template is not treated as an ESPHome dashboard project.
- ESPHome: Phase 16 rename step on `spectra_ls_system` path — rename final active package includes from `control-board-audio-tcp.yaml` and `control-board-lighting.yaml` to `spectra-ls-audio-tcp.yaml` and `spectra-ls-lighting.yaml`, and repoint `esphome/spectra_ls_system.yaml` include map/comments.
- HA: Harden `sensor.now_playing_state` in `packages/ma_control_hub/template.inc` to avoid propagating transient `unknown/unavailable` from `sensor.now_playing_entity`; fallback now resolves to `sensor.ma_active_state` (or `idle`) for stable rename-step validation and routing diagnostics.
- Docs: Normalize section numbering/order in `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` so rename validation checks run in ascending sequence (9 → 10 → 11).
- ESPHome: Phase 15 rename step on `spectra_ls_system` path — rename system package include from `packages/control-board-system.yaml` to `packages/spectra-ls-system.yaml` and repoint `esphome/spectra_ls_system.yaml` include.
- ESPHome: Phase 14 rename step on `spectra_ls_system` path — rename UI package include from `packages/control-board-ui.yaml` to `packages/spectra-ls-ui.yaml` and repoint `esphome/spectra_ls_system.yaml` include.
- Docs: Add a dedicated `ma_control_hub` package-loader regression template to `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` for fast PASS/WARN/FAIL checks in HA Developer Tools after reload/restart.
- Repo: Add regression guardrails for `ma_control_hub` split package layout by ignoring `packages/ma_control_hub/*.yaml` (allow only `.inc`) and adding `.github/validate-ma-control-hub-layout.sh` to fail fast on duplicate fragments or missing host include files.
- HA: Fix `ma_control_hub` package loader conflicts by removing duplicate `packages/ma_control_hub/*.yaml` split fragments (keep `.inc` only) so `!include_dir_named packages` does not auto-load sub-fragments as standalone packages.
- HA: Restore missing `/config/spectra_ls_primary_tcp_host.yaml` and `/config/spectra_ls_room_tcp_host.yaml` include files used by `packages/ma_control_hub/input_text.inc` to resolve startup config load errors.
- ESPHome: Phase 13 rename step on `spectra_ls_system` path — rename hardware package include from `packages/control-board-hardware.yaml` to `packages/spectra-ls-hardware.yaml` and repoint `esphome/spectra_ls_system.yaml` include.
- ESPHome: Phase 12 rename step on `spectra_ls_system` path — rename active peripherals include from `control-board-peripherals-no-rings.yaml` to `spectra-ls-peripherals.yaml` and repoint `esphome/spectra_ls_system.yaml` include.
- Repo: Stop syncing archived `previous/` trees to GitHub by ignoring `esphome/control-py/previous/` and `esphome/spectra_ls_system/previous/`.
- ESPHome: Move legacy/stale package files out of active paths into `previous/` (non-runtime archive storage).
- Repo: Sync `esphome/spectra_ls_system/` content to `main` so GitHub reflects the active spectra_ls_system project tree.

## 2026-04-16

- ESPHome: Phase 11 rename step on tracked main path — rename archived rings peripherals file from `esphome/control-py/previous/control-board-peripherals.yaml` to `esphome/control-py/previous/spectra-ls-peripherals-rings-legacy.yaml` (archive-only, not in active includes).
- ESPHome: Phase 10 rename step on tracked main path — rename legacy non-TCP audio package file from `esphome/control-py/packages/control-board-audio.yaml` to `esphome/control-py/packages/spectra-ls-audio-legacy.yaml` (legacy/stale, TCP package remains authoritative).
- ESPHome: Phase 9 rename step on tracked main path — rename legacy headless package file from `control-board-headless.yaml` to `spectra-ls-headless.yaml` (no active include references).
- ESPHome: Phase 8 rename step on tracked main path — rename active peripherals include from `spectra-ls-peripherals-no-rings.yaml` to `spectra-ls-peripherals.yaml` and repoint `esphome/control-board-esp32-tcp.yaml` include.
- Docs: Update rename validation wording in `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` from “Peripherals No-Rings” to generic “Peripherals” for the new filename.
- ESPHome: Phase 7 rename step on tracked main path — rename no-rings peripherals file to `spectra-ls-peripherals-no-rings.yaml` and repoint `esphome/control-board-esp32-tcp.yaml` include.
- Docs: Add targeted post-rename HA reload validation template (peripherals no-rings step) to `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` for per-step spectra rename checks.
- ESPHome: Phase 6 rename step on tracked main path — rename hardware package to `spectra-ls-hardware.yaml` and repoint `esphome/control-board-esp32-tcp.yaml` include.
- Docs: Add targeted post-rename HA reload validation template (hardware package step) to `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` for per-step spectra rename checks.
- ESPHome: Phase 5 rename step on tracked main path — rename UI package to `spectra-ls-ui.yaml` and repoint `esphome/control-board-esp32-tcp.yaml` include.
- Docs: Add targeted post-rename HA reload validation template (UI package step) to `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` for per-step spectra rename checks.
- ESPHome: Phase 4 rename step on tracked main path — rename system package to `spectra-ls-system.yaml` and repoint `esphome/control-board-esp32-tcp.yaml` include.
- Docs: Add targeted post-rename HA reload validation template (system package step) to `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` for per-step spectra rename checks.
- ESPHome: Phase 3 rename step on tracked main path — rename audio TCP package to `spectra-ls-audio-tcp.yaml` and repoint `esphome/control-board-esp32-tcp.yaml` include.
- Docs: Add targeted post-rename HA reload validation template (audio package step) to `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` for per-step spectra rename checks.
- Docs: Add targeted post-rename HA reload validation template (lighting package step) to `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` for per-step spectra rename checks.
- ESPHome: Phase 2 rename step on tracked main path — rename lighting package to `spectra-ls-lighting.yaml` and repoint `esphome/control-board-esp32-tcp.yaml` include.
- Docs: Publish `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` to `main` and add README high-level system-test overview for Templates 1–5 smoke/diagnostic workflow.
- HA: Prevent `ma_control_hub` split fragments from being misloaded as standalone packages by renaming `packages/ma_control_hub/*.yaml` to `*.inc` and updating `packages/ma_control_hub.yaml` includes.
- HA: Restore `packages/ma_control_hub.yaml` and all split files from `menu-only` branch for parity, and revert temporary absolute include-root rewrite.
- HA: Fix `packages/ma_control_hub.yaml` include roots to `/config/packages/ma_control_hub/*` so YAML reload resolves split package files correctly.
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
