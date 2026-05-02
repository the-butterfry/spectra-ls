<!-- Description: Contributor workflow guide for Spectra L/S with clear branch boundaries, quality gates, and PR expectations. -->
<!-- Version: 2026.05.02.31 -->
<!-- Last updated: 2026-05-02 -->

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
  - component-first is the default execution path for new behavior/contract work; legacy-touch should be exception-only.

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

## Lean-team operating mode (active)

Current execution context is a two-person team. While this remains true:

- Default PR mode is `lean_team`.
- Required merge packet is the **Lean v2 one-screen core packet** in the PR template.
- Core packet now includes a single status line (`complete|incomplete`) for fast reviewer triage.
- Core packet now includes a coherence line (`coherent|needs-fix`) for fast packet consistency triage.
- Core packet now includes explicit risk level (`low|medium|high`) for reviewer depth triage.
- Core packet now includes explicit follow-up signals (`yes|no` + tracking reference or `N/A`).
- Core packet now includes validation-confidence signal (`high|medium|low`) for uncertainty visibility.
- Core packet now includes rollback-posture signal (`safe|needs-attention`) for fast reversibility triage.
- Core packet now includes handoff-note reference (`N/A` if none) for reviewer/operator continuity.
- Core packet now includes explicit test-scope signal (`full|targeted|minimal`) for verification breadth clarity.
- Core packet now includes explicit contract-delta signal (`none|minor|major`) for contract-impact visibility.
- Core packet now includes communication-note reference (`N/A` if none) for operational follow-through traceability.
- Core packet must include a named owner for accountability.
- Core packet should include explicit blocker verdict (`ready|blocked`) for merge-readiness clarity.
- Extended governance sections are conditional by scope (trigger-matrix driven, not always-on).
- Use compact scope toggles (`yes|no`) before optional sections to disposition scope quickly and consistently.
- Include a one-line scope summary (`A`, `B`, `A+B`, or `none`) for fast reviewer scan.
- Include one-line optional-section completion summary (`A done`, `B done`, `A+B done`, or `none`).
- Include one-line evidence artifact reference (`URL/path` or `N/A`) for proof lookup speed.
- Declaration mismatch and exception evidence blockers remain mandatory.
- Include an explicit evidence capture timestamp (`UTC`) in the minimal evidence block.
- Add evidence freshness hint (`fresh|stale`) beside timestamp to signal recency quickly.
- Include blocker reason summary (`N/A` when ready) for fast blocked-state triage.
- Include reviewer attestation timestamp (`UTC`) in fast-path sign-off.
- Use PR-template quick-fill snippets for `ci_enforced` and `manual_enforced_now` to reduce packet formatting drift.
- Optional sections should default to `N/A (not in scope)` unless explicitly triggered by scope.
- Reviewer sign-off in lean mode uses the PR template fast-path attestation line.

## Slice-C write-path integrity intake (scheduler + metadata bridge)

When a PR touches scheduler or metadata bridge behavior-visible paths, include this intake check before coding:

- classify lane (`scheduler` or `metadata_bridge`),
- confirm canonical owner file from `docs/notes/NOTES-engineering-rigor.md` Slice-C matrix,
- identify paired-review files and verify no owner-bypass/forked logic,
- pre-record two-track disposition intent (runtime + component),
- ensure PR checklist section `Slice-C write-path integrity` is completed before merge.

Issue intake parity:

- Bug/feature issue forms now capture lane classification and canonical owner-file routing up front for scheduler/metadata-bridge requests.
- Keep issue intake and PR checklist records aligned; if they differ, the PR must explain the lane reclassification reason explicitly.
- Issue↔PR reconciliation is required when a linked issue exists: capture linked issue ID(s), issue intake lane/owner, and PR lane/owner in the PR template.
- Mismatch rationale field is mandatory for any intake-vs-PR lane/owner divergence; use `N/A (no mismatch)` only when records are identical.
- Reviewer attestation is required for scheduler/metadata-bridge PRs: maintainer must confirm reconciliation evidence is complete before merge readiness.
- Reviewer attestation is required for legacy exceptions: maintainer must confirm runtime touch is necessary, bounded, and rollback-safe.
- Missing reconciliation or legacy-exception evidence is merge-blocking for scheduler/metadata-bridge PR readiness.
- Planned component target-file evidence (expected `custom_components/spectra_ls/*` touchpoints) is required at intake and must reconcile with PR changed files.
- Runtime-touch declaration is required at intake (`component_only_declared` vs `bounded_legacy_exception_expected`) and must reconcile with actual PR file scope.
- If intake declares `component_only_declared`, runtime-file changes are merge-blocking unless bounded exception rationale + tracking reference are complete.
- Declaration gate mode must be recorded in PR (`manual_enforced_now` until CI gate is active, then `ci_enforced`).
- When gate mode is `ci_enforced`, PR must include CI workflow/job identifier and run evidence URL; missing CI evidence is merge-blocking.
- When `manual_enforced_now` exception posture is used, PR must include waiver owner + expiry date; indefinite waivers are not allowed.
- When gate mode is `ci_enforced`, PR must also capture CI verdict (`pass|fail|not_run`) and failure reason when verdict is `fail`.
- When gate mode is `manual_enforced_now`, PR must include a target date to transition to `ci_enforced`.
- When gate mode is `manual_enforced_now`, PR must include a manual-waiver tracking reference link.

Lean docs-parity batching policy:

- Changelog-first remains immediate.
- Roadmap/wiki/masterwork wording sync may be batched up to 4 micro-slices per pass during `lean_team` mode.
- If policy direction changes mid-batch, record a plan-delta note in the next parity sync entry.

Lean parity-stamp format (roadmap/notes):

- `parity_stamp: YYYY-MM-DD / slice-group / mode=lean_team / batch=n`
- Keep stamp lines concise; include only decision delta + two-track disposition + P1/P2/P3 impact.

## Two-person fast-start (60 seconds)

1. Link issue ID in PR.
2. Select declaration mode (`manual_enforced_now` or `ci_enforced`).
3. Record declaration-vs-diff blocker decision, set core packet status (`complete|incomplete`), and set core packet owner.
4. Set core packet coherence (`coherent|needs-fix`) and fill evidence artifact reference (`URL/path` or `N/A`).
5. Set risk/follow-up packet lines (`risk`, `follow-up needed`, `follow-up tracking reference`).
6. Set confidence/reversibility/handoff packet lines (`validation confidence`, `rollback posture`, `handoff note reference`).
7. Set scope/delta/communication packet lines (`test scope`, `contract delta`, `communication note reference`).
8. Paste the matching quick-fill snippet from the PR template and fill values.
9. Set quick scope toggles (`yes|no`) and mark optional sections as completed or `N/A (not in scope)`.
10. Add evidence capture timestamp (`UTC`), freshness hint (`fresh|stale`), and blocker reason summary (`N/A` when ready).
11. Add reviewer attestation timestamp (`UTC`) in fast-path section.

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
