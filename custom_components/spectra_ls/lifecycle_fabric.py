# Description: Lifecycle-fabric workflow for Spectra LS coordinator listener setup/shutdown orchestration extracted from coordinator.
# Version: 2026.08.01.5
# Last updated: 2026-08-01
# PARITY DIRECTIVE (until full cutover): behavior/contract edits here require same-slice two-track parity review
# and version-metadata review in runtime (`packages/` + `esphome/`) and component (`custom_components/spectra_ls/`) tracks.

from __future__ import annotations

from typing import Any


class LifecycleFabricWorkflow:
    """Owns coordinator lifecycle listener orchestration extracted from coordinator."""

    def __init__(self, coordinator: Any) -> None:
        self._coordinator = coordinator

    async def async_setup(self) -> None:
        """Initialize data and state listeners."""
        c = self._coordinator
        await c.async_refresh()

        # Churn hardening:
        # Component self-observing listeners can create feedback loops where output
        # sensor writes trigger additional refreshes. Keep listener fan-in disabled
        # and rely on bounded coordinator polling + explicit service-triggered refresh.
        c._unsub_state_events = None
        c._unsub_global_state_events = None

    async def async_shutdown(self) -> None:
        """Detach listeners on unload."""
        c = self._coordinator
        if c._unsub_state_events is not None:
            c._unsub_state_events()
            c._unsub_state_events = None
        if c._unsub_global_state_events is not None:
            c._unsub_global_state_events()
            c._unsub_global_state_events = None
        if c._deferred_snapshot_refresh_unsub is not None:
            c._deferred_snapshot_refresh_unsub()
            c._deferred_snapshot_refresh_unsub = None
        if c._startup_recovery_unsub is not None:
            c._startup_recovery_unsub()
            c._startup_recovery_unsub = None
        if c._startup_recovery_task is not None and not c._startup_recovery_task.done():
            c._startup_recovery_task.cancel()
        c._startup_recovery_task = None
