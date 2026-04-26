<!-- Description: Operator guide for the Home Assistant sidebar Spectra L/S settings dashboard surface. -->
<!-- Version: 2026.04.22.2 -->
<!-- Last updated: 2026-04-22 -->

# Spectra Sidebar Settings

Use this page as the practical “home” for Spectra settings visibility in Home Assistant.

## What this is

- A dedicated Home Assistant sidebar dashboard entry: **Spectra L/S**.
- A full-page surface for quick readiness/mapping visibility while you tune settings.
- One-click action controls for safe dry-run probes and preset application.
- A companion to integration Configure (which remains the canonical write path).

## Why this exists

The Configure modal in Integrations is useful but small. The sidebar dashboard gives a persistent page so you can keep status in view while adjusting mappings.

## Enable/checklist

1. Confirm `configuration.yaml` includes the Spectra dashboard registration under `lovelace.dashboards`.
2. Confirm `dashboards/spectra_ls_settings.yaml` exists.
3. Reload Lovelace dashboards (or restart Home Assistant).
4. Verify **Spectra L/S** appears in the left sidebar.

## Daily workflow

1. Open sidebar **Spectra L/S** to watch readiness and last-attempt state.
2. Use quick-action buttons for safe checks:
   - `Dry-run encoder press`
   - `Dry-run encoder turn`
   - `Apply media preset` / `Apply target-nav preset` (read-only-safe defaults)
3. If needed, open Integrations -> `Spectra LS` -> Configure for full manual remap.
4. Return to sidebar page and confirm readiness/attempt surfaces reflect expected state.

## Notes

- This page is intentionally lightweight and migration-safe.
- Runtime authority/cutover behavior is unchanged by this UI surface.
- Read-only-first and rollback-safe boundaries remain in effect.
