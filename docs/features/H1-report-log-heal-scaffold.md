<!-- Description: Deferred implementation scaffold for H1 diagnostics-driven report/log/heal pipeline for Spectra LS P5/P6 operations. -->
<!-- Version: 2026.04.21.1 -->
<!-- Last updated: 2026-04-21 -->

# H1 Scaffold — Diagnostics-Driven Report / Log / Heal (Deferred)

Status: **Scaffolded, deferred for later implementation**

Scope intent: define a concrete, low-risk path to evolve current P5 diagnostics templates into an operational loop that can:

1. **Report** deterministic health/readiness state,
2. **Log** structured runtime evidence records, and
3. **Heal** only bounded, reversible, low-risk conditions.

This document is design-first and execution-ready, but **does not change runtime behavior by itself**.

## Why this exists

Current templates (for example `p5_s02_metadata_functionality_monitor.jinja`) are excellent for ad hoc validation but remain operator-pull diagnostics. H1 introduces a standardized runtime pattern where diagnostics can be periodically harvested and actioned with explicit safety policy.

Primary benefits:

- Reduced manual drift in evidence capture,
- Faster triage with structured event history,
- Controlled recovery for known-safe cases,
- Reusable pattern for P5 closeout and later P6 control-center operations.

## Design constraints (must hold)

- Fail-closed by default.
- No authority expansion by accident.
- No auto-heal writes in ambiguous/unsafe states.
- Reversible actions only in H1.
- Explicit cooldown/reentrancy controls.
- Legacy authority boundary preserved unless explicitly armed in future slices.

## H1 architecture (deferred target)

### A) Report layer (read-only diagnostics)

Sources:

- `sensor.shadow_active_target` attributes:
  - `contract_validation`
  - `metadata_prep_validation`
  - `write_controls`
  - `route_trace`
  - `captured_at`
- Existing Jinja diagnostics templates as human-readable overlays.

Output shape (canonical):

- `status`: `PASS|WARN|FAIL`
- `readiness`: `READY|CAUTION|BLOCKED|NOT_READY`
- `authority_mode`
- `route_decision`
- `contract_valid`
- `missing_required_count`
- `unresolved_required_count`
- `metadata_verdict`
- `metadata_ready`
- `audit_payload_state`
- `missing_audit_fields_count`
- `fresh`
- `captured_at`
- `evaluation_ts`

### B) Log layer (structured record persistence)

Deferred implementation targets:

- HA script/service writes structured JSON-ish records to:
  - persistent notification summary (human-visible),
  - `logbook.log` compact event lines,
  - optional helper-backed rolling state (`input_text`/`sensor` attributes),
  - optional file sink via controlled path (future, if required).

Record schema (minimum):

- `record_id`
- `window_id`
- `slice_id` (e.g. `P5-S02-H1`)
- `status`
- `readiness`
- `authority_mode`
- `route_decision`
- `contract_valid`
- `metadata_verdict`
- `metadata_ready`
- `audit_payload_state`
- `missing_audit_fields`
- `fresh`
- `captured_at`
- `recorded_at`
- `action_taken` (`none|suggested|executed`)
- `action_result`

### C) Heal layer (bounded policy engine)

Allowed in H1:

- non-destructive refresh/validation actions only:
  - `spectra_ls.validate_metadata_prep`
  - `spectra_ls.run_p3_s03_sequence` (legacy mode)
  - `spectra_ls.validate_contracts`

Not allowed in H1:

- authority mode switching,
- non-dry-run metadata authority writes,
- any routing/selection ownership transition.

Heal policy classes:

- `NOOP`: already healthy, log only.
- `SUGGEST`: operator action suggested, no auto execution.
- `AUTO_SAFE`: execute one allowed refresh action with cooldown + audit.
- `BLOCK`: unsafe/ambiguous; log and stop.

## H1 policy matrix (initial)

1. If `fresh=false` and contracts are valid:
   - action: `AUTO_SAFE` → `validate_metadata_prep`
2. If `metadata_verdict=WARN` and `authority_mode=legacy` and no missing/unresolved required:
   - action: `AUTO_SAFE` (single pass) → `run_p3_s03_sequence`
3. If `audit_payload_state=PARTIAL`:
   - action: `SUGGEST` (no auto write)
   - rationale: evidence quality issue; requires bounded rerun
4. If `authority_mode!=legacy` during gate-prep windows:
   - action: `BLOCK`
5. If contracts invalid/missing/unresolved:
   - action: `BLOCK`

## Operational guardrails

- Cooldown: minimum 120s between automated H1 actions.
- Max auto actions per window: 1 (H1 conservative baseline).
- Reentrancy lock: do not execute while prior H1 action is in progress.
- Safety stop:
  - two consecutive `BLOCK` records in same window,
  - mismatch/unresolved growth after auto action,
  - freshness still false after action + grace period.

## Implementation slices (future pickup plan)

### H1-S01 (report-only)

Deliverables:

- canonical report payload service/script (no actions),
- deterministic record schema validation,
- dashboard/logbook visibility.

Exit:

- stable schema + reproducible report records.

### H1-S02 (logging automation)

Deliverables:

- scheduled/triggered logger automation,
- bounded retention strategy,
- record correlation IDs.

Exit:

- no duplicate storms, clear traceability across windows.

### H1-S03 (auto-safe heal, minimal)

Deliverables:

- one-action policy engine for safe refresh actions,
- cooldown/reentrancy lock,
- action audit fields (`before`/`after` status).

Exit:

- stable no-flap behavior, no authority drift, rollback-safe.

### H1-S04 (closeout + handoff)

Deliverables:

- operator runbook updates,
- acceptance checklist,
- explicit defer/escalation criteria for future H2.

Exit:

- closeout evidence published; no unresolved safety blockers.

## Acceptance checklist for future implementation

All required before marking H1 active:

- [ ] deterministic schema contract reviewed
- [ ] safe action allowlist approved
- [ ] cooldown + reentrancy tested
- [ ] authority boundary invariants proven
- [ ] rollback/disarm path documented
- [ ] evidence capture integrated with P5 checklist format

## P1/P2/P3 impact framing

- **P1:** unchanged (read-only parity source remains intact)
- **P2:** unchanged (route/contract validation remains authoritative guard)
- **P3:** unchanged (single-writer boundary preserved; H1 excludes authority expansion)

## Defer rationale

H1 is intentionally deferred to keep current focus on active P5-S02 mechanism and evidence closure. This scaffold exists to avoid rediscovery later and reduce risk when implementation starts.

## Related references

- `docs/testing/raw/p5_s02_metadata_functionality_monitor.jinja`
- `docs/testing/raw/p5_s02_metadata_cutover_run_window_checklist.md`
- `docs/roadmap/v-next-NOTES.md`
- `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`
- `custom_components/spectra_ls/coordinator.py`
