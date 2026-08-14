<!-- Description: Repository changelog for Spectra L/S integration-first development. -->
<!-- Version: 2026.08.14.4 -->
<!-- Last updated: 2026-08-14 -->

# Changelog

## 2026-08-14

- Spectra component-first now-playing metadata-priority correction (planned/implemented in this slice):
  - objective: restore OLED primary contract to true now-playing metadata (title/artist) when available, with passthrough source labels as bounded fallback only.
  - root-cause class: passthrough source-context selector posture could settle on source-only winners before metadata-rich candidates, and broad display-allowed semantics obscured metadata-readiness intent.
  - scope: `custom_components/spectra_ls/metadata_stack.py` selector + metadata prep logic, with runtime consumer behavior preserved as contract consumer.
  - expected result: when active playback metadata exists upstream, component now-playing entities publish title/artist-ready payloads and OLED consumers stop defaulting to source/friendly-only labels.
  - two-track disposition: runtime track compatibility-shimmed (consumer behavior unchanged in this slice); component track implemented (contract selection logic hardened).
  - passthrough no-live-metadata correction: when title/artist are unavailable, component now-playing fallback now prefers passthrough source continuity labels (for example `Optical In`) and avoids room-friendly label dominance (for example `Kitchen Speakers`) on OLED consumers.
  - diagnostics gate correction: selection-handoff and parity drift warnings now avoid false FAIL/WARN in component-authority mode when runtime behavior is intentionally component-owned and legacy parity fields are compatibility-only.
  - selection-handoff final normalization: helper option-alignment mismatches remain visible as advisory telemetry in component-authority mode and no longer force top-line WARN when route/contract readiness is PASS.

- Docs parity update for this behavior slice:
  - synchronized `README.md`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`, and `docs/roadmap/v-next-NOTES.md` to reflect metadata-priority contract posture.

## 2026-08-01

- README second-pass concision + hardware inventory: removed duplicate-sounding intro sections, tightened user-facing product copy, and added a complete current hardware list (main unit, controlled endpoint hardware, and optional remote lane) with an explicit maintainer reminder to update the list and changelog in the same hardware-change slice.

- README opening clarity pass: replaced remaining abstract intro language with a direct end-user statement of product identity ("physical control board for Home Assistant" / "home DJ mixer for music + lights") so first-time readers immediately understand what Spectra L/S is.

- README plain-language rewrite for non-technical readers: replaced implementation-heavy top-of-page status/roadmap copy with user-first messaging focused on what Spectra L/S is, what it does today, who it is for, and what to expect during beta.

- Integration-only residue cleanup: removed remaining legacy/fallback wording from active validation and architecture docs, and switched the full-stack tester guidance to component-contract-only messaging/sources.

- Integration-first baseline reset: repository documentation and roadmap surfaces were reset to a clean current-state baseline focused on the active `custom_components/spectra_ls` implementation lane and current runtime consumers.
- Runtime observer alignment: hardware status refresh automation now consumes integration now-playing entities (`sensor.component_now_playing_*`) instead of deprecated `sensor.ma_active_*` trigger surfaces.
- Runtime artifact cleanup: removed retired runtime archive/stub paths that were no longer part of active execution.
- Documentation baseline refresh: replaced historical migration narrative with concise active-state contracts and forward-only execution guidance.

### Track disposition

- Runtime track: implemented
- Integration track: implemented

### Version parity review

- Runtime: updated
- Integration: updated
