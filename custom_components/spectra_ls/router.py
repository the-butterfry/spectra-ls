# Description: Router scaffold helpers for Spectra LS Phase 2 read-only route-trace visibility with deterministic resolved-path decisions.
# Version: 2026.04.19.2
# Last updated: 2026-04-19

from __future__ import annotations

from typing import Any


def build_route_trace(active_target: str, active_control_path: str, registry: dict[str, Any]) -> dict[str, Any]:
    """Build a read-only route trace from active surfaces and registry scaffold."""
    entries: dict[str, dict[str, Any]] = registry.get("entries", {})
    target_key = (active_target or "").strip()
    normalized_path = (active_control_path or "").strip()

    selected = entries.get(target_key)
    selected_control_path = (
        str(selected.get("control_path", "")).strip().lower() if isinstance(selected, dict) else ""
    )
    resolved_path = normalized_path or selected_control_path

    if not target_key:
        decision = "defer_no_target"
        reason = "Active target is empty"
    elif selected is None:
        decision = "defer_unknown_target"
        reason = "Active target is not present in registry snapshot"
    elif resolved_path != "linkplay_tcp":
        decision = "defer_unsupported_path"
        reason = "Only linkplay_tcp is mapped in current Phase 2 scaffold"
    elif not selected.get("control_capable", False):
        decision = "defer_not_capable"
        reason = "Target does not advertise control_capable in registry snapshot"
    else:
        decision = "route_linkplay_tcp"
        reason = "Target/path are supported by read-only scaffold mapping"

    return {
        "active_target": target_key,
        "active_control_path": normalized_path,
        "resolved_control_path": resolved_path,
        "selected_control_path": selected_control_path,
        "decision": decision,
        "reason": reason,
        "selected_target": selected,
        "registry_target_count": int(registry.get("target_count", 0) or 0),
    }
