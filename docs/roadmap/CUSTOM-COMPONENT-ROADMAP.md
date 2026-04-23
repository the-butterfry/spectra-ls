<!-- Description: Specification and phased roadmap for the Spectra LS custom Home Assistant component developed in parallel with existing runtime. -->
<!-- Version: 2026.04.22.109 -->
<!-- Last updated: 2026-04-22 -->

# Spectra LS Custom Component — Specification + Roadmap

## Purpose

Define a production-grade `custom_components/spectra_ls` program that runs **in parallel** with the existing HA package + ESPHome runtime, then incrementally migrates ownership without breaking deployed contracts.

Execution playbook reference: `docs/program/PARALLEL-PROGRAM-PLAYBOOK.md`.

## Product Principles (non-negotiable)

- Spectra is anonymized and user-portable by default.
- Discovery-first adaptation to each user’s HA entity topology.
- Capability-mapped routing and behavior gating.
- Minimal hardcoded install-specific entity IDs.
- Backward-compatible migration before replacement.
- Audio and lighting are first-class depth domains, while input primitives remain mappable for broader Home Assistant control domains.

## Scope

### In scope

- Home Assistant custom integration (`custom_components/spectra_ls`) for orchestration, discovery, routing, diagnostics, profiles, and migration tooling.
- Parallel operation with current contracts in:
  - `packages/ma_control_hub/*`
  - `packages/spectra_ls_lighting_hub.yaml`
  - `esphome/spectra_ls_system/packages/*`
- Phase mapping and status alignment in `v-next-NOTES.md`.

### Out of scope (initially)

- Immediate removal of current template/package logic.
- Breaking helper/entity ID renames.
- Premature multi-repo split before maturity gates.

## Current-state contract inventory (v.now)

### Runtime control/routing surfaces in use today

- Active target + route helpers (`ma_active_target`, `ma_control_hosts`, `ma_control_host`, `ma_active_control_path`, `ma_active_control_capable`).
- Metadata resolution surfaces (`ma_meta_candidates`, `ma_meta_resolver`, `now_playing_*`).
- Lighting selector/catalog surfaces (`control_board_room/target`, `control_board_*_options`, `control_board_target_entity_id`, room/target HS/on states).
- ESPHome dependencies via substitutions and HA entity reads in:
  - `spectra-ls-audio-tcp.yaml`
  - `spectra-ls-lighting.yaml`
  - `spectra-ls-ui.yaml`

### Known constraints

- Legacy runtime IDs (`control_board_*`) are still deployed contracts.
- Parser compatibility must handle native object payloads + string JSON payloads.
- Only supported direct routed control path now: `linkplay_tcp`.

## Target architecture (component control plane)

## Component domains

1. **Registry domain**
   - Discovery-first normalized target catalog.
   - Per-target metadata: `hardware_family`, `control_path`, `control_capable`, `capabilities`.

2. **Routing domain**
   - Adapter-based dispatch per `control_path`.
   - Unsupported paths visible for diagnostics, not direct-routed.

3. **Mode/policy domain**
   - Hardware-first mode semantics + fallback menu semantics.
   - Selector/control-class policy contracts.

4. **Profile domain**
   - User-facing behavior bundles (lighting/audio sensitivity, routing preference, UX mode).

5. **Diagnostics domain**
   - Health states, contract parity checks, route traces, and explainability surfaces.

6. **Migration domain**
   - Schema-versioned config entries/options.
   - Compatibility shims and deprecation gates.

## Feature set

### v.now (must support during migration)

- Contract parity surfaces for current ESPHome + package expectations.
- Discovery-first target enumeration and route classification.
- Legacy helper/entity compatibility outputs.
- Basic route diagnostics + parity validation services.
- Dual-write guard rails to avoid loop flapping.

### v.future (planned expansion)

- Full programmable action catalog (arm/confirm/cooldown/safety/audit).
- Profile system (room, target, UX, sensitivity policies).
- Capability matrix routing (feature-level gating beyond boolean control-capable).
- Multi-family adapter expansion beyond `linkplay_tcp`.
- Crossfade/balance slider service layer:
  - multi-room: room-to-room weighted balance
  - single-room: L/R balance
- Guided setup and onboarding UX in component flows.
- Full HA sidebar control-center experience (setup/tuning/defaults/overrides/mapped-environment pages).
- Generalized analog-control mappings for broader HA actions (scenes, scripts, climate routines, safety toggles, and domain-specific automations).

## Product positioning contract (README + v-next parity)

- Spectra L/S is the analog tactile control surface for Home Assistant.
- Audio + lighting retain primary depth and optimization focus.
- Physical controls are mappable primitives for broader Home Assistant actions beyond those two flagship domains.

## Phased implementation roadmap

## Program status ledger

| Slice | Phase | Runtime Track | Component Track | Parity | Risk | Status |
| --- | --- | --- | --- | --- | --- | --- |
| P1-S01 | 1 | Implemented (legacy source-of-truth retained) | Implemented (read-only shadow parity) | Implemented | Low | Implemented |
| P2-S01 | 2 | Implemented (legacy route contracts retained) | Implemented (registry/router scaffold; read-only) | Implemented | Low | Implemented |
| P2-S02 | 2 | Implemented (legacy route contracts retained) | Implemented (deterministic validation hardening + P2 diagnostics closure) | Implemented | Low | Implemented |
| P3-S01 | 3 | Validated (legacy write authority retained behind switch) | Validated (guard framework + manual routing write trial services) | Validated | Medium | Validated |
| P3-S02 | 3 | Validated (selection scripts/automations compatibility shim validation) | Validated (one-shot validation sequence + selection handoff diagnostics) | Validated (single-capable waiver) | High | Validated |
| P3-S03 | 3 | Validated (metadata ownership explicitly deferred to legacy compatibility mode) | Validated (metadata prep diagnostics + one-shot sequence + listener-safe validation template) | Validated (diagnostics-only) | Medium | Validated |
| F4-S01 | 4 | Validated (compatibility contracts retained; no ownership cutover) | Validated (capability matrix + profile schema diagnostics scaffolding) | Validated (diagnostics-only) | Medium | Validated |
| F4-S02 | 4 | Validated (legacy action ownership retained; diagnostics-only) | Validated (programmable action-catalog safety skeleton + dry-run diagnostics) | Validated (diagnostics-only) | Medium | Validated |
| F4-S03 | 4 | Validated (legacy crossfade/balance behavior remains authoritative) | Validated (crossfade/balance diagnostics scaffold + validation sequence) | Validated (diagnostics-only) | Medium | Validated |
| P5-S01 | 5 | Validated (legacy retained as rollback authority path; post-window rollback proof captured) | Validated (routing-domain run-window execution with VERIFIED in-window proof) | Validated (in-window VERIFIED + post-window legacy rollback) | Medium | Validated |
| P5-S02 | 5 | Validated (legacy metadata ownership retained; bounded closeout evidence accepted) | Validated (metadata-domain gate-prep/readiness validation execution completed with consolidated PASS evidence) | Validated (Run-1 + Run-2 closeout packet) | Medium | Validated |
| P5-S03 | 5 | Validated (legacy lighting orchestration retained with safe post-window authority proof) | Validated (lighting-domain run-window checklist execution completed with PASS closeout evidence) | Validated (Run-1 pre/in/post packet) | Medium | Validated |
| P5-S04 | 5 | Validated (phase-exit closeout governance completed; no runtime ownership expansion) | Validated (cross-slice evidence packet accepted + Phase-6 handoff gating complete) | Validated (PASS/READY 7/7 closeout packet) | Medium | Validated |
| P6-S01 | 6 | Validated (legacy/runtime contracts preserved; no authority expansion) | Validated (HA sidebar control center foundation with read-only mapped-environment baseline proven) | Validated (PASS/READY 6/6 closeout packet) | Medium | Validated |
| P6-S02 | 6 | Validated (legacy/runtime contracts preserved; no ownership cutover) | Validated (control-center settings contract via options flow, service path, and diagnostics visibility proven) | Validated (PASS/READY 4/4 settings packet) | Medium | Validated |
| P6-S03 | 6 | Validated (legacy/runtime contracts preserved; no authority expansion) | Validated (control-input execution skeleton with dry-run-first safety + attempt diagnostics proven) | Validated (execution-lane dry-run proof accepted) | Medium | Validated |
| P6-S04 | 6 | Validated (legacy/runtime contracts preserved; no ownership cutover) | Validated (execution-lane validation monitor/checklist with accepted closeout packet) | Validated (PASS/READY 5/5 dry-run-first packet) | Medium | Validated |
| P7-S01 | 7 | Validated (legacy compatibility/rollback baseline confirmed at pre-flip gate) | Validated (component-first cutover-readiness gate accepted) | Validated (Run-2 PASS/READY 4/4) | High | Validated |
| P7-S02 | 7 | Validated (legacy retained as bounded rollback authority with post-window rollback-safe proof accepted) | Validated (first bounded authority-flip execution lane complete) | Completed (Run-1 pre/in/post PASS) | High | Validated |
| P7-S03 | 7 | Validated (legacy retained as rollback-safe metadata authority baseline with post-window proof accepted) | Validated (bounded metadata-domain authority-flip execution lane complete) | Completed (Run-1 pre/in PASS + Run-2 post PASS) | High | Validated |
| P7-S04 | 7 | Validated (rollback-safe legacy authority baseline preserved at closeout capture) | Validated (phase-exit closeout packet completed and accepted) | Completed (Run-1 closeout PASS/READY 4/4) | High | Validated |
| P8-S01 | 8 | Validated (legacy sealed baseline readiness gate completed with pre/in/post PASS packet) | Validated (post-cutover governance/readiness lane completed for starter gate) | Completed (Run-1/Run-2/Run-3 PASS; promoted) | High | Validated |

## P1/P2 validation snapshot (2026-04-19)

Validated now:

- P2 verification template score observed at `8/8` with deterministic route decision and contract-valid diagnostics.
- Component diagnostic surfaces now include `registry`, `route_trace`, `contract_validation`, and `captured_at` freshness gating.
- Legacy source-of-truth surfaces remain in place (`sensor.ma_*` / `binary_sensor.ma_*`) and component remains read-only.

Known evidence boundary (explicit):

- Validation is strong for documented parity templates and code-surface audit, but live HA runtime can still drift due to environment timing/restart state.
- Any Phase 3 write-path activation must re-run parity templates and include fresh proof artifacts in the same change set.

Latest runtime proof artifact (2026-04-19):

- P2 verification output: `PASS`, score `8/8`.
- Route trace decision: `route_linkplay_tcp`.
- Contract validation: `ready=true`, `valid=true`, `missing_required=0`.
- Parity drift: `unresolved_sources=0`, `mismatches=0`.
- Snapshot freshness: `true` (captured-at age within threshold).

## Phase 0 — Charter + contract freeze

- Publish this roadmap and baseline contract inventory.
- Add required parallel-program policy in `.github/copilot-instructions.md`.
- Add synchronized phase section in `v-next-NOTES.md`.

### Phase 0 exit criteria

- Policy, roadmap, and v-next phase map are all present and consistent.

## Phase 1 — Skeleton + shadow mode (read-only)

- Scaffold:
  - `custom_components/spectra_ls/manifest.json`
  - `__init__.py`, `const.py`, `config_flow.py`, `coordinator.py`, `diagnostics.py`
- Implement read-only parity entities for route/meta/status outputs.
- Add parity diagnostics (`legacy` vs `component`) with explicit mismatch reporting.

### Phase 1 exit criteria

- Shadow entities publish stable outputs with no control-path side effects.

### Phase 1 Slice-01 (Draft) — Shadow parity for routing core

#### Slice objective

Implement the first read-only parity slice for routing core visibility without introducing any write-path behavior.

#### Scope (in)

- Scaffold component core files if missing:
  - `custom_components/spectra_ls/manifest.json`
  - `custom_components/spectra_ls/__init__.py`
  - `custom_components/spectra_ls/const.py`
  - `custom_components/spectra_ls/config_flow.py`
  - `custom_components/spectra_ls/coordinator.py`
  - `custom_components/spectra_ls/diagnostics.py`
- Publish read-only parity sensors for these legacy surfaces:
  - `sensor.ma_active_target`
  - `sensor.ma_active_control_path`
  - `binary_sensor.ma_active_control_capable`
  - `sensor.ma_control_hosts`

#### Scope (out)

- No control writes/services changing active target or host route.
- No helper/entity ID migrations.
- No dual-write behavior in this slice.

#### Runtime and component track disposition (required)

- **Track A (current runtime):** `implemented` (existing package logic remains source of truth)
- **Track B (custom component):** `implemented` as read-only shadows
- **Parity note:** required before slice close (pass/fail + mismatch list)

#### Acceptance criteria

1. Component parity entities update within normal HA template cadence.
2. Values match legacy semantics for non-error states.
3. On unresolved source data, parity entities degrade with explicit diagnostics (not silent fallback writes).
4. No side-effect service calls are emitted by the component in this slice.
5. Existing dashboards/scripts that rely on legacy entities continue unchanged.

#### Verification checklist

- Compare legacy and component values for all four parity surfaces across:
  - boot/reload,
  - active playback,
  - idle/no-target,
  - transient ambiguity.
- Confirm no `climate`/`media_player`/`light` write services are called by the component.
- Capture one parity report artifact in diagnostics output.

#### README parity decision template (required)

- `README parity: required` when architecture/operator workflow meaningfully changes.
- `README parity: no material repo-state change` when slice is read-only internal scaffolding.

## Phase 2 — Registry + router foundation

- Implement normalized target registry.
- Implement adapter router with `linkplay_tcp` support only.
- Add maintenance services:
  - `spectra_ls.rebuild_registry`
  - `spectra_ls.validate_contracts`
  - `spectra_ls.dump_route_trace`

### Phase 2 exit criteria

- Registry and router are deterministic and discovery-first on clean installs.

## Phase 3 — Controlled write path (dual-write)

- Slice into explicit sub-phases to prevent blended ownership:
  - **P3-S01 (Routing write path only):** target + host route writes behind a runtime authority switch.
  - **P3-S02 (Selection handoff):** controlled handoff of target-selection orchestration with legacy compatibility shims.
  - **P3-S03 (Metadata prep):** metadata ownership instrumentation and parity checks, no premature full metadata cutover.
- Preserve existing helper/script endpoints expected by ESPHome and dashboards.
- Add anti-loop safeguards (correlation IDs/debounce windows/reentrancy guards + single-writer guard).
- Keep fallback policy explicit: no silent static-fallback enablement when fallback is configured off.

### P3-S01 implementation status (2026-04-19)

Implemented in component:

- Single-writer authority mode control (`legacy` default, `component` opt-in) via service contract.
- Guarded manual route-write trial service bound to route-trace decision eligibility.
- Loop/flap protections: authority gate, debounce window, reentrancy guard, and correlation IDs.
- Write-control diagnostics exposed in shadow entity attributes and coordinator snapshot.

Closeout status (2026-04-20):

- runtime trial and soak evidence captured under `component` authority mode,
- no remaining P3-S01 parity/soak blockers,
- slice sealed in final P3 closeout checkpoint below.

### P3-S02 implementation checkpoint (2026-04-19)

Implemented in component:

- one-shot `run_p3_s02_sequence` orchestration for selection-handoff validation,
- optional guarded write-trial execution inside the sequence (explicit operator toggle),
- snapshot diagnostics payload `selection_handoff_validation` for helper/options + legacy compatibility shim checks,
- raw operator template for S02 verdict checks (`docs/testing/raw/p3_s02_selection_handoff_validation.jinja`).

Closeout decision (2026-04-19):

- sustained runtime evidence captured with stable S01/S02 PASS behavior and clean compatibility/parity signals.
- soak gate satisfied at baseline (3 PASS cycles across 5 attempts) with expected non-capable soft-skip behavior.
- explicit single-capable-topology waiver applied for the distinct PASS-target gate.
- future reruns should use `docs/testing/raw/p3_s01_s02_closure_gate_check.jinja` for deterministic repeatable closure evidence.

Latest runtime proof artifact (2026-04-19):

- Template verdict: `PASS` (`p3_s02_selection_handoff_validation.jinja`).
- Authority/route: `component` + `route_linkplay_tcp`.
- Contract validation: `ready=true`, `valid=true`.
- Handoff diagnostics: `payload_ready=true`, `verdict=PASS`, `helper_exists=true`, `target_in_options=true`, `missing_scripts=0`, `missing_automation_ids=0`.

Latest soak runtime artifact (2026-04-19):

- Automated script result: `Spectra soak complete` from `script.spectra_p3_soak_one_shot`.
- Soak evidence: `3` successful cycles in `5` attempts.
- PASS-cycle diagnostics: `route=route_linkplay_tcp`, `contract_valid=True`, `handoff=PASS`.
- Compatibility/parity maintained: `missing_scripts=0`, `missing_automation_ids=0`, `unresolved_sources=0`, `mismatches=0`.
- Non-capable target behavior: soft-skips on `route=defer_not_capable` observed and tolerated by soak automation.
- Closure gate note: baseline soak stability met; distinct PASS-target gate remains open unless explicitly waived for single-capable-topology operation.

### Stage report snapshot — ownership + readiness (2026-04-19)

- Current ownership boundary:
  - **Legacy runtime (`packages/ma_control_hub/*.inc`) still owns** broad production selection/control orchestration.
  - **Component track (`custom_components/spectra_ls`) owns** parity/diagnostics, S01/S02 one-shot orchestration, and guarded routing write-trial scaffolding.
- Readiness call:
  - **Closure-ready and sealed for P3-S02** with final soak evidence (`3/3` successful cycles in `4` attempts, `distinct_pass_targets=2`).
  - Distinct PASS-target gate satisfied without waiver in the final run.

### P3-S03 implementation checkpoint (2026-04-19)

Implemented in component:

- coordinator metadata-prep diagnostics payload (`metadata_prep_validation`) with deterministic readiness verdict,
- explicit metadata contract checks (`sensor.ma_active_meta_entity`, `sensor.now_playing_entity`, `sensor.now_playing_state`, `sensor.now_playing_title`, `sensor.ma_meta_candidates`),
- new services: `spectra_ls.validate_metadata_prep` and `spectra_ls.run_p3_s03_sequence`,
- raw validation template for repeatable operator evidence: `docs/testing/raw/p3_s03_metadata_prep_validation.jinja`.

Closeout decision (2026-04-19):

- runtime S03 validation captured at `PASS` with full gate score (`7/7`) and `ready_for_metadata_handoff=true`,
- metadata contract checks report zero missing required entities/keys,
- explicit compatibility boundary retained: metadata ownership remains legacy/runtime (component remains diagnostics/validation lane),
- runtime route/selection context outside the S03 target window can remain non-cutover (`defer_not_capable`, legacy authority, S02 FAIL) and is not a P3-S03 diagnostics blocker.

Latest runtime proof artifact (2026-04-19):

- Template verdict: `PASS` (`docs/testing/raw/p3_s03_metadata_prep_validation.jinja`).
- Gate score: `7/7`.
- Metadata-prep readiness: `true`.
- Contract detail: `missing_required=0`, `missing_keys=[]`.

Final runtime proof snapshot (2026-04-19 22:51 local):

- Active target/path: `media_player.spectra_ls_2` / `linkplay_tcp`.
- Metadata probes resolved in validation output (`active_meta_entity`, `now_playing_entity`, `now_playing_state`, `now_playing_title`).
- All S03 gates true with `missing_required=0`.
- Compatibility boundary retained by design: non-cutover route/selection context (`defer_not_capable`, legacy authority, S02 FAIL) does not block diagnostics-only S03 closeout.

### P3-H1 second-pass hardening checkpoint (2026-04-19)

Implemented reliability hardening with no authority expansion:

- broader coordinator state-listener coverage for helper/metadata control surfaces,
- stricter metadata-candidate readiness checks to reject empty/non-meaningful candidate payloads,
- closure gate consistency guard for soak attempts versus pass cycles,
- freshness gates added in P3 raw validation templates to avoid stale PASS interpretations.

Track disposition:

- Runtime track: implemented as compatibility-preserving hardening only.
- Component track: implemented in diagnostics/validation lane.
- Parity note: no contract rename/cutover; re-run P3 templates for refreshed runtime evidence on next validation cycle.

### P3-H2 closure-gate soak parity checkpoint (2026-04-19)

Closeout template correctness update:

- add explicit soak-evidence input `observed_parity_ok` to closure gate,
- use observed parity when `evaluation_mode=soak_evidence` while still exposing runtime parity as a diagnostic companion signal,
- maintain `runtime` mode behavior unchanged for strict live validation.

### P3-H3 closure-gate fail-closed checkpoint (2026-04-19)

Closure integrity hardening:

- default closure inputs changed to fail-closed values,
- soak-evidence mode now requires explicit evidence provenance/freshness fields (source, reference, collected-at <=24h),
- invalid/missing provenance now hard-fails closure to enforce evidence-backed sign-off quality.

### P3 final closeout checkpoint (2026-04-20)

Final sealing evidence captured:

- Soak automation completion: `Spectra soak complete` with `3` successful cycles in `4` attempts and `distinct_pass_targets=2`.
- PASS-cycle diagnostics remained deterministic: `route=route_linkplay_tcp`, `contract_valid=True`, `handoff=PASS`.
- Closure-gate mode semantics clarified and enforced (`soak_evidence` closure-grade; `runtime` health-check-only).
- Metadata candidate payload parity verification: `PASS 5/5` with aligned `candidate_rows_json`, `candidate_summary_json`, and `best_candidate_json`.

Seal decision:

- **P3-S01:** sealed.
- **P3-S02:** sealed.
- **P3-S03:** sealed (diagnostics-only metadata ownership boundary retained).
- **Phase 3 overall:** sealed; Phase-4 validation now sealed through F4-S03.

### Phase 4 bounded slice plan (execution-ready)

| Slice | Scope | Runtime Track | Component Track | Exit gate |
| --- | --- | --- | --- | --- |
| F4-S01 | Capability matrix + profile scaffolding | Preserve existing helper behavior/contracts; no ownership cutover | Add profile schema skeleton + capability-map diagnostics surfaces | Deterministic diagnostics output; parity clean |
| F4-S02 | Programmable action catalog safety skeleton | Keep legacy action flows authoritative | Add arm/confirm/cooldown/audit schema + dry-run validation service | Safety-gate diagnostics pass |
| F4-S03 | Crossfade/balance service contract (diagnostics-first) | Keep current runtime control lane | Add normalized slider-domain contract + no-op service validation path | Contract + diagnostics pass with no authority expansion |

### F4-S01 implementation checkpoint (2026-04-19)

Implemented in component:

- coordinator diagnostics payload `capability_profile_validation`,
- capability matrix summary from registry entries (paths/families/capabilities/control-capable counts),
- deterministic profile-schema scaffolding surface for next-slice consumers,
- no-authority-expansion check and visibility in diagnostics,
- services: `spectra_ls.validate_capability_profile` and `spectra_ls.run_f4_s01_sequence`,
- raw operator template: `docs/testing/raw/f4_s01_capability_profile_validation.jinja`.

F4-S01 closeout evidence (2026-04-20):

- Runtime closure artifact captured with **PASS** (`gate_score=6/6`, timestamp `2026-04-20 03:14:23.318195-07:00`).
- Authority/ownership check passed: `authority_mode=legacy`, `no_authority_expansion=true`.
- Route/contract/metadata checks passed: `route=route_linkplay_tcp`, `contract_valid=true`, `metadata_prep_ready=true`.

Seal decision:

- **F4-S01:** sealed/validated.
- Continue active work on **F4-S02** diagnostics lane.

### F4-S02 implementation checkpoint (2026-04-20)

Implemented in component:

- coordinator diagnostics payload `action_catalog_validation`,
- deterministic action-schema contract surface (including required `safety` keys),
- diagnostics-only action catalog rows with explicit `dry_run_only` posture,
- no-authority-expansion and F4-S01 readiness checks,
- services: `spectra_ls.validate_action_catalog` and `spectra_ls.run_f4_s02_sequence`,
- raw operator template: `docs/testing/raw/f4_s02_action_catalog_validation.jinja`.

F4-S02 closeout evidence (2026-04-20):

- Runtime closure artifact captured with **PASS** (`gate_score=7/7`, timestamp `2026-04-20 03:19:04.074224-07:00`).
- Authority/safety checks passed: `authority_mode=legacy`, `dry_run_only=true`, `no_authority_expansion=true`.
- Dependency check passed: `f4_s01_ready_reference=true`.

Seal decision:

- **F4-S02:** sealed/validated.
- Continue Phase-4 execution on active **F4-S03** diagnostics lane.

### F4-S03 implementation checkpoint (2026-04-20)

Implemented in component:

- coordinator diagnostics payload `crossfade_balance_validation`,
- normalized slider-domain contract schema (`f4_s03.v1`) and mode-profile diagnostics,
- sample dry-run mix-plan diagnostics (no-op/fallback visibility),
- services: `spectra_ls.validate_crossfade_balance`, `spectra_ls.run_f4_s03_sequence`,
- raw operator template: `docs/testing/raw/f4_s03_crossfade_balance_validation.jinja`.

Hardening pass-2 (2026-04-20):

- F4 one-shot sequence services (`run_f4_s01_sequence`, `run_f4_s02_sequence`, `run_f4_s03_sequence`) now report explicit stage-failure context when action execution errors occur, improving operator debugging and reducing opaque "Unknown error" outcomes.
- F4-S03 dependency access is now guarded against nullable action-catalog payloads during snapshot builds and callback refresh failures are contained to logged diagnostics, preventing repeated event-dispatch exception cascades.

Hardening pass-3 (2026-04-20):

- F4-S03 payload now includes explicit dependency context (`active_target_resolved`, `route_decision`, `blocking_reasons`) and operator validation template guidance for dependency-only/no-target WARN captures (`f4_s02_not_ready`, `route_deferred_no_target`) with deterministic legacy-mode rerun order.

Hardening pass-4 (2026-04-20):

- Fixed accidental function-split regression where F4-S02 action-catalog builder could return `None` after F4-S03 insertion, causing persistent false dependency WARN gates in F4-S03; restored full F4-S02 payload return path.

F4-S03 closeout evidence (2026-04-20):

- Runtime closure artifact captured with **PASS** (`gate_score=8/8`, timestamp `2026-04-20 03:57:35.874550-07:00`).
- Authority/safety checks passed: `authority_mode=legacy`, `no_authority_expansion=true`.
- Dependency and route checks passed: `ready_for_f4_s03_closeout=true`, `f4_s02_ready_reference=true`, `route_decision=route_linkplay_tcp`, `active_target=media_player.spectra_ls_2`, `active_path=linkplay_tcp`.
- Contract checks passed: `slider_schema_present=true`, `mode_profiles_present=true`, `sample_mix_plan.dry_run_only=true`, `dependency_reference.active_target_resolved=true`.

Seal decision:

- **F4-S03:** sealed/validated.
- **Phase 4 bounded diagnostics slice set (F4-S01/F4-S02/F4-S03):** sealed/validated.

P1/P2/P3 impact check (required):

- **P1 impact:** none; shadow parity surfaces remain read-only and unchanged.
- **P2 impact:** none; registry/router diagnostics contract remains unchanged and validated by closeout route context.
- **P3 impact:** none; guarded write-path authority model remains unchanged (`legacy` retained in F4 diagnostics lane).

### Phase 3 exit criteria

- No route or selection flapping under dual-write operation.
- Single-writer authority is provable at any instant (legacy or component, never both).
- Rollback switch restores legacy authority without contract breakage.
- P2 parity templates still PASS after P3-S01 and P3-S02 trials.

## Phase 4 — Functional expansion beyond setup/settings

- Mode engine APIs for hardware-first policy.
- Profile APIs + options flow integration.
- Programmable action catalog.
- Crossfade/balance service layer implementation.
- Capability-matrix gating for per-feature routing (not only boolean control-capable).

### Phase 4 exit criteria

- New features operate through component contracts while legacy surfaces remain intact.
- Sensitive actions use explicit safety gates (confirm/cooldown/audit).

### Phase 5 entry criteria delta note (2026-04-20)

Post-F4 closeout, Phase 5 remains gated and should not auto-start from sealed diagnostics status alone.

Required entry gates:

1. **Authority baseline gate:** `legacy` remains default owner; cutover authority is explicitly armed per slice and reversible.
2. **Parity gate:** P2 parity/contract verification remains PASS after enabling any Phase 5 domain flag.
3. **Isolation gate:** only one cutover domain per slice (`routing`, then `metadata`, then optional `lighting orchestration`).
4. **Rollback gate:** each slice includes tested rollback path + explicit stop conditions (loop/flap, contract mismatch, missing compatibility surfaces).
5. **Evidence gate:** each slice captures fresh runtime evidence before status can move Active → Validated.

Disposition:

- Phase 5 remains **In Progress** with domain-isolated slice gating; additional slices activate only after required gates are satisfied for the selected domain.
- No P1/P2/P3 source-of-truth or authority change is enacted by this delta note.

## Phase 5 — Domain cutover + legacy retirement

- Cut over by domain in small slices:
  1) routing
  2) metadata
  3) optional lighting orchestration
- Retire duplicated template logic only after parity soak.
- Keep naming cleanup deferred to existing trigger gates.

### Phase 5 starter slice card — P5-S01 (routing domain)

Status: **Validated**

Scope:

- **In:** routing-domain cutover trial only (component-led route-write decision path under explicit arm/disarm control).
- **Out:** metadata authority cutover, lighting-orchestration cutover, and legacy naming retirement work.

Two-track disposition (required):

- **Track A (current runtime):** compatibility-shimmed / retained as rollback source-of-truth.
- **Track B (custom component):** routing cutover trial implementation + diagnostics-led validation.

Activation gates (all required):

1. Authority baseline gate satisfied (`legacy` default; reversible trial arm/disarm path confirmed).
2. P2 parity/contract gate PASS immediately pre-trial.
3. Single-domain isolation gate enforced (no metadata/lighting cutover flags enabled).
4. Rollback gate validated in-window (tested rollback command/path + stop conditions documented).
5. Evidence gate satisfied (fresh runtime capture for outcome and closure decision).

Stop conditions (fail-closed):

- route-write loop/flap detected,
- required compatibility surface mismatch,
- unresolved active target/control host route eligibility,
- stale closure evidence window.

Current runtime evidence snapshot (2026-04-20):

- monitor verdict captured: `Status=PASS`, `Write proof=VERIFIED`;
- `last_attempt.status=noop_already_selected` (accepted guarded-write verification outcome);
- routing/contract/parity/freshness healthy (`route_linkplay_tcp`, `contract_valid=true`, `missing_required=0`, `unresolved=0`, `mismatches=0`, fresh snapshot).

Remaining for closeout:

- complete bounded run-window record with explicit end-of-window authority disposition,
- execute/record rollback-to-`legacy` (unless an approved extension rationale is documented),
- publish closeout verdict (`PASS`/`WARN`/`FAIL`) with timestamped evidence.

Closeout evidence update (2026-04-20):

- post-window rollback snapshot captured with `authority_mode=legacy`;
- route/contract/parity/freshness remained healthy after disarm (`route_linkplay_tcp`, `contract_valid=true`, mismatch/unresolved counts `0`, fresh snapshot);
- slice now meets routing-domain validation posture and is sealed as **Validated**.

Next-slice note:

- broader Phase-5 program work remains open; metadata/lighting cutover slices require separate domain-isolated activation and evidence.

### Phase 5 follow-on slice card — P5-S02 (metadata domain)

Status: **Active (gate-prep)**

Scope:

- **In:** metadata-domain readiness/gate validation and bounded run-window evidence capture.
- **Out:** routing-domain ownership (already validated in P5-S01), lighting orchestration cutover, naming retirement.

Current mechanism posture:

- dedicated metadata trial contract service is now implemented: `spectra_ls.metadata_write_trial`.
- current semantics remain gate-prep/readiness-first and fail-closed by default (dry-run-first; legacy authority baseline retained).

Activation gates (all required):

1. Authority baseline (`legacy`) confirmed and rollback-safe posture explicit.
2. P2 parity template PASS in active window.
3. Metadata readiness validation PASS (`p3_s03_metadata_prep_validation.jinja`) in active window.
4. Domain isolation preserved (no concurrent routing/lighting cutover execution).
5. Fresh timestamped evidence captured for pre/in/post window.

Implementation sequence (beyond mirroring, required):

- **Metadata contract inventory lock:** enumerate authoritative metadata entities/attributes and ownership expectations; mark which surfaces remain legacy-owned during gate-prep.
- **Mechanism definition slice:** define explicit component metadata cutover mechanism/service contract (if absent) and require reversible authority semantics with audit fields equivalent to routing trials.
- **Bounded metadata trial slice:** run explicit trial window using the defined mechanism and capture pre/in/post window results with fail-closed stop conditions.
- **Rollback + closure slice:** prove safe end-of-window authority disposition (`legacy` unless approved extension) and close only with complete/fresh evidence and no unresolved contract drift.

Run-window checklist:

- `docs/testing/raw/p5_s02_metadata_cutover_run_window_checklist.md`

Latest runtime evidence snapshot (2026-04-20):

- Operator-captured monitor output reports `Status=PASS` and `Metadata readiness=READY` (`2026-04-20 17:59:21.972073-07:00`).
- Baseline remains safe and explicit: `authority_mode=legacy`, `route_decision=route_linkplay_tcp`.
- Contract + metadata gates are healthy: `contract_valid=true`, missing required counts `0`, `metadata_prep_validation.verdict=PASS`, `ready_for_metadata_handoff=true`.
- Parity/freshness remain clean: `unresolved_sources=0`, `mismatches=0`, snapshot within freshness threshold.
- Post-window proof captured at `2026-04-20 18:08:32.691994-07:00` confirms `authority_mode=legacy` with metadata readiness still `PASS/READY`.
- Slice disposition: this run window is closeout-eligible and recorded; slice remains Active (gate-prep) pending mechanism-definition and broader Phase-5 metadata cutover gates.

Run-3 evidence update (2026-04-20 evening):

- Legacy-mode `p5s02-run3` captured explicit fail-closed dry-run blocking while not ready (`metadata_trial_last_attempt.status=blocked_metadata_not_ready`) with route/contract/parity still healthy.
- Follow-up legacy capture in the same run window reached `PASS/READY` with `gate_score=9/9` under fresh active metadata conditions.
- Component-mode comparison capture remains intentionally `WARN/CAUTION` due to `authority_mode_not_legacy`; metadata ownership is still `legacy_contract_surfaces`, so this is an expected policy boundary signal (not a parity failure).

Mechanism-definition next step (P5-S02-M1):

- Implemented deliverable: dry-run service contract shape, audit payload fields, and fail-closed stop handling are now wired in `custom_components/spectra_ls` (`metadata_write_trial` + coordinator snapshot surfacing).
- Implemented deliverable: one-shot bounded-window sequence service (`run_p5_s02_sequence`) now executes the required P5-S02 order (authority baseline, registry/contracts/route/handoff/metadata refresh, guarded metadata trial, post-trial metadata refresh) in a single deterministic path.
- Hardening update: contract validation now treats unresolved required surfaces as invalid (not only missing entities), closing the gap where metadata could appear healthy while control-host surfaces degraded.
- Hardening update (audit canonicalization): coordinator now publishes `metadata_trial_last_attempt.audit_payload_state`, `audit_payload_complete`, and `missing_audit_fields` so closeout readiness can be classified from payload-native completeness semantics.
- Hardening update (trial gate semantics): coordinator now publishes `blocking_reasons`, `trial_gate_verdict`, and `eligible_for_closeout` in `metadata_trial_last_attempt` for deterministic gate-prep classification.
- Fresh promotion evidence captured (`p5s02-2026-04-21-run1`):
  - monitor output at `2026-04-21 17:18:18.431382-07:00` reports `Status=PASS`, `Metadata readiness=READY`,
  - baseline safe: `authority_mode=legacy`, `route_decision=route_linkplay_tcp`,
  - contract clean: `valid=true`, missing/unresolved required counts `0`,
  - metadata gate healthy: `verdict=PASS`, `gate_score=9/9`,
  - trial audit complete: `status=dry_run_ok`, `audit_payload_state=COMPLETE`, `trial_gate_verdict=PASS`, `eligible_for_closeout=true`, `missing_audit_fields=0`.
- Promotion-gate status: the “fresh dry-run + COMPLETE audit payload” gate is satisfied for P5-S02-M1. Slice remains **Active (gate-prep)** pending broader bounded-window/post-window evidence progression for full P5-S02 validation.
- Immediate next run target (Run-2 strict comparator): execute one fresh bounded sequence with `mode=legacy`, `dry_run=true`, and a new `window_id`; set comparator guards from the pre-window snapshot (`expected_target=<route_trace.active_target>`, `expected_route=<route_trace.decision>`) to preserve discovery-first portability while still proving deterministic alignment in the audit payload.
- Run-2 success criteria: monitor outputs remain `PASS/READY`, trial audit remains `COMPLETE` with `missing_audit_fields=0`, and trial semantics report `trial_gate_verdict=PASS`, `eligible_for_closeout=true`, with explicit post-window authority disposition `legacy`.
- Run-2 evidence captured (`p5s02-2026-04-21-run2`): monitor output at `2026-04-21 17:25:39.987075-07:00` confirms `Status=PASS`, `Metadata readiness=READY`, safe baseline (`authority_mode=legacy`, `route_decision=route_linkplay_tcp`), contract clean (`missing_required=0`, `unresolved_required=0`), metadata gate `PASS` (`9/9`), and complete trial audit (`status=dry_run_ok`, `audit_payload_state=COMPLETE`, `trial_gate_verdict=PASS`, `eligible_for_closeout=true`, `missing_audit_fields=0`).
- Disposition update: Run-2 strict comparator expectations are satisfied with fresh evidence; `P5-S02` is promoted to **Validated** via consolidated closeout packet acceptance while metadata ownership remains legacy by policy.
- Closeout packet candidate: bounded Run-1 and Run-2 evidence now forms a consolidated closeout packet with explicit legacy authority retention, clean contract/parity signals, and complete trial-audit payloads; promotion recommendation is evidence-supported while awaiting explicit status-lane promotion recording.

### Phase 5 next-slice card — P5-S03 (lighting orchestration domain)

Status: **Validated**

Scope:

- **In:** lighting-domain orchestration gate-prep and bounded run-window validation.
- **Out:** routing ownership, metadata ownership cutover, naming retirement.

Activation gates (required):

1. P5-S02 closeout decision captured in status ledger (`Validated`).
2. Authority baseline remains `legacy` at lighting-window start.
3. Lighting parity/contract checks PASS in active window.
4. Domain isolation enforced (no concurrent metadata/routing cutover).
5. Rollback/disarm evidence captured in the same window.

Execution checklist:

- `docs/testing/raw/p5_s03_lighting_orchestration_run_window_checklist.md`
- Primary live monitor: `docs/testing/raw/p5_s03_lighting_functionality_monitor.jinja`
- Freshness semantics correction: monitor-side control snapshot age is now contextual (informational) and does not by itself downgrade lighting verdicts when authority/contract/selector/parity gates pass.
- Run-1 completed and closed out with full pre/in/post evidence:
  - pre-window `PASS/READY` (`2026-04-21 17:41:12.841574-07:00`),
  - in-window `PASS/READY` (`2026-04-21 17:44:00.229390-07:00`),
  - post-window `PASS/READY` (`2026-04-21 17:44:45.600796-07:00`).
- Closeout posture confirmed: `authority_mode=legacy`, contract/parity clean (`missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`), stop conditions not triggered.

### Phase 5 next-slice card — P5-S04 (phase-exit closeout)

Status: **Validated**

Scope:

- **In:** Phase-5 closeout packet consolidation, final authority/parity safety snapshot, and P6 planning handoff gate.
- **Out:** new write-path ownership behavior changes in routing/metadata/lighting domains.

Activation gates (required):

1. P5-S01, P5-S02, and P5-S03 are `Validated` with linked evidence artifacts.
2. Fresh closeout snapshot confirms safe authority posture and clean contract/parity state.
3. Legacy retirement remains explicitly deferred (no implicit retirement action in this slice).
4. P6 handoff stance is planning-only unless a separate bounded slice explicitly changes authority behavior.

Execution checklist:

- `docs/testing/raw/p5_s04_phase_exit_closeout_checklist.md`
- Primary live monitor: `docs/testing/raw/p5_s04_phase_exit_functionality_monitor.jinja`

Closeout evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `Phase-5 closeout readiness=READY`, `gate_score=7/7` (`2026-04-21 19:04:03.253466-07:00`),
- runtime safety gates all pass with safe baseline (`authority_mode=legacy`) and clean route/contract/parity/freshness,
- governance gates all pass with explicit P5-S01/S02/S03 closure linkage and planning-only P6 handoff stance.

Disposition:

- `P5-S04` promoted to **Validated**.

## Phase 7 — Component-first cutover and legacy sealing

Program intent:

- Component becomes the default primary control plane for net-new sidebar and beyond features.
- Legacy runtime remains trusted, stable, and respected as compatibility + rollback baseline during bounded cutover gates.
- Legacy exits normal feature-growth ownership once cutover readiness and domain flip proofs are accepted.

### Phase 7 starter slice card — P7-S01 (component-first cutover readiness gate)

Status: **Validated**

Scope:

- **In:** cutover-readiness gate activation, sustained parity criteria, rollback proof criteria, and legacy-seal publication.
- **Out:** immediate cross-domain authority cutover and irreversible legacy retirement actions.

Activation gates (required):

1. `P6-S01..P6-S04` validated with accepted evidence packets.
2. Runtime baseline remains safe at activation (`authority_mode=legacy`, clean contract/parity).
3. Explicit rollback posture and proof fields are published for each follow-on domain flip slice.
4. Component-first ownership direction is explicit for net-new features.

Execution checklist:

- `docs/testing/raw/p7_s01_cutover_readiness_checklist.md`
- Primary live monitor: `docs/testing/raw/p7_s01_cutover_readiness_monitor.jinja`

Two-track disposition:

- **Track A (current runtime):** compatibility/rollback baseline, net-new feature growth deferred.
- **Track B (custom component):** active primary ownership readiness lane.

P1/P2/P3 impact check:

- **P1:** unchanged read-only parity contracts.
- **P2:** unchanged registry/router diagnostics ownership.
- **P3:** unchanged single-writer boundary in this slice (authority flips deferred to follow-on P7 slices).
Run-1 evidence (2026-04-21):

- monitor verdict: `Status=FAIL`, `P7-S01 readiness=BLOCKED`, `gate_score=3/4` (`2026-04-21 20:33:32.373259-07:00`),
- baseline failure details: `route_decision=defer_no_target`, `unresolved_required=4`, `unresolved_sources=3`, `mismatches=2`.

Run-2 closeout evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P7-S01 readiness=READY`, `gate_score=4/4` (`2026-04-21 20:34:32.639010-07:00`),
- baseline restored: `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, `missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`, freshness within threshold.

Promotion disposition:

- `P7-S01` promoted to **Validated**.

### Phase 7 follow-on slice checkpoint — P7-S02 (first bounded authority-flip execution lane)

Status: **Validated**

Scope:

- **In:** first bounded authority-flip execution lane (routing/selection domain), strict single-writer enforcement, rollback-safe activation controls, and run-window evidence capture.
- **Out:** cross-domain ownership flips, unbounded legacy retirement actions, and irreversible helper/entity contract removal.

Activation gates (required):

1. `P7-S01` validated with accepted closeout evidence.
2. Runtime baseline remains clean at activation (`authority_mode=legacy`, contract/parity clean).
3. Domain-flip rollback path and stop conditions are explicit before first write-window attempt.
4. Component lane remains net-new feature primary while flip windows are bounded and reversible.

Execution checklist:

- `docs/testing/raw/p7_s02_domain_flip_readiness_checklist.md`
- Primary live monitor: `docs/testing/raw/p7_s02_domain_flip_readiness_monitor.jinja`

Two-track disposition:

- **Track A (current runtime):** rollback-safe authority baseline retained outside bounded flip windows.
- **Track B (custom component):** active first authority-flip execution lane.

P1/P2/P3 impact check:

- **P1:** unchanged read-only parity contract surfaces.
- **P2:** unchanged registry/router diagnostics ownership.
- **P3:** single-writer controls remain mandatory and explicitly audited in this slice.

Run-1 pre-window evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P7-S02 readiness=READY`, `gate_score=4/4` (`2026-04-21 20:38:00.223973-07:00`),
- baseline/gates clean: `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, `missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`, freshness within threshold,
- execution disposition: pre-window authorization granted; in-window and post-window captures are required before closeout eligibility.

Run-1 in-window evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P7-S02 readiness=READY`, `gate_score=4/4` (`2026-04-21 20:55:41.000516-07:00`),
- in-window probe remained clean: `monitor_source_sensor=sensor.shadow_active_target`, `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, `missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`, freshness within threshold,
- execution disposition: in-window gate accepted; post-window capture remains required before closeout eligibility.

Run-1 post-window evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P7-S02 readiness=READY`, `gate_score=4/4` (`2026-04-21 20:57:00.162663-07:00`),
- post-window rollback-safe baseline verified: `monitor_source_sensor=sensor.shadow_active_target`, `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, `missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`, freshness within threshold,
- execution disposition: post-window gate accepted with no stop-condition triggers; slice is closeout eligible.

Promotion disposition:

- `P7-S02` promoted to **Validated**.

### Phase 7 follow-on slice checkpoint — P7-S03 (bounded metadata-domain authority-flip execution lane)

Status: **Validated**

Scope:

- **In:** bounded metadata-domain authority-flip execution lane, metadata trial service-path probe (`metadata_write_trial`) with dry-run-first semantics, strict single-writer enforcement, rollback-safe activation controls, and pre/in/post run-window evidence capture.
- **Out:** routing-domain revalidation, lighting-domain ownership flips, unbounded legacy retirement actions, and irreversible helper/entity contract removal.

Activation gates (required):

1. `P7-S02` validated with accepted closeout evidence.
2. Runtime baseline remains clean at activation (`authority_mode=legacy`, contract/parity clean).
3. Metadata readiness is PASS/ready (`metadata_prep_validation.verdict=PASS`, `ready_for_metadata_handoff=true`) with route eligibility present.
4. Metadata-domain rollback path and stop conditions are explicit before first in-window metadata trial attempt.

Execution checklist:

- `docs/testing/raw/p7_s03_metadata_domain_flip_readiness_checklist.md`
- Primary live monitor: `docs/testing/raw/p7_s03_metadata_domain_flip_readiness_monitor.jinja`

Two-track disposition:

- **Track A (current runtime):** rollback-safe metadata authority baseline retained outside bounded P7-S03 windows.
- **Track B (custom component):** active bounded metadata-domain authority-flip execution lane.

P1/P2/P3 impact check:

- **P1:** unchanged read-only parity contract surfaces.
- **P2:** unchanged registry/router diagnostics ownership.
- **P3:** single-writer controls remain mandatory and explicitly audited in this slice.

Run-1 pre-window evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P7-S03 readiness=READY`, `gate_score=4/4` (`2026-04-21 21:03:00.345491-07:00`),
- baseline/metadata gates clean: `monitor_source_sensor=sensor.shadow_active_target`, `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, `metadata_prep_validation.verdict=PASS`, `ready_for_metadata_handoff=true`, `metadata_prep_validation.missing_required=0`, contract/parity clean (`missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`), freshness within threshold,
- execution disposition: pre-window authorization granted; in-window and post-window captures are required for closeout eligibility.

Run-1 in-window evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P7-S03 readiness=READY`, `gate_score=4/4` (`2026-04-21 21:05:29.978417-07:00`),
- in-window probe remained clean: `monitor_source_sensor=sensor.shadow_active_target`, `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, `metadata_prep_validation.verdict=PASS`, `ready_for_metadata_handoff=true`, `metadata_prep_validation.missing_required=0`, `metadata_trial_last_attempt.status=dry_run_ok`, `metadata_trial_last_attempt.trial_gate_verdict=PASS`, contract/parity clean (`missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`), freshness within threshold,
- execution disposition: in-window gate accepted; post-window capture remained required before closeout eligibility.

Run-2 post-window evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P7-S03 readiness=READY`, `gate_score=4/4` (`2026-04-21 21:07:08.345292-07:00`),
- post-window rollback-safe baseline remained clean: `monitor_source_sensor=sensor.shadow_active_target`, `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, `metadata_prep_validation.verdict=PASS`, `ready_for_metadata_handoff=true`, `metadata_prep_validation.missing_required=0`, `metadata_trial_last_attempt.status=dry_run_ok`, `metadata_trial_last_attempt.window_id=window_id: p7s03-2026-04-21-run2`, `metadata_trial_last_attempt.trial_gate_verdict=PASS`, contract/parity clean (`missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`), freshness within threshold,
- execution disposition: post-window gate accepted with no stop-condition triggers; slice is closeout eligible.

Promotion disposition:

- `P7-S03` promoted to **Validated**.

### Phase 7 follow-on slice checkpoint — P7-S04 (phase-exit closeout packet)

Status: **Validated**

Scope:

- **In:** Phase-7 closeout packet consolidation, final rollback-safe baseline evidence capture, and promotion gating.
- **Out:** new domain authority expansion, additional write-path cutover trials, and immediate legacy retirement execution.

Activation gates (required):

1. `P7-S01`, `P7-S02`, and `P7-S03` are validated with linked evidence packets.
2. Runtime baseline remains rollback-safe at closeout capture (`authority_mode=legacy`, contract/parity clean).
3. Rollback path and single-writer boundary remain explicit and operator-verifiable.
4. Component-primary posture and legacy-seal scope are documented for closeout governance.

Execution checklist:

- `docs/testing/raw/p7_s04_phase_exit_closeout_checklist.md`
- Primary live monitor: `docs/testing/raw/p7_s04_phase_exit_functionality_monitor.jinja`

Two-track disposition:

- **Track A (current runtime):** rollback-safe compatibility baseline retained for closeout capture.
- **Track B (custom component):** active phase-exit closeout packet lane.

P1/P2/P3 impact check:

- **P1:** unchanged read-only parity contract surfaces.
- **P2:** unchanged registry/router diagnostics ownership.
- **P3:** unchanged single-writer boundary and rollback discipline.

Run-1 closeout evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P7-S04 readiness=READY`, `gate_score=4/4` (`2026-04-21 21:13:00.468462-07:00`),
- baseline remained rollback-safe and clean: `monitor_source_sensor=sensor.shadow_active_target`, `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, `contract_valid=true`, `missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`, freshness within threshold (`age_s=60.0`),
- closeout disposition: no stop-condition triggers; phase-exit packet is complete and promotion-eligible.

Promotion disposition:

- `P7-S04` promoted to **Validated**.

### Phase 8 starter slice card — P8-S01 (legacy-seal readiness gate)

Status: **Validated**

Scope:

- **In:** post-cutover legacy-seal readiness gating, rollback-safe baseline verification, and governance continuity checks.
- **Out:** runtime ownership expansion, irreversible legacy retirement actions, and net-new write-path cutover behavior.

Activation gates (required):

1. Phase-7 closeout packet is validated.
2. Runtime baseline remains rollback-safe (`authority_mode=legacy`) with clean contract/parity.
3. Rollback + single-writer controls remain explicit and verifiable.
4. Legacy net-new growth freeze and component-primary posture remain explicit.

Execution checklist:

- `docs/testing/raw/p8_s01_legacy_seal_readiness_checklist.md`
- Primary live monitor: `docs/testing/raw/p8_s01_legacy_seal_readiness_monitor.jinja`

Two-track disposition:

- **Track A (runtime):** sealed rollback-safe baseline with no net-new ownership growth.
- **Track B (component):** active governance/readiness lane for post-cutover operation.

Activation disposition:

- `P8-S01` activated with monitor/checklist artifacts and completed with full pre/in/post PASS evidence packet.
- `P8-S01` promoted to **Validated**.

Run-1 pre-window evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P8-S01 readiness=READY`, `gate_score=4/4` (`2026-04-21 21:18:39.504385-07:00`),
- baseline/gates clean: `monitor_source_sensor=sensor.shadow_active_target`, `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, `contract_valid=true`, `missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`, freshness within threshold (`age_s=157.6`),
- execution disposition: pre-window authorization accepted; in-window and post-window captures remain required before closeout eligibility.

Run-2 in-window evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P8-S01 readiness=READY`, `gate_score=4/4` (`2026-04-21 21:22:08.276673-07:00`),
- baseline/gates clean: `monitor_source_sensor=sensor.shadow_active_target`, `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, `contract_valid=true`, `missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`, freshness within threshold (`age_s=171.6`),
- execution disposition: in-window capture accepted; post-window capture remained required before closeout eligibility.

Run-3 post-window evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P8-S01 readiness=READY`, `gate_score=4/4` (`2026-04-21 21:22:20.668596-07:00`),
- baseline/gates clean: `monitor_source_sensor=sensor.shadow_active_target`, `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, `contract_valid=true`, `missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`, freshness within threshold (`age_s=184.0`),
- execution disposition: post-window capture accepted; pre/in/post packet complete with no stop-condition triggers.

### Phase 8 follow-on slice card — P8-S02 (docs + wiki native-English overhaul)

Status: **Active**

Scope:

- **In:** improve user/operator/developer-facing documentation with direct, native-English, task-oriented language; remove AI-sounding phrasing; improve wiki utility with clear outcomes, decision paths, and troubleshooting flow.
- **Out:** runtime/component behavior changes, contract ownership changes, or migration gate policy changes.

Activation gates (required):

1. P8-S01 is validated and closed.
2. A reusable writing standard is published for wiki/repo docs consistency.
3. Wiki navigation and page intent are updated to prioritize operator usefulness.
4. Documentation changes remain parity-synchronized through changelog + roadmap ledgers.

Execution checklist:

- Writing standard: `docs/wiki/DOCUMENTATION-WRITING-STANDARD.md`
- Wiki source index: `docs/wiki/README.md`
- Wiki home/navigation: `docs/wiki/Home.md`, `docs/wiki/_Sidebar.md`

Two-track disposition:

- **Track A (runtime):** unchanged sealed compatibility baseline.
- **Track B (component):** unchanged primary product-growth lane while docs quality lane executes.

P1/P2/P3 impact check:

- **P1:** unchanged read-only parity contract surfaces.
- **P2:** unchanged registry/router diagnostics ownership.
- **P3:** unchanged single-writer boundary and rollback discipline.

Initial execution disposition:

- P8-S02 activated with writing-standard scaffolding and wiki-navigation updates.

Run-1 execution update (2026-04-21):

- Sidebar/component lane: added `Control Center Last Attempt Status` diagnostic sensor in `custom_components/spectra_ls/sensor.py` so mapped-input outcomes are visible as first-class state instead of only deep attributes.
- Documentation/wiki lane: improved high-traffic operator onboarding/install/setup pages (`docs/wiki/Getting-Started.md`, `docs/wiki/Install-on-Your-Own-HA.md`, `docs/wiki/User-Setup-Deploy-and-HA-Integration.md`) with task-first structure, explicit expected outcomes, and failure actions.
- Execution disposition: run-1 packet accepted; remaining wiki/page sweep continues in subsequent packets.

Run-2 execution update (2026-04-21):

- Top-level docs lane: improved `CONTRIBUTING.md` with clearer workflow language, branch boundaries, and migration posture expectations.
- Execution disposition: run-2 contributor-doc polish accepted; additional repo/docs and wiki passes remain queued.

Run-3 execution update (2026-04-22):

- Top-level docs lane: polished `README.md` and `docs/README.md` with more directive, task-first language and clearer “what to read next” guidance.
- Validation lane: completed local wiki sync dry-run (`dry_run_ok`) with clone/read sync success and 17 staged wiki-file deltas in temp workspace (no push), confirming publish-ready source changes.
- Execution disposition: run-3 packet accepted; continue remaining page-by-page wiki cleanup passes.

Run-4 execution update (2026-04-22):

- Wiki docs lane: improved remaining core workflow/architecture contributor pages (`docs/wiki/Operations-Runbooks.md`, `docs/wiki/System-Architecture.md`, `docs/wiki/Contributing-Workflow.md`) with direct task flow, explicit outcomes, and parity/ownership reminders.
- Execution disposition: run-4 packet accepted; continue remaining lower-traffic wiki cleanup pages and consistency passes.

Run-5 execution update (2026-04-22):

- Navigation/reference lane: aligned top-level + wiki entry navigation (`README.md`, `docs/wiki/Home.md`, `docs/wiki/_Sidebar.md`, `docs/wiki/README.md`) to link-first reference paths and stronger canonical source routing.
- Language lane: removed low-value process narration about edit mechanics and kept page intent outcome-focused.
- Execution disposition: run-5 packet accepted; continue remaining long-tail page consistency cleanup.

Run-6 execution update (2026-04-22):

- Long-tail wiki lane: improved process/reference-heavy pages (`docs/wiki/Getting-Started.md`, `docs/wiki/Discussions-and-Projects-Workflow.md`, `docs/wiki/Release-and-Changelog-Process.md`, `docs/wiki/Wiki-Content-Scope-Policy.md`, `docs/wiki/Contributing-Workflow.md`, `docs/wiki/Operations-Runbooks.md`) with explicit clickable links for canonical repo references.
- Execution disposition: run-6 packet accepted; continue remaining page-by-page consistency sweep as follow-on maintenance.

Run-7 execution update (2026-04-22):

- High-traffic wiki lane: improved architecture/orientation/install pages (`docs/wiki/System-Architecture.md`, `docs/wiki/Welcome-README-and-Bug-Workflow.md`, `docs/wiki/Install-on-Your-Own-HA.md`) with explicit link-first references for canonical sources and runbooks.
- Execution disposition: run-7 packet accepted; continue residual link-normalization sweep as follow-on maintenance.

Run-8 execution update (2026-04-22):

- Residual wiki lane: improved contract/control-surface/setup-roadmap pages (`docs/wiki/Control-Contracts-and-Scope-Paths.md`, `docs/wiki/Control-Surface-Inputs-and-Expanders.md`, `docs/wiki/User-Setup-Deploy-and-HA-Integration.md`, `docs/wiki/Custom-Component-Setup-Roadmap-Stub.md`) with explicit link-first references for canonical repo sources.
- Execution disposition: run-8 packet accepted; continue small residual cleanup as follow-on maintenance.

Run-9 execution update (2026-04-22):

- Process/navigation lane: improved residual process and wiki-publishing pages (`docs/wiki/Contributing-Workflow.md`, `docs/wiki/Operations-Runbooks.md`, `docs/wiki/Release-and-Changelog-Process.md`, `docs/wiki/README.md`, `docs/wiki/Home.md`) with explicit link-first references for parity and publishing workflows.
- Execution disposition: run-9 packet accepted; continue optional long-tail consistency cleanup as follow-on maintenance.

Run-10 execution update (2026-04-22):

- Residual policy lane: improved final non-table policy/process literals in `docs/wiki/Contributing-Workflow.md`, `docs/wiki/Wiki-Content-Scope-Policy.md`, and `docs/wiki/Install-on-Your-Own-HA.md` with explicit links where operator navigation benefits.
- Execution disposition: run-10 packet accepted; remaining literals are primarily intentional contract/path notation.

Run-11 execution update (2026-04-22):

- Writing-standard lane: improved `docs/wiki/DOCUMENTATION-WRITING-STANDARD.md` examples and path references with explicit link-aware references while keeping guidance semantics intact.
- Execution disposition: run-11 packet accepted; remaining literal references are primarily intentional contract/table notation.

Run-12 execution update (2026-04-22):

- Component UX lane: improved `custom_components/spectra_ls` control-center setup defaults and diagnostics visibility by adding scene-aware options defaults/selectors, stricter scene-binding normalization, richer coordinator readiness diagnostics, and a dedicated readiness sensor surface.
- Execution disposition: run-12 packet accepted; runtime track unchanged compatibility baseline, component track additive UX/observability hardening.

GitHub/developer declaration (policy mirror):

- Legacy runtime path is sealed as rollback-safe compatibility baseline.
- Custom component path is primary for net-new feature/control-plane growth.

Deferred H1 note (report/log/heal):

- Detailed implementation scaffold is published at `docs/features/H1-report-log-heal-scaffold.md`.
- H1 is intentionally deferred while Phase-5 active execution lanes continue.
- Scope is planning + runbook readiness only in this slice (no authority/control-path ownership change).

P1/P2/P3 impact check for P5-S02 draft:

- **P1:** unchanged read-only parity contracts.
- **P2:** remains parity-validation authority gate.
- **P3:** single-writer boundary preserved with explicit rollback.

Run-window execution checklist (required for activation/closeout evidence):

- `docs/testing/raw/p5_s02_metadata_cutover_run_window_checklist.md`

### Phase 5 exit criteria

- Component is primary control plane with validated backward compatibility.

## Phase 6 — HA sidebar Spectra control center

- Deliver a modern, complete Spectra control center in the Home Assistant sidebar after Phase-5 gates are completed.
- Keep migration-safe rollout: read-only visibility first, then bounded writable controls once parity/evidence checks stay healthy.

### Phase 6 starter slice card — P6-S01 (control-center foundation)

Status: **Validated**

Scope:

- **In:**
  - Control Center scaffold in HA sidebar context,
  - setup/onboarding flow (discovery + readiness),
  - tuning surfaces (profiles, response/debounce),
  - defaults and per-target override surfaces,
  - mapped-environment view (rooms/targets/control paths/capabilities),
  - diagnostics/evidence panel aligned to existing PASS/WARN/FAIL artifacts.
- **Out:**
  - unbounded authority expansion,
  - breaking helper/entity contract renames,
  - legacy retirement before parity soak.

Activation gates (required):

1. Phase-5 slice gates complete for active domain sequence.
2. P2/P3 parity and authority guardrails remain stable under current runtime evidence.
3. UX surfaces initially launch in read-only-safe mode where needed.
4. Rollback path is explicit for any newly writable control-center action.

Execution checklist:

- `docs/testing/raw/p6_s01_control_center_foundation_checklist.md`
- Primary live monitor: `docs/testing/raw/p6_s01_control_center_foundation_monitor.jinja`

Baseline evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P6-S01 readiness=READY`, `gate_score=6/6` (`2026-04-21 19:18:22.634239-07:00`),
- runtime baseline remains safe (`authority_mode=legacy`) with clean route/contract/parity and fresh snapshot,
- foundation governance gates all pass (read-only-first, compatibility, rollback, bounded authority).

Disposition:

- `P6-S01` promoted to **Validated** with baseline + closeout packet evidence accepted.

Closeout evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P6-S01 readiness=READY`, `gate_score=6/6` (`2026-04-21 20:17:21.077121-07:00`),
- runtime baseline clean: `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, `contract_valid=true`, `missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`, freshness within threshold,
- foundation governance gates all true: read-only-first launch, compatibility posture, rollback posture, and bounded-authority posture.

### Phase 6 follow-on slice checkpoint — P6-S02 (control-center settings contract)

Status: **Validated**

Scope:

- **In:** initial functional customization contract for control-center inputs (encoder turn/press/long-press mappings + button scene bindings), operator-updatable settings path, and diagnostics visibility for mapped values.
- **Out:** write-authority expansion, runtime ownership cutover, breaking helper/entity contract renames, and legacy retirement.

Implemented surfaces:

- options-flow settings form in `custom_components/spectra_ls/config_flow.py`,
- normalized settings/defaults contract in `custom_components/spectra_ls/const.py`,
- service path `spectra_ls.set_control_center_settings` in `custom_components/spectra_ls/__init__.py` + `services.yaml`,
- coordinator snapshot diagnostics `control_center_validation` + `write_controls.control_center_settings` in `custom_components/spectra_ls/coordinator.py` with shadow/diagnostics export visibility.

Two-track disposition:

- **Track A (current runtime):** compatibility-preserved (unchanged runtime ownership and rollback baseline).
- **Track B (custom component):** validated P6 settings contract foundation for sidebar/control-center customization workflow.

P1/P2/P3 impact check:

- **P1:** unchanged read-only parity contracts.
- **P2:** unchanged registry/router diagnostics contract surfaces.
- **P3:** unchanged single-writer authority boundary (`legacy` remains baseline).

Execution checklist:

- `docs/testing/raw/p6_s02_control_center_settings_checklist.md`
- Primary live monitor: `docs/testing/raw/p6_s02_control_center_settings_monitor.jinja`

Closeout evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P6-S02 readiness=READY`, `gate_score=4/4` (`2026-04-21 20:15:35.644673-07:00`),
- settings-contract readiness proven: `schema_version=p6_s02.v1`, `settings_present=true`, `ready_for_customization=true`, `required_keys=8`,
- safe baseline retained: `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, clean contract/parity (`missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`).

Promotion disposition:

- `P6-S02` promoted to **Validated**.

### Phase 6 follow-on slice checkpoint — P6-S03 (control-input execution skeleton)

Status: **Validated**

Scope:

- **In:** first bounded execution lane for mapped control-center input events (encoder/button), dry-run-first operation, read-only enforcement, and explicit action-attempt diagnostics.
- **Out:** authority expansion, broad domain service dispatch beyond staged mappings, helper/entity contract breakage, and legacy retirement.

Implemented surfaces:

- `execute_control_center_input` service contract (`custom_components/spectra_ls/services.yaml` + `__init__.py`),
- coordinator action-attempt engine with explicit fail-closed status semantics and correlation IDs,
- scene execution path only when mapping resolves to `scene.*` and read-only mode is disabled,
- diagnostics visibility of latest action attempt in `write_controls.control_center_last_attempt`.

Two-track disposition:

- **Track A (current runtime):** compatibility-preserved (runtime/source-of-truth unchanged).
- **Track B (custom component):** validated bounded execution skeleton for control-center mappings.

Closeout evidence linkage (2026-04-21):

- accepted execution proof via P6-S04 closeout packet (`Status=PASS`, `P6-S04 readiness=READY`, `gate_score=5/5` at `2026-04-21 20:07:51.471030-07:00`),
- deterministic dry-run semantics observed: `last_attempt.status=dry_run_ok`, `input_event=encoder_press`, `mapped_action=play_pause`, `last_attempt.dry_run=true`,
- safety baseline preserved: `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, clean contract/parity (`missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`).

Promotion disposition:

- `P6-S03` promoted to **Validated**.

P1/P2/P3 impact check:

- **P1:** unchanged read-only parity contracts.
- **P2:** unchanged registry/router diagnostics ownership.
- **P3:** unchanged authority boundary; `legacy` remains baseline owner.

### Phase 6 follow-on slice checkpoint — P6-S04 (control-input execution validation artifacts)

Status: **Validated**

Scope:

- **In:** operator-grade validation and closeout artifacts for `spectra_ls.execute_control_center_input` lane.
- **Out:** authority ownership changes, broad execution-surface refactors, or legacy retirement.

Implemented surfaces:

- `docs/testing/raw/p6_s04_control_input_execution_monitor.jinja`
- `docs/testing/raw/p6_s04_control_input_execution_checklist.md`

Two-track disposition:

- **Track A (current runtime):** compatibility-preserved (legacy authority baseline unchanged).
- **Track B (custom component/docs):** validated evidence-capture/closeout classification artifacts for execution readiness.

Closeout evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P6-S04 readiness=READY`, `gate_score=5/5` (`2026-04-21 20:07:51.471030-07:00`),
- deterministic dry-run-first semantics proven: `last_attempt.status=dry_run_ok`, `input_event=encoder_press`, `mapped_action=play_pause`, `last_attempt.dry_run=true`,
- safe baseline retained: `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, clean contract/parity (`missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`).

Promotion disposition:

- `P6-S04` promoted to **Validated**.

P1/P2/P3 impact check:

- **P1:** unchanged read-only parity contracts.
- **P2:** unchanged registry/router validation ownership.
- **P3:** unchanged single-writer authority boundary.

P1/P2/P3 impact check:

- **P1:** unchanged (shadow parity contracts remain read-only/stable).
- **P2:** unchanged (registry/router diagnostics remain authoritative).
- **P3:** unchanged (single-writer authority boundary remains explicit and bounded).

Acceptance criteria:

1. Operators can complete setup/tuning/defaults/overrides from the sidebar without raw-template dependency for routine tasks.
2. Mapped-environment page explains effective routing/capability decisions for active targets.
3. Diagnostics panel links directly to evidence-grade artifacts used in roadmap closeout decisions.
4. Existing runtime/component contracts remain backward compatible during rollout.

## Migration plan (step-by-step)

1. Build shadow outputs first (no writes).
2. Validate parity using diagnostics templates + component parity checks.
3. Enable dual-write for one domain only (routing first).
4. Monitor for loops/flaps and fix before widening scope.
5. Add domain cutover flags and rollback switches.
6. Cut over next domain only after previous domain soak passes.
7. Decommission legacy logic after sustained parity and no downstream dependency.

## Parallel execution policy (required per feature slice)

Every feature change must include:

- **Track A (current runtime):** implement/shim/defer status.
- **Track B (custom component):** implement/shim/defer status.
- **Parity note:** acceptance result or explicit gap with owner and deadline.

## Documentation parity protocol (required)

For architecture/process/contract changes, update in the same change set:

1. `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`
2. `docs/roadmap/v-next-NOTES.md`
3. `docs/CHANGELOG.md`
4. `README.md` (or explicit no-material-change decision)

Missing one item means the slice is not done.

## Retroactive baseline docs (active references)

- Runtime architecture baseline: `docs/architecture/CODEBASE-RUNTIME-ARCHITECTURE.md`
- Control-hub architecture baseline: `docs/architecture/CONTROL-HUB-ARCHITECTURE.md`
- Dead-path cleanup matrix: `docs/cleanup/DEAD-PATHS-CLEANUP.md`

## Plan Delta protocol (required)

If new findings force strategy changes mid-slice:

1. Stop scope expansion.
2. Add a **Plan Delta** note (what changed, why, stable assumptions, new exit criteria).
3. Update both roadmap and v-next status before resuming.

## Risk register

1. **Contract drift** between templates and component outputs.
2. **Write-loop flapping** during dual-write windows.
3. **Parser shape regressions** across string/native payload forms.
4. **Target ambiguity regressions** in discovery/routing transitions.
5. **Naming migration blast radius** if cleanup starts before gates.

## Known tough spots (must be surfaced, not glossed)

1. **Selection-loop risk (High):** `ma_auto_select` + broad `state_changed` automation triggers can fight component write trials unless single-writer + debounce guards are active.
2. **Fallback ambiguity risk (Medium):** static host/entity fallback branches still exist and can mask discovery-routing regressions when enabled.
3. **Parser contract risk (Medium):** dual-mode payload parsing is broad and duplicated; regressions can appear if component payload shape drifts.
4. **Authority boundary risk (High):** routing, selection, and metadata are coupled in legacy templates; P3 must avoid multi-domain write activation in one slice.

## Verification matrix

- Contract parity checks (legacy vs component entities/attributes).
- Route determinism checks across ambiguous and non-ambiguous targets.
- Diagnostics health checks from existing `docs/testing/DEVTOOLS-TEMPLATES.local.md` + component diagnostics.
- Startup/bootstrap race checks (target options and host resolution).
- Dual-write stability checks (no repeated oscillation or stale override loops).

## GitHub structure strategy

### Current strategy (recommended now)

- Stay in one structured monorepo at `/mnt/homeassistant`.
- Keep boundaries explicit by directory ownership and workflow labels.

### Future split (optional, gated)

Split into multiple repos only after all are true:

1. Component schema/API stable across multiple releases.
2. Migration tooling tested and documented.
3. Independent CI confidence per domain.
4. Operator docs fully support split lifecycle.

Until then, use monorepo with strict domain boundaries to preserve cross-contract velocity.
