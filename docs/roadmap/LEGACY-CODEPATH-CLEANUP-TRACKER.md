<!-- Description: Legacy codepath cleanup tracker for runtime/component/ESP retirement tasks during component-first migration. -->
<!-- Version: 2026.05.04.4 -->
<!-- Last updated: 2026-05-04 -->

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
| LC-06 | Runtime package retirement staging | `packages/ma_control_hub/*` read/write compatibility surfaces | runtime templates/scripts/automations | Mark each retained runtime surface with `retire_after` gate and replacement component entity/service | Tracker rows exist for each retained runtime contract; all non-required surfaces either retired or explicitly blocked | queued |

## Current blockers and prerequisites

1. LC-01/LC-02 now run through component-service mediated write lanes; helper entities remain bounded compatibility storage surfaces until explicit retirement gates are opened.
2. Control-port lane now uses component contract for linkplay path; future non-linkplay path expansion should add explicit per-path port semantics before declaring cross-path retirement complete.

## Verification requirements for each retirement task

- Changelog entry added **before** behavior edits.
- Build gate: `bin/esphome_spectra_build_local.sh` succeeds.
- Deployment gate: OTA upload succeeds with `INFO OTA successful`.
- Two-track disposition documented (`runtime` + `component`) in changelog and roadmap ledgers.
- If retirement deferred: blocker and rationale must be updated in this tracker.
