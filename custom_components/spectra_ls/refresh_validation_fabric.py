# Description: Refresh-validation fabric workflow for Spectra LS snapshot refresh and validation service orchestration extracted from coordinator.
# Version: 2026.08.18.1
# Last updated: 2026-08-18
# PARITY DIRECTIVE (until full cutover): behavior/contract edits here require same-slice two-track parity review
# and version-metadata review in runtime (`packages/` + `esphome/`) and component (`custom_components/spectra_ls/`) tracks.

from __future__ import annotations

from datetime import timedelta
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

    def _publish_snapshot(self, *, allow_cached: bool = True, force_emit: bool = False) -> dict[str, Any]:
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

        signature = c._stable_payload_signature(data)
        playback_active = c._is_payload_playback_active(data)
        diagnostics_enabled = c._diagnostics_refresh_enabled()
        min_interval = (
            c._publish_min_interval_enabled_s
            if diagnostics_enabled
            else (
                c._publish_min_interval_disabled_active_s
                if playback_active
                else c._publish_min_interval_disabled_s
            )
        )

        if not force_emit:
            if signature == c._publish_signature_last and c._publish_signature_last:
                return c.data if isinstance(getattr(c, "data", None), dict) else data

            if c._publish_monotonic_last > 0 and (now_mono - c._publish_monotonic_last) < min_interval:
                return c.data if isinstance(getattr(c, "data", None), dict) else data

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
        self._publish_snapshot(allow_cached=False, force_emit=force)

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
        self._publish_snapshot(allow_cached=False, force_emit=True)

    async def _async_refresh_validation_surface(self, *, allow_cached: bool = True) -> None:
        """Refresh parity/validation surfaces using canonical publish policy."""
        self._publish_snapshot(allow_cached=allow_cached)

    async def _async_rebuild_contract_surface(self) -> None:
        """Refresh and explicitly rebuild contract validation payload surface."""
        c = self._coordinator
        data = self._publish_snapshot(allow_cached=False, force_emit=True)
        data["contract_validation"] = c._build_contract_validation()
        c.async_set_updated_data(data)
        self._snapshot_cache_payload = data
        self._snapshot_cache_monotonic = monotonic()

    async def async_validate_contracts(self) -> None:
        """Refresh parity data and emit contract validation visibility in snapshot."""
        await self._async_rebuild_contract_surface()

    async def async_dump_route_trace(self) -> None:
        """Refresh parity data so latest route trace appears in diagnostics."""
        await self._async_refresh_validation_surface(allow_cached=True)

    async def async_validate_selection_handoff(self) -> None:
        """Refresh parity data and emit selection-handoff validation diagnostics."""
        await self._async_refresh_validation_surface(allow_cached=True)

    async def async_validate_capability_profile(self) -> None:
        """Refresh parity data and emit F4-S01 capability/profile diagnostics."""
        await self._async_refresh_validation_surface(allow_cached=True)

    async def async_validate_action_catalog(self) -> None:
        """Refresh parity data and emit F4-S02 action-catalog safety diagnostics."""
        await self._async_refresh_validation_surface(allow_cached=True)

    async def async_validate_crossfade_balance(self) -> None:
        """Refresh parity data and emit F4-S03 crossfade/balance diagnostics."""
        await self._async_refresh_validation_surface(allow_cached=True)

    async def async_validate_scheduler(self) -> None:
        """Refresh parity data and emit scheduler readiness/decision diagnostics."""
        await self._async_refresh_validation_surface()

    async def async_update_data(self) -> dict[str, Any]:
        """Read legacy surfaces and compute parity snapshot."""
        c = self._coordinator
        data = c._build_snapshot()

        diagnostics_enabled = c._diagnostics_refresh_enabled()
        playback_active = c._is_payload_playback_active(data)

        # Dynamic poll cadence: keep diagnostics responsive only when useful,
        # and slow idle polling aggressively to prevent background churn.
        if diagnostics_enabled:
            desired_interval_s = 5.0 if playback_active else 15.0
        else:
            desired_interval_s = 10.0 if playback_active else 60.0
        current_interval = getattr(c, "update_interval", None)
        current_interval_s = (
            float(current_interval.total_seconds())
            if isinstance(current_interval, timedelta)
            else None
        )
        if current_interval_s is None or abs(current_interval_s - desired_interval_s) >= 0.5:
            c.update_interval = timedelta(seconds=desired_interval_s)
        self._snapshot_cache_payload = data
        self._snapshot_cache_monotonic = monotonic()
        return data
