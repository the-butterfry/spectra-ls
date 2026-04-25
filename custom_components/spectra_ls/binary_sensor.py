# Description: Binary sensor entities for Spectra LS shadow parity routing surfaces with Phase 3 write-control, Phase 4 diagnostics attributes (F4-S01/F4-S03), monitor-manager publish-gate status, and runtime compatibility component_* surfaces.
# Version: 2026.04.25.2
# Last updated: 2026-04-25

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


def _is_resolved_value(value: Any) -> bool:
    normalized = str(value or "").strip().lower()
    return normalized not in {"", "unknown", "unavailable", "none", "missing", "null"}


class SpectraLsComponentControlAmbiguousBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Compatibility binary sensor for runtime control-target ambiguity gating."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:help-network-outline"
    _attr_name = "Component Control Ambiguous"
    _attr_unique_id = "spectra_ls_component_control_ambiguous"

    @property
    def is_on(self) -> bool:
        explicit_legacy = self.coordinator.hass.states.get("binary_sensor.ma_control_ambiguous")
        if explicit_legacy is not None:
            normalized = str(explicit_legacy.state or "").strip().lower()
            return normalized in {"on", "true", "1", "yes"}

        monitor = self.coordinator.data.get("component_monitor", {})
        monitor = monitor if isinstance(monitor, dict) else {}
        target_resolution = monitor.get("target_resolution", {})
        target_resolution = target_resolution if isinstance(target_resolution, dict) else {}
        sources = monitor.get("sources", {})
        sources = sources if isinstance(sources, dict) else {}

        helper_target_stale_idle = bool(target_resolution.get("helper_target_stale_idle", False))
        effective_target_resolved = bool(target_resolution.get("effective_target_resolved", False))

        candidates = sources.get("control_host_candidates", [])
        resolved_candidates = []
        if isinstance(candidates, list):
            for item in candidates:
                if _is_resolved_value(item):
                    resolved_candidates.append(str(item).strip())

        return helper_target_stale_idle or (not effective_target_resolved) or len(resolved_candidates) > 1

    @property
    def extra_state_attributes(self):
        monitor = self.coordinator.data.get("component_monitor", {})
        monitor = monitor if isinstance(monitor, dict) else {}
        return {
            "component_monitor": monitor,
            "captured_at": self.coordinator.data.get("captured_at"),
        }


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
            "component_monitor": data.get("component_monitor", {}),
            "write_controls": data.get("write_controls", {}),
        }


class SpectraLsMonitorPublishGateBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor exposing whether monitor freshness gate currently allows publish."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:shield-check"
    _attr_name = "Monitor Publish Gate"
    _attr_unique_id = "spectra_ls_monitor_publish_gate"

    @property
    def is_on(self) -> bool:
        monitor = self.coordinator.data.get("component_monitor", {})
        gate = monitor.get("publish_gate", {}) if isinstance(monitor.get("publish_gate", {}), dict) else {}
        return bool(gate.get("allowed", False))

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        monitor = data.get("component_monitor", {})
        return {
            "monitor_health": monitor.get("monitor_health"),
            "publish_gate": monitor.get("publish_gate", {}),
            "freshness": monitor.get("freshness", {}),
            "target_resolution": monitor.get("target_resolution", {}),
            "published": monitor.get("published", {}),
            "captured_at": data.get("captured_at"),
        }


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Spectra LS shadow binary sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            SpectraLsComponentControlAmbiguousBinarySensor(coordinator),
            SpectraLsShadowControlCapableBinarySensor(coordinator),
            SpectraLsMonitorPublishGateBinarySensor(coordinator),
        ]
    )
