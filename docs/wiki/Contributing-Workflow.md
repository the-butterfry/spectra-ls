<!-- Description: Practical contribution lifecycle from issue intake to verified merge in Spectra L/S. -->
<!-- Version: 2026.04.22.4 -->
<!-- Last updated: 2026-04-22 -->

# Contributing Workflow

Use this as the default path for any change.

## End-to-end lifecycle

1. Intake via Issue form (or Discussion promotion).
2. Triage with labels (`type`, `area`, `priority`).
3. Add item to Project board with Area/Track/Status.
4. Implement in a focused branch/slice.
5. Validate with required evidence and diagnostics.
6. Update docs parity in the same change set.
7. Open PR using template checklist.
8. Merge only after ownership + parity review.

## Mandatory parity in each slice

For roadmap/process/contract changes, update together:

1. [`docs/CHANGELOG.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/CHANGELOG.md)
2. [`docs/roadmap/v-next-NOTES.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/roadmap/v-next-NOTES.md)
3. [`docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md)
4. [`README.md`](https://github.com/the-butterfry/spectra-ls/blob/main/README.md) (or explicit no-material-change note)

If one is missing, the slice is not done.

## Branch and track posture

- Runtime path is sealed compatibility baseline.
- Custom component path is primary growth lane.
- `control-py` and `menu-only` are legacy contexts for `main` guidance.

## Required references

- [`CONTRIBUTING.md`](https://github.com/the-butterfry/spectra-ls/blob/main/CONTRIBUTING.md)
- [`.github/pull_request_template.md`](https://github.com/the-butterfry/spectra-ls/blob/main/.github/pull_request_template.md)
- [`docs/CHANGELOG.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/CHANGELOG.md)
- [`docs/roadmap/v-next-NOTES.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/roadmap/v-next-NOTES.md)

## Review expectations

- Clear problem statement and scope boundary
- Explicit risk and rollback notes
- Verification evidence for impacted paths
- No secrets or machine-local artifacts

## Fast quality checklist before commit

- Is the change small and reversible?
- Are both runtime/component tracks dispositioned (implemented/shimmed/deferred)?
- Are changelog + roadmaps updated?
- Are diagnostics clean for touched files?
