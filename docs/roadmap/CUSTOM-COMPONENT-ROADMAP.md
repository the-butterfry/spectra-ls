<!-- Description: Integration roadmap for Spectra L/S Home Assistant component. -->
<!-- Version: 2026.08.14.4 -->
<!-- Last updated: 2026-08-14 -->

# Spectra L/S Home Assistant Integration Roadmap

## Goal

Deliver all active behavior through `custom_components/spectra_ls` with runtime consumers bound to integration contract outputs.

## Operating rules

- Integration-first for all net-new behavior.
- Runtime updates are allowed when required for stability, observability, or consumer binding.
- Discovery-first adaptation and capability-mapped routing remain mandatory.
- No install-specific hardcoding in tracked product logic.

## Near-term roadmap

### R1 — Contract stability

- Harden component outputs used by ESP/runtime consumers.
- Keep now-playing, target, and host contract payloads deterministic.

### R2 — Execution stability

- Keep startup/reconnect behavior consistent and fail-closed.
- Eliminate drift between integration packet outputs and runtime consumers.

### R3 — Operator trust

- Keep one-source diagnostics for readiness and health.
- Keep release notes and runbooks aligned to implemented behavior.

## Current status

- Integration control plane is active and primary.
- Runtime observers and consumers are aligned to integration contract surfaces in active paths.
- Documentation surfaces were reset to forward-only baseline for this roadmap.
- Metadata-priority hardening slice active: component now-playing selection is being tightened to prefer metadata-rich winners before passthrough source-only fallback in active playback windows.
- Diagnostics gate normalization active: component-authority mode now treats legacy parity fields as compatibility-only in top-line drift scoring to avoid false WARN/FAIL when OLED/metadata contracts are healthy.
- Selection-handoff gate normalization active: helper options alignment remains visible for operator insight but is advisory-only in component-authority mode when route + contract gates pass.

### Disposition

- Runtime track: implemented
- Integration track: implemented
