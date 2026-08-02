<!-- Description: Operator guide for the Home Assistant sidebar Spectra L/S settings dashboard surface. -->
<!-- Version: 2026.08.01.3 -->
<!-- Last updated: 2026-08-01 -->

# Spectra Sidebar Settings

Use this page as your day-to-day control-center dashboard in Home Assistant.

## What this page is for

- Quick visibility into readiness and last-attempt status
- Safe dry-run actions while tuning mappings
- Fast access to presets before deeper integration config work

## Why this exists

The integration Configure modal is good for editing, but bad for continuous feedback. Sidebar gives you persistent signal while you tune.

## Enable checklist

1. Confirm `configuration.yaml` includes the Spectra dashboard registration under `lovelace.dashboards`.
2. Confirm `dashboards/spectra_ls_settings.yaml` exists.
3. Reload Lovelace dashboards (or restart Home Assistant).
4. Verify **Spectra L/S** appears in the left sidebar.

## Daily workflow (recommended)

1. Open **Spectra L/S** in sidebar.
2. Run quick safe checks:
   - `Dry-run encoder press`
   - `Dry-run encoder turn`
   - `Apply media preset` / `Apply target-nav preset` (read-only-safe defaults)
3. If mappings need edits, go to **Settings → Devices & Services → Spectra LS → Configure**.
4. Return to sidebar and verify readiness/attempt state changed as expected.

## If behavior looks wrong

| Symptom | First check | Next action |
| --- | --- | --- |
| Dry-run reports fail | Read-only mode + active mapping | Verify mapping in Configure, retry dry-run |
| Preset seems ignored | Last-attempt status entity | Check latest attempt detail and target route health |
| Status stale after change | Dashboard refresh/reload | Reload dashboard, then re-check state entities |

## Notes

- This page is intentionally lightweight and migration-safe.
- Runtime authority/cutover behavior is unchanged by this UI surface.
- Read-only-first and rollback-safe boundaries remain in effect.
