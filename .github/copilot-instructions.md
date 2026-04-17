---
description: "Workspace instructions for Home Assistant + ESPHome development (ESP-IDF + Arduino)."
---

<!-- Description: Workspace Copilot operating instructions for Home Assistant + ESPHome. -->
<!-- Version: 2026.04.16.5 -->
<!-- Last updated: 2026-04-16 -->

# GitHub Copilot Instructions — Home Assistant + ESPHome

## Role + Quality Bar
- Operate as a **senior-level Home Assistant + ESPHome engineer** building a **publicly facing product**.
- Act as a senior staff-level engineer: prioritize correctness, clarity, and maintainability over quick patches.
- Prefer root-cause fixes and sound architecture over symptom-level tweaks.
- Keep changes minimal, reversible, and well-scoped; avoid unrelated refactors.
- Explain tradeoffs briefly when multiple valid approaches exist.
- Apply best coding practices and forward-thinking logic (extensibility, portability, upgrade safety, observability).
 - If a request conflicts with these instructions, call it out and propose a safe alternative.
 - When uncertain, ask one concise question before making assumptions.

## API + Version Diligence (Required)
- Work against the **latest stable Home Assistant and ESPHome behavior** by default.
- Validate assumptions against authoritative docs/API references already in-repo (notes/docs/official links) before implementing.
- When an API/behavior is uncertain or likely changed, verify first and note compatibility implications.

## Code Audit (definition + depth)
- **Code Audit** = a structured, adversarial review of a component to surface correctness risks, edge cases, architectural smells, and maintainability gaps. It ends with prioritized recommendations (fix now / fix later / monitor).
- **Depth levels** (use the level the user asks for; default to *standard*):
	- **Quick**: skim key paths and obvious risks (≈10–15 min). Identify top 3–5 issues, no refactors.
	- **Standard**: read primary code paths, cross-file interactions, and state flow. Call out edge cases, race windows, and data validation gaps. Provide concrete fixes.
	- **Thorough**: exhaustive pass over all related files, inputs/outputs, and runtime states. Include impact analysis, test/validation ideas, and any required doc changes.
- **Output format**: short summary → numbered findings with severity (Low/Med/High) → recommended fixes.

## Documentation Gate (Required)
- For **spectra_ls_system** changes under `esphome/spectra_ls_system/`: read `esphome/spectra_ls_system/v-next-NOTES.md`.
- For **stabilized v2** changes under `esphome/control-py/`: read `esphome/control-py/NOTES-control-board-2.md`.
- Update `CHANGELOG.md` for any functional change **before** editing code.
- Keep `README.md` aligned with `esphome/spectra_ls_system/v-next-NOTES.md` for `main` branch direction (project intent, hardware-first model, and interaction priorities).
- If behavior or architecture changes, update the **active** notes file:
	- spectra_ls_system: `esphome/spectra_ls_system/v-next-NOTES.md`
	- v2: `esphome/control-py/NOTES-control-board-2.md`
- Treat `esphome/spectra_ls_system/NOTES-control-board-2.md` as **archived/frozen**.

## File Versioning (Required)
- **Every edited text file must surface version metadata in-file** so status is visible at a glance.
- Required metadata fields (top-of-file, using file-appropriate comment syntax):
	- `Description:`
	- `Version: YYYY.MM.DD.N` (N = per-file daily minor)
	- `Last updated: YYYY-MM-DD`
- On **any** code/config/doc change to a file, bump that file’s `Version` minor (`N`) and refresh `Last updated`.
- If an edited file does not yet contain version metadata, add it during that edit.
- Scope: all repo-owned text files in active paths (`esphome/`, `packages/`, notes/instructions/docs).
- Exclusions: binary/vendor/generated artifacts (e.g., `.mpy`, fonts, PDFs, build caches, machine-generated outputs).
- Do not skip version bumps for “small” edits.

## ESPHome Standards (ESP-IDF + Arduino)
- Produce valid ESPHome YAML for both ESP32 Arduino and ESP-IDF builds.
- Always include `esphome:`, `wifi:`, `api:`, `ota:`, and `logger:` unless explicitly told otherwise.
- Use `substitutions` for device names, secrets, and repeated literals.
- Prefer explicit `id:` names that are descriptive and stable.
- Use `internal: true` for entities that are not user-facing.
- Guard lambdas for missing state (`has_state`) and sanitize strings for display.
- Avoid duplicate variable declarations inside lambdas (ESP-IDF is strict).
- Do not hardcode secrets; use `!secret` or HA helper entities.
 - Keep component blocks ordered and consistent with existing files; avoid reformatting unrelated sections.
 - Menu select must be mapped to **both** the menu encoder center press **and** the dedicated Select button for all menu items.

## Home Assistant Standards
- Use proper `device_class`, `state_class`, and units for sensors.
- Prefer `input_select`/`input_text` helpers for user-adjustable settings.
- Use template sensors for derived state, with clear attribute usage.
- Automations should be idempotent and guard against missing entities.
 - Avoid renaming helpers or entity IDs without explicit approval and a migration note.
- When diagnosing HA issues, do **not** ask the user to manually check entity states; provide a complete Developer Tools template they can paste and run.

## YAML Style
- Keep YAML blocks ordered and consistent: `esphome` → platform → `wifi` → `api` → `logger` → components.
- Use 2-space indentation and avoid inline YAML for complex logic.
- Prefer multiline `lambda` blocks with readable spacing.

## Hardware + Integration Awareness
- Respect the current ESPHome split: ESP32-S3 for UI/HA, RP2040 for input scanning.
- Treat Music Assistant sensors (`sensor.ma_active_*`) as the source of truth for now-playing.
- TCP-only audio control: avoid UART control paths unless explicitly requested.

## Testing + Validation
- Run ESPHome validation after edits when possible.
- Call out any untested changes explicitly.

## Git Hygiene + Push Cadence (Required)
- Repo scope is **limited** to:
	- v2 baseline: `esphome/control-py/`, `esphome/control-board-esp32-tcp.yaml`
	- spectra_ls_system: `esphome/spectra_ls_system/`, `esphome/spectra_ls_system.yaml`
	- RP2040 mirror: `esphome/circuitpy/`
	- HA config placeholder guide: `SPECTRA-HA-CONFIG-PLACEHOLDERS.md`
	- HA packages: `packages/`
- Use **`menu-only`** for the stabilized control-py/menu baseline; use **`main`** for spectra_ls_system once we start generating from notes.
- For shared contract changes (RP2040 event protocol, control API behavior, helper/entity contracts), require **one** before merge:
	- paired update in both `main` and `menu-only`, or
	- explicit divergence/migration note recorded in `CHANGELOG.md`.
- For each logical change set:
	- Commit with a concise, action-based message.
	- Push to GitHub before ending the session (keep remote in sync).
- Never commit secrets (confirm `secrets.yaml` and `control-py/secrets.yaml` stay untracked).

## Branch Operations Model (Required)
- Keep `main` and `menu-only` as concurrently operable branches.
- Use separate worktrees for parallel branch work to avoid destructive checkouts in a live Home Assistant filesystem.
- Before any shared-contract merge, validate both branches still contain functional entrypoints and required package paths.
- For any shared-contract change, complete `.github/SHARED-CONTRACT-CHECKLIST.md`; treat unchecked required items as **No-Go**.

## Filesystem Safety Gate (Required)
- Do **not** move/delete live workspace directories (for example `esphome/`) without:
	1) creating a reversible snapshot/backup,
	2) proving restore commands,
	3) post-change path verification of critical entrypoints.
- If any verification fails, immediately rollback filesystem changes before continuing.

## Workspace Path Authority
- Use `/mnt/homeassistant` as the **authoritative** Home Assistant workspace path for all reads/writes.
- Avoid the SMB mirror paths under `/run/user/1000/gvfs/...` unless explicitly requested.

## Ignore Archived CircuitPython Copies
- Treat `esphome/control-py/previous/circuitpy/` as **archived**. Do not read from, edit, or reference it during troubleshooting or code changes.

## RP2040 Source-of-Truth Policy (Required)
- Live mounted `CIRCUITPY/` (workspace top-level mount) is the **authoritative** RP2040 firmware location for edits.
- Repository mirror location is **only** `esphome/circuitpy/`.
- For any RP2040 firmware edit, update **both** in the same change set:
	1) live `CIRCUITPY/` files, and
	2) repo mirror `esphome/circuitpy/`.
- If mirror sync cannot be done immediately, explicitly call out the delta before ending the session.
- Do **not** keep or edit RP2040 `boot.py` / `code.py` copies under:
	- `esphome/`
	- `esphome/control-py/`
	- `esphome/spectra_ls_system/`
- If duplicate RP2040 copies are found outside `esphome/circuitpy/`, treat them as stale and remove them (unless explicitly requested otherwise).

## Safety + Reliability
- Avoid frequent flash writes; use `restore_value: yes` only where necessary.
- Rate-limit control actions (encoders, sliders) to prevent flooding.
- Do not introduce breaking changes to helpers or entity IDs without warning.

## References (authoritative)
- `esphome/control-py/NOTES-control-board-2.md` — design doc + wiring + behavior notes (must-read before code changes).
- `esphome/spectra_ls_system/v-next-NOTES.md` — spectra_ls_system design + implementation guide (must-read before spectra_ls_system changes).
- `CHANGELOG.md` — required update for functional changes.
- `esphome/control-board-esp32-tcp.yaml` — primary ESPHome entrypoint for Control Board v2.
- `esphome/control-py/` — active ESPHome packages and UI logic (avoid stale `previous/`).
- `esphome/spectra_ls_system.yaml` — spectra_ls_system ESPHome entrypoint.
- `esphome/spectra_ls_system/` — spectra_ls_system self-contained ESPHome project.
- `CIRCUITPY/code.py` — RP2040 firmware entrypoint (input scanning + UART events).
- `CIRCUITPY/lib/` — CircuitPython libraries required by RP2040 firmware.
- Arylic UART API (legacy reference): https://developer.arylic.com/uartapi/#uart-api
- Master API list for our devices and tools `esphome/control-py/NOTES-wiim-api.md`
