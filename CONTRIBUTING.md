<!-- Description: Contributor workflow guide for Spectra L/S with clear branch boundaries, quality gates, and PR expectations. -->
<!-- Version: 2026.04.21.6 -->
<!-- Last updated: 2026-04-21 -->

# Contributing to Spectra L/S

Thanks for helping build Spectra.

This guide tells you where to work, how to scope changes, and what proof is required before merge.

## Before opening work

1. Read `docs/developer/DEVELOPER-INSTRUCTIONS.md`.
2. Review active direction in `docs/roadmap/v-next-NOTES.md`.
3. Confirm docs parity expectations in `.github/copilot-instructions.md`.

## Scope and branch model

- Active development branch: `main`
- `menu-only` is legacy/stabilized historical branch context, not an active implementation lane.
- `control-py` is archived exploration history, not an active implementation lane.
- Shared-contract changes must follow `.github/SHARED-CONTRACT-CHECKLIST.md`.

## Contribution standards

- Keep PRs focused: one logical change set per PR.
- Prefer root-cause fixes over symptom patches.
- Do not commit secrets or environment-local artifacts.
- Respect migration posture:
  - runtime (`packages/` + `esphome/`) is sealed for compatibility/rollback,
  - net-new ownership/features belong in `custom_components/spectra_ls`,
  - legacy expansion requires an explicit bounded exception with evidence.

## Required for functional changes

- Update `docs/CHANGELOG.md` before or with code changes.
- Update affected docs/contracts in the same change set.
- Include verification evidence in the PR description (build/tests/templates as applicable).

## Pull request checklist (minimum)

- Problem and scope are clearly stated.
- Risk and rollback notes are included.
- Verification evidence is included.
- Documentation impact is addressed.

Use `.github/pull_request_template.md` when opening a PR.

## Reporting bugs and requesting features

- Use the issue forms in `.github/ISSUE_TEMPLATE/`.
- Feature requests should include user impact and proposed behavior.
- Use GitHub Discussions for ideation/Q&A before opening scoped implementation issues.

## Discussions and Projects usage

- Discussions are the front door for Q&A, ideation, and RFC-style architecture threads.
- Issues/PRs are execution artifacts with testable scope.
- Add scoped issues to the repository Project board and set Area/Track/Priority fields.
- Scope-path mapping and governance details: `docs/governance/DISCUSSIONS-PROJECTS-OPERATING-MODEL.md`.

## Community expectations

All contributors are expected to follow `CODE_OF_CONDUCT.md`.
