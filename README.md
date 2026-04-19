<!-- Description: End-user overview for the Spectra L/S Home Assistant + ESPHome system. -->
<!-- Version: 2026.04.19.10 -->
<!-- Last updated: 2026-04-19 -->

# Spectra L/S

**⚠️ State of project (published 2026-04-16): Active heavy development on `main`. Not currently recommended for fresh production installations unless you are comfortable with frequent updates and occasional migration adjustments.**

Spectra Level / Source (Spectra L/S) is the tactile control surface for Home Assistant: instant, physical control over the moments that matter in your home.

Instead of digging through apps and dashboards, you can touch real controls for transport, lighting, volume, tone, scenes, and automations. The goal is simple: make everyday home control feel immediate, shared, and human.

Audio and lighting are the deepest focus areas today, but the model is broader: if Home Assistant can run it, Spectra L/S is designed to make it feel physical.

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

Inspired by modern physical-control craftsmanship from [Condesa Electronics — Carmen SE](https://condesaelectronics.com/) and [Varia Instruments — RDM series](https://www.varia-instruments.com/), Spectra L/S adapts that tactile design ethos for everyday Home Assistant control.

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
- AirPlay / Apple TV style sources
- Plex sessions/players (optional)

## Documentation

For setup, operations, developer onboarding, architecture notes, and deep technical references, start here:

- `docs/README.md`

Common entry points:

- Setup placeholders: `docs/setup/SPECTRA-HA-CONFIG-PLACEHOLDERS.md`
- Latest project changes: `docs/CHANGELOG.md`
- Developer onboarding/runbook: `docs/developer/DEVELOPER-INSTRUCTIONS.md`
