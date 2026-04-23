<!-- Description: Practical operations runbooks for docs parity, runtime validation, deployment proof, and rollback readiness. -->
<!-- Version: 2026.04.22.2 -->
<!-- Last updated: 2026-04-22 -->

# Operations Runbooks

Use this page when you need the exact “what do I do next?” steps.

## Documentation parity runbook

1. Update `docs/CHANGELOG.md` first.
2. Update the affected roadmap docs:
   - `docs/roadmap/v-next-NOTES.md`
   - `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`
3. Update any changed wiki source pages under `docs/wiki/`.
4. Update `README.md` only when user-facing behavior or workflow changed.
5. Validate markdown and file diagnostics.
6. Commit and push with a clear slice label.

Expected result:

- changelog + roadmap + docs stay in sync,
- no “mystery” documentation drift between pages.

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
   - push a small `docs/wiki/*` change and rerun.
4. Confirm the `Sync docs/wiki to GitHub Wiki` step is green.

Quick triage checklist:

- If clone of `<repo>.wiki.git` fails: wiki is disabled/uninitialized or token cannot read it.
- If push fails with auth error: token scope/target repo is wrong.

## Bug intake to execution runbook

1. Validate issue has deterministic repro + impact.
2. Apply labels (`type`, `area`, `priority`).
3. Add issue to project board with `Status`, `Area`, `Track`, `Priority`.
4. Move to implementation only after scope is clear.
5. Require PR evidence + docs parity before merge.

## Required proof in status updates

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
