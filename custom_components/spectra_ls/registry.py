# Description: Registry scaffold helpers for Spectra LS Phase 2 read-only target normalization and deterministic payload parsing with helper/active-target fallback seeding hardening.
# Version: 2026.04.28.1
# Last updated: 2026-04-28
# PARITY DIRECTIVE (until full cutover): runtime-affecting contract behavior changed here must be mirrored/reconciled in `packages/` + `esphome/`
# in the same slice, with explicit implemented/shim/defer two-track disposition and version-metadata review.

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any, Callable

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er


INVALID_STATE_VALUES = {"", "none", "unknown", "unavailable", "null"}
EMPIRICAL_PROFILE_ENTITY = "sensor.spectra_ls_feature_profile_db"


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


def _state_age_seconds(state_obj: Any) -> float | None:
    changed = getattr(state_obj, "last_changed", None)
    if changed is None:
        return None
    if changed.tzinfo is None:
        changed = changed.replace(tzinfo=UTC)
    age = (datetime.now(UTC) - changed.astimezone(UTC)).total_seconds()
    return round(max(age, 0.0), 1)


def _timestamp_age_seconds(raw_value: Any) -> float | None:
    if raw_value in (None, "", "none", "unknown", "unavailable"):
        return None
    parsed: datetime | None = None
    if isinstance(raw_value, datetime):
        parsed = raw_value
    elif isinstance(raw_value, str):
        value = raw_value.strip()
        if value.endswith("Z"):
            value = f"{value[:-1]}+00:00"
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            parsed = None
    if parsed is None:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    age = (datetime.now(UTC) - parsed.astimezone(UTC)).total_seconds()
    return round(max(age, 0.0), 1)


def _availability_quality(state_raw: str, state_age_s: float | None, position_age_s: float | None) -> str:
    state_l = (state_raw or "").strip().lower()
    if state_l in INVALID_STATE_VALUES:
        return "missing"
    if isinstance(position_age_s, float):
        if position_age_s <= 30:
            return "fresh"
        if position_age_s <= 300:
            return "warm"
    if isinstance(state_age_s, float):
        if state_age_s <= 120:
            return "fresh"
        if state_age_s <= 900:
            return "warm"
    return "stale"


def _observed_capabilities(attrs: dict[str, Any], supported_features: int) -> list[str]:
    observed: list[str] = []
    if attrs.get("volume_level") is not None:
        observed.append("volume_level")
    if isinstance(attrs.get("source_list"), list) and len(attrs.get("source_list", [])) > 0:
        observed.append("source_select")
    if isinstance(attrs.get("sound_mode_list"), list) and len(attrs.get("sound_mode_list", [])) > 0:
        observed.append("sound_mode_select")
    if attrs.get("media_position") is not None or attrs.get("media_duration") is not None:
        observed.append("timeline")
    if attrs.get("ip_address") not in (None, "", "none", "unknown", "unavailable"):
        observed.append("network_endpoint")
    members = attrs.get("group_members") or attrs.get("members") or []
    if isinstance(members, list) and len(members) > 0:
        observed.append("group_membership")
    if isinstance(supported_features, int) and supported_features > 0:
        observed.append("feature_mask")
    return sorted(set(observed))


def _load_empirical_profile_overlays(hass: HomeAssistant) -> dict[str, dict[str, Any]]:
    state = hass.states.get(EMPIRICAL_PROFILE_ENTITY)
    if state is None:
        return {}

    payload = state.attributes.get("profiles_json")
    parsed: Any = None
    if isinstance(payload, dict):
        parsed = payload
    elif isinstance(payload, str):
        parsed = _load_json_maybe(payload)

    if isinstance(parsed, dict):
        return {
            str(key): value
            for key, value in parsed.items()
            if isinstance(key, str) and isinstance(value, dict)
        }

    if isinstance(parsed, list):
        overlays: dict[str, dict[str, Any]] = {}
        for item in parsed:
            if not isinstance(item, dict):
                continue
            target = str(item.get("target") or item.get("entity") or "").strip()
            if target:
                overlays[target] = item
        return overlays

    return {}


def _empirical_overlay_for_target(overlays: dict[str, dict[str, Any]], target: str) -> dict[str, Any]:
    direct = overlays.get(target)
    if isinstance(direct, dict):
        return direct
    short = target.split(".")[-1] if "." in target else target
    short_overlay = overlays.get(short)
    if isinstance(short_overlay, dict):
        return short_overlay
    mp_overlay = overlays.get(f"media_player.{short}")
    if isinstance(mp_overlay, dict):
        return mp_overlay
    return {}


def _build_feature_profile(
    hass: HomeAssistant,
    target: str,
    entity_reg: Any,
    device_reg: Any,
) -> dict[str, Any]:
    state = hass.states.get(target)
    if state is None:
        return {
            "entity": target,
            "available": False,
            "availability_quality": "missing",
            "integration_domain": "unknown",
            "supported_features": 0,
            "observed_capabilities": [],
            "manufacturer": "",
            "model": "",
            "via_device": "",
            "state_age_s": None,
            "position_age_s": None,
        }

    attrs = dict(state.attributes)
    supported_features = attrs.get("supported_features")
    if not isinstance(supported_features, int):
        supported_features = 0

    entity_entry = entity_reg.async_get(target) if entity_reg is not None else None
    integration_domain = ""
    if entity_entry is not None:
        integration_domain = str(getattr(entity_entry, "platform", "") or "")
    if not integration_domain:
        integration_domain = target.split(".")[0] if "." in target else "unknown"

    manufacturer = str(attrs.get("manufacturer") or "")
    model = str(attrs.get("device_model") or attrs.get("model") or "")
    device_id = getattr(entity_entry, "device_id", None) if entity_entry is not None else None
    via_device = ""
    if device_id and device_reg is not None:
        device_entry = device_reg.async_get(device_id)
        if device_entry is not None:
            if not manufacturer:
                manufacturer = str(getattr(device_entry, "manufacturer", "") or "")
            if not model:
                model = str(getattr(device_entry, "model", "") or "")
            via_device_id = getattr(device_entry, "via_device_id", None)
            if via_device_id:
                via_device = str(via_device_id)

    state_age_s = _state_age_seconds(state)
    position_age_s = _timestamp_age_seconds(attrs.get("media_position_updated_at"))
    quality = _availability_quality(state.state, state_age_s, position_age_s)
    observed_caps = _observed_capabilities(attrs, supported_features)
    source_list = attrs.get("source_list") if isinstance(attrs.get("source_list"), list) else []
    sound_mode_list = attrs.get("sound_mode_list") if isinstance(attrs.get("sound_mode_list"), list) else []

    return {
        "entity": target,
        "available": (str(state.state or "").strip().lower() not in INVALID_STATE_VALUES),
        "availability_quality": quality,
        "integration_domain": integration_domain,
        "supported_features": supported_features,
        "observed_capabilities": observed_caps,
        "manufacturer": manufacturer,
        "model": model,
        "via_device": via_device,
        "source_count": len(source_list),
        "sound_mode_count": len(sound_mode_list),
        "state_age_s": state_age_s,
        "position_age_s": position_age_s,
    }


def _discover_entity_host(hass: HomeAssistant, entity_id: str) -> str:
    state = hass.states.get(entity_id)
    if state is None:
        return ""
    return _clean_host(state.attributes.get("ip_address"))


def _discover_entity_host_with_members(hass: HomeAssistant, entity_id: str) -> str:
    state = hass.states.get(entity_id)
    if state is None:
        return ""

    direct_host = _clean_host(state.attributes.get("ip_address"))
    if direct_host:
        return direct_host

    members = state.attributes.get("group_members") or state.attributes.get("members") or []
    if not isinstance(members, list):
        return ""

    for member in members:
        if not isinstance(member, str) or not member.strip():
            continue
        member_state = hass.states.get(member)
        if member_state is None:
            continue
        member_host = _clean_host(member_state.attributes.get("ip_address"))
        if member_host:
            return member_host
    return ""


def _discover_alias_host(hass: HomeAssistant, friendly_name: str, skip_entity_ids: set[str] | None = None) -> str:
    normalized_name = str(friendly_name or "").strip().lower()
    if not normalized_name:
        return ""

    skip = {entity_id.strip() for entity_id in (skip_entity_ids or set()) if isinstance(entity_id, str) and entity_id.strip()}
    for state in hass.states.async_all("media_player"):
        if state.entity_id in skip:
            continue
        state_friendly = str(state.attributes.get("friendly_name") or "").strip().lower()
        if state_friendly != normalized_name:
            continue
        alias_host = _discover_entity_host_with_members(hass, state.entity_id)
        if alias_host:
            return alias_host
    return ""


def _room_target_ids(room: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    for key in ("entity", "entity_id", "id", "name"):
        value = room.get(key)
        if isinstance(value, str) and value.strip():
            ids.append(value.strip())
    return ids


def _infer_host_type(
    hass: HomeAssistant,
    target: str,
    *,
    meta_entity: str,
    room_control_path: str,
    room_hardware_family: str,
) -> str:
    hints: list[str] = []
    hints.extend([room_control_path, room_hardware_family, target])

    for candidate in (target, meta_entity):
        state = hass.states.get(candidate)
        if state is None:
            continue
        hints.extend(
            [
                str(state.attributes.get("manufacturer", "") or ""),
                str(state.attributes.get("device_model", "") or ""),
                str(state.attributes.get("integration_purpose", "") or ""),
            ]
        )

    joined = " ".join(hints).lower()
    if "wiim" in joined:
        return "wiim"
    if any(token in joined for token in ("arylic", "linkplay", "up2stream")):
        return "linkplay_tcp"
    return "generic"


def _candidate_row(source: str, host: str) -> dict[str, Any]:
    clean = _clean_host(host)
    return {
        "source": source,
        "host": clean,
        "resolved": bool(clean),
    }


def _resolve_from_candidates(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    selected = next((row for row in candidates if row.get("resolved")), None)
    return {
        "host": str(selected.get("host", "") if isinstance(selected, dict) else ""),
        "reason": str(selected.get("source", "") if isinstance(selected, dict) else "unresolved"),
        "candidates": candidates,
        "resolved": bool(selected),
    }


def _resolve_generic_host(
    hass: HomeAssistant,
    target: str,
    *,
    meta_entity: str,
    room_host: str,
    target_friendly: str,
) -> dict[str, Any]:
    candidates = [
        _candidate_row("target.ip_or_member", _discover_entity_host_with_members(hass, target)),
        _candidate_row("room.meta.ip_or_member", _discover_entity_host_with_members(hass, meta_entity)),
        _candidate_row("friendly_alias.ip_or_member", _discover_alias_host(hass, target_friendly, {target, meta_entity})),
        _candidate_row("room.tcp_host", room_host),
    ]
    return _resolve_from_candidates(candidates)


def _resolve_linkplay_host(
    hass: HomeAssistant,
    target: str,
    *,
    meta_entity: str,
    room_host: str,
    target_friendly: str,
) -> dict[str, Any]:
    candidates = [
        _candidate_row("linkplay.target.ip_or_member", _discover_entity_host_with_members(hass, target)),
        _candidate_row("linkplay.meta.ip_or_member", _discover_entity_host_with_members(hass, meta_entity)),
        _candidate_row("linkplay.alias.ip_or_member", _discover_alias_host(hass, target_friendly, {target, meta_entity})),
        _candidate_row("linkplay.room.tcp_host", room_host),
    ]
    return _resolve_from_candidates(candidates)


def _resolve_wiim_host(
    hass: HomeAssistant,
    target: str,
    *,
    meta_entity: str,
    room_host: str,
    target_friendly: str,
) -> dict[str, Any]:
    candidates = [
        _candidate_row("wiim.target.ip_or_member", _discover_entity_host_with_members(hass, target)),
        _candidate_row("wiim.alias.ip_or_member", _discover_alias_host(hass, target_friendly, {target, meta_entity})),
        _candidate_row("wiim.meta.ip_or_member", _discover_entity_host_with_members(hass, meta_entity)),
        _candidate_row("wiim.room.tcp_host", room_host),
    ]
    return _resolve_from_candidates(candidates)


HostResolverFn = Callable[[HomeAssistant, str], dict[str, Any]]


def _build_host_resolver(
    resolver: Callable[..., dict[str, Any]],
    *,
    meta_entity: str,
    room_host: str,
    target_friendly: str,
) -> HostResolverFn:
    def _runner(hass: HomeAssistant, target: str) -> dict[str, Any]:
        return resolver(
            hass,
            target,
            meta_entity=meta_entity,
            room_host=room_host,
            target_friendly=target_friendly,
        )

    return _runner


HOST_MODULES: dict[str, str] = {
    "wiim": "hostmods.wiim",
    "linkplay_tcp": "hostmods.linkplay_tcp",
    "generic": "hostmods.generic",
}

SUPPORTED_CONTROL_PATHS = {"linkplay_tcp"}


def build_registry_snapshot(
    hass: HomeAssistant,
    legacy_control_host_entity: str,
    legacy_control_targets_entity: str,
    legacy_rooms_json_entity: str,
    legacy_rooms_raw_entity: str,
    legacy_active_target_helper_entity: str | None = None,
    legacy_active_target_entity: str | None = None,
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

    helper_seed_targets: set[str] = set()
    helper_state = hass.states.get(legacy_active_target_helper_entity) if legacy_active_target_helper_entity else None
    if helper_state is not None:
        helper_current = str(helper_state.state or "").strip()
        if helper_current and helper_current.lower() not in INVALID_STATE_VALUES:
            helper_seed_targets.add(helper_current)
        helper_options = helper_state.attributes.get("options", [])
        if isinstance(helper_options, list):
            helper_seed_targets.update(
                str(item).strip()
                for item in helper_options
                if isinstance(item, str) and str(item).strip() and str(item).strip().lower() not in INVALID_STATE_VALUES
            )

    active_target_seed = ""
    active_target_state = hass.states.get(legacy_active_target_entity) if legacy_active_target_entity else None
    if active_target_state is not None:
        active_target_seed = str(active_target_state.state or "").strip()
        if active_target_seed and active_target_seed.lower() not in INVALID_STATE_VALUES:
            helper_seed_targets.add(active_target_seed)

    rooms_payload = None
    if rooms_json_state is not None:
        rooms_payload = _load_json_maybe(str(rooms_json_state.attributes.get("rooms_json", "")))
    if rooms_payload is None:
        rooms_payload = _load_json_maybe(rooms_json_state.state if rooms_json_state else "")
    if rooms_payload is None and rooms_raw_state is not None:
        rooms_payload = rooms_raw_state.attributes.get("rooms")
    if rooms_payload is None and rooms_raw_state is not None:
        rooms_payload = _load_json_maybe(rooms_raw_state.state)
    if rooms_payload is None and rooms_raw_state is not None:
        rooms_payload = _load_json_maybe(str(rooms_raw_state.attributes.get("rooms_json", "")))
    if rooms_payload is None and rooms_json_state is not None:
        rooms_payload = rooms_json_state.attributes.get("rooms")

    rooms = _extract_rooms(rooms_payload)
    empirical_overlays = _load_empirical_profile_overlays(hass)
    entity_reg = er.async_get(hass)
    device_reg = dr.async_get(hass)

    registry_targets: set[str] = set(control_targets)
    registry_targets.update(helper_seed_targets)
    room_meta_by_target: dict[str, str] = {}
    room_host_by_target: dict[str, str] = {}
    room_entry_by_target: dict[str, dict[str, Any]] = {}
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
            if isinstance(room, dict) and target_id not in room_entry_by_target:
                room_entry_by_target[target_id] = room

    unresolved_sources: list[str] = []
    if control_host_state is None:
        unresolved_sources.append("control_host")
    if control_targets_state is None:
        unresolved_sources.append("control_targets")
    if rooms_json_state is None and rooms_raw_state is None:
        unresolved_sources.append("rooms")

    entries: dict[str, dict[str, Any]] = {}
    resolved_hosts = 0
    host_type_counts: dict[str, int] = {}
    resolver_module_counts: dict[str, int] = {}
    profiled_targets = 0
    empirical_profiled_targets = 0
    for target in sorted(registry_targets):
        meta_entity = room_meta_by_target.get(target, "")
        room_host = _clean_host(room_host_by_target.get(target, ""))
        target_state = hass.states.get(target)
        target_friendly = str(target_state.attributes.get("friendly_name") or "").strip() if target_state is not None else ""

        room_entry = room_entry_by_target.get(target, {})
        room_control_path = str(room_entry.get("control_path", "") if isinstance(room_entry, dict) else "")
        room_hardware_family = str(room_entry.get("hardware_family", "") if isinstance(room_entry, dict) else "")

        host_type = _infer_host_type(
            hass,
            target,
            meta_entity=meta_entity,
            room_control_path=room_control_path,
            room_hardware_family=room_hardware_family,
        )

        resolver_module = HOST_MODULES.get(host_type, HOST_MODULES["generic"])
        resolver_fn = {
            "wiim": _build_host_resolver(
                _resolve_wiim_host,
                meta_entity=meta_entity,
                room_host=room_host,
                target_friendly=target_friendly,
            ),
            "linkplay_tcp": _build_host_resolver(
                _resolve_linkplay_host,
                meta_entity=meta_entity,
                room_host=room_host,
                target_friendly=target_friendly,
            ),
            "generic": _build_host_resolver(
                _resolve_generic_host,
                meta_entity=meta_entity,
                room_host=room_host,
                target_friendly=target_friendly,
            ),
        }.get(host_type)
        if resolver_fn is None:
            resolver_fn = _build_host_resolver(
                _resolve_generic_host,
                meta_entity=meta_entity,
                room_host=room_host,
                target_friendly=target_friendly,
            )

        resolution = resolver_fn(hass, target)
        effective_host = _clean_host(resolution.get("host", ""))
        resolved_control_path = "linkplay_tcp" if host_type == "linkplay_tcp" else "unknown"
        control_capable = bool(effective_host) and resolved_control_path in SUPPORTED_CONTROL_PATHS
        feature_profile = _build_feature_profile(hass, target, entity_reg, device_reg)
        empirical_overlay = _empirical_overlay_for_target(empirical_overlays, target)
        if feature_profile:
            profiled_targets += 1
        if empirical_overlay:
            empirical_profiled_targets += 1

        if effective_host:
            resolved_hosts += 1
        host_type_counts[host_type] = host_type_counts.get(host_type, 0) + 1
        resolver_module_counts[resolver_module] = resolver_module_counts.get(resolver_module, 0) + 1

        entries[target] = {
            "target": target,
            "control_path": resolved_control_path,
            "hardware_family": room_hardware_family if room_hardware_family else ("arylic_linkplay" if host_type == "linkplay_tcp" and effective_host else "unknown"),
            "control_capable": control_capable,
            "host": effective_host,
            "capabilities": ["volume", "transport"] if control_capable else [],
            "host_type": host_type,
            "resolver_module": resolver_module,
            "host_resolution": resolution,
            "feature_profile": feature_profile,
            "empirical_profile": empirical_overlay,
            "scheduler_profile": {
                "host": effective_host,
                "host_type": host_type,
                "resolver_module": resolver_module,
                "control_capable": control_capable,
                "availability_quality": feature_profile.get("availability_quality", "missing"),
                "observed_capabilities": feature_profile.get("observed_capabilities", []),
                "integration_domain": feature_profile.get("integration_domain", "unknown"),
                "empirical_overlay_present": bool(empirical_overlay),
            },
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
            "helper_seed_targets_count": len(helper_seed_targets),
            "active_target_seed_present": bool(active_target_seed),
            "rooms_count": len(rooms),
            "resolved_target_hosts_count": resolved_hosts,
            "host_type_counts": host_type_counts,
            "resolver_module_counts": resolver_module_counts,
            "profiled_targets_count": profiled_targets,
            "empirical_profiled_targets_count": empirical_profiled_targets,
        },
        "host_modules": HOST_MODULES,
        "empirical_overlay": {
            "source_entity": EMPIRICAL_PROFILE_ENTITY,
            "profiles_count": len(empirical_overlays),
        },
        "source_entities": {
            "control_host": legacy_control_host_entity,
            "control_targets": legacy_control_targets_entity,
            "rooms_json": legacy_rooms_json_entity,
            "rooms_raw": legacy_rooms_raw_entity,
            "active_target_helper": legacy_active_target_helper_entity,
            "active_target": legacy_active_target_entity,
        },
    }
