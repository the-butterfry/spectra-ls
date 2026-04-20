<!-- Description: Operator runbook for small soak validation of Spectra LS P3-S01 and P3-S02 one-shot sequences. -->
<!-- Version: 2026.04.19.1 -->
<!-- Last updated: 2026-04-19 -->

# P3 S01+S02 Small Soak Protocol (`spectra_ls`)

Purpose: collect enough runtime evidence to graduate P3-S02 from **Active/Pending** without premature closure.

## Preconditions (must be true before cycle 1)

- `p3_s01_guarded_write_validation.jinja` currently reports PASS in `component` authority mode.
- `p3_s02_selection_handoff_validation.jinja` currently reports PASS.
- Active route decision is `route_linkplay_tcp`.
- Contract validation remains `ready=true`, `valid=true`.

## Scope

- Small soak only: **3 target-switch cycles** across at least **2 distinct targets** (prefer 3 if available).
- No forced guard bypass by default (`force=false`).
- Sequence-first validation, no manual patching during soak.

## Per-cycle steps (repeat 3x)

1. Switch to next target in `input_select.ma_active_target` options.
2. Run action: `spectra_ls.run_p3_s01_sequence`
   - Recommended fields: `mode=component`, unique `correlation_id`, `force=false`.
3. Render template: `docs/testing/raw/p3_s01_guarded_write_validation.jinja`.
4. Run action: `spectra_ls.run_p3_s02_sequence`
   - Recommended fields: `mode=component`, `run_write_trial=false` (baseline handoff check).
5. Render template: `docs/testing/raw/p3_s02_selection_handoff_validation.jinja`.
6. Record cycle result in the table below.

## Optional stress pass (after baseline 3/3 PASS)

Run one additional S02 cycle with `run_write_trial=true` and a unique `correlation_id`.

## Cycle evidence log

Use this fill-in template while running the soak:

```text
Cycle 1
Target:
S01 result / last_status:
S02 result / handoff_verdict:
Missing scripts / missing automation IDs:
Notes:

Cycle 2
Target:
S01 result / last_status:
S02 result / handoff_verdict:
Missing scripts / missing automation IDs:
Notes:

Cycle 3
Target:
S01 result / last_status:
S02 result / handoff_verdict:
Missing scripts / missing automation IDs:
Notes:
```

## Pass criteria (graduation candidate)

All must hold:

1. S01 PASS in every cycle.
2. S02 PASS in every cycle.
3. Route decision remains `route_linkplay_tcp` in every cycle.
4. No parity regressions (`unresolved_sources=0`, `mismatches=0`).
5. S02 compatibility remains clean (`missing_scripts=0`, `missing_automation_ids=0`) in every cycle.
6. No unexpected `write_error` or persistent guard-failure loop statuses.

## Warn criteria (hold in Active/Pending)

Any of:

- Intermittent WARN that self-recovers but repeats across cycles.
- Transient helper/options drift or contract payload gaps.
- One-off guard blocks that are not explained by intended debounce/reentrancy behavior.

## Fail criteria (block closure)

Any of:

- Any cycle with S01 FAIL or S02 FAIL.
- Persistent non-eligible route decisions.
- Missing compatibility scripts/automation IDs in any cycle.
- Parity drift (`unresolved_sources>0` or `mismatches>0`) that persists after refresh sequence.

## Closure recommendation template

- **Recommend P3-S02 closure:** Yes/No
- **Evidence summary:** `PASS x/3` cycles (or explain deviation)
- **Open blockers:** none / list
- **Next action:** close P3-S02 or continue soak/remediation
