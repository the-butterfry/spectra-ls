<!-- Description: First-stop wiki page for new users covering orientation, support paths, and bug submission workflow. -->
<!-- Version: 2026.04.19.2 -->
<!-- Last updated: 2026-04-19 -->

# Welcome, README, and Bug Workflow

If you are new to Spectra L/S, start here.

## Step 1 — Read this first

1. `README.md` (what Spectra is and why it exists)
2. `docs/wiki/Install-on-Your-Own-HA.md` (strict install checklist)
3. `docs/wiki/User-Setup-Deploy-and-HA-Integration.md` (operator setup and deployment)
4. `docs/wiki/Discussions-and-Projects-Workflow.md` (how work moves from idea to implementation)

## Step 2 — Pick the right intake path

- **Question / idea / architectural discussion** → GitHub Discussions
- **Reproducible defect** → GitHub Issue (`bug_report.yml`)
- **Implementation work** → GitHub Issue + Project item + PR

## Step 3 — Bug submission how-to

When submitting a bug:

1. Reproduce the issue with deterministic steps.
2. Capture exact logs and relevant redacted config.
3. Specify affected area (`esphome`, `packages`, `rp2040`, docs/tooling).
4. Include branch/commit/version context.
5. State user impact and any workaround.

## Triage + fix workflow

1. Maintainer triages labels (`type`, `area`, `priority`).
2. Issue is added to the Project board.
3. Work proceeds in a scoped PR with verification evidence.
4. Changelog/docs parity is updated in the same change set.
5. Issue closes only after validated behavior and evidence.

## Good bug reports include

- Expected vs actual behavior
- Deterministic repro steps
- Relevant logs/output
- Clear impact statement
- Scope path and branch
