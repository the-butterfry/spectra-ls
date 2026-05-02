# Description: Shared MA authority-contract packet builder for diagnostics, entity attributes, and service responses.
# Version: 2026.05.02.1
# Last updated: 2026-05-02

from __future__ import annotations

from typing import Any


def build_authority_contract_packet(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Build normalized MA authority packet from metadata-prep validation payload."""
    metadata_prep = (
        snapshot.get("metadata_prep_validation", {})
        if isinstance(snapshot.get("metadata_prep_validation", {}), dict)
        else {}
    )
    authority_mode = str(metadata_prep.get("authority_mode", "") or "")
    authority_gate_results = (
        metadata_prep.get("authority_gate_results", {})
        if isinstance(metadata_prep.get("authority_gate_results", {}), dict)
        else {}
    )
    blocking_reasons = metadata_prep.get("blocking_reasons", [])
    if not isinstance(blocking_reasons, list):
        blocking_reasons = []

    authority_reasons = [
        str(reason)
        for reason in blocking_reasons
        if isinstance(reason, str) and reason.startswith("ma_")
    ]

    return {
        "authority_mode": authority_mode,
        "authority_gate_results": authority_gate_results,
        "authority_reasons": authority_reasons,
    }
