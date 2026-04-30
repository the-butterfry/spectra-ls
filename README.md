<!-- Description: End-user overview for the Spectra L/S Home Assistant + ESPHome system. -->
<!-- Version: 2026.04.29.24 -->
<!-- Last updated: 2026-04-29 -->

# Spectra L/S

**⚠️ State of project (published 2026-04-16): Active heavy development on `main`. Not currently recommended for fresh production installations unless you are comfortable with frequent updates and occasional migration adjustments.**

Spectra Level / Source (Spectra L/S) is the tactile control surface for Home Assistant: instant, physical control over the moments that matter in your home.

Instead of digging through apps and dashboards, you can touch real controls for transport, lighting, volume, tone, scenes, and automations. The goal is simple: make everyday home control feel immediate, shared, and human.

Audio and lighting are the deepest focus areas today, but the model is broader: if Home Assistant can run it, Spectra L/S is designed to make it feel physical.

## Program Status — Legacy Sealed, Component Primary

Current operating posture:

- The legacy runtime path (`packages/` + `esphome/`) is now treated as a **sealed rollback-safe baseline**.
- The custom integration (`custom_components/spectra_ls`) is the **primary path for net-new control-plane and feature growth**.
- The legacy `control-py` path is **archived exploration history** on `main` and is no longer a development or run target.
- Legacy path changes are still allowed for compatibility, safety, and rollback integrity — but not for unbounded new ownership behavior.

This keeps migration reversible while keeping forward development focused.

## Hardware-First Context (Important)

Spectra L/S is a **hardware-first control stack**. The physical control surface comes first; Home Assistant orchestration is what makes that hardware useful across your home.

Core MCU/control path today:

- **ESP32-S3** — main ESPHome runtime/controller (UI/menu/orchestration path)
- **RP2040** — physical input capture firmware path (buttons/encoders/pots) feeding the controller runtime

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
- Ecosystem expansion remains capability-mapped and discovery-first; Sendspin-class and adjacent endpoint families are treated as roadmap integrations under the same safety/rollback gate discipline.
- Runtime control-target host resolution is discovery-only and fail-closed by contract: no install-specific hardcoded target IP bootstrap defaults in tracked product logic.
- Fast MA backend testing is now helper-driven in runtime: use `input_select.ma_server_profile` (`beta` / `stable` / `manual`) with profile URL helpers to switch endpoints quickly without editing package YAML.
- HACS publishing cadence is release-tag driven (not commit-driven): keep iterative work on `main`, then publish to HACS only when a tagged release is intentionally cut.
- ESPHome runtime deploy guidance is aligned to 2026.4.x OTA schema: `ota` platform entries (`esphome` + `web_server`) are the supported path, and legacy `web_server.ota: true` usage should be treated as incompatible in modern builds.
- Operator-grade validation artifacts remain the execution truth surface: `docs/testing/raw/*` checklists/monitors and synchronized roadmap ledgers.
- Startup authority handling is hardened to avoid mixed boot semantics across migration windows, and deterministic diagnostics now include source/provenance + playback-modality context for faster operator triage.

## Documentation

Start here for setup, operations, and development workflow:

- [`docs/README.md`](docs/README.md)

Common entry points:

- Setup placeholders: [`docs/setup/SPECTRA-HA-CONFIG-PLACEHOLDERS.md`](docs/setup/SPECTRA-HA-CONFIG-PLACEHOLDERS.md)
- Latest project changes: [`docs/CHANGELOG.md`](docs/CHANGELOG.md)
- Developer onboarding/runbook: [`docs/developer/DEVELOPER-INSTRUCTIONS.md`](docs/developer/DEVELOPER-INSTRUCTIONS.md)

Need current execution status? Use [`docs/roadmap/v-next-NOTES.md`](docs/roadmap/v-next-NOTES.md).

Need migration mechanics and slice evidence? Use:

- [`docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`](docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md)
- [`docs/testing/raw/`](docs/testing/raw/)

Need wiki navigation? Start at [`docs/wiki/Home.md`](docs/wiki/Home.md).
