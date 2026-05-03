# Description: Shared MA authority-contract packet builder for diagnostics, entity attributes, and service responses including cutover-prep and proof-summary fields with packet metadata.
# Version: 2026.05.03.6
# Last updated: 2026-05-03
# PARITY DIRECTIVE: Behavior/contract edits must include same-slice two-track parity review and version-metadata review (runtime + component).

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .payload_surface_fabric import PayloadSurfaceFabric


_AUTHORITY_PACKET_CACHE: dict[str, dict[str, Any]] = {}
_AUTHORITY_PACKET_CACHE_MAX = 64


def _cache_authority_packet(cache_key: str, packet: dict[str, Any]) -> None:
    _AUTHORITY_PACKET_CACHE[cache_key] = packet
    while len(_AUTHORITY_PACKET_CACHE) > _AUTHORITY_PACKET_CACHE_MAX:
        oldest_key = next(iter(_AUTHORITY_PACKET_CACHE), None)
        if oldest_key is None:
            break
        _AUTHORITY_PACKET_CACHE.pop(oldest_key, None)


def build_authority_contract_packet(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Build normalized MA authority packet from metadata-prep validation payload."""
    cache_key = str(snapshot.get("captured_at", "") or "")
    if cache_key:
        cached = _AUTHORITY_PACKET_CACHE.get(cache_key)
        if isinstance(cached, dict):
            return dict(cached)

    metadata_prep = PayloadSurfaceFabric.dict_surface(snapshot, "metadata_prep_validation")
    authority_mode = str(metadata_prep.get("authority_mode", "") or "")
    metadata_authority_owner = str(metadata_prep.get("metadata_authority_owner", "") or "")
    metadata_cutover_active = bool(metadata_prep.get("metadata_cutover_active", False))
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

    cutover_prep_validation = PayloadSurfaceFabric.dict_surface(snapshot, "cutover_prep_validation")
    cutover_prep_complete = bool(cutover_prep_validation.get("cutover_prep_complete", False))

    cutover_prep_verdict = str(cutover_prep_validation.get("verdict", "") or "")
    cutover_prep_blocking_reasons = cutover_prep_validation.get("blocking_reasons", [])
    if not isinstance(cutover_prep_blocking_reasons, list):
        cutover_prep_blocking_reasons = []
    cutover_prep_blocking_reasons = [
        str(reason) for reason in cutover_prep_blocking_reasons if isinstance(reason, str)
    ]

    metadata_bridge_validation = PayloadSurfaceFabric.dict_surface(snapshot, "metadata_bridge_validation")

    write_controls = PayloadSurfaceFabric.dict_surface(snapshot, "write_controls")
    bridge_attempt = PayloadSurfaceFabric.dict_surface(write_controls, "metadata_bridge_last_attempt")
    cutover_proof = PayloadSurfaceFabric.dict_surface(bridge_attempt, "cutover_proof")
    pre_window = cutover_proof.get("pre_window") if isinstance(cutover_proof.get("pre_window"), dict) else None
    in_window = cutover_proof.get("in_window") if isinstance(cutover_proof.get("in_window"), dict) else None
    post_window = cutover_proof.get("post_window") if isinstance(cutover_proof.get("post_window"), dict) else None

    proof_checkpoint_presence = {
        "pre_window": isinstance(pre_window, dict),
        "in_window": isinstance(in_window, dict),
        "post_window": isinstance(post_window, dict),
    }
    proof_in_window_assertions = {
        "metadata_cutover_active": bool(in_window.get("metadata_cutover_active", False))
        if isinstance(in_window, dict)
        else False,
        "metadata_owner_component": str(in_window.get("metadata_authority_owner", "") or "")
        == "component_contract_surfaces"
        if isinstance(in_window, dict)
        else False,
    }

    cutover_prep_checks = cutover_prep_validation.get("checks", [])
    if not isinstance(cutover_prep_checks, dict):
        cutover_prep_checks = {}

    required_proof_checkpoints_present = all(bool(present) for present in proof_checkpoint_presence.values())
    authority_contract_blocking_reasons: list[str] = []
    if not cutover_prep_complete:
        authority_contract_blocking_reasons.append("cutover_prep_incomplete")
    if not required_proof_checkpoints_present:
        authority_contract_blocking_reasons.append("proof_checkpoint_missing")
    if not bool(proof_in_window_assertions.get("metadata_cutover_active", False)):
        authority_contract_blocking_reasons.append("proof_in_window_cutover_inactive")
    if not bool(proof_in_window_assertions.get("metadata_owner_component", False)):
        authority_contract_blocking_reasons.append("proof_in_window_owner_not_component")

    authority_contract_ready = len(authority_contract_blocking_reasons) == 0

    packet_generated_at = datetime.now(UTC).isoformat()

    packet = {
        "schema_version": "authority_contract.v2",
        "packet_generated_at": packet_generated_at,
        "authority_mode": authority_mode,
        "metadata_authority_owner": metadata_authority_owner,
        "metadata_cutover_active": metadata_cutover_active,
        "cutover_prep_complete": cutover_prep_complete,
        "cutover_prep_verdict": cutover_prep_verdict,
        "cutover_prep_blocking_reasons": cutover_prep_blocking_reasons,
        "cutover_prep_blocker_count": len(cutover_prep_blocking_reasons),
        "cutover_prep_check_count": len(cutover_prep_checks),
        "cutover_prep_passed_check_count": sum(
            1 for passed in cutover_prep_checks.values() if bool(passed)
        ),
        "authority_contract_ready": authority_contract_ready,
        "authority_contract_blocking_reasons": authority_contract_blocking_reasons,
        "authority_contract_blocker_count": len(authority_contract_blocking_reasons),
        "bridge_status": str(metadata_bridge_validation.get("bridge_status", "") or ""),
        "trial_status": str(metadata_bridge_validation.get("trial_status", "") or ""),
        "proof_checkpoint_presence": proof_checkpoint_presence,
        "required_proof_checkpoints_present": required_proof_checkpoints_present,
        "proof_checkpoint_count": sum(1 for present in proof_checkpoint_presence.values() if bool(present)),
        "proof_in_window_assertions": proof_in_window_assertions,
        "authority_gate_results": authority_gate_results,
        "authority_reasons": authority_reasons,
    }

    if cache_key:
        _cache_authority_packet(cache_key, packet)

    return dict(packet)
