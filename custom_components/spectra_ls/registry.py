# Description: Registry scaffold helpers for Spectra LS Phase 2 read-only target normalization and deterministic payload parsing.
# Version: 2026.04.23.1
# Last updated: 2026-04-23
# PARITY DIRECTIVE (until full cutover): runtime-affecting contract behavior changed here must be mirrored/reconciled in `packages/` + `esphome/`
# in the same slice, with explicit implemented/shim/defer two-track disposition and version-metadata review.

from __future__ import annotations

import json
from typing import Any

from homeassistant.core import HomeAssistant


def _split_csv(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def _load_json_maybe(value: str) -> Any:
    raw = (value or "").strip()
    if not raw:
        return None
    if not (raw.startswith("{") or raw.startswith("[")):
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def _extract_rooms(raw: Any) -> list[dict[str, Any]]:
    if isinstance(raw, list):
        return [item for item in raw if isinstance(item, dict)]
    if isinstance(raw, dict):
        rooms = raw.get("rooms")
        if isinstance(rooms, list):
            return [item for item in rooms if isinstance(item, dict)]
    return []


def _extract_strings(raw: Any) -> list[str]:
    if isinstance(raw, list):
        return [str(item).strip() for item in raw if isinstance(item, str) and str(item).strip()]
    if isinstance(raw, dict):
        for key in ("targets", "options", "entities", "result"):
            value = raw.get(key)
            if isinstance(value, list):
                return [str(item).strip() for item in value if isinstance(item, str) and str(item).strip()]
    if isinstance(raw, str):
        parsed = _load_json_maybe(raw)
        if parsed is not None:
            return _extract_strings(parsed)
        return _split_csv(raw)
    return []


def _clean_host(value: Any) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    if raw.lower() in {"unknown", "unavailable", "none", "null"}:
        return ""
    # Parity hardening: normalize accidental host:port payloads to host-only,
    # matching runtime contract expectation for control-host surfaces.
    if ":" in raw and raw.count(":") == 1:
        host, port = raw.rsplit(":", 1)
        if host and port.isdigit():
            raw = host.strip()
    return raw


def _discover_entity_host(hass: HomeAssistant, entity_id: str) -> str:
    state = hass.states.get(entity_id)
    if state is None:
        return ""
    return _clean_host(state.attributes.get("ip_address"))


def _room_target_ids(room: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    for key in ("entity", "entity_id", "id", "name"):
        value = room.get(key)
        if isinstance(value, str) and value.strip():
            ids.append(value.strip())
    return ids


def build_registry_snapshot(
    hass: HomeAssistant,
    legacy_control_host_entity: str,
    legacy_control_targets_entity: str,
    legacy_rooms_json_entity: str,
    legacy_rooms_raw_entity: str,
) -> dict[str, Any]:
    """Build normalized target registry scaffold from current legacy surfaces."""
    control_host_state = hass.states.get(legacy_control_host_entity)
    control_targets_state = hass.states.get(legacy_control_targets_entity)
    rooms_json_state = hass.states.get(legacy_rooms_json_entity)
    rooms_raw_state = hass.states.get(legacy_rooms_raw_entity)

    control_host = _clean_host(control_host_state.state if control_host_state else "")

    control_targets: set[str] = set(_split_csv(control_targets_state.state if control_targets_state else ""))
    if control_targets_state is not None:
        for key in ("targets", "options", "entities", "result"):
            control_targets.update(_extract_strings(control_targets_state.attributes.get(key)))

    rooms_payload = None
    if rooms_json_state is not None:
        rooms_payload = _load_json_maybe(str(rooms_json_state.attributes.get("rooms_json", "")))
    if rooms_payload is None:
        rooms_payload = _load_json_maybe(rooms_json_state.state if rooms_json_state else "")
    if rooms_payload is None and rooms_raw_state is not None:
        rooms_payload = rooms_raw_state.attributes.get("rooms")

    rooms = _extract_rooms(rooms_payload)

    registry_targets: set[str] = set(control_targets)
    room_meta_by_target: dict[str, str] = {}
    room_host_by_target: dict[str, str] = {}
    for room in rooms:
        room_targets = _room_target_ids(room)
        if not room_targets:
            continue
        room_host = _clean_host(room.get("tcp_host"))
        room_meta = str(room.get("meta") or "").strip()
        for target_id in room_targets:
            registry_targets.add(target_id)
            if room_host and target_id not in room_host_by_target:
                room_host_by_target[target_id] = room_host
            if room_meta and target_id not in room_meta_by_target:
                room_meta_by_target[target_id] = room_meta

    unresolved_sources: list[str] = []
    if control_host_state is None:
        unresolved_sources.append("control_host")
    if control_targets_state is None:
        unresolved_sources.append("control_targets")
    if rooms_json_state is None and rooms_raw_state is None:
        unresolved_sources.append("rooms")

    entries: dict[str, dict[str, Any]] = {}
    resolved_hosts = 0
    for target in sorted(registry_targets):
        discovered_host = _discover_entity_host(hass, target)
        meta_host = _discover_entity_host(hass, room_meta_by_target.get(target, ""))
        room_host = _clean_host(room_host_by_target.get(target, ""))
        effective_host = discovered_host or meta_host or room_host
        if effective_host:
            resolved_hosts += 1
        entries[target] = {
            "target": target,
            "control_path": "linkplay_tcp" if effective_host else "unknown",
            "hardware_family": "arylic_linkplay" if effective_host else "unknown",
            "control_capable": bool(effective_host),
            "host": effective_host,
            "capabilities": ["volume", "transport"] if effective_host else [],
        }

    if resolved_hosts == 0 and registry_targets:
        unresolved_sources.append("target_hosts")

    return {
        "entries": entries,
        "target_count": len(entries),
        "unresolved_sources": unresolved_sources,
        "source_summary": {
            "control_host_present": bool(control_host_state is not None),
            "control_targets_count": len(control_targets),
            "rooms_count": len(rooms),
            "resolved_target_hosts_count": resolved_hosts,
        },
        "source_entities": {
            "control_host": legacy_control_host_entity,
            "control_targets": legacy_control_targets_entity,
            "rooms_json": legacy_rooms_json_entity,
            "rooms_raw": legacy_rooms_raw_entity,
        },
    }
