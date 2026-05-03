# Description: Event-recovery fabric workflow for Spectra LS state-change orchestration extracted from meta-fabric.
# Version: 2026.05.03.4
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
    LEGACY_MA_PLAYERS,
    LEGACY_META_DETECTED_ENTITY,
    LEGACY_META_STALE,
    LEGACY_NO_CONTROL_CAPABLE_HOSTS,
    LEGACY_NOW_PLAYING_ENTITY,
    LEGACY_OVERRIDE_ACTIVE,
    LEGACY_SURFACES,
    WRITE_AUTH_COMPONENT,
)
from .write_path_fabric import WritePathFabric

_LOGGER = logging.getLogger(__name__)


class EventRecoveryFabricWorkflow:
    """Owns event/recovery orchestration lane extracted from meta-fabric."""

    def __init__(self, coordinator: Any) -> None:
        self._coordinator = coordinator
        self._global_state_last_trigger_monotonic: dict[str, float] = {}
        self._global_state_cooldown_s = 0.35
        self._global_state_inflight_targets: set[str] = set()
        self._global_state_cache_max_entries = 512
        self._global_state_cache_prune_window_s = 30.0

    def _prune_global_state_cache(self, now_mono: float) -> None:
        """Bound cache size and remove stale coalescing entries."""
        stale_cutoff = max(now_mono - self._global_state_cache_prune_window_s, 0.0)
        stale_keys = [
            key
            for key, ts in self._global_state_last_trigger_monotonic.items()
            if ts <= stale_cutoff and key not in self._global_state_inflight_targets
        ]
        for key in stale_keys:
            self._global_state_last_trigger_monotonic.pop(key, None)

        if len(self._global_state_last_trigger_monotonic) <= self._global_state_cache_max_entries:
            return

        by_age = sorted(
            self._global_state_last_trigger_monotonic.items(),
            key=lambda item: item[1],
        )
        to_remove = len(self._global_state_last_trigger_monotonic) - self._global_state_cache_max_entries
        removed = 0
        for entity_id, _ts in by_age:
            if entity_id in self._global_state_inflight_targets:
                continue
            self._global_state_last_trigger_monotonic.pop(entity_id, None)
            removed += 1
            if removed >= to_remove:
                break

    async def _async_run_global_state_auto_select(self, entity_id: str) -> None:
        """Run one coalesced global-state auto-select loop for a target and clear in-flight marker."""
        try:
            await self.async_run_component_auto_select_loop(
                source=f"global-state:{entity_id}",
                force=False,
            )
        finally:
            self._global_state_inflight_targets.discard(entity_id)

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
            helper_options = WritePathFabric.normalize_options(helper_state.attributes.get("options", []))
            watched_targets = {
                str(item).strip()
                for item in helper_options
                if isinstance(item, str) and str(item).strip()
            }
            if entity_id in watched_targets:
                now_mono = monotonic()
                self._prune_global_state_cache(now_mono)
                last_trigger = self._global_state_last_trigger_monotonic.get(entity_id, 0.0)
                if last_trigger > 0 and (now_mono - last_trigger) < self._global_state_cooldown_s:
                    return

                if entity_id in self._global_state_inflight_targets:
                    return

                self._global_state_last_trigger_monotonic[entity_id] = now_mono
                self._global_state_inflight_targets.add(entity_id)
                c.hass.async_create_task(self._async_run_global_state_auto_select(entity_id))
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
