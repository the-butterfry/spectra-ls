# Notes

- Always pull Home Assistant device stats (e.g., `supported_color_modes`, `color_mode`, `hs_color`, `rgb_color`, `brightness`) before adding new ESPHome “features” or payload types. Do not assume a light supports HS/RGB/XY/RGBW without verifying.
- When troubleshooting light control, first capture HA entity attributes and validate a Developer Tools → Actions call for the target entity.

## Global verification checklist

Use this checklist whenever a behavior is required to be global (e.g., “never jump volume”, “back works everywhere”). If it’s global, it must be enforced at **all entry points**, not just one path.

### Scope audit

- [ ] Search for every place the behavior is set, toggled, or referenced (state vars, scripts, menus, sensors, automations).
- [ ] Identify all UI entry points (menu `on_enter`, `on_leave`, button handlers, encoder handlers, screensaver paths).
- [ ] Identify all non-UI entry points (intervals, sensors, HA callbacks, boot hooks).

### Guardrails

- [ ] Enforce the rule at the **lowest-level shared logic** (e.g., slider handler, central script), not just in one menu.
- [ ] Add negative guards (explicitly block when state is not valid).
- [ ] Confirm fallback behavior when devices/entities are unavailable.

### Regression checks

- [ ] Try the behavior from every relevant screen (menus, screensaver/controls, hidden menu states).
- [ ] Try “bad state” conditions (stale data, unavailable entities, mismatched slider position).
- [ ] Verify logs/telemetry reflect the intended path.

### Documentation

- [ ] Update `CHANGELOG.md` with what changed and why.
- [ ] If the change affects global behavior, document the guard in this checklist section.
