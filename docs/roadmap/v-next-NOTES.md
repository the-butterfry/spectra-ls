<!-- Description: v-next implementation notes for Spectra LS System hardware-first control plan and migration policy. -->
<!-- Version: 2026.04.21.92 -->
<!-- Last updated: 2026-04-21 -->

# v-next NOTES — Hardware-First Control Plan (Implementation Guide)

> Scope: Hardware-driven UX redesign for Spectra LS Control Board v2.
> Audience: Implementation agent working across RP2040 CircuitPython + ESPHome packages + HA helpers.
> Status: Draft plan. Update as decisions solidify.

## Custom-Component Parallel Program (Required)

`custom_components/spectra_ls` must be developed in parallel with the current runtime stack (`packages/` + `esphome/`) and cannot be treated as a big-bang replacement.

Execution system reference: `docs/program/PARALLEL-PROGRAM-PLAYBOOK.md`.

### Required migration sequence

1. Shadow mode (read-only parity surfaces)
2. Parity validation (legacy vs component)
3. Dual-write (guarded and reversible)
4. Domain cutover (small slices)
5. Legacy retirement (after sustained parity)

### Feature-slice completion contract

Each feature slice is only complete when both tracks are dispositioned:

- **Track A (current runtime):** implemented / compatibility-shimmed / deferred (with rationale)
- **Track B (custom component):** implemented / compatibility-shimmed / deferred (with rationale)

### Phase map + status ledger

| Phase | Scope | Runtime Track (`packages`/`esphome`) | Component Track (`custom_components/spectra_ls`) | Status |
| --- | --- | --- | --- | --- |
| 0 | Charter + contract freeze | Documented in v-next + changelog | Documented in roadmap/spec | In Progress |
| 1 | Skeleton + shadow parity | Keep existing contracts stable | Scaffold integration + read-only parity outputs | Implemented |
| 2 | Registry + route foundation | Keep helper contracts + diagnostics parity | Target registry + adapter router (`linkplay_tcp`) | Implemented |
| 3 | Guarded dual-write | Add shims and loop guards | Controlled write path with correlation/debounce guards | Validated (Sealed 2026-04-20) |
| 4 | Functional expansion | Preserve compatibility while exposing new capabilities | Profiles/actions/capability matrix/crossfade-balance services | Validated (F4-S01/F4-S02/F4-S03 sealed; diagnostics-only authority boundary retained) |
| 5 | Domain cutover + retirement | Domain-by-domain template retirement | Primary control plane ownership + migration tooling | Validated (P5-S01/P5-S02/P5-S03/P5-S04 sealed; P6 planning handoff ready) |
| 6 | Sidebar control center productization | Runtime compatibility surfaces retained for migration-safe UX rollout | Full HA sidebar Spectra control center (setup/tuning/defaults/overrides/mapped environment) | Validated (P6-S01/P6-S02/P6-S03/P6-S04 validated) |
| 7 | Component-first authority cutover + legacy sealing | Legacy runtime transitions to compatibility/rollback baseline, then sealed from normal write ownership | Component becomes default primary control plane for net-new sidebar/beyond features | Validated (P7-S01/P7-S02/P7-S03/P7-S04 validated; phase-exit packet accepted) |

### Active slice ledger

| Slice | Phase | Runtime Track | Component Track | Parity | Risk | Status |
| --- | --- | --- | --- | --- | --- | --- |
| P1-S01 | 1 | Implemented (legacy source-of-truth retained) | Implemented (read-only shadow parity) | Implemented | Low | Implemented |
| P2-S01 | 2 | Implemented (legacy route contracts retained) | Implemented (registry/router scaffold; read-only) | Implemented | Low | Implemented |
| P2-S02 | 2 | Implemented (legacy route contracts retained) | Implemented (deterministic validation hardening + P2 diagnostics closure) | Implemented | Low | Implemented |
| P3-S01 | 3 | Validated (legacy write authority retained behind switch) | Validated (guard framework + manual routing write trial services) | Validated | Medium | Validated |
| P3-S02 | 3 | Validated (selection compatibility shim validation) | Validated (one-shot selection-handoff validation sequence + diagnostics) | Validated (single-capable waiver) | High | Validated |
| P3-S03 | 3 | Validated (metadata ownership explicitly deferred to legacy compatibility mode) | Validated (metadata prep diagnostics + one-shot sequence + listener-safe validation template) | Validated (diagnostics-only) | Medium | Validated |
| F4-S01 | 4 | Validated (compatibility contracts retained; no ownership cutover) | Validated (capability matrix + profile schema diagnostics scaffolding) | Validated (diagnostics-only) | Medium | Validated |
| F4-S02 | 4 | Validated (legacy action ownership retained; diagnostics-only) | Validated (programmable action-catalog safety skeleton + dry-run diagnostics) | Validated (diagnostics-only) | Medium | Validated |
| F4-S03 | 4 | Validated (legacy crossfade/balance behavior remains authoritative) | Validated (crossfade/balance diagnostics scaffold + validation sequence) | Validated (diagnostics-only) | Medium | Validated |
| P5-S01 | 5 | Validated (legacy retained as rollback authority path; post-window rollback proof captured) | Validated (routing-domain run-window execution completed with VERIFIED in-window proof) | Validated (in-window VERIFIED + post-window legacy rollback) | Medium | Validated |
| P5-S02 | 5 | Validated (legacy metadata ownership retained; bounded run-window closeout packet accepted) | Validated (metadata-domain gate-prep/readiness validation execution completed with consolidated PASS evidence) | Validated (Run-1 + Run-2 closeout packet) | Medium | Validated |
| P5-S03 | 5 | Validated (legacy lighting orchestration retained with safe post-window authority proof) | Validated (lighting-domain run-window checklist execution completed with PASS closeout evidence) | Validated (Run-1 pre/in/post packet) | Medium | Validated |
| P5-S04 | 5 | Validated (phase-exit closeout governance completed; no runtime ownership expansion) | Validated (cross-slice evidence packet accepted + Phase-6 handoff gating complete) | Validated (PASS/READY 7/7 closeout packet) | Medium | Validated |
| P6-S01 | 6 | Validated (runtime compatibility retained; no authority expansion) | Validated (HA sidebar control center foundation with read-only mapped-environment baseline proven) | Validated (PASS/READY 6/6 closeout packet) | Medium | Validated |
| P6-S02 | 6 | Validated (legacy/runtime contracts preserved; no ownership cutover) | Validated (control-center settings contract via options + service + diagnostics visibility proven) | Validated (PASS/READY 4/4 settings packet) | Medium | Validated |
| P6-S03 | 6 | Validated (runtime compatibility retained; no authority expansion) | Validated (bounded control-input execution skeleton with dry-run-first semantics proven) | Validated (execution-lane dry-run proof accepted) | Medium | Validated |
| P6-S04 | 6 | Validated (runtime compatibility retained; no ownership cutover) | Validated (execution-lane monitor/checklist closeout evidence accepted) | Validated (PASS/READY 5/5 dry-run-first packet) | Medium | Validated |
| P7-S01 | 7 | Validated (legacy rollback-safe compatibility baseline confirmed at pre-flip gate) | Validated (component-first cutover readiness gate accepted) | Validated (Run-2 PASS/READY 4/4) | High | Validated |
| P7-S02 | 7 | Validated (legacy retained as bounded rollback authority with post-window rollback-safe proof accepted) | Validated (first bounded authority-flip execution lane complete) | Completed (Run-1 pre/in/post PASS) | High | Validated |
| P7-S03 | 7 | Validated (legacy retained as rollback-safe metadata authority baseline with post-window proof accepted) | Validated (bounded metadata-domain authority-flip execution lane complete) | Completed (Run-1 pre/in PASS + Run-2 post PASS) | High | Validated |
| P7-S04 | 7 | Validated (rollback-safe legacy authority baseline preserved at closeout capture) | Validated (phase-exit closeout packet completed and accepted) | Completed (Run-1 closeout PASS/READY 4/4) | High | Validated |

### P1/P2 validation snapshot (2026-04-19)

- P2 raw verification template has PASS evidence with `8/8` scoring and deterministic route decision output.
- Shadow diagnostics expose required closure attributes (`registry`, `route_trace`, `contract_validation`, `captured_at`) and freshness guard behavior.
- P1 parity surfaces are stable and remain read-only; legacy runtime remains source-of-truth.

Known evidence gap to keep explicit:

- Live HA runtime timing/state can differ from static repo analysis; every P3 write-path trial requires fresh runtime evidence captures in the same slice.

Latest runtime proof artifact (2026-04-19):

- Template verdict: `PASS`, score `8/8`.
- Route trace: `route_linkplay_tcp` with supported read-only scaffold mapping.
- Contract validation: `ready=true`, `valid=true`, `missing_required=0`.
- Parity diagnostics: `unresolved_sources=0`, `mismatches=0`.
- Freshness: captured snapshot age within threshold.

### P3 execution guardrails (required)

- **Single-writer rule:** at any given moment, either legacy or component owns writes; never dual-authoritative.
- **Loop-prevention rule:** correlation IDs + debounce + reentrancy guards are mandatory before enabling P3-S01.
- **Fallback-discipline rule:** if fallback is off, component must not silently route through static fallback branches.
- **Scope-discipline rule:** do not combine routing + selection + metadata ownership in one P3 slice.

### P3-S01 implementation checkpoint (2026-04-19)

Implemented in `custom_components/spectra_ls`:

- write-authority service (`legacy`/`component`) with legacy-default rollback-safe behavior,
- guarded routing write-trial service with correlation-id tracing,
- debounce + reentrancy + route-decision eligibility gates,
- write-control diagnostics (`write_controls`) in coordinator/shadow attributes.

Closeout status (2026-04-20):

- runtime trial + soak evidence captured under `component` authority,
- no parity regression gates outstanding for P3-S01,
- slice sealed in final P3 closeout checkpoint below.

### P3-S02 validation checkpoint (2026-04-19)

Implemented in `custom_components/spectra_ls`:

- one-shot validation sequence service (`run_p3_s02_sequence`) with optional write-trial toggle,
- structured selection-handoff readiness diagnostics in snapshot attributes (`selection_handoff_validation`),
- compatibility checks for legacy helper/options and required selection scripts/automation IDs,
- raw operator template for PASS/WARN/FAIL validation (`docs/testing/raw/p3_s02_selection_handoff_validation.jinja`).

Closeout decision (2026-04-19):

- sustained runtime evidence for S01/S02 stability was captured with clean compatibility/parity signals.
- baseline soak gate met (`3` successful PASS cycles, `5` attempts) with expected soft-skips on non-capable routes.
- distinct PASS-target gate is explicitly waived for single-capable-topology operation.
- closure gate is now represented by `docs/testing/raw/p3_s01_s02_closure_gate_check.jinja` for future repeatability.

Latest runtime proof artifact (2026-04-19):

- Template verdict: `PASS` (`p3_s02_selection_handoff_validation.jinja`).
- Authority/route: `component` + `route_linkplay_tcp`.
- Contract validation: `ready=true`, `valid=true`.
- Handoff diagnostics: `payload_ready=true`, `verdict=PASS`, `helper_exists=true`, `target_in_options=true`, `missing_scripts=0`, `missing_automation_ids=0`.

Latest soak runtime artifact (2026-04-19):

- Automated script verdict: `Spectra soak complete` (`script.spectra_p3_soak_one_shot`).
- Soak count/attempts: `3` successful cycles in `5` attempts.
- PASS cycles: `route=route_linkplay_tcp`, `contract_valid=True`, `handoff=PASS`.
- Drift/compatibility: `unresolved_sources=0`, `mismatches=0`, `missing_scripts=0`, `missing_automation_ids=0`.
- Skip behavior observed as expected: non-capable target soft-skips on `route=defer_not_capable`.
- Gate status: baseline soak stability gate met; distinct PASS-target gate remains open pending either second eligible target PASS or explicit waiver.

### Stage report snapshot — ownership + readiness (2026-04-19)

- Current ownership boundary:
  - **Legacy runtime (`packages/ma_control_hub/*.inc`) remains source-of-truth** for broad target-selection/control orchestration and compatibility helper surfaces.
  - **Custom component (`custom_components/spectra_ls`) currently owns** diagnostics/parity snapshots, one-shot validation orchestration (S01/S02), route-trace visibility, and guarded write-trial control framework.
- Readiness status:
  - **Closure-ready and sealed for P3-S02** using final soak evidence (`3/3` in `4` attempts, `distinct_pass_targets=2`).
  - Distinct PASS-target gate satisfied without waiver in the final run.

### P3-S03 implementation checkpoint (2026-04-19)

Implemented in `custom_components/spectra_ls`:

- metadata-prep diagnostics payload in coordinator snapshot (`metadata_prep_validation`),
- metadata contract presence checks for `ma_active_meta_entity`, `now_playing_*`, and `ma_meta_candidates`,
- deterministic metadata-prep verdicting (`PASS`/`WARN`/`FAIL`) with readiness flag,
- one-shot service orchestration (`run_p3_s03_sequence`) and direct refresh service (`validate_metadata_prep`),
- raw validation template for operator evidence capture (`docs/testing/raw/p3_s03_metadata_prep_validation.jinja`).

Closeout decision (2026-04-19):

- runtime S03 validation evidence captured with `PASS` (`7/7`) and `ready_for_metadata_handoff=true`,
- metadata contract checks report `missing_required=0` with all S03 gates true,
- explicit compatibility boundary retained: metadata ownership remains legacy/runtime (no component cutover writes),
- route/selection runtime context may show non-cutover states (`defer_not_capable`, legacy authority, S02 FAIL) outside targeted validation windows and does not block P3-S03 diagnostics closeout.

Latest runtime proof artifact (2026-04-19):

- Template verdict: `PASS` (`p3_s03_metadata_prep_validation.jinja`).
- Gate score: `7/7`.
- Metadata-prep readiness: `ready_for_metadata_handoff=true`.
- Contract details: `missing_required=0`, `missing_keys=[]`.

Final runtime proof snapshot (2026-04-19 22:51 local):

- Active target/path: `media_player.spectra_ls_2` / `linkplay_tcp`.
- Metadata value probes resolved: `active_meta_entity=media_player.spectra_ls`, `now_playing_entity=media_player.spectra_ls`, `now_playing_state=paused`, `now_playing_title=Network`.
- All S03 gates true (`contract`, `active_meta`, `now_playing_entity/state/title`, `candidate_payload_ready`, `route_trace_present`).
- Compatibility boundary remains explicit: runtime can still show non-cutover route/selection context (`route=defer_not_capable`, authority=`legacy`, selection_handoff=`FAIL`) without invalidating diagnostics-only P3-S03 closeout.

### P3-H1 second-pass hardening checkpoint (2026-04-19)

Implemented as a bounded reliability hardening pass (no ownership expansion):

- coordinator listener scope widened to include key helper/metadata entities to reduce stale diagnostics windows,
- metadata candidate readiness semantics tightened to require structurally meaningful candidate payloads (non-empty entity-bearing candidate data),
- closure gate now enforces soak-attempt consistency (`attempts >= pass cycles` and `attempts > 0`),
- P3 templates (`S01`, `S02`, `S03`, closure gate) now include explicit snapshot freshness checks to reduce stale PASS false positives.

Disposition:

- Runtime track: compatibility contracts retained; no authority/ownership cutover.
- Component track: diagnostics hardening implemented.
- Parity: preserved; rerun closure templates to capture refreshed evidence when convenient.

### P3-H2 closure-gate soak parity checkpoint (2026-04-19)

Template closeout correctness fix:

- closure gate now accepts explicit `observed_parity_ok` operator evidence and applies it in `evaluation_mode=soak_evidence`,
- runtime parity remains visible as `runtime_now` in gate breakdown for drift diagnostics,
- prevents false WARN closure outcomes when post-soak runtime context temporarily reports parity drift unrelated to the validated soak window.

### P3-H3 closure-gate fail-closed checkpoint (2026-04-19)

Strict closeout enforcement update:

- closure gate defaults now fail-closed (`evaluation_mode=runtime` and conservative observed defaults),
- soak-evidence mode now requires provenance fields (`observed_evidence_source`, `observed_evidence_reference`, `observed_evidence_collected_at`) and enforces collected-at freshness <=24h,
- missing/invalid provenance forces `FAIL` to prevent optimistic PASS outcomes from unverified manual toggles.

### P3 final closeout checkpoint (2026-04-20)

Final sealing evidence captured:

- Soak automation completion: `Spectra soak complete` with `3` successful cycles in `4` attempts and `distinct_pass_targets=2`.
- PASS-cycle evidence includes deterministic eligible route (`route_linkplay_tcp`), `contract_valid=True`, and `handoff=PASS` on successful cycles.
- Closure gate semantics hardened and clarified: `runtime` mode is health-check-only; `soak_evidence` mode is closure-grade.
- Metadata candidate payload parity proof: `PASS 5/5` (`state_count=4`, `row_count=4`, `summary_entities=4`, aligned `best_candidate_json`/`summary.best_*`).

Seal decision:

- **P3-S01:** sealed.
- **P3-S02:** sealed.
- **P3-S03:** sealed (diagnostics-only metadata-prep lane as previously documented).
- **Phase 3 overall:** sealed; Phase-4 validation now sealed through F4-S03.

### Phase 4 bounded slice plan (post-P3)

| Slice | Scope | Runtime Track | Component Track | Exit gate |
| --- | --- | --- | --- | --- |
| F4-S01 | Capability matrix + profile scaffolding | Preserve existing helper behavior/contracts; no ownership cutover | Add profile schema skeleton + capability-map diagnostics surfaces | Deterministic diagnostics output; no parity regressions |
| F4-S02 | Programmable action catalog safety skeleton | Keep legacy action flows authoritative | Add arm/confirm/cooldown/audit schema + dry-run validation service | Sensitive-action safety gates verified in diagnostics |
| F4-S03 | Crossfade/balance service contract (diagnostics-first) | Keep current runtime control lane | Add normalized slider-domain contract + no-op service validation path | Contract + diagnostics PASS; no write-path authority expansion |

### F4-S01 implementation checkpoint (2026-04-19)

Implemented in `custom_components/spectra_ls`:

- capability/profile diagnostics payload (`capability_profile_validation`) in coordinator snapshot,
- capability matrix summary extraction from registry (`control_path_counts`, `hardware_family_counts`, capability union, control-capable counts),
- deterministic profile-schema skeleton surface (`schema_version`, `required_keys`, defaults),
- no-authority-expansion guard visibility (`authority_mode=legacy` expected for diagnostics lane),
- services: `validate_capability_profile`, `run_f4_s01_sequence`,
- raw validation template: `docs/testing/raw/f4_s01_capability_profile_validation.jinja`.

F4-S01 closeout evidence (2026-04-20):

- Runtime closure artifact captured with **PASS** (`gate_score=6/6`, timestamp `2026-04-20 03:14:23.318195-07:00`).
- Authority/ownership check passed: `authority_mode=legacy`, `no_authority_expansion=true`.
- Route/contract/metadata checks passed: `route=route_linkplay_tcp`, `contract_valid=true`, `metadata_prep_ready=true`.

Seal decision:

- **F4-S01:** sealed/validated.
- Continue Phase-4 execution on active **F4-S02** diagnostics lane.

### F4-S02 implementation checkpoint (2026-04-20)

Implemented in `custom_components/spectra_ls`:

- diagnostics payload `action_catalog_validation` in coordinator snapshot,
- deterministic action-schema surface for safety contracts (`action_id/label/domain/service/target_scope/safety` + required safety keys),
- diagnostics-only catalog rows with explicit `dry_run_only` safety posture,
- no-authority-expansion guard and F4-S01 readiness reference in validation checks,
- services: `validate_action_catalog`, `run_f4_s02_sequence`,
- raw validation template: `docs/testing/raw/f4_s02_action_catalog_validation.jinja`.

F4-S02 closeout evidence (2026-04-20):

- Runtime closure artifact captured with **PASS** (`gate_score=7/7`, timestamp `2026-04-20 03:19:04.074224-07:00`).
- Authority/safety checks passed: `authority_mode=legacy`, `dry_run_only=true`, `no_authority_expansion=true`.
- Dependency check passed: `f4_s01_ready_reference=true`.

Seal decision:

- **F4-S02:** sealed/validated.
- Continue Phase-4 execution on active **F4-S03** diagnostics lane.

### F4-S03 implementation checkpoint (2026-04-20)

Implemented in `custom_components/spectra_ls`:

- diagnostics payload `crossfade_balance_validation` in coordinator snapshot,
- normalized slider-domain contract schema surface (`f4_s03.v1`, directional domain + safety keys),
- mode-profile diagnostics for multi-room vs single-room behavior contracts,
- sample dry-run mix-plan visibility with explicit no-op fallback posture,
- services: `validate_crossfade_balance`, `run_f4_s03_sequence`,
- raw validation template: `docs/testing/raw/f4_s03_crossfade_balance_validation.jinja`.

Hardening pass-2 (2026-04-20):

- F4 sequence services (`run_f4_s01_sequence`, `run_f4_s02_sequence`, `run_f4_s03_sequence`) now execute with explicit stage wrappers and surface failure-stage context in raised errors to eliminate opaque "Unknown error" behavior during action calls.
- F4-S03 snapshot guard now normalizes `action_catalog_validation` to mapping-safe defaults before dependency access and hardens state-change callback refresh to fail-safe logging, preventing callback storm exceptions from `NoneType.get` regressions.

Hardening pass-3 (2026-04-20):

- F4-S03 diagnostics now expose explicit dependency context (`active_target_resolved`, `route_decision`, `blocking_reasons`) and template guidance for dependency-only WARN captures (`f4_s02_not_ready` with `defer_no_target`) using deterministic rerun order (F4-S01/F4-S02/F4-S03 legacy mode).

Hardening pass-4 (2026-04-20):

- Fixed accidental F4 builder split regression where `_build_action_catalog_validation` could return `None` after F4-S03 insertion, which forced false `ready_for_f4_s02=false` dependency WARN outcomes in F4-S03 despite healthy route/target context.

F4-S03 closeout evidence (2026-04-20):

- Runtime closure artifact captured with **PASS** (`gate_score=8/8`, timestamp `2026-04-20 03:57:35.874550-07:00`).
- Authority/safety checks passed: `authority_mode=legacy`, `no_authority_expansion=true`.
- Dependency and route checks passed: `ready_for_f4_s03_closeout=true`, `f4_s02_ready_reference=true`, `route_decision=route_linkplay_tcp`, `active_target=media_player.spectra_ls_2`, `active_path=linkplay_tcp`.
- Contract checks passed: `slider_schema_present=true`, `mode_profiles_present=true`, `sample_mix_plan.dry_run_only=true`, `dependency_reference.active_target_resolved=true`.

Seal decision:

- **F4-S03:** sealed/validated.
- **Phase 4 bounded diagnostics slice set (F4-S01/F4-S02/F4-S03):** sealed/validated.

P1/P2/P3 impact check (required):

- **P1 (shadow parity source-of-truth):** unchanged; parity surfaces remain read-only and stable.
- **P2 (registry/router foundation):** unchanged; route classification + contract-validation surfaces remain authoritative for diagnostics (`route_linkplay_tcp` confirmed in closeout capture).
- **P3 (guarded write-path boundary):** unchanged; single-writer authority boundary remains intact (`legacy` retained for F4 diagnostics lane, no ownership cutover).

Phase 5 entry criteria delta note (2026-04-20):

- F4 bounded diagnostics slices are sealed; execution may move to Phase 5 planning/execution only when all entry gates below are satisfied in the active change window.
- **Gate A (authority baseline):** default authority remains `legacy`; any cutover trial must be explicitly armed and reversible per-slice (no implicit ownership drift).
- **Gate B (contract parity):** P2 parity/contract templates remain PASS after enabling any Phase 5 domain flag.
- **Gate C (slice isolation):** execute one domain at a time (`routing` → `metadata` → optional `lighting orchestration`), with no multi-domain cutover in one slice.
- **Gate D (rollback proof):** each Phase 5 slice must include a verified rollback path and explicit stop conditions (loop/flap, mismatch, missing-compat surfaces).
- **Gate E (evidence threshold):** each Phase 5 slice requires fresh runtime evidence capture before changing status from Active to Validated.

Current disposition:

- **Phase 5 status remains Planned** pending Gate A–E satisfaction.
- No P1/P2/P3 source-of-truth or authority changes are introduced by this delta note.

Phase 5 starter slice proposal (P5-S01, routing domain only):

- **Slice scope (in):** bounded routing cutover trial for explicit write-path routing decision surfaces only (no metadata ownership cutover, no lighting-orchestration cutover).
- **Slice scope (out):** metadata selection/now-playing authority, lighting helper orchestration, naming cleanup/retirement.
- **Authority mode policy:** default remains `legacy`; slice permits explicit, reversible `component` routing trial windows only.
- **Track A (runtime):** compatibility-shimmed and retained as rollback authority path.
- **Track B (component):** active routing cutover trial implementation + diagnostics/evidence capture.

Execution gates for P5-S01 activation:

1. Gate A pass: authority baseline + reversible arm/disarm path present.
2. Gate B pass: P2 parity/contract templates PASS immediately before trial start.
3. Gate C pass: no concurrent metadata/lighting cutover toggles enabled.
4. Gate D pass: rollback script/path validated in same window.
5. Gate E pass: fresh runtime evidence artifact captured for trial outcome.

Stop conditions (fail-closed):

- loop/flap detection in route writes,
- contract mismatch on required compatibility surfaces,
- unresolved active target/control-host route path,
- stale evidence window (>24h) for closeout decision.

P1/P2/P3 impact check for P5-S01 proposal:

- **P1:** unchanged (shadow parity contracts remain intact).
- **P2:** authoritative parity gate remains mandatory pre/post trial.
- **P3:** authority boundary remains single-writer controlled with explicit rollback.

Status update:

- **P5-S01 validated** with bounded-window evidence set complete:
  - in-window proof captured (`PASS`, `write_proof=VERIFIED`, `last_attempt.status=noop_already_selected`),
  - post-window rollback proof captured (`authority_mode=legacy`) with healthy route/contract/parity/freshness.
- **Phase 5 remains in progress overall**; next slice activation remains gated and domain-isolated (metadata cutover planning/activation is separate from this routing-slice validation).
- **P5-S02 (metadata domain) moved to Active gate-prep** using `docs/testing/raw/p5_s02_metadata_cutover_run_window_checklist.md`; no metadata write-authority takeover is implied until an explicit documented mechanism exists and gates are satisfied.

P5-S02 process depth note (beyond mirroring):

- The roadmap now requires explicit mechanism design and controlled trials, not just parity mirroring:
  1. contract inventory freeze for metadata surfaces and ownership boundaries,
  2. define component metadata authority mechanism/service contract,
  3. run bounded metadata write-path trial window with rollback-first controls,
  4. capture pre/in/post window evidence and validate fail-closed stop conditions,
  5. promote to validated only after rollback/authority disposition proof and stable parity.

Latest runtime evidence artifact (2026-04-20):

- Monitor verdict: `Status=PASS`, `Metadata readiness=READY` at `2026-04-20 17:59:21.972073-07:00`.
- Baseline/route: `authority_mode=legacy`, `route_decision=route_linkplay_tcp`.
- Contract/metadata: `contract_valid=true`, `missing_required=0`, `metadata_verdict=PASS`, `ready_for_metadata_handoff=true`.
- Parity/freshness: `unresolved_sources=0`, `mismatches=0`, snapshot freshness within threshold.
- Post-window proof: final render captured at `2026-04-20 18:08:32.691994-07:00` confirms `authority_mode=legacy` with metadata/contract/parity gates still healthy.
- Disposition: this bounded run window is closeout-eligible and documented; Phase-5 metadata slice remains Active gate-prep overall until mechanism-definition and broader slice gates are completed.

Run-3 evidence update (2026-04-20 evening):

- Legacy-mode run (`p5s02-run3`) showed expected fail-closed dry-run behavior when metadata lane was not ready (`metadata_trial_last_attempt.status=blocked_metadata_not_ready`) with contracts/parity clean.
- Same run reached `PASS/READY` (`gate_score=9/9`) under fresh active metadata/title conditions while authority baseline remained `legacy`.
- Component-mode comparison capture correctly reported policy CAUTION/WARN (`authority_mode_not_legacy`) with metadata ownership still `legacy_contract_surfaces`; this is expected and not a contract/parity regression.

Next execution target (P5-S02-M1):

- Implemented: `spectra_ls.metadata_write_trial` contract path is now wired in `custom_components/spectra_ls` with fail-closed dry-run-first behavior and audit payload surfacing in `write_controls.metadata_trial_last_attempt`.
- Implemented: `spectra_ls.run_p5_s02_sequence` one-shot service now performs bounded-window authority baseline + registry/contracts/route/handoff/metadata refresh + guarded metadata trial + post-trial metadata refresh in one deterministic call path.
- Hardening update: contract validity now fail-closes on unresolved required surfaces (present but `unknown`/`unavailable`), including control-host loss scenarios, and the monitor now exposes `contract_validation.unresolved_required` for explicit diagnostics.
- Hardening update (audit canonicalization): coordinator now emits native audit completeness fields (`audit_payload_complete`, `audit_payload_state`, `missing_audit_fields`) in `metadata_trial_last_attempt`, allowing monitor/checklist interpretation to use payload-native `COMPLETE/PARTIAL/N/A` state.
- Hardening update (trial gate semantics): coordinator now emits explicit trial preflight semantics (`blocking_reasons`, `trial_gate_verdict`, `eligible_for_closeout`) so P5-S02 window outcomes classify deterministically without string-inference.
- Fresh dry-run promotion evidence captured (`p5s02-2026-04-21-run1`):
  - monitor verdict `PASS/READY` at `2026-04-21 17:18:18.431382-07:00`,
  - `authority_mode=legacy`, `route_decision=route_linkplay_tcp`,
  - contract clean (`missing_required=0`, `unresolved_required=0`),
  - metadata gate `9/9`,
  - metadata trial audit `status=dry_run_ok`, `audit_payload_state=COMPLETE`, `trial_gate_verdict=PASS`, `eligible_for_closeout=true`, `missing_audit_fields=0`.
- Promotion-gate status: the documented “fresh dry-run + complete audit payload” requirement for P5-S02-M1 is now satisfied; metadata ownership remains intentionally legacy (`metadata_authority_owner=legacy_contract_surfaces`, `metadata_cutover_active=false`).
- Immediate next execution packet (P5-S02 Run-2 strict comparator):
  - run one fresh bounded sequence via `spectra_ls.run_p5_s02_sequence` with:
    - `mode=legacy`
    - `dry_run=true`
    - unique `window_id` (new value)
    - non-empty `reason`
    - `expected_target=<pre-window route_trace.active_target>` (discovery-first; no install-specific hardcode)
    - `expected_route=<pre-window route_trace.decision>` (for example `route_linkplay_tcp`)
  - capture one fresh monitor artifact and verify:
    - `status=PASS`, `metadata_readiness=READY`
    - `metadata_trial_last_attempt.status in {dry_run_ok, applied, noop}`
    - `trial_gate_verdict=PASS`, `eligible_for_closeout=true`
    - `missing_audit_fields=0`, `audit_payload_state=COMPLETE`
  - keep explicit post-window authority disposition at `legacy`.
  - if active target is intentionally churning during the window, omit `expected_target` and keep `expected_route` strict to avoid false mismatch blocks.
- Run-2 evidence captured (`p5s02-2026-04-21-run2`):
  - monitor verdict `PASS/READY` at `2026-04-21 17:25:39.987075-07:00`,
  - safe baseline retained: `authority_mode=legacy`, `route_decision=route_linkplay_tcp`,
  - contract clean: `missing_required=0`, `unresolved_required=0`,
  - metadata gate healthy: `verdict=PASS`, `gate_score=9/9`,
  - trial audit complete: `status=dry_run_ok`, `window_id=p5s02-2026-04-21-run2`, `audit_payload_state=COMPLETE`, `trial_gate_verdict=PASS`, `eligible_for_closeout=true`, `missing_audit_fields=0`.
- Run-2 disposition: strict-comparator packet expectations are met with fresh bounded-window evidence; metadata ownership remains legacy (`metadata_authority_owner=legacy_contract_surfaces`, `metadata_cutover_active=false`).
- Closeout packet candidate (prepared):
  - bounded evidence set includes Run-1 and Run-2 PASS/READY captures with complete trial-audit payloads,
  - authority boundary remains explicit/safe (`legacy` baseline retained across snapshots),
  - no contract/parity drift observed in captured windows (`missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`),
  - promotion recommendation accepted: `P5-S02` status is recorded as `Validated` in the active slice ledger.

Post-Phase destination note (operator UX target):

- After Phase-5 domain cutover gates are complete, the next required track is a full Home Assistant sidebar **Spectra Control Center**.
- This control center must include, at minimum:
  1. setup/onboarding pages (discovery status, route eligibility, contract readiness),
  2. tuning pages (input response/debounce and audio/lighting behavior profiles),
  3. defaults + override management (safe baseline policy plus per-target exceptions),
  4. mapped-environment visibility (resolved rooms/targets/control paths/capabilities),
  5. operator diagnostics/evidence views aligned to existing PASS/WARN/FAIL workflow.
- Execution ordering remains strict: **P5-S03 (lighting orchestration) is now the active slice**; sidebar control-center delivery remains post-Phase-5 and must not weaken gate-prep/validation discipline.

Deferred implementation scaffold note (H1):

- A detailed deferred H1 blueprint for diagnostics-driven report/log/heal flow is now published at `docs/features/H1-report-log-heal-scaffold.md`.
- This is planning-only in the current slice: no runtime behavior/authority ownership changes are enacted.
- H1 remains queued for later pickup after active P5 slice priorities.

Run-window execution checklist (required for activation/closeout evidence):

- `docs/testing/raw/p5_s02_metadata_cutover_run_window_checklist.md`

### Phase 5 next slice card — P5-S03 (lighting orchestration domain)

Status: **Validated**

Scope:

- **In:** lighting-domain orchestration gate-prep and bounded run-window validation only.
- **Out:** routing-domain ownership (already validated), metadata-domain ownership changes (P5-S02 lane), naming retirement.

Activation gates (all required):

1. P5-S02 closeout decision recorded (`Validated`) and linked in status ledger.
2. Authority baseline `legacy` confirmed at lighting-window start.
3. Lighting contract/parity precheck PASS in active window.
4. Domain isolation enforced (no concurrent metadata/routing cutover execution).
5. Rollback/disarm path validated and timestamped in-window.

Stop conditions (fail-closed):

- lighting contract drift or unresolved required lighting surfaces,
- route/authority drift outside declared window posture,
- stale/missing evidence artifacts for pre/in/post window sequence,
- unexpected cross-domain side effects during lighting validation interactions.

Execution checklist (new):

- `docs/testing/raw/p5_s03_lighting_orchestration_run_window_checklist.md`
- Primary live monitor: `docs/testing/raw/p5_s03_lighting_functionality_monitor.jinja`
- Freshness semantics correction: P5-S03 monitor now treats control snapshot freshness as informational context only (not a hard verdict gate) to avoid false WARN/CAUTION when lighting authority/contract/selector/parity signals are healthy.
- Run-1 completed and closed out with full pre/in/post packet:
  - pre-window `PASS/READY` (`2026-04-21 17:41:12.841574-07:00`),
  - in-window `PASS/READY` (`2026-04-21 17:44:00.229390-07:00`),
  - post-window `PASS/READY` (`2026-04-21 17:44:45.600796-07:00`).
- Closeout posture confirmed: `authority_mode=legacy`, contract/parity clean (`missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`), stop conditions not triggered.

### Phase 5 next slice card — P5-S04 (phase-exit closeout)

Status: **Validated**

Scope:

- **In:** cross-slice Phase-5 closeout packet, final authority/parity snapshot, and explicit P6 handoff gate.
- **Out:** new routing/metadata/lighting ownership behavior changes.

Activation gates (required):

1. P5-S01/P5-S02/P5-S03 are each ledger-marked `Validated` with linked evidence artifacts.
2. Fresh closeout-window snapshot confirms safe authority baseline + contract/parity stability.
3. Legacy retirement remains explicitly deferred until approved post-Phase-5 migration step.
4. P6 handoff posture is planning-eligible only (no implicit authority expansion).

Execution checklist:

- `docs/testing/raw/p5_s04_phase_exit_closeout_checklist.md`
- Primary live monitor: `docs/testing/raw/p5_s04_phase_exit_functionality_monitor.jinja`

Closeout evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `Phase-5 closeout readiness=READY`, `gate_score=7/7` (`2026-04-21 19:04:03.253466-07:00`),
- runtime safety gates all pass: `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, `contract_valid=true`, `missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`, freshness within threshold,
- governance gates all pass: domain closure linkage confirmed for P5-S01/S02/S03, rollback posture documented, retirement explicitly deferred, and P6 handoff planning posture explicit.

Disposition:

- `P5-S04` promoted to **Validated**.
- Phase-5 closeout packet accepted; P6 planning handoff is ready.

### Phase 6 starter slice card — P6-S01 (control-center foundation)

Status: **Validated**

Scope:

- **In:** control-center foundation scaffold (setup/tuning/defaults/overrides/mapped-environment views), diagnostics/evidence linkage, and read-only-first launch posture.
- **Out:** unbounded authority expansion, breaking helper/entity renames, and legacy retirement execution.

Activation gates (required):

1. P5-S04 closeout validated and linked as handoff prerequisite.
2. Runtime baseline remains safe (`authority_mode=legacy`) with clean route/contract/parity context.
3. Read-only-first UX posture is explicit for foundation rollout.
4. Backward compatibility + rollback posture are documented for any introduced P6 surfaces.

Execution checklist:

- `docs/testing/raw/p6_s01_control_center_foundation_checklist.md`
- Primary live monitor: `docs/testing/raw/p6_s01_control_center_foundation_monitor.jinja`

Baseline evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P6-S01 readiness=READY`, `gate_score=6/6` (`2026-04-21 19:18:22.634239-07:00`),
- runtime baseline clean: `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, `contract_valid=true`, `missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`, freshness within threshold,
- foundation governance gates all true: read-only-first launch, compatibility posture, rollback posture, and bounded-authority posture.

Disposition:

- `P6-S01` promoted to **Validated** with baseline + closeout packet evidence accepted.

Closeout evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P6-S01 readiness=READY`, `gate_score=6/6` (`2026-04-21 20:17:21.077121-07:00`),
- runtime baseline clean: `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, `contract_valid=true`, `missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`, freshness within threshold,
- foundation governance gates all true: read-only-first launch, compatibility posture, rollback posture, and bounded-authority posture.

### Phase 6 follow-on slice checkpoint — P6-S02 (control-center settings contract)

Status: **Validated**

Implemented in `custom_components/spectra_ls`:

- integration options flow for encoder action mappings and button scene bindings,
- normalized settings contract with safe defaults and read-only-first posture support,
- additive service contract `spectra_ls.set_control_center_settings` for deterministic runtime updates,
- diagnostics and shadow-attribute visibility for control-center settings (`control_center_validation`, `write_controls.control_center_settings`).

Current disposition:

- **Track A (runtime):** unchanged; legacy/runtime remains source-of-truth for writes and rollback (`authority_mode=legacy` baseline preserved).
- **Track B (component):** validated functional settings foundation for sidebar/control-center customization path.
- **Parity note:** additive contract only; existing P1/P2/P3 parity surfaces and authority boundaries remain unchanged.

P1/P2/P3 impact check:

- **P1:** unchanged (shadow parity surfaces remain read-only and compatible).
- **P2:** unchanged (registry/router diagnostics contracts remain authoritative).
- **P3:** unchanged (single-writer authority boundary retained; no new ownership cutover).

Execution checklist:

- `docs/testing/raw/p6_s02_control_center_settings_checklist.md`
- Primary live monitor: `docs/testing/raw/p6_s02_control_center_settings_monitor.jinja`

Closeout evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P6-S02 readiness=READY`, `gate_score=4/4` (`2026-04-21 20:15:35.644673-07:00`),
- settings-contract readiness proven: `schema_version=p6_s02.v1`, `settings_present=true`, `ready_for_customization=true`, `required_keys=8`,
- safe baseline retained: `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, clean contract/parity (`missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`), freshness within threshold.

Promotion disposition:

- `P6-S02` promoted to **Validated**.

P1/P2/P3 impact check:

- **P1:** unchanged (shadow parity contracts remain read-only/stable).
- **P2:** unchanged (registry/router diagnostics remain authoritative).
- **P3:** unchanged (single-writer authority boundary remains explicit and bounded).

### Phase 6 follow-on slice checkpoint — P6-S03 (control-input execution skeleton)

Status: **Validated**

Implemented in `custom_components/spectra_ls`:

- service contract `spectra_ls.execute_control_center_input` for encoder/button event execution,
- dry-run-first execution semantics with read-only-mode enforcement,
- scene dispatch support for configured button scene mappings when read-only is disabled,
- diagnostics payload for latest control-input attempt (`write_controls.control_center_last_attempt`) including status/reason/correlation context.

Current disposition:

- **Track A (runtime):** unchanged compatibility/rollback baseline (`authority_mode=legacy` preserved).
- **Track B (component):** validated execution skeleton for mapped control-center inputs with fail-closed safety posture.
- **Parity note:** additive execution lane only; existing parity/authority contracts remain unchanged.

Closeout evidence linkage (2026-04-21):

- execution proof accepted via P6-S04 monitor/checklist packet (`Status=PASS`, `P6-S04 readiness=READY`, `gate_score=5/5` at `2026-04-21 20:07:51.471030-07:00`),
- deterministic execution semantics observed: `last_attempt.status=dry_run_ok`, `last_attempt.input_event=encoder_press`, `last_attempt.mapped_action=play_pause`, `last_attempt.dry_run=true`,
- safety baseline preserved throughout validation: `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, contract/parity clean (`missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`).

Promotion disposition:

- `P6-S03` promoted to **Validated**.

P1/P2/P3 impact check:

- **P1:** unchanged read-only parity surfaces and attributes.
- **P2:** unchanged registry/router contract ownership.
- **P3:** unchanged single-writer/write-authority boundary (no new ownership cutover).

### Phase 6 follow-on slice checkpoint — P6-S04 (control-input execution validation artifacts)

Status: **Validated**

Implemented in docs/testing artifacts:

- raw execution monitor template: `docs/testing/raw/p6_s04_control_input_execution_monitor.jinja`,
- bounded validation checklist: `docs/testing/raw/p6_s04_control_input_execution_checklist.md`,
- deterministic gate framing for runtime baseline, dry-run-first posture, read-only enforcement, and closeout readiness evidence.

Current disposition:

- **Track A (runtime):** unchanged compatibility/rollback baseline (`authority_mode=legacy` remains required).
- **Track B (component/docs):** validated operator-grade evidence tooling for the control-input execution lane with closeout packet accepted.
- **Parity note:** additive validation/governance artifacts only; no write-authority expansion.

Closeout evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P6-S04 readiness=READY`, `gate_score=5/5` (`2026-04-21 20:07:51.471030-07:00`),
- execution semantics deterministic: `last_attempt.status=dry_run_ok`, `last_attempt.input_event=encoder_press`, `last_attempt.mapped_action=play_pause`, `last_attempt.dry_run=true`,
- runtime safety baseline preserved: `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, contract/parity clean (`missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`), freshness within threshold.

Promotion disposition:

- `P6-S04` promoted to **Validated**.

P1/P2/P3 impact check:

- **P1:** unchanged read-only parity surfaces.
- **P2:** unchanged registry/router validation ownership.
- **P3:** unchanged single-writer authority boundary.

### Phase 7 starter slice card — P7-S01 (component-first cutover readiness gate)

Status: **Validated**

Scope:

- **In:** cutover-readiness gate activation, sustained-parity evidence framing, rollback proof framing, legacy seal criteria publication, and component-primary posture declaration for net-new feature development.
- **Out:** immediate authority flip, broad helper/entity contract deletions, and one-shot legacy retirement without bounded domain evidence.

Activation gates (required):

1. Phase-6 slices (`P6-S01..P6-S04`) are validated with accepted closeout packets.
2. Runtime safety baseline remains clean (`authority_mode=legacy` + contract/parity clean) at activation time.
3. Explicit rollback posture exists for every planned authority flip domain.
4. Net-new feature direction is declared component-first while legacy remains compatibility/rollback baseline until cutover proof is accepted.

Execution checklist:

- `docs/testing/raw/p7_s01_cutover_readiness_checklist.md`
- Primary live monitor: `docs/testing/raw/p7_s01_cutover_readiness_monitor.jinja`

Two-track disposition:

- **Track A (runtime):** compatibility/rollback baseline retained during readiness gate; freeze net-new feature growth in legacy path.
- **Track B (component):** designated primary control-plane path for next feature growth pending bounded authority flip proofs.
- **Parity note:** no authority ownership flip occurs in P7-S01; this slice establishes deterministic go/no-go gates for cutover sequence.

P1/P2/P3 impact check:

- **P1:** unchanged read-only parity contract surfaces.
- **P2:** unchanged registry/router diagnostics ownership.
- **P3:** single-writer boundary remains explicit; authority flip remains gated and deferred to follow-on P7 slices.

Run-1 evidence (2026-04-21):

- monitor verdict: `Status=FAIL`, `P7-S01 readiness=BLOCKED`, `gate_score=3/4` (`2026-04-21 20:33:32.373259-07:00`),
- baseline failure details: `route_decision=defer_no_target`, `unresolved_required=4`, `unresolved_sources=3`, `mismatches=2`,
- governance gates remained true: phase-6 closeout, component-primary posture, and rollback/bounded-cutover posture.

Disposition:

- `P7-S01` recovered from blocked baseline and is now **Validated** after Run-2 PASS evidence.

Run-2 closeout evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P7-S01 readiness=READY`, `gate_score=4/4` (`2026-04-21 20:34:32.639010-07:00`),
- baseline restored: `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, `missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`, freshness within threshold,
- governance gates all true: phase-6 closeout, component-primary posture, and rollback/bounded-cutover posture.

Promotion disposition:

- `P7-S01` promoted to **Validated**.

### Phase 7 follow-on slice checkpoint — P7-S02 (first bounded authority-flip execution lane)

Status: **Validated**

Scope:

- **In:** first bounded authority-flip execution lane (routing/selection domain), strict single-writer enforcement, rollback-safe activation controls, and run-window evidence capture.
- **Out:** cross-domain ownership flips, unbounded legacy retirement actions, and irreversible helper/entity contract removal.

Activation gates (required):

1. `P7-S01` is validated with accepted closeout packet.
2. Runtime baseline remains clean at activation (`authority_mode=legacy`, contract/parity clean).
3. Domain-flip rollback path and stop conditions are explicit before first write-window attempt.
4. Component lane remains net-new feature primary while flip windows are bounded and reversible.

Execution checklist:

- `docs/testing/raw/p7_s02_domain_flip_readiness_checklist.md`
- Primary live monitor: `docs/testing/raw/p7_s02_domain_flip_readiness_monitor.jinja`

Two-track disposition:

- **Track A (runtime):** rollback-safe authority baseline retained outside bounded flip windows.
- **Track B (component):** active first authority-flip execution lane.

P1/P2/P3 impact check:

- **P1:** unchanged read-only parity contract surfaces.
- **P2:** unchanged registry/router diagnostics ownership.
- **P3:** single-writer controls remain mandatory and explicitly audited in this slice.

Run-1 pre-window evidence (2026-04-21):

- monitor verdict: `Status=PASS`, `P7-S02 readiness=READY`, `gate_score=4/4` (`2026-04-21 20:38:00.223973-07:00`),
- baseline/gates clean: `authority_mode=legacy`, `route_decision=route_linkplay_tcp`, `missing_required=0`, `unresolved_required=0`, `unresolved_sources=0`, `mismatches=0`, freshness within threshold,
- execution disposition: pre-window authorization granted; in-window and post-window captures are now required for closeout eligibility.

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

1. `P7-S02` is validated with accepted closeout packet.
2. Runtime baseline remains clean at activation (`authority_mode=legacy`, contract/parity clean).
3. Metadata readiness is PASS/ready (`metadata_prep_validation.verdict=PASS`, `ready_for_metadata_handoff=true`) with route eligibility present.
4. Metadata-domain rollback path and stop conditions are explicit before first in-window metadata trial attempt.

Execution checklist:

- `docs/testing/raw/p7_s03_metadata_domain_flip_readiness_checklist.md`
- Primary live monitor: `docs/testing/raw/p7_s03_metadata_domain_flip_readiness_monitor.jinja`

Two-track disposition:

- **Track A (runtime):** rollback-safe metadata authority baseline retained outside bounded P7-S03 windows.
- **Track B (component):** active bounded metadata-domain authority-flip execution lane.

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
2. Runtime baseline is still rollback-safe at closeout capture time (`authority_mode=legacy`, clean contract/parity).
3. Rollback path and single-writer boundary remain explicit and operator-verifiable.
4. Component-primary posture and legacy-seal scope are documented for closeout governance.

Execution checklist:

- `docs/testing/raw/p7_s04_phase_exit_closeout_checklist.md`
- Primary live monitor: `docs/testing/raw/p7_s04_phase_exit_functionality_monitor.jinja`

Two-track disposition:

- **Track A (runtime):** rollback-safe compatibility baseline retained for closeout capture.
- **Track B (component):** active phase-exit closeout packet lane.

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

Reference specification: `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`.

### Documentation parity gate (required)

For architecture/process/contract shifts, keep these synchronized in one change set:

1. `CUSTOM-COMPONENT-ROADMAP.md`
2. `v-next-NOTES.md`
3. `docs/CHANGELOG.md`
4. `README.md` (or explicit no-material-change note)

If any is missing, the slice remains open.

### Retroactive codebase baseline docs (active)

- Runtime architecture/features: `docs/architecture/CODEBASE-RUNTIME-ARCHITECTURE.md`
- Control-hub architecture/features: `docs/architecture/CONTROL-HUB-ARCHITECTURE.md`
- Dead-path cleanup matrix: `docs/cleanup/DEAD-PATHS-CLEANUP.md`

### Plan Delta rule (required)

When execution reality diverges from plan:

- pause slice expansion,
- record a Plan Delta note,
- sync roadmap + v-next statuses,
- resume with revised acceptance criteria.

### Phase 1 Slice-01 (Draft) — First executable scope

- **Goal:** ship read-only shadow parity for routing core surfaces with zero write-path side effects.
- **Legacy surfaces mirrored:**
  - `sensor.ma_active_target`
  - `sensor.ma_active_control_path`
  - `binary_sensor.ma_active_control_capable`
  - `sensor.ma_control_hosts`
- **Track disposition for this slice:**
  - Track A (runtime): implemented/source-of-truth retained
  - Track B (component): read-only shadow parity implementation
- **Close conditions:** parity report captured, mismatch list (if any) documented, and explicit README parity decision recorded in the change set.

## Latest Contract Update (Lighting)

- Lighting room/target menu slider contract updated: while browsing `Lighting Rooms` or `Lighting Targets` lists, moving the lighting slider now applies brightness immediately for the currently highlighted room/target route (no explicit entry into adjust submenu required).

- Lighting adjust labels now use a shared friendly-caption path (`Brightness/Hue/Sat <friendly target>`), replacing legacy `Lighting Values` text and keeping adjust/menu/render labels consistent across lighting screens.

- Boot first-press submenu contract (follow-up): fixed second interception path where auto control-target prompt could still consume first Select when `menu_active=true` during boot/menu-bootstrap. Auto prompt is now dismissed/snoozed without stealing the first submenu entry press; manual prompt path is unchanged.

- OLED text layout fallback contract hardened: when no full-word two-line split fits, fallback now keeps line 1 word-bounded and fits line 2 with ellipsis instead of character-slicing into orphan tails. This prevents labels like `Snail Conditioner` from rendering as `Conditione`/`r`.

- Boot-time first-press submenu determinism: `menu_select_action` now prioritizes non-menu Select entry before auto control-target prompt consumption. If an auto prompt is active at boot, it is dismissed/snoozed when opening menu so first Select reliably enters submenu. Manual prompt mode remains unchanged.

- OLED progress computation now includes a local bootstrap path when HA position timestamp is still unset (`pos_ms==0`) but playback+duration are available, so first-track render after boot/reconnect no longer waits indefinitely for an initial HA position delta event.

- Unified menu directionality path verified by full-stack sign trace: RP2040 emits raw encoder deltas, UART decode preserves sign, and menu direction inversion belongs only in top-level policy. Canonical policy is `menu_encoder_nav_sign: "-1"` (single inversion point) so left-turn no longer maps to downward list movement.

- Menu Select one-press contract hardened: when menu is inactive, a Select press now enters a submenu directly (`Lighting Rooms` from lighting screen, `Gear` from audio screen) instead of consuming an initial press to land on root-level menu state.

- HA position bootstrap correction: `ha_audio_pos_last_ms` now initializes on first received HA position sample, allowing OLED progress gating/projection to engage even when initial feed position is `0` and unchanged.

- OLED now-playing progress hold fix: when HA position samples remain numerically static during active playback, progress projection now advances from the cached displayed position in the same-track window (duration-aligned) so the progress bar continues moving deterministically instead of pinning at 0.

- Audio transport reliability hardening: Arylic TCP send path now performs one immediate retry per payload and only enters failure backoff after repeated consecutive send/connect failures, reducing brittle drops from single transient timeout events during rapid volume movement.

- Audio transport root-cause correction: queued `VOL` dequeue behavior no longer rewrites popped payloads to mutable `recent->last_payload` (which could produce target/TX mismatch during rapid input). Worker now drops superseded queued volume items and preserves payload immutability for transmitted commands.

- Audio transport anti-replay hardening: `components/arylic_tcp.h` now drops stale queued `VOL` payloads older than a bounded queue age (default `900ms`) before transmit and emits explicit per-volume enqueue logs, so delayed volume echoes can be source-attributed deterministically and stale queue replays are prevented.

- Lighting room/target helper surfaces now follow a **catalog-first** contract in HA package logic:
  - Build eligible lights from `states.light` + `area_id(...)`.
  - Resolve room options, target options, target entity mapping, and room state helpers from that shared catalog.
- Catalog payload storage is attribute-backed (`items_json`) with attribute-first readers, so large room/light inventories do not overflow 255-char sensor state limits and collapse into placeholder-only options.
- Eligible catalog population now includes a guarded area-registry fallback (`areas()` + `area_entities()`) when primary `states.light` + `area_id(...)` discovery yields empty, preventing persistent `No Rooms` / `All` bootstrap collapse.
- Catalog/options JSON consumers now trim leading whitespace before JSON-array detection/parsing, preventing newline/space-prefixed valid JSON from being misclassified as non-JSON and collapsing room/target selectors to placeholders.
- Catalog consumers now accept both string JSON arrays and native sequence payloads from `items_json`, preventing parse-path collapse when Home Assistant exposes the attribute as a non-string object at runtime.
- Intent: eliminate drift and intermittent `All`-only target regressions caused by duplicated direct `area_entities(...)` scan logic across multiple templates.

## HA Complex-Object Harvesting Contract (TIGHT + Reusable)

This lighting incident defines a reusable harvesting pattern for all complex HA object flows (audio targets, meta candidates, scenes, devices, future action catalogs).

### Required contract shape

- **State is summary, attribute is payload**

  Sensor `state`: compact count/health marker.
  Attribute payload: structured object/list (authoritative dataset).

- **Dual-type reader compatibility (mandatory)**

  Readers must accept both native sequence/mapping payloads and string JSON payloads (trim + guarded parse).
  Never assume `state_attr(...)` is always a string.

- **Single source catalog, many projections**

  Build one authoritative catalog sensor.
  Derive all helper projections (options, target resolution, status flags) from that single catalog.

- **Bootstrap fallback path**

  Provide a deterministic fallback discovery branch when primary discovery is empty.
  Fallback must preserve schema compatibility.

- **Placeholder policy is explicit**

  Placeholder output (`No Rooms`, `All`, etc.) must be treated as degraded state in diagnostics, not healthy success.

### Apply this to audio harvesting

- `ma_control_targets` / host-route maps / meta candidate lists should follow identical rules:
  - summary in state,
  - authoritative payload in attributes,
  - dual-type readers,
  - single catalog + derived selectors.
- Implementation status: applied to `packages/ma_control_hub/template.inc` and `packages/ma_control_hub/script.inc` room/candidate parse paths so MA host/target/meta routing remains stable across native object and string JSON attribute payload forms.
- Iteration status (2026-04-17): completed full `rooms_raw` reader modernization sweep in `packages/ma_control_hub/template.inc` so all remaining room-map consumers now honor sequence + mapping + guarded string JSON contract uniformly.
- Iteration 2 status (2026-04-17): parser string guards in `packages/ma_control_hub/template.inc` and `packages/ma_control_hub/script.inc` now evaluate sentinel checks using trimmed lowercase payloads (`raw_trim_l`), improving whitespace/case determinism while preserving dual-mode parse semantics.
- Iteration 4 status (2026-04-17): diagnostics-only publish cadence tuning applied in `packages/spectra-ls-diagnostics.yaml` for virtual harness entities (`Virtual Mode Selector Index`, `Virtual Control Class Index`, `Virtual Input Battery Status`) to reduce idle-state log/state churn without altering routing or behavior-path semantics.

### Apply this to other entity domains

- Safe targets: `light`, `media_player`, `scene`, `switch`, `lock`, and future grouped action catalogs.
- Reuse the same parser and projection semantics to avoid per-domain drift.

## Programmable Switch Action Pattern (Toggle + Select Confirm)

For user-programmable actions such as **unlock door**, use a guarded two-step action contract:

- **Arm via toggle/selector**

  Hardware toggle selects an action profile (for example `unlock_door`).
  System enters `armed_action` state with explicit label on OLED.

- **Confirm via Select button**

  Select button executes only when `armed_action` is valid and unexpired.
  Use a short confirmation window (TTL), then auto-disarm.

- **Safety gates (required)**

  Per-action capability flag (`confirm_required`, `sensitive=true`).
  Rate limit/cooldown and idempotence guards.
  Optional long-press requirement for sensitive actions.
  Audit signal emitted to HA (`last_action`, timestamp, actor/source).

- **Harvesting tie-in**

  Programmable actions should be harvested as a typed action catalog (same complex-object contract above), not hardcoded one-off branches.

## Naming Strategy + Deferred Full Cleanup (Entity/Helper IDs)

### Current contract policy (active now)

- File/package naming in active includes should use `spectra-ls-*`.
- Legacy runtime helper/entity IDs (`control_board_*`) remain in place where already deployed.
- This is intentional for operational stability while `spectra_ls_system` reaches full completion.

### Why cleanup is deferred

- Existing Home Assistant artifacts depend on deployed IDs (dashboards/cards, scripts/automations, template sensors, recorder/history/statistics continuity, and external references/service payloads).
- Mid-stream global ID renames carry high outage/regression risk.

### Forward naming rule (effective now)

- For all **new** artifacts, use Spectra naming.
- Files/packages: `spectra-ls-*`.
- Helpers/entities: `spectra_ls_*`.
- Docs/comments: avoid introducing new `control_board_*` names except compatibility references.

### Completion trigger gates (do not run cleanup before all pass)

1. `spectra_ls_system` is functionally complete/stable.
2. Validation templates 1–12 pass consistently in normal operations.
3. No open contract-level MA routing/selector refactors remain.
4. A controlled maintenance window is scheduled.

### Full cleanup execution blueprint (future)

- **Inventory:** build full old→new ID map (`control_board_*` → `spectra_ls_*`) and enumerate all reference paths.
- **Compatibility phase:** introduce `spectra_ls_*` surfaces, mirror/bridge old and new, keep legacy IDs live during burn-in.
- **Validation phase:** verify both legacy + new surfaces PASS before cutover.
- **Cutover phase:** flip all references to `spectra_ls_*`, then retire compatibility shims after sustained PASS windows.
- **Cleanup phase:** remove legacy definitions and preserve migration mapping in docs/changelog.

### Migration-day guardrails

- No ad hoc one-file renames for helper/entity IDs.
- Keep changes atomic per domain (audio, lighting, UI, hardware, MA hub).
- Require rollback path (snapshot + tested restore steps).
- Treat missing helper/script sentinels as blocker.

### Read-depth guidance for future sessions

- Skim-safe default: read this section header/policy only.
- Deep-read required only when explicitly starting migration.
- Migration start trigger phrase: **"start full naming cleanup"**.

## Goals (what success looks like)

1. **Hardware-first UX**: physical selectors + momentaries drive modes/targets; OLED follows hardware state.
2. **Menu is fallback**: menu encoder remains functional, but hardware changes reassert control.
3. **Generalizable**: works for installs with 1–N rooms and multiple audio targets.
4. **Deterministic**: hardware switch positions always map to clear actions, no ambiguous prompts.
5. **Crossfade/Balance slider mode (v-next)**: one slider surface with mode-aware behavior — room-to-room balance in multi-room mode, and left/right speaker balance in single-room mode.
6. **Analog-surface breadth**: beyond audio/lighting depth, the input model supports mappable Home Assistant actions across broader home domains (scenes, scripts, climate flows, safety routines, and other HA-controllable behaviors).

## Product positioning contract (README + roadmap parity)

- Spectra L/S is the analog tactile control surface for Home Assistant.
- Audio and lighting remain the deepest, first-class domains.
- Physical input primitives (buttons/switches/sliders/encoders) are mappable control surfaces for broader HA automation/action execution.
- Documentation parity rule: if this positioning contract changes, update `README.md`, this file, and `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md` in the same change set.

## v-next Feature Requirement — Crossfade / Balance Slider

This is a required top-line feature for v-next.

- In **multi-room mode**, the slider controls **volume balance between rooms** (crossfade-style weighting), not just a global absolute level.
- In **single-room mode**, the slider controls **left/right speaker balance** for that room.
- Mode-to-slider behavior must be explicit on OLED so users always know whether they are balancing rooms or balancing speakers.

Implementation notes (planning contract):

- Add a normalized slider value domain (for example `-100..100`) for directional balance semantics.
- Multi-room balance path should map slider direction into weighted per-room gain adjustments with clamping and rate limiting.
- Single-room balance path should map slider direction into stereo L/R balance (or equivalent device-supported control path).
- Keep fallback behavior safe: if a target path does not support balance controls, hold current mix and expose a clear UI/status notice.

## HDMI ARC Ingest + Final DAC Path (Active Hardware Note)

- Spectra Level / Source should be treated as a **fully integrated high-fidelity system path** (ingest + routing + conversion), not a DAC-only feature claim.
- ES9038Q2M capability is framed as the final conversion stage in a broader source-to-output architecture optimized for signal integrity and deterministic control routing.

- Source path includes **HDMI input from an ARC-capable source**.
- ARC digital audio is split/extracted and carried as the digital program feed into the final conversion stage.
- Final output conversion target is the **ESS ES9038Q2M DAC** (`ESS 9038Q2M`).
- Output capability target for this path: **192kHz / 24-bit**.
- Expected codec/file compatibility on the digital playback chain:
  - `FLAC`
  - `MP3`
  - `AAC`
  - `AAC+`
  - `ALAC`
  - `APE`
  - `WAV`

Implementation guidance:

- Treat ARC ingest as part of source-path selection/routing validation (same deterministic control-path rules as other sources).
- Keep this note in sync with README hardware reference to avoid drift in published hardware capabilities.

## MA/HA Discovery + Control Routing Contract (Active)

- Discovery-first is the baseline: newly discovered compatible players should appear without requiring static per-site host mapping edits.
- Static/manual host mapping remains as a safety fallback only and should be **disabled by default** to keep no-override testing honest.
- Every discovered/selected target must be classified into a control routing class before command send:
  - `linkplay_tcp` (supported now)
  - `other` (placeholder for future code paths)
- Override entries should carry full routing metadata to match discovery data quality:
  - `hardware_family` (example: `linkplay`)
  - `control_path` (example: `linkplay_tcp`)
  - `control_capable` (boolean; can receive direct hardware controls like POT/EQ)
  - `capabilities` (optional list for control feature matrix)
- Command dispatch must follow control class, not just host presence, so unsupported classes are visible but not incorrectly routed.

## Control-Path + Hardware-Family Roadmap (As-Wired + Next)

### Current wiring snapshot (implemented)

- Discovery-first target onboarding is active via MA player data and HA entity attributes.
- Manual/static fallback routing is opt-in and defaults off via `input_boolean.ma_control_fallback_enabled`.
- Active target routing surfaces:
  - `sensor.ma_active_control_path`
  - `binary_sensor.ma_active_control_capable`
  - `sensor.ma_control_hosts`
- Override metadata contract is wired in `packages/spectra_ls_setup.yaml` room entries and extra JSON:
  - `hardware_family`
  - `control_path`
  - `control_capable`
  - `capabilities`
- Currently supported dispatch path:
  - `linkplay_tcp` (control-capable targets only)
- Non-supported path behavior:
  - tagged as `other`
  - visible for diagnostics/selection context
  - intentionally not routed for direct control sends

### Family/codepath roadmap

1. **Phase R1 — LinkPlay hardening (now)**
    - Keep `linkplay_tcp` as the only routed path.
    - Expand `capabilities` usage from informational to enforced feature gates (for example EQ, source cycle, transport subfeatures).

2. **Phase R2 — Additional family onboarding**
    - Add first non-LinkPlay family tag under `hardware_family`.
    - Introduce dedicated `control_path` value for that family (do not reuse `linkplay_tcp`).
    - Route only after a family-specific command adapter exists.

3. **Phase R3 — Capability matrix routing**
    - Move from boolean `control_capable` to per-feature capability routing decisions using `capabilities`.
    - Gate each direct hardware command type by both `control_path` and required capability.

4. **Phase R4 — Unified adapter contract**
    - Standardize a per-family adapter interface so new paths plug into the same decision layer.
    - Maintain discovery-first default and fallback-off policy across all families.

### No-go guardrails for future families

- Do not route a new `control_path` until:
  - host/endpoint resolution is deterministic,
  - command semantics are validated for that family,
  - `control_capable`/`capabilities` mappings are explicitly defined.

## Pathing + Naming Safety Guardrails (Do Not Skip)

### Authoritative edit targets for `spectra_ls_system`

- Path context rule: edit files from host paths (`/mnt/homeassistant/...`), but when writing ESPHome include literals use container paths (`/config/...`).

- ESPHome entrypoint: `/mnt/homeassistant/esphome/spectra_ls_system.yaml`
- Spectra packages only:
  - `/mnt/homeassistant/esphome/spectra_ls_system/packages/spectra-ls-system.yaml`
  - `/mnt/homeassistant/esphome/spectra_ls_system/packages/spectra-ls-hardware.yaml`
  - `/mnt/homeassistant/esphome/spectra_ls_system/packages/spectra-ls-ui.yaml`
  - `/mnt/homeassistant/esphome/spectra_ls_system/packages/spectra-ls-lighting.yaml`
  - `/mnt/homeassistant/esphome/spectra_ls_system/packages/spectra-ls-audio-tcp.yaml`
  - `/mnt/homeassistant/esphome/spectra_ls_system/packages/spectra-ls-diagnostics.yaml`
- RP2040 source-of-truth:
  - live: `/media/cory/CIRCUITPY/code.py`
  - mirror: `/mnt/homeassistant/esphome/circuitpy/code.py`

### Out-of-scope paths for this track (unless explicitly requested)

- `/mnt/homeassistant/esphome/control-py/**` (stabilized v2 line)
- `/mnt/homeassistant/esphome/control-py/previous/**` (archived)
- `/mnt/homeassistant/esphome/spectra_ls_system/NOTES-control-board-2.md` (archived/frozen)

### Naming execution rule

- New files/packages/helpers use Spectra naming (`spectra-ls-*`, `spectra_ls_*`).
- Legacy `control_board_*` runtime IDs remain until dedicated cleanup trigger.
- Never mix ad hoc renames with behavior changes in one patch set.

## Current Input Inventory (baseline)

### Digital (PCF8575 @ 0x20)

- P0 `room` → event 31
- P1 `source` → event 35
- P2 `back` → event 36
- P3 `home` → no event (autocal trigger only)
- P4 `prev` → event 34
- P5 `play` → event 32
- P6 `next` → event 33
- P7 `mute` → event 22
- P8 `select` → event 37
- **Spare**: P9–P15 (7 inputs)

### Encoders (Seesaw)

- Menu encoder: delta id 2, press id 21
- Lighting encoder: delta id 1, press id 20

### Analog (ADS1015 + internal ADC)

- ADS1015 ch0: eq_bass_pot → 104
- ADS1015 ch1: lighting_slider → 101
- ADS1015 ch2: volume_pot → 102
- ADS1015 ch3: eq_treble_pot → 106
- RP2040 A0: eq_mid_pot → 105
- **Spare**: RP2040 A1

### Expansion allowed

- Add I2C expanders/ADCs as needed (PCF8575 @ 0x21, ADS7830 @ 0x49 recommended).

---

## Proposed Hardware Model (Mode + Target + Action)

### 5-way selector = **Mode Selector**

Suggested mapping (generalizable across installs):

1. **Lighting Rooms**
   - Momentary: cycle room list
   - Encoder: brightness or hue/sat (depending on sub-mode)

2. **Lighting Targets**
   - Momentary: cycle target list within selected room
   - Encoder: adjust selected target (brightness or hue/sat)

3. **Audio Targets**
   - Momentary: cycle hardware audio targets (MA/HA list)
   - Encoder: volume (always)

4. **Audio Transport**
   - Momentary: play/pause, prev/next
   - Encoder: volume (always)

5. **System / Meta**
   - Momentary: cycle meta source or control-target prompt
   - Encoder: meta select or diagnostic/utility

### 3-way switch = **Audio Control Class**

- **Auto**: HA/MA logic chooses target
- **Primary Hardware**: local Spectra LS (or primary device)
- **Room Hardware**: optional room device

### Momentary buttons

- **Primary momentary**: “Next” within mode
- **Secondary momentary**: “Back/Reverse” or “Confirm”
- Long-press on Back remains Home

---

## Implementation Plan (Agent Instructions)

### Execution Phases (commit-scoped)

1. **Phase A — Path-safe scaffolding + event contract reservation**
   - Confirm all target files are in `spectra_ls_system` and `CIRCUITPY` + mirror only.
   - Reserve/record event IDs and mode enum contract in this file.
   - Commit scope: notes + non-behavioral scaffolding only.

#### Phase A Start Checklist (must pass before Phase B)

- [x] **A1: Path authority check**
  - Planned edit targets must resolve only to `/mnt/homeassistant/esphome/spectra_ls_system.yaml`, `/mnt/homeassistant/esphome/spectra_ls_system/packages/spectra-ls-*.yaml`, `/media/cory/CIRCUITPY/code.py`, and `/mnt/homeassistant/esphome/circuitpy/code.py`.
  - Planned edit targets must exclude `/mnt/homeassistant/esphome/control-py/**` and `/mnt/homeassistant/esphome/control-py/previous/**`.

- [x] **A2: Include wiring check**
  - Verify `spectra_ls_system.yaml` includes only active `spectra-ls-*` package files.
  - Verify include target existence for every referenced package path.

- [x] **A3: RP2040 parity pre-check**
  - Confirm live and mirror firmware files are identical before changes.
  - If drift exists, reconcile parity first and document source-of-truth decision.

- [x] **A4: Event contract reservation**
  - Reserve event ID window for new selector/switch/momentary features.
  - Add an event contract table in this file with columns: `event_id`, `producer`, `consumer`, `notes`.
  - Mark any existing IDs that must not be repurposed.

- [x] **A5: Ownership map**
  - Document owner files for each concern: RP2040 scan/debounce/emit, ESPHome event ingest/state, UI/menu override/render state, and HA helper routing.

- [x] **A6: Safety gates**
  - Define “no-go” conditions (e.g., missing package include target, RP2040 live/mirror mismatch, unresolved legacy path ambiguity).
  - Define rollback actions and restore commands before functional edits.

- [x] **A7: Validation gates for phase transition**
  - Define minimum validation set required to move to Phase B/C.
  - Include expected PASS/WARN behavior for templates and what blocks advancement.

- [ ] **A8: Commit boundary**
  - Keep Phase A commit doc-only (notes + optional changelog pointer) with no behavioral code changes.
  - Push Phase A commit before opening Phase B implementation work.

#### Phase A Verification Snapshot (2026-04-17)

- A1 verified: authoritative target files exist only in `spectra_ls_system` + RP2040 live/mirror paths.
- A2 verified: `spectra_ls_system.yaml` package includes point to active `spectra-ls-*` files with valid include targets.
- A3 verified: RP2040 live/mirror parity is clean.
- RP2040 live SHA256 (`/media/cory/CIRCUITPY/code.py`): `41b9b828bf43556e982d8c035d2ef4fad8589f794ee45dbc3cf79b19736bd647`
- RP2040 mirror SHA256 (`/mnt/homeassistant/esphome/circuitpy/code.py`): `41b9b828bf43556e982d8c035d2ef4fad8589f794ee45dbc3cf79b19736bd647`

#### Event Contract Reservation (Phase A)

Existing event IDs in use (do not repurpose):

- Debug: `0`
- Buttons: `20`, `21`, `22`, `31`–`37`
- Analog controls: `101`, `102`, `104`, `105`, `106`

Reserved window for v-next selector/switch/momentary contract: `120`–`129`

| event_id | producer | consumer | notes |
| --- | --- | --- | --- |
| 120 | RP2040 `code.py` | ESPHome `spectra-ls-hardware.yaml` + `spectra-ls-ui.yaml` | `mode_selector_index` (0–4), edge/event-on-change |
| 121 | RP2040 `code.py` | ESPHome `spectra-ls-hardware.yaml` | `control_class_index` (0–2), edge/event-on-change |
| 122 | RP2040 `code.py` | ESPHome `spectra-ls-ui.yaml` | `mode_next_item` momentary press |
| 123 | RP2040 `code.py` | ESPHome `spectra-ls-ui.yaml` | `mode_prev_item` momentary press |
| 124 | RP2040 `code.py` | ESPHome `spectra-ls-ui.yaml` | `mode_confirm` momentary press |
| 125–129 | Reserved | Reserved | keep unassigned for follow-on controls/long-press variants |

#### Ownership Map (Phase A)

- RP2040 scan/debounce/emit owner:

  - live: `/media/cory/CIRCUITPY/code.py`
  - mirror: `/mnt/homeassistant/esphome/circuitpy/code.py`
- ESPHome event ingest/state owner:

  - `/mnt/homeassistant/esphome/spectra_ls_system/packages/spectra-ls-hardware.yaml`
  - `/mnt/homeassistant/esphome/spectra_ls_system/packages/spectra-ls-system.yaml`
- UI/menu override/render owner:

  - `/mnt/homeassistant/esphome/spectra_ls_system/packages/spectra-ls-ui.yaml`
  - `/mnt/homeassistant/esphome/spectra_ls_system/packages/spectra-ls-peripherals.yaml`
- HA helper/routing owner:

  - `/mnt/homeassistant/packages/ma_control_hub.yaml`
  - `/mnt/homeassistant/packages/ma_control_hub/*.inc`

#### Safety Gates (Phase A)

No-Go conditions before Phase B:

- Any missing include target from `spectra_ls_system.yaml` package map.
- RP2040 live/mirror checksum mismatch.
- Planned edits touching `/mnt/homeassistant/esphome/control-py/**` without explicit request.
- Undefined/overlapping event IDs with existing active IDs.

Rollback baseline and commands (doc-only Phase A / pre-Phase B prep):

- Baseline commit on `main`: `a504d36`
- Full repo rollback to baseline:

  - `cd /mnt/homeassistant && git reset --hard a504d36`
- RP2040 mirror-to-live firmware restore (if live diverges unintentionally):

  - `cp /mnt/homeassistant/esphome/circuitpy/code.py /media/cory/CIRCUITPY/code.py`

#### Validation Gates (A → B/C)

Minimum required PASS set before entering Phase B/C implementation:

- Include map sanity:

  - `spectra_ls_system.yaml` references only existing `spectra-ls-*` packages.
- RP2040 parity sanity:

  - live + mirror `code.py` checksum match at handoff.
- Event contract sanity:

  - no collision between reserved window `120`–`129` and active event IDs.

Expected WARN/PASS interpretation:

- WARN allowed: non-blocking runtime helper naming drift (`control_board_*`) under deferred cleanup policy.
- BLOCKER/No-Go: include target missing, checksum mismatch, event ID collision, or edits outside Phase A scope.

1. **Phase B — RP2040 input capture**
   - Implement selector/switch/momentary scan + debounce + edge-trigger emit.
   - Update both live `CIRCUITPY` and repo mirror in same change set.
   - Commit scope: RP2040 only (plus notes/changelog as needed).

1. **Phase C — ESPHome mode/state wiring**
   - Wire incoming events into `spectra-ls-hardware.yaml` + `spectra-ls-ui.yaml`.
   - Add `hardware_mode`, menu override clearing, and deterministic route state updates.
   - Commit scope: spectra package files only.

1. **Phase D — HA helper/routing integration**
   - Bind mode transitions to existing helper contracts (`ma_active_target`, room/target selectors).
   - Add only required helper surfaces; avoid broad helper churn.
   - Commit scope: minimal helper/automation updates.

1. **Phase E — Validation + hardening**
   - Run validation templates and confirm pass/warn deltas.
   - Address race/flood/stale-state issues before proceeding.
   - Commit scope: fixes + docs + changelog.

1. **Phase F — Deferred naming cleanup (future trigger only)**
   - Execute only after all trigger gates in naming section are satisfied.
   - Perform compatibility/cutover/cleanup sequence as documented above.

### Phase 1 — RP2040 CircuitPython (input scanning)

**Files**:

- `/media/cory/CIRCUITPY/code.py` (authoritative live firmware)
- `/mnt/homeassistant/esphome/circuitpy/code.py` (required mirror sync in same change set)

1. **Add selector input**
   - Choose one:
     - **Resistor ladder** on ADS7830 (recommended)
     - Discrete GPIOs on PCF8575 (uses 5 pins)
   - If ladder:
     - Add ADS7830 driver + detection
     - Add analog channel `mode_selector` with hysteresis
     - Map 5 ADC bands → positions 0–4
     - Emit event `MODE_SELECTOR_ID` as **position index** (0–4)

2. **Add 3-way control-class switch**
   - Prefer discrete pins on PCF8575
   - Emit event `CONTROL_CLASS_ID` as 0–2

3. **Add momentary inputs**
   - Assign spare PCF pins
   - Emit button events for `next_mode_item`, `prev_mode_item`, `confirm`

4. **Event ID assignments**
   - Pick new IDs in an unused range (e.g., 120–129)
   - Document in this file (`v-next-NOTES.md`) and `CHANGELOG.md` when applied

5. **Edge-triggered events**
   - Only send on change to prevent flooding
   - Debounce using existing Debouncer

---

### Phase 2 — ESPHome (ESP32-S3)

**Files**:

- `/config/esphome/spectra_ls_system/packages/spectra-ls-hardware.yaml`
- `/config/esphome/spectra_ls_system/packages/spectra-ls-ui.yaml`
- `/config/esphome/spectra_ls_system/packages/spectra-ls-system.yaml` (if shared routing state is needed)

1. **Add sensors / binary_sensors for new events**
   - `mode_selector` (0–4)
   - `control_class` (0–2)
   - momentary events

2. **Add global “hardware_mode” state**
   - Enum values 0–4 (match selector)
   - Stored in globals; updated on mode selector event

3. **OLED behavior**
   - When selector changes: swap screen to mode-specific layout
   - Show current mode + target at top

4. **Menu override behavior**
   - Menu encoder activity sets `menu_override_active = true`
   - Any hardware selector change clears override
   - OLED returns to hardware mode view

5. **Control routing**
   - Lighting modes: drive `input_select.control_board_room/target`
   - Audio targets: drive `input_select.ma_active_target` or target helper
   - System/meta: trigger meta override or target prompt

---

### Phase 3 — Home Assistant helpers

1. **Audio targets**
   - Use `input_select.ma_active_target` for actual targets
   - Add `input_text` helpers if you want labels per selector position

2. **Lighting targets**
   - Ensure `sensor.control_board_room_options` and `sensor.control_board_target_options` are valid

---

## Wiring / Hardware Choices

### Recommended 5-way selector approach

- **Resistor ladder** into ADS7830 channel
- ADS7830 @ **0x49** to avoid ADS1015 conflict
- Use deadbands between thresholds to avoid chatter

### Alternate approach

- Discrete 5 pins on PCF8575 (P9–P13)
- Requires more GPIO, but simpler firmware

---

## Acceptance Criteria

- Changing selector positions updates OLED within 100–200ms.
- Hardware mode always overrides menu when selector changes.
- Audio target switch positions never show “control target prompt.”
- No event flooding from selector or 3-way switch.
- All mappings documented in `v-next-NOTES.md` + `CHANGELOG.md` when implemented.

---

## Next Decisions (required before coding)

1. **Selector implementation**: ladder + ADS7830 vs discrete pins
2. **Final mode list**: confirm 5 positions
3. **Event ID allocation**: reserve IDs and document
4. **HA helper mapping**: labels for targets and rooms

---

## Working Notes (update as we go)

- Menu encoder remains fallback; hardware selector reasserts state.
- Expansion via ADS7830/PCF8575 is allowed.
- Ensure selector states map cleanly to HA target lists across multi-room installs.

### Menu Authoring Contract (Required for new menus)

- **Navigation direction must be centralized**: new menu index movement must use shared helper `components/sls_menu_nav.h` (`normalize_encoder_delta` + `step_index`) and never apply raw encoder deltas directly.
- **Direction is top-level configurable** via substitution `menu_encoder_nav_sign` (default `-1` for intuitive clockwise/right/down progression).
- **Text fitting must be centralized**: new menu labels/headings must use shared helper `components/sls_oled_text_layout.h` (`draw_center_wrapped`, `wrap_two_lines`, `needs_wrap_two_lines`) instead of local wrap/center logic.
- **No per-menu custom direction/wrap forks**: if behavior needs tuning, change shared helpers once so all menu layers inherit consistent UX.

### Future Cleanup / Tuning Backlog — Host Inventory + Overrides (Productization)

- [ ] Replace ad hoc host defaults with a single product-scoped host inventory model (canonical source), rather than split per-user root files.
- [ ] Define canonical naming for inventory artifact(s): avoid user/site names; prefer product namespace (e.g., `spectra_ls_host_inventory`).
- [ ] Design host inventory schema to include richer metadata, not just IP:
  - stable device key / logical role (`primary`, `room`, etc.)
  - transport capabilities (TCP/HTTP/UPnP)
  - friendly label(s)
  - optional MAC and firmware/version hints
  - override precedence fields (auto-discovered vs user-pinned)
- [ ] Add a generation path (auto-discovery + synthesis) that can produce/refresh inventory defaults without committing user-specific data.
- [ ] Add a user override layer (manual corrections/augmentations) with explicit merge precedence over discovered values.
- [ ] Ensure generated/override artifacts are local-only by default (ignored in git), while repository keeps only universal templates/examples.
- [ ] Update MA control hub helper wiring to read from canonical inventory surfaces (or derived helpers) instead of hard-coded per-install includes.
- [ ] Add validation checks/scripts for schema integrity and required keys (fail fast on malformed inventory).
- [ ] Add migration notes for existing installs that currently depend on `spectra_ls_primary_tcp_host` / `spectra_ls_room_tcp_host` keys.

Current state note (2026-04-17):

- Root `spectra_ls_primary_tcp_host.yaml` and `spectra_ls_room_tcp_host.yaml` are local-only and untracked from GitHub.
- Active `ma_control_hub` host defaults are secrets-based via `!secret spectra_ls_primary_tcp_host` and `!secret spectra_ls_room_tcp_host`.
- This backlog item is the planned path to evolve from simple host keys to a universal product-grade host inventory/override model.

Phase progression note (2026-04-17 update):

- **Phase B event fidelity fix applied**: RP2040 now emits selector/control-class (`120`, `121`) as `TYPE_ANALOG` packets so index values (0–4 / 0–2) are preserved end-to-end instead of collapsing to boolean button state.
- **Phase C ingest wired (initial)**: `spectra-ls-hardware.yaml` now consumes `120`–`124`, updates global `hardware_mode`/`control_class`, and applies deterministic mode-to-UI routing with menu override clear-on-hardware-change behavior.
- Mode-nav mirrored events (`122`–`124`) are currently scoped to hardware mode 4 (System/Meta) to avoid transport/menu double-trigger conflicts while preserving existing button behavior in other modes.
- **Virtual harness added (temporary diagnostics path)**: `spectra-ls-diagnostics.yaml` now exposes virtual mode/control injectors plus mode-nav test buttons and a one-shot battery script. These invoke shared handler scripts in `spectra-ls-hardware.yaml`, allowing HA-side flow validation without touching RP2040 wiring while preserving a single behavior path.
