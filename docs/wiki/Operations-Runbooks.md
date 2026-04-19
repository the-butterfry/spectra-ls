<!-- Description: Operations runbooks for docs parity, runtime validation, deployment proof, and rollback readiness. -->
<!-- Version: 2026.04.19.1 -->
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

## Required proof in status updates

- Build result (success/failure summary)
- OTA result (`OTA successful` or exact failure)
- Git sync evidence (`HEAD` and `origin/main` SHAs)

## Recovery and rollback expectations

- Keep change sets small and reversible.
- Document rollback plan in PRs for behavior/contract modifications.
