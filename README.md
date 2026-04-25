<!-- Description: End-user overview for the Spectra L/S Home Assistant + ESPHome system. -->
<!-- Version: 2026.04.25.3 -->
<!-- Last updated: 2026-04-25 -->

# Spectra L/S

**⚠️ State of project (published 2026-04-16): Active heavy development on `main`. Not currently recommended for fresh production installations unless you are comfortable with frequent updates and occasional migration adjustments.**

Spectra Level / Source (Spectra L/S) is the tactile control surface for Home Assistant: instant, physical control over the moments that matter in your home.

Instead of digging through apps and dashboards, you can touch real controls for transport, lighting, volume, tone, scenes, and automations. The goal is simple: make everyday home control feel immediate, shared, and human.

Audio and lighting are the deepest focus areas today, but the model is broader: if Home Assistant can run it, Spectra L/S is designed to make it feel physical.

## Program Status — Legacy Sealed, Component Primary

Current operating posture:

- The legacy runtime path (`packages/` + `esphome/`) is now treated as a **sealed rollback-safe baseline**.
- The custom integration (`custom_components/spectra_ls`) is the **primary path for net-new control-plane and feature growth**.
- Component control-plane code now runs on **component-native source contracts** (active-target helper + discovery) and no longer depends on legacy `sensor.ma_*` / `sensor.now_playing_*` inputs.
- Runtime compatibility contracts now use pywiim-canonical control-path naming (`control_path=pywiim`) with bounded legacy alias compatibility where transition shims are still required.
- Runtime legacy alias pass-through (`route_linkplay_tcp`) is now hard-deprecated in active package diagnostics/gates; canonical runtime pass semantics are `route_pywiim`.
- ESP runtime host intake is now **component-authoritative and fail-closed** on `sensor.component_control_hosts` / `sensor.component_control_host` (legacy runtime fallback host sensors are no longer used in active send-path selection).
- Legacy direct transport/API lanes are now disabled by default behind explicit rollback gates:
  - Arylic HTTP polling lane: `${legacy_transport_httpapi_enabled}` (default `false`)
  - UPnP hack scripts: require `SPECTRA_ALLOW_LEGACY_UPNP=1`
- Runtime OLED metadata feed is aligned to **component-authoritative now-playing sensors** to keep metadata and control host in the same authority plane.
- Component registry/coordinator summary contracts are hardened against wrapper alias drift and payload-shape mismatch so control-host and metadata summary surfaces stay stable through restart/recovery windows.
- Component control-path semantics are now pywiim-canonical (`control_path=pywiim`, `route_decision=route_pywiim`) with compatibility-safe legacy alias diagnostics during monitor/runbook transition.
- The legacy `control-py` path is **archived exploration history** on `main` and is no longer a development or run target.
- Legacy path changes are still allowed for compatibility, safety, and rollback integrity — but not for unbounded new ownership behavior.

This keeps migration reversible while keeping forward development focused.

## Sealed Install Profile (fresh HA deployments)

For fresh Home Assistant installs, `custom_components/spectra_ls` now ships in a sealed component-first profile:

- default authority baseline is `component` on startup,
- diagnostics/phase-sequence debug services are not exposed in normal service UI,
- operator-facing service surface is intentionally small:
  - `spectra_ls.set_control_center_settings`
  - `spectra_ls.execute_control_center_input`

This is intended for dogfood/sandbox and clean installs where you want a production-lean package surface instead of migration-debug scaffolding.

## Hardware-First Context (Important)

Spectra L/S is a **hardware-first control stack**. The physical control surface comes first; Home Assistant orchestration is what makes that hardware useful across your home.

Core MCU/control path today:

- **ESP32-S3** — main ESPHome runtime/controller (UI/menu/orchestration path)
- **RP2040** — physical input capture firmware path (buttons/encoders/pots) feeding the controller runtime
- **OTA target authority** — use `esphome/spectra_ls_system/substitutions.yaml` `static_ip` for firmware upload target selection (current configured value: `192.168.10.40`).

In short: hardware first, then ESPHome + Home Assistant software stack.

## What It Feels Like to Use Spectra L/S

- **Instant physical control**: adjust sound and lights in real time from dedicated controls, not nested app screens.
- **Room-aware operation**: jump between rooms quickly and control the right targets without reconfiguring every step.
- **Always-clear feedback**: the OLED keeps navigation and active actions visible, so you always know what you’re controlling.
- **Reliable day-to-day flow**: physical actions stay responsive even when the smart-home stack is busy in the background.

## Why This Is Missing from Home Assistant

- Most smart-home workflows are app-first; Spectra L/S brings control back to physical space.
- No app gatekeeping for the actions that should be instantly accessible in your home.
- Shared spaces become more inclusive: anyone can walk up and use dedicated controls without training.
- It restores “eyes-up, hands-on” control for moments where touchscreens are friction.

Inspired by modern physical-control craftsmanship from [Condesa Electronics — Carmen SE](https://condesaelectronics.com/) and [Varia Instruments — RDM series](https://www.varia-instruments.com/), Spectra L/S is a minimal home DJ-mixer style control surface coupled with lighting, automation, and human-centric interaction for everyday Home Assistant control.

## Analog Surface for the Whole Home

- **Audio + lighting first**: these remain the deepest, most polished domains.
- **Mappable physical inputs**: buttons/sliders/encoders can be assigned to broader Home Assistant actions.
- **Touchscreen alternative**: where many dashboards are glass-first, Spectra L/S is designed as a tactile-first control surface.
- **Composable control model**: one hardware interface can drive media, scenes, automations, scripts, and domain-specific home controls.

## Works with the Audio Ecosystem You Already Have

- Music Assistant players
- Home Assistant media players
- WiiM-based rooms
- Arylic/LinkPlay-class endpoints
- Sendspin-class endpoints (roadmap target)
- AirPlay / Apple TV style sources
- Plex sessions/players (optional)

## Roadmap (Current Build Direction)

- We are actively building the Home Assistant sidebar **Spectra Control Center** in `custom_components/spectra_ls` as the primary product surface.
- Current execution focus: setup/onboarding, mapped-environment visibility, tuning/defaults/overrides, and bounded input-to-action execution under evidence-first gates.
- Control Center settings + execution contracts are already live and operator-verifiable via `spectra_ls.set_control_center_settings` and `spectra_ls.execute_control_center_input`.
- Runtime resilience follow-up: target-switch stale now-playing metadata hold behavior in ESP display path is hardened with explicit cache invalidation + metadata freshness quality gating, and cached OLED text replay is now fail-closed unless live transport-playing evidence is present.
- Ecosystem expansion remains capability-mapped and discovery-first; Sendspin-class and adjacent endpoint families are treated as roadmap integrations under the same safety/rollback gate discipline.
- Runtime control-target host resolution is discovery-only and fail-closed by contract: no install-specific hardcoded target IP bootstrap defaults in tracked product logic.
- Operator-grade validation artifacts remain the execution truth surface: `docs/testing/raw/*` checklists/monitors and synchronized roadmap ledgers.

## Documentation

Start here for setup, operations, and development workflow:

- [`docs/README.md`](docs/README.md)

Common entry points:

- Setup placeholders: [`docs/setup/SPECTRA-HA-CONFIG-PLACEHOLDERS.md`](docs/setup/SPECTRA-HA-CONFIG-PLACEHOLDERS.md)
- Latest project changes: [`docs/CHANGELOG.md`](docs/CHANGELOG.md)
- Developer onboarding/runbook: [`docs/developer/DEVELOPER-INSTRUCTIONS.md`](docs/developer/DEVELOPER-INSTRUCTIONS.md)

Need current execution status? Use [`docs/roadmap/v-next-NOTES.md`](docs/roadmap/v-next-NOTES.md).

Need to verify pywiim upstream sync status? Run the local checker: `bin/pywiim_sync_check.py`.

Need migration mechanics and slice evidence? Use:

- [`docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`](docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md)
- [`docs/testing/raw/`](docs/testing/raw/)

Need wiki navigation? Start at [`docs/wiki/Home.md`](docs/wiki/Home.md).
