<!-- Description: Pull request checklist template for quality, parity, and verification evidence. -->
<!-- Version: 2026.04.21.2 -->
<!-- Last updated: 2026-04-21 -->

# Pull Request

## Summary

- What changed:
- Why it changed:
- Scope intentionally excluded:

## Type of change

- [ ] Bug fix
- [ ] Feature
- [ ] Refactor/cleanup
- [ ] Documentation
- [ ] Governance/process

## Validation evidence

- [ ] Build/compile status included (when applicable)
- [ ] Runtime or template verification included (when applicable)
- [ ] No new known blockers

Evidence notes:

## Docs parity

- [ ] `docs/CHANGELOG.md` updated
- [ ] Relevant architecture/roadmap docs updated (if behavior/contracts changed)
- [ ] `README.md` updated **or** explicitly not required

Docs touched:

## Legacy-seal boundary check

- [ ] This PR preserves sealed legacy-runtime posture **or** includes explicit bounded exception rationale
- [ ] Net-new ownership/feature growth is component-first (`custom_components/spectra_ls`) unless explicitly approved and documented
- [ ] Two-track disposition is stated (runtime + component)

## Risk and rollback

- Risk level: Low / Medium / High
- Rollback plan:

## Shared-contract impact

- [ ] No shared-contract impact
- [ ] Shared-contract impact addressed via `.github/SHARED-CONTRACT-CHECKLIST.md`

## Final checks

- [ ] No secrets/environment-local artifacts committed
- [ ] Changes are scoped and reversible
- [ ] Commit message and PR title are clear
