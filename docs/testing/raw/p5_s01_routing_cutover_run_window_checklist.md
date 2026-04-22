<!-- Description: Deterministic operator run-window checklist for Phase 5 Slice-01 routing-domain cutover trial (P5-S01). -->
<!-- Version: 2026.04.20.7 -->
<!-- Last updated: 2026-04-20 -->

# P5-S01 Routing Cutover — Run Window Checklist

Use this checklist to execute one bounded P5-S01 routing-domain trial with explicit evidence, rollback proof, and fail-closed behavior.

## Practical cutover guide (human version)

If you ignore everything else, run this section in order.

### What you are doing

- You are testing whether component-owned routing can run safely for a short window.
- You are **not** cutting over metadata, lighting orchestration, or naming cleanup.
- This is a trial window, not a permanent switch.

### What this is **not**

- This is **not** deleting the legacy control hub.
- This is **not** moving legacy files out of the way.
- This is **not** a full migration.

Legacy control-hub surfaces stay in place during P5-S01. The mechanism is single-writer control, not file removal.

### Mechanism (plain terms)

P5-S01 uses an authority switch:

- `legacy` = legacy hub is the writer (default/safe baseline).
- `component` = component is temporarily allowed to perform guarded routing writes for the trial window.

You switch that state with the service:

- `spectra_ls.set_write_authority` (`mode: legacy|component`)

Supporting services used in the same window:

- `spectra_ls.rebuild_registry`
- `spectra_ls.validate_contracts`
- `spectra_ls.dump_route_trace`
- optional guarded write attempt: `spectra_ls.route_write_trial`

Live feedback monitor template:

- `docs/testing/raw/p5_s01_component_functionality_monitor.jinja`

End of window rule: set authority back to `legacy` unless you have a documented, approved extension.

### Before you start (2-minute check)

Do not start until all of these are true:

- Routing authority is currently `legacy`.
- Your parity check is PASS right now (not from yesterday): run `docs/testing/raw/p2_registry_router_verification.jinja` and confirm **Result = PASS**.
- Metadata and lighting are explicitly out of this run window: no metadata ownership/cutover action, no lighting orchestration cutover action, and no parallel migration slice.
- You already know your rollback path and can execute it immediately.

### About “meta/lighting flags” (important)

There are no dedicated metadata/lighting cutover toggle entities documented as mandatory for P5-S01.

In practical terms, “flags off” means **scope discipline**:

- keep this run routing-only,
- do not introduce metadata ownership changes during this window,
- do not introduce lighting orchestration ownership changes during this window.

### The run window (simple operator flow)

1. Capture a baseline snapshot (authority, target, route, contract status, timestamp).
2. Arm the routing trial (`component`) for a short, explicit window.
3. Trigger normal routing activity on your active target.
4. Watch for instability (flapping, mismatches, unresolved route eligibility).
5. Capture an in-window snapshot.
6. End the window by returning authority to `legacy`.
7. Capture a post-window snapshot and write the final verdict.

### Stop immediately if this happens

- route flapping/loop behavior appears,
- required compatibility surface mismatches,
- active target/control-host eligibility is unresolved,
- evidence is missing or stale and you cannot trust the result.

When any of the above occurs: rollback first, investigate second.

### How to score the run

- **PASS:** stable window, no stop conditions, complete fresh evidence, and authority returned to `legacy`.
- **WARN:** no hard failure, but evidence is incomplete/stale or the result is inconclusive.
- **FAIL:** stop condition triggered or rollback failed.

### One-line operator rule

If you are uncertain, call it `WARN`, return to `legacy`, and rerun with cleaner evidence.

## Scope guard (must hold)

- In scope: routing-domain write-path cutover trial only.
- Out of scope: metadata ownership cutover, lighting-orchestration cutover, naming retirement.
- Single-domain rule: no concurrent cutover flags outside routing domain.

## Preflight gates (all required before arm)

1. **Authority baseline gate**
   - `authority_mode` default is `legacy` before trial arm.
   - Reversible arm/disarm path is available and tested in this window.

2. **Parity gate**
   - P2 parity/contract validation is PASS immediately pre-trial.
   - Snapshot freshness is within active window.

3. **Isolation gate**
   - Metadata and lighting cutover toggles are disabled.
   - No parallel migration slices are active.

4. **Rollback gate**
   - Rollback command/path is declared before arm.
   - Operator confirms rollback can be executed without dependency gaps.

5. **Evidence gate (pre-arm baseline)**
   - Baseline capture includes target, route decision, contract validity, and timestamp.

## Arm + observe sequence (bounded)

1. Capture pre-arm baseline evidence.
2. Arm routing-domain trial (`component` authority for bounded window only).
3. Execute deterministic routing actions for selected active target(s).
4. Observe route outcomes and guard signals.
5. Capture in-window evidence snapshot.
6. Disarm or rollback per outcome.
7. Capture post-window state (`authority_mode=legacy` unless explicitly extending window with documented rationale).

## Fail-closed stop conditions (immediate rollback)

- route-write loop/flap detected,
- required compatibility surface mismatch,
- unresolved active target/control-host route eligibility,
- missing or stale evidence for closeout decision.

If any stop condition triggers, execute rollback immediately and mark run window as non-closeout.

## Required evidence fields

- `captured_at`
- `authority_mode` (pre-arm, in-window, post-window)
- `active_target`
- `route_decision`
- `contract_valid`
- compatibility mismatch counters/surfaces
- rollback execution result (if triggered)
- operator verdict (`PASS`, `WARN`, `FAIL`) with rationale

## Copy/paste evidence capture template (one record per run window)

Use this block as a deterministic operator record for each P5-S01 run window.

```text
P5-S01 Run Window Evidence Record
---------------------------------
run_id: 
captured_at: 
operator: 
window_scope: routing-domain only

preflight:
   gate_a_authority_baseline: PASS|WARN|FAIL
   gate_b_parity_precheck: PASS|WARN|FAIL
   gate_c_isolation: PASS|WARN|FAIL
   gate_d_rollback_ready: PASS|WARN|FAIL
   gate_e_prearm_evidence: PASS|WARN|FAIL

pre_arm_snapshot:
   authority_mode: legacy|component
   active_target: 
   route_decision: 
   contract_valid: true|false
   compatibility_mismatch_count: 
   captured_at: 

in_window_snapshot:
   authority_mode: legacy|component
   active_target: 
   route_decision: 
   contract_valid: true|false
   loop_or_flap_detected: true|false
   unresolved_route_eligibility: true|false
   compatibility_mismatch_count: 
   captured_at: 

stop_conditions:
   triggered: true|false
   reason: none|loop_flap|compat_mismatch|unresolved_route|stale_or_missing_evidence|other

rollback:
   executed: true|false
   result: success|failed|not_required
   rollback_command_or_path: 
   rollback_captured_at: 

post_window_snapshot:
   authority_mode: legacy|component
   active_target: 
   route_decision: 
   contract_valid: true|false
   captured_at: 

verdict:
   outcome: PASS|WARN|FAIL
   rationale: 
   closeout_eligible: true|false
```

Template usage rules:

- `PASS` closeout eligibility requires complete/fresh evidence and no triggered stop condition.
- Any triggered stop condition requires immediate rollback and `FAIL` or non-closeout `WARN`.
- If post-window authority remains `component`, include explicit approved extension rationale.

## Gold-standard explicit examples

### Example A — Closeout-eligible PASS (no rollback required)

```text
P5-S01 Run Window Evidence Record
---------------------------------
run_id: p5-s01-routing-2026-04-20T19:12:31Z
captured_at: 2026-04-20T19:36:44Z
operator: cory
window_scope: routing-domain only

preflight:
   gate_a_authority_baseline: PASS
   gate_b_parity_precheck: PASS
   gate_c_isolation: PASS
   gate_d_rollback_ready: PASS
   gate_e_prearm_evidence: PASS

pre_arm_snapshot:
   authority_mode: legacy
   active_target: media_player.spectra_ls_2
   route_decision: route_linkplay_tcp
   contract_valid: true
   compatibility_mismatch_count: 0
   captured_at: 2026-04-20T19:13:02Z

in_window_snapshot:
   authority_mode: component
   active_target: media_player.spectra_ls_2
   route_decision: route_linkplay_tcp
   contract_valid: true
   loop_or_flap_detected: false
   unresolved_route_eligibility: false
   compatibility_mismatch_count: 0
   captured_at: 2026-04-20T19:24:18Z

stop_conditions:
   triggered: false
   reason: none

rollback:
   executed: false
   result: not_required
   rollback_command_or_path: authority disarm to legacy remained prepared but unused
   rollback_captured_at: n/a

post_window_snapshot:
   authority_mode: legacy
   active_target: media_player.spectra_ls_2
   route_decision: route_linkplay_tcp
   contract_valid: true
   captured_at: 2026-04-20T19:35:51Z

verdict:
   outcome: PASS
   rationale: all gates held; no stop conditions; complete and fresh evidence.
   closeout_eligible: true
```

Why this is PASS:

- all preflight gates are PASS,
- no stop condition fired,
- trial authority was bounded and returned to `legacy`,
- route and contract stayed valid with zero compatibility mismatches,
- evidence includes pre-arm/in-window/post-window timestamps.

### Example B — FAIL with mandatory rollback (loop/flap)

```text
P5-S01 Run Window Evidence Record
---------------------------------
run_id: p5-s01-routing-2026-04-20T21:08:04Z
captured_at: 2026-04-20T21:22:39Z
operator: cory
window_scope: routing-domain only

preflight:
   gate_a_authority_baseline: PASS
   gate_b_parity_precheck: PASS
   gate_c_isolation: PASS
   gate_d_rollback_ready: PASS
   gate_e_prearm_evidence: PASS

pre_arm_snapshot:
   authority_mode: legacy
   active_target: media_player.spectra_ls_2
   route_decision: route_linkplay_tcp
   contract_valid: true
   compatibility_mismatch_count: 0
   captured_at: 2026-04-20T21:08:41Z

in_window_snapshot:
   authority_mode: component
   active_target: media_player.spectra_ls_2
   route_decision: route_linkplay_tcp
   contract_valid: true
   loop_or_flap_detected: true
   unresolved_route_eligibility: false
   compatibility_mismatch_count: 0
   captured_at: 2026-04-20T21:13:26Z

stop_conditions:
   triggered: true
   reason: loop_flap

rollback:
   executed: true
   result: success
   rollback_command_or_path: set write authority back to legacy and halt P5-S01 window
   rollback_captured_at: 2026-04-20T21:14:07Z

post_window_snapshot:
   authority_mode: legacy
   active_target: media_player.spectra_ls_2
   route_decision: route_linkplay_tcp
   contract_valid: true
   captured_at: 2026-04-20T21:20:12Z

verdict:
   outcome: FAIL
   rationale: fail-closed stop condition triggered (loop/flap) requiring immediate rollback.
   closeout_eligible: false
```

Why this is FAIL:

- stop condition `loop_flap` triggered in-window,
- rollback was required and executed,
- window cannot be closeout-eligible even with successful rollback.

### Example C — Runtime VERIFIED proof (operator-captured)

```text
P5-S01 Monitor Evidence (runtime)
---------------------------------
captured_at: 2026-04-20T17:16:32.833050-07:00
status: PASS
write_proof: VERIFIED

authority:
   mode: component
   in_progress: false

last_attempt:
   status: noop_already_selected
   reason: Target helper already matches active target
   correlation_id: manual-proof-2
   timestamp: 2026-04-21T00:16:31.422785+00:00

routing:
   active_target: media_player.spectra_ls_2
   active_path: linkplay_tcp
   control_capable: true
   control_hosts: 192.168.10.50
   route_decision: route_linkplay_tcp
   route_reason: Target/path are supported by read-only scaffold mapping

contract_parity:
   contract_valid: true
   missing_required_entities: 0
   parity_unresolved_count: 0
   parity_mismatch_count: 0
   snapshot_fresh: true
   snapshot_age_s: 1.4

operator_interpretation:
   verdict: VERIFIED (accepted)
   note: noop_already_selected is valid write-proof for P5-S01 because guarded write-path executed and correctly detected no state change was needed.
```

Why this is closeout-useful:

- shows a real `VERIFIED` proof event from component authority mode,
- uses an allowed verification status (`noop_already_selected`),
- keeps route/contract/parity/freshness clean and deterministic.

### Example D — Post-window rollback proof (operator-captured)

```text
P5-S01 Post-Window Rollback Evidence
------------------------------------
captured_at: 2026-04-20T17:44:33.180780-07:00
status: WARN
write_proof: READY

authority:
   mode: legacy
   in_progress: false

last_attempt:
   status: authority_set
   reason: Authority mode updated
   correlation_id: authority-44109e8fec17
   timestamp: 2026-04-21T00:44:24.173357+00:00

routing:
   active_target: media_player.kitchen_speakers
   active_path: linkplay_tcp
   control_capable: true
   control_hosts: 192.168.10.51
   route_decision: route_linkplay_tcp
   route_reason: Target/path are supported by read-only scaffold mapping

contract_parity:
   contract_valid: true
   missing_required_entities: 0
   parity_unresolved_count: 0
   parity_mismatch_count: 0
   snapshot_fresh: true
   snapshot_age_s: 9.0

operator_interpretation:
   verdict: rollback confirmed (accepted)
   note: WARN is expected after disarm because authority is intentionally back on legacy; this is required closeout posture unless approved extension is documented.
```

Why this is closeout-useful:

- confirms explicit end-of-window authority return to `legacy`,
- preserves healthy route/contract/parity checks after disarm,
- provides the required post-window proof complementing in-window `VERIFIED` evidence.

## Closeout decision rules

 **PASS (closeout-eligible):** all activation gates held, no stop conditions triggered, evidence complete and fresh.
 **WARN (repeat required):** no hard safety violation, but evidence is incomplete/stale or outcome inconclusive.
 **FAIL (blocked):** any stop condition triggered or rollback failed.

## P1/P2/P3 impact assertion (for this checklist publication)

 **P1:** unchanged (read-only parity surfaces remain intact).
 **P2:** unchanged (parity/contract gate remains authoritative).
 **P3:** unchanged boundary model (single-writer control with explicit rollback).

## Artifact linkage (record in same change window)

 `docs/roadmap/v-next-NOTES.md` (run-window status/evidence note)
 `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md` (slice status/evidence note)
 `docs/CHANGELOG.md` (parity entry)
 `README.md` parity decision (`no material repo-state change` unless explicitly changed)
