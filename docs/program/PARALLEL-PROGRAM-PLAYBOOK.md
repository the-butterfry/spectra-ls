<!-- Description: Execution playbook for running Spectra runtime and custom component development tracks in strict-parity parallel. -->
<!-- Version: 2026.04.21.3 -->
<!-- Last updated: 2026-04-21 -->

# Spectra Parallel Program Playbook

## Purpose

Provide strict, flexible guardrails for building two systems in parallel:

1. Runtime track (`packages/` + `esphome/`)
2. Custom-component track (`custom_components/spectra_ls/`)

This playbook is designed to prevent detail drift, enforce parity, and keep execution deterministic while still allowing adaptation when new information appears.

## Operating posture

- We are effectively maintaining a parallel fork model in one monorepo.
- Runtime track remains operational source-of-truth until explicit domain cutover.
- Component track matures from shadow parity to primary ownership in controlled phases.
- Every meaningful change must preserve migration safety.

## Non-negotiable invariants

1. No big-bang replacement.
2. No untracked contract changes.
3. No feature considered complete without two-track disposition.
4. No roadmap-only updates without matching `v-next-NOTES.md` state updates.
5. No repo-state changes without explicit README parity decision.

## Anti-detail-trap workflow (required)

When a task arrives, process it in this order:

1. **Classify**: bug fix, contract change, architecture change, migration slice, or docs-only.
2. **Bound**: define one small feature slice with explicit in/out scope.
3. **Dual-map**: record Track A + Track B disposition before implementation.
4. **Implement**: complete the smallest verifiable increment.
5. **Verify**: parity checks + side-effect checks + contract checks.
6. **Sync docs**: update roadmap + v-next + changelog (+ README when required).

If a request is too broad, split into bounded slices first.

## Program phases and control gates

### Phase 0 — Governance + charter

- Policy, roadmap, and v-next phase map documented.
- Slice templates available.
- Parity protocol active.

### Phase 1 — Shadow parity

- Build component scaffolding and read-only parity outputs.
- No write-path behavior.
- Diagnose mismatches early.

### Phase 2 — Registry/router foundation

- Normalize discovery and route metadata.
- Build adapter contract (`linkplay_tcp` first).
- Keep runtime source-of-truth for active control.

### Phase 3 — Guarded dual-write

- Enable one domain at a time.
- Add anti-loop guards, debounces, correlation IDs.
- Halt expansion when instability appears.

### Phase 4 — Capability expansion

- Profiles, action catalog, capability matrix routing.
- Crossfade/balance service path.
- Preserve backward compatibility surfaces.

### Phase 5 — Domain cutover + retirement

- Cut over by domain with rollback gates.
- Retire legacy logic only after soak parity.

### Phase 6 — Sidebar control center productization

- Deliver full operator-facing sidebar surfaces in component track.
- Keep runtime track compatibility-preserved while product UX matures.
- Validate with operator-grade evidence packets before promotion.

### Phase 7 — Component-first authority cutover + legacy sealing

- Execute explicit cutover-readiness gate before any authority flip.
- Flip ownership by bounded domains with reversible rollback controls.
- Seal legacy runtime as maintenance/rollback path, then retire from normal operations.
- Keep net-new sidebar and beyond features component-first by default.

## Feature slice contract (template)

Use this template for every slice:

- **Slice ID**: `P<phase>-S<nn>`
- **Objective**: single measurable outcome
- **Scope in**: explicit files/surfaces
- **Scope out**: explicit exclusions
- **Track A status**: implemented / shim / deferred (+ rationale)
- **Track B status**: implemented / shim / deferred (+ rationale)
- **Parity checks**: list of entities/contracts
- **Side-effect checks**: write calls expected/forbidden
- **Exit criteria**: binary pass/fail conditions
- **Rollback**: exact revert path
- **Docs sync required**: roadmap/v-next/changelog/README

## Definition of done (per slice)

A slice is done only when all are true:

1. Runtime and component dispositions are both recorded.
2. Acceptance and parity checks pass (or explicit deferred mismatch is logged).
3. No unexpected side effects remain.
4. `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md` and `docs/roadmap/v-next-NOTES.md` are synchronized.
5. `docs/CHANGELOG.md` updated.
6. README parity decision explicitly recorded (`required` or `no material change`).

## Parity synchronization protocol (strict)

For architecture/contract/process changes:

- Update all four docs in the same change set:
  1. `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`
  2. `docs/roadmap/v-next-NOTES.md`
  3. `docs/CHANGELOG.md`
  4. `README.md` (or explicit no-change decision)

If one cannot be updated immediately, mark task as incomplete.

## Flex protocol (strict but adaptable)

When new data invalidates current plan:

1. Freeze affected slice expansion.
2. Log a **Plan Delta** entry:
   - what changed,
   - why it changed,
   - what remains stable,
   - new acceptance criteria.
3. Update roadmap + v-next status in same change set.
4. Resume with a re-scoped slice.

## Cadence and checkpoints

### Daily execution cadence

- Start: choose one active slice only.
- Mid-session: checkpoint commit at logical boundary.
- End: parity sync and status ledger update.

### Weekly governance cadence

- Review open slices and blocked risks.
- Re-rank next 3 slices by value and risk.
- Confirm roadmap/v-next remain in lockstep.

## Risks and stop conditions

Pause expansion and fix root cause when any occurs:

- Route/target flapping under dual-write.
- Contract mismatch that affects existing dashboards/scripts.
- Discovery parser drift across payload shapes.
- Documentation parity drift (roadmap vs v-next vs README).

## Program status ledger (maintain continuously)

Use this ledger format in roadmap and v-next references:

| Slice | Phase | Runtime Track | Component Track | Parity | Risk | Status |
| --- | --- | --- | --- | --- | --- | --- |
| P1-S01 | 1 | Implemented | In progress | Pending | Low | Active |

Allowed statuses: `Planned`, `Active`, `Blocked`, `Validated`, `Deferred`, `Closed`.

## Senior-operator note

Execution quality target is team-grade delivery by one operator:

- strict scope discipline,
- root-cause bias,
- explicit contracts,
- reversible steps,
- synchronized documentation.

If uncertain, narrow the slice. If unstable, stop expansion. If contracts shift, sync docs before proceeding.

## Post-P6 Plan Delta (2026-04-21)

- What changed:
  - Phase-6 slices are validated end-to-end; productization baseline is complete.
  - Program focus shifts from UX foundation delivery to authority ownership transition.
- Why it changed:
  - Net-new sidebar and broader control-surface features now require component-first ownership velocity.
  - Legacy remains high quality and trusted but should no longer carry new feature growth burden.
- Stable assumptions:
  - Single-writer guardrails remain mandatory.
  - Runtime track remains rollback-capable until bounded cutover proofs are accepted.
  - Discovery-first contracts and anonymized product posture remain unchanged.
- New exit criteria:
  - P7-S01 cutover-readiness gate PASS with sustained parity + rollback proof.
  - Domain cutover sequence validated without loop/flap regressions.
  - Legacy path explicitly sealed with deprecation/retirement contract documented.
