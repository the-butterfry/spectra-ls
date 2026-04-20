<!-- Description: Entry checklist for Spectra LS Phase 4 Slice-03 crossfade/balance diagnostics-first execution. -->
<!-- Version: 2026.04.20.2 -->
<!-- Last updated: 2026-04-20 -->

# F4-S03 Crossfade/Balance Entry Checklist (Diagnostics-First)

Purpose: start Phase 4 Slice-03 with explicit preflight and acceptance criteria, while preserving legacy ownership boundaries and no-authority-expansion guarantees.

## Current lane status

- F4-S01: sealed (`PASS 6/6` in legacy mode).
- F4-S02: sealed (`PASS 7/7` in legacy mode).
- F4-S03: active next slice (entry checklist only; implementation evidence pending).

## Preflight gates (must pass before implementation closeout work)

1. Authority baseline remains diagnostics-safe:
   - `write_controls.authority_mode = legacy`
   - no ownership cutover writes enabled.
2. F4 dependency baseline remains healthy:
   - latest F4-S01 validation still `PASS`.
   - latest F4-S02 validation still `PASS`.
3. Runtime contract baseline remains healthy:
   - `contract_validation.valid = true` on active target snapshot.
4. Route baseline is explicit in capture:
   - route decision present in `route_trace`.

## F4-S03 implementation scope guardrails

- Scope target: crossfade/balance **service contract + diagnostics-first path** only.
- Keep runtime track authoritative for control behavior during this slice.
- Component track adds normalized slider-domain contract surfaces (planning target: directional domain such as `-100..100`) with diagnostics visibility.
- No authority expansion: any diagnostics output must continue to validate legacy write authority for this lane.
- No broad refactor/no naming churn during the slice.

## Closeout evidence requirements (slice not complete until captured)

1. Runtime artifact captured from an F4-S03 raw validation output (PASS/WARN/FAIL).
   - Preferred artifact path: `docs/testing/raw/f4_s03_crossfade_balance_validation.jinja`
2. Explicit gate readout includes:
   - contract presence/validity,
   - crossfade/balance contract surface presence,
   - no-authority-expansion (`legacy`) status,
   - diagnostics freshness.
3. Closeout decision recorded in:
   - `docs/roadmap/v-next-NOTES.md`
   - `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`
   - `docs/CHANGELOG.md`
4. README parity note included (`no material repo-state change` unless operator workflow materially changes).

## Operator expectations during diagnostics-only sequencing

- Action calls are expected to be quiet in UI (no strong toast/modal guarantees).
- Confirmation source-of-truth is rendered template output and shadow entity attributes.
- Missing F4-S03 service surfaces during entry are acceptable before implementation starts; treat as expected pre-implementation baseline, not a runtime regression.
