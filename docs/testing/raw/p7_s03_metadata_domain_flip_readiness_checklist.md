<!-- Description: Deterministic operator checklist for Phase 7 Slice-03 bounded metadata-domain authority-flip execution lane readiness and closeout gating. -->
<!-- Version: 2026.04.21.4 -->
<!-- Last updated: 2026-04-21 -->

# P7-S03 Bounded Metadata-Domain Authority-Flip Lane — Checklist

Use this checklist to run the second bounded Phase-7 domain lane (metadata) with strict single-writer and rollback-safe controls.

Primary live monitor template for this slice:

- `docs/testing/raw/p7_s03_metadata_domain_flip_readiness_monitor.jinja`

## Scope guard (must hold)

- In scope: bounded metadata-domain authority-flip execution lane, pre/in/post evidence capture, rollback-safe posture verification.
- Out of scope: routing-domain revalidation (already sealed in P7-S02), lighting-domain ownership flip, irreversible legacy retirement actions.
- Single-purpose rule: this slice is metadata-domain bounded execution only.

## Inputs (must exist)

- `P7-S02` validated with accepted closeout evidence.
- Runtime baseline is clean at pre-window capture.
- Metadata readiness diagnostics are PASS/ready.
- Rollback switch and single-writer enforcement are explicit and tested.

## Quick-start execution flow (operator-grade)

1. Capture pre-window readiness using the P7-S03 monitor.
2. Execute one bounded metadata-domain window using metadata trial service path.
3. Capture in-window and post-window monitor outputs.
4. Record stop-condition status and classify PASS/WARN/FAIL.

## Phase definitions + exactly what to run

### PRE (before bounded window opens)

- Meaning: baseline validation only; no metadata trial mutation yet.
- Required posture: `authority_mode=legacy`, clean contract/parity, metadata readiness true.
- Run now:
  1. Open HA **Developer Tools -> Template**.
  2. Paste `docs/testing/raw/p7_s03_metadata_domain_flip_readiness_monitor.jinja`.
  3. Set `window_phase` in template to `pre`.
  4. Run and copy output into evidence record as `window_phase: pre`.

### IN (bounded metadata lane window active)

- Meaning: perform one bounded metadata trial probe while window is active.
- Run now:
  1. In HA **Developer Tools -> Actions**, call `spectra_ls.metadata_write_trial` once with:
     - `mode: legacy`
     - `window_id: p7s03-<timestamp>-run1`
     - `reason: P7-S03 bounded metadata lane in-window trial`
     - `dry_run: true`
  2. Verify trial status is non-blocking (`dry_run_ok` expected in first pass).
  3. Verify metadata readiness remains true and route remains `route_linkplay_tcp`.
  4. Re-run the same monitor with `window_phase` set to `in`.
  5. Copy output into evidence record as `window_phase: in`.

### POST (after bounded metadata lane window closes)

- Meaning: verify rollback-safe baseline posture after bounded metadata probe.
- Run now:
  1. Ensure baseline control posture remains/restores to `authority_mode=legacy`.
  2. Re-run the same monitor with `window_phase` set to `post`.
  3. Copy output into evidence record as `window_phase: post`.
  4. Confirm stop conditions remain `triggered: false`.

Promotion note: P7-S03 closeout eligibility requires PASS/READY evidence across `pre`, `in`, and `post` captures with no stop conditions.

## Activation gates (all required)

1. **Baseline gate:** clean legacy baseline + fresh snapshot.
2. **Entry gate:** P7-S02 validated + rollback path verified.
3. **Safety gate:** single-writer + bounded-scope confirmation.
4. **Metadata gate:** metadata readiness PASS (`metadata_prep_validation`) with route eligibility and no metadata missing-required entities.

## Stop conditions (fail-closed)

- metadata readiness drops from PASS/ready during window,
- contract/parity drift during window,
- metadata trial status enters blocking/failure state,
- rollback ambiguity/failure,
- cross-domain ownership side effects outside metadata lane.

If any stop condition triggers: abort window, rollback, and keep P7-S03 active.

## Evidence template (copy/paste)

```text
P7-S03 Metadata-Domain Evidence Record
--------------------------------------
run_id:
window_phase: pre|in|post
captured_at:
operator:

gate_checks:
   baseline_gate: PASS|WARN|FAIL
   entry_gate: PASS|WARN|FAIL
   safety_gate: PASS|WARN|FAIL
   metadata_gate: PASS|WARN|FAIL

snapshot:
   monitor_source_sensor:
   authority_mode:
   route_decision:
   metadata_verdict:
   metadata_ready:
   metadata_missing_required:
   metadata_trial_status:
   metadata_trial_window_id:
   metadata_trial_gate_verdict:
   missing_required:
   unresolved_required:
   unresolved_sources:
   mismatches:
   freshness_age_s:

stop_conditions:
   triggered: true|false
   reason: none|metadata_not_ready|metadata_trial_blocked|contract_drift|rollback_failure|scope_bleed|other

verdict:
   outcome: PASS|WARN|FAIL
   p7_s03_closeout_eligible: true|false
   next_slice_ready: true|false
   rationale:
```

## Closeout decision rule

- `PASS`: all gates pass across window captures, no stop conditions, rollback posture remains deterministic.
- `WARN`: partial evidence or non-blocking ambiguity; keep P7-S03 active.
- `FAIL`: stop condition or baseline/entry gate failure.

## P7-S03 pre-window evidence (Run-1)

```text
P7-S03 Metadata-Domain Evidence Record
--------------------------------------
run_id: p7s03-2026-04-21-run1
window_phase: pre
captured_at: 2026-04-21 21:03:00.345491-07:00
operator: cory

gate_checks:
   baseline_gate: PASS
   entry_gate: PASS
   safety_gate: PASS
   metadata_gate: PASS

snapshot:
   monitor_source_sensor: sensor.shadow_active_target
   authority_mode: legacy
   route_decision: route_linkplay_tcp
   metadata_verdict: PASS
   metadata_ready: true
   metadata_missing_required: 0
   metadata_trial_status: never_attempted
   metadata_trial_window_id: n/a
   metadata_trial_gate_verdict: N/A
   missing_required: 0
   unresolved_required: 0
   unresolved_sources: 0
   mismatches: 0
   freshness_age_s: 8.0

stop_conditions:
   triggered: false
   reason: none

verdict:
   outcome: PASS
   p7_s03_closeout_eligible: false
   next_slice_ready: true
   rationale: pre-window metadata readiness and baseline gates are fully green; bounded in-window execution may proceed.
```

Disposition: P7-S03 remains **Active**; pre-window gate passed and in-window execution is authorized.

## P7-S03 in-window evidence (Run-1)

```text
P7-S03 Metadata-Domain Evidence Record
--------------------------------------
run_id: p7s03-2026-04-21-run1
window_phase: in
captured_at: 2026-04-21 21:05:29.978417-07:00
operator: cory

gate_checks:
   baseline_gate: PASS
   entry_gate: PASS
   safety_gate: PASS
   metadata_gate: PASS

snapshot:
   monitor_source_sensor: sensor.shadow_active_target
   authority_mode: legacy
   route_decision: route_linkplay_tcp
   metadata_verdict: PASS
   metadata_ready: true
   metadata_missing_required: 0
   metadata_trial_status: dry_run_ok
   metadata_trial_window_id: window_id: p7s03-2026-04-21-run1
   metadata_trial_gate_verdict: PASS
   missing_required: 0
   unresolved_required: 0
   unresolved_sources: 0
   mismatches: 0
   freshness_age_s: 1.2

stop_conditions:
   triggered: false
   reason: none

verdict:
   outcome: PASS
   p7_s03_closeout_eligible: false
   next_slice_ready: true
   rationale: in-window bounded metadata trial probe executed with clean gates and non-blocking trial status.
```

Disposition: P7-S03 remains **Active**; in-window gate passed and post-window capture is now required for closeout eligibility.

## P7-S03 post-window evidence (Run-2)

```text
P7-S03 Metadata-Domain Evidence Record
--------------------------------------
run_id: p7s03-2026-04-21-run2
window_phase: post
captured_at: 2026-04-21 21:07:08.345292-07:00
operator: cory

gate_checks:
   baseline_gate: PASS
   entry_gate: PASS
   safety_gate: PASS
   metadata_gate: PASS

snapshot:
   monitor_source_sensor: sensor.shadow_active_target
   authority_mode: legacy
   route_decision: route_linkplay_tcp
   metadata_verdict: PASS
   metadata_ready: true
   metadata_missing_required: 0
   metadata_trial_status: dry_run_ok
   metadata_trial_window_id: window_id: p7s03-2026-04-21-run2
   metadata_trial_gate_verdict: PASS
   missing_required: 0
   unresolved_required: 0
   unresolved_sources: 0
   mismatches: 0
   freshness_age_s: 1.2

stop_conditions:
   triggered: false
   reason: none

verdict:
   outcome: PASS
   p7_s03_closeout_eligible: true
   next_slice_ready: true
   rationale: post-window rollback-safe baseline and metadata trial diagnostics remained clean; bounded lane closeout criteria are satisfied.
```

Disposition: P7-S03 is **Validated**; bounded metadata-domain lane closeout packet is complete (pre/in/post PASS, no stop conditions).

## P7-S03 closeout packet status

1. **Pre-window capture:** PASS/READY.
2. **In-window capture:** PASS/READY with non-blocking trial status.
3. **Post-window capture:** PASS/READY with rollback-safe baseline verified.
4. **Stop-condition audit:** no triggers.
5. **Closeout classification:** validated.

## Artifact linkage

- `docs/roadmap/v-next-NOTES.md`
- `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`
- `docs/CHANGELOG.md`
