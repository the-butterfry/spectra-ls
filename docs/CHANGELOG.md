<!-- Description: Repository changelog for Spectra L/S integration-first development. -->
<!-- Version: 2026.08.01.3 -->
<!-- Last updated: 2026-08-01 -->

# Changelog

## 2026-08-01

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
