<!-- Description: Contributor guide for Spectra L/S development, scope, workflow, and quality expectations. -->
<!-- Version: 2026.04.21.4 -->
<!-- Last updated: 2026-04-21 -->

# Contributing to Spectra L/S

Thank you for contributing.

## Before opening work

1. Read `docs/developer/DEVELOPER-INSTRUCTIONS.md`.
2. Review active direction in `docs/roadmap/v-next-NOTES.md`.
3. Confirm docs parity expectations in `.github/copilot-instructions.md`.

## Scope and branch model

- Active development branch: `main`
- `control-py` is archived legacy exploration history and is not a development/run target on `main`.
- Shared-contract changes must follow `.github/SHARED-CONTRACT-CHECKLIST.md`.

## Contribution standards

- Keep PRs focused and small.
- One logical change set per PR.
- Root-cause fixes over symptom patches.
- No secrets or environment-local artifacts.
- Respect migration posture: legacy runtime path is sealed for compatibility/rollback; net-new ownership/features should target `custom_components/spectra_ls` unless a bounded legacy exception is explicitly documented.

## Required for functional changes

- Update `docs/CHANGELOG.md` before or with code changes.
- Update affected docs/contracts in same change set.
- Provide verification evidence (build/tests/templates) in PR description.

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
