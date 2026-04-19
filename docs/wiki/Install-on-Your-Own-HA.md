<!-- Description: Strict operator checklist for installing Spectra on a user-owned Home Assistant instance with runtime and custom-component tracks. -->
<!-- Version: 2026.04.19.2 -->
<!-- Last updated: 2026-04-19 -->

# Install on Your Own Home Assistant

Use this as a strict checklist.

## Track A (current path): Runtime-first install

### 0) Prerequisites

- [ ] Home Assistant is running and reachable.
- [ ] ESPHome integration/add-on is installed.
- [ ] You can edit HA config files safely.
- [ ] You have a rollback snapshot/backup.

### 1) Prepare secrets and local values

- [ ] Put deployment-specific values in `secrets.yaml` or local includes.
- [ ] Do **not** commit IPs, tokens, or private host mappings.
- [ ] Resolve placeholders from `docs/setup/SPECTRA-HA-CONFIG-PLACEHOLDERS.md`.

### 2) Apply runtime config

- [ ] Apply required package configuration.
- [ ] Apply ESPHome runtime configuration.
- [ ] Ensure route/target helpers are present.

Expected result:

- [ ] Required entities/helpers appear in Home Assistant with valid states.

### 3) Validate + deploy

- [ ] Validate Home Assistant config.
- [ ] Compile ESPHome successfully.
- [ ] Upload OTA/flash if required for your target.
- [ ] Confirm runtime entities and controls appear as expected.

Evidence to keep (copy/paste into notes/issue if needed):

- [ ] Build success output snippet.
- [ ] OTA success output snippet (if applicable).
- [ ] One screenshot or state dump showing control entities populated.

### 4) Integration verification

- [ ] Audio controls work and reflect state.
- [ ] Lighting controls work and reflect state.
- [ ] Room/target selection is populated (not placeholders only).
- [ ] Control target/routing behavior is stable across reload/restart.

Failure indicators (stop and investigate):

- [ ] Placeholder-only room/target lists remain after reload.
- [ ] Controls issue commands but entity state never updates.
- [ ] Route metadata (`control_path`, `control_capable`) is missing/invalid.

### 5) If something breaks

- [ ] File a bug using the issue form.
- [ ] Include logs, repro steps, affected area, and impact.
- [ ] Link to `Welcome-README-and-Bug-Workflow` for triage flow.

## Track B (upcoming): Custom component install flow (stub)

This will become the preferred install path as `custom_components/spectra_ls` matures.

Planned additions to this page:

- [ ] HACS/manual custom component install steps
- [ ] Config flow onboarding screens
- [ ] Registry/routing diagnostics walkthrough
- [ ] Migration checkpoints from runtime helpers to component surfaces
- [ ] First-time setup wizard expectations and diagnostics capture

Roadmap references:

- `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`
- `docs/roadmap/v-next-NOTES.md`

## Optional: wiki publishing token (docs automation only)

This is **not** needed to run Spectra in your home.

- Use `WIKI_FINE_GRAINED_PAT` only if you want GitHub Actions to publish `docs/wiki/*` to the GitHub Wiki.
- Setup steps are in `docs/wiki/README.md`.

## Rollback checklist (operator safety)

- [ ] Keep known-good config backup before changing runtime files.
- [ ] If deploy fails, restore prior known-good config snapshot.
- [ ] Re-validate baseline controls before attempting incremental changes.
