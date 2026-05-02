<!-- Description: First-stop operator page for orientation, support routing, and high-quality bug submission workflow. -->
<!-- Version: 2026.05.02.1 -->
<!-- Last updated: 2026-05-02 -->

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

## Step 2.5 — Fast sanity checks before filing a bug

Do these first to avoid filing environment drift as a product defect:

1. Confirm active target and route surfaces are populated (not `none/unknown/unavailable`).
2. Confirm latest deploy succeeded (build + OTA evidence if runtime path changed).
3. Re-run the relevant runbook once from [`Operations-Runbooks.md`](Operations-Runbooks).

If all three still fail, file the bug.

## Step 3 — Submit a useful bug report

When submitting a bug:

1. Reproduce the issue with deterministic steps.
2. Capture exact logs and relevant redacted config.
3. Specify affected area (`esphome`, `packages`, `rp2040`, docs/tooling).
4. Include branch/commit/version context.
5. State user impact and any workaround.

For scheduler/metadata-bridge behavior-visible reports, also include:

1. Write-path lane classification (`scheduler` or `metadata_bridge`).
2. Canonical owner file routing (`packages/ma_control_hub/template.inc` or `custom_components/spectra_ls/registry.py`).
3. Slice-C intake integrity confirmation (no owner-bypass/forked-lane intent).

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

## Copy/paste bug packet (recommended)

- Repro steps:
- Expected behavior:
- Actual behavior:
- Affected area (`esphome` / `packages` / `custom_components` / docs/tooling):
- Version context (`branch`, `commit`, deployment timestamp):
- Evidence attached (logs/config snippets/screenshots):
- Impact + workaround (if any):

### Slice-C add-on fields (when scheduler/metadata bridge is involved)

- Write-path lane (`scheduler` / `metadata_bridge` / `not_applicable`):
- Canonical owner file:
- Owner-bypass confirmation (`no` expected):
- Parity-anchor expectation (runtime + component):

See also: [Contributing Workflow](Contributing-Workflow) for PR-side `Slice-C write-path integrity` checklist expectations.
