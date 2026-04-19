<!-- Description: Contributor guide for Spectra L/S development, scope, workflow, and quality expectations. -->
<!-- Version: 2026.04.19.1 -->
<!-- Last updated: 2026-04-19 -->

# Contributing to Spectra L/S

Thank you for contributing.

## Before opening work

1. Read `docs/developer/DEVELOPER-INSTRUCTIONS.md`.
2. Review active direction in `docs/roadmap/v-next-NOTES.md`.
3. Confirm docs parity expectations in `.github/copilot-instructions.md`.

## Scope and branch model

- Active development branch: `main`
- Stabilized branch: `menu-only`
- Shared-contract changes must follow `.github/SHARED-CONTRACT-CHECKLIST.md`.

## Contribution standards

- Keep PRs focused and small.
- One logical change set per PR.
- Root-cause fixes over symptom patches.
- No secrets or environment-local artifacts.

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

## Community expectations

All contributors are expected to follow `CODE_OF_CONDUCT.md`.
