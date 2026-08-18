# Description: Shared payload-surface helpers for Spectra LS dict/list extraction and shape-safe reads.
# Version: 2026.08.17.2
# Last updated: 2026-08-17
# PARITY DIRECTIVE (until full cutover): behavior/contract edits here require same-slice two-track parity review
# and version-metadata review in runtime (`packages/` + `esphome/`) and component (`custom_components/spectra_ls/`) tracks.

from __future__ import annotations

from typing import Any


class PayloadSurfaceFabric:
    """Shape-safe helpers for repeated dict/list payload extraction patterns."""

    INVALID_TEXT_VALUES = frozenset({"", "none", "unknown", "unavailable", "null"})

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

    @staticmethod
    def metadata_prep(payload: Any) -> dict[str, Any]:
        return PayloadSurfaceFabric.dict_surface(payload, "metadata_prep_validation")

    @staticmethod
    def metadata_values(payload: Any) -> dict[str, Any]:
        metadata_prep = PayloadSurfaceFabric.metadata_prep(payload)
        return PayloadSurfaceFabric.as_dict(metadata_prep.get("values", {}))

    @staticmethod
    def metadata_checks(payload: Any) -> dict[str, Any]:
        metadata_prep = PayloadSurfaceFabric.metadata_prep(payload)
        return PayloadSurfaceFabric.as_dict(metadata_prep.get("checks", {}))

    @staticmethod
    def write_controls(payload: Any) -> dict[str, Any]:
        return PayloadSurfaceFabric.dict_surface(payload, "write_controls")

    @staticmethod
    def metadata_override_packet(payload: Any) -> dict[str, Any]:
        write_controls = PayloadSurfaceFabric.write_controls(payload)
        return PayloadSurfaceFabric.as_dict(write_controls.get("metadata_override", {}))

    @staticmethod
    def metadata_provider_packet(payload: Any) -> dict[str, Any]:
        write_controls = PayloadSurfaceFabric.write_controls(payload)
        return PayloadSurfaceFabric.as_dict(write_controls.get("metadata_provider_last", {}))

    @staticmethod
    def contract_text(value: Any) -> str:
        text = str(value or "").strip()
        if text.lower() in PayloadSurfaceFabric.INVALID_TEXT_VALUES:
            return ""
        return text

    @staticmethod
    def metadata_value_text(payload: Any, key: str) -> str:
        values = PayloadSurfaceFabric.metadata_values(payload)
        return PayloadSurfaceFabric.contract_text(values.get(key, ""))

    @staticmethod
    def metadata_override_entity(payload: Any) -> str:
        packet = PayloadSurfaceFabric.metadata_override_packet(payload)
        return PayloadSurfaceFabric.contract_text(packet.get("entity", ""))
