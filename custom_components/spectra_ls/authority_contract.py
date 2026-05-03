# Description: Shared MA authority-contract packet builder for diagnostics, entity attributes, and service responses including cutover-prep and proof-summary fields with packet metadata.
# Version: 2026.05.03.5
# Last updated: 2026-05-03
# PARITY DIRECTIVE: Behavior/contract edits must include same-slice two-track parity review and version-metadata review (runtime + component).

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


def build_authority_contract_packet(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Build normalized MA authority packet from metadata-prep validation payload."""
    metadata_prep = (
        snapshot.get("metadata_prep_validation", {})
        if isinstance(snapshot.get("metadata_prep_validation", {}), dict)
        else {}
    )
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

    cutover_prep_validation = (
        snapshot.get("cutover_prep_validation", {})
        if isinstance(snapshot.get("cutover_prep_validation", {}), dict)
        else {}
    )
    cutover_prep_complete = bool(cutover_prep_validation.get("cutover_prep_complete", False))

    cutover_prep_verdict = str(cutover_prep_validation.get("verdict", "") or "")
    cutover_prep_blocking_reasons = cutover_prep_validation.get("blocking_reasons", [])
    if not isinstance(cutover_prep_blocking_reasons, list):
        cutover_prep_blocking_reasons = []
    cutover_prep_blocking_reasons = [
        str(reason) for reason in cutover_prep_blocking_reasons if isinstance(reason, str)
    ]

    metadata_bridge_validation = (
        snapshot.get("metadata_bridge_validation", {})
        if isinstance(snapshot.get("metadata_bridge_validation", {}), dict)
        else {}
    )

    write_controls = (
        snapshot.get("write_controls", {}) if isinstance(snapshot.get("write_controls", {}), dict) else {}
    )
    bridge_attempt = (
        write_controls.get("metadata_bridge_last_attempt", {})
        if isinstance(write_controls.get("metadata_bridge_last_attempt", {}), dict)
        else {}
    )
    cutover_proof = (
        bridge_attempt.get("cutover_proof", {})
        if isinstance(bridge_attempt.get("cutover_proof", {}), dict)
        else {}
    )
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

    return {
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
