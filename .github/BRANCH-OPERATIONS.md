<!-- Description: Operational runbook for current main-only workflow and legacy-branch archival posture. -->
<!-- Version: 2026.04.21.2 -->
<!-- Last updated: 2026-04-21 -->

# Branch Operations Runbook

## Objective

Keep `main` (`esphome/spectra_ls_system` active development) healthy and synchronized while treating retired legacy paths as out-of-scope for default workflow.

## Worktree Layout

- `main` worktree: `/mnt/homeassistant`

## Required Workflow

1. Make changes in the correct worktree for the target branch.
2. Validate active entrypoint before commit:
   - `main`: `esphome/spectra_ls_system.yaml`
3. Commit and push `main`; keep remote synchronized.
4. Treat `esphome/control-py/**` and `esphome/control-board-esp32-tcp.yaml` as retired/ignored on `main`.

## Safety Rules

- Never move/delete live `esphome/` paths without reversible backup and restore validation.
- Never commit real `secrets.yaml`; only commit templates like `secrets.example.yaml`.
