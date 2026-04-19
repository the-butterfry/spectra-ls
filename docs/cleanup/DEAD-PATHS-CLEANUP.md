<!-- Description: Dead-path candidates and cleanup matrix for Spectra LS runtime and MA control hub tracked files. -->
<!-- Version: 2026.04.19.1 -->
<!-- Last updated: 2026-04-19 -->

# Dead Paths + Cleanup Opportunities (Retroactive Audit)

## Scope

This audit is restricted to tracked files relevant to:

- `esphome/spectra_ls_system/**`
- `packages/ma_control_hub.yaml`
- `packages/ma_control_hub/**`

Active include roots analyzed:

- `esphome/spectra_ls_system.yaml`
- `packages/ma_control_hub.yaml`

## Active runtime files (not dead)

The following are active runtime dependencies and should be treated as live paths:

- `spectra_ls_system.yaml`
- `substitutions.yaml`
- `spectra-ls-peripherals.yaml`
- `packages/spectra-ls-{hardware,ui,system,diagnostics,audio-tcp,lighting}.yaml`
- `components/*` referenced from entrypoint and package lambdas
- `packages/ma_control_hub.yaml` and all `.inc` fragments

## Candidate dead/stale paths

### Tier A — Safe-now archival/document cleanup (low risk)

1. `esphome/spectra_ls_system/NOTES-control-board-2.md`
   - Evidence: `v-next-NOTES.md` explicitly marks it archived/frozen and out-of-scope for this track.
   - Action: move under explicit archive docs folder (or mark header as `ARCHIVED` clearly).

2. `esphome/spectra_ls_system/v2-baseline-arch-readme.md`
   - Evidence: not included by runtime; name indicates legacy baseline narrative.
   - Action: archive or merge any still-needed context into v-next docs, then retire.

3. `esphome/spectra_ls_system/v3.md`
   - Evidence: not in active include graph; appears historical planning artifact.
   - Action: archive or fold into `v-next-NOTES.md` if still authoritative.

4. `esphome/spectra_ls_system/previous/`
   - Evidence: folder naming and policy indicate archival content.
   - Action: keep ignored/archive-only; avoid referencing from active docs/workflows.

### Tier B — Likely stale references requiring surgical cleanup (medium risk)

1. Commented legacy include line in `spectra_ls_system.yaml`
   - Current: `# peripherals: !include /config/esphome/spectra_ls_system/control-board-peripherals.yaml`
   - Risk: future confusion during edits.
   - Action: replace with modern alias comment or remove legacy line.

2. Dev templates containing rename-era checks no longer needed for current steady state
   - File: `DEVTOOLS-TEMPLATES.local.md` (contains historical rename-step templates).
   - Risk: operator confusion and long-template maintenance burden.
   - Action: split into:
     - `DEVTOOLS-RUNTIME.md` (current ops)
     - `DEVTOOLS-MIGRATION-ARCHIVE.md` (historical rename diagnostics)

3. `ma_control_hub` write helper scripts that are intentionally disabled
   - File: `packages/ma_control_hub/script.inc` (`ma_set_volume`, `ma_set_balance` both `stop` early)
   - Risk: unclear intent for future maintainers.
   - Action: either
     - keep (preferred if contract placeholders are needed), but label as `compatibility placeholders`, or
     - remove only with explicit downstream contract verification.

### Tier C — Keep (not dead, but monitor)

1. `packages/ma_control_hub/rest.inc`
   - Potentially appears redundant with template-heavy data path, but still supplies MA API snapshots (`players/all`, active player).
   - Action: keep unless replaced by an equivalent authoritative source.

2. `packages/ma_control_hub/automation.inc`
   - Event-driven orchestration critical for startup refresh/auto-select/restore behavior.
   - Action: keep; only refactor with parity tests.

## Recommended cleanup sequence

1. Archive-only documentation pass (Tier A).
2. Legacy-comment and template hygiene pass (Tier B item 1 + 2).
3. Optional script placeholder clarification pass (`ma_set_*` intent comments).
4. Re-run HA template diagnostics and ESPHome runtime smoke checks.

## Safety guardrails

Before deleting/moving anything, follow move/delete safety gate:

- backup path outside tracked repo,
- changelog entry,
- explicit restore command/path.

Do not remove paths that are:

- include-linked by active entrypoints,
- consumed by active HA package loads,
- required by current operator runbooks unless replacement docs are shipped same change set.
