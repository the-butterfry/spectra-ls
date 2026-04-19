<!-- Description: High-level architecture map for Spectra L/S runtime, control plane, and migration tracks. -->
<!-- Version: 2026.04.19.1 -->
<!-- Last updated: 2026-04-19 -->

# System Architecture

## Top-level domains

1. **Runtime domain**
   - ESPHome runtime stack under `esphome/spectra_ls_system/`
   - Home Assistant package integration under `packages/`
2. **Control-plane migration domain**
   - Parallel custom component track under `custom_components/spectra_ls/`
3. **RP2040 input domain**
   - CircuitPython firmware in live `CIRCUITPY/` with mirrored source under `esphome/circuitpy/`

## Program execution model

The project runs a required parallel program:

- Runtime track (current production behavior)
- Custom-component track (future control-plane architecture)

Every feature slice must map both tracks as implemented, compatibility-shimmed, or deferred with rationale.

## Authoritative references

- Runtime architecture: `docs/architecture/CODEBASE-RUNTIME-ARCHITECTURE.md`
- Control hub architecture: `docs/architecture/CONTROL-HUB-ARCHITECTURE.md`
- Parallel program playbook: `docs/program/PARALLEL-PROGRAM-PLAYBOOK.md`
- Custom-component roadmap: `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`
- v-next notes: `docs/roadmap/v-next-NOTES.md`
