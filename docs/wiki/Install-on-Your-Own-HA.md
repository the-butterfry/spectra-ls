<!-- Description: Operator runbook for installing Spectra on a user-owned Home Assistant instance with explicit pass/fail checkpoints. -->
<!-- Version: 2026.08.01.2 -->
<!-- Last updated: 2026-08-01 -->

# Install on Your Own Home Assistant

Use this for a practical, reproducible install.

Target outcome: audio + lighting control working, room/target menus populated, and enough evidence to debug quickly if anything misbehaves.

## Done means all of these are true

- HA config validates
- ESPHome build and deploy complete
- room/target options are real (not placeholders)
- at least one audio action and one lighting action pass

## 1) Preflight

- [ ] Home Assistant is reachable
- [ ] ESPHome integration/add-on is available
- [ ] You have a backup/snapshot

## 2) Local values and secrets

- [ ] Put install-specific values in `secrets.yaml` or local includes
- [ ] Do not commit tokens/IPs/private host mappings
- [ ] Resolve placeholders from [`docs/setup/SPECTRA-HA-CONFIG-PLACEHOLDERS.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/setup/SPECTRA-HA-CONFIG-PLACEHOLDERS.md)

## 3) Apply config

- [ ] Apply package/runtime config
- [ ] Apply ESPHome config
- [ ] Confirm expected entities/helpers appear in HA

## 4) Validate and deploy

- [ ] Validate HA config
- [ ] Compile ESPHome
- [ ] Upload OTA/flash as needed
- [ ] Verify entities/controls in HA

Keep these proof lines:

- build success output
- OTA success output (if used)
- one screenshot/state dump of populated control entities

### OTA schema reminder

Use modern `ota:` platform entries (`esphome`, `web_server`). Avoid legacy `web_server.ota: true` syntax.

## 5) Functional verification

- [ ] Audio control works and reflects state
- [ ] Lighting control works and reflects state
- [ ] Room/target selection is populated
- [ ] Routing stays stable across restart/reload

## 6) If it fails

Don’t guess—capture evidence and route it:

1. [Operations Runbooks](Operations-Runbooks)
2. [Welcome, README, and Bug Workflow](Welcome-README-and-Bug-Workflow)

## Custom component install note (current reality)

Component-first setup is still evolving. For now, if you update `custom_components/spectra_ls/`:

1. Restart Home Assistant fully
2. Use **Settings → Devices & Services → Add Integration**
3. Configure include/exclude policy for `media_player` routing/metadata selectors

Roadmap source:

- [`docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md)
- [`docs/roadmap/v-next-NOTES.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/roadmap/v-next-NOTES.md)
