<!-- Description: Practical contribution lifecycle from issue intake to verified merge in Spectra L/S. -->
<!-- Version: 2026.05.02.28 -->
<!-- Last updated: 2026-05-02 -->

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

## Lean-team mode (current)

With two active contributors, workflow currently uses a lean execution profile:

- Lean v2 one-screen core packet fields are required every PR.
- Core packet includes a simple status line (`complete|incomplete`) for fast triage.
- Core packet includes a coherence line (`coherent|needs-fix`) for fast consistency triage.
- Core packet includes risk level (`low|medium|high`) for reviewer depth triage.
- Core packet includes follow-up signals (`yes|no` + tracking reference or `N/A`) for post-merge planning clarity.
- Core packet includes validation-confidence signal (`high|medium|low`) for uncertainty visibility.
- Core packet includes rollback-posture signal (`safe|needs-attention`) for reversibility triage.
- Core packet includes handoff-note reference (`N/A` if none) for reviewer/operator continuity.
- Core packet includes test-scope signal (`full|targeted|minimal`) for verification breadth visibility.
- Core packet includes contract-delta signal (`none|minor|major`) for contract-impact visibility.
- Core packet includes communication-note reference (`N/A` if none) for operational follow-through traceability.
- Core packet should identify a single owner for completion accountability.
- Core packet should include blocker verdict (`ready|blocked`) for merge-readiness interpretation.
- Extended governance sections are completed only when the PR-template scope trigger matrix marks them in scope.
- Quick scope toggles (`yes|no`) should be filled before optional sections to speed disposition.
- Scope summary line (`A`, `B`, `A+B`, or `none`) should be filled for reviewer scan speed.
- Optional-section completion summary (`A done`, `B done`, `A+B done`, or `none`) should be filled for closure scan speed.
- Evidence artifact reference line (`URL/path` or `N/A`) should be filled for proof lookup speed.
- Declaration mismatch and exception evidence blockers remain strict.
- Minimal evidence block should include evidence capture time (`UTC`).
- Minimal evidence block should include freshness hint (`fresh|stale`).
- Minimal evidence block should include blocker reason summary (`N/A` when ready).
- Reviewer fast-path should include attestation timestamp (`UTC`).
- Documentation parity may be batched across up to 4 micro-slices, with changelog-first retained.
- Use PR-template quick-fill snippets to fill `ci_enforced` / `manual_enforced_now` packets consistently.
- Leave optional sections as `N/A (not in scope)` by default; only replace when scope triggers them.
- Use reviewer fast-path attestation for compact merge-readiness confirmation.

### Two-person fast-start checklist

1. Add linked issue ID.
2. Choose declaration mode (`manual_enforced_now` or `ci_enforced`).
3. Record declaration-vs-diff blocker decision, set core packet status (`complete|incomplete`), and set core packet owner.
4. Set core packet coherence (`coherent|needs-fix`) and fill evidence artifact reference (`URL/path` or `N/A`).
5. Set risk/follow-up packet lines (`risk`, `follow-up needed`, `follow-up tracking reference`).
6. Set confidence/reversibility/handoff packet lines (`validation confidence`, `rollback posture`, `handoff note reference`).
7. Set scope/delta/communication packet lines (`test scope`, `contract delta`, `communication note reference`).
8. Fill the matching quick-fill snippet.
9. Set quick scope toggles (`yes|no`), then complete optional sections only when triggered; otherwise mark `N/A (not in scope)`.
10. Add evidence capture timestamp (`UTC`) plus freshness hint (`fresh|stale`) and blocker reason summary (`N/A` when ready) in minimal evidence.
11. Add reviewer attestation timestamp (`UTC`) in fast-path section.

## Slice-C intake + PR integrity bridge

For scheduler/metadata-bridge behavior-visible work, the flow is intentionally two-stage:

1. **Issue intake** captures lane classification + canonical owner file routing.
2. **PR checklist** confirms the same lane/owner mapping, parity-anchor disposition, and no-go guards.

If issue and PR lane/owner records differ, the PR must include an explicit lane reclassification rationale.

Minimum required reconciliation fields in PR:

- linked issue ID(s),
- issue intake lane + owner,
- PR lane + owner,
- reclassification rationale (mandatory for mismatch; `N/A (no mismatch)` only when identical).

Reviewer attestation requirement:

- For scheduler/metadata-bridge PRs, reviewer must confirm the reconciliation block is fully populated and consistent with linked issue intake before merge readiness.

Component-first execution requirement:

- Net-new behavior/contract work should land in `custom_components/spectra_ls` by default.
- Runtime/legacy path touches are exception-only and must include bounded rationale plus reviewer acknowledgment.
- Missing reconciliation/legacy-exception evidence should be treated as merge-blocking until completed.
- Planned component target-file evidence should be captured in issue intake and reconciled against PR changed files.
- Runtime-touch declaration should be captured at intake and reconciled in PR review (component-only declaration vs bounded runtime exception).
- Declaration-vs-diff mismatch (`component_only_declared` + runtime-file diff) is merge-blocking unless bounded exception evidence is complete.
- Declaration gate mode should be recorded in PR (`manual_enforced_now` now; `ci_enforced` once CI gate is active).
- If gate mode is `ci_enforced`, include CI workflow/job and run evidence in PR before merge readiness.
- If manual gate exception is used, include waiver owner + expiry date; indefinite waivers are merge-blocking.
- For `ci_enforced`, include CI verdict (`pass|fail|not_run`) and failure reason when verdict is `fail`.
- For `manual_enforced_now`, include a target date to transition that gate to `ci_enforced`.
- For `manual_enforced_now`, include a waiver tracking reference link (issue/discussion/decision).

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
- [`docs/notes/NOTES-engineering-rigor.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/notes/NOTES-engineering-rigor.md)

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
