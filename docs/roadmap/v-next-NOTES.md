<!-- Description: Active implementation notes for Spectra L/S integration-first execution. -->
<!-- Version: 2026.08.01.1 -->
<!-- Last updated: 2026-08-01 -->

# v-next Notes

## Current execution posture

- Active product lane is `custom_components/spectra_ls`.
- Runtime in `packages/` + `esphome/` consumes integration-owned contracts.
- Changes are executed as small, evidence-backed slices with parity across runtime and integration surfaces.

## Active priorities

1. Keep control routing deterministic from integration contract outputs.
2. Keep metadata/now-playing contracts coherent for UI + hardware consumers.
3. Keep startup/reconnect behavior stable under HA and device restarts.
4. Keep docs/governance synchronized with actual implemented behavior.

## Required completion gates per slice

- Root-cause implementation complete.
- Runtime + integration disposition explicitly recorded.
- Diagnostics/build checks clean for touched files.
- `README.md`, this file, roadmap spec, and changelog updated together when contracts or behavior change.

## Latest update (2026-08-01)

- Performed integration-first baseline cleanup and removed retired runtime archive/stub artifacts from active tracked surfaces.
- Rewired active hardware status observer to integration now-playing entities.
- Replaced long historical narrative with forward-only execution notes.

### Disposition

- Runtime track: implemented
- Integration track: implemented
