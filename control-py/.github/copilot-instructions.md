---
description: "Project-wide instructions for control-board configs."
---

Never edit `control-board-peripherals.yaml` (rings). All changes must go only to `control-board-peripherals-no-rings.yaml` unless the user explicitly asks for rings updates.

## Versioning discipline (required)

- Every edited text file must expose and maintain at top-of-file:
	- `Description:`
	- `Version: YYYY.MM.DD.N`
	- `Last updated: YYYY-MM-DD`
- On each change, bump per-file minor `N` and update `Last updated`.
- If an edited file lacks this metadata, add it during that edit.

For RP2040 firmware, treat `/media/cory/CIRCUITPY/` as the **authoritative** filesystem. Do **not** edit repo copies under `/config/esphome/control-py/` unless the user explicitly asks to update repo copies or synchronize them.

RP2040 repo mirror is `esphome/circuitpy/` only. If `boot.py` / `code.py` appear under `control-py/`, treat them as stale duplicates and remove unless explicitly requested.
