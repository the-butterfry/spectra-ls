<!-- Description: High-level architecture map for Spectra L/S runtime, control plane, and migration tracks. -->
<!-- Version: 2026.04.22.1 -->
<!-- Last updated: 2026-04-22 -->

# System Architecture

This page explains where things live and which path owns what.

## Top-level domains

1. **Runtime domain (legacy compatibility baseline)**
   - `esphome/spectra_ls_system/`
   - `packages/`
2. **Control-center domain (primary growth path)**
   - `custom_components/spectra_ls/`
3. **RP2040 input firmware domain**
   - live source: `CIRCUITPY/`
   - mirror source: `esphome/circuitpy/`

## What “sealed runtime baseline” means

- Runtime remains available for compatibility and rollback.
- Net-new growth is directed to the custom component path.
- Behavior-visible bugfixes should be evaluated in both tracks.

## Program execution model

Spectra runs a required parallel program:

- Runtime track: current stable behavior and rollback safety.
- Custom-component track: primary implementation path for forward features.

Every feature slice must map both tracks as implemented, compatibility-shimmed, or deferred with rationale.

## Ownership snapshot (current)

- Source-of-truth for active growth: `custom_components/spectra_ls/`
- Source-of-truth for compatibility baseline: `packages/` + `esphome/spectra_ls_system/`
- RP2040 firmware updates must be mirrored in both required locations.

## If you are new, read in this order

1. `docs/wiki/Getting-Started.md`
2. `docs/wiki/Install-on-Your-Own-HA.md`
3. `docs/wiki/User-Setup-Deploy-and-HA-Integration.md`
4. this page (for architecture context)

## Authoritative references

- Runtime architecture: `docs/architecture/CODEBASE-RUNTIME-ARCHITECTURE.md`
- Control hub architecture: `docs/architecture/CONTROL-HUB-ARCHITECTURE.md`
- Parallel program playbook: `docs/program/PARALLEL-PROGRAM-PLAYBOOK.md`
- Custom-component roadmap: `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`
- v-next notes: `docs/roadmap/v-next-NOTES.md`
