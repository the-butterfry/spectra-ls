<!-- Description: Practical operations runbooks for docs parity, runtime validation, deployment proof, and rollback readiness. -->
<!-- Version: 2026.08.01.3 -->
<!-- Last updated: 2026-08-01 -->

# Operations Runbooks

Use this page when something is broken and you want a clear next step, not a theory lecture.

Need the full install→validate→rollback flow in one page? Use [Complete Operator Runbook](Complete-Operator-Runbook).

## Symptom routing

| If your problem is... | Start here |
| --- | --- |
| Docs are out of sync | Documentation parity runbook |
| Runtime change needs proof | Runtime-impacting change runbook |
| Wiki sync is failing | Wiki sync failed runbook |
| Bug needs triage routing | Bug intake to execution runbook |

## Documentation parity runbook

1. Update [`docs/CHANGELOG.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/CHANGELOG.md).
2. Update affected roadmap docs:
   - [`docs/roadmap/v-next-NOTES.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/roadmap/v-next-NOTES.md)
   - [`docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md)
3. Update changed wiki pages under [`docs/wiki/`](https://github.com/the-butterfry/spectra-ls/tree/main/docs/wiki).
4. Update [`README.md`](https://github.com/the-butterfry/spectra-ls/blob/main/README.md) if user-facing behavior/workflow changed.
5. Run markdown/diagnostic checks.
6. Commit and push with a clear slice label.

Outcome: no mystery drift between README, roadmap, and wiki.

## Runtime-impacting change runbook

1. Edit runtime/package files.
2. Build/compile before commit.
3. If build fails, fix root cause and rebuild.
4. Commit and push checkpoint.
5. If deployment is requested or implied, run OTA upload.
6. Capture and report proof lines.

Required proof lines:

- build summary (pass/fail),
- upload summary (`OTA successful` or exact error),
- git sync summary (`HEAD` and `origin/main` short SHAs).

## Wiki sync failed (`Wiki Sync`) runbook

1. Check failing step in Actions run details.
2. If failure is **preflight wiki access**:
   - verify wiki is enabled,
   - verify wiki was initialized once from GitHub UI,
   - verify `WIKI_FINE_GRAINED_PAT` exists and has `Contents: Read and write`.
3. If failure is **sync/push**:
   - verify PAT repository selection includes this repo,
   - push a small change under [`docs/wiki/*`](https://github.com/the-butterfry/spectra-ls/tree/main/docs/wiki) and rerun.
4. Confirm the `Sync docs/wiki to GitHub Wiki` step is green.

Quick triage cheatsheet:

- If clone of `<repo>.wiki.git` fails: wiki is disabled/uninitialized or token cannot read it.
- If push fails with auth error: token scope/target repo is wrong.

## Bug intake to execution runbook

1. Validate issue has deterministic repro + impact.
2. Apply labels (`type`, `area`, `priority`).
3. Add issue to project board with `Status`, `Area`, `Track`, `Priority`.
4. Move to implementation only after scope is clear.
5. Require PR evidence + docs parity before merge.

## Proof required in status updates

- Build result (success/failure summary)
- OTA result (`OTA successful` or exact failure)
- Git sync evidence (`HEAD` and `origin/main` SHAs)

If one is missing, the slice is not complete.

## Recovery and rollback expectations

- Keep change sets small and reversible.
- Document rollback plan in PRs for behavior/contract modifications.

## Operational references

- [Install-on-Your-Own-HA.md](Install-on-Your-Own-HA)
- [Welcome-README-and-Bug-Workflow.md](Welcome-README-and-Bug-Workflow)
- [Discussions-and-Projects-Workflow.md](Discussions-and-Projects-Workflow)
