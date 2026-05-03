# Description: Refresh-validation fabric workflow for Spectra LS snapshot refresh and validation service orchestration extracted from coordinator.
# Version: 2026.05.03.3
# Last updated: 2026-05-03
# PARITY DIRECTIVE (until full cutover): behavior/contract edits here require same-slice two-track parity review
# and version-metadata review in runtime (`packages/` + `esphome/`) and component (`custom_components/spectra_ls/`) tracks.

from __future__ import annotations

import logging
from time import monotonic
from typing import Any

_LOGGER = logging.getLogger(__name__)


class RefreshValidationFabricWorkflow:
    """Owns coordinator refresh/validation orchestration lane extracted from coordinator."""

    def __init__(self, coordinator: Any) -> None:
        self._coordinator = coordinator
        self._snapshot_cache_payload: dict[str, Any] | None = None
        self._snapshot_cache_monotonic = 0.0
        self._snapshot_cache_ttl_s = 0.20

    def _publish_snapshot(self, *, allow_cached: bool = True) -> dict[str, Any]:
        """Build and publish a fresh snapshot payload."""
        c = self._coordinator
        now_mono = monotonic()
        cache_valid = (
            allow_cached
            and self._snapshot_cache_payload is not None
            and self._snapshot_cache_monotonic > 0
            and (now_mono - self._snapshot_cache_monotonic) <= self._snapshot_cache_ttl_s
        )

        if cache_valid:
            data = self._snapshot_cache_payload
        else:
            data = c._build_snapshot()
            self._snapshot_cache_payload = data
            self._snapshot_cache_monotonic = now_mono

        c.async_set_updated_data(data)
        return data

    def refresh_snapshot(self, *, force: bool = False) -> None:
        """Refresh snapshot with debounce-aware cadence control."""
        c = self._coordinator
        now_mono = monotonic()
        if (
            not force
            and c._last_snapshot_refresh_monotonic > 0
            and (now_mono - c._last_snapshot_refresh_monotonic) < c._snapshot_refresh_min_interval_s
        ):
            return

        c._last_snapshot_refresh_monotonic = now_mono
        self._publish_snapshot(allow_cached=False)

    def handle_deferred_snapshot_refresh(self, _now) -> None:
        """Run deferred refresh callback after cooldown window."""
        c = self._coordinator
        c._deferred_snapshot_refresh_unsub = None
        try:
            self.refresh_snapshot(force=True)
        except Exception:  # pragma: no cover - defensive callback hardening
            _LOGGER.exception("Failed deferred Spectra LS snapshot refresh")

    async def async_rebuild_registry(self) -> None:
        """Refresh parity data, including registry scaffold snapshot."""
        self._publish_snapshot(allow_cached=False)

    async def async_validate_contracts(self) -> None:
        """Refresh parity data and emit contract validation visibility in snapshot."""
        c = self._coordinator
        data = self._publish_snapshot(allow_cached=False)
        data["contract_validation"] = c._build_contract_validation()
        c.async_set_updated_data(data)
        self._snapshot_cache_payload = data
        self._snapshot_cache_monotonic = monotonic()

    async def async_dump_route_trace(self) -> None:
        """Refresh parity data so latest route trace appears in diagnostics."""
        self._publish_snapshot(allow_cached=True)

    async def async_validate_selection_handoff(self) -> None:
        """Refresh parity data and emit selection-handoff validation diagnostics."""
        self._publish_snapshot(allow_cached=True)

    async def async_validate_capability_profile(self) -> None:
        """Refresh parity data and emit F4-S01 capability/profile diagnostics."""
        self._publish_snapshot(allow_cached=True)

    async def async_validate_action_catalog(self) -> None:
        """Refresh parity data and emit F4-S02 action-catalog safety diagnostics."""
        self._publish_snapshot(allow_cached=True)

    async def async_validate_crossfade_balance(self) -> None:
        """Refresh parity data and emit F4-S03 crossfade/balance diagnostics."""
        self._publish_snapshot(allow_cached=True)

    async def async_validate_scheduler(self) -> None:
        """Refresh parity data and emit scheduler readiness/decision diagnostics."""
        self._publish_snapshot()

    async def async_update_data(self) -> dict[str, Any]:
        """Read legacy surfaces and compute parity snapshot."""
        c = self._coordinator
        return c._build_snapshot()
