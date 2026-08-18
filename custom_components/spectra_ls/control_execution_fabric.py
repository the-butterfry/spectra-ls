# Description: Control-execution fabric workflow for Spectra LS control-center settings/input and guarded write-trial services extracted from coordinator.
# Version: 2026.08.18.1
# Last updated: 2026-08-18
# PARITY DIRECTIVE (until full cutover): behavior/contract edits here require same-slice two-track parity review
# and version-metadata review in runtime (`packages/` + `esphome/`) and component (`custom_components/spectra_ls/`) tracks.

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from time import monotonic
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
        self._volume_service_min_interval_s = 0.08
        self._volume_service_retry_attempts = 2
        self._volume_service_retry_delay_s = 0.012
        self._last_volume_service_monotonic_by_target: dict[str, float] = {}

    def _parse_volume_delta(self, raw_delta: Any) -> float:
        """Parse and normalize volume delta for deterministic write math."""
        try:
            if raw_delta is not None:
                parsed = float(raw_delta)
                if parsed != 0:
                    return parsed
        except (TypeError, ValueError):
            pass
        return 1.0

    @staticmethod
    def _clamp_volume_level(level: float) -> float:
        return max(0.0, min(1.0, round(level, 3)))

    async def _async_pace_volume_service(self, target_entity: str) -> None:
        """Apply small per-target pacing to reduce service burst churn."""
        target = str(target_entity or "").strip()
        if not target:
            return
        last_mono = self._last_volume_service_monotonic_by_target.get(target, 0.0)
        if last_mono > 0:
            elapsed = monotonic() - last_mono
            wait_s = self._volume_service_min_interval_s - elapsed
            if wait_s > 0:
                await asyncio.sleep(wait_s)
        self._last_volume_service_monotonic_by_target[target] = monotonic()

    async def _async_call_volume_service_with_retry(
        self,
        service_name: str,
        service_data: dict[str, Any],
    ) -> tuple[bool, int, str]:
        """Call media_player volume services with bounded retry semantics."""
        c = self._coordinator
        last_error = ""
        for attempt in range(1, self._volume_service_retry_attempts + 1):
            try:
                await c.hass.services.async_call(
                    "media_player",
                    service_name,
                    service_data,
                    blocking=True,
                )
                return True, attempt, ""
            except Exception as err:  # pragma: no cover - defensive runtime guard
                last_error = str(err)
                if attempt < self._volume_service_retry_attempts:
                    await asyncio.sleep(self._volume_service_retry_delay_s)
        return False, self._volume_service_retry_attempts, last_error

    def _resolve_route_target(self, target_hint: str | None) -> str:
        """Resolve target from hint, cached route snapshot surfaces, or helper fallback."""
        c = self._coordinator
        hint = str(target_hint or "").strip()
        if hint:
            return hint

        snapshot = c.data if isinstance(c.data, dict) else {}
        route_trace = snapshot.get("route_trace", {}) if isinstance(snapshot.get("route_trace", {}), dict) else {}
        route_target = str(route_trace.get("active_target", "") or "").strip()
        if route_target:
            return route_target

        parity = snapshot.get("parity", {}) if isinstance(snapshot.get("parity", {}), dict) else {}
        parity_target = str(parity.get("active_target", "") or "").strip()
        if parity_target:
            return parity_target

        helper_state = c.hass.states.get("input_select.ma_active_target")
        return str(helper_state.state if helper_state is not None else "").strip()

    def _schedule_snapshot_refresh(self) -> None:
        """Request throttled coordinator refresh instead of immediate full snapshot rebuild."""
        c = self._coordinator
        refresh = getattr(c, "_refresh_snapshot", None)
        if callable(refresh):
            refresh(force=False)
            return
        c.async_set_updated_data(c._build_snapshot())

    def _mapped_action_for_event(self, normalized_event: str) -> str:
        """Resolve configured mapped action for a supported control-center input event."""
        c = self._coordinator
        if normalized_event == "encoder_turn":
            return str(c._control_center_settings.get("encoder_turn_action", "") or "").strip()
        if normalized_event == "encoder_press":
            return str(c._control_center_settings.get("encoder_press_action", "") or "").strip()
        if normalized_event == "encoder_long_press":
            return str(c._control_center_settings.get("encoder_long_press_action", "") or "").strip()
        if normalized_event == "button_1":
            return str(c._control_center_settings.get("button_1_scene", "") or "").strip()
        if normalized_event == "button_2":
            return str(c._control_center_settings.get("button_2_scene", "") or "").strip()
        if normalized_event == "button_3":
            return str(c._control_center_settings.get("button_3_scene", "") or "").strip()
        if normalized_event == "button_4":
            return str(c._control_center_settings.get("button_4_scene", "") or "").strip()
        return ""

    @staticmethod
    def _normalized_action_key(mapped_action: str) -> str:
        """Normalize mapped action text into stable strategy keys."""
        action_key = mapped_action.strip().lower().replace("-", "_").replace(" ", "_")
        if action_key == "playpause":
            return "play_pause"
        if action_key in {"mutetoggle", "mute"}:
            return "mute_toggle"
        if action_key in {"noop", "none_op"}:
            return "no_op"
        if action_key in {"scene_none", "scene.none"}:
            return "scene.none"
        return action_key

    @staticmethod
    def _target_unresolved(target_entity: str) -> bool:
        return str(target_entity or "").strip().lower() in {"", "none", "unknown", "unavailable"}

    async def _execute_volume_action(
        self,
        *,
        result: dict[str, Any],
        hint: str,
        dry_run: bool,
        delta: Any,
    ) -> None:
        c = self._coordinator
        target_entity = self._resolve_route_target(hint)
        if self._target_unresolved(target_entity):
            result["status"] = "blocked_target_unresolved"
            result["reason"] = "No resolved component route target is available for volume action"
            return
        if result["read_only_mode"] and not dry_run:
            result["status"] = "blocked_read_only_mode"
            result["reason"] = "Control-center read_only_mode is enabled; non-dry-run execution is blocked"
            return

        parsed_delta = self._parse_volume_delta(delta)

        state_obj = c.hass.states.get(target_entity)
        current_level: float | None = None
        if state_obj is not None:
            raw_level = state_obj.attributes.get("volume_level")
            try:
                if raw_level is not None:
                    current_level = float(raw_level)
            except (TypeError, ValueError):
                current_level = None
        current_mute: bool | None = None
        if state_obj is not None:
            raw_mute = state_obj.attributes.get("is_volume_muted")
            if isinstance(raw_mute, bool):
                current_mute = raw_mute

        result["target_entity"] = target_entity
        result["current_volume_level"] = current_level
        result["current_is_volume_muted"] = current_mute
        result["requested_volume_delta"] = parsed_delta

        if dry_run:
            if current_level is not None:
                proposed_level = self._clamp_volume_level(current_level + (parsed_delta / 100.0))
                result["proposed_volume_level"] = proposed_level
            else:
                result["proposed_volume_step_service"] = "volume_up" if parsed_delta >= 0 else "volume_down"
                result["proposed_volume_step_count"] = 1
            if current_mute is True:
                result["proposed_is_volume_muted"] = False
            result["status"] = "dry_run_ok"
            result["reason"] = "Volume action resolved successfully in dry-run mode"
            return

        try:
            await self._async_pace_volume_service(target_entity)

            if current_mute is True:
                unmute_ok, unmute_attempts, unmute_error = await self._async_call_volume_service_with_retry(
                    "volume_mute",
                    {
                        "entity_id": target_entity,
                        "is_volume_muted": False,
                    },
                )
                result["unmute_attempts"] = unmute_attempts
                if not unmute_ok:
                    raise RuntimeError(f"volume_mute retry failure: {unmute_error}")
                result["proposed_is_volume_muted"] = False

            if current_level is not None:
                proposed_level = self._clamp_volume_level(current_level + (parsed_delta / 100.0))
                ok, attempts, last_error = await self._async_call_volume_service_with_retry(
                    "volume_set",
                    {
                        "entity_id": target_entity,
                        "volume_level": proposed_level,
                    },
                )
                result["volume_write_attempts"] = attempts
                if not ok:
                    raise RuntimeError(f"volume_set retry failure: {last_error}")
                result["proposed_volume_level"] = proposed_level
                result["status"] = "applied_volume_set"
                result["reason"] = "Mapped volume action executed via media_player.volume_set"
                return

            service_name = "volume_up" if parsed_delta >= 0 else "volume_down"
            ok, attempts, last_error = await self._async_call_volume_service_with_retry(
                service_name,
                {"entity_id": target_entity},
            )
            result["volume_write_attempts"] = attempts
            if not ok:
                raise RuntimeError(f"{service_name} retry failure: {last_error}")
            result["volume_step_service"] = service_name
            result["volume_step_count"] = 1
            result["status"] = "applied_volume_step"
            result["reason"] = (
                f"Mapped volume action executed via media_player.{service_name} "
                "(steps=1 fallback)"
            )
        except Exception as err:  # pragma: no cover - defensive runtime guard
            result["status"] = "volume_write_error"
            result["reason"] = f"Volume action failed: {err}"

    async def _execute_transport_action(
        self,
        *,
        action_key: str,
        result: dict[str, Any],
        hint: str,
        dry_run: bool,
    ) -> None:
        c = self._coordinator
        target_entity = self._resolve_route_target(hint)
        if self._target_unresolved(target_entity):
            result["status"] = "blocked_target_unresolved"
            result["reason"] = f"No resolved component route target is available for {action_key} action"
            return
        if result["read_only_mode"] and not dry_run:
            result["status"] = "blocked_read_only_mode"
            result["reason"] = "Control-center read_only_mode is enabled; non-dry-run execution is blocked"
            return

        result["target_entity"] = target_entity
        state_obj = c.hass.states.get(target_entity)
        current_mute: bool | None = None
        if state_obj is not None:
            raw_mute = state_obj.attributes.get("is_volume_muted")
            if isinstance(raw_mute, bool):
                current_mute = raw_mute

        if dry_run:
            result["status"] = "dry_run_ok"
            if action_key == "play_pause":
                result["reason"] = "play_pause action resolved successfully in dry-run mode"
            else:
                result["current_is_volume_muted"] = current_mute
                if current_mute is not None:
                    result["proposed_is_volume_muted"] = not current_mute
                result["reason"] = "mute_toggle action resolved successfully in dry-run mode"
            return

        try:
            if action_key == "play_pause":
                await c.hass.services.async_call(
                    "media_player",
                    "media_play_pause",
                    {"entity_id": target_entity},
                    blocking=False,
                )
                result["status"] = "applied_play_pause"
                result["reason"] = "Mapped play_pause action executed via media_player.media_play_pause"
                return

            desired_mute = not current_mute if current_mute is not None else True
            await c.hass.services.async_call(
                "media_player",
                "volume_mute",
                {
                    "entity_id": target_entity,
                    "is_volume_muted": desired_mute,
                },
                blocking=False,
            )
            result["current_is_volume_muted"] = current_mute
            result["proposed_is_volume_muted"] = desired_mute
            result["status"] = "applied_mute_toggle"
            result["reason"] = "Mapped mute_toggle action executed via media_player.volume_mute"
        except Exception as err:  # pragma: no cover - defensive runtime guard
            if action_key == "play_pause":
                result["status"] = "play_pause_error"
                result["reason"] = f"play_pause action failed: {err}"
            else:
                result["status"] = "mute_toggle_error"
                result["reason"] = f"mute_toggle action failed: {err}"

    async def _execute_scene_quick_trigger(
        self,
        *,
        result: dict[str, Any],
        dry_run: bool,
    ) -> None:
        c = self._coordinator
        quick_scene = str(c._control_center_settings.get("button_1_scene", "scene.none") or "scene.none").strip()
        result["mapped_action"] = f"scene_quick_trigger:{quick_scene}"
        if quick_scene.lower() in {"", "scene.none"}:
            result["status"] = "blocked_scene_unconfigured"
            result["reason"] = "scene_quick_trigger requires button_1_scene to be configured"
            return
        if result["read_only_mode"] and not dry_run:
            result["status"] = "blocked_read_only_mode"
            result["reason"] = "Control-center read_only_mode is enabled; non-dry-run execution is blocked"
            return
        if dry_run:
            result["status"] = "dry_run_ok"
            result["reason"] = "scene_quick_trigger resolved successfully in dry-run mode"
            return

        try:
            await c.hass.services.async_call(
                "scene",
                "turn_on",
                {"entity_id": quick_scene},
                blocking=False,
            )
            result["status"] = "applied_scene_turn_on"
            result["reason"] = "scene_quick_trigger executed via button_1_scene binding"
        except Exception as err:  # pragma: no cover - defensive runtime guard
            result["status"] = "scene_turn_on_error"
            result["reason"] = f"Scene call failed: {err}"

    async def _execute_scene_entity_action(
        self,
        *,
        result: dict[str, Any],
        mapped_action: str,
        dry_run: bool,
    ) -> None:
        c = self._coordinator
        if result["read_only_mode"] and not dry_run:
            result["status"] = "blocked_read_only_mode"
            result["reason"] = "Control-center read_only_mode is enabled; non-dry-run execution is blocked"
            return
        if dry_run:
            result["status"] = "dry_run_ok"
            result["reason"] = "Mapping resolved successfully in dry-run mode"
            return

        try:
            await c.hass.services.async_call(
                "scene",
                "turn_on",
                {"entity_id": mapped_action},
                blocking=False,
            )
            result["status"] = "applied_scene_turn_on"
            result["reason"] = "Mapped scene turn_on call executed"
        except Exception as err:  # pragma: no cover - defensive runtime guard
            result["status"] = "scene_turn_on_error"
            result["reason"] = f"Scene call failed: {err}"

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
            mapped_action: str = self._mapped_action_for_event(normalized_event)
            result["mapped_action"] = mapped_action
            action_key = self._normalized_action_key(mapped_action)

            if not mapped_action:
                result["status"] = "blocked_unmapped_input"
                result["reason"] = "No mapping exists for the selected input_event"
            elif action_key in {"scene.none", "none"}:
                result["status"] = "blocked_scene_unconfigured"
                result["reason"] = "Input is mapped to placeholder scene.none"
            elif action_key == "no_op":
                result["status"] = "noop_action"
                result["reason"] = "Mapped action is no_op; execution intentionally performs no runtime write"
            if action_key == "volume":
                await self._execute_volume_action(
                    result=result,
                    hint=hint,
                    dry_run=dry_run,
                    delta=delta,
                )
            elif action_key in {"play_pause", "mute_toggle"}:
                await self._execute_transport_action(
                    action_key=action_key,
                    result=result,
                    hint=hint,
                    dry_run=dry_run,
                )
            elif action_key == "scene_quick_trigger":
                await self._execute_scene_quick_trigger(
                    result=result,
                    dry_run=dry_run,
                )
            elif mapped_action.lower().startswith("scene."):
                await self._execute_scene_entity_action(
                    result=result,
                    mapped_action=mapped_action,
                    dry_run=dry_run,
                )
            elif result["read_only_mode"] and not dry_run:
                result["status"] = "blocked_read_only_mode"
                result["reason"] = "Control-center read_only_mode is enabled; non-dry-run execution is blocked"
            elif dry_run:
                result["status"] = "dry_run_ok"
                result["reason"] = "Mapping resolved successfully in dry-run mode"
            else:
                result["status"] = "blocked_unimplemented_action"
                result["reason"] = f"Mapped action '{mapped_action}' (normalized='{action_key}') is reserved for future bounded execution slices"

        result["completed_at"] = datetime.now(UTC).isoformat()
        c._last_control_center_action_attempt = result
        self._schedule_snapshot_refresh()
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
