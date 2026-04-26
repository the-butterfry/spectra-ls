<!-- Description: Future planning note for MA-native Spectra audio plugin route and bounded fast-cutover execution. -->
<!-- Version: 2026.04.22.3 -->
<!-- Last updated: 2026-04-22 -->

# NOTES — MA-Native Audio Plugin + Fast Cutover Plan

## Intent

Capture the MA-side plugin/provider path as a **queued next phase** after current UX usefulness closure, so execution can resume later without re-research.

Status: **Active (execution packet published)**

## Decision summary (current best route)

Primary recommendation:

1. Start with a **Music Assistant Player Provider** implementation path for Spectra audio-side control.
2. Keep any HA bridge/plugin linkage as compatibility support, not the primary authority lane.
3. Preserve rollback-safe legacy runtime posture while proving MA-native control-path behavior in bounded windows.

Why this route:

- strongest alignment with MA-native player lifecycle and controls,
- clearer capability mapping and diagnostics ownership,
- better long-term cutover path than stitching behavior through ad hoc service calls.

## Route matrix (fleshed for future pickup)

### Route A — MA Player Provider (recommended first)

- Fit: direct player semantics, transport hooks, capability reporting.
- Pros: clean control ownership, native MA integrations, future-proof for multi-target routing.
- Risks: requires provider lifecycle/scaffold work and strict safety gates.
- Disposition target: **component track implemented**, runtime track compatibility-shimmed.

### Route B — MA Plugin (audio source/receiver adjunct)

- Fit: useful for ingestion/extensions and ecosystem glue.
- Pros: faster proof-of-concept for specific audio-side features.
- Risks: may not own complete player-control semantics alone.
- Disposition target: **component track shim or deferred** unless A is blocked.

### Route C — HA-plugin-mediated control path

- Fit: interoperability bridge only.
- Pros: lowest immediate novelty.
- Risks: ownership ambiguity, duplicate state surfaces, higher drift risk.
- Disposition target: **runtime compatibility shim**, not primary growth lane.

## Fast-cutover packet (bounded, fail-closed)

Execution order when this slice starts:

1. **Pre-window baseline**
   - capture `authority_mode=legacy` + route/contract/parity snapshot,
   - confirm rollback path and stop conditions are armed.
2. **In-window bounded probe**
   - execute MA provider/plugin scaffold probe in dry-run-first posture,
   - verify deterministic control-path/capability diagnostics output.
3. **Post-window rollback proof**
   - return to legacy authority baseline,
   - capture proof packet with no unresolved parity/contract drift.

Stop conditions (mandatory):

- route loop/flap behavior,
- unresolved required contracts,
- ownership ambiguity across runtime/component,
- stale/missing evidence packet.

Execution artifacts (published):

- `docs/testing/raw/p8_s04_ma_plugin_cutover_readiness_monitor.jinja`
- `docs/testing/raw/p8_s04_ma_plugin_cutover_readiness_checklist.md`

## P1/P2/P3 impact framing

- **P1:** unchanged read-only parity source-of-truth surfaces.
- **P2:** unchanged registry/router ownership during planning.
- **P3:** unchanged single-writer boundary until explicit bounded execution windows are started.

## Two-track execution targets (when activated)

- Runtime track: **compatibility-shimmed** (rollback-safe baseline retained).
- Component track: **implemented** for MA-native provider scaffold + diagnostics-first probes.

If strict lock-step is not feasible in one slice, publish explicit defer/shim rationale in changelog + roadmap entry.

## Activation gates (must pass before implementation)

1. P8-S03 UX usefulness closure confirmed.
2. Legacy baseline clean (`authority_mode=legacy`, parity/contract clean).
3. Chosen MA route dispositioned across both tracks (implemented/shimmed/deferred).
4. Pre/in/post evidence template path defined before touching authority behavior.

Immediate execution order (Run-1 starter):

1. Capture `pre` monitor output with `route_selection_confirmed` set and baseline gate PASS.
2. Execute one bounded MA probe in dry-run-first posture.
3. Capture `in` monitor output + artifact reference in checklist.
4. Capture `post` monitor output with rollback proof fields complete.

Immediate execution target (Run-2 strict packet):

- Use `run_id: p8s04-2026-04-22-run2` in the checklist in-window block.
- Keep `selected_path: player_provider` and `dry_run_first: true`.
- Record probe artifact reference in `probe_artifact.artifact_ref`.
- Do not promote in Run-2; promotion remains blocked until post-window rollback proof is captured.

## Deferred implementation checklist

- [ ] Finalize provider scaffold path and package boundary.
- [ ] Publish bounded run-window checklist for P8-S04 execution.
- [ ] Add diagnostics schema for MA-side control-path verdicting.
- [ ] Add rollback verification fields (pre/post authority proof).
- [ ] Capture first dry-run execution artifact and classify PASS/WARN/FAIL.
