---
description: "Project-wide instructions for control-board configs."
---

Never edit `control-board-peripherals.yaml` (rings). All changes must go only to `control-board-peripherals-no-rings.yaml` unless the user explicitly asks for rings updates.

For RP2040 firmware, treat `/media/cory/CIRCUITPY/` as the **authoritative** filesystem. Do **not** edit repo copies under `/config/esphome/control-py/` unless the user explicitly asks to update repo copies or synchronize them.
