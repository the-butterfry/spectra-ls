# Description: Sensor entities for Spectra LS shadow parity routing surfaces with Phase 3 write-control, Phase 4 diagnostics attributes, Phase 6/8 control-center settings/readiness/last-attempt visibility, monitor-manager freshness diagnostics, and runtime compatibility component_* surfaces.
# Version: 2026.04.25.2
# Last updated: 2026-04-25

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


def _is_resolved_value(value: Any) -> bool:
    normalized = str(value or "").strip().lower()
    return normalized not in {"", "unknown", "unavailable", "none", "missing", "null"}


def _resolved_string(value: Any) -> str:
    return str(value).strip() if _is_resolved_value(value) else ""


def _state_resolved_string(hass: HomeAssistant, entity_id: str) -> str:
    state = hass.states.get(entity_id)
    if state is None:
        return ""
    return _resolved_string(state.state)


def _monitor_payload(coordinator) -> dict[str, Any]:
    payload = coordinator.data.get("component_monitor", {})
    return payload if isinstance(payload, dict) else {}


def _monitor_section(monitor: dict[str, Any], key: str) -> dict[str, Any]:
    payload = monitor.get(key, {})
    return payload if isinstance(payload, dict) else {}


def _monitor_now_playing_state(coordinator) -> tuple[dict[str, Any], str, Any]:
    monitor = _monitor_payload(coordinator)
    sources = _monitor_section(monitor, "sources")
    entity_id = _resolved_string(sources.get("now_playing_entity"))
    state_obj = coordinator.hass.states.get(entity_id) if entity_id else None
    return monitor, entity_id, state_obj


class SpectraLsComponentCompatibilitySensor(CoordinatorEntity, SensorEntity):
    """Compatibility sensor surface consumed by runtime/ESP plumbing contracts."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:tune-variant"

    def __init__(self, coordinator, key: str, name: str, unique_id: str) -> None:
        super().__init__(coordinator)
        self._compat_key = key
        self._attr_name = name
        self._attr_unique_id = unique_id

    @property
    def native_value(self):
        key = self._compat_key
        monitor = _monitor_payload(self.coordinator)
        published = _monitor_section(monitor, "published")
        sources = _monitor_section(monitor, "sources")
        target_resolution = _monitor_section(monitor, "target_resolution")

        if key == "control_host":
            return _resolved_string(published.get("control_host"))

        if key == "control_hosts":
            host = _resolved_string(published.get("control_host"))
            if host:
                return host
            candidates = sources.get("control_host_candidates", [])
            if isinstance(candidates, list):
                resolved = [_resolved_string(item) for item in candidates]
                resolved = [item for item in resolved if item]
                return ",".join(resolved)
            return ""

        if key == "active_meta_entity":
            return _state_resolved_string(self.coordinator.hass, "sensor.ma_active_meta_entity")

        if key == "now_playing_entity":
            return _resolved_string(sources.get("now_playing_entity"))

        if key == "now_playing_state":
            return _resolved_string(sources.get("now_playing_state"))

        if key == "now_playing_title":
            return _resolved_string(published.get("now_playing_title") or sources.get("now_playing_title_candidate"))

        monitor_payload, entity_id, state_obj = _monitor_now_playing_state(self.coordinator)
        _ = monitor_payload
        _ = entity_id

        if key == "now_playing_artist":
            if state_obj is None:
                return ""
            return _resolved_string(state_obj.attributes.get("media_artist"))

        if key == "now_playing_album":
            if state_obj is None:
                return ""
            return _resolved_string(state_obj.attributes.get("media_album_name"))

        if key == "now_playing_source":
            if state_obj is None:
                return ""
            return _resolved_string(state_obj.attributes.get("source"))

        if key == "now_playing_app":
            if state_obj is None:
                return ""
            return _resolved_string(state_obj.attributes.get("app_name"))

        if key == "now_playing_duration":
            if state_obj is None:
                return ""
            duration = state_obj.attributes.get("media_duration")
            if duration is None:
                return ""
            return str(duration)

        if key == "now_playing_position":
            if state_obj is None:
                return ""
            position = state_obj.attributes.get("media_position")
            if position is None:
                return ""
            return str(position)

        if key == "active_friendly":
            effective_target = _resolved_string(target_resolution.get("effective_target"))
            if not effective_target:
                return ""
            state = self.coordinator.hass.states.get(effective_target)
            if state is None:
                return effective_target
            friendly = _resolved_string(state.attributes.get("friendly_name"))
            return friendly or effective_target

        if key == "control_targets":
            registry = self.coordinator.data.get("registry", {})
            if not isinstance(registry, dict):
                return ""
            entries = registry.get("entries", {})
            if isinstance(entries, dict):
                return ",".join(sorted([_resolved_string(item) for item in entries.keys() if _resolved_string(item)]))
            return ""

        if key == "meta_candidates":
            return _state_resolved_string(self.coordinator.hass, "sensor.ma_meta_candidates")

        return ""

    @property
    def extra_state_attributes(self):
        monitor = _monitor_payload(self.coordinator)
        return {
            "component_monitor": monitor,
            "captured_at": self.coordinator.data.get("captured_at"),
        }


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
            "component_monitor": data.get("component_monitor", {}),
            "control_center_validation": data.get("control_center_validation", {}),
            "write_controls": data.get("write_controls", {}),
        }


class SpectraLsMonitorHealthSensor(CoordinatorEntity, SensorEntity):
    """Diagnostic sensor exposing monitor manager freshness and fail-closed gate state."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:heart-pulse"
    _attr_name = "Monitor Health"
    _attr_unique_id = "spectra_ls_monitor_health"

    @property
    def native_value(self):
        monitor = self.coordinator.data.get("component_monitor", {})
        health = str(monitor.get("monitor_health", "unknown") or "").strip()
        return health or "unknown"

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        monitor = data.get("component_monitor", {})

        return {
            "schema_version": monitor.get("schema_version"),
            "monitor_enabled": monitor.get("monitor_enabled"),
            "fail_closed": monitor.get("fail_closed"),
            "publish_gate": monitor.get("publish_gate", {}),
            "freshness": monitor.get("freshness", {}),
            "target_resolution": monitor.get("target_resolution", {}),
            "sources": monitor.get("sources", {}),
            "published": monitor.get("published", {}),
            "captured_at": data.get("captured_at"),
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
            "mapping_preset": cc_validation.get("mapping_preset"),
            "effective_mapping": cc_validation.get("effective_mapping", {}),
            "ready_for_customization": cc_validation.get("ready_for_customization"),
            "unresolved_scene_bindings": cc_validation.get("unresolved_scene_bindings", []),
            "captured_at": data.get("captured_at"),
        }


class SpectraLsControlCenterReadinessSensor(CoordinatorEntity, SensorEntity):
    """Diagnostic sensor exposing Control Center readiness state and setup guidance."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:clipboard-check-outline"
    _attr_name = "Control Center Readiness"
    _attr_unique_id = "spectra_ls_control_center_readiness"

    @property
    def native_value(self):
        cc_validation = self.coordinator.data.get("control_center_validation", {})
        readiness_state = str(cc_validation.get("readiness_state", "needs_scene_binding") or "").strip()
        return readiness_state or "needs_scene_binding"

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        cc_validation = data.get("control_center_validation", {})
        write_controls = data.get("write_controls", {})

        return {
            "ready_for_execution": cc_validation.get("ready_for_execution"),
            "recommended_next_step": cc_validation.get("recommended_next_step"),
            "mapping_preset": cc_validation.get("mapping_preset"),
            "preset_applied": cc_validation.get("preset_applied"),
            "effective_mapping": cc_validation.get("effective_mapping", {}),
            "configured_scene_bindings_count": cc_validation.get("configured_scene_bindings_count"),
            "total_scene_bindings": cc_validation.get("total_scene_bindings"),
            "resolved_scene_bindings": cc_validation.get("resolved_scene_bindings", []),
            "unresolved_scene_bindings": cc_validation.get("unresolved_scene_bindings", []),
            "quick_trigger_scene": cc_validation.get("quick_trigger_scene"),
            "quick_trigger_ready": cc_validation.get("quick_trigger_ready"),
            "read_only_mode": cc_validation.get("read_only_mode"),
            "non_dry_run_supported_actions": cc_validation.get("non_dry_run_supported_actions", []),
            "non_dry_run_pending_actions": cc_validation.get("non_dry_run_pending_actions", []),
            "control_center_settings": write_controls.get("control_center_settings", {}),
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
            SpectraLsComponentCompatibilitySensor(
                coordinator,
                "control_hosts",
                "Component Control Hosts",
                "spectra_ls_component_unit_control_hosts",
            ),
            SpectraLsComponentCompatibilitySensor(
                coordinator,
                "control_host",
                "Component Control Host",
                "spectra_ls_component_unit_control_host",
            ),
            SpectraLsComponentCompatibilitySensor(
                coordinator,
                "active_meta_entity",
                "Component Active Meta Entity",
                "spectra_ls_component_unit_active_meta_entity",
            ),
            SpectraLsComponentCompatibilitySensor(
                coordinator,
                "now_playing_entity",
                "Component Now Playing Entity",
                "spectra_ls_component_unit_now_playing_entity",
            ),
            SpectraLsComponentCompatibilitySensor(
                coordinator,
                "now_playing_state",
                "Component Now Playing State",
                "spectra_ls_component_unit_now_playing_state",
            ),
            SpectraLsComponentCompatibilitySensor(
                coordinator,
                "now_playing_title",
                "Component Now Playing Title",
                "spectra_ls_component_unit_now_playing_title",
            ),
            SpectraLsComponentCompatibilitySensor(
                coordinator,
                "now_playing_artist",
                "Component Now Playing Artist",
                "spectra_ls_component_unit_now_playing_artist",
            ),
            SpectraLsComponentCompatibilitySensor(
                coordinator,
                "now_playing_album",
                "Component Now Playing Album",
                "spectra_ls_component_unit_now_playing_album",
            ),
            SpectraLsComponentCompatibilitySensor(
                coordinator,
                "now_playing_source",
                "Component Now Playing Source",
                "spectra_ls_component_unit_now_playing_source",
            ),
            SpectraLsComponentCompatibilitySensor(
                coordinator,
                "now_playing_app",
                "Component Now Playing App",
                "spectra_ls_component_unit_now_playing_app",
            ),
            SpectraLsComponentCompatibilitySensor(
                coordinator,
                "now_playing_duration",
                "Component Now Playing Duration",
                "spectra_ls_component_unit_now_playing_duration",
            ),
            SpectraLsComponentCompatibilitySensor(
                coordinator,
                "now_playing_position",
                "Component Now Playing Position",
                "spectra_ls_component_unit_now_playing_position",
            ),
            SpectraLsComponentCompatibilitySensor(
                coordinator,
                "active_friendly",
                "Component Active Friendly",
                "spectra_ls_component_summary_active_friendly",
            ),
            SpectraLsComponentCompatibilitySensor(
                coordinator,
                "control_targets",
                "Component Control Targets",
                "spectra_ls_component_summary_control_targets",
            ),
            SpectraLsComponentCompatibilitySensor(
                coordinator,
                "meta_candidates",
                "Component Meta Candidates",
                "spectra_ls_component_summary_meta_candidates",
            ),
            SpectraLsShadowSensor(coordinator, "active_target", "Shadow Active Target"),
            SpectraLsShadowSensor(coordinator, "active_control_path", "Shadow Active Control Path"),
            SpectraLsShadowSensor(coordinator, "control_hosts", "Shadow Control Hosts"),
            SpectraLsMonitorHealthSensor(coordinator),
            SpectraLsControlCenterReadinessSensor(coordinator),
            SpectraLsControlCenterLastAttemptStatusSensor(coordinator),
        ]
    )
