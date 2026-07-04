# Description: Snapshot-fabric workflow for Spectra LS coordinator snapshot and write-controls packet assembly extracted from coordinator.
# Version: 2026.06.22.3
# Last updated: 2026-06-22
# PARITY DIRECTIVE (until full cutover): behavior/contract edits here require same-slice two-track parity review
# and version-metadata review in runtime (`packages/` + `esphome/`) and component (`custom_components/spectra_ls/`) tracks.

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .const import (
    LEGACY_CONTROL_HOST,
    LEGACY_CONTROL_TARGETS,
    LEGACY_ROOMS_JSON,
    LEGACY_ROOMS_RAW,
    LEGACY_SURFACES,
    WRITE_AUTH_ALLOWED,
)
from .payload_surface_fabric import PayloadSurfaceFabric
from .registry import build_registry_snapshot
from .router import build_route_trace


class SnapshotFabricWorkflow:
    """Owns coordinator snapshot packet assembly extracted from coordinator."""

    def __init__(self, coordinator: Any) -> None:
        self._coordinator = coordinator

    @staticmethod
    def _dict_surface(payload: dict[str, Any], key: str) -> dict[str, Any]:
        """Return a dict-valued payload surface or a safe empty dict."""
        return PayloadSurfaceFabric.dict_surface(payload, key)

    @staticmethod
    def _normalize_helper_text(raw: Any) -> str:
        value = str(raw or "").strip()
        if value.lower() in {"", "none", "unknown", "unavailable", "null"}:
            return ""
        return value

    def _build_metadata_provider_packet(self) -> dict[str, Any]:
        c = self._coordinator
        component_packet = (
            c.last_metadata_provider_packet if isinstance(getattr(c, "last_metadata_provider_packet", {}), dict) else {}
        )

        def _packet_text(key: str) -> str:
            return self._normalize_helper_text(component_packet.get(key, ""))

        status = _packet_text("status")
        response = _packet_text("response")
        providers = _packet_text("providers")
        item_uri = _packet_text("item_uri")
        reason = _packet_text("reason")
        updated_at = _packet_text("updated_at")
        source = _packet_text("source")
        if status == "" and response == "" and providers == "" and item_uri == "" and reason == "" and updated_at == "":
            source = "component_packet_missing"

        age_s = c._timestamp_age_seconds(updated_at) if updated_at else None

        visible = any(
            text != ""
            for text in (
                status,
                response,
                providers,
                item_uri,
                reason,
                updated_at,
            )
        )

        return {
            "status": status,
            "response": response,
            "providers": providers,
            "item_uri": item_uri,
            "reason": reason,
            "updated_at": updated_at,
            "age_s": round(float(age_s), 1) if age_s is not None else None,
            "visible": visible,
            "source": source or "component_service_packet",
        }

    def build_write_controls(self) -> dict[str, Any]:
        """Build write-controls packet from coordinator and meta-fabric surfaces."""
        c = self._coordinator
        meta_policy = c._meta_fabric.build_meta_policy_surface()
        metadata_surfaces = c._meta_fabric.build_write_controls_metadata_surfaces()
        metadata_provider_last = self._build_metadata_provider_packet()

        return {
            "authority_mode": c._write_authority_mode,
            "allowed_modes": list(WRITE_AUTH_ALLOWED),
            "debounce_s": c._write_debounce_s,
            "in_progress": c._write_in_progress,
            "last_attempt": c._last_write_attempt,
            **metadata_surfaces,
            "metadata_provider_last": metadata_provider_last,
            "scheduler_last_decision": c._last_scheduler_decision,
            "scheduler_last_apply": c._last_scheduler_apply,
            "target_options_last_attempt": c._last_target_options_attempt,
            "auto_select_last_attempt": c._last_auto_select_attempt,
            "cycle_target_last_attempt": c._last_cycle_target_attempt,
            "restore_last_valid_last_attempt": c._last_restore_last_valid_attempt,
            "track_last_valid_last_attempt": c._last_track_last_valid_attempt,
            "target_entity_source": "route_trace.active_target",
            "control_center_settings": c._control_center_settings,
            "setup_entity_policy": c.setup_entity_policy,
            "control_center_last_attempt": c._last_control_center_action_attempt,
            "meta_policy": meta_policy,
        }

    def build_snapshot(self) -> dict[str, Any]:
        """Build complete coordinator snapshot packet with parity/validation surfaces."""
        c = self._coordinator
        active_target = c._snapshot_for_entity(LEGACY_SURFACES["active_target"])
        active_control_path = c._snapshot_for_entity(LEGACY_SURFACES["active_control_path"])
        control_hosts = c._snapshot_for_entity(LEGACY_SURFACES["control_hosts"])
        active_control_capable = c._snapshot_for_entity(
            LEGACY_SURFACES["active_control_capable"],
            as_bool=True,
        )

        legacy = {
            "active_target": active_target.state,
            "active_control_path": active_control_path.state,
            "control_hosts": control_hosts.state,
            "active_control_capable": active_control_capable.value,
        }

        parity = {
            "active_target": active_target.value,
            "active_control_path": active_control_path.value,
            "control_hosts": control_hosts.value,
            "active_control_capable": active_control_capable.value,
        }

        unresolved_sources: list[str] = []
        for key, snapshot in {
            "active_target": active_target,
            "active_control_path": active_control_path,
            "control_hosts": control_hosts,
            "active_control_capable": active_control_capable,
        }.items():
            if not snapshot.available:
                unresolved_sources.append(key)

        mismatches = [
            key
            for key in ("active_target", "active_control_path", "control_hosts", "active_control_capable")
            if parity[key] != legacy[key]
        ]

        registry = build_registry_snapshot(
            hass=c.hass,
            legacy_control_host_entity=LEGACY_CONTROL_HOST,
            legacy_control_targets_entity=LEGACY_CONTROL_TARGETS,
            legacy_rooms_json_entity=LEGACY_ROOMS_JSON,
            legacy_rooms_raw_entity=LEGACY_ROOMS_RAW,
            legacy_active_target_helper_entity=None,
            legacy_active_target_entity=LEGACY_SURFACES["active_target"],
        )

        route_trace = build_route_trace(
            active_target=str(parity.get("active_target", "") or ""),
            active_control_path=str(parity.get("active_control_path", "") or ""),
            registry=registry,
        )

        selected_target = (
            route_trace.get("selected_target", {})
            if isinstance(route_trace.get("selected_target", {}), dict)
            else {}
        )

        def _clean_text(raw: Any) -> str:
            value = str(raw or "").strip()
            if value.lower() in {"", "none", "unknown", "unavailable", "null"}:
                return ""
            return value

        def _clean_port(raw: Any) -> str:
            value = _clean_text(raw)
            if value == "":
                return ""
            try:
                num = int(float(value))
            except (TypeError, ValueError):
                return ""
            return str(num) if 0 < num <= 65534 else ""

        route_host = _clean_text(
            route_trace.get("control_host")
            or route_trace.get("active_host")
            or route_trace.get("host")
        )
        route_port = _clean_port(
            route_trace.get("control_port")
            or route_trace.get("active_port")
            or route_trace.get("port")
        )

        selected_host = _clean_text(selected_target.get("host", ""))
        component_host = _clean_text(c.hass.states.get("sensor.component_control_host").state if c.hass.states.get("sensor.component_control_host") is not None else "")
        runtime_host = _clean_text(c.hass.states.get(LEGACY_CONTROL_HOST).state if c.hass.states.get(LEGACY_CONTROL_HOST) is not None else "")
        parity_hosts = _clean_text(parity.get("control_hosts", ""))
        if "," in parity_hosts:
            parity_hosts = _clean_text(parity_hosts.split(",", 1)[0])

        selected_port = _clean_port(selected_target.get("port", ""))
        component_port = _clean_port(c.hass.states.get("sensor.component_control_port").state if c.hass.states.get("sensor.component_control_port") is not None else "")
        runtime_port = _clean_port(c.hass.states.get("sensor.ma_control_port").state if c.hass.states.get("sensor.ma_control_port") is not None else "")

        resolved_route_host = route_host or selected_host or component_host or runtime_host or parity_hosts
        resolved_route_port = route_port or selected_port or component_port or runtime_port

        route_trace = {
            **route_trace,
            "control_host": resolved_route_host,
            "active_host": resolved_route_host,
            "host": resolved_route_host,
            "control_port": resolved_route_port,
            "active_port": resolved_route_port,
            "port": resolved_route_port,
        }

        validation_packet = c._meta_fabric.build_snapshot_validation_packet(
            parity=parity,
            registry=registry,
            route_trace=route_trace,
        )
        host_control_cutover_gate = self._dict_surface(validation_packet, "host_control_cutover_gate")
        contract_validation = self._dict_surface(validation_packet, "contract_validation")
        selection_handoff_validation = self._dict_surface(validation_packet, "selection_handoff_validation")
        route_safety_validation = self._dict_surface(validation_packet, "route_safety_validation")
        metadata_prep_validation = self._dict_surface(validation_packet, "metadata_prep_validation")
        metadata_bridge_validation = self._dict_surface(validation_packet, "metadata_bridge_validation")
        cutover_prep_validation = self._dict_surface(validation_packet, "cutover_prep_validation")
        capability_profile_validation = self._dict_surface(validation_packet, "capability_profile_validation")
        action_catalog_validation = self._dict_surface(validation_packet, "action_catalog_validation")
        crossfade_balance_validation = self._dict_surface(validation_packet, "crossfade_balance_validation")
        scheduler_validation = self._dict_surface(validation_packet, "scheduler_validation")
        control_center_validation = self._dict_surface(validation_packet, "control_center_validation")

        ma_backend_profile = c._build_ma_backend_profile()

        return {
            "legacy": legacy,
            "parity": parity,
            "unresolved_sources": unresolved_sources,
            "mismatches": mismatches,
            "registry": registry,
            "route_trace": route_trace,
            "host_control_cutover_gate": host_control_cutover_gate,
            "contract_validation": contract_validation,
            "selection_handoff_validation": selection_handoff_validation,
            "route_safety_validation": route_safety_validation,
            "metadata_prep_validation": metadata_prep_validation,
            "capability_profile_validation": capability_profile_validation,
            "action_catalog_validation": action_catalog_validation,
            "crossfade_balance_validation": crossfade_balance_validation,
            "scheduler_validation": scheduler_validation,
            "metadata_bridge_validation": metadata_bridge_validation,
            "cutover_prep_validation": cutover_prep_validation,
            "handoff_inventory": c._build_handoff_inventory(),
            "ma_backend_profile": ma_backend_profile,
            "control_center_validation": control_center_validation,
            "write_controls": self.build_write_controls(),
            "captured_at": datetime.now(UTC).isoformat(),
        }
