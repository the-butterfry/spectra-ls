<!-- Description: Documentation index for Spectra L/S technical, onboarding, roadmap, and operations artifacts. -->
<!-- Version: 2026.04.21.2 -->
<!-- Last updated: 2026-04-21 -->

# Spectra L/S Documentation Index

Use this folder as the single location for project documentation and notes.

## Start here

- Developer onboarding: `docs/developer/DEVELOPER-INSTRUCTIONS.md`
- Changelog: `docs/CHANGELOG.md`
- GitHub governance blueprint: `docs/governance/GITHUB-MASTERWORK-BLUEPRINT.md`
- Active ESPHome runtime path on `main`: `esphome/spectra_ls_system/**` (entrypoint `esphome/spectra_ls_system.yaml`); `esphome/control-py/**` is the stabilized alternate line unless explicitly targeted.

## Roadmap and program governance

- `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`
- `docs/roadmap/v-next-NOTES.md`
- `docs/program/PARALLEL-PROGRAM-PLAYBOOK.md`

## Architecture

- Runtime architecture: `docs/architecture/CODEBASE-RUNTIME-ARCHITECTURE.md`
- Control hub architecture: `docs/architecture/CONTROL-HUB-ARCHITECTURE.md`

## Testing and diagnostics

- Dev Tools templates: `docs/testing/DEVTOOLS-TEMPLATES.local.md`

## Cleanup and maintenance

- Dead-path cleanup matrix: `docs/cleanup/DEAD-PATHS-CLEANUP.md`

## Notes

- Spectra system notes: `docs/notes/NOTES-control-board-2.md`, `docs/notes/NOTES-wiim-api.md`
- control-py notes: `docs/control-py/NOTES-control-board-2.md`, `docs/control-py/NOTES-wiim-api.md`, `docs/control-py/v-next-NOTES.md`
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
- User setup/deploy/integration guide (stub): `docs/wiki/User-Setup-Deploy-and-HA-Integration.md`
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
