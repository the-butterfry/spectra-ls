<!-- Description: Practical setup/deploy/integration guide for Spectra on Home Assistant with clear operator outcomes and failure actions. -->
<!-- Version: 2026.04.22.14 -->
<!-- Last updated: 2026-04-22 -->

# User Setup, Deploy, and HA Integration

Use this page to deploy Spectra and verify that control paths are actually usable.

Target outcome:

- runtime deploy completes,
- audio + lighting routes work,
- room/target menus are populated,
- you have enough evidence to debug or file a high-quality bug if needed.

## Current setup model (today)

- Runtime control path: ESPHome + Home Assistant packages
- Parallel migration target: [`custom_components/spectra_ls`](https://github.com/the-butterfry/spectra-ls/tree/main/custom_components/spectra_ls) (in roadmap phases)
- Discovery-first design remains default

## What is automated vs manual today

### Automated (when healthy)

- Target discovery and route metadata publication.
- Control-host resolution from MA/HA discovery surfaces (`sensor.ma_control_hosts` / `sensor.ma_control_host`) with fail-closed runtime gating until valid hosts are present.
- Runtime surface synchronization between HA helper/catalog entities and control UI.
- Wiki publishing (if `WIKI_FINE_GRAINED_PAT` is configured and workflow succeeds).

### Manual (operator responsibility)

- Environment-specific host/IP/secret values.
- Initial HA package/runtime placement and include wiring.
- Token/secret setup for optional automation workflows.
- Troubleshooting and rollback actions when environment drift occurs.

## Prerequisites

1. Home Assistant installed and reachable.
2. ESPHome addon/integration available.
3. Spectra runtime files available in your deployment path.
4. Network reachability between HA and control endpoints.
5. Secrets strategy in place (`!secret` + local non-tracked files).

## Manual items you must provide (non-automated)

### Required

- Home Assistant host/address details for your environment.
- Environment-specific secret values in `secrets.yaml` or local secrets include.

Discovery contract note:

- Spectra runtime no longer ships install-specific target host/IP bootstrap defaults.
- If discovery surfaces are unresolved or invalid, control writes remain blocked (fail-closed) until valid hosts are published.

### Optional / workflow tooling

- GitHub wiki publish token (if enabling wiki sync automation): `WIKI_FINE_GRAINED_PAT`
- Home Assistant Long-Lived Access Token (only if using custom external API tooling that requires token auth).

## Minimum viable integration baseline

- A reachable HA instance with expected helper/entity contracts present.
- ESPHome runtime compiled and deployed without errors.
- At least one valid audio target and one valid lighting target discovered.
- Room/target navigation menus populated with concrete options.

## Control-center settings (P6 early availability)

You can now stage core control-center mappings from the Spectra integration itself:

- **Sidebar settings page (new):** Home Assistant sidebar -> `Spectra L/S` (dashboard-backed settings surface).
- This gives you a persistent full page for readiness/mapping visibility while tuning, instead of relying only on the small configure modal.
- Sidebar page now includes direct one-click action controls for safe checks/preset application:
  - `Dry-run encoder press`
  - `Dry-run encoder turn`
  - `Apply media preset`
  - `Apply target-nav preset`

- **Fast remap path (today):** Home Assistant -> Settings -> Devices & Services -> Integrations -> `Spectra LS` -> Configure.
- This remains the canonical settings write path and is now intentionally kept simple.

- Integration options (Configure on `Spectra LS`) now include:
  - **Single-step form:** read-only mode + mapping preset + encoder turn/press/long-press actions + button 1–4 scene bindings.
- Recommended fast-remap workflow:
  1. choose a mapping preset,
  2. adjust any per-input actions/scenes you want,
  3. save,
  4. confirm active mapping via `sensor.spectra_ls_control_center_readiness` attributes.
- Scene bindings now use scene-aware selectors in options flow (instead of free-text only), and button-1 quick-trigger defaults are pre-suggested when scenes are discoverable.
- Service path is also available for automation/operator workflows:
  - `spectra_ls.set_control_center_settings`
  - `spectra_ls.execute_control_center_input` (dry-run-first)
- New readiness diagnostics entities improve setup visibility without opening full diagnostics payloads:
  - `sensor.spectra_ls_control_center_readiness`
  - `sensor.spectra_ls_control_center_last_attempt_status`

This is additive and migration-safe: runtime/source-of-truth ownership remains unchanged while Control Center settings are staged.

Cutover note:

- Component is the primary development lane for net-new control-center behavior.
- Legacy runtime remains a rollback-safe compatibility baseline until bounded retirement gates are completed.

For P6 execution-lane validation evidence, use:

- [`docs/testing/raw/p6_s04_control_input_execution_monitor.jinja`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/testing/raw/p6_s04_control_input_execution_monitor.jinja)
- [`docs/testing/raw/p6_s04_control_input_execution_checklist.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/testing/raw/p6_s04_control_input_execution_checklist.md)

## Step-by-step runtime setup (operator flow)

1. Copy/setup required package and ESPHome config references for your install.
2. Ensure placeholders from [`docs/setup/SPECTRA-HA-CONFIG-PLACEHOLDERS.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/setup/SPECTRA-HA-CONFIG-PLACEHOLDERS.md) are resolved with your local values.
3. Store secrets using `!secret` and local-only files (never commit deployment secrets).
4. Validate HA configuration and template entities.
5. Compile ESPHome configuration.
6. Deploy OTA/flash and confirm success.
7. Verify routing, room/target options, and core controls in HA UI.

Expected result after Step 7:

- no placeholder-only room/target menus,
- control-path metadata is present,
- at least one audio and one lighting action succeed and reflect state.

## Integration checks with your own HA

- Target discovery surfaces are populated (no placeholder-only menus).
- Control path metadata resolves correctly (`control_path`, `control_capable`).
- Audio and lighting controls both operate and reflect expected state.
- Menu feedback and selected target synchronization are stable.

## Verification matrix (quick)

| Check | Pass condition |
| --- | --- |
| Discovery | Room/target options are concrete, not placeholder-only |
| Routing | `control_path` and `control_capable` are present/consistent |
| Audio actions | Transport/volume actions apply and state reflects changes |
| Lighting actions | Brightness/color actions apply and state reflects changes |
| Restart resilience | State and options recover correctly after restart |

## Bug reporting when setup fails

Use the issue form and include:

- exact repro steps,
- affected area,
- branch/version context,
- redacted logs and config snippets,
- impact and workaround.

See: [`docs/wiki/Welcome-README-and-Bug-Workflow.md`](Welcome-README-and-Bug-Workflow).

Attach these when possible:

- runtime build/deploy evidence,
- concise repro timeline,
- redacted config snippets,
- affected area + impact statement.

## Fast failure triage

| If you see this | Check this first | Then do this |
| --- | --- | --- |
| Empty room/target options | Placeholder resolution and helper entities | Re-apply local values, reload templates/helpers, rerun checks |
| Route keeps deferring/no target | Active target/helper state + route metadata | Set a known-good target and revalidate `control_path` + `control_capable` |
| Scene/input mapping does nothing | Control Center mapping + read-only mode | Check integration options, confirm mapping exists, and verify `read_only_mode` behavior |

## Custom component setup roadmap (stub)

Setup will gradually move from package-heavy wiring to guided integration flows in [`custom_components/spectra_ls`](https://github.com/the-butterfry/spectra-ls/tree/main/custom_components/spectra_ls).

Roadmap source:

- [`docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md)
- [`docs/roadmap/v-next-NOTES.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/roadmap/v-next-NOTES.md)

As each phase lands, this page will gain concrete screenshots/steps/migration notes.
