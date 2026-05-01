<!-- Description: Fast, practical onboarding guide for Spectra L/S operators and contributors with direct task paths. -->
<!-- Version: 2026.05.01.1 -->
<!-- Last updated: 2026-05-01 -->

# Getting Started

Use this page to get moving fast.

If you are installing Spectra, this tells you where to start.
If you are contributing, this tells you exactly which docs define workflow and quality gates.

## 15-minute orientation

1. Read [`README.md`](https://github.com/the-butterfry/spectra-ls/blob/main/README.md) to understand product direction and current migration status.
2. Read [`docs/wiki/Install-on-Your-Own-HA.md`](Install-on-Your-Own-HA) if you are setting up a real instance.
3. Read [`docs/wiki/User-Setup-Deploy-and-HA-Integration.md`](User-Setup-Deploy-and-HA-Integration) for detailed integration and validation.
4. Read [`docs/wiki/Welcome-README-and-Bug-Workflow.md`](Welcome-README-and-Bug-Workflow) so you use the right intake path when something fails.

Expected result:

- You know whether you are on an operator path, bug-reporting path, or contributor path.

## Pick your path

Use this quick chooser first:

- If you need Spectra running in your house today, take the **Operator path**.
- If something is failing and you need support or a fix, take the **Bug-reporting path**.
- If you are changing code/docs/process, take the **Contributor path**.

### Operator path (install and run Spectra)

1. [Install-on-Your-Own-HA.md](Install-on-Your-Own-HA)
2. [User-Setup-Deploy-and-HA-Integration.md](User-Setup-Deploy-and-HA-Integration)
3. [Operations-Runbooks.md](Operations-Runbooks)

Path complete when:

- install/deploy checklist is complete,
- room/target menus are populated,
- audio + lighting actions both verify pass.

### Bug-reporting path (something broke)

1. [Welcome-README-and-Bug-Workflow.md](Welcome-README-and-Bug-Workflow)
2. [.github/ISSUE_TEMPLATE/bug_report.yml](https://github.com/the-butterfry/spectra-ls/blob/main/.github/ISSUE_TEMPLATE/bug_report.yml)
3. [Discussions-and-Projects-Workflow.md](Discussions-and-Projects-Workflow)

Path complete when:

- repro steps are deterministic,
- expected vs actual behavior is written clearly,
- redacted logs/config + impact statement are attached.

### Contributor path (code/docs changes)

1. [`CONTRIBUTING.md`](https://github.com/the-butterfry/spectra-ls/blob/main/CONTRIBUTING.md)
2. [`docs/developer/DEVELOPER-INSTRUCTIONS.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/developer/DEVELOPER-INSTRUCTIONS.md)
3. [`.github/pull_request_template.md`](https://github.com/the-butterfry/spectra-ls/blob/main/.github/pull_request_template.md)
4. [Release-and-Changelog-Process.md](Release-and-Changelog-Process)

Path complete when:

- required docs parity files are updated,
- verification evidence is captured,
- PR checklist is fully satisfied.

## Source-of-truth map

- Docs index: [`docs/README.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/README.md)
- Runtime architecture: [`docs/architecture/CODEBASE-RUNTIME-ARCHITECTURE.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/architecture/CODEBASE-RUNTIME-ARCHITECTURE.md)
- Control-hub architecture: [`docs/architecture/CONTROL-HUB-ARCHITECTURE.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/architecture/CONTROL-HUB-ARCHITECTURE.md)
- Wiring protocol: [`docs/hardware/WIRING-LAYOUT-PROTOCOL.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/hardware/WIRING-LAYOUT-PROTOCOL.md)
- Active roadmap ledger: [`docs/roadmap/v-next-NOTES.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/roadmap/v-next-NOTES.md)
- Changelog: [`docs/CHANGELOG.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/CHANGELOG.md)

## If you are contributing today

Non-negotiables:

- Keep fixes root-cause and reversible.
- Keep runtime path sealed unless a bounded exception is explicitly approved.
- Update docs parity in the same change set.
- Include verification evidence in your PR.

## First-day checklist

- [ ] I know which path I am on (operator, bug report, contributor).
- [ ] I know where install steps live.
- [ ] I know where to file a reproducible bug.
- [ ] I know which roadmap/changelog docs are authoritative.
