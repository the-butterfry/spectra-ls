<!-- Description: Retroactive architecture and feature documentation for the active Spectra LS ESPHome runtime codebase. -->
<!-- Version: 2026.06.09.1 -->
<!-- Last updated: 2026-06-09 -->

# Spectra LS Runtime Architecture (Retroactive Baseline)

## Purpose

This document captures the **current active runtime architecture** for `esphome/spectra_ls_system` so future changes can be made against a stable, explicit baseline.

Entry point: `esphome/spectra_ls_system.yaml`

## Active include graph (source of truth)

- `substitutions.yaml`
- `spectra-ls-peripherals.yaml`
- `packages/spectra-ls-hardware.yaml`
- `packages/spectra-ls-ui.yaml`
- `packages/spectra-ls-system.yaml`
- `packages/spectra-ls-diagnostics.yaml`
- `packages/spectra-ls-audio-tcp.yaml`
- `packages/spectra-ls-lighting.yaml`

C++ local components:

- `components/arylic_tcp.h`
- `components/sls_oled_text_layout.h`
- `components/sls_menu_nav.h`
- `components/rp2040_uart`
- `components/cpu_usage`

## Runtime domains

### 1) Boot + platform domain

Owned in `spectra_ls_system.yaml`:

- ESP32-S3 + ESP-IDF setup
- Wi-Fi/API/OTA/web server
- build flags for Arylic TCP transport tuning
- on-boot sequencing:
  - target options refresh
  - splash/contrast init
  - lighting sync
  - menu/display state init

### 2) Shared-state domain

Owned in `packages/spectra-ls-system.yaml`:

- cross-package globals (menu/display/audio/meta/lighting/control-target state)
- cadence loops (heartbeat, HTTP poll hooks, screensaver watchdog)
- calibration/state bookkeeping
- base scripts (`note_user_input`, `note_menu_input`, calibration flow, status logging)
- exported ESP status text sensors include transport-safe OLED diagnostics (`esp_oled_status`) with ASCII-sanitized + bounded payloads to avoid malformed UTF-8/protobuf decode failures during telemetry updates
- `esp_oled_status` keeps HA display policy as authority and applies a bounded Arylic-title fallback only when HA policy allows rendering but HA title is transiently empty, preventing short `oled:-` gaps during metadata propagation lag
- `esp_oled_status` now fail-closes to blank payload (`-`) when live playback evidence is absent (no HA `playing`, no transport-playing signal, and no fresh advancing now-playing clock), preventing idle `audio|oled:SRC`/source-placeholder carryover after playback stops
- OLED render compute path (`spectra-ls-peripherals.yaml`) now applies the same live-playback evidence gate to source-context placeholder promotion: `SRC` is emitted only when transport playback is live, and remains blank under idle/no-transport conditions even if source context strings are present
- Display-state deep detection now treats passthrough source contexts without track evidence (no title/artist/album cache, no transport-playing flags, and no recent position advancement) as no-audio-activity, forcing blank state instead of lingering audio-mode no-meta posture
- Source-only passthrough hints are now time-bounded in OLED now-playing rendering: source text appears during bounded source-popup windows (not persistently), and source context popup can be invoked from button press with host attribution (`source @ host:port`) for quick operator provenance checks
- OLED metadata cache rescue now excludes source-like hint titles when source-popup window is inactive, preventing sticky `Optical In`/`SRC`/source-context text carryover after transient hint display expires
- Runtime display-state + now-playing renderer now fail-close to blank/no-bar posture for passthrough contexts that have no text payload outside active source-hint windows, preventing bar-only “playing” surfaces when track metadata is absent
- Component freshness semantics now require recent progress evidence for `fresh_play_signal`; `playing` without progress clock is explicitly classified as stale (`playing_without_fresh_signal`) to reduce false-positive metadata freshness in passthrough routes
- Component metadata-prep now applies bounded passthrough metadata cache reuse (title/artist/album/app) during active source-only windows, preventing immediate OLED blank collapse after transient upstream metadata drops while preserving fail-closed blanking when cache TTL expires
- Source popup renderer now uses operator-focused formatting (`SOURCE`, source value, `Target: <active target>`, `Mode: <optical|wifi|bluetooth|line-in|...>`), with source label producer reduced to source/app value to avoid cluttered host/port-heavy popup text
- Source popup layout is now compact 3-line to avoid OLED overlap (`SOURCE`, source value, `T:<target> M:<mode>`)
- Source popup now renders as two alternating pages within popup window for readability on constrained OLED height: page A shows `SOURCE` + source label, page B shows `TARGET` + target label + `MODE` label
- Source popup trigger ownership is now outside compute loop and popup render is fixed single-page (header + source + detail) to prevent overlap/timer-thrash flashing under transient metadata/source windows
- Passthrough metadata lock emphasis is enforced in component selection path (`metadata_stack`) by preferring active/paused candidates with real metadata payload in passthrough windows, reducing route-target source-only winner drift
- Runtime HA ingest loop now applies guarded now-playing contract refresh when playback is active but title/artist are unresolved after restart, reducing blank-until-song-change bootstrap gaps
- Runtime HA ingest/bootstrap now seeds recent-playing timestamps during early uptime `playing` states and rate-limited forced refreshes, reducing full-reboot blank-now-playing windows
- Passthrough no-metadata idle policy remains fail-closed blank, but explicit user interaction wake windows now permit a constrained audio overlay path (source wake header + volume bar) so hardware feedback remains visible during adjustments
- Wake overlay path is gated by very recent user input (`idle <= 2.5s`) in both display-state and renderer paths, preventing persistent idle volume-only frames when nothing is actively playing
- Component metadata-prep now-playing entity selection is metadata-bearing freshness-first (prefer fresh + payload metadata before freshness-only candidates) to avoid first-track stale pinning when a transport-live route entity does not publish per-track metadata
- Component now-playing entity selection includes scored candidate ordering (fresh signal + payload metadata + recent progress + Music Assistant app/source hints, with stale end-of-track penalties) so active MA metadata carriers outrank stale route-side DLNA carriers during mixed-signal windows
- OLED cache-rescue is now fail-closed for passthrough no-metadata windows: when source context is passthrough (Optical/Line-In/AUX/Coax/HDMI/ARC) and no current metadata payload exists, stale cached title/artist/album are not resurrected; source hint is only allowed in the active source-popup window
- Passthrough no-metadata runtime render now keeps a deterministic live source label fallback (for example `Optical In`) during active playback so OLED does not oscillate between stale-title carryover and full blank at track/startup boundaries
- Passthrough no-text suppression now requires missing playback evidence before forcing blank state; active passthrough windows (playing transport/source context present) remain render-eligible with source-label fallback, while true idle passthrough still fail-closes to blank
- Source-like title filtering now preserves guarded passthrough fallback titles (for example `Optical In`) in active no-metadata passthrough windows so runtime does not regress to blank/volume-only frames after assigning source fallback text
- Active passthrough no-metadata fallback now enriches OLED context with a secondary target line (when available) so source-only windows are informative rather than top-line-only
- ESP `esp_oled_status` export now mirrors runtime source-context fallback when title metadata is absent but playback evidence and display policy allow rendering, preventing false `audio|oled:-` reports while OLED is showing passthrough source context
- Runtime passthrough source-only fallback was refined to keep concise source context without injected room/target scrolling text in no-metadata windows
- Runtime audio control send paths (volume/EQ/source) now rehydrate control hosts from live HA control-host sensors at send time when cache was cleared, preventing post-target-churn `no_hosts` dead windows when HA host value does not emit a fresh change event
- Runtime audio control path now includes bounded split-brain auto-heal for passthrough contexts: when active target differs from effective now-playing entity and ambiguity is not active, runtime requests `spectra_ls.set_active_target` to align control host with the actually playing entity before subsequent control writes
- Runtime split-brain auto-heal service contract now uses the component-required payload key `target` (not `entity_id`) when calling `spectra_ls.set_active_target`, ensuring explicit target handoff requests are applied instead of no-op schema mismatches
- Runtime split-brain auto-heal trigger coverage is now autonomous (not control-write-only): convergence checks run on now-playing entity/source/play-state HA transitions and in the periodic HA refresh cadence, preserving passthrough-only + ambiguity/cooldown fail-closed guards while removing manual-poke timing dependence
- Runtime split-brain auto-heal now additionally requires active playback state (`playing`/`paused`) before requesting target handoff, and avoids redundant nested refresh-path trigger calls because interval-level reevaluation already covers that branch
- Runtime display-state now treats HA `playing` as effective only with recent playback evidence (meta/position recency), preventing idle passthrough/source-only windows from holding now-playing state on stale/raw `playing` flags
- Runtime passthrough no-text idle suppression now keys no-play evidence to concrete passthrough live activity signals (transport-playing flags or recent position advancement), not HA source-heartbeat recency, preventing overnight source-only `Optical In` idle windows from remaining render-eligible without real playback activity
- Runtime passthrough source-only policy is now strict fail-closed outside popup/wake windows: when title/artist/album payload is absent in passthrough context, display-state and renderer suppress now-playing chrome regardless of upstream `playing` heartbeat recency, preventing persistent no-track `Optical In` idle rendering
- Runtime passthrough source-label/title fallback no longer promotes passthrough source text into cached title outside active source-hint windows, closing a residual path where source-only `Optical In` could bypass no-text suppression and remain render-eligible in idle windows
- ESP `esp_oled_status` passthrough no-track policy is aligned to fail closed (`-`) instead of source-label fallback text, preventing telemetry/UI validation drift where status exported `Optical In` while strict no-text passthrough policy should be blank
- ESP control target diagnostics now emit canonical `ma_active_target` contract value (not stale-friendly-first), preventing route/helper/control-target comparison drift in contract validation
- Component now-playing contract sensors for artist/album/app/source prefer metadata-stack values first and fallback to entity attrs, preserving contract continuity when source entity attrs degrade transiently
- ESP status text telemetry cadence is intentionally bounded at 30s for operator log clarity (`esp_control_handoff_status`, `esp_control_target`, `esp_oled_status`, `arylic_http_scheme`, `arylic_http_transport`) to avoid repeated unchanged logs
- ESP emits a dedicated 30s HA-contract metadata summary line (`ha_meta`) sourced from HA-authoritative surfaces (`ha_audio_media_class`, `ha_audio_display_allowed`, `ha_audio_state`, `ha_audio_source`, `ha_audio_app`, `ha_audio_title`) so operators can distinguish HA policy state from transport-native Arylic status lines
- `ha_meta` field provenance is now single-contract for state/source/app/title: ESP binds these to component-native now-playing contract surfaces (`sensor.spectra_ls_component_now_playing_state`, `sensor.spectra_ls_component_now_playing_source`, `sensor.spectra_ls_component_now_playing_app`, `sensor.spectra_ls_component_now_playing_title` via substitutions), preventing mixed cross-family context in periodic metadata logs
- OLED metadata tuple coherence contract: ESP now binds title/artist/album from the component-native now-playing contract family (`sensor.spectra_ls_component_now_playing_title`, `sensor.spectra_ls_component_now_playing_artist`, `sensor.spectra_ls_component_now_playing_album`) via substitutions, preventing stale cross-source album/artist carryover when one legacy MA-active field lags
- ESP now consumes explicit now-playing context surfaces from component-native contracts (`sensor.spectra_ls_component_now_playing_entity`, `sensor.spectra_ls_component_now_playing_friendly`, `sensor.spectra_ls_component_now_playing_preview_key`) and forces bounded metadata/display refresh on entity-switch and preview-key changes, reducing stale carryover windows during source handoff churn
- Component now emits deterministic `sensor.spectra_ls_component_now_playing_preview_key` values (non-empty contract-derived key) so ESP source-switch and non-music preview transitions can react to contract-level content changes without relying on volatile/freeform fields
- Component now emits `sensor.spectra_ls_component_now_playing_freshness_age_s` and ESP consumes it to suppress stale cached OLED metadata rescue when freshness is outside bounded windows, reducing stale carryover during churn without changing display-policy authority
- `ha_meta` title rendering is fail-closed for policy coherence: title is blanked when `display_allowed=false` or media class is non-display (`none/unknown/unavailable`) to prevent stale MA title carryover in hidden-display contexts
- Arylic HTTP poller now learns and reuses per-host preferred scheme/port from successful sessions (`arylic_http_pref_*` globals), and suppresses opposite-scheme fallback flips when the current host is already on a known-good scheme; this preserves discovery-first dynamic routing while reducing scheme churn without hardcoded host pinning
- Arylic HTTP hitch-stability defaults now use a tighter request timeout budget with stronger fail-backoff windows and delayed fallback-scheme switching on sustained failures, reducing perceived UI hitch/freeze windows under repeated transport errors while preserving discovery-first fallback behavior
- Arylic HTTP polling now includes a short interaction-priority guard window keyed to `last_input_ms`, temporarily skipping non-critical HTTP status polls immediately after user input so tactile control operations remain prioritized during rapid knob activity while transport errors are present
- Arylic HTTP preferred transport memory now keeps bounded per-host slots (primary + alternate) so active-target host churn can restore each host’s last-known good scheme/port, preventing repeated default-protocol restarts when different hosts require different HTTP/HTTPS behavior
- Runtime control-host ownership cutover is now authority-driven (non-hybrid in normal operation): `sensor.ma_authority_mode` exposes effective `legacy|component` authority, legacy target/host writers in `ma_control_hub` are disabled when component authority is active, and `sensor.ma_control_hosts` prefers component host-cutover candidate host from `sensor.spectra_ls_host_authority_cutover_gate` while preserving fail-closed fallback behavior when component authority/candidate host is unresolved
- Host-candidate coherence guard hardening: component host-cutover candidate host is now accepted only when gate status is `ready` **and** candidate target matches current active target (or active target is unresolved), preventing stale candidate host drift under feed churn.
- ESP control-route ingest now binds component-native route feeds (`sensor.spectra_ls_component_control_targets`, `sensor.spectra_ls_component_control_hosts`, `sensor.spectra_ls_component_control_host`, `sensor.spectra_ls_component_control_port`) for active target/host/port option refresh and route cache updates
- ESP control handoff telemetry now treats resolved active-friendly context as a fallback target-presence signal, reducing transient false `no_target` during helper timing windows
- ESP control-host ingest now applies bounded runtime compatibility fallbacks (`sensor.ma_control_hosts` / `sensor.ma_control_host` / `sensor.ma_control_port`) when component-native control host feeds are transiently unresolved, preserving fail-closed posture for sustained invalid feeds while reducing false `no_hosts` gating during feed churn
- Validation semantics: `sensor.spectra_ls_system_esp_oled_status=lighting|oled:-` is expected in lighting mode and should not be interpreted as degraded audio OLED metadata
- Runtime OLED telemetry clarity hardening: lighting mode now emits explicit `lighting|oled:LIGHTING` when no audio title line is applicable, replacing ambiguous blank placeholder output
- AY.5 hard cutover: active authority is component-pinned in normal operation (legacy authority mode selection is disabled), and component auto-select keeps current valid helper target by default unless explicit force is requested, reducing unsolicited target/host churn from transient ranking noise
- AY.6 transport correction: Arylic HTTP timeout/cadence defaults were widened from an overly aggressive timeout budget to tolerate normal LinkPlay/AirPlay endpoint response jitter, and default probe bootstrap was corrected to HTTP:80 (from HTTPS:443) for HTTP-first LinkPlay targets to avoid repeated TLS handshake/backoff churn before fallback. This reduces `http_request` collapse windows without changing discovery-first routing or authority ownership contracts
- AY.7 hitch guard correction: Arylic HTTP polling is suppressed during transient HA idle/off windows when Arylic is already known-playing, and post-input quiet guard was extended so polling does not immediately re-enter after dense control bursts; this reduces interval blocking spikes without changing ownership or route contracts
- Lighting runtime brightness apply path now sends brightness-only payloads to `script.control_board_set_light_dynamic` (no HS payload on brightness-only operations), preventing hue/saturation drift while adjusting brightness via slider/brightness mode

### 3) Hardware ingest domain

Owned in `packages/spectra-ls-hardware.yaml`:

- UART transport and RP2040 hub
- reserved hardware-mode/control-class streams (`120`, `121`)
- mode nav button events (`122`–`124`)
- mode-to-screen/menu routing scripts

### 4) UI/menu domain

Owned in `packages/spectra-ls-ui.yaml` + `spectra-ls-peripherals.yaml`:

- menu state machine and menu action handlers
- encoder and button menu navigation
- dynamic options parsing for room/target/meta/control-target prompts
- display renderer (splash, menu, now-playing, EQ, lighting, blank)
- display-state decision script (`compute_display_state`)
- now-playing progress pipeline keeps cache continuity during HA↔Arylic handoff gaps by holding/projection of last valid progress while playback is active, reducing transient progress-bar dropouts when metadata arrives before stable duration/position updates

### 5) Audio control domain (TCP-only)

Owned in `packages/spectra-ls-audio-tcp.yaml`:

- transport controls (play/pause/next/prev/source/meta select)
- volume + EQ ingest from RP2040 analog/encoder
- guarded send paths via `arylic_tcp` (prompt/host gating)
- active-playback volume unblock: volume paths may proceed during prompt state when playback is active and hosts are resolvable (still fail-closed when hosts are unresolved)
- host/port intake from HA (`sensor.ma_control_hosts`, `sensor.ma_control_port`)
- reconnect-aware host-feed guardrails: transient HA/API reconnect invalid updates (`''/unknown/unavailable/none`) retain cached control-host surfaces during bounded reconnect/pending windows; sustained invalid feeds still fail-closed clear caches
- reconnect-aware port-feed guardrails: transient non-numeric `sensor.ma_control_port` values are parsed as guarded text and no longer produce numeric conversion warnings; bounded fallback keeps runtime control port stable during reconnect churn
- now-playing/meta resolver feed inputs
- explicit now-playing entity/friendly/preview-key feed inputs are consumed for source-switch reactivity and low-information OLED source fallback polishing
- active-friendly status ingest lane now binds to component now-playing friendly surface (`sensor.spectra_ls_component_now_playing_friendly`) instead of runtime `sensor.ma_active_friendly`, reducing legacy read-path coupling in audio runtime logs/status
- active-target ingest lane now binds to component surface (`sensor.spectra_ls_component_active_target`) for ESP read-path updates, and UI prompt commit lane now routes through explicit component service `spectra_ls.set_active_target` (guarded helper apply semantics)
- metadata-candidates ingest lanes now bind to component surfaces (`sensor.spectra_ls_component_meta_candidates`, `binary_sensor.spectra_ls_component_meta_low_confidence`) for active candidate list + confidence posture
- metadata override menu apply lane now routes through explicit component service `spectra_ls.set_metadata_override` (guarded apply/clear semantics); direct ESP helper writes for metadata override are retired from active UI path while helper entities remain compatibility storage surfaces
- control-target prompt lifecycle

### 6) Lighting control domain

Owned in `packages/spectra-ls-lighting.yaml`:

- room/target selection and sync with HA helpers
- slider/encoder mapping to brightness/hue/sat
- debounced light script calls (`script.control_board_set_light_dynamic`)
- toggle actions (room/selected target)
- menu-hold and resume behavior for lighting-adjust flows

### 7) Diagnostics domain

Owned in `packages/spectra-ls-diagnostics.yaml`:

- OLED contrast diagnostics and control number
- CPU/heap/PSRAM diagnostics
- CPU periodic stats logging emits every 30s for lightweight runtime health sampling during active troubleshooting
- virtual input battery harness for mode/control-path validation

## External contracts consumed by runtime

Primary HA helper/sensor contracts (via substitutions + package usage):

- target/route: `sensor.spectra_ls_component_active_target`, `sensor.spectra_ls_component_control_hosts`, `sensor.spectra_ls_component_control_host`, `sensor.spectra_ls_component_control_port`, `sensor.spectra_ls_component_control_targets` (helper `input_select.ma_active_target` remains compatibility storage, but active ESP write lane is mediated by component service `spectra_ls.set_active_target`)
- control-host compatibility fallbacks (read-lane safety only): `sensor.ma_control_hosts`, `sensor.ma_control_host`, `sensor.ma_control_port` are consumed by ESP only when component-native control-host feeds are transiently unresolved
- metadata: `sensor.spectra_ls_component_now_playing_title`, `sensor.spectra_ls_component_now_playing_artist`, `sensor.spectra_ls_component_now_playing_album`, `sensor.spectra_ls_component_now_playing_app`, `sensor.spectra_ls_component_now_playing_source`, `sensor.spectra_ls_component_now_playing_state`, `sensor.spectra_ls_component_now_playing_duration`, `sensor.spectra_ls_component_now_playing_position`, `sensor.spectra_ls_component_now_playing_volume`
- OLED now-playing tuple surfaces: `sensor.spectra_ls_component_now_playing_title`, `sensor.spectra_ls_component_now_playing_artist`, `sensor.spectra_ls_component_now_playing_album` (single-source OLED metadata contract)
- now-playing coherence surfaces: `sensor.spectra_ls_component_now_playing_preview_key`, `sensor.spectra_ls_component_now_playing_freshness_age_s` (deterministic preview-change token + freshness-age signal for consumer-side reactivity)
- candidate/override: `sensor.spectra_ls_component_meta_candidates`, `binary_sensor.spectra_ls_component_meta_low_confidence` + component write service `spectra_ls.set_metadata_override` (helper entities `input_boolean.ma_meta_override_active` / `input_text.ma_meta_override_entity` retained as compatibility storage behind service semantics)
- lighting helpers: `input_select.control_board_room`, `input_select.control_board_target`, and dynamic catalog sensors

## Feature map (user-visible)

- Hardware-first room/target/audio control surface
- OLED menu + now-playing + EQ + lighting rendering
- Audio transport via MA-selected target host(s) over Linkplay TCP
- Prompted control-target selection under ambiguity
- Dynamic lighting room/target routing with direct slider apply
- Virtual input diagnostics for mode/class/event sanity checks

## Known active constraints

- Runtime still depends on legacy helper naming (`control_board_*`) in several HA contracts.
- Direct audio routing currently supports `linkplay_tcp` path only.
- Some docs/files in this folder are archival/reference and not runtime-included (see dead-path matrix).

## Change discipline for future slices

When runtime behavior changes, update this file in the same change set with:

1. domain impact (which of the 7 domains changed),
2. contract deltas (added/removed/renamed helpers/entities),
3. migration note if legacy compatibility is affected.
