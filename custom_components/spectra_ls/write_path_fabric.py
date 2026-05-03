# Description: Shared write-path helper/guard workflow for Spectra LS deduped helper-state parsing, write-guard checks, and attempt bookkeeping.
# Version: 2026.05.03.1
# Last updated: 2026-05-03
# PARITY DIRECTIVE (until full cutover): behavior/contract edits here require same-slice two-track parity review
# and version-metadata review in runtime (`packages/` + `esphome/`) and component (`custom_components/spectra_ls/`) tracks.

from __future__ import annotations

from time import monotonic
from typing import Any


class WritePathFabric:
    """Shared helpers for write-lane dedupe and guard consistency."""

    @staticmethod
    def normalize_options(options_attr: Any) -> list[str]:
        if not isinstance(options_attr, list):
            return []
        return [
            str(item).strip()
            for item in options_attr
            if isinstance(item, str) and str(item).strip()
        ]

    @classmethod
    def helper_state_packet(cls, hass: Any, entity_id: str) -> dict[str, Any]:
        state = hass.states.get(entity_id)
        current = str(state.state if state is not None else "").strip()
        options = cls.normalize_options(state.attributes.get("options", []) if state is not None else [])
        return {
            "state": state,
            "exists": state is not None,
            "current": current,
            "options": options,
        }

    @staticmethod
    def correlation_id(prefix: str, correlation_id: str | None) -> str:
        raw = (correlation_id or "").strip()
        return raw if raw else f"{prefix}-{monotonic():.6f}".replace(".", "")

    @staticmethod
    def apply_standard_write_guards(
        coordinator: Any,
        result: dict[str, Any],
        *,
        force: bool,
        dry_run: bool,
        authority_required: str | None,
        authority_block_reason: str,
    ) -> None:
        if result.get("status") != "pending":
            return

        if authority_required and coordinator._write_authority_mode != authority_required and not dry_run:
            result["status"] = "blocked_authority"
            result["reason"] = authority_block_reason
            return

        if coordinator._write_in_progress and not force:
            result["status"] = "blocked_reentrancy"
            result["reason"] = "A prior write attempt is still in progress"
            return

        if not force and not dry_run and coordinator._last_write_monotonic > 0:
            elapsed = monotonic() - coordinator._last_write_monotonic
            if elapsed < coordinator._write_debounce_s:
                result["status"] = "blocked_debounce"
                result["reason"] = "Debounce guard active"
                result["elapsed_s"] = round(elapsed, 3)
                result["debounce_s"] = coordinator._write_debounce_s

    @staticmethod
    def mark_write_touch(coordinator: Any) -> None:
        coordinator._last_write_monotonic = monotonic()

    @staticmethod
    def stamp_last_write_attempt(
        coordinator: Any,
        *,
        result: dict[str, Any],
        source: str,
        correlation_id: str,
        active_target: str,
    ) -> None:
        coordinator._last_write_attempt = {
            "status": result.get("status", "unknown"),
            "timestamp": result.get("completed_at") or result.get("timestamp"),
            "authority_mode": coordinator._write_authority_mode,
            "reason": result.get("reason", ""),
            "correlation_id": correlation_id,
            "source": source,
            "active_target": active_target,
        }
