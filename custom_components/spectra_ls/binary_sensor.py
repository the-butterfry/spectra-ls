# Description: Binary sensor entities for Spectra LS shadow parity routing surfaces with Phase 3 write-control and Phase 4 diagnostics attributes (F4-S01/F4-S03).
# Version: 2026.04.20.9
# Last updated: 2026-04-20

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


class SpectraLsShadowControlCapableBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Read-only shadow parity for active control-capable flag."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:audio-video"
    _attr_name = "Shadow Active Control Capable"
    _attr_unique_id = "spectra_ls_shadow_active_control_capable"

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data["parity"].get("active_control_capable", False))

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        return {
            "legacy_value": data["legacy"].get("active_control_capable"),
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
            "write_controls": data.get("write_controls", {}),
        }


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Spectra LS shadow binary sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SpectraLsShadowControlCapableBinarySensor(coordinator)])
