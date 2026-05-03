# Description: Binary sensor entities for Spectra LS shadow parity routing surfaces with Phase 3 write-control, Phase 4 diagnostics attributes, and Phase 6 control-center settings visibility, including host-cutover readiness and shared MA authority-contract packet propagation.
# Version: 2026.05.03.1
# Last updated: 2026-05-03
# PARITY DIRECTIVE (until full cutover): behavior/contract edits here require same-slice two-track parity review
# and version-metadata review in runtime (`packages/` + `esphome/`) and component (`custom_components/spectra_ls/`) tracks.

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .authority_contract import build_authority_contract_packet
from .const import DOMAIN


class SpectraLsShadowControlCapableBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Read-only shadow parity for active control-capable flag."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:audio-video"
    _attr_name = "Shadow Active Control Capable"
    _attr_unique_id = "spectra_ls_shadow_active_control_capable"
    # Keep rich diagnostics visible in state while avoiding Recorder DB bloat and
    # 16KB attribute warnings on high-volume nested payloads.
    _unrecorded_attributes = frozenset(
        {
            "registry",
            "route_trace",
            "contract_validation",
            "selection_handoff_validation",
            "route_safety_validation",
            "metadata_prep_validation",
            "capability_profile_validation",
            "action_catalog_validation",
            "crossfade_balance_validation",
            "host_control_cutover_gate",
            "control_center_validation",
            "write_controls",
        }
    )

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
            "route_safety_validation": data.get("route_safety_validation", {}),
            "metadata_prep_validation": data.get("metadata_prep_validation", {}),
            "capability_profile_validation": data.get("capability_profile_validation", {}),
            "action_catalog_validation": data.get("action_catalog_validation", {}),
            "crossfade_balance_validation": data.get("crossfade_balance_validation", {}),
            "host_control_cutover_gate": data.get("host_control_cutover_gate", {}),
            "control_center_validation": data.get("control_center_validation", {}),
            "write_controls": data.get("write_controls", {}),
            "authority_contract": build_authority_contract_packet(data),
        }


class SpectraLsHostCutoverGateReadyBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Read-only binary surface for host-control cutover gate readiness."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:shield-check-outline"
    _attr_name = "Host Cutover Gate Ready"
    _attr_unique_id = "spectra_ls_host_cutover_gate_ready"

    @property
    def is_on(self) -> bool:
        gate = self.coordinator.data.get("host_control_cutover_gate", {})
        return bool(gate.get("ready_for_cutover", False))

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        gate = data.get("host_control_cutover_gate", {}) if isinstance(data.get("host_control_cutover_gate", {}), dict) else {}
        return {
            "status": gate.get("status", "blocked"),
            "ready_for_authoritative_activation": gate.get("ready_for_authoritative_activation", False),
            "authority_source_mode": gate.get("authority_source_mode", "legacy"),
            "authority_mode": gate.get("authority_mode", "legacy"),
            "component_authoritative_candidate": gate.get("component_authoritative_candidate", {}),
            "legacy_authority_snapshot": gate.get("legacy_authority_snapshot", {}),
            "route_decision": gate.get("route_decision", ""),
            "resolved_control_path": gate.get("resolved_control_path", ""),
            "checks": gate.get("checks", {}),
            "gate_blockers": gate.get("gate_blockers", []),
            "activation_blockers": gate.get("activation_blockers", []),
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
            SpectraLsShadowControlCapableBinarySensor(coordinator),
            SpectraLsHostCutoverGateReadyBinarySensor(coordinator),
        ]
    )
