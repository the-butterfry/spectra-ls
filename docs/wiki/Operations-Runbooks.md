<!-- Description: Operations runbooks for docs parity, runtime validation, deployment proof, and rollback readiness. -->
<!-- Version: 2026.04.19.2 -->
<!-- Last updated: 2026-04-19 -->

# Operations Runbooks

## Runbook: Documentation parity change

1. Update `docs/CHANGELOG.md` first.
2. Update affected architecture/roadmap/governance docs.
3. Update `README.md` when operator-facing behavior changes.
4. Validate markdown lint/consistency checks.

## Runbook: Runtime-impacting change

1. Edit runtime/package files.
2. Compile/build successfully before commit.
3. Fix root cause of failures, rebuild.
4. Commit and push checkpoint.
5. If deployment requested: OTA upload + post-upload proof.

## Runbook: Wiki sync failed (`Wiki Sync`)

1. Check failing step in Actions run details.
2. If failure is preflight wiki access:
   - Confirm wiki is enabled.
   - Confirm wiki was initialized with first `Home` save.
   - Confirm `WIKI_FINE_GRAINED_PAT` exists and has repository `Contents: Read and write`.
3. If failure is sync/push:
   - Confirm PAT repository selection includes this repo.
   - Re-run workflow after a small `docs/wiki/*` change.
4. Confirm `Sync docs/wiki to GitHub Wiki` step is green.

## Runbook: Bug intake to execution

1. Validate issue has deterministic repro + impact.
2. Apply labels (`type`, `area`, `priority`).
3. Add issue to project board with `Status`, `Area`, `Track`, `Priority`.
4. Move to implementation only after scope is clear.
5. Require PR evidence + docs parity before merge.

## Required proof in status updates

- Build result (success/failure summary)
- OTA result (`OTA successful` or exact failure)
- Git sync evidence (`HEAD` and `origin/main` SHAs)

## Recovery and rollback expectations

- Keep change sets small and reversible.
- Document rollback plan in PRs for behavior/contract modifications.

## Operational references

- `docs/wiki/Install-on-Your-Own-HA.md`
- `docs/wiki/Welcome-README-and-Bug-Workflow.md`
- `docs/wiki/Discussions-and-Projects-Workflow.md`
