<!-- Description: Deterministic operator checklist for Phase 6 Slice-02 control-center settings-contract validation and bounded closeout readiness. -->
<!-- Version: 2026.04.21.2 -->
<!-- Last updated: 2026-04-21 -->

# P6-S02 Control-Center Settings Contract — Checklist

Use this checklist to validate the first bounded settings-contract lane for control-center customization (`options` + `spectra_ls.set_control_center_settings`).

Primary live monitor template for this slice:

- `docs/testing/raw/p6_s02_control_center_settings_monitor.jinja`

## Scope guard (must hold)

- In scope: settings-contract readiness validation, required-key/schema visibility checks, read-only-first posture verification, and closeout evidence capture.
- Out of scope: authority ownership cutover, broad execution-lane refactors, helper/entity contract breakage, or legacy retirement actions.
- Single-purpose rule: this slice is settings-contract validation and closeout governance only.

## Inputs (must exist)

- P6-S01 foundation baseline previously validated.
- Runtime baseline remains safe (`authority_mode=legacy`) with clean contract/parity context.
- Control-center settings contract surfaces present in shadow diagnostics (`control_center_validation`, `write_controls.control_center_settings`).

## Quick-start execution flow (operator-grade)

1. Apply one bounded settings update (integration options flow or `spectra_ls.set_control_center_settings`).
2. Render `docs/testing/raw/p6_s02_control_center_settings_monitor.jinja`.
3. Record monitor output in the evidence block below.
4. Confirm unresolved scene bindings are expected (or explicitly documented) before closeout classification.

## Activation gates (all required)

1. **Runtime baseline gate**
   - `authority_mode=legacy` and clean route/contract/parity/freshness posture.
2. **Settings-surface gate**
   - settings schema/required keys are present and `ready_for_customization=true`.
3. **Read-only-first gate**
   - read-only posture remains explicit/bounded unless intentionally disabled for validation.
4. **Governance gate**
   - compatibility and rollback posture remains explicit and no-authority-expansion stance is intact.

## Stop conditions (fail-closed)

- Any authority expansion without explicit bounded approval,
- settings contract/schema visibility regresses,
- contract/parity baseline regresses during validation,
- compatibility/rollback posture becomes ambiguous.

If any stop condition triggers: classify as non-closeout, keep P6-S02 open, and publish remediation actions.

## Evidence template (copy/paste)

```text
P6-S02 Settings Validation Evidence Record
-----------------------------------------
run_id:
captured_at:
operator:

gate_checks:
   runtime_baseline_gate: PASS|WARN|FAIL
   settings_surface_gate: PASS|WARN|FAIL
   read_only_first_gate: PASS|WARN|FAIL
   governance_gate: PASS|WARN|FAIL

settings_snapshot:
   authority_mode:
   route_decision:
   schema_version:
   settings_present:
   ready_for_customization:
   required_keys_count:
   unresolved_scene_bindings_count:
   read_only_mode:
   missing_required:
   unresolved_required:
   unresolved_sources:
   mismatches:
   freshness_age_s:

stop_conditions:
   triggered: true|false
   reason: none|authority_expansion|schema_regression|contract_regression|compatibility_ambiguity|rollback_ambiguity|other

verdict:
   outcome: PASS|WARN|FAIL
   p6_s02_closeout_eligible: true|false
   next_slice_ready: true|false
   rationale:
```

## Closeout decision rule

- `PASS`: all gates pass, no stop conditions, and settings-contract readiness is deterministic.
- `WARN`: partial evidence or posture ambiguity; keep P6-S02 active.
- `FAIL`: baseline/settings-surface regression or stop-condition trigger.

## P6-S02 closeout evidence (Run-1)

```text
P6-S02 Settings Validation Evidence Record
-----------------------------------------
run_id: p6s02-2026-04-21-run1
captured_at: 2026-04-21 20:15:35.644673-07:00
operator: cory

gate_checks:
   runtime_baseline_gate: PASS
   settings_surface_gate: PASS
   read_only_first_gate: PASS
   governance_gate: PASS

settings_snapshot:
   authority_mode: legacy
   route_decision: route_linkplay_tcp
   schema_version: p6_s02.v1
   settings_present: true
   ready_for_customization: true
   required_keys_count: 8
   unresolved_scene_bindings_count: 4
   read_only_mode: false
   missing_required: 0
   unresolved_required: 0
   unresolved_sources: 0
   mismatches: 0
   freshness_age_s: 2.6

stop_conditions:
   triggered: false
   reason: none

verdict:
   outcome: PASS
   p6_s02_closeout_eligible: true
   next_slice_ready: true
   rationale: all settings-contract validation gates pass with deterministic schema/readiness visibility and preserved legacy authority baseline.
```

Disposition: P6-S02 closeout packet accepted; slice is eligible for `Validated` promotion in phase ledgers.

## Artifact linkage

- `docs/roadmap/v-next-NOTES.md`
- `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`
- `docs/CHANGELOG.md`
