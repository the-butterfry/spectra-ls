# Description: Sensor entities for Spectra LS shadow parity routing surfaces with Phase 3 write-control, Phase 4 diagnostics attributes, and Phase 6/8 control-center settings/readiness/last-attempt visibility, including recorder-safe attribute payload sizing and shared MA authority-contract packet propagation.
# Version: 2026.08.18.3
# Last updated: 2026-08-18
# PARITY DIRECTIVE (until full cutover): behavior/contract edits here require same-slice two-track parity review
# and version-metadata review in runtime (`packages/` + `esphome/`) and component (`custom_components/spectra_ls/`) tracks.

from __future__ import annotations

import json
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .authority_contract import build_authority_contract_packet
from .const import (
    DOMAIN,
    LEGACY_META_CANDIDATES,
    LEGACY_META_CONFIDENCE_MIN,
    LEGACY_META_RESOLVER,
)
from .payload_surface_fabric import PayloadSurfaceFabric


def _dict_surface(payload: dict[str, Any], key: str) -> dict[str, Any]:
    candidate = payload.get(key, {})
    return candidate if isinstance(candidate, dict) else {}


def _metadata_values(data: dict[str, Any]) -> dict[str, Any]:
    return PayloadSurfaceFabric.metadata_values(data)


def _metadata_checks(data: dict[str, Any]) -> dict[str, Any]:
    return PayloadSurfaceFabric.metadata_checks(data)


def _metadata_prep_packet(data: dict[str, Any]) -> dict[str, Any]:
    return _dict_surface(data, "metadata_prep_validation")


def _metadata_prep_values_packet(data: dict[str, Any]) -> dict[str, Any]:
    return _dict_surface(_metadata_prep_packet(data), "values")


def _metadata_prep_checks_packet(data: dict[str, Any]) -> dict[str, Any]:
    return _dict_surface(_metadata_prep_packet(data), "checks")


def _registry_entries(data: dict[str, Any]) -> dict[str, Any]:
    return _dict_surface(_dict_surface(data, "registry"), "entries")


def _coerce_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _coerce_positive_float(value: Any) -> float | None:
    parsed = _coerce_float(value)
    if parsed is None or parsed <= 0.0:
        return None
    return parsed


def _jsonish(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None
    return None


def _component_meta_candidates_packet(entity: CoordinatorEntity) -> dict[str, Any]:
    hass = entity.coordinator.hass
    candidates_state = hass.states.get(LEGACY_META_CANDIDATES)
    resolver_state = hass.states.get(LEGACY_META_RESOLVER)

    confidence_min_state = hass.states.get(LEGACY_META_CONFIDENCE_MIN)
    confidence_min = 4.0
    if confidence_min_state is not None:
        try:
            confidence_min = float(confidence_min_state.state)
        except (TypeError, ValueError):
            confidence_min = 4.0

    entities: list[str] = []
    names: list[str] = []
    scores: list[float] = []
    best_entity = ""
    best_score = 0.0
    candidate_count_hint = 0

    if candidates_state is not None:
        attrs = candidates_state.attributes if isinstance(candidates_state.attributes, dict) else {}

        summary = _jsonish(attrs.get("candidate_summary_json"))
        if isinstance(summary, dict):
            raw_candidate_count = summary.get("candidate_count", 0)
            if isinstance(raw_candidate_count, (int, float)) and raw_candidate_count > 0:
                candidate_count_hint = int(raw_candidate_count)
            raw_entities = summary.get("entities", [])
            raw_names = summary.get("names", [])
            raw_scores = summary.get("scores", [])
            if isinstance(raw_entities, list):
                entities = [str(item).strip() for item in raw_entities if str(item).strip()]
            if isinstance(raw_names, list):
                names = [str(item).strip() for item in raw_names if str(item).strip()]
            if isinstance(raw_scores, list):
                parsed_scores: list[float] = []
                for item in raw_scores:
                    try:
                        parsed_scores.append(float(item))
                    except (TypeError, ValueError):
                        continue
                scores = parsed_scores

        rows = _jsonish(attrs.get("candidate_rows_json"))
        if isinstance(rows, list) and len(entities) == 0:
            for row in rows:
                if not isinstance(row, dict):
                    continue
                ent = str(row.get("entity", "") or "").strip()
                if not ent:
                    continue
                entities.append(ent)
                names.append(str(row.get("name", "") or ent).strip())
                try:
                    scores.append(float(row.get("score", 0)))
                except (TypeError, ValueError):
                    scores.append(0.0)

        best_candidate = _jsonish(attrs.get("best_candidate_json"))
        if isinstance(best_candidate, dict):
            best_entity = str(best_candidate.get("entity", "") or "").strip()
            try:
                best_score = float(best_candidate.get("score", 0))
            except (TypeError, ValueError):
                best_score = 0.0

        if best_entity == "":
            best_entity = str(attrs.get("best_entity", "") or "").strip()
        if best_score == 0.0:
            try:
                best_score = float(attrs.get("best_score", 0))
            except (TypeError, ValueError):
                best_score = 0.0

    if best_entity == "" and resolver_state is not None:
        best_entity = str(resolver_state.attributes.get("best_entity", "") or "").strip()
    if best_score == 0.0 and resolver_state is not None:
        try:
            best_score = float(resolver_state.attributes.get("best_score", 0))
        except (TypeError, ValueError):
            best_score = 0.0

    candidate_count = max(len(entities), candidate_count_hint)
    low_confidence = best_entity == "" or best_score < confidence_min

    return {
        "candidate_count": candidate_count,
        "entities": entities,
        "names": names,
        "scores": [round(item, 2) for item in scores],
        "best_entity": best_entity,
        "best_score": round(best_score, 2),
        "confidence_min": round(confidence_min, 2),
        "low_confidence": low_confidence,
    }


def _component_active_target(data: dict[str, Any]) -> str:
    route_trace = _dict_surface(data, "route_trace")
    target = str(route_trace.get("active_target", "") or "").strip()
    return target


def _component_control_hosts(data: dict[str, Any]) -> str:
    active_target = _component_active_target(data)
    active_target_l = active_target.strip().lower()
    active_target_resolved = active_target_l not in {"", "none", "unknown", "unavailable"}

    host_cutover = _dict_surface(data, "host_control_cutover_gate")
    gate_status = str(host_cutover.get("status", "") or "").strip().lower()
    component_candidate = host_cutover.get("component_authoritative_candidate", {})
    if isinstance(component_candidate, dict):
        candidate_target = str(component_candidate.get("target", "") or "").strip()
        candidate_target_l = candidate_target.lower()
        candidate_target_resolved = candidate_target_l not in {"", "none", "unknown", "unavailable"}
        candidate_target_matches_active = (
            (not active_target_resolved)
            or (candidate_target_resolved and candidate_target_l == active_target_l)
        )
        candidate_host = str(component_candidate.get("host", "") or "").strip()
        if candidate_host and gate_status == "ready" and candidate_target_matches_active:
            return candidate_host

    route_trace = _dict_surface(data, "route_trace")
    selected_target = route_trace.get("selected_target", {})
    if isinstance(selected_target, dict):
        selected_target_id = str(selected_target.get("target", "") or "").strip().lower()
        selected_target_matches_active = (
            (not active_target_resolved)
            or (selected_target_id not in {"", "none", "unknown", "unavailable"}
                and selected_target_id == active_target_l)
        )
        selected_host = str(selected_target.get("host", "") or "").strip()
        if selected_host and selected_target_matches_active:
            return selected_host
    return ""


def _component_control_port(data: dict[str, Any]) -> str:
    route_trace = _dict_surface(data, "route_trace")
    selected_target = route_trace.get("selected_target", {})
    selected_entry = selected_target if isinstance(selected_target, dict) else {}

    resolved_control_path = str(route_trace.get("resolved_control_path", "") or "").strip().lower()
    selected_control_path = str(selected_entry.get("control_path", "") or "").strip().lower()
    active_path = resolved_control_path or selected_control_path

    has_host = bool(_component_control_hosts(data))
    if active_path == "linkplay_tcp" and has_host:
        return "8899"
    return ""


def _component_ma_backend_profile(data: dict[str, Any]) -> dict[str, Any]:
    backend = data.get("ma_backend_profile", {})
    return backend if isinstance(backend, dict) else {}


def _metadata_value_text(data: dict[str, Any], key: str) -> str:
    return PayloadSurfaceFabric.metadata_value_text(data, key)


def _contract_text(value: Any) -> str:
    return PayloadSurfaceFabric.contract_text(value)


def _component_now_playing_state(entity: CoordinatorEntity) -> Any | None:
    entity_id = _metadata_value_text(entity.coordinator.data, "now_playing_entity")
    if not entity_id:
        return None
    return entity.coordinator.hass.states.get(entity_id)


def _state_attrs(state_obj: Any) -> dict[str, Any]:
    attrs = getattr(state_obj, "attributes", {})
    return attrs if isinstance(attrs, dict) else {}


def _component_state_attr_text(state_obj: Any, keys: tuple[str, ...]) -> str:
    if state_obj is None:
        return ""
    attrs = _state_attrs(state_obj)
    for key in keys:
        value = PayloadSurfaceFabric.contract_text(attrs.get(key, ""))
        if value:
            return value
    return ""


def _component_now_playing_contract_or_state(
    entity: CoordinatorEntity,
    *,
    metadata_key: str,
    state_field: str,
) -> str:
    value = _metadata_value_text(entity.coordinator.data, metadata_key)
    if value:
        return value
    state_obj = _component_now_playing_state(entity)
    if state_obj is None:
        return ""
    return _contract_text(getattr(state_obj, state_field, ""))


def _component_now_playing_contract_or_attr(
    entity: CoordinatorEntity,
    *,
    metadata_key: str,
    attr_keys: tuple[str, ...],
) -> str:
    value = _metadata_value_text(entity.coordinator.data, metadata_key)
    if value:
        return value
    state_obj = _component_now_playing_state(entity)
    return _component_state_attr_text(state_obj, attr_keys)


def _component_metadata_provider_packet(data: dict[str, Any]) -> dict[str, Any]:
    return PayloadSurfaceFabric.metadata_provider_packet(data)


def _component_metadata_override_packet(data: dict[str, Any]) -> dict[str, Any]:
    return PayloadSurfaceFabric.metadata_override_packet(data)


def _component_runtime_track_disposition(data: dict[str, Any]) -> str:
    """Return current runtime-track disposition for CA closeout consumers."""
    route_trace = _dict_surface(data, "route_trace")
    contract = _dict_surface(data, "contract_validation")
    route_decision = str(route_trace.get("decision", "") or "").strip()
    contract_valid = bool(contract.get("valid", False))
    if route_decision and contract_valid:
        return "compatibility-shimmed"
    return "deferred with rationale"


def _component_component_track_disposition(data: dict[str, Any]) -> str:
    """Return current component-track disposition for CA closeout consumers."""
    metadata_prep = _metadata_prep_packet(data)
    handoff = _dict_surface(data, "handoff_inventory")
    prep_ready = bool(metadata_prep.get("ready_for_metadata_handoff", False))
    metadata_lane = str(handoff.get("metadata_resolver_status", "") or "").strip().lower()
    if prep_ready or metadata_lane == "implemented":
        return "implemented"
    return "compatibility-shimmed"


def _component_lc06_final_disposition(data: dict[str, Any]) -> str:
    """Return closeout disposition summary for LC-06 runtime retirement lanes."""
    backend = _component_ma_backend_profile(data)
    backend_ready = bool(backend.get("profile_resolved", False)) and bool(
        backend.get("api_url_resolved", False)
    )
    return "compatibility-shimmed" if backend_ready else "deferred with rationale"


def _component_lc07_final_disposition(data: dict[str, Any]) -> str:
    """Return closeout disposition summary for LC-07 fallback listener lanes."""
    route_trace = _dict_surface(data, "route_trace")
    decision = str(route_trace.get("decision", "") or "").strip().lower()
    if decision == "route_linkplay_tcp":
        return "compatibility-shimmed"
    return "deferred with rationale"


def _component_lc08_final_disposition(data: dict[str, Any]) -> str:
    """Return closeout disposition summary for LC-08 diagnostics fallback lanes."""
    metadata_prep = _metadata_prep_packet(data)
    checks = _metadata_prep_checks_packet(data)
    component_ready = bool(metadata_prep.get("ready_for_metadata_handoff", False))
    fresh_signal = bool(checks.get("now_playing_fresh_play_signal", False))
    if component_ready or fresh_signal:
        return "compatibility-shimmed"
    return "deferred with rationale"


def _component_retirement_ledger_consistency(data: dict[str, Any]) -> str:
    """Return deterministic ledger-consistency status for closeout validators."""
    required = (
        "route_trace",
        "contract_validation",
        "metadata_prep_validation",
        "host_control_cutover_gate",
        "write_controls",
    )
    missing = [key for key in required if not isinstance(data.get(key, {}), dict)]
    if missing:
        return "blocked"
    runtime_disposition = _component_runtime_track_disposition(data)
    component_disposition = _component_component_track_disposition(data)
    if runtime_disposition and component_disposition:
        return "clean"
    return "blocked"


class SpectraLsComponentActiveTargetSensor(CoordinatorEntity, SensorEntity):
    """Component-native active-target contract surface."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:crosshairs-gps"
    _attr_name = "Component Active Target"
    _attr_unique_id = "spectra_ls_component_active_target"
    _unrecorded_attributes = frozenset({"resolved_control_path", "route_decision", "route_reason"})

    @property
    def native_value(self):
        return _component_active_target(self.coordinator.data)

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        route_trace = _dict_surface(data, "route_trace")
        return {
            "resolved_control_path": route_trace.get("resolved_control_path", ""),
            "route_decision": route_trace.get("decision", ""),
            "route_reason": route_trace.get("reason", ""),
        }


class SpectraLsComponentControlHostsSensor(CoordinatorEntity, SensorEntity):
    """Component-native control-hosts contract surface."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:server-network"
    _attr_name = "Component Control Hosts"
    _attr_unique_id = "spectra_ls_component_control_hosts"
    _unrecorded_attributes = frozenset({"authority_mode", "component_authoritative_candidate", "gate_status"})

    @property
    def native_value(self):
        return _component_control_hosts(self.coordinator.data)

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        host_cutover = _dict_surface(data, "host_control_cutover_gate")
        return {
            "authority_mode": host_cutover.get("authority_mode", "component"),
            "component_authoritative_candidate": host_cutover.get("component_authoritative_candidate", {}),
            "gate_status": host_cutover.get("status", "blocked"),
        }


class SpectraLsComponentControlHostSensor(CoordinatorEntity, SensorEntity):
    """Component-native primary control-host contract surface."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:router-network"
    _attr_name = "Component Control Host"
    _attr_unique_id = "spectra_ls_component_control_host"
    _unrecorded_attributes = frozenset({"control_hosts"})

    @property
    def native_value(self):
        hosts = _component_control_hosts(self.coordinator.data)
        if "," in hosts:
            return hosts.split(",")[0].strip()
        return hosts

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        return {
            "control_hosts": _component_control_hosts(data),
        }


class SpectraLsComponentControlTargetsSensor(CoordinatorEntity, SensorEntity):
    """Component-native control-target inventory contract surface."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:format-list-bulleted-square"
    _attr_name = "Component Control Targets"
    _attr_unique_id = "spectra_ls_component_control_targets"
    _unrecorded_attributes = frozenset({"entities", "labels", "target_count"})

    @property
    def native_value(self):
        entries = _registry_entries(self.coordinator.data)
        count = 0
        for entry in entries.values():
            if not isinstance(entry, dict):
                continue
            host = str(entry.get("host", "") or "").strip()
            if host:
                count += 1
        return count

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        entries = _registry_entries(data)

        entities: list[str] = []
        labels: list[str] = []
        for target, entry in entries.items():
            if not isinstance(entry, dict):
                continue
            host = str(entry.get("host", "") or "").strip()
            if not host:
                continue
            target_id = str(target or "").strip()
            if target_id:
                entities.append(target_id)
                labels.append(target_id)

        return {
            "entities": entities,
            "labels": labels,
            "target_count": len(entities),
        }


class SpectraLsComponentControlPortSensor(CoordinatorEntity, SensorEntity):
    """Component-native control-port contract surface."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:ethernet-cable"
    _attr_name = "Component Control Port"
    _attr_unique_id = "spectra_ls_component_control_port"
    _unrecorded_attributes = frozenset({"resolved_control_path", "control_hosts"})

    @property
    def native_value(self):
        return _component_control_port(self.coordinator.data)

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        route_trace = _dict_surface(data, "route_trace")
        selected_target = route_trace.get("selected_target", {})
        selected_entry = selected_target if isinstance(selected_target, dict) else {}
        resolved_control_path = str(route_trace.get("resolved_control_path", "") or "").strip().lower()
        selected_control_path = str(selected_entry.get("control_path", "") or "").strip().lower()
        active_path = resolved_control_path or selected_control_path
        return {
            "resolved_control_path": active_path,
            "control_hosts": _component_control_hosts(data),
        }


class SpectraLsComponentBackendProfileSensor(CoordinatorEntity, SensorEntity):
    """Component-native backend profile diagnostics bridge (LC6-L05)."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:server"
    _attr_name = "Component Backend Profile"
    _attr_unique_id = "spectra_ls_component_backend_profile"
    _unrecorded_attributes = frozenset(
        {
            "profile_entity",
            "effective_entity",
            "selected_url",
            "profile_resolved",
            "selected_url_resolved",
        }
    )

    @property
    def native_value(self):
        packet = _component_ma_backend_profile(self.coordinator.data)
        profile = str(packet.get("profile", "") or "").strip()
        return profile or "missing"

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        packet = _component_ma_backend_profile(data)
        return {
            "profile_entity": packet.get("profile_entity", ""),
            "effective_entity": packet.get("effective_entity", ""),
            "selected_url": packet.get("selected_url", ""),
            "profile_resolved": packet.get("profile_resolved", False),
            "selected_url_resolved": packet.get("selected_url_resolved", False),
        }


class SpectraLsComponentApiUrlSensor(CoordinatorEntity, SensorEntity):
    """Component-native MA API URL diagnostics bridge (LC6-L05)."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:api"
    _attr_name = "Component MA API URL"
    _attr_unique_id = "spectra_ls_component_ma_api_url"
    _unrecorded_attributes = frozenset(
        {
            "api_url_entity",
            "api_url_resolved",
            "selected_url",
            "selected_url_resolved",
        }
    )

    @property
    def native_value(self):
        packet = _component_ma_backend_profile(self.coordinator.data)
        api_url = str(packet.get("api_url", "") or "").strip()
        selected_url = str(packet.get("selected_url", "") or "").strip().rstrip("/")
        if api_url:
            return api_url
        if selected_url:
            return f"{selected_url}/api"
        return ""

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        packet = _component_ma_backend_profile(data)
        return {
            "api_url_entity": packet.get("api_url_entity", ""),
            "api_url_resolved": packet.get("api_url_resolved", False),
            "selected_url": packet.get("selected_url", ""),
            "selected_url_resolved": packet.get("selected_url_resolved", False),
        }


class _ComponentNowPlayingContractStateSensor(CoordinatorEntity, SensorEntity):
    """Shared now-playing sensor base: metadata key with state-field fallback."""

    _metadata_key: str = ""
    _state_field: str = "state"

    @property
    def native_value(self):
        return _component_now_playing_contract_or_state(
            self,
            metadata_key=self._metadata_key,
            state_field=self._state_field,
        )


class _ComponentNowPlayingContractAttrSensor(CoordinatorEntity, SensorEntity):
    """Shared now-playing sensor base: metadata key with attribute fallback chain."""

    _metadata_key: str = ""
    _attr_keys: tuple[str, ...] = ()

    @property
    def native_value(self):
        return _component_now_playing_contract_or_attr(
            self,
            metadata_key=self._metadata_key,
            attr_keys=self._attr_keys,
        )


class _ComponentNowPlayingMetadataTextSensor(CoordinatorEntity, SensorEntity):
    """Shared now-playing sensor base: direct metadata text value."""

    _metadata_key: str = ""

    @property
    def native_value(self):
        return _metadata_value_text(self.coordinator.data, self._metadata_key)


class SpectraLsComponentNowPlayingEntitySensor(_ComponentNowPlayingContractStateSensor):
    """Component-native now-playing entity contract surface."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:play-network"
    _attr_name = "Component Now Playing Entity"
    _attr_unique_id = "spectra_ls_component_now_playing_entity"
    _metadata_key = "now_playing_entity"
    _state_field = "entity_id"


class SpectraLsComponentNowPlayingStateSensor(_ComponentNowPlayingContractStateSensor):
    """Component-native now-playing state contract surface."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:play-pause"
    _attr_name = "Component Now Playing State"
    _attr_unique_id = "spectra_ls_component_now_playing_state"
    _metadata_key = "now_playing_state"
    _state_field = "state"


class SpectraLsComponentNowPlayingTitleSensor(_ComponentNowPlayingContractAttrSensor):
    """Component-native now-playing title contract surface."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:music-note"
    _attr_name = "Component Now Playing Title"
    _attr_unique_id = "spectra_ls_component_now_playing_title"
    _metadata_key = "now_playing_title"
    _attr_keys = ("media_title", "title", "name")


class SpectraLsComponentNowPlayingFriendlySensor(CoordinatorEntity, SensorEntity):
    """Component-native now-playing friendly-label contract surface."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:card-account-details-outline"
    _attr_name = "Component Now Playing Friendly"
    _attr_unique_id = "spectra_ls_component_now_playing_friendly"

    @property
    def native_value(self):
        state_obj = _component_now_playing_state(self)
        friendly = _component_state_attr_text(state_obj, ("friendly_name", "name"))
        if friendly:
            return friendly
        return _metadata_value_text(self.coordinator.data, "now_playing_entity")


class SpectraLsComponentNowPlayingArtistSensor(_ComponentNowPlayingContractAttrSensor):
    """Component-native now-playing artist contract surface."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:account-music"
    _attr_name = "Component Now Playing Artist"
    _attr_unique_id = "spectra_ls_component_now_playing_artist"
    _metadata_key = "now_playing_artist"
    _attr_keys = ("media_artist", "artist")


class SpectraLsComponentNowPlayingAlbumSensor(_ComponentNowPlayingContractAttrSensor):
    """Component-native now-playing album contract surface."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:album"
    _attr_name = "Component Now Playing Album"
    _attr_unique_id = "spectra_ls_component_now_playing_album"
    _metadata_key = "now_playing_album"
    _attr_keys = ("media_album_name", "media_album", "album")


class SpectraLsComponentNowPlayingAppSensor(_ComponentNowPlayingContractAttrSensor):
    """Component-native now-playing app contract surface."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:application-cog-outline"
    _attr_name = "Component Now Playing App"
    _attr_unique_id = "spectra_ls_component_now_playing_app"
    _metadata_key = "now_playing_app"
    _attr_keys = ("app_name", "media_channel", "app", "application")


class SpectraLsComponentNowPlayingSourceSensor(_ComponentNowPlayingContractAttrSensor):
    """Component-native now-playing source contract surface."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:source-branch"
    _attr_name = "Component Now Playing Source"
    _attr_unique_id = "spectra_ls_component_now_playing_source"
    _metadata_key = "now_playing_source"
    _attr_keys = ("source", "source_name", "media_source", "input_source")


class SpectraLsComponentNowPlayingPositionSensor(CoordinatorEntity, SensorEntity):
    """Component-native now-playing position contract surface."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:timeline-clock"
    _attr_name = "Component Now Playing Position"
    _attr_unique_id = "spectra_ls_component_now_playing_position"
    _attr_native_unit_of_measurement = "s"

    @property
    def native_value(self):
        values = _metadata_values(self.coordinator.data)
        parsed = _coerce_float(values.get("now_playing_position"))
        if parsed is not None:
            return parsed

        state_obj = _component_now_playing_state(self)
        if state_obj is None:
            return None
        return _coerce_float(_state_attrs(state_obj).get("media_position"))


class SpectraLsComponentNowPlayingDurationSensor(CoordinatorEntity, SensorEntity):
    """Component-native now-playing duration contract surface."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:timer-outline"
    _attr_name = "Component Now Playing Duration"
    _attr_unique_id = "spectra_ls_component_now_playing_duration"
    _attr_native_unit_of_measurement = "s"

    @property
    def native_value(self):
        values = _metadata_values(self.coordinator.data)
        parsed = _coerce_positive_float(values.get("now_playing_duration"))
        if parsed is not None:
            return parsed

        state_obj = _component_now_playing_state(self)
        if state_obj is not None:
            fallback_parsed = _coerce_positive_float(_state_attrs(state_obj).get("media_duration"))
            if fallback_parsed is not None:
                return fallback_parsed

        helper_parsed = _coerce_positive_float(values.get("ma_active_duration"))
        if helper_parsed is not None:
            return helper_parsed

        return None


class SpectraLsComponentNowPlayingVolumeSensor(CoordinatorEntity, SensorEntity):
    """Component-native now-playing volume contract surface."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:volume-high"
    _attr_name = "Component Now Playing Volume"
    _attr_unique_id = "spectra_ls_component_now_playing_volume"

    @property
    def native_value(self):
        state_obj = _component_now_playing_state(self)
        if state_obj is None:
            return 0.0
        attrs = _state_attrs(state_obj)
        raw = attrs.get("media_volume_level", attrs.get("volume_level", 0))
        value = _coerce_float(raw)
        if value is None:
            return 0.0
        if value <= 1.0:
            value *= 100.0
        if value < 0.0:
            value = 0.0
        if value > 100.0:
            value = 100.0
        return round(value, 1)


class SpectraLsComponentNowPlayingMediaClassSensor(_ComponentNowPlayingMetadataTextSensor):
    """Component-native now-playing media-class contract surface."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:music-circle"
    _attr_name = "Component Now Playing Media Class"
    _attr_unique_id = "spectra_ls_component_now_playing_media_class"
    _metadata_key = "now_playing_media_class"


class SpectraLsComponentNowPlayingPreviewKeySensor(_ComponentNowPlayingMetadataTextSensor):
    """Component-native now-playing preview-key contract surface."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:key-variant"
    _attr_name = "Component Now Playing Preview Key"
    _attr_unique_id = "spectra_ls_component_now_playing_preview_key"
    _metadata_key = "now_playing_preview_key"


class SpectraLsComponentNowPlayingFreshnessAgeSensor(CoordinatorEntity, SensorEntity):
    """Component-native now-playing freshness-age contract surface."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:clock-fast"
    _attr_name = "Component Now Playing Freshness Age"
    _attr_unique_id = "spectra_ls_component_now_playing_freshness_age_s"
    _attr_native_unit_of_measurement = "s"

    @property
    def native_value(self):
        values = _metadata_values(self.coordinator.data)
        raw = values.get("now_playing_position_age_s", 0)
        try:
            return float(raw)
        except (TypeError, ValueError):
            return 0.0

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        values = _metadata_values(data)
        checks = _metadata_checks(data)
        return {
            "position_age_source": values.get("now_playing_position_age_source", "missing"),
            "suppression_reason": checks.get("now_playing_suppression_reason", ""),
            "fresh_play_signal": checks.get("now_playing_fresh_play_signal"),
            "captured_at": data.get("captured_at"),
        }


class SpectraLsComponentMetaCandidatesSensor(CoordinatorEntity, SensorEntity):
    """Component-native metadata-candidates contract surface."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:playlist-star"
    _attr_name = "Component Meta Candidates"
    _attr_unique_id = "spectra_ls_component_meta_candidates"

    @property
    def native_value(self):
        packet = _component_meta_candidates_packet(self)
        return int(packet.get("candidate_count", 0))

    @property
    def extra_state_attributes(self):
        packet = _component_meta_candidates_packet(self)
        packet["captured_at"] = self.coordinator.data.get("captured_at")
        return packet


class SpectraLsComponentMetadataOverrideEntitySensor(CoordinatorEntity, SensorEntity):
    """Component-owned metadata override entity status surface (LC-08)."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:form-textbox"
    _attr_name = "Component Metadata Override Entity"
    _attr_unique_id = "spectra_ls_component_metadata_override_entity"

    @property
    def native_value(self):
        data = self.coordinator.data
        return PayloadSurfaceFabric.metadata_override_entity(data)

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        packet = _component_metadata_override_packet(data)
        metadata_attempt = self.coordinator.metadata_stack.last_metadata_override_attempt
        return {
            "last_attempt_status": packet.get("last_attempt_status") or metadata_attempt.get("status", "unknown"),
            "last_attempt_reason": packet.get("last_attempt_reason") or metadata_attempt.get("reason", ""),
            "last_attempt_requested_at": packet.get("last_attempt_requested_at") or metadata_attempt.get("requested_at"),
            "last_attempt_completed_at": packet.get("last_attempt_completed_at") or metadata_attempt.get("completed_at"),
            "source": packet.get("source", "component_packet_missing"),
            "captured_at": data.get("captured_at"),
        }


class SpectraLsComponentMetadataProviderStatusSensor(CoordinatorEntity, SensorEntity):
    """Component-owned provider refresh telemetry surface (LC6-L04)."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:database-sync"
    _attr_name = "Component Metadata Provider Status"
    _attr_unique_id = "spectra_ls_component_metadata_provider_status"

    @property
    def native_value(self):
        packet = _component_metadata_provider_packet(self.coordinator.data)
        status = str(packet.get("status", "") or "").strip()
        return status or "never_attempted"

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        packet = _component_metadata_provider_packet(data)
        return {
            "providers": packet.get("providers", ""),
            "response": packet.get("response", ""),
            "item_uri": packet.get("item_uri", ""),
            "reason": packet.get("reason", ""),
            "updated_at": packet.get("updated_at", ""),
            "age_s": packet.get("age_s"),
            "visible": packet.get("visible", False),
            "source": packet.get("source", "component_packet_missing"),
            "captured_at": data.get("captured_at"),
        }


class SpectraLsComponentRuntimeTrackDispositionSensor(CoordinatorEntity, SensorEntity):
    """Component closeout surface for runtime-track disposition."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:timeline-alert"
    _attr_name = "Component Runtime Track Disposition"
    _attr_unique_id = "spectra_ls_component_runtime_track_disposition"

    @property
    def native_value(self):
        return _component_runtime_track_disposition(self.coordinator.data)


class SpectraLsComponentComponentTrackDispositionSensor(CoordinatorEntity, SensorEntity):
    """Component closeout surface for component-track disposition."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:timeline-check"
    _attr_name = "Component Component Track Disposition"
    _attr_unique_id = "spectra_ls_component_component_track_disposition"

    @property
    def native_value(self):
        return _component_component_track_disposition(self.coordinator.data)


class SpectraLsComponentLc06FinalDispositionSensor(CoordinatorEntity, SensorEntity):
    """Component closeout surface for LC-06 final disposition."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:format-list-checks"
    _attr_name = "Component LC06 Final Disposition"
    _attr_unique_id = "spectra_ls_component_lc06_final_disposition"

    @property
    def native_value(self):
        return _component_lc06_final_disposition(self.coordinator.data)


class SpectraLsComponentLc07FinalDispositionSensor(CoordinatorEntity, SensorEntity):
    """Component closeout surface for LC-07 final disposition."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:format-list-checks"
    _attr_name = "Component LC07 Final Disposition"
    _attr_unique_id = "spectra_ls_component_lc07_final_disposition"

    @property
    def native_value(self):
        return _component_lc07_final_disposition(self.coordinator.data)


class SpectraLsComponentLc08FinalDispositionSensor(CoordinatorEntity, SensorEntity):
    """Component closeout surface for LC-08 final disposition."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:format-list-checks"
    _attr_name = "Component LC08 Final Disposition"
    _attr_unique_id = "spectra_ls_component_lc08_final_disposition"

    @property
    def native_value(self):
        return _component_lc08_final_disposition(self.coordinator.data)


class SpectraLsComponentRetirementLedgerConsistencySensor(CoordinatorEntity, SensorEntity):
    """Component closeout surface for retirement-ledger consistency."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:ledger"
    _attr_name = "Component Retirement Ledger Consistency"
    _attr_unique_id = "spectra_ls_component_retirement_ledger_consistency"

    @property
    def native_value(self):
        return _component_retirement_ledger_consistency(self.coordinator.data)

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        return {
            "runtime_track_disposition": _component_runtime_track_disposition(data),
            "component_track_disposition": _component_component_track_disposition(data),
            "lc06_final_disposition": _component_lc06_final_disposition(data),
            "lc07_final_disposition": _component_lc07_final_disposition(data),
            "lc08_final_disposition": _component_lc08_final_disposition(data),
            "captured_at": data.get("captured_at"),
        }


class SpectraLsShadowSensor(CoordinatorEntity, SensorEntity):
    """Generic read-only shadow sensor."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:audio-video"
    # Keep rich diagnostics visible in state while avoiding Recorder DB bloat and
    # 16KB attribute warnings on high-volume nested payloads.
    _unrecorded_attributes = frozenset(
        {
            "legacy_value",
            "unresolved_sources",
            "mismatches",
            "route_trace",
            "contract_validation",
            "selection_handoff_validation",
            "route_safety_validation",
            "metadata_prep_validation",
            "scheduler_validation",
            "metadata_bridge_validation",
            "handoff_inventory",
            "host_control_cutover_gate",
            "control_center_validation",
            "write_controls",
        }
    )

    def __init__(self, coordinator, key: str, name: str) -> None:
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"spectra_ls_shadow_{key}"

    @property
    def native_value(self):
        return self.coordinator.data["parity"].get(self._key, "")

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        base = {
            "legacy_value": data["legacy"].get(self._key),
            "unresolved_sources": data.get("unresolved_sources", []),
            "mismatches": data.get("mismatches", []),
        }

        # Keep non-primary shadow entities lightweight to avoid Recorder attribute-size drops.
        if self._key != "active_target":
            return {
                **base,
                "route_trace": data.get("route_trace", {}),
                "host_control_cutover_gate": data.get("host_control_cutover_gate", {}),
                "authority_contract": build_authority_contract_packet(data),
            }

        # Primary diagnostics surface (active target): include required operator contracts,
        # but intentionally omit high-volume payloads (e.g. full registry/action catalogs)
        # to stay under Recorder attribute limits.
        return {
            **base,
            "route_trace": data.get("route_trace", {}),
            "contract_validation": data.get("contract_validation", {}),
            "selection_handoff_validation": data.get("selection_handoff_validation", {}),
            "route_safety_validation": data.get("route_safety_validation", {}),
            "metadata_prep_validation": data.get("metadata_prep_validation", {}),
            "scheduler_validation": data.get("scheduler_validation", {}),
            "metadata_bridge_validation": data.get("metadata_bridge_validation", {}),
            "handoff_inventory": data.get("handoff_inventory", {}),
            "host_control_cutover_gate": data.get("host_control_cutover_gate", {}),
            "ma_backend_profile": data.get("ma_backend_profile", {}),
            "control_center_validation": data.get("control_center_validation", {}),
            "write_controls": data.get("write_controls", {}),
            "authority_contract": build_authority_contract_packet(data),
        }


class SpectraLsControlCenterLastAttemptStatusSensor(CoordinatorEntity, SensorEntity):
    """Diagnostic sensor exposing the latest control-center execution result status."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:gesture-tap-button"
    _attr_name = "Control Center Last Attempt Status"
    _attr_unique_id = "spectra_ls_control_center_last_attempt_status"

    @property
    def native_value(self):
        write_controls = self.coordinator.data.get("write_controls", {})
        last_attempt = write_controls.get("control_center_last_attempt", {})
        status = str(last_attempt.get("status", "never_attempted") or "").strip()
        return status or "never_attempted"

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        write_controls = data.get("write_controls", {})
        last_attempt = write_controls.get("control_center_last_attempt", {})
        cc_validation = data.get("control_center_validation", {})

        return {
            "reason": last_attempt.get("reason"),
            "input_event": last_attempt.get("input_event"),
            "mapped_action": last_attempt.get("mapped_action"),
            "dry_run": last_attempt.get("dry_run"),
            "read_only_mode": last_attempt.get("read_only_mode"),
            "correlation_id": last_attempt.get("correlation_id"),
            "target_hint": last_attempt.get("target_hint"),
            "requested_at": last_attempt.get("requested_at"),
            "completed_at": last_attempt.get("completed_at"),
            "control_center_settings": write_controls.get("control_center_settings", {}),
            "mapping_preset": cc_validation.get("mapping_preset"),
            "effective_mapping": cc_validation.get("effective_mapping", {}),
            "ready_for_customization": cc_validation.get("ready_for_customization"),
            "unresolved_scene_bindings": cc_validation.get("unresolved_scene_bindings", []),
            "captured_at": data.get("captured_at"),
        }


class SpectraLsControlCenterReadinessSensor(CoordinatorEntity, SensorEntity):
    """Diagnostic sensor exposing Control Center readiness state and setup guidance."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:clipboard-check-outline"
    _attr_name = "Control Center Readiness"
    _attr_unique_id = "spectra_ls_control_center_readiness"

    @property
    def native_value(self):
        cc_validation = self.coordinator.data.get("control_center_validation", {})
        readiness_state = str(cc_validation.get("readiness_state", "needs_scene_binding") or "").strip()
        return readiness_state or "needs_scene_binding"

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        cc_validation = data.get("control_center_validation", {})
        write_controls = data.get("write_controls", {})

        return {
            "ready_for_execution": cc_validation.get("ready_for_execution"),
            "recommended_next_step": cc_validation.get("recommended_next_step"),
            "mapping_preset": cc_validation.get("mapping_preset"),
            "preset_applied": cc_validation.get("preset_applied"),
            "effective_mapping": cc_validation.get("effective_mapping", {}),
            "configured_scene_bindings_count": cc_validation.get("configured_scene_bindings_count"),
            "total_scene_bindings": cc_validation.get("total_scene_bindings"),
            "resolved_scene_bindings": cc_validation.get("resolved_scene_bindings", []),
            "unresolved_scene_bindings": cc_validation.get("unresolved_scene_bindings", []),
            "quick_trigger_scene": cc_validation.get("quick_trigger_scene"),
            "quick_trigger_ready": cc_validation.get("quick_trigger_ready"),
            "read_only_mode": cc_validation.get("read_only_mode"),
            "non_dry_run_supported_actions": cc_validation.get("non_dry_run_supported_actions", []),
            "non_dry_run_pending_actions": cc_validation.get("non_dry_run_pending_actions", []),
            "control_center_settings": write_controls.get("control_center_settings", {}),
            "authority_contract": build_authority_contract_packet(data),
            "captured_at": data.get("captured_at"),
        }


class SpectraLsHostResolutionStatusSensor(CoordinatorEntity, SensorEntity):
    """Diagnostic sensor exposing pluggable host-module resolution status."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:router-network"
    _attr_name = "Host Resolution Status"
    _attr_unique_id = "spectra_ls_host_resolution_status"

    @property
    def native_value(self):
        data = self.coordinator.data
        entries = _registry_entries(data)
        total = len(entries)
        resolved = 0
        for entry in entries.values():
            if not isinstance(entry, dict):
                continue
            host = str(entry.get("host", "") or "").strip()
            if host:
                resolved += 1
        return f"{resolved}/{total}"

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        registry = _dict_surface(data, "registry")
        host_cutover = data.get("host_control_cutover_gate", {}) if isinstance(data.get("host_control_cutover_gate", {}), dict) else {}
        entries = _registry_entries(data)
        summary = registry.get("source_summary", {}) if isinstance(registry.get("source_summary", {}), dict) else {}

        targets: dict[str, dict[str, object]] = {}
        for target, entry in entries.items():
            if not isinstance(entry, dict):
                continue
            targets[str(target)] = {
                "host": entry.get("host", ""),
                "host_type": entry.get("host_type", "generic"),
                "resolver_module": entry.get("resolver_module", "hostmods.generic"),
                "control_path": entry.get("control_path", "unknown"),
                "control_capable": bool(entry.get("control_capable", False)),
                "host_resolution": entry.get("host_resolution", {}),
                "feature_profile": entry.get("feature_profile", {}),
                "empirical_profile": entry.get("empirical_profile", {}),
                "scheduler_profile": entry.get("scheduler_profile", {}),
            }

        return {
            "host_modules": registry.get("host_modules", {}),
            "empirical_overlay": registry.get("empirical_overlay", {}),
            "host_type_counts": summary.get("host_type_counts", {}),
            "resolver_module_counts": summary.get("resolver_module_counts", {}),
            "resolved_target_hosts_count": summary.get("resolved_target_hosts_count", 0),
            "profiled_targets_count": summary.get("profiled_targets_count", 0),
            "empirical_profiled_targets_count": summary.get("empirical_profiled_targets_count", 0),
            "target_count": registry.get("target_count", 0),
            "unresolved_sources": registry.get("unresolved_sources", []),
            "targets": targets,
            "authority_source_mode": host_cutover.get("authority_source_mode", "legacy"),
            "authoritative_host_candidate": host_cutover.get("component_authoritative_candidate", {}),
            "cutover_gate_status": host_cutover.get("status", "blocked"),
            "cutover_gate_ready": host_cutover.get("ready_for_cutover", False),
            "cutover_gate_blockers": host_cutover.get("gate_blockers", []),
            "route_trace": data.get("route_trace", {}),
            "captured_at": data.get("captured_at"),
        }


class SpectraLsHostAuthorityCutoverGateSensor(CoordinatorEntity, SensorEntity):
    """Diagnostic sensor exposing host-control authority cutover readiness gate."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:source-branch-check"
    _attr_name = "Host Authority Cutover Gate"
    _attr_unique_id = "spectra_ls_host_authority_cutover_gate"

    @property
    def native_value(self):
        gate = self.coordinator.data.get("host_control_cutover_gate", {})
        status = str(gate.get("status", "blocked") or "").strip().lower()
        return status or "blocked"

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        gate = data.get("host_control_cutover_gate", {}) if isinstance(data.get("host_control_cutover_gate", {}), dict) else {}
        return {
            "schema_version": gate.get("schema_version", ""),
            "ready_for_cutover": gate.get("ready_for_cutover", False),
            "ready_for_authoritative_activation": gate.get("ready_for_authoritative_activation", False),
            "authority_source_mode": gate.get("authority_source_mode", "legacy"),
            "authority_mode": gate.get("authority_mode", "legacy"),
            "component_authoritative_candidate": gate.get("component_authoritative_candidate", {}),
            "legacy_authority_snapshot": gate.get("legacy_authority_snapshot", {}),
            "route_decision": gate.get("route_decision", ""),
            "resolved_control_path": gate.get("resolved_control_path", ""),
            "checks": gate.get("checks", {}),
            "gate_blockers": gate.get("gate_blockers", []),
            "activation_blockers": gate.get("activation_blockers", []),
            "captured_at": data.get("captured_at"),
        }


class SpectraLsSchedulerDecisionSensor(CoordinatorEntity, SensorEntity):
    """Diagnostic sensor exposing last scheduler decision status and payload."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:timeline-check"
    _attr_name = "Scheduler Decision Status"
    _attr_unique_id = "spectra_ls_scheduler_decision_status"

    @property
    def native_value(self):
        write_controls = self.coordinator.data.get("write_controls", {})
        decision = write_controls.get("scheduler_last_decision", {})
        status = str(decision.get("status", "never_attempted") or "").strip()
        return status or "never_attempted"

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        write_controls = data.get("write_controls", {})
        decision = write_controls.get("scheduler_last_decision", {})
        apply_result = write_controls.get("scheduler_last_apply", {})
        return {
            "selected_target": decision.get("selected_target", ""),
            "selected_host": decision.get("selected_host", ""),
            "selected_score": decision.get("selected_score", 0.0),
            "reason": decision.get("reason", ""),
            "policy": decision.get("policy", {}),
            "candidate_count": decision.get("candidate_count", 0),
            "ranked_candidates": decision.get("ranked_candidates", []),
            "correlation_id": decision.get("correlation_id", ""),
            "requested_at": decision.get("requested_at"),
            "completed_at": decision.get("completed_at"),
            "last_apply_status": apply_result.get("status", "never_attempted"),
            "last_apply_reason": apply_result.get("reason", ""),
            "last_apply_target": apply_result.get("selected_target", ""),
            "last_apply_dry_run": apply_result.get("dry_run", True),
            "last_apply_force": apply_result.get("force", False),
            "last_apply_requested_at": apply_result.get("requested_at"),
            "last_apply_completed_at": apply_result.get("completed_at"),
            "scheduler_validation": data.get("scheduler_validation", {}),
            "captured_at": data.get("captured_at"),
        }


class SpectraLsMetaPolicyStatusSensor(CoordinatorEntity, SensorEntity):
    """Diagnostic sensor exposing canonical metadata policy + suppression posture."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:tune-variant"
    _attr_name = "Meta Policy Status"
    _attr_unique_id = "spectra_ls_meta_policy_status"

    @property
    def native_value(self):
        write_controls = self.coordinator.data.get("write_controls", {})
        policy = write_controls.get("meta_policy", {}) if isinstance(write_controls.get("meta_policy", {}), dict) else {}
        mode = str(policy.get("mode", "auto") or "auto").strip().lower()
        return mode or "auto"

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        write_controls = data.get("write_controls", {})
        policy = write_controls.get("meta_policy", {}) if isinstance(write_controls.get("meta_policy", {}), dict) else {}
        checks = _metadata_prep_checks_packet(data)
        values = _metadata_prep_values_packet(data)

        return {
            "meta_policy": policy,
            "suppression_reason": checks.get("now_playing_suppression_reason", ""),
            "fresh_play_signal": checks.get("now_playing_fresh_play_signal"),
            "now_playing_preview_key": values.get("now_playing_preview_key", ""),
            "now_playing_display_allowed": values.get("now_playing_display_allowed"),
            "display_contract_consistent": checks.get("now_playing_display_contract_consistent"),
            "now_playing_preview_age_s": values.get("now_playing_preview_age_s"),
            "recent_play_progress": checks.get("now_playing_recent_play_progress", None),
            "recent_paused_progress": checks.get("now_playing_recent_paused_progress", None),
            "playing_without_recent_progress": checks.get("now_playing_playing_without_fresh_signal"),
            "paused_without_recent_progress": checks.get("now_playing_paused_without_fresh_signal"),
            "long_idle_stale_hidden": checks.get("now_playing_long_idle_stale_hidden"),
            "now_playing_entity": values.get("now_playing_entity", ""),
            "now_playing_position_age_s": values.get("now_playing_position_age_s"),
            "now_playing_position_age_source": values.get("now_playing_position_age_source", "missing"),
            "meta_stale_s": values.get("meta_stale_s"),
            "paused_hide_s": values.get("paused_hide_s"),
            "authority_contract": build_authority_contract_packet(data),
            "captured_at": data.get("captured_at"),
        }


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Spectra LS shadow sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    shadow_specs: tuple[tuple[str, str], ...] = (
        ("active_target", "Shadow Active Target"),
        ("active_control_path", "Shadow Active Control Path"),
        ("control_hosts", "Shadow Control Hosts"),
    )
    component_sensor_types = (
        SpectraLsComponentActiveTargetSensor,
        SpectraLsComponentControlHostsSensor,
        SpectraLsComponentControlHostSensor,
        SpectraLsComponentControlTargetsSensor,
        SpectraLsComponentControlPortSensor,
        SpectraLsComponentBackendProfileSensor,
        SpectraLsComponentApiUrlSensor,
        SpectraLsComponentNowPlayingEntitySensor,
        SpectraLsComponentNowPlayingStateSensor,
        SpectraLsComponentNowPlayingTitleSensor,
        SpectraLsComponentNowPlayingFriendlySensor,
        SpectraLsComponentNowPlayingArtistSensor,
        SpectraLsComponentNowPlayingAlbumSensor,
        SpectraLsComponentNowPlayingAppSensor,
        SpectraLsComponentNowPlayingSourceSensor,
        SpectraLsComponentNowPlayingPositionSensor,
        SpectraLsComponentNowPlayingDurationSensor,
        SpectraLsComponentNowPlayingVolumeSensor,
        SpectraLsComponentNowPlayingMediaClassSensor,
        SpectraLsComponentNowPlayingPreviewKeySensor,
        SpectraLsComponentNowPlayingFreshnessAgeSensor,
        SpectraLsComponentMetaCandidatesSensor,
        SpectraLsComponentMetadataOverrideEntitySensor,
        SpectraLsComponentMetadataProviderStatusSensor,
        SpectraLsComponentRuntimeTrackDispositionSensor,
        SpectraLsComponentComponentTrackDispositionSensor,
        SpectraLsComponentLc06FinalDispositionSensor,
        SpectraLsComponentLc07FinalDispositionSensor,
        SpectraLsComponentLc08FinalDispositionSensor,
        SpectraLsComponentRetirementLedgerConsistencySensor,
        SpectraLsHostResolutionStatusSensor,
        SpectraLsHostAuthorityCutoverGateSensor,
        SpectraLsSchedulerDecisionSensor,
        SpectraLsMetaPolicyStatusSensor,
        SpectraLsControlCenterReadinessSensor,
        SpectraLsControlCenterLastAttemptStatusSensor,
    )

    entities = [
        *(SpectraLsShadowSensor(coordinator, key, name) for key, name in shadow_specs),
        *(sensor_type(coordinator) for sensor_type in component_sensor_types),
    ]
    async_add_entities(entities)
