<!-- Description: GitHub Discussions and Projects operating workflow mapped to Spectra L/S scope paths. -->
<!-- Version: 2026.04.19.2 -->
<!-- Last updated: 2026-04-19 -->

# Discussions and Projects Workflow

## Why use both

- **Discussions**: idea shaping, Q&A, architecture tradeoff threads, early UX feedback.
- **Issues/PRs**: execution artifacts with reproducible scope and verification evidence.
- **Projects**: portfolio-level tracking across runtime, docs, tooling, and migration paths.

## Recommended Discussions categories

- `Ideas`
- `Q&A`
- `Show and Tell`
- `RFC / Architecture`
- `Announcements`

Use Discussions for exploration and consensus; promote to Issues when a bounded implementation task exists.

## Recommended Project board model

Single org/repo project titled: **Spectra Program Board**

### Core fields

- `Status`: Backlog, Planned, In Progress, In Review, Blocked, Done
- `Area`: ESPHome Runtime, MA Control Hub, RP2040, Custom Component, Docs/Governance, Tooling
- `Track`: Runtime, Custom Component, Shared Contract, Docs/Governance
- `Priority`: P0, P1, P2, P3
- `Risk`: Low, Medium, High
- `Target`: v-next, maintenance, hotfix

## Scope-path routing matrix

| Scope path | Project Area | Typical issue label set |
| --- | --- | --- |
| `esphome/spectra_ls_system/**` | ESPHome Runtime | `type:*` + `area:esphome-runtime` + `priority:*` |
| `packages/**` | MA Control Hub | `type:*` + `area:ma-control-hub` + `priority:*` |
| `esphome/circuitpy/**` + live `CIRCUITPY/` | RP2040 | `type:*` + `area:rp2040` + `priority:*` |
| `custom_components/spectra_ls/**` | Custom Component | `type:*` + `area:custom-component` + `priority:*` |
| `docs/**`, `.github/**` | Docs/Governance | `type:documentation` or `type:governance` + `area:docs`/`area:governance` |
| `bin/**` | Tooling | `type:*` + `area:tooling` |

## Intake flow (mature OSS style)

1. Idea/question starts in Discussions.
2. Maintainer adds summary + decision note.
3. Convert to Issue when implementation is scoped.
4. Add Issue to Project with Area/Track/Priority/Risk.
5. Execute via PR with checklist + verification evidence.

## Definition of ready (Issue)

- Problem statement is clear and user-impactful.
- Repro or acceptance criteria are concrete.
- Scope boundaries are explicit (what is in/out).
- Area/priority labels are present.
- Project fields are populated (`Status`, `Area`, `Track`, `Priority`).

## Definition of done (Issue/PR)

- Implementation is merged with verification evidence.
- Changelog/docs/wiki parity is updated as required.
- Any contract/routing implications are documented.
- Project item moved to `Done`.

## Practical board hygiene

- Keep `In Progress` limited to active owner capacity.
- Move stale items back to `Planned` or `Blocked` with reason.
- Prefer one issue per logical slice to keep rollback clean.
