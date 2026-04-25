<!-- Description: Retroactive architecture and feature documentation for the MA control hub package split. -->
<!-- Version: 2026.04.25.2 -->
<!-- Last updated: 2026-04-25 -->

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
- `command_line.inc`
- `script.inc`
- `automation.inc`
- `template.inc`

Guardrail script: `.github/validate-ma-control-hub-layout.sh`

## Domain breakdown

### 1) Helper contract domain

Defined by `input_*.inc` fragments:

- target selector (`input_select.ma_active_target`)
- manual/override/fallback booleans
- confidence/staleness/timing numeric tunables
- install-local endpoint and mapping text helpers

### 2) MA API ingestion domain

Defined by `rest.inc` + `rest_command.inc`:

- `players/all` polling surface (`sensor.ma_players`)
- active player request surface (`sensor.ma_active_player`)
- generic MA API POST wrapper (`rest_command.ma_api_command`)

Defined by `command_line.inc`:

- pywiim discovery feed (`sensor.ma_pywiim_discovery`) using `wiim-discover --output json` contract with local script fallback (`/config/bin/pywiim_discover_targets.py`)
- normalized device payload (`name`, `model`, `firmware`, `ip`, `mac`, `uuid`) for target-option enrichment
- discovery normalization gate drops non-usable rows before publication (`ip` missing and explicit `validated=false` records)

### 3) Orchestration script domain

Defined by `script.inc`:

- target option synthesis (`ma_update_target_options`)
  - blacklist helper `input_text.ma_discovery_blacklist_hosts` (CSV host deny list) excludes matching IP-backed candidates from both pywiim and MA fallback discovery lanes
  - primary discovery enrichment from pywiim device feed mapped to HA media_player entities by IP
  - fallback discovery enrichment from `sensor.ma_players` heuristic contract
- target cycling (`ma_cycle_target`)
- auto-selection policy (`ma_auto_select`)
- explicit read-only lock for write helpers:
  - `ma_set_volume` -> disabled
  - `ma_set_balance` -> disabled

### 4) Automation lifecycle domain

Defined by `automation.inc`:

- startup option refresh and auto-select
  - target-option refresh now also reacts to pywiim discovery sensor updates
- continuous auto-select loop (with guard conditions)
- last-valid target persistence
- ambiguity lock + stale-unlock handling
- startup restore of last-valid target
- user feedback notification path for host capability degradation (`binary_sensor.ma_no_control_capable_hosts` -> persistent notification create/dismiss)

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

## Parser contract (critical)

`ma_control_hub` uses a dual-mode parser contract for complex attributes:

1. accept native sequence payloads,
2. accept native mapping payloads with `rooms`/`result` extraction,
3. parse string JSON only when trimmed payload starts with `[` or `{` and is not `unknown/unavailable/none/''`.

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
  - discovery candidates are sourced first from pywiim-validated network discovery, then MA players fallback
- classify active target route (`pywiim` vs `other`) and control capability
- resolve now-playing title/artist/album/source/state with fallback ordering
- expose host(s)/port contracts for ESPHome TCP control
- surface ambiguity/confidence/staleness for prompt gating

## Known constraints

- `ma_set_volume` and `ma_set_balance` are intentionally disabled (read-only write path policy).
- Route support is currently practical for `pywiim`; other routes are classified but not direct-routed by runtime.
- Legacy helper names are still part of active runtime contract.

## Component migration interaction contract (P3-S01)

During guarded migration trials, the custom component may attempt routing writes to
`input_select.ma_active_target` only when explicit authority mode is set to `component`.

Implemented guard controls in `custom_components/spectra_ls` include:

- single-writer authority mode (`legacy` default, `component` opt-in),
- guarded manual route-write trial path (no broad autonomous write loop),
- debounce and reentrancy protections,
- route-decision eligibility gate (`route_linkplay_tcp` only in P3-S01),
- correlation-id and last-attempt diagnostics (`write_controls`).

Compatibility posture:

- legacy control-hub remains source-of-truth by default,
- component write behavior is explicitly opt-in and reversible,
- metadata/selection broader ownership remains deferred to later P3 slices.

## Change discipline for future slices

When editing `ma_control_hub` behavior, update this document with:

1. changed domain(s) above,
2. parser contract impact (if any),
3. new/removed exported helper/sensor contracts,
4. compatibility note for ESPHome runtime consumers.
