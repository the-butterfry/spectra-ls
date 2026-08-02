# Description: Refresh-validation fabric workflow for Spectra LS snapshot refresh and validation service orchestration extracted from coordinator.
# Version: 2026.08.02.6
# Last updated: 2026-08-02
# PARITY DIRECTIVE (until full cutover): behavior/contract edits here require same-slice two-track parity review
# and version-metadata review in runtime (`packages/` + `esphome/`) and component (`custom_components/spectra_ls/`) tracks.

from __future__ import annotations

from datetime import timedelta
import json
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
        self._last_publish_signature = ""
        self._last_publish_monotonic = 0.0
        self._last_operational_fingerprint = ""
        self._active_publish_min_interval_s = 1.25
        self._idle_publish_min_interval_s = 20.0
        self._diagnostics_disabled_publish_min_interval_active_s = 10.0
        self._diagnostics_disabled_publish_min_interval_idle_s = 75.0
        self._diagnostics_disabled_heartbeat_active_s = 10.0
        self._diagnostics_disabled_heartbeat_s = 180.0
        self._diagnostics_toggle_helper_entity = "input_boolean.spectra_ls_component_diagnostics_enabled"

    @staticmethod
    def _is_invalid_text(value: Any) -> bool:
        text = str(value or "").strip().lower()
        return text in {"", "none", "unknown", "unavailable", "null"}

    def _diagnostics_refresh_enabled(self) -> bool:
        """Return whether high-frequency diagnostics refresh is enabled.

        Optional operator gate: input_boolean.spectra_ls_component_diagnostics_enabled
        - missing helper -> defaults to disabled (fail-closed for churn)
        - off/false/0  -> diagnostics-refresh throttled mode
        """
        c = self._coordinator
        state = c.hass.states.get(self._diagnostics_toggle_helper_entity)
        if state is None:
            return False
        normalized = c._normalize_state(getattr(state, "state", ""))
        return normalized in {"on", "true", "1"}

    def _is_playback_active(self, data: dict[str, Any]) -> bool:
        """Return True when current snapshot indicates active playback context."""
        metadata_prep = data.get("metadata_prep_validation", {})
        values = metadata_prep.get("values", {}) if isinstance(metadata_prep, dict) else {}
        now_playing_state = str(values.get("now_playing_state", "") or "").strip().lower()
        if now_playing_state in {"playing", "buffering"}:
            return True

        route_trace = data.get("route_trace", {}) if isinstance(data.get("route_trace", {}), dict) else {}
        active_target = str(route_trace.get("active_target", "") or "").strip()
        if self._is_invalid_text(active_target):
            return False

        target_state = self._coordinator.hass.states.get(active_target)
        normalized_target_state = self._coordinator._normalize_state(
            target_state.state if target_state is not None else ""
        )
        return normalized_target_state in {"playing", "buffering"}

    def _stable_signature(self, payload: Any) -> str:
        """Build deterministic signature ignoring volatile telemetry timestamp fields."""
        volatile_keys = {
            "captured_at",
            "updated_at",
            "requested_at",
            "completed_at",
            "timestamp",
            "last_changed",
            "last_updated",
        }

        def _strip(value: Any) -> Any:
            if isinstance(value, dict):
                out: dict[str, Any] = {}
                for key, item in value.items():
                    key_text = str(key)
                    lowered = key_text.lower()
                    if lowered in volatile_keys:
                        continue
                    if lowered.endswith("_at") or lowered.endswith("_ts") or lowered.endswith("_timestamp"):
                        continue
                    if lowered.endswith("_age_s") or lowered.endswith("_age_ms"):
                        continue
                    out[key_text] = _strip(item)
                return out
            if isinstance(value, list):
                return [_strip(item) for item in value]
            return value

        try:
            return json.dumps(_strip(payload), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        except TypeError:
            return repr(_strip(payload))

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

        signature = self._stable_signature(data)
        playback_active = self._is_playback_active(data)
        diagnostics_enabled = self._diagnostics_refresh_enabled()
        min_interval = self._active_publish_min_interval_s if playback_active else self._idle_publish_min_interval_s
        if not diagnostics_enabled:
            min_interval = max(
                min_interval,
                self._diagnostics_disabled_publish_min_interval_active_s
                if playback_active
                else self._diagnostics_disabled_publish_min_interval_idle_s,
            )

        if not force_emit:
            if signature == self._last_publish_signature and self._last_publish_signature:
                return c.data if isinstance(getattr(c, "data", None), dict) else data

            if self._last_publish_monotonic > 0 and (now_mono - self._last_publish_monotonic) < min_interval:
                return c.data if isinstance(getattr(c, "data", None), dict) else data

        c.async_set_updated_data(data)
        self._last_publish_signature = signature
        self._last_publish_monotonic = now_mono
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

    async def async_validate_contracts(self) -> None:
        """Refresh parity data and emit contract validation visibility in snapshot."""
        c = self._coordinator
        data = self._publish_snapshot(allow_cached=False, force_emit=True)
        data["contract_validation"] = c._build_contract_validation()
        c.async_set_updated_data(data)
        self._last_publish_signature = self._stable_signature(data)
        self._last_publish_monotonic = monotonic()
        self._snapshot_cache_payload = data
        self._snapshot_cache_monotonic = self._last_publish_monotonic

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
        now_mono = monotonic()
        data = c._build_snapshot()

        signature = self._stable_signature(data)
        diagnostics_enabled = self._diagnostics_refresh_enabled()
        playback_active = self._is_playback_active(data)

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

        min_interval = self._active_publish_min_interval_s if playback_active else self._idle_publish_min_interval_s

        coordinator_disabled_floor = float(
            getattr(
                c,
                "_publish_min_interval_disabled_active_s" if playback_active else "_publish_min_interval_disabled_s",
                self._diagnostics_disabled_publish_min_interval_active_s
                if playback_active
                else self._diagnostics_disabled_publish_min_interval_idle_s,
            )
        )
        if not diagnostics_enabled:
            min_interval = max(min_interval, coordinator_disabled_floor)

        last_data = c.data if isinstance(getattr(c, "data", None), dict) else None

        operational_fingerprint = ""
        if hasattr(c, "_operational_fingerprint"):
            try:
                operational_fingerprint = str(c._operational_fingerprint(data) or "")
            except Exception:  # pragma: no cover - defensive fallback
                operational_fingerprint = ""

        if last_data is not None:
            if self._last_publish_signature and signature == self._last_publish_signature:
                if diagnostics_enabled or not playback_active:
                    return last_data

                active_heartbeat_s = float(
                    getattr(c, "_publish_heartbeat_disabled_active_s", self._diagnostics_disabled_heartbeat_active_s)
                )
                if self._last_publish_monotonic > 0 and (now_mono - self._last_publish_monotonic) < active_heartbeat_s:
                    return last_data

            if self._last_publish_monotonic > 0 and (now_mono - self._last_publish_monotonic) < min_interval:
                return last_data

            if not diagnostics_enabled and operational_fingerprint:
                if (
                    self._last_operational_fingerprint
                    and operational_fingerprint == self._last_operational_fingerprint
                ):
                    heartbeat_s = float(
                        getattr(
                            c,
                            "_publish_heartbeat_disabled_active_s" if playback_active else "_publish_heartbeat_disabled_s",
                            self._diagnostics_disabled_heartbeat_active_s
                            if playback_active
                            else self._diagnostics_disabled_heartbeat_s,
                        )
                    )
                    if self._last_publish_monotonic > 0 and (now_mono - self._last_publish_monotonic) < heartbeat_s:
                        return last_data

        self._last_publish_signature = signature
        self._last_publish_monotonic = now_mono
        self._last_operational_fingerprint = operational_fingerprint
        self._snapshot_cache_payload = data
        self._snapshot_cache_monotonic = now_mono
        return data
