<!-- Description: Active implementation notes for Spectra L/S integration-first execution. -->
<!-- Version: 2026.08.14.4 -->
<!-- Last updated: 2026-08-14 -->

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

### Disposition (2026-08-14)

- Runtime track: implemented
- Integration track: implemented

## Latest update (2026-08-14)

- Initiated component-first now-playing metadata-priority correction slice to restore OLED-first contract: show true title/artist when available; passthrough source label remains bounded fallback only.
- Scope narrowed to `custom_components/spectra_ls/metadata_stack.py` selection + metadata prep semantics so runtime remains a contract consumer in this slice.
- Normalized validation gates so component-authority operation no longer emits false parity/handoff WARN states when legacy parity fields are unresolved but component route/metadata contracts are healthy.
- Finalized selection-handoff scoring to treat helper option-alignment mismatches as advisory-only in component-authority mode while preserving strict WARN behavior outside component mode.

### Disposition

- Runtime track: compatibility-shimmed
- Integration track: implemented
