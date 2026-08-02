<!-- Description: Practical setup/deploy/integration guide for Spectra on Home Assistant with clear operator outcomes and failure actions. -->
<!-- Version: 2026.08.02.1 -->
<!-- Last updated: 2026-08-02 -->

# User Setup, Deploy, and HA Integration

Use this page after install when you want confidence that Spectra is truly usable, not just “running.”

## Success criteria

- deploy completes cleanly
- audio + lighting controls both work
- room/target menus are populated with real values
- you have evidence ready if you need to open a bug

## Current operating model

- Home Assistant integration path (`custom_components/spectra_ls/`) is the primary lane for active behavior.
- Runtime path (`packages/` + `esphome/`) stays available for stability and recovery.
- Discovery-first and fail-closed routing remain the safety defaults.

## What is automatic vs what you own

### Automatic (when healthy)

- Target discovery and route metadata publication
- Control path state updates in HA entities
- Component diagnostics surfaces

### You still own

- Local secrets and host values
- Initial placement/wiring of runtime files
- Environment troubleshooting and rollback actions

## Practical integration checklist

1. Resolve local placeholders/secrets
2. Validate HA config
3. Compile/deploy ESPHome
4. Verify routing metadata and active target state
5. Verify at least one audio + one lighting action
6. Restart once and confirm state recovers cleanly

## Control-center settings quick path

Use **Settings → Devices & Services → Spectra LS → Configure** for remap/tuning.

Recommended flow:

1. choose a mapping preset
2. tweak actions/scenes
3. save
4. verify readiness via `sensor.spectra_ls_control_center_readiness`

Useful services:

- `spectra_ls.set_control_center_settings`
- `spectra_ls.execute_control_center_input` (start with dry-run)

## Fast failure triage

| Symptom | First check | Next move |
| --- | --- | --- |
| Empty room/target options | Placeholder resolution + helper/entity health | Re-apply local values, reload, retry |
| No route / deferred route | Active target + `control_path`/`control_capable` | Set known-good target and retest |
| Mapping feels ignored | Read-only mode + current mapping | Re-open Configure, verify applied settings |

## If setup fails hard

Open a bug with:

- deterministic repro
- expected vs actual
- redacted logs/config
- commit/version context
- user impact

Routing pages:

- [Welcome, README, and Bug Workflow](Welcome-README-and-Bug-Workflow)
- [Operations Runbooks](Operations-Runbooks)

## References

- Setup placeholders: [`docs/setup/SPECTRA-HA-CONFIG-PLACEHOLDERS.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/setup/SPECTRA-HA-CONFIG-PLACEHOLDERS.md)
- Runtime roadmap: [`docs/roadmap/v-next-NOTES.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/roadmap/v-next-NOTES.md)
- Component roadmap: [`docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md)
