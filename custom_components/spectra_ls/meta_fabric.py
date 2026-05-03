# Description: Meta fabric startup-orchestration workflow for Spectra LS metadata recovery and MA boot-gate readiness semantics.
# Version: 2026.05.03.12
# Last updated: 2026-05-03
# PARITY DIRECTIVE (until full cutover): behavior/contract edits here require same-slice two-track parity review
# and version-metadata review in runtime (`packages/` + `esphome/`) and component (`custom_components/spectra_ls/`) tracks.

from __future__ import annotations

from datetime import UTC, datetime
import logging
from time import monotonic
from typing import Any
from uuid import uuid4

from homeassistant.helpers.event import async_call_later

from .const import (
    LEGACY_ACTIVE_TARGET_HELPER,
    LEGACY_CONTROL_AMBIGUOUS,
    LEGACY_CONTROL_HOST,
    LEGACY_CONTROL_TARGETS,
    LEGACY_META_DETECTED_ENTITY,
    LEGACY_META_OVERRIDE_ACTIVE,
    LEGACY_META_OVERRIDE_ENTITY,
    LEGACY_META_RESOLVER,
    LEGACY_META_CONFIDENCE_MIN,
    LEGACY_META_PAUSED_HIDE_S,
    LEGACY_META_STALE_S,
    LEGACY_MA_PLAYERS,
    LEGACY_LAST_VALID_TARGET,
    LEGACY_NO_CONTROL_CAPABLE_HOSTS,
    LEGACY_OVERRIDE_ACTIVE,
    LEGACY_ROOMS_JSON,
    LEGACY_ROOMS_RAW,
    LEGACY_SERVER_PROFILE,
    LEGACY_SERVER_PROFILE_EFFECTIVE,
    LEGACY_SURFACES,
    META_POLICY_DEFAULTS,
    WRITE_AUTH_ALLOWED,
    WRITE_AUTH_COMPONENT,
    WRITE_AUTH_LEGACY,
)
from .registry import build_registry_snapshot
from .router import build_route_trace
from .selection_fabric import SelectionFabricWorkflow
from .validation_fabric import ValidationFabricWorkflow

_LOGGER = logging.getLogger(__name__)


class MetaFabricWorkflow:
    """Owns metadata startup recovery orchestration extracted from coordinator."""

    def __init__(self, coordinator: Any) -> None:
        self._coordinator = coordinator
        self._selection_fabric = SelectionFabricWorkflow(coordinator)
        self._validation_fabric = ValidationFabricWorkflow(coordinator, self._selection_fabric)

    async def async_schedule_startup_recovery(self) -> None:
        """Schedule bounded post-startup recovery for target/options and bridge alignment."""
        c = self._coordinator
        c._startup_recovery_attempt = 0
        c._startup_recovery_wait_cycles = 0
        if c._startup_recovery_unsub is not None:
            c._startup_recovery_unsub()
            c._startup_recovery_unsub = None
        c._startup_recovery_unsub = async_call_later(
            c.hass,
            c._startup_recovery_initial_delay_s,
            c._handle_startup_recovery_timer,
        )

    def handle_startup_recovery_timer(self, _now) -> None:
        """Kick off one startup recovery attempt from timer callback."""
        c = self._coordinator
        c._startup_recovery_unsub = None
        if c._startup_recovery_task is not None and not c._startup_recovery_task.done():
            return
        c._startup_recovery_task = c.hass.async_create_task(c._async_run_startup_recovery_attempt())

    async def async_run_startup_recovery_attempt(self) -> None:
        """Run one bounded startup recovery attempt and schedule retry if needed."""
        c = self._coordinator
        boot_ready, boot_reasons = self.is_startup_recovery_boot_ready()
        if not boot_ready:
            c._startup_recovery_wait_cycles += 1
            wait_reason = self.startup_wait_reason_prefix(boot_reasons)
            reason_suffix = self.format_startup_boot_wait_reasons(boot_reasons)

            c.metadata_stack.set_last_metadata_bridge_attempt({
                "status": "waiting_for_ma_boot",
                "requested_at": datetime.now(UTC).isoformat(),
                "completed_at": datetime.now(UTC).isoformat(),
                "reason": f"{wait_reason}: {reason_suffix}",
                "resolver_status": "never_attempted",
                "trial_status": "never_attempted",
            })
            c.async_set_updated_data(c.build_snapshot())

            if c._startup_recovery_wait_cycles <= c._startup_recovery_max_wait_cycles:
                _LOGGER.info(
                    "Startup auto-recovery is waiting for Music Assistant boot readiness (%s/%s): %s",
                    c._startup_recovery_wait_cycles,
                    c._startup_recovery_max_wait_cycles,
                    reason_suffix,
                )
                c._startup_recovery_unsub = async_call_later(
                    c.hass,
                    c._startup_recovery_retry_delay_s,
                    c._handle_startup_recovery_timer,
                )
                return

            _LOGGER.warning(
                "Startup auto-recovery readiness wait window exhausted after %s cycles; continuing with guarded recovery",
                c._startup_recovery_max_wait_cycles,
            )

        c._startup_recovery_wait_cycles = 0
        c._startup_recovery_attempt += 1
        attempt = c._startup_recovery_attempt

        try:
            await c.async_restore_last_valid_target(
                dry_run=c._write_authority_mode != WRITE_AUTH_COMPONENT,
                force=True,
                correlation_id=f"startup-restore-{attempt}-{uuid4().hex[:8]}",
            )

            if c._write_authority_mode == WRITE_AUTH_COMPONENT:
                options_result = await c.async_build_target_options_scaffold(
                    dry_run=False,
                    force=True,
                    include_none=True,
                    correlation_id=f"startup-component-options-{attempt}-{uuid4().hex[:8]}",
                )
                auto_result = await c.async_run_auto_select_scaffold(
                    dry_run=False,
                    force=True,
                    sync_options_if_missing=True,
                    include_none=True,
                    correlation_id=f"startup-component-auto-select-{attempt}-{uuid4().hex[:8]}",
                )

                now_iso = datetime.now(UTC).isoformat()
                c.metadata_stack.set_last_metadata_bridge_attempt({
                    "status": "skipped_component_startup_no_mix",
                    "requested_at": now_iso,
                    "completed_at": now_iso,
                    "reason": (
                        "Startup bridge trial skipped in component authority; "
                        "component-only recovery executed to avoid boot authority mixing"
                    ),
                    "resolver_status": "never_attempted",
                    "trial_status": "never_attempted",
                    "stages": {
                        "component_target_options": {
                            "status": options_result.get("status", "unknown"),
                            "reason": options_result.get("reason", ""),
                        },
                        "component_auto_select": {
                            "status": auto_result.get("status", "unknown"),
                            "reason": auto_result.get("reason", ""),
                            "selected_target": auto_result.get("selected_target", ""),
                        },
                    },
                })
                c.async_set_updated_data(c.build_snapshot())
                _LOGGER.info(
                    "Startup auto-recovery completed with component-only no-mix flow (%s/%s)",
                    attempt,
                    c._startup_recovery_max_attempts,
                )
                return

            if c._write_authority_mode == WRITE_AUTH_LEGACY:
                now_iso = datetime.now(UTC).isoformat()
                c.metadata_stack.set_last_metadata_bridge_attempt({
                    "status": "skipped_legacy_authority",
                    "requested_at": now_iso,
                    "completed_at": now_iso,
                    "reason": (
                        "Startup bridge recovery skipped because authority mode is legacy; "
                        "runtime helper flow remains single-writer during boot"
                    ),
                    "resolver_status": "never_attempted",
                    "trial_status": "never_attempted",
                })
                c.async_set_updated_data(c.build_snapshot())
                _LOGGER.info(
                    "Startup auto-recovery skipped component bridge on legacy authority (%s/%s)",
                    attempt,
                    c._startup_recovery_max_attempts,
                )
                return

            result = await c.metadata_stack.async_run_metadata_trial_bridge_scaffold(
                window_id=f"startup-recovery-{attempt}",
                reason="HA restart startup auto-recovery",
                resolver_dry_run=True,
                trial_dry_run=True,
                force=False,
                expected_target=None,
                expected_route=None,
                expected_meta_entity=None,
                correlation_id=f"startup-recovery-{uuid4().hex[:12]}",
            )
            status = str(result.get("status", "unknown") or "unknown")
            if status == "bridge_completed":
                _LOGGER.info(
                    "Startup auto-recovery succeeded on attempt %s/%s",
                    attempt,
                    c._startup_recovery_max_attempts,
                )
                return

            if attempt < c._startup_recovery_max_attempts:
                _LOGGER.warning(
                    "Startup auto-recovery attempt %s/%s incomplete: status=%s reason=%s; retrying in %.1fs",
                    attempt,
                    c._startup_recovery_max_attempts,
                    status,
                    str(result.get("reason", "") or ""),
                    c._startup_recovery_retry_delay_s,
                )
                c._startup_recovery_unsub = async_call_later(
                    c.hass,
                    c._startup_recovery_retry_delay_s,
                    c._handle_startup_recovery_timer,
                )
            else:
                _LOGGER.warning(
                    "Startup auto-recovery exhausted after %s attempts (last_status=%s, last_reason=%s)",
                    c._startup_recovery_max_attempts,
                    status,
                    str(result.get("reason", "") or ""),
                )
        except Exception as err:  # pragma: no cover - defensive runtime guard
            if attempt < c._startup_recovery_max_attempts:
                _LOGGER.warning(
                    "Startup auto-recovery attempt %s/%s failed (%s); retrying in %.1fs",
                    attempt,
                    c._startup_recovery_max_attempts,
                    err,
                    c._startup_recovery_retry_delay_s,
                )
                c._startup_recovery_unsub = async_call_later(
                    c.hass,
                    c._startup_recovery_retry_delay_s,
                    c._handle_startup_recovery_timer,
                )
            else:
                _LOGGER.warning(
                    "Startup auto-recovery exhausted after %s attempts due to repeated failures",
                    c._startup_recovery_max_attempts,
                )

    def is_startup_recovery_boot_ready(self) -> tuple[bool, list[str]]:
        """Return whether MA/runtime surfaces are ready for startup recovery attempts."""
        c = self._coordinator
        reasons: list[str] = []

        ma_players_state = c.hass.states.get(LEGACY_MA_PLAYERS)
        ma_players_ready = ma_players_state is not None and c._is_resolved_state(ma_players_state.state)
        if not ma_players_ready:
            reasons.append("ma_players_not_ready")

        control_targets_state = c.hass.states.get(LEGACY_CONTROL_TARGETS)
        control_targets_ready = control_targets_state is not None and c._is_resolved_state(control_targets_state.state)
        if not control_targets_ready:
            reasons.append("control_targets_not_ready")

        helper_state = c.hass.states.get(LEGACY_ACTIVE_TARGET_HELPER)
        helper_exists = helper_state is not None
        if not helper_exists:
            reasons.append("active_target_helper_missing")

        helper_options_ready = False
        if helper_state is not None:
            options_attr = helper_state.attributes.get("options", [])
            if isinstance(options_attr, list):
                normalized_options = [
                    str(item).strip()
                    for item in options_attr
                    if isinstance(item, str) and str(item).strip()
                ]
                non_none_options = [item for item in normalized_options if c._normalize_state(item) != "none"]
                helper_options_ready = len(non_none_options) > 0
        if not helper_options_ready:
            reasons.append("active_target_options_not_ready")

        boot_ready = ma_players_ready and control_targets_ready and helper_exists and helper_options_ready
        return boot_ready, reasons

    @staticmethod
    def startup_wait_reason_prefix(reasons: list[str]) -> str:
        """Return human-readable startup wait prefix aligned to the blocking phase."""
        ma_boot_blockers = {"ma_players_not_ready", "control_targets_not_ready"}
        if any(item in ma_boot_blockers for item in reasons):
            return "waiting for Music Assistant boot readiness"
        return "waiting for control contract readiness after Music Assistant boot"

    @staticmethod
    def format_startup_boot_wait_reasons(reasons: list[str]) -> str:
        """Format startup readiness blockers into operator-friendly wait messaging."""
        if not reasons:
            return "Music Assistant startup signals are still initializing"

        reason_map = {
            "ma_players_not_ready": "Music Assistant player list is not ready yet",
            "control_targets_not_ready": "control target catalog is not ready yet",
            "active_target_helper_missing": "active-target helper is not available yet",
            "active_target_options_not_ready": "active-target options are still initializing",
        }
        friendly = [reason_map.get(item, item.replace("_", " ")) for item in reasons]
        return "; ".join(friendly)

    def build_metadata_validation_bundle(
        self,
        *,
        route_trace: dict[str, Any],
        contract_validation: dict[str, Any],
    ) -> dict[str, Any]:
        """Build metadata prep/bridge/cutover validation bundle for snapshot assembly."""
        return self._validation_fabric.build_metadata_validation_bundle(
            route_trace=route_trace,
            contract_validation=contract_validation,
        )

    def normalize_metadata_validation_bundle(
        self,
        metadata_bundle: dict[str, Any],
    ) -> dict[str, dict[str, Any]]:
        """Normalize metadata validation bundle payload shapes for snapshot assembly."""
        return self._validation_fabric.normalize_metadata_validation_bundle(metadata_bundle)

    def build_write_controls_metadata_surfaces(self) -> dict[str, Any]:
        """Build metadata-related write-control surfaces for coordinator snapshot payload."""
        return self._validation_fabric.build_write_controls_metadata_surfaces()

    def build_meta_policy_surface(self) -> dict[str, Any]:
        """Build metadata policy surface from helpers/defaults for write-controls payload."""
        return self._validation_fabric.build_meta_policy_surface()

    def evaluate_handoff_scaffold_statuses(
        self,
        *,
        component_scaffolds: dict[str, Any],
        target_options_attempt: dict[str, Any],
        auto_select_attempt: dict[str, Any],
        metadata_attempt: dict[str, Any],
        metadata_bridge_attempt: dict[str, Any],
    ) -> dict[str, str]:
        """Evaluate handoff scaffold status ladder for target-options, auto-select, and metadata lanes."""
        return self._validation_fabric.evaluate_handoff_scaffold_statuses(
            component_scaffolds=component_scaffolds,
            target_options_attempt=target_options_attempt,
            auto_select_attempt=auto_select_attempt,
            metadata_attempt=metadata_attempt,
            metadata_bridge_attempt=metadata_bridge_attempt,
        )

    def build_handoff_dependency_map(
        self,
        *,
        target_options_status: str,
        auto_select_status: str,
        metadata_status: str,
    ) -> list[dict[str, Any]]:
        """Build handoff dependency map rows from scaffold-status surfaces."""
        return self._validation_fabric.build_handoff_dependency_map(
            target_options_status=target_options_status,
            auto_select_status=auto_select_status,
            metadata_status=metadata_status,
        )

    def build_scheduler_validation(
        self,
        *,
        registry: dict[str, Any],
        route_trace: dict[str, Any],
        contract_validation: dict[str, Any],
    ) -> dict[str, Any]:
        """Build scheduler readiness and default-decision validation payload."""
        return self._validation_fabric.build_scheduler_validation(
            registry=registry,
            route_trace=route_trace,
            contract_validation=contract_validation,
        )

    def build_contract_validation(self) -> dict[str, Any]:
        """Build required/soft contract validation payload for routing surfaces."""
        return self._validation_fabric.build_contract_validation()

    def build_selection_handoff_validation(
        self,
        *,
        parity: dict[str, Any],
        route_trace: dict[str, Any],
        contract_validation: dict[str, Any],
    ) -> dict[str, Any]:
        """Build selection-handoff compatibility/guard validation payload."""
        return self._validation_fabric.build_selection_handoff_validation(
            parity=parity,
            route_trace=route_trace,
            contract_validation=contract_validation,
        )

    def build_route_safety_validation(
        self,
        *,
        parity: dict[str, Any],
        route_trace: dict[str, Any],
    ) -> dict[str, Any]:
        """Build explicit route-safety diagnostics for active-target binding and host posture."""
        return self._validation_fabric.build_route_safety_validation(
            parity=parity,
            route_trace=route_trace,
        )

    def build_host_control_cutover_gate(
        self,
        *,
        parity: dict[str, Any],
        registry: dict[str, Any],
        route_trace: dict[str, Any],
    ) -> dict[str, Any]:
        """Compute deterministic host-control cutover readiness for component authority windows."""
        return self._validation_fabric.build_host_control_cutover_gate(
            parity=parity,
            registry=registry,
            route_trace=route_trace,
        )

    def build_control_center_validation(self) -> dict[str, Any]:
        """Build control-center settings and execution-readiness diagnostics payload."""
        return self._validation_fabric.build_control_center_validation()

    def build_capability_profile_validation(
        self,
        *,
        registry: dict[str, Any],
        route_trace: dict[str, Any],
        contract_validation: dict[str, Any],
        metadata_prep_validation: dict[str, Any],
    ) -> dict[str, Any]:
        """Build F4-S01 capability/profile validation packet from registry + route surfaces."""
        return self._validation_fabric.build_capability_profile_validation(
            registry=registry,
            route_trace=route_trace,
            contract_validation=contract_validation,
            metadata_prep_validation=metadata_prep_validation,
        )

    def build_action_catalog_validation(
        self,
        *,
        registry: dict[str, Any],
        contract_validation: dict[str, Any],
        capability_profile_validation: dict[str, Any],
    ) -> dict[str, Any]:
        """Build F4-S02 action-catalog validation packet from capability/profile diagnostics."""
        return self._validation_fabric.build_action_catalog_validation(
            registry=registry,
            contract_validation=contract_validation,
            capability_profile_validation=capability_profile_validation,
        )

    def build_crossfade_balance_validation(
        self,
        *,
        route_trace: dict[str, Any],
        contract_validation: dict[str, Any],
        action_catalog_validation: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Build F4-S03 crossfade/balance validation packet from route + action diagnostics."""
        return self._validation_fabric.build_crossfade_balance_validation(
            route_trace=route_trace,
            contract_validation=contract_validation,
            action_catalog_validation=action_catalog_validation,
        )

    def build_snapshot_validation_packet(
        self,
        *,
        parity: dict[str, Any],
        registry: dict[str, Any],
        route_trace: dict[str, Any],
    ) -> dict[str, Any]:
        """Build packetized snapshot-validation surfaces for coordinator snapshot assembly."""
        return self._validation_fabric.build_snapshot_validation_packet(
            parity=parity,
            registry=registry,
            route_trace=route_trace,
        )

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

        target_options_plan = self.compute_component_target_options_plan()
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

    def compute_component_target_options_plan(self) -> dict[str, Any]:
        """Compute deterministic component target-options plan from helpers/registry/runtime surfaces."""
        return self._selection_fabric.compute_component_target_options_plan()

    def compute_scheduler_decision(
        self,
        *,
        registry: dict[str, Any],
        route_trace: dict[str, Any],
        policy: dict[str, Any],
    ) -> dict[str, Any]:
        """Compute deterministic scheduler ranking and selected candidate payload."""
        return self._selection_fabric.compute_scheduler_decision(
            registry=registry,
            route_trace=route_trace,
            policy=policy,
        )

    def build_handoff_inventory(self) -> dict[str, Any]:
        """Build legacy dependency and scaffold-status handoff inventory packet."""
        c = self._coordinator
        component_scaffolds = self.build_component_scaffolds()
        target_options_attempt = c._last_target_options_attempt if isinstance(c._last_target_options_attempt, dict) else {}
        auto_select_attempt = c._last_auto_select_attempt if isinstance(c._last_auto_select_attempt, dict) else {}
        metadata_attempt = c.metadata_stack.last_metadata_resolver_attempt
        metadata_bridge_attempt = c.metadata_stack.last_metadata_bridge_attempt
        status_surfaces = self.evaluate_handoff_scaffold_statuses(
            component_scaffolds=component_scaffolds,
            target_options_attempt=target_options_attempt,
            auto_select_attempt=auto_select_attempt,
            metadata_attempt=metadata_attempt,
            metadata_bridge_attempt=metadata_bridge_attempt,
        )
        target_options_status = str(status_surfaces.get("target_options_status", "planned") or "planned")
        auto_select_status = str(status_surfaces.get("auto_select_status", "planned") or "planned")
        metadata_status = str(status_surfaces.get("metadata_status", "planned") or "planned")

        legacy_dependency_map = self.build_handoff_dependency_map(
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

    async def async_run_scheduler_choice(
        self,
        *,
        require_control_capable: bool,
        prefer_fresh: bool,
        max_results: int,
        target_hint: str,
        correlation_id: str | None,
    ) -> dict[str, Any]:
        """Run scheduler ranking against current registry/profile snapshot and store decision payload."""
        return await self._selection_fabric.async_run_scheduler_choice(
            require_control_capable=require_control_capable,
            prefer_fresh=prefer_fresh,
            max_results=max_results,
            target_hint=target_hint,
            correlation_id=correlation_id,
        )

    async def async_apply_scheduler_choice(
        self,
        *,
        require_control_capable: bool,
        prefer_fresh: bool,
        max_results: int,
        target_hint: str,
        dry_run: bool,
        force: bool,
        correlation_id: str | None,
    ) -> dict[str, Any]:
        """Run scheduler decision and guardedly apply selected target to helper entity."""
        return await self._selection_fabric.async_apply_scheduler_choice(
            require_control_capable=require_control_capable,
            prefer_fresh=prefer_fresh,
            max_results=max_results,
            target_hint=target_hint,
            dry_run=dry_run,
            force=force,
            correlation_id=correlation_id,
        )

    async def async_build_target_options_scaffold(
        self,
        *,
        dry_run: bool,
        force: bool,
        include_none: bool,
        correlation_id: str | None,
    ) -> dict[str, Any]:
        """Build (and optionally apply) component-native target-options scaffold plan."""
        return await self._selection_fabric.async_build_target_options_scaffold(
            dry_run=dry_run,
            force=force,
            include_none=include_none,
            correlation_id=correlation_id,
        )

    async def async_run_auto_select_scaffold(
        self,
        *,
        dry_run: bool,
        force: bool,
        sync_options_if_missing: bool,
        include_none: bool,
        correlation_id: str | None,
    ) -> dict[str, Any]:
        """Run component-native auto-select scaffold with guarded helper apply semantics."""
        return await self._selection_fabric.async_run_auto_select_scaffold(
            dry_run=dry_run,
            force=force,
            sync_options_if_missing=sync_options_if_missing,
            include_none=include_none,
            correlation_id=correlation_id,
        )

    async def async_track_last_valid_target(
        self,
        *,
        dry_run: bool,
        force: bool,
        correlation_id: str | None,
        source: str = "service_track_last_valid_target",
    ) -> dict[str, Any]:
        """Track helper-selected target into last-valid helper with guarded writes."""
        return await self._selection_fabric.async_track_last_valid_target(
            dry_run=dry_run,
            force=force,
            correlation_id=correlation_id,
            source=source,
        )

    async def async_restore_last_valid_target(
        self,
        *,
        dry_run: bool,
        force: bool,
        correlation_id: str | None,
    ) -> dict[str, Any]:
        """Restore helper selection from last-valid helper when current selection is unresolved."""
        return await self._selection_fabric.async_restore_last_valid_target(
            dry_run=dry_run,
            force=force,
            correlation_id=correlation_id,
        )

    async def async_cycle_active_target(
        self,
        *,
        dry_run: bool,
        force: bool,
        include_none: bool,
        correlation_id: str | None,
    ) -> dict[str, Any]:
        """Cycle active-target helper options with optional none filtering and override activation."""
        return await self._selection_fabric.async_cycle_active_target(
            dry_run=dry_run,
            force=force,
            include_none=include_none,
            correlation_id=correlation_id,
        )

    def auto_select_loop_preflight(self) -> tuple[bool, str]:
        """Return whether component auto-select loop can run in current authority/runtime state."""
        c = self._coordinator
        if c._write_authority_mode != WRITE_AUTH_COMPONENT:
            return False, "authority_not_component"

        players_state = c.hass.states.get(LEGACY_MA_PLAYERS)
        players_count = 0
        if players_state is not None and c._is_resolved_state(players_state.state):
            try:
                players_count = int(float(str(players_state.state).strip()))
            except (TypeError, ValueError):
                players_count = 0
        if players_count <= 0:
            return False, "players_not_ready"

        override_state = c.hass.states.get(LEGACY_OVERRIDE_ACTIVE)
        override_on = c._normalize_state(override_state.state if override_state is not None else "") == "on"
        if override_on:
            return False, "override_active"

        return True, "ready"

    async def async_run_component_auto_select_loop(self, *, source: str, force: bool = False) -> None:
        """Run component-side auto-select loop parity behavior under guarded semantics."""
        c = self._coordinator
        ok, _reason = self.auto_select_loop_preflight()
        if not ok:
            return

        await c.async_run_auto_select_scaffold(
            dry_run=False,
            force=force,
            sync_options_if_missing=True,
            include_none=True,
            correlation_id=f"component-auto-loop-{source}-{uuid4().hex[:8]}",
        )

    async def async_run_component_players_change_refresh(self, *, source: str) -> None:
        """Mirror legacy players-change sequencing: refresh options, then auto-select."""
        c = self._coordinator
        if c._write_authority_mode != WRITE_AUTH_COMPONENT:
            return

        corr_suffix = uuid4().hex[:8]
        await c.async_build_target_options_scaffold(
            dry_run=False,
            force=False,
            include_none=True,
            correlation_id=f"players-change-options-{source}-{corr_suffix}",
        )
        await self.async_run_component_auto_select_loop(
            source=f"{source}-auto-select",
            force=False,
        )

    async def async_apply_ambiguity_lock(self, *, source: str) -> None:
        """Mirror legacy lock-on-ambiguous-select behavior for component authority windows."""
        c = self._coordinator
        if c._write_authority_mode != WRITE_AUTH_COMPONENT:
            return

        ambiguous_state = c.hass.states.get(LEGACY_CONTROL_AMBIGUOUS)
        ambiguous_on = c._normalize_state(ambiguous_state.state if ambiguous_state is not None else "") == "on"
        if not ambiguous_on:
            return

        helper_state = c.hass.states.get(LEGACY_ACTIVE_TARGET_HELPER)
        current_target = str(helper_state.state if helper_state is not None else "").strip()
        if not c._is_resolved_state(current_target):
            return
        if c.hass.states.get(current_target) is None:
            return

        override_state = c.hass.states.get(LEGACY_OVERRIDE_ACTIVE)
        if override_state is None:
            return
        if c._normalize_state(override_state.state) == "on":
            return

        await c.hass.services.async_call(
            "input_boolean",
            "turn_on",
            {"entity_id": LEGACY_OVERRIDE_ACTIVE},
            blocking=True,
        )
        c._last_write_attempt = {
            "status": "write_applied",
            "timestamp": datetime.now(UTC).isoformat(),
            "authority_mode": c._write_authority_mode,
            "reason": "Applied ambiguity lock parity behavior",
            "correlation_id": f"ambiguity-lock-{uuid4().hex[:12]}",
            "source": source,
            "active_target": current_target,
        }
        c.async_set_updated_data(c._build_snapshot())

    async def async_apply_stale_unlock(self, *, source: str) -> None:
        """Mirror legacy stale-meta unlock behavior with bounded auto-select follow-up."""
        c = self._coordinator
        if c._write_authority_mode != WRITE_AUTH_COMPONENT:
            return

        meta_stale_state = c.hass.states.get(LEGACY_META_STALE)
        if c._normalize_state(meta_stale_state.state if meta_stale_state is not None else "") != "on":
            return

        override_state = c.hass.states.get(LEGACY_OVERRIDE_ACTIVE)
        if c._normalize_state(override_state.state if override_state is not None else "") != "on":
            return

        await c.hass.services.async_call(
            "input_boolean",
            "turn_off",
            {"entity_id": LEGACY_OVERRIDE_ACTIVE},
            blocking=True,
        )
        await self.async_run_component_auto_select_loop(source=f"{source}-auto-select", force=True)

    def handle_meta_stale_unlock_timer(self, _now) -> None:
        """Handle delayed stale unlock hold callback."""
        c = self._coordinator
        c._meta_stale_unlock_unsub = None
        c.hass.async_create_task(self.async_apply_stale_unlock(source="meta_stale_hold"))

    async def async_dismiss_no_control_feedback_notification(self) -> None:
        """Dismiss no-control feedback notification if present."""
        c = self._coordinator
        try:
            await c.hass.services.async_call(
                "persistent_notification",
                "dismiss",
                {"notification_id": c._no_control_feedback_notification_id},
                blocking=True,
            )
        except Exception:  # pragma: no cover - defensive runtime guard
            _LOGGER.exception("Failed dismissing no-control-capable-hosts feedback notification")

    def handle_no_control_feedback_hold_timer(self, _now) -> None:
        """Start self-heal sequence after no-control feedback hold timer."""
        c = self._coordinator
        c._no_control_feedback_hold_unsub = None
        c.hass.async_create_task(self.async_run_no_control_feedback_self_heal())

    async def async_run_no_control_feedback_self_heal(self) -> None:
        """Run bounded self-heal sequence for no-control-capable-hosts state."""
        c = self._coordinator
        if c._write_authority_mode != WRITE_AUTH_COMPONENT:
            return

        no_host_state = c.hass.states.get(LEGACY_NO_CONTROL_CAPABLE_HOSTS)
        if c._normalize_state(no_host_state.state if no_host_state is not None else "") != "on":
            return

        corr_suffix = uuid4().hex[:8]
        await c.async_build_target_options_scaffold(
            dry_run=False,
            force=True,
            include_none=True,
            correlation_id=f"no-host-feedback-options-{corr_suffix}",
        )
        await c.async_run_auto_select_scaffold(
            dry_run=False,
            force=True,
            sync_options_if_missing=True,
            include_none=True,
            correlation_id=f"no-host-feedback-auto-select-{corr_suffix}",
        )

        if c._no_control_feedback_post_heal_unsub is not None:
            c._no_control_feedback_post_heal_unsub()
        c._no_control_feedback_post_heal_unsub = async_call_later(
            c.hass,
            10.0,
            c._handle_no_control_feedback_post_heal_timer,
        )

    def handle_no_control_feedback_post_heal_timer(self, _now) -> None:
        """Handle post-heal delay timer before creating notification."""
        c = self._coordinator
        c._no_control_feedback_post_heal_unsub = None
        c.hass.async_create_task(self.async_finalize_no_control_feedback_notification())

    async def async_finalize_no_control_feedback_notification(self) -> None:
        """Create final no-control feedback notification when state persists after self-heal."""
        c = self._coordinator
        if c._write_authority_mode != WRITE_AUTH_COMPONENT:
            return

        no_host_state = c.hass.states.get(LEGACY_NO_CONTROL_CAPABLE_HOSTS)
        if c._normalize_state(no_host_state.state if no_host_state is not None else "") != "on":
            return

        active_target_state = c.hass.states.get(LEGACY_ACTIVE_TARGET_HELPER)
        active_target = str(active_target_state.state if active_target_state is not None else "")

        control_path_state = c.hass.states.get(LEGACY_SURFACES["active_control_path"])
        control_path = str(control_path_state.state if control_path_state is not None else "")

        control_capable_state = c.hass.states.get(LEGACY_SURFACES["active_control_capable"])
        control_capable = str(control_capable_state.state if control_capable_state is not None else "")

        control_hosts_state = c.hass.states.get(LEGACY_SURFACES["control_hosts"])
        control_hosts = str(control_hosts_state.state if control_hosts_state is not None else "")
        if not c._is_resolved_state(control_hosts):
            control_hosts = "none"

        reason = str(no_host_state.attributes.get("reason", "unknown") if no_host_state is not None else "unknown")
        if not c._is_resolved_state(reason):
            reason = "unknown"

        message = (
            f"Active target: {active_target or 'unknown'}\\n"
            f"Control path: {control_path or 'unknown'}\\n"
            f"Control capable: {control_capable or 'unknown'}\\n"
            f"Control hosts: {control_hosts}\\n"
            f"Reason: {reason}\\n"
            "Suggested action: auto-refresh already attempted; if this persists, confirm active "
            "target eligibility and rerun MA target/options refresh."
        )

        try:
            await c.hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "notification_id": c._no_control_feedback_notification_id,
                    "title": "Spectra L/S: No control-capable hosts",
                    "message": message,
                },
                blocking=True,
            )
        except Exception:  # pragma: no cover - defensive runtime guard
            _LOGGER.exception("Failed creating no-control-capable-hosts feedback notification")

    def handle_global_state_change(self, event) -> None:
        """Mirror legacy event-based auto-select trigger for watched target entities."""
        c = self._coordinator
        try:
            if c._write_authority_mode != WRITE_AUTH_COMPONENT:
                return
            event_data = event.data if event is not None else {}
            entity_id = str(event_data.get("entity_id", "") or "")
            if entity_id == "":
                return

            helper_state = c.hass.states.get(LEGACY_ACTIVE_TARGET_HELPER)
            if helper_state is None:
                return
            options_attr = helper_state.attributes.get("options", [])
            helper_options = options_attr if isinstance(options_attr, list) else []
            watched_targets = {
                str(item).strip()
                for item in helper_options
                if isinstance(item, str) and str(item).strip()
            }
            if entity_id in watched_targets:
                c.hass.async_create_task(
                    self.async_run_component_auto_select_loop(
                        source=f"global-state:{entity_id}",
                        force=False,
                    )
                )
        except Exception:  # pragma: no cover - defensive callback hardening
            _LOGGER.exception("Failed global state-change handling for component auto-select parity")

    def handle_state_change(self, event) -> None:
        """Handle state-change orchestration lane for event/recovery parity behaviors."""
        c = self._coordinator
        try:
            entity_id = str(event.data.get("entity_id", "") or "") if event is not None else ""

            if entity_id == LEGACY_META_STALE:
                new_state = event.data.get("new_state") if event is not None else None
                new_state_value = c._normalize_state(new_state.state if new_state is not None else "")
                if new_state_value == "on":
                    if c._meta_stale_unlock_unsub is not None:
                        c._meta_stale_unlock_unsub()
                    c._meta_stale_unlock_unsub = async_call_later(
                        c.hass,
                        5.0,
                        c._handle_meta_stale_unlock_timer,
                    )
                elif c._meta_stale_unlock_unsub is not None:
                    c._meta_stale_unlock_unsub()
                    c._meta_stale_unlock_unsub = None

            if entity_id == LEGACY_NO_CONTROL_CAPABLE_HOSTS:
                new_state = event.data.get("new_state") if event is not None else None
                new_state_value = c._normalize_state(new_state.state if new_state is not None else "")

                if new_state_value == "on" and c._write_authority_mode == WRITE_AUTH_COMPONENT:
                    if c._no_control_feedback_hold_unsub is not None:
                        c._no_control_feedback_hold_unsub()
                    if c._no_control_feedback_post_heal_unsub is not None:
                        c._no_control_feedback_post_heal_unsub()
                        c._no_control_feedback_post_heal_unsub = None
                    c._no_control_feedback_hold_unsub = async_call_later(
                        c.hass,
                        30.0,
                        c._handle_no_control_feedback_hold_timer,
                    )
                else:
                    if c._no_control_feedback_hold_unsub is not None:
                        c._no_control_feedback_hold_unsub()
                        c._no_control_feedback_hold_unsub = None
                    if c._no_control_feedback_post_heal_unsub is not None:
                        c._no_control_feedback_post_heal_unsub()
                        c._no_control_feedback_post_heal_unsub = None
                    c.hass.async_create_task(self.async_dismiss_no_control_feedback_notification())

            if entity_id == LEGACY_ACTIVE_TARGET_HELPER and c._write_authority_mode == WRITE_AUTH_COMPONENT:
                c.hass.async_create_task(
                    c.async_track_last_valid_target(
                        dry_run=False,
                        force=False,
                        correlation_id=f"state-change-track-{uuid4().hex[:12]}",
                        source="state_change_listener",
                    )
                )
                c.hass.async_create_task(self.async_apply_ambiguity_lock(source="state_change_ambiguity_lock"))

            if entity_id in {LEGACY_MA_PLAYERS, LEGACY_META_DETECTED_ENTITY, LEGACY_NOW_PLAYING_ENTITY}:
                c.hass.async_create_task(
                    self.async_run_component_players_change_refresh(
                        source=f"state-change:{entity_id}",
                    )
                )
            elif entity_id == LEGACY_ACTIVE_TARGET_HELPER:
                c.hass.async_create_task(
                    self.async_run_component_auto_select_loop(
                        source=f"state-change:{entity_id}",
                        force=False,
                    )
                )

            now_mono = monotonic()
            elapsed = now_mono - c._last_snapshot_refresh_monotonic
            if c._last_snapshot_refresh_monotonic == 0.0 or elapsed >= c._snapshot_refresh_min_interval_s:
                c._refresh_snapshot(force=True)
                if c._deferred_snapshot_refresh_unsub is not None:
                    c._deferred_snapshot_refresh_unsub()
                    c._deferred_snapshot_refresh_unsub = None
                return

            if c._deferred_snapshot_refresh_unsub is None:
                delay_s = max(c._snapshot_refresh_min_interval_s - elapsed, 0.05)
                c._deferred_snapshot_refresh_unsub = async_call_later(
                    c.hass,
                    delay_s,
                    c._handle_deferred_snapshot_refresh,
                )
        except Exception:  # pragma: no cover - defensive callback hardening
            _LOGGER.exception("Failed to refresh Spectra LS snapshot on state-change event")