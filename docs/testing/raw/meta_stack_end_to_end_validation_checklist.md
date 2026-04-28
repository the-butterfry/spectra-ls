<!-- Description: Deterministic end-to-end checklist for Spectra LS metadata-stack stale-healing, policy diagnostics, and ESP UI auto-only behavior validation. -->
<!-- Version: 2026.04.27.2 -->
<!-- Last updated: 2026-04-27 -->

# Meta Stack End-to-End Validation Checklist

Use this checklist as the **rolling evidence ledger** for remaining metadata-stack slices.

## Scope

- Runtime metadata winner/freshness behavior (`packages/ma_control_hub/template.inc`).
- Component metadata-policy/suppression diagnostics (`custom_components/spectra_ls/*`).
- ESP UI auto-only metadata menu behavior (`esphome/spectra_ls_system/packages/spectra-ls-ui.yaml`).
- Hidden emergency fallback contract continuity (`input_boolean.ma_meta_override_active`, `input_text.ma_meta_override_entity`).

Out of scope:

- Metadata ownership cutover.
- New control-path families.
- Helper/entity renames.

## Required templates and checks

Run and capture outputs from:

1. `docs/testing/raw/scheduler_apply_deterministic_validation.jinja`
2. `docs/testing/raw/p5_s02_metadata_functionality_monitor.jinja`
3. `docs/testing/raw/stale_meta_root_cause_diagnostic.jinja`

Optional deep check (if ambiguity remains):

- `docs/testing/raw/p3_s03_metadata_prep_validation.jinja`

## Execution cadence (repeat per slice)

1. **Pre-change baseline capture**
   - Run templates 1 + 2.
   - Save status, readiness, active target/path, freshness ages, suppression/policy fields.
2. **In-change behavior probe**
   - Trigger deterministic refresh actions:
     - `spectra_ls.validate_metadata_policy`
     - `spectra_ls.validate_metadata_prep`
     - `spectra_ls.validate_contracts`
   - Re-run templates 1 + 2.
3. **Ghost/stale guard probe**
   - Run template 3 when stale/paused/playing confusion is observed.
   - Record stale reason classification and winner entity evidence.
4. **ESP UX gate probe**
   - Confirm metadata menu shows auto-only path in normal operation.
   - Confirm hidden fallback helpers remain writable and clearable via existing contract.
5. **Closeout proof packet**
   - Build proof line.
   - OTA proof line.
   - Git sync proof (`HEAD == origin/main`).

## PASS/WARN/FAIL rubric

- **PASS**
  - Scheduler + metadata monitor are `PASS/READY`.
  - No stale metadata rendered when no fresh active playback signal exists.
  - Suppression reason is deterministic when hiding stale/paused/long-idle signals.
  - ESP auto-only UX behavior is preserved.
- **WARN**
  - Core path healthy but one or more freshness/parity warnings remain.
  - Closeout blocked until warning cause is explicitly classified and accepted.
- **FAIL**
  - Contract invalid/missing-required, stale visible regression, or UX gate broken.

## Evidence record template

```text
Meta Stack Validation Record
----------------------------
run_id:
window_phase: pre|in|post
captured_at:
operator:

runtime_track:
  scheduler_status:
  metadata_monitor_status:
  route_decision:
  contract_valid:
  missing_required:

component_track:
  policy_verdict:
  suppression_reason:
  metadata_ready:
  trial_status:

stale_guard_probe:
  executed: true|false
  stale_reason:
  winner_entity:
  now_playing_state:
  now_playing_title:

esp_ui_probe:
  auto_only_menu_confirmed: true|false
  hidden_fallback_contract_intact: true|false

closeout_proof:
  build_line:
  ota_line:
  git_head:
  git_origin_main:

verdict:
  outcome: PASS|WARN|FAIL
  rationale:
  next_action:
```

## Rolling run log

### Run-0 baseline (2026-04-27)

- Build proof: `INFO Successfully compiled program.`
- OTA proof: `INFO OTA successful`
- Git sync proof: `HEAD 301538a` and `origin/main 301538a`
- Status: baseline infrastructure healthy after Step-5 ESP auto-only menu gating.

### Run-1 stale-window decoupling slice (2026-04-27)

- Slice: dual-threshold stale-policy hardening (`ma_meta_stale_s` for playing freshness, `ma_meta_paused_hide_s` for paused hold/hide) across runtime + component + diagnostics templates.
- Testing surfaces logged:
  - `docs/testing/raw/scheduler_apply_deterministic_validation.jinja`
  - `docs/testing/raw/p5_s02_metadata_functionality_monitor.jinja`
  - `docs/testing/raw/stale_meta_root_cause_diagnostic.jinja`
- In-slice verification captured:
  - Static problems check on touched files (no new template/yaml/docs errors; known environment import-resolution warnings only for `homeassistant.*` in workspace context).
  - Git sync proof: `HEAD 6ede5bf` and `origin/main 6ede5bf`.
- Runtime template packet status: **pending operator/runtime capture** (pre/in/post template renders not executed in this code-only slice).
- Status: code + diagnostics parity hardening completed and pushed; next closeout action is a fresh runtime template packet capture on the three required surfaces.
