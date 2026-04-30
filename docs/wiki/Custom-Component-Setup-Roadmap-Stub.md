<!-- Description: User-facing stub roadmap for migrating setup flow to custom_components/spectra_ls over phased delivery. -->
<!-- Version: 2026.04.29.6 -->
<!-- Last updated: 2026-04-29 -->

# Custom Component Setup Roadmap Stub

This page tracks how setup becomes easier as the [`custom_components/spectra_ls`](https://github.com/the-butterfry/spectra-ls/tree/main/custom_components/spectra_ls) program matures.

## Current state

- Production path remains runtime + packages + ESPHome.
- Custom component is the primary lane for net-new control-center feature growth and is developed in parallel with strict compatibility posture.

## Setup roadmap by phase

### Phase 1 — Shadow mode parity (read-only)

- Component scaffolding and parity surfaces land.
- User setup remains package/runtime-based.

### Phase 2 — Registry/router foundation

- More deterministic target discovery and route diagnostics.
- Setup docs begin adding component-assisted validation steps.

### Phase 3 — Controlled write path (dual-write)

- Component starts orchestrating selected write paths behind compatibility shims.
- Setup docs include dual-write guardrail guidance and rollback switches.

### Phase 4 — Guided setup expansion

- Profile/mode features mature.
- Component-oriented setup flows become primary for new installs.

### Phase 5 — Domain cutover

- Domain-by-domain migration from legacy package logic to component control plane.
- Setup docs migrate from “runtime-first” to “component-first.”

### Phase 6 — Sidebar control-center productization

- Sidebar-first setup/tuning/defaults/overrides UX becomes primary.
- P6 settings checkpoint is validated and available:
  - integration options provide encoder/button mapping fields,
  - service `spectra_ls.set_control_center_settings` supports operator/automation updates,
  - diagnostics surfaces expose control-center settings for verification.
- P6 execution checkpoint is validated and available:
  - service `spectra_ls.execute_control_center_input` runs mapped encoder/button events,
  - dry-run-first and read-only-mode enforcement are enabled by default,
  - latest execution attempt diagnostics are exposed for operator verification.
- P6 execution validation artifact checkpoint is validated:
  - monitor template [`docs/testing/raw/p6_s04_control_input_execution_monitor.jinja`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/testing/raw/p6_s04_control_input_execution_monitor.jinja),
  - checklist [`docs/testing/raw/p6_s04_control_input_execution_checklist.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/testing/raw/p6_s04_control_input_execution_checklist.md),
  - deterministic PASS/WARN/FAIL gate capture for bounded closeout decisions.

## How this wiki page will evolve

- Add concrete setup checklists per phase.
- Add migration FAQ and rollback examples.
- Add screenshots/examples once component UI/config flow surfaces are stable.

## Source references

- [`docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md)
- [`docs/roadmap/v-next-NOTES.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/roadmap/v-next-NOTES.md)
- [`docs/program/PARALLEL-PROGRAM-PLAYBOOK.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/program/PARALLEL-PROGRAM-PLAYBOOK.md)
