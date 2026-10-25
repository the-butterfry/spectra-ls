# Automation Link Audit

- yaml_automations: **75**
- live_automation_entities_total: **113**
- missing_entity_issues: **2**
- missing_service_issues: **0**
- missing_live_entity_count: **0**
- off_automation_count: **6**

## Broken references
- `/mnt/homeassistant/packages/spectra_ls_interactables.yaml` :: `spectra_interactable_ble_button_single_source_bridge` (Spectra: BLE Button-Single Source to Interactable Bridge) -> **missing_entity** `binary_sensor.ble_presence_door_cory_ble_button_single`
- `/mnt/homeassistant/packages/spectra_ls_interactables.yaml` :: `spectra_interactable_ble_arriving_source_bridge` (Spectra: BLE Arriving Source to Interactable Bridge) -> **missing_entity** `binary_sensor.ble_presence_door_cory_ble_arriving`

## Loaded but disabled automations (state=off)
- `1785987105001` (Crosstrek - Poll Vehicle Every 15 Minutes) from `/mnt/homeassistant/automations.yaml`
- `trash_hp_schedule_weekday_morning_comfort` (Trash Heatpump Schedule Weekday Morning Comfort) from `/mnt/homeassistant/packages/dst_ge_trash_heatpump.yaml`
- `trash_hp_schedule_weekday_away_eco` (Trash Heatpump Schedule Weekday Away Eco) from `/mnt/homeassistant/packages/dst_ge_trash_heatpump.yaml`
- `trash_hp_schedule_weekday_return_home` (Trash Heatpump Schedule Weekday Return Home) from `/mnt/homeassistant/packages/dst_ge_trash_heatpump.yaml`
- `trash_hp_schedule_night_sleep` (Trash Heatpump Schedule Night Sleep) from `/mnt/homeassistant/packages/dst_ge_trash_heatpump.yaml`
- `snail_ac_manual_fan_only_keepalive` (Snail AC Manual Fan Only Keepalive) from `/mnt/homeassistant/packages/dst_tuya_ac.yaml`