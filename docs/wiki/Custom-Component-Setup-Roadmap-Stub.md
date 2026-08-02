<!-- Description: User-facing stub roadmap for migrating setup flow to custom_components/spectra_ls over phased delivery. -->
<!-- Version: 2026.08.01.7 -->
<!-- Last updated: 2026-08-01 -->

# Custom Component Setup Roadmap Stub

This page tracks how setup moves from runtime-heavy to component-first.

## Current state (today)

- Runtime path is still the compatibility baseline for install stability.
- Component path is where net-new control behavior lands.

## Setup roadmap by phase (operator view)

### Phase 1 — Shadow parity

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

- Sidebar-first setup/tuning UX becomes primary.
- P6 settings checkpoint is available:
  - integration options provide encoder/button mapping fields,
  - service `spectra_ls.set_control_center_settings` supports operator/automation updates,
  - diagnostics surfaces expose control-center settings for verification.
- P6 execution checkpoint is available:
  - service `spectra_ls.execute_control_center_input` runs mapped encoder/button events,
  - dry-run-first and read-only-mode enforcement are enabled by default,
  - latest execution attempt diagnostics are exposed for operator verification.
- P6 execution validation artifacts are available:
  - monitor template [`docs/testing/raw/p6_s04_control_input_execution_monitor.jinja`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/testing/raw/p6_s04_control_input_execution_monitor.jinja),
  - checklist [`docs/testing/raw/p6_s04_control_input_execution_checklist.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/testing/raw/p6_s04_control_input_execution_checklist.md),
  - deterministic PASS/WARN/FAIL gate capture for bounded closeout decisions.

## What will be added next

- Concrete install checklist per phase
- Migration FAQ with rollback examples
- UI screenshots once config-flow surfaces stabilize

## Source references

- [`docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md)
- [`docs/roadmap/v-next-NOTES.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/roadmap/v-next-NOTES.md)
- [`docs/program/PARALLEL-PROGRAM-PLAYBOOK.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/program/PARALLEL-PROGRAM-PLAYBOOK.md)
