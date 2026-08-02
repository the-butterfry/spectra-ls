<!-- Description: Repository changelog for Spectra L/S integration-first development. -->
<!-- Version: 2026.08.01.5 -->
<!-- Last updated: 2026-08-01 -->

# Changelog

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
