<!-- Description: CA-S05 checklist for ESP fallback-listener soak evidence and fail-closed retirement gate evaluation. -->
<!-- Version: 2026.05.05.1 -->
<!-- Last updated: 2026-05-05 -->

# CA-S05 ESP Fallback-Listener Soak Checklist

## Scope

- Slice: `CA-S05`
- Domain: `LC-07` fallback-listener retirement readiness
- Objective: prove fallback listeners are no longer required under normal operation before retirement actions are allowed.

## Lane inventory

- `ESP-L04` `ma_control_hosts_fallback` listener
- `ESP-L05` `ma_control_host_fallback` listener
- `ESP-L06` `ma_control_port_fallback` listener

## Required evidence windows

For each run packet, capture all three windows:

1. `pre_window` baseline
2. `in_window` soak interaction window
3. `post_window` settle verification

Required minimum soak packet fields:

- `window_id`
- `captured_at`
- `authority_mode`
- `route_decision`
- `fallback_apply_count_hosts`
- `fallback_apply_count_host`
- `fallback_apply_count_port`
- `fallback_last_type`
- `fallback_last_age_s`
- `contract_valid`
- `unresolved_required`
- `mismatches`
- `verdict`
- `blocking_reasons`

## Fail-closed gate policy

Retirement readiness is `READY` only when all are true:

1. authority safety: `authority_mode in {legacy, component}` and not unknown
2. route stability: `route_decision` remains supported (`route_linkplay_tcp` in current runtime)
3. contract clean: `contract_valid=true`, `unresolved_required=0`, `mismatches=0`
4. fallback non-use: all fallback apply counters remain `0` for the entire packet window
5. stale safety: `fallback_last_age_s` is either `n/a` or above soak stale threshold while counters remain zero

Any missing required field or parse failure is immediate `BLOCKED`.

## Blocker taxonomy

- `authority_not_safe`
- `route_not_stable`
- `contract_not_clean`
- `fallback_listener_applied`
- `fallback_age_not_ready`
- `missing_required_evidence`

## Two-track disposition

- Runtime track: `compatibility-shimmed` until `READY` packets are sustained
- Component track: `implemented` (component route feed + diagnostics packet contract active)

## Closeout recommendation rule

- Recommend `READY` only with at least one complete pre/in/post packet and zero fallback listener applies.
- Recommend `HOLD` if any packet has warning-only drift but no hard blockers.
- Recommend `BLOCKED` on any blocker taxonomy hit.
