# Description: Scaffold-fabric workflow for Spectra LS scaffold/inventory/backend assembly extracted from meta-fabric.
# Version: 2026.05.03.1
# Last updated: 2026-05-03
# PARITY DIRECTIVE (until full cutover): behavior/contract edits here require same-slice two-track parity review
# and version-metadata review in runtime (`packages/` + `esphome/`) and component (`custom_components/spectra_ls/`) tracks.

from __future__ import annotations

from typing import Any

from .const import (
    LEGACY_ACTIVE_TARGET_HELPER,
    LEGACY_CONTROL_HOST,
    LEGACY_CONTROL_TARGETS,
    LEGACY_META_DETECTED_ENTITY,
    LEGACY_META_OVERRIDE_ACTIVE,
    LEGACY_META_OVERRIDE_ENTITY,
    LEGACY_META_RESOLVER,
    LEGACY_ROOMS_JSON,
    LEGACY_ROOMS_RAW,
    LEGACY_SERVER_PROFILE,
    LEGACY_SERVER_PROFILE_EFFECTIVE,
    LEGACY_SURFACES,
)
from .registry import build_registry_snapshot
from .router import build_route_trace


class ScaffoldFabricWorkflow:
    """Owns scaffold/backend assembly seams extracted from meta-fabric."""

    def __init__(
        self,
        coordinator: Any,
        selection_fabric: Any,
        validation_fabric: Any,
    ) -> None:
        self._coordinator = coordinator
        self._selection_fabric = selection_fabric
        self._validation_fabric = validation_fabric

    def build_component_scaffolds(self) -> dict[str, Any]:
        """Build component-native scaffold plans for selection/metadata ownership handoff."""
        c = self._coordinator
        registry: dict[str, Any]
        route_trace: dict[str, Any]
        if isinstance(c.data, dict) and isinstance(c.data.get("registry", {}), dict):
            registry = c.data.get("registry", {})
        else:
            registry = build_registry_snapshot(
                hass=c.hass,
                legacy_control_host_entity=LEGACY_CONTROL_HOST,
                legacy_control_targets_entity=LEGACY_CONTROL_TARGETS,
                legacy_rooms_json_entity=LEGACY_ROOMS_JSON,
                legacy_rooms_raw_entity=LEGACY_ROOMS_RAW,
                legacy_active_target_helper_entity=LEGACY_ACTIVE_TARGET_HELPER,
                legacy_active_target_entity=LEGACY_SURFACES["active_target"],
            )

        if isinstance(c.data, dict) and isinstance(c.data.get("route_trace", {}), dict):
            route_trace = c.data.get("route_trace", {})
        else:
            active_target_state = c.hass.states.get(LEGACY_SURFACES["active_target"])
            active_control_path_state = c.hass.states.get(LEGACY_SURFACES["active_control_path"])
            route_trace = build_route_trace(
                active_target=str(active_target_state.state if active_target_state is not None else ""),
                active_control_path=str(
                    active_control_path_state.state if active_control_path_state is not None else ""
                ),
                registry=registry,
            )

        target_options_plan = self._selection_fabric.compute_component_target_options_plan()
        helper_options = (
            target_options_plan.get("proposed_options", [])
            if isinstance(target_options_plan.get("proposed_options", []), list)
            else []
        )
        candidates = (
            target_options_plan.get("selectable_candidates", [])
            if isinstance(target_options_plan.get("selectable_candidates", []), list)
            else []
        )
        detected_candidate = str(target_options_plan.get("detected_candidate", "") or "").strip()

        active_target = str(route_trace.get("active_target", "") or "").strip()
        selected_target = ""
        selection_reason = "no_candidate"
        detected_ready = False
        if c._is_resolved_state(detected_candidate) and detected_candidate in helper_options:
            detected_state = c.hass.states.get(detected_candidate)
            if detected_state is not None:
                detected_norm = c._normalize_state(str(detected_state.state or ""))
                detected_ready = detected_norm not in {"", "unknown", "unavailable"}

        if detected_ready:
            selected_target = detected_candidate
            selection_reason = "detected_candidate_ready"
        elif active_target and active_target in candidates:
            selected_target = active_target
            selection_reason = "active_target_candidate"
        else:
            for target_id in helper_options:
                if target_id.lower() == "none" or not target_id.startswith("media_player."):
                    continue
                state = c.hass.states.get(target_id)
                if state is None:
                    continue
                state_l = c._normalize_state(state.state)
                if state_l in {"playing", "paused"}:
                    selected_target = target_id
                    selection_reason = "first_active_helper_option"
                    break
        if not selected_target and candidates:
            selected_target = candidates[0]
            selection_reason = "first_candidate_fallback"

        best_candidate = ""
        best_score = 0
        meta_resolver_state = c.hass.states.get(LEGACY_META_RESOLVER)
        if meta_resolver_state is not None:
            best_candidate = str(meta_resolver_state.attributes.get("best_entity", "") or "").strip()
            best_score = int(meta_resolver_state.attributes.get("best_score", 0) or 0)

        detected_candidate = str(
            c.hass.states.get(LEGACY_META_DETECTED_ENTITY).state
            if c.hass.states.get(LEGACY_META_DETECTED_ENTITY) is not None
            else ""
        ).strip()
        detected_candidate = detected_candidate if c._is_resolved_state(detected_candidate) else ""

        selected_meta_entity = ""
        metadata_selection_reason = "no_candidate"
        if c._is_resolved_state(best_candidate):
            selected_meta_entity = best_candidate
            metadata_selection_reason = "meta_resolver_best_entity"
        elif detected_candidate:
            selected_meta_entity = detected_candidate
            metadata_selection_reason = "detected_meta_entity"

        if not selected_meta_entity and selected_target:
            selected_meta_entity = selected_target
            metadata_selection_reason = "selected_target_fallback"

        override_state = c.hass.states.get(LEGACY_META_OVERRIDE_ACTIVE)
        override_entity_state = c.hass.states.get(LEGACY_META_OVERRIDE_ENTITY)
        override_active = c._normalize_state(override_state.state if override_state is not None else "") == "on"
        override_entity = str(override_entity_state.state if override_entity_state is not None else "").strip()
        override_entity = override_entity if c._is_resolved_state(override_entity) else ""

        return {
            "target_options_plan": target_options_plan,
            "auto_select_plan": {
                "active_target": active_target,
                "selected_target": selected_target,
                "selection_reason": selection_reason,
                "ready": selected_target != "",
            },
            "metadata_resolver_plan": {
                "override_active_entity": LEGACY_META_OVERRIDE_ACTIVE,
                "override_entity_helper": LEGACY_META_OVERRIDE_ENTITY,
                "current_override_active": override_active,
                "current_override_entity": override_entity,
                "meta_resolver_entity": LEGACY_META_RESOLVER,
                "detected_meta_entity_source": LEGACY_META_DETECTED_ENTITY,
                "best_candidate": best_candidate,
                "best_score": best_score,
                "detected_candidate": detected_candidate,
                "selected_meta_entity": selected_meta_entity,
                "selection_reason": metadata_selection_reason,
                "ready": selected_meta_entity != "",
            },
        }

    def build_handoff_inventory(self) -> dict[str, Any]:
        """Build legacy dependency and scaffold-status handoff inventory packet."""
        c = self._coordinator
        component_scaffolds = self.build_component_scaffolds()
        target_options_attempt = c._last_target_options_attempt if isinstance(c._last_target_options_attempt, dict) else {}
        auto_select_attempt = c._last_auto_select_attempt if isinstance(c._last_auto_select_attempt, dict) else {}
        metadata_attempt = c.metadata_stack.last_metadata_resolver_attempt
        metadata_bridge_attempt = c.metadata_stack.last_metadata_bridge_attempt
        status_surfaces = self._validation_fabric.evaluate_handoff_scaffold_statuses(
            component_scaffolds=component_scaffolds,
            target_options_attempt=target_options_attempt,
            auto_select_attempt=auto_select_attempt,
            metadata_attempt=metadata_attempt,
            metadata_bridge_attempt=metadata_bridge_attempt,
        )
        target_options_status = str(status_surfaces.get("target_options_status", "planned") or "planned")
        auto_select_status = str(status_surfaces.get("auto_select_status", "planned") or "planned")
        metadata_status = str(status_surfaces.get("metadata_status", "planned") or "planned")

        legacy_dependency_map = self._validation_fabric.build_handoff_dependency_map(
            target_options_status=target_options_status,
            auto_select_status=auto_select_status,
            metadata_status=metadata_status,
        )

        implemented = sum(
            1 for row in legacy_dependency_map if row.get("component_scaffold_status") == "implemented"
        )
        scaffolded = sum(
            1 for row in legacy_dependency_map if row.get("component_scaffold_status") == "scaffolded"
        )
        planned = sum(1 for row in legacy_dependency_map if row.get("component_scaffold_status") == "planned")
        deferred = sum(1 for row in legacy_dependency_map if row.get("component_scaffold_status") == "deferred")

        return {
            "schema_version": "handoff_inventory.v1",
            "legacy_dependency_map": legacy_dependency_map,
            "component_scaffolds": component_scaffolds,
            "summary": {
                "total": len(legacy_dependency_map),
                "implemented": implemented,
                "scaffolded": scaffolded,
                "planned": planned,
                "deferred": deferred,
                "ready_for_full_handoff": planned == 0 and deferred == 0,
            },
        }

    def build_ma_backend_profile(self) -> dict[str, Any]:
        """Build MA backend profile/effective URL diagnostics payload."""
        c = self._coordinator
        profile_state = c.hass.states.get(LEGACY_SERVER_PROFILE)
        profile_effective_state = c.hass.states.get(LEGACY_SERVER_PROFILE_EFFECTIVE)

        profile_value = ""
        if profile_state is not None:
            profile_value = str(profile_state.state or "").strip().lower()

        selected_url = ""
        if profile_effective_state is not None:
            selected_url = str(profile_effective_state.attributes.get("selected_url", "") or "").strip()

        return {
            "profile_entity": LEGACY_SERVER_PROFILE,
            "effective_entity": LEGACY_SERVER_PROFILE_EFFECTIVE,
            "profile": profile_value,
            "selected_url": selected_url,
            "profile_resolved": c._is_resolved_state(profile_value),
            "selected_url_resolved": c._is_resolved_state(selected_url),
        }
