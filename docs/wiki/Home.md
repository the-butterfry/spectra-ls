<!-- Description: Wiki home page for Spectra L/S operations, architecture, contribution flow, and runbooks. -->
<!-- Version: 2026.08.01.3 -->
<!-- Last updated: 2026-08-01 -->

# Spectra L/S Wiki

Spectra L/S is a tactile control surface for Home Assistant. This wiki is the operator-and-contributor layer: setup, troubleshooting, workflow, and architecture orientation.

If you only read one section on this page, read the next one.

## Where should I start?

- **I want to install it now** → [Install on Your Own Home Assistant](Install-on-Your-Own-HA)
- **I already installed it but behavior is weird** → [Operations Runbooks](Operations-Runbooks)
- **I need to file a solid bug** → [Welcome, README, and Bug Workflow](Welcome-README-and-Bug-Workflow)
- **I’m contributing code/docs** → [Getting Started](Getting-Started) then [Contributing Workflow](Contributing-Workflow)

## Core pages

- [Getting Started](Getting-Started)
- [Install on Your Own Home Assistant](Install-on-Your-Own-HA)
- [User Setup, Deploy, and HA Integration](User-Setup-Deploy-and-HA-Integration)
- [Operations Runbooks](Operations-Runbooks)
- [Complete Operator Runbook](Complete-Operator-Runbook)
- [Welcome, README, and Bug Workflow](Welcome-README-and-Bug-Workflow)
- [System Architecture](System-Architecture)

## Project truth sources

- Docs index: [`docs/README.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/README.md)
- Changelog: [`docs/CHANGELOG.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/CHANGELOG.md)
- Runtime roadmap ledger: [`docs/roadmap/v-next-NOTES.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/roadmap/v-next-NOTES.md)
- Component roadmap ledger: [`docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md)

## Quick context (so language in other pages makes sense)

- Runtime path (`packages/` + `esphome/`) is the compatibility/rollback baseline.
- `custom_components/spectra_ls/` is the primary lane for net-new behavior.
- Good fixes stay discovery-first, reproducible, and evidence-backed.

## Wiki publishing notes

- Source pages live in [`docs/wiki/`](https://github.com/the-butterfry/spectra-ls/tree/main/docs/wiki)
- Sync automation: [`.github/workflows/wiki-sync.yml`](https://github.com/the-butterfry/spectra-ls/blob/main/.github/workflows/wiki-sync.yml)
- Setup/troubleshooting for sync: [Wiki Source + Sync](README)
