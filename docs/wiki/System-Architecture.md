<!-- Description: High-level architecture map for Spectra L/S runtime, control plane, and migration tracks. -->
<!-- Version: 2026.08.01.2 -->
<!-- Last updated: 2026-08-01 -->

# System Architecture

This page answers one practical question: **where should this change live?**

## The three domains

1. **Runtime domain (compatibility + rollback baseline)**
   - [`esphome/spectra_ls_system/`](https://github.com/the-butterfry/spectra-ls/tree/main/esphome/spectra_ls_system)
   - [`packages/`](https://github.com/the-butterfry/spectra-ls/tree/main/packages)
2. **Component domain (primary growth path)**
   - [`custom_components/spectra_ls/`](https://github.com/the-butterfry/spectra-ls/tree/main/custom_components/spectra_ls)
3. **RP2040 input domain**
   - live source: `CIRCUITPY/`
   - mirror source: [`esphome/circuitpy/`](https://github.com/the-butterfry/spectra-ls/tree/main/esphome/circuitpy)

## What “sealed runtime baseline” actually means

- Runtime stays available for stability and rollback.
- Net-new behavior goes to `custom_components/spectra_ls/` by default.
- Behavior-visible bugfixes still require a two-track check (runtime + component).

## Ownership rules (short version)

- If you are adding/changing behavior: start in component path.
- If you are patching active runtime behavior: include bounded rationale and rollback notes.
- If you touch RP2040 logic: keep live `CIRCUITPY/` and `esphome/circuitpy/` mirror in parity.

## File-routing quick map

| If you are changing... | Start here |
| --- | --- |
| Control-plane logic, selectors, routing policy, metadata policy | [`custom_components/spectra_ls/`](https://github.com/the-butterfry/spectra-ls/tree/main/custom_components/spectra_ls) |
| Runtime package behavior, HA helper contracts | [`packages/`](https://github.com/the-butterfry/spectra-ls/tree/main/packages) |
| ESP runtime firmware behavior | [`esphome/spectra_ls_system/`](https://github.com/the-butterfry/spectra-ls/tree/main/esphome/spectra_ls_system) |
| RP2040 input protocol/event map | live `CIRCUITPY/` + [`esphome/circuitpy/`](https://github.com/the-butterfry/spectra-ls/tree/main/esphome/circuitpy) |
| Process/docs/governance | [`docs/`](https://github.com/the-butterfry/spectra-ls/tree/main/docs) + [`.github/`](https://github.com/the-butterfry/spectra-ls/tree/main/.github) |

## If you are new

1. [`docs/wiki/Getting-Started.md`](Getting-Started)
2. [`docs/wiki/Install-on-Your-Own-HA.md`](Install-on-Your-Own-HA)
3. [`docs/wiki/User-Setup-Deploy-and-HA-Integration.md`](User-Setup-Deploy-and-HA-Integration)
4. this page

## Authoritative references

- Runtime architecture: [`docs/architecture/CODEBASE-RUNTIME-ARCHITECTURE.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/architecture/CODEBASE-RUNTIME-ARCHITECTURE.md)
- Control hub architecture: [`docs/architecture/CONTROL-HUB-ARCHITECTURE.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/architecture/CONTROL-HUB-ARCHITECTURE.md)
- Amped + HiFi ESP32 Plus S3 pin map: [`docs/hardware/AMPED-HIFI-ESP32-PLUS-S3-PIN-MAP.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/hardware/AMPED-HIFI-ESP32-PLUS-S3-PIN-MAP.md)
- Parallel program playbook: [`docs/program/PARALLEL-PROGRAM-PLAYBOOK.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/program/PARALLEL-PROGRAM-PLAYBOOK.md)
- Custom-component roadmap: [`docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md)
- v-next notes: [`docs/roadmap/v-next-NOTES.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/roadmap/v-next-NOTES.md)
