<!-- Description: Repository changelog for Home Assistant + ESPHome work. -->
<!-- Version: 2026.04.20.81 -->
<!-- Last updated: 2026-04-20 -->

# Changelog

## 2026-04-20

- Custom Component/F4-S02 Builder Regression Fix (`custom_components/spectra_ls/coordinator.py`, `docs/roadmap/v-next-NOTES.md`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`): fix accidental function-split regression where `_build_action_catalog_validation` returned `None` (due misplaced F4-S03 builder insertion), which forced persistent `ready_for_f4_s02=false` and blocked F4-S03 closeout dependency gate despite healthy route/target context. Restored complete F4-S02 payload builder flow and kept F4-S03 dependency guards intact. README parity: no material repo-state change.

- Validation/F4-S03 Dependency-WARN Guidance Hardening (`custom_components/spectra_ls/coordinator.py`, `docs/testing/raw/f4_s03_crossfade_balance_validation.jinja`, `docs/roadmap/v-next-NOTES.md`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`): harden F4-S03 diagnostics for no-target/deferred-route captures by surfacing explicit dependency context (`active_target_resolved`, `route_decision`, `ready_for_f4_s02`) and adding deterministic rerun guidance (set/confirm active target, rerun F4-S01 → F4-S02 → F4-S03 in legacy mode) when the only failing gate is F4-S02 readiness. README parity: no material repo-state change.

- Custom Component/F4-S03 None-Payload Crash Guard (`custom_components/spectra_ls/coordinator.py`, `docs/roadmap/v-next-NOTES.md`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`): fix runtime crash path where `crossfade_balance_validation` attempted `.get(...)` on a `None` `action_catalog_validation` object during snapshot builds (service and state-change callback paths), by normalizing upstream F4 payloads to mapping-safe defaults and hardening event callback snapshot refresh to fail-safe logging rather than uncaught callback exceptions. README parity: no material repo-state change.

- Custom Component/F4 Sequence Hardening Pass-2 (`custom_components/spectra_ls/__init__.py`, `docs/roadmap/v-next-NOTES.md`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`): harden `run_f4_s01_sequence`, `run_f4_s02_sequence`, and `run_f4_s03_sequence` with explicit stage-level execution wrappers and surfaced failure stage context (instead of opaque unknown-action failures), preserving diagnostics-only behavior and legacy authority boundaries. README parity: no material repo-state change.

- Custom Component/F4-S03 Crossfade-Balance Diagnostics Scaffold (`custom_components/spectra_ls/const.py`, `custom_components/spectra_ls/__init__.py`, `custom_components/spectra_ls/coordinator.py`, `custom_components/spectra_ls/services.yaml`, `custom_components/spectra_ls/sensor.py`, `custom_components/spectra_ls/binary_sensor.py`, `docs/roadmap/v-next-NOTES.md`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`): implement Phase 4 Slice-03 diagnostics-only service/payload path (`validate_crossfade_balance`, `run_f4_s03_sequence`) with normalized slider-domain schema, mode-profile contract visibility, sample no-op mix plan diagnostics, and no-authority-expansion checks while preserving legacy runtime write ownership. README parity: no material repo-state change.

- Validation/F4-S03 Raw Template Scaffold (`docs/testing/raw/f4_s03_crossfade_balance_validation.jinja`, `docs/testing/raw/f4_s03_crossfade_balance_entry_checklist.md`, `docs/roadmap/v-next-NOTES.md`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`): add a deterministic copy/paste raw validator for Phase 4 Slice-03 crossfade/balance contract readiness with freshness guards, authority safety checks, and explicit pre-implementation handling when F4-S03 payload/service surfaces are not yet present; update F4-S03 checkpoint docs to include the runtime evidence artifact path. README parity: no material repo-state change.

- Validation/F4-S03 Entry Checklist Publication (`docs/testing/raw/f4_s03_crossfade_balance_entry_checklist.md`, `docs/roadmap/v-next-NOTES.md`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`): add a deterministic diagnostics-first F4-S03 kickoff checklist covering preflight gates, scope guardrails, closeout evidence requirements, and operator expectation that diagnostics sequence actions are UI-quiet with confirmation in template/entity outputs. README parity: no material repo-state change.

- Validation/F4-S02 Closeout Seal + Action Feedback Clarity (`docs/roadmap/v-next-NOTES.md`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`, `docs/testing/raw/f4_s02_action_catalog_validation.jinja`): close F4-S02 using runtime `PASS 7/7` evidence in legacy authority mode (`ready_for_f4_s02=true`, `f4_s01_ready_reference=true`, `dry_run_only=true`, `no_authority_expansion=true`) and clarify operator expectations that `run_f4_s01_sequence`/`run_f4_s02_sequence` are silent diagnostics-refresh actions whose confirmation is observed in template/entity outputs rather than UI toast feedback. README parity: no material repo-state change.

- Validation/F4-S01 Closeout Seal + Legacy-Mode Runbook Clarification (`docs/roadmap/v-next-NOTES.md`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`, `docs/testing/raw/f4_s01_capability_profile_validation.jinja`): close F4-S01 with runtime `PASS 6/6` evidence in legacy authority mode (`authority_mode=legacy`, `ready_for_f4_s01=true`, `route=route_linkplay_tcp`, metadata prep ready), and add explicit operator-facing guidance for running `spectra_ls.run_f4_s01_sequence` with `mode: legacy` before closeout checks. README parity: no material repo-state change.

- Validation/F4-S02 Runtime WARN Evidence Capture (`docs/roadmap/v-next-NOTES.md`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`, `docs/testing/raw/f4_s02_action_catalog_validation.jinja`): archive a concrete F4-S02 runtime artifact with `WARN 6/7` where only `capability_profile_ready=false` blocked closeout, and add deterministic rerun guidance to execute legacy-mode F4-S01 first and then rerun F4-S02 sequence for closure-grade evidence. README parity: no material repo-state change.

- Validation/F4-S01 Runtime Evidence Capture (`docs/roadmap/v-next-NOTES.md`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`, `docs/testing/raw/f4_s01_capability_profile_validation.jinja`): archive a concrete F4-S01 runtime artifact with `WARN` (`gate_score=5/6`) where all capability/profile gates were healthy except `no_authority_expansion` (`authority_mode=component`), and tighten template recommendation text to explicitly require rerun with `run_f4_s01_sequence(mode='legacy')` for diagnostics-only closeout eligibility. README parity: no material repo-state change.

- Validation/F4-S01 Runtime Evidence Blocker Note (`docs/roadmap/v-next-NOTES.md`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`): record explicit evidence gap for F4-S01 closeout where runtime PASS/WARN/FAIL template output is not yet captured in tracked artifacts/logs for this slice window; keep F4-S01 open and evidence-first (no inferred closeout). README parity: no material repo-state change.

- Custom Component/F4-S02 Programmable Action Safety Skeleton (`custom_components/spectra_ls/const.py`, `custom_components/spectra_ls/__init__.py`, `custom_components/spectra_ls/coordinator.py`, `custom_components/spectra_ls/services.yaml`, `custom_components/spectra_ls/sensor.py`, `custom_components/spectra_ls/binary_sensor.py`, `docs/testing/raw/f4_s02_action_catalog_validation.jinja`, `docs/roadmap/v-next-NOTES.md`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`): add diagnostics-only action-catalog safety scaffolding with explicit arm/confirm/cooldown/audit schema visibility, no-authority-expansion checks, and one-shot validation services while preserving legacy ownership boundaries. README parity: no material repo-state change.

- Validation/P3 Final Closeout Seal (`docs/roadmap/v-next-NOTES.md`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`): publish final evidence-backed Phase-3 seal with soak completion (`3` successful cycles in `4` attempts, `distinct_pass_targets=2`), closure-gate semantics alignment (`soak_evidence` is closure-grade; runtime is health-check-only), and metadata candidate payload parity proof (`PASS 5/5`, consistent rows/summary/best payload). P3-S01/P3-S02/P3-S03 are now explicitly sealed and Phase-4 continuation is confirmed on active F4-S01 lane. README parity: no material repo-state change.

- Validation/P3 Candidate Payload Parity Template (`docs/testing/raw/p3_candidate_payload_parity_validation.jinja`): add a raw copy/paste operator template that checks consistency between `sensor.ma_meta_candidates` state count, `candidate_rows_json`, `candidate_summary_json`, and `best_candidate_json`, with deterministic PASS/WARN/FAIL diagnostics for row/summary/best mismatches and empty-entity false-positive regressions. README parity: no material repo-state change.

- ESPHome/Active Entrypoint Stale-Reference Cleanup (`esphome/spectra_ls_system.yaml`): remove deprecated `control-board-peripherals` include comment and retire outdated “no-rings vs rings” checklist wording from the active runtime entrypoint, keeping package guidance aligned to current `spectra-ls-peripherals.yaml` source-of-truth naming. README parity: no material repo-state change.

- Validation/P3 Closure Gate Operator-Clarity Hardening (`docs/testing/raw/p3_s01_s02_closure_gate_check.jinja`): improve runtime vs soak-evidence readability by rendering soak-only gates as `n/a (runtime mode)` outside `soak_evidence`, add explicit inline mode guidance/output so runtime checks cannot be mistaken for closure-grade evidence, and add a compact “how to run soak_evidence mode” section with required fields sourced from `script.spectra_p3_soak_one_shot` notifications/logging. README parity: no material repo-state change.

## 2026-04-19

- Validation/P3 Closure Gate Runtime-Mode Semantics Hardening (`docs/testing/raw/p3_s01_s02_closure_gate_check.jinja`): make closeout gating explicitly mode-aware so runtime evaluation no longer hard-fails solely on missing soak counters (`observed_soak_attempts=0`) while still enforcing strict soak-cycle/attempt/distinct-target/provenance gates in `soak_evidence` mode; runtime-only outputs are now explicitly non-closeout (`WARN` floor) to prevent accidental closure without evidence-backed soak capture. README parity: no material repo-state change.

- HA/Now-Playing Title Correctness Hardening (`packages/ma_control_hub/template.inc`): remove source/app/friendly-name fallback from `sensor.now_playing_entity` title resolver so non-track labels (for example device/source placeholders) no longer appear as fake now-playing titles during metadata startup gaps; source visibility remains available via `sensor.now_playing_source`. README parity: no material repo-state change.

- HA/MA Meta Candidate Contract Fix (`packages/ma_control_hub/template.inc`): resolve a Jinja accumulation scope bug in `sensor.ma_meta_candidates` where `candidate_rows_json` (and MA-ID enrichment inputs) were built with loop-local list reassignment, yielding `state > 0` while `candidate_summary_json`/`best_candidate_json` stayed empty (`best_entity=''`, `best_score=0`). Switched to namespace-backed accumulation so row payload, summary entities, and best-candidate outputs remain contract-consistent for diagnostics and metadata-prep gates. README parity: no material repo-state change.

- Validation/P3-H3 Closure Gate Fail-Closed Hardening (`docs/testing/raw/p3_s01_s02_closure_gate_check.jinja`, `docs/testing/raw/p3_s01_s02_soak_protocol.md`, `docs/roadmap/v-next-NOTES.md`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`): enforce strict closure semantics by changing defaults to runtime-safe fail values and requiring soak-evidence provenance (`observed_evidence_source`, `observed_evidence_reference`, `observed_evidence_collected_at <=24h`) before soak-mode closure can PASS/WARN; missing provenance now hard-FAILs to prevent optimistic/manual-only closeout toggles. README parity: no material repo-state change.

- Validation/P3-H2 Closure Gate Soak-Parity Fix (`docs/testing/raw/p3_s01_s02_closure_gate_check.jinja`, `docs/testing/raw/p3_s01_s02_soak_protocol.md`, `docs/roadmap/v-next-NOTES.md`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`): eliminate soak-mode false WARN outcomes caused by runtime parity drift outside soak windows by adding explicit operator evidence input `observed_parity_ok` and using it when `evaluation_mode=soak_evidence` (runtime parity is still reported in breakdown for diagnostics). README parity: no material repo-state change.

- Validation/P3-H1 Hardening Second Pass (`custom_components/spectra_ls/coordinator.py`, `docs/testing/raw/p3_s01_guarded_write_validation.jinja`, `docs/testing/raw/p3_s02_selection_handoff_validation.jinja`, `docs/testing/raw/p3_s03_metadata_prep_validation.jinja`, `docs/testing/raw/p3_s01_s02_closure_gate_check.jinja`, `docs/testing/raw/p3_s01_s02_soak_protocol.md`, `docs/roadmap/v-next-NOTES.md`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`): strengthen Phase-3 reliability with stricter metadata-candidate readiness semantics (reject empty best-candidate payloads), broader coordinator listener coverage for helper/metadata entities, closure-gate soak-attempt consistency checks, and snapshot-freshness guards across P3 validation templates to reduce stale/false-positive closeout outcomes. README parity: no material repo-state change.

- Custom Component/F4-S01 Capability+Profile Diagnostics Slice (`custom_components/spectra_ls/const.py`, `custom_components/spectra_ls/__init__.py`, `custom_components/spectra_ls/coordinator.py`, `custom_components/spectra_ls/services.yaml`, `custom_components/spectra_ls/sensor.py`, `custom_components/spectra_ls/binary_sensor.py`, `docs/testing/raw/f4_s01_capability_profile_validation.jinja`, `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md`, `docs/roadmap/v-next-NOTES.md`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`): implement Phase-4 Slice-01 diagnostics-only scaffolding with capability-matrix summary, profile-schema contract surface, no-authority-expansion guard visibility, one-shot validation sequence services, and deterministic operator template/checkpoint docs without introducing control ownership cutover writes. README parity: no material repo-state change.

- Validation/P3-S03 Final Runtime Proof Snapshot (`docs/roadmap/v-next-NOTES.md`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`): archive final operator evidence for metadata-prep closeout (`PASS`, `7/7`, `ready_for_metadata_handoff=true`) with resolved metadata probes (`active_meta_entity`, `now_playing_entity/state/title`) and zero missing metadata contracts; explicitly retain compatibility-mode boundary and note that non-cutover runtime route/selection context (`defer_not_capable`, legacy authority, S02 FAIL) is expected and non-blocking for diagnostics-only S03 closure. README parity: no material repo-state change.

- Validation/P3-S03 Closeout + Phase-4 Planning (`docs/testing/raw/p3_s03_metadata_prep_validation.jinja`, `docs/roadmap/v-next-NOTES.md`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`): close P3-S03 diagnostics slice using runtime evidence (`PASS 7/7`, `ready_for_metadata_handoff=true`, missing-required=`0`) while keeping metadata ownership explicitly in legacy compatibility mode, and publish a bounded Phase-4 cutover slice plan (`F4-S01` capability matrix + profile scaffolding, `F4-S02` programmable action catalog safety skeleton, `F4-S03` crossfade/balance service contract + diagnostics-only probe). Also improve S03 template metadata value-probe rendering with live-entity fallback to avoid misleading `missing` display when checks are resolved true. README parity: no material repo-state change.

- Validation/P3-S03 Template Listener Fallback (`docs/testing/raw/p3_s03_metadata_prep_validation.jinja`): add direct rendered listener-anchor lines using explicit `states('entity_id')` and `state_attr('entity_id', ...)` calls for both shadow sensor variants and metadata contract entities, ensuring Home Assistant Template UI registers concrete dependencies even when intermediate-variable anchors are ignored. README parity: no material repo-state change.

- Validation/P3-S03 Template Listener Hardening (`docs/testing/raw/p3_s03_metadata_prep_validation.jinja`): switch listener anchors to explicit `states.sensor.*` object-path references and include a lightweight watcher checksum in rendered output so Home Assistant’s dependency tracker reliably detects concrete entity subscriptions in Developer Tools Template mode. README parity: no material repo-state change.

- Validation/P3-S03 Template Event Tracking Fix (`docs/testing/raw/p3_s03_metadata_prep_validation.jinja`): add explicit static entity/attribute watchers for both `shadow_*` and `spectra_ls_shadow_*` sensor variants so Home Assistant template dependency tracking reliably subscribes to runtime updates instead of warning that the template has no event listeners. README parity: no material repo-state change.

- Custom Component/P3-S03 Metadata Prep (Diagnostics-Only) (`custom_components/spectra_ls/*`, `docs/testing/raw/p3_s03_metadata_prep_validation.jinja`, `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md`, `docs/roadmap/v-next-NOTES.md`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`): add metadata-preparation validation surfaces and one-shot sequence service for Phase 3 Slice-03 without enabling metadata ownership cutover, including explicit checks for legacy metadata contract entities and candidate payload readiness. README parity: no material repo-state change.

- Validation/P3 Closure Gate False-Negative Fix (`docs/testing/raw/p3_s01_s02_closure_gate_check.jinja`, `docs/testing/raw/p3_s01_s02_soak_protocol.md`, `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md`): add explicit `evaluation_mode` support so closeout checks can run against recorded soak evidence (`soak_evidence`) instead of transient live runtime context (`runtime`) that may legitimately return `legacy` authority or `defer_not_capable` after the soak window; prevents post-soak false FAIL outcomes while keeping runtime-strict mode available for live checks. README parity: no material repo-state change.

- Validation/P3-S01+S02 Closeout Decision (`docs/roadmap/v-next-NOTES.md`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`): apply explicit single-capable-topology waiver for the distinct PASS-target gate (based on sustained 3 PASS cycles with clean route/contract/parity/handoff compatibility signals) and advance P3-S01/P3-S02 from Active/Pending to validated closeout state; P3-S03 remains next in-sequence. README parity: no material repo-state change.

- Validation/P3 Closure Gate Tooling (`docs/testing/raw/p3_s01_s02_closure_gate_check.jinja`, `docs/testing/raw/p3_s01_s02_soak_protocol.md`, `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md`, `docs/roadmap/v-next-NOTES.md`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`): add a single deterministic closeout template that combines S01 guard status, S02 handoff status, parity/contract checks, and explicit soak evidence inputs (including single-capable-topology waiver handling) so P3-S01/S02 closure decisions are evidence-driven and reproducible without broad multi-template interpretation drift. README parity: no material repo-state change.

- ESPHome/Audio Warning Noise Reduction (`esphome/control-py/packages/spectra-ls-audio-tcp.yaml`, mirrored in `esphome/spectra_ls_system/packages/spectra-ls-audio-tcp.yaml`): remove unused Home Assistant numeric mirror sensor for `sensor.ma_active_volume` (`id: ha_audio_volume`) to eliminate repeated ESPHome conversion warnings when MA volume is transiently `unknown` during startup/reconnect windows; no control-path behavior changes. README parity: no material repo-state change.

- HA/DST Config Warning Cleanup (`packages/dst_tuya_ac.yaml`): remove `min_cycle_duration` from `dual_smart_thermostat` config because it is ignored when `keep_alive` is defined, eliminating recurring integration warnings while preserving existing cool-only control behavior. README parity: no material repo-state change.

- Validation/P3 Soak Runner Topology Default (`scripts.yaml`): align `script.spectra_p3_soak_one_shot` default distinct-pass-target gate to single-active-target topology (`required_distinct_pass_targets=1`) so successful 3/3 single-target control-path validation no longer reports false "incomplete" outcomes by default; strict multi-target validation remains available by explicitly setting the gate to `2+`. README parity: no material repo-state change.

- Validation/P3-S02 Soak Runtime Evidence (`docs/roadmap/v-next-NOTES.md`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`): capture automated one-shot soak result (`script.spectra_p3_soak_one_shot`) with **3 successful cycles in 5 attempts**, preserving zero contract/parity drift (`contract_valid=true`, `missing_scripts=0`, `missing_automation_ids=0`, `unresolved_sources=0`, `mismatches=0`) and deterministic eligible-route PASS cycles on `route_linkplay_tcp`; note that non-capable target hops were soft-skipped (`defer_not_capable`) and the explicit “≥2 distinct PASS targets” closure gate remains open unless waived for single-capable-topology conditions. README parity: no material repo-state change.

- Validation/P3 Stage-Report Ownership Snapshot (`docs/roadmap/v-next-NOTES.md`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`): add an explicit stage-report note clarifying current ownership boundaries (legacy `.inc` runtime remains source-of-truth for broad selection/control orchestration while `custom_components/spectra_ls` owns diagnostics/one-shot orchestration/guarded write-trial framework), with readiness callouts for next-step soak execution vs. closure readiness. README parity: no material repo-state change.

- Validation/P3 Soak Protocol (`docs/testing/raw/p3_s01_s02_soak_protocol.md`, `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`, `docs/roadmap/v-next-NOTES.md`): add a no-cowboy small soak runbook for repeating P3-S01 + P3-S02 one-shot validation across multiple active-target switches, and codify evidence-based closure gates (consecutive PASS cycles, zero parity/missing-compat regressions) before graduating P3-S02 from Active/Pending. README parity: no material repo-state change.

- Validation/P3-S02 Runtime Proof (`docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`, `docs/roadmap/v-next-NOTES.md`): capture live operator evidence for `p3_s02_selection_handoff_validation.jinja` showing `PASS` in `component` authority mode with deterministic `route_linkplay_tcp`, valid contracts, helper/options readiness (`target_in_options=true`), and zero missing compatibility scripts/automation IDs. README parity: no material repo-state change.

- Custom Component/P3-S02 One-Shot Validation Slice (`custom_components/spectra_ls/__init__.py`, `custom_components/spectra_ls/const.py`, `custom_components/spectra_ls/coordinator.py`, `custom_components/spectra_ls/services.yaml`, `custom_components/spectra_ls/sensor.py`, `custom_components/spectra_ls/binary_sensor.py`, `docs/testing/raw/p3_s02_selection_handoff_validation.jinja`, `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`, `docs/roadmap/v-next-NOTES.md`): add a guarded one-shot P3-S02 validation sequence that performs authority/registry/contract/route refresh and emits explicit selection-handoff readiness diagnostics (legacy helper/options/scripting surfaces) with a raw template for PASS/WARN/FAIL operator validation. README parity: no material repo-state change.

- Custom Component/P3 Operator UX (`custom_components/spectra_ls/__init__.py`, `custom_components/spectra_ls/const.py`, `custom_components/spectra_ls/services.yaml`, `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md`): add one-shot Phase 3-S01 sequence service (`spectra_ls.run_p3_s01_sequence`) to run authority set + rebuild + contract validation + route-trace refresh + guarded write trial in a single action call, reducing manual multi-step operator execution overhead. README parity: no material repo-state change.

- Custom Component/P3 Validation Correctness Fix (`custom_components/spectra_ls/coordinator.py`, `docs/testing/raw/p3_s01_guarded_write_validation.jinja`): fix false FAIL outcomes where `contract_validation` could disappear on subsequent snapshot refreshes after a successful write trial; coordinator now emits contract-validation state consistently and P3 template degrades to WARN when contract-validation payload is missing rather than misclassifying healthy guarded write outcomes as hard FAIL. README parity: no material repo-state change.

- Validation/Template Hardening (`docs/testing/raw/p2_negative_case_regression.jinja`, `docs/testing/raw/p3_s01_guarded_write_validation.jinja`, `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md`): clarify that service checkmarks indicate execution (not semantic pass), strengthen negative-case interpretation when route remains healthy, and add a dedicated P3-S01 guarded-write validation template focused on authority mode, last write attempt status, and guard outcomes. README parity: no material repo-state change.

- Custom Component/Phase 3 Slice-01 Guard Framework (`custom_components/spectra_ls/__init__.py`, `custom_components/spectra_ls/coordinator.py`, `custom_components/spectra_ls/const.py`, `custom_components/spectra_ls/services.yaml`, `custom_components/spectra_ls/sensor.py`, `custom_components/spectra_ls/binary_sensor.py`, `custom_components/spectra_ls/manifest.json`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`, `docs/roadmap/v-next-NOTES.md`, `docs/architecture/CONTROL-HUB-ARCHITECTURE.md`): implement single-writer authority controls (`legacy` default, `component` opt-in), guarded manual route-write trial service, and anti-loop safeguards (debounce, reentrancy, route-decision eligibility, correlation-id tracing) with write-control diagnostics surfaced in shadow attributes. README parity: no material repo-state change.

- Custom Component/Phase 3 Slice-01 Start (`custom_components/spectra_ls/*`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`, `docs/roadmap/v-next-NOTES.md`): begin guarded routing write-path work with single-writer authority controls, loop/flap prevention guards, and rollback-safe defaults while preserving legacy source-of-truth compatibility during activation staging. README parity: no material repo-state change.

- Validation/Roadmap Progression (`docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`, `docs/roadmap/v-next-NOTES.md`): record fresh live P2 runtime proof artifact (`PASS 8/8`, deterministic `route_linkplay_tcp`, contract valid with zero missing required entities, zero unresolved/mismatch drift, fresh snapshot) and advance `P3-S01` status to **Active** for guarded routing write-path work. README parity: no material repo-state change.

- Program Governance/No-Assumption Hardening (`.github/copilot-instructions.md`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`, `docs/roadmap/v-next-NOTES.md`, `docs/notes/NOTES-engineering-rigor.md`): codify evidence-first implementation policy (no cowboy/no assumptions), require explicit contract inventory + tough-spot disclosure before migration write-path changes, add a P1/P2 validation snapshot, and expand Phase 3+ into explicit guarded slices (`P3-S01` routing write path, `P3-S02` selection handoff, `P3-S03` metadata prep) with stricter acceptance gates. README parity: no material repo-state change.

- Docs/Roadmap Quality Cleanup (`docs/roadmap/v-next-NOTES.md`): resolve residual roadmap markdown structure debt (heading/list spacing and indentation) so validation/lint checks are clean before Phase 3 execution work. README parity: no material repo-state change.

- Custom Component/Phase 2 Closure Hardening (`custom_components/spectra_ls/sensor.py`, `custom_components/spectra_ls/binary_sensor.py`, `docs/testing/raw/p2_registry_router_verification.jinja`, `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md`, `docs/testing/raw/p2_negative_case_regression.jinja`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`, `docs/roadmap/v-next-NOTES.md`): expose registry/route-trace/contract-validation diagnostics on shadow entities, add snapshot freshness gating to P2 verification, and add an explicit negative-case regression template for alarm-path validation before Phase 3 planning. README parity: no material repo-state change.

- Docs/DevTools Copy-Paste UX (`esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md`, `docs/testing/raw/p2_registry_router_verification.jinja`): add raw no-fence Jinja template path for Phase 2 verification so operators can copy/paste directly into Home Assistant Template editor without markdown code-fence cleanup. README parity: no material repo-state change.

- Docs/Validation Template Robustness — Shadow Entity ID Auto-Detection (`esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md`): fix Phase 2 validation false-fail after reboot by supporting both HA entity-id styles (`sensor.shadow_*` from has-entity-name registry behavior and legacy `sensor.spectra_ls_shadow_*` assumptions), and add explicit legacy upstream readiness context so startup `unknown` states are diagnosed as settling vs. true parity failure. README parity: no material repo-state change.

- Custom Component/Phase 2 Slice-02 Deterministic Validation Hardening (`custom_components/spectra_ls/registry.py`, `custom_components/spectra_ls/router.py`, `custom_components/spectra_ls/coordinator.py`, `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`, `docs/roadmap/v-next-NOTES.md`): strengthen read-only registry/router determinism with dual-shape rooms/targets payload parsing and resolved-path route tracing, and add a dedicated P2 verification DevTools workbench for contract validation + route-trace checks. README parity: no material repo-state change.

- Custom Component/Official HA Brand Folder Compliance (`custom_components/spectra_ls/brand/icon.png`, `custom_components/spectra_ls/brand/logo.png`, `.github/copilot-instructions.md`, `custom_components/spectra_ls/manifest.json`): align integration icon process to Home Assistant 2026.3+ documented behavior by shipping local brand assets under `brand/` (supported by the Brands Proxy API), add explicit docs-first branding workflow rules to workspace instructions, and bump integration version to force metadata refresh on reload. README parity: no material repo-state change.

- Custom Component/Phase 2 Slice-01 Registry + Router Scaffold (`custom_components/spectra_ls/__init__.py`, `custom_components/spectra_ls/coordinator.py`, `custom_components/spectra_ls/diagnostics.py`, `custom_components/spectra_ls/const.py`, `custom_components/spectra_ls/registry.py`, `custom_components/spectra_ls/router.py`, `custom_components/spectra_ls/services.yaml`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`, `docs/roadmap/v-next-NOTES.md`): start Phase 2 with discovery-first normalized target registry and read-only route-trace foundation (`linkplay_tcp` classification only), plus maintenance services (`rebuild_registry`, `validate_contracts`, `dump_route_trace`) for deterministic diagnostics without introducing control write-path behavior. README parity: no material repo-state change.

- Custom Component/Icon Availability Fix (`custom_components/spectra_ls/manifest.json`): add explicit manifest icon fallback (`mdi:audio-video`) and bump integration version so Home Assistant refreshes integration metadata and stops showing “icon not available” when brand assets are not resolved.

- Custom Component/Validation UX Polish (`custom_components/spectra_ls/icon.png`, `custom_components/spectra_ls/logo.png`, `docs/testing/DEVTOOLS-TEMPLATES.local.md`): add placeholder integration image assets for Devices & Services branding and add a persistent P1-S01 shadow-parity Developer Tools template block for repeatable validation/triage across load/parity/attributes/icon checks.

- Custom Component/Icon + Install Flow Clarification (`custom_components/spectra_ls/sensor.py`, `custom_components/spectra_ls/binary_sensor.py`, `docs/wiki/Install-on-Your-Own-HA.md`): add placeholder icon (`mdi:audio-video`) for Spectra LS shadow parity entities and document required Home Assistant reboot before adding the new custom integration so discovery reflects freshly deployed `custom_components` files.

- Custom Component/Phase 1 Slice-01 Shadow Parity (`custom_components/spectra_ls/*`, `.gitignore`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`, `docs/roadmap/v-next-NOTES.md`): scaffold `spectra_ls` integration baseline, unignore the dedicated tracked component path, and add read-only routing parity surfaces for `ma_active_target`, `ma_active_control_path`, `ma_active_control_capable`, and `ma_control_hosts` with diagnostics-first mismatch visibility and no control write-path side effects. README parity: no material repo-state change.

- Docs/Wiki Control Surface Inventory (`docs/wiki/Control-Surface-Inputs-and-Expanders.md`, `docs/wiki/Home.md`, `docs/wiki/_Sidebar.md`, `docs/wiki/README.md`): add a dedicated operator-facing control reference for buttons, selectors, encoders, sliders/pots, expander bus addresses, and RP→ESP event-path mapping; wire the page into wiki navigation. README parity: no material repo-state change.

- Docs/Wiki Content Expansion + Marker Cleanup (`docs/wiki/Home.md`, `docs/wiki/Getting-Started.md`, `docs/wiki/Install-on-Your-Own-HA.md`, `docs/wiki/User-Setup-Deploy-and-HA-Integration.md`, `docs/wiki/Operations-Runbooks.md`, `docs/wiki/Discussions-and-Projects-Workflow.md`, `docs/wiki/README.md`): remove temporary wiki sync marker and expand wiki stubs into fuller operator-facing runbooks, install guidance, workflow criteria, and troubleshooting references.

- Docs/Wiki Sync Retest Trigger (`docs/wiki/Home.md`): publish a tiny wiki-source update after manual wiki initialization to force a new `Wiki Sync` run and verify end-to-end automation.

- Docs/Wiki Initialization Clarification (`docs/wiki/README.md`): add explicit requirement to initialize the wiki repository by creating/saving the first wiki Home page before automated git sync can clone `<repo>.wiki.git`.

- Tooling/Wiki Sync Reliability + Node24 Readiness (`.github/workflows/wiki-sync.yml`, `docs/wiki/README.md`): upgrade checkout action to Node24-ready version, add explicit Node24 opt-in env, and add preflight diagnostics for wiki repository reachability/auth so `exit 128` failures report actionable causes (wiki disabled/uninitialized or PAT scope/permission mismatch).

- Docs/Wiki Sync Smoke Test (`docs/wiki/Home.md`): add a small visible sync-marker line to confirm GitHub Actions wiki publishing is functioning after repository secret setup.

- Docs/Wiki PAT Navigation Fix (`docs/wiki/README.md`): correct fine-grained PAT instructions to a valid profile-settings route and add direct URL fallback so users can reliably reach token creation UI.

- Docs/README Inspiration Line Expansion (`README.md`): update front-page inspiration sentence to describe Spectra L/S as a minimal home DJ-mixer style control surface coupled with lighting, automation, and human-centric interaction.

- Docs/README Hardware-First Context (`README.md`): clarify on the front page that Spectra L/S is a hardware-first stack that requires the physical controller path first, then uses ESPHome + Home Assistant software orchestration; add explicit MCU role list (ESP32-S3 + RP2040) so new users understand installation context.

- Docs/README Front-Pitch Cleanup + Install Checklist Stub (`README.md`, `docs/wiki/Install-on-Your-Own-HA.md`, `docs/wiki/Home.md`, `docs/wiki/_Sidebar.md`, `docs/wiki/Welcome-README-and-Bug-Workflow.md`): simplify front-page elevator pitch to be strongly user-focused (minimal hardware/repo-detail emphasis), and add a strict copy/paste style “Install on your own HA” checklist with runtime-first steps plus placeholder track for upcoming custom-component setup flow.

- Docs/Wiki User-Onboarding + Bug Workflow + README Positioning (`README.md`, `.github/copilot-instructions.md`, `docs/wiki/*`, `.github/ISSUE_TEMPLATE/bug_report.yml`): add first-pass Welcome/README-and-bug-submission wiki workflow, add user-focused setup/deploy/integration stub with explicit manual prerequisites (tokens/API/manual setup), add wiki content policy for what should/should-not live in wiki, add custom-component setup roadmap stub tied to current roadmap phases, enforce mandatory wiki-parity update step in workspace instructions, and update README positioning section to “Why this is missing from Home Assistant” with physical-first framing and inspiration links.

- Governance/Wiki Automation + PM Operating Model (`.github/workflows/wiki-sync.yml`, `docs/wiki/*`, `docs/governance/GITHUB-MASTERWORK-BLUEPRINT.md`, `docs/governance/LABEL-TAXONOMY.md`, `CONTRIBUTING.md`, `docs/README.md`): add production-ready GitHub Wiki sync workflow from `docs/wiki/`, expand wiki information architecture using mature OSS patterns (home/sidebar/runbooks/architecture/triage/release flow), document fine-grained PAT setup for wiki publishing, and define Discussions + Projects operating model mapped to all repository scope paths for triage and delivery governance.

- Docs/Product Positioning Expansion (`README.md`, `docs/roadmap/v-next-NOTES.md`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`): position Spectra L/S as the analog, tactile control surface for Home Assistant beyond audio/lighting (while keeping heavy focus on those domains), with explicit mappable input philosophy for broader home control actions.

- Governance/GitHub Maturity Baseline (`CONTRIBUTING.md`, `CODEOWNERS`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `.github/ISSUE_TEMPLATE/*`, `.github/pull_request_template.md`, `docs/governance/GITHUB-MASTERWORK-BLUEPRINT.md`, `docs/governance/LABEL-TAXONOMY.md`, `docs/README.md`, `.github/copilot-instructions.md`): establish a mature, Immich-inspired repository governance foundation with structured issue intake, PR quality gates, ownership mapping, security reporting policy, contribution standards, and a documented rollout blueprint for “masterwork” GitHub implementation quality.

- Docs/Legend + Wiring Protocol Upgrade (`docs/circuitpy/RP-LEGEND.md`, `docs/hardware/WIRING-LAYOUT-PROTOCOL.md`, `docs/README.md`, `README.md`, `.github/copilot-instructions.md`, optional wiki sync scaffolding): expand the docs legend into a directive wiring/layout protocol reference with deep links to component-level details, add a docs index entry for the new protocol document, enforce docs/README parity directives in workspace instructions, and simplify frontpage README to user-focused overview with basic documentation links.

- Docs/Repository Documentation Reorganization (`docs/**`, `README.md`, `.github/copilot-instructions.md`): move project documentation/notes into `docs/` (except top-level `README.md`), remap key workflow/reference paths, and keep frontpage README end-user-focused while relocating developer onboarding to docs.

- Docs/Developer Instructions (`DEVELOPER-INSTRUCTIONS.md`, `README.md`): move contributor/developer hygiene guidance off frontpage README into a dedicated developer instruction document, and add a formal preflight checklist plus implementation workflow for instrumentation, documentation parity, and code-change verification.

- Docs/README Workflow Pointer (`README.md`): add a contributor-visible development hygiene pointer to `.github/copilot-instructions.md` so code-hygiene and note-hygiene requirements are discoverable without opening workspace instruction internals first.

- Workflow/Hygiene Policy (`.github/copilot-instructions.md`): add an explicit code-hygiene + note-hygiene standard so future edits keep concise in-code intent comments near non-obvious logic while maintaining synchronized architecture/contract documentation in repo docs.

- Docs/Retroactive Runtime Audit (`esphome/spectra_ls_system/CODEBASE-RUNTIME-ARCHITECTURE.md`, `packages/ma_control_hub/CONTROL-HUB-ARCHITECTURE.md`, `esphome/spectra_ls_system/DEAD-PATHS-CLEANUP.md`, `.github/copilot-instructions.md`, `README.md`, `esphome/spectra_ls_system/CUSTOM-COMPONENT-ROADMAP.md`, `esphome/spectra_ls_system/v-next-NOTES.md`): add baseline architecture/feature documentation for active ESPHome runtime + MA control hub, publish dead-path/cleanup candidate matrix with risk tiers, and require ongoing functionality/feature documentation updates in future slices.

- Docs/Parallel Program Operating System (`esphome/spectra_ls_system/PARALLEL-PROGRAM-PLAYBOOK.md`, `.github/copilot-instructions.md`, `esphome/spectra_ls_system/CUSTOM-COMPONENT-ROADMAP.md`, `esphome/spectra_ls_system/v-next-NOTES.md`, `README.md`): add strict-but-flexible guardrails for running runtime + custom-component tracks in parallel, including slice templates, parity checkpoints, anti-detail-trap workflow, and mandatory roadmap/v-next/README synchronization protocol.

- Docs/Implementation Draft (`esphome/spectra_ls_system/CUSTOM-COMPONENT-ROADMAP.md`, `esphome/spectra_ls_system/v-next-NOTES.md`): add a concrete Phase-1 Slice-01 implementation draft (shadow-mode parity surfaces, acceptance criteria, file skeleton, and track-A/track-B disposition template) to make first-step execution deterministic.

- Workflow/Docs Parity Gate (`.github/copilot-instructions.md`): add an explicit README update step to the mandatory workflow so repo-state changes include README parity checks/updates before completion.

- Docs/Program Governance (`.github/copilot-instructions.md`, `esphome/spectra_ls_system/CUSTOM-COMPONENT-ROADMAP.md`, `esphome/spectra_ls_system/v-next-NOTES.md`): formalize a required parallel-development program for the new `custom_components/spectra_ls` track alongside the current HA package + ESPHome runtime, define phased migration/cutover gates, and add v-next alignment checkpoints so roadmap, contracts, and implementation status remain synchronized.

## 2026-04-18

- HA/AC Porch-Pattern Cool-Only Baseline (`packages/dst_tuya_ac.yaml`): rebuild window AC control to emulate the working Sun Porch DST integration model (template actuator switch + DST-owned cycle decisions + DST→Tuya setpoint sync automation), explicitly scoped to cool-only operation for stability-first behavior.

- Workflow/Quality Gate Hardening (`.github/copilot-instructions.md`): add mandatory verification gates for ESPHome changes — compile/build must succeed **before** commit/push, OTA upload must complete before closing deployment tasks, and responses must include explicit evidence (`build result`, `OTA successful`, `HEAD==origin`) rather than assumptions.

- ESPHome/Lighting Compile Hotfix (`esphome/spectra_ls_system/packages/spectra-ls-lighting.yaml`): fix slider lambda scope error by recomputing `lighting_menu_active` within the value-processing lambda (where deferred-vs-immediate brightness apply is decided), restoring successful firmware compilation for the room-menu brightness UX refactor.

- ESPHome/Lighting Menu UX Refactor (`esphome/spectra_ls_system/packages/spectra-ls-lighting.yaml`, `esphome/spectra_ls_system/spectra-ls-peripherals.yaml`): make lighting slider apply **room brightness directly** while browsing Lighting Rooms/Targets lists (no need to enter `All -> Lighting Values` first), and replace legacy `Lighting Values` labeling with reusable friendly labels (`Brightness <friendly name>`, `Hue <friendly name>`, `Sat <friendly name>`) across lighting-adjust menu rendering paths.

- Repo Scope Separation (`.gitignore`, `packages/dst_tuya_ac.yaml`): de-track `packages/dst_tuya_ac.yaml` from the Spectra repository and add an explicit ignore rule so this local AC-specific package is kept outside Spectra versioned scope while preserving the file locally.

- Repo Ignore Precedence Fix (`.gitignore`): enforce `packages/dst_tuya_ac.yaml` ignore after broad package re-include rules so the file remains untracked persistently.

- HA/AC Control-Path Simplification (`packages/dst_tuya_ac.yaml`): remove external policy reconciler intervention (`automation.dst_mode_reconciler`) and stop fan helper scripts from writing thermostat mode directly (`climate.room_dst`). DST is now the sole mode decision authority while helper scripts only execute direct Tuya device actions, reducing off/on thrash and command-beep chatter caused by layered controller feedback loops.

- HA/AC DST Ownership + Anti-Thrash Rollback (`packages/dst_tuya_ac.yaml`): reduce command-chatter/beep behavior by disabling DST keep-alive (`keep_alive: 0`), removing periodic 1-minute mode reconciler forcing, and deleting aggressive fan fallback off→on retry path that could cause brief compressor dropouts. Control flow now favors DST-native cycle logic over external re-assertion loops.

- Workflow/Git Push Cadence Policy (`.github/copilot-instructions.md`): add mandatory active-session checkpoint push cadence (at least every 10 minutes or on each completed logical slice, whichever comes first) so rollback points remain recent during iterative work.

- HA/AC Numeric Template State Guard (`packages/dst_tuya_ac.yaml`): enforce numeric output for `sensor.dst_room_temp_change_1h` and `sensor.dst_room_temp_rate_1h` even when the raw statistics source is temporarily unavailable, preventing Template integration validator errors that reject non-numeric `unknown` states.

- Repo Ignore-Scope Lockdown (`.gitignore`): stop re-including `blueprints/` and `custom_components/` and explicitly ignore both paths so environment-specific/HA-HACS artifacts are not tracked or uploaded to GitHub from this project repository.

- HA/Global Target Exclusion Filter (`packages/spectra_ls_lighting_hub.yaml`, `packages/ma_control_hub/script.inc`, `packages/ma_control_hub/template.inc`): add centralized `no-spectra` label exclusion so entities tagged with this label are never included in Spectra lighting catalogs, MA discovered/known target option lists, or control-target prompt target catalogs.

- ESPHome/Menu Boot First-Press Intercept Follow-up (`esphome/spectra_ls_system/packages/spectra-ls-ui.yaml`): fix remaining boot-only two-press path where auto control-target prompt could still consume first Select when menu was already active. Auto prompt is now dismissed/snoozed without consuming submenu entry; manual prompt behavior remains unchanged.

- ESPHome/OLED Word-Wrap Tail Fix (`esphome/spectra_ls_system/components/sls_oled_text_layout.h`): replace character-slice fallback behavior for non-fitting multi-word labels with word-preserving fallback + ellipsis on line 2, preventing orphan single-character second lines (for example `Conditione` / `r`) while keeping centered two-line rendering deterministic.

- ESPHome/Menu First-Press Boot Intercept Fix (`esphome/spectra_ls_system/packages/spectra-ls-ui.yaml`): resolve boot-only double-press submenu entry by prioritizing non-menu Select handling before auto control-target prompt consumption; first Select now enters submenu deterministically, while manual control-target prompt behavior remains intact.

- ESPHome/Menu UX One-Press Entry Fix (`esphome/spectra_ls_system/packages/spectra-ls-ui.yaml`): remove two-step submenu entry behavior by routing a non-menu Select press directly into a submenu (`Lighting Rooms` when in lighting screen, `Gear` when in audio screen) instead of consuming an initial press to land on root-menu state.

- ESPHome/Menu Directionality Root-Cause Correction (`esphome/spectra_ls_system/substitutions.yaml`): after full-stack sign trace (RP2040 encoder generation → UART packet decode → unified menu mapper), confirm RP path publishes raw encoder deltas without inversion and restore canonical top-level policy to `menu_encoder_nav_sign: "-1"` so left-turn no longer maps to downward movement.

- ESPHome/OLED Progress Bootstrap Hardening (`esphome/spectra_ls_system/spectra-ls-peripherals.yaml`): add local HA progress timestamp bootstrap when playback is active and duration is known but `ha_audio_pos_last_ms` is still `0` (for example no initial HA position-change event yet). This allows now-playing progress computation to arm and advance from cached/local elapsed time instead of staying permanently invalid.

- ESPHome/Menu Directionality Fix (`esphome/spectra_ls_system/substitutions.yaml`): set unified menu navigation direction policy to raw encoder sign (`menu_encoder_nav_sign: "1"`) so left-turn index motion is no longer inverted into downward movement.

- ESPHome/OLED Progress Bootstrap Fix (`esphome/spectra_ls_system/packages/spectra-ls-audio-tcp.yaml`): initialize `ha_audio_pos_last_ms` on first received HA position sample (even when delta is flat) so now-playing progress logic can arm and project forward instead of remaining permanently invalid when position starts at `0`.

- ESPHome/OLED Progress Hold Fix (`esphome/spectra_ls_system/spectra-ls-peripherals.yaml`): fix static progress-bar behavior when HA position updates remain numerically flat (for example repeated `0`) by projecting from cached displayed position for the same track window while playback is active. This keeps OLED progress advancing deterministically from local elapsed time instead of repeatedly resetting to the non-advancing feed sample.

- ESPHome/Audio Transport Reliability Hardening (`esphome/spectra_ls_system/components/arylic_tcp.h`): make TCP send path resilient to transient network jitter by adding one immediate retry attempt per payload and deferring global backoff until repeated consecutive failures (instead of tripping backoff on a single timeout). This reduces brittle command drops during fast volume sweeps when occasional `connect() timeout` events occur.

- Tooling/OTA Safety Hardening (`bin/esphome_spectra_upload_local.sh`): uploader now rebuilds staged firmware by default before OTA (with `--no-build` escape hatch and `--clean-stage` passthrough), preventing silent stale-artifact uploads that can leave runtime behavior on old transport code despite recent source edits.

- ESPHome/Audio Transport Root-Cause Fix (`esphome/spectra_ls_system/components/arylic_tcp.h`): remove dequeue-time payload mutation for queued `VOL` sends (previously replacing popped payload with `recent->last_payload`) and replace it with deterministic superseded-item drop logic for volume commands only. This eliminates target/TX divergence (for example `Pot send ... target=N` while TX emits a different `VOL:M`) caused by mutable latest-payload rewrite race behavior.

- ESPHome/Audio Transport Anti-Replay Guard (`esphome/spectra_ls_system/components/arylic_tcp.h`): add queue-age protection for volume passthrough commands (`VOL`) so stale queued volume payloads are dropped instead of being transmitted late, and add explicit per-volume enqueue logging to make delayed-source attribution deterministic during ghost-volume investigations. **Shared-contract note:** applied to `spectra_ls_system` (`main`) now for live issue containment; `menu-only` (`esphome/control-py`) parity update is intentionally deferred and tracked as branch divergence until validated migration.

- HA/AC Tuya Authority Enforcement (`packages/dst_tuya_ac.yaml`): make DST controller authoritative over Tuya internal thermostat behavior by setting Tuya cool setpoint farther below DST target (`DST target - 4°F`, clamped to Tuya min/max) and extending `dst_mode_reconciler` to re-assert Tuya mode/setpoint whenever Tuya drifts (`off`/`cool`/`fan_only`/`dry`), preventing app-side Tuya logic from silently overriding policy-selected HVAC intent.

- ESPHome/Audio Tuning Rollback Test (`esphome/spectra_ls_system/substitutions.yaml`): re-apply recommended **Profile B+** control/tcp audio tunings (pot cadence + TCP pacing/coalescing/backoff) after user-local edits introduced lag/replay behavior, restoring known-good baseline values for A/B validation.

- HA/AC Fan Flap Fix (`packages/dst_tuya_ac.yaml`): prevent forced off→fan retry loops when Tuya reports `hvac_action: unknown` by only retrying fan re-apply when mode is not `fan_only` or action is explicitly `idle/off`; this removes false recovery cycles that could briefly stop/restart fan output.

- HA/AC Controller Architecture Refactor (`packages/dst_tuya_ac.yaml`): replace overlapping fan/cool/off automations with a policy-first control model (`sensor.ac_target_mode` + `binary_sensor.ac_schedule_cool_request`) and a single reconciler automation (`automation.dst_mode_reconciler`) that applies mode transitions deterministically (`off`/`cool`/`fan_only`/`dry`) to eliminate race-driven state flapping.

- HA/AC Fan Reliability Hardening (`packages/dst_tuya_ac.yaml`): strengthen `dst_apply_fan_only_low` with an explicit Tuya fan-only apply + verification + fallback off→fan_only retry path when `hvac_action` remains idle, and add `sensor.ac_tuya_hvac_action` for direct visibility into real device runtime action vs optimistic mode state.

- HA/AC Trend Diagnostics UX (`packages/dst_tuya_ac.yaml`): enrich rising-trend visibility by preserving numeric 1-hour delta state handling (`sensor.dst_room_temp_change_1h` with unknown-aware output) and adding explicit trend-rate/summary sensors (`sensor.dst_room_temp_rate_1h`, `sensor.dst_room_temp_trend_1h_summary`) so operators can see meaningful metrics instead of binary-only `on/off` trend status.

- HA/AC Policy Tuning (`packages/dst_tuya_ac.yaml`): lower warm+rising fan-policy activation temperature threshold from `>70°F` to `>68°F` while retaining the existing 1-hour rising requirement.

- HA/AC Trend Signal Stabilization (`packages/dst_tuya_ac.yaml`): replace `binary_sensor.dst_room_temp_rising_1h` trend-platform dependency with a statistics-based 1-hour temperature-change sensor (`sensor.dst_room_temp_change_1h`) and template rising binary logic, eliminating frequent `unknown` state behavior and making fan-policy threshold evaluation deterministic.

- HA/AC Sensor Source Cleanup (`packages/dst_tuya_ac.yaml`): remove `sensor.ac_internal_temperature` and `sensor.ac_internal_humidity` template sensors sourced from broken Tuya attributes (including invalid `-40` readings), standardizing frontend/environment monitoring on the external room sensor path.

- HA/AC Diagnostics (`packages/dst_tuya_ac.yaml`): add `sensor.ac_control_reason` to expose active AC control-path reasoning (`away_lock`, `paused`, `manual_override`, `fan_override_manual`, `fan_policy_warm_rising`, `schedule_cool`, `fan_only_active`, `dry_active`, `off`, `idle`) for frontend visibility and troubleshooting.

- HA/AC Architecture Refactor (`packages/dst_tuya_ac.yaml`): consolidate manual/schedule policy into centralized template binary sensors (`ac_pause_active`, `ac_manual_override_active`, `ac_warm_rising_policy_active`, `ac_fan_policy_active`), add reusable control scripts (`dst_set_manual_override_24h`, `dst_clear_manual_override`, `dst_apply_fan_only_low`), and replace fragmented/race-prone fan/manual automations with a unified manual-first flow (thermostat fan bridges + explicit manual hold gates + simplified cool/off schedule conditions).

- HA/AC DST Fan Command Reliability (`packages/dst_tuya_ac.yaml`): add event-level bridge on `climate.set_fan_mode` calls targeting `climate.room_dst` to force direct Tuya fan-only activation and low preset, ensuring thermostat-card fan actions execute even when DST state remains `idle`.

- HA/AC Thermostat Fan-Control Bridge (`packages/dst_tuya_ac.yaml`): add explicit automation that converts fan requests made from `climate.room_dst` fan controls into persistent `fan_only` HVAC mode + low fan preset and sets manual override hold, so thermostat-card fan actions behave like manual mode overrides instead of being ignored.

- HA/AC Manual Mode Persistence (`packages/dst_tuya_ac.yaml`): manual mode interventions (`cool`/`fan_only`/`dry`) now assert a manual override hold so schedule automations do not immediately revert user-selected modes; auto-off now only applies while DST is actively cooling (not fan-only/dry), and manual `off` clears the hold.

- HA/AC Scheduling Enhancement (`packages/dst_tuya_ac.yaml`): add an all-day fan-only control path that activates when room temperature is above 70°F and rising over the past hour (compressor off, fan low), plus a frontend `Fan Override` toggle to force fan-only behavior and block compressor auto-cool while active.

- ESPHome/Menu Navigation Direction Contract: Add shared top-level menu navigation helper (`components/sls_menu_nav.h`) and route menu-encoder delta handling through a global direction mapping (`menu_encoder_nav_sign`) in `spectra-ls-ui.yaml`, so clockwise/counterclockwise behavior is configured once and applied consistently across all menu levels/prompt lists.

- HA/Command-Line Resilience Fix: In `packages/spectra_ls_hw_status.yaml`, harden the `Spectra LS HW Status` command to guard for missing script/input files and emit a valid fallback JSON payload when unavailable, preventing recurring `command_line` return-code errors while preserving dependent attribute contracts.

- ESPHome/OLED Universal Title-Style Split Tuning: In `esphome/spectra_ls_system/components/sls_oled_text_layout.h`, refine two-line split scoring with capitalization-aware and connector-word penalties so labels avoid awkward breaks (for example ending line 1 with minor words like `of`, `the`, `in`, `to`) while preserving pixel-fit and center alignment across all OLED views.

- ESPHome/OLED Universal Label Layout Reset: In `esphome/spectra_ls_system/spectra-ls-peripherals.yaml`, remove the incremental line/centering helper stack and replace it with a single universal pixel-width-based centered wrap/fit method (shared by menu and lighting paths) so all label rendering uses the same deterministic split/truncate rules and avoids right-edge clipping across fonts.

- ESPHome/OLED Pixel-Width Header Wrap Fix: In `esphome/spectra_ls_system/spectra-ls-peripherals.yaml`, replace lighting-header-only character-count wrapping with font-pixel-width-aware split/fit logic and per-line width guards so long labels (including wider glyph endings) cannot clip at the right edge in centered two-line rendering.

- ESPHome/OLED Edge-Clipping Fix: In `esphome/spectra_ls_system/spectra-ls-peripherals.yaml`, tighten lighting-header wrap thresholds using display-width-based character limits to prevent right-edge clipping of long labels in both active and slider-only lighting screens.

- ESPHome/OLED Lighting Header Wrap Fix: In `esphome/spectra_ls_system/spectra-ls-peripherals.yaml`, update the active non-slider lighting header path to use centered two-line wrapping for long target labels and shift mode/brightness HUD elements down to avoid overlap.

- ESPHome/Universal Fallback Targets: In `esphome/spectra_ls_system/spectra-ls-peripherals.yaml`, replace room-specific fallback target construction with a universal target fallback set so menu behavior remains portable when HA option feeds are temporarily unavailable.

- ESPHome/OLED Text Fit Improvement: In `esphome/spectra_ls_system/spectra-ls-peripherals.yaml`, add centered two-line word-wrap rendering for long menu/prompt/lighting labels (instead of hard cutoff/ellipsis-only rendering) while keeping current font sizes unchanged; list row heights now expand only when wrapping is actually needed to preserve normal menu density for short labels.

- ESPHome/NP Responsiveness + Noise Tuning: In `esphome/spectra_ls_system/substitutions.yaml`, speed metadata refresh cadence (`ha_audio_refresh_ms` `6000→2000`, `meta_refresh_ms` `5000→1500`, `meta_refresh_tick_ms` `500→250`) to reduce new-track/play-start detection lag; also reduce periodic heartbeat status logging (`heartbeat_interval_ms` `60000→300000`). In `esphome/spectra_ls_system/packages/spectra-ls-audio-tcp.yaml`, slow HA-facing control number republish cadence (`EQ Low/Mid/High`, `Arylic Volume Set` `60s→300s`). In `esphome/spectra_ls_system/packages/spectra-ls-diagnostics.yaml`, move passive diagnostics publishing from `60s→300s` (including CPU/heap/PSRAM/virtual diagnostics) to cut recurring `[S]` state spam.

- ESPHome/Runtime Noise Reduction (quiet by default): In `esphome/spectra_ls_system.yaml`, disable `web_server` state logging (`log: false`) to stop high-churn `[S][...]` state-stream output; in `esphome/spectra_ls_system/packages/spectra-ls-diagnostics.yaml`, disable CPU debug logging by default and raise passive diagnostic refresh intervals to 60s; in `esphome/spectra_ls_system/packages/spectra-ls-audio-tcp.yaml`, raise HA-facing EQ/volume template number refresh intervals to 60s to reduce routine status chatter.

- ESPHome/Diagnostics Cleanup: Remove one-cycle `disp_diag` transition logger from `esphome/spectra_ls_system/spectra-ls-peripherals.yaml` after root-cause playback predicate hardening, reducing log noise without changing display-state behavior.

- ESPHome/HA Position Activity Debounce: In `esphome/spectra_ls_system/packages/spectra-ls-audio-tcp.yaml`, only refresh `ha_audio_pos_last_ms` when `ha_audio_position` actually moves (>=0.05s delta), preventing unchanged paused-position updates from being misread as active playback evidence.

- ESPHome/Now-Playing Idle-Recency Clamp (follow-up): Refine `playing_effective` in `esphome/spectra_ls_system/spectra-ls-peripherals.yaml` so Arylic/LR recency and activity windows only contribute when corresponding sources are non-idle, and only refresh `last_playing_true_ms` under active-source conditions. This prevents idle metadata timestamp churn from holding `play=1`/NP state with empty content.

- ESPHome/Now-Playing Evidence Gate Fix (diagnostic-driven): Use one-cycle `disp_diag` findings to harden `playing_effective` in `esphome/spectra_ls_system/spectra-ls-peripherals.yaml` so HA `state=playing` only refreshes playback-hold timestamps when recent HA playback evidence exists (recent meta or position updates). This prevents stale upstream `playing` flags from pinning the idle display on Now Playing with empty content.

- ESPHome/Display Diagnostics (One-Cycle Instrumentation): Add always-on, rate-limited transition logging in `esphome/spectra_ls_system/spectra-ls-peripherals.yaml` (`compute_display_state`) for `display_state`, `no_audio_activity`, `menu_active`, `lighting_active`, and `screen_mode` so stuck-idle branch selection can be traced from a single reboot cycle.

- ESPHome/Now-Playing Predicate Hardening: In `esphome/spectra_ls_system/spectra-ls-peripherals.yaml`, tighten `playing_effective` recovery so Arylic/LR recency no longer revives playback when source is idle, and make the clear-down condition depend on active-source/activity signals rather than raw recency timestamps. This prevents idle no-content systems from being pinned on the Now Playing screen.

- ESPHome/UI Display-State Routing Fix: In `esphome/spectra_ls_system/spectra-ls-peripherals.yaml`, update `compute_display_state` decision ordering so `no_audio_activity` resolves directly to `STATE_BLANK` when menu and lighting-activity windows are not active, preventing idle home/target text screens from persisting when nothing is playing.

- ESPHome/UI Idle Blanking Root-Cause Fix: In `esphome/spectra_ls_system/packages/spectra-ls-audio-tcp.yaml`, stop treating passive volume-pot polling as synthetic user activity by only updating `last_input_ms` when the mapped pot target actually changes; this prevents idle timers from being continuously reset by analog polling noise and allows proper blanking when nothing is playing.

## 2026-04-17

- ESPHome/UI Idle-Blank Safety Fix: In `esphome/spectra_ls_system/spectra-ls-peripherals.yaml`, change the unknown display-state fallback renderer to fail closed (blank screen) instead of drawing `${friendly_name}`/status text; in `packages/spectra-ls-system.yaml`, initialize `display_state` to blank by default so post-flash startup/compute race windows cannot surface the stale top-line `SPECTRA LS` header when nothing is playing.

- HA/MA Control-Hub Consolidation (template.inc, batch 11): Final 5+ dedupe sweep by adding shared scalar resolver attributes for now-playing (`resolved_position`, `resolved_duration`, `resolved_volume`, `resolved_friendly`) and MA-active (`resolved_duration`, `resolved_position`, `resolved_volume`) surfaces, then rewiring the corresponding sensors to consume shared attributes instead of repeating inline target/meta fallback blocks.

- HA/MA Control-Hub Consolidation (template.inc, batch 10): Execute a 5+ slice maintainability pass by (1) adding shared `resolved_app` on `sensor.ma_active_player_id_resolved` and rewiring `MA Active App`, and (2) normalizing remaining control-path `rooms_json` string parsing callsites to the dual-mode contract (trim+sentinel guard, `[`/`{` support, mapping extraction) across host/path/target/capability/ambiguity readers.

- HA/MA Control-Hub Dedupe (template.inc, batch 9): Add shared `resolved_artist` and `resolved_album` attributes on `sensor.now_playing_entity` and `sensor.ma_active_player_id_resolved`, then rewire `Now Playing Artist/Album` and `MA Active Artist/Album` sensors to consume those shared attributes; preserves existing fallback precedence while removing duplicated inline artist/album resolution blocks.

- HA/MA Control-Hub Dedupe (template.inc, batch 8): Add shared `resolved_title` attributes on `sensor.now_playing_entity` and `sensor.ma_active_player_id_resolved`, then rewire `Now Playing Title` and `MA Active Title` sensors to consume those shared attributes; preserves existing URL/queue suppression and fallback ordering while removing duplicated inline title-resolution blocks.

- HA/MA Control-Hub Dedupe (template.inc, batch 7): Add shared resolved source attributes on `sensor.now_playing_entity` and `sensor.ma_active_player_id_resolved` (candidate filtering + queue/placeholder guards + media_player friendly-name normalization), then rewire `Now Playing Source` and `MA Active Source` to consume those shared resolved values instead of duplicating inline candidate-reduction loops.

- HA/MA Control-Hub Dedupe (template.inc, batch 6): Add shared `player_json` + `player_fields_json` attributes on `sensor.now_playing_entity` and rewire `Now Playing Title/Artist/Album/Source/State` to consume the shared fields payload instead of repeating per-sensor MA player lookup loops; also align `packages/ma_control_hub/script.inc` string JSON guard to accept both `[` and `{` payload starts for mapping-compatible room parser behavior.

- HA/MA Control-Hub Dedupe (template.inc, batch 5): Add shared `player_fields_json` projection on `sensor.ma_active_player_id_resolved` and rewire `MA Active Title/Artist/Album/App/Source` to consume that shared payload instead of repeating per-sensor `player_json` parse/field extraction blocks; also normalize `packages/ma_control_hub/script.inc` room JSON string parse branch to use trimmed payload + sentinel guard consistency.

- DevTools + HA/MA Control-Hub Quality (batch 4): In `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` Iteration Workbench 1A and command-effect templates, replace manual `expected_value` dependency with action-aligned effect expectation (`expected_effect_value`) derived from a single probe action value input (with safe default to entity `min`) to eliminate false WARN deltas from mismatched expected/probe payloads; in `packages/ma_control_hub/template.inc`, add shared `player_json` lookup payload on `sensor.ma_active_player_id_resolved` and reuse it across `MA Active Title/Artist/Album/App/Source` to dedupe repeated `lookup_id/short_id/players/ns.p` loops without behavior drift.

- HA/MA Control-Hub Correctness + Quality (template.inc, batch 3): Fix high-risk self-reference in `sensor.spectra_ls_rooms_json` state parser to source room data from `sensor.spectra_ls_rooms_raw.rooms` (authoritative input) instead of self-reading `sensor.spectra_ls_rooms_json.rooms_json`; additionally normalize `MA Meta Resolver` guarded string parse to use `raw_trim | from_json`, switch `MA Detected Receiver Entity` to normalized `sensor.spectra_ls_rooms_json.rooms_json`, and remove dead locals (`_mp`, `appletv`) that were not consumed.

- HA/MA Control-Hub Code Quality (template.inc, batch 2): Continue parser-contract cleanup in `packages/ma_control_hub/template.inc` by (1) routing additional room consumers (`MA Detected Receiver Entity`, `MA Active Meta Entity`) to normalized `sensor.spectra_ls_rooms_json.rooms_json` payloads instead of re-reading raw rooms attributes, and (2) standardizing guarded string JSON parsing in touched branches to parse `raw_trim` values.

- HA/MA Control-Hub Code Quality (template.inc): Refactor `sensor.ma_meta_candidates` attribute derivation in `packages/ma_control_hub/template.inc` to use a shared parsed summary payload (`candidate_summary_json`) for entities/names/labels/scores/best-candidate outputs, reducing duplicated parser branches and improving maintainability; also normalize guarded JSON parse inputs to use trimmed payloads in touched parser branches.

- Docs/DevTools Batched Refactor (3 slices): Update `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` to (1) route Iteration Workbench 1A and Template #2 room-map parsing through normalized `sensor.spectra_ls_rooms_json.rooms_json` payloads instead of re-parsing `sensor.spectra_ls_rooms_raw` inline, and (2) replace broad `states.number` scans in Templates #3 and #5 with explicit Spectra audio control candidate lists to reduce listener noise and render churn.

- HA/MA Meta Candidates Refactor: Consolidate repeated candidate scan loops in `packages/ma_control_hub/template.inc` by introducing a shared candidate-row payload attribute for `sensor.ma_meta_candidates` and deriving summary attributes from that shared structure, reducing drift and repeated high-cost template passes.

- Docs/DevTools 1A Noise Reduction: Tune `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` Iteration Workbench (Template 1A) command-readiness scan to use a targeted audio-control number candidate list instead of broad `states.number` domain enumeration, reducing irrelevant listener wakeups while keeping expected Spectra control-surface probes intact.

- HA/MA Meta Candidates Dedupe: Reduce duplicated scoring loops in `packages/ma_control_hub/template.inc` by introducing a shared `best_candidate_json` attribute for `sensor.ma_meta_candidates` and routing `best_entity`/`best_score` through that shared payload.

- HA/MA Script Parser Unification: Update `packages/ma_control_hub/script.inc` (`ma_update_target_options`) to consume normalized `sensor.spectra_ls_rooms_json` payload (`rooms_json`) for room-target option derivation, aligning script-side parsing with template-side helper refactors and reducing contract drift.

- HA/MA Parser Helper Refactor: Reduce duplicated `rooms` parser blocks in `packages/ma_control_hub/template.inc` by routing key control-path sensors (`ma_control_hosts`, `ma_active_control_path`, `ma_control_targets` + attributes, `ma_active_target_by_host`, `ma_active_control_capable`, `ma_control_ambiguous`) through normalized `sensor.spectra_ls_rooms_json` payload ingestion.

- HA/MA Refactor (Meta Resolver): Reduce parser drift in `packages/ma_control_hub/template.inc` by introducing a shared `best_candidate_json` attribute in `sensor.ma_meta_resolver` and routing both `best_entity` and `best_score` through it instead of maintaining duplicate `candidates_json` parse/scan blocks.

- Docs/DevTools Iteration Workbench: Add a unified single-paste `1→4` diagnostics template (`1A`) to `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` that consolidates health, routing path, command readiness, and command-effect checks into one iterative operator workflow with compact roll-up status and inline probe payload suggestions.

- HA/Now-Playing Source Stability (ma_control_hub): Harden `packages/ma_control_hub/template.inc` source resolvers (`Now Playing Source`, `MA Active Source`) to select the first valid non-placeholder, non-queue candidate in deterministic order (with media_player entity-id friendly-name resolution and final friendly-name fallback), preventing intermittent blank `src` output while target/host/meta are otherwise healthy.

- ESPHome/Runtime Cleanup (Code-Side): Remove unreferenced high-frequency internal template sensors from `esphome/spectra_ls_system/packages/spectra-ls-lighting.yaml` (`lighting_hue_state`, `lighting_sat_state`, `lighting_brightness_state`, `selected_room_state`, `selected_target_state`) to eliminate unnecessary 500ms polling work with no behavioral contract impact.

- Docs/DevTools Phase-4 Template Modernization: Update `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` Template #2 and Template #14 to use the full dual-mode payload contract (native sequence/mapping + guarded string JSON parse) with trimmed lowercase sentinel checks (`raw_trim_l`) for deterministic parser behavior.

- Docs/DevTools Iteration-4 Accuracy Fix: Update `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` Template #16 to detect virtual battery status using HA `sensor`-domain entities (not `text_sensor` domain) and soften verdict semantics so idle/no-recent-probe activity reports `WARN` rather than hard `FAIL` when core virtual entities are present.

- Docs/DevTools Hotfix: Repair Jinja syntax corruption in `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` Template #16 (`Iteration 4 Diagnostics Chatter Check`) by removing stray `endif/endfor` mismatches and leaked lines from adjacent templates, restoring valid render behavior in HA Developer Tools.

- Docs/DevTools Diagnostics Hardening: Update `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` Iteration 4 chatter template virtual-entity discovery to tolerate prefixed `friendly_name` variants (substring match) and reorder tail templates into strict `13 → 14 → 15 → 16` numeric sequence for predictable navigation.

- Docs/DevTools Ordering: Reorder `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` template sections into strict numeric sequence so the tail block is now `13 → 14 → 15 → 16` (eliminates out-of-order `16/14/15/13` layout).

- Diagnostics/Template Fix (Iteration 4): Harden `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` Template #16 entity resolution to use `friendly_name` matching with explicit entity-id fallbacks, preventing false FAIL reports where virtual diagnostics exist but `name`-based lookup returns empty IDs.

- ESPHome/Diagnostics Iteration 4: Reduce virtual-input diagnostics chatter in `esphome/spectra_ls_system/packages/spectra-ls-diagnostics.yaml` by slowing passive publish cadence for virtual mode/control/status entities (no behavior-path changes), and add an Iteration 4 DT verification template in `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` focused on interaction visibility with lower idle spam.

- HA/MA Parser Guard Determinism (Iteration 2): Tighten complex-payload string parser guards in `packages/ma_control_hub/template.inc` and `packages/ma_control_hub/script.inc` to evaluate sentinel checks against trimmed lowercase payloads, reducing whitespace/case-induced drift while preserving dual-mode sequence/mapping behavior.

- HA/MA Full Parser Modernization (Iteration): Expand `packages/ma_control_hub/template.inc` rooms/candidate readers to fully honor the dual-mode contract across remaining call sites (native sequence, native mapping with canonical key extraction, and guarded string JSON parse) and add an iteration DT validation template in `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` to verify parser-shape compatibility after each modernization pass.

- HA/MA Contract Hardening: Update `packages/ma_control_hub/template.inc` and `packages/ma_control_hub/script.inc` rooms/candidate readers to a dual-mode parser contract (native sequence payloads accepted directly; string JSON payloads parsed only after trim+guard checks), preventing audio routing/meta/control surfaces from collapsing when Home Assistant exposes attribute payloads as non-string objects.

- HA/Lighting Native Payload Parse Fix: Update `packages/spectra_ls_lighting_hub.yaml` catalog consumers to accept both string JSON arrays and native sequence payloads from `items_json`, preventing false-empty parses when Home Assistant surfaces `state_attr(..., 'items_json')` as a non-string object.

- HA/Lighting JSON Parse Hardening: Make `packages/spectra_ls_lighting_hub.yaml` catalog/options JSON parsing whitespace-tolerant (`| trim` before `[` checks and parse) across template sensors and sync automations, preventing valid JSON payloads with leading newline/space from being treated as empty and collapsing selectors to `No Rooms` / `All`.

- HA/Lighting Catalog Fallback Hardening: Add area-registry (`areas()` + `area_entities()`) fallback population path inside `sensor.control_board_eligible_light_catalog` so room/target helper surfaces recover even when primary `states.light`/`area_id(...)` pass yields empty results. This prevents persistent `No Rooms`/`All` selector collapse after reload when catalog bootstrap is unexpectedly empty.

- HA/Lighting Catalog Payload Overflow Fix: Move `sensor.control_board_eligible_light_catalog` payload from sensor state into attribute-backed JSON (`items_json`) and switch dependent templates to read attribute-first with state fallback. This prevents long JSON truncation/parse collapse that manifested as `control_board_room_options = ["No Rooms"]` and `control_board_target_options = ["All"]` despite healthy entities.

- HA/Lighting Catalog-First Target Resolution Fix: Refactor `packages/spectra_ls_lighting_hub.yaml` room/target contract surfaces to resolve from a shared eligible-light catalog built from `states.light` + `area_id(...)`, then drive `room_options`, `target_options`, `room_area_id`, `target_entity_id`, `room_hs`, and `room_on` from that catalog. This removes dependence on direct per-template `area_entities(...)` scans and restores per-room target population where selectors previously degraded to `All`-only.

- HA/Lighting Area-Selection Scope Fix: Correct Jinja loop-scope behavior in `packages/spectra_ls_lighting_hub.yaml` by replacing plain `area_id_selected` loop assignments with `namespace(area_id=...)` in room-dependent target/HS/on templates. This restores per-room light discovery so populated rooms no longer show `All`-only targets.

- HA/Lighting Template Runtime Fix: Correct malformed Jinja block closures in `packages/spectra_ls_lighting_hub.yaml` (`Control Board Target Options` and `Control Board Target Entity ID`) where `endif` incorrectly closed `for ent in lights` loops; this was driving `sensor.control_board_room_options`/`target_options` contract dependents into `unavailable` and collapsing room UI back to static fallback labels.

- Diagnostics Hardening: Update `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` Template #6 (Lighting Rename Validation) to treat placeholder-only room options (`No Rooms`/`Unknown`) as **FAIL** and `All`-only target options as degraded (**WARN**), preventing false PASS reports when room population is actually broken.

- HA/Lighting Room Source-of-Truth Fix: Switch `packages/spectra_ls_lighting_hub.yaml` room/target derivation to HA area registry as primary contract (`areas()` + `area_entities()`), including `room_options`, `room_area_id`, `target_options`, `target_entity_id`, `room_hs`, and `room_on`, decoupling visible room population from eligible-light catalog filtering.

- HA/Lighting Fallback Policy Correction: Remove `Unassigned` all-lights fallback from `sensor.control_board_eligible_light_catalog` and switch empty room fallback to `No Rooms`; add placeholder-only guard in room sync to preserve existing concrete room options. This prevents repeated `Unassigned + Back` loops from masking real area contract issues.

- HA/Lighting Startup Stabilization: Remove transient availability gating from `sensor.control_board_eligible_light_catalog` and add anti-downgrade guard in room sync so `input_select.control_board_room` is not overwritten by `['Unassigned']` when concrete room options already exist; addresses recurring `Unassigned + Back` regressions after reload/boot churn.

- Hotfix: Correct `packages/spectra_ls_lighting_hub.yaml` Jinja block terminator in `sensor.control_board_eligible_light_catalog` (`endif` vs accidental `endfor`) to restore template loading; this unblocks room/target option generation that had been failing at HA config parse time.

- HA/Lighting Regression Correction: Restore `packages/spectra_ls_lighting_hub.yaml` eligible-light catalog to area-first discovery (`areas()` + `area_entities()`), with all-lights fallback only when area-derived results are empty; fixes unintended "Unassigned-only" room output introduced by prior all-lights-first refactor.

- MA Control Targets Boot Fallback: Harden `packages/ma_control_hub/template.inc` so `sensor.ma_control_targets` falls back to `input_select.ma_active_target` options when `sensor.spectra_ls_rooms_raw` is not yet populated at boot/reload, preventing blank control-target prompt/options during startup race windows.

- HA/Lighting Selectability Regression Fix: Update `packages/spectra_ls_lighting_hub.yaml` sync automations to stop preserving stale room/target option values in `input_select` options, and force-reset to valid parsed options when contracts repopulate; resolves "Select Control Target" lock state with no selectable targets.

- HA/Lighting Room Options Root-Cause Fix: Rework `sensor.control_board_eligible_light_catalog` in `packages/spectra_ls_lighting_hub.yaml` to derive candidates from all `light.*` entities (including unassigned-area lights) instead of area-only enumeration, preventing `['Unknown']` option collapse that forced ESP OLED room-menu fallback labels (`Room 1/2/3/4`).

- Diagnostics/Template Fix: Correct `Source Truth Test` false-negative behavior in `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` by replacing brittle core sentinel failure logic (`sensor.time`/`sun.sun`) with a core entity-count heuristic and by switching source probes to realistic exposed entities; prevents misleading "HA degraded" conclusions when control-hub contracts are the actual fault domain.

- HA/Lighting Control-Hub Recovery: Broaden `sensor.control_board_eligible_light_catalog` eligibility in `packages/spectra_ls_lighting_hub.yaml` to include on/off and legacy light entities (while still excluding speaker-like pseudo-lights), preventing false-empty room/target catalogs that caused ESP menus to fall back to generic room labels.

- ESPHome/Source Status UX Hardening: Normalize source placeholders and surface explicit fallback status (`HA not accessible`) in OLED source resolution when all source feeds are empty/unavailable, removing ambiguous blank/unknown source states.

- ESPHome/HA Option Intake Resilience: Add dual-source room/target option feeds (`input_select` attribute options + catalog sensors) and prefer non-empty parsed lists for OLED menu rendering and UI count refresh paths, preventing transient helper-state gaps from collapsing lighting menus to static fallback room labels.

- ESPHome/Now-Playing Architecture Hardening: Remove source-only activity from playback truth in `spectra-ls-peripherals.yaml` (no longer promotes passive source labels into active playback), tighten display hold to real playing/recent-playing signals, and clear source fallback caches when hold is inactive so idle state resolves to true blank.

- ESPHome/Option Parser Contract Hardening: Apply placeholder-value filtering (`unknown`, `unavailable`, `none`, `null`, `idle`) to duplicated dynamic option parsers in `spectra-ls-lighting.yaml` so HA transient states cannot contaminate room/target selector mapping paths.

- ESPHome/Lighting Menu Resilience Fix: Sanitize dynamic option parsing in `spectra-ls-peripherals.yaml` so placeholder HA values (`unknown`, `unavailable`, `none`, `null`, `idle`) are dropped instead of rendered as real menu entries; Lighting Rooms now correctly falls back to configured room labels when HA options are temporarily unavailable.

- ESPHome/OLED Idle-State Fix: Prevent stale source labels (for example `YOUTUBE`) from holding Now Playing when no active playback exists by tightening display-active gating to playing/recent-media signals and clearing source-fallback fields when media display hold is inactive.

- ESPHome/Display Contract Refactor: Move display-state IDs to shared substitutions and replace local enum literals in `spectra-ls-peripherals.yaml` state computation/render paths, keeping display mode semantics centralized and reusable across package evolution.

- ESPHome/Nav Constants Refactor: Add shared menu-count/fallback-count substitutions and replace active hardcoded menu counts/branch sizes in UI, hardware nav handlers, and OLED menu rendering paths to reduce cross-file drift and make menu evolution centrally tunable.

- HA/Lighting Architecture Refactor: Introduce a reusable `sensor.control_board_eligible_light_catalog` contract in `packages/spectra_ls_lighting_hub.yaml` and route room options, target options, room area resolution, target entity resolution, room HS, and room on/off state through that single eligibility source to prevent layered filtering drift.

- Workflow/Instruction Update: Extend `.github/copilot-instructions.md` with an explicit architecture-first directive for this workspace: treat bug reports as signals to improve reusable design and avoid "just make it work" patch layering.

- HA/Lighting Target Hygiene: Harden `packages/spectra_ls_lighting_hub.yaml` target derivation to exclude speaker-like pseudo-light entities (name/entity contains `speaker`) while retaining domain-light routing, preventing entries like `Kitchen speakers` from appearing in lighting target menus.

- HA/Lighting Contract Fix: Enforce strict light-only target options in `packages/spectra_ls_lighting_hub.yaml` by removing stale-current option carryover from target sync, preventing non-light entries (for example speaker labels) from persisting in `input_select.control_board_target`.

- ESPHome/UI UX Fix: Add direct one-click entry from non-menu lighting screen into Lighting Rooms menu in `spectra-ls-ui.yaml` so opening lighting menu no longer requires an extra select press.

- ESPHome/UI Navigation Fix: Eliminate boot-time ghost root-menu rendering that was visually presenting menu tiles without an active menu state, causing dead-end-feeling navigation and hidden menu semantics.

- ESPHome/UI Menu Fix: Force boot/root menu rendering to the icon-tile root level so fallback/boot states no longer show literal `Lighting / Audio / Gear` list text; those labels are internal root-category semantics behind icon navigation.

- ESPHome/UI Regression Fix: Remove implicit top-level menu re-entry after lighting-adjust hold and playback-stop transitions so the UI no longer auto-shows literal `Lighting / Audio / Gear` tiles unless the menu is explicitly opened by user input.

- ESPHome/UI Architecture: Replace hardcoded menu-level magic numbers in active lighting/UI control paths with named menu-level constants from substitutions to reduce transition fragility and improve v-next maintainability.

- ESPHome/Lighting Architecture: Centralize lighting value-adjust transition flow into a single script path (`start_lighting_value_adjust`) to eliminate duplicated menu-to-adjust state writes and reduce transition drift risk as v-next menu behavior expands.

- ESPHome/Lighting UX Flow: Rework lighting value adjustment behavior so Hue/Saturation (and lighting adjust paths) do not get pre-empted by active playback; after adjustment activity ends, UI returns to the same lighting menu context, holds for 5000ms, then gracefully transitions to Home (no active playback) or Now Playing (when active).

- ESPHome/Lighting Hardening: Make UI auto-routing hardware-mode-aware in `spectra-ls-ui.yaml` so audio-driven auto-flip behavior no longer overrides explicit lighting selector modes (`hardware_mode` 0/1), improving hardware-first determinism for v-next.

- ESPHome/Lighting Hardening: Add structural guardrails for v-next stability by removing hardcoded lighting hold timing (new substitution), sanitizing slider selection index handling in room/target menu contexts, and gating HA light service dispatch when neither target entity nor area routing is available.

- ESPHome/Lighting Audit Fix: Correct display-state gating so lighting render windows honor `hue_ring_active_until_ms` (not only brightness/audio windows), preventing Hue/Saturation lighting views from dropping back to the main/menu screen during active adjustments.

- ESPHome/Lighting Audit Fix: Harden slider input routing in `spectra-ls-lighting.yaml` so slider movement exits stale non-lighting menu states and applies as lighting input, while still preserving room/target selection behavior when explicitly in Room/Target menu levels.

- ESPHome/Lighting Audit Fix: Add a consistent temporary lighting hold window in `focus_lighting` so encoder/button/slider interactions all keep `screen_mode=0` long enough to prevent immediate auto-flip back to audio while playback is active.

- Docs/README: Tighten `Digital Audio Ingest + Final DAC Path` intro wording and add an explicit plain-language positioning line: “In plain terms: a DAC for your home.”

- Docs/README: Re-group Inputs feature copy into explicit **Lighting Controls** and **Audio Controls** blocks, and replace the awkward controls-example heading with a concise **Controls** section label for cleaner launch-page flow.

- Docs/README: Final editorial launch-page pass — enforce one-time `Spectra Level / Source (Spectra L/S)` introduction and use `Spectra L/S` thereafter, while tightening opening narrative flow for a cohesive front-to-back product voice.

- Docs/README: Rework non-spec sections into product-outcome language (what users feel and can do) by removing file-path/architecture-heavy prose from system interaction and feature sections; keep detailed technical capability data centered in specs/cutsheet areas.

- Docs/README: Replace implementation-heavy input inventory wording with outcome-focused product copy; explicitly call out direct lighting Brightness/Hue/Saturation control over rooms or individual lights and keep the Inputs section centered on what users can do (not internal mechanics).

- Docs/README + v-next NOTES: Add promotional hands-on input examples (including full transport controls: Play/Pause, Next, Back/Previous), strengthen product-forward copy tone, and add a formal v-next crossfade/balance slider requirement: in multi-room mode, slider shifts volume balance between rooms; in single-room mode, slider controls speaker balance.

- Docs/README: Replace dry input inventory copy with concrete control behavior notes for the lighting slider (brightness mapping + debounced sends), room switching (cycle + input_select sync), and the implemented multi-room transition/crossfade path via `script.control_board_set_light_dynamic` transition support.

- Docs/README: Add an explicit `HD DAC Capability Cutsheet` block (wireless stack, multi-room behavior, music-service list, and local-source support) and add plain-language whole-home multi-speaker synchronization copy (same-track room lock + independent room playback) without protocol-insider wording.

- Docs/README: Normalize shorthand usage to `Spectra L/S` (no standalone `L/S`), change EQ phrasing to `Physical 3-Band EQ`, move Seesaw under an explicit Inputs section, and expand physical-control listing to call out switches/buttons/knobs/sliders/dials.

- Docs/README: Add explicit direct analog-input control wording for Volume + 3-band EQ, document automatic Light/Sound interaction behavior when Home Assistant already knows targets, and include UP2STREAM HD DAC audio-side capability notes (dual-band Wi-Fi, AirPlay 2, Spotify Connect, TIDAL Connect, aptX HD Bluetooth 5.0, no-amp module class) sourced from published product metadata.

- Docs/README: Expand front-page intended-use messaging to explicitly call out direct analog control for Volume + 3-band EQ (bass/mid/treble), home dance-party usage, v-next multiple switches/dials expansion, and responsive screen/menu navigation feedback.

- Docs/README: Link `Home Assistant` at its first paragraph mention and de-link later duplicate `Home Assistant` link usage so external-linking follows first-mention-only style.

- Docs/README: Reframe the Digital Audio Ingest section around intended day-to-day use (coffee-table/home digital-to-analog control hub, couch/desk operation) and remove HDMI/ARC hyperlinking in that section while keeping capability statements intact.

- Docs/README: Remove the literal “audio nerd” phrasing in the Digital Audio Ingest + Final DAC Path section and replace the multi-bullet codec list with a single concise `Supports: FLAC, MP3, AAC, AAC+, ALAC, APE, WAV.` line.

- Docs/README: Set front-page title and first project mention to **Spectra Level / Source** (with immediate **L/S** shorthand), normalize remaining visible **Spectra LS** wording to **L/S**, and remove the dedicated external-links block including the dead `n4archive` reference in favor of inline linked hardware/ecosystem mentions.

- Docs/README: Convert front-page hardware/audio ecosystem mentions to inline manufacturer/project URLs (MCUs, input ICs, control interface ecosystems, HDMI/ARC reference, ESS ES9038Q2M, and OLED controller references) so readers can jump directly from each mention to its canonical project/vendor page.

- Docs/README: Normalize product naming in front-page audio section to introduce **Level / Source** once and use **L/S** shorthand thereafter while preserving published ARC/DAC capability details.

- Docs/README: Strengthen front-page hardware/audio positioning to describe Spectra Level / Source as a fully integrated high-fidelity source-to-output system (not a DAC-only claim), while retaining the explicit ARC ingest → ESS ES9038Q2M conversion path and published 192kHz/24-bit + codec capability references.

- Docs/Hardware Notes: Document HDMI ARC-capable source ingest path (HDMI input → ARC digital audio split/extract → final ESS ES9038Q2M DAC stage) including 192kHz/24-bit target capability and codec support references (`FLAC`, `MP3`, `AAC`, `AAC+`, `ALAC`, `APE`, `WAV`) in project notes/README.

- ESPHome/Diagnostics: Add a temporary virtual-input harness in `esphome/spectra_ls_system/packages/spectra-ls-diagnostics.yaml` with mode/control injectors, mode-nav test buttons, and a one-shot battery script so selector/control-class/menu flows can be validated in HA without physical RP2040 wiring changes.
- RP2040/Phase B: Fix v-next selector/control-class event fidelity by emitting IDs `120` and `121` as analog packets (index payload preserved) instead of button packets (boolean collapse), updated in both live `CIRCUITPY/code.py` and mirror `esphome/circuitpy/code.py`.
- ESPHome/Phase C: Add initial `120`–`124` event consumers in `esphome/spectra_ls_system/packages/spectra-ls-hardware.yaml` and new shared state globals in `packages/spectra-ls-system.yaml` (`hardware_mode`, `control_class`, `menu_override_active`) with deterministic mode routing and clear-on-hardware-change menu override behavior.

- Tooling/Build: Harden `bin/esphome_spectra_build_local.sh` + `bin/esphome_spectra_upload_local.sh` for fast iteration with incremental stage sync, stable local artifact copies, build summary output, optional forced clean stage, and upload helper auto-use of latest staged config.
- ESPHome/OTA: Migrate `esphome/spectra_ls_system.yaml` from legacy `web_server.ota: true` to OTA platform syntax (`ota: - platform: web_server`) for ESPHome 2026.4.0+ compatibility while preserving web UI upload support.
- Tooling/Build: Add local workstation automation scripts under `bin/` for one-command Spectra LS build kickoff (staging copy + path rewrite + compile artifact reporting) with optional OTA upload, so fast Ryzen-side builds avoid HA VM/Celeron compile bottlenecks without modifying tracked runtime YAML.
- ESPHome/Web UI: Enable `web_server` OTA exposure in `esphome/spectra_ls_system.yaml` (`web_server.ota: true`) so the built-in device web UI renders the firmware upload form (POST `/update`) for direct binary uploads.
- UI/Code Cleanup: Deduplicate OLED display lambda option parsing helpers in `esphome/spectra_ls_system/spectra-ls-peripherals.yaml` by reusing a single shared `trim_ascii`/`parse_options` implementation for both control-target prompt and dynamic options lists (no behavior change).
- UI/Code Cleanup: Remove redundant/unreachable second `STATE_NOW_PLAYING` render branch in `esphome/spectra_ls_system/spectra-ls-peripherals.yaml` display lambda and drop unused local state variable, reducing ambiguity in display-state flow.
- UI/Splash Stability: Fix startup splash sequence restart in `esphome/spectra_ls_system/spectra-ls-peripherals.yaml` by preventing delayed `on_boot` splash timer reinitialization after the display loop has already started splash timing.
- UI/Splash Readability: Keep the “SPECTRA” title line visible throughout splash stage 2 (subtitle reveal), removing the abrupt title disappearance while preserving existing splash timing.
- HA/MA Boot Auto-Select Fix: Update `packages/ma_control_hub/script.inc` so startup default target selection includes discovered targets (not only static room targets), preventing `none` from persisting when discoverable control-capable targets exist.
- HA/MA Startup UX: Add fallback auto-pick of first active (playing/paused) allowed target when detected receiver is not ready yet, reducing blank-screen/prompt-on-boot behavior while discovery data settles.
- Docs/Architecture Notes: Expand `esphome/spectra_ls_system/v-next-NOTES.md` with a dedicated control-path/hardware-family roadmap section, including current as-wired implementation snapshot and phased family/codepath expansion plan.
- HA/MA Override Schema: Extend room/target override contract to carry `hardware_family`, `control_path`, `control_capable`, and `capabilities` metadata so overrides can fully represent control routing intent for current and future device families.
- HA/MA Capability Routing: Gate control-host resolution on `control_capable` + routed `control_path` (currently `linkplay_tcp`) so direct POT adjustments are sent only to explicitly control-capable targets.
- HA/MA Routing Policy: Add discovery-first control-path routing in `packages/ma_control_hub/template.inc` with explicit per-target tagging (`linkplay_tcp` now, extensible for future non-LinkPlay paths) and expose active control path as a template sensor.
- HA/MA Fallback Safety: Add `input_boolean.ma_control_fallback_enabled` (default `off`) in `packages/ma_control_hub/input_boolean.inc` and gate static host override/fallback routing branches behind this tunable for clean no-override testing by default.
- HA/MA Target Discovery: Tighten discovered target inclusion in `packages/ma_control_hub/script.inc` to include only linkplay-compatible TCP targets by default, while preserving extensibility for future routing classes.
- Project Guidance: Update `.github/copilot-instructions.md` and `esphome/spectra_ls_system/v-next-NOTES.md` to codify discovery-first onboarding, default-off fallback policy, and per-device control-path decision requirements.
- HA/MA Auto-Discovery: Enhance `packages/ma_control_hub/script.inc` and `packages/ma_control_hub/template.inc` so MA-discovered players with valid entity IDs and IP addresses are treated as first-class targets/options and TCP host candidates, reducing dependency on static per-room host mappings for plug-in onboarding.
- HA/MA Routing: In `sensor.ma_control_hosts`, prefer active target entity `ip_address` when available before static fallback mappings, enabling zero-touch control host resolution for newly discovered compatible players.
- ESPHome/Config Hygiene: Clarify Arylic endpoint section in `esphome/spectra_ls_system/substitutions.yaml` to document HA runtime authority (`sensor.ma_control_hosts` / `sensor.ma_control_port`) and switch bootstrap endpoint defaults to neutral non-site-specific values instead of repo-pinned local hosts.
- ESPHome/Config Hygiene: Reorganize `esphome/spectra_ls_system/substitutions.yaml` tunables into distinct domain sections (system cadence, display/menu UI, audio UX/prompting, lighting UX, and control-loop/log cadence) to remove mixed random grouping and improve operator readability.
- Docs: Update `esphome/spectra_ls_system/SUBSTITUTIONS-TUNING-LEGEND.md` with a substitutions layout map so tuning guidance matches the new sectioned structure.
- ESPHome/Tuning Policy: Adopt B+ as default in `esphome/spectra_ls_system/substitutions.yaml` based on observed low-latency/high-quality network behavior with occasional jitter spikes; reserve B++ as DJ-candidate profile pending extended soak validation.
- ESPHome/Tuning Surface: Add next-batch substitution tunables for non-transport smoothing in `esphome/spectra_ls_system/substitutions.yaml` (control-target evaluation cadence, MA target sync interval, meta-cycle settle delay, input/log throttle intervals) and wire these into `packages/spectra-ls-audio-tcp.yaml` to remove hardcoded timing constants.
- Docs: Update `esphome/spectra_ls_system/SUBSTITUTIONS-TUNING-LEGEND.md` with network-quality guidance, B+ default positioning, and B++ DJ-candidate profile notes.
- ESPHome/Audio UX: Add reboot ambiguity grace handling in `esphome/spectra_ls_system/packages/spectra-ls-audio-tcp.yaml` so a valid MA target + control host can establish lock during early boot even when transient ambiguity sensors report true, preventing repeated post-reboot control-target prompts.
- ESPHome/Tuning: Apply a tighter B++ responsiveness profile in `esphome/spectra_ls_system/substitutions.yaml` (pot intervals/settle and Arylic TCP pacing/burst/worker tuning) for reduced perceived control lag while preserving transport stability margins.
- ESPHome/Substitutions: Prune non-spectra dead keys from `esphome/spectra_ls_system/substitutions.yaml` (legacy BLE presence + lighting-controller carryovers and other unreferenced runtime leftovers) and expand section comments into operator-oriented guidance (purpose, gains, risks, and tuning intent).
- ESPHome/Audio TCP: Add substitution-driven tunables for Arylic TCP worker/log behavior (queue length, worker stack/priority, and TX log throttle) and wire them through build flags into `components/arylic_tcp.h` so they can be tuned without C++ edits.
- ESPHome/Audio TCP: Wire Arylic TCP pacing constants to compile-time substitution-driven build flags from `esphome/spectra_ls_system/substitutions.yaml` (including newly exposed burst-guard knobs), so tuning values are actually applied without editing `arylic_tcp.h` defaults.
- Docs: Add `esphome/spectra_ls_system/SUBSTITUTIONS-TUNING-LEGEND.md` with baseline profile sets (Baseline/Safe/Performance/Aggressive), parameter descriptions, and staged test guidance for per-network tuning.
- ESPHome/Audio TCP: Consolidate duplicated script-level EQ gate/send logic by introducing shared `arylic_set_eq_channel` in `esphome/spectra_ls_system/packages/spectra-ls-audio-tcp.yaml`, with existing `arylic_set_bass/mid/treble` IDs retained as thin compatibility wrappers.
- ESPHome/Audio TCP: Consolidate duplicated EQ pot update/defer logic in `esphome/spectra_ls_system/packages/spectra-ls-audio-tcp.yaml` into a shared channel-aware script path to reduce repeated hot-path code while preserving per-channel behavior and deferred-send semantics.
- Docs: Update `README.md` with explicit external reference links (ESPHome, Home Assistant, Music Assistant, and Arylic/LinkPlay API references) for easier operator onboarding.
- ESPHome/Audio TCP: Add reversible Arylic TCP burst guard in `esphome/spectra_ls_system/components/arylic_tcp.h` to pace sustained command bursts per host/port via a short sliding-window delay (delay/coalesce behavior, no protocol changes) to reduce control-lane chatter while preserving responsiveness.
- ESPHome: Update `esphome/spectra_ls_system/substitutions.yaml` `friendly_name` to remove reserved URL path separator (`/`) and avoid 2026.7.0 validation failure.
- RP2040/Architecture: Pass 3B.1 removes dead legacy inline autocalibration/tracking functions and globals from `code.py` now that `sls_calibration_runtime.py` is authoritative, reducing monolith drift and keeping loop behavior manager-driven.
- RP2040/Docs+Architecture: Add per-file RP ownership/instruction contracts at top of all RP firmware source files (`boot.py`, `code.py`, `sls_*.py`) and add a detailed RP legend document on-device (`CIRCUITPY`) with mirrored repo copy; begin Pass 3B by extracting autocalibration/tracking state machine responsibilities toward a dedicated runtime module to reduce monolith drift risk.
- RP2040/Architecture: Pass 3 introduces reusable runtime helper functions for button-edge emit/log flow and precomputed analog channel profiles to reduce repeated hot-path lookups/branches while preserving packet format and behavioral semantics.
- RP2040/Architecture: Pass 2 modularization extracts analog/calibration helper functions from `code.py` into `sls_analog.py` and `sls_calibration.py` (live `CIRCUITPY` + repo mirror) while preserving runtime loop behavior and packet contract.
- RP2040/Architecture: Begin v-next-safe modularization of firmware by extracting config/protocol/input-decode helpers from monolithic `code.py` into dedicated modules in live `CIRCUITPY/` with synchronized mirror under `esphome/circuitpy/`; preserve existing packet contract and runtime behavior.
- RP2040/Phase B: Add hardware input-capture contract in `CIRCUITPY/code.py` + mirror `esphome/circuitpy/code.py` for v-next reserved events (`120`–`124`) including mode selector, control-class selector, and mode-navigation momentary event emits; preserve existing event IDs and behavior while adding parallel v-next event path.
- Productization: de-track `spectra_ls_primary_tcp_host.yaml` and `spectra_ls_room_tcp_host.yaml` from git/GitHub while keeping local files in place; host defaults now use secrets-based values and these per-user endpoint files are ignored to prevent personal config pollution.
- Docs/Policy: add explicit universal-product directive in `.github/copilot-instructions.md` forbidding tracked per-user host/IP config artifacts.
- Docs/Policy: Add a required pre-flight checklist to `.github/copilot-instructions.md` for any file move/delete operation; session must show backup path, planned `CHANGELOG.md` line, and restore command/path before execution.
- Docs/Policy: Strengthen `.github/copilot-instructions.md` with mandatory file move/delete governance — deletes now require non-repo backup + changelog entry + restore path, and moves/renames must be changelogged with source/destination paths.
- Repo/ESPHome: Rename `esphome/secrets.example.yaml` to `esphome/secrets.example` so the secrets template is not treated as an ESPHome dashboard project.
- ESPHome: Phase 16 rename step on `spectra_ls_system` path — rename final active package includes from `control-board-audio-tcp.yaml` and `control-board-lighting.yaml` to `spectra-ls-audio-tcp.yaml` and `spectra-ls-lighting.yaml`, and repoint `esphome/spectra_ls_system.yaml` include map/comments.
- HA: Harden `sensor.now_playing_state` in `packages/ma_control_hub/template.inc` to avoid propagating transient `unknown/unavailable` from `sensor.now_playing_entity`; fallback now resolves to `sensor.ma_active_state` (or `idle`) for stable rename-step validation and routing diagnostics.
- Docs: Normalize section numbering/order in `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` so rename validation checks run in ascending sequence (9 → 10 → 11).
- ESPHome: Phase 15 rename step on `spectra_ls_system` path — rename system package include from `packages/control-board-system.yaml` to `packages/spectra-ls-system.yaml` and repoint `esphome/spectra_ls_system.yaml` include.
- ESPHome: Phase 14 rename step on `spectra_ls_system` path — rename UI package include from `packages/control-board-ui.yaml` to `packages/spectra-ls-ui.yaml` and repoint `esphome/spectra_ls_system.yaml` include.
- Docs: Add a dedicated `ma_control_hub` package-loader regression template to `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` for fast PASS/WARN/FAIL checks in HA Developer Tools after reload/restart.
- Repo: Add regression guardrails for `ma_control_hub` split package layout by ignoring `packages/ma_control_hub/*.yaml` (allow only `.inc`) and adding `.github/validate-ma-control-hub-layout.sh` to fail fast on duplicate fragments or missing host include files.
- HA: Fix `ma_control_hub` package loader conflicts by removing duplicate `packages/ma_control_hub/*.yaml` split fragments (keep `.inc` only) so `!include_dir_named packages` does not auto-load sub-fragments as standalone packages.
- HA: Restore missing `/config/spectra_ls_primary_tcp_host.yaml` and `/config/spectra_ls_room_tcp_host.yaml` include files used by `packages/ma_control_hub/input_text.inc` to resolve startup config load errors.
- ESPHome: Phase 13 rename step on `spectra_ls_system` path — rename hardware package include from `packages/control-board-hardware.yaml` to `packages/spectra-ls-hardware.yaml` and repoint `esphome/spectra_ls_system.yaml` include.
- ESPHome: Phase 12 rename step on `spectra_ls_system` path — rename active peripherals include from `control-board-peripherals-no-rings.yaml` to `spectra-ls-peripherals.yaml` and repoint `esphome/spectra_ls_system.yaml` include.
- Repo: Stop syncing archived `previous/` trees to GitHub by ignoring `esphome/control-py/previous/` and `esphome/spectra_ls_system/previous/`.
- ESPHome: Move legacy/stale package files out of active paths into `previous/` (non-runtime archive storage).
- Repo: Sync `esphome/spectra_ls_system/` content to `main` so GitHub reflects the active spectra_ls_system project tree.

## 2026-04-16

- ESPHome: Phase 11 rename step on tracked main path — rename archived rings peripherals file from `esphome/control-py/previous/control-board-peripherals.yaml` to `esphome/control-py/previous/spectra-ls-peripherals-rings-legacy.yaml` (archive-only, not in active includes).
- ESPHome: Phase 10 rename step on tracked main path — rename legacy non-TCP audio package file from `esphome/control-py/packages/control-board-audio.yaml` to `esphome/control-py/packages/spectra-ls-audio-legacy.yaml` (legacy/stale, TCP package remains authoritative).
- ESPHome: Phase 9 rename step on tracked main path — rename legacy headless package file from `control-board-headless.yaml` to `spectra-ls-headless.yaml` (no active include references).
- ESPHome: Phase 8 rename step on tracked main path — rename active peripherals include from `spectra-ls-peripherals-no-rings.yaml` to `spectra-ls-peripherals.yaml` and repoint `esphome/control-board-esp32-tcp.yaml` include.
- Docs: Update rename validation wording in `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` from “Peripherals No-Rings” to generic “Peripherals” for the new filename.
- ESPHome: Phase 7 rename step on tracked main path — rename no-rings peripherals file to `spectra-ls-peripherals-no-rings.yaml` and repoint `esphome/control-board-esp32-tcp.yaml` include.
- Docs: Add targeted post-rename HA reload validation template (peripherals no-rings step) to `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` for per-step spectra rename checks.
- ESPHome: Phase 6 rename step on tracked main path — rename hardware package to `spectra-ls-hardware.yaml` and repoint `esphome/control-board-esp32-tcp.yaml` include.
- Docs: Add targeted post-rename HA reload validation template (hardware package step) to `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` for per-step spectra rename checks.
- ESPHome: Phase 5 rename step on tracked main path — rename UI package to `spectra-ls-ui.yaml` and repoint `esphome/control-board-esp32-tcp.yaml` include.
- Docs: Add targeted post-rename HA reload validation template (UI package step) to `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` for per-step spectra rename checks.
- ESPHome: Phase 4 rename step on tracked main path — rename system package to `spectra-ls-system.yaml` and repoint `esphome/control-board-esp32-tcp.yaml` include.
- Docs: Add targeted post-rename HA reload validation template (system package step) to `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` for per-step spectra rename checks.
- ESPHome: Phase 3 rename step on tracked main path — rename audio TCP package to `spectra-ls-audio-tcp.yaml` and repoint `esphome/control-board-esp32-tcp.yaml` include.
- Docs: Add targeted post-rename HA reload validation template (audio package step) to `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` for per-step spectra rename checks.
- Docs: Add targeted post-rename HA reload validation template (lighting package step) to `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` for per-step spectra rename checks.
- ESPHome: Phase 2 rename step on tracked main path — rename lighting package to `spectra-ls-lighting.yaml` and repoint `esphome/control-board-esp32-tcp.yaml` include.
- Docs: Publish `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md` to `main` and add README high-level system-test overview for Templates 1–5 smoke/diagnostic workflow.
- HA: Prevent `ma_control_hub` split fragments from being misloaded as standalone packages by renaming `packages/ma_control_hub/*.yaml` to `*.inc` and updating `packages/ma_control_hub.yaml` includes.
- HA: Restore `packages/ma_control_hub.yaml` and all split files from `menu-only` branch for parity, and revert temporary absolute include-root rewrite.
- HA: Fix `packages/ma_control_hub.yaml` include roots to `/config/packages/ma_control_hub/*` so YAML reload resolves split package files correctly.
- ESPHome: Phase 1 rename step on tracked main path — rename active diagnostics package to `spectra-ls-diagnostics.yaml` and repoint `esphome/control-board-esp32-tcp.yaml` include.
- Docs: README description now calls out room/lighting/audio auto-discovery and minimal user configuration expectations.
- Repo/Docs: Stop tracking root `configuration.yaml`; switch to placeholder-based integration via `SPECTRA-HA-CONFIG-PLACEHOLDERS.md` for adding Spectra-specific lines into an existing Home Assistant config.
- Docs: Add bold README project-state banner (active heavy development + publish date) and a current hardware reference section covering MCUs, expanders, control interfaces, and recommended OLED screen profile.
- Docs: Declare `esphome/spectra_ls_system/v-next-NOTES.md` as the `main` branch direction source and require `README.md` alignment to that hardware-first roadmap.
- Docs: Update README elevator pitch to plain-English whole-home audio + lighting focus and add explicit audio clients/player types section (Music Assistant, HA media_player, WiiM integration, Arylic/LinkPlay, AirPlay/Apple TV, Plex optional).
- Docs: Rewrite README project-intent intro to emphasize whole-home audio + lighting control and simplify system interaction language.
- Docs: Add mandatory shared-contract go/no-go checklist (`.github/SHARED-CONTRACT-CHECKLIST.md`) and wire it into branch runbook + Copilot directives.
- Docs: Add top-level repository `README.md` with project intent, architecture interaction summary, key features, and detailed deploy instructions.
- ESPHome: Reduce diagnostics and control-number publish cadence to 30s (`EQ Low/Mid/High`, `Arylic Volume Set`, `OLED Contrast`, heap/PSRAM diagnostics) and simplify CPU reporting to a single `CPU Usage` sensor (disable per-core sensors and top-task logs).
- ESPHome: Reduce number state publish spam by throttling template number update intervals (`EQ Low/Mid/High`, `Arylic Volume Set`) from 500ms to 5s and `OLED Contrast` from 1s to 10s.
- ESPHome: Canonicalize secrets structure to `esphome/secrets.yaml` and remove duplicate per-project `secrets.yaml` under `esphome/spectra_ls_system/`.
- Repo: Add tracked `esphome/secrets.example.yaml` template while keeping real secret files ignored.
- Repo: Establish concurrent dual-branch operations with dedicated `menu-only` worktree under `.worktrees/menu-only`.
- Docs: Add filesystem safety gate to prevent destructive live-path moves/deletes without reversible snapshot and verification.
- Repo: Tighten HA tracking scope to Spectra project docs/packages/ESPHome paths and stop tracking generic HA root runtime files.

## 2026-04-15

- Repo: Enforce RP2040 source-of-truth policy (live `CIRCUITPY/` + single repo mirror `esphome/circuitpy/`) and remove stale duplicate `boot.py`/`code.py` copies from other ESPHome paths.
- Docs: Tighten Copilot instructions for senior/public-product standards, latest HA/ESPHome API diligence, and mandatory dual-sync RP2040 edits (live `CIRCUITPY/` + `esphome/circuitpy/`).
- Repo: Migrate to top-level `/mnt/homeassistant` Git root and import `esphome` history under `esphome/` with preserved commit history.
- Repo: Track core HA root files on `main` (`configuration.yaml`, `automations.yaml`, `scripts.yaml`, `scenes.yaml`, and `packages/`).
- Docs: Add dual-branch shared-contract merge gate (`main` + `menu-only`) with required paired update or explicit divergence note.

## 2026-04-14

- HA: Explicitly enable the template integration to ensure package template sensors load.
- HA: Explicitly enable the command_line integration for Spectra LS HW status polling.
- HA: Remove unsupported from_json default parameter in Spectra LS rooms template to ensure sensor loads.
- HA: Reduce false control-target ambiguity when now-playing clearly matches the active target.
- ESPHome: Add v.next self-contained `spectra_ls_system/` project and repoint `spectra_ls_system.yaml` to use it (substitutions, packages, components, and assets).
- ESPHome: Rename v.next peripherals file to `spectra-ls-peripherals.yaml` (drop legacy naming).

## 2026-04-13

- ESPHome: Repoint Control Board v2 entrypoint to control-py-scoped substitutions and components so the config is self-contained when duplicating control-py.
- ESPHome: Consolidate control-board dependencies into control-py (components and fonts), keeping root entrypoint in place.
- ESPHome: Fix rp2040_uart header path after moving components into control-py.
- ESPHome: Use MA active sensors directly for now-playing metadata to restore artist/source fields.
- HA: Add unified now-playing meta resolver with normalized scoring across MA/HA sources.
- HA: Harden meta resolver Plex allowlist defaults and debug candidate output handling.
- HA: Split ma_control_hub into logical include files for maintainability.
- HA: Gate kitchen meta override behind MA meta confidence so strong detections win.
- HA: Prefer active meta when it is playing/paused or fresh to avoid stale now-playing selection.
- HA: Use media_player is_playing/is_paused/play_state attributes to determine active meta and reduce stale picks.
- ESPHome: Add animated boot splash for Spectra L \ S lettering.
- Docs: Update Copilot instructions to avoid editing rings peripherals file.
- ESPHome: Add audio control gate logging + fallback to ma_control_host when ma_control_hosts is empty (volume/EQ TCP sends).
- ESPHome: Keep last valid control host(s) when active target is valid (avoid transient clears on HA flaps).
- ESPHome: Apply manual_ip from substitutions so Control Board stays on the IoT subnet.
- ESPHome: Temporarily pin `wifi.use_address` to 192.168.30.246 for Control Board v2 (OTA/API target only).
- ESPHome: Switch Control Board v2 Wi-Fi secrets to non-IoT keys and remove temporary use_address pin.
- Repo: Restore tracking of `esphome/circuitpy/` (authoritative RP2040 firmware mirror), while ignoring `control-py/previous/circuitpy/`.
- Repo: Track HA packages `packages/dst_tuya_ac.yaml` and `packages/ma_control_hub.yaml`.

## 2026-04-12

- HA: DST manual override now sticks until the room reaches the target temperature, and Tuya cool setpoint defaults 2°F below the DST target when turning on AC.
- HA: DST auto-off now respects manual override window to prevent premature shutdown.
- HA: DST now uses bedroom enviro temperature/humidity sensors with faster updates.
- HA: DST now reasserts Tuya cool mode while DST is cooling, without forcing preset changes during manual override.
- HA: Fix tuya_unsupported_sensors config flow await error and set DST automation/script modes to avoid “Already running” warnings.
- ESPHome: Stop forced HA update_entity calls for MA control host sensors to avoid template AssertionError spam.
- HA: Prefer active target for now-playing entity when target is playing with metadata to avoid stale AirPlay meta on OLED.
- ESPHome: Add control-target prompt grace window around playback/ambiguity transitions to prevent popups during track switches.
- ESPHome: Add Gear menu (Meta Select + Control Select) and manual Control Target prompt entry.
- ESPHome: Label control-target popup “Control Targets”.
- RP2040/Docs: Add dedicated Select button on PCF8575 (event 37) and mirror select input to menus.
- ESPHome: Harden control-target prompt parsing (escaped JSON), add prompt cancel/empty handling, and align menu activation index.
- ESPHome: Debounce control-target prompts, add Control Target popup label, and hold last valid TCP hosts during transient HA updates.
- ESPHome: Reduce Control Target popup highlight top overlap (2px padding).
- HA/ESPHome: Harden lighting target label → entity mapping and debounce slider brightness sends to avoid bursts.
- ESPHome: Lighting slider no longer pushes brightness while in menu mode; brightness mode auto-exits after inactivity and on menu entry.
- ESPHome: Deduplicate lighting HS/color apply logic (shared script).
- ESPHome: Remove unused lighting HS wrapper script (use shared apply path).
- ESPHome: Add control-target prompt cooldown to avoid repeated prompts on volume touches when hosts/ambiguity are unstable.
- ESPHome: Keep control-target selection sticky until the play/control source changes; suppress re-prompts while locked.
- ESPHome: Apply sticky control-target lock guard across EQ/volume audio control paths.
- ESPHome: Keep sticky control-target lock from clearing on empty/unknown source keys (only clear on confirmed source change).
- ESPHome: Ignore invalid control host updates while sticky lock is active to prevent prompt flapping.
- ESPHome: Adopt first valid source key into sticky lock to prevent initial lock drop.
- ESPHome: Fix EQ pot rounding so full range reaches -10..10.
- ESPHome: Block control-target prompt immediately on selection to avoid double-press.
- ESPHome: Centralize control-target prompt gating and keep lock sticky until user explicitly reopens the selector.
- Docs: Added detailed plan for ADS7830 + 5‑position control‑target rotary switch reorg (no implementation yet).

## 2026-04-07

- HA: Refactored MA meta/control hub for dynamic meta detection, receiver matching, overrides, and low‑confidence handling.
- HA: Meta candidates now filtered to active (playing/paused) sources and respect Plex allow‑lists plus legacy local session filter.
- HA: Added MA/HA labeling for meta candidates (`MA:` / `HA:`) to disambiguate origins.
- HA: Active target options now include the detected receiver when not already present.
- HA: Added universal TV/HDMI → Spectra auto‑switch package (`spectra_ls_tv_source_auto.yaml`).
- ESPHome: Added Meta menu (low‑confidence chooser) and HA override calls for manual selection.
- ESPHome: Meta menu header renamed to “Meta Player”.
- ESPHome: Suppressed EQ overlay during boot to avoid brief EQ flash.
- ESPHome: UI render path no longer mutates menu timing; last input timestamp now initialized at boot.
- ESPHome: Moved stale `control-board-peripherals.yaml` to `previous/` to keep it out of active builds.
- ESPHome: Tightened now-playing gating so stale metadata doesn’t revive the screen when nothing is playing.
- Docs: Updated control‑board notes to use “Meta player” terminology for override behavior.

## 2026-04-09

- HA: MA Active Friendly now prefers host-mapped/target entity (removes meta-driven label flips).
- ESPHome: Volume pot now mirrors EQ handling (interval/settle/jump deferral + 50ms deferred send loop).

## 2026-04-10

- ESPHome: Centralized Control Board v2 substitutions into `substitutions.yaml` and updated control-board configs to include it.
- ESPHome: Adjusted splash screen layout (bottom-justified subtitle) and reduced splash font sizes to fit OLED.
- ESPHome: Restored `presence.yaml` to its standalone substitutions (kept separate project unchanged).
- ESPHome: Removed HA volume fallback in OLED render path (TCP volume only).
- ESPHome: Nudged splash title down 5px for improved vertical balance.
- ESPHome: Suppressed EQ overlay immediately after splash unless EQ changes post-splash.
- ESPHome: Fixed splash EQ gating compile error (avoid id() shadowing).
- ESPHome: Updated boot splash stages (Stage 1: SPECTRA + "L \ S"; Stage 2: "Level \ Source"; SPECTRA hides after 1s in Stage 2).
- ESPHome: Added missing `eq_overlay_ignore_until_ms` global for display state gating.
- ESPHome: Fixed duplicate `now` declarations in audio TCP lambdas that caused build failures.
- Repo: Added workspace-level Copilot instructions for Home Assistant + ESPHome guidance.
- Repo: Expanded Copilot instructions with additional directives and reference links.
- Repo: Documented CIRCUITPY RP2040 firmware paths in Copilot instructions references.
- Docs: Corrected Control Board v2 notes (RP2040 hardware, TCP-only control path, and ADC channel mapping) and added explicit update gate.
- HA: Treat AirPlay/Apple TV sources as control-target ambiguous to force prompt selection.
- HA: Harden MA selection templates (guard room JSON parsing; define primary Spectra entity in now-playing templates).
- ESPHome: Treat AirPlay/Apple TV sources as ambiguous locally and clear stale control hosts on invalid updates to ensure popup triggers.
- HA: Add Apple TV entity allowlist for ambiguity (ensures prompt even when app/source is non-AirPlay).
- ESPHome: Reset control target prompt after popup expiry so repeated hardware interactions re-trigger the prompt.
- ESPHome: Keep control target prompt visible until ambiguity clears (no timeout when selection required).
- ESPHome: Trigger target prompt immediately when ambiguity turns on (no waiting for hardware input).
- ESPHome/HA: Add control-target selection list wiring (entities + menu selection via encoder).
- HA: Autodetect receiver now prefers a playing room entity from `spectra_ls_rooms_raw` before heuristic scoring.
- HA: Auto-select bypasses idle delay when a detected receiver is actively playing.
- HA: Added UART-over-TCP hardware play-state polling across rooms (`spectra_ls_hw_status`) using `PINFGET`.
- HA: Detected receiver now prefers hardware playing entity when available.
- HA: HW status polling is now on-demand (now-playing triggers + 15s active refresh) instead of constant 5s polling.
- HA: HW polling now treats AirPlay as playing when progress advances (mode-based + cached deltas).
- Docs: Updated Control Board v2 wiring/input ID map to match current ESPHome button/encoder/analog IDs.
- Docs: Updated RP2040 PCF8575 pin map and button list to match current CircuitPython firmware.
- Docs: Reordered control-py notes to surface pin maps near the top and refreshed deploy steps for current firmware.
- Docs: Re-read and refreshed control-board-2 notes with current TCP control path and reality check.
- ESPHome: Added debug logging for progress-bar drops and HA position/duration updates to trace meta gating.
- Hybrid: Move position smoothing to ESPHome (local timer between HA updates) and keep HA position sensors lightweight.
- Cleanup: Remove temporary HA/meta progress debug logging after hybrid stabilization.
- ESPHome: Decouple progress bar source from meta slots (prefer HA progress when active; fall back to arylic).
- ESPHome: CPU usage component refactor (single-source header, logging controls + tag) and diagnostic logging toggle.
- Audit: Confirmed `control-board-peripherals-no-rings.yaml` in `esphome/control-py/` is complete (not empty).
- ESPHome: Fix control-target prompt rendering and selection handling in UI/menu paths.
- HA/ESPHome: Remove Apple TV ambiguity detection (AirPlay-only prompt).

## 2026-04-11

- ESPHome: Fix OLED interval lambda missing time base (`now`) compilation error.
- ESPHome: Fix control-target prompt encoder navigation (use labels list for count).
- ESPHome: Use menu encoder center press as Select input.
- RP2040/Docs: Remove bass/treble encoder references (EQ is pot-only).
- ESPHome: Auto-dismiss control-target prompt once control hosts are valid and ambiguity clears; track manual prompts to avoid auto-close.
- HA: DST auto-cool raises setpoint to 74°F after 11pm for late-night comfort.
- HA: DST auto-cool fan scaling now uses low/high/strong only (no auto).
- HA: DST now uses bedroom temp/humidity sensors as primary controllers.
- HA: DST presets simplified to Home/Away; Away disables automations and turns HVAC off.
- HA: Add manual override window + 10-hour pause controls for DST automations.

## 2026-04-06

- ESPHome/RP2040: removed calibration UI/autocal/tracking flows; RP2040 continues to apply `/calibration.json`.
- ESPHome: simplified menu to Lighting/Audio only; TCP audio package is authoritative (non-TCP marked legacy).
- Docs: consolidated to a single control-board-2 notes file.
- ESPHome: EQ display now renders 3-band vertical bars (L/M/H) to match the three physical EQ pots.
- ESPHome: EQ overlay layout refined (slimmer rows, adjusted label spacing/positioning).
- RP2040: EQ pots now snap near edges to guarantee full min/max sweep.
- RP2040: enabled EQ pot auto-capture (tracking) to save min/max to `/calibration.json`.
- ESPHome: EQ bars no longer render fully filled at 0; draw outline with center fill only.
- ESPHome: fixed EQ endpoint rounding so 0% maps to full negative dB (no truncation).
- ESPHome: stabilized Now Playing against brief HA/meta dropouts (no blanking flicker).
- ESPHome: EQ overlay bars thickened (3px slider tick, taller container).
- ESPHome: volume pot pickup/catch to prevent HA/MA volume replay overriding the knob.
- ESPHome: extended Now Playing hold window to avoid periodic blanking when HA state flaps.
- HA: MA auto-select now ignores missing media_player entities to avoid forced update failures.
- HA: delay MA target refresh on startup and skip auto-select until MA players are available.
- ESPHome: Settings menu brightness slider now points at OLED contrast control.
- HA: auto-select can switch immediately on boot/invalid target while retaining debounce for normal changes.
- HA: Control Board view now targets live MA selector and OLED contrast entity.
- ESPHome: expose OLED contrast number to HA for brightness control.
- HA: MA auto-select now reacts to player/target changes and polls faster to cut startup lag.
- RP2040: add idle noise gate for volume pot to prevent phantom volume drift.
- HA: persist and restore last valid MA target to prevent target loss and volume dropouts.
- RP2040: require multiple consistent volume pot readings before sending changes.
- ESPHome/HA: volume controls are now read-only (ignore HA/MA volume writes; hide HA slider).
- ESPHome: removed volume pot catch/hold logic (input handling is RP2040-only).
- HA: disabled MA balance volume writes to keep volume read-only.
- HA: added volume_set watcher to log and notify any HA volume writes to MA targets.
- HA: volume_set watcher now logs HA context (user_id/parent_id/origin) for faster source tracing.
- HA: paused MA auto-select time-pattern loop to stop 5s focus flapping during volume debug.
- HA: auto-select no longer switches away when current target is active (reduces target churn).
- HA: auto-select action now uses script.turn_on to fix unknown action error.
- HA: added watcher for MA volume state changes (with context) to trace non-HA volume shifts.
- HA: now-playing/meta entity pinned to active target to prevent cross-room stale metadata.
- HA: now-playing entity selection prefers the player with real metadata and most recent updates (reduces AirPlay/Spectra blanks).
- HA: MA Active Title now falls back to Now Playing Title/Source/Friendly to avoid OLED blanks when MA metadata is empty.
- HA: Spectra LS meta entity now matches its playback entity to keep MA Active metadata populated.
- HA: Replaced AirPlay-specific meta heuristics with dynamic meta detection and receiver matching.
- HA: Refactored meta/control architecture with dynamic meta detection, receiver detection, meta override, and low-confidence indicator; removed debug volume watcher automations.

## 2026-03-25

- ESPHome: Added EQ full-screen slider view (9-band, 75% adjacent) and mirrored it to both `control-board-peripherals-no-rings.yaml` and `control-board-peripherals.yaml`.
- ESPHome: Added MA control host fallback (`sensor.ma_control_host`) when `ma_control_hosts` is empty; refreshes both sensors periodically.
- ESPHome: Arylic TCP send coalescing to reduce burst flooding while keeping pot responsiveness (latest payload wins, skip immediate duplicates).

## 2026-03-24

- HA: Split MA control hub into focused package files for maintainability.
- ESPHome: Increased Arylic TCP timeout and added ADS read safeguards/recovery in RP2040 input path.
- ESPHome: Added EQ screen overlay features and display state improvements to prevent Now Playing blanking.
