# Description: Binary sensor entities for Spectra LS shadow parity routing surfaces with Phase 3 write-control, Phase 4 diagnostics attributes, and Phase 6 control-center settings visibility, including host-cutover readiness and shared MA authority-contract packet propagation.
# Version: 2026.05.04.3
# Last updated: 2026-05-04
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
from .const import (
    DOMAIN,
    LEGACY_META_CONFIDENCE_MIN,
    LEGACY_META_OVERRIDE_ACTIVE,
    LEGACY_META_OVERRIDE_ENTITY,
    LEGACY_META_RESOLVER,
)


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


class SpectraLsComponentNowPlayingDisplayAllowedBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Component-native now-playing display-policy contract surface."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:television-play"
    _attr_name = "Component Now Playing Display Allowed"
    _attr_unique_id = "spectra_ls_component_now_playing_display_allowed"

    @property
    def is_on(self) -> bool:
        metadata_prep = self.coordinator.data.get("metadata_prep_validation", {})
        values = metadata_prep.get("values", {}) if isinstance(metadata_prep.get("values", {}), dict) else {}
        return bool(values.get("now_playing_display_allowed", False))

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        metadata_prep = data.get("metadata_prep_validation", {}) if isinstance(data.get("metadata_prep_validation", {}), dict) else {}
        values = metadata_prep.get("values", {}) if isinstance(metadata_prep.get("values", {}), dict) else {}
        checks = metadata_prep.get("checks", {}) if isinstance(metadata_prep.get("checks", {}), dict) else {}
        return {
            "now_playing_media_class": values.get("now_playing_media_class", ""),
            "expected_display_allowed": values.get("expected_display_allowed"),
            "display_contract_consistent": checks.get("now_playing_display_contract_consistent"),
            "music_guard_active": values.get("music_guard_active"),
            "captured_at": data.get("captured_at"),
        }


class SpectraLsComponentMetaLowConfidenceBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Component-native metadata low-confidence contract surface."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:alert-circle-outline"
    _attr_name = "Component Meta Low Confidence"
    _attr_unique_id = "spectra_ls_component_meta_low_confidence"

    @property
    def is_on(self) -> bool:
        candidate_state = self.coordinator.hass.states.get("sensor.spectra_ls_component_meta_candidates")
        if candidate_state is not None and isinstance(candidate_state.attributes, dict):
            attrs = candidate_state.attributes
            low_conf = attrs.get("low_confidence")
            if isinstance(low_conf, bool):
                return low_conf

            try:
                best_score = float(attrs.get("best_score", 0))
            except (TypeError, ValueError):
                best_score = 0.0

            try:
                confidence_min = float(attrs.get("confidence_min", 4.0))
            except (TypeError, ValueError):
                confidence_min = 4.0

            best_entity = str(attrs.get("best_entity", "") or "").strip()
            return best_entity == "" or best_score < confidence_min

        resolver_state = self.coordinator.hass.states.get(LEGACY_META_RESOLVER)
        confidence_min_state = self.coordinator.hass.states.get(LEGACY_META_CONFIDENCE_MIN)

        try:
            confidence_min = float(confidence_min_state.state) if confidence_min_state is not None else 4.0
        except (TypeError, ValueError):
            confidence_min = 4.0

        if resolver_state is None:
            return True

        best_entity = str(resolver_state.attributes.get("best_entity", "") or "").strip()
        try:
            best_score = float(resolver_state.attributes.get("best_score", 0))
        except (TypeError, ValueError):
            best_score = 0.0

        return best_entity == "" or best_score < confidence_min

    @property
    def extra_state_attributes(self):
        candidate_state = self.coordinator.hass.states.get("sensor.spectra_ls_component_meta_candidates")
        attrs = candidate_state.attributes if candidate_state is not None and isinstance(candidate_state.attributes, dict) else {}
        return {
            "best_entity": attrs.get("best_entity", ""),
            "best_score": attrs.get("best_score", 0),
            "confidence_min": attrs.get("confidence_min", 4.0),
            "candidate_count": attrs.get("candidate_count", 0),
            "captured_at": self.coordinator.data.get("captured_at"),
        }


class SpectraLsComponentMetadataOverrideActiveBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Component-owned metadata override active status surface (LC-08)."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:toggle-switch"
    _attr_name = "Component Metadata Override Active"
    _attr_unique_id = "spectra_ls_component_metadata_override_active"

    @property
    def is_on(self) -> bool:
        override_active = self.coordinator.hass.states.get(LEGACY_META_OVERRIDE_ACTIVE)
        if override_active is None:
            return False
        state = str(override_active.state or "").strip().lower()
        return state in {"on", "true", "1"}

    @property
    def extra_state_attributes(self):
        override_entity = self.coordinator.hass.states.get(LEGACY_META_OVERRIDE_ENTITY)
        override_entity_value = ""
        if override_entity is not None:
            value = str(override_entity.state or "").strip()
            if value.lower() not in {"", "none", "unknown", "unavailable", "null"}:
                override_entity_value = value

        metadata_attempt = self.coordinator.metadata_stack.last_metadata_override_attempt
        return {
            "override_entity": override_entity_value,
            "last_attempt_status": metadata_attempt.get("status", "unknown"),
            "last_attempt_reason": metadata_attempt.get("reason", ""),
            "last_attempt_requested_at": metadata_attempt.get("requested_at"),
            "last_attempt_completed_at": metadata_attempt.get("completed_at"),
            "captured_at": self.coordinator.data.get("captured_at"),
        }


class SpectraLsComponentRollbackSafePostureBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Component closeout binary surface for rollback-safe posture."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:backup-restore"
    _attr_name = "Component Rollback Safe Posture"
    _attr_unique_id = "spectra_ls_component_rollback_safe_posture"

    @property
    def is_on(self) -> bool:
        data = self.coordinator.data
        route_trace = data.get("route_trace", {}) if isinstance(data.get("route_trace", {}), dict) else {}
        contract = (
            data.get("contract_validation", {})
            if isinstance(data.get("contract_validation", {}), dict)
            else {}
        )
        write_controls = (
            data.get("write_controls", {}) if isinstance(data.get("write_controls", {}), dict) else {}
        )
        route_decision = str(route_trace.get("decision", "") or "").strip().lower()
        authority_mode = str(write_controls.get("authority_mode", "") or "").strip().lower()
        contract_valid = bool(contract.get("valid", False))
        return route_decision == "route_linkplay_tcp" and authority_mode in {
            "legacy",
            "component",
        } and contract_valid

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        route_trace = data.get("route_trace", {}) if isinstance(data.get("route_trace", {}), dict) else {}
        contract = (
            data.get("contract_validation", {})
            if isinstance(data.get("contract_validation", {}), dict)
            else {}
        )
        write_controls = (
            data.get("write_controls", {}) if isinstance(data.get("write_controls", {}), dict) else {}
        )
        return {
            "route_decision": route_trace.get("decision", ""),
            "authority_mode": write_controls.get("authority_mode", ""),
            "contract_valid": contract.get("valid", False),
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
            SpectraLsComponentNowPlayingDisplayAllowedBinarySensor(coordinator),
            SpectraLsComponentMetaLowConfidenceBinarySensor(coordinator),
            SpectraLsComponentMetadataOverrideActiveBinarySensor(coordinator),
            SpectraLsComponentRollbackSafePostureBinarySensor(coordinator),
        ]
    )
