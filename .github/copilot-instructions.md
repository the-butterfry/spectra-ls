---
description: "Workspace instructions for Home Assistant + ESPHome development (ESP-IDF + Arduino)."
---

<!-- Description: Workspace Copilot operating instructions for Home Assistant + ESPHome. -->
<!-- Version: 2026.04.18.2 -->
<!-- Last updated: 2026-04-18 -->

# GitHub Copilot Instructions — Home Assistant + ESPHome

## Quick Operating Rules (read first)
- Operate as a senior engineer for a **public-facing** HA + ESPHome product.
- Prefer root-cause fixes over symptom patches; keep changes minimal and reversible.
- If a request conflicts with safety/contract rules, call it out and offer the safest alternative.
- If uncertain and blocked by ambiguity, ask one concise question.

## Mandatory Workflow
- For `esphome/spectra_ls_system/**`, read `esphome/spectra_ls_system/v-next-NOTES.md` before changes.
- For `esphome/control-py/**`, read `esphome/control-py/NOTES-control-board-2.md` before changes.
- For any functional change, update `CHANGELOG.md` **before** code edits.
- Keep `README.md` aligned to current `main` direction in `v-next-NOTES.md`.

## Scope + Branch Model
- Active repo scope:
  - `esphome/spectra_ls_system/`, `esphome/spectra_ls_system.yaml`
  - `esphome/control-py/`, `esphome/control-board-esp32-tcp.yaml`
  - `esphome/circuitpy/`
  - `packages/`
  - `SPECTRA-HA-CONFIG-PLACEHOLDERS.md`
- Keep `main` and `menu-only` concurrently operable.
- For shared contracts (RP events, control API, helper/entity contracts), require either:
  - paired update in both branches, or
  - explicit divergence note in `CHANGELOG.md`.
- Complete `.github/SHARED-CONTRACT-CHECKLIST.md` before shared-contract merge.

## Path + Source-of-Truth Rules
- Authoritative workspace path is `/mnt/homeassistant` (avoid SMB mirror path unless explicitly requested).
- RP2040 firmware source of truth is live `CIRCUITPY/`; mirror is `esphome/circuitpy/`.
- Any RP2040 firmware change must update both live and mirror in same change set.
- Treat `esphome/control-py/previous/circuitpy/` as archived (do not edit/reference).

## Git + Productization Rules
- Never commit secrets or environment-local artifacts.
- Do not track per-user host/IP files (for example `*_tcp_host.yaml`) or site-specific mappings.
- Use `!secret` and ignored local files for deployment-specific values.
- Push cadence (required during active work): create and push a rollback checkpoint at least every 10 minutes **or** at each completed logical slice, whichever comes first.
- Checkpoint commits must be clearly labeled (for example `checkpoint:` / `wip:`), limited to relevant files, and never include secrets/local-only artifacts.
- For each logical change set: commit cleanly and push before ending session.

## File Change Governance
- Every edited text file must include/update metadata:
  - `Description:`
  - `Version: YYYY.MM.DD.N`
  - `Last updated: YYYY-MM-DD`
- Applies to repo-owned text files in active paths (`esphome/`, `packages/`, docs/notes/instructions).
- Exclude binary/vendor/generated artifacts.

## Move/Delete Safety Gate (No-Go if missing)
- Before any move/delete, explicitly provide:
  1) backup path outside tracked repo,
  2) planned `CHANGELOG.md` entry,
  3) restore command/path.
- For deletes, perform backup + changelog + restore instructions in same change set.
- For renames/moves, record source and destination in `CHANGELOG.md`.

## Engineering Standards

### ESPHome
- Produce valid ESP32 Arduino + ESP-IDF compatible YAML.
- Include `esphome:`, `wifi:`, `api:`, `ota:`, `logger:` unless explicitly told otherwise.
- Use `substitutions`, stable/descriptive `id`, and `internal: true` for non-user entities.
- Guard lambdas for missing state (`has_state`) and avoid duplicate declarations.
- Keep section ordering/style consistent and avoid unrelated reformatting.
- Menu select must work from **both** encoder center press and dedicated Select button.

### Home Assistant
- Use correct `device_class`, `state_class`, and units.
- Prefer helper-backed controls (`input_select`, `input_text`, etc.) for user tuning.
- Keep automations idempotent and guarded against missing entities.
- Do not rename helpers/entity IDs without explicit approval + migration note.
- During diagnosis, provide copy/paste Developer Tools templates instead of asking for manual checks.

### Routing/Control Policy
- Discovery-first onboarding is default.
- Static/manual host overrides are fallback-only and disabled by default.
- Expose and honor per-target route/capability metadata (`control_path`, `hardware_family`, `control_capable`, optional `capabilities`).
- Only route through currently supported control paths.

## Validation + Reliability
- Validate ESPHome configs after edits when possible; clearly call out anything untested.
- Avoid excessive flash writes (`restore_value: yes` only when needed).
- Rate-limit noisy control actions (encoders/sliders).
- Avoid breaking changes to helper/entity contracts without explicit warning.

## Code Audit Mode (when requested)
- Quick: top risks only.
- Standard (default): cross-file/state flow and concrete fixes.
- Thorough: full interaction/risk/testing pass.
- Output: short summary + numbered findings with severity + recommended fixes.

## Key References
- `esphome/spectra_ls_system/v-next-NOTES.md`
- `esphome/control-py/NOTES-control-board-2.md`
- `CHANGELOG.md`
- `esphome/spectra_ls_system.yaml`
- `esphome/control-board-esp32-tcp.yaml`
- `esphome/control-py/NOTES-wiim-api.md`
