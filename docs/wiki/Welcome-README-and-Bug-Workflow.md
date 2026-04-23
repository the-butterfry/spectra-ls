<!-- Description: First-stop operator page for orientation, support routing, and high-quality bug submission workflow. -->
<!-- Version: 2026.04.22.4 -->
<!-- Last updated: 2026-04-22 -->

# Welcome, README, and Bug Workflow

Start here if you are new to Spectra or if something is broken and you need the right intake path.

## Step 1 — Read these pages first

1. [`README.md`](https://github.com/the-butterfry/spectra-ls/blob/main/README.md) (what Spectra is and why it exists)
2. [`docs/wiki/Install-on-Your-Own-HA.md`](Install-on-Your-Own-HA) (strict install checklist)
3. [`docs/wiki/User-Setup-Deploy-and-HA-Integration.md`](User-Setup-Deploy-and-HA-Integration) (operator setup and deployment)
4. [`docs/wiki/Discussions-and-Projects-Workflow.md`](Discussions-and-Projects-Workflow) (how work moves from idea to implementation)

## Step 2 — Choose the right intake path

- **Question / idea / architectural discussion** → GitHub Discussions
- **Reproducible defect** → GitHub Issue (`bug_report.yml`)
- **Implementation work** → GitHub Issue + Project item + PR

## Step 3 — Submit a useful bug report

When submitting a bug:

1. Reproduce the issue with deterministic steps.
2. Capture exact logs and relevant redacted config.
3. Specify affected area (`esphome`, `packages`, `rp2040`, docs/tooling).
4. Include branch/commit/version context.
5. State user impact and any workaround.

Expected result:

- Maintainers can reproduce quickly and route the issue without back-and-forth.

## What happens after you submit

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
