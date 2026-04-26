<!-- Description: Deterministic operator checklist for Phase 8 Slice-04 MA-native audio plugin/provider fast-cutover gate-prep execution. -->
<!-- Version: 2026.04.22.2 -->
<!-- Last updated: 2026-04-22 -->

# P8-S04 MA-Native Audio Plugin Fast-Cutover — Checklist

Use this checklist to execute `P8-S04` as a bounded pre/in/post evidence lane with rollback-safe posture.

Primary live monitor template:

- `docs/testing/raw/p8_s04_ma_plugin_cutover_readiness_monitor.jinja`

## Scope guard

- In scope: MA-native provider/plugin feasibility probe windows, route selection proof, rollback-safe evidence capture.
- Out of scope: immediate global ownership flip, legacy helper/entity retirement, and cross-domain authority expansion.

## Activation gates (all required)

1. `P8-S03` is validated.
2. Legacy baseline is clean (`authority_mode=legacy`, contract/parity clean, fresh snapshot).
3. Route selection is explicit (`player_provider` preferred; `plugin_adjunct`/`bridge_shim` allowed with rationale).
4. Monitor/checklist packet is published before probe execution.
5. Rollback path is verified before in-window activity.

## Stop conditions (fail-closed)

- `authority_mode != legacy` outside explicit bounded probe semantics,
- contract/parity regressions (`missing_required`, `unresolved_required`, `mismatches`),
- rollback proof missing,
- missing or stale evidence packet,
- route ownership ambiguity between runtime/component tracks.

If any stop condition triggers: keep `P8-S04` active and do not promote.

## Evidence template

```text
P8-S04 MA Plugin Cutover Record
--------------------------------
run_id:
window_phase: pre|in|post
captured_at:
operator:

route_selection:
   selected_path: player_provider|plugin_adjunct|bridge_shim
   rationale:

gate_checks:
   baseline_gate: PASS|WARN|FAIL
   entry_gate: PASS|WARN|FAIL
   safety_gate: PASS|WARN|FAIL
   execution_gate: PASS|WARN|FAIL

snapshot:
   monitor_source_sensor:
   authority_mode:
   route_decision:
   contract_valid:
   missing_required:
   unresolved_required:
   unresolved_sources:
   mismatches:
   freshness_age_s:

probe_artifact:
   captured: true|false
   artifact_ref:
   dry_run_first: true|false

stop_conditions:
   triggered: true|false
   reason: none|baseline_drift|contract_parity_regression|rollback_missing|stale_evidence|ownership_ambiguity|other

verdict:
   outcome: PASS|WARN|FAIL
   p8_s04_closeout_eligible: true|false
   p8_s04_promoted_validated: true|false
   rationale:
```

## Artifact linkage

- `docs/notes/NOTES-ma-audio-plugin-cutover-plan.md`
- `docs/roadmap/v-next-NOTES.md`
- `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`
- `docs/CHANGELOG.md`

## Run-1 evidence record (pending)

```text
P8-S04 MA Plugin Cutover Record
--------------------------------
run_id: p8s04-YYYY-MM-DD-run1
window_phase: pre
captured_at:
operator:

route_selection:
   selected_path:
   rationale:

gate_checks:
   baseline_gate:
   entry_gate:
   safety_gate:
   execution_gate:

snapshot:
   monitor_source_sensor:
   authority_mode:
   route_decision:
   contract_valid:
   missing_required:
   unresolved_required:
   unresolved_sources:
   mismatches:
   freshness_age_s:

probe_artifact:
   captured: false
   artifact_ref: n/a
   dry_run_first: true

stop_conditions:
   triggered:
   reason:

verdict:
   outcome:
   p8_s04_closeout_eligible: false
   p8_s04_promoted_validated: false
   rationale:
```

## Run-2 strict execution packet (in-window)

Use this for the second bounded window capture after pre-window baseline has already been recorded.

```text
P8-S04 MA Plugin Cutover Record
--------------------------------
run_id: p8s04-2026-04-22-run2
window_phase: in
captured_at:
operator:

route_selection:
   selected_path: player_provider
   rationale: primary recommended MA-native route for direct player semantics/capability mapping

gate_checks:
   baseline_gate:
   entry_gate:
   safety_gate:
   execution_gate:

snapshot:
   monitor_source_sensor:
   authority_mode:
   route_decision:
   contract_valid:
   missing_required:
   unresolved_required:
   unresolved_sources:
   mismatches:
   freshness_age_s:

probe_artifact:
   captured: true
   artifact_ref:
   dry_run_first: true

stop_conditions:
   triggered:
   reason:

verdict:
   outcome:
   p8_s04_closeout_eligible: false
   p8_s04_promoted_validated: false
   rationale: Run-2 is an in-window capture and requires post-window rollback proof before closeout eligibility.
```
