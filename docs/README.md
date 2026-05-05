<!-- Description: Documentation index for Spectra L/S technical, onboarding, roadmap, and operations artifacts. -->
<!-- Version: 2026.05.05.8 -->
<!-- Last updated: 2026-05-05 -->

# Spectra L/S Documentation Index

Use this folder as the source of truth for project documentation and notes.

## Start here

- Developer onboarding: `docs/developer/DEVELOPER-INSTRUCTIONS.md`
- Changelog: `docs/CHANGELOG.md`
- GitHub governance blueprint: `docs/governance/GITHUB-MASTERWORK-BLUEPRINT.md`
- Active ESPHome runtime path on `main`: `esphome/spectra_ls_system/**` (entrypoint `esphome/spectra_ls_system.yaml`).

Legacy-seal status (current):

- Runtime path (`packages/` + `esphome/`) is sealed as compatibility + rollback baseline.
- Custom integration path (`custom_components/spectra_ls/`) is primary for net-new control-plane/feature growth.

If you are new: read `README.md` first, then this file, then `docs/roadmap/v-next-NOTES.md`.

## Roadmap and program governance

- `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`
- `docs/roadmap/v-next-NOTES.md`
- `docs/program/PARALLEL-PROGRAM-PLAYBOOK.md`
- `docs/program/CA-S01D-PROOF-PACKET-CHECKLIST.md`
- `docs/program/CA-S02B-RESOLVER-REPLAY-CHECKLIST.md`
- `docs/program/CA-S03-CONSUMER-PROJECTION-CUTOVER-CHECKLIST.md`
- `docs/program/CA-S04-RUNTIME-WRITE-LANE-RETIREMENT-CHECKLIST.md`
- `docs/program/CA-S05-ESP-FALLBACK-LISTENER-SOAK-CHECKLIST.md`
- `docs/program/CA-S06-RUNTIME-WRITE-HELPER-RETIREMENT-WAVE2-CHECKLIST.md`
- `docs/program/CA-S07-LEGACY-DIAGNOSTICS-TEMPLATE-FALLBACK-CLEANUP-CHECKLIST.md`
- `docs/program/CA-S08-DOMAIN-CLOSEOUT-ROLLBACK-SEAL-CHECKLIST.md`

## Architecture

- Runtime architecture: `docs/architecture/CODEBASE-RUNTIME-ARCHITECTURE.md`
- Control hub architecture: `docs/architecture/CONTROL-HUB-ARCHITECTURE.md`

## Testing and diagnostics

- Dev Tools templates: `docs/testing/DEVTOOLS-TEMPLATES.local.md`
- CA-S04 runtime write-lane validation template: `docs/testing/raw/ca_s04_runtime_write_lane_retirement_validation.jinja`
- CA-S05 fallback-listener soak validation template: `docs/testing/raw/ca_s05_esp_fallback_listener_soak_validation.jinja`
- CA-S06 runtime write/helper wave-2 validation template: `docs/testing/raw/ca_s06_runtime_write_helper_retirement_wave2_validation.jinja`
- CA-S07 diagnostics/template fallback cleanup validation template: `docs/testing/raw/ca_s07_legacy_diagnostics_template_fallback_cleanup_validation.jinja`
- CA-S08 domain closeout + rollback-safe seal validation template: `docs/testing/raw/ca_s08_domain_closeout_rollback_seal_validation.jinja`

## Cleanup and maintenance

- Dead-path cleanup matrix: `docs/cleanup/DEAD-PATHS-CLEANUP.md`

## Notes

- Spectra system notes: `docs/notes/NOTES-control-board-2.md`, `docs/notes/NOTES-wiim-api.md`
- RP2040 notes: `docs/circuitpy/RP-LEGEND.md`

## Hardware wiring and layout protocols

- Wiring/layout protocol (detailed): `docs/hardware/WIRING-LAYOUT-PROTOCOL.md`
- RP2040 legend (summary + component links): `docs/circuitpy/RP-LEGEND.md`

## Wiki-ready pages (optional automation)

- Wiki source pages: `docs/wiki/`
- Auto-sync workflow: `.github/workflows/wiki-sync.yml`
- Auto-sync script (fallback): `bin/sync_docs_to_wiki.sh`
- Wiki setup runbook: `docs/wiki/README.md`
- Welcome + bug workflow: `docs/wiki/Welcome-README-and-Bug-Workflow.md`
- User setup/deploy/integration guide: `docs/wiki/User-Setup-Deploy-and-HA-Integration.md`
- Wiki content policy: `docs/wiki/Wiki-Content-Scope-Policy.md`
- Custom component setup roadmap stub: `docs/wiki/Custom-Component-Setup-Roadmap-Stub.md`

## Setup and feature references

- Setup placeholders: `docs/setup/SPECTRA-HA-CONFIG-PLACEHOLDERS.md`
- Feature notes: `docs/features/dst_tuya_ac.FEATURES.md`
- Deferred H1 report/log/heal scaffold: `docs/features/H1-report-log-heal-scaffold.md`

## Repository governance

- Contribution guide: `CONTRIBUTING.md`
- Code of conduct: `CODE_OF_CONDUCT.md`
- Security policy: `SECURITY.md`
- Ownership map: `CODEOWNERS`
- Issue templates: `.github/ISSUE_TEMPLATE/`
- PR template: `.github/pull_request_template.md`
- Label taxonomy: `docs/governance/LABEL-TAXONOMY.md`
- Discussions + Projects model: `docs/governance/DISCUSSIONS-PROJECTS-OPERATING-MODEL.md`
