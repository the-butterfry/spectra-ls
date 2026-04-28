# Description: Sensor entities for Spectra LS shadow parity routing surfaces with Phase 3 write-control, Phase 4 diagnostics attributes, and Phase 6/8 control-center settings/readiness/last-attempt visibility, including recorder-safe attribute payload sizing.
# Version: 2026.04.27.2
# Last updated: 2026-04-27

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
    # Keep rich diagnostics visible in state while avoiding Recorder DB bloat and
    # 16KB attribute warnings on high-volume nested payloads.
    _unrecorded_attributes = frozenset(
        {
            "route_trace",
            "contract_validation",
            "selection_handoff_validation",
            "route_safety_validation",
            "metadata_prep_validation",
            "scheduler_validation",
            "metadata_bridge_validation",
            "handoff_inventory",
            "control_center_validation",
            "write_controls",
        }
    )

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
        base = {
            "legacy_value": data["legacy"].get(self._key),
            "unresolved_sources": data.get("unresolved_sources", []),
            "mismatches": data.get("mismatches", []),
            "captured_at": data.get("captured_at"),
        }

        # Keep non-primary shadow entities lightweight to avoid Recorder attribute-size drops.
        if self._key != "active_target":
            return {
                **base,
                "route_trace": data.get("route_trace", {}),
            }

        # Primary diagnostics surface (active target): include required operator contracts,
        # but intentionally omit high-volume payloads (e.g. full registry/action catalogs)
        # to stay under Recorder attribute limits.
        return {
            **base,
            "route_trace": data.get("route_trace", {}),
            "contract_validation": data.get("contract_validation", {}),
            "selection_handoff_validation": data.get("selection_handoff_validation", {}),
            "route_safety_validation": data.get("route_safety_validation", {}),
            "metadata_prep_validation": data.get("metadata_prep_validation", {}),
            "scheduler_validation": data.get("scheduler_validation", {}),
            "metadata_bridge_validation": data.get("metadata_bridge_validation", {}),
            "handoff_inventory": data.get("handoff_inventory", {}),
            "ma_backend_profile": data.get("ma_backend_profile", {}),
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


class SpectraLsHostResolutionStatusSensor(CoordinatorEntity, SensorEntity):
    """Diagnostic sensor exposing pluggable host-module resolution status."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:router-network"
    _attr_name = "Host Resolution Status"
    _attr_unique_id = "spectra_ls_host_resolution_status"

    @property
    def native_value(self):
        data = self.coordinator.data
        registry = data.get("registry", {})
        entries = registry.get("entries", {}) if isinstance(registry.get("entries", {}), dict) else {}
        total = len(entries)
        resolved = 0
        for entry in entries.values():
            if not isinstance(entry, dict):
                continue
            host = str(entry.get("host", "") or "").strip()
            if host:
                resolved += 1
        return f"{resolved}/{total}"

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        registry = data.get("registry", {})
        entries = registry.get("entries", {}) if isinstance(registry.get("entries", {}), dict) else {}
        summary = registry.get("source_summary", {}) if isinstance(registry.get("source_summary", {}), dict) else {}

        targets: dict[str, dict[str, object]] = {}
        for target, entry in entries.items():
            if not isinstance(entry, dict):
                continue
            targets[str(target)] = {
                "host": entry.get("host", ""),
                "host_type": entry.get("host_type", "generic"),
                "resolver_module": entry.get("resolver_module", "hostmods.generic"),
                "control_path": entry.get("control_path", "unknown"),
                "control_capable": bool(entry.get("control_capable", False)),
                "host_resolution": entry.get("host_resolution", {}),
                "feature_profile": entry.get("feature_profile", {}),
                "empirical_profile": entry.get("empirical_profile", {}),
                "scheduler_profile": entry.get("scheduler_profile", {}),
            }

        return {
            "host_modules": registry.get("host_modules", {}),
            "empirical_overlay": registry.get("empirical_overlay", {}),
            "host_type_counts": summary.get("host_type_counts", {}),
            "resolver_module_counts": summary.get("resolver_module_counts", {}),
            "resolved_target_hosts_count": summary.get("resolved_target_hosts_count", 0),
            "profiled_targets_count": summary.get("profiled_targets_count", 0),
            "empirical_profiled_targets_count": summary.get("empirical_profiled_targets_count", 0),
            "target_count": registry.get("target_count", 0),
            "unresolved_sources": registry.get("unresolved_sources", []),
            "targets": targets,
            "route_trace": data.get("route_trace", {}),
            "captured_at": data.get("captured_at"),
        }


class SpectraLsSchedulerDecisionSensor(CoordinatorEntity, SensorEntity):
    """Diagnostic sensor exposing last scheduler decision status and payload."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:timeline-check"
    _attr_name = "Scheduler Decision Status"
    _attr_unique_id = "spectra_ls_scheduler_decision_status"

    @property
    def native_value(self):
        write_controls = self.coordinator.data.get("write_controls", {})
        decision = write_controls.get("scheduler_last_decision", {})
        status = str(decision.get("status", "never_attempted") or "").strip()
        return status or "never_attempted"

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        write_controls = data.get("write_controls", {})
        decision = write_controls.get("scheduler_last_decision", {})
        apply_result = write_controls.get("scheduler_last_apply", {})
        return {
            "selected_target": decision.get("selected_target", ""),
            "selected_host": decision.get("selected_host", ""),
            "selected_score": decision.get("selected_score", 0.0),
            "reason": decision.get("reason", ""),
            "policy": decision.get("policy", {}),
            "candidate_count": decision.get("candidate_count", 0),
            "ranked_candidates": decision.get("ranked_candidates", []),
            "correlation_id": decision.get("correlation_id", ""),
            "requested_at": decision.get("requested_at"),
            "completed_at": decision.get("completed_at"),
            "last_apply_status": apply_result.get("status", "never_attempted"),
            "last_apply_reason": apply_result.get("reason", ""),
            "last_apply_target": apply_result.get("selected_target", ""),
            "last_apply_dry_run": apply_result.get("dry_run", True),
            "last_apply_force": apply_result.get("force", False),
            "last_apply_requested_at": apply_result.get("requested_at"),
            "last_apply_completed_at": apply_result.get("completed_at"),
            "scheduler_validation": data.get("scheduler_validation", {}),
            "captured_at": data.get("captured_at"),
        }


class SpectraLsMetaPolicyStatusSensor(CoordinatorEntity, SensorEntity):
    """Diagnostic sensor exposing canonical metadata policy + suppression posture."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:tune-variant"
    _attr_name = "Meta Policy Status"
    _attr_unique_id = "spectra_ls_meta_policy_status"

    @property
    def native_value(self):
        write_controls = self.coordinator.data.get("write_controls", {})
        policy = write_controls.get("meta_policy", {}) if isinstance(write_controls.get("meta_policy", {}), dict) else {}
        mode = str(policy.get("mode", "auto") or "auto").strip().lower()
        return mode or "auto"

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        write_controls = data.get("write_controls", {})
        policy = write_controls.get("meta_policy", {}) if isinstance(write_controls.get("meta_policy", {}), dict) else {}
        metadata_prep = (
            data.get("metadata_prep_validation", {})
            if isinstance(data.get("metadata_prep_validation", {}), dict)
            else {}
        )
        checks = metadata_prep.get("checks", {}) if isinstance(metadata_prep.get("checks", {}), dict) else {}
        values = metadata_prep.get("values", {}) if isinstance(metadata_prep.get("values", {}), dict) else {}

        return {
            "meta_policy": policy,
            "suppression_reason": checks.get("now_playing_suppression_reason", ""),
            "fresh_play_signal": checks.get("now_playing_fresh_play_signal"),
            "recent_play_progress": checks.get("now_playing_recent_play_progress", None),
            "recent_paused_progress": checks.get("now_playing_recent_paused_progress", None),
            "playing_without_recent_progress": checks.get("now_playing_playing_without_fresh_signal"),
            "paused_without_recent_progress": checks.get("now_playing_paused_without_fresh_signal"),
            "long_idle_stale_hidden": checks.get("now_playing_long_idle_stale_hidden"),
            "now_playing_entity": values.get("now_playing_entity", ""),
            "now_playing_position_age_s": values.get("now_playing_position_age_s"),
            "meta_stale_s": values.get("meta_stale_s"),
            "paused_hide_s": values.get("paused_hide_s"),
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
            SpectraLsHostResolutionStatusSensor(coordinator),
            SpectraLsSchedulerDecisionSensor(coordinator),
            SpectraLsMetaPolicyStatusSensor(coordinator),
            SpectraLsControlCenterReadinessSensor(coordinator),
            SpectraLsControlCenterLastAttemptStatusSensor(coordinator),
        ]
    )
