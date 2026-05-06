<!-- Description: Legacy codepath cleanup tracker for runtime/component/ESP retirement tasks during component-first migration. -->
<!-- Version: 2026.05.05.11 -->
<!-- Last updated: 2026-05-05 -->

# Legacy Codepath Cleanup Tracker

## Purpose

Track remaining legacy runtime/ESP/component dependencies so retirement work is explicit, scheduled, and verified instead of lingering as stale compatibility scaffolding.

## Status legend

- `queued`: identified and logged, not yet started
- `active`: implementation in progress
- `blocked`: cannot proceed until listed blocker is cleared
- `validated`: implemented + build/runtime evidence captured
- `retired`: legacy surface removed and no longer consumed

## Active cleanup backlog

| ID | Domain | Legacy dependency | Current consumer(s) | Cleanup action | Exit criteria | Status |
| --- | --- | --- | --- | --- | --- | --- |
| LC-01 | ESP metadata override | `sensor.ma_meta_candidates`, `binary_sensor.ma_meta_low_confidence`, `input_boolean.ma_meta_override_active`, `input_text.ma_meta_override_entity` | `esphome/spectra_ls_system/substitutions.yaml`, `packages/spectra-ls-audio-tcp.yaml` | Add component-native metadata-candidate/override packet surfaces and swap substitutions | ESP compiles + OTA succeeds; metadata override cycle is component-service mediated with helper storage retained as explicit compatibility shim | validated (2026-05-04, phase-1 read-lane + phase-2 write-lane cutover complete; helper entities retained as bounded compatibility storage behind component service contract) |
| LC-02 | ESP control target helper | `input_select.ma_active_target` | `packages/spectra-ls-audio-tcp.yaml`, `packages/spectra-ls-ui.yaml` | Introduce component-active-target writable/selection surface (or controlled proxy service) and migrate consumers | Target refresh/action flows pass with component surface; no direct ESP writes to runtime helper from UI prompt lanes | validated (2026-05-04, phase-2 explicit set_active_target service cutover) |
| LC-03 | ESP control port feed | `sensor.ma_control_port` | `packages/spectra-ls-audio-tcp.yaml`, substitutions | Add component-owned control-port surface fed by route packet and migrate substitution | Build + OTA + route control send tests pass using component port feed; reconnect guard behavior parity maintained | validated (2026-05-03, Slice-BH build+OTA) |
| LC-04 | ESP active friendly label | `sensor.ma_active_friendly` | `packages/spectra-ls-audio-tcp.yaml` | Replace with component-native friendly context surface | Log/status output uses component friendly feed; no runtime friendly dependency remains | validated (2026-05-03, Slice-BG build+OTA) |
| LC-05 | Component internal legacy scaffold constants | `LEGACY_*` resolver/helper constants | `custom_components/spectra_ls/*_fabric.py`, `coordinator.py` | Split constants into `compat_required` vs `retire_candidate`, remove dead legacy-only accesses | No unreachable legacy constants in active path; compatibility-only constants have explicit retirement gate IDs | validated (2026-05-04, Slice-BQ constant governance split + diagnostics exposure; no dead `LEGACY_*` constants detected in active component path inventory) |
| LC-06 | Runtime package retirement staging | `packages/ma_control_hub/*` read/write compatibility surfaces | runtime templates/scripts/automations | Decompose runtime legacy surfaces into explicit retire lanes with contract replacements and parity gates | LC-06 runtime inventory lanes are mapped, each lane has replacement contract + gate + disposition, and non-required lanes are retired or blocked with rationale | active (2026-05-04 decomposition pass; lane execution pending) |
| LC-07 | ESP control-route fallback retirement | `ha_ma_control_hosts_fallback`, `ha_ma_control_host_fallback`, `ha_ma_control_port_fallback` + runtime `sensor.ma_control_*` feeds | `esphome/spectra_ls_system/substitutions.yaml`, `packages/spectra-ls-audio-tcp.yaml`, `packages/spectra-ls-system.yaml` | Remove runtime feed fallbacks and fallback listeners after component route feed stability soak | 14-day reconnect soak with zero fallback-apply logs; component route feeds remain resolved across HA/ESP reconnect cycles; OTA+runtime proof captured | active (2026-05-04 counters/last-applied landed; Slice-BV transport stabilization verified build+OTA+live logs with fallback counts still 0; soak + removal pending) |
| LC-08 | ESP metadata helper passthrough retirement staging | helper-backed metadata override passthrough read-lane | `esphome/spectra_ls_system/substitutions.yaml`, `packages/spectra-ls-audio-tcp.yaml`, `packages/spectra-ls-ui.yaml`, `custom_components/spectra_ls/{sensor.py,binary_sensor.py}` | Replace passthrough read-lane with component-owned metadata override status packet and retire helper passthrough dependency | ESP substitutions consume component metadata override entities; build+OTA+menu regression evidence captured; helper passthrough no longer required by active ESP lane | active (2026-05-04 component status entities + substitution cutover landed; validation/removal pending) |

## ESP legacy rip-out inventory (documented 2026-05-04)

The table below catalogs currently retained ESP compatibility surfaces that are explicitly marked for later retirement once listed gates are met.

| Inventory ID | File | Legacy/compatibility surface | Current behavior | Retirement gate |
| --- | --- | --- | --- | --- |
| ESP-L01 | `esphome/spectra_ls_system/substitutions.yaml` | `ha_ma_control_hosts_fallback: sensor.ma_control_hosts` | Runtime host-list fallback feed remains available when component host-list feed is transiently unresolved | LC-07 |
| ESP-L02 | `esphome/spectra_ls_system/substitutions.yaml` | `ha_ma_control_host_fallback: sensor.ma_control_host` | Runtime single-host fallback feed remains available when component host feed is transiently unresolved | LC-07 |
| ESP-L03 | `esphome/spectra_ls_system/substitutions.yaml` | `ha_ma_control_port_fallback: sensor.ma_control_port` | Runtime control-port fallback feed remains available when component port feed is transiently unresolved | LC-07 |
| ESP-L04 | `esphome/spectra_ls_system/packages/spectra-ls-audio-tcp.yaml` | `text_sensor` listener `id: ma_control_hosts_fallback` | Applies fallback host-list into `arylic_control_hosts` cache only when primary component feed is invalid | LC-07 |
| ESP-L05 | `esphome/spectra_ls_system/packages/spectra-ls-audio-tcp.yaml` | `text_sensor` listener `id: ma_control_host_fallback` | Applies fallback single-host into `arylic_control_host` cache only when primary component feed is invalid | LC-07 |
| ESP-L06 | `esphome/spectra_ls_system/packages/spectra-ls-audio-tcp.yaml` | `text_sensor` listener `id: ma_control_port_fallback` | Applies fallback parsed port into `arylic_control_port` only when primary component feed is invalid | LC-07 |
| ESP-L07 | `esphome/spectra_ls_system/substitutions.yaml` | `ha_ma_meta_override_active: binary_sensor.component_metadata_override_active` | Active metadata override read-lane now component-owned; helper-backed passthrough dependency removed from active ESP substitutions | LC-08 |
| ESP-L08 | `esphome/spectra_ls_system/substitutions.yaml` | `ha_ma_meta_override_entity: sensor.component_metadata_override_entity` | Override entity read-lane now component-owned; helper-backed passthrough dependency removed from active ESP substitutions | LC-08 |
| ESP-L09 | `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` | Legacy `sensor.ma_*` / `input_*ma_*` diagnostics references | Operator templates still include runtime compatibility entities for dual-path troubleshooting | LC-06 + LC-07 + LC-08 (docs/test tooling cleanup after contract retirements) |

## LC-06 runtime package legacy inventory (decomposed 2026-05-04)

CA-S04 wave-1 baseline update (2026-05-05):

- Published deterministic CA-S04 runtime write-lane retirement checklist + one-screen validation template for wave-1 lanes (`LC6-L01`, `LC6-L03`, `LC6-L05`) to keep retirement readiness fail-closed and auditable before lane-disabling edits.
- Runtime lane status remains compatibility-shimmed pending lane-level readiness evidence; component lane status is implemented for authority/readiness evidence publication.

CA-S05 LC-07 fallback-listener soak baseline update (2026-05-05):

- Published deterministic CA-S05 soak checklist + one-screen validator for fallback-listener retirement evidence (`ESP-L04`, `ESP-L05`, `ESP-L06`) with explicit fail-closed blocker taxonomy.
- LC-07 remains active and compatibility-shimmed until clean pre/in/post window packets show zero fallback applies with safe authority/route posture.

CA-S06 LC-06 wave-2 baseline update (2026-05-05):

- Published deterministic CA-S06 wave-2 checklist + one-screen validator for remaining LC-06 runtime tails (`LC6-L01`, `LC6-L03`, `LC6-L06`, `LC6-L02`) with explicit lane-disposition and fail-closed blocker rules.
- LC-06 remains active and compatibility-shimmed until each wave-2 lane is closed as retired, compatibility-shimmed, or deferred-with-rationale under explicit evidence packets.

CA-S07 LC-08 fallback cleanup baseline update (2026-05-05):

- Published deterministic CA-S07 checklist + one-screen validator for legacy diagnostics/template fallback cleanup verification with explicit component-first readiness and fallback-inventory blocker taxonomy.
- LC-08 remains active and compatibility-shimmed until legacy fallback references are fully dispositioned (retired or explicitly deferred with rationale) under explicit evidence packets.

CA-S08 final seal baseline update (2026-05-05):

- Published deterministic CA-S08 closeout checklist + one-screen validator for final `LC-06`/`LC-07`/`LC-08` disposition capture, rollback-safe posture assertion, and closure ledger consistency checks.
- CA-S08 closeout governance posture is validated (closure verdict semantics + two-track packet requirements are now canonical); lane rows for LC-06/LC-07/LC-08 remain explicitly `active` until lane-level retirement/defer decisions are executed under those validated gates.

Slice-CR dormant-by-default active-participation baseline update (2026-05-05):

- Runtime legacy-active control-hub automation/script lanes now require explicit fallback-enable helper state (`input_boolean.ma_control_fallback_enabled`) in addition to non-component authority posture.
- ESP fallback listener apply lanes (`ESP-L04`, `ESP-L05`, `ESP-L06`) now no-op unless the same fallback-enable helper is explicitly enabled.
- LC-06/LC-07/LC-08 remain `active` for retirement governance, but default runtime posture is now component-primary with legacy compatibility lanes dormant unless intentionally opened.

This table breaks `packages/ma_control_hub/*` into concrete retirement lanes so implementation can proceed incrementally with explicit parity gates.

| Lane ID | Runtime surface group | Primary files | Replacement contract target | Gate ID | Disposition |
| --- | --- | --- | --- | --- | --- |
| LC6-L01 | Active-target writer lane (`input_select.ma_active_target` writes + option churn scripts) | `packages/ma_control_hub/script.inc`, `packages/ma_control_hub/automation.inc` | Component target-selection services (`spectra_ls.set_active_target`, `spectra_ls.cycle_active_target`) | LC-06A | compatibility-shimmed (authority-gated today; full runtime writer retirement pending) |
| LC6-L02 | Override-flag writer lane (`input_boolean.ma_override_active` lifecycle) | `packages/ma_control_hub/script.inc`, `packages/ma_control_hub/input_boolean.inc` | Component authority/selection policy state packet | LC-06B | deferred with rationale (still used for bounded legacy mode + rollback semantics) |
| LC6-L03 | Metadata override helper storage (`input_boolean.ma_meta_override_active`, `input_text.ma_meta_override_entity`) | `packages/ma_control_hub/template.inc`, `packages/ma_control_hub/input_boolean.inc`, `packages/ma_control_hub/input_text.inc` | Component metadata override status packet + service telemetry | LC-06C / LC-08 | compatibility-shimmed (service-mediated writes landed; helper storage still consumed by runtime templates) |
| LC6-L04 | Provider telemetry helper sink (`input_text.ma_metadata_provider_last_*`) | `packages/ma_control_hub/script.inc`, `packages/ma_control_hub/input_text.inc` | Component diagnostics/write-attempt packet fields | LC-06D | validated (2026-05-04 Slice-BX: runtime provider dispatch now publishes telemetry through component service `spectra_ls.set_metadata_provider_packet`; runtime helper sink retained as fallback-only path when component sink is unavailable) |
| LC6-L05 | Server-profile + API URL helper stack (`input_select.ma_server_profile`, `input_text.ma_server_url*`, `sensor.ma_api_url`, rest/rest_command) | `packages/ma_control_hub/template.inc`, `rest.inc`, `rest_command.inc`, `input_select.inc`, `input_text.inc` | Component options/config-entry endpoint contract | LC-06E | active (2026-05-04 Slice-BY phase-1 bridge complete; 2026-05-05 Slice-CA phase-2 consumer cutover moved diagnostics/operator consumers to component-first; 2026-05-05 Slice-CT tightened runtime REST consumers (`rest.inc`, `rest_command.inc`) to component-first `sensor.component_ma_api_url` with bounded `sensor.ma_api_url` fallback; 2026-05-05 Slice-CU bridged remaining template/read lanes by making `sensor.ma_server_profile_effective` component-first with bounded helper fallback and updating full-stack validator backend/API read-lane checks) |
| LC6-L06 | Runtime metadata resolver read surfaces (`sensor.ma_meta_*`, resolver templates used by diagnostics/devtools) | `packages/ma_control_hub/template.inc`, `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` | Component metadata packet family (`sensor.component_*` / diagnostics packet) | LC-06F | deferred with rationale (2026-05-05 Slice-CI..CO override-focused consumers closed as component-first with bounded fallback; remaining non-override resolver tails await broader component packet-family parity expansion and are explicitly bounded compatibility/deferred lanes) |

### LC-06 execution order (current recommendation)

1. **LC6-L04** provider telemetry helper sink (lowest user-facing risk).
2. **LC6-L05** server-profile/API helper stack (requires options migration parity evidence).
3. **LC6-L06** runtime metadata resolver read surfaces (coordinate with devtools template updates).
4. **LC6-L01** remaining active-target writer remnants (after LC-07 stability soak).
5. **LC6-L03** metadata override helper storage (in lock-step with LC-08 packet cutover).
6. **LC6-L02** override-flag writer lane (final retirement once rollback policy is revised).

## Current blockers and prerequisites

1. LC-01/LC-02 now run through component-service mediated write lanes; helper entities remain bounded compatibility storage surfaces until explicit retirement gates are opened.
2. Control-port lane now uses component contract for linkplay path; future non-linkplay path expansion should add explicit per-path port semantics before declaring cross-path retirement complete.
3. ESP fallback listeners are intentionally retained until component host/port feed resilience is proven across reconnect windows; fallback-hit telemetry (`esp_control_fallback_*`) is now available and must show sustained non-use before LC-07 removal.
4. LC-06 runtime package retirement is now decomposed into lanes, but several lanes remain intentionally compatibility-shimmed until LC-07/LC-08 gates and rollback policy decisions are completed.

## Verification requirements for each retirement task

- Changelog entry added **before** behavior edits.
- Build gate: `bin/esphome_spectra_build_local.sh` succeeds.
- Deployment gate: OTA upload succeeds with `INFO OTA successful`.
- Two-track disposition documented (`runtime` + `component`) in changelog and roadmap ledgers.
- If retirement deferred: blocker and rationale must be updated in this tracker.

## LC-07 soak checkpoints

- 2026-05-04 (Slice-BV post-deploy checkpoint #1):
  - Build: success (`ESPHome 2026.4.3`, config hash `0x80e01b19`, compiled `2026-05-04 06:44:23 -0700`).
  - OTA: success (`INFO OTA successful`) to `192.168.10.40`.
  - Runtime evidence sample:
    - `ESP Control Handoff Status => ready`
    - `ESP Control Fallback Apply Count => 0`
    - `ESP Control Hosts/Host/Port Fallback Count => 0/0/0`
    - HTTP connect-reset still present on host `192.168.10.50`, but sustained unknown-transport failures now escalate to max backoff (`backoff 120000ms, fail=3`) instead of rapid retry churn.
  - Disposition: soak remains active; no fallback listener retirement yet.
