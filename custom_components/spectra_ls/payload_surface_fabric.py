# Description: Shared payload-surface helpers for Spectra LS dict/list extraction and shape-safe reads.
# Version: 2026.05.03.1
# Last updated: 2026-05-03
# PARITY DIRECTIVE (until full cutover): behavior/contract edits here require same-slice two-track parity review
# and version-metadata review in runtime (`packages/` + `esphome/`) and component (`custom_components/spectra_ls/`) tracks.

from __future__ import annotations

from typing import Any


class PayloadSurfaceFabric:
    """Shape-safe helpers for repeated dict/list payload extraction patterns."""

    @staticmethod
    def dict_surface(payload: Any, key: str) -> dict[str, Any]:
        if not isinstance(payload, dict):
            return {}
        candidate = payload.get(key, {})
        return candidate if isinstance(candidate, dict) else {}

    @staticmethod
    def list_surface(payload: Any, key: str) -> list[Any]:
        if not isinstance(payload, dict):
            return []
        candidate = payload.get(key, [])
        return candidate if isinstance(candidate, list) else []

    @staticmethod
    def as_dict(value: Any) -> dict[str, Any]:
        return value if isinstance(value, dict) else {}

    @staticmethod
    def as_list(value: Any) -> list[Any]:
        return value if isinstance(value, list) else []
