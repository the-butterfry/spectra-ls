# Description: Event-recovery fabric workflow for Spectra LS state-change orchestration extracted from meta-fabric.
# Version: 2026.08.01.6
# Last updated: 2026-08-01
# PARITY DIRECTIVE (until full cutover): behavior/contract edits here require same-slice two-track parity review
# and version-metadata review in runtime (`packages/` + `esphome/`) and component (`custom_components/spectra_ls/`) tracks.

from __future__ import annotations

import logging
from time import monotonic
from typing import Any
from uuid import uuid4

from homeassistant.helpers.event import async_call_later

from .const import (
    COMPONENT_ACTIVE_TARGET,
    COMPONENT_CONTROL_TARGETS,
    COMPONENT_METADATA_OVERRIDE_ACTIVE,
    COMPONENT_NOW_PLAYING_ENTITY,
    WRITE_AUTH_COMPONENT,
)

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
        self._component_state_last_trigger_monotonic: dict[str, float] = {}
        self._component_state_cooldown_s = 0.8
        self._component_state_inflight_targets: set[str] = set()

    async def _async_run_component_players_change_refresh_coalesced(self, entity_id: str) -> None:
        """Run one coalesced players-change refresh task and clear in-flight marker."""
        try:
            await self.async_run_component_players_change_refresh(
                source=f"state-change:{entity_id}",
            )
        finally:
            self._component_state_inflight_targets.discard(entity_id)

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

    def _component_override_active(self) -> bool:
        """Return component-owned metadata override active state."""
        c = self._coordinator
        override_state = getattr(c, "_component_metadata_override_state", {})
        if isinstance(override_state, dict):
            raw = override_state.get("active")
            if isinstance(raw, bool):
                return raw
            if isinstance(raw, str):
                return raw.strip().lower() in {"on", "true", "1"}

        state = c.hass.states.get(COMPONENT_METADATA_OVERRIDE_ACTIVE)
        normalized = c._normalize_state(state.state if state is not None else "")
        return normalized in {"on", "true", "1"}

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
        """Return whether component auto-select loop can run in current authority/state posture."""
        c = self._coordinator
        if c._write_authority_mode != WRITE_AUTH_COMPONENT:
            return False, "authority_not_component"

        target_count_state = c.hass.states.get(COMPONENT_CONTROL_TARGETS)
        target_count = 0
        if target_count_state is not None:
            try:
                target_count = int(float(str(target_count_state.state).strip()))
            except (TypeError, ValueError):
                target_count = 0
        if target_count <= 0:
            component_selection_state = getattr(c, "_component_selection_state", {})
            if isinstance(component_selection_state, dict):
                options = component_selection_state.get("options", [])
                if isinstance(options, list):
                    target_count = len([item for item in options if isinstance(item, str) and item.strip()])
        if target_count <= 0:
            return False, "component_targets_not_ready"

        if self._component_override_active():
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
        """Refresh options and run bounded component auto-select on key component state changes."""
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
            force=True,
        )

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

            target_options_plan = c._compute_component_target_options_plan()
            if not isinstance(target_options_plan, dict):
                return
            helper_options = (
                target_options_plan.get("proposed_options", [])
                if isinstance(target_options_plan.get("proposed_options", []), list)
                else []
            )
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
            event_data = event.data if event is not None and isinstance(event.data, dict) else {}
            entity_id = str(event_data.get("entity_id", "") or "")
            old_state_obj = event_data.get("old_state")
            new_state_obj = event_data.get("new_state")
            old_state = str(getattr(old_state_obj, "state", "") or "")
            new_state = str(getattr(new_state_obj, "state", "") or "")

            watched_entities = {
                COMPONENT_ACTIVE_TARGET,
                COMPONENT_CONTROL_TARGETS,
                COMPONENT_NOW_PLAYING_ENTITY,
                COMPONENT_METADATA_OVERRIDE_ACTIVE,
            }

            if entity_id in watched_entities:
                # Ignore attribute-only mutations (for example captured_at churn) and
                # unresolved->unresolved transitions to avoid self-trigger refresh loops.
                if old_state == new_state:
                    return

                old_norm = c._normalize_state(old_state)
                new_norm = c._normalize_state(new_state)
                unresolved = {"unknown", "unavailable", "none", "", "null"}
                if old_norm in unresolved and new_norm in unresolved:
                    return

                # Only these component trigger entities are allowed to schedule
                # snapshot refresh work; other watched entities are output-facing
                # diagnostics that can self-trigger churn loops.
                if entity_id not in {COMPONENT_CONTROL_TARGETS, COMPONENT_NOW_PLAYING_ENTITY}:
                    return

            if entity_id in {COMPONENT_CONTROL_TARGETS, COMPONENT_NOW_PLAYING_ENTITY}:
                now_mono = monotonic()
                last_trigger = self._component_state_last_trigger_monotonic.get(entity_id, 0.0)
                if last_trigger > 0 and (now_mono - last_trigger) < self._component_state_cooldown_s:
                    return

                if entity_id in self._component_state_inflight_targets:
                    return

                self._component_state_last_trigger_monotonic[entity_id] = now_mono
                self._component_state_inflight_targets.add(entity_id)
                c.hass.async_create_task(
                    self._async_run_component_players_change_refresh_coalesced(entity_id)
                )

            now_mono = monotonic()
            elapsed = now_mono - c._last_snapshot_refresh_monotonic
            if c._last_snapshot_refresh_monotonic == 0.0 or elapsed >= c._snapshot_refresh_min_interval_s:
                c._refresh_snapshot(force=False)
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
