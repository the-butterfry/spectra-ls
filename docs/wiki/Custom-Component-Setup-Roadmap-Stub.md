<!-- Description: User-facing stub roadmap for migrating setup flow to custom_components/spectra_ls over phased delivery. -->
<!-- Version: 2026.04.19.1 -->
<!-- Last updated: 2026-04-19 -->

# Custom Component Setup Roadmap Stub

This page tracks how setup becomes easier as the `custom_components/spectra_ls` program matures.

## Current state

- Production path remains runtime + packages + ESPHome.
- Custom component is developed in parallel and must preserve compatibility.

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

## How this wiki page will evolve

- Add concrete setup checklists per phase.
- Add migration FAQ and rollback examples.
- Add screenshots/examples once component UI/config flow surfaces are stable.

## Source references

- `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`
- `docs/roadmap/v-next-NOTES.md`
- `docs/program/PARALLEL-PROGRAM-PLAYBOOK.md`
