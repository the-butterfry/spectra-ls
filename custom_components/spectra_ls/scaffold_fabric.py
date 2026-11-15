# Description: Scaffold-fabric workflow for Spectra LS scaffold/inventory/backend assembly extracted from meta-fabric.
# Version: 2026.11.14.1
# Last updated: 2026-11-14
# PARITY DIRECTIVE (until full cutover): behavior/contract edits here require same-slice two-track parity review
# and version-metadata review in runtime (`packages/` + `esphome/`) and component (`custom_components/spectra_ls/`) tracks.

from __future__ import annotations

from typing import Any

from .const import (
    COMPONENT_NOW_PLAYING_ENTITY,
)


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
            registry = {"entries": {}, "target_count": 0, "unresolved_sources": ["registry_missing"]}

        if isinstance(c.data, dict) and isinstance(c.data.get("route_trace", {}), dict):
            route_trace = c.data.get("route_trace", {})
        else:
            component_active_target_state = c.hass.states.get("sensor.component_active_target")
            active_target = str(component_active_target_state.state if component_active_target_state is not None else "")
            route_trace = {
                "active_target": active_target,
                "active_control_path": "linkplay_tcp" if c._is_resolved_state(active_target) else "unknown",
                "resolved_control_path": "linkplay_tcp" if c._is_resolved_state(active_target) else "unknown",
                "decision": "route_linkplay_tcp" if c._is_resolved_state(active_target) else "defer_no_target",
                "reason": "component_fallback_route_trace",
                "selected_target": {},
            }

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

        metadata_prep = c.data.get("metadata_prep_validation", {}) if isinstance(getattr(c, "data", {}), dict) and isinstance(c.data.get("metadata_prep_validation", {}), dict) else {}
        metadata_values = metadata_prep.get("values", {}) if isinstance(metadata_prep.get("values", {}), dict) else {}
        best_candidate = str(metadata_values.get("resolver_best_candidate", "") or "").strip()
        try:
            best_score = int(float(metadata_values.get("resolver_best_score", 0) or 0))
        except (TypeError, ValueError):
            best_score = 0

        detected_candidate = str(
            c.hass.states.get(COMPONENT_NOW_PLAYING_ENTITY).state
            if c.hass.states.get(COMPONENT_NOW_PLAYING_ENTITY) is not None
            else ""
        ).strip()
        detected_candidate = detected_candidate if c._is_resolved_state(detected_candidate) else ""

        override_store = getattr(c, "_component_metadata_override_state", {})
        override_active = bool(override_store.get("active", False)) if isinstance(override_store, dict) else False
        override_entity = str(override_store.get("entity", "") or "").strip()
        override_entity = override_entity if c._is_resolved_state(override_entity) else ""

        selected_meta_entity = ""
        metadata_selection_reason = "no_candidate"
        if override_active and override_entity:
            selected_meta_entity = override_entity
            metadata_selection_reason = "component_override_entity"
        elif c._is_resolved_state(best_candidate):
            selected_meta_entity = best_candidate
            metadata_selection_reason = "meta_resolver_best_entity"
        elif detected_candidate:
            selected_meta_entity = detected_candidate
            metadata_selection_reason = "detected_meta_entity"

        if not selected_meta_entity and selected_target:
            selected_meta_entity = selected_target
            metadata_selection_reason = "selected_target_fallback"

        return {
            "target_options_plan": target_options_plan,
            "auto_select_plan": {
                "active_target": active_target,
                "selected_target": selected_target,
                "selection_reason": selection_reason,
                "ready": selected_target != "",
            },
            "metadata_resolver_plan": {
                "override_active_entity": "component_metadata_override_active",
                "override_entity_helper": "component_metadata_override_entity",
                "current_override_active": override_active,
                "current_override_entity": override_entity,
                "meta_resolver_entity": "component_meta_candidates",
                "detected_meta_entity_source": COMPONENT_NOW_PLAYING_ENTITY,
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
        metadata_prep_validation = (
            c.data.get("metadata_prep_validation", {})
            if isinstance(getattr(c, "data", {}), dict)
            and isinstance(c.data.get("metadata_prep_validation", {}), dict)
            else {}
        )
        metadata_bridge_validation = (
            c.data.get("metadata_bridge_validation", {})
            if isinstance(getattr(c, "data", {}), dict)
            and isinstance(c.data.get("metadata_bridge_validation", {}), dict)
            else {}
        )
        component_now_playing_entity_state = c.hass.states.get("sensor.component_now_playing_entity")
        component_now_playing_entity = (
            str(component_now_playing_entity_state.state or "").strip()
            if component_now_playing_entity_state is not None
            else ""
        )
        status_surfaces = self._validation_fabric.evaluate_handoff_scaffold_statuses(
            component_scaffolds=component_scaffolds,
            target_options_attempt=target_options_attempt,
            auto_select_attempt=auto_select_attempt,
            metadata_attempt=metadata_attempt,
            metadata_bridge_attempt=metadata_bridge_attempt,
            metadata_prep_validation=metadata_prep_validation,
            metadata_bridge_validation=metadata_bridge_validation,
            component_now_playing_entity=component_now_playing_entity,
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
        profile_value = "component_discovered"
        selected_url = ""
        api_url = ""

        selected_url_fallback = ""
        if not c._is_resolved_state(selected_url):
            internal_url = str(getattr(c.hass.config, "internal_url", "") or "").strip()
            external_url = str(getattr(c.hass.config, "external_url", "") or "").strip()
            selected_url_fallback = internal_url or external_url
            if c._is_resolved_state(selected_url_fallback):
                selected_url = selected_url_fallback.rstrip("/")

        if not c._is_resolved_state(api_url) and c._is_resolved_state(selected_url):
            api_url = f"{selected_url.rstrip('/')}/api"

        if not c._is_resolved_state(profile_value):
            if c._is_resolved_state(selected_url):
                profile_value = "component_discovered"
            elif c._is_resolved_state(api_url):
                profile_value = "api_only_discovered"

        return {
            "profile_entity": "component_backend_profile",
            "effective_entity": "component_backend_profile",
            "api_url_entity": "component_ma_api_url",
            "profile": profile_value,
            "selected_url": selected_url,
            "selected_url_fallback": selected_url_fallback,
            "api_url": api_url,
            "profile_resolved": c._is_resolved_state(profile_value),
            "selected_url_resolved": c._is_resolved_state(selected_url),
            "api_url_resolved": c._is_resolved_state(api_url),
        }
