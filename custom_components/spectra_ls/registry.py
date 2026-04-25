# Description: Registry scaffold helpers for Spectra LS Phase 2 read-only target normalization and deterministic payload parsing.
# Version: 2026.04.25.1
# Last updated: 2026-04-25

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

    control_host = (control_host_state.state if control_host_state else "").strip()

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
    for room in rooms:
        for key in ("id", "name", "entity_id"):
            value = room.get(key)
            if isinstance(value, str) and value.strip():
                registry_targets.add(value.strip())
                break

    unresolved_sources: list[str] = []
    if control_host_state is None:
        unresolved_sources.append("control_host")
    if control_targets_state is None:
        unresolved_sources.append("control_targets")
    if rooms_json_state is None and rooms_raw_state is None:
        unresolved_sources.append("rooms")

    entries: dict[str, dict[str, Any]] = {}
    for target in sorted(registry_targets):
        entries[target] = {
            "target": target,
            "control_path": "pywiim" if control_host else "unknown",
            "hardware_family": "arylic_linkplay" if control_host else "unknown",
            "control_capable": bool(control_host),
            "host": control_host,
            "capabilities": ["volume", "transport"] if control_host else [],
        }

    return {
        "entries": entries,
        "target_count": len(entries),
        "unresolved_sources": unresolved_sources,
        "source_summary": {
            "control_host_present": bool(control_host_state is not None),
            "control_targets_count": len(control_targets),
            "rooms_count": len(rooms),
        },
        "source_entities": {
            "control_host": legacy_control_host_entity,
            "control_targets": legacy_control_targets_entity,
            "rooms_json": legacy_rooms_json_entity,
            "rooms_raw": legacy_rooms_raw_entity,
        },
    }
