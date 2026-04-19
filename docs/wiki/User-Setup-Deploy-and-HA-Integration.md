<!-- Description: User-focused setup, deploy, and Home Assistant integration guide with manual prerequisites and token/API steps. -->
<!-- Version: 2026.04.19.1 -->
<!-- Last updated: 2026-04-19 -->

# User Setup, Deploy, and HA Integration

This is a first-pass setup stub for current runtime + parallel custom-component direction.

## Current setup model (today)

- Runtime control path: ESPHome + Home Assistant packages
- Parallel migration target: `custom_components/spectra_ls` (in roadmap phases)
- Discovery-first design remains default

## Prerequisites

1. Home Assistant installed and reachable.
2. ESPHome addon/integration available.
3. Spectra runtime files available in your deployment path.
4. Network reachability between HA and control endpoints.
5. Secrets strategy in place (`!secret` + local non-tracked files).

## Manual items you must provide (non-automated)

### Required

- Home Assistant host/address details for your environment.
- Device IPs/hostnames where auto-discovery cannot resolve.
- Environment-specific secret values in `secrets.yaml` or local secrets include.

### Optional / workflow tooling

- GitHub wiki publish token (if enabling wiki sync automation): `WIKI_FINE_GRAINED_PAT`
- Home Assistant Long-Lived Access Token (only if using custom external API tooling that requires token auth).

## Step-by-step runtime setup (operator flow)

1. Copy/setup required package and ESPHome config references for your install.
2. Ensure placeholders from `docs/setup/SPECTRA-HA-CONFIG-PLACEHOLDERS.md` are resolved with your local values.
3. Store secrets using `!secret` and local-only files (never commit deployment secrets).
4. Validate HA configuration and template entities.
5. Compile ESPHome configuration.
6. Deploy OTA/flash and confirm success.
7. Verify routing, room/target options, and core controls in HA UI.

## Integration checks with your own HA

- Target discovery surfaces are populated (no placeholder-only menus).
- Control path metadata resolves correctly (`control_path`, `control_capable`).
- Audio and lighting controls both operate and reflect expected state.
- Menu feedback and selected target synchronization are stable.

## Bug reporting when setup fails

Use the issue form and include:

- exact repro steps,
- affected area,
- branch/version context,
- redacted logs and config snippets,
- impact and workaround.

See: `docs/wiki/Welcome-README-and-Bug-Workflow.md`.

## Custom component setup roadmap (stub)

Setup will gradually move from package-heavy wiring to guided integration flows in `custom_components/spectra_ls`.

Roadmap source:

- `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`
- `docs/roadmap/v-next-NOTES.md`

As each phase lands, this page will gain concrete screenshots/steps/migration notes.
