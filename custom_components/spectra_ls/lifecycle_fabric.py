# Description: Lifecycle-fabric workflow for Spectra LS coordinator listener setup/shutdown orchestration extracted from coordinator.
# Version: 2026.05.03.1
# Last updated: 2026-05-03
# PARITY DIRECTIVE (until full cutover): behavior/contract edits here require same-slice two-track parity review
# and version-metadata review in runtime (`packages/` + `esphome/`) and component (`custom_components/spectra_ls/`) tracks.

from __future__ import annotations

from typing import Any

from homeassistant.helpers.event import async_track_state_change_event

from .const import (
    LEGACY_ACTIVE_META_ENTITY,
    LEGACY_ACTIVE_TARGET_HELPER,
    LEGACY_CONTROL_AMBIGUOUS,
    LEGACY_CONTROL_HOST,
    LEGACY_CONTROL_TARGETS,
    LEGACY_META_CANDIDATES,
    LEGACY_META_DETECTED_ENTITY,
    LEGACY_META_STALE,
    LEGACY_NO_CONTROL_CAPABLE_HOSTS,
    LEGACY_NOW_PLAYING_ENTITY,
    LEGACY_NOW_PLAYING_STATE,
    LEGACY_NOW_PLAYING_TITLE,
    LEGACY_OVERRIDE_ACTIVE,
    LEGACY_ROOMS_JSON,
    LEGACY_ROOMS_RAW,
    LEGACY_SERVER_PROFILE,
    LEGACY_SERVER_PROFILE_EFFECTIVE,
    LEGACY_SURFACES,
)


class LifecycleFabricWorkflow:
    """Owns coordinator lifecycle listener orchestration extracted from coordinator."""

    def __init__(self, coordinator: Any) -> None:
        self._coordinator = coordinator

    async def async_setup(self) -> None:
        """Initialize data and state listeners."""
        c = self._coordinator
        await c.async_refresh()

        watched_entities = set(LEGACY_SURFACES.values())
        watched_entities.update(
            {
                LEGACY_ACTIVE_TARGET_HELPER,
                LEGACY_OVERRIDE_ACTIVE,
                LEGACY_META_STALE,
                LEGACY_META_DETECTED_ENTITY,
                LEGACY_CONTROL_AMBIGUOUS,
                LEGACY_ACTIVE_META_ENTITY,
                LEGACY_NOW_PLAYING_ENTITY,
                LEGACY_NOW_PLAYING_STATE,
                LEGACY_NOW_PLAYING_TITLE,
                LEGACY_META_CANDIDATES,
                LEGACY_CONTROL_HOST,
                LEGACY_CONTROL_TARGETS,
                LEGACY_SERVER_PROFILE,
                LEGACY_SERVER_PROFILE_EFFECTIVE,
                LEGACY_ROOMS_JSON,
                LEGACY_ROOMS_RAW,
                LEGACY_NO_CONTROL_CAPABLE_HOSTS,
            }
        )

        c._unsub_state_events = async_track_state_change_event(
            c.hass,
            sorted(watched_entities),
            c._handle_state_change,
        )
        c._unsub_global_state_events = c.hass.bus.async_listen(
            "state_changed",
            c._handle_global_state_change,
        )

    async def async_shutdown(self) -> None:
        """Detach listeners on unload."""
        c = self._coordinator
        if c._unsub_state_events is not None:
            c._unsub_state_events()
            c._unsub_state_events = None
        if c._unsub_global_state_events is not None:
            c._unsub_global_state_events()
            c._unsub_global_state_events = None
        if c._meta_stale_unlock_unsub is not None:
            c._meta_stale_unlock_unsub()
            c._meta_stale_unlock_unsub = None
        if c._deferred_snapshot_refresh_unsub is not None:
            c._deferred_snapshot_refresh_unsub()
            c._deferred_snapshot_refresh_unsub = None
        if c._startup_recovery_unsub is not None:
            c._startup_recovery_unsub()
            c._startup_recovery_unsub = None
        if c._startup_recovery_task is not None and not c._startup_recovery_task.done():
            c._startup_recovery_task.cancel()
        c._startup_recovery_task = None
        if c._no_control_feedback_hold_unsub is not None:
            c._no_control_feedback_hold_unsub()
            c._no_control_feedback_hold_unsub = None
        if c._no_control_feedback_post_heal_unsub is not None:
            c._no_control_feedback_post_heal_unsub()
            c._no_control_feedback_post_heal_unsub = None
