<!-- Description: Deterministic operator run-window checklist for Phase 5 Slice-03 lighting-orchestration gate-prep and bounded validation (P5-S03). -->
<!-- Version: 2026.04.21.6 -->
<!-- Last updated: 2026-04-21 -->

# P5-S03 Lighting Orchestration — Run Window Checklist

Use this checklist to run one bounded **lighting-domain** validation window after P5-S02 closeout decision recording.

Primary live monitor template for this slice:

- `docs/testing/raw/p5_s03_lighting_functionality_monitor.jinja`

## Scope guard (must hold)

- In scope: lighting-orchestration readiness and bounded validation only.
- Out of scope: routing-domain ownership, metadata-domain ownership, naming retirement.
- Single-domain rule: no concurrent metadata/routing cutover activity in this window.

## Current-state safety note

- Legacy/runtime lighting ownership remains authoritative by default.
- This checklist validates contracts/orchestration readiness and bounded behavior evidence.
- No implicit ownership takeover is allowed from checklist execution alone.

## Preflight gates (all required)

1. **P5-S02 closeout gate**
   - P5-S02 status decision is recorded (Validated or explicit defer rationale).
2. **Authority baseline gate**
   - `write_controls.authority_mode=legacy` at window start.
3. **Lighting contract gate**
   - Required lighting selectors/helpers resolve and are non-degraded.
4. **Isolation gate**
   - No metadata/routing cutover sequence is running in parallel.
5. **Evidence freshness gate**
   - Pre/in/post monitor renders are all captured in this run window.

## Recommended bounded sequence

1. Capture pre-window lighting baseline (selectors/options/target mapping + authority mode).
2. Execute bounded lighting interactions only (room/target browse + slider apply checks).
3. Capture in-window behavior evidence and parity/contract health.
4. Confirm/restore explicit post-window authority disposition (`legacy`).
5. Record verdict (`PASS` / `WARN` / `FAIL`) with rationale and closeout eligibility.

## Quick-start execution flow (operator-grade)

1. Render `docs/testing/raw/p5_s03_lighting_functionality_monitor.jinja`.
2. Capture **pre-window** output block.
3. Perform bounded lighting interactions only:
   - browse `input_select.control_board_room`,
   - browse `input_select.control_board_target`,
   - apply lighting slider adjustments in the active lighting mode.
4. Re-render monitor and capture **in-window** block.
5. Confirm/restore `authority_mode=legacy`, rerender monitor, and capture **post-window** block.
6. Fill the evidence template and classify verdict.

## Stop conditions (fail-closed)

- required lighting selectors/helpers become missing/unresolved,
- route/authority posture drifts outside declared window,
- stale/missing evidence artifacts,
- cross-domain side effects are observed.

When triggered: freeze slice advancement, restore/confirm `legacy` authority posture, and classify as non-closeout.

## Evidence template (copy/paste)

```text
P5-S03 Run Window Evidence Record
---------------------------------
run_id:
captured_at:
operator:
window_scope: lighting-domain only

preflight:
   gate_a_p5_s02_closeout_recorded: PASS|WARN|FAIL
   gate_b_authority_baseline: PASS|WARN|FAIL
   gate_c_lighting_contracts: PASS|WARN|FAIL
   gate_d_isolation: PASS|WARN|FAIL
   gate_e_fresh_evidence: PASS|WARN|FAIL

pre_window_snapshot:
   authority_mode: legacy|component
   lighting_room_selector_state:
   lighting_target_selector_state:
   lighting_target_entity_id:
   selector_options_ready: true|false
   captured_at:

in_window_snapshot:
   authority_mode: legacy|component
   lighting_behavior_verdict: PASS|WARN|FAIL
   parity_mismatches_count:
   unresolved_sources_count:
   captured_at:

stop_conditions:
   triggered: true|false
   reason: none|lighting_contract_missing|authority_drift|cross_domain_side_effect|stale_or_missing_evidence|other

post_window_snapshot:
   authority_mode: legacy|component
   lighting_behavior_verdict: PASS|WARN|FAIL
   captured_at:

verdict:
   outcome: PASS|WARN|FAIL
   rationale:
   closeout_eligible: true|false
```

## Closeout rule

- `PASS` closeout-eligible only when all preflight gates pass, stop conditions are not triggered, and post-window authority disposition is explicit/safe (`legacy` unless an approved extension is documented).
- `WARN` for incomplete or inconclusive evidence.
- `FAIL` for stop-condition triggers or unsafe authority drift.

## Immediate next action — Run-1 lighting evidence packet

Use this as the first real capture block for the active P5-S03 slice.

```text
P5-S03 Run Window Evidence Record
---------------------------------
run_id: p5s03-2026-04-21-run1
captured_at:
operator: local
window_scope: lighting-domain only

preflight:
   gate_a_p5_s02_closeout_recorded: PASS
   gate_b_authority_baseline:
   gate_c_lighting_contracts:
   gate_d_isolation:
   gate_e_fresh_evidence:

pre_window_snapshot:
   authority_mode:
   lighting_room_selector_state:
   lighting_target_selector_state:
   lighting_target_entity_id:
   selector_options_ready:
   captured_at:

in_window_snapshot:
   authority_mode:
   lighting_behavior_verdict:
   parity_mismatches_count:
   unresolved_sources_count:
   captured_at:

stop_conditions:
   triggered:
   reason:

post_window_snapshot:
   authority_mode:
   lighting_behavior_verdict:
   captured_at:

verdict:
   outcome:
   rationale:
   closeout_eligible:
```

Run-1 fill hints (source = `p5_s03_lighting_functionality_monitor.jinja`):

- `authority_mode` ← `write_controls.authority_mode`
- `lighting_room_selector_state` ← `input_select.control_board_room`
- `lighting_target_selector_state` ← `input_select.control_board_target`
- `lighting_target_entity_id` ← `sensor.control_board_target_entity_id`
- `selector_options_ready` ← monitor line `Selector options ready`
- `lighting_behavior_verdict` ← monitor `Status`/`Lighting readiness` interpretation
- `parity_mismatches_count` ← `mismatches`
- `unresolved_sources_count` ← `unresolved_sources`
- `captured_at` ← monitor timestamp (`Timestamp`) and control-snapshot context line

Freshness interpretation note (P5-S03):

- `Control snapshot freshness` is contextual visibility from the shared shadow snapshot.
- Do **not** classify `WARN/CAUTION` from control-snapshot age alone when authority/contract/selector/parity gates are healthy.

Run-1 live evidence capture (pre-window recorded):

```text
P5-S03 Run Window Evidence Record
---------------------------------
run_id: p5s03-2026-04-21-run1
captured_at: 2026-04-21 17:44:45.600796-07:00
operator: local
window_scope: lighting-domain only

preflight:
   gate_a_p5_s02_closeout_recorded: PASS
   gate_b_authority_baseline: PASS
   gate_c_lighting_contracts: PASS
   gate_d_isolation: PASS
   gate_e_fresh_evidence: PASS (pre/in/post captured in-window)

pre_window_snapshot:
   authority_mode: legacy
   lighting_room_selector_state: Living Room
   lighting_target_selector_state: All
   lighting_target_entity_id: n/a (valid for target=All)
   selector_options_ready: true
   parity_mismatches_count: 0
   unresolved_sources_count: 0
   lighting_behavior_verdict: PASS/READY
   captured_at: 2026-04-21 17:41:12.841574-07:00

in_window_snapshot:
   authority_mode: legacy
   lighting_behavior_verdict: PASS/READY
   parity_mismatches_count: 0
   unresolved_sources_count: 0
   captured_at: 2026-04-21 17:44:00.229390-07:00

stop_conditions:
   triggered: false
   reason: none

post_window_snapshot:
   authority_mode: legacy
   lighting_behavior_verdict: PASS/READY
   captured_at: 2026-04-21 17:44:45.600796-07:00

verdict:
   outcome: PASS
   rationale: All preflight gates passed with complete pre/in/post evidence, no stop-condition triggers, and explicit safe post-window authority posture (`legacy`) under clean contract/parity signals.
   closeout_eligible: true
```

## Artifact linkage

- `docs/roadmap/v-next-NOTES.md`
- `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`
- `docs/CHANGELOG.md`
- `README.md` parity decision (`no material repo-state change` unless explicitly changed)
