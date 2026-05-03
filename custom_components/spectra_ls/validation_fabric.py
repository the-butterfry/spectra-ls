# Description: Validation/control fabric workflow for Spectra LS snapshot validation assembly extracted from meta-fabric.
# Version: 2026.05.03.3
# Last updated: 2026-05-03
# PARITY DIRECTIVE (until full cutover): behavior/contract edits here require same-slice two-track parity review
# and version-metadata review in runtime (`packages/` + `esphome/`) and component (`custom_components/spectra_ls/`) tracks.

from __future__ import annotations

from typing import Any

from .const import (
    LEGACY_ACTIVE_TARGET_HELPER,
    LEGACY_CONTROL_HOST,
    LEGACY_CONTROL_TARGETS,
    LEGACY_META_CONFIDENCE_MIN,
    LEGACY_META_PAUSED_HIDE_S,
    LEGACY_META_STALE_S,
    LEGACY_ROOMS_JSON,
    LEGACY_ROOMS_RAW,
    LEGACY_SURFACES,
    META_POLICY_DEFAULTS,
    WRITE_AUTH_ALLOWED,
    WRITE_AUTH_COMPONENT,
)
from .selection_fabric import SelectionFabricWorkflow
from .write_path_fabric import WritePathFabric


class ValidationFabricWorkflow:
    """Owns validation/control assembly methods extracted from meta-fabric."""

    def __init__(self, coordinator: Any, selection_fabric: SelectionFabricWorkflow) -> None:
        self._coordinator = coordinator
        self._selection_fabric = selection_fabric

    def build_metadata_validation_bundle(
        self,
        *,
        route_trace: dict[str, Any],
        contract_validation: dict[str, Any],
    ) -> dict[str, Any]:
        """Build metadata prep/bridge/cutover validation bundle for snapshot assembly."""
        c = self._coordinator
        metadata_prep_validation = c.metadata_stack.build_metadata_prep_validation(
            route_trace=route_trace,
            contract_validation=contract_validation,
        )
        metadata_bridge_validation = c.metadata_stack.build_metadata_bridge_validation(
            metadata_prep_validation=metadata_prep_validation,
        )
        cutover_prep_validation = c.metadata_stack.build_cutover_prep_validation(
            metadata_prep_validation=metadata_prep_validation,
            metadata_bridge_validation=metadata_bridge_validation,
        )
        return {
            "metadata_prep_validation": metadata_prep_validation,
            "metadata_bridge_validation": metadata_bridge_validation,
            "cutover_prep_validation": cutover_prep_validation,
        }

    def normalize_metadata_validation_bundle(
        self,
        metadata_bundle: dict[str, Any],
    ) -> dict[str, dict[str, Any]]:
        """Normalize metadata validation bundle payload shapes for snapshot assembly."""
        prep = (
            metadata_bundle.get("metadata_prep_validation", {})
            if isinstance(metadata_bundle.get("metadata_prep_validation", {}), dict)
            else {}
        )
        bridge = (
            metadata_bundle.get("metadata_bridge_validation", {})
            if isinstance(metadata_bundle.get("metadata_bridge_validation", {}), dict)
            else {}
        )
        cutover = (
            metadata_bundle.get("cutover_prep_validation", {})
            if isinstance(metadata_bundle.get("cutover_prep_validation", {}), dict)
            else {}
        )
        return {
            "metadata_prep_validation": prep,
            "metadata_bridge_validation": bridge,
            "cutover_prep_validation": cutover,
        }

    def build_write_controls_metadata_surfaces(self) -> dict[str, Any]:
        """Build metadata-related write-control surfaces for coordinator snapshot payload."""
        c = self._coordinator
        return {
            "metadata_trial_in_progress": c.metadata_stack.metadata_trial_in_progress,
            "metadata_trial_last_attempt": c.metadata_stack.last_metadata_trial_attempt,
            "metadata_resolver_last_attempt": c.metadata_stack.last_metadata_resolver_attempt,
            "metadata_bridge_last_attempt": c.metadata_stack.last_metadata_bridge_attempt,
        }

    def build_meta_policy_surface(self) -> dict[str, Any]:
        """Build metadata policy surface from helpers/defaults for write-controls payload."""
        c = self._coordinator
        return {
            "mode": str(META_POLICY_DEFAULTS.get("mode", "auto")),
            "meta_stale_s": c._read_float_helper(
                LEGACY_META_STALE_S,
                float(META_POLICY_DEFAULTS.get("meta_stale_s", 45.0)),
            ),
            "paused_hide_s": c._read_float_helper(
                LEGACY_META_PAUSED_HIDE_S,
                float(META_POLICY_DEFAULTS.get("paused_hide_s", 600.0)),
            ),
            "confidence_min": c._read_float_helper(
                LEGACY_META_CONFIDENCE_MIN,
                float(META_POLICY_DEFAULTS.get("confidence_min", 4.0)),
            ),
            "clear_when_no_active_playback": bool(
                META_POLICY_DEFAULTS.get("clear_when_no_active_playback", True)
            ),
            "control_host_coupling": bool(META_POLICY_DEFAULTS.get("control_host_coupling", True)),
        }

    @staticmethod
    def evaluate_handoff_scaffold_statuses(
        *,
        component_scaffolds: dict[str, Any],
        target_options_attempt: dict[str, Any],
        auto_select_attempt: dict[str, Any],
        metadata_attempt: dict[str, Any],
        metadata_bridge_attempt: dict[str, Any],
    ) -> dict[str, str]:
        """Evaluate handoff scaffold status ladder for target-options, auto-select, and metadata lanes."""
        target_options_status = "planned"
        if bool(component_scaffolds.get("target_options_plan", {}).get("candidates")):
            target_options_status = "scaffolded"
        target_options_attempt_status = str(target_options_attempt.get("status", "") or "")
        if target_options_attempt_status in {"dry_run_ok", "options_applied"}:
            target_options_status = "implemented"

        auto_select_status = "planned"
        if bool(component_scaffolds.get("auto_select_plan", {}).get("selected_target")):
            auto_select_status = "scaffolded"
        auto_select_attempt_status = str(auto_select_attempt.get("status", "") or "")
        if auto_select_attempt_status in {"dry_run_ok", "noop_already_selected", "write_applied"}:
            auto_select_status = "implemented"

        metadata_status = (
            "scaffolded"
            if bool(component_scaffolds.get("metadata_resolver_plan", {}).get("selected_meta_entity"))
            else "planned"
        )
        metadata_attempt_status = str(metadata_attempt.get("status", "") or "")
        metadata_bridge_status = str(metadata_bridge_attempt.get("status", "") or "")
        if (
            metadata_attempt_status in {"dry_run_ok", "noop_already_selected", "write_applied"}
            or metadata_bridge_status == "bridge_completed"
        ):
            metadata_status = "implemented"

        return {
            "target_options_status": target_options_status,
            "auto_select_status": auto_select_status,
            "metadata_status": metadata_status,
        }

    @staticmethod
    def build_handoff_dependency_map(
        *,
        target_options_status: str,
        auto_select_status: str,
        metadata_status: str,
    ) -> list[dict[str, Any]]:
        """Build handoff dependency map rows from scaffold-status surfaces."""
        return [
            {
                "feature": "target_options_builder",
                "legacy_surface": "script.ma_update_target_options",
                "component_scaffold_status": target_options_status,
                "component_surface": "handoff_inventory.target_options_builder",
                "scheduler_relevance": "high",
                "notes": "Component now exposes candidate/options scaffold plan; write-path ownership still legacy.",
            },
            {
                "feature": "auto_select_pipeline",
                "legacy_surface": "script.ma_auto_select",
                "component_scaffold_status": auto_select_status,
                "component_surface": "handoff_inventory.auto_select_pipeline",
                "scheduler_relevance": "high",
                "notes": "Component now exposes deterministic auto-select planning scaffold; runtime loop remains legacy-owned.",
            },
            {
                "feature": "active_target_apply",
                "legacy_surface": "input_select.ma_active_target",
                "component_scaffold_status": "implemented",
                "component_surface": "service.apply_scheduler_choice",
                "scheduler_relevance": "high",
                "notes": "Guarded component apply path now available (authority/debounce/reentrancy/option guards).",
            },
            {
                "feature": "metadata_resolver_authority",
                "legacy_surface": "sensor.ma_active_meta_entity / sensor.now_playing_entity",
                "component_scaffold_status": metadata_status,
                "component_surface": "service.run_metadata_resolver_scaffold + metadata_prep_validation",
                "scheduler_relevance": "medium",
                "notes": "Component metadata authority can activate when write authority is component and resolver cutover readiness is satisfied; legacy remains rollback baseline.",
            },
            {
                "feature": "control_host_resolution_runtime_authority",
                "legacy_surface": "sensor.ma_control_hosts / sensor.ma_control_host",
                "component_scaffold_status": "implemented",
                "component_surface": "registry.host_resolution + route_trace",
                "scheduler_relevance": "high",
                "notes": "Pluggable host resolver + route-trace scaffolds implemented for scheduler feed.",
            },
        ]

    def build_scheduler_validation(
        self,
        *,
        registry: dict[str, Any],
        route_trace: dict[str, Any],
        contract_validation: dict[str, Any],
    ) -> dict[str, Any]:
        """Build scheduler readiness and default-decision validation payload."""
        c = self._coordinator
        contract_valid = bool(contract_validation.get("valid", False))
        route_decision = str(route_trace.get("decision", "") or "")
        ma_boot_ready, ma_boot_reasons = c._is_startup_recovery_boot_ready()
        ma_boot_wait_reason = c._format_startup_boot_wait_reasons(ma_boot_reasons)

        default_policy = {
            "require_control_capable": True,
            "prefer_fresh": True,
            "max_results": 5,
            "target_hint": "",
        }
        decision = self._selection_fabric.compute_scheduler_decision(
            registry=registry,
            route_trace=route_trace,
            policy=default_policy,
        )

        checks = {
            "contract_valid": contract_valid,
            "registry_present": isinstance(registry.get("entries", {}), dict)
            and len(registry.get("entries", {})) > 0,
            "route_trace_present": route_decision != "",
            "candidate_available": decision.get("candidate_count", 0) > 0,
            "no_authority_expansion": c._write_authority_mode in WRITE_AUTH_ALLOWED,
            "ma_boot_ready": ma_boot_ready,
        }

        verdict = "PASS"
        if not checks["route_trace_present"]:
            verdict = "FAIL"
        elif not checks["ma_boot_ready"]:
            verdict = "WARN"
        elif not checks["contract_valid"] or not checks["registry_present"]:
            verdict = "FAIL"
        elif not checks["candidate_available"] or not checks["no_authority_expansion"]:
            verdict = "WARN"

        blocking_reasons: list[str] = []
        if not checks["route_trace_present"]:
            blocking_reasons.append("route_trace_missing")
        if not checks["ma_boot_ready"]:
            blocking_reasons.append("waiting_for_ma_boot")
        if checks["ma_boot_ready"] and not checks["contract_valid"]:
            blocking_reasons.append("contract_invalid")
        if checks["ma_boot_ready"] and not checks["registry_present"]:
            blocking_reasons.append("registry_missing")
        if checks["ma_boot_ready"] and not checks["candidate_available"]:
            blocking_reasons.append("no_scheduler_candidate")
        if checks["ma_boot_ready"] and not checks["no_authority_expansion"]:
            blocking_reasons.append("authority_mode_not_legacy")

        return {
            "verdict": verdict,
            "ready_for_scheduler_use": verdict == "PASS",
            "checks": checks,
            "route_decision": route_decision,
            "default_policy": default_policy,
            "default_decision": decision,
            "blocking_reasons": blocking_reasons,
            "waiting_for_ma_boot": not ma_boot_ready,
            "ma_boot_wait_reasons": ma_boot_reasons,
            "ma_boot_wait_reason": ma_boot_wait_reason,
        }

    def build_contract_validation(self) -> dict[str, Any]:
        """Build required/soft contract validation payload for routing surfaces."""
        c = self._coordinator
        required_entities = {
            "active_target": LEGACY_SURFACES["active_target"],
            "active_control_path": LEGACY_SURFACES["active_control_path"],
            "active_control_capable": LEGACY_SURFACES["active_control_capable"],
            "control_targets": LEGACY_CONTROL_TARGETS,
            "rooms_json": LEGACY_ROOMS_JSON,
            "rooms_raw": LEGACY_ROOMS_RAW,
        }
        soft_required_entities = {
            "control_hosts": LEGACY_SURFACES["control_hosts"],
            "control_host": LEGACY_CONTROL_HOST,
        }
        missing_required = [
            key for key, entity_id in required_entities.items() if c.hass.states.get(entity_id) is None
        ]
        missing_soft_required = [
            key for key, entity_id in soft_required_entities.items() if c.hass.states.get(entity_id) is None
        ]
        unresolved_required: list[str] = []
        unresolved_soft_required: list[str] = []
        required_states: dict[str, str] = {}
        for key, entity_id in required_entities.items():
            state = c.hass.states.get(entity_id)
            state_value = state.state if state is not None else "missing"
            required_states[key] = state_value
            if state is None:
                continue
            if not c._is_resolved_state(state_value):
                unresolved_required.append(key)

        soft_required_states: dict[str, str] = {}
        for key, entity_id in soft_required_entities.items():
            state = c.hass.states.get(entity_id)
            state_value = state.state if state is not None else "missing"
            soft_required_states[key] = state_value
            if state is None:
                continue
            if not c._is_resolved_state(state_value):
                unresolved_soft_required.append(key)

        soft_surface_warnings = [*missing_soft_required, *unresolved_soft_required]

        return {
            "required_entities": required_entities,
            "soft_required_entities": soft_required_entities,
            "missing_required": missing_required,
            "missing_soft_required": missing_soft_required,
            "unresolved_required": unresolved_required,
            "unresolved_soft_required": unresolved_soft_required,
            "required_states": required_states,
            "soft_required_states": soft_required_states,
            "soft_surface_warnings": soft_surface_warnings,
            "valid": len(missing_required) == 0 and len(unresolved_required) == 0,
        }

    def build_selection_handoff_validation(
        self,
        *,
        parity: dict[str, Any],
        route_trace: dict[str, Any],
        contract_validation: dict[str, Any],
    ) -> dict[str, Any]:
        """Build selection-handoff compatibility/guard validation payload."""
        c = self._coordinator
        helper_state = c.hass.states.get(LEGACY_ACTIVE_TARGET_HELPER)
        helper_exists = helper_state is not None
        helper_options = WritePathFabric.normalize_options(
            helper_state.attributes.get("options", []) if helper_state is not None else []
        )

        active_target = str(parity.get("active_target", "") or "").strip()
        active_target_resolved = active_target.lower() not in {"", "none", "unknown", "unavailable"}
        target_in_helper_options = active_target_resolved and active_target in helper_options

        required_scripts = [
            "script.ma_update_target_options",
            "script.ma_auto_select",
            "script.ma_cycle_target",
        ]
        missing_scripts = [entity_id for entity_id in required_scripts if c.hass.states.get(entity_id) is None]

        required_automation_ids = [
            "ma_update_target_options_start",
            "ma_auto_select_loop",
            "ma_track_last_valid_target",
        ]
        available_automation_ids = {
            str(state.attributes.get("id", ""))
            for state in c.hass.states.async_all("automation")
            if isinstance(state.attributes.get("id", ""), str)
        }
        missing_automation_ids = [
            automation_id
            for automation_id in required_automation_ids
            if automation_id not in available_automation_ids
        ]

        route_decision = str(route_trace.get("decision", "") or "")
        route_ready = route_decision == "route_linkplay_tcp"
        contract_valid = bool(contract_validation.get("valid", False))

        verdict = "PASS"
        if not helper_exists or not active_target_resolved or not route_ready or not contract_valid:
            verdict = "FAIL"
        elif (
            not helper_options
            or not target_in_helper_options
            or len(missing_scripts) > 0
            or len(missing_automation_ids) > 0
        ):
            verdict = "WARN"

        return {
            "verdict": verdict,
            "ready_for_handoff": verdict == "PASS",
            "active_target": active_target,
            "route_decision": route_decision,
            "contract_valid": contract_valid,
            "helper": {
                "entity_id": LEGACY_ACTIVE_TARGET_HELPER,
                "exists": helper_exists,
                "options_count": len(helper_options),
                "target_in_options": target_in_helper_options,
            },
            "compatibility": {
                "required_scripts": required_scripts,
                "missing_scripts": missing_scripts,
                "required_automation_ids": required_automation_ids,
                "missing_automation_ids": missing_automation_ids,
            },
        }

    def build_route_safety_validation(
        self,
        *,
        parity: dict[str, Any],
        route_trace: dict[str, Any],
    ) -> dict[str, Any]:
        """Build explicit route-safety diagnostics for active-target binding and host posture."""
        c = self._coordinator
        active_target = str(parity.get("active_target", "") or "").strip()
        control_hosts = str(parity.get("control_hosts", "") or "").strip()
        route_decision = str(route_trace.get("decision", "") or "").strip()

        selected_target = route_trace.get("selected_target", {})
        selected_target = selected_target if isinstance(selected_target, dict) else {}
        selected_target_id = str(selected_target.get("target", "") or "").strip()
        selected_target_host = str(selected_target.get("host", "") or "").strip()

        active_target_resolved = c._is_resolved_state(active_target)
        control_hosts_resolved = c._is_resolved_state(control_hosts)
        selected_target_matches_active = (
            active_target_resolved
            and c._is_resolved_state(selected_target_id)
            and selected_target_id == active_target
        )
        selected_target_host_resolved = c._is_resolved_state(selected_target_host)

        blocking_reasons: list[str] = []
        if active_target_resolved and not selected_target_matches_active:
            blocking_reasons.append("selected_target_mismatch")
        if route_decision == "route_linkplay_tcp" and not selected_target_host_resolved:
            blocking_reasons.append("selected_target_host_unresolved")
        if not control_hosts_resolved:
            blocking_reasons.append("control_hosts_unresolved")

        verdict = "PASS"
        if "selected_target_mismatch" in blocking_reasons:
            verdict = "FAIL"
        elif "selected_target_host_unresolved" in blocking_reasons:
            verdict = "WARN"

        return {
            "verdict": verdict,
            "route_decision": route_decision,
            "active_target": active_target,
            "selected_target": selected_target_id,
            "selected_target_host": selected_target_host,
            "ready_for_cutover": verdict == "PASS" and selected_target_host_resolved,
            "checks": {
                "active_target_resolved": active_target_resolved,
                "selected_target_matches_active": selected_target_matches_active,
                "selected_target_host_resolved": selected_target_host_resolved,
                "control_hosts_resolved": control_hosts_resolved,
            },
            "blocking_reasons": blocking_reasons,
        }

    def build_host_control_cutover_gate(
        self,
        *,
        parity: dict[str, Any],
        registry: dict[str, Any],
        route_trace: dict[str, Any],
    ) -> dict[str, Any]:
        """Compute deterministic host-control cutover readiness for component authority windows."""
        c = self._coordinator
        entries = registry.get("entries", {}) if isinstance(registry.get("entries", {}), dict) else {}

        active_target = str(parity.get("active_target", "") or "").strip()
        selected_entry = entries.get(active_target)

        component_candidate_host = (
            str(selected_entry.get("host", "") or "").strip()
            if isinstance(selected_entry, dict)
            else ""
        )
        component_candidate_path = (
            str(selected_entry.get("control_path", "") or "").strip().lower()
            if isinstance(selected_entry, dict)
            else ""
        )
        component_candidate_capable = (
            bool(selected_entry.get("control_capable", False)) if isinstance(selected_entry, dict) else False
        )

        route_decision = str(route_trace.get("decision", "") or "").strip()
        resolved_control_path = str(route_trace.get("resolved_control_path", "") or "").strip().lower()

        legacy_control_host_state = c.hass.states.get(LEGACY_CONTROL_HOST)
        legacy_control_host = (
            str(legacy_control_host_state.state or "").strip()
            if legacy_control_host_state is not None
            else ""
        )
        if not c._is_resolved_state(legacy_control_host):
            legacy_control_host = ""

        legacy_control_hosts = str(parity.get("control_hosts", "") or "").strip()
        if not c._is_resolved_state(legacy_control_hosts):
            legacy_control_hosts = ""

        legacy_first_host = ""
        if legacy_control_hosts:
            legacy_first_host = str(legacy_control_hosts.split(",", 1)[0] or "").strip()

        checks = {
            "active_target_resolved": c._is_resolved_state(active_target),
            "target_present_in_registry": isinstance(selected_entry, dict),
            "candidate_host_resolved": c._is_resolved_state(component_candidate_host),
            "candidate_control_capable": bool(component_candidate_capable),
            "route_decision_supported": route_decision == "route_linkplay_tcp",
            "resolved_control_path_supported": resolved_control_path == "linkplay_tcp",
            "legacy_active_control_capable_true": bool(parity.get("active_control_capable", False)),
            "legacy_control_host_consistent": True,
            "legacy_control_hosts_first_consistent": True,
        }

        if legacy_control_host:
            checks["legacy_control_host_consistent"] = (
                component_candidate_host.lower() == legacy_control_host.lower()
            )
        if legacy_first_host:
            checks["legacy_control_hosts_first_consistent"] = (
                component_candidate_host.lower() == legacy_first_host.lower()
            )

        gate_blockers: list[str] = []
        if not checks["active_target_resolved"]:
            gate_blockers.append("active_target_unresolved")
        if not checks["target_present_in_registry"]:
            gate_blockers.append("target_missing_in_registry")
        if not checks["candidate_host_resolved"]:
            gate_blockers.append("component_candidate_host_unresolved")
        if not checks["candidate_control_capable"]:
            gate_blockers.append("component_candidate_not_control_capable")
        if not checks["route_decision_supported"]:
            gate_blockers.append(f"route_decision_not_supported:{route_decision or 'missing'}")
        if not checks["resolved_control_path_supported"]:
            gate_blockers.append(
                f"resolved_control_path_not_supported:{resolved_control_path or 'missing'}"
            )
        if not checks["legacy_active_control_capable_true"]:
            gate_blockers.append("legacy_active_control_capable_false")
        if not checks["legacy_control_host_consistent"]:
            gate_blockers.append("legacy_control_host_mismatch")
        if not checks["legacy_control_hosts_first_consistent"]:
            gate_blockers.append("legacy_control_hosts_first_mismatch")

        activation_blockers: list[str] = []
        if c._write_authority_mode != WRITE_AUTH_COMPONENT:
            activation_blockers.append("authority_mode_not_component")

        ready_for_cutover = len(gate_blockers) == 0
        ready_for_authoritative_activation = ready_for_cutover and len(activation_blockers) == 0

        return {
            "schema_version": "host_control_cutover_gate.v1",
            "status": "ready" if ready_for_cutover else "blocked",
            "ready_for_cutover": ready_for_cutover,
            "ready_for_authoritative_activation": ready_for_authoritative_activation,
            "authority_source_mode": (
                "component" if c._write_authority_mode == WRITE_AUTH_COMPONENT else "legacy"
            ),
            "authority_mode": c._write_authority_mode,
            "component_authoritative_candidate": {
                "target": active_target,
                "host": component_candidate_host,
                "control_path": component_candidate_path,
                "control_capable": component_candidate_capable,
            },
            "legacy_authority_snapshot": {
                "control_host": legacy_control_host,
                "control_hosts": legacy_control_hosts,
                "control_hosts_first": legacy_first_host,
                "active_control_capable": bool(parity.get("active_control_capable", False)),
            },
            "route_decision": route_decision,
            "resolved_control_path": resolved_control_path,
            "checks": checks,
            "gate_blockers": gate_blockers,
            "activation_blockers": activation_blockers,
        }

    def build_control_center_validation(self) -> dict[str, Any]:
        """Build control-center settings and execution-readiness diagnostics payload."""
        c = self._coordinator
        settings = dict(c._control_center_settings)
        mapping_preset = str(settings.get("mapping_preset", "custom") or "custom").strip().lower()
        required_keys = sorted(settings.keys())
        scene_keys = [
            "button_1_scene",
            "button_2_scene",
            "button_3_scene",
            "button_4_scene",
        ]
        unresolved_scenes = [
            key for key in scene_keys if str(settings.get(key, "") or "").strip().lower() in {"", "scene.none"}
        ]
        resolved_scene_bindings = [key for key in scene_keys if key not in unresolved_scenes]
        quick_trigger_scene = str(settings.get("button_1_scene", "scene.none") or "scene.none").strip()
        quick_trigger_ready = quick_trigger_scene.lower() not in {"", "scene.none"}

        effective_mapping = {
            "encoder_turn": str(settings.get("encoder_turn_action", "") or ""),
            "encoder_press": str(settings.get("encoder_press_action", "") or ""),
            "encoder_long_press": str(settings.get("encoder_long_press_action", "") or ""),
            "button_1": str(settings.get("button_1_scene", "scene.none") or "scene.none"),
            "button_2": str(settings.get("button_2_scene", "scene.none") or "scene.none"),
            "button_3": str(settings.get("button_3_scene", "scene.none") or "scene.none"),
            "button_4": str(settings.get("button_4_scene", "scene.none") or "scene.none"),
        }

        non_dry_run_supported_actions = [
            "scene_quick_trigger",
            "no_op",
            "button_1_scene",
            "button_2_scene",
            "button_3_scene",
            "button_4_scene",
        ]
        non_dry_run_pending_actions = [
            "volume",
            "brightness",
            "target_cycle",
            "source_cycle",
            "play_pause",
            "mute_toggle",
        ]

        readiness_state = "ready" if quick_trigger_ready or len(resolved_scene_bindings) > 0 else "needs_scene_binding"
        recommended_next_step = (
            "Bind at least one scene (button 1 recommended) to enable non-dry-run scene execution"
            if readiness_state != "ready"
            else "Control-center scene bindings are ready for bounded execution"
        )

        return {
            "schema_version": "p6_s02.v1",
            "settings": settings,
            "mapping_preset": mapping_preset,
            "preset_applied": mapping_preset != "custom",
            "effective_mapping": effective_mapping,
            "required_keys": required_keys,
            "settings_present": len(required_keys) > 0,
            "read_only_mode": bool(settings.get("read_only_mode", True)),
            "unresolved_scene_bindings": unresolved_scenes,
            "resolved_scene_bindings": resolved_scene_bindings,
            "configured_scene_bindings_count": len(resolved_scene_bindings),
            "total_scene_bindings": len(scene_keys),
            "quick_trigger_scene": quick_trigger_scene,
            "quick_trigger_ready": quick_trigger_ready,
            "non_dry_run_supported_actions": non_dry_run_supported_actions,
            "non_dry_run_pending_actions": non_dry_run_pending_actions,
            "readiness_state": readiness_state,
            "recommended_next_step": recommended_next_step,
            "ready_for_customization": len(required_keys) > 0,
            "ready_for_execution": readiness_state == "ready",
        }

    def build_capability_profile_validation(
        self,
        *,
        registry: dict[str, Any],
        route_trace: dict[str, Any],
        contract_validation: dict[str, Any],
        metadata_prep_validation: dict[str, Any],
    ) -> dict[str, Any]:
        """Build F4-S01 capability/profile validation packet from registry + route surfaces."""
        c = self._coordinator
        entries = registry.get("entries", {}) if isinstance(registry.get("entries", {}), dict) else {}
        targets = list(entries.values()) if isinstance(entries, dict) else []

        control_path_counts: dict[str, int] = {}
        hardware_family_counts: dict[str, int] = {}
        capabilities_union: set[str] = set()
        control_capable_count = 0

        for entry in targets:
            if not isinstance(entry, dict):
                continue
            control_path = str(entry.get("control_path", "unknown") or "unknown")
            hardware_family = str(entry.get("hardware_family", "unknown") or "unknown")
            control_path_counts[control_path] = control_path_counts.get(control_path, 0) + 1
            hardware_family_counts[hardware_family] = hardware_family_counts.get(hardware_family, 0) + 1

            if bool(entry.get("control_capable", False)):
                control_capable_count += 1

            caps = entry.get("capabilities", [])
            if isinstance(caps, list):
                for cap in caps:
                    if isinstance(cap, str) and cap.strip():
                        capabilities_union.add(cap.strip())

        route_decision = str(route_trace.get("decision", "") or "")
        contract_valid = bool(contract_validation.get("valid", False))
        metadata_ready = bool(metadata_prep_validation.get("ready_for_metadata_handoff", False))

        checks = {
            "registry_present": len(targets) > 0,
            "capability_matrix_present": len(control_path_counts) > 0,
            "route_trace_present": route_decision != "",
            "contract_valid": contract_valid,
            "metadata_prep_ready": metadata_ready,
            "no_authority_expansion": c._write_authority_mode in WRITE_AUTH_ALLOWED,
        }

        verdict = "PASS"
        if not checks["registry_present"] or not checks["route_trace_present"] or not checks["contract_valid"]:
            verdict = "FAIL"
        elif (
            not checks["capability_matrix_present"]
            or not checks["metadata_prep_ready"]
            or not checks["no_authority_expansion"]
        ):
            verdict = "WARN"

        profile_schema = {
            "schema_version": "f4_s01.v1",
            "required_keys": [
                "profile_id",
                "label",
                "target_scope",
                "routing_policy",
                "safety",
            ],
            "defaults": {
                "target_scope": "active_target",
                "routing_policy": "capability_mapped",
                "safety": {
                    "confirm_required": False,
                    "cooldown_s": 0,
                },
            },
        }

        return {
            "verdict": verdict,
            "ready_for_f4_s01": verdict == "PASS",
            "checks": checks,
            "authority_mode": c._write_authority_mode,
            "route_decision": route_decision,
            "capability_matrix": {
                "target_count": len(targets),
                "control_capable_count": control_capable_count,
                "control_path_counts": control_path_counts,
                "hardware_family_counts": hardware_family_counts,
                "capabilities": sorted(capabilities_union),
                "sample_targets": sorted(
                    [str(t.get("target", "")) for t in targets if isinstance(t, dict) and t.get("target")]
                )[:5],
            },
            "profile_schema": profile_schema,
        }

    def build_action_catalog_validation(
        self,
        *,
        registry: dict[str, Any],
        contract_validation: dict[str, Any],
        capability_profile_validation: dict[str, Any],
    ) -> dict[str, Any]:
        """Build F4-S02 action-catalog validation packet from capability/profile diagnostics."""
        c = self._coordinator
        entries = registry.get("entries", {}) if isinstance(registry.get("entries", {}), dict) else {}
        targets = list(entries.values()) if isinstance(entries, dict) else []

        capabilities_union: set[str] = set()
        for entry in targets:
            if not isinstance(entry, dict):
                continue
            caps = entry.get("capabilities", [])
            if isinstance(caps, list):
                for cap in caps:
                    if isinstance(cap, str) and cap.strip():
                        capabilities_union.add(cap.strip())

        action_schema = {
            "schema_version": "f4_s02.v1",
            "required_keys": [
                "action_id",
                "label",
                "domain",
                "service",
                "target_scope",
                "safety",
            ],
            "safety_required_keys": [
                "confirm_required",
                "cooldown_s",
                "sensitive",
                "audit_event",
            ],
            "defaults": {
                "target_scope": "active_target",
                "dry_run_only": True,
                "safety": {
                    "confirm_required": True,
                    "cooldown_s": 3,
                    "sensitive": True,
                },
            },
        }

        action_catalog = [
            {
                "action_id": "transport_play_pause",
                "label": "Play/Pause",
                "domain": "media_player",
                "service": "media_play_pause",
                "target_scope": "active_target",
                "requires_capabilities": [],
                "dry_run_only": True,
                "safety": {
                    "confirm_required": False,
                    "cooldown_s": 0,
                    "sensitive": False,
                    "audit_event": "transport_play_pause",
                },
            },
            {
                "action_id": "safe_scene_trigger",
                "label": "Run Safe Scene",
                "domain": "scene",
                "service": "turn_on",
                "target_scope": "profile_scope",
                "requires_capabilities": [],
                "dry_run_only": True,
                "safety": {
                    "confirm_required": True,
                    "cooldown_s": 5,
                    "sensitive": True,
                    "audit_event": "safe_scene_trigger",
                },
            },
        ]

        contract_valid = bool(contract_validation.get("valid", False))
        capability_profile_ready = bool(capability_profile_validation.get("ready_for_f4_s01", False))
        no_authority_expansion = c._write_authority_mode in WRITE_AUTH_ALLOWED

        schema_required = action_schema.get("required_keys", [])
        schema_safety_required = action_schema.get("safety_required_keys", [])

        dry_run_only = all(bool(action.get("dry_run_only", False)) for action in action_catalog)

        checks = {
            "registry_present": len(targets) > 0,
            "contract_valid": contract_valid,
            "capability_profile_ready": capability_profile_ready,
            "action_schema_present": isinstance(schema_required, list)
            and len(schema_required) > 0
            and isinstance(schema_safety_required, list)
            and len(schema_safety_required) > 0,
            "action_catalog_present": len(action_catalog) > 0,
            "dry_run_only": dry_run_only,
            "no_authority_expansion": no_authority_expansion,
        }

        verdict = "PASS"
        if (
            not checks["registry_present"]
            or not checks["contract_valid"]
            or not checks["action_schema_present"]
            or not checks["action_catalog_present"]
        ):
            verdict = "FAIL"
        elif (
            not checks["capability_profile_ready"]
            or not checks["dry_run_only"]
            or not checks["no_authority_expansion"]
        ):
            verdict = "WARN"

        confirm_required_count = 0
        sensitive_count = 0
        max_cooldown_s = 0
        for action in action_catalog:
            safety = action.get("safety", {}) if isinstance(action.get("safety", {}), dict) else {}
            if bool(safety.get("confirm_required", False)):
                confirm_required_count += 1
            if bool(safety.get("sensitive", False)):
                sensitive_count += 1
            cooldown = safety.get("cooldown_s", 0)
            if isinstance(cooldown, (int, float)):
                max_cooldown_s = max(max_cooldown_s, int(cooldown))

        return {
            "verdict": verdict,
            "ready_for_f4_s02": verdict == "PASS",
            "checks": checks,
            "authority_mode": c._write_authority_mode,
            "capability_reference": {
                "ready_for_f4_s01": capability_profile_ready,
                "schema_version": (
                    capability_profile_validation.get("profile_schema", {}).get("schema_version", "missing")
                    if isinstance(capability_profile_validation.get("profile_schema", {}), dict)
                    else "missing"
                ),
            },
            "action_schema": action_schema,
            "action_catalog": action_catalog,
            "catalog_summary": {
                "action_count": len(action_catalog),
                "confirm_required_count": confirm_required_count,
                "sensitive_count": sensitive_count,
                "max_cooldown_s": max_cooldown_s,
                "capability_pool": sorted(capabilities_union),
            },
        }

    def build_crossfade_balance_validation(
        self,
        *,
        route_trace: dict[str, Any],
        contract_validation: dict[str, Any],
        action_catalog_validation: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Build F4-S03 crossfade/balance validation packet from route + action diagnostics."""
        c = self._coordinator
        action_validation = action_catalog_validation if isinstance(action_catalog_validation, dict) else {}
        route_decision = str(route_trace.get("decision", "") or "")
        active_target = str(route_trace.get("active_target", "") or "").strip()
        active_target_resolved = active_target.lower() not in {"", "none", "unknown", "unavailable"}
        contract_valid = bool(contract_validation.get("valid", False))
        f4_s02_ready = bool(action_validation.get("ready_for_f4_s02", False))

        slider_domain_schema = {
            "schema_version": "f4_s03.v1",
            "domain": [-100, 100],
            "center": 0,
            "step": 1,
            "required_keys": [
                "mode",
                "value",
                "target_scope",
                "safety",
            ],
            "safety_required_keys": [
                "dry_run_only",
                "cooldown_s",
                "audit_event",
            ],
        }

        mode_profiles = {
            "multi_room": {
                "intent": "room_weight_balance",
                "value_map": "negative=weight_room_a, positive=weight_room_b",
                "supports_write": False,
            },
            "single_room": {
                "intent": "stereo_lr_balance",
                "value_map": "negative=left_bias, positive=right_bias",
                "supports_write": False,
            },
        }

        sample_mix_plan = {
            "dry_run_only": True,
            "samples": {
                "-100": {"multi_room": {"room_a": 1.0, "room_b": 0.0}, "single_room": {"left": 1.0, "right": 0.0}},
                "0": {"multi_room": {"room_a": 0.5, "room_b": 0.5}, "single_room": {"left": 0.5, "right": 0.5}},
                "100": {"multi_room": {"room_a": 0.0, "room_b": 1.0}, "single_room": {"left": 0.0, "right": 1.0}},
            },
            "fallback": "hold_current_mix_and_emit_notice",
        }

        schema_required = slider_domain_schema.get("required_keys", [])
        schema_safety_required = slider_domain_schema.get("safety_required_keys", [])

        checks = {
            "payload_present": True,
            "contract_valid": contract_valid,
            "route_trace_present": route_decision != "",
            "f4_s02_ready": f4_s02_ready,
            "slider_schema_present": isinstance(schema_required, list)
            and len(schema_required) > 0
            and isinstance(schema_safety_required, list)
            and len(schema_safety_required) > 0,
            "mode_profiles_present": isinstance(mode_profiles, dict)
            and "multi_room" in mode_profiles
            and "single_room" in mode_profiles,
            "no_authority_expansion": c._write_authority_mode in WRITE_AUTH_ALLOWED,
            "snapshot_fresh": True,
        }

        verdict = "PASS"
        if not checks["contract_valid"] or not checks["route_trace_present"]:
            verdict = "FAIL"
        elif (
            not checks["f4_s02_ready"]
            or not checks["slider_schema_present"]
            or not checks["mode_profiles_present"]
            or not checks["no_authority_expansion"]
        ):
            verdict = "WARN"

        blocking_reasons: list[str] = []
        if not checks["contract_valid"]:
            blocking_reasons.append("contract_invalid")
        if not checks["route_trace_present"]:
            blocking_reasons.append("route_trace_missing")
        if not checks["f4_s02_ready"]:
            blocking_reasons.append("f4_s02_not_ready")
        if not active_target_resolved:
            blocking_reasons.append("active_target_unresolved")
        if route_decision == "defer_no_target":
            blocking_reasons.append("route_deferred_no_target")
        if not checks["slider_schema_present"]:
            blocking_reasons.append("slider_schema_missing")
        if not checks["mode_profiles_present"]:
            blocking_reasons.append("mode_profiles_missing")
        if not checks["no_authority_expansion"]:
            blocking_reasons.append("authority_expansion_detected")

        return {
            "verdict": verdict,
            "ready_for_f4_s03": verdict == "PASS",
            "checks": checks,
            "authority_mode": c._write_authority_mode,
            "route_decision": route_decision,
            "dependency_reference": {
                "ready_for_f4_s02": f4_s02_ready,
                "active_target": active_target,
                "active_target_resolved": active_target_resolved,
                "route_decision": route_decision,
                "blocking_reasons": blocking_reasons,
                "schema_version": (
                    action_validation.get("action_schema", {}).get("schema_version", "missing")
                    if isinstance(action_validation.get("action_schema", {}), dict)
                    else "missing"
                ),
            },
            "slider_domain_schema": slider_domain_schema,
            "mode_profiles": mode_profiles,
            "sample_mix_plan": sample_mix_plan,
        }

    def build_snapshot_validation_packet(
        self,
        *,
        parity: dict[str, Any],
        registry: dict[str, Any],
        route_trace: dict[str, Any],
    ) -> dict[str, Any]:
        """Build packetized snapshot-validation surfaces for coordinator snapshot assembly."""
        contract_validation = self.build_contract_validation()
        selection_handoff_validation = self.build_selection_handoff_validation(
            parity=parity,
            route_trace=route_trace,
            contract_validation=contract_validation,
        )
        route_safety_validation = self.build_route_safety_validation(
            parity=parity,
            route_trace=route_trace,
        )
        host_control_cutover_gate = self.build_host_control_cutover_gate(
            parity=parity,
            registry=registry,
            route_trace=route_trace,
        )

        metadata_bundle = self.build_metadata_validation_bundle(
            route_trace=route_trace,
            contract_validation=contract_validation,
        )
        normalized_metadata_bundle = self.normalize_metadata_validation_bundle(metadata_bundle)
        metadata_prep_validation = normalized_metadata_bundle.get("metadata_prep_validation", {})
        metadata_bridge_validation = normalized_metadata_bundle.get("metadata_bridge_validation", {})
        cutover_prep_validation = normalized_metadata_bundle.get("cutover_prep_validation", {})

        capability_profile_validation = self.build_capability_profile_validation(
            registry=registry,
            route_trace=route_trace,
            contract_validation=contract_validation,
            metadata_prep_validation=metadata_prep_validation,
        )
        action_catalog_validation = self.build_action_catalog_validation(
            registry=registry,
            contract_validation=contract_validation,
            capability_profile_validation=capability_profile_validation,
        ) or {}
        crossfade_balance_validation = self.build_crossfade_balance_validation(
            route_trace=route_trace,
            contract_validation=contract_validation,
            action_catalog_validation=action_catalog_validation,
        )
        scheduler_validation = self.build_scheduler_validation(
            registry=registry,
            route_trace=route_trace,
            contract_validation=contract_validation,
        )
        control_center_validation = self.build_control_center_validation()

        return {
            "host_control_cutover_gate": host_control_cutover_gate,
            "contract_validation": contract_validation,
            "selection_handoff_validation": selection_handoff_validation,
            "route_safety_validation": route_safety_validation,
            "metadata_prep_validation": metadata_prep_validation,
            "metadata_bridge_validation": metadata_bridge_validation,
            "cutover_prep_validation": cutover_prep_validation,
            "capability_profile_validation": capability_profile_validation,
            "action_catalog_validation": action_catalog_validation,
            "crossfade_balance_validation": crossfade_balance_validation,
            "scheduler_validation": scheduler_validation,
            "control_center_validation": control_center_validation,
        }
