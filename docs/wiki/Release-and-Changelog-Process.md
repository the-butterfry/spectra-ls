<!-- Description: Release-note and changelog discipline for Spectra L/S behavior, contract, and governance changes. -->
<!-- Version: 2026.04.22.1 -->
<!-- Last updated: 2026-04-22 -->

# Release and Changelog Process

This is the minimum release hygiene for every slice.

## Changelog is mandatory

For functional behavior, contract, architecture, workflow, or governance changes:

1. Update `docs/CHANGELOG.md` in the same change set.
2. Include affected file paths in the entry.
3. Keep entries concise and impact-oriented.

## Required parity set

For roadmap/process/contract changes, update these together:

1. `docs/CHANGELOG.md`
2. `docs/roadmap/v-next-NOTES.md`
3. `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`
4. `README.md` (or explicit no-material-change note)

## Release hygiene recommendations

- Use `changelog:*` labels on PRs for future automation.
- Keep PR scope narrow to improve release-note quality.
- Include risk and rollback notes in PR descriptions.

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

- Main changelog: `docs/CHANGELOG.md`
- Runtime roadmap ledger: `docs/roadmap/v-next-NOTES.md`
- Component roadmap ledger: `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`
- Contributor process: `CONTRIBUTING.md`
