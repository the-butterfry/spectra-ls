<!-- Description: Scope-path contracts and ownership map for Spectra L/S implementation and operations. -->
<!-- Version: 2026.08.01.3 -->
<!-- Last updated: 2026-08-01 -->

# Control Contracts and Scope Paths

Use this page to route work fast and avoid owner confusion.

## Scope map

| Scope path | Owner concern | Suggested labels |
| --- | --- | --- |
| `esphome/spectra_ls_system/**` | Runtime behavior, firmware contracts, menu/control UX | `area:esphome-runtime` |
| `packages/**` | Home Assistant control-hub contracts and automations | `area:ma-control-hub` |
| `esphome/circuitpy/**` + live `CIRCUITPY/` | RP2040 input protocol and mirror parity | `area:rp2040` |
| `custom_components/spectra_ls/**` | Primary control-plane behavior and migration ownership | `area:custom-component` |
| `docs/**`, `.github/**` | Docs/governance/process operations | `area:docs`, `area:governance` |
| `bin/**` | Tooling and local operator automation | `area:tooling` |

## Shared-contract policy

- Keep parity or log explicit divergence in [`docs/CHANGELOG.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/CHANGELOG.md).
- Complete [`.github/SHARED-CONTRACT-CHECKLIST.md`](https://github.com/the-butterfry/spectra-ls/blob/main/.github/SHARED-CONTRACT-CHECKLIST.md) before merge.

## Quick review checklist

- [ ] Change is in the correct scope path
- [ ] Labels match the scope path
- [ ] Changelog includes contract-impact summary (if any)
- [ ] Runtime/component two-track disposition is explicit
- [ ] Shared-contract checklist is complete when applicable

## Verification references

- Build gate and deployment gate policies: [`.github/copilot-instructions.md`](https://github.com/the-butterfry/spectra-ls/blob/main/.github/copilot-instructions.md)
- Contribution workflow: [`CONTRIBUTING.md`](https://github.com/the-butterfry/spectra-ls/blob/main/CONTRIBUTING.md)

## Linked reference map

- Runtime architecture: [`docs/architecture/CODEBASE-RUNTIME-ARCHITECTURE.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/architecture/CODEBASE-RUNTIME-ARCHITECTURE.md)
- Control-hub architecture: [`docs/architecture/CONTROL-HUB-ARCHITECTURE.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/architecture/CONTROL-HUB-ARCHITECTURE.md)
- Parallel program execution: [`docs/program/PARALLEL-PROGRAM-PLAYBOOK.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/program/PARALLEL-PROGRAM-PLAYBOOK.md)
- Runtime roadmap ledger: [`docs/roadmap/v-next-NOTES.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/roadmap/v-next-NOTES.md)
- Component roadmap ledger: [`docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md)
- Shared contract checklist: [`.github/SHARED-CONTRACT-CHECKLIST.md`](https://github.com/the-butterfry/spectra-ls/blob/main/.github/SHARED-CONTRACT-CHECKLIST.md)
