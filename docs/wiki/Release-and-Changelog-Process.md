<!-- Description: Release-note and changelog discipline for Spectra L/S behavior, contract, and governance changes. -->
<!-- Version: 2026.04.29.4 -->
<!-- Last updated: 2026-04-29 -->

# Release and Changelog Process

This is the minimum release hygiene for every slice.

## Changelog is mandatory

For functional behavior, contract, architecture, workflow, or governance changes:

1. Update [`docs/CHANGELOG.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/CHANGELOG.md) in the same change set.
2. Include affected file paths in the entry.
3. Keep entries concise and impact-oriented.

## Required parity set

For roadmap/process/contract changes, update these together:

1. [`docs/CHANGELOG.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/CHANGELOG.md)
2. [`docs/roadmap/v-next-NOTES.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/roadmap/v-next-NOTES.md)
3. [`docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md)
4. [`README.md`](https://github.com/the-butterfry/spectra-ls/blob/main/README.md) (or explicit no-material-change note)

## Release hygiene recommendations

- Use `changelog:*` labels on PRs for future automation.
- Keep PR scope narrow to improve release-note quality.
- Include risk and rollback notes in PR descriptions.

HACS publication cadence (recommended):

- Keep day-to-day commits on `main` without creating a HACS release each time.
- Publish to HACS when you intentionally cut a release tag with stable release notes.
- Treat release tags as operator-facing checkpoints, not commit-frequency mirrors.

## Suggested changelog grouping

- Feature / enhancement
- Bug fix
- Docs / governance
- Breaking / migration notes
- Security

## Definition of done

- Changes merged with docs parity complete.
- Verification evidence present.
- Changelog entry accurately reflects user/operator impact.

## Linked references

- Main changelog: [`docs/CHANGELOG.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/CHANGELOG.md)
- Runtime roadmap ledger: [`docs/roadmap/v-next-NOTES.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/roadmap/v-next-NOTES.md)
- Component roadmap ledger: [`docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md)
- Contributor process: [`CONTRIBUTING.md`](https://github.com/the-butterfry/spectra-ls/blob/main/CONTRIBUTING.md)
