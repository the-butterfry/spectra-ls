<!-- Description: First-stop operator page for orientation, support routing, and high-quality bug submission workflow. -->
<!-- Version: 2026.08.01.2 -->
<!-- Last updated: 2026-08-01 -->

# Welcome, README, and Bug Workflow

If you’re new, or if things are on fire, start here.

## Read this first

1. [`README.md`](https://github.com/the-butterfry/spectra-ls/blob/main/README.md)
2. [Install on Your Own Home Assistant](Install-on-Your-Own-HA)
3. [User Setup, Deploy, and HA Integration](User-Setup-Deploy-and-HA-Integration)

## Pick the right channel

- **Question / idea** → GitHub Discussions
- **Reproducible bug** → GitHub Issue (`bug_report.yml`)
- **Code/docs change** → Issue + PR

## Before filing a bug (saves everyone time)

1. Confirm target/routing surfaces are not `none/unknown/unavailable`.
2. Confirm your latest build/deploy was successful.
3. Run the matching runbook once: [Operations Runbooks](Operations-Runbooks).

If it still breaks, file it.

## What makes a bug report actually useful

- Deterministic repro steps
- Expected vs actual behavior
- Relevant logs (redacted)
- Scope area (`esphome`, `packages`, `custom_components`, `rp2040`, docs/tooling)
- Commit/branch/version context
- User impact

### Extra fields for scheduler/metadata-bridge issues

- Write-path lane (`scheduler`, `metadata_bridge`, or `not_applicable`)
- Canonical owner surface (for this issue)
- Owner-bypass confirmation (`no` expected)
- Runtime/component parity expectation

## Copy/paste bug packet

- Repro steps:
- Expected behavior:
- Actual behavior:
- Affected area:
- Version context (branch/commit/timestamp):
- Evidence attached:
- Impact + workaround:

## What happens after submission

1. Maintainer triage (`type`, `area`, `priority`)
2. Project board routing
3. Scoped fix PR with proof
4. Changelog/docs parity update
5. Closure after behavior is verified

For PR quality gates, use [Contributing Workflow](Contributing-Workflow).
