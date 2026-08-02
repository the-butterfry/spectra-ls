<!-- Description: End-user overview for the Spectra L/S Home Assistant + ESPHome system. -->
<!-- Version: 2026.08.01.3 -->
<!-- Last updated: 2026-08-01 -->

# Spectra L/S

**⚠️ State of project (reviewed 2026-08-01): Public beta. Fresh pilot installs are reasonable for experienced Home Assistant operators. If you need low-change, enterprise-style stability, wait for a declared stable milestone because `main` still moves fast.**

Spectra Level / Source (Spectra L/S) is the tactile control surface for Home Assistant: instant, physical control over the moments that matter in your home.

Instead of digging through apps and dashboards, you can touch real controls for transport, lighting, volume, tone, scenes, and automations. The goal is simple: make everyday home control feel immediate, shared, and human.

Audio and lighting are the deepest focus areas today, but the model is broader: if Home Assistant can run it, Spectra L/S is designed to make it feel physical.

## Program Status — Home Assistant Integration First

Current operating posture:

- The Home Assistant integration at `custom_components/spectra_ls` is the main path for active behavior and feature work.
- The runtime files in `packages/` + `esphome/` consume integration-owned contracts.
- Active target, host routing, and metadata behavior are driven by integration contracts and services.
- New install-specific hardcoded entity IDs/private host literals are CI-blocked in active product logic paths.
- Current build targets are the active integration and system runtime paths documented under `docs/`.

This keeps operations stable while keeping active development focused.

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
- HA setup-flow foundation now includes guided entity-policy capture for routing/metadata include-exclude lists (component options flow), establishing the first end-user onboarding framework for per-install entity curation.
- Control Center settings + execution contracts are already live and operator-verifiable via `spectra_ls.set_control_center_settings` and `spectra_ls.execute_control_center_input`.
- Host-control cutover readiness is service-addressable via `spectra_ls.get_host_cutover_gate` (with fail-closed options for readiness/activation gating in automation workflows).
- Canonical playback/progress robustness is now formalized as an integration-first architecture program (`custom_components/spectra_ls`) with multi-source field-level resolution, provenance, and deterministic healing (`docs/architecture/COMPONENT-DATA-FABRIC-ARCHITECTURE.md`).
- Canonical ownership/read/write authority across runtime + component surfaces is now centralized in a single ledger: `docs/architecture/CONTRACT-OWNERSHIP-LEDGER.md`.
- Canonical execution is codified as `CA-S01..CA-S08` (CORE/PROJ/COMPAT/OPS lanes), and those baseline CA slices are now validated; active work continues in post-CA parity/hardening lanes (see `docs/roadmap/v-next-NOTES.md`).
- Architecture governance is explicit and normative with token-locked MA authority semantics and deterministic health-state diagnostics.
- Ecosystem expansion remains capability-mapped and discovery-first; Sendspin-class and adjacent endpoint families are treated as roadmap integrations under the same safety/rollback gate discipline.
- Runtime control-target host resolution is discovery-only and fail-closed by contract: no install-specific hardcoded target IP bootstrap defaults in tracked product logic.
- Fast MA backend testing is now helper-driven in runtime: use `input_select.ma_server_profile` (`beta` / `stable` / `manual`) with profile URL helpers to switch endpoints quickly without editing package YAML.
- HACS publishing cadence is release-tag driven (not commit-driven): keep iterative work on `main`, then publish to HACS only when a tagged release is intentionally cut.
- ESPHome runtime deploy guidance is aligned to 2026.4.x OTA schema: `ota` platform entries (`esphome` + `web_server`) are the supported path, and older `web_server.ota: true` usage should be treated as incompatible in modern builds.
- Operator-grade validation artifacts remain the execution truth surface: `docs/testing/raw/*` checklists/monitors and synchronized roadmap ledgers.
- Startup authority handling is hardened to avoid mixed boot semantics across migration windows, and deterministic diagnostics now include source/provenance + playback-modality context for faster operator triage.

## Compatibility baseline (verified vs expected)

This section reflects an evidence-first compatibility audit against current upstream release notes plus local code-surface checks. It is intentionally conservative:

- **Verified up to (audit baseline):**
  - Home Assistant Core: **2026.6.4**
  - Home Assistant OS: **18.0**
  - ESPHome: **2026.6.2**
  - ESPHome add-on: **2026.6.2**
  - ESPHome Device Builder backend: **1.0.12**
  - ESPHome Device Builder frontend: **0.1.174**

- **What “verified” means in this context:**
  - Upstream changelog/release deltas were reviewed and compared to current Spectra runtime + component contract surfaces.
  - No blocking incompatibilities were identified in the current static code/config surface.

- **Expected (pending live soak confirmation):**
  - Build/deploy/runtime behavior remains expected-compatible on the versions above, but should still be confirmed with live compile + runtime validation evidence for each environment.

- **Known watch items:**
  - BLE scanning default changes in HA/ESPHome may affect operational behavior on `bluetooth_proxy` nodes; treat as an operational tuning watchpoint.
  - Compatibility statements here are contract-surface/audit based, not a blanket guarantee for every custom deployment topology.

## Spectra LS Remote (new additive lane)

- A new standalone ESPHome node (`spectra-ls-remote`) is being introduced as a **movable coffee-table control box**.
- Current input model is encoder-first: rotary volume step control + encoder center-press play/pause + dedicated momentary next-track button.
- Power direction is battery-aware by design (final target board: ESP32-S3-DEVKIT-LIPO with charging + deep-sleep + battery telemetry).
- Communication direction is BLE-bridge-primary for low wake overhead, with Wi-Fi retained as secondary OTA/service lane.
- Scope/progress source of truth: `docs/program/SPECTRA-LS-REMOTE-SCOPE-PROGRESS.md`.
- Separate local operations helpers:
  - build: `bin/esphome_spectra_remote_build_local.sh`
  - upload: `bin/esphome_spectra_remote_upload_local.sh`

## Documentation

Start here for setup, operations, and development workflow:

- [`docs/README.md`](docs/README.md)

Common entry points:

- Setup placeholders: [`docs/setup/SPECTRA-HA-CONFIG-PLACEHOLDERS.md`](docs/setup/SPECTRA-HA-CONFIG-PLACEHOLDERS.md)
- Latest project changes: [`docs/CHANGELOG.md`](docs/CHANGELOG.md)
- Parallel Amped integration entrypoint (additive, current runtime preserved): [`esphome/spectra_ls_system_amped_combined.yaml`](esphome/spectra_ls_system_amped_combined.yaml)
- Developer onboarding/runbook: [`docs/developer/DEVELOPER-INSTRUCTIONS.md`](docs/developer/DEVELOPER-INSTRUCTIONS.md)
- WLED palette room E2E test runbook: [`docs/testing/raw/wled_palette_room_e2e_runbook.md`](docs/testing/raw/wled_palette_room_e2e_runbook.md)

Need current execution status? Use [`docs/roadmap/v-next-NOTES.md`](docs/roadmap/v-next-NOTES.md).

Need migration mechanics and slice evidence? Use:

- [`docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`](docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md)
- [`docs/testing/raw/`](docs/testing/raw/)

Need wiki navigation? Start at [`docs/wiki/Home.md`](docs/wiki/Home.md).

## Reader journey (start in 60 seconds)

- **I want to install and run Spectra** → [`docs/wiki/Install-on-Your-Own-HA.md`](docs/wiki/Install-on-Your-Own-HA.md)
- **I already installed and need setup/deploy verification** → [`docs/wiki/User-Setup-Deploy-and-HA-Integration.md`](docs/wiki/User-Setup-Deploy-and-HA-Integration.md)
- **Something broke and I need the right bug path** → [`docs/wiki/Welcome-README-and-Bug-Workflow.md`](docs/wiki/Welcome-README-and-Bug-Workflow.md)
- **I’m contributing code/docs** → [`docs/wiki/Contributing-Workflow.md`](docs/wiki/Contributing-Workflow.md)
