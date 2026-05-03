# Description: Snapshot-fabric workflow for Spectra LS coordinator snapshot and write-controls packet assembly extracted from coordinator.
# Version: 2026.05.03.3
# Last updated: 2026-05-03
# PARITY DIRECTIVE (until full cutover): behavior/contract edits here require same-slice two-track parity review
# and version-metadata review in runtime (`packages/` + `esphome/`) and component (`custom_components/spectra_ls/`) tracks.

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .const import (
    LEGACY_ACTIVE_TARGET_HELPER,
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

    def build_write_controls(self) -> dict[str, Any]:
        """Build write-controls packet from coordinator and meta-fabric surfaces."""
        c = self._coordinator
        meta_policy = c._meta_fabric.build_meta_policy_surface()
        metadata_surfaces = c._meta_fabric.build_write_controls_metadata_surfaces()

        return {
            "authority_mode": c._write_authority_mode,
            "allowed_modes": list(WRITE_AUTH_ALLOWED),
            "debounce_s": c._write_debounce_s,
            "in_progress": c._write_in_progress,
            "last_attempt": c._last_write_attempt,
            **metadata_surfaces,
            "scheduler_last_decision": c._last_scheduler_decision,
            "scheduler_last_apply": c._last_scheduler_apply,
            "target_options_last_attempt": c._last_target_options_attempt,
            "auto_select_last_attempt": c._last_auto_select_attempt,
            "cycle_target_last_attempt": c._last_cycle_target_attempt,
            "restore_last_valid_last_attempt": c._last_restore_last_valid_attempt,
            "track_last_valid_last_attempt": c._last_track_last_valid_attempt,
            "target_helper_entity": LEGACY_ACTIVE_TARGET_HELPER,
            "control_center_settings": c._control_center_settings,
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
            legacy_active_target_helper_entity=LEGACY_ACTIVE_TARGET_HELPER,
            legacy_active_target_entity=LEGACY_SURFACES["active_target"],
        )

        route_trace = build_route_trace(
            active_target=str(parity.get("active_target", "") or ""),
            active_control_path=str(parity.get("active_control_path", "") or ""),
            registry=registry,
        )
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
