# Description: Sensor entities for Spectra LS shadow parity routing surfaces with Phase 3 write-control, Phase 4 diagnostics attributes, and Phase 6 control-center settings/last-attempt visibility.
# Version: 2026.04.21.11
# Last updated: 2026-04-21

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


class SpectraLsShadowSensor(CoordinatorEntity, SensorEntity):
    """Generic read-only shadow sensor."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:audio-video"

    def __init__(self, coordinator, key: str, name: str) -> None:
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"spectra_ls_shadow_{key}"

    @property
    def native_value(self):
        return self.coordinator.data["parity"].get(self._key, "")

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        return {
            "legacy_value": data["legacy"].get(self._key),
            "unresolved_sources": data.get("unresolved_sources", []),
            "mismatches": data.get("mismatches", []),
            "captured_at": data.get("captured_at"),
            "registry": data.get("registry", {}),
            "route_trace": data.get("route_trace", {}),
            "contract_validation": data.get("contract_validation", {}),
            "selection_handoff_validation": data.get("selection_handoff_validation", {}),
            "metadata_prep_validation": data.get("metadata_prep_validation", {}),
            "capability_profile_validation": data.get("capability_profile_validation", {}),
            "action_catalog_validation": data.get("action_catalog_validation", {}),
            "crossfade_balance_validation": data.get("crossfade_balance_validation", {}),
            "control_center_validation": data.get("control_center_validation", {}),
            "write_controls": data.get("write_controls", {}),
        }


class SpectraLsControlCenterLastAttemptStatusSensor(CoordinatorEntity, SensorEntity):
    """Diagnostic sensor exposing the latest control-center execution result status."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:gesture-tap-button"
    _attr_name = "Control Center Last Attempt Status"
    _attr_unique_id = "spectra_ls_control_center_last_attempt_status"

    @property
    def native_value(self):
        write_controls = self.coordinator.data.get("write_controls", {})
        last_attempt = write_controls.get("control_center_last_attempt", {})
        status = str(last_attempt.get("status", "never_attempted") or "").strip()
        return status or "never_attempted"

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        write_controls = data.get("write_controls", {})
        last_attempt = write_controls.get("control_center_last_attempt", {})
        cc_validation = data.get("control_center_validation", {})

        return {
            "reason": last_attempt.get("reason"),
            "input_event": last_attempt.get("input_event"),
            "mapped_action": last_attempt.get("mapped_action"),
            "dry_run": last_attempt.get("dry_run"),
            "read_only_mode": last_attempt.get("read_only_mode"),
            "correlation_id": last_attempt.get("correlation_id"),
            "target_hint": last_attempt.get("target_hint"),
            "requested_at": last_attempt.get("requested_at"),
            "completed_at": last_attempt.get("completed_at"),
            "control_center_settings": write_controls.get("control_center_settings", {}),
            "ready_for_customization": cc_validation.get("ready_for_customization"),
            "unresolved_scene_bindings": cc_validation.get("unresolved_scene_bindings", []),
            "captured_at": data.get("captured_at"),
        }


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Spectra LS shadow sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            SpectraLsShadowSensor(coordinator, "active_target", "Shadow Active Target"),
            SpectraLsShadowSensor(coordinator, "active_control_path", "Shadow Active Control Path"),
            SpectraLsShadowSensor(coordinator, "control_hosts", "Shadow Control Hosts"),
            SpectraLsControlCenterLastAttemptStatusSensor(coordinator),
        ]
    )
