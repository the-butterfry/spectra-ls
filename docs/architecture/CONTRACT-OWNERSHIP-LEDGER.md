<!-- Description: Canonical ownership ledger for Spectra LS runtime/component contracts and migration disposition. -->
<!-- Version: 2026.06.21.1 -->
<!-- Last updated: 2026-06-21 -->

# Spectra LS Canonical Contract Ownership Ledger

This ledger is the single table-of-record for active contract surfaces across runtime (`packages/` + `esphome/`) and component (`custom_components/spectra_ls`) tracks.

Legend:

- **Owner**: authoritative design owner for the contract semantics.
- **Writer**: who actively mutates/populates the surface.
- **Readers**: primary consumers in active paths.
- **Authority**: `component-primary`, `runtime-primary`, or `compatibility`.
- **Fallback**: bounded fallback posture (`none`, `bounded`, `legacy-only`).
- **Retirement**: `implemented`, `compatibility-shimmed`, or `deferred with rationale`.

## Active contract table

| Contract surface | Owner | Writer | Primary readers | Authority | Fallback | Retirement disposition |
| --- | --- | --- | --- | --- | --- | --- |
| `input_select.ma_active_target` | Runtime compatibility lane (`ma_control_hub`) | Component service path (`spectra_ls.set_active_target`) in component mode; runtime compatibility flows as bounded lane | ESP runtime (`spectra-ls-audio-tcp.yaml`), HA templates, diagnostics | component-primary (normal operation) | bounded | compatibility-shimmed |
| `sensor.component_control_targets` / `sensor.component_control_hosts` / `sensor.component_control_host` / `sensor.component_control_port` | Component (`custom_components/spectra_ls`) | Component snapshot/coordinator | ESP runtime control-host ingest, validation templates | component-primary | bounded runtime helper fallback | implemented |
| `sensor.ma_control_targets` / `sensor.ma_control_hosts` / `sensor.ma_control_host` / `sensor.ma_control_port` | Runtime compatibility lane | Runtime templates; may consume component-first bridges | ESP fallback ingest, legacy templates, rollback workflows | compatibility | legacy-only | compatibility-shimmed |
| `sensor.component_now_playing_entity/state/title/artist/album/source` | Component | Component metadata stack + snapshot | ESP OLED/telemetry consumers, diagnostics templates | component-primary | bounded runtime now-playing fallback | implemented |
| `sensor.now_playing_entity/state/title/artist/album/source` | Runtime compatibility lane | Runtime templates (`ma_control_hub/template.inc`) | Runtime/legacy dashboards + fallback consumers | compatibility | legacy-only | compatibility-shimmed |
| `binary_sensor.component_now_playing_display_allowed` | Component | Component policy/metadata-prep surfaces | ESP display gates, validation templates | component-primary | bounded HA runtime contract visibility | implemented |
| `binary_sensor.now_playing_display_allowed` | Runtime compatibility lane | Runtime templates | ESP compatibility gates, fallback validation lanes | compatibility | legacy-only | compatibility-shimmed |
| `sensor.component_meta_candidates` / `binary_sensor.component_meta_low_confidence` | Component | Component resolver/diagnostics | P3/CA validation templates, runtime compatibility consumers | component-primary | bounded `sensor.ma_meta_candidates` fallback | implemented |
| `sensor.ma_meta_candidates` / `sensor.ma_meta_resolver` | Runtime compatibility lane | Runtime templates | Legacy diagnostics, fallback consumers | compatibility | legacy-only | compatibility-shimmed |
| `binary_sensor.component_metadata_override_active` / `sensor.component_metadata_override_entity` | Component | Component write-controls packet + diagnostics | ESP/runtime/template consumers | component-primary | bounded helper fallback where explicitly retained | implemented |
| `input_boolean.ma_meta_override` / `input_text.ma_meta_override_entity` | Runtime compatibility storage lane | Component service (`spectra_ls.set_metadata_override`) with guarded compatibility apply | Legacy templates/tools expecting helper storage | compatibility | bounded | compatibility-shimmed |
| `sensor.component_backend_profile` / `sensor.component_ma_api_url` | Component | Component snapshot bridge | Runtime REST/read-lane consumers, validation templates | component-primary | bounded `sensor.ma_server_profile_effective` / `sensor.ma_api_url` fallback | implemented |
| `sensor.ma_server_profile_effective` / `sensor.ma_api_url` | Runtime compatibility lane | Runtime helper/template stack | Compatibility consumers and rollback workflows | compatibility | legacy-only | compatibility-shimmed |
| `sensor.spectra_ls_system_esp_control_handoff_status` / `sensor.spectra_ls_system_esp_control_target` / `sensor.spectra_ls_system_esp_oled_status` | Runtime ESP lane | ESP runtime (`spectra-ls-system.yaml` + peripherals) | HA diagnostics templates and operator triage flows | runtime-primary (telemetry lane) | bounded | implemented |

## Two-track disposition summary

- **Runtime track:** compatibility + rollback-safe baseline retained; active consumer lanes increasingly component-first with bounded fallback where explicitly documented.
- **Component track:** primary control-plane and metadata/read contracts for net-new and active authority paths.

## Governance notes

- This ledger does **not** authorize unmanaged legacy re-expansion.
- Any behavior/contract change touching these surfaces must update this file and `docs/CHANGELOG.md` in the same slice.
- If strict lock-step updates are not feasible, add explicit `deferred with rationale` notes in changelog two-track disposition.
