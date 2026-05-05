# Description: Selection-fabric workflow for Spectra LS scheduler, target-options, and helper write orchestration extracted from meta-fabric.
# Version: 2026.05.04.5
# Last updated: 2026-05-04
# PARITY DIRECTIVE (until full cutover): behavior/contract edits here require same-slice two-track parity review
# and version-metadata review in runtime (`packages/` + `esphome/`) and component (`custom_components/spectra_ls/`) tracks.

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from .const import (
    LEGACY_ACTIVE_TARGET_HELPER,
    LEGACY_LAST_VALID_TARGET,
    LEGACY_MA_PLAYERS,
    LEGACY_META_DETECTED_ENTITY,
    LEGACY_OVERRIDE_ACTIVE,
    LEGACY_ROOMS_JSON,
    WRITE_AUTH_COMPONENT,
    WRITE_AUTH_LEGACY,
)
from .write_path_fabric import WritePathFabric


class SelectionFabricWorkflow:
    """Owns scheduler/selection/write-orchestration methods extracted from meta-fabric."""

    def __init__(self, coordinator: Any) -> None:
        self._coordinator = coordinator

    @staticmethod
    def _append_unique(target_list: list[str], seen: set[str], value: str) -> None:
        if value and value not in seen:
            seen.add(value)
            target_list.append(value)

    def compute_component_target_options_plan(self) -> dict[str, Any]:
        """Compute deterministic component target-options plan from helpers/registry/runtime surfaces."""
        c = self._coordinator
        helper_entity = LEGACY_ACTIVE_TARGET_HELPER
        helper_state = c.hass.states.get(helper_entity)
        helper_options: list[str] = []
        helper_current = ""
        if helper_state is not None:
            helper_current = str(helper_state.state or "").strip()
            helper_options = WritePathFabric.normalize_options(helper_state.attributes.get("options", []))

        last_valid_state = c.hass.states.get(LEGACY_LAST_VALID_TARGET)
        last_valid = str(last_valid_state.state if last_valid_state is not None else "").strip()

        known_targets: list[str] = []
        known_seen: set[str] = set()
        rooms_state = c.hass.states.get(LEGACY_ROOMS_JSON)
        rooms_raw = rooms_state.attributes.get("rooms_json", []) if rooms_state is not None else []
        rooms_list = c.utility_fabric.extract_payload_list(rooms_raw, ("rooms", "result"))
        for room in rooms_list:
            if not isinstance(room, dict):
                continue
            ent = str(room.get("entity", "") or "").strip()
            if not c._is_resolved_state(ent):
                continue
            if not ent.startswith("media_player."):
                continue
            if c.hass.states.get(ent) is None:
                continue
            self._append_unique(known_targets, known_seen, ent)

        discovered_targets: list[str] = []
        discovered_seen: set[str] = set()
        ma_players_state = c.hass.states.get(LEGACY_MA_PLAYERS)
        ma_players_raw = ma_players_state.attributes.get("result", []) if ma_players_state is not None else []
        players_list = c.utility_fabric.extract_payload_list(ma_players_raw, ("result", "players"))
        for player in players_list:
            if not isinstance(player, dict):
                continue
            ent = str(player.get("entity_id", "") or "").strip()
            if not c._is_resolved_state(ent) or not ent.startswith("media_player."):
                continue
            entity_state = c.hass.states.get(ent)
            if entity_state is None:
                continue
            ip = str(entity_state.attributes.get("ip_address", "") or player.get("ip_address", "") or "").strip()
            if not c._is_resolved_state(ip):
                continue
            self._append_unique(discovered_targets, discovered_seen, ent)

        discovered_live_targets: list[str] = []
        discovered_live_seen: set[str] = set()
        for player_state in c.hass.states.async_all("media_player"):
            ent = str(player_state.entity_id or "").strip()
            if not c._is_resolved_state(ent):
                continue
            ip = str(player_state.attributes.get("ip_address", "") or "").strip()
            if not c._is_resolved_state(ip):
                continue
            control_capable_attr = player_state.attributes.get("control_capable")
            control_path = str(player_state.attributes.get("control_path", "") or "").strip().lower()
            model = str(player_state.attributes.get("device_model", "") or "").strip().lower()
            manufacturer = str(player_state.attributes.get("manufacturer", "") or "").strip().lower()
            purpose = str(player_state.attributes.get("integration_purpose", "") or "").strip().lower()
            hint = f"{ent} {model} {manufacturer} {purpose}".lower()
            hint_supported = any(marker in hint for marker in ("wiim", "linkplay", "arylic", "up2stream"))
            control_capable = control_capable_attr in [True, "true", "True", "1", 1, "yes", "on"]
            control_path_ok = control_path == "linkplay_tcp"
            if control_capable or control_path_ok or hint_supported:
                self._append_unique(discovered_live_targets, discovered_live_seen, ent)

        registry_capability_targets: list[str] = []
        registry_seen: set[str] = set()
        registry_payload = c.data.get("registry", {}) if isinstance(c.data, dict) else {}
        registry_entries = registry_payload.get("entries", {}) if isinstance(registry_payload, dict) else {}
        if isinstance(registry_entries, dict):
            for target_id, entry in registry_entries.items():
                if not isinstance(entry, dict):
                    continue
                target = str(target_id or "").strip()
                if not target.startswith("media_player."):
                    continue
                if c.hass.states.get(target) is None:
                    continue

                control_capable = bool(entry.get("control_capable", False))
                host_resolved = c._is_resolved_state(str(entry.get("host", "") or ""))
                control_path = str(entry.get("control_path", "") or "").strip().lower()
                feature_profile = (
                    entry.get("feature_profile", {})
                    if isinstance(entry.get("feature_profile", {}), dict)
                    else {}
                )
                availability_quality = str(feature_profile.get("availability_quality", "") or "").strip().lower()
                fresh_enough = availability_quality in {"fresh", "warm", ""}
                control_path_supported = control_path in {"", "linkplay_tcp"}

                if control_capable and host_resolved and control_path_supported and fresh_enough:
                    self._append_unique(registry_capability_targets, registry_seen, target)

        detected_state = c.hass.states.get("sensor.ma_detected_receiver_entity")
        detected_candidate = str(detected_state.state if detected_state is not None else "").strip()
        if not c._is_resolved_state(detected_candidate):
            detected_candidate = ""
        elif not detected_candidate.startswith("media_player."):
            detected_candidate = ""
        elif c.hass.states.get(detected_candidate) is None:
            detected_candidate = ""

        selectable_candidates: list[str] = []
        selectable_seen: set[str] = set()
        for item in [*known_targets, *discovered_targets, *discovered_live_targets, *registry_capability_targets]:
            self._append_unique(selectable_candidates, selectable_seen, item)
        self._append_unique(selectable_candidates, selectable_seen, detected_candidate)

        current_extra: list[str] = []
        if c._is_resolved_state(helper_current) and helper_current not in selectable_candidates:
            current_extra = [helper_current]

        proposed_options: list[str] = []
        proposed_seen: set[str] = set()
        for item in ["none", *selectable_candidates, *current_extra]:
            self._append_unique(proposed_options, proposed_seen, item)
        if not proposed_options:
            proposed_options = ["none"]

        current_ok = c._is_resolved_state(helper_current) and helper_current in selectable_candidates
        last_ok = c._is_resolved_state(last_valid) and last_valid in selectable_candidates
        default_option = "none"
        if current_ok:
            default_option = helper_current
        elif last_ok:
            default_option = last_valid
        elif selectable_candidates:
            default_option = selectable_candidates[0]

        return {
            "helper_entity": helper_entity,
            "current_helper_options": helper_options,
            "helper_current": helper_current,
            "last_valid_target": last_valid,
            "known_targets": known_targets,
            "discovered_targets": discovered_targets,
            "discovered_live_targets": discovered_live_targets,
            "registry_capability_targets": registry_capability_targets,
            "detected_candidate": detected_candidate,
            "candidates": selectable_candidates,
            "selectable_candidates": selectable_candidates,
            "proposed_options": proposed_options,
            "default_option": default_option,
            "ready": len(selectable_candidates) > 0,
        }

    def compute_scheduler_decision(
        self,
        *,
        registry: dict[str, Any],
        route_trace: dict[str, Any],
        policy: dict[str, Any],
    ) -> dict[str, Any]:
        """Compute deterministic scheduler ranking and selected candidate payload."""
        c = self._coordinator
        entries = registry.get("entries", {}) if isinstance(registry.get("entries", {}), dict) else {}
        active_target = str(route_trace.get("active_target", "") or "").strip()

        require_control_capable = bool(policy.get("require_control_capable", True))
        prefer_fresh = bool(policy.get("prefer_fresh", True))
        max_results = int(policy.get("max_results", 5) or 5)
        max_results = max(1, min(max_results, 20))
        target_hint = str(policy.get("target_hint", "") or "").strip()

        ranked: list[dict[str, Any]] = []
        for target, entry in entries.items():
            if not isinstance(entry, dict):
                continue

            host = str(entry.get("host", "") or "").strip()
            control_capable = bool(entry.get("control_capable", False))
            feature_profile = (
                entry.get("feature_profile", {})
                if isinstance(entry.get("feature_profile", {}), dict)
                else {}
            )
            empirical_profile = (
                entry.get("empirical_profile", {})
                if isinstance(entry.get("empirical_profile", {}), dict)
                else {}
            )

            if require_control_capable and not control_capable:
                continue
            if host == "":
                continue

            availability_quality = str(feature_profile.get("availability_quality", "missing") or "missing")
            availability_points = c._availability_points(availability_quality)
            if prefer_fresh and availability_quality == "missing":
                continue

            observed_caps = feature_profile.get("observed_capabilities", [])
            observed_count = len(observed_caps) if isinstance(observed_caps, list) else 0

            empirical_bonus = c._empirical_bonus(empirical_profile)

            target_match_bonus = 5 if str(target) == active_target else 0
            hint_bonus = 0
            if target_hint:
                target_l = str(target).lower()
                hint_l = target_hint.lower()
                if hint_l in target_l:
                    hint_bonus = 12

            score = (
                (40 if control_capable else 0)
                + (25 if host else 0)
                + availability_points
                + min(observed_count, 10)
                + target_match_bonus
                + hint_bonus
                + empirical_bonus
            )

            ranked.append(
                {
                    "target": str(target),
                    "score": round(float(score), 2),
                    "host": host,
                    "host_type": entry.get("host_type", "generic"),
                    "resolver_module": entry.get("resolver_module", "hostmods.generic"),
                    "control_capable": control_capable,
                    "availability_quality": availability_quality,
                    "observed_capability_count": observed_count,
                    "empirical_bonus": empirical_bonus,
                    "score_breakdown": {
                        "control_capable": 40 if control_capable else 0,
                        "host_resolved": 25 if host else 0,
                        "availability": availability_points,
                        "observed_capabilities": min(observed_count, 10),
                        "active_target_bonus": target_match_bonus,
                        "target_hint_bonus": hint_bonus,
                        "empirical_bonus": empirical_bonus,
                    },
                    "scheduler_profile": entry.get("scheduler_profile", {}),
                }
            )

        ranked.sort(key=lambda item: (-float(item.get("score", 0.0)), str(item.get("target", ""))))
        top = ranked[:max_results]
        selected = top[0] if top else None
        helper_fallback_reason = ""

        if selected is None:
            helper_state = c.hass.states.get(LEGACY_ACTIVE_TARGET_HELPER)
            helper_current = str(helper_state.state if helper_state is not None else "").strip()
            helper_options: list[str] = []
            if helper_state is not None:
                helper_options = WritePathFabric.normalize_options(helper_state.attributes.get("options", []))

            helper_current_resolved = c._is_resolved_state(helper_current)
            helper_current_in_options = helper_current_resolved and helper_current in helper_options
            helper_entry = entries.get(helper_current, {}) if isinstance(entries.get(helper_current, {}), dict) else {}
            helper_entry_control_capable = bool(helper_entry.get("control_capable", False))
            helper_entry_host = str(helper_entry.get("host", "") or "").strip()
            helper_entry_host_resolved = c._is_resolved_state(helper_entry_host)
            helper_fallback_eligible = (
                helper_current_in_options and helper_entry_control_capable and helper_entry_host_resolved
            )

            if helper_fallback_eligible:
                selected = {
                    "target": helper_current,
                    "score": 0.0,
                    "host": helper_entry_host,
                    "host_type": str(helper_entry.get("host_type", "fallback") or "fallback"),
                    "resolver_module": str(
                        helper_entry.get("resolver_module", "helper_current_fallback")
                        or "helper_current_fallback"
                    ),
                    "control_capable": helper_entry_control_capable,
                    "availability_quality": "fallback",
                    "observed_capability_count": 0,
                    "empirical_bonus": 0.0,
                    "score_breakdown": {
                        "control_capable": 40,
                        "host_resolved": 25,
                        "availability": 0,
                        "observed_capabilities": 0,
                        "active_target_bonus": 0,
                        "target_hint_bonus": 0,
                        "empirical_bonus": 0.0,
                        "fallback_bonus": 1,
                    },
                    "scheduler_profile": {
                        "selection_mode": "helper_current_fallback",
                    },
                }
                top = [selected]
            elif helper_current_in_options:
                helper_fallback_reason = (
                    "Helper current target fallback rejected because registry entry is not control-capable "
                    "or host is unresolved"
                )
            elif helper_current_resolved:
                helper_fallback_reason = (
                    "Helper current target fallback rejected because target is not in helper options"
                )

        if c._write_authority_mode == WRITE_AUTH_LEGACY:
            helper_state = c.hass.states.get(LEGACY_ACTIVE_TARGET_HELPER)
            helper_current = str(helper_state.state if helper_state is not None else "").strip()
            helper_options: list[str] = []
            if helper_state is not None:
                helper_options = WritePathFabric.normalize_options(helper_state.attributes.get("options", []))

            helper_current_resolved = c._is_resolved_state(helper_current)
            helper_current_in_options = helper_current_resolved and helper_current in helper_options
            if helper_current_in_options:
                helper_entry = entries.get(helper_current, {}) if isinstance(entries.get(helper_current, {}), dict) else {}
                helper_host = str(helper_entry.get("host", "") or "").strip()
                helper_host_type = str(helper_entry.get("host_type", "legacy_helper") or "legacy_helper")
                helper_resolver_module = str(
                    helper_entry.get("resolver_module", "legacy_helper_authority")
                    or "legacy_helper_authority"
                )
                helper_control_capable = bool(helper_entry.get("control_capable", False))
                helper_host_resolved = c._is_resolved_state(helper_host)
                helper_feature_profile = (
                    helper_entry.get("feature_profile", {})
                    if isinstance(helper_entry.get("feature_profile", {}), dict)
                    else {}
                )
                helper_availability_quality = str(
                    helper_feature_profile.get("availability_quality", "legacy_helper_authority")
                    or "legacy_helper_authority"
                )
                if helper_control_capable and helper_host_resolved:
                    selected = {
                        "target": helper_current,
                        "score": 9999.0,
                        "host": helper_host,
                        "host_type": helper_host_type,
                        "resolver_module": helper_resolver_module,
                        "control_capable": helper_control_capable,
                        "availability_quality": helper_availability_quality,
                        "observed_capability_count": 0,
                        "empirical_bonus": 0.0,
                        "score_breakdown": {
                            "legacy_authority_pin": 9999,
                        },
                        "scheduler_profile": {
                            "selection_mode": "legacy_helper_authority",
                        },
                    }

                    filtered_top = [
                        item for item in top if str(item.get("target", "") or "") != helper_current
                    ]
                    top = [selected, *filtered_top][:max_results]
                else:
                    legacy_fallback = None
                    for item in top:
                        item_host = str(item.get("host", "") or "").strip()
                        item_control_capable = bool(item.get("control_capable", False))
                        if item_control_capable and c._is_resolved_state(item_host):
                            legacy_fallback = item
                            break

                    if legacy_fallback is not None:
                        selected = dict(legacy_fallback)
                        selected["scheduler_profile"] = {
                            "selection_mode": "legacy_helper_authority_fallback",
                        }
                        selected_target = str(selected.get("target", "") or "")
                        filtered_top = [
                            item for item in top if str(item.get("target", "") or "") != selected_target
                        ]
                        top = [selected, *filtered_top][:max_results]
                    else:
                        selected = None
                        top = [
                            item
                            for item in top
                            if bool(item.get("control_capable", False))
                            and c._is_resolved_state(str(item.get("host", "") or ""))
                        ][:max_results]

        status = "selected" if selected is not None else "no_candidate"
        selection_mode = str(
            selected.get("scheduler_profile", {}).get("selection_mode", "")
            if isinstance(selected, dict)
            else ""
        )
        if selected is None:
            reason = helper_fallback_reason or "No candidates satisfied scheduler policy"
        elif selection_mode == "legacy_helper_authority":
            reason = "Legacy authority mode pins scheduler selection to helper current target"
        elif selection_mode == "legacy_helper_authority_fallback":
            reason = (
                "Legacy helper target is not control-capable or host-resolved; using highest-ranked control-host candidate"
            )
        elif selection_mode == "helper_current_fallback":
            reason = "Using helper current target fallback because scheduler ranking produced no candidates"
        else:
            reason = "Highest scored candidate selected"

        if c._write_authority_mode == WRITE_AUTH_LEGACY and selected is None:
            candidate_count = len(
                [
                    item
                    for item in ranked
                    if bool(item.get("control_capable", False))
                    and c._is_resolved_state(str(item.get("host", "") or ""))
                ]
            )
        else:
            candidate_count = len(ranked)
        if selected is not None and candidate_count == 0:
            candidate_count = 1

        return {
            "status": status,
            "reason": reason,
            "policy": {
                "require_control_capable": require_control_capable,
                "prefer_fresh": prefer_fresh,
                "max_results": max_results,
                "target_hint": target_hint,
            },
            "selected_target": str(selected.get("target", "") if isinstance(selected, dict) else ""),
            "selected_host": str(selected.get("host", "") if isinstance(selected, dict) else ""),
            "selected_score": float(selected.get("score", 0.0) if isinstance(selected, dict) else 0.0),
            "candidate_count": candidate_count,
            "ranked_candidates": top,
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
        c = self._coordinator
        requested_at = datetime.now(UTC).isoformat()
        corr = (correlation_id or "").strip() or f"scheduler-{uuid4().hex[:12]}"

        snapshot = c._build_snapshot()
        registry = snapshot.get("registry", {}) if isinstance(snapshot.get("registry", {}), dict) else {}
        route_trace = snapshot.get("route_trace", {}) if isinstance(snapshot.get("route_trace", {}), dict) else {}

        decision = self.compute_scheduler_decision(
            registry=registry,
            route_trace=route_trace,
            policy={
                "require_control_capable": bool(require_control_capable),
                "prefer_fresh": bool(prefer_fresh),
                "max_results": int(max_results),
                "target_hint": str(target_hint or "").strip(),
            },
        )

        result = {
            "requested_at": requested_at,
            "completed_at": datetime.now(UTC).isoformat(),
            "correlation_id": corr,
            **decision,
        }

        c._last_scheduler_decision = result
        c.async_set_updated_data(c._build_snapshot())
        return result

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
        c = self._coordinator
        requested_at = datetime.now(UTC).isoformat()
        corr = (correlation_id or "").strip() or f"scheduler-apply-{uuid4().hex[:12]}"

        snapshot = c._build_snapshot()
        registry = snapshot.get("registry", {}) if isinstance(snapshot.get("registry", {}), dict) else {}
        route_trace = snapshot.get("route_trace", {}) if isinstance(snapshot.get("route_trace", {}), dict) else {}
        host_cutover_gate = (
            snapshot.get("host_control_cutover_gate", {})
            if isinstance(snapshot.get("host_control_cutover_gate", {}), dict)
            else {}
        )

        decision = self.compute_scheduler_decision(
            registry=registry,
            route_trace=route_trace,
            policy={
                "require_control_capable": bool(require_control_capable),
                "prefer_fresh": bool(prefer_fresh),
                "max_results": int(max_results),
                "target_hint": str(target_hint or "").strip(),
            },
        )

        selected_target = str(decision.get("selected_target", "") or "").strip()
        helper_state = c.hass.states.get(LEGACY_ACTIVE_TARGET_HELPER)

        result: dict[str, Any] = {
            "status": "pending",
            "reason": "",
            "requested_at": requested_at,
            "completed_at": requested_at,
            "correlation_id": corr,
            "dry_run": bool(dry_run),
            "force": bool(force),
            "authority_mode": c._write_authority_mode,
            "target_helper_entity": LEGACY_ACTIVE_TARGET_HELPER,
            "host_cutover_gate_status": str(host_cutover_gate.get("status", "blocked") or "blocked"),
            "host_cutover_gate_ready": bool(host_cutover_gate.get("ready_for_cutover", False)),
            "host_cutover_gate_blockers": host_cutover_gate.get("gate_blockers", []),
            **decision,
        }

        if not selected_target:
            result["status"] = "blocked_no_candidate"
            result["reason"] = "Scheduler produced no selected target"
        elif c._write_authority_mode != WRITE_AUTH_COMPONENT:
            result["status"] = "blocked_authority"
            result["reason"] = "Write authority is legacy; scheduler apply is intentionally blocked"
        elif not bool(host_cutover_gate.get("ready_for_cutover", False)):
            result["status"] = "blocked_host_cutover_gate"
            result["reason"] = "Host-control cutover gate is not ready; scheduler apply is intentionally blocked"
        WritePathFabric.apply_standard_write_guards(
            c,
            result,
            force=bool(force),
            dry_run=bool(dry_run),
            authority_required=WRITE_AUTH_COMPONENT,
            authority_block_reason="Write authority is legacy; scheduler apply is intentionally blocked",
        )

        if result["status"] == "pending" and helper_state is None:
            result["status"] = "blocked_missing_target_helper"
            result["reason"] = "Target helper entity is missing"

        helper_options: list[str] = []
        helper_current = ""
        if helper_state is not None:
            helper_current = str(helper_state.state or "").strip()
            helper_options = WritePathFabric.normalize_options(helper_state.attributes.get("options", []))

        if result["status"] == "pending" and helper_options and selected_target not in helper_options:
            result["status"] = "blocked_option_mismatch"
            result["reason"] = "Selected scheduler target is not present in helper options"
            result["helper_options_count"] = len(helper_options)

        if result["status"] == "pending" and helper_current == selected_target:
            result["status"] = "noop_already_selected"
            result["reason"] = "Target helper already matches scheduler-selected target"

        if result["status"] == "pending" and dry_run:
            result["status"] = "dry_run_ok"
            result["reason"] = "Scheduler apply guards passed (dry run); no helper write executed"

        if result["status"] == "pending":
            c._write_in_progress = True
            try:
                await c.hass.services.async_call(
                    "input_select",
                    "select_option",
                    {
                        "entity_id": LEGACY_ACTIVE_TARGET_HELPER,
                        "option": selected_target,
                    },
                    blocking=True,
                )
                result["status"] = "write_applied"
                result["reason"] = "Scheduler-selected target applied to helper successfully"
            except Exception as err:  # pragma: no cover - defensive runtime guard
                result["status"] = "write_error"
                result["reason"] = "Service call failed during scheduler apply"
                result["error"] = str(err)
            finally:
                c._write_in_progress = False

        if result["status"] in {"dry_run_ok", "noop_already_selected", "write_applied", "write_error"}:
            WritePathFabric.mark_write_touch(c)

        result["completed_at"] = datetime.now(UTC).isoformat()

        c._last_scheduler_decision = {
            "requested_at": requested_at,
            "completed_at": result["completed_at"],
            "correlation_id": corr,
            **decision,
        }
        c._last_scheduler_apply = result
        WritePathFabric.stamp_last_write_attempt(
            c,
            result=result,
            source="scheduler_apply_choice",
            correlation_id=corr,
            active_target=selected_target,
        )

        c.async_set_updated_data(c._build_snapshot())
        return result

    async def async_build_target_options_scaffold(
        self,
        *,
        dry_run: bool,
        force: bool,
        include_none: bool,
        correlation_id: str | None,
    ) -> dict[str, Any]:
        """Build (and optionally apply) component-native target-options scaffold plan."""
        c = self._coordinator
        requested_at = datetime.now(UTC).isoformat()
        corr = (correlation_id or "").strip() or f"target-options-{uuid4().hex[:12]}"
        scaffolds = c._build_component_scaffolds()
        plan = (
            scaffolds.get("target_options_plan", {})
            if isinstance(scaffolds.get("target_options_plan", {}), dict)
            else {}
        )
        helper_entity = str(plan.get("helper_entity", LEGACY_ACTIVE_TARGET_HELPER) or LEGACY_ACTIVE_TARGET_HELPER)
        helper_state = c.hass.states.get(helper_entity)

        candidates = plan.get("candidates", []) if isinstance(plan.get("candidates", []), list) else []
        candidates = [str(item).strip() for item in candidates if isinstance(item, str) and str(item).strip()]
        proposed_options = list(candidates)
        if include_none:
            proposed_options = ["none"] + proposed_options
        if len(proposed_options) == 0:
            proposed_options = ["none"]

        result: dict[str, Any] = {
            "status": "pending",
            "reason": "",
            "requested_at": requested_at,
            "completed_at": requested_at,
            "correlation_id": corr,
            "authority_mode": c._write_authority_mode,
            "helper_entity": helper_entity,
            "helper_exists": helper_state is not None,
            "dry_run": bool(dry_run),
            "force": bool(force),
            "include_none": bool(include_none),
            "planned_options": proposed_options,
            "default_option": str(plan.get("default_option", "none") or "none"),
            "applied_options": [],
            "candidate_count": len(candidates),
        }

        if helper_state is None:
            result["status"] = "blocked_missing_target_helper"
            result["reason"] = "Target helper entity is missing"
        WritePathFabric.apply_standard_write_guards(
            c,
            result,
            force=bool(force),
            dry_run=bool(dry_run),
            authority_required=WRITE_AUTH_COMPONENT,
            authority_block_reason="Write authority is legacy; target-options apply is intentionally blocked",
        )

        if result["status"] == "pending" and dry_run:
            result["status"] = "dry_run_ok"
            result["reason"] = "Target-options scaffold computed successfully (dry run)"
            helper_current = str(helper_state.state or "").strip() if helper_state is not None else ""
            current_ok = c._is_resolved_state(helper_current) and helper_current in proposed_options
            default_option = str(result.get("default_option", "none") or "none")
            result["would_select_default"] = (not current_ok) and default_option in proposed_options

        if result["status"] == "pending":
            c._write_in_progress = True
            try:
                helper_current = str(helper_state.state or "").strip() if helper_state is not None else ""
                current_ok = c._is_resolved_state(helper_current) and helper_current in proposed_options
                default_option = str(result.get("default_option", "none") or "none")
                await c.hass.services.async_call(
                    "input_select",
                    "set_options",
                    {
                        "entity_id": helper_entity,
                        "options": proposed_options,
                    },
                    blocking=True,
                )
                result["status"] = "options_applied"
                result["reason"] = "Target-options scaffold applied to helper successfully"
                result["applied_options"] = proposed_options
                if (not current_ok) and default_option in proposed_options:
                    await c.hass.services.async_call(
                        "input_select",
                        "select_option",
                        {
                            "entity_id": helper_entity,
                            "option": default_option,
                        },
                        blocking=True,
                    )
                    result["selected_default_option"] = default_option
            except Exception as err:  # pragma: no cover - defensive runtime guard
                result["status"] = "write_error"
                result["reason"] = "Service call failed during target-options scaffold apply"
                result["error"] = str(err)
            finally:
                c._write_in_progress = False

        if result["status"] in {"dry_run_ok", "options_applied", "write_error"}:
            WritePathFabric.mark_write_touch(c)

        result["completed_at"] = datetime.now(UTC).isoformat()
        c._last_target_options_attempt = result
        WritePathFabric.stamp_last_write_attempt(
            c,
            result=result,
            source="build_target_options_scaffold",
            correlation_id=corr,
            active_target="",
        )
        c.async_set_updated_data(c._build_snapshot())
        return result

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
        c = self._coordinator
        requested_at = datetime.now(UTC).isoformat()
        corr = (correlation_id or "").strip() or f"auto-select-{uuid4().hex[:12]}"

        scaffolds = c._build_component_scaffolds()
        target_options_plan = (
            scaffolds.get("target_options_plan", {})
            if isinstance(scaffolds.get("target_options_plan", {}), dict)
            else {}
        )
        auto_select_plan = (
            scaffolds.get("auto_select_plan", {})
            if isinstance(scaffolds.get("auto_select_plan", {}), dict)
            else {}
        )

        helper_entity = str(
            target_options_plan.get("helper_entity", LEGACY_ACTIVE_TARGET_HELPER) or LEGACY_ACTIVE_TARGET_HELPER
        )
        helper_state = c.hass.states.get(helper_entity)
        selected_target = str(auto_select_plan.get("selected_target", "") or "").strip()
        selection_reason = str(auto_select_plan.get("selection_reason", "no_candidate") or "no_candidate")

        helper_options: list[str] = []
        helper_current = ""
        if helper_state is not None:
            helper_current = str(helper_state.state or "").strip()
            helper_options = WritePathFabric.normalize_options(helper_state.attributes.get("options", []))

        helper_current_resolved = c._is_resolved_state(helper_current)
        helper_current_in_options = helper_current_resolved and helper_current in helper_options
        if helper_current_in_options and not force:
            selected_target = helper_current
            selection_reason = "component_sticky_current_target"
        if selected_target == "" and helper_current_in_options:
            selected_target = helper_current
            selection_reason = "helper_current_fallback"

        planned_options = (
            target_options_plan.get("proposed_options", [])
            if isinstance(target_options_plan.get("proposed_options", []), list)
            else []
        )
        planned_options = [
            str(item).strip() for item in planned_options if isinstance(item, str) and str(item).strip()
        ]
        if include_none and "none" not in planned_options:
            planned_options = ["none"] + planned_options

        result: dict[str, Any] = {
            "status": "pending",
            "reason": "",
            "requested_at": requested_at,
            "completed_at": requested_at,
            "correlation_id": corr,
            "authority_mode": c._write_authority_mode,
            "helper_entity": helper_entity,
            "helper_exists": helper_state is not None,
            "dry_run": bool(dry_run),
            "force": bool(force),
            "sync_options_if_missing": bool(sync_options_if_missing),
            "include_none": bool(include_none),
            "selected_target": selected_target,
            "selection_reason": selection_reason,
            "helper_current": helper_current,
            "helper_options_count": len(helper_options),
        }

        if selected_target == "":
            result["status"] = "blocked_no_candidate"
            result["reason"] = "Auto-select scaffold has no selected target candidate"
        elif helper_state is None:
            result["status"] = "blocked_missing_target_helper"
            result["reason"] = "Target helper entity is missing"
        WritePathFabric.apply_standard_write_guards(
            c,
            result,
            force=bool(force),
            dry_run=bool(dry_run),
            authority_required=WRITE_AUTH_COMPONENT,
            authority_block_reason="Write authority is legacy; auto-select apply is intentionally blocked",
        )

        if result["status"] == "pending" and selected_target not in helper_options:
            if dry_run and sync_options_if_missing and len(planned_options) > 0:
                result["options_sync_planned"] = True
                result["planned_options_count"] = len(planned_options)
            elif sync_options_if_missing and len(planned_options) > 0:
                try:
                    await c.hass.services.async_call(
                        "input_select",
                        "set_options",
                        {
                            "entity_id": helper_entity,
                            "options": planned_options,
                        },
                        blocking=True,
                    )
                    helper_options = planned_options
                    result["helper_options_count"] = len(helper_options)
                    result["options_synced"] = True
                except Exception as err:  # pragma: no cover - defensive runtime guard
                    result["status"] = "write_error"
                    result["reason"] = "Failed syncing helper options before auto-select apply"
                    result["error"] = str(err)
            else:
                result["status"] = "blocked_option_mismatch"
                result["reason"] = "Selected target is not present in helper options"

        if result["status"] == "pending" and helper_current == selected_target:
            result["status"] = "noop_already_selected"
            result["reason"] = "Helper already matches auto-select scaffold target"

        if result["status"] == "pending" and dry_run:
            result["status"] = "dry_run_ok"
            result["reason"] = "Auto-select scaffold guards passed (dry run)"

        if result["status"] == "pending":
            c._write_in_progress = True
            try:
                await c.hass.services.async_call(
                    "input_select",
                    "select_option",
                    {
                        "entity_id": helper_entity,
                        "option": selected_target,
                    },
                    blocking=True,
                )
                result["status"] = "write_applied"
                result["reason"] = "Auto-select scaffold applied selected target successfully"
            except Exception as err:  # pragma: no cover - defensive runtime guard
                result["status"] = "write_error"
                result["reason"] = "Service call failed during auto-select scaffold apply"
                result["error"] = str(err)
            finally:
                c._write_in_progress = False

        if result["status"] in {"dry_run_ok", "noop_already_selected", "write_applied", "write_error"}:
            WritePathFabric.mark_write_touch(c)

        result["completed_at"] = datetime.now(UTC).isoformat()
        c._last_auto_select_attempt = result
        WritePathFabric.stamp_last_write_attempt(
            c,
            result=result,
            source="run_auto_select_scaffold",
            correlation_id=corr,
            active_target=selected_target,
        )
        c.async_set_updated_data(c._build_snapshot())
        return result

    async def async_track_last_valid_target(
        self,
        *,
        dry_run: bool,
        force: bool,
        correlation_id: str | None,
        source: str = "service_track_last_valid_target",
    ) -> dict[str, Any]:
        """Track helper-selected target into last-valid helper with guarded writes."""
        c = self._coordinator
        requested_at = datetime.now(UTC).isoformat()
        corr = (correlation_id or "").strip() or f"track-last-valid-{uuid4().hex[:12]}"

        helper_state = c.hass.states.get(LEGACY_ACTIVE_TARGET_HELPER)
        last_valid_state = c.hass.states.get(LEGACY_LAST_VALID_TARGET)
        helper_current = str(helper_state.state if helper_state is not None else "").strip()

        result: dict[str, Any] = {
            "status": "pending",
            "reason": "",
            "requested_at": requested_at,
            "completed_at": requested_at,
            "correlation_id": corr,
            "source": source,
            "authority_mode": c._write_authority_mode,
            "dry_run": bool(dry_run),
            "force": bool(force),
            "helper_entity": LEGACY_ACTIVE_TARGET_HELPER,
            "last_valid_entity": LEGACY_LAST_VALID_TARGET,
            "tracked_target": helper_current,
        }

        if helper_state is None:
            result["status"] = "blocked_missing_target_helper"
            result["reason"] = "Target helper entity is missing"
        elif last_valid_state is None:
            result["status"] = "blocked_missing_last_valid_helper"
            result["reason"] = "Last-valid target helper is missing"
        elif not c._is_resolved_state(helper_current):
            result["status"] = "blocked_unresolved_target"
            result["reason"] = "Current helper target is unresolved and cannot be tracked"
        WritePathFabric.apply_standard_write_guards(
            c,
            result,
            force=bool(force),
            dry_run=bool(dry_run),
            authority_required=WRITE_AUTH_COMPONENT,
            authority_block_reason="Write authority is legacy; last-valid tracking write is intentionally blocked",
        )

        if result["status"] == "pending":
            current_last_valid = str(last_valid_state.state if last_valid_state is not None else "").strip()
            if current_last_valid == helper_current:
                result["status"] = "noop_already_tracked"
                result["reason"] = "Last-valid helper already matches current active target"

        if result["status"] == "pending" and dry_run:
            result["status"] = "dry_run_ok"
            result["reason"] = "Last-valid tracking guards passed (dry run)"

        if result["status"] == "pending":
            c._write_in_progress = True
            try:
                await c.hass.services.async_call(
                    "input_text",
                    "set_value",
                    {
                        "entity_id": LEGACY_LAST_VALID_TARGET,
                        "value": helper_current,
                    },
                    blocking=True,
                )
                result["status"] = "write_applied"
                result["reason"] = "Last-valid target updated from current helper selection"
            except Exception as err:  # pragma: no cover - defensive runtime guard
                result["status"] = "write_error"
                result["reason"] = "Service call failed during last-valid tracking"
                result["error"] = str(err)
            finally:
                c._write_in_progress = False

        if result["status"] in {"dry_run_ok", "noop_already_tracked", "write_applied", "write_error"}:
            WritePathFabric.mark_write_touch(c)

        result["completed_at"] = datetime.now(UTC).isoformat()
        c._last_track_last_valid_attempt = result
        WritePathFabric.stamp_last_write_attempt(
            c,
            result=result,
            source=source,
            correlation_id=corr,
            active_target=helper_current,
        )
        c.async_set_updated_data(c._build_snapshot())
        return result

    async def async_restore_last_valid_target(
        self,
        *,
        dry_run: bool,
        force: bool,
        correlation_id: str | None,
    ) -> dict[str, Any]:
        """Restore helper selection from last-valid helper when current selection is unresolved."""
        c = self._coordinator
        requested_at = datetime.now(UTC).isoformat()
        corr = (correlation_id or "").strip() or f"restore-last-valid-{uuid4().hex[:12]}"

        helper_state = c.hass.states.get(LEGACY_ACTIVE_TARGET_HELPER)
        last_valid_state = c.hass.states.get(LEGACY_LAST_VALID_TARGET)

        helper_current = str(helper_state.state if helper_state is not None else "").strip()
        last_valid_target = str(last_valid_state.state if last_valid_state is not None else "").strip()
        helper_options: list[str] = []
        if helper_state is not None:
            helper_options = WritePathFabric.normalize_options(helper_state.attributes.get("options", []))

        current_resolved = c._is_resolved_state(helper_current)
        restore_candidate = (
            last_valid_target if c._is_resolved_state(last_valid_target) and last_valid_target in helper_options else ""
        )

        result: dict[str, Any] = {
            "status": "pending",
            "reason": "",
            "requested_at": requested_at,
            "completed_at": requested_at,
            "correlation_id": corr,
            "authority_mode": c._write_authority_mode,
            "dry_run": bool(dry_run),
            "force": bool(force),
            "helper_entity": LEGACY_ACTIVE_TARGET_HELPER,
            "last_valid_entity": LEGACY_LAST_VALID_TARGET,
            "helper_current": helper_current,
            "last_valid_target": last_valid_target,
            "restore_target": restore_candidate,
            "helper_options_count": len(helper_options),
        }

        if helper_state is None:
            result["status"] = "blocked_missing_target_helper"
            result["reason"] = "Target helper entity is missing"
        elif last_valid_state is None:
            result["status"] = "blocked_missing_last_valid_helper"
            result["reason"] = "Last-valid target helper is missing"
        elif current_resolved and not force:
            result["status"] = "noop_current_target_resolved"
            result["reason"] = "Current helper target is already resolved; restore is not required"
        elif restore_candidate == "":
            result["status"] = "blocked_no_last_valid_candidate"
            result["reason"] = "No restorable last-valid target is present in current helper options"
        WritePathFabric.apply_standard_write_guards(
            c,
            result,
            force=bool(force),
            dry_run=bool(dry_run),
            authority_required=WRITE_AUTH_COMPONENT,
            authority_block_reason="Write authority is legacy; restore-last-valid write is intentionally blocked",
        )

        if result["status"] == "pending" and helper_current == restore_candidate:
            result["status"] = "noop_already_selected"
            result["reason"] = "Helper already matches restorable last-valid target"

        if result["status"] == "pending" and dry_run:
            result["status"] = "dry_run_ok"
            result["reason"] = "Restore-last-valid guards passed (dry run)"

        if result["status"] == "pending":
            c._write_in_progress = True
            try:
                await c.hass.services.async_call(
                    "input_select",
                    "select_option",
                    {
                        "entity_id": LEGACY_ACTIVE_TARGET_HELPER,
                        "option": restore_candidate,
                    },
                    blocking=True,
                )
                result["status"] = "write_applied"
                result["reason"] = "Restored helper selection from last-valid target"
            except Exception as err:  # pragma: no cover - defensive runtime guard
                result["status"] = "write_error"
                result["reason"] = "Service call failed during restore-last-valid apply"
                result["error"] = str(err)
            finally:
                c._write_in_progress = False

        if result["status"] in {
            "dry_run_ok",
            "noop_current_target_resolved",
            "noop_already_selected",
            "write_applied",
            "write_error",
        }:
            WritePathFabric.mark_write_touch(c)

        result["completed_at"] = datetime.now(UTC).isoformat()
        c._last_restore_last_valid_attempt = result
        WritePathFabric.stamp_last_write_attempt(
            c,
            result=result,
            source="restore_last_valid_target",
            correlation_id=corr,
            active_target=restore_candidate,
        )
        c.async_set_updated_data(c._build_snapshot())
        return result

    async def async_cycle_active_target(
        self,
        *,
        dry_run: bool,
        force: bool,
        include_none: bool,
        correlation_id: str | None,
    ) -> dict[str, Any]:
        """Cycle active-target helper options with optional none filtering and override activation."""
        c = self._coordinator
        requested_at = datetime.now(UTC).isoformat()
        corr = (correlation_id or "").strip() or f"cycle-target-{uuid4().hex[:12]}"

        helper_state = c.hass.states.get(LEGACY_ACTIVE_TARGET_HELPER)
        override_state = c.hass.states.get(LEGACY_OVERRIDE_ACTIVE)

        helper_current = str(helper_state.state if helper_state is not None else "").strip()
        helper_options: list[str] = []
        if helper_state is not None:
            helper_options = WritePathFabric.normalize_options(helper_state.attributes.get("options", []))

        cycle_options = list(helper_options)
        if not include_none:
            cycle_options = [item for item in cycle_options if c._normalize_state(item) != "none"]

        next_target = ""
        if len(cycle_options) > 0:
            if helper_current in cycle_options:
                current_index = cycle_options.index(helper_current)
                next_target = cycle_options[(current_index + 1) % len(cycle_options)]
            else:
                next_target = cycle_options[0]

        result: dict[str, Any] = {
            "status": "pending",
            "reason": "",
            "requested_at": requested_at,
            "completed_at": requested_at,
            "correlation_id": corr,
            "authority_mode": c._write_authority_mode,
            "dry_run": bool(dry_run),
            "force": bool(force),
            "include_none": bool(include_none),
            "helper_entity": LEGACY_ACTIVE_TARGET_HELPER,
            "override_entity": LEGACY_OVERRIDE_ACTIVE,
            "helper_current": helper_current,
            "helper_options_count": len(helper_options),
            "cycle_options_count": len(cycle_options),
            "next_target": next_target,
        }

        if helper_state is None:
            result["status"] = "blocked_missing_target_helper"
            result["reason"] = "Target helper entity is missing"
        elif len(cycle_options) == 0:
            result["status"] = "blocked_no_cycle_options"
            result["reason"] = "No cycle candidates are available in target helper options"
        elif next_target == "":
            result["status"] = "blocked_no_next_target"
            result["reason"] = "Unable to derive next cycle target"
        WritePathFabric.apply_standard_write_guards(
            c,
            result,
            force=bool(force),
            dry_run=bool(dry_run),
            authority_required=WRITE_AUTH_COMPONENT,
            authority_block_reason="Write authority is legacy; cycle-target write is intentionally blocked",
        )

        if result["status"] == "pending" and len(cycle_options) == 1 and helper_current == next_target:
            result["status"] = "noop_single_option"
            result["reason"] = "Only one cycle option is available; active target remains unchanged"

        if result["status"] == "pending" and dry_run:
            result["status"] = "dry_run_ok"
            result["reason"] = "Cycle-target guards passed (dry run)"
            result["would_enable_override"] = (
                override_state is not None and c._normalize_state(override_state.state) != "on"
            )

        if result["status"] == "pending":
            c._write_in_progress = True
            try:
                if override_state is not None and c._normalize_state(override_state.state) != "on":
                    await c.hass.services.async_call(
                        "input_boolean",
                        "turn_on",
                        {
                            "entity_id": LEGACY_OVERRIDE_ACTIVE,
                        },
                        blocking=True,
                    )
                await c.hass.services.async_call(
                    "input_select",
                    "select_option",
                    {
                        "entity_id": LEGACY_ACTIVE_TARGET_HELPER,
                        "option": next_target,
                    },
                    blocking=True,
                )
                result["status"] = "write_applied"
                result["reason"] = "Cycle-target selection applied successfully"

                if c._is_resolved_state(next_target):
                    await self.async_track_last_valid_target(
                        dry_run=False,
                        force=True,
                        correlation_id=f"{corr}-track",
                        source="cycle_active_target",
                    )
            except Exception as err:  # pragma: no cover - defensive runtime guard
                result["status"] = "write_error"
                result["reason"] = "Service call failed during cycle-target apply"
                result["error"] = str(err)
            finally:
                c._write_in_progress = False

        if result["status"] in {"dry_run_ok", "noop_single_option", "write_applied", "write_error"}:
            WritePathFabric.mark_write_touch(c)

        result["completed_at"] = datetime.now(UTC).isoformat()
        c._last_cycle_target_attempt = result
        WritePathFabric.stamp_last_write_attempt(
            c,
            result=result,
            source="cycle_active_target",
            correlation_id=corr,
            active_target=next_target,
        )
        c.async_set_updated_data(c._build_snapshot())
        return result

    async def async_set_active_target(
        self,
        *,
        target: str,
        dry_run: bool,
        force: bool,
        sync_options_if_missing: bool,
        correlation_id: str | None,
    ) -> dict[str, Any]:
        """Set active-target helper selection through component-guarded explicit target contract."""
        c = self._coordinator
        requested_at = datetime.now(UTC).isoformat()
        corr = (correlation_id or "").strip() or f"set-active-target-{uuid4().hex[:12]}"

        requested_target = str(target or "").strip()
        helper_state = c.hass.states.get(LEGACY_ACTIVE_TARGET_HELPER)
        helper_current = str(helper_state.state if helper_state is not None else "").strip()
        helper_options: list[str] = []
        if helper_state is not None:
            helper_options = WritePathFabric.normalize_options(helper_state.attributes.get("options", []))

        result: dict[str, Any] = {
            "status": "pending",
            "reason": "",
            "requested_at": requested_at,
            "completed_at": requested_at,
            "correlation_id": corr,
            "authority_mode": c._write_authority_mode,
            "dry_run": bool(dry_run),
            "force": bool(force),
            "sync_options_if_missing": bool(sync_options_if_missing),
            "helper_entity": LEGACY_ACTIVE_TARGET_HELPER,
            "helper_exists": helper_state is not None,
            "helper_current": helper_current,
            "helper_options_count": len(helper_options),
            "requested_target": requested_target,
            "selected_target": requested_target,
        }

        if requested_target == "" or not c._is_resolved_state(requested_target):
            result["status"] = "blocked_invalid_target"
            result["reason"] = "Requested target is unresolved"
        elif c._normalize_state(requested_target) == "none":
            result["status"] = "blocked_invalid_target"
            result["reason"] = "Requested target cannot be none"
        elif helper_state is None:
            result["status"] = "blocked_missing_target_helper"
            result["reason"] = "Target helper entity is missing"

        WritePathFabric.apply_standard_write_guards(
            c,
            result,
            force=bool(force),
            dry_run=bool(dry_run),
            authority_required=WRITE_AUTH_COMPONENT,
            authority_block_reason="Write authority is legacy; explicit target set is intentionally blocked",
        )

        if result["status"] == "pending" and requested_target not in helper_options:
            if dry_run and sync_options_if_missing:
                result["options_sync_planned"] = True
            elif sync_options_if_missing:
                scaffolds = c._build_component_scaffolds()
                target_options_plan = (
                    scaffolds.get("target_options_plan", {})
                    if isinstance(scaffolds.get("target_options_plan", {}), dict)
                    else {}
                )
                planned_options = (
                    target_options_plan.get("proposed_options", [])
                    if isinstance(target_options_plan.get("proposed_options", []), list)
                    else []
                )
                planned_options = [
                    str(item).strip() for item in planned_options if isinstance(item, str) and str(item).strip()
                ]
                if requested_target in planned_options:
                    try:
                        await c.hass.services.async_call(
                            "input_select",
                            "set_options",
                            {
                                "entity_id": LEGACY_ACTIVE_TARGET_HELPER,
                                "options": planned_options,
                            },
                            blocking=True,
                        )
                        helper_options = planned_options
                        result["options_synced"] = True
                        result["helper_options_count"] = len(helper_options)
                    except Exception as err:  # pragma: no cover - defensive runtime guard
                        result["status"] = "write_error"
                        result["reason"] = "Failed syncing helper options before explicit target set"
                        result["error"] = str(err)
                else:
                    result["status"] = "blocked_option_mismatch"
                    result["reason"] = "Requested target is not present in helper options"
            else:
                result["status"] = "blocked_option_mismatch"
                result["reason"] = "Requested target is not present in helper options"

        if result["status"] == "pending" and helper_current == requested_target:
            result["status"] = "noop_already_selected"
            result["reason"] = "Helper already matches requested target"

        if result["status"] == "pending" and dry_run:
            result["status"] = "dry_run_ok"
            result["reason"] = "Explicit target-set guards passed (dry run)"

        if result["status"] == "pending":
            c._write_in_progress = True
            try:
                await c.hass.services.async_call(
                    "input_select",
                    "select_option",
                    {
                        "entity_id": LEGACY_ACTIVE_TARGET_HELPER,
                        "option": requested_target,
                    },
                    blocking=True,
                )
                result["status"] = "write_applied"
                result["reason"] = "Requested target applied successfully"

                await self.async_track_last_valid_target(
                    dry_run=False,
                    force=True,
                    correlation_id=f"{corr}-track",
                    source="set_active_target",
                )
            except Exception as err:  # pragma: no cover - defensive runtime guard
                result["status"] = "write_error"
                result["reason"] = "Service call failed during explicit target set"
                result["error"] = str(err)
            finally:
                c._write_in_progress = False

        if result["status"] in {"dry_run_ok", "noop_already_selected", "write_applied", "write_error"}:
            WritePathFabric.mark_write_touch(c)

        result["completed_at"] = datetime.now(UTC).isoformat()
        c._last_set_active_target_attempt = result
        WritePathFabric.stamp_last_write_attempt(
            c,
            result=result,
            source="set_active_target",
            correlation_id=corr,
            active_target=requested_target,
        )
        c.async_set_updated_data(c._build_snapshot())
        return result
