---
description: "Workspace instructions for Home Assistant + ESPHome development (ESP-IDF + Arduino)."
---

<!-- Description: Workspace Copilot operating instructions for Home Assistant + ESPHome. -->
<!-- Version: 2026.04.19.11 -->
<!-- Last updated: 2026-04-19 -->

# GitHub Copilot Instructions — Home Assistant + ESPHome

## Quick Operating Rules (read first)
- Operate as a senior engineer for a **public-facing** HA + ESPHome product.
- Prefer root-cause fixes over symptom patches; keep changes minimal and reversible.
- If a request conflicts with safety/contract rules, call it out and offer the safest alternative.
- If uncertain and blocked by ambiguity, ask one concise question.

## Mandatory Workflow
- For `esphome/spectra_ls_system/**`, read `docs/roadmap/v-next-NOTES.md` before changes.
- For `esphome/control-py/**`, read `docs/control-py/NOTES-control-board-2.md` before changes.
- For any functional change, update `docs/CHANGELOG.md` **before** code edits.
- For any functionality or feature change, update or create the corresponding architecture/feature documentation in the same change set (for example runtime docs, control-hub docs, and cleanup/deprecation notes when relevant).
- Keep `README.md` aligned to current `main` direction in `docs/roadmap/v-next-NOTES.md`.
- Add a required docs-parity step for repo-state changes: update `README.md` in the same change set whenever contracts, behavior, architecture, structure, setup, or operator workflow materially changes.
- Add a required wiki-parity step for repo-state/operator-workflow changes: update `docs/wiki/` pages in the same change set when user-facing setup, deployment, integration, bug workflow, governance intake, or process routing changes.
- For ESPHome/runtime changes, enforce this sequence with no shortcuts: **edit → update README parity (if repo-state changed) → build/compile verify → fix failures → commit → push → OTA upload (when requested or implied) → post-upload verification evidence**.

## Parallel Custom-Component Program (Required)
- Develop `custom_components/spectra_ls` in parallel with the current runtime stack (`packages/` + `esphome/`) rather than as a big-bang replacement.
- Every feature slice must include a two-track disposition:
  1) current runtime implementation/shim/defer note, and
  2) custom-component implementation/shim/defer note.
- No feature is considered complete unless both tracks are mapped as: implemented, compatibility-shimmed, or explicitly deferred with rationale.
- Keep migration compatibility first: **shadow mode → parity validation → dual-write → domain cutover → legacy retirement**.
- Preserve existing helper/entity/script contracts during migration windows unless an approved migration step explicitly changes them.
- For each roadmap phase, update `docs/roadmap/v-next-NOTES.md` status and contract deltas in the same change set.
- Follow `docs/program/PARALLEL-PROGRAM-PLAYBOOK.md` as the execution system of record for slice templates, anti-detail-trap workflow, and parity controls.

## Roadmap + v-next + README Parity Discipline (Required)
- Documentation parity is mandatory for architecture/process/contract changes.
- In the same change set, keep these synchronized:
  1) `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`
  2) `docs/roadmap/v-next-NOTES.md`
  3) `docs/CHANGELOG.md`
  4) `README.md` (or explicit `README parity: no material repo-state change` note)
- If one of the required docs is not updated, the task is not complete.
- If plan direction changes mid-slice, log a **Plan Delta** and update roadmap + v-next before continuing.

## Documentation System + Legend Parity (Required)
- `README.md` is end-user facing; avoid embedding deep developer implementation detail there.
- Place developer and technical detail under `docs/` with `docs/README.md` as the index.
- Wiki content policy:
  - `docs/wiki/` SHOULD contain user/operator friendly navigation, setup/deploy runbooks, HA integration steps, bug-submission workflow, and high-level project operations.
  - `docs/wiki/` SHOULD NOT contain long low-level implementation internals, exhaustive architecture dumps, or branch-specific engineering notes better suited to `docs/architecture/`, `docs/roadmap/`, `docs/program/`, or `docs/notes/`.
- Wiring/layout/event protocol detail must be maintained in:
  - `docs/hardware/WIRING-LAYOUT-PROTOCOL.md` (detailed), and
  - `docs/circuitpy/RP-LEGEND.md` (summary + routing links).
- When updating legend/protocol docs, include direct links to fine-detail component/runtime sources where relevant.
- Optional wiki sync source is `docs/wiki/`; if wiki automation is enabled, keep wiki source pages synchronized with docs changes.

## GitHub Governance Parity (Required)
- Keep repository governance artifacts current and synchronized with process expectations:
  - `CONTRIBUTING.md`
  - `CODEOWNERS`
  - `CODE_OF_CONDUCT.md`
  - `SECURITY.md`
  - `.github/ISSUE_TEMPLATE/*`
  - `.github/pull_request_template.md`
  - `docs/governance/GITHUB-MASTERWORK-BLUEPRINT.md`
- When contribution/triage/release workflow changes, update governance docs/templates in the same change set as the process change.
- Prefer structured issue forms and PR checklists over free-form intake for reproducibility and triage quality.
- Keep README end-user focused; contributor workflow detail belongs in governance docs and templates.

## GitHub Structure Strategy (Current + Future)
- Current required strategy: **structured monorepo** rooted at `/mnt/homeassistant` with clear domain boundaries.
- Runtime sources remain in `packages/` + `esphome/`; parallel control-plane work lands in `custom_components/spectra_ls/`.
- Future split to separate repos is optional and deferred until maturity gates pass:
  1) stable component schema/API across releases,
  2) tested migration tooling,
  3) independent CI confidence per domain,
  4) operator docs updated for separated lifecycle.

## Verification Gates (Required, No Exceptions)

### Pre-Commit Build Gate (ESPHome)
- Never commit or push ESPHome/runtime YAML/C++ changes before a successful compile/build.
- Use local build automation when available (for Spectra: `bin/esphome_spectra_build_local.sh`).
- If build fails, treat as blocked for commit/push: fix root cause first, then rebuild.

### Pre-Push Evidence Gate
- Before `git push`, confirm and report:
  1) build status is success,
  2) critical diagnostics checked (if applicable),
  3) no known compile/runtime blockers remain.
- Do not present “ready/pushed” status while build is unverified or failing.

### Deployment Gate (OTA/Flash)
- When user asks to “build/upload to ESP/device” (or request implies deployment), OTA/flash is required to complete the task.
- For Spectra OTA flows, use upload helper with explicit device target (for example `--device <ip>`) and require `OTA successful` confirmation.
- If upload prerequisites are missing (device IP, connectivity, auth), surface the exact blocker and the next command needed.

### Post-Action Proof Requirement
- Report concrete proof lines, not assumptions:
  - Build: success/failure summary from tool output.
  - Upload: explicit `OTA successful` (or exact error).
  - Git sync: `HEAD` and `origin/main` short SHAs (must match when claiming synced).
- If any proof is missing, explicitly state the task is not complete.

## Scope + Branch Model
- Active repo scope:
  - `esphome/spectra_ls_system/`, `esphome/spectra_ls_system.yaml`
  - `esphome/control-py/`, `esphome/control-board-esp32-tcp.yaml`
  - `esphome/circuitpy/`
  - `packages/`
  - `docs/setup/SPECTRA-HA-CONFIG-PLACEHOLDERS.md`
- Keep `main` and `menu-only` concurrently operable.
- For shared contracts (RP events, control API, helper/entity contracts), require either:
  - paired update in both branches, or
  - explicit divergence note in `docs/CHANGELOG.md`.
- Complete `.github/SHARED-CONTRACT-CHECKLIST.md` before shared-contract merge.

## Path + Source-of-Truth Rules
- Authoritative workspace path is `/mnt/homeassistant` (avoid SMB mirror path unless explicitly requested).
- RP2040 firmware source of truth is live `CIRCUITPY/`; mirror is `esphome/circuitpy/`.
- Any RP2040 firmware change must update both live and mirror in same change set.
- Treat `esphome/control-py/previous/circuitpy/` as archived (do not edit/reference).

## Git + Productization Rules
- Never commit secrets or environment-local artifacts.
- Do not track per-user host/IP files (for example `*_tcp_host.yaml`) or site-specific mappings.
- Treat Spectra as an anonymized, user-portable product by default (no install-specific naming/contracts in tracked product logic).
- Prefer discovery-first + capability-mapped adaptation to each user’s HA entity topology; avoid hardcoded entity IDs unless explicitly required.
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

## Code Hygiene + Note Hygiene (Required)
- Keep code changes small, composable, and local to the root cause; avoid broad refactors unless explicitly requested.
- Prefer clarity over cleverness: extract repeated logic, remove dead branches, and keep naming stable/descriptive.
- For non-obvious logic, add concise in-code intent notes near the implementation (why/guardrail/contract), not long narrative blocks.
- Do not leave stale comments: when behavior changes, update or remove adjacent comments in the same change set.
- Keep architecture/contract explanations in docs, not only in code comments; update corresponding docs whenever behavior/contracts change.
- Minimum documentation sync for behavior/contract changes:
  1) `docs/CHANGELOG.md`
  2) relevant architecture doc(s) (for example runtime/control-hub/cleanup docs)
  3) `README.md` when operator-facing behavior or workflow materially changes
- When deprecating or freezing paths, mark them explicitly (`ARCHIVED`, `LEGACY`, or `DEPRECATED`) and provide the replacement/source-of-truth path.

## Move/Delete Safety Gate (No-Go if missing)
- Before any move/delete, explicitly provide:
  1) backup path outside tracked repo,
  2) planned `docs/CHANGELOG.md` entry,
  3) restore command/path.
- For deletes, perform backup + changelog + restore instructions in same change set.
- For renames/moves, record source and destination in `docs/CHANGELOG.md`.

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
- For custom integration branding/icons, follow official docs-first flow (no assumptions):
  - Verify current guidance from Home Assistant developer docs/blog and HACS docs before changing branding behavior.
  - For HA 2026.3+ custom integrations, place branding assets in `custom_components/<domain>/brand/`.
  - Supported filenames are: `icon.png`, `logo.png`, optional `dark_*` and `@2x` variants.
  - Do not rely on `manifest.json` `icon` key as the primary integration-brand source.
  - If branding assets change, note expected cache/restart effects in operator-facing docs/changelog.

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
- Never treat “commit pushed” as equivalent to “firmware deployed”; these are separate required checks.

## Code Audit Mode (when requested)
- Quick: top risks only.
- Standard (default): cross-file/state flow and concrete fixes.
- Thorough: full interaction/risk/testing pass.
- Output: short summary + numbered findings with severity + recommended fixes.

## Key References
- `docs/roadmap/v-next-NOTES.md`
- `docs/control-py/NOTES-control-board-2.md`
- `docs/hardware/WIRING-LAYOUT-PROTOCOL.md`
- `docs/circuitpy/RP-LEGEND.md`
- `docs/governance/GITHUB-MASTERWORK-BLUEPRINT.md`
- `docs/CHANGELOG.md`
- `esphome/spectra_ls_system.yaml`
- `esphome/control-board-esp32-tcp.yaml`
- `docs/notes/NOTES-wiim-api.md`
