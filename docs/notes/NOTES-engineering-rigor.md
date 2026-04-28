<!-- Description: Engineering rigor baseline for custom-component migration decisions, contract inventory, and explicit tough-spot tracking. -->
<!-- Version: 2026.04.27.1 -->
<!-- Last updated: 2026-04-27 -->

# NOTES — Engineering Rigor Baseline

## Intent (non-negotiable)

- No cowboy changes.
- No assumptions presented as fact.
- No install-specific hardcodes in tracked product logic.
- Discovery-first + capability-mapped behavior by default.
- If evidence is incomplete, say exactly what is missing and block risky progression.

## Evidence boundary (explicit)

This note is based on repository-contract inventory and documented diagnostics.
Live HA runtime state can differ at any moment due to startup timing, integration reload order, or transient unavailable entities.

Required to close this gap before write-path changes:

1. fresh runtime parity template output,
2. fresh route-trace + contract-validation output,
3. explicit comparison against legacy source-of-truth surfaces.

## Current contract inventory baseline (ma_control_hub + spectra_ls)

Control-hub `.inc` files inventoried:

- `packages/ma_control_hub/input_select.inc`
- `packages/ma_control_hub/input_boolean.inc`
- `packages/ma_control_hub/input_number.inc`
- `packages/ma_control_hub/input_text.inc`
- `packages/ma_control_hub/rest.inc`
- `packages/ma_control_hub/rest_command.inc`
- `packages/ma_control_hub/script.inc`
- `packages/ma_control_hub/automation.inc`
- `packages/ma_control_hub/template.inc`

Component legacy surface mapping baseline:

- `sensor.ma_active_target`
- `sensor.ma_active_control_path`
- `binary_sensor.ma_active_control_capable`
- `sensor.ma_control_hosts`
- `sensor.ma_control_host`
- `sensor.ma_control_targets`
- `sensor.spectra_ls_rooms_json`
- `sensor.spectra_ls_rooms_raw`

Static contract inventory snapshot:

- Distinct referenced entity/service surfaces in `packages/ma_control_hub/*.inc`: **59**
- Key referenced surfaces include:
  - `sensor.ma_*` routing/meta/now-playing derivatives,
  - `sensor.spectra_ls_rooms_*` room-map sources,
  - `input_select.ma_active_target`,
  - `input_boolean.ma_control_fallback_enabled`,
  - `script.ma_update_target_options`, `script.ma_auto_select`.

## Tough spots (must be surfaced; not glossed)

1. **Selection loop risk (High)**
   - `ma_auto_select` and `state_changed`-driven automation activity can conflict with component write-path trials.
   - Mitigation: single-writer switch + correlation IDs + debounce + reentrancy guard required before P3-S01 enablement.

2. **Fallback ambiguity risk (Medium)**
   - Static fallback hosts/entities still exist and can hide discovery-routing regressions when enabled.
   - Mitigation: preserve explicit fallback-off default and validate both fallback-off and fallback-on behavior with separate evidence.

3. **Parser-shape risk (Medium)**
   - Broad dual-mode payload parsing (native object + string JSON) has high coupling and drift risk.
   - Mitigation: keep shape contract explicit and fail noisy in diagnostics when shape assumptions break.

4. **Authority boundary risk (High)**
   - Legacy template graph mixes routing + selection + metadata concerns; unsafe to hand off all at once.
   - Mitigation: enforce P3 sub-slices with routing-only first, then selection, metadata later.

5. **Ghost-broadcaster stale-playing risk (High)**
   - Some players can continue reporting `playing` while effectively stale (progress clock not moving), causing stale metadata to remain selected/displayed.
   - Mitigation: enforce freshness-aware `playing` gates when progress clocks are present (runtime + component parity), align preferred/resolver freshness windows to `input_number.ma_meta_paused_hide_s`, and publish explicit suppression reasons (`playing_stale_hidden`, `paused_stale_hidden`, `long_idle_stale_hidden`) for deterministic operator triage.

## P1/P2 validation checkpoint status

- P1-S01: validated as read-only parity slice (legacy source-of-truth retained).
- P2-S01/P2-S02: validated with deterministic diagnostics and closure template support.

Still required on every P3 trial:

- rerun parity templates and capture fresh outputs in-slice,
- verify no flapping and no mismatches before widening scope.
