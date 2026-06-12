<!-- Description: Operator runbook for end-to-end WLED palette sampling, room-entity discovery, and apply-path validation for Spectra LS integration prep. -->
<!-- Version: 2026.06.11.1 -->
<!-- Last updated: 2026-06-11 -->

# WLED Palette → Room Lights E2E Runbook

## Purpose

Run a deterministic end-to-end test that:

1. Samples WLED colors from either direct WLED API (`--wled-url`) or a Home Assistant WLED entity source.
2. Resolves room light entities from Home Assistant area contracts (or explicit fallback entities).
3. Applies sampled colors to room lights (or dry-run only).
4. Produces integration-ready JSON output for Spectra LS workflow follow-on.
5. Automatically detects WLED run mode and adapts color strategy.

## Script

- Path: `bin/spectra_wled_palette_e2e.py`
- Runtime: Python 3 (standard library only)
- Auth: Home Assistant LL token from `secrets.yaml` key `ha_ll_token` by default

## Quick start

Dry-run first (recommended):

- `python3 /mnt/homeassistant/bin/spectra_wled_palette_e2e.py`

Apply mode:

- `python3 /mnt/homeassistant/bin/spectra_wled_palette_e2e.py --apply`

Target a specific room:

- `python3 /mnt/homeassistant/bin/spectra_wled_palette_e2e.py --room "Living Room" --apply`

Use a specific HA WLED entity as source (HA-first path):

- `python3 /mnt/homeassistant/bin/spectra_wled_palette_e2e.py --room "Living Room" --wled-entity "light.living_room_lights" --apply`

Use direct WLED URL source (legacy/direct path):

- `python3 /mnt/homeassistant/bin/spectra_wled_palette_e2e.py --wled-url "http://192.168.10.251" --apply`

Target explicit entities:

- `python3 /mnt/homeassistant/bin/spectra_wled_palette_e2e.py --entities "light.star_light,light.reading,light.play_gradient_tube" --apply`

Write output to a file:

- `python3 /mnt/homeassistant/bin/spectra_wled_palette_e2e.py --apply --output /mnt/homeassistant/docs/testing/raw/_tmp_wled_e2e_output.json`

## Key options

- `--ha-url` (default: `http://192.168.10.10:8123`)
- `--wled-url` (optional; when omitted, HA-first WLED entity source is used)
- `--wled-entity` (optional explicit HA `light.*` WLED source)
- `--wled-helper-entity` (default: `input_select.control_board_wled_source`)
- `--token` (optional direct token)
- `--secrets-file` / `--secrets-key` (default key: `ha_ll_token`)
- `--room` (HA area name)
- `--room-helper-entity` (default: `input_select.control_board_room`)
- `--entities` (comma-separated explicit `light.*` IDs)
- `--max-lights`, `--include-off-lights`
- `--brightness`, `--transition`
- `--apply` (without this flag, mode is dry-run)
- `--output` (optional JSON artifact path)

## Smart adaptive behavior (automatic)

The script now auto-detects WLED operating mode:

- If WLED is running palette/effect/playlist context, it follows sampled WLED colors directly.
- If WLED is truly solid/static with a single sampled color, it generates complementary colors and maps them across targets.

For HA-entity source mode, run mode is inferred from the entity effect state (`Solid`/`Static` vs active effect/palette family).

No extra flags are required for this behavior.

## Expected outputs

The script prints JSON with:

- WLED sampling context (`seg`, sampled colors, palette/effect references)
- target resolution strategy (`room_area`, `explicit_entities`, `fallback`)
- apply payloads/results per entity
- integration notes for Spectra LS control-center follow-on

## Integration path into Spectra LS (next step)

Use this as the short bridge plan:

1. Keep this script as the truth-source E2E validator.
2. Wrap it in a Home Assistant script/shell command for controlled execution windows (now implemented in `packages/spectra_ls_lighting_hub.yaml`).
3. Trigger that wrapper from control-center mappings (`spectra_ls.execute_control_center_input`) once desired UX is finalized.
4. Promote validated behavior into a first-class `custom_components/spectra_ls` service only after deterministic dry-run + apply evidence is stable.

## Safety notes

- Keep `--apply` off during initial room-target validation.
- Use bounded trial windows; avoid perpetual automation loops at first integration.
- Rotate any exposed tokens if captured in logs/transcripts.
