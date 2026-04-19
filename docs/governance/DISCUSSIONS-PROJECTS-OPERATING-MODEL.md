<!-- Description: Operating model for GitHub Discussions and Projects mapped to Spectra L/S scope paths and delivery workflow. -->
<!-- Version: 2026.04.19.1 -->
<!-- Last updated: 2026-04-19 -->

# Discussions and Projects Operating Model

This document defines how Spectra L/S uses GitHub Discussions and Projects to manage intake, planning, and execution across all scope paths.

## Goals

- Keep ideas and questions discoverable without polluting issue backlog.
- Keep implementation work scoped, triaged, and traceable.
- Maintain consistent visibility across runtime, control-hub, firmware, docs, and tooling tracks.

## One-time enablement steps

### Enable Discussions

1. GitHub repository → `Settings` → `General`.
2. In `Features`, enable **Discussions**.
3. Create categories:
   - `Ideas`
   - `Q&A`
   - `RFC / Architecture`
   - `Show and Tell`
   - `Announcements`

### Create the Project board

1. GitHub repository/org → `Projects` → `New project`.
2. Create table/board named **Spectra Program Board**.
3. Add fields:
   - `Status` (single select): Backlog, Planned, In Progress, In Review, Blocked, Done
   - `Area` (single select): ESPHome Runtime, MA Control Hub, RP2040, Custom Component, Docs-Governance, Tooling
   - `Track` (single select): Runtime, Custom Component, Shared Contract, Docs-Governance
   - `Priority` (single select): P0, P1, P2, P3
   - `Risk` (single select): Low, Medium, High
   - `Target` (single select): v-next, maintenance, hotfix
4. Add automation (recommended):
   - New issues auto-add to project.
   - Merged PRs move linked items to `Done`.

## Discussions model

### Recommended categories

- `Ideas`
- `Q&A`
- `RFC / Architecture`
- `Show and Tell`
- `Announcements`

### Lifecycle

1. Start in Discussions for ideation and ambiguity reduction.
2. Capture maintainer decision summary in-thread.
3. Convert to Issue when implementation boundaries are clear.
4. Link originating Discussion in the Issue body.

## Projects model

### Board recommendation

Create one board: **Spectra Program Board**.

### Required fields

- `Status`: Backlog / Planned / In Progress / In Review / Blocked / Done
- `Area`: ESPHome Runtime / MA Control Hub / RP2040 / Custom Component / Docs-Governance / Tooling
- `Track`: Runtime / Custom Component / Shared Contract / Docs-Governance
- `Priority`: P0 / P1 / P2 / P3
- `Risk`: Low / Medium / High
- `Target`: v-next / maintenance / hotfix

### Scope-path mapping

| Scope path | Area field value | Required labels |
| --- | --- | --- |
| `esphome/spectra_ls_system/**` | ESPHome Runtime | `area:esphome-runtime` + `priority:*` + `type:*` |
| `packages/**` | MA Control Hub | `area:ma-control-hub` + `priority:*` + `type:*` |
| `esphome/circuitpy/**` + live `CIRCUITPY/` | RP2040 | `area:rp2040` + `priority:*` + `type:*` |
| `custom_components/spectra_ls/**` | Custom Component | `area:custom-component` + `priority:*` + `type:*` |
| `docs/**`, `.github/**` | Docs-Governance | `area:docs` or `area:governance` + `type:*` |
| `bin/**` | Tooling | `area:tooling` + `priority:*` + `type:*` |

## Intake and triage policy

- New reproducible defects must use Issue forms.
- Feature proposals should start in Discussions and become Issues after shaping.
- Every active Issue should be added to Project with `Area`, `Status`, and `Priority` set.
- PRs must reference an Issue (or include rationale when no issue is used).

## Review and completion policy

- Use `.github/pull_request_template.md` for all PRs.
- Include verification evidence and docs parity statements.
- On merge, set project status to `Done` and ensure `docs/CHANGELOG.md` entry exists when required.

## References

- `CONTRIBUTING.md`
- `docs/governance/GITHUB-MASTERWORK-BLUEPRINT.md`
- `docs/governance/LABEL-TAXONOMY.md`
- `docs/CHANGELOG.md`
