<!-- Description: Deterministic operator checklist for Phase 7 Slice-02 first bounded authority-flip execution lane readiness and closeout gating. -->
<!-- Version: 2026.04.21.6 -->
<!-- Last updated: 2026-04-21 -->

# P7-S02 First Bounded Authority-Flip Lane — Checklist

Use this checklist to run the first bounded domain flip (routing/selection lane) with strict single-writer and rollback-safe controls.

Primary live monitor template for this slice:

- `docs/testing/raw/p7_s02_domain_flip_readiness_monitor.jinja`

## Scope guard (must hold)

- In scope: first bounded routing/selection authority-flip lane, pre/in/post window evidence capture, rollback-safe posture verification.
- Out of scope: multi-domain ownership flips, metadata/lighting domain retirement, irreversible legacy contract removals.
- Single-purpose rule: this slice is first bounded authority-flip execution lane only.

## Inputs (must exist)

- `P7-S01` validated with accepted closeout evidence.
- Runtime baseline is clean at pre-window capture.
- Rollback switch and single-writer enforcement are explicit and tested.

## Quick-start execution flow (operator-grade)

1. Capture pre-window readiness using the P7-S02 monitor.
2. Execute one bounded authority-flip window for routing/selection domain.
3. Capture in-window and post-window monitor outputs.
4. Record stop-condition status and classify PASS/WARN/FAIL.

## Phase definitions + exactly what to run

### PRE (before bounded window opens)

- Meaning: baseline validation only; no lane mutation yet.
- Required posture: `authority_mode=legacy`, clean contract/parity, route eligibility present.
- Run now:
   1. Open HA **Developer Tools -> Template**.
   2. Paste `docs/testing/raw/p7_s02_domain_flip_readiness_monitor.jinja`.
   3. Set `window_phase` in template to `pre`.
   4. Run and copy output into evidence record as `window_phase: pre`.

### IN (bounded lane window active)

- Meaning: perform one bounded routing/selection probe while window is active.
- Run now (deterministic probe set; no dedicated UI control surface required):
   1. In HA **Developer Tools -> States**, set `input_select.ma_active_target` once (A -> B).
   2. In HA **Developer Tools -> Actions**, call `spectra_ls.execute_control_center_input` once (for example `input_event: encoder_press`, optional `dry_run: true`).
   3. Verify route remains `route_linkplay_tcp`.
   4. Re-run the same monitor with `window_phase` set to `in`.
   5. Copy output into evidence record as `window_phase: in`.

### POST (after bounded lane window closes)

- Meaning: verify rollback-safe baseline posture after the bounded probe.
- Run now:
   1. Close the bounded window / return to baseline control posture.
   2. Re-run the same monitor with `window_phase` set to `post`.
   3. Copy output into evidence record as `window_phase: post`.
   4. Confirm stop conditions remain `triggered: false`.

Promotion note: P7-S02 closeout eligibility requires PASS/READY evidence across `pre`, `in`, and `post` captures with no stop conditions.

## Activation gates (all required)

1. **Baseline gate:** clean legacy baseline + fresh snapshot.
2. **Entry gate:** P7-S01 validated + rollback path verified.
3. **Safety gate:** single-writer + bounded-scope confirmation.
4. **Route gate:** first lane requires `route_linkplay_tcp` eligibility.

## Stop conditions (fail-closed)

- contract/parity drift during window,
- loop/flap behavior detected,
- rollback ambiguity or failure,
- cross-domain ownership side effects outside intended lane.

If any stop condition triggers: abort flip window, rollback, and keep P7-S02 active.

## Evidence template (copy/paste)

```text
P7-S02 Domain-Flip Evidence Record
----------------------------------
run_id:
window_phase: pre|in|post
captured_at:
operator:

gate_checks:
   baseline_gate: PASS|WARN|FAIL
   entry_gate: PASS|WARN|FAIL
   safety_gate: PASS|WARN|FAIL
   route_gate: PASS|WARN|FAIL

snapshot:
   monitor_source_sensor:
   authority_mode:
   route_decision:
   missing_required:
   unresolved_required:
   unresolved_sources:
   mismatches:
   freshness_age_s:

stop_conditions:
   triggered: true|false
   reason: none|contract_drift|loop_flap|rollback_failure|scope_bleed|other

verdict:
   outcome: PASS|WARN|FAIL
   p7_s02_closeout_eligible: true|false
   next_slice_ready: true|false
   rationale:
```

## Closeout decision rule

- `PASS`: all gates pass across window captures, no stop conditions, rollback posture remains deterministic.
- `WARN`: partial evidence or non-blocking ambiguity; keep P7-S02 active.
- `FAIL`: stop condition or baseline/entry gate failure.

## P7-S02 pre-window evidence (Run-1)

```text
P7-S02 Domain-Flip Evidence Record
----------------------------------
run_id: p7s02-2026-04-21-run1
window_phase: pre
captured_at: 2026-04-21 20:38:00.223973-07:00
operator: cory

gate_checks:
   baseline_gate: PASS
   entry_gate: PASS
   safety_gate: PASS
   route_gate: PASS

snapshot:
   monitor_source_sensor: sensor.shadow_active_target
   authority_mode: legacy
   route_decision: route_linkplay_tcp
   missing_required: 0
   unresolved_required: 0
   unresolved_sources: 0
   mismatches: 0
   freshness_age_s: 207.6

stop_conditions:
   triggered: false
   reason: none

verdict:
   outcome: PASS
   p7_s02_closeout_eligible: false
   next_slice_ready: true
   rationale: pre-window readiness gates are fully green; bounded authority-flip window may proceed.
```

Disposition: P7-S02 remains **Active**; pre-window gate passed and in-window execution is authorized.

## P7-S02 in-window evidence (Run-1)

```text
P7-S02 Domain-Flip Evidence Record
----------------------------------
run_id: p7s02-2026-04-21-run1
window_phase: in
captured_at: 2026-04-21 20:55:41.000516-07:00
operator: cory

gate_checks:
   baseline_gate: PASS
   entry_gate: PASS
   safety_gate: PASS
   route_gate: PASS

snapshot:
   monitor_source_sensor: sensor.shadow_active_target
   authority_mode: legacy
   route_decision: route_linkplay_tcp
   missing_required: 0
   unresolved_required: 0
   unresolved_sources: 0
   mismatches: 0
   freshness_age_s: 0.9

stop_conditions:
   triggered: false
   reason: none

verdict:
   outcome: PASS
   p7_s02_closeout_eligible: false
   next_slice_ready: true
   rationale: in-window bounded routing/selection probe executed with clean gates and no stop conditions.
```

Disposition: P7-S02 remains **Active**; in-window gate passed and post-window capture is now required for closeout eligibility.

## P7-S02 post-window evidence (Run-1)

```text
P7-S02 Domain-Flip Evidence Record
----------------------------------
run_id: p7s02-2026-04-21-run1
window_phase: post
captured_at: 2026-04-21 20:57:00.162663-07:00
operator: cory

gate_checks:
   baseline_gate: PASS
   entry_gate: PASS
   safety_gate: PASS
   route_gate: PASS

snapshot:
   monitor_source_sensor: sensor.shadow_active_target
   authority_mode: legacy
   route_decision: route_linkplay_tcp
   missing_required: 0
   unresolved_required: 0
   unresolved_sources: 0
   mismatches: 0
   freshness_age_s: 6.3

stop_conditions:
   triggered: false
   reason: none

verdict:
   outcome: PASS
   p7_s02_closeout_eligible: true
   next_slice_ready: true
   rationale: post-window rollback-safe baseline verified; all gates pass with no stop-condition triggers.
```

Disposition: P7-S02 **closeout eligible** and promoted to **Validated**.

## P7-S02 execution packet (completion summary)

1. **In-window capture (Run-1/in):** execute bounded routing/selection authority flip and capture monitor during active window.
2. **Post-window capture (Run-1/post):** restore/verify rollback-safe baseline posture and capture monitor after window close.
3. **Stop-condition check:** explicitly record whether loop/flap, contract drift, or scope bleed occurred.
4. **Closeout eligibility:** PASS achieved across pre/in/post captures with no stop conditions.

## Artifact linkage

- `docs/roadmap/v-next-NOTES.md`
- `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`
- `docs/CHANGELOG.md`
