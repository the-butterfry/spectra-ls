<!-- Description: Specification and phased roadmap for the Spectra LS custom Home Assistant component developed in parallel with existing runtime. -->
<!-- Version: 2026.04.19.24 -->
<!-- Last updated: 2026-04-19 -->

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
| F4-S01 | 4 | Active (compatibility contracts retained; no ownership cutover) | Active (capability matrix + profile schema diagnostics scaffolding) | Active (diagnostics-only) | Medium | Active |

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

Not yet claimed complete:

- P3-S01 parity/soak closeout is pending runtime trial evidence under `component` authority mode.

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
  - **Ready for closure logging + gate decision** (baseline soak evidence captured via automated run).
  - **Not closure-ready for full P3-S02 sign-off** until distinct PASS-target gate is satisfied or explicitly waived.

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

Open before F4-S01 closeout:

- capture runtime PASS/WARN/FAIL evidence from F4-S01 template,
- verify diagnostics lane remains legacy authority (no ownership cutover writes),
- record closeout decision in roadmap + v-next + changelog.

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

## Phase 5 — Domain cutover + legacy retirement

- Cut over by domain in small slices:
  1) routing
  2) metadata
  3) optional lighting orchestration
- Retire duplicated template logic only after parity soak.
- Keep naming cleanup deferred to existing trigger gates.

### Phase 5 exit criteria

- Component is primary control plane with validated backward compatibility.

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
