<!-- Description: Repository maturity blueprint for implementing best-in-class GitHub governance, contribution, and delivery workflows. -->
<!-- Version: 2026.04.19.1 -->
<!-- Last updated: 2026-04-19 -->

# Spectra L/S GitHub Masterwork Blueprint

This blueprint defines the target state for a mature, highly maintainable public repository.

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
- `docs/CHANGELOG.md`

## Operating standards

### Issue quality standard

A bug issue must include:

- reproducible steps,
- expected vs actual behavior,
- environment/runtime context,
- relevant logs/config excerpts.

### PR quality standard

A PR must include:

- clear purpose/scope,
- risk notes,
- verification evidence,
- docs impact statement,
- rollback notes when behavior/contract changes.

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
