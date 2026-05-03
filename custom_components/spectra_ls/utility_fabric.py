# Description: Utility-fabric workflow for Spectra LS coordinator helper/state parsing and scoring seams extracted from coordinator.
# Version: 2026.05.03.2
# Last updated: 2026-05-03
# PARITY DIRECTIVE (until full cutover): behavior/contract edits here require same-slice two-track parity review
# and version-metadata review in runtime (`packages/` + `esphome/`) and component (`custom_components/spectra_ls/`) tracks.

from __future__ import annotations

from datetime import UTC, datetime
import json
from typing import Any


class UtilityFabricWorkflow:
    """Owns coordinator utility/helper seams extracted from coordinator."""

    def __init__(self, coordinator: Any) -> None:
        self._coordinator = coordinator

    @staticmethod
    def normalize_state(state_value: str) -> str:
        return (state_value or "").strip().lower()

    @staticmethod
    def parse_jsonish_payload(raw: Any) -> Any:
        if isinstance(raw, (list, dict)):
            return raw
        if isinstance(raw, str):
            trimmed = raw.strip()
            if not trimmed:
                return None
            if not (trimmed.startswith("[") or trimmed.startswith("{")):
                return None
            try:
                return json.loads(trimmed)
            except json.JSONDecodeError:
                return None
        return None

    def extract_payload_list(self, raw: Any, keys: tuple[str, ...]) -> list[Any]:
        """Normalize list-like payloads from direct/raw/jsonish structures using candidate keys."""
        payload = self.parse_jsonish_payload(raw)
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            for key in keys:
                candidate = payload.get(key, [])
                if isinstance(candidate, list):
                    return candidate
        return []

    def read_float_helper(self, entity_id: str, default: float) -> float:
        c = self._coordinator
        state = c.hass.states.get(entity_id)
        if state is None:
            return float(default)
        raw = str(state.state or "").strip().lower()
        if raw in {"", "unknown", "unavailable", "none"}:
            return float(default)
        try:
            return float(state.state)
        except (TypeError, ValueError):
            return float(default)

    @staticmethod
    def availability_points(quality: str) -> int:
        q = str(quality or "").strip().lower()
        if q == "fresh":
            return 15
        if q == "warm":
            return 8
        if q == "stale":
            return 2
        return 0

    @staticmethod
    def empirical_bonus(overlay: dict[str, Any]) -> float:
        if not isinstance(overlay, dict) or len(overlay) == 0:
            return 0.0

        bonus = 0.0
        score = overlay.get("score")
        if isinstance(score, (int, float)):
            bonus += max(min(float(score) * 0.2, 20.0), -20.0)

        success_rate = overlay.get("success_rate")
        if isinstance(success_rate, (int, float)):
            bonus += max(min(float(success_rate), 1.0), 0.0) * 20.0

        confidence = overlay.get("confidence")
        if isinstance(confidence, (int, float)):
            bonus += max(min(float(confidence), 1.0), 0.0) * 10.0

        latency_ms = overlay.get("latency_ms")
        if isinstance(latency_ms, (int, float)):
            if float(latency_ms) > 250:
                bonus -= min((float(latency_ms) - 250.0) / 50.0, 10.0)

        return round(bonus, 2)

    @staticmethod
    def is_resolved_state(raw_state: str) -> bool:
        normalized = (raw_state or "").strip().lower()
        return normalized not in {"", "none", "unknown", "unavailable", "missing"}

    @staticmethod
    def timestamp_age_seconds(raw_value: Any) -> float | None:
        if raw_value in (None, "", "none", "unknown", "unavailable"):
            return None

        parsed: datetime | None = None
        if isinstance(raw_value, datetime):
            parsed = raw_value
        elif isinstance(raw_value, str):
            cleaned = raw_value.strip()
            if cleaned.endswith("Z"):
                cleaned = f"{cleaned[:-1]}+00:00"
            try:
                parsed = datetime.fromisoformat(cleaned)
            except ValueError:
                parsed = None

        if parsed is None:
            return None

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)

        age_s = (datetime.now(UTC) - parsed.astimezone(UTC)).total_seconds()
        return max(age_s, 0.0)

    def snapshot_for_entity(self, entity_id: str, *, as_bool: bool = False) -> dict[str, Any]:
        c = self._coordinator
        state = c.hass.states.get(entity_id)
        if state is None:
            return {
                "value": False if as_bool else "",
                "state": "missing",
                "available": False,
            }

        normalized = self.normalize_state(state.state)
        available = normalized not in {"", "unknown", "unavailable", "none"}

        if as_bool:
            bool_value = normalized in {"on", "true", "1", "yes"}
            return {
                "value": bool_value,
                "state": state.state,
                "available": available,
            }

        return {
            "value": state.state if available else "",
            "state": state.state,
            "available": available,
        }

    @staticmethod
    def normalize_write_authority(mode: str, allowed_modes: set[str], default_mode: str) -> str:
        normalized = (mode or "").strip().lower()
        return normalized if normalized in allowed_modes else default_mode
