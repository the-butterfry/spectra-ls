<!-- Description: Operator runbook for installing Spectra on a user-owned Home Assistant instance with explicit pass/fail checkpoints. -->
<!-- Version: 2026.04.22.6 -->
<!-- Last updated: 2026-04-22 -->

# Install on Your Own Home Assistant

Use this page when you want a clean, reproducible install on your own HA instance.

Goal: finish with working audio + lighting control, populated room/target menus, and rollback-safe evidence.

## Track A (current path): Runtime-first install

### 0) Before you start

- [ ] Home Assistant is running and reachable.
- [ ] ESPHome integration/add-on is installed.
- [ ] You can edit HA config files safely.
- [ ] You have a rollback snapshot/backup.

### 1) Prepare secrets and local values

- [ ] Put deployment-specific values in `secrets.yaml` or local includes.
- [ ] Do **not** commit IPs, tokens, or private host mappings.
- [ ] Resolve placeholders from [`docs/setup/SPECTRA-HA-CONFIG-PLACEHOLDERS.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/setup/SPECTRA-HA-CONFIG-PLACEHOLDERS.md).

### 2) Apply runtime config

- [ ] Apply required package configuration.
- [ ] Apply ESPHome runtime configuration.
- [ ] Ensure route/target helpers are present.

Expected result after Step 2:

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

## Track B (evolving): Custom component install flow

This becomes the preferred path as `custom_components/spectra_ls` matures through active roadmap slices.

Current required discovery note (applies now):

- [ ] After adding/updating files under `custom_components/spectra_ls/`, perform a full Home Assistant restart **before** using **Add Integration**.
- [ ] After restart, go to **Settings → Devices & Services → Add Integration** and search for `Spectra LS`.

Planned additions to this page:

- [ ] HACS/manual custom component install steps
- [ ] Config flow onboarding screens
- [ ] Registry/routing diagnostics walkthrough
- [ ] Migration checkpoints from runtime helpers to component surfaces
- [ ] First-time setup wizard expectations and diagnostics capture

Roadmap references:

- [`docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md)
- [`docs/roadmap/v-next-NOTES.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/roadmap/v-next-NOTES.md)

## Optional: wiki publishing token (docs automation only)

This is **not** needed to run Spectra in your home.

- Use `WIKI_FINE_GRAINED_PAT` only if you want GitHub Actions to publish changes from [`docs/wiki/*`](https://github.com/the-butterfry/spectra-ls/tree/main/docs/wiki) to the GitHub Wiki.
- Setup steps are in [`docs/wiki/README.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/wiki/README.md).

## Rollback checklist (operator safety)

- [ ] Keep known-good config backup before changing runtime files.
- [ ] If deploy fails, restore prior known-good config snapshot.
- [ ] Re-validate baseline controls before attempting incremental changes.

## Quick troubleshooting map

| Symptom | Likely cause | Action |
| --- | --- | --- |
| Room/target menus are empty | unresolved placeholders or helper bootstrap failure | Re-check [`docs/setup/SPECTRA-HA-CONFIG-PLACEHOLDERS.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/setup/SPECTRA-HA-CONFIG-PLACEHOLDERS.md), reload helpers, and revalidate template entities |
| Controls trigger but state never changes | route metadata unresolved or wrong target path | Verify `control_path` and `control_capable` surfaces, then confirm active target selection is valid |
| OTA/build succeeds but behavior is wrong | stale runtime state after deploy | Restart HA + integration path, then rerun integration verification checklist |
