<!-- Description: Operational runbook for keeping main and menu-only branches healthy. -->
<!-- Version: 2026.04.16.2 -->
<!-- Last updated: 2026-04-16 -->

# Branch Operations Runbook

## Objective

Keep `main` (spectra_ls_system active development) and `menu-only` (v2 stabilization) concurrently operable without disrupting live filesystem paths.

## Worktree Layout

- `main` worktree: `/mnt/homeassistant`
- `menu-only` worktree: `/mnt/homeassistant/.worktrees/menu-only`

## Required Workflow

1. Make changes in the correct worktree for the target branch.
2. For shared contracts (RP2040 protocol, control API, helper/entity contracts), do one:
   - paired update in both branches, or
   - explicit divergence + migration note in `CHANGELOG.md`.
3. Validate entrypoints before commit:
   - `main`: `esphome/spectra_ls_system.yaml`
   - `menu-only`: `control-board-esp32-tcp.yaml`
4. Commit and push each branch independently; keep remotes in sync.

## Shared-Contract Parity Gate (Go / No-Go)

Before merging or pushing any shared-contract change, complete `.github/SHARED-CONTRACT-CHECKLIST.md`.

- **Go** only when every required item is checked and evidence is recorded.
- **No-Go** if any shared-contract item is unchecked or evidence is missing.
- If parity is intentionally skipped, add explicit divergence + migration note to `CHANGELOG.md` before push.

## Safety Rules

- Never move/delete live `esphome/` paths without reversible backup and restore validation.
- Never commit real `secrets.yaml`; only commit templates like `secrets.example.yaml`.
