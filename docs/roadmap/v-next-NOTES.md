<!-- Description: v-next implementation notes for Spectra LS System hardware-first control plan and migration policy. -->
<!-- Version: 2026.05.04.14 -->
<!-- Last updated: 2026-05-04 -->

# v-next NOTES — Hardware-First Control Plan (Implementation Guide)

> Scope: Hardware-driven UX redesign for Spectra LS Control Board v2.
> Audience: Implementation agent working across RP2040 CircuitPython + ESPHome packages + HA helpers.
> Status: Draft plan. Update as decisions solidify.

Operator local deployment note (non-contract, do not hardcode in product logic):

- Current Spectra ESP node management IP: `192.168.10.40`.

Latest run update (2026-05-04, Slice-BP LC-01 component entity namespace binding remap):

- Verified live HA component entities are exposed as `sensor.component_*` / `binary_sensor.component_*` (not `sensor.spectra_ls_component_*`), and remapped active ESP substitutions accordingly in `esphome/spectra_ls_system/substitutions.yaml`.
- Runtime track disposition: implemented (ESP consumer-binding correction only).
- Component track disposition: compatibility-shimmed (component contracts/services unchanged).
- P1/P2/P3 impact check: no source-of-truth ownership change; environment-binding correctness hardening only.
- README parity: no material repo-state change.

Latest run update (2026-05-04, Slice-BQ LC-05 legacy scaffold constant governance split):

- Split component `LEGACY_*` internal scaffold constants into explicit governance buckets (`compat_required` vs `retire_candidate`) and added deterministic retirement gate IDs (`LC-05` / `LC-06`) in `custom_components/spectra_ls/const.py`.
- Exported the same classification packet in config-entry diagnostics to keep retirement gating auditable from one surface.
- Runtime track disposition: compatibility-shimmed (no runtime behavior mutation).
- Component track disposition: implemented (constant governance split + diagnostics exposure).
- P1/P2/P3 impact check: no source-of-truth ownership change; migration governance/retirement traceability hardening only.

Latest run update (2026-05-04, Slice-BR ESP legacy rip-out inventory documentation):

- Added explicit ESP legacy retirement inventory coverage to `docs/roadmap/LEGACY-CODEPATH-CLEANUP-TRACKER.md` for fallback host/port bindings, fallback listeners, metadata helper passthrough bindings, and dual-path devtools compatibility references.
- Mapped each retained ESP compatibility surface to retirement gates (`LC-06` / `LC-07` / `LC-08`) with concrete exit criteria for eventual removal.
- Runtime track disposition: compatibility-shimmed (docs-only slice; no runtime behavior mutation).
- Component track disposition: compatibility-shimmed (docs-only slice; no component behavior mutation).
- P1/P2/P3 impact check: no source-of-truth ownership change; retirement traceability and cleanup completeness hardening only.

Latest run update (2026-05-04, Slice-BS LC-06 runtime retirement decomposition):

- Decomposed LC-06 (`packages/ma_control_hub/*`) from a single placeholder into explicit retirement lanes (writer lane, override lane, metadata override helper storage lane, provider telemetry helper sink, server-profile/API helper stack, and metadata resolver read surfaces).
- Added lane-level replacement targets and execution order in `docs/roadmap/LEGACY-CODEPATH-CLEANUP-TRACKER.md`; LC-06 status moved to `active` (decomposition complete, implementation pending).
- Runtime track disposition: compatibility-shimmed (docs-only planning slice; no runtime behavior mutation).
- Component track disposition: compatibility-shimmed (docs-only planning slice; no component behavior mutation).
- P1/P2/P3 impact check: no source-of-truth ownership change; retirement sequencing clarity and traceability hardening only.

Latest run update (2026-05-04, Slice-BT LC-07/LC-08 execution sweep):

- Added component-owned metadata override status entities (`binary_sensor.component_metadata_override_active`, `sensor.component_metadata_override_entity`) and switched ESP metadata override substitutions to consume component surfaces.
- Added ESP fallback-hit evidence counters and runtime telemetry surfaces (`esp_control_fallback_*`) so LC-07 fallback retirement can be gated on measured non-use instead of log sampling alone.
- Runtime track disposition: implemented (ESP substitution/telemetry hardening only; fallback listeners intentionally retained pending soak evidence).
- Component track disposition: implemented (metadata override status packet surfaces published for ESP consumers).
- P1/P2/P3 impact check: no source-of-truth ownership change; LC-07/LC-08 execution evidence and read-lane cutover hardening only.

Latest run update (2026-05-04, Slice-BV Arylic HTTP connect-reset churn stabilization):

- Hardened ESP Arylic HTTP failure handling so unknown-transport hosts escalate quickly to long backoff windows (up to max at fail>=3) and suppress scheme-flip probe churn when no known-good HTTP transport history exists for that host.
- Verified in-session build + OTA + live logs on `192.168.10.40`; runtime now backs off to `120000ms` on sustained reset churn while control path remains healthy (`ESP Control Handoff Status=ready`, fallback counters unchanged at zero).
- Runtime track disposition: implemented (poll/backoff stabilization only; control-route ownership unchanged).
- Component track disposition: compatibility-shimmed (component contracts unchanged; equivalent failure mode not in component lane).
- P1/P2/P3 impact check: no source-of-truth ownership change; runtime transport-noise suppression and LC-07 soak safety hardening only.

Latest run update (2026-05-04, Slice-BW LC6-L04 provider telemetry helper-sink migration bridge):

- Added component-owned provider telemetry packet mirror in snapshot write-controls (`write_controls.metadata_provider_last`) and published diagnostics sensor `sensor.component_metadata_provider_status` (status/providers/response/item_uri/reason/updated_at/age/source).
- Migrated active validation templates to component-first provider telemetry reads with bounded runtime helper fallback for compatibility during staged retirement.
- Runtime track disposition: compatibility-shimmed (runtime helper sink writes retained as temporary source while consumers cut over).
- Component track disposition: implemented (component packet/sensor now authoritative consumer surface).
- P1/P2/P3 impact check: no source-of-truth ownership change; LC6-L04 consumer cutover bridge and retirement readiness hardening only.

Latest run update (2026-05-04, Slice-BX LC6-L04 runtime provider sink retirement):

- Added component telemetry ingest service `spectra_ls.set_metadata_provider_packet` and coordinator-owned packet state so provider diagnostics are sourced from component state instead of runtime helper sink writes.
- Updated runtime provider dispatch (`script.ma_send_metadata_to_providers`) to publish telemetry via component service in normal operation, with bounded helper-write fallback only when component sink is unavailable.
- Runtime track disposition: implemented (helper sink removed from active provider dispatch path; fallback-only compatibility retained).
- Component track disposition: implemented (service + snapshot packet now authoritative telemetry owner for provider refresh diagnostics).
- P1/P2/P3 impact check: no source-of-truth ownership change; LC6-L04 sink retirement execution and migration safety hardening only.

Latest run update (2026-05-04, Slice-BY LC6-L05 server-profile/API helper-stack migration bridge phase-1):

- Extended component diagnostics packet `ma_backend_profile` with explicit MA API URL capture (`sensor.ma_api_url`) alongside profile/effective URL state and published component-facing bridge entities `sensor.component_backend_profile` + `sensor.component_ma_api_url`.
- Runtime track disposition: compatibility-shimmed (runtime profile/url helpers remain source while bridge consumers cut over).
- Component track disposition: implemented (component snapshot/sensor bridge surfaces now available for deterministic LC6-L05 parity validation).
- P1/P2/P3 impact check: no source-of-truth ownership change; LC6-L05 bridge execution and retirement-readiness hardening only.

Latest run update (2026-05-04, Slice-BZ scheduler deterministic guidance consistency hardening):

- Updated deterministic validation template to treat `skipped_component_startup_no_mix` bridge posture under component authority as non-actionable bridge failure context, preventing contradictory `RUN_BRIDGE` hints while metadata-prep blockers are the real next action.
- Runtime track disposition: compatibility-shimmed (diagnostics-only template behavior hardening).
- Component track disposition: implemented (operator guidance now aligns with no-mix startup semantics).
- P1/P2/P3 impact check: no source-of-truth ownership change; diagnostics actionability consistency hardening only.

## Custom-Component Parallel Program (Required)

`custom_components/spectra_ls` must be developed in parallel with the current runtime stack (`packages/` + `esphome/`) and cannot be treated as a big-bang replacement.

Execution system reference: `docs/program/PARALLEL-PROGRAM-PLAYBOOK.md`.

### Required migration sequence

1. Shadow mode (read-only parity surfaces)
2. Parity validation (legacy vs component)
3. Dual-write (guarded and reversible)
4. Domain cutover (small slices)
5. Legacy retirement (after sustained parity)

### Feature-slice completion contract

Each feature slice is only complete when both tracks are dispositioned:

- **Track A (current runtime):** implemented / compatibility-shimmed / deferred (with rationale)
- **Track B (custom component):** implemented / compatibility-shimmed / deferred (with rationale)

### Phase map + status ledger

| Phase | Scope | Runtime Track (`packages`/`esphome`) | Component Track (`custom_components/spectra_ls`) | Status |
| --- | --- | --- | --- | --- |
| 0 | Charter + contract freeze | Documented in v-next + changelog | Documented in roadmap/spec | In Progress |
| 1 | Skeleton + shadow parity | Keep existing contracts stable | Scaffold integration + read-only parity outputs | Implemented |
| 2 | Registry + route foundation | Keep helper contracts + diagnostics parity | Target registry + adapter router (`linkplay_tcp`) | Implemented |
| 3 | Guarded dual-write | Add shims and loop guards | Controlled write path with correlation/debounce guards | Validated (Sealed 2026-04-20) |
| 4 | Functional expansion | Preserve compatibility while exposing new capabilities | Profiles/actions/capability matrix/crossfade-balance services | Validated (F4-S01/F4-S02/F4-S03 sealed; diagnostics-only authority boundary retained) |
| 5 | Domain cutover + retirement | Domain-by-domain template retirement | Primary control plane ownership + migration tooling | Validated (P5-S01/P5-S02/P5-S03/P5-S04 sealed; P6 planning handoff ready) |
| 6 | Sidebar control center productization | Runtime compatibility surfaces retained for migration-safe UX rollout | Full HA sidebar Spectra control center (setup/tuning/defaults/overrides/mapped environment) | Validated (P6-S01/P6-S02/P6-S03/P6-S04 validated) |
| 7 | Component-first authority cutover + legacy sealing | Legacy runtime transitions to compatibility/rollback baseline, then sealed from normal write ownership | Component becomes default primary control plane for net-new sidebar/beyond features | Validated (P7-S01/P7-S02/P7-S03/P7-S04 validated; phase-exit packet accepted) |
| 8 | Post-cutover stabilization + legacy-seal governance | Runtime retained as rollback-safe sealed baseline with no net-new growth | Component continues as primary feature/control plane under strict governance gates | Active (P8-S01 active) |

### Active slice ledger

| Slice | Phase | Runtime Track | Component Track | Parity | Risk | Status |
| --- | --- | --- | --- | --- | --- | --- |
| P1-S01 | 1 | Implemented (legacy source-of-truth retained) | Implemented (read-only shadow parity) | Implemented | Low | Implemented |
| P2-S01 | 2 | Implemented (legacy route contracts retained) | Implemented (registry/router scaffold; read-only) | Implemented | Low | Implemented |
| P2-S02 | 2 | Implemented (legacy route contracts retained) | Implemented (deterministic validation hardening + P2 diagnostics closure) | Implemented | Low | Implemented |
| P3-S01 | 3 | Validated (legacy write authority retained behind switch) | Validated (guard framework + manual routing write trial services) | Validated | Medium | Validated |
| P3-S02 | 3 | Validated (selection compatibility shim validation) | Validated (one-shot selection-handoff validation sequence + diagnostics) | Validated (single-capable waiver) | High | Validated |
| P3-S03 | 3 | Validated (metadata ownership explicitly deferred to legacy compatibility mode) | Validated (metadata prep diagnostics + one-shot sequence + listener-safe validation template) | Validated (diagnostics-only) | Medium | Validated |
| F4-S01 | 4 | Validated (compatibility contracts retained; no ownership cutover) | Validated (capability matrix + profile schema diagnostics scaffolding) | Validated (diagnostics-only) | Medium | Validated |
| F4-S02 | 4 | Validated (legacy action ownership retained; diagnostics-only) | Validated (programmable action-catalog safety skeleton + dry-run diagnostics) | Validated (diagnostics-only) | Medium | Validated |
| F4-S03 | 4 | Validated (legacy crossfade/balance behavior remains authoritative) | Validated (crossfade/balance diagnostics scaffold + validation sequence) | Validated (diagnostics-only) | Medium | Validated |
| P5-S01 | 5 | Validated (legacy retained as rollback authority path; post-window rollback proof captured) | Validated (routing-domain run-window execution completed with VERIFIED in-window proof) | Validated (in-window VERIFIED + post-window legacy rollback) | Medium | Validated |
| P5-S02 | 5 | Validated (legacy metadata ownership retained; bounded run-window closeout packet accepted) | Validated (metadata-domain gate-prep/readiness validation execution completed with consolidated PASS evidence) | Validated (Run-1 + Run-2 closeout packet) | Medium | Validated |
| P5-S03 | 5 | Validated (legacy lighting orchestration retained with safe post-window authority proof) | Validated (lighting-domain run-window checklist execution completed with PASS closeout evidence) | Validated (Run-1 pre/in/post packet) | Medium | Validated |
| P5-S04 | 5 | Validated (phase-exit closeout governance completed; no runtime ownership expansion) | Validated (cross-slice evidence packet accepted + Phase-6 handoff gating complete) | Validated (PASS/READY 7/7 closeout packet) | Medium | Validated |
| P6-S01 | 6 | Validated (runtime compatibility retained; no authority expansion) | Validated (HA sidebar control center foundation with read-only mapped-environment baseline proven) | Validated (PASS/READY 6/6 closeout packet) | Medium | Validated |
| P6-S02 | 6 | Validated (legacy/runtime contracts preserved; no ownership cutover) | Validated (control-center settings contract via options + service + diagnostics visibility proven) | Validated (PASS/READY 4/4 settings packet) | Medium | Validated |
| P6-S03 | 6 | Validated (runtime compatibility retained; no authority expansion) | Validated (bounded control-input execution skeleton with dry-run-first semantics proven) | Validated (execution-lane dry-run proof accepted) | Medium | Validated |
| P6-S04 | 6 | Validated (runtime compatibility retained; no ownership cutover) | Validated (execution-lane monitor/checklist closeout evidence accepted) | Validated (PASS/READY 5/5 dry-run-first packet) | Medium | Validated |
| P7-S01 | 7 | Validated (legacy rollback-safe compatibility baseline confirmed at pre-flip gate) | Validated (component-first cutover readiness gate accepted) | Validated (Run-2 PASS/READY 4/4) | High | Validated |
| P7-S02 | 7 | Validated (legacy retained as bounded rollback authority with post-window rollback-safe proof accepted) | Validated (first bounded authority-flip execution lane complete) | Completed (Run-1 pre/in/post PASS) | High | Validated |
| P7-S03 | 7 | Validated (legacy retained as rollback-safe metadata authority baseline with post-window proof accepted) | Validated (bounded metadata-domain authority-flip execution lane complete) | Completed (Run-1 pre/in PASS + Run-2 post PASS) | High | Validated |
| P7-S04 | 7 | Validated (rollback-safe legacy authority baseline preserved at closeout capture) | Validated (phase-exit closeout packet completed and accepted) | Completed (Run-1 closeout PASS/READY 4/4) | High | Validated |
| P8-S01 | 8 | Validated (legacy sealed baseline readiness gate completed with pre/in/post PASS packet) | Validated (post-cutover governance/readiness lane completed for starter gate) | Completed (Run-1/Run-2/Run-3 PASS; promoted) | High | Validated |

Latest run update (2026-05-03, Slice-H host-cutover gate enforcement + binary readiness surface):

Latest run update (2026-05-04, Slice-AY.2 Arylic HTTP per-host scheme memory):

Latest run update (2026-05-03, Slice-BF legacy codepath cleanup tracker activation):

Latest run update (2026-05-03, Slice-BG legacy active-friendly feed cleanup (LC-04)):

Latest run update (2026-05-03, Slice-BH legacy control-port feed cleanup (LC-03)):

Latest run update (2026-05-03, Slice-BI now-playing freshness fallback clock fix):

- Runtime `sensor.now_playing_freshness_age_s` now uses bounded fallback clock semantics (`media_position_updated_at` → `last_updated` → `last_changed`) instead of hard-falling to `9999` when position timestamp is missing.
- Runtime track disposition: implemented (freshness false-negative reduction for metadata readiness gates).
- Component track disposition: compatibility-shimmed (component metadata stack already applies bounded fallback semantics; equivalent mode reviewed).
- P1/P2/P3 impact check: no source-of-truth ownership change; freshness contract correctness hardening only.

Latest run update (2026-05-03, Slice-BJ LC-02 active-target read-lane cutover phase-1):

- ESP active-target read substitution now binds component surface (`sensor.spectra_ls_component_active_target`) instead of runtime helper `input_select.ma_active_target`.
- Runtime track disposition: compatibility-shimmed (helper write lane retained as temporary UI prompt compatibility shim).
- Component track disposition: implemented (component active-target contract now drives ESP read lane).
- P1/P2/P3 impact check: bounded read-path retirement only; explicit-target write service/proxy still pending for full LC-02 closure.

Latest run update (2026-05-04, Slice-BK LC-02 active-target write-lane cutover phase-2):

- Added explicit component service contract `spectra_ls.set_active_target` with authority/debounce/reentrancy-guarded helper apply semantics in `custom_components/spectra_ls` selection fabric and service wiring.
- ESP UI control-target prompt commit (`apply_control_target_selection` in `esphome/spectra_ls_system/packages/spectra-ls-ui.yaml`) now calls `spectra_ls.set_active_target` instead of direct `input_select.select_option` helper writes.
- Runtime track disposition: implemented (active ESP prompt write lane no longer writes helper directly).
- Component track disposition: implemented (explicit active-target write contract exposed and consumed).
- P1/P2/P3 impact check: source-of-truth ownership unchanged; LC-02 write-lane retirement completed under component-mediated guard semantics.

Latest run update (2026-05-04, Slice-BL LC-01 metadata-candidates read-lane cutover phase-1):

- Added component-native metadata candidate contract entities (`sensor.spectra_ls_component_meta_candidates`, `binary_sensor.spectra_ls_component_meta_low_confidence`) sourced by component diagnostics/resolver state and exposed as stable read surfaces.
- ESP substitutions for metadata candidate and confidence ingest now bind component entities (`ha_ma_meta_candidates`, `ha_ma_meta_low_confidence`) instead of legacy runtime entities.
- Runtime track disposition: compatibility-shimmed (metadata override write helpers remain in compatibility mode pending write-lane migration).
- Component track disposition: implemented (component metadata candidate/low-confidence read contracts now drive active ESP ingest lane).
- P1/P2/P3 impact check: bounded read-path retirement only; override write-lane retirement remains deferred to next LC-01 phase.

Latest run update (2026-05-04, Slice-BM LC-01 metadata override write-lane cutover phase-2):

- Added explicit component service contract `spectra_ls.set_metadata_override` with guarded apply/clear semantics (authority/reentrancy/debounce + helper/entity existence and input-shape fail-closed checks) in metadata-stack workflow + service wiring.
- ESP metadata override menu apply lane (`apply_meta_override_selection` in `esphome/spectra_ls_system/packages/spectra-ls-ui.yaml`) now calls `spectra_ls.set_metadata_override` instead of direct `input_boolean.turn_on/off` + `input_text.set_value` helper writes.
- Runtime track disposition: implemented (active ESP metadata override write lane now component-mediated; helper entities retained as compatibility storage surfaces).
- Component track disposition: implemented (explicit metadata override write contract exposed and consumed by active ESP lane).
- P1/P2/P3 impact check: no source-of-truth ownership change; LC-01 write-lane retirement completed with bounded compatibility-storage retention.

Latest run update (2026-05-04, Slice-BN ESP handoff false-`no_target` guard + lighting OLED tester semantics):

- ESP handoff status classification now treats resolved active-friendly context as a valid target-presence signal, reducing transient false `no_target` status during helper-state timing windows.
- Full-stack tester semantics now treat `lighting|oled:-` as expected while UI mode is lighting, avoiding misleading implication that blank OLED text is degraded in non-audio mode.
- Runtime track disposition: implemented (telemetry/validation semantics hardening only).
- Component track disposition: compatibility-shimmed (component contracts unchanged; equivalent failure-mode posture reviewed).
- P1/P2/P3 impact check: no source-of-truth ownership change; diagnostics and operator-triage correctness hardening only.

Latest run update (2026-05-04, Slice-BO control-host fallback ingest + lighting OLED label hardening):

- ESP control-host/port ingest now includes bounded runtime compatibility fallbacks (`sensor.ma_control_hosts`, `sensor.ma_control_host`, `sensor.ma_control_port`) that apply only when component-native control-host feeds are transiently unresolved, reducing false `no_hosts` control gating while preserving fail-closed semantics for sustained invalid feeds.
- ESP handoff readiness classification now accepts resolved cached control-host state, preventing false `no_target` posture when component shadow route is healthy but read-lane feeds are in transient churn.
- Lighting mode OLED status now emits explicit `LIGHTING` label instead of blank placeholder text for clearer operator telemetry semantics.
- Runtime track disposition: implemented (runtime ingest/status/render hardening only).
- Component track disposition: compatibility-shimmed (component contracts unchanged; equivalent failure-mode posture reviewed).
- P1/P2/P3 impact check: no source-of-truth ownership change; runtime host-gate correctness and telemetry clarity hardening only.

- Added component-native control-port contract surface (`sensor.spectra_ls_component_control_port`) and switched ESP control-port substitution consumption to this component entity.
- Runtime track disposition: compatibility-shimmed (runtime `sensor.ma_control_port` retained as rollback artifact, no longer active ESP consumer dependency).
- Component track disposition: implemented (component route/host packet now provides active control-port lane for ESP runtime).
- P1/P2/P3 impact check: bounded read-path migration completed for control-port lane; no write-path ownership changes in this slice.

- ESP active-friendly ingest (`ma_active_friendly` lane in `spectra-ls-audio-tcp.yaml`) now consumes component-native friendly surface via substitutions (`sensor.spectra_ls_component_now_playing_friendly`) instead of runtime `sensor.ma_active_friendly`.
- Runtime track disposition: compatibility-shimmed (legacy runtime friendly surface remains available but is no longer consumed in this ESP lane).
- Component track disposition: implemented (component-friendly context surface is now authoritative for this consumer path).
- P1/P2/P3 impact check: bounded legacy read-path retirement with no write-path ownership change.

- Added explicit cleanup ledger `docs/roadmap/LEGACY-CODEPATH-CLEANUP-TRACKER.md` with concrete task IDs (LC-01..LC-06), blockers, and exit criteria covering remaining ESP/runtime/component legacy dependencies.
- Runtime track disposition: compatibility-shimmed (legacy contracts intentionally retained until each task exit gate is validated).
- Component track disposition: implemented (cleanup backlog ownership + retirement gates are now explicit and auditable).
- P1/P2/P3 impact check: no immediate contract retirement; governance now enforces explicit stale-code retirement planning and proof requirements.

Latest run update (2026-05-03, Slice-BE component-native now-playing volume consumer swap):

- Component now publishes `sensor.spectra_ls_component_now_playing_volume` (derived from active now-playing entity volume attributes) and ESP volume ingest substitution now consumes this component surface.
- Runtime track disposition: compatibility-shimmed (runtime volume contract retained as fallback compatibility artifact).
- Component track disposition: implemented (component now-playing volume surface now drives active ESP volume consumer lane).
- P1/P2/P3 impact check: no immediate legacy retirement; component-owned now-playing consumer coverage expanded to include volume.

Latest run update (2026-05-03, Slice-BD component-native control-route feed swap):

- ESP control-route substitutions now consume component-native target/host feeds (`sensor.spectra_ls_component_control_targets`, `sensor.spectra_ls_component_control_hosts`, `sensor.spectra_ls_component_control_host`) for target-options and host-cache update lanes, while keeping runtime `sensor.ma_control_port` as bounded compatibility shim.
- Runtime track disposition: compatibility-shimmed (runtime route surfaces retained as rollback-safe compatibility; no ownership expansion).
- Component track disposition: implemented (component route packet surfaces now drive active ESP target/host ingest paths).
- P1/P2/P3 impact check: no immediate legacy retirement; component-owned control-route read-path coverage expanded with bounded runtime port shim retained.

Latest run update (2026-05-03, Slice-BC component-native now-playing context completion):

- Component now publishes derived now-playing context surfaces (`friendly`, `artist`, `album`, `app`, `source`) and ESP substitutions now consume these component entities for active metadata context lanes.
- Runtime track disposition: compatibility-shimmed (legacy runtime context surfaces remain available as rollback-safe compatibility contracts).
- Component track disposition: implemented (component-owned now-playing context tuple coverage expanded for ESP consumers).
- P1/P2/P3 impact check: no immediate legacy retirement; component-native now-playing read-path coverage expanded to full context tuple.

Latest run update (2026-05-03, Slice-BB component-native now-playing consumer contract swap):

- ESP now-playing consumer substitutions now prefer component-native now-playing contract entities (`sensor.spectra_ls_component_now_playing_*`, `binary_sensor.spectra_ls_component_now_playing_display_allowed`) for entity/state/title/position/duration/media-class/preview-key/freshness-age lanes while preserving legacy runtime contracts as rollback-safe compatibility surfaces.
- Runtime track disposition: compatibility-shimmed (legacy runtime now-playing contracts remain available; no write-path ownership expansion).
- Component track disposition: implemented (component-native now-playing contracts are now active ESP read-path inputs).
- P1/P2/P3 impact check: no immediate source-of-truth retirement; consumer read-path now prefers component-owned now-playing contract surfaces.

Latest run update (2026-05-04, Slice-AY.7 idle-transition poll guard + input quiet window):

- Added poll-lane guard to suppress Arylic HTTP polling during HA idle/off transition windows when Arylic is already in known-playing state, reducing transient idle-transition failure spikes.
- Extended post-input quiet guard window so HTTP polling does not immediately re-enter after dense control bursts, reducing interval blocking/hitch pressure.
- Runtime track disposition: implemented (ESP poll-loop guard hardening).
- Component track disposition: compatibility-shimmed (component path does not own ESP HTTP poll loop).
- P1/P2/P3 impact check: no source-of-truth ownership change; runtime hitch-risk reduction only.

Latest run update (2026-05-04, Slice-AY.6 timeout-budget correction):

- Root-cause correction applied to Arylic HTTP defaults: request timeout widened from an overly aggressive budget and poll/input-guard cadence tuned to tolerate normal endpoint response jitter under active playback/control.
- Objective is to reduce false `http_request Code: -1` churn without changing routing ownership, authority mode, or discovery-first host contracts.
- Runtime track disposition: implemented (ESP transport resilience correction).
- Component track disposition: compatibility-shimmed (component path does not own ESP HTTP transport loop).
- P1/P2/P3 impact check: no source-of-truth ownership change; runtime transport stability correction only.

Latest run update (2026-05-04, Slice-AY.5 hard component pin):

- Component write authority is now pinned: coordinator authority normalization/default behavior no longer accepts legacy-mode activation, and runtime authority fallback defaults to component mode.
- Component auto-select scaffold now keeps current helper target when already valid and not forced, reducing unsolicited helper target churn from transient ranking/metadata noise.
- Runtime track disposition: implemented (legacy authority lane disabled for normal operation).
- Component track disposition: implemented (authority and selection lanes pinned to component semantics).
- P1/P2/P3 impact check: active write ownership is component-only for target/host selection lanes; legacy remains dormant rollback artifact only.

Latest run update (2026-05-04, Slice-AY.4 non-hybrid authority cutover):

- Runtime `ma_control_hub` now exposes `sensor.ma_authority_mode` and authority-gates legacy target/host write lanes (`ma_update_target_options`, `ma_auto_select`, restore/lock automations), preventing dual-writer churn when component authority is active.
- Runtime manual cycle action now delegates to component service `spectra_ls.cycle_active_target` in component mode; legacy helper write path remains fallback in legacy mode.
- Runtime `sensor.ma_control_hosts` now prefers component host-cutover candidate host when host authority gate reports `authority_mode=component`, aligning ESP host feeds to component-selected authority host while retaining fail-closed fallback behavior.
- Runtime track disposition: implemented (non-hybrid target/host ownership in component mode).
- Component track disposition: implemented (existing authority/cycle/cutover-gate surfaces consumed as canonical control authority; no schema expansion required).
- P1/P2/P3 impact check: source-of-truth ownership remains migration-bounded but normal-operation target/host authority is now component-primary and non-hybrid.

- Runtime Arylic HTTP preferred transport memory now preserves bounded per-host scheme/port slots (primary + alternate), avoiding repeated default-protocol restarts during active-target host churn when hosts have different HTTP/HTTPS support.
- Runtime track disposition: implemented (active ESP runtime transport-selection stability hardening).
- Component track disposition: compatibility-shimmed (component path does not own ESP HTTP polling lane; equivalent failure-mode posture reviewed).
- P1/P2/P3 impact check: no source-of-truth ownership change; runtime transport-selection correctness hardening only.

Latest run update (2026-05-04, Slice-AY.1 Arylic HTTP interaction-priority guard + timeout tightening):

- Runtime Arylic HTTP poll loop now uses a tighter timeout budget and a short post-input poll guard window keyed from `last_input_ms`, skipping non-critical status polls immediately after user interaction to preserve tactile responsiveness under transport-fault windows.
- Runtime track disposition: implemented (active ESP runtime poll-loop responsiveness hardening).
- Component track disposition: compatibility-shimmed (component path does not own ESP HTTP polling lane; equivalent failure-mode posture reviewed).
- P1/P2/P3 impact check: no source-of-truth ownership change; runtime interaction smoothness hardening only.

Latest run update (2026-05-04, Slice-AY Arylic HTTP hitch stabilization under transport errors):

- Runtime Arylic HTTP poll loop now uses tighter timeout + stronger fail-backoff tuning (`arylic_http_timeout_ms`, `arylic_http_backoff_*`) and delays fallback-scheme switching until sustained failures, reducing perceived freeze/hitch windows during repeated transport errors.
- Runtime track disposition: implemented (active ESP runtime poll-loop stability hardening).
- Component track disposition: compatibility-shimmed (component path does not own ESP HTTP polling lane; equivalent failure-mode posture reviewed).
- P1/P2/P3 impact check: no source-of-truth ownership change; runtime transport resilience and interaction smoothness hardening only.

Latest run update (2026-05-03, Slice-AX3+AX4 freshness-age + deterministic preview-key contract):

- Added deterministic now-playing preview-change contract surface (`sensor.now_playing_preview_key`) and explicit freshness-age surface (`sensor.now_playing_freshness_age_s`) in runtime templates so ESP consumers can react to coherent content transitions instead of blank/no-op preview tokens.
- ESP now consumes freshness-age signal and suppresses stale cached metadata rescue outside bounded freshness windows while still honoring HA display policy authority.
- Runtime track disposition: implemented (active HA+ESP consumer determinism/freshness hardening).
- Component track disposition: compatibility-shimmed (component behavior unchanged; equivalent failure mode reviewed).
- P1/P2/P3 impact check: no source-of-truth ownership change; consumer-side coherence and stale-window hardening only.

Latest run update (2026-05-03, Slice-AW3 OLED metadata tuple coherency fix):

- Fixed ESP metadata contract mixing for OLED now-playing fields by aligning substitutions to a single now-playing family for title/artist/album (`sensor.now_playing_title`, `sensor.now_playing_artist`, `sensor.now_playing_album`) instead of mixed `now_playing_title` + `ma_active_*` tuple inputs.
- Removes stale cross-source album carryover where title/artist were current but album lagged from prior MA-active context.
- Runtime track disposition: implemented (active ESP runtime metadata contract alignment).
- Component track disposition: compatibility-shimmed (component behavior unchanged; equivalent failure mode reviewed).
- P1/P2/P3 impact check: no source-of-truth ownership change; metadata display coherence hardening only.

Latest run update (2026-05-03, Slice-AW2 restart cutover persistence + active-target capability recovery hardening):

- Restored component cutover continuity across HA restart windows by sourcing startup write-authority mode from persisted config-entry options (`default_write_authority_mode`) instead of fixed legacy default.
- Added bounded option persistence in authority-set path so operator-selected authority mode survives reload/restart and service flows that omit explicit mode now default to persisted authority.
- Hardened component registry fallback for active target host discovery by applying a constrained `ma_control_host` fallback when target-local discovery is temporarily unresolved, reducing false `defer_not_capable` route windows.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged; equivalent lane reviewed).
- Component track disposition: implemented (startup authority persistence + route-capability fallback hardening).
- P1/P2/P3 impact check: no source-of-truth ownership change; restart stability and route-readiness reliability hardening only.

Latest run update (2026-05-03, Slice-AS metadata prep freshness tolerance for resolved active playback):

- Hardened `custom_components/spectra_ls/metadata_stack.py` metadata-prep authority gate semantics to tolerate resolved active-playback contract surfaces when progress freshness clocks are temporarily stale, preventing false `ma_degraded_fallback` closeout blockers in contract-complete playback windows.
- In this bounded posture, freshness gate and metadata handoff readiness no longer fail-close solely due `no_fresh_play_signal` / `playing_without_recent_progress` when playback state/title/position/duration contracts remain resolved.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: implemented (authority gate false-negative path corrected).
- P1/P2/P3 impact check: no source-of-truth ownership change; authority closeout reliability hardening only.

Latest run update (2026-05-03, Slice-AR MA control-port parse guard + reconnect no-clear noise hardening):

- Hardened runtime ESP HA-feed ingestion in `esphome/spectra_ls_system/packages/spectra-ls-audio-tcp.yaml` by moving `sensor.ma_control_port` ingest to guarded text parsing so transient non-numeric states (`unknown`/`unavailable`/empty) no longer trigger numeric conversion warnings while preserving bounded default-port fallback semantics.
- Tightened reconnect-window host/hosts invalid-state handling to suppress reconnect-grace fail-closed clear noise when HA feed surfaces are transiently invalid at reconnect, while preserving fail-closed behavior outside guarded windows.
- Runtime track disposition: implemented (runtime parser/reconnect noise hardening).
- Component track disposition: compatibility-shimmed (component contracts unchanged; equivalent mode checked).
- P1/P2/P3 impact check: no source-of-truth ownership change; runtime ingest/observability hardening only.

Latest run update (2026-05-03, Slice-AQ metadata trial audit completeness contract fix):

- Corrected metadata trial preflight/status sequencing in `custom_components/spectra_ls/metadata_stack.py` so expected-meta matched trial windows continue through canonical status assignment (`dry_run_ok`/`noop_applied`) instead of falling through with no `status` field.
- Removes false partial audit payloads (`missing_audit_fields=['status']`) that previously caused deterministic `cutover_prep_incomplete` blockers despite successful bridge/trial execution.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged; equivalent audit-surface failure mode reviewed).
- Component track disposition: implemented (metadata trial audit status emission now deterministic on expected-meta matched paths).
- P1/P2/P3 impact check: no source-of-truth ownership change; metadata trial audit-contract correctness hardening only.

Latest run update (2026-05-03, Slice-AP metadata bridge expected-target stability guard):

- Hardened `custom_components/spectra_ls/metadata_stack.py` bridge execution flow to preserve validated expected-target route stability during bounded metadata cutover windows; when `expected_target` is provided and already matches current routed target under supported route decision, bridge no longer performs an unnecessary auto-select recovery write that can reselect a non-control-capable metadata source target.
- Prevents deterministic mid-window route regression (`route_linkplay_tcp` → `defer_not_capable`) that otherwise cascades into `blocked_metadata_not_ready` trial failures unrelated to authority-owner semantics.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged; equivalent route-stability failure mode reviewed).
- Component track disposition: implemented (bridge preflight target-stability guard added; recovery auto-select only runs when route preconditions are not already satisfied).
- P1/P2/P3 impact check: no source-of-truth ownership change; bounded execution-window stability hardening only.

Latest run update (2026-05-03, Slice-AO metadata bridge in-window authority proof alignment):

- Hardened `custom_components/spectra_ls/metadata_stack.py` bridge sequencing so metadata trial authority mode is selected from live post-resolver cutover state: when component metadata cutover is already active, trial runs in component mode and in-window proof remains component-owned; legacy trial mode is now only used when cutover is not active.
- Eliminates deterministic false authority-contract blockers where owner/cutover were globally active but in-window proof was captured after forced legacy trial authority switch.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged; equivalent failure mode reviewed).
- Component track disposition: implemented (metadata bridge trial-stage authority selection/proof capture corrected).
- P1/P2/P3 impact check: no source-of-truth ownership change; authority closeout proof correctness hardening only.

Latest run update (2026-05-03, Slice-AN registry capability-path alignment for WiiM host targets):

- Hardened component registry capability classification in `custom_components/spectra_ls/registry.py` so host-resolved WiiM-target entries that are transport-compatible with the supported Linkplay/TCP control path are not forced into `control_path=unknown`/`control_capable=false` under current gate consumers.
- Removes false `defer_not_capable` route posture and restores scheduler candidate eligibility for host-cutover readiness when host + supported path conditions are satisfied.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: implemented (registry route-capability inference corrected).
- P1/P2/P3 impact check: no source-of-truth ownership change; capability/path classification correctness hardening only.

Latest run update (2026-05-03, Slice-AM meta full-stack tester schema+scoring correction):

- Corrected `docs/testing/raw/meta_component_full_stack_tester.jinja` for current shadow packet schema and list-valued fields: unresolved/mismatch surfaces now read top-level packet attributes, contract/parity list checks use counts (not scalar equals), and `contract_ready` derives from valid+required-count fallback when explicit `ready` is absent.
- Capability/action/crossfade checks now auto-classify as `n/a_not_exposed` (informational note, non-blocking) when those validation lanes are not present in current shadow attributes.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: implemented (validation template consumption/score logic corrected).
- P1/P2/P3 impact check: no source-of-truth ownership change; diagnostics truthfulness and operator triage reliability hardening only.

Latest run update (2026-05-03, Slice-AL runtime reconnect fail-closed guard hardening):

- Hardened ESP runtime host-feed invalid-state handling in `esphome/spectra_ls_system/packages/spectra-ls-audio-tcp.yaml` so transient HA/API reconnect updates (`''/unknown/unavailable/none`) do not immediately clear control-host caches during reconnect grace or bounded short stale windows.
- Preserved fail-closed posture for sustained invalid feeds while reducing noisy reconnect degradation loops and false `control_host(s) cleared fail-closed` churn.
- Runtime track disposition: implemented (active ESP runtime reconnect resilience hardening).
- Component track disposition: compatibility-shimmed (equivalent failure mode reviewed; no direct component behavior mutation required).
- P1/P2/P3 impact check: no source-of-truth ownership change; reconnect resilience and observability noise hardening only.

Latest run update (2026-05-03, Slice-AK coordinator async-import hardening):

- Replaced dynamic runtime imports in `custom_components/spectra_ls/coordinator.py` initialization (`importlib.import_module`) with static class imports for coordinator workflow dependencies, eliminating Home Assistant blocking import warnings during integration load/reload.
- Hardens coordinator startup path and reduces event-loop churn risk while preserving existing contracts and behavior surfaces.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged; equivalent warning mode checked).
- Component track disposition: implemented (coordinator startup import lane hardened).
- P1/P2/P3 impact check: no source-of-truth ownership change; startup reliability/compliance hardening only.

Latest run update (2026-05-03, Slice-AJ snapshot contract regression fix):

- Fixed snapshot refresh/build crash path in `custom_components/spectra_ls/validation_fabric.py` by replacing stale references to removed coordinator-private fields (`_legacy_surfaces`, `_legacy_rooms_raw`) with canonical constant-backed legacy surface mapping.
- Restores deterministic snapshot publication for state-change, deferred refresh, and coordinator update flows that previously failed with `AttributeError` during contract validation assembly.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged; equivalent failure mode checked).
- Component track disposition: implemented (component validation regression corrected).
- P1/P2/P3 impact check: no source-of-truth ownership change; regression correction and stability hardening only.

Latest run update (2026-05-03, Slice-AI meta component full-stack Jinja tester):

- Added a consolidated raw template `docs/testing/raw/meta_component_full_stack_tester.jinja` for one-screen component-stack validation (authority/host gate, route/contract, scheduler/handoff/metadata prep, capability/action/crossfade, control-center/write-attempts, parity/freshness, and deterministic next-step guidance).
- Registered the new template in `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` quick-path list for copy/paste operator use.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: implemented (validation tooling expansion for full-stack evidence capture).
- P1/P2/P3 impact check: no source-of-truth ownership change; diagnostics/evidence workflow hardening only.

Latest run update (2026-05-03, Slice-AH Pack D reuse + cache + hardening implementation):

- parity_stamp: 2026-05-03 / Slice-AH-pack-d-reuse-cache-harden / mode=implementation
- Implemented Pack D shared reuse/caching layer by adding `payload_surface_fabric.py` helpers and rewiring snapshot/service summary consumers to shape-safe shared extractors instead of repeated inline dict/list guards.
- Added bounded micro-caching/hardening in high-frequency paths: short-TTL snapshot publish cache in `refresh_validation_fabric.py` with defensive cache lifecycle behavior, plus bounded authority-contract packet cache in `authority_contract.py` keyed by snapshot `captured_at` for repeated diagnostics/sensor reads.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: implemented (Pack D reuse/caching/hardening landed in component internals).
- P1/P2/P3 impact check: no source-of-truth ownership change; internal reuse/caching and brittleness-hardening only.

Latest run update (2026-05-03, Slice-AH Pack D reuse + cache + hardening activation):

- parity_stamp: 2026-05-03 / Slice-AH-pack-d-reuse-cache-harden / mode=docs-first
- Activated docs-first Pack D macro cycle for `custom_components/spectra_ls`: add shared payload-surface extraction utilities for repeated dict/list shape checks, introduce safe bounded micro-caching on high-frequency snapshot publish paths, and apply additional defensive hardening around cache lifecycle/state churn behavior while preserving existing behavior contracts.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: compatibility-shimmed (docs-first activation step completed; implementation/verification follows in the same macro cycle).
- P1/P2/P3 impact check: no source-of-truth ownership change; internal reuse/caching/hardening workflow activation only.

Latest run update (2026-05-03, Slice-AG Pack C optimization + reuse + hardening implementation):

- parity_stamp: 2026-05-03 / Slice-AG-pack-c-opt-reuse-harden / mode=implementation
- Implemented Pack C optimizations and reuse hardening in component paths: added reusable payload-list extraction helper in `utility_fabric.py`, converted selection target aggregation to linear-time de-duplication with set-backed uniqueness in `selection_fabric.py`, and reduced callback storm brittleness via bounded global-state coalescing cache pruning + in-flight dedupe in `event_recovery_fabric.py`.
- Applied additional common-code reuse and robustness tightening: shared helper-state/options normalization usage in `control_execution_fabric.py`, `startup_recovery_fabric.py`, and `validation_fabric.py`; reusable dict-surface extraction in `snapshot_fabric.py`; and deduped snapshot publish flow in `refresh_validation_fabric.py` to reduce repeated brittle shape/publish patterns.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: implemented (Pack C optimization/reuse/hardening landed).
- P1/P2/P3 impact check: no source-of-truth ownership change; internal performance/reuse and defensive-hardening only.

Latest run update (2026-05-03, Slice-AG Pack C optimization + reuse + hardening activation):

- parity_stamp: 2026-05-03 / Slice-AG-pack-c-opt-reuse-harden / mode=docs-first
- Activated docs-first Pack C macro cycle for `custom_components/spectra_ls`: apply performance optimizations in high-frequency selection/event paths, expand reusable helper abstractions for repeated extraction/normalization logic, and execute a defensive hardening pass to reduce brittleness/callback storm risk while preserving behavior contracts.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: compatibility-shimmed (docs-first activation step completed; implementation/rewire verification follows in the same macro cycle).
- P1/P2/P3 impact check: no source-of-truth ownership change; internal optimization/reuse/hardening workflow activation only.

Latest run update (2026-05-03, Slice-AF Pack A+B hardening implementation):

- parity_stamp: 2026-05-03 / Slice-AF-pack-a-b-hardening / mode=implementation
- Added shared write-path hardening helpers in `write_path_fabric.py` (deduped helper-options normalization, common authority/reentrancy/debounce guard evaluation, and standardized write-attempt stamping), then rewired high-churn write lanes in `selection_fabric.py` and `control_execution_fabric.py` to consume the shared helpers while preserving status/reason contracts.
- Added bounded global state-change event coalescing and in-flight dedupe in `event_recovery_fabric.py` to reduce task fan-out under rapid HA state churn.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: implemented (Pack A+B reliability/performance/dedupe hardening landed in component write and event-recovery lanes).
- P1/P2/P3 impact check: no source-of-truth ownership change; internal reliability/performance hardening only.

Latest run update (2026-05-03, Slice-AF Pack A+B hardening activation):

- parity_stamp: 2026-05-03 / Slice-AF-pack-a-b-hardening / mode=docs-first
- Activated a docs-first macro hardening cycle for `custom_components/spectra_ls` Pack A+B execution: introduce shared write-path dedupe/guard helpers (helper-state packet normalization, common guard-chain evaluation, and write-attempt recording) and rewire high-churn write lanes to consume those helpers while preserving status/reason contracts; add bounded global state-change event coalescing in event-recovery orchestration to reduce task-storm risk under rapid HA state churn.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: compatibility-shimmed (docs-first activation step completed; implementation/rewire verification follows in the same macro cycle).
- P1/P2/P3 impact check: no source-of-truth ownership change; internal reliability/performance hardening workflow activation only.

Latest run update (2026-05-03, Slice-AE coordinator endgame internals extraction implementation):

- parity_stamp: 2026-05-03 / Slice-AE-coordinator-endgame-internals / mode=implementation
- Moved remaining coordinator internals to workflow boundaries by extracting `_snapshot_for_entity` parsing semantics and write-authority normalization policy to `utility_fabric.py`, and `_async_update_data` refresh dispatch to `refresh_validation_fabric.py`.
- Rewired coordinator methods to thin delegations through utility/refresh workflow boundaries while preserving helper contracts consumed across existing orchestration paths.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: implemented (endgame internals now boundary-owned by dedicated workflow modules).
- P1/P2/P3 impact check: no source-of-truth ownership change; internal architecture hardening only.

Latest run update (2026-05-03, Slice-AE coordinator endgame internals extraction activation):

- parity_stamp: 2026-05-03 / Slice-AE-coordinator-endgame-internals / mode=docs-first
- Activated the final endgame extraction cycle to move remaining coordinator internals (`_snapshot_for_entity` field parsing semantics, write-authority mode normalization policy, and `_async_update_data` refresh path dispatch) from `coordinator.py` into workflow boundaries, then rewire coordinator methods to thin delegation wrappers.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: compatibility-shimmed (docs-first activation step completed; implementation/rewire verification follows in the same macro cycle).
- P1/P2/P3 impact check: no source-of-truth ownership change; architecture-hardening execution progression only.

Latest run update (2026-05-03, Slice-AD coordinator utility-helper final one-shot extraction implementation):

- parity_stamp: 2026-05-03 / Slice-AD-coordinator-utility-helper-final-one-shot / mode=implementation
- Added dedicated workflow boundary module `utility_fabric.py` and moved remaining coordinator utility/helper lane ownership out of `coordinator.py` (state normalization, JSON payload parsing, float-helper parsing, availability scoring, empirical bonus scoring, resolved-state checks, and timestamp age parsing).
- Rewired coordinator helper methods to thin delegations through `UtilityFabricWorkflow`, preserving helper contracts consumed across workflow boundaries.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: implemented (remaining utility/helper lane now boundary-owned by dedicated workflow module).
- P1/P2/P3 impact check: no source-of-truth ownership change; internal architecture hardening only.

Latest run update (2026-05-03, Slice-AD coordinator utility-helper final one-shot extraction activation):

- parity_stamp: 2026-05-03 / Slice-AD-coordinator-utility-helper-final-one-shot / mode=docs-first
- Activated the next super-macro extraction cycle to move the remaining coordinator utility/helper seams (state normalization, JSON payload parsing, float-helper parsing, availability scoring, empirical bonus scoring, resolved-state checks, and timestamp age parsing) from `coordinator.py` into a dedicated workflow boundary module, then rewire coordinator helper methods to thin delegation wrappers.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: compatibility-shimmed (docs-first activation step completed; implementation/rewire verification follows in the same macro cycle).
- P1/P2/P3 impact check: no source-of-truth ownership change; architecture-hardening execution progression only.

Latest run update (2026-05-03, Slice-AC coordinator refresh-validation super-chunk extraction implementation):

- parity_stamp: 2026-05-03 / Slice-AC-coordinator-refresh-validation-super-chunk / mode=implementation
- Added dedicated workflow boundary module `refresh_validation_fabric.py` and moved coordinator refresh/validation service lane ownership out of `coordinator.py` (`_refresh_snapshot`, deferred refresh callback handling, `async_rebuild_registry`, `async_validate_contracts`, `async_dump_route_trace`, `async_validate_selection_handoff`, `async_validate_capability_profile`, `async_validate_action_catalog`, `async_validate_crossfade_balance`, and `async_validate_scheduler`).
- Rewired coordinator methods to thin delegations through `RefreshValidationFabricWorkflow`, preserving service and callback contracts.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: implemented (refresh/validation super-chunk lane now boundary-owned by dedicated workflow module).
- P1/P2/P3 impact check: no source-of-truth ownership change; internal architecture hardening only.

Latest run update (2026-05-03, Slice-AC coordinator refresh-validation super-chunk extraction activation):

- parity_stamp: 2026-05-03 / Slice-AC-coordinator-refresh-validation-super-chunk / mode=docs-first
- Activated the next super-macro extraction cycle to move coordinator refresh/validation service seams (`_refresh_snapshot`, deferred refresh callback handling, `async_rebuild_registry`, `async_validate_contracts`, `async_dump_route_trace`, `async_validate_selection_handoff`, `async_validate_capability_profile`, `async_validate_action_catalog`, `async_validate_crossfade_balance`, and `async_validate_scheduler`) from `coordinator.py` into a dedicated workflow boundary module, then rewire coordinator methods to thin delegation wrappers.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: compatibility-shimmed (docs-first activation step completed; implementation/rewire verification follows in the same macro cycle).
- P1/P2/P3 impact check: no source-of-truth ownership change; architecture-hardening execution progression only.

Latest run update (2026-05-03, Slice-AB coordinator lifecycle-listener lane extraction implementation):

- parity_stamp: 2026-05-03 / Slice-AB-coordinator-lifecycle-listener-extraction / mode=implementation
- Added dedicated workflow boundary module `lifecycle_fabric.py` and moved coordinator lifecycle listener lane ownership out of `coordinator.py` (`async_setup` and `async_shutdown`).
- Rewired coordinator lifecycle methods to thin delegations through `LifecycleFabricWorkflow`, preserving listener/watch-set contracts and unload cleanup semantics.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: implemented (lifecycle listener lane now boundary-owned by dedicated workflow module).
- P1/P2/P3 impact check: no source-of-truth ownership change; internal architecture hardening only.

Latest run update (2026-05-03, Slice-AB coordinator lifecycle-listener lane extraction activation):

- parity_stamp: 2026-05-03 / Slice-AB-coordinator-lifecycle-listener-extraction / mode=docs-first
- Activated the next super-macro extraction cycle to move coordinator lifecycle listener seams (`async_setup` and `async_shutdown`) from `coordinator.py` into a dedicated workflow boundary module, then rewire coordinator methods to thin delegation wrappers.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: compatibility-shimmed (docs-first activation step completed; implementation/rewire verification follows in the same macro cycle).
- P1/P2/P3 impact check: no source-of-truth ownership change; architecture-hardening execution progression only.

Latest run update (2026-05-03, Slice-AA coordinator control-execution lane extraction implementation):

- parity_stamp: 2026-05-03 / Slice-AA-coordinator-control-execution-extraction / mode=implementation
- Added dedicated workflow boundary module `control_execution_fabric.py` and moved coordinator control-execution service lane ownership out of `coordinator.py` (`async_apply_control_center_settings`, `async_execute_control_center_input`, `async_set_write_authority`, and `async_route_write_trial`).
- Rewired coordinator methods to thin delegations through `ControlExecutionFabricWorkflow`, preserving service payload/status contracts and guarded write semantics.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: implemented (control-execution lane now boundary-owned by dedicated workflow module).
- P1/P2/P3 impact check: no source-of-truth ownership change; internal architecture hardening only.

Latest run update (2026-05-03, Slice-AA coordinator control-execution lane extraction activation):

- parity_stamp: 2026-05-03 / Slice-AA-coordinator-control-execution-extraction / mode=docs-first
- Activated the next super-macro extraction cycle to move coordinator control-execution service seams (`async_apply_control_center_settings`, `async_execute_control_center_input`, `async_set_write_authority`, and `async_route_write_trial`) from `coordinator.py` into a dedicated workflow boundary module, then rewire coordinator methods to thin delegation wrappers.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: compatibility-shimmed (docs-first activation step completed; implementation/rewire verification follows in the same macro cycle).
- P1/P2/P3 impact check: no source-of-truth ownership change; architecture-hardening execution progression only.

Latest run update (2026-05-03, Slice-Z coordinator snapshot-lane extraction implementation):

- parity_stamp: 2026-05-03 / Slice-Z-coordinator-snapshot-extraction / mode=implementation
- Added dedicated workflow boundary module `snapshot_fabric.py` and moved coordinator snapshot-assembly lane ownership out of `coordinator.py` (`build_snapshot` packet assembly and `build_write_controls` packet packaging).
- Rewired coordinator `_build_snapshot` and `_build_write_controls` methods to thin delegations through `SnapshotFabricWorkflow`, preserving coordinator-facing payload contracts.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: implemented (snapshot lane now boundary-owned by dedicated workflow module).
- P1/P2/P3 impact check: no source-of-truth ownership change; internal architecture hardening only.

Latest run update (2026-05-03, Slice-Z coordinator snapshot-lane extraction activation):

- parity_stamp: 2026-05-03 / Slice-Z-coordinator-snapshot-extraction / mode=docs-first
- Activated the next super-macro extraction cycle to move coordinator snapshot assembly seams (`_build_snapshot` packet assembly and write-controls snapshot packaging) from `coordinator.py` into a dedicated workflow boundary module, then rewire coordinator methods to thin delegation wrappers.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: compatibility-shimmed (docs-first activation step completed; implementation/rewire verification follows in the same macro cycle).
- P1/P2/P3 impact check: no source-of-truth ownership change; architecture-hardening execution progression only.

Latest run update (2026-05-03, Slice-Y startup-recovery lane extraction implementation):

- parity_stamp: 2026-05-03 / Slice-Y-startup-recovery-extraction / mode=implementation
- Added dedicated workflow boundary module `startup_recovery_fabric.py` and moved startup-recovery orchestration lane ownership out of `meta_fabric.py` (`async_schedule_startup_recovery`, timer callback dispatch, startup attempt engine, boot-readiness evaluation, and startup wait-reason formatting).
- Rewired meta-fabric methods to thin delegations through `StartupRecoveryFabricWorkflow`, preserving coordinator callback/service contracts and coordinator-facing behavior.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: implemented (startup-recovery lane now boundary-owned by dedicated workflow module).
- P1/P2/P3 impact check: no source-of-truth ownership change; internal architecture hardening only.

Latest run update (2026-05-03, Slice-Y startup-recovery lane extraction activation):

- parity_stamp: 2026-05-03 / Slice-Y-startup-recovery-extraction / mode=docs-first
- Activated the next super-macro extraction cycle to move the startup-recovery orchestration lane from `meta_fabric.py` into a dedicated workflow boundary module, then rewire meta-fabric methods to thin delegation wrappers.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: compatibility-shimmed (docs-first activation step completed; implementation/rewire verification follows in the same macro cycle).
- P1/P2/P3 impact check: no source-of-truth ownership change; architecture-hardening execution progression only.

Latest run update (2026-05-03, Slice-X event-recovery lane extraction implementation):

- parity_stamp: 2026-05-03 / Slice-X-event-recovery-extraction / mode=implementation
- Added dedicated workflow boundary module `event_recovery_fabric.py` and moved event/recovery orchestration lane ownership out of `meta_fabric.py` (auto-select loop preflight/execution, players-change refresh, ambiguity lock, stale unlock/timer handling, no-control feedback hold/self-heal/post-heal notification lifecycle, and global/state callback orchestration).
- Rewired meta-fabric methods to thin delegations through `EventRecoveryFabricWorkflow`, preserving callback/service contracts and coordinator-facing behavior.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: implemented (event/recovery lane now boundary-owned by dedicated workflow module).
- P1/P2/P3 impact check: no source-of-truth ownership change; internal architecture hardening only.

Latest run update (2026-05-03, Slice-X event-recovery lane extraction activation):

- parity_stamp: 2026-05-03 / Slice-X-event-recovery-extraction / mode=docs-first
- Activated the next super-macro extraction cycle to move the event/recovery orchestration lane from `meta_fabric.py` into a dedicated workflow boundary module, then rewire meta-fabric methods to thin delegation wrappers.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: compatibility-shimmed (docs-first activation step completed; implementation/rewire verification follows in the same macro cycle).
- P1/P2/P3 impact check: no source-of-truth ownership change; architecture-hardening execution progression only.

Latest run update (2026-05-03, Slice-W scaffold-backend lane extraction implementation):

- parity_stamp: 2026-05-03 / Slice-W-scaffold-backend-extraction / mode=implementation
- Added dedicated workflow boundary module `scaffold_fabric.py` and moved scaffold/backend assembly lane ownership out of `meta_fabric.py` (`build_component_scaffolds`, `build_handoff_inventory`, `build_ma_backend_profile`).
- Rewired meta-fabric methods to thin delegations through `ScaffoldFabricWorkflow` while preserving existing packet contracts and coordinator-facing outputs.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: implemented (scaffold/backend lane now boundary-owned by dedicated workflow module).
- P1/P2/P3 impact check: no source-of-truth ownership change; internal architecture hardening only.

Latest run update (2026-05-03, Slice-W scaffold-backend lane extraction activation):

- parity_stamp: 2026-05-03 / Slice-W-scaffold-backend-extraction / mode=docs-first
- Activated the next super-macro extraction cycle to move the scaffold/backend assembly lane from `meta_fabric.py` into a dedicated workflow boundary module, then rewire meta-fabric methods to thin delegation wrappers.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: compatibility-shimmed (docs-first activation step completed; implementation/rewire verification follows in the same macro cycle).
- P1/P2/P3 impact check: no source-of-truth ownership change; architecture-hardening execution progression only.

Latest run update (2026-05-03, Slice-V validation-control lane extraction implementation):

- parity_stamp: 2026-05-03 / Slice-V-validation-control-extraction / mode=implementation
- Extracted the remaining validation/control assembly lane from `meta_fabric.py` into a dedicated workflow boundary module `validation_fabric.py` (metadata validation bundle/policy surfaces, handoff status/dependency map, scheduler/contract/selection/route safety builders, host cutover gate, control-center validation, F4 capability/action/crossfade validations, and snapshot validation packet assembly).
- Rewired meta-fabric methods to thin delegation wrappers through `ValidationFabricWorkflow`, preserving existing packet contracts and coordinator-facing behavior.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: implemented (validation/control lane now boundary-owned by dedicated workflow module).
- P1/P2/P3 impact check: no source-of-truth ownership change; internal architecture hardening only.

Latest run update (2026-05-03, Slice-V validation-control lane extraction activation):

- parity_stamp: 2026-05-03 / Slice-V-validation-control-extraction / mode=docs-first
- Activated the next super-macro extraction cycle to move the remaining validation/control assembly lane from `meta_fabric.py` into a dedicated workflow boundary module, then rewire meta-fabric methods to thin delegation wrappers.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: compatibility-shimmed (docs-first activation step completed; implementation/rewire verification follows in the same macro cycle).
- P1/P2/P3 impact check: no source-of-truth ownership change; architecture-hardening execution progression only.

Latest run update (2026-05-03, Slice-U selection-fabric lane extraction):

- parity_stamp: 2026-05-03 / Slice-U-selection-fabric-extraction / mode=implementation
- Extracted the large scheduler/selection/write-orchestration lane out of `meta_fabric.py` into a dedicated workflow module (`selection_fabric.py`): target-options planning, scheduler decision/choice/apply, target-options scaffold, auto-select scaffold, and track/restore/cycle helpers.
- Rewired meta-fabric methods to thin delegation wrappers to the new selection-fabric boundary.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: implemented (major orchestration lane moved from meta-fabric monolith into dedicated workflow boundary).
- P1/P2/P3 impact check: no source-of-truth ownership change; internal architecture hardening only.

Latest run update (2026-05-03, Slice-T meta-fabric event-recovery orchestration extraction):

- parity_stamp: 2026-05-03 / Slice-T-meta-fabric-event-recovery / mode=implementation
- Moved the remaining coordinator event/recovery orchestration lane into meta-fabric workflow methods: auto-select loop preflight/execution, players-change refresh sequencing, ambiguity lock, stale unlock/timer handling, no-control feedback self-heal/notification lifecycle, and global/state change callback orchestration.
- Rewired coordinator callback/service surfaces to thin delegation wrappers in the same slice.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: implemented (remaining event/recovery orchestration lane now boundary-owned by meta-fabric).
- P1/P2/P3 impact check: no source-of-truth ownership change; internal architecture hardening only.

Latest run update (2026-05-03, Slice-S meta-fabric write-orchestration super-macro):

- parity_stamp: 2026-05-03 / Slice-S-meta-fabric-write-orchestration / mode=implementation
- Moved the core async write-orchestration service lane (scheduler choice/apply, target-options scaffold, auto-select scaffold, track-last-valid, restore-last-valid, cycle-target) from coordinator into meta-fabric methods.
- Rewired coordinator service methods to thin delegation wrappers in the same slice.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: implemented (major async write-orchestration lane now boundary-owned by meta-fabric).
- P1/P2/P3 impact check: no source-of-truth ownership change; internal architecture hardening only.

Latest run update (2026-05-03, Slice-R meta-fabric compute-engine macro extraction):

- parity_stamp: 2026-05-03 / Slice-R-meta-fabric-compute-engines / mode=implementation
- Moved coordinator target-options planning engine and scheduler decision/ranking engine into meta-fabric helpers.
- Rewired coordinator compute methods and downstream usage paths to delegate through meta-fabric in the same slice.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: implemented (major coordinator compute seams now boundary-owned by meta-fabric).
- P1/P2/P3 impact check: no source-of-truth ownership change; internal architecture hardening only.

Latest run update (2026-05-03, Slice-Q meta-fabric scaffolds+inventory+backend macro rewire):

- parity_stamp: 2026-05-03 / Slice-Q-meta-fabric-scaffolds-inventory-backend / mode=implementation
- Moved component-scaffold planning assembly, handoff-inventory packet assembly, and MA backend-profile assembly into meta-fabric helpers.
- Rewired coordinator methods to delegate these seams through the meta-fabric boundary in the same slice.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: implemented (coordinator orchestration surface reduced across scaffolds/inventory/backend seams).
- P1/P2/P3 impact check: no source-of-truth ownership change; internal architecture hardening only.

Latest run update (2026-05-03, Slice-P meta-fabric snapshot validation packetization):

- parity_stamp: 2026-05-03 / Slice-P-meta-fabric-snapshot-packet / mode=implementation
- Added a meta-fabric snapshot-validation packet helper that assembles host-cutover, contract/selection/route-safety, metadata validation bundle normalization, F4 capability/action/crossfade validations, scheduler validation, and control-center validation in one boundary call.
- Rewired coordinator snapshot assembly to consume the packetized validation bundle and unwrap stable diagnostic surfaces.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: implemented (snapshot validation orchestration coupling reduced through packetized boundary delegation).
- P1/P2/P3 impact check: no source-of-truth ownership change; internal architecture hardening only.

Latest run update (2026-05-03, Slice-O meta-fabric validation+gate macro rewire bundle):

- parity_stamp: 2026-05-03 / Slice-O-meta-fabric-validation-gate-rewire / mode=implementation
- Performed a macro extraction/rewire pass by moving host-cutover gate validation, control-center validation assembly, and F4 capability/action/crossfade validation builders from `coordinator.py` into `meta_fabric.py` helpers.
- Coordinator methods now delegate these validation/gate assembly surfaces through the meta-fabric boundary in the same slice.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: implemented (coordinator validation/gate assembly surface narrowed via macro boundary rewiring).
- P1/P2/P3 impact check: no source-of-truth ownership change; internal architecture hardening only.

Latest run update (2026-05-03, Slice-N meta-fabric macro rewire bundle):

- parity_stamp: 2026-05-03 / Slice-N-meta-fabric-macro-rewire / mode=implementation
- Performed macro extraction/rewire by moving coordinator contract-validation, selection-handoff validation, route-safety validation, and scheduler-validation assembly logic into meta-fabric workflow helpers.
- Coordinator methods now delegate these validation assemblies through meta-fabric boundaries in the same slice.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: implemented (coordinator orchestration surface narrowed via macro boundary rewiring).
- P1/P2/P3 impact check: no source-of-truth ownership change; internal architecture hardening only.

Latest run update (2026-05-03, Slice-M meta-fabric follow-on seam bundle):

- parity_stamp: 2026-05-03 / Slice-M-meta-fabric-follow-on-seams / mode=implementation
- Extracted follow-on metadata-adjacent coordinator seams into meta-fabric helpers for write-controls metadata surface assembly, handoff metadata-status evaluation, and snapshot metadata-bundle normalization/unpack.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: implemented (coordinator metadata assembly coupling reduced via behavior-preserving delegation).
- P1/P2/P3 impact check: no source-of-truth ownership change; internal architecture hardening only.

Latest run update (2026-05-03, Slice-L meta-fabric metadata-validation bundle delegation):

- parity_stamp: 2026-05-03 / Slice-L-meta-fabric-metadata-bundle / mode=implementation
- Added a meta-fabric metadata-validation bundle helper so metadata-prep/bridge/cutover snapshot assembly seams are delegated through `meta_fabric.py`.
- Coordinator now consumes a bundled metadata validation payload instead of stitching metadata stack bridge/cutover seams inline.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: implemented (coordinator coupling reduced for metadata-prep/bridge-facing validation assembly).
- P1/P2/P3 impact check: no source-of-truth ownership change; internal architecture hardening only.

Latest run update (2026-05-03, Slice-K meta-fabric startup-orchestration extraction):

- parity_stamp: 2026-05-03 / Slice-K-meta-fabric-startup-extract / mode=implementation
- Extracted metadata startup-recovery/boot-gate orchestration from `coordinator.py` into new workflow boundary module `meta_fabric.py` and switched coordinator to delegation wrappers for startup scheduling/timer execution and wait-reason formatting.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: implemented (metadata startup orchestration now lives behind dedicated meta-fabric module boundary).
- P1/P2/P3 impact check: no source-of-truth ownership change; internal architecture hardening only.
- README parity: no material repo-state change.

Latest run update (2026-05-03, Slice-I+J host-cutover service contract + diagnostics highlights):

- parity_stamp: 2026-05-03 / Slice-IJ-host-cutover-service-diagnostics / mode=implementation
- Added response-capable `spectra_ls.get_host_cutover_gate` service with optional fail-closed readiness/activation guards and optional `snapshot_summary` envelope for deterministic automation consumption.
- Added compact `host_cutover_gate_highlights` block to diagnostics export for one-screen readiness/activation triage.
- Runtime track disposition: compatibility-shimmed (legacy host helper/entity authority remains rollback baseline).
- Component track disposition: implemented (host-cutover gate packet is now service-addressable and diagnostics-highlighted).
- P1/P2/P3 impact check: no source-of-truth ownership change; service-level evidence/actionability and observability hardening only.

- parity_stamp: 2026-05-03 / Slice-H-host-cutover-enforcement / mode=implementation
- Added a dedicated binary diagnostic entity for host cutover readiness so operators can monitor gate readiness with a single on/off surface.
- Added fail-closed host-cutover gating in scheduler-apply write flow: when authority mode is component and host cutover gate is not ready, scheduler apply is blocked with explicit gate blocker context.
- Runtime track disposition: compatibility-shimmed (legacy host helper/entity authority remains rollback baseline).
- Component track disposition: implemented (component write-path safety now enforces host-cutover readiness before helper mutation in component-authority windows).
- P1/P2/P3 impact check: no source-of-truth ownership change; guardrail and diagnostics hardening only.

Latest run update (2026-05-03, Slice-G host-control cutover gate + authoritative host surfaces):

- parity_stamp: 2026-05-03 / Slice-G-host-control-cutover-gate / mode=implementation
- Added deterministic component-side `host_control_cutover_gate` packet in coordinator snapshot with fail-closed checks/blockers for active-target resolution, registry membership, host resolution, capability/path support, and legacy consistency drift.
- Added explicit readiness split: `ready_for_cutover` (contract/path parity readiness) vs `ready_for_authoritative_activation` (readiness + authority-mode activation gate).
- Exposed component-authoritative host candidate and cutover-gate state in diagnostics sensors (`Host Resolution Status` attributes + dedicated `Host Authority Cutover Gate` sensor).
- Runtime track disposition: compatibility-shimmed (legacy host helper/entity contracts remain rollback-safe authority baseline).
- Component track disposition: implemented (cutover-readiness and authority-candidate observability surfaces are now first-class in component snapshot/sensor contracts).
- P1/P2/P3 impact check: no source-of-truth ownership change; host-control cutover readiness determinism and observability hardening only.

Latest run update (2026-05-03, Slice-F service coercion + lifecycle dedupe hardening):

- parity_stamp: 2026-05-03 / Slice-F-service-lifecycle-coercion / mode=implementation
- Replaced brittle `bool(...)` service input coercion with explicit truthy/falsy normalization for scheduler/scaffold/trial/control-input service paths.
- Collapsed duplicated domain service register/unregister chains into shared lifecycle plumbing so setup/unload service surfaces remain lock-step as services evolve.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: implemented (input-safety + lifecycle-drift hardening only).
- P1/P2/P3 impact check: no source-of-truth ownership change; internal safety/maintainability hardening only.

- parity_stamp: 2026-05-03 / Slice-E-followup-boundary-sequence / mode=implementation
- Added a coordinator snapshot-refresh surface and switched metadata workflow refresh calls to that public coordinator hook instead of direct private snapshot rebuild calls.
- Consolidated repeated integration service stage execution loops into a shared internal sequence runner with unchanged stage-level fail-closed error reporting.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: implemented (internal maintainability + coupling-hardening only).
- P1/P2/P3 impact check: no source-of-truth ownership change; internal robustness/readability hardening only.

Latest run update (2026-05-03, Slice-E metadata-stack final extraction + service routing cleanup):

- parity_stamp: 2026-05-03 / Slice-E-metadata-stack-extract-final / mode=implementation
- Completed metadata-stack ownership transfer by moving metadata trial/resolver/bridge attempt state to `MetadataStackWorkflow` and removing remaining coordinator-owned metadata attempt-state/wrapper responsibilities.
- Updated integration service routing so metadata operations execute through `coordinator.metadata_stack` directly, keeping coordinator as orchestration-only for metadata stack flows.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: implemented (metadata stack extracted to dedicated workflow ownership with reduced coordinator coupling).
- P1/P2/P3 impact check: no source-of-truth ownership change; component architecture/contract-boundary hardening only.

Latest run update (2026-05-03, Slice-D authority-json-capture + three-slice hardening bundle):

- parity_stamp: 2026-05-03 / Slice-D-authority-next-three / mode=implementation
- Added operator copy/paste JSON capture guidance for authority packet service responses into `input_text` helpers to reduce validation friction.
- Expanded authority packet contract with deterministic readiness surfaces: `authority_contract_ready`, `authority_contract_blocking_reasons`, `authority_contract_blocker_count`, and `required_proof_checkpoints_present`.
- Hardened `spectra_ls.get_authority_contract` with additional fail-closed options: `fail_closed_if_contract_not_ready` and `required_checkpoint_count`.
- Extended diagnostics highlights to surface readiness/blocker status directly for one-glance triage.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: implemented (authority packet/service/diagnostics validation ergonomics and fail-closed signaling hardened).
- P1/P2/P3 impact check: no source-of-truth ownership change; validation/actionability hardening only.

Latest run update (2026-05-03, Slice-D authority-validator dual-input envelope support):

- parity_stamp: 2026-05-03 / Slice-D-authority-validator-dual-input / mode=implementation
- Extended the raw authority validator template to auto-accept both packet-only and service-envelope JSON (`authority_contract` + optional `snapshot_summary`) from input-text capture entities, with fallback to shadow sensor attributes.
- Added explicit source diagnostics (`source_mode`, `source_entity`, snapshot-summary presence) to make packet provenance deterministic during closeout captures.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: implemented (validator tooling now envelope-aware and lower-friction for operator validation workflows).
- P1/P2/P3 impact check: no source-of-truth ownership change; validation ergonomics hardening only.

Latest run update (2026-05-03, Slice-D authority-contract three-slice bundle):

- parity_stamp: 2026-05-03 / Slice-D-authority-three-slice / mode=implementation
- Added authority packet metadata and deterministic checklist/proof counters: `schema_version`, `packet_generated_at`, prep check counts, and proof checkpoint count for compact closeout consumption.
- Hardened `spectra_ls.get_authority_contract` service with optional strict fail-closed behavior (`fail_closed_if_unready`) and optional compact snapshot summary envelope (`include_snapshot_summary`).
- Extended diagnostics export with `authority_contract_highlights` and added raw validator template `docs/testing/raw/slice_d_authority_contract_validation.jinja` for one-screen operator packet verification.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: implemented (authority-contract packet/service/diagnostics path hardened end-to-end).
- P1/P2/P3 impact check: no source-of-truth ownership change; evidence/actionability hardening only.

Latest run update (2026-05-03, Slice-D authority-contract packet expansion):

- parity_stamp: 2026-05-03 / Slice-D-authority-packet-expand / mode=implementation
- Expanded `spectra_ls.get_authority_contract` response with deterministic cutover-prep/proof-summary fields: prep verdict/blocker count, bridge/trial status echo, proof checkpoint presence (`pre_window|in_window|post_window`), and in-window cutover/owner assertions.
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged).
- Component track disposition: implemented (authority-contract response envelope expanded additively for meta-stack automation/closeout consumption).
- P1/P2/P3 impact check: no source-of-truth ownership change; contract/actionability hardening only.

Latest run update (2026-05-03, Slice-D strict endpoint closeout packet hardening):

- parity_stamp: 2026-05-03 / Slice-D-endpoint-strict-packet / mode=implementation
- Added strict endpoint-complete closeout packet example to P5-S02 checklist with fail-closed interpretation rules.
- Expanded rolling meta-stack evidence schema with endpoint blocker count + explicit cutover checkpoint/assertion fields (`pre_window|in_window|post_window`, in-window cutover-active + owner-component assertions).
- Runtime track disposition: compatibility-shimmed (runtime contracts unchanged; docs/evidence schema hardening only).
- Component track disposition: implemented (existing endpoint/proof contract now captured in stricter closeout packet fields).
- P1/P2/P3 impact check: no source-of-truth ownership change; closeout evidence precision hardening only.

Latest run update (2026-05-03, Slice-D closeout endpoint evidence wiring):

- parity_stamp: 2026-05-03 / Slice-D-closeout-evidence / mode=implementation
- Active P5 monitor/checklist artifacts now consume explicit endpoint gate fields: `cutover_prep_validation.cutover_prep_complete`, endpoint blocker count, and `cutover_proof` checkpoint presence (`pre_window|in_window|post_window`).
- Rolling meta-stack evidence template now includes endpoint completion/blocker fields for deterministic closeout packets.
- Runtime track disposition: compatibility-shimmed (runtime behavior/contracts unchanged; evidence surfaces only).
- Component track disposition: implemented (existing endpoint/proof contract is now wired into operator closeout artifacts).
- P1/P2/P3 impact check: no source-of-truth ownership change; closeout evidence determinism hardening only.

Latest run update (2026-05-03, Slice-D metadata bridge cutover proof packet + endpoint gate):

- parity_stamp: 2026-05-03 / Slice-D-meta-bridge-proof / mode=implementation
- Metadata bridge result payload now emits deterministic cutover proof checkpoints: `cutover_proof.pre_window`, `cutover_proof.in_window`, and `cutover_proof.post_window`.
- Each checkpoint includes authority mode, metadata owner, cutover-active state, readiness, and cutover-block reason for direct pre/in/post validation.
- Snapshot now emits explicit cutover-prep endpoint gate `cutover_prep_validation.cutover_prep_complete` with deterministic checklist + blocker reasons.
- Authority contract packet/service now includes `cutover_prep_complete` for one-glance cutover-prep readiness status.
- Runtime track disposition: compatibility-shimmed (legacy metadata contracts remain rollback baseline).
- Component track disposition: implemented (bridge evidence packet hardening + explicit endpoint readiness gate).
- P1/P2/P3 impact check: source-of-truth ownership remains migration-bounded; validation evidence quality improved without ownership overreach.

Latest run update (2026-05-03, Slice-D metadata authority-satisfied trial contract):

- parity_stamp: 2026-05-03 / Slice-D-meta-authority-trial / mode=implementation
- Metadata trial authority checks now pass when either legacy authority is active or component metadata cutover is active (`metadata_cutover_active=true`).
- Metadata trial payload/closeout now records metadata owner + cutover state for deterministic cutover evidence.
- Authority contract packet/service now includes `metadata_authority_owner` + `metadata_cutover_active`.
- Runtime track disposition: compatibility-shimmed (legacy metadata contracts preserved as rollback baseline).
- Component track disposition: implemented (authority-satisfied trial gating + packet visibility).
- P1/P2/P3 impact check: source-of-truth ownership remains migration-bounded; cutover readiness is now explicitly contract-driven.

Latest run update (2026-05-02, Slice-D metadata authority rewrite kickoff):

- parity_stamp: 2026-05-02 / Slice-D-meta-authority-kickoff / mode=implementation
- Replaced hardcoded legacy-only metadata authority owner/cutover diagnostics with component-aware authority resolution (mode + resolver-cutover readiness).
- Bridge validation now treats component metadata cutover as a valid authority posture and only requires legacy trial-stage checks when cutover is not active.
- Runtime track disposition: compatibility-shimmed (legacy runtime metadata contracts preserved as rollback baseline).
- Component track disposition: implemented (metadata authority diagnostics now support component-first cutover posture).
- P1/P2/P3 impact check: source-of-truth ownership remains migration-bounded; metadata authority diagnostics no longer permanently pinned to legacy.

Latest run update (2026-05-02, Slice-D sub-slice 36: lean v2.7 test-scope signal):

- parity_stamp: 2026-05-02 / Slice-D-36 / mode=lean_team / batch=9
- Added explicit test-scope line (`full|targeted|minimal`) for compact verification-breadth signaling.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; verification-breadth visibility hardening only.

Latest run update (2026-05-02, Slice-D sub-slice 37: lean v2.7 contract-delta signal):

- parity_stamp: 2026-05-02 / Slice-D-37 / mode=lean_team / batch=9
- Added explicit contract-delta line (`none|minor|major`) for compact contract-impact visibility.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; contract-impact signaling hardening only.

Latest run update (2026-05-02, Slice-D sub-slice 38: lean v2.7 communication-note signal):

- parity_stamp: 2026-05-02 / Slice-D-38 / mode=lean_team / batch=9
- Added communication-note reference line (`N/A` if none) for operational follow-through traceability.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; communication traceability hardening only.

Latest run update (2026-05-02, Slice-D sub-slice 33: lean v2.6 validation-confidence signal):

- parity_stamp: 2026-05-02 / Slice-D-33 / mode=lean_team / batch=8
- Added explicit validation-confidence line (`high|medium|low`) for fast uncertainty calibration in lean reviews.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; validation-confidence signaling hardening only.

Latest run update (2026-05-02, Slice-D sub-slice 34: lean v2.6 rollback-posture signal):

- parity_stamp: 2026-05-02 / Slice-D-34 / mode=lean_team / batch=8
- Added explicit rollback-posture line (`safe|needs-attention`) for compact reversibility triage.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; rollback-readiness visibility hardening only.

Latest run update (2026-05-02, Slice-D sub-slice 35: lean v2.6 handoff-note signal):

- parity_stamp: 2026-05-02 / Slice-D-35 / mode=lean_team / batch=8
- Added handoff-note reference line (`N/A` if none) for reviewer/operator continuity traceability.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; operational continuity signaling hardening only.

Latest run update (2026-05-02, Slice-D sub-slice 30: lean v2.5 change-risk signal):

- parity_stamp: 2026-05-02 / Slice-D-30 / mode=lean_team / batch=7
- Added explicit change-risk line (`low|medium|high`) for reviewer depth triage without checklist expansion.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; review-depth triage clarity hardening only.

Latest run update (2026-05-02, Slice-D sub-slice 31: lean v2.5 follow-up need signal):

- parity_stamp: 2026-05-02 / Slice-D-31 / mode=lean_team / batch=7
- Added explicit follow-up needed signal (`yes|no`) to separate merge-readiness from post-merge action planning.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; post-merge planning visibility hardening only.

Latest run update (2026-05-02, Slice-D sub-slice 32: lean v2.5 follow-up reference signal):

- parity_stamp: 2026-05-02 / Slice-D-32 / mode=lean_team / batch=7
- Added follow-up tracking reference line (`N/A` if none) for durable linkage of declared follow-up work.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; follow-up traceability hardening only.

Latest run update (2026-05-02, Slice-D sub-slice 27: lean v2.4 core coherence signal):

- parity_stamp: 2026-05-02 / Slice-D-27 / mode=lean_team / batch=6
- Added explicit core-packet coherence line (`coherent|needs-fix`) for low-overhead packet consistency signaling.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; packet consistency clarity hardening only.

Latest run update (2026-05-02, Slice-D sub-slice 28: lean v2.4 evidence artifact reference):

- parity_stamp: 2026-05-02 / Slice-D-28 / mode=lean_team / batch=6
- Added explicit evidence artifact reference line (URL/path or `N/A`) for faster reviewer proof lookup.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; evidence location clarity hardening only.

Latest run update (2026-05-02, Slice-D sub-slice 29: lean v2.4 blocker summary signal):

- parity_stamp: 2026-05-02 / Slice-D-29 / mode=lean_team / batch=6
- Added one-line blocker reason summary (`N/A` when ready) for compact blocked-state interpretation.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; blocker triage clarity hardening only.

Latest run update (2026-05-02, Slice-D sub-slice 24: lean v2.3 blocker verdict signal):

- parity_stamp: 2026-05-02 / Slice-D-24 / mode=lean_team / batch=5
- Added explicit blocker verdict line (`ready|blocked`) for faster merge-readiness interpretation.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; blocker clarity hardening only.

Latest run update (2026-05-02, Slice-D sub-slice 25: lean v2.3 optional-section completion summary):

- parity_stamp: 2026-05-02 / Slice-D-25 / mode=lean_team / batch=5
- Added optional-section completion summary (`A done`, `B done`, `A+B done`, or `none`) for one-line closure checks.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; closure scan-speed hardening only.

Latest run update (2026-05-02, Slice-D sub-slice 26: lean v2.3 reviewer timestamp signal):

- parity_stamp: 2026-05-02 / Slice-D-26 / mode=lean_team / batch=5
- Added reviewer attestation timestamp field (`UTC`) for compact recency proof in fast-path review.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; attestation recency hardening only.

Latest run update (2026-05-02, Slice-D sub-slice 21: lean v2.2 core owner signal):

- parity_stamp: 2026-05-02 / Slice-D-21 / mode=lean_team / batch=4
- Added explicit core-packet owner field for reviewer accountability and packet closure ownership clarity.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; accountability signal hardening only.

Latest run update (2026-05-02, Slice-D sub-slice 22: lean v2.2 scope summary line):

- parity_stamp: 2026-05-02 / Slice-D-22 / mode=lean_team / batch=4
- Added compact scope summary line (`A`, `B`, `A+B`, or `none`) for one-glance optional-section expectations.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; reviewer scan-speed hardening only.

Latest run update (2026-05-02, Slice-D sub-slice 23: lean v2.2 evidence freshness hint):

- parity_stamp: 2026-05-02 / Slice-D-23 / mode=lean_team / batch=4
- Added evidence freshness hint (`fresh|stale`) alongside UTC timestamp for fast recency interpretation.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; evidence-recency interpretation hardening only.

Latest run update (2026-05-02, Slice-D sub-slice 18: lean v2.1 core packet status line):

- parity_stamp: 2026-05-02 / Slice-D-18 / mode=lean_team / batch=3
- Added explicit core packet status field (`complete|incomplete`) for faster reviewer triage in lean flow.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; review-signal clarity hardening only.

Latest run update (2026-05-02, Slice-D sub-slice 19: lean v2.1 compact scope toggles):

- parity_stamp: 2026-05-02 / Slice-D-19 / mode=lean_team / batch=3
- Added compact `yes|no` scope-toggle lines before optional sections to reduce disposition overhead.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; optional-section decision speed hardening only.

Latest run update (2026-05-02, Slice-D sub-slice 20: lean v2.1 evidence timestamp signal):

- parity_stamp: 2026-05-02 / Slice-D-20 / mode=lean_team / batch=3
- Added explicit minimal-evidence timestamp field (`UTC`) plus reviewer fast-path timestamp check.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; evidence-recency confidence hardening only.

Latest run update (2026-05-02, Slice-D sub-slice 15: lean v2 one-screen core packet):

- parity_stamp: 2026-05-02 / Slice-D-15 / mode=lean_team / batch=2
- Compressed PR workflow to one-screen must-fill core packet while preserving blocker-critical declaration and evidence fields.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; PR fill-time reduction only.

Latest run update (2026-05-02, Slice-D sub-slice 16: optional blocks default-N/A):

- parity_stamp: 2026-05-02 / Slice-D-16 / mode=lean_team / batch=2
- Optional sections now default to explicit `N/A (not in scope)` unless triggered, reducing unnecessary text churn.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; optional-section friction reduction only.

Latest run update (2026-05-02, Slice-D sub-slice 17: reviewer fast-path attestation):

- parity_stamp: 2026-05-02 / Slice-D-17 / mode=lean_team / batch=2
- Added minimal reviewer fast-path attestation that preserves merge-blocking evidence checks.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; review-loop speedup only.

Latest run update (2026-05-02, Slice-D sub-slice 10: lean template trim):

- parity_stamp: 2026-05-02 / Slice-D-10 / mode=lean_team / batch=1
- Collapsed PR checklist into compact core gate + optional scope-triggered sections.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; checklist overhead reduction only.

Latest run update (2026-05-02, Slice-D sub-slice 11: scope trigger matrix):

- parity_stamp: 2026-05-02 / Slice-D-11 / mode=lean_team / batch=1
- Added explicit trigger matrix so non-applicable sections can be safely skipped.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; scope clarity hardening only.

Latest run update (2026-05-02, Slice-D sub-slice 12: quick-fill evidence snippets):

- parity_stamp: 2026-05-02 / Slice-D-12 / mode=lean_team / batch=1
- Added quick-fill snippet blocks for CI/manual evidence packets.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; packet fill-time reduction only.

Latest run update (2026-05-02, Slice-D sub-slice 13: lean parity-stamp format):

- parity_stamp: 2026-05-02 / Slice-D-13 / mode=lean_team / batch=1
- Standardized concise parity-stamp wording for lean roadmap/notes updates.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; docs-ledger overhead reduction only.

Latest run update (2026-05-02, Slice-D sub-slice 14: two-person fast-start):

- parity_stamp: 2026-05-02 / Slice-D-14 / mode=lean_team / batch=1
- Added 60-second contributor fast-start path for compliant lean PR opening.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; onboarding speedup only.

Latest run update (2026-05-02, Slice-D sub-slice 6: lean-team mode activation):

- Activated explicit `lean_team` execution posture for current two-person workflow.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; process throughput hardening only.

Latest run update (2026-05-02, Slice-D sub-slice 7: core-gate minimum packet):

- Defined minimum always-required merge packet for `lean_team` mode and made extended governance checks conditional by scope.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; cycle-time reduction hardening only.

Latest run update (2026-05-02, Slice-D sub-slice 8: docs-parity batching policy):

- Allowed bounded parity batching (up to 4 micro-slices) in lean mode while preserving immediate changelog-first discipline.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; documentation effort smoothing only.

Latest run update (2026-05-02, Slice-D sub-slice 9: masterwork target non-blocking during lean execution):

- Reframed masterwork baseline as strategic target-state while keeping blocker-critical safety controls strict.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; strategic-vs-operational clarity hardening only.

Latest run update (2026-05-02, Slice-D sub-slice 5: manual-waiver tracking reference contract):

- Added required manual-waiver tracking reference field for `manual_enforced_now` declaration-gate packets.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; exception traceability hardening only.

Latest run update (2026-05-02, Slice-D sub-slice 4: manual-to-CI cutover target contract):

- Added required target-date capture for transitioning `manual_enforced_now` declaration gates to `ci_enforced`.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; enforcement transition planning hardening only.

Latest run update (2026-05-02, Slice-D sub-slice 3: CI verdict contract):

- Added explicit CI verdict capture (`pass|fail|not_run`) for `ci_enforced` gate mode.
- Added required failure-reason evidence when CI verdict is `fail`.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; CI decision traceability hardening only.

Latest run update (2026-05-02, Slice-D sub-slice 2: manual-gate waiver expiry contract):

- Added waiver owner + expiry evidence fields for `manual_enforced_now` exception posture in PR governance packet.
- Established explicit no-indefinite-waiver merge policy in reviewer governance language.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; manual-enforcement accountability hardening only.

Latest run update (2026-05-02, Slice-D sub-slice 1: CI evidence contract):

- Added PR-level CI evidence fields for `ci_enforced` declaration gate mode (workflow/job name + run URL evidence).
- Added merge-readiness expectation that missing CI evidence blocks `ci_enforced` posture closure.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; enforcement evidence traceability hardening only.

Latest run update (2026-05-02, Slice-D kickoff: declaration gate mode contract):

- Introduced explicit declaration gate mode capture in PR workflow (`manual_enforced_now` vs `ci_enforced`) to operationalize transition from reviewer-only enforcement to CI-backed enforcement.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; governance operationalization readiness hardening only.

Latest run update (2026-05-02, Slice-C declaration-vs-diff merge-blocker hardening):

- Explicitly marked declaration-vs-diff mismatch as merge-blocking when intake declares `component_only_declared` but PR diff includes runtime files.
- Added requirement that bounded exception rationale + tracking reference must be complete to clear this blocker.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; merge-readiness decision clarity hardening only.

Latest run update (2026-05-02, Slice-C component-only declaration enforcement):

- Added intake runtime-touch declaration fields (`component_only_declared` vs `bounded_legacy_exception_expected`) to make scope intent explicit before implementation.
- Added PR reconciliation requirement comparing declared runtime-touch posture against actual changed-file scope, with mandatory rationale when mismatched.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; intake-to-review scope-auditability hardening only.

Latest run update (2026-05-02, Slice-C component-target file evidence):

- Added planned component target-file evidence fields to intake/PR workflow so component-first intent is file-level auditable before merge.
- Added PR-side reconciliation fields comparing planned component files vs actual changed files, with divergence rationale requirement.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; execution-scoping auditability hardening only.

Latest run update (2026-05-02, Slice-C component-first merge-blocker enforcement):

- Upgraded component-first governance from guidance to explicit merge-blocker semantics when reconciliation/legacy-exception evidence is missing.
- Added intake/PR evidence fields for legacy-exception tracking reference (`N/A` allowed only when not applicable).
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; reviewer gate auditability hardening only.

Latest run update (2026-05-02, Slice-C component-first execution gate):

- Added component-first execution gating to issue/PR workflow surfaces so net-new behavior/contract work defaults to `custom_components/spectra_ls`.
- Runtime/legacy path touches are now documented as bounded exceptions requiring rationale and reviewer acknowledgment.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; execution routing hardening to reduce legacy touch churn.

Latest run update (2026-05-02, Slice-C reconciliation evidence + reviewer attestation):

- Added explicit reviewer-attestation expectation to scheduler/metadata-bridge PR reconciliation flow so maintainers verify issue-baseline lane/owner mapping evidence before merge-readiness claims.
- Added issue-template config routing pointer to PR reconciliation requirements so contributors encounter evidence expectations at intake entry.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; reconciliation auditability hardening only.

Latest run update (2026-05-02, Slice-C issue↔PR reconciliation governance closure):

- Propagated mandatory issue↔PR lane/owner reconciliation wording into contributor and governance workflow docs (beyond templates) to remove ambiguity in review expectations.
- Standardized required reconciliation packet: linked issue IDs, issue intake lane/owner, PR lane/owner, and mandatory mismatch rationale (`N/A` only for no mismatch).
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; governance-enforcement clarity hardening only.

Latest run update (2026-05-02, Slice-C issue↔PR lane-reclassification rationale enforcement):

- Tightened bug/feature intake wording so scheduler/metadata-bridge lane and canonical owner entries are explicit intake baseline contracts for downstream PR reconciliation.
- Updated PR checklist flow to require explicit issue↔PR lane/owner reconciliation capture and mandatory reclassification rationale when mismatch exists.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; issue-to-PR enforcement consistency hardening only.

Latest run update (2026-05-02, Slice-C wiki intake + workflow parity):

- Updated wiki operator/contributor workflow surfaces so scheduler/metadata-bridge issue intake mirrors PR integrity expectations end-to-end.
- Added explicit lane/owner-file capture guidance and parity-anchor expectation references in bug-workflow and contributing pages.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; wiki/operator workflow parity hardening only.

Latest run update (2026-05-02, Slice-C issue-intake integrity wiring):

- Extended Slice-C enforcement into issue intake forms so scheduler/metadata-bridge proposals are lane-classified and owner-routed before implementation starts.
- Updated issue template routing/config to direct contributors toward intake requirements and contributor workflow references.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; intake-stage governance enforcement hardening only.

Latest run update (2026-05-02, Slice-C governance propagation pack):

- Propagated Slice-C scheduler/metadata-bridge enforcement from reference notes into contributor and governance workflow surfaces (`CONTRIBUTING.md`, `.github/copilot-instructions.md`, `docs/governance/GITHUB-MASTERWORK-BLUEPRINT.md`).
- Enforcement visibility now spans intake, execution instructions, and PR-quality governance criteria.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; governance-consistency hardening only.

Latest run update (2026-05-02, Slice-C PR workflow wiring):

- Wired Slice-C scheduler/metadata-bridge enforcement into `.github/pull_request_template.md` so lane ownership checks are captured in PR review flow, not only in reference notes.
- Added required checks for lane classification, canonical owner confirmation, no-owner-bypass posture, parity-anchor disposition, and paired-review parity checks.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; workflow enforcement hardening only.

Latest run update (2026-05-02, Slice-C enforcement micro-checklist activation):

- Extended Slice C from owner-matrix publication to execution enforcement by adding a compact scheduler/metadata-bridge preflight + PR checklist in `docs/notes/NOTES-engineering-rigor.md`.
- Checklist now requires owner routing confirmation, paired-review confirmation, parity-anchor status, and explicit two-track disposition before closure.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; enforcement discipline hardening only.

Latest run update (2026-05-02, Slice-C owner quick-reference matrix kickoff):

- Started Slice C by adding a compact scheduler/metadata-bridge owner quick-reference matrix in `docs/notes/NOTES-engineering-rigor.md` to accelerate correct file routing during behavior-visible write-path changes.
- Matrix now exposes lane-specific `edit here` owner files, `do not fork` boundaries, and required paired-review files.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; anti-mispatch clarity and execution-speed hardening only.

Latest run update (2026-05-02, Slice-B scheduler + metadata bridge ownership integrity map):

- Extended Slice-A fabric ownership guardrails with a compact service/write-path integrity map for the scheduler and metadata bridge lanes in `docs/notes/NOTES-engineering-rigor.md`.
- Captured canonical owner files, allowed mutation boundaries, lane-specific anti-mispatch preflight checks, and no-go conditions for behavior-visible scheduler/bridge changes.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; write-lane boundary integrity and execution-discipline hardening only.

Latest run update (2026-05-02, Slice-A fabric ownership integrity capture):

- Activated explicit data-fabric file ownership integrity guardrails in engineering-rigor notes with canonical owner map (builder/coordinator/projection/service/constants/docs) and anti-mispatch pre-edit checks.
- Added required parity anchors (`packages/ma_control_hub/template.inc` and `custom_components/spectra_ls/registry.py`) for behavior-visible fabric slices with explicit disposition tracking.
- Runtime track disposition: compatibility-shimmed (governance/docs-only).
- Component track disposition: compatibility-shimmed (governance/docs-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; patch-boundary integrity and execution-discipline hardening only.

Plan Delta (2026-05-02, component-first canonical playback data-fabric direction):

- Scope-discipline update: active file-level no-miss ledger is now tracked in `docs/notes/NOTES-engineering-rigor.md` under `Active scoped execution ledger (file-level, no-miss contract)` and must be updated in-slice whenever authority/naming contracts are touched in code.

- Architecture governance contract now explicitly codified in `docs/architecture/COMPONENT-DATA-FABRIC-ARCHITECTURE.md` between core design goals and canonical model, with token-locked MA authority semantics: `health.authority_mode` = `ma_primary | ma_degraded_fallback`; degraded reasons include `ma_degraded_fallback_active`, `ma_payload_stale`, `ma_payload_shape_invalid`, and `ma_api_unreachable`.

- Direction adjustment: robust playback/progress ownership is now explicitly targeted as a component-first canonical data-fabric program, not continued legacy-inline fallback expansion.
- Canonical architecture spec published: `docs/architecture/COMPONENT-DATA-FABRIC-ARCHITECTURE.md`.
- Next execution slices queued:
  - `CDF-S01` canonical model + adapters,
  - `CDF-S02` field resolver with confidence/provenance,
  - `CDF-S03` compatibility projection bridge,
  - `CDF-S04` cutover gate + rollback-safe closeout.
- Runtime track disposition: compatibility-shimmed (ownership unchanged in this plan-delta slice).
- Component track disposition: implemented (architecture/system-design target published; execution slices staged).
- P1/P2/P3 impact check: no source-of-truth ownership change in this slice; structured anti-collapse cutover design established.

- Runtime progress contracts now use MA-authoritative multi-source augmentation for duration continuity: active/now-playing duration resolution includes robust MA payload chain plus MA-managed peer-entity fallback by track identity (title/artist) when selected render entities expose position but no duration.
- Component metadata-prep diagnostics now explicitly gate active-playback progress readiness with `playing_with_missing_duration_contract`, making “playing + position + duration=0” a first-class blocker for cutover-readiness analysis.
- Runtime track disposition: implemented (progress contract resilience hardening).
- Component track disposition: implemented (diagnostics parity for progress-contract failures).
- P1/P2/P3 impact check: no source-of-truth ownership change; systemic progress-contract correctness hardening only.

- Updated top navigation and high-traffic onboarding pages with explicit journey routing (install, deploy verification, bug intake, contributor flow).
- Added symptom-first runbook routing and stronger bug pre-intake sanity checks to reduce avoidable issue churn.
- Runtime track disposition: compatibility-shimmed (documentation-only).
- Component track disposition: compatibility-shimmed (documentation-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; onboarding and operator workflow clarity hardening only.

Latest run update (2026-04-29, docs parity sweep):

- Completed README-through-wiki documentation currency pass and synchronized deployment/release guidance with current runtime facts.
- Added explicit deploy guidance for ESPHome 2026.4.x OTA platform schema and release-tag-based HACS publication cadence.
- Runtime track disposition: compatibility-shimmed (documentation-only).
- Component track disposition: compatibility-shimmed (documentation-only).
- P1/P2/P3 impact check: no source-of-truth ownership change; documentation parity hardening only.

Latest run update (2026-04-28, MA metadata-provider refresh dispatch):

- Runtime now-playing display policy is refined to explicit Music-Lite semantics: non-music preview window increased to 30s, preview visibility re-arms on fresh preview-key changes, and non-music preview is gated behind an active-music guard (other music playing/paused blocks TV/non-music preview while music remains always display-eligible).
- Runtime track disposition: implemented (active template display-policy contract updated).
- Component track disposition: implemented (metadata-prep diagnostics now validate runtime media contract surfaces and surface drift on `media_class`/`preview_key`/`display_allowed`/`music_guard_active` semantics).
- P1/P2/P3 impact check: no source-of-truth ownership change; deterministic display-policy correctness hardening only.

- Runtime track now includes explicit MA metadata-provider refresh dispatch via `script.ma_send_metadata_to_providers` (`metadata/update_metadata`) using resolved now-playing MA URI and existing MA API transport wrapper.
- Runtime track now persists refresh API response telemetry (status/response/item/reason/updated-at) to helper-backed surfaces for deterministic validation evidence.
- Runtime telemetry now also persists compact provider-result summary (`input_text.ma_metadata_provider_last_providers`) so templates can display provider-level outcomes directly.
- Provider-summary extraction now tolerates mapping and list-shaped response payloads and persists bounded compact output for helper-length safety.
- Provider-refresh trigger inputs are explicitly boolean-normalized (including string/number payloads) before dispatch to prevent false-positive refresh execution.
- Registry target classification now fail-closes unsupported host families by deriving `control_path`/`control_capable` from supported path mappings instead of host presence alone.
- Runtime URI eligibility is hardened with MA active-player fallback (`player_json.current_media.uri`) before `media_content_id` fallback to reduce false invalid-URI dispatch skips.
- Component track `spectra_ls.validate_metadata_policy` now optionally triggers that runtime refresh script after policy diagnostics refresh, with guarded compatibility behavior when the runtime script surface is unavailable.
- Runtime track disposition: implemented (explicit provider-refresh action path).
- Component track disposition: implemented (service-level parity trigger + compatibility shim fallback).
- P1/P2/P3 impact check: no source-of-truth ownership change; metadata-provider refresh actionability hardening only.

- Selection lifecycle parity migration advanced with component-side lock lifecycle behavior now mirrored for migration windows:
  - lock-on-ambiguous-select parity handling,
  - stale-meta unlock parity handling (5s hold semantics),
  - component auto-select loop parity triggers on legacy-equivalent state transitions.
- Runtime track disposition: compatibility-shimmed (legacy automations remain rollback baseline).
- Component track disposition: implemented (guarded parity lifecycle behavior in coordinator).
- P1/P2/P3 impact check: no source-of-truth ownership flip; bounded selection-domain migration behavior only.

Latest run update (2026-04-26, parity correctness/cleanup follow-up):

- Closed `GAP-20260426-auto-select-loop-watched-options-filter` by aligning component global watcher semantics to legacy watched-options membership behavior.
- Removed unnecessary `media_player.*` watcher filter in component global state-change handling (useless restriction removed; existing guardrails still enforce safe execution).
- Runtime track disposition: implemented (legacy baseline unchanged).
- Component track disposition: implemented (gap closure + behavior cleanup).

Latest run update (2026-04-26, no-control feedback lifecycle parity):

- Closed parity gap for legacy `ma_feedback_no_control_capable_hosts` lifecycle in component migration windows.
- Component now mirrors bounded lifecycle semantics under component authority: 30s degrade hold, one-shot self-heal (component target-options + auto-select scaffolds), post-heal 10s persistence check, and persistent notification create/dismiss (`spectra_ls_no_control_capable_hosts`).
- Runtime track disposition: compatibility-shimmed (legacy automation retained as rollback baseline).
- Component track disposition: implemented (feedback lifecycle parity + guarded adaptation).
- P1/P2/P3 impact check: no source-of-truth ownership flip; bounded parity and operator feedback resilience hardening only.

Latest run update (2026-04-26, MA-players options-refresh parity):

- Closed parity gap where legacy MA-player-change lifecycle refreshed options before auto-select while component listener previously ran auto-select-only.
- Component now runs additive players-change sequencing in component-authority windows: target-options scaffold refresh first, then guarded auto-select loop.
- Candidate synthesis was extended additively (no rewrite) with capability-aware registry/profile feeds (`control_capable`, host resolved, supported control path, availability quality).
- Runtime track disposition: compatibility-shimmed (legacy automation retained as rollback baseline).
- Component track disposition: implemented (players-change sequencing parity + additive capability-aware candidate feed).
- P1/P2/P3 impact check: no source-of-truth ownership change; bounded parity and options freshness hardening only.

Latest run update (2026-04-26, legacy handoff-latency optimization):

- Runtime handoff cadence hardened for legacy-authority operation by adding event-driven target-options/auto-select refresh triggers on detected-receiver and now-playing-entity changes, reducing dependence on `/5` periodic refresh windows.
- ESP-side active-target change handling now performs an optimistic host-refresh push (`update_entity` for `sensor.ma_control_targets`, `sensor.ma_control_hosts`, and `sensor.ma_control_host`) so control-host convergence reaches ESP immediately after helper target shifts.
- Runtime track disposition: implemented (handoff latency reduction).
- Component track disposition: compatibility-shimmed (no component ownership/contract change in this slice).
- P1/P2/P3 impact check: no source-of-truth ownership change; runtime handoff responsiveness hardening only.

Latest run update (2026-04-27, component parity + ESP handoff telemetry):

Latest run update (2026-04-27, ghost-broadcaster healing + policy diagnostics):

- Runtime metadata winner logic now treats stale-progress `playing` entities as non-fresh when a progress clock is present (fail-closed), with explicit dual-threshold policy windows: `input_number.ma_meta_stale_s` for `playing` freshness and `input_number.ma_meta_paused_hide_s` for paused hold/hide behavior.
- Component metadata prep now mirrors the same stale-playing suppression semantics and exposes canonical policy + suppression reason diagnostics for operator triage.
- Runtime track disposition: implemented (freshness gate hardening for stale-playing broadcaster cases).
- Component track disposition: implemented (matching suppression semantics + policy diagnostics surface).
- P1/P2/P3 impact check: no source-of-truth ownership change; parity/decision-correctness hardening only.

Latest run update (2026-04-27, stale-window decoupling parity hardening):

- Completed parity-safe stale-window decoupling across runtime + component + validation templates so `playing` freshness no longer inherits the longer paused-hide window.
- Runtime track disposition: implemented (active-meta/now-playing winner gates now apply `ma_meta_stale_s` for `playing` freshness and `ma_meta_paused_hide_s` for paused hold/hide).
- Component track disposition: implemented (`_build_now_playing_signal` + metadata-prep diagnostics now expose/use dual thresholds with explicit recent-play vs recent-paused signals).
- P1/P2/P3 impact check: no source-of-truth ownership change; deterministic stale suppression correctness hardening only.

Latest run update (2026-04-27, metadata-stack rolling validation ledger activation):

- Published deterministic rolling evidence checklist for metadata-stack completion packets (`docs/testing/raw/meta_stack_end_to_end_validation_checklist.md`) and linked it into operator DevTools docs (`docs/testing/DEVTOOLS-TEMPLATES.local.md`).
- Engineering rigor baseline now requires pre/in/post + stale-root-cause + closeout proof recording for each remaining metadata slice.
- Runtime track disposition: compatibility-shimmed (governance/docs activation only; no runtime contract mutation).
- Component track disposition: compatibility-shimmed (governance/docs activation only; no component behavior mutation).
- P1/P2/P3 impact check: no source-of-truth ownership change; validation-evidence discipline hardening only.

- Component state-change parity now mirrors legacy handoff-trigger intent for additional entity changes used in runtime acceleration: detected receiver and now-playing entity updates now run the same component players-change refresh sequencing path (target-options refresh -> guarded auto-select) as MA-players changes.
- ESP now exports HA-visible telemetry surfaces for deterministic handoff diagnostics: control handoff status, resolved control target, and OLED/UI status.
- Deterministic scheduler validation template now reports ESP handoff/target/OLED status with runtime fallback visibility when ESP telemetry entities are unavailable.
- Runtime track disposition: implemented (ESP telemetry observability expansion).
- Component track disposition: implemented (trigger parity expansion).
- P1/P2/P3 impact check: no source-of-truth ownership change; parity + observability hardening only.

Latest run update (2026-04-27, startup no-mix + ESP diagnostics source/modality expansion):

- Component startup recovery now enforces no-mix sequencing for component authority windows: startup runs component-only options/auto-select scaffolds and skips legacy-trial bridge transitions (`skipped_component_startup_no_mix`) to prevent cross-authority boot windows.
- Deterministic scheduler validation diagnostics now include explicit source provenance and playback modality context in ESP diagnostics (resolved source entity/value/reason, playback player/modality classification, and available source options harvested from control-host candidate entities).
- Runtime track disposition: implemented (diagnostics surface expansion consumed from existing runtime contracts; no ownership/authority expansion).
- Component track disposition: implemented (startup no-mix recovery hardening + richer operator diagnostics visibility).
- P1/P2/P3 impact check: no source-of-truth ownership change; startup safety and observability hardening only.

Latest run update (2026-04-27, HA-reboot-safe ESP forced-refresh guard hardening):

- Runtime ESP handoff acceleration path now gates active-target-triggered forced `homeassistant.update_entity` calls for `sensor.ma_control_targets`, `sensor.ma_control_hosts`, and `sensor.ma_control_host` behind HA API reconnect grace + template-feed readiness checks.
- This removes the HA-reboot race where ESP uptime remained high and uptime-only guard logic still forced template updates during HA template initialization windows.
- Runtime track disposition: implemented (reconnect-safe forced-refresh guard hardening).
- Component track disposition: checked/not-applicable (component path does not originate these ESP-side force-update calls).
- P1/P2/P3 impact check: no source-of-truth ownership change; startup/reconnect race hardening only.

Latest run update (2026-04-27, startup handoff deadspot reduction):

- Runtime startup/refresh cadence hardened in `packages/ma_control_hub/automation.inc` to reduce post-boot deadspots: startup refresh delay reduced to 15s, periodic refresh tightened from `/5` to `/1`, and restore-last-valid target now re-attempts on early `ma_players`/`ma_control_targets` feed changes instead of startup-only timing.
- Component startup auto-recovery cadence hardened in `custom_components/spectra_ls/coordinator.py`: initial delay reduced to 4s, retry interval reduced to 8s, and max wait cycles reduced to 20 for faster MA-readiness convergence.
- Runtime track disposition: implemented (handoff latency deadspot reduction).
- Component track disposition: implemented (startup recovery responsiveness hardening).
- P1/P2/P3 impact check: no source-of-truth ownership change; bounded startup-latency and retry-cadence hardening only.

### P1/P2 validation snapshot (2026-04-19)

- P2 raw verification template has PASS evidence with `8/8` scoring and deterministic route decision output.
- Shadow diagnostics expose required closure attributes (`registry`, `route_trace`, `contract_validation`, `captured_at`) and freshness guard behavior.
- P1 parity surfaces are stable and remain read-only; legacy runtime remains source-of-truth.

Known evidence gap to keep explicit:

- Live HA runtime timing/state can differ from static repo analysis; every P3 write-path trial requires fresh runtime evidence captures in the same slice.

Latest runtime proof artifact (2026-04-19):

- Template verdict: `PASS`, score `8/8`.
- Route trace: `route_linkplay_tcp` with supported read-only scaffold mapping.
- Contract validation: `ready=true`, `valid=true`, `missing_required=0`.
- Parity diagnostics: `unresolved_sources=0`, `mismatches=0`.
- Freshness: captured snapshot age within threshold.

### P3 execution guardrails (required)

- **Single-writer rule:** at any given moment, either legacy or component owns writes; never dual-authoritative.
- **Loop-prevention rule:** correlation IDs + debounce + reentrancy guards are mandatory before enabling P3-S01.
- **Fallback-discipline rule:** if fallback is off, component must not silently route through static fallback branches.
- **Scope-discipline rule:** do not combine routing + selection + metadata ownership in one P3 slice.

### P3-S01 implementation checkpoint (2026-04-19)

Implemented in `custom_components/spectra_ls`:

- write-authority service (`legacy`/`component`) with legacy-default rollback-safe behavior,
- guarded routing write-trial service with correlation-id tracing,
- debounce + reentrancy + route-decision eligibility gates,
- write-control diagnostics (`write_controls`) in coordinator/shadow attributes.

Closeout status (2026-04-20):

- runtime trial + soak evidence captured under `component` authority,
- no parity regression gates outstanding for P3-S01,
- slice sealed in final P3 closeout checkpoint below.

### P3-S02 validation checkpoint (2026-04-19)

Implemented in `custom_components/spectra_ls`:

- one-shot validation sequence service (`run_p3_s02_sequence`) with optional write-trial toggle,
- structured selection-handoff readiness diagnostics in snapshot attributes (`selection_handoff_validation`),
- compatibility checks for legacy helper/options and required selection scripts/automation IDs,
- raw operator template for PASS/WARN/FAIL validation (`docs/testing/raw/p3_s02_selection_handoff_validation.jinja`).

Closeout decision (2026-04-19):

- sustained runtime evidence for S01/S02 stability was captured with clean compatibility/parity signals.
- baseline soak gate met (`3` successful PASS cycles, `5` attempts) with expected soft-skips on non-capable routes.
- distinct PASS-target gate is explicitly waived for single-capable-topology operation.
- closure gate is now represented by `docs/testing/raw/p3_s01_s02_closure_gate_check.jinja` for future repeatability.

Latest runtime proof artifact (2026-04-19):

- Template verdict: `PASS` (`p3_s02_selection_handoff_validation.jinja`).
- Authority/route: `component` + `route_linkplay_tcp`.
- Contract validation: `ready=true`, `valid=true`.
- Handoff diagnostics: `payload_ready=true`, `verdict=PASS`, `helper_exists=true`, `target_in_options=true`, `missing_scripts=0`, `missing_automation_ids=0`.

Latest soak runtime artifact (2026-04-19):

- Automated script verdict: `Spectra soak complete` (`script.spectra_p3_soak_one_shot`).
- Soak count/attempts: `3` successful cycles in `5` attempts.
- PASS cycles: `route=route_linkplay_tcp`, `contract_valid=True`, `handoff=PASS`.
- Drift/compatibility: `unresolved_sources=0`, `mismatches=0`, `missing_scripts=0`, `missing_automation_ids=0`.
- Skip behavior observed as expected: non-capable target soft-skips on `route=defer_not_capable`.
- Gate status: baseline soak stability gate met; distinct PASS-target gate remains open pending either second eligible target PASS or explicit waiver.

### Stage report snapshot — ownership + readiness (2026-04-19)

- Current ownership boundary:
  - **Legacy runtime (`packages/ma_control_hub/*.inc`) remains source-of-truth** for broad target-selection/control orchestration and compatibility helper surfaces.
  - **Custom component (`custom_components/spectra_ls`) currently owns** diagnostics/parity snapshots, one-shot validation orchestration (S01/S02), route-trace visibility, and guarded write-trial control framework.
- Readiness status:
  - **Closure-ready and sealed for P3-S02** using final soak evidence (`3/3` in `4` attempts, `distinct_pass_targets=2`).
  - Distinct PASS-target gate satisfied without waiver in the final run.

### P3-S03 implementation checkpoint (2026-04-19)

Implemented in `custom_components/spectra_ls`:

- metadata-prep diagnostics payload in coordinator snapshot (`metadata_prep_validation`),
- metadata contract presence checks for `ma_active_meta_entity`, `now_playing_*`, and `ma_meta_candidates`,
- deterministic metadata-prep verdicting (`PASS`/`WARN`/`FAIL`) with readiness flag,
- one-shot service orchestration (`run_p3_s03_sequence`) and direct refresh service (`validate_metadata_prep`),
- raw validation template for operator evidence capture (`docs/testing/raw/p3_s03_metadata_prep_validation.jinja`).

Closeout decision (2026-04-19):

- runtime S03 validation evidence captured with `PASS` (`7/7`) and `ready_for_metadata_handoff=true`,
- metadata contract checks report `missing_required=0` with all S03 gates true,
- explicit compatibility boundary retained: metadata ownership remains legacy/runtime (no component cutover writes),
- route/selection runtime context may show non-cutover states (`defer_not_capable`, legacy authority, S02 FAIL) outside targeted validation windows and does not block P3-S03 diagnostics closeout.

Latest runtime proof artifact (2026-04-19):

- Template verdict: `PASS` (`p3_s03_metadata_prep_validation.jinja`).
- Gate score: `7/7`.
- Metadata-prep readiness: `ready_for_metadata_handoff=true`.
- Contract details: `missing_required=0`, `missing_keys=[]`.

Final runtime proof snapshot (2026-04-19 22:51 local):

- Active target/path: `media_player.spectra_ls_2` / `linkplay_tcp`.
- Metadata value probes resolved: `active_meta_entity=media_player.spectra_ls`, `now_playing_entity=media_player.spectra_ls`, `now_playing_state=paused`, `now_playing_title=Network`.
- All S03 gates true (`contract`, `active_meta`, `now_playing_entity/state/title`, `candidate_payload_ready`, `route_trace_present`).
- Compatibility boundary remains explicit: runtime can still show non-cutover route/selection context (`route=defer_not_capable`, authority=`legacy`, selection_handoff=`FAIL`) without invalidating diagnostics-only P3-S03 closeout.

### P3-H1 second-pass hardening checkpoint (2026-04-19)

Implemented as a bounded reliability hardening pass (no ownership expansion):

- coordinator listener scope widened to include key helper/metadata entities to reduce stale diagnostics windows,
- metadata candidate readiness semantics tightened to require structurally meaningful candidate payloads (non-empty entity-bearing candidate data),
- closure gate now enforces soak-attempt consistency (`attempts >= pass cycles` and `attempts > 0`),
- P3 templates (`S01`, `S02`, `S03`, closure gate) now include explicit snapshot freshness checks to reduce stale PASS false positives.

Disposition:

- Runtime track: compatibility contracts retained; no authority/ownership cutover.
- Component track: diagnostics hardening implemented.
- Parity: preserved; rerun closure templates to capture refreshed evidence when convenient.

### P3-H2 closure-gate soak parity checkpoint (2026-04-19)

Template closeout correctness fix:

- closure gate now accepts explicit `observed_parity_ok` operator evidence and applies it in `evaluation_mode=soak_evidence`,
- runtime parity remains visible as `runtime_now` in gate breakdown for drift diagnostics,
- prevents false WARN closure outcomes when post-soak runtime context temporarily reports parity drift unrelated to the validated soak window.

### P3-H3 closure-gate fail-closed checkpoint (2026-04-19)

Strict closeout enforcement update:

- closure gate defaults now fail-closed (`evaluation_mode=runtime` and conservative observed defaults),
- soak-evidence mode now requires provenance fields (`observed_evidence_source`, `observed_evidence_reference`, `observed_evidence_collected_at`) and enforces collected-at freshness <=24h,
- missing/invalid provenance forces `FAIL` to prevent optimistic PASS outcomes from unverified manual toggles.

### P3 final closeout checkpoint (2026-04-20)

Final sealing evidence captured:

- Soak automation completion: `Spectra soak complete` with `3` successful cycles in `4` attempts and `distinct_pass_targets=2`.
- PASS-cycle evidence includes deterministic eligible route (`route_linkplay_tcp`), `contract_valid=True`, and `handoff=PASS` on successful cycles.
- Closure gate semantics hardened and clarified: `runtime` mode is health-check-only; `soak_evidence` mode is closure-grade.
- Metadata candidate payload parity proof: `PASS 5/5` (`state_count=4`, `row_count=4`, `summary_entities=4`, aligned `best_candidate_json`/`summary.best_*`).

Seal decision:

- **P3-S01:** sealed.
- **P3-S02:** sealed.
- **P3-S03:** sealed (diagnostics-only metadata-prep lane as previously documented).
- **Phase 3 overall:** sealed; Phase-4 validation now sealed through F4-S03.

### Phase 4 bounded slice plan (post-P3)

| Slice | Scope | Runtime Track | Component Track | Exit gate |
| --- | --- | --- | --- | --- |
| F4-S01 | Capability matrix + profile scaffolding | Preserve existing helper behavior/contracts; no ownership cutover | Add profile schema skeleton + capability-map diagnostics surfaces | Deterministic diagnostics output; no parity regressions |
| F4-S02 | Programmable action catalog safety skeleton | Keep legacy action flows authoritative | Add arm/confirm/cooldown/audit schema + dry-run validation service | Sensitive-action safety gates verified in diagnostics |
| F4-S03 | Crossfade/balance service contract (diagnostics-first) | Keep current runtime control lane | Add normalized slider-domain contract + no-op service validation path | Contract + diagnostics PASS; no write-path authority expansion |

### F4-S01 implementation checkpoint (2026-04-19)

Implemented in `custom_components/spectra_ls`:

- capability/profile diagnostics payload (`capability_profile_validation`) in coordinator snapshot,
- capability matrix summary extraction from registry (`control_path_counts`, `hardware_family_counts`, capability union, control-capable counts),
- deterministic profile-schema skeleton surface (`schema_version`, `required_keys`, defaults),
- no-authority-expansion guard visibility (`authority_mode=legacy` expected for diagnostics lane),
- services: `validate_capability_profile`, `run_f4_s01_sequence`,
- raw validation template: `docs/testing/raw/f4_s01_capability_profile_validation.jinja`.

F4-S01 closeout evidence (2026-04-20):

- Runtime closure artifact captured with **PASS** (`gate_score=6/6`, timestamp `2026-04-20 03:14:23.318195-07:00`).
- Authority/ownership check passed: `authority_mode=legacy`, `no_authority_expansion=true`.
- Route/contract/metadata checks passed: `route=route_linkplay_tcp`, `contract_valid=true`, `metadata_prep_ready=true`.

Seal decision:

- **F4-S01:** sealed/validated.
- Continue Phase-4 execution on active **F4-S02** diagnostics lane.

### F4-S02 implementation checkpoint (2026-04-20)

Implemented in `custom_components/spectra_ls`:

- diagnostics payload `action_catalog_validation` in coordinator snapshot,
- deterministic action-schema surface for safety contracts (`action_id/label/domain/service/target_scope/safety` + required safety keys),
- diagnostics-only catalog rows with explicit `dry_run_only` safety posture,
- no-authority-expansion guard and F4-S01 readiness reference in validation checks,
- services: `validate_action_catalog`, `run_f4_s02_sequence`,
- raw validation template: `docs/testing/raw/f4_s02_action_catalog_validation.jinja`.

F4-S02 closeout evidence (2026-04-20):

- Runtime closure artifact captured with **PASS** (`gate_score=7/7`, timestamp `2026-04-20 03:19:04.074224-07:00`).
- Authority/safety checks passed: `authority_mode=legacy`, `dry_run_only=true`, `no_authority_expansion=true`.
- Dependency check passed: `f4_s01_ready_reference=true`.

Seal decision:

- **F4-S02:** sealed/validated.
- Continue Phase-4 execution on active **F4-S03** diagnostics lane.

### F4-S03 implementation checkpoint (2026-04-20)

Implemented in `custom_components/spectra_ls`:

- diagnostics payload `crossfade_balance_validation` in coordinator snapshot,
- normalized slider-domain contract schema surface (`f4_s03.v1`, directional domain + safety keys),
- mode-profile diagnostics for multi-room vs single-room behavior contracts,
- sample dry-run mix-plan visibility with explicit no-op fallback posture,
- services: `validate_crossfade_balance`, `run_f4_s03_sequence`,
- raw validation template: `docs/testing/raw/f4_s03_crossfade_balance_validation.jinja`.

Hardening pass-2 (2026-04-20):

- F4 sequence services (`run_f4_s01_sequence`, `run_f4_s02_sequence`, `run_f4_s03_sequence`) now execute with explicit stage wrappers and surface failure-stage context in raised errors to eliminate opaque "Unknown error" behavior during action calls.
- F4-S03 snapshot guard now normalizes `action_catalog_validation` to mapping-safe defaults before dependency access and hardens state-change callback refresh to fail-safe logging, preventing callback storm exceptions from `NoneType.get` regressions.

Hardening pass-3 (2026-04-20):

- F4-S03 diagnostics now expose explicit dependency context (`active_target_resolved`, `route_decision`, `blocking_reasons`) and template guidance for dependency-only WARN captures (`f4_s02_not_ready` with `defer_no_target`) using deterministic rerun order (F4-S01/F4-S02/F4-S03 legacy mode).

Hardening pass-4 (2026-04-20):

- Fixed accidental F4 builder split regression where `_build_action_catalog_validation` could return `None` after F4-S03 insertion, which forced false `ready_for_f4_s02=false` dependency WARN outcomes in F4-S03 despite healthy route/target context.

F4-S03 closeout evidence (2026-04-20):

- Runtime closure artifact captured with **PASS** (`gate_score=8/8`, timestamp `2026-04-20 03:57:35.874550-07:00`).
- Authority/safety checks passed: `authority_mode=legacy`, `no_authority_expansion=true`.
- Dependency and route checks passed: `ready_for_f4_s03_closeout=true`, `f4_s02_ready_reference=true`, `route_decision=route_linkplay_tcp`, `active_target=media_player.spectra_ls_2`, `active_path=linkplay_tcp`.
- Contract checks passed: `slider_schema_present=true`, `mode_profiles_present=true`, `sample_mix_plan.dry_run_only=true`, `dependency_reference.active_target_resolved=true`.

Seal decision:

- **F4-S03:** sealed/validated.
- **Phase 4 bounded diagnostics slice set (F4-S01/F4-S02/F4-S03):** sealed/validated.

P1/P2/P3 impact check (required):

- **P1 (shadow parity source-of-truth):** unchanged; parity surfaces remain read-only and stable.
- **P2 (registry/router foundation):** unchanged; route classification + contract-validation surfaces remain authoritative for diagnostics (`route_linkplay_tcp` confirmed in closeout capture).
- **P3 (guarded write-path boundary):** unchanged; single-writer authority boundary remains intact (`legacy` retained for F4 diagnostics lane, no ownership cutover).

Phase 5 entry criteria delta note (2026-04-20):

- F4 bounded diagnostics slices are sealed; execution may move to Phase 5 planning/execution only when all entry gates below are satisfied in the active change window.
- **Gate A (authority baseline):** default authority remains `legacy`; any cutover trial must be explicitly armed and reversible per-slice (no implicit ownership drift).
- **Gate B (contract parity):** P2 parity/contract templates remain PASS after enabling any Phase 5 domain flag.
- **Gate C (slice isolation):** execute one domain at a time (`routing` → `metadata` → optional `lighting orchestration`), with no multi-domain cutover in one slice.
- **Gate D (rollback proof):** each Phase 5 slice must include a verified rollback path and explicit stop conditions (loop/flap, mismatch, missing-compat surfaces).
- **Gate E (evidence threshold):** each Phase 5 slice requires fresh runtime evidence capture before changing status from Active to Validated.

Current disposition:

- **Phase 5 status remains Planned** pending Gate A–E satisfaction.
- No P1/P2/P3 source-of-truth or authority changes are introduced by this delta note.

Phase 5 starter slice proposal (P5-S01, routing domain only):

- **Slice scope (in):** bounded routing cutover trial for explicit write-path routing decision surfaces only (no metadata ownership cutover, no lighting-orchestration cutover).
- **Slice scope (out):** metadata selection/now-playing authority, lighting helper orchestration, naming cleanup/retirement.
- **Authority mode policy:** default remains `legacy`; slice permits explicit, reversible `component` routing trial windows only.
- **Track A (runtime):** compatibility-shimmed and retained as rollback authority path.
- **Track B (component):** active routing cutover trial implementation + diagnostics/evidence capture.

Execution gates for P5-S01 activation:

1. Gate A pass: authority baseline + reversible arm/disarm path present.
2. Gate B pass: P2 parity/contract templates PASS immediately before trial start.
3. Gate C pass: no concurrent metadata/lighting cutover toggles enabled.
4. Gate D pass: rollback script/path validated in same window.
5. Gate E pass: fresh runtime evidence artifact captured for trial outcome.

Stop conditions (fail-closed):

- loop/flap detection in route writes,
- contract mismatch on required compatibility surfaces,
- unresolved active target/control-host route path,
- stale evidence window (>24h) for closeout decision.

P1/P2/P3 impact check for P5-S01 proposal:

- **P1:** unchanged (shadow parity contracts remain intact).
- **P2:** authoritative parity gate remains mandatory pre/post trial.
- **P3:** authority boundary remains single-writer controlled with explicit rollback.

Status update:

- **P5-S01 validated** with bounded-window evidence set complete:
  - in-window proof captured (`PASS`, `write_proof=VERIFIED`, `last_attempt.status=noop_already_selected`),
  - post-window rollback proof captured (`authority_mode=legacy`) with healthy route/contract/parity/freshness.
- **Phase 5 remains in progress overall**; next slice activation remains gated and domain-isolated (metadata cutover planning/activation is separate from this routing-slice validation).
- **P5-S02 (metadata domain) moved to Active gate-prep** using `docs/testing/raw/p5_s02_metadata_cutover_run_window_checklist.md`; no metadata write-authority takeover is implied until an explicit documented mechanism exists and gates are satisfied.

P5-S02 process depth note (beyond mirroring):

- The roadmap now requires explicit mechanism design and controlled trials, not just parity mirroring:
  1. contract inventory freeze for metadata surfaces and ownership boundaries,
  2. define component metadata authority mechanism/service contract,
  3. run bounded metadata write-path trial window with rollback-first controls,
  4. capture pre/in/post window evidence and validate fail-closed stop conditions,
  5. promote to validated only after rollback/authority disposition proof and stable parity.

Latest runtime evidence artifact (2026-04-20):

- Monitor verdict: `Status=PASS`, `Metadata readiness=READY` at `2026-04-20 17:59:21.972073-07:00`.
- Baseline/route: `authority_mode=legacy`, `route_decision=route_linkplay_tcp`.
- Contract/metadata: `contract_valid=true`, `missing_required=0`, `metadata_verdict=PASS`, `ready_for_metadata_handoff=true`.
- Parity/freshness: `unresolved_sources=0`, `mismatches=0`, snapshot freshness within threshold.
- Post-window proof: final render captured at `2026-04-20 18:08:32.691994-07:00` confirms `authority_mode=legacy` with metadata/contract/parity gates still healthy.
- Disposition: this bounded run window is closeout-eligible and documented; Phase-5 metadata slice remains Active gate-prep overall until mechanism-definition and broader slice gates are completed.

Run-3 evidence update (2026-04-20 evening):

- Legacy-mode run (`p5s02-run3`) showed expected fail-closed dry-run behavior when metadata lane was not ready (`metadata_trial_last_attempt.status=blocked_metadata_not_ready`) with contracts/parity clean.
- Same run reached `PASS/READY` (`gate_score=9/9`) under fresh active metadata/title conditions while authority baseline remained `legacy`.
- Component-mode comparison capture correctly reported policy CAUTION/WARN (`authority_mode_not_legacy`) with metadata ownership still `legacy_contract_surfaces`; this is expected and not a contract/parity regression.

Next execution target (P5-S02-M1):

- Implemented: `spectra_ls.metadata_write_trial` contract path is now wired in `custom_components/spectra_ls` with fail-closed dry-run-first behavior and audit payload surfacing in `write_controls.metadata_trial_last_attempt`.
- Implemented: `spectra_ls.run_p5_s02_sequence` one-shot service now performs bounded-window authority baseline + registry/contracts/route/handoff/metadata refresh + guarded metadata trial + post-trial metadata refresh in one deterministic call path.
- Hardening update: contract validity now fail-closes on unresolved required surfaces (present but `unknown`/`unavailable`), including control-host loss scenarios, and the monitor now exposes `contract_validation.unresolved_required` for explicit diagnostics.
- Hardening update (audit canonicalization): coordinator now emits native audit completeness fields (`audit_payload_complete`, `audit_payload_state`, `missing_audit_fields`) in `metadata_trial_last_attempt`, allowing monitor/checklist interpretation to use payload-native `COMPLETE/PARTIAL/N/A` state.
- Hardening update (trial gate semantics): coordinator now emits explicit trial preflight semantics (`blocking_reasons`, `trial_gate_verdict`, `eligible_for_closeout`) so P5-S02 window outcomes classify deterministically without string-inference.
- Fresh dry-run promotion evidence captured (`p5s02-2026-04-21-run1`):
  - monitor verdict `PASS/READY` at `2026-04-21 17:18:18.431382-07:00`,
  - `authority_mode=legacy`, `route_decision=route_linkplay_tcp`,
  - contract clean (`missing_required=0`, `unresolved_required=0`),
  - metadata gate `9/9`,
  - metadata trial audit `status=dry_run_ok`, `audit_payload_state=COMPLETE`, `trial_gate_verdict=PASS`, `eligible_for_closeout=true`, `missing_audit_fields=0`.
- Promotion-gate status: the documented “fresh dry-run + complete audit payload” requirement for P5-S02-M1 is now satisfied; metadata ownership remains intentionally legacy (`metadata_authority_owner=legacy_contract_surfaces`, `metadata_cutover_active=false`).
- Immediate next execution packet (P5-S02 Run-2 strict comparator):
  - run one fresh bounded sequence via `spectra_ls.run_p5_s02_sequence` with:
    - `mode=legacy`
    - `dry_run=true`
    - unique `window_id` (new value)
    - non-empty `reason`
    - `expected_target=<pre-window route_trace.active_target>` (discovery-first; no install-specific hardcode)
    - `expected_route=<pre-window route_trace.decision>` (for example `route_linkplay_tcp`)
  - capture one fresh monitor artifact and verify:
    - `status=PASS`, `metadata_readiness=READY`
    - `metadata_trial_last_attempt.status in {dry_run_ok, applied, noop}`
    - `trial_gate_verdict=PASS`, `eligible_for_closeout=true`
    - `missing_audit_fields=0`, `audit_payload_state=COMPLETE`
  - keep explicit post-window authority disposition at `legacy`.
  - if active target is intentionally churning during the window, omit `expected_target` and keep `expected_route` strict to avoid false mismatch blocks.
- Run-2 evidence captured (`p5s02-2026-04-21-run2`):
  - monitor verdict `PASS/READY` at `2026-04-21 17:25:39.987075-07:00`,
  - safe baseline retained: `authority_mode=legacy`, `route_decision=route_linkplay_tcp`,
  - contract clean: `missing_required=0`, `unresolved_required=0`,
  - metadata gate healthy: `verdict=PASS`, `gate_score=9/9`,
  - trial audit complete: `status=dry_run_ok`, `window_id=p5s02-2026-04-21-run2`, `audit_payload_state=COMPLETE`, `trial_gate_verdict=PASS`, `eligible_for_closeout=true`, `missing_audit_fields=0`.
- Run-2 disposition: strict-comparator packet expectations are met with fresh bounded-window evidence; metadata ownership remains legacy (`metadata_authority_owner=legacy_contract_surfaces`, `metadata_cutover_active=false`).
- Closeout packet candidate (prepared):
  - bounded evidence set includes Run-1 and Run-2 PASS/READY captures with complete trial-audit payloads,
  - authority boundary remains explicit/safe (`legacy` baseline retained across snapshots),
  - no contract/parity drift observed in captured windows (`missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`),
  - promotion recommendation accepted: `P5-S02` status is recorded as `Validated` in the active slice ledger.

Post-Phase destination note (operator UX target):

- After Phase-5 domain cutover gates are complete, the next required track is a full Home Assistant sidebar **Spectra Control Center**.
- This control center must include, at minimum:
  1. setup/onboarding pages (discovery status, route eligibility, contract readiness),
  2. tuning pages (input response/debounce and audio/lighting behavior profiles),
  3. defaults + override management (safe baseline policy plus per-target exceptions),
  4. mapped-environment visibility (resolved rooms/targets/control paths/capabilities),
  5. operator diagnostics/evidence views aligned to existing PASS/WARN/FAIL workflow.
- Execution ordering remains strict: **P5-S03 (lighting orchestration) is now the active slice**; sidebar control-center delivery remains post-Phase-5 and must not weaken gate-prep/validation discipline.

Deferred implementation scaffold note (H1):

- A detailed deferred H1 blueprint for diagnostics-driven report/log/heal flow is now published at `docs/features/H1-report-log-heal-scaffold.md`.
- This is planning-only in the current slice: no runtime behavior/authority ownership changes are enacted.
- H1 remains queued for later pickup after active P5 slice priorities.

Run-window execution checklist (required for activation/closeout evidence):

- `docs/testing/raw/p5_s02_metadata_cutover_run_window_checklist.md`

### Phase 5 next slice card — P5-S03 (lighting orchestration domain)

Status: **Validated**

Scope:

- **In:** lighting-domain orchestration gate-prep and bounded run-window validation only.
- **Out:** routing-domain ownership (already validated), metadata-domain ownership changes (P5-S02 lane), naming retirement.

Activation gates (all required):

1. P5-S02 closeout decision recorded (`Validated`) and linked in status ledger.
2. Authority baseline `legacy` confirmed at lighting-window start.
3. Lighting contract/parity precheck PASS in active window.
4. Domain isolation enforced (no concurrent metadata/routing cutover execution).
5. Rollback/disarm path validated and timestamped in-window.

Stop conditions (fail-closed):

- lighting contract drift or unresolved required lighting surfaces,
- route/authority drift outside declared window posture,
- stale/missing evidence artifacts for pre/in/post window sequence,
- unexpected cross-domain side effects during lighting validation interactions.

Execution checklist (new):

- `docs/testing/raw/p5_s03_lighting_orchestration_run_window_checklist.md`
- Primary live monitor: `docs/testing/raw/p5_s03_lighting_functionality_monitor.jinja`
- Freshness semantics correction: P5-S03 monitor now treats control snapshot freshness as informational context only (not a hard verdict gate) to avoid false WARN/CAUTION when lighting authority/contract/selector/parity signals are healthy.
- Run-1 completed and closed out with full pre/in/post packet:
  - pre-window `PASS/READY` (`2026-04-21 17:41:12.841574-07:00`),
  - in-window `PASS/READY` (`2026-04-21 17:44:00.229390-07:00`),
  - post-window `PASS/READY` (`2026-04-21 17:44:45.600796-07:00`).
- Closeout posture confirmed: `authority_mode=legacy`, contract/parity clean (`missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`), stop conditions not triggered.

### Phase 5 next slice card — P5-S04 (phase-exit closeout)

Status: **Validated**

Scope:

- **In:** cross-slice Phase-5 closeout packet, final authority/parity snapshot, and explicit P6 handoff gate.
- **Out:** new routing/metadata/lighting ownership behavior changes.

Activation gates (required):

1. P5-S01/P5-S02/P5-S03 are each ledger-marked `Validated` with linked evidence artifacts.
2. Fresh closeout-window snapshot confirms safe authority baseline + contract/parity stability.
3. Legacy retirement remains explicitly deferred until approved post-Phase-5 migration step.
4. P6 handoff posture is planning-eligible only (no implicit authority expansion).

Execution checklist:

- `docs/testing/raw/p5_s04_phase_exit_closeout_checklist.md`
- Primary live monitor: `docs/testing/raw/p5_s04_phase_exit_functionality_monitor.jinja`

Closeout evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `Phase-5 closeout readiness=READY`, `gate_score=7/7` (`2026-04-21 19:04:03.253466-07:00`),
- runtime safety gates all pass: `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, `contract_valid=true`, `missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`, freshness within threshold,
- governance gates all pass: domain closure linkage confirmed for P5-S01/S02/S03, rollback posture documented, retirement explicitly deferred, and P6 handoff planning posture explicit.

Disposition:

- `P5-S04` promoted to **Validated**.
- Phase-5 closeout packet accepted; P6 planning handoff is ready.

### Phase 6 starter slice card — P6-S01 (control-center foundation)

Status: **Validated**

Scope:

- **In:** control-center foundation scaffold (setup/tuning/defaults/overrides/mapped-environment views), diagnostics/evidence linkage, and read-only-first launch posture.
- **Out:** unbounded authority expansion, breaking helper/entity renames, and legacy retirement execution.

Activation gates (required):

1. P5-S04 closeout validated and linked as handoff prerequisite.
2. Runtime baseline remains safe (`authority_mode=legacy`) with clean route/contract/parity context.
3. Read-only-first UX posture is explicit for foundation rollout.
4. Backward compatibility + rollback posture are documented for any introduced P6 surfaces.

Execution checklist:

- `docs/testing/raw/p6_s01_control_center_foundation_checklist.md`
- Primary live monitor: `docs/testing/raw/p6_s01_control_center_foundation_monitor.jinja`

Baseline evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P6-S01 readiness=READY`, `gate_score=6/6` (`2026-04-21 19:18:22.634239-07:00`),
- runtime baseline clean: `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, `contract_valid=true`, `missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`, freshness within threshold,
- foundation governance gates all true: read-only-first launch, compatibility posture, rollback posture, and bounded-authority posture.

Disposition:

- `P6-S01` promoted to **Validated** with baseline + closeout packet evidence accepted.

Closeout evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P6-S01 readiness=READY`, `gate_score=6/6` (`2026-04-21 20:17:21.077121-07:00`),
- runtime baseline clean: `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, `contract_valid=true`, `missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`, freshness within threshold,
- foundation governance gates all true: read-only-first launch, compatibility posture, rollback posture, and bounded-authority posture.

### Phase 6 follow-on slice checkpoint — P6-S02 (control-center settings contract)

Status: **Validated**

Implemented in `custom_components/spectra_ls`:

- integration options flow for encoder action mappings and button scene bindings,
- normalized settings contract with safe defaults and read-only-first posture support,
- additive service contract `spectra_ls.set_control_center_settings` for deterministic runtime updates,
- diagnostics and shadow-attribute visibility for control-center settings (`control_center_validation`, `write_controls.control_center_settings`).

Current disposition:

- **Track A (runtime):** unchanged; legacy/runtime remains source-of-truth for writes and rollback (`authority_mode=legacy` baseline preserved).
- **Track B (component):** validated functional settings foundation for sidebar/control-center customization path.
- **Parity note:** additive contract only; existing P1/P2/P3 parity surfaces and authority boundaries remain unchanged.

P1/P2/P3 impact check:

- **P1:** unchanged (shadow parity surfaces remain read-only and compatible).
- **P2:** unchanged (registry/router diagnostics contracts remain authoritative).
- **P3:** unchanged (single-writer authority boundary retained; no new ownership cutover).

Execution checklist:

- `docs/testing/raw/p6_s02_control_center_settings_checklist.md`
- Primary live monitor: `docs/testing/raw/p6_s02_control_center_settings_monitor.jinja`

Closeout evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P6-S02 readiness=READY`, `gate_score=4/4` (`2026-04-21 20:15:35.644673-07:00`),
- settings-contract readiness proven: `schema_version=p6_s02.v1`, `settings_present=true`, `ready_for_customization=true`, `required_keys=8`,
- safe baseline retained: `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, clean contract/parity (`missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`), freshness within threshold.

Promotion disposition:

- `P6-S02` promoted to **Validated**.

P1/P2/P3 impact check:

- **P1:** unchanged (shadow parity contracts remain read-only/stable).
- **P2:** unchanged (registry/router diagnostics remain authoritative).
- **P3:** unchanged (single-writer authority boundary remains explicit and bounded).

### Phase 6 follow-on slice checkpoint — P6-S03 (control-input execution skeleton)

Status: **Validated**

Implemented in `custom_components/spectra_ls`:

- service contract `spectra_ls.execute_control_center_input` for encoder/button event execution,
- dry-run-first execution semantics with read-only-mode enforcement,
- scene dispatch support for configured button scene mappings when read-only is disabled,
- diagnostics payload for latest control-input attempt (`write_controls.control_center_last_attempt`) including status/reason/correlation context.

Current disposition:

- **Track A (runtime):** unchanged compatibility/rollback baseline (`authority_mode=legacy` preserved).
- **Track B (component):** validated execution skeleton for mapped control-center inputs with fail-closed safety posture.
- **Parity note:** additive execution lane only; existing parity/authority contracts remain unchanged.

Closeout evidence linkage (2026-04-21):

- execution proof accepted via P6-S04 monitor/checklist packet (`Status=PASS`, `P6-S04 readiness=READY`, `gate_score=5/5` at `2026-04-21 20:07:51.471030-07:00`),
- deterministic execution semantics observed: `last_attempt.status=dry_run_ok`, `last_attempt.input_event=encoder_press`, `last_attempt.mapped_action=play_pause`, `last_attempt.dry_run=true`,
- safety baseline preserved throughout validation: `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, contract/parity clean (`missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`).

Promotion disposition:

- `P6-S03` promoted to **Validated**.

P1/P2/P3 impact check:

- **P1:** unchanged read-only parity surfaces and attributes.
- **P2:** unchanged registry/router contract ownership.
- **P3:** unchanged single-writer/write-authority boundary (no new ownership cutover).

### Phase 6 follow-on slice checkpoint — P6-S04 (control-input execution validation artifacts)

Status: **Validated**

Implemented in docs/testing artifacts:

- raw execution monitor template: `docs/testing/raw/p6_s04_control_input_execution_monitor.jinja`,
- bounded validation checklist: `docs/testing/raw/p6_s04_control_input_execution_checklist.md`,
- deterministic gate framing for runtime baseline, dry-run-first posture, read-only enforcement, and closeout readiness evidence.

Current disposition:

- **Track A (runtime):** unchanged compatibility/rollback baseline (`authority_mode=legacy` remains required).
- **Track B (component/docs):** validated operator-grade evidence tooling for the control-input execution lane with closeout packet accepted.
- **Parity note:** additive validation/governance artifacts only; no write-authority expansion.

Closeout evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P6-S04 readiness=READY`, `gate_score=5/5` (`2026-04-21 20:07:51.471030-07:00`),
- execution semantics deterministic: `last_attempt.status=dry_run_ok`, `last_attempt.input_event=encoder_press`, `last_attempt.mapped_action=play_pause`, `last_attempt.dry_run=true`,
- runtime safety baseline preserved: `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, contract/parity clean (`missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`), freshness within threshold.

Promotion disposition:

- `P6-S04` promoted to **Validated**.

P1/P2/P3 impact check:

- **P1:** unchanged read-only parity surfaces.
- **P2:** unchanged registry/router validation ownership.
- **P3:** unchanged single-writer authority boundary.

### Phase 7 starter slice card — P7-S01 (component-first cutover readiness gate)

Status: **Validated**

Scope:

- **In:** cutover-readiness gate activation, sustained-parity evidence framing, rollback proof framing, legacy seal criteria publication, and component-primary posture declaration for net-new feature development.
- **Out:** immediate authority flip, broad helper/entity contract deletions, and one-shot legacy retirement without bounded domain evidence.

Activation gates (required):

1. Phase-6 slices (`P6-S01..P6-S04`) are validated with accepted closeout packets.
2. Runtime safety baseline remains clean (`authority_mode=legacy` + contract/parity clean) at activation time.
3. Explicit rollback posture exists for every planned authority flip domain.
4. Net-new feature direction is declared component-first while legacy remains compatibility/rollback baseline until cutover proof is accepted.

Execution checklist:

- `docs/testing/raw/p7_s01_cutover_readiness_checklist.md`
- Primary live monitor: `docs/testing/raw/p7_s01_cutover_readiness_monitor.jinja`

Two-track disposition:

- **Track A (runtime):** compatibility/rollback baseline retained during readiness gate; freeze net-new feature growth in legacy path.
- **Track B (component):** designated primary control-plane path for next feature growth pending bounded authority flip proofs.
- **Parity note:** no authority ownership flip occurs in P7-S01; this slice establishes deterministic go/no-go gates for cutover sequence.

P1/P2/P3 impact check:

- **P1:** unchanged read-only parity contract surfaces.
- **P2:** unchanged registry/router diagnostics ownership.
- **P3:** single-writer boundary remains explicit; authority flip remains gated and deferred to follow-on P7 slices.

Run-1 evidence (2026-04-21):

- monitor verdict: `Status=FAIL`, `P7-S01 readiness=BLOCKED`, `gate_score=3/4` (`2026-04-21 20:33:32.373259-07:00`),
- baseline failure details: `route_decision=defer_no_target`, `unresolved_required=4`, `unresolved_sources=3`, `mismatches=2`,
- governance gates remained true: phase-6 closeout, component-primary posture, and rollback/bounded-cutover posture.

Disposition:

- `P7-S01` recovered from blocked baseline and is now **Validated** after Run-2 PASS evidence.

Run-2 closeout evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P7-S01 readiness=READY`, `gate_score=4/4` (`2026-04-21 20:34:32.639010-07:00`),
- baseline restored: `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, `missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`, freshness within threshold,
- governance gates all true: phase-6 closeout, component-primary posture, and rollback/bounded-cutover posture.

Promotion disposition:

- `P7-S01` promoted to **Validated**.

### Phase 7 follow-on slice checkpoint — P7-S02 (first bounded authority-flip execution lane)

Status: **Validated**

Scope:

- **In:** first bounded authority-flip execution lane (routing/selection domain), strict single-writer enforcement, rollback-safe activation controls, and run-window evidence capture.
- **Out:** cross-domain ownership flips, unbounded legacy retirement actions, and irreversible helper/entity contract removal.

Activation gates (required):

1. `P7-S01` is validated with accepted closeout packet.
2. Runtime baseline remains clean at activation (`authority_mode=legacy`, contract/parity clean).
3. Domain-flip rollback path and stop conditions are explicit before first write-window attempt.
4. Component lane remains net-new feature primary while flip windows are bounded and reversible.

Execution checklist:

- `docs/testing/raw/p7_s02_domain_flip_readiness_checklist.md`
- Primary live monitor: `docs/testing/raw/p7_s02_domain_flip_readiness_monitor.jinja`

Two-track disposition:

- **Track A (runtime):** rollback-safe authority baseline retained outside bounded flip windows.
- **Track B (component):** active first authority-flip execution lane.

P1/P2/P3 impact check:

- **P1:** unchanged read-only parity contract surfaces.
- **P2:** unchanged registry/router diagnostics ownership.
- **P3:** single-writer controls remain mandatory and explicitly audited in this slice.

Run-1 pre-window evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P7-S02 readiness=READY`, `gate_score=4/4` (`2026-04-21 20:38:00.223973-07:00`),
- baseline/gates clean: `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, `missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`, freshness within threshold,
- execution disposition: pre-window authorization granted; in-window and post-window captures are now required for closeout eligibility.

Run-1 in-window evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P7-S02 readiness=READY`, `gate_score=4/4` (`2026-04-21 20:55:41.000516-07:00`),
- in-window probe remained clean: `monitor_source_sensor=sensor.shadow_active_target`, `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, `missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`, freshness within threshold,
- execution disposition: in-window gate accepted; post-window capture remains required before closeout eligibility.

Run-1 post-window evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P7-S02 readiness=READY`, `gate_score=4/4` (`2026-04-21 20:57:00.162663-07:00`),
- post-window rollback-safe baseline verified: `monitor_source_sensor=sensor.shadow_active_target`, `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, `missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`, freshness within threshold,
- execution disposition: post-window gate accepted with no stop-condition triggers; slice is closeout eligible.

Promotion disposition:

- `P7-S02` promoted to **Validated**.

### Phase 7 follow-on slice checkpoint — P7-S03 (bounded metadata-domain authority-flip execution lane)

Status: **Validated**

Scope:

- **In:** bounded metadata-domain authority-flip execution lane, metadata trial service-path probe (`metadata_write_trial`) with dry-run-first semantics, strict single-writer enforcement, rollback-safe activation controls, and pre/in/post run-window evidence capture.
- **Out:** routing-domain revalidation, lighting-domain ownership flips, unbounded legacy retirement actions, and irreversible helper/entity contract removal.

Activation gates (required):

1. `P7-S02` is validated with accepted closeout packet.
2. Runtime baseline remains clean at activation (`authority_mode=legacy`, contract/parity clean).
3. Metadata readiness is PASS/ready (`metadata_prep_validation.verdict=PASS`, `ready_for_metadata_handoff=true`) with route eligibility present.
4. Metadata-domain rollback path and stop conditions are explicit before first in-window metadata trial attempt.

Execution checklist:

- `docs/testing/raw/p7_s03_metadata_domain_flip_readiness_checklist.md`
- Primary live monitor: `docs/testing/raw/p7_s03_metadata_domain_flip_readiness_monitor.jinja`

Two-track disposition:

- **Track A (runtime):** rollback-safe metadata authority baseline retained outside bounded P7-S03 windows.
- **Track B (component):** active bounded metadata-domain authority-flip execution lane.

P1/P2/P3 impact check:

- **P1:** unchanged read-only parity contract surfaces.
- **P2:** unchanged registry/router diagnostics ownership.
- **P3:** single-writer controls remain mandatory and explicitly audited in this slice.

Run-1 pre-window evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P7-S03 readiness=READY`, `gate_score=4/4` (`2026-04-21 21:03:00.345491-07:00`),
- baseline/metadata gates clean: `monitor_source_sensor=sensor.shadow_active_target`, `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, `metadata_prep_validation.verdict=PASS`, `ready_for_metadata_handoff=true`, `metadata_prep_validation.missing_required=0`, contract/parity clean (`missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`), freshness within threshold,
- execution disposition: pre-window authorization granted; in-window and post-window captures are required for closeout eligibility.

Run-1 in-window evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P7-S03 readiness=READY`, `gate_score=4/4` (`2026-04-21 21:05:29.978417-07:00`),
- in-window probe remained clean: `monitor_source_sensor=sensor.shadow_active_target`, `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, `metadata_prep_validation.verdict=PASS`, `ready_for_metadata_handoff=true`, `metadata_prep_validation.missing_required=0`, `metadata_trial_last_attempt.status=dry_run_ok`, `metadata_trial_last_attempt.trial_gate_verdict=PASS`, contract/parity clean (`missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`), freshness within threshold,
- execution disposition: in-window gate accepted; post-window capture remained required before closeout eligibility.

Run-2 post-window evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P7-S03 readiness=READY`, `gate_score=4/4` (`2026-04-21 21:07:08.345292-07:00`),
- post-window rollback-safe baseline remained clean: `monitor_source_sensor=sensor.shadow_active_target`, `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, `metadata_prep_validation.verdict=PASS`, `ready_for_metadata_handoff=true`, `metadata_prep_validation.missing_required=0`, `metadata_trial_last_attempt.status=dry_run_ok`, `metadata_trial_last_attempt.window_id=window_id: p7s03-2026-04-21-run2`, `metadata_trial_last_attempt.trial_gate_verdict=PASS`, contract/parity clean (`missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`), freshness within threshold,
- execution disposition: post-window gate accepted with no stop-condition triggers; slice is closeout eligible.

Promotion disposition:

- `P7-S03` promoted to **Validated**.

### Phase 7 follow-on slice checkpoint — P7-S04 (phase-exit closeout packet)

Status: **Validated**

Scope:

- **In:** Phase-7 closeout packet consolidation, final rollback-safe baseline evidence capture, and promotion gating.
- **Out:** new domain authority expansion, additional write-path cutover trials, and immediate legacy retirement execution.

Activation gates (required):

1. `P7-S01`, `P7-S02`, and `P7-S03` are validated with linked evidence packets.
2. Runtime baseline is still rollback-safe at closeout capture time (`authority_mode=legacy`, clean contract/parity).
3. Rollback path and single-writer boundary remain explicit and operator-verifiable.
4. Component-primary posture and legacy-seal scope are documented for closeout governance.

Execution checklist:

- `docs/testing/raw/p7_s04_phase_exit_closeout_checklist.md`
- Primary live monitor: `docs/testing/raw/p7_s04_phase_exit_functionality_monitor.jinja`

Two-track disposition:

- **Track A (runtime):** rollback-safe compatibility baseline retained for closeout capture.
- **Track B (component):** active phase-exit closeout packet lane.

P1/P2/P3 impact check:

- **P1:** unchanged read-only parity contract surfaces.
- **P2:** unchanged registry/router diagnostics ownership.
- **P3:** unchanged single-writer boundary and rollback discipline.

Run-1 closeout evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P7-S04 readiness=READY`, `gate_score=4/4` (`2026-04-21 21:13:00.468462-07:00`),
- baseline remained rollback-safe and clean: `monitor_source_sensor=sensor.shadow_active_target`, `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, `contract_valid=true`, `missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`, freshness within threshold (`age_s=60.0`),
- closeout disposition: no stop-condition triggers; phase-exit packet is complete and promotion-eligible.

Promotion disposition:

- `P7-S04` promoted to **Validated**.

### Phase 8 starter slice card — P8-S01 (legacy-seal readiness gate)

Status: **Validated**

Scope:

- **In:** post-cutover legacy-seal readiness gating, rollback-safe baseline verification, and governance continuity checks.
- **Out:** runtime ownership expansion, irreversible legacy retirement actions, and net-new write-path cutover behavior.

Activation gates (required):

1. Phase-7 closeout packet is validated.
2. Runtime baseline remains rollback-safe (`authority_mode=legacy`) with clean contract/parity.
3. Rollback + single-writer controls remain explicit and verifiable.
4. Legacy net-new growth freeze and component-primary posture remain explicit.

Execution checklist:

- `docs/testing/raw/p8_s01_legacy_seal_readiness_checklist.md`
- Primary live monitor: `docs/testing/raw/p8_s01_legacy_seal_readiness_monitor.jinja`

Two-track disposition:

- **Track A (runtime):** sealed rollback-safe baseline with no net-new ownership growth.
- **Track B (component):** active governance/readiness lane for post-cutover operation.

P1/P2/P3 impact check:

- **P1:** unchanged read-only parity contract surfaces.
- **P2:** unchanged registry/router diagnostics ownership.
- **P3:** unchanged single-writer boundary and rollback discipline.

Run-1 pre-window evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P8-S01 readiness=READY`, `gate_score=4/4` (`2026-04-21 21:18:39.504385-07:00`),
- baseline/gates clean: `monitor_source_sensor=sensor.shadow_active_target`, `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, `contract_valid=true`, `missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`, freshness within threshold (`age_s=157.6`),
- execution disposition: pre-window authorization accepted; in-window and post-window captures remain required before closeout eligibility.

Run-2 in-window evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P8-S01 readiness=READY`, `gate_score=4/4` (`2026-04-21 21:22:08.276673-07:00`),
- baseline/gates clean: `monitor_source_sensor=sensor.shadow_active_target`, `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, `contract_valid=true`, `missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`, freshness within threshold (`age_s=171.6`),
- execution disposition: in-window capture accepted; post-window capture remained required before closeout eligibility.

Run-3 post-window evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P8-S01 readiness=READY`, `gate_score=4/4` (`2026-04-21 21:22:20.668596-07:00`),
- baseline/gates clean: `monitor_source_sensor=sensor.shadow_active_target`, `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, `contract_valid=true`, `missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`, freshness within threshold (`age_s=184.0`),
- execution disposition: post-window capture accepted; pre/in/post packet complete with no stop-condition triggers.

Activation disposition:

- `P8-S01` activation packet is published with full pre/in/post PASS packet captured.
- `P8-S01` promoted to **Validated**.

### Phase 8 follow-on slice card — P8-S02 (docs + wiki native-English overhaul)

Status: **Active**

Scope:

- **In:** improve user/operator/developer-facing documentation with direct, native-English, task-oriented language; remove AI-sounding phrasing; improve wiki utility with clear outcomes, decision paths, and troubleshooting flow.
- **Out:** runtime/component behavior changes, contract ownership changes, or migration gate policy changes.

Activation gates (required):

1. P8-S01 is validated and closed.
2. A reusable writing standard is published for wiki/repo docs consistency.
3. Wiki navigation and page intent are updated to prioritize operator usefulness.
4. Documentation changes remain parity-synchronized through changelog + roadmap ledgers.

Execution checklist:

- Writing standard: `docs/wiki/DOCUMENTATION-WRITING-STANDARD.md`
- Wiki source index: `docs/wiki/README.md`
- Wiki home/navigation: `docs/wiki/Home.md`, `docs/wiki/_Sidebar.md`

Two-track disposition:

- **Track A (runtime):** unchanged sealed compatibility baseline.
- **Track B (component):** unchanged primary product-growth lane while docs quality lane executes.

P1/P2/P3 impact check:

- **P1:** unchanged read-only parity contract surfaces.
- **P2:** unchanged registry/router diagnostics ownership.
- **P3:** unchanged single-writer boundary and rollback discipline.

Initial execution disposition:

- P8-S02 activated with writing-standard scaffolding and wiki-navigation updates.

Run-1 execution update (2026-04-21):

- Sidebar/component lane: added `Control Center Last Attempt Status` diagnostic sensor in `custom_components/spectra_ls/sensor.py` so mapped-input outcomes are visible as first-class state instead of only deep attributes.
- Documentation/wiki lane: improved high-traffic operator onboarding/install/setup pages (`docs/wiki/Getting-Started.md`, `docs/wiki/Install-on-Your-Own-HA.md`, `docs/wiki/User-Setup-Deploy-and-HA-Integration.md`) with task-first structure, explicit expected outcomes, and failure actions.
- Execution disposition: run-1 packet accepted; remaining wiki/page sweep continues in subsequent packets.

Run-2 execution update (2026-04-21):

- Top-level docs lane: improved `CONTRIBUTING.md` with clearer workflow language, branch boundaries, and migration posture expectations.
- Execution disposition: run-2 contributor-doc polish accepted; additional repo/docs and wiki passes remain queued.

Run-3 execution update (2026-04-22):

- Top-level docs lane: polished `README.md` and `docs/README.md` with more directive, task-first language and clearer “what to read next” guidance.
- Validation lane: completed local wiki sync dry-run (`dry_run_ok`) with clone/read sync success and 17 staged wiki-file deltas in temp workspace (no push), confirming publish-ready source changes.
- Execution disposition: run-3 packet accepted; continue remaining page-by-page wiki cleanup passes.

Run-4 execution update (2026-04-22):

- Wiki docs lane: improved remaining core workflow/architecture contributor pages (`docs/wiki/Operations-Runbooks.md`, `docs/wiki/System-Architecture.md`, `docs/wiki/Contributing-Workflow.md`) with direct task flow, explicit outcomes, and parity/ownership reminders.
- Execution disposition: run-4 packet accepted; continue remaining lower-traffic wiki cleanup pages and consistency passes.

Run-5 execution update (2026-04-22):

- Navigation/reference lane: aligned top-level + wiki entry navigation (`README.md`, `docs/wiki/Home.md`, `docs/wiki/_Sidebar.md`, `docs/wiki/README.md`) to link-first reference paths and stronger canonical source routing.
- Language lane: removed low-value process narration about edit mechanics and kept page intent outcome-focused.
- Execution disposition: run-5 packet accepted; continue remaining long-tail page consistency cleanup.

Run-6 execution update (2026-04-22):

- Long-tail wiki lane: improved process/reference-heavy pages (`docs/wiki/Getting-Started.md`, `docs/wiki/Discussions-and-Projects-Workflow.md`, `docs/wiki/Release-and-Changelog-Process.md`, `docs/wiki/Wiki-Content-Scope-Policy.md`, `docs/wiki/Contributing-Workflow.md`, `docs/wiki/Operations-Runbooks.md`) with explicit clickable links for canonical repo references.
- Execution disposition: run-6 packet accepted; continue remaining page-by-page consistency sweep as follow-on maintenance.

Run-7 execution update (2026-04-22):

- High-traffic wiki lane: improved architecture/orientation/install pages (`docs/wiki/System-Architecture.md`, `docs/wiki/Welcome-README-and-Bug-Workflow.md`, `docs/wiki/Install-on-Your-Own-HA.md`) with explicit link-first references for canonical sources and runbooks.
- Execution disposition: run-7 packet accepted; continue residual link-normalization sweep as follow-on maintenance.

Run-8 execution update (2026-04-22):

- Residual wiki lane: improved contract/control-surface/setup-roadmap pages (`docs/wiki/Control-Contracts-and-Scope-Paths.md`, `docs/wiki/Control-Surface-Inputs-and-Expanders.md`, `docs/wiki/User-Setup-Deploy-and-HA-Integration.md`, `docs/wiki/Custom-Component-Setup-Roadmap-Stub.md`) with explicit link-first references for canonical repo sources.
- Execution disposition: run-8 packet accepted; continue small residual cleanup as follow-on maintenance.

Run-9 execution update (2026-04-22):

- Process/navigation lane: improved residual process and wiki-publishing pages (`docs/wiki/Contributing-Workflow.md`, `docs/wiki/Operations-Runbooks.md`, `docs/wiki/Release-and-Changelog-Process.md`, `docs/wiki/README.md`, `docs/wiki/Home.md`) with explicit link-first references for parity and publishing workflows.
- Execution disposition: run-9 packet accepted; continue optional long-tail consistency cleanup as follow-on maintenance.

Run-10 execution update (2026-04-22):

- Residual policy lane: improved final non-table policy/process literals in `docs/wiki/Contributing-Workflow.md`, `docs/wiki/Wiki-Content-Scope-Policy.md`, and `docs/wiki/Install-on-Your-Own-HA.md` with explicit links where operator navigation benefits.
- Execution disposition: run-10 packet accepted; remaining literals are primarily intentional contract/path notation.

Run-11 execution update (2026-04-22):

- Writing-standard lane: improved `docs/wiki/DOCUMENTATION-WRITING-STANDARD.md` examples and path references with explicit link-aware references while keeping guidance semantics intact.
- Execution disposition: run-11 packet accepted; remaining literal references are primarily intentional contract/table notation.

Run-12 execution update (2026-04-22):

- Component UX lane: improved `custom_components/spectra_ls` control-center setup defaults and diagnostics visibility by adding scene-aware options defaults/selectors, stricter scene-binding normalization, richer coordinator readiness diagnostics, and a dedicated readiness sensor surface.
- Execution disposition: run-12 packet accepted; runtime track unchanged compatibility baseline, component track additive UX/observability hardening.

Run-13 execution update (2026-04-22):

- Plan-delta lane: clarified cutover semantics so component remains the primary development lane for net-new work while legacy remains an explicit rollback-safe authority baseline for compatibility contracts until bounded retirement gates are executed.
- Priority lane: activated `P8-S03` as a core fast-remap UX slice so operators can quickly re-map button/encoder input behavior from Home Assistant integration settings without script-level edits.
- Execution disposition: run-13 packet accepted; runtime track unchanged compatibility baseline, component track prioritizes operator remap workflow acceleration.

Run-14 execution update (2026-04-22):

- Component remap lane: implemented preset-driven fast remap contract in integration settings/service surfaces (`media_default`, `scene_focus`, `target_navigation`, `custom`) with backward-compatible manual override flow.
- Diagnostics lane: added active preset + effective mapping visibility in control-center readiness/attempt diagnostics for quick operator verification after remap.
- Execution disposition: run-14 packet accepted; runtime track unchanged compatibility baseline, component track advanced P8-S03 operator remap implementation.

Run-15 execution update (2026-04-22):

- Component UX maturity lane: refactored integration settings to a guided two-step flow (quick preset/safety step + conditional advanced custom-mapping step) so common remaps complete faster while custom mapping remains one click away.
- Selector ergonomics lane: replaced raw option-value style with explicit human-readable option labels for presets and encoder action choices to better match mature HA integration settings UX patterns.
- Execution disposition: run-15 packet accepted; runtime track unchanged compatibility baseline, component track implemented guided remap flow ergonomics hardening.

Run-16 execution update (2026-04-22):

- Setup-lane clarity lane: added an explicit first-step chooser in integration options so operators select `Quick setup` or `Advanced mapping` before entering remap fields.
- Flow-structure lane: split options UX into dedicated quick and advanced steps (`init -> quick/advanced`) so the common preset path is fast while manual mapping remains a focused advanced path.
- Execution disposition: run-16 packet accepted; runtime track unchanged compatibility baseline, component track implemented explicit lane separation for settings UX.

Run-17 execution update (2026-04-22):

- Label-clarity lane: refined setup/action selector labels for quicker scanability and lower operator ambiguity.
- Default-lane lane: set smarter setup-lane default (`advanced` when existing preset is `custom`, otherwise `quick`) so re-opened settings land in the expected path.
- Execution disposition: run-17 packet accepted; runtime track unchanged compatibility baseline, component track implemented settings-flow polish.

Run-18 execution update (2026-04-22):

- Corrective UX lane: simplify integration Configure UX from multi-lane flow back to a single-step settings form to reduce operator confusion.
- Sidebar surface lane: add a real Home Assistant sidebar dashboard entry (`Spectra L/S`) for persistent settings/readiness visibility outside the modal configure dialog.
- Execution disposition: run-18 packet accepted; runtime track unchanged compatibility baseline, component track implemented usability/navigation correction.

Run-19 execution update (2026-04-22):

- Sidebar reliability lane: correct sidebar dashboard sensor bindings to match real registered entity IDs and eliminate post-restart `Entity not found` cards.
- Execution disposition: run-19 packet accepted; runtime track unchanged compatibility baseline, component track implemented dashboard reliability correction.

Run-20 execution update (2026-04-22):

- MA exploration lane: publish a future-focused technical note that consolidates Music Assistant plugin/provider extension routes, capability constraints, and recommended integration path for Spectra audio-side ownership.
- Fast-cutover planning lane: queue the next bounded phase slice to execute immediately after UX usefulness closure, with explicit gates, stop conditions, rollback posture, and evidence packet requirements.
- Execution disposition: run-20 packet accepted; runtime track compatibility-shimmed, component track deferred-with-rationale as the queued next slice.

Run-21 execution update (2026-04-22):

- UX completion lane: finish the sidebar usability pass by replacing dev-tools-only quick actions with direct one-click action buttons for dry-run probes and rollback-safe preset application.
- Operator flow lane: align wiki/setup docs to the click-first sidebar workflow and mark the current UX-stage lane complete.
- Execution disposition: run-21 packet accepted; `P8-S03` promoted to validated, and `P8-S04` moved from queued to active planning/execution prep.

Run-22 execution update (2026-04-22):

- P8-S04 activation lane: publish deterministic monitor + checklist artifacts for MA-native plugin/provider fast-cutover gate-prep windows (pre/in/post).
- Evidence lane: add explicit rollback-safe stop conditions and packet fields so first MA probe can be classified PASS/WARN/FAIL without ad hoc interpretation.
- Execution disposition: run-22 packet accepted; `P8-S04` is now active with execution artifacts published.

Run-23 execution update (2026-04-22):

- Run-2 packet lane: publish a strict in-window execution packet for `P8-S04` with explicit `run_id`, `selected_path=player_provider`, dry-run-first probe posture, and artifact-reference capture fields.
- Governance lane: keep promotion blocked at Run-2 by policy until post-window rollback proof is captured in a subsequent record.
- Execution disposition: run-23 packet accepted; P8-S04 Run-2 is execution-ready.

Run-24 execution update (2026-04-26):

- Runtime MA-ops lane: added fast MA backend profile switching contract in `ma_control_hub` (`beta`/`stable`/`manual`) with profile-aware API URL resolution and explicit effective-profile sensor visibility for rapid Beta↔Stable test loops.
- Component diagnostics lane: added parity-visibility snapshot fields for MA backend profile/effective URL in `custom_components/spectra_ls` without ownership expansion.
- Execution disposition: run-24 packet accepted; two-track disposition is runtime `implemented`, component `compatibility-shimmed`. P1/P2/P3 impact check: no ownership/source-of-truth flip; additive operator workflow hardening only.

Run-25 execution update (2026-04-26):

- Runtime host-routing lane: harden `ma_control_hub` control-host derivation for wrapper targets by adding direct alias-entity lookup before static host fallback (detected receiver, active meta, now-playing, active-player entity, and friendly-name alias candidates with direct/member `ip_address`).
- Component parity lane: mirror the same host-discovery order in `custom_components/spectra_ls` registry (direct target/member resolution + alias-friendly fallback) so route-trace diagnostics stay lock-step with runtime host resolution semantics.
- Execution disposition: run-25 packet accepted; two-track disposition is runtime `implemented`, component `implemented`. P1/P2/P3 impact check: no ownership/source-of-truth flip; host-routing correctness hardening only.

Run-26 execution update (2026-04-26):

- Component parity hardening lane: metadata-prep readiness now uses a signal-ready title gate so transient title lag does not force false blocker states when fresh-play + active-meta context is present; metadata-candidate readiness now falls back to resolver best-candidate context when candidate payload shape is delayed.
- Maturity/progression lane: handoff inventory status transitions for `target_options_builder`, `auto_select_pipeline`, and `metadata_resolver_authority` now move to `implemented` only after successful guarded scaffold attempts (instead of static scaffold-plan presence), making next-slice parity progress explicit.
- Execution disposition: run-26 packet accepted; two-track disposition runtime `compatibility-shimmed`, component `implemented`. P1/P2/P3 impact: no ownership/source-of-truth cutover change; metadata readiness and parity-progress signal correctness hardening only.

Run-27 execution update (2026-04-26):

- Selection-ownership migration lane: implemented component-native executable services for legacy selection lifecycle parity (`cycle_active_target`, `restore_last_valid_target`, `track_last_valid_target`) with guarded authority/reentrancy/debounce semantics and attempt telemetry in `write_controls`.
- Startup-recovery lane: startup auto-recovery now invokes bounded component restore-last-valid behavior when component authority is active (dry-run otherwise), reducing manual post-restart selection repair steps while preserving fail-closed legacy baseline.
- Execution disposition: run-27 packet accepted; two-track disposition runtime `compatibility-shimmed`, component `implemented`. P1/P2/P3 impact: no source-of-truth ownership flip; bounded selection-domain migration progression only.

### Phase 8 follow-on slice card — P8-S03 (fast input-remap UX in HA settings)

Status: **Validated**

Scope:

- **In:** operator-first remap workflow for encoder/button actions in integration settings, tighter quick-remap defaults/presets, and diagnostics that explicitly show “what is currently mapped where.”
- **Out:** unbounded authority expansion, legacy contract retirement, or cross-domain ownership changes.

Activation gates (required):

1. P8-S01 validated baseline remains clean (`authority_mode=legacy`, parity/contract clean).
2. Existing P6 settings contract remains backward compatible (no helper/entity contract breaks).
3. Remap workflow is fast/operator-friendly from HA integration settings path.
4. Rollback-safe posture remains explicit with read-only-first behavior where applicable.

Execution checklist:

- Component settings workflow: `custom_components/spectra_ls/config_flow.py`
- Mapping normalization/contract: `custom_components/spectra_ls/const.py`
- Execution/readiness visibility: `custom_components/spectra_ls/coordinator.py`, `custom_components/spectra_ls/sensor.py`, `custom_components/spectra_ls/diagnostics.py`
- Operator docs parity: `docs/wiki/User-Setup-Deploy-and-HA-Integration.md`

Two-track disposition:

- **Track A (runtime):** compatibility-shimmed rollback baseline, no ownership expansion.
- **Track B (component):** active operator remap UX priority lane.

P1/P2/P3 impact check:

- **P1:** unchanged read-only parity contract surfaces.
- **P2:** unchanged registry/router diagnostics ownership.
- **P3:** unchanged single-writer boundary and rollback discipline.

GitHub/developer declaration (policy mirror):

- Legacy runtime path is sealed as rollback-safe compatibility baseline.
- Custom component path is primary for net-new feature/control-plane growth.

### Phase 8 next slice card — P8-S04 (MA-native audio plugin feasibility + fast cutover packet)

Status: **Active (execution packet published)**

Scope:

- **In:**
  - consolidate MA-native extension options into one implementation-ready path,
  - define a bounded Spectra audio-side plugin/provider scaffold plan,
  - publish a fast cutover packet with explicit rollback and evidence controls.
- **Out:**
  - immediate authority flip in this planning slice,
  - cross-domain helper/entity retirement,
  - unbounded runtime ownership expansion.

Primary planning artifact:

- `docs/notes/NOTES-ma-audio-plugin-cutover-plan.md`

Execution artifacts:

- `docs/testing/raw/p8_s04_ma_plugin_cutover_readiness_monitor.jinja`
- `docs/testing/raw/p8_s04_ma_plugin_cutover_readiness_checklist.md`

Activation gates (required):

1. P8-S03 UX usefulness closure accepted (operator-confirmed usable baseline).
2. Legacy rollback baseline remains clean (`authority_mode=legacy`, contract/parity clean).
3. Chosen MA integration route is explicitly mapped as implemented/shimmed/deferred across both tracks.
4. Pre/in/post evidence capture template is defined before any authority-touching implementation.

Two-track disposition target (for execution start):

- **Track A (runtime):** compatibility-shimmed rollback baseline retained during plugin feasibility/probe windows.
- **Track B (component):** implement MA-native audio plugin/provider scaffold and diagnostics-first control-path probes.

P1/P2/P3 impact check:

- **P1:** unchanged read-only parity surfaces.
- **P2:** unchanged registry/router ownership in this planning queue step.
- **P3:** unchanged single-writer boundary; any authority move stays explicitly gated for execution windows.

Reference specification: `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`.

### Documentation parity gate (required)

For architecture/process/contract shifts, keep these synchronized in one change set:

1. `CUSTOM-COMPONENT-ROADMAP.md`
2. `v-next-NOTES.md`
3. `docs/CHANGELOG.md`
4. `README.md` (or explicit no-material-change note)

If any is missing, the slice remains open.

### Retroactive codebase baseline docs (active)

- Runtime architecture/features: `docs/architecture/CODEBASE-RUNTIME-ARCHITECTURE.md`
- Control-hub architecture/features: `docs/architecture/CONTROL-HUB-ARCHITECTURE.md`
- Dead-path cleanup matrix: `docs/cleanup/DEAD-PATHS-CLEANUP.md`

### Plan Delta rule (required)

When execution reality diverges from plan:

- pause slice expansion,
- record a Plan Delta note,
- sync roadmap + v-next statuses,
- resume with revised acceptance criteria.

### Phase 1 Slice-01 (Draft) — First executable scope

- **Goal:** ship read-only shadow parity for routing core surfaces with zero write-path side effects.
- **Legacy surfaces mirrored:**
  - `sensor.ma_active_target`
  - `sensor.ma_active_control_path`
  - `binary_sensor.ma_active_control_capable`
  - `sensor.ma_control_hosts`
- **Track disposition for this slice:**
  - Track A (runtime): implemented/source-of-truth retained
  - Track B (component): read-only shadow parity implementation
- **Close conditions:** parity report captured, mismatch list (if any) documented, and explicit README parity decision recorded in the change set.

## Latest Contract Update (Lighting)

- Lighting room/target menu slider contract updated: while browsing `Lighting Rooms` or `Lighting Targets` lists, moving the lighting slider now applies brightness immediately for the currently highlighted room/target route (no explicit entry into adjust submenu required).

- Lighting adjust labels now use a shared friendly-caption path (`Brightness/Hue/Sat <friendly target>`), replacing legacy `Lighting Values` text and keeping adjust/menu/render labels consistent across lighting screens.

- Boot first-press submenu contract (follow-up): fixed second interception path where auto control-target prompt could still consume first Select when `menu_active=true` during boot/menu-bootstrap. Auto prompt is now dismissed/snoozed without stealing the first submenu entry press; manual prompt path is unchanged.

- OLED text layout fallback contract hardened: when no full-word two-line split fits, fallback now keeps line 1 word-bounded and fits line 2 with ellipsis instead of character-slicing into orphan tails. This prevents labels like `Snail Conditioner` from rendering as `Conditione`/`r`.

- Boot-time first-press submenu determinism: `menu_select_action` now prioritizes non-menu Select entry before auto control-target prompt consumption. If an auto prompt is active at boot, it is dismissed/snoozed when opening menu so first Select reliably enters submenu. Manual prompt mode remains unchanged.

- OLED progress computation now includes a local bootstrap path when HA position timestamp is still unset (`pos_ms==0`) but playback+duration are available, so first-track render after boot/reconnect no longer waits indefinitely for an initial HA position delta event.

- Unified menu directionality path verified by full-stack sign trace: RP2040 emits raw encoder deltas, UART decode preserves sign, and menu direction inversion belongs only in top-level policy. Canonical policy is `menu_encoder_nav_sign: "-1"` (single inversion point) so left-turn no longer maps to downward list movement.

- Menu Select one-press contract hardened: when menu is inactive, a Select press now enters a submenu directly (`Lighting Rooms` from lighting screen, `Gear` from audio screen) instead of consuming an initial press to land on root-level menu state.

- HA position bootstrap correction: `ha_audio_pos_last_ms` now initializes on first received HA position sample, allowing OLED progress gating/projection to engage even when initial feed position is `0` and unchanged.

- OLED now-playing progress hold fix: when HA position samples remain numerically static during active playback, progress projection now advances from the cached displayed position in the same-track window (duration-aligned) so the progress bar continues moving deterministically instead of pinning at 0.

- Audio transport reliability hardening: Arylic TCP send path now performs one immediate retry per payload and only enters failure backoff after repeated consecutive send/connect failures, reducing brittle drops from single transient timeout events during rapid volume movement.

- Audio transport root-cause correction: queued `VOL` dequeue behavior no longer rewrites popped payloads to mutable `recent->last_payload` (which could produce target/TX mismatch during rapid input). Worker now drops superseded queued volume items and preserves payload immutability for transmitted commands.

- Audio transport anti-replay hardening: `components/arylic_tcp.h` now drops stale queued `VOL` payloads older than a bounded queue age (default `900ms`) before transmit and emits explicit per-volume enqueue logs, so delayed volume echoes can be source-attributed deterministically and stale queue replays are prevented.

- Lighting room/target helper surfaces now follow a **catalog-first** contract in HA package logic:
  - Build eligible lights from `states.light` + `area_id(...)`.
  - Resolve room options, target options, target entity mapping, and room state helpers from that shared catalog.
- Catalog payload storage is attribute-backed (`items_json`) with attribute-first readers, so large room/light inventories do not overflow 255-char sensor state limits and collapse into placeholder-only options.
- Eligible catalog population now includes a guarded area-registry fallback (`areas()` + `area_entities()`) when primary `states.light` + `area_id(...)` discovery yields empty, preventing persistent `No Rooms` / `All` bootstrap collapse.
- Catalog/options JSON consumers now trim leading whitespace before JSON-array detection/parsing, preventing newline/space-prefixed valid JSON from being misclassified as non-JSON and collapsing room/target selectors to placeholders.
- Catalog consumers now accept both string JSON arrays and native sequence payloads from `items_json`, preventing parse-path collapse when Home Assistant exposes the attribute as a non-string object at runtime.
- Intent: eliminate drift and intermittent `All`-only target regressions caused by duplicated direct `area_entities(...)` scan logic across multiple templates.

## HA Complex-Object Harvesting Contract (TIGHT + Reusable)

This lighting incident defines a reusable harvesting pattern for all complex HA object flows (audio targets, meta candidates, scenes, devices, future action catalogs).

### Required contract shape

- **State is summary, attribute is payload**

  Sensor `state`: compact count/health marker.
  Attribute payload: structured object/list (authoritative dataset).

- **Dual-type reader compatibility (mandatory)**

  Readers must accept both native sequence/mapping payloads and string JSON payloads (trim + guarded parse).
  Never assume `state_attr(...)` is always a string.

- **Single source catalog, many projections**

  Build one authoritative catalog sensor.
  Derive all helper projections (options, target resolution, status flags) from that single catalog.

- **Bootstrap fallback path**

  Provide a deterministic fallback discovery branch when primary discovery is empty.
  Fallback must preserve schema compatibility.

- **Placeholder policy is explicit**

  Placeholder output (`No Rooms`, `All`, etc.) must be treated as degraded state in diagnostics, not healthy success.

### Apply this to audio harvesting

- `ma_control_targets` / host-route maps / meta candidate lists should follow identical rules:
  - summary in state,
  - authoritative payload in attributes,
  - dual-type readers,
  - single catalog + derived selectors.
- Implementation status: applied to `packages/ma_control_hub/template.inc` and `packages/ma_control_hub/script.inc` room/candidate parse paths so MA host/target/meta routing remains stable across native object and string JSON attribute payload forms.
- Iteration status (2026-04-17): completed full `rooms_raw` reader modernization sweep in `packages/ma_control_hub/template.inc` so all remaining room-map consumers now honor sequence + mapping + guarded string JSON contract uniformly.
- Iteration 2 status (2026-04-17): parser string guards in `packages/ma_control_hub/template.inc` and `packages/ma_control_hub/script.inc` now evaluate sentinel checks using trimmed lowercase payloads (`raw_trim_l`), improving whitespace/case determinism while preserving dual-mode parse semantics.
- Iteration 4 status (2026-04-17): diagnostics-only publish cadence tuning applied in `packages/spectra-ls-diagnostics.yaml` for virtual harness entities (`Virtual Mode Selector Index`, `Virtual Control Class Index`, `Virtual Input Battery Status`) to reduce idle-state log/state churn without altering routing or behavior-path semantics.

### Apply this to other entity domains

- Safe targets: `light`, `media_player`, `scene`, `switch`, `lock`, and future grouped action catalogs.
- Reuse the same parser and projection semantics to avoid per-domain drift.

## Programmable Switch Action Pattern (Toggle + Select Confirm)

For user-programmable actions such as **unlock door**, use a guarded two-step action contract:

- **Arm via toggle/selector**

  Hardware toggle selects an action profile (for example `unlock_door`).
  System enters `armed_action` state with explicit label on OLED.

- **Confirm via Select button**

  Select button executes only when `armed_action` is valid and unexpired.
  Use a short confirmation window (TTL), then auto-disarm.

- **Safety gates (required)**

  Per-action capability flag (`confirm_required`, `sensitive=true`).
  Rate limit/cooldown and idempotence guards.
  Optional long-press requirement for sensitive actions.
  Audit signal emitted to HA (`last_action`, timestamp, actor/source).

- **Harvesting tie-in**

  Programmable actions should be harvested as a typed action catalog (same complex-object contract above), not hardcoded one-off branches.

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
6. **Analog-surface breadth**: beyond audio/lighting depth, the input model supports mappable Home Assistant actions across broader home domains (scenes, scripts, climate flows, safety routines, and other HA-controllable behaviors).

## Product positioning contract (README + roadmap parity)

- Spectra L/S is the analog tactile control surface for Home Assistant.
- Audio and lighting remain the deepest, first-class domains.
- Physical input primitives (buttons/switches/sliders/encoders) are mappable control surfaces for broader HA automation/action execution.
- Documentation parity rule: if this positioning contract changes, update `README.md`, this file, and `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md` in the same change set.

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

### Menu Authoring Contract (Required for new menus)

- **Navigation direction must be centralized**: new menu index movement must use shared helper `components/sls_menu_nav.h` (`normalize_encoder_delta` + `step_index`) and never apply raw encoder deltas directly.
- **Direction is top-level configurable** via substitution `menu_encoder_nav_sign` (default `-1` for intuitive clockwise/right/down progression).
- **Text fitting must be centralized**: new menu labels/headings must use shared helper `components/sls_oled_text_layout.h` (`draw_center_wrapped`, `wrap_two_lines`, `needs_wrap_two_lines`) instead of local wrap/center logic.
- **No per-menu custom direction/wrap forks**: if behavior needs tuning, change shared helpers once so all menu layers inherit consistent UX.

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
