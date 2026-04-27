<!-- Description: Retroactive architecture and feature documentation for the MA control hub package split. -->
<!-- Version: 2026.04.27.50 -->
<!-- Last updated: 2026-04-27 -->

# MA Control Hub Architecture (Retroactive Baseline)

## Purpose

Document the active behavior and contracts of `packages/ma_control_hub.yaml` and split fragments under `packages/ma_control_hub/`.

Aggregate package entrypoint: `packages/ma_control_hub.yaml`

## Active include graph

- `input_select.inc`
- `input_boolean.inc`
- `input_number.inc`
- `input_text.inc`
- `rest.inc`
- `rest_command.inc`
- `script.inc`
- `automation.inc`
- `template.inc`

Guardrail script: `.github/validate-ma-control-hub-layout.sh`

## Domain breakdown

### 1) Helper contract domain

Defined by `input_*.inc` fragments:

- target selector (`input_select.ma_active_target`)
- MA backend profile selector (`input_select.ma_server_profile`: `beta` / `stable` / `manual`)
- manual/override/fallback booleans
- confidence/staleness/timing numeric tunables
- install-local endpoint and mapping text helpers
- MA backend profile URL helpers (`input_text.ma_server_url_beta`, `input_text.ma_server_url_stable`, `input_text.ma_server_url`)

### 2) MA API ingestion domain

Defined by `rest.inc` + `rest_command.inc`:

- `players/all` polling surface (`sensor.ma_players`)
- active player request surface (`sensor.ma_active_player`)
- generic MA API POST wrapper (`rest_command.ma_api_command`)
- profile-aware MA API URL surface (`sensor.ma_api_url`) with active profile visibility (`sensor.ma_server_profile_effective`)
- command-shape compatibility note: avoid unsupported MA command aliases in REST sensors (for example `players/get_active`); use supported command shapes and template-side selection/parsing.

### 3) Orchestration script domain

Defined by `script.inc`:

- target option synthesis (`ma_update_target_options`)
- target option synthesis now includes a live fallback discovery pass over `media_player.*` entities when MA player feeds are sparse, admitting only IP-backed control-hinted targets (`control_capable=true`, `control_path=linkplay_tcp`, or supported LinkPlay/WiiM-class identity hints) to preserve discovery-first routing without hardcoded install IDs
- target cycling (`ma_cycle_target`)
- auto-selection policy (`ma_auto_select`)
- explicit read-only lock for write helpers:
  - `ma_set_volume` -> disabled
  - `ma_set_balance` -> disabled

### 4) Automation lifecycle domain

Defined by `automation.inc`:

- startup option refresh and auto-select
- continuous auto-select loop (with guard conditions)
- last-valid target persistence
- ambiguity lock + stale-unlock handling
- startup restore of last-valid target
- event-driven handoff acceleration triggers for target-options/auto-select on detected receiver and now-playing entity changes (legacy authority lane)
- user feedback notification path for host capability degradation (`binary_sensor.ma_no_control_capable_hosts` -> persistent notification create/dismiss)
- pre-notification self-heal for host-capability degradation (`script.ma_update_target_options` + `script.ma_auto_select`) before warning emission

### 5) Template computation domain

Defined by `template.inc`:

- room payload normalization (`sensor.spectra_ls_rooms_json`)
- MA/HA candidate scoring and selection (`ma_meta_candidates`, `ma_meta_resolver`)
- now-playing entity and resolved fields
- explicit playback-state derivation (`playing/paused/stopped/idle/...`) that prioritizes authoritative state over metadata recency/title presence
- stale-hold prevention guards: resolver winner eligibility now requires active-or-recent playback evidence, and preferred-meta fallback no longer promotes based on metadata presence alone
- paused stale suppression: paused candidates without recent progress evidence are excluded from active metadata winner eligibility to prevent stale-title promotion
- mapped-meta freshness guard: room-mapped meta fallbacks must meet the same active/recent criteria before they can override target metadata selection
- component gate visibility: metadata-prep diagnostics include explicit gate scoring and blocking reasons for authority/freshness failures
- active control path/capability/host derivation
- ambiguity/staleness/confidence binary surfaces
- friendly labels and helper projection sensors
- ESP-facing handoff note: on active-target changes, ESP requests immediate HA recompute for control-target/host surfaces (`sensor.ma_control_targets`, `sensor.ma_control_hosts`, `sensor.ma_control_host`) to reduce host handoff latency, but forced recompute is reconnect-safe gated (HA API reconnect grace window + template-feed readiness checks) to avoid HA reboot startup assertion races.
- ESP exported handoff telemetry: ESP now publishes HA-visible diagnostics sensors for handoff status, resolved control target, and OLED/UI status (`sensor.spectra_ls_system_esp_control_handoff_status`, `sensor.spectra_ls_system_esp_control_target`, `sensor.spectra_ls_system_esp_oled_status`) for deterministic operator validation.

## Parser contract (critical)

`ma_control_hub` uses a dual-mode parser contract for complex attributes:

1. accept native sequence payloads,
2. accept native mapping payloads with `rooms`/`result` extraction,
3. parse string JSON only when trimmed payload starts with `[` or `{` and is not `unknown/unavailable/none/''`.

`script.ma_update_target_options` explicitly follows this same string-mode rule for both array and object payloads (object payloads extract `rooms`/`result`) to avoid accidental target-option collapse during room-contract shape drift.

This contract is required across readers of:

- room maps,
- candidate JSON payloads,
- derived summary payloads.

## External dependencies consumed

- `sensor.spectra_ls_rooms_raw` (`rooms` attribute)
- media_player entity attributes/state
- labels (`no-spectra`, `no_spectra`)
- optional Plex allowlist helpers (`input_text.plex_allowed_users`, `input_text.plex_allowed_players`)
- MA token + URL helpers

## Feature responsibilities

- choose active control target from known + discovered + valid candidates
- classify active target route (`linkplay_tcp` vs `other`) and control capability
- resolve now-playing title/artist/album/source/state with fallback ordering
- expose host(s)/port contracts for ESPHome TCP control
- surface ambiguity/confidence/staleness for prompt gating

## Known constraints

- `ma_set_volume` and `ma_set_balance` are intentionally disabled (read-only write path policy).
- Route support is currently practical for `linkplay_tcp`; other routes are classified but not direct-routed by runtime.
- Legacy helper names are still part of active runtime contract.
- Discovery-first control-host contract is fail-closed: runtime must not rely on install-specific bootstrap IP defaults for control hosts, and control sends stay blocked until `sensor.ma_control_hosts` / `sensor.ma_control_host` provide valid resolved values.
- `ma_update_target_options` is now resilient to temporary `sensor.ma_players.result` sparsity by adding a bounded live `media_player.*` fallback source; this source is intentionally filtered to IP-backed, control-hinted targets only to avoid broad unsupported-target promotion.
- Host resolution should come from live HA entity discovery (for example `media_player.<target>.ip_address` on WiiM/LinkPlay-class targets) before any manual override paths are considered.
- Host recovery for target-bound rooms is deadlock-safe: active-target host resolution does not depend on downstream classifier outputs (`control_path` / `control_capable`), and room contracts may fall back to the mapped `meta` entity `ip_address` when the selected target entity is a wrapper/group entity without direct `ip_address`.
- When room-target matching is unresolved for wrapper targets, host recovery may use active MA player mapping (`sensor.ma_active_player_id_resolved.player_json.entity_id`) to resolve host by discovered `ip_address` while preserving fail-closed/no-static-bootstrap posture.
- Host recovery also includes room `meta` entity fallback (`meta.ip_address`) and meta-group member IP fallback (`meta.group_members` / `meta.members`) when wrapper entities expose no direct `ip_address`.
- Wrapper-target alias recovery includes direct entity alias probing by receiver/meta/now-playing/player entities and friendly-name-matched `media_player` entities with `ip_address` (including member fallback) before static `tcp_host` fallback.
- `binary_sensor.ma_no_control_capable_hosts` is intentionally contract-readiness gated (MA players + control-target surfaces must be resolved) and ambiguity-suppressed, to avoid startup/transient false alarm churn while preserving actionable persistent degradation warnings.
- `binary_sensor.ma_no_control_capable_hosts` also requires explicit control-expected signals for the active target (direct/member `ip_address` or room contract host/capability hint) before raising degradation; metadata-only/non-control-expected active targets now report `target_not_control_expected` instead of noisy host-capability alarms.

## Component migration interaction contract (P3-S01)

During guarded migration trials, the custom component may attempt routing writes to
`input_select.ma_active_target` only when explicit authority mode is set to `component`.

Implemented guard controls in `custom_components/spectra_ls` include:

- single-writer authority mode (`legacy` default, `component` opt-in),
- guarded manual route-write trial path (no broad autonomous write loop),
- debounce and reentrancy protections,
- route-decision eligibility gate (`route_linkplay_tcp` only in P3-S01),
- explicit route-safety diagnostics (`route_safety_validation`) that verify selected route target matches active target and host resolution remains fail-closed,
- explicit shadow-attribute exposure of `route_safety_validation` on `sensor.shadow_active_target` so Developer Tools templates can consume route-safety verdicts directly without reconstructing from `route_trace`,
- correlation-id and last-attempt diagnostics (`write_controls`).

Compatibility posture:

- legacy control-hub remains source-of-truth by default,
- component write behavior is explicitly opt-in and reversible,
- metadata/selection broader ownership remains deferred to later P3 slices.

## Pluggable host-resolution feed contract (scheduler-facing)

To support deterministic scheduling without hardcoding a single device family, the custom component registry now emits host resolution through host-type modules:

- `wiim` -> `hostmods.wiim`
- `linkplay_tcp` -> `hostmods.linkplay_tcp`
- `generic` -> `hostmods.generic`

Each registry entry now carries scheduler-facing host-resolution metadata:

- `host_type`
- `resolver_module`
- `host_resolution`:
  - selected `host`
  - selected `reason` (source path)
  - ordered `candidates` list (`source`, `host`, `resolved`)

Each registry entry also carries profile inputs for scheduler decisions:

- `feature_profile` (runtime snapshot profile):
  - `integration_domain`
  - `supported_features`
  - `observed_capabilities`
  - `manufacturer` / `model` / `via_device`
  - `availability_quality` + freshness fields (`state_age_s`, `position_age_s`)
- `empirical_profile` (optional overlay from DB-fed payload)
- `scheduler_profile` (normalized scheduler-ready summary)

Empirical data ingestion hook:

- optional source entity: `sensor.spectra_ls_feature_profile_db`
- expected payload: attribute `profiles_json` with target-keyed metrics/contracts
- overlay presence is explicit in snapshot summary (`empirical_profiled_targets_count`)

Diagnostics visibility:

- sensor `sensor.spectra_ls_host_resolution_status` exposes aggregate module counts, per-target host-resolution traces, and unresolved source hints.
- same sensor now also exposes profile coverage counts and per-target feature/empirical/scheduler profiles.

Compatibility note:

- runtime (`packages/ma_control_hub`) host logic remains authoritative for current control-path execution;
- component pluggable host-module outputs are currently additive scheduler-feed diagnostics/normalization surfaces.

## Scheduler decision engine contract (component)

The component now provides a deterministic scheduler decision layer that ranks targets using:

- resolved host module outputs (`host`, `host_type`, `resolver_module`),
- runtime feature profile signals (`availability_quality`, `observed_capabilities`, integration identity),
- optional empirical overlay metrics (`empirical_profile`),
- policy inputs (`require_control_capable`, `prefer_fresh`, `max_results`, `target_hint`).

Service surfaces:

- `spectra_ls.validate_scheduler`
- `spectra_ls.run_scheduler_choice`
- `spectra_ls.apply_scheduler_choice` (guarded helper-apply path)
- `spectra_ls.build_target_options_scaffold` (component-native target-options planning/apply scaffold)
- `spectra_ls.run_auto_select_scaffold` (component-native auto-select planning/apply scaffold)
- `spectra_ls.run_metadata_resolver_scaffold` (component-native metadata resolver planning/apply scaffold)
- `spectra_ls.run_metadata_trial_bridge_scaffold` (resolver-authority gated metadata bridge sequencing)
- `spectra_ls.cycle_active_target` (component-native parity path for legacy `ma_cycle_target` behavior)
- component-parity feedback lifecycle for host-capability degradation is available under guarded component-authority windows (30s hold -> one-shot self-heal -> 10s recheck -> persistent notification create/dismiss using `spectra_ls_no_control_capable_hosts`)
- MA-player-change parity sequencing is additive in component authority windows: target-options scaffold refresh runs before auto-select loop, and target option candidate synthesis now consumes capability-aware registry/profile signals (control-capable + host-resolved + supported path + availability quality) without replacing existing discovery feeds
- component state-change trigger parity now includes detected receiver + now-playing entity transitions in the same players-change refresh sequencing path (`target-options` scaffold refresh -> guarded auto-select), matching runtime handoff acceleration intent during migration windows.
- `spectra_ls.restore_last_valid_target` (component-native parity path for legacy startup/repair restore behavior)
- `spectra_ls.track_last_valid_target` (component-native parity path for legacy last-valid persistence behavior)

Diagnostics surfaces:

- `scheduler_validation` snapshot payload (readiness/checks/default decision)
- `write_controls.scheduler_last_decision` payload (last run status + ranked candidates)
- `write_controls.scheduler_last_apply` payload (last apply attempt status/reason/target/guards)
- `write_controls.target_options_last_attempt` payload (last options-scaffold attempt)
- `write_controls.auto_select_last_attempt` payload (last auto-select-scaffold attempt)
- `write_controls.metadata_resolver_last_attempt` payload (last metadata-resolver scaffold attempt)
- `write_controls.metadata_bridge_last_attempt` payload (last resolver/trial bridge sequence attempt)
- `write_controls.cycle_target_last_attempt` payload (last component cycle-target attempt)
- `write_controls.restore_last_valid_last_attempt` payload (last restore-last-valid attempt)
- `write_controls.track_last_valid_last_attempt` payload (last last-valid tracking attempt)
- `sensor.spectra_ls_scheduler_decision_status` convenience sensor
- `handoff_inventory` payload (legacy-only dependency map + component scaffold status)

Metadata bridge alignment note:

- metadata trial contract remains legacy-authority gated (`authority_mode=legacy` required),
- resolver scaffold stages are component-authority gated,
- bridge sequencing explicitly handles this authority transition and records stage statuses/blockers so migration runs are deterministic and reversible.
- bridge sequencing now includes an automatic pre-bridge target recovery stage (`run_auto_select_scaffold` with options sync enabled) so stale/non-control-capable active targets are recovered to a control-capable candidate without manual helper-option editing before resolver/trial checks.
- component target-options scaffolding is now parity-expanded with legacy option-synthesis behavior: options planning pulls from room contracts, MA players payload, live IP-backed `media_player.*` discovery with LinkPlay/WiiM-class hints, detected receiver candidate, and helper current/last-valid context (instead of registry-only candidates).
- component target-options apply now includes default-option recovery semantics so invalid/not-in-options helper current state is corrected to a computed fallback (`current valid` -> `last-valid` -> `first selectable` -> `none`) in the same apply path.
- component auto-select scaffold planning now prefers a ready detected receiver candidate first, then active playable helper options, before generic candidate fallback for closer legacy behavioral parity during migration windows.
- scaffold debounce guards now skip dry-run executions for target-options/auto-select/metadata-resolver scaffolds, so back-to-back dry-run validation and bridge preflight sequences remain deterministic without weakening non-dry-run write safeguards.
- metadata bridge internal target-recovery sequencing now applies an explicit in-sequence override for the bridge-owned auto-select recovery stage so same-transaction debounce timing from earlier attempts cannot prematurely fail bridge orchestration as `blocked_target_recovery_stage`.
- metadata bridge validation now infers trial-stage success from `bridge_completed` context when trial-stage status payloads are transiently unresolved (`unknown`/missing), preventing contradictory diagnostics states where completed bridge execution is still flagged as `trial_stage_not_ok`.
- scheduler/metadata validation authority-policy checks now treat supported authority modes (`legacy`, `component`) as diagnostics-valid posture for bounded migration runs, while metadata trial execution remains legacy-gated at execution time; completed bridge context satisfies trial-authority validation even when authority is restored to component after bridge sequencing.
- on integration startup, the component now schedules a bounded automatic bridge-recovery sequence (delayed initial attempt + retries) so HA restarts can self-recover helper target/options alignment and control-capable target selection without requiring manual scaffold action calls.
- startup recovery is MA boot-gated and reports explicit wait-state messaging (`waiting_for_ma_boot` / "waiting for Music Assistant boot readiness") while MA/control-target surfaces are still initializing, using operator-friendly reason text (for example player-list/control-target readiness) instead of internal token strings or premature recovery-error style messaging.
- scheduler and bridge validation payloads now mirror this boot-gate posture: when MA boot-readiness is not yet satisfied, diagnostics classify the state as explicit wait (`waiting_for_ma_boot`) with operator-friendly reason text instead of hard failure classification for transient pre-boot gaps.
- startup bridge sequencing now restores write authority to the pre-run mode on all exit paths (including blocked target-recovery stages), preventing stale `component` authority residue after failed startup attempts.
- startup recovery now has an explicit legacy no-mix guard: when authority is `legacy`, component bridge sequencing is skipped (`skipped_legacy_authority`) so startup does not perform component-owned helper mutations in legacy single-writer windows.
- startup recovery now also has a component no-mix guard: when authority is `component`, startup executes component-only options/auto-select recovery and skips legacy-trial bridge transitions (`skipped_component_startup_no_mix`) to avoid cross-authority boot sequencing.
- startup boot-readiness gating now requires resolved control-host surface and initialized active-target helper options (at least one non-`none` option) in addition to MA players/control-target readiness, reducing premature bridge-attempt exhaustion during reboot churn.
- startup boot-readiness gating is additionally hardened for host-surface lag: unresolved `sensor.ma_control_hosts` by itself no longer keeps startup in perpetual MA-boot wait when MA players/control-targets and helper options are otherwise ready.
- startup auto-select recovery now supports a guarded helper-current fallback (`input_select.ma_active_target` resolved and present in options) when candidate scaffolds are temporarily empty, preventing avoidable `blocked_no_candidate` bridge-stage failures during reboot churn.
- startup wait messaging now distinguishes phases: true MA gates (`ma_players` / control-target catalog) use “waiting for Music Assistant boot readiness,” while post-boot helper/options readiness waits use control-contract wording to avoid false “MA is not booted” interpretation.
- shadow diagnostic sensor payloads are recorder-size hardened: high-volume attributes are trimmed from generic shadow entities and concentrated to the primary active-target diagnostics surface (with bulky catalogs omitted) to avoid Recorder attribute-drop warnings and preserve persisted diagnostics visibility.
- contract validation now treats host-feed surfaces (`sensor.ma_control_hosts`, `sensor.ma_control_host`) as soft-required warnings rather than hard-invalid gates, so transient fail-closed host clears do not force global `contract_invalid` cascades while still surfacing host-quality risk explicitly.
- scheduler decision now includes a guarded helper-current fallback when ranked candidates are empty, allowing a resolved `input_select.ma_active_target` value (present in helper options) to be reused as deterministic selected target instead of emitting a false `no_scheduler_candidate` during transient profile/host freshness churn.
- helper-current scheduler fallback now requires registry-backed control capability and resolved host (`control_capable=true` + non-empty host) before promotion; otherwise decision remains `no_candidate` with explicit fallback-rejection reason to avoid false control-capable assumptions for AppleTV-like/non-TCP targets.
- when authority is `legacy`, scheduler decision output is explicitly pinned to helper-current target (when helper state is resolved and in-options) so diagnostics and blocker classification remain ownership-consistent during boot/startup churn.
- deterministic scheduler validation template now falls back to coordinator `scheduler_validation.default_decision` when `scheduler_last_decision` is `never_attempted`, preventing stale `selected_target=none` / `candidate_count=0` displays in otherwise PASS-ready snapshots.
- deterministic scheduler validation template additionally falls back to helper-current selection (when scheduler readiness is PASS and helper current is valid/in-options) to keep displayed decision fields truthful even when shadow-entity decision payload attributes are stale or partially absent.
- deterministic scheduler validation template now includes a dedicated hotspot-triage section (decision-source provenance, shadow-source selection rationale, route decision, registry coverage, contract hard/soft warning surfaces, metadata-prep blockers, and top-candidate score context) to reduce multi-template debugging loops during reboot/post-boot churn.
- registry snapshot seeding is now hardened with helper/active-target fallback inputs (`input_select.ma_active_target` options/current + active-target state) and broader rooms payload parsing fallbacks (`rooms_raw`/`rooms_json` state+attribute variants), reducing empty-registry diagnostic churn during transient legacy-feed lag.
- route defer classification ordering now prefers `defer_not_capable` before `defer_unsupported_path` when selected targets lack control capability, improving operator signal quality for host-resolution gaps.
- bridge validation now infers metadata-trial stage status from bridge-attempt stage telemetry (`stages.metadata_trial.status`) when global `metadata_trial_last_attempt` still reports `never_attempted`, reducing false bridge WARN persistence after successful bridge dry-run sequencing.
- registry snapshot build path now reuses first-hit room mappings per target (instead of rescanning full rooms list per target), reducing avoidable refresh overhead during frequent coordinator snapshots.
- metadata-prep readiness now treats title availability as a signal gate (`now_playing_title_signal_ready`) rather than a strict raw-title requirement: unresolved `now_playing_title` can still classify as ready when fresh-play evidence and resolved active-meta context are present, reducing false WARN loops during transient metadata lag.
- metadata-candidate readiness now includes a resolver fallback (`ma_meta_resolver.best_entity` + positive score) when `ma_meta_candidates` payload shape is delayed, and handoff inventory maturity status (`target_options_builder`, `auto_select_pipeline`, `metadata_resolver_authority`) now advances to `implemented` based on successful guarded scaffold attempts instead of static scaffold-plan presence only.
- component selection-ownership migration now includes executable parity services for cycle/restore/track last-valid target flows, and active-target helper state changes trigger bounded component-mode last-valid tracking (`state_change_listener`) to reduce reliance on runtime-only lifecycle automations during migration windows.
- component selection-ownership migration now also mirrors legacy lock lifecycle behaviors in component-authority windows: lock-on-ambiguous-select parity, stale-meta unlock parity with 5-second hold behavior, and guarded component auto-select loop triggering on legacy-equivalent state transitions (`ma_players`, active-target helper, and watched target state changes).
- auto-select loop parity watcher semantics are now aligned to legacy options-membership behavior (full non-empty helper options set); the prior `media_player.*`-only watcher filter was removed as an unnecessary restriction.

Guarded apply semantics (`apply_scheduler_choice`):

- requires `authority_mode=component`,
- enforces write reentrancy + debounce safeguards unless `force=true`,
- verifies target helper presence and option-membership contract before write,
- supports `dry_run` for deterministic preflight without helper mutation,
- records full attempt/audit payload for operator triage.

Current parity status:

- legacy/runtime path is **compatibility-shimmed** for scheduler behavior (no legacy scheduler implementation in this slice),
- component path is **implemented** for scheduler decision computation and diagnostics.

## Change discipline for future slices

When editing `ma_control_hub` behavior, update this document with:

1. changed domain(s) above,
2. parser contract impact (if any),
3. new/removed exported helper/sensor contracts,
4. compatibility note for ESPHome runtime consumers.
