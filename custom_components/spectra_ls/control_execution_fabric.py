# Description: Control-execution fabric workflow for Spectra LS control-center settings/input and guarded write-trial services extracted from coordinator.
# Version: 2026.06.22.2
# Last updated: 2026-06-22
# PARITY DIRECTIVE (until full cutover): behavior/contract edits here require same-slice two-track parity review
# and version-metadata review in runtime (`packages/` + `esphome/`) and component (`custom_components/spectra_ls/`) tracks.

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from .const import (
    CONTROL_CENTER_INPUT_EVENTS,
    OPT_DEFAULT_WRITE_AUTHORITY_MODE,
    WRITE_AUTH_COMPONENT,
    normalize_control_center_settings,
)
from .write_path_fabric import WritePathFabric


class ControlExecutionFabricWorkflow:
    """Owns control-execution service lane extracted from coordinator."""

    def __init__(self, coordinator: Any) -> None:
        self._coordinator = coordinator

    async def async_apply_control_center_settings(self, raw_options: dict[str, Any] | None) -> dict[str, Any]:
        """Normalize and apply control-center settings from config-entry options."""
        c = self._coordinator
        c._control_center_settings = normalize_control_center_settings(raw_options)
        c.async_set_updated_data(c._build_snapshot())
        return dict(c._control_center_settings)

    async def async_execute_control_center_input(
        self,
        *,
        input_event: str,
        correlation_id: str | None,
        target_hint: str | None,
        dry_run: bool,
        delta: Any,
    ) -> dict[str, Any]:
        """Execute one mapped control-center input with dry-run-first safety."""
        c = self._coordinator
        requested_at = datetime.now(UTC).isoformat()
        normalized_event = (input_event or "").strip().lower()
        corr = (correlation_id or "").strip() or f"p6-input-{uuid4().hex[:12]}"
        hint = (target_hint or "").strip()

        result: dict[str, Any] = {
            "status": "pending",
            "requested_at": requested_at,
            "completed_at": requested_at,
            "correlation_id": corr,
            "input_event": normalized_event,
            "target_hint": hint,
            "dry_run": bool(dry_run),
            "delta": delta,
            "mapped_action": None,
            "reason": "",
            "read_only_mode": bool(c._control_center_settings.get("read_only_mode", True)),
        }

        if normalized_event not in CONTROL_CENTER_INPUT_EVENTS:
            result["status"] = "blocked_unknown_input_event"
            result["reason"] = "input_event is not part of the supported control-center contract"
        else:
            mapped_action: str = ""
            if normalized_event == "encoder_turn":
                mapped_action = str(c._control_center_settings.get("encoder_turn_action", "") or "").strip()
            elif normalized_event == "encoder_press":
                mapped_action = str(c._control_center_settings.get("encoder_press_action", "") or "").strip()
            elif normalized_event == "encoder_long_press":
                mapped_action = str(c._control_center_settings.get("encoder_long_press_action", "") or "").strip()
            elif normalized_event == "button_1":
                mapped_action = str(c._control_center_settings.get("button_1_scene", "") or "").strip()
            elif normalized_event == "button_2":
                mapped_action = str(c._control_center_settings.get("button_2_scene", "") or "").strip()
            elif normalized_event == "button_3":
                mapped_action = str(c._control_center_settings.get("button_3_scene", "") or "").strip()
            elif normalized_event == "button_4":
                mapped_action = str(c._control_center_settings.get("button_4_scene", "") or "").strip()

            result["mapped_action"] = mapped_action

            if not mapped_action:
                result["status"] = "blocked_unmapped_input"
                result["reason"] = "No mapping exists for the selected input_event"
            elif mapped_action.lower() in {"scene.none", "none"}:
                result["status"] = "blocked_scene_unconfigured"
                result["reason"] = "Input is mapped to placeholder scene.none"
            elif mapped_action == "no_op":
                result["status"] = "noop_action"
                result["reason"] = "Mapped action is no_op; execution intentionally performs no runtime write"
            elif mapped_action == "volume":
                snapshot = c._build_snapshot()
                route_trace = snapshot.get("route_trace", {}) if isinstance(snapshot.get("route_trace", {}), dict) else {}
                route_target = str(route_trace.get("active_target", "") or "").strip()
                target_entity = hint or route_target
                target_entity = target_entity.strip()
                if target_entity.lower() in {"", "none", "unknown", "unavailable"}:
                    result["status"] = "blocked_target_unresolved"
                    result["reason"] = "No resolved component route target is available for volume action"
                elif result["read_only_mode"] and not dry_run:
                    result["status"] = "blocked_read_only_mode"
                    result["reason"] = "Control-center read_only_mode is enabled; non-dry-run execution is blocked"
                else:
                    parsed_delta: float | None = None
                    try:
                        if delta is not None:
                            parsed_delta = float(delta)
                    except (TypeError, ValueError):
                        parsed_delta = None

                    if parsed_delta is None or parsed_delta == 0:
                        parsed_delta = 1.0

                    state_obj = c.hass.states.get(target_entity)
                    current_level: float | None = None
                    if state_obj is not None:
                        raw_level = state_obj.attributes.get("volume_level")
                        try:
                            if raw_level is not None:
                                current_level = float(raw_level)
                        except (TypeError, ValueError):
                            current_level = None

                    result["target_entity"] = target_entity
                    result["current_volume_level"] = current_level

                    if dry_run:
                        if current_level is not None:
                            proposed_level = max(0.0, min(1.0, round(current_level + (parsed_delta / 100.0), 3)))
                            result["proposed_volume_level"] = proposed_level
                        result["status"] = "dry_run_ok"
                        result["reason"] = "Volume action resolved successfully in dry-run mode"
                    else:
                        try:
                            if current_level is not None:
                                proposed_level = max(0.0, min(1.0, round(current_level + (parsed_delta / 100.0), 3)))
                                await c.hass.services.async_call(
                                    "media_player",
                                    "volume_set",
                                    {
                                        "entity_id": target_entity,
                                        "volume_level": proposed_level,
                                    },
                                    blocking=True,
                                )
                                result["proposed_volume_level"] = proposed_level
                                result["status"] = "applied_volume_set"
                                result["reason"] = "Mapped volume action executed via media_player.volume_set"
                            else:
                                service_name = "volume_up" if parsed_delta >= 0 else "volume_down"
                                await c.hass.services.async_call(
                                    "media_player",
                                    service_name,
                                    {"entity_id": target_entity},
                                    blocking=True,
                                )
                                result["status"] = "applied_volume_step"
                                result["reason"] = f"Mapped volume action executed via media_player.{service_name}"
                        except Exception as err:  # pragma: no cover - defensive runtime guard
                            result["status"] = "volume_write_error"
                            result["reason"] = f"Volume action failed: {err}"
            elif mapped_action == "scene_quick_trigger":
                quick_scene = str(c._control_center_settings.get("button_1_scene", "scene.none") or "scene.none").strip()
                result["mapped_action"] = f"scene_quick_trigger:{quick_scene}"
                if quick_scene.lower() in {"", "scene.none"}:
                    result["status"] = "blocked_scene_unconfigured"
                    result["reason"] = "scene_quick_trigger requires button_1_scene to be configured"
                elif result["read_only_mode"] and not dry_run:
                    result["status"] = "blocked_read_only_mode"
                    result["reason"] = "Control-center read_only_mode is enabled; non-dry-run execution is blocked"
                elif dry_run:
                    result["status"] = "dry_run_ok"
                    result["reason"] = "scene_quick_trigger resolved successfully in dry-run mode"
                else:
                    try:
                        await c.hass.services.async_call(
                            "scene",
                            "turn_on",
                            {"entity_id": quick_scene},
                            blocking=True,
                        )
                        result["status"] = "applied_scene_turn_on"
                        result["reason"] = "scene_quick_trigger executed via button_1_scene binding"
                    except Exception as err:  # pragma: no cover - defensive runtime guard
                        result["status"] = "scene_turn_on_error"
                        result["reason"] = f"Scene call failed: {err}"
            elif result["read_only_mode"] and not dry_run:
                result["status"] = "blocked_read_only_mode"
                result["reason"] = "Control-center read_only_mode is enabled; non-dry-run execution is blocked"
            elif dry_run:
                result["status"] = "dry_run_ok"
                result["reason"] = "Mapping resolved successfully in dry-run mode"
            elif mapped_action.startswith("scene."):
                try:
                    await c.hass.services.async_call(
                        "scene",
                        "turn_on",
                        {"entity_id": mapped_action},
                        blocking=True,
                    )
                    result["status"] = "applied_scene_turn_on"
                    result["reason"] = "Mapped scene turn_on call executed"
                except Exception as err:  # pragma: no cover - defensive runtime guard
                    result["status"] = "scene_turn_on_error"
                    result["reason"] = f"Scene call failed: {err}"
            else:
                result["status"] = "blocked_unimplemented_action"
                result["reason"] = "Mapped action is reserved for future bounded execution slices"

        result["completed_at"] = datetime.now(UTC).isoformat()
        c._last_control_center_action_attempt = result
        c.async_set_updated_data(c._build_snapshot())
        return result

    async def async_set_write_authority(self, mode: str, reason: str = "") -> None:
        """Set write authority mode for guarded routing write-path trials."""
        c = self._coordinator
        requested_mode = str(mode or "").strip().lower()
        normalized_mode = WRITE_AUTH_COMPONENT
        c._write_authority_mode = normalized_mode

        options = dict(c._entry.options)
        persisted_mode = str(options.get(OPT_DEFAULT_WRITE_AUTHORITY_MODE, "") or "").strip().lower()
        if persisted_mode != normalized_mode:
            options[OPT_DEFAULT_WRITE_AUTHORITY_MODE] = normalized_mode
            c.hass.config_entries.async_update_entry(c._entry, options=options)

        c._last_write_attempt = {
            "status": "authority_set_component_only",
            "timestamp": datetime.now(UTC).isoformat(),
            "authority_mode": normalized_mode,
            "requested_mode": requested_mode,
            "reason": (reason or "").strip() or "Authority mode pinned to component",
            "correlation_id": f"authority-{uuid4().hex[:12]}",
        }
        c.async_set_updated_data(c._build_snapshot())

    async def async_route_write_trial(self, correlation_id: str | None = None, force: bool = False) -> None:
        """Record guarded route-write trial posture without legacy helper mutation."""
        c = self._coordinator
        corr = (correlation_id or "").strip() or f"route-write-{uuid4().hex[:12]}"
        now_iso = datetime.now(UTC).isoformat()
        snapshot = c._build_snapshot()
        route_trace = snapshot.get("route_trace", {})
        active_target = str(route_trace.get("active_target", "") or "").strip()
        route_decision = str(route_trace.get("decision", "") or "").strip()

        result: dict[str, Any] = {
            "timestamp": now_iso,
            "correlation_id": corr,
            "authority_mode": c._write_authority_mode,
            "force": bool(force),
            "route_decision": route_decision,
            "active_target": active_target,
            "target_entity_source": "route_trace.active_target",
        }

        result["status"] = "pending"
        result["reason"] = ""
        WritePathFabric.apply_standard_write_guards(
            c,
            result,
            force=bool(force),
            dry_run=False,
            authority_required=WRITE_AUTH_COMPONENT,
            authority_block_reason="Component-only authority required; write blocked by guardrail",
        )
        if result.get("status") == "pending" and route_decision != "route_linkplay_tcp":
            result.update(
                {
                    "status": "blocked_route_decision",
                    "reason": "Route decision is not eligible for P3-S01 routing write trial",
                }
            )
        if result.get("status") == "pending" and active_target.lower() in {"", "none", "unknown", "unavailable"}:
            result.update(
                {
                    "status": "blocked_target_missing",
                    "reason": "Active target is unresolved",
                }
            )
        if result.get("status") == "pending":
            result.update(
                {
                    "status": "retired_legacy_helper_write_lane",
                    "reason": "Legacy helper write lane is retired; component route state is authoritative",
                }
            )

        WritePathFabric.mark_write_touch(c)
        WritePathFabric.stamp_last_write_attempt(
            c,
            result=result,
            source="route_write_trial_retired",
            correlation_id=corr,
            active_target=active_target,
        )
        c.async_set_updated_data(c._build_snapshot())
