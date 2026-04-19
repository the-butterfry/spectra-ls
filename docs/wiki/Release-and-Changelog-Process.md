<!-- Description: Release-note and changelog discipline for Spectra L/S behavior, contract, and governance changes. -->
<!-- Version: 2026.04.19.1 -->
<!-- Last updated: 2026-04-19 -->

# Release and Changelog Process

## Changelog is mandatory

For functional behavior, contract, architecture, workflow, or governance changes:

1. Update `docs/CHANGELOG.md` in the same change set.
2. Include affected file paths in the entry.
3. Keep entries concise and impact-oriented.

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
