<!-- Description: Repository maturity blueprint for implementing best-in-class GitHub governance, contribution, and delivery workflows. -->
<!-- Version: 2026.05.02.25 -->
<!-- Last updated: 2026-05-02 -->

# Spectra L/S GitHub Masterwork Blueprint

This blueprint defines the target state for a mature, highly maintainable public repository.

Lean-team execution note (current):

- The masterwork baseline is the strategic target-state.
- During two-person active execution windows, only core blocker controls are merge-blocking by default; other masterwork controls are non-blocking optimization targets unless explicitly activated for a slice.
- Lean run updates should use concise parity-stamp format in roadmap ledgers to reduce overhead while preserving decision traceability.
- Lean v2 execution favors one-screen PR core packet + reviewer fast-path attestation while preserving blocker-critical evidence rules.
- Lean v2.1 execution adds compact scope toggles, explicit core-packet status, and UTC evidence timestamp signaling while preserving blocker-critical controls.
- Lean v2.2 execution adds explicit packet-owner accountability, one-line scope summary, and freshness hinting for evidence recency while preserving blocker-critical controls.
- Lean v2.3 execution adds explicit blocker verdict, optional-section completion summary, and reviewer timestamp signaling while preserving blocker-critical controls.
- Lean v2.4 execution adds core-packet coherence signaling, evidence artifact reference capture, and one-line blocker reason summary while preserving blocker-critical controls.
- Lean v2.5 execution adds explicit change-risk + follow-up signals (`yes|no` + tracking reference) to improve review-depth triage and post-merge traceability while preserving blocker-critical controls.
- Lean v2.6 execution adds validation-confidence, rollback-posture, and handoff-note signals for uncertainty/reversibility/continuity visibility while preserving blocker-critical controls.
- Lean v2.7 execution adds test-scope, contract-delta, and communication-note signals to improve verification-breadth, impact, and follow-through visibility while preserving blocker-critical controls.

## Benchmark inspiration

Primary benchmark reference: Immich (`immich-app/immich`) patterns for:

- structured issue intake,
- PR quality checklists,
- explicit ownership (`CODEOWNERS`),
- clear contributing and security policies,
- docs-first contributor onboarding.

## Maturity pillars

1. **Clear contribution pathway**
   - `CONTRIBUTING.md` defines workflow, scope, and quality expectations.
2. **Structured intake and triage**
   - issue forms separate bugs from feature requests.
3. **Review quality and ownership**
   - `CODEOWNERS` routes high-risk areas to maintainers.
4. **Community and safety standards**
   - `CODE_OF_CONDUCT.md` + `SECURITY.md` are explicit.
5. **Docs parity discipline**
   - behavior/process changes are reflected in docs in the same change set.

## Required governance artifacts

- `CONTRIBUTING.md`
- `CODEOWNERS`
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`
- `.github/ISSUE_TEMPLATE/config.yml`
- `.github/ISSUE_TEMPLATE/bug_report.yml`
- `.github/ISSUE_TEMPLATE/feature_request.yml`
- `.github/pull_request_template.md`
- `docs/governance/LABEL-TAXONOMY.md`
- `docs/governance/DISCUSSIONS-PROJECTS-OPERATING-MODEL.md`
- `docs/CHANGELOG.md`

## Discussions standard

- Maintain categories for `Ideas`, `Q&A`, `RFC / Architecture`, and `Announcements`.
- Route questions and early ideation to Discussions first, then promote to Issues when work is implementation-ready.
- Keep decision summaries in Discussion threads to preserve historical context.

## Projects standard

- Track all scoped work in a single portfolio board with fields for `Status`, `Area`, `Track`, `Priority`, `Risk`, and `Target`.
- Map every issue to a scope-path area (`esphome`, `packages`, `circuitpy`, `custom_components`, `docs/.github`, `bin`).
- Use Project workflows to keep triage throughput and visibility predictable.

## Wiki publication standard

- Source wiki pages in `docs/wiki/`.
- Publish via `.github/workflows/wiki-sync.yml`.
- Keep wiki parity in the same change set for operator/process changes where wiki pages are affected.

## Operating standards

### Issue quality standard

A bug issue must include:

- reproducible steps,
- expected vs actual behavior,
- environment/runtime context,
- relevant logs/config excerpts.
- for scheduler/metadata bridge behavior-visible issues: Slice-C lane classification and canonical owner-file routing from the owner matrix.
- for scheduler/metadata bridge behavior-visible issues: lane/owner entries are the intake baseline used for PR reconciliation.

### PR quality standard

A PR must include:

- clear purpose/scope,
- risk notes,
- verification evidence,
- docs impact statement,
- rollback notes when behavior/contract changes.
- for scheduler/metadata bridge slices: Slice-C write-path integrity checks (lane classification, canonical owner routing, parity-anchor disposition, and no-go confirmation).
- for linked scheduler/metadata bridge issues: explicit issue↔PR lane/owner reconciliation fields (issue ID(s), issue intake lane/owner, PR lane/owner).
- if issue and PR lane/owner differ: mandatory non-empty reclassification rationale (`N/A` permitted only when no mismatch).
- for scheduler/metadata bridge PR readiness: reviewer attestation that reconciliation evidence was verified against linked issue baseline.
- component-first execution is default for net-new behavior/contract work (`custom_components/spectra_ls`), with runtime/legacy touch treated as bounded exception.
- any bounded legacy exception requires explicit rationale and reviewer attestation before merge readiness.
- missing reconciliation/legacy-exception evidence is treated as merge-blocking in scheduler/metadata-bridge PR quality gate.
- planned component target-file evidence (`custom_components/spectra_ls/*`) is required for component-first slice scoping and PR reconciliation.
- runtime-touch declaration (`component_only_declared` vs `bounded_legacy_exception_expected`) is required at intake and must be reconciled during PR review against actual changed-file scope.
- declaration-vs-diff mismatch (`component_only_declared` with runtime file changes) is merge-blocking unless bounded exception evidence is complete.
- declaration gate mode must be explicit in PR workflow (`manual_enforced_now` or `ci_enforced`) to preserve enforcement-state auditability.
- when declaration gate mode is `ci_enforced`, CI workflow/job identity and run evidence must be present in PR quality packet.
- when manual gate exceptions are used, waiver owner + expiry evidence is mandatory and indefinite waivers fail PR quality gate.
- CI-enforced packets must record explicit CI verdict (`pass|fail|not_run`) and failure reason when verdict is `fail`.
- manual gate packets must include a bounded target date for transition to `ci_enforced`.
- manual gate packets must include a durable waiver tracking reference (issue/discussion/decision link).

Lean-team core gate minimum (active):

- linked issue ID,
- declaration gate mode,
- declaration-vs-diff merge-blocker decision,
- mode-specific evidence packet.

All other governance checklist surfaces are conditional by scope and may be batched for parity updates.

### Ownership standard

Critical paths requiring explicit review ownership:

- runtime stack (`esphome/spectra_ls_system/**`),
- control-hub contracts (`packages/**`),
- policy/automation (`.github/**`, `docs/**`).

## Release and triage hygiene (target)

- Consistent labels by type and subsystem.
- Changelog entries grouped by impact category.
- Optional future: release-drafter style categories for automated notes.

## Automation roadmap (phased)

### Phase A (now)

- Governance docs/templates established.
- Contribution and review expectations enforced socially.
- Discussions + Projects operating model documented and active.
- Wiki sync automation published and tokenized.

### Phase B

- Add label automation and optional stale/triage automation.
- Add docs-link checks for PRs touching governance/runtime contracts.

### Phase C

- Add release-note category automation.
- Add PR gates for required checklist completion.

## Definition of done for “masterwork baseline”

- All required governance artifacts exist and are usable.
- Templates enforce reproducible issue/PR quality.
- Ownership map reflects actual critical areas.
- Copilot instructions enforce parity with these artifacts.
- README remains end-user facing while contributor detail lives in docs/governance.
