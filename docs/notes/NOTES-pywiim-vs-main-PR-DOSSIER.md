<!-- Description: PR-ready branch comparison dossier for pywiim vs main with merge topology, file deltas, validation evidence, and merge guidance. -->
<!-- Version: 2026.04.25.1 -->
<!-- Last updated: 2026-04-25 -->

# Pywiim vs Main — PR Dossier

## Purpose

This document is the authoritative local reference for reviewing and merging branch `pywiim` into `main`.

- Scope: only `main...pywiim` delta (merge-base scoped)
- Audience: operator/reviewer/implementation agent
- Intended use: PR summary + pre-merge risk check + post-merge verification baseline

## Topology Snapshot (captured 2026-04-25)

- `main`: `552c6e7`
- `pywiim`: `aa92efc`
- merge base: `957cf25`
- divergence (`git rev-list --left-right --count main...pywiim`): `1 2`
  - `main`-only commits: 1
  - `pywiim`-only commits: 2

### Left/Right commit view

- `< 552c6e7` `checkpoint: commit pre-pywiim unstaged baseline work` (main-only)
- `> 2b1a5d3` `pywiim: add sync workflow and hard-deprecate legacy runtime lanes`
- `> aa92efc` `pywiim: harden sync checker and enforce pinned manifest contract`

## PR Delta (merge-base scoped)

### Files changed in `main...pywiim`

1. `README.md`
2. `bin/pywiim_sync_check.py` (new)
3. `custom_components/spectra_ls/manifest.json`
4. `docs/CHANGELOG.md`
5. `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`
6. `docs/roadmap/v-next-NOTES.md`
7. `esphome/spectra_ls_system/packages/spectra-ls-system.yaml`
8. `esphome/spectra_ls_system/substitutions.yaml`
9. `esphome/spectra_ls_system/upnp_hack/config.inc`
10. `packages/ma_control_hub/template.inc`
11. `packages/spectra_ls_diagnostics_hub.yaml` (new)

### Diffstat

- `11 files changed, 2283 insertions(+), 203 deletions(-)`

## What the branch does

## 1) Pywiim governance/sync contract

- Adds local checker script: `bin/pywiim_sync_check.py`
- Restores/enforces pinned dependency contract in integration manifest:
  - `custom_components/spectra_ls/manifest.json`
  - `requirements: ["pywiim==2.2.3"]`
- Hardens checker behavior:
  - strict operator parsing (`==` required by default)
  - fail-closed on missing/non-exact requirement
  - optional bounded override: `--allow-nonexact-pin`
  - token-aware GitHub API usage: `--github-token-env` (default `GITHUB_TOKEN`)
  - configurable timeout: `--timeout`

## 2) Runtime lane hard-deprecation + rollback gates

- Canonical runtime pass semantics shifted to pywiim-compatible route checks.
- Legacy direct transport/API lanes default to fail-closed:
  - `${legacy_transport_httpapi_enabled}: "false"` in substitutions
  - HTTP poll checks gated by `${legacy_transport_httpapi_enabled}`
  - UPnP hack scripts gated by `SPECTRA_ALLOW_LEGACY_UPNP=1`

## 3) Documentation parity

- Changelog + roadmap + README updated to reflect:
  - pywiim canonical route posture
  - upstream sync checker contract
  - hard-deprecation/rollback-gate behavior

## Validation evidence already captured

## Checker execution

Command used:

- `python3 /mnt/homeassistant/bin/pywiim_sync_check.py --manifest /mnt/homeassistant/custom_components/spectra_ls/manifest.json`

Observed output (latest in-session):

- `requirement_operator: "=="`
- `strict_pin_ok: true`
- `pinned_version: "2.2.3"`
- `upstream_version: "2.2.3"`
- `status: "up_to_date"`

## Static validation

- No checker syntax errors (`py_compile` pass).
- Repo diagnostic checks returned no relevant errors for modified docs/scripts.
- Expected ESPHome package-fragment lint warning can appear when validating package files standalone (`'esphome' section missing`); this is normal for package snippets.

## Merge risks & reviewer focus

## Primary risks

1. **Route-gate strictness drift**
   - Review `packages/ma_control_hub/template.inc` and diagnostics gates to ensure canonical route behavior does not block valid transitional contexts unexpectedly.

2. **Legacy rollback gate usability**
   - Confirm operator runbooks clearly specify when/how to temporarily enable:
     - `legacy_transport_httpapi_enabled=true`
     - `SPECTRA_ALLOW_LEGACY_UPNP=1`

3. **Main-only checkpoint divergence**
   - `main` has additional checkpoint commit (`552c6e7`).
   - Merge should be performed with conflict review, especially for files touched on both sides (README/roadmaps/changelog and control-hub/runtime yaml files).

## Suggested merge approach

1. Rebase `pywiim` on current `main` (or merge `main` into `pywiim`) before PR finalization.
2. Resolve overlap in:
   - `README.md`
   - `docs/CHANGELOG.md`
   - `docs/roadmap/*`
   - `packages/ma_control_hub/template.inc`
   - `esphome/spectra_ls_system/*`
3. Re-run checker and targeted runtime gate sanity after conflict resolution.
4. Keep rollback gates fail-closed by default in merged result.

## PR-ready summary text (copy/paste)

`pywiim` introduces a pywiim-governed control-lane hardening slice with two commits: (1) canonical route/deprecation gates across runtime contracts and (2) hardened upstream sync governance tooling.

Key outcomes:

- Added deterministic `pywiim` upstream sync checker (`bin/pywiim_sync_check.py`) with strict exact-pin validation, token-aware GitHub API handling, and bounded override controls.
- Restored explicit integration dependency contract `pywiim==2.2.3` in `custom_components/spectra_ls/manifest.json`.
- Shifted active runtime gate semantics toward canonical pywiim route posture and fail-closed legacy lane defaults, while preserving explicit rollback toggles for bounded diagnostics.
- Updated README/changelog/roadmap parity in the same slice.

Validation highlights:

- Checker run confirms `strict_pin_ok=true` and `status=up_to_date` (`2.2.3` vs upstream `2.2.3`).
- Targeted static checks pass (with expected standalone package-fragment warning class for ESPHome snippets).

Merge note:

- `main` currently has one additional checkpoint commit (`552c6e7`) not present in `pywiim`; resolve overlap carefully in docs + control/runtime contracts before merge.

## Local reference policy for future agent work

When working on `pywiim` or merge planning, treat this file as the first local reference:

- `/mnt/homeassistant/docs/notes/NOTES-pywiim-vs-main-PR-DOSSIER.md`

If branch topology changes (new commits on `main` or `pywiim`), update this dossier in the same change set as any merge-prep adjustments.
