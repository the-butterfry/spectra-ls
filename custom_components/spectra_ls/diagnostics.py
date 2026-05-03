# Description: Diagnostics export for Spectra LS read-only shadow parity, Phase 2 scaffold snapshots, and Phase 6 control-center settings/readiness visibility, including expanded shared MA authority-contract packet highlights.
# Version: 2026.05.03.3
# Last updated: 2026-05-03
# PARITY DIRECTIVE: Behavior/contract edits must include same-slice two-track parity review and version-metadata review (runtime + component).

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .authority_contract import build_authority_contract_packet
from .const import DOMAIN, LEGACY_SURFACES


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    shadow_snapshot = coordinator.data if isinstance(coordinator.data, dict) else {}

    source_states: dict[str, str] = {}
    for key, entity_id in LEGACY_SURFACES.items():
        state = hass.states.get(entity_id)
        source_states[key] = state.state if state is not None else "missing"

    authority_contract = build_authority_contract_packet(shadow_snapshot)
    host_cutover_gate = (
        shadow_snapshot.get("host_control_cutover_gate", {})
        if isinstance(shadow_snapshot.get("host_control_cutover_gate", {}), dict)
        else {}
    )
    gate_blockers = host_cutover_gate.get("gate_blockers", [])
    activation_blockers = host_cutover_gate.get("activation_blockers", [])

    return {
        "entry_id": entry.entry_id,
        "control_center_settings": coordinator.data.get("write_controls", {}).get("control_center_settings", {}),
        "control_center_validation": coordinator.data.get("control_center_validation", {}),
        "control_center_last_attempt": coordinator.data.get("write_controls", {}).get("control_center_last_attempt", {}),
        "authority_contract": authority_contract,
        "authority_contract_highlights": {
            "schema_version": authority_contract.get("schema_version", ""),
            "packet_generated_at": authority_contract.get("packet_generated_at", ""),
            "authority_contract_ready": authority_contract.get("authority_contract_ready", False),
            "authority_contract_blocker_count": authority_contract.get("authority_contract_blocker_count", 0),
            "cutover_prep_complete": authority_contract.get("cutover_prep_complete", False),
            "cutover_prep_verdict": authority_contract.get("cutover_prep_verdict", ""),
            "cutover_prep_blocker_count": authority_contract.get("cutover_prep_blocker_count", 0),
            "required_proof_checkpoints_present": authority_contract.get("required_proof_checkpoints_present", False),
            "proof_checkpoint_count": authority_contract.get("proof_checkpoint_count", 0),
            "bridge_status": authority_contract.get("bridge_status", ""),
            "trial_status": authority_contract.get("trial_status", ""),
        },
        "host_cutover_gate": host_cutover_gate,
        "host_cutover_gate_highlights": {
            "schema_version": host_cutover_gate.get("schema_version", ""),
            "status": host_cutover_gate.get("status", "blocked"),
            "ready_for_cutover": host_cutover_gate.get("ready_for_cutover", False),
            "ready_for_authoritative_activation": host_cutover_gate.get(
                "ready_for_authoritative_activation", False
            ),
            "authority_mode": host_cutover_gate.get("authority_mode", "legacy"),
            "authority_source_mode": host_cutover_gate.get("authority_source_mode", "legacy"),
            "route_decision": host_cutover_gate.get("route_decision", ""),
            "resolved_control_path": host_cutover_gate.get("resolved_control_path", ""),
            "gate_blocker_count": len(gate_blockers) if isinstance(gate_blockers, list) else 0,
            "activation_blocker_count": len(activation_blockers) if isinstance(activation_blockers, list) else 0,
        },
        "source_states": source_states,
        "shadow_snapshot": shadow_snapshot,
    }
