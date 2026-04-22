<!-- Description: Scope-path contracts and ownership map for Spectra L/S implementation and operations. -->
<!-- Version: 2026.04.22.1 -->
<!-- Last updated: 2026-04-22 -->

# Control Contracts and Scope Paths

Use this page as the routing map for work intake, review ownership, and project tracking.

## Scope-path map

| Scope path | Primary concern | Suggested labels |
| --- | --- | --- |
| `esphome/spectra_ls_system/**` | Runtime behavior, firmware contracts, menu/control UX | `area:esphome-runtime` |
| `packages/**` | Home Assistant control-hub contracts and automations | `area:ma-control-hub` |
| `esphome/circuitpy/**` + live `CIRCUITPY/` | RP2040 input protocol and mirror parity | `area:rp2040` |
| `custom_components/spectra_ls/**` | New control-plane architecture/migration | `area:custom-component` |
| `docs/**`, `.github/**` | Docs/governance/process operations | `area:docs`, `area:governance` |
| `bin/**` | Tooling and local operator automation | `area:tooling` |

## Shared contract policy

- For shared contracts, maintain branch parity or explicitly log divergence in `docs/CHANGELOG.md`.
- Complete `.github/SHARED-CONTRACT-CHECKLIST.md` before shared-contract merges.

## Verification references

- Build gate and deployment gate policies: `.github/copilot-instructions.md`
- Contribution workflow: `CONTRIBUTING.md`

## Linked reference map

- Runtime architecture: `docs/architecture/CODEBASE-RUNTIME-ARCHITECTURE.md`
- Control-hub architecture: `docs/architecture/CONTROL-HUB-ARCHITECTURE.md`
- Parallel program execution: `docs/program/PARALLEL-PROGRAM-PLAYBOOK.md`
- Runtime roadmap ledger: `docs/roadmap/v-next-NOTES.md`
- Component roadmap ledger: `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`
- Shared contract checklist: `.github/SHARED-CONTRACT-CHECKLIST.md`
