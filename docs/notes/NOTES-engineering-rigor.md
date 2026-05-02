<!-- Description: Engineering rigor baseline for custom-component migration decisions, contract inventory, and explicit tough-spot tracking. -->
<!-- Version: 2026.05.02.6 -->
<!-- Last updated: 2026-05-02 -->

# NOTES — Engineering Rigor Baseline

## Intent (non-negotiable)

- No cowboy changes.
- No assumptions presented as fact.
- No install-specific hardcodes in tracked product logic.
- Discovery-first + capability-mapped behavior by default.
- If evidence is incomplete, say exactly what is missing and block risky progression.

## Evidence boundary (explicit)

This note is based on repository-contract inventory and documented diagnostics.
Live HA runtime state can differ at any moment due to startup timing, integration reload order, or transient unavailable entities.

Required to close this gap before write-path changes:

1. fresh runtime parity template output,
2. fresh route-trace + contract-validation output,
3. explicit comparison against legacy source-of-truth surfaces.

## Current contract inventory baseline (ma_control_hub + spectra_ls)

Control-hub `.inc` files inventoried:

- `packages/ma_control_hub/input_select.inc`
- `packages/ma_control_hub/input_boolean.inc`
- `packages/ma_control_hub/input_number.inc`
- `packages/ma_control_hub/input_text.inc`
- `packages/ma_control_hub/rest.inc`
- `packages/ma_control_hub/rest_command.inc`
- `packages/ma_control_hub/script.inc`
- `packages/ma_control_hub/automation.inc`
- `packages/ma_control_hub/template.inc`

Component legacy surface mapping baseline:

- `sensor.ma_active_target`
- `sensor.ma_active_control_path`
- `binary_sensor.ma_active_control_capable`
- `sensor.ma_control_hosts`
- `sensor.ma_control_host`
- `sensor.ma_control_targets`
- `sensor.spectra_ls_rooms_json`
- `sensor.spectra_ls_rooms_raw`

Static contract inventory snapshot:

- Distinct referenced entity/service surfaces in `packages/ma_control_hub/*.inc`: **59**
- Key referenced surfaces include:
  - `sensor.ma_*` routing/meta/now-playing derivatives,
  - `sensor.spectra_ls_rooms_*` room-map sources,
  - `input_select.ma_active_target`,
  - `input_boolean.ma_control_fallback_enabled`,
  - `script.ma_update_target_options`, `script.ma_auto_select`.

## Tough spots (must be surfaced; not glossed)

1. **Selection loop risk (High)**
   - `ma_auto_select` and `state_changed`-driven automation activity can conflict with component write-path trials.
   - Mitigation: single-writer switch + correlation IDs + debounce + reentrancy guard required before P3-S01 enablement.

2. **Fallback ambiguity risk (Medium)**
   - Static fallback hosts/entities still exist and can hide discovery-routing regressions when enabled.
   - Mitigation: preserve explicit fallback-off default and validate both fallback-off and fallback-on behavior with separate evidence.

3. **Parser-shape risk (Medium)**
   - Broad dual-mode payload parsing (native object + string JSON) has high coupling and drift risk.
   - Mitigation: keep shape contract explicit and fail noisy in diagnostics when shape assumptions break.

4. **Authority boundary risk (High)**
   - Legacy template graph mixes routing + selection + metadata concerns; unsafe to hand off all at once.
   - Mitigation: enforce P3 sub-slices with routing-only first, then selection, metadata later.

5. **Ghost-broadcaster stale-playing risk (High)**
   - Some players can continue reporting `playing` while effectively stale (progress clock not moving), causing stale metadata to remain selected/displayed.
   - Mitigation: enforce dual-threshold freshness policy in runtime + component parity (`input_number.ma_meta_stale_s` for `playing` freshness, `input_number.ma_meta_paused_hide_s` for paused hold/hide), and publish explicit suppression reasons (`playing_stale_hidden`, `paused_stale_hidden`, `long_idle_stale_hidden`) for deterministic operator triage.

## P1/P2 validation checkpoint status

- P1-S01: validated as read-only parity slice (legacy source-of-truth retained).
- P2-S01/P2-S02: validated with deterministic diagnostics and closure template support.

Still required on every P3 trial:

- rerun parity templates and capture fresh outputs in-slice,
- verify no flapping and no mismatches before widening scope.

## Active rolling validation/test ledger (metadata stack)

The active metadata stack now uses a single deterministic closeout checklist:

- `docs/testing/raw/meta_stack_end_to_end_validation_checklist.md`

Required discipline for all remaining slices in this lane:

1. capture pre-change baseline,
2. capture in-change probe evidence,
3. capture stale-root-cause probe evidence when stale/ghost behavior appears,
4. capture post-change closeout proof (build + OTA + git sync).

Step-3 consolidated runtime assessment surface:

- `docs/testing/raw/meta_stack_step3_full_validation.jinja` (single DT render covering scheduler, metadata policy/suppression, stale-root-cause classification, and ESP UX gate checks).

No metadata-stack slice is considered complete without a recorded evidence packet row in that checklist.

## Active scoped execution ledger (file-level, no-miss contract)

Purpose: prevent implementation miss risk when naming/contracts are introduced in real files by keeping one explicit done/remaining file map.

### MA authority-contract propagation scope

Completed (implemented in code):

- `custom_components/spectra_ls/const.py`
  - canonical MA authority mode/reason tokens centralized.
- `custom_components/spectra_ls/coordinator.py`
  - metadata-prep now emits tokenized `authority_mode`, `authority_gate_results`, and degraded-reason tokens.
- `custom_components/spectra_ls/diagnostics.py`
  - config-entry diagnostics now exports normalized `authority_contract` packet.
- `custom_components/spectra_ls/sensor.py`
  - shadow/control-center/meta-policy sensors now expose `authority_contract` attributes.
- `custom_components/spectra_ls/binary_sensor.py`
  - shadow control-capable binary sensor now exposes `authority_contract` attributes.

Completed (implemented in code, Slice A follow-up):

- `custom_components/spectra_ls/authority_contract.py`
  - shared packet-normalization helper added as canonical authority-contract builder.
- `custom_components/spectra_ls/services.yaml`
  - service-facing authority echo contract documented via `get_authority_contract`.
- `custom_components/spectra_ls/__init__.py`
  - response-capable `get_authority_contract` service added; optional metadata-prep refresh + packet echo implemented.
- `custom_components/spectra_ls/diagnostics.py` + `sensor.py` + `binary_sensor.py`
  - local authority-packet helper duplication removed; all surfaces now consume shared helper.

Execution rule (active):

- Any new authority/naming token added in code must be recorded here with exact file path and status (`completed`/`remaining`) in the same slice.

## Slice-A fabric file ownership integrity (required)

Purpose: prevent wrong-file patches and contract drift by forcing every data-fabric/authority edit through canonical file ownership boundaries.

### Canonical owner map (do not bypass)

- `custom_components/spectra_ls/authority_contract.py`
  - Owner for authority packet normalization/build shape (`authority_mode`, `authority_gate_results`, `authority_reasons`).
- `custom_components/spectra_ls/coordinator.py`
  - Owner for snapshot assembly, metadata-prep gate derivation, and authority diagnostics source fields.
- `custom_components/spectra_ls/diagnostics.py`
  - Owner for config-entry diagnostic export projection (must consume shared builder, no local packet shape forks).
- `custom_components/spectra_ls/sensor.py`
  - Owner for shadow/control-center attribute projection of authority packet.
- `custom_components/spectra_ls/binary_sensor.py`
  - Owner for binary-sensor authority projection attributes.
- `custom_components/spectra_ls/__init__.py`
  - Owner for authority-facing service lifecycle/wiring (registration, response-capability, unload cleanup).
- `custom_components/spectra_ls/services.yaml`
  - Owner for service contract schema/docs for authority retrieval endpoints.
- `custom_components/spectra_ls/const.py`
  - Owner for authority token constants and service-name constants.

### Required parity anchors (active)

- Runtime anchor: `packages/ma_control_hub/template.inc`
- Component anchor: `custom_components/spectra_ls/registry.py`

Rule: any behavior-visible authority/fabric slice must explicitly verify both anchors as `implemented`, `compatibility-shimmed`, or `deferred with rationale` in the same slice note/changelog.

### Anti-mispatch pre-edit checks (mandatory)

Before editing any fabric/authority behavior path:

1. identify changed field/contract,
2. route change to canonical owner file above,
3. confirm no parallel local helper/shape fork exists in projection files,
4. add/update changelog entry before functional edits,
5. record two-track disposition (runtime + component),
6. rerun parity review after fix iteration (parity → validate/debug/fix → parity).

### No-go conditions

- Introducing a second local authority-packet builder in projection files.
- Editing projection files (`diagnostics.py` / `sensor.py` / `binary_sensor.py`) without shared-owner alignment in `authority_contract.py` when shape changes.
- Service behavior change without synchronized update to `services.yaml` and `__init__.py` lifecycle handling.
- Token changes outside `const.py` without synchronized constant ownership review.

### Divergence handling

If strict lock-step ownership edits are not feasible in one slice, record explicit shim/defer rationale and impacted owner files in:

- `docs/CHANGELOG.md`, and
- this notes file under active execution ledger.

## Slice-B compact service/write-path integrity map (scheduler + metadata bridge)

Purpose: apply the same no-mispatch ownership rigor from Slice-A to the two highest-risk write lanes that drive behavior-visible handoff decisions.

### Lane 1 — Scheduler write path

Canonical owner files:

- `custom_components/spectra_ls/coordinator.py`
  - Owner for scheduler decision payload, candidate ranking context, guarded apply gating, and write attempt audit fields.
- `custom_components/spectra_ls/registry.py`
  - Owner for target/host/control-capable capability feed used by scheduler ranking and eligibility.
- `custom_components/spectra_ls/const.py`
  - Owner for scheduler status/action constants and write-control key names.
- `custom_components/spectra_ls/__init__.py`
  - Owner for scheduler service wiring and call lifecycle behavior.
- `custom_components/spectra_ls/services.yaml`
  - Owner for scheduler service contract schema/docs (inputs/outputs and dry-run semantics).

Allowed mutation boundary:

- Selection/ranking/apply behavior changes must start in `coordinator.py` and only propagate through service contracts/constants after owner alignment.
- Registry capability-shape changes that influence scheduler eligibility must be declared in `registry.py` first, then consumed in scheduler logic.

### Lane 2 — Metadata bridge write path

Canonical owner files:

- `custom_components/spectra_ls/coordinator.py`
  - Owner for metadata bridge stage orchestration, readiness gates, and bridge trial diagnostics payload.
- `custom_components/spectra_ls/__init__.py`
  - Owner for metadata bridge service invocation lifecycle and runtime dispatch handoff hooks.
- `custom_components/spectra_ls/services.yaml`
  - Owner for metadata bridge/validation service schema and dry-run/write semantics.
- `custom_components/spectra_ls/const.py`
  - Owner for metadata-bridge status/reason constants and write-control key names.
- `packages/ma_control_hub/script.inc`
  - Runtime owner for legacy-compatible metadata provider refresh dispatch path consumed by bridge-trigger compatibility behavior.

Allowed mutation boundary:

- Bridge-stage behavior, verdicting, and gate reasons are owned by `coordinator.py`; avoid ad-hoc stage mutation in service wiring files.
- Runtime dispatch compatibility behavior is owned by `packages/ma_control_hub/script.inc`; component bridge changes must not silently fork runtime dispatch semantics.

### Slice-B anti-mispatch preflight (mandatory)

Before scheduler/metadata bridge behavior edits:

1. classify lane (`scheduler` or `metadata_bridge`),
2. identify canonical owner file for the intended mutation,
3. confirm constants/service schema parity when behavior contract changes,
4. verify runtime parity anchor check outcome (`packages/ma_control_hub/template.inc`) and component parity anchor (`custom_components/spectra_ls/registry.py`),
5. update `docs/CHANGELOG.md` before functional edits,
6. record two-track disposition (`implemented` / `compatibility-shimmed` / `deferred with rationale`).

### Slice-B no-go conditions

- Scheduler decision/apply behavior changed outside `coordinator.py` without corresponding owner-file alignment.
- Metadata bridge stage semantics changed in service wiring/docs files without synchronized `coordinator.py` stage logic update.
- Bridge-trigger runtime dispatch assumptions changed without explicit runtime owner review in `packages/ma_control_hub/script.inc`.
- Behavior-visible lane edits merged without explicit two-track disposition and changelog note.

## Slice-C quick owner matrix (scheduler + metadata bridge)

Purpose: provide a one-screen execution matrix for rapid owner routing during active slices.

| Lane | Change intent | Edit here (owner) | Do not fork here | Required paired review |
| --- | --- | --- | --- | --- |
| Scheduler | candidate scoring / selected target / apply verdict | `custom_components/spectra_ls/coordinator.py` | ad-hoc scheduler logic in `sensor.py`, `diagnostics.py`, or docs-only schema files | `const.py`, `services.yaml`, `__init__.py` |
| Scheduler | capability eligibility inputs (`control_capable`, host/path readiness) | `custom_components/spectra_ls/registry.py` | local eligibility patches in service handlers | `coordinator.py` |
| Metadata bridge | stage flow, readiness gates, bridge verdict reasons | `custom_components/spectra_ls/coordinator.py` | bridge-stage rewrites inside `services.yaml` or caller wrappers | `const.py`, `__init__.py` |
| Metadata bridge | service call schema and response contract | `custom_components/spectra_ls/services.yaml` | hidden service-shape drift in coordinator payload-only changes | `__init__.py`, `coordinator.py` |
| Metadata bridge | runtime provider dispatch compatibility handoff | `packages/ma_control_hub/script.inc` | component-only shadow dispatch forks | `custom_components/spectra_ls/__init__.py`, `coordinator.py` |

Quick rule: if the intended behavior changes and the owner column is untouched, treat as no-go until routed to the canonical owner file.

## Slice-C enforcement micro-checklist (scheduler + metadata bridge)

Purpose: convert the quick owner matrix into a repeatable preflight/PR checklist so lane edits are merge-ready and auditable.

### Preflight (must pass before behavior edits)

- [ ] Lane identified: `scheduler` or `metadata_bridge`.
- [ ] Canonical owner file selected from Slice-C quick owner matrix.
- [ ] `Do not fork` boundary reviewed and acknowledged.
- [ ] Paired-review files identified and touched/reviewed as required.
- [ ] Changelog-first update completed (`docs/CHANGELOG.md`).

### PR readiness (must pass before merge)

- [ ] Two-track disposition recorded (`runtime`, `component`) as `implemented` / `compatibility-shimmed` / `deferred with rationale`.
- [ ] Runtime parity anchor status recorded (`packages/ma_control_hub/template.inc`).
- [ ] Component parity anchor status recorded (`custom_components/spectra_ls/registry.py`).
- [ ] No-go checks passed (no owner bypass, no silent service/schema drift, no runtime bridge dispatch fork).
- [ ] Roadmap parity sync complete (`docs/roadmap/v-next-NOTES.md` + `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`).

Ready-to-paste enforcement line:

`Slice-C enforcement: owner route confirmed, paired-review complete, no-go checks clear, two-track disposition recorded.`
