<!-- Description: Deterministic operator run-window checklist for Phase 5 Slice-02 metadata-domain cutover readiness and bounded validation (P5-S02). -->
<!-- Version: 2026.04.20.10 -->
<!-- Last updated: 2026-04-20 -->

# P5-S02 Metadata Cutover — Run Window Checklist

Use this checklist to run one bounded **metadata-domain** validation window after P5-S01, with explicit evidence and rollback-first posture.

Primary live monitor template for this slice:

- `docs/testing/raw/p5_s02_metadata_functionality_monitor.jinja`

## Scope guard (must hold)

- In scope: metadata-domain readiness and bounded validation only.
- Out of scope: routing-domain ownership (already validated in P5-S01), lighting orchestration cutover, naming retirement.
- Single-domain rule: no concurrent cutover activity outside metadata domain.

## Important current-state note (no assumptions)

P5-S02 now has a dedicated metadata trial contract service: `spectra_ls.metadata_write_trial`.

Practical consequence:

- P5-S02 remains **gate-prep/readiness-first** and fail-closed by default.
- Legacy/runtime metadata ownership remains authoritative by default (`authority_mode=legacy`).
- Initial mechanism validation is dry-run-first; no metadata write-authority takeover is implied by contract availability alone.

## Implementation process (beyond mirroring, required)

P5-S02 is not limited to parity mirror checks; execute these slices in order:

1. Contract inventory lock
   - list metadata entities/attributes that define ownership boundaries,
   - explicitly mark which remain legacy-authoritative during gate-prep.
2. Mechanism definition
   - define component metadata cutover mechanism/service contract (if absent),
   - include reversible authority posture, audit fields, and fail-closed behavior.
3. Bounded metadata trial
   - execute a short explicit trial window using the defined mechanism,
   - capture pre/in/post evidence and stop-condition behavior.
4. Rollback and closeout
   - confirm safe post-window authority disposition (`legacy` unless approved extension),
   - close only when evidence is complete/fresh and no contract drift is unresolved.

## P5-S02-M1 Mechanism-definition contract (implemented)

Purpose: define the metadata authority mechanism contract *before* any metadata write-authority trial is attempted.

### Service contract (implemented)

- Service name: `spectra_ls.metadata_write_trial`
- Required fields:
  - `mode`: `legacy | component`
  - `window_id`: string
  - `reason`: string
  - `dry_run`: bool (default `true` for first implementation pass)
- Optional fields:
  - `expected_target`: entity_id
  - `expected_route`: string
  - `correlation_id`: string

### Required audit payload fields

- `window_id`
- `requested_mode`
- `effective_mode`
- `requested_at`
- `completed_at`
- `status` (`applied | noop | blocked_* | failed_*`)
- `reason`
- `correlation_id`

Current implementation status:

- implemented as fail-closed contract audit in custom-component coordinator,
- surfaced at `write_controls.metadata_trial_last_attempt` in shadow snapshot,
- dry-run-first semantics active; non-dry-run non-legacy requests are blocked.

### Preflight gates for M1 implementation readiness

1. Authority baseline remains `legacy` and disarm path is documented.
2. P2 parity template PASS in current window.
3. P3-S03 metadata readiness PASS in current window.
4. Stop conditions and rollback command/path are written and testable.
5. Evidence fields above are surfaced in a deterministic snapshot location.

### Stop conditions for M1 trial planning (fail-closed)

- unresolved required metadata contracts,
- parity mismatch drift introduced by mechanism arm/disarm,
- authority transition without matching audit payload,
- inability to prove `effective_mode=legacy` after disarm.

### M1 evidence required before promoting beyond gate-prep

- one dry-run execution record with full audit payload,
- one bounded active-window execution record,
- one post-window rollback proof capture with `effective_mode=legacy`,
- no unresolved required entities and no parity mismatches in final snapshot.

## Preflight gates (all required)

1. **Authority baseline gate**
   - `write_controls.authority_mode` is `legacy` at window start.
   - Rollback/disarm posture is explicit and immediately executable.

2. **Parity gate**
   - `docs/testing/raw/p2_registry_router_verification.jinja` reports PASS in current window.

3. **Metadata readiness gate**
   - `docs/testing/raw/p3_s03_metadata_prep_validation.jinja` reports PASS in current window.
   - `metadata_prep_validation.ready_for_metadata_handoff=true` (or equivalent PASS semantics in rendered output).

4. **Isolation gate**
   - No routing-domain cutover execution in same window.
   - No lighting-domain cutover execution in same window.

5. **Evidence freshness gate**
   - All captured snapshots are fresh and timestamped in this run window.

## Recommended bounded sequence

1. Capture pre-window baseline (`authority`, `route_decision`, `contract_valid`, metadata validation summary).
2. Run metadata validation refresh services:
   - `spectra_ls.validate_metadata_prep`
   - `spectra_ls.metadata_write_trial` (start with `dry_run: true`)
   - optional full diagnostics sequence for metadata lane context: `spectra_ls.run_p3_s03_sequence`
3. Capture in-window metadata readiness evidence.
4. Confirm post-window authority remains or returns to `legacy`.
5. Record verdict (`PASS`/`WARN`/`FAIL`) with rationale.

## Quick-start execution flow (operator-grade)

1. Run service: `spectra_ls.validate_metadata_prep`
2. (Optional context refresh) run service: `spectra_ls.run_p3_s03_sequence`
3. Render `docs/testing/raw/p5_s02_metadata_functionality_monitor.jinja`
4. Capture **pre-window** evidence block.
5. Interact minimally (metadata-context actions only), then re-render monitor.
6. Capture **in-window** evidence block.
7. Confirm/restore `authority_mode=legacy` and capture **post-window** block.

## Stop conditions (fail-closed)

- metadata-prep validation flips FAIL in-window,
- required metadata contract entities become unresolved/missing,
- evidence is stale/missing,
- authority posture drifts without explicit documented mechanism.

When a stop condition triggers: freeze slice advancement, restore/confirm `legacy` authority posture, and mark non-closeout.

## Evidence template (copy/paste)

```text
P5-S02 Run Window Evidence Record
---------------------------------
run_id:
captured_at:
operator:
window_scope: metadata-domain only

preflight:
   gate_a_authority_baseline: PASS|WARN|FAIL
   gate_b_parity_precheck: PASS|WARN|FAIL
   gate_c_metadata_readiness: PASS|WARN|FAIL
   gate_d_isolation: PASS|WARN|FAIL
   gate_e_fresh_evidence: PASS|WARN|FAIL

pre_window_snapshot:
   authority_mode: legacy|component
   route_decision:
   contract_valid: true|false
   metadata_validation_verdict: PASS|WARN|FAIL
   metadata_ready_for_handoff: true|false
   captured_at:

in_window_snapshot:
   authority_mode: legacy|component
   metadata_validation_verdict: PASS|WARN|FAIL
   metadata_ready_for_handoff: true|false
   missing_required_entities_count:
   captured_at:

stop_conditions:
   triggered: true|false
   reason: none|metadata_contract_missing|metadata_validation_fail|stale_or_missing_evidence|authority_drift|other

post_window_snapshot:
   authority_mode: legacy|component
   metadata_validation_verdict: PASS|WARN|FAIL
   metadata_ready_for_handoff: true|false
   captured_at:

verdict:
   outcome: PASS|WARN|FAIL
   rationale:
   closeout_eligible: true|false
```

## Closeout rule for this scaffolded slice

- `PASS` closeout-eligible only when all gates pass and post-window authority posture is explicit/safe (`legacy` unless an approved metadata cutover mechanism is documented).
- `WARN` for inconclusive or incomplete evidence.
- `FAIL` for stop-condition trigger or unsafe authority drift.

## Example A — Closeout-eligible gate-prep evidence (copy structure)

```text
P5-S02 Run Window Evidence Record
---------------------------------
run_id: p5-s02-2026-04-20-a
captured_at: 2026-04-20T10:42:00-07:00
operator: local
window_scope: metadata-domain only

preflight:
   gate_a_authority_baseline: PASS
   gate_b_parity_precheck: PASS
   gate_c_metadata_readiness: PASS
   gate_d_isolation: PASS
   gate_e_fresh_evidence: PASS

pre_window_snapshot:
   authority_mode: legacy
   route_decision: route_linkplay_tcp
   contract_valid: true
   metadata_validation_verdict: PASS
   metadata_ready_for_handoff: true
   captured_at: 2026-04-20T10:39:15-07:00

in_window_snapshot:
   authority_mode: legacy
   metadata_validation_verdict: PASS
   metadata_ready_for_handoff: true
   missing_required_entities_count: 0
   captured_at: 2026-04-20T10:40:37-07:00

stop_conditions:
   triggered: false
   reason: none

post_window_snapshot:
   authority_mode: legacy
   metadata_validation_verdict: PASS
   metadata_ready_for_handoff: true
   captured_at: 2026-04-20T10:41:55-07:00

verdict:
   outcome: PASS
   rationale: all gates passed; metadata lane stayed healthy with explicit legacy authority disposition.
   closeout_eligible: true
```

## Example B — First live evidence capture (Run 1, fill from monitor output)

Use this as the **first real run record** for current P5-S02 gate-prep execution.

```text
P5-S02 Run Window Evidence Record
---------------------------------
run_id: p5-s02-2026-04-20-run1
captured_at: 2026-04-20T__ :__ :__-07:00
operator: local
window_scope: metadata-domain only

preflight:
   gate_a_authority_baseline: 
   gate_b_parity_precheck: 
   gate_c_metadata_readiness: 
   gate_d_isolation: 
   gate_e_fresh_evidence: 

pre_window_snapshot:
   authority_mode: 
   route_decision: 
   contract_valid: 
   metadata_validation_verdict: 
   metadata_ready_for_handoff: 
   captured_at: 

in_window_snapshot:
   authority_mode: 
   metadata_validation_verdict: 
   metadata_ready_for_handoff: 
   missing_required_entities_count: 
   captured_at: 

stop_conditions:
   triggered: 
   reason: 

post_window_snapshot:
   authority_mode: 
   metadata_validation_verdict: 
   metadata_ready_for_handoff: 
   captured_at: 

verdict:
   outcome: 
   rationale: 
   closeout_eligible: 
```

Run-1 fill hints (source = `p5_s02_metadata_functionality_monitor.jinja`):

- `authority_mode` ← `write_controls.authority_mode`
- `route_decision` ← `route_trace.decision`
- `contract_valid` ← `contract_validation.valid`
- `metadata_validation_verdict` ← `metadata_prep_validation.verdict`
- `metadata_ready_for_handoff` ← `metadata_prep_validation.ready_for_metadata_handoff`
- `missing_required_entities_count` ← `metadata_prep_validation.missing_required | length`

## Example C — Operator-captured runtime baseline (2026-04-20)

```text
P5-S02 Run Window Evidence Record
---------------------------------
run_id: p5-s02-2026-04-20-run1
captured_at: 2026-04-20T17:59:21.972073-07:00
operator: local
window_scope: metadata-domain only

preflight:
   gate_a_authority_baseline: PASS
   gate_b_parity_precheck: PASS
   gate_c_metadata_readiness: PASS
   gate_d_isolation: PASS
   gate_e_fresh_evidence: PASS

pre_window_snapshot:
   authority_mode: legacy
   route_decision: route_linkplay_tcp
   contract_valid: true
   metadata_validation_verdict: PASS
   metadata_ready_for_handoff: true
   captured_at: 2026-04-20T17:59:21.972073-07:00

in_window_snapshot:
   authority_mode: legacy
   metadata_validation_verdict: PASS
   metadata_ready_for_handoff: true
   missing_required_entities_count: 0
   captured_at: 2026-04-20T17:59:21.972073-07:00

stop_conditions:
   triggered: false
   reason: none

post_window_snapshot:
   authority_mode: legacy
   metadata_validation_verdict: PASS
   metadata_ready_for_handoff: true
   captured_at: 2026-04-20T18:08:32.691994-07:00

verdict:
   outcome: PASS
   rationale: operator-captured pre and post window monitor outputs both report PASS/READY with clean contract/parity/freshness and explicit legacy authority disposition.
   closeout_eligible: true
```

## Post-window proof capture (single remaining closure step)

When you are ready to close this run, perform one final monitor render and update the record with:

1. `post_window_snapshot.authority_mode`
2. `post_window_snapshot.metadata_validation_verdict`
3. `post_window_snapshot.metadata_ready_for_handoff`
4. `post_window_snapshot.captured_at`
5. final `verdict.closeout_eligible`

Closeout rule for this run remains strict:

- `closeout_eligible=true` only when post-window snapshot confirms safe authority posture (`legacy`) and metadata/contract/parity conditions remain healthy.

## Example D — Post-window completion block (fill from final render)

```text
P5-S02 Run Window Evidence Record (Completion)
----------------------------------------------
run_id: p5-s02-2026-04-20-run1
completion_captured_at: 2026-04-20T18:08:32.691994-07:00

post_window_snapshot:
   authority_mode: legacy
   metadata_validation_verdict: PASS
   metadata_ready_for_handoff: true
   captured_at: 2026-04-20T18:08:32.691994-07:00

verdict:
   outcome: PASS
   rationale: final post-window render confirms safe legacy authority posture and stable metadata/contract/parity gates.
   closeout_eligible: true
```

## Example E — Run-3 evidence consolidation (legacy + component posture check)

```text
P5-S02 Run Window Evidence Record
---------------------------------
run_id: p5s02-run3
captured_at: 2026-04-20T21:39:22.603783-07:00
operator: local
window_scope: metadata-domain only

pre_window_snapshot:
   authority_mode: legacy
   route_decision: route_linkplay_tcp
   contract_valid: true
   metadata_validation_verdict: WARN
   metadata_ready_for_handoff: false
   captured_at: 2026-04-20T21:23:30.311234-07:00

in_window_snapshot:
   authority_mode: legacy
   metadata_validation_verdict: WARN
   metadata_ready_for_handoff: false
   metadata_trial_status: blocked_metadata_not_ready
   metadata_trial_window_id: p5s02-run3
   metadata_trial_dry_run: true
   metadata_trial_reason: Metadata prep validation is not PASS/ready; fail-closed
   captured_at: 2026-04-20T21:24:30.309943-07:00

post_window_snapshot:
   authority_mode: legacy
   metadata_validation_verdict: PASS
   metadata_ready_for_handoff: true
   gate_score: 9/9
   captured_at: 2026-04-20T21:39:22.603783-07:00

component_policy_check:
   authority_mode: component
   metadata_validation_verdict: WARN
   metadata_ready_for_handoff: false
   blocking_reason: authority_mode_not_legacy
   captured_at: 2026-04-20T21:40:20.772778-07:00

verdict:
   outcome: PASS (gate-prep)
   rationale: legacy-mode lane reached PASS/READY under active metadata conditions with clean contract/parity and explicit fail-closed dry-run behavior when not ready; component-mode WARN remains expected policy posture while metadata ownership is still legacy.
   closeout_eligible: true (gate-prep evidence)
```

## Artifact linkage

- `docs/roadmap/v-next-NOTES.md`
- `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`
- `docs/CHANGELOG.md`
- `README.md` parity decision (`no material repo-state change` unless explicitly changed)
