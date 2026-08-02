<!-- Description: Practical contribution lifecycle from issue intake to verified merge in Spectra L/S. -->
<!-- Version: 2026.08.01.29 -->
<!-- Last updated: 2026-08-01 -->

# Contributing Workflow

Use this for every change. Keep it small, testable, and reviewable.

## Default flow

1. Open/confirm issue scope.
2. Label scope (`type`, `area`, `priority`) and project status.
3. Implement one logical slice.
4. Validate (build/tests/diagnostics relevant to change).
5. Update required docs parity.
6. Open PR with evidence.
7. Merge only when checklist and parity are complete.

## Non-negotiables

- Keep fixes root-cause and reversible.
- Keep runtime/component two-track disposition explicit.
- Include verification evidence, not just claims.
- Never commit secrets or local-only host/token data.

## Fast-start PR checklist

1. Link the issue.
2. Fill PR template required fields.
3. Attach evidence (build/test/diagnostics/log snippets).
4. Set explicit runtime/component disposition.
5. Confirm docs parity files were updated.

## Scheduler/metadata-bridge slices

For behavior-visible scheduler/metadata-bridge work, keep intake and PR owner/lane metadata aligned.

Minimum reconciliation in PR:

- linked issue ID
- intake lane + owner
- PR lane + owner
- reclassification rationale when mismatched

## Component-first requirement

- Net-new behavior belongs in `custom_components/spectra_ls` by default.
- Runtime touches require bounded rationale and rollback posture.
- Mismatch between declared scope and changed files is merge-blocking unless exception evidence is explicit.

## Mandatory parity set

For roadmap/process/contract changes, update together:

1. [`docs/CHANGELOG.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/CHANGELOG.md)
2. [`docs/roadmap/v-next-NOTES.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/roadmap/v-next-NOTES.md)
3. [`docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md)
4. [`README.md`](https://github.com/the-butterfry/spectra-ls/blob/main/README.md) (or explicit no-material-change note)

If one is missing, the slice is not done.

## Branch/track posture

- Runtime path is sealed compatibility baseline.
- Custom component path is primary growth lane.
- `control-py` and `menu-only` are legacy contexts for `main` guidance.

## Required references

- [`CONTRIBUTING.md`](https://github.com/the-butterfry/spectra-ls/blob/main/CONTRIBUTING.md)
- [`.github/pull_request_template.md`](https://github.com/the-butterfry/spectra-ls/blob/main/.github/pull_request_template.md)
- [`docs/CHANGELOG.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/CHANGELOG.md)
- [`docs/roadmap/v-next-NOTES.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/roadmap/v-next-NOTES.md)
- [`docs/notes/NOTES-engineering-rigor.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/notes/NOTES-engineering-rigor.md)

## Reviewer expectations

- Clear problem statement and scope boundary
- Explicit risk and rollback notes
- Verification evidence for impacted paths
- No secrets or machine-local artifacts

## Before you push

- Is the change small and reversible?
- Are both runtime/component tracks dispositioned (implemented/shimmed/deferred)?
- Are changelog + roadmaps updated?
- Are diagnostics clean for touched files?
