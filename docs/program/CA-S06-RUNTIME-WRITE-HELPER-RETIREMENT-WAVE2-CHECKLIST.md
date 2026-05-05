<!-- Description: CA-S06 checklist for runtime write/helper retirement wave-2 tail lanes under LC-06. -->
<!-- Version: 2026.05.05.1 -->
<!-- Last updated: 2026-05-05 -->

# CA-S06 Runtime Write/Helper Retirement Wave-2 Checklist

## Scope

- Slice: `CA-S06`
- Domain: `LC-06` runtime retirement wave-2 tails
- Objective: classify and close remaining runtime write/helper legacy tails with deterministic lane evidence.

## Target lanes

- `LC6-L01` active-target writer remnants (post-service migration cleanup)
- `LC6-L03` metadata override helper-storage compatibility lane
- `LC6-L06` runtime metadata resolver read-lane cleanup
- `LC6-L02` override-flag writer lane (explicit defer/retire decision required)

## Required evidence packet fields

- `window_id`
- `captured_at`
- `authority_mode`
- `route_decision`
- `lane_l01_disposition`
- `lane_l03_disposition`
- `lane_l06_disposition`
- `lane_l02_disposition`
- `component_contract_presence`
- `runtime_legacy_surface_presence`
- `blocking_reasons`
- `verdict`
- `next_action`

## Wave-2 pass policy

CA-S06 readiness is `READY` only when:

1. all target lanes have explicit dispositions,
2. non-retired lanes are explicitly `compatibility-shimmed` or `deferred with rationale`,
3. replacement component contract surfaces for active consumers are present,
4. blocker taxonomy is explicit and deterministic,
5. missing required evidence fails closed.

## Blocker taxonomy

- `authority_not_safe`
- `route_not_supported`
- `missing_lane_disposition`
- `component_contract_missing`
- `runtime_tail_unclassified`
- `missing_required_evidence`

## Two-track disposition

- Runtime track: `compatibility-shimmed` until lane-level retirement/defer evidence is closed
- Component track: `implemented` for replacement contract publication and consumer cutover telemetry

## Closeout recommendation rule

- `READY`: all lane dispositions explicit, no blockers, replacement component contracts visible.
- `HOLD`: partial lane classification completed; no hard blockers but closure evidence incomplete.
- `BLOCKED`: any blocker taxonomy hit or required evidence missing.
