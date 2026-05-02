<!-- Description: Pull request checklist template for quality, parity, and verification evidence. -->
<!-- Version: 2026.05.02.26 -->
<!-- Last updated: 2026-05-02 -->

# Pull Request

## Summary

- What changed:
- Why it changed:
- Scope intentionally excluded:

## Team execution mode

- Mode: `lean_team` (default) or `full_masterwork`
- Active contributors:

## Lean v2 one-screen core packet (required)

- [ ] Linked issue ID present
- [ ] Declaration gate mode recorded (`manual_enforced_now` or `ci_enforced`)
- [ ] Declaration-vs-diff blocker decision recorded
- [ ] Core packet status set (`complete` or `incomplete`)
- [ ] Core packet coherence set (`coherent` or `needs-fix`)
- [ ] Change risk level set (`low`, `medium`, or `high`)
- [ ] Follow-up needed set (`yes` or `no`)
- [ ] Follow-up tracking reference set (`N/A` if no follow-up)
- [ ] Validation confidence set (`high`, `medium`, or `low`)
- [ ] Rollback posture set (`safe` or `needs-attention`)
- [ ] Handoff note reference set (`N/A` if none)
- [ ] Test scope set (`full`, `targeted`, or `minimal`)
- [ ] Contract delta set (`none`, `minor`, or `major`)
- [ ] Communication note reference set (`N/A` if none)
- [ ] Mode-specific packet complete:
  - `ci_enforced`: workflow/job, run URL, verdict (`pass|fail|not_run`), and failure reason when `fail`
  - `manual_enforced_now`: waiver owner, waiver expiry, waiver tracking reference, and target date to transition to `ci_enforced`

Linked issue ID(s):

Declaration gate mode (`manual_enforced_now` or `ci_enforced`):

Declaration-vs-diff blocker decision:

Blocker verdict (`ready` or `blocked`):

Core packet status (`complete` or `incomplete`):

Core packet coherence (`coherent` or `needs-fix`):

Change risk level (`low`, `medium`, or `high`):

Follow-up needed (`yes` or `no`):

Follow-up tracking reference (`N/A` if no follow-up):

Validation confidence (`high`, `medium`, or `low`):

Rollback posture (`safe` or `needs-attention`):

Handoff note reference (`N/A` if none):

Test scope (`full`, `targeted`, or `minimal`):

Contract delta (`none`, `minor`, or `major`):

Communication note reference (`N/A` if none):

Core packet owner:

Mode-specific packet:

- CI workflow/job (`ci_enforced` else `N/A`):
- CI run URL (`ci_enforced` else `N/A`):
- CI verdict (`ci_enforced` else `N/A`):
- CI failure reason (`fail` else `N/A`):
- Manual waiver owner (`manual_enforced_now` else `N/A`):
- Manual waiver expiry (`manual_enforced_now` else `N/A`):
- Manual waiver tracking reference (`manual_enforced_now` else `N/A`):
- Manual->CI target date (`manual_enforced_now` else `N/A`):

## Scope trigger matrix (optional sections)

Quick scope toggles:

- Scheduler/metadata-bridge in scope? (`yes`/`no`)
- Shared-contract in scope? (`yes`/`no`)
- Runtime/legacy files touched? (`yes`/`no`)
- Scope trigger summary (`A`, `B`, `A+B`, or `none`):
- Optional-section completion summary (`A done`, `B done`, `A+B done`, or `none`):
- Evidence artifact reference (URL/path or `N/A`):

- Scheduler/metadata-bridge behavior-visible touched?
  - If **yes**: complete optional section A.
  - If **no**: mark section A `N/A (not in scope)`.
- Shared-contract change?
  - If **yes**: complete optional section B.
  - If **no**: mark section B `N/A (not in scope)`.
- Runtime/legacy files touched?
  - If **yes**: bounded-exception evidence is required.

## Optional section A — Scheduler/metadata-bridge integrity

Default value: `N/A (not in scope)`.
Only replace with details when section is in scope.

- Lane classification:
- Canonical owner file:
- Parity anchors disposition:
- Reclassification rationale (if mismatch):

## Optional section B — Shared-contract impact

Default value: `N/A (not in scope)`.
Only replace with details when section is in scope.

- Shared-contract checklist reference:
- Rollback note:

## Quick-fill snippets (copy/paste)

`ci_enforced` snippet:

- declaration mode: ci_enforced
- workflow/job: [workflow-job-name]
- run URL: [run-url]
- verdict: pass
- failure reason: N/A

`manual_enforced_now` snippet:

- declaration mode: manual_enforced_now
- waiver owner: [owner-name]
- waiver expiry: YYYY-MM-DD
- waiver tracking reference: [issue/discussion/decision-link]
- target ci_enforced date: YYYY-MM-DD

## Minimal validation evidence

- Build/compile status (if applicable):
- Runtime/template verification (if applicable):
- Evidence captured at (UTC):
- Evidence freshness hint (`fresh` or `stale`):
- Known blockers:
- Blocker reason summary (`N/A` if ready):

## Reviewer fast-path attestation (required)

- [ ] Core packet is complete/coherent; owner identified; risk/follow-up + confidence/rollback/handoff + scope/delta/communication signals recorded; declaration mismatch/exception blockers checked; mode-specific evidence packet present; evidence timestamp/freshness/artifact reference recorded; blocker summary recorded.
- Reviewer attestation time (UTC):

## Docs parity (lean)

- [ ] `docs/CHANGELOG.md` updated
- [ ] Roadmap docs updated now **or** queued in active parity batch
- [ ] README update needed? (`yes`/`no`)

## Final checks

- [ ] No secrets/environment-local artifacts committed
- [ ] Changes are scoped and reversible
- [ ] Commit message and PR title are clear
