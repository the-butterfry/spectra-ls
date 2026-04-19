<!-- Description: Specification and phased roadmap for the Spectra LS custom Home Assistant component developed in parallel with existing runtime. -->
<!-- Version: 2026.04.19.3 -->
<!-- Last updated: 2026-04-19 -->

# Spectra LS Custom Component — Specification + Roadmap

## Purpose

Define a production-grade `custom_components/spectra_ls` program that runs **in parallel** with the existing HA package + ESPHome runtime, then incrementally migrates ownership without breaking deployed contracts.

Execution playbook reference: `esphome/spectra_ls_system/PARALLEL-PROGRAM-PLAYBOOK.md`.

## Product Principles (non-negotiable)

- Spectra is anonymized and user-portable by default.
- Discovery-first adaptation to each user’s HA entity topology.
- Capability-mapped routing and behavior gating.
- Minimal hardcoded install-specific entity IDs.
- Backward-compatible migration before replacement.

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

## Phased implementation roadmap

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

- Start orchestration writes behind compatibility shims.
- Preserve existing helper/script endpoints expected by ESPHome and dashboards.
- Add anti-loop safeguards (correlation IDs/debounce windows/reentrancy guards).

### Phase 3 exit criteria

- No route or selection flapping under dual-write operation.

## Phase 4 — Functional expansion beyond setup/settings

- Mode engine APIs for hardware-first policy.
- Profile APIs + options flow integration.
- Programmable action catalog.
- Crossfade/balance service layer implementation.

### Phase 4 exit criteria

- New features operate through component contracts while legacy surfaces remain intact.

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

1. `CUSTOM-COMPONENT-ROADMAP.md`
2. `v-next-NOTES.md`
3. `CHANGELOG.md`
4. `README.md` (or explicit no-material-change decision)

Missing one item means the slice is not done.

## Retroactive baseline docs (active references)

- Runtime architecture baseline: `esphome/spectra_ls_system/CODEBASE-RUNTIME-ARCHITECTURE.md`
- Control-hub architecture baseline: `packages/ma_control_hub/CONTROL-HUB-ARCHITECTURE.md`
- Dead-path cleanup matrix: `esphome/spectra_ls_system/DEAD-PATHS-CLEANUP.md`

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

## Verification matrix

- Contract parity checks (legacy vs component entities/attributes).
- Route determinism checks across ambiguous and non-ambiguous targets.
- Diagnostics health checks from existing `DEVTOOLS-TEMPLATES.local.md` + component diagnostics.
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
