# Description: Data coordinator for Spectra LS parity diagnostics, Phase 3 guarded routing write-path controls, Phase 4 diagnostics scaffolding (F4-S01/F4-S03), and Phase 5 metadata trial contract auditing with unresolved-contract hardening.
# Version: 2026.04.21.20
# Last updated: 2026-04-21

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import json
import logging
from time import monotonic
from typing import Any
from uuid import uuid4

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DOMAIN,
    LEGACY_ACTIVE_META_ENTITY,
    LEGACY_CONTROL_HOST,
    LEGACY_CONTROL_TARGETS,
    LEGACY_META_CANDIDATES,
    LEGACY_ACTIVE_TARGET_HELPER,
    LEGACY_NOW_PLAYING_ENTITY,
    LEGACY_NOW_PLAYING_STATE,
    LEGACY_NOW_PLAYING_TITLE,
    LEGACY_ROOMS_JSON,
    LEGACY_ROOMS_RAW,
    LEGACY_SURFACES,
    WRITE_AUTH_ALLOWED,
    WRITE_AUTH_COMPONENT,
    WRITE_AUTH_LEGACY,
    WRITE_DEBOUNCE_SECONDS,
)
from .registry import build_registry_snapshot
from .router import build_route_trace

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class LegacySnapshot:
    """Normalized legacy value snapshot."""

    value: Any
    state: str
    available: bool


class SpectraLsShadowCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinates read-only shadow parity data for legacy routing surfaces."""

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=f"{DOMAIN}_shadow_parity",
        )
        self._unsub_state_events = None
        self._write_authority_mode = WRITE_AUTH_LEGACY
        self._write_debounce_s = float(WRITE_DEBOUNCE_SECONDS)
        self._write_in_progress = False
        self._last_write_monotonic = 0.0
        self._last_write_attempt: dict[str, Any] = {
            "status": "never_attempted",
            "timestamp": None,
            "reason": "No write attempts yet",
        }
        self._metadata_trial_in_progress = False
        self._last_metadata_trial_attempt: dict[str, Any] = {
            "status": "never_attempted",
            "requested_at": None,
            "completed_at": None,
            "reason": "No metadata trial attempts yet",
            "audit_payload_complete": False,
            "audit_payload_state": "N/A",
            "missing_audit_fields": [],
        }

    @staticmethod
    def _metadata_trial_audit_missing_fields(payload: dict[str, Any]) -> list[str]:
        required_fields = {
            "status": payload.get("status"),
            "window_id": payload.get("window_id"),
            "requested_mode": payload.get("requested_mode"),
            "effective_mode": payload.get("effective_mode"),
            "dry_run": payload.get("dry_run"),
            "reason": payload.get("reason"),
            "correlation_id": payload.get("correlation_id"),
            "requested_at": payload.get("requested_at"),
            "completed_at": payload.get("completed_at"),
        }

        missing: list[str] = []
        for field, value in required_fields.items():
            if field == "dry_run":
                if value is None:
                    missing.append(field)
                continue
            if value is None:
                missing.append(field)
                continue
            if isinstance(value, str) and value.strip() == "":
                missing.append(field)

        return missing

    async def async_setup(self) -> None:
        """Initialize data and state listeners."""
        await self.async_refresh()

        watched_entities = set(LEGACY_SURFACES.values())
        watched_entities.update(
            {
                LEGACY_ACTIVE_TARGET_HELPER,
                LEGACY_ACTIVE_META_ENTITY,
                LEGACY_NOW_PLAYING_ENTITY,
                LEGACY_NOW_PLAYING_STATE,
                LEGACY_NOW_PLAYING_TITLE,
                LEGACY_META_CANDIDATES,
                LEGACY_CONTROL_HOST,
                LEGACY_CONTROL_TARGETS,
                LEGACY_ROOMS_JSON,
                LEGACY_ROOMS_RAW,
            }
        )

        self._unsub_state_events = async_track_state_change_event(
            self.hass,
            sorted(watched_entities),
            self._handle_state_change,
        )

    async def async_shutdown(self) -> None:
        """Detach listeners on unload."""
        if self._unsub_state_events is not None:
            self._unsub_state_events()
            self._unsub_state_events = None

    async def _async_update_data(self) -> dict[str, Any]:
        """Read legacy surfaces and compute parity snapshot."""
        return self._build_snapshot()

    @staticmethod
    def _normalize_state(state_value: str) -> str:
        return (state_value or "").strip().lower()

    def _snapshot_for_entity(self, entity_id: str, *, as_bool: bool = False) -> LegacySnapshot:
        state = self.hass.states.get(entity_id)
        if state is None:
            return LegacySnapshot(value=False if as_bool else "", state="missing", available=False)

        normalized = self._normalize_state(state.state)
        available = normalized not in {"", "unknown", "unavailable", "none"}

        if as_bool:
            bool_value = normalized in {"on", "true", "1", "yes"}
            return LegacySnapshot(value=bool_value, state=state.state, available=available)

        return LegacySnapshot(value=state.state if available else "", state=state.state, available=available)

    @staticmethod
    def _normalize_write_authority(mode: str) -> str:
        normalized = (mode or "").strip().lower()
        return normalized if normalized in WRITE_AUTH_ALLOWED else WRITE_AUTH_LEGACY

    def _build_write_controls(self) -> dict[str, Any]:
        return {
            "authority_mode": self._write_authority_mode,
            "allowed_modes": list(WRITE_AUTH_ALLOWED),
            "debounce_s": self._write_debounce_s,
            "in_progress": self._write_in_progress,
            "last_attempt": self._last_write_attempt,
            "metadata_trial_in_progress": self._metadata_trial_in_progress,
            "metadata_trial_last_attempt": self._last_metadata_trial_attempt,
            "target_helper_entity": LEGACY_ACTIVE_TARGET_HELPER,
        }

    def _build_contract_validation(self) -> dict[str, Any]:
        required_entities = {
            "active_target": LEGACY_SURFACES["active_target"],
            "active_control_path": LEGACY_SURFACES["active_control_path"],
            "active_control_capable": LEGACY_SURFACES["active_control_capable"],
            "control_hosts": LEGACY_SURFACES["control_hosts"],
            "control_host": LEGACY_CONTROL_HOST,
            "control_targets": LEGACY_CONTROL_TARGETS,
            "rooms_json": LEGACY_ROOMS_JSON,
            "rooms_raw": LEGACY_ROOMS_RAW,
        }
        missing_required = [
            key for key, entity_id in required_entities.items() if self.hass.states.get(entity_id) is None
        ]
        unresolved_required: list[str] = []
        required_states: dict[str, str] = {}
        for key, entity_id in required_entities.items():
            state = self.hass.states.get(entity_id)
            state_value = state.state if state is not None else "missing"
            required_states[key] = state_value
            if state is None:
                continue
            if not self._is_resolved_state(state_value):
                unresolved_required.append(key)

        return {
            "required_entities": required_entities,
            "missing_required": missing_required,
            "unresolved_required": unresolved_required,
            "required_states": required_states,
            "valid": len(missing_required) == 0 and len(unresolved_required) == 0,
        }

    def _build_selection_handoff_validation(
        self,
        *,
        parity: dict[str, Any],
        route_trace: dict[str, Any],
        contract_validation: dict[str, Any],
    ) -> dict[str, Any]:
        helper_state = self.hass.states.get(LEGACY_ACTIVE_TARGET_HELPER)
        helper_exists = helper_state is not None
        helper_options_attr = helper_state.attributes.get("options", []) if helper_state is not None else []
        helper_options = (
            [str(item) for item in helper_options_attr if isinstance(item, str)]
            if isinstance(helper_options_attr, list)
            else []
        )

        active_target = str(parity.get("active_target", "") or "").strip()
        active_target_resolved = active_target.lower() not in {"", "none", "unknown", "unavailable"}
        target_in_helper_options = active_target_resolved and active_target in helper_options

        required_scripts = [
            "script.ma_update_target_options",
            "script.ma_auto_select",
            "script.ma_cycle_target",
        ]
        missing_scripts = [entity_id for entity_id in required_scripts if self.hass.states.get(entity_id) is None]

        required_automation_ids = [
            "ma_update_target_options_start",
            "ma_auto_select_loop",
            "ma_track_last_valid_target",
        ]
        available_automation_ids = {
            str(state.attributes.get("id", ""))
            for state in self.hass.states.async_all("automation")
            if isinstance(state.attributes.get("id", ""), str)
        }
        missing_automation_ids = [
            automation_id for automation_id in required_automation_ids if automation_id not in available_automation_ids
        ]

        route_decision = str(route_trace.get("decision", "") or "")
        route_ready = route_decision == "route_linkplay_tcp"
        contract_valid = bool(contract_validation.get("valid", False))

        verdict = "PASS"
        if not helper_exists or not active_target_resolved or not route_ready or not contract_valid:
            verdict = "FAIL"
        elif (
            not helper_options
            or not target_in_helper_options
            or len(missing_scripts) > 0
            or len(missing_automation_ids) > 0
        ):
            verdict = "WARN"

        return {
            "verdict": verdict,
            "ready_for_handoff": verdict == "PASS",
            "active_target": active_target,
            "route_decision": route_decision,
            "contract_valid": contract_valid,
            "helper": {
                "entity_id": LEGACY_ACTIVE_TARGET_HELPER,
                "exists": helper_exists,
                "options_count": len(helper_options),
                "target_in_options": target_in_helper_options,
            },
            "compatibility": {
                "required_scripts": required_scripts,
                "missing_scripts": missing_scripts,
                "required_automation_ids": required_automation_ids,
                "missing_automation_ids": missing_automation_ids,
            },
        }

    @staticmethod
    def _is_resolved_state(raw_state: str) -> bool:
        normalized = (raw_state or "").strip().lower()
        return normalized not in {"", "none", "unknown", "unavailable", "missing"}

    @staticmethod
    def _timestamp_age_seconds(raw_value: Any) -> float | None:
        if raw_value in (None, "", "none", "unknown", "unavailable"):
            return None

        parsed: datetime | None = None
        if isinstance(raw_value, datetime):
            parsed = raw_value
        elif isinstance(raw_value, str):
            cleaned = raw_value.strip()
            if cleaned.endswith("Z"):
                cleaned = f"{cleaned[:-1]}+00:00"
            try:
                parsed = datetime.fromisoformat(cleaned)
            except ValueError:
                parsed = None

        if parsed is None:
            return None

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)

        age_s = (datetime.now(UTC) - parsed.astimezone(UTC)).total_seconds()
        return max(age_s, 0.0)

    def _build_now_playing_signal(self, entity_id: str) -> dict[str, Any]:
        if not self._is_resolved_state(entity_id):
            return {
                "resolved": False,
                "state": "missing",
                "play_state_attr": "",
                "is_playing_attr": None,
                "is_paused_attr": None,
                "position_age_s": None,
                "recent_progress": False,
                "fresh_play_signal": False,
                "paused_without_fresh_signal": False,
            }

        state = self.hass.states.get(entity_id)
        if state is None:
            return {
                "resolved": False,
                "state": "missing",
                "play_state_attr": "",
                "is_playing_attr": None,
                "is_paused_attr": None,
                "position_age_s": None,
                "recent_progress": False,
                "fresh_play_signal": False,
                "paused_without_fresh_signal": False,
            }

        state_norm = self._normalize_state(state.state)
        play_state_attr = self._normalize_state(str(state.attributes.get("play_state", "") or ""))
        is_playing_attr = state.attributes.get("is_playing")
        is_paused_attr = state.attributes.get("is_paused")
        pos_age_s = self._timestamp_age_seconds(state.attributes.get("media_position_updated_at"))
        recent_progress = pos_age_s is not None and pos_age_s <= 300

        playing_signal = (
            state_norm == "playing"
            or play_state_attr in {"play", "playing"}
            or is_playing_attr is True
        )
        paused_signal = (
            state_norm == "paused"
            or play_state_attr in {"pause", "paused"}
            or is_paused_attr is True
        )

        fresh_play_signal = playing_signal or (paused_signal and recent_progress)
        paused_without_fresh_signal = paused_signal and not recent_progress

        return {
            "resolved": True,
            "state": state_norm,
            "play_state_attr": play_state_attr,
            "is_playing_attr": is_playing_attr,
            "is_paused_attr": is_paused_attr,
            "position_age_s": round(pos_age_s, 1) if isinstance(pos_age_s, float) else None,
            "recent_progress": recent_progress,
            "fresh_play_signal": fresh_play_signal,
            "paused_without_fresh_signal": paused_without_fresh_signal,
        }

    def _metadata_candidate_payload_ready(self) -> bool:
        candidates_state = self.hass.states.get(LEGACY_META_CANDIDATES)
        if candidates_state is None:
            return False

        def _parse_jsonish(value: Any) -> Any:
            if isinstance(value, (dict, list)):
                return value
            if isinstance(value, str):
                raw = value.strip()
                if not raw or raw in {"{}", "[]"}:
                    return None
                try:
                    return json.loads(raw)
                except json.JSONDecodeError:
                    return None
            return None

        best_candidate_raw = candidates_state.attributes.get("best_candidate_json")
        best_candidate = _parse_jsonish(best_candidate_raw)
        if isinstance(best_candidate, dict):
            best_entity = str(best_candidate.get("entity", "") or "").strip()
            if best_entity:
                return True

        summary_raw = candidates_state.attributes.get("candidate_summary_json")
        summary = _parse_jsonish(summary_raw)
        if isinstance(summary, dict):
            entities = summary.get("entities", [])
            if isinstance(entities, list):
                if any(isinstance(entity, str) and entity.strip() for entity in entities):
                    return True
            candidate_count = summary.get("candidate_count", 0)
            if isinstance(candidate_count, (int, float)) and candidate_count > 0:
                return True

        rows_raw = candidates_state.attributes.get("candidate_rows_json")
        rows = _parse_jsonish(rows_raw)
        if isinstance(rows, list):
            for row in rows:
                if isinstance(row, dict):
                    entity = str(row.get("entity", "") or "").strip()
                    if entity:
                        return True

        return False

    def _build_metadata_prep_validation(
        self,
        *,
        route_trace: dict[str, Any],
        contract_validation: dict[str, Any],
    ) -> dict[str, Any]:
        required_entities = {
            "active_meta_entity": LEGACY_ACTIVE_META_ENTITY,
            "now_playing_entity": LEGACY_NOW_PLAYING_ENTITY,
            "now_playing_state": LEGACY_NOW_PLAYING_STATE,
            "now_playing_title": LEGACY_NOW_PLAYING_TITLE,
            "meta_candidates": LEGACY_META_CANDIDATES,
        }

        missing_required = [
            key for key, entity_id in required_entities.items() if self.hass.states.get(entity_id) is None
        ]

        active_meta_raw = self.hass.states.get(LEGACY_ACTIVE_META_ENTITY)
        now_playing_entity_raw = self.hass.states.get(LEGACY_NOW_PLAYING_ENTITY)
        now_playing_state_raw = self.hass.states.get(LEGACY_NOW_PLAYING_STATE)
        now_playing_title_raw = self.hass.states.get(LEGACY_NOW_PLAYING_TITLE)

        active_meta_entity = active_meta_raw.state if active_meta_raw is not None else "missing"
        now_playing_entity = now_playing_entity_raw.state if now_playing_entity_raw is not None else "missing"
        now_playing_state = now_playing_state_raw.state if now_playing_state_raw is not None else "missing"
        now_playing_title = now_playing_title_raw.state if now_playing_title_raw is not None else "missing"

        active_meta_entity_resolved = self._is_resolved_state(active_meta_entity)
        now_playing_entity_resolved = self._is_resolved_state(now_playing_entity)
        now_playing_state_resolved = self._is_resolved_state(now_playing_state)
        now_playing_title_resolved = self._is_resolved_state(now_playing_title)

        route_decision = str(route_trace.get("decision", "") or "")
        route_trace_present = route_decision != ""
        contract_valid = bool(contract_validation.get("valid", False))
        candidate_payload_ready = self._metadata_candidate_payload_ready()
        now_playing_signal = self._build_now_playing_signal(now_playing_entity)
        paused_without_fresh_signal = bool(now_playing_signal.get("paused_without_fresh_signal", False))
        now_playing_fresh_play_signal = bool(now_playing_signal.get("fresh_play_signal", False))
        metadata_authority_owner = "legacy_contract_surfaces"
        metadata_cutover_active = False
        cutover_block_reason = "metadata_authority_not_cut_over"
        no_authority_expansion = self._write_authority_mode == WRITE_AUTH_LEGACY

        gate_checks: dict[str, bool] = {
            "contract_valid": contract_valid,
            "active_meta_entity_resolved": active_meta_entity_resolved,
            "now_playing_entity_resolved": now_playing_entity_resolved,
            "now_playing_state_resolved": now_playing_state_resolved,
            "now_playing_title_resolved": now_playing_title_resolved,
            "candidate_payload_ready": candidate_payload_ready,
            "route_trace_present": route_trace_present,
            "no_authority_expansion": no_authority_expansion,
            "now_playing_fresh_play_signal": now_playing_fresh_play_signal,
        }
        gate_score = sum(1 for ok in gate_checks.values() if ok)
        gate_max = len(gate_checks)
        blocking_reasons: list[str] = []
        if not contract_valid:
            blocking_reasons.append("contract_invalid")
        if len(missing_required) > 0:
            blocking_reasons.append("missing_required_metadata_entities")
        if not active_meta_entity_resolved:
            blocking_reasons.append("active_meta_entity_unresolved")
        if not now_playing_entity_resolved:
            blocking_reasons.append("now_playing_entity_unresolved")
        if not now_playing_state_resolved:
            blocking_reasons.append("now_playing_state_unresolved")
        if not now_playing_title_resolved:
            blocking_reasons.append("now_playing_title_unresolved")
        if not candidate_payload_ready:
            blocking_reasons.append("candidate_payload_not_ready")
        if not route_trace_present:
            blocking_reasons.append("route_trace_missing")
        if not no_authority_expansion:
            blocking_reasons.append("authority_mode_not_legacy")
        if paused_without_fresh_signal and now_playing_title_resolved:
            blocking_reasons.append("paused_without_recent_progress")
        elif not now_playing_fresh_play_signal and now_playing_title_resolved:
            blocking_reasons.append("no_fresh_play_signal")

        verdict = "PASS"
        if len(missing_required) > 0 or not contract_valid:
            verdict = "FAIL"
        elif (
            not active_meta_entity_resolved
            or not now_playing_entity_resolved
            or not now_playing_state_resolved
            or not route_trace_present
        ):
            verdict = "FAIL"
        elif not no_authority_expansion:
            verdict = "WARN"
        elif paused_without_fresh_signal and now_playing_title_resolved:
            verdict = "WARN"
        elif not now_playing_title_resolved or not candidate_payload_ready:
            verdict = "WARN"

        return {
            "verdict": verdict,
            "ready_for_metadata_handoff": verdict == "PASS",
            "required_entities": required_entities,
            "missing_required": missing_required,
            "contract_valid": contract_valid,
            "route_decision": route_decision,
            "gate_score": gate_score,
            "gate_max": gate_max,
            "blocking_reasons": blocking_reasons,
            "metadata_authority_owner": metadata_authority_owner,
            "metadata_cutover_active": metadata_cutover_active,
            "cutover_block_reason": cutover_block_reason,
            "checks": {
                "active_meta_entity_resolved": active_meta_entity_resolved,
                "now_playing_entity_resolved": now_playing_entity_resolved,
                "now_playing_state_resolved": now_playing_state_resolved,
                "now_playing_title_resolved": now_playing_title_resolved,
                "candidate_payload_ready": candidate_payload_ready,
                "route_trace_present": route_trace_present,
                "no_authority_expansion": no_authority_expansion,
                "now_playing_fresh_play_signal": now_playing_fresh_play_signal,
                "now_playing_paused_without_fresh_signal": paused_without_fresh_signal,
            },
            "values": {
                "active_meta_entity": active_meta_entity,
                "now_playing_entity": now_playing_entity,
                "now_playing_state": now_playing_state,
                "now_playing_title": now_playing_title,
                "now_playing_position_age_s": now_playing_signal.get("position_age_s"),
            },
        }

    def _build_capability_profile_validation(
        self,
        *,
        registry: dict[str, Any],
        route_trace: dict[str, Any],
        contract_validation: dict[str, Any],
        metadata_prep_validation: dict[str, Any],
    ) -> dict[str, Any]:
        entries = registry.get("entries", {}) if isinstance(registry.get("entries", {}), dict) else {}
        targets = list(entries.values()) if isinstance(entries, dict) else []

        control_path_counts: dict[str, int] = {}
        hardware_family_counts: dict[str, int] = {}
        capabilities_union: set[str] = set()
        control_capable_count = 0

        for entry in targets:
            if not isinstance(entry, dict):
                continue
            control_path = str(entry.get("control_path", "unknown") or "unknown")
            hardware_family = str(entry.get("hardware_family", "unknown") or "unknown")
            control_path_counts[control_path] = control_path_counts.get(control_path, 0) + 1
            hardware_family_counts[hardware_family] = hardware_family_counts.get(hardware_family, 0) + 1

            if bool(entry.get("control_capable", False)):
                control_capable_count += 1

            caps = entry.get("capabilities", [])
            if isinstance(caps, list):
                for cap in caps:
                    if isinstance(cap, str) and cap.strip():
                        capabilities_union.add(cap.strip())

        route_decision = str(route_trace.get("decision", "") or "")
        contract_valid = bool(contract_validation.get("valid", False))
        metadata_ready = bool(metadata_prep_validation.get("ready_for_metadata_handoff", False))

        checks = {
            "registry_present": len(targets) > 0,
            "capability_matrix_present": len(control_path_counts) > 0,
            "route_trace_present": route_decision != "",
            "contract_valid": contract_valid,
            "metadata_prep_ready": metadata_ready,
            "no_authority_expansion": self._write_authority_mode == WRITE_AUTH_LEGACY,
        }

        verdict = "PASS"
        if not checks["registry_present"] or not checks["route_trace_present"] or not checks["contract_valid"]:
            verdict = "FAIL"
        elif (
            not checks["capability_matrix_present"]
            or not checks["metadata_prep_ready"]
            or not checks["no_authority_expansion"]
        ):
            verdict = "WARN"

        profile_schema = {
            "schema_version": "f4_s01.v1",
            "required_keys": [
                "profile_id",
                "label",
                "target_scope",
                "routing_policy",
                "safety",
            ],
            "defaults": {
                "target_scope": "active_target",
                "routing_policy": "capability_mapped",
                "safety": {
                    "confirm_required": False,
                    "cooldown_s": 0,
                },
            },
        }

        return {
            "verdict": verdict,
            "ready_for_f4_s01": verdict == "PASS",
            "checks": checks,
            "authority_mode": self._write_authority_mode,
            "route_decision": route_decision,
            "capability_matrix": {
                "target_count": len(targets),
                "control_capable_count": control_capable_count,
                "control_path_counts": control_path_counts,
                "hardware_family_counts": hardware_family_counts,
                "capabilities": sorted(capabilities_union),
                "sample_targets": sorted([str(t.get("target", "")) for t in targets if isinstance(t, dict) and t.get("target")])[:5],
            },
            "profile_schema": profile_schema,
        }

    def _build_action_catalog_validation(
        self,
        *,
        registry: dict[str, Any],
        contract_validation: dict[str, Any],
        capability_profile_validation: dict[str, Any],
    ) -> dict[str, Any]:
        entries = registry.get("entries", {}) if isinstance(registry.get("entries", {}), dict) else {}
        targets = list(entries.values()) if isinstance(entries, dict) else []

        capabilities_union: set[str] = set()
        for entry in targets:
            if not isinstance(entry, dict):
                continue
            caps = entry.get("capabilities", [])
            if isinstance(caps, list):
                for cap in caps:
                    if isinstance(cap, str) and cap.strip():
                        capabilities_union.add(cap.strip())

        action_schema = {
            "schema_version": "f4_s02.v1",
            "required_keys": [
                "action_id",
                "label",
                "domain",
                "service",
                "target_scope",
                "safety",
            ],
            "safety_required_keys": [
                "confirm_required",
                "cooldown_s",
                "sensitive",
                "audit_event",
            ],
            "defaults": {
                "target_scope": "active_target",
                "dry_run_only": True,
                "safety": {
                    "confirm_required": True,
                    "cooldown_s": 3,
                    "sensitive": True,
                },
            },
        }

        action_catalog = [
            {
                "action_id": "transport_play_pause",
                "label": "Play/Pause",
                "domain": "media_player",
                "service": "media_play_pause",
                "target_scope": "active_target",
                "requires_capabilities": [],
                "dry_run_only": True,
                "safety": {
                    "confirm_required": False,
                    "cooldown_s": 0,
                    "sensitive": False,
                    "audit_event": "transport_play_pause",
                },
            },
            {
                "action_id": "safe_scene_trigger",
                "label": "Run Safe Scene",
                "domain": "scene",
                "service": "turn_on",
                "target_scope": "profile_scope",
                "requires_capabilities": [],
                "dry_run_only": True,
                "safety": {
                    "confirm_required": True,
                    "cooldown_s": 5,
                    "sensitive": True,
                    "audit_event": "safe_scene_trigger",
                },
            },
        ]

        contract_valid = bool(contract_validation.get("valid", False))
        capability_profile_ready = bool(capability_profile_validation.get("ready_for_f4_s01", False))
        no_authority_expansion = self._write_authority_mode == WRITE_AUTH_LEGACY

        schema_required = action_schema.get("required_keys", [])
        schema_safety_required = action_schema.get("safety_required_keys", [])

        dry_run_only = all(bool(action.get("dry_run_only", False)) for action in action_catalog)

        checks = {
            "registry_present": len(targets) > 0,
            "contract_valid": contract_valid,
            "capability_profile_ready": capability_profile_ready,
            "action_schema_present": isinstance(schema_required, list)
            and len(schema_required) > 0
            and isinstance(schema_safety_required, list)
            and len(schema_safety_required) > 0,
            "action_catalog_present": len(action_catalog) > 0,
            "dry_run_only": dry_run_only,
            "no_authority_expansion": no_authority_expansion,
        }

        verdict = "PASS"
        if (
            not checks["registry_present"]
            or not checks["contract_valid"]
            or not checks["action_schema_present"]
            or not checks["action_catalog_present"]
        ):
            verdict = "FAIL"
        elif (
            not checks["capability_profile_ready"]
            or not checks["dry_run_only"]
            or not checks["no_authority_expansion"]
        ):
            verdict = "WARN"

        confirm_required_count = 0
        sensitive_count = 0
        max_cooldown_s = 0
        for action in action_catalog:
            safety = action.get("safety", {}) if isinstance(action.get("safety", {}), dict) else {}
            if bool(safety.get("confirm_required", False)):
                confirm_required_count += 1
            if bool(safety.get("sensitive", False)):
                sensitive_count += 1
            cooldown = safety.get("cooldown_s", 0)
            if isinstance(cooldown, (int, float)):
                max_cooldown_s = max(max_cooldown_s, int(cooldown))

        return {
            "verdict": verdict,
            "ready_for_f4_s02": verdict == "PASS",
            "checks": checks,
            "authority_mode": self._write_authority_mode,
            "capability_reference": {
                "ready_for_f4_s01": capability_profile_ready,
                "schema_version": capability_profile_validation.get("profile_schema", {}).get("schema_version", "missing")
                if isinstance(capability_profile_validation.get("profile_schema", {}), dict)
                else "missing",
            },
            "action_schema": action_schema,
            "action_catalog": action_catalog,
            "catalog_summary": {
                "action_count": len(action_catalog),
                "confirm_required_count": confirm_required_count,
                "sensitive_count": sensitive_count,
                "max_cooldown_s": max_cooldown_s,
                "capability_pool": sorted(capabilities_union),
            },
        }

    def _build_crossfade_balance_validation(
        self,
        *,
        route_trace: dict[str, Any],
        contract_validation: dict[str, Any],
        action_catalog_validation: dict[str, Any] | None,
    ) -> dict[str, Any]:
        action_validation = action_catalog_validation if isinstance(action_catalog_validation, dict) else {}
        route_decision = str(route_trace.get("decision", "") or "")
        active_target = str(route_trace.get("active_target", "") or "").strip()
        active_target_resolved = active_target.lower() not in {"", "none", "unknown", "unavailable"}
        contract_valid = bool(contract_validation.get("valid", False))
        f4_s02_ready = bool(action_validation.get("ready_for_f4_s02", False))

        slider_domain_schema = {
            "schema_version": "f4_s03.v1",
            "domain": [-100, 100],
            "center": 0,
            "step": 1,
            "required_keys": [
                "mode",
                "value",
                "target_scope",
                "safety",
            ],
            "safety_required_keys": [
                "dry_run_only",
                "cooldown_s",
                "audit_event",
            ],
        }

        mode_profiles = {
            "multi_room": {
                "intent": "room_weight_balance",
                "value_map": "negative=weight_room_a, positive=weight_room_b",
                "supports_write": False,
            },
            "single_room": {
                "intent": "stereo_lr_balance",
                "value_map": "negative=left_bias, positive=right_bias",
                "supports_write": False,
            },
        }

        sample_mix_plan = {
            "dry_run_only": True,
            "samples": {
                "-100": {"multi_room": {"room_a": 1.0, "room_b": 0.0}, "single_room": {"left": 1.0, "right": 0.0}},
                "0": {"multi_room": {"room_a": 0.5, "room_b": 0.5}, "single_room": {"left": 0.5, "right": 0.5}},
                "100": {"multi_room": {"room_a": 0.0, "room_b": 1.0}, "single_room": {"left": 0.0, "right": 1.0}},
            },
            "fallback": "hold_current_mix_and_emit_notice",
        }

        schema_required = slider_domain_schema.get("required_keys", [])
        schema_safety_required = slider_domain_schema.get("safety_required_keys", [])

        checks = {
            "payload_present": True,
            "contract_valid": contract_valid,
            "route_trace_present": route_decision != "",
            "f4_s02_ready": f4_s02_ready,
            "slider_schema_present": isinstance(schema_required, list)
            and len(schema_required) > 0
            and isinstance(schema_safety_required, list)
            and len(schema_safety_required) > 0,
            "mode_profiles_present": isinstance(mode_profiles, dict)
            and "multi_room" in mode_profiles
            and "single_room" in mode_profiles,
            "no_authority_expansion": self._write_authority_mode == WRITE_AUTH_LEGACY,
            "snapshot_fresh": True,
        }

        verdict = "PASS"
        if not checks["contract_valid"] or not checks["route_trace_present"]:
            verdict = "FAIL"
        elif (
            not checks["f4_s02_ready"]
            or not checks["slider_schema_present"]
            or not checks["mode_profiles_present"]
            or not checks["no_authority_expansion"]
        ):
            verdict = "WARN"

        blocking_reasons: list[str] = []
        if not checks["contract_valid"]:
            blocking_reasons.append("contract_invalid")
        if not checks["route_trace_present"]:
            blocking_reasons.append("route_trace_missing")
        if not checks["f4_s02_ready"]:
            blocking_reasons.append("f4_s02_not_ready")
        if not active_target_resolved:
            blocking_reasons.append("active_target_unresolved")
        if route_decision == "defer_no_target":
            blocking_reasons.append("route_deferred_no_target")
        if not checks["slider_schema_present"]:
            blocking_reasons.append("slider_schema_missing")
        if not checks["mode_profiles_present"]:
            blocking_reasons.append("mode_profiles_missing")
        if not checks["no_authority_expansion"]:
            blocking_reasons.append("authority_expansion_detected")

        return {
            "verdict": verdict,
            "ready_for_f4_s03": verdict == "PASS",
            "checks": checks,
            "authority_mode": self._write_authority_mode,
            "route_decision": route_decision,
            "dependency_reference": {
                "ready_for_f4_s02": f4_s02_ready,
                "active_target": active_target,
                "active_target_resolved": active_target_resolved,
                "route_decision": route_decision,
                "blocking_reasons": blocking_reasons,
                "schema_version": action_validation.get("action_schema", {}).get("schema_version", "missing")
                if isinstance(action_validation.get("action_schema", {}), dict)
                else "missing",
            },
            "slider_domain_schema": slider_domain_schema,
            "mode_profiles": mode_profiles,
            "sample_mix_plan": sample_mix_plan,
        }

    def _build_snapshot(self) -> dict[str, Any]:
        active_target = self._snapshot_for_entity(LEGACY_SURFACES["active_target"])
        active_control_path = self._snapshot_for_entity(LEGACY_SURFACES["active_control_path"])
        control_hosts = self._snapshot_for_entity(LEGACY_SURFACES["control_hosts"])
        active_control_capable = self._snapshot_for_entity(
            LEGACY_SURFACES["active_control_capable"],
            as_bool=True,
        )

        legacy = {
            "active_target": active_target.state,
            "active_control_path": active_control_path.state,
            "control_hosts": control_hosts.state,
            "active_control_capable": active_control_capable.value,
        }

        parity = {
            "active_target": active_target.value,
            "active_control_path": active_control_path.value,
            "control_hosts": control_hosts.value,
            "active_control_capable": active_control_capable.value,
        }

        unresolved_sources: list[str] = []
        for key, snapshot in {
            "active_target": active_target,
            "active_control_path": active_control_path,
            "control_hosts": control_hosts,
            "active_control_capable": active_control_capable,
        }.items():
            if not snapshot.available:
                unresolved_sources.append(key)

        mismatches = [
            key
            for key in ("active_target", "active_control_path", "control_hosts", "active_control_capable")
            if parity[key] != legacy[key]
        ]

        registry = build_registry_snapshot(
            hass=self.hass,
            legacy_control_host_entity=LEGACY_CONTROL_HOST,
            legacy_control_targets_entity=LEGACY_CONTROL_TARGETS,
            legacy_rooms_json_entity=LEGACY_ROOMS_JSON,
            legacy_rooms_raw_entity=LEGACY_ROOMS_RAW,
        )

        route_trace = build_route_trace(
            active_target=str(parity.get("active_target", "") or ""),
            active_control_path=str(parity.get("active_control_path", "") or ""),
            registry=registry,
        )

        contract_validation = self._build_contract_validation()
        selection_handoff_validation = self._build_selection_handoff_validation(
            parity=parity,
            route_trace=route_trace,
            contract_validation=contract_validation,
        )
        metadata_prep_validation = self._build_metadata_prep_validation(
            route_trace=route_trace,
            contract_validation=contract_validation,
        )
        capability_profile_validation = self._build_capability_profile_validation(
            registry=registry,
            route_trace=route_trace,
            contract_validation=contract_validation,
            metadata_prep_validation=metadata_prep_validation,
        )
        action_catalog_validation = self._build_action_catalog_validation(
            registry=registry,
            contract_validation=contract_validation,
            capability_profile_validation=capability_profile_validation,
        ) or {}
        crossfade_balance_validation = self._build_crossfade_balance_validation(
            route_trace=route_trace,
            contract_validation=contract_validation,
            action_catalog_validation=action_catalog_validation,
        )

        return {
            "legacy": legacy,
            "parity": parity,
            "unresolved_sources": unresolved_sources,
            "mismatches": mismatches,
            "registry": registry,
            "route_trace": route_trace,
            "contract_validation": contract_validation,
            "selection_handoff_validation": selection_handoff_validation,
            "metadata_prep_validation": metadata_prep_validation,
            "capability_profile_validation": capability_profile_validation,
            "action_catalog_validation": action_catalog_validation,
            "crossfade_balance_validation": crossfade_balance_validation,
            "write_controls": self._build_write_controls(),
            "captured_at": datetime.now(UTC).isoformat(),
        }

    async def async_rebuild_registry(self) -> None:
        """Refresh parity data, including registry scaffold snapshot."""
        self.async_set_updated_data(self._build_snapshot())

    async def async_validate_contracts(self) -> None:
        """Refresh parity data and emit contract validation visibility in snapshot."""
        data = self._build_snapshot()
        data["contract_validation"] = self._build_contract_validation()
        self.async_set_updated_data(data)

    async def async_dump_route_trace(self) -> None:
        """Refresh parity data so latest route trace appears in diagnostics."""
        self.async_set_updated_data(self._build_snapshot())

    async def async_validate_selection_handoff(self) -> None:
        """Refresh parity data and emit selection-handoff validation diagnostics."""
        self.async_set_updated_data(self._build_snapshot())

    async def async_validate_metadata_prep(self) -> None:
        """Refresh parity data and emit metadata-prep validation diagnostics."""
        self.async_set_updated_data(self._build_snapshot())

    async def async_validate_capability_profile(self) -> None:
        """Refresh parity data and emit F4-S01 capability/profile diagnostics."""
        self.async_set_updated_data(self._build_snapshot())

    async def async_validate_action_catalog(self) -> None:
        """Refresh parity data and emit F4-S02 action-catalog safety diagnostics."""
        self.async_set_updated_data(self._build_snapshot())

    async def async_validate_crossfade_balance(self) -> None:
        """Refresh parity data and emit F4-S03 crossfade/balance diagnostics."""
        self.async_set_updated_data(self._build_snapshot())

    async def async_set_write_authority(self, mode: str, reason: str = "") -> None:
        """Set write authority mode for guarded routing write-path trials."""
        normalized_mode = self._normalize_write_authority(mode)
        self._write_authority_mode = normalized_mode
        self._last_write_attempt = {
            "status": "authority_set",
            "timestamp": datetime.now(UTC).isoformat(),
            "authority_mode": normalized_mode,
            "reason": (reason or "").strip() or "Authority mode updated",
            "correlation_id": f"authority-{uuid4().hex[:12]}",
        }
        self.async_set_updated_data(self._build_snapshot())

    async def async_route_write_trial(self, correlation_id: str | None = None, force: bool = False) -> None:
        """Attempt a guarded routing write to the active-target helper."""
        corr = (correlation_id or "").strip() or f"route-write-{uuid4().hex[:12]}"
        now_iso = datetime.now(UTC).isoformat()
        snapshot = self._build_snapshot()
        route_trace = snapshot.get("route_trace", {})
        active_target = str(route_trace.get("active_target", "") or "").strip()
        route_decision = str(route_trace.get("decision", "") or "").strip()
        helper_state = self.hass.states.get(LEGACY_ACTIVE_TARGET_HELPER)

        result: dict[str, Any] = {
            "timestamp": now_iso,
            "correlation_id": corr,
            "authority_mode": self._write_authority_mode,
            "force": bool(force),
            "route_decision": route_decision,
            "active_target": active_target,
            "target_helper_entity": LEGACY_ACTIVE_TARGET_HELPER,
        }

        if self._write_authority_mode != WRITE_AUTH_COMPONENT:
            result.update(
                {
                    "status": "blocked_authority",
                    "reason": "Write authority is legacy; component write is intentionally blocked",
                }
            )
        elif self._write_in_progress and not force:
            result.update(
                {
                    "status": "blocked_reentrancy",
                    "reason": "A prior write attempt is still in progress",
                }
            )
        elif not force and self._last_write_monotonic > 0:
            elapsed = monotonic() - self._last_write_monotonic
            if elapsed < self._write_debounce_s:
                result.update(
                    {
                        "status": "blocked_debounce",
                        "reason": "Debounce guard active",
                        "elapsed_s": round(elapsed, 3),
                        "debounce_s": self._write_debounce_s,
                    }
                )
        if "status" not in result and route_decision != "route_linkplay_tcp":
            result.update(
                {
                    "status": "blocked_route_decision",
                    "reason": "Route decision is not eligible for P3-S01 routing write trial",
                }
            )
        if "status" not in result and active_target.lower() in {"", "none", "unknown", "unavailable"}:
            result.update(
                {
                    "status": "blocked_target_missing",
                    "reason": "Active target is unresolved",
                }
            )
        if "status" not in result and helper_state is None:
            result.update(
                {
                    "status": "blocked_missing_target_helper",
                    "reason": "Target helper entity is missing",
                }
            )

        helper_options: list[str] = []
        if helper_state is not None:
            options_attr = helper_state.attributes.get("options", [])
            if isinstance(options_attr, list):
                helper_options = [str(item) for item in options_attr if isinstance(item, str)]

        if "status" not in result and helper_options and active_target not in helper_options:
            result.update(
                {
                    "status": "blocked_option_mismatch",
                    "reason": "Active target is not present in helper options",
                    "helper_options_count": len(helper_options),
                }
            )

        helper_current = helper_state.state if helper_state is not None else ""
        if "status" not in result and helper_current == active_target:
            result.update(
                {
                    "status": "noop_already_selected",
                    "reason": "Target helper already matches active target",
                }
            )

        if "status" not in result:
            self._write_in_progress = True
            try:
                await self.hass.services.async_call(
                    "input_select",
                    "select_option",
                    {
                        "entity_id": LEGACY_ACTIVE_TARGET_HELPER,
                        "option": active_target,
                    },
                    blocking=True,
                )
                result.update(
                    {
                        "status": "write_applied",
                        "reason": "Guarded routing write was applied successfully",
                    }
                )
            except Exception as err:  # pragma: no cover - defensive runtime guard
                result.update(
                    {
                        "status": "write_error",
                        "reason": "Service call failed during guarded routing write",
                        "error": str(err),
                    }
                )
            finally:
                self._write_in_progress = False

        self._last_write_monotonic = monotonic()
        self._last_write_attempt = result
        self.async_set_updated_data(self._build_snapshot())

    async def async_metadata_write_trial(
        self,
        *,
        mode: str,
        window_id: str,
        reason: str,
        dry_run: bool,
        expected_target: str | None,
        expected_route: str | None,
        correlation_id: str | None,
    ) -> None:
        """Run a fail-closed metadata trial contract with audit payload emission."""
        requested_at = datetime.now(UTC).isoformat()
        completed_at = requested_at
        corr = (correlation_id or "").strip() or f"metadata-trial-{uuid4().hex[:12]}"
        requested_mode = self._normalize_write_authority(mode)
        effective_mode = self._write_authority_mode
        window = (window_id or "").strip()
        operator_reason = (reason or "").strip()
        expected_target_norm = (expected_target or "").strip()
        expected_route_norm = (expected_route or "").strip()

        snapshot = self._build_snapshot()
        route_trace = snapshot.get("route_trace", {}) if isinstance(snapshot.get("route_trace", {}), dict) else {}
        contract_validation = (
            snapshot.get("contract_validation", {}) if isinstance(snapshot.get("contract_validation", {}), dict) else {}
        )
        metadata_validation = (
            snapshot.get("metadata_prep_validation", {})
            if isinstance(snapshot.get("metadata_prep_validation", {}), dict)
            else {}
        )

        active_target = str(route_trace.get("active_target", "") or "").strip()
        route_decision = str(route_trace.get("decision", "") or "").strip()
        contract_valid = bool(contract_validation.get("valid", False))
        metadata_ready = bool(metadata_validation.get("ready_for_metadata_handoff", False))

        result: dict[str, Any] = {
            "requested_at": requested_at,
            "completed_at": completed_at,
            "window_id": window,
            "requested_mode": requested_mode,
            "effective_mode": effective_mode,
            "dry_run": bool(dry_run),
            "reason": operator_reason,
            "correlation_id": corr,
            "expected_target": expected_target_norm,
            "expected_route": expected_route_norm,
            "active_target": active_target,
            "route_decision": route_decision,
            "contract_valid": contract_valid,
            "metadata_ready": metadata_ready,
        }

        if not window:
            result.update(
                {
                    "status": "blocked_missing_window_id",
                    "reason": "window_id is required for bounded metadata trial auditability",
                }
            )
        elif not operator_reason:
            result.update(
                {
                    "status": "blocked_missing_reason",
                    "reason": "reason is required for metadata trial auditability",
                }
            )
        elif self._metadata_trial_in_progress:
            result.update(
                {
                    "status": "blocked_reentrancy",
                    "reason": "A prior metadata trial attempt is still in progress",
                }
            )
        elif self._write_authority_mode != WRITE_AUTH_LEGACY:
            result.update(
                {
                    "status": "blocked_authority_not_legacy",
                    "reason": "Metadata trial contract requires legacy authority baseline",
                }
            )
        elif not contract_valid:
            result.update(
                {
                    "status": "blocked_contract_invalid",
                    "reason": "Required contract entities are missing; fail-closed",
                }
            )
        elif not metadata_ready:
            result.update(
                {
                    "status": "blocked_metadata_not_ready",
                    "reason": "Metadata prep validation is not PASS/ready; fail-closed",
                }
            )
        elif expected_route_norm and route_decision != expected_route_norm:
            result.update(
                {
                    "status": "blocked_expected_route_mismatch",
                    "reason": "Observed route decision does not match expected_route",
                }
            )
        elif expected_target_norm and active_target != expected_target_norm:
            result.update(
                {
                    "status": "blocked_expected_target_mismatch",
                    "reason": "Observed active target does not match expected_target",
                }
            )
        elif not dry_run and requested_mode != WRITE_AUTH_LEGACY:
            result.update(
                {
                    "status": "blocked_nonlegacy_non_dry_run",
                    "reason": "Non-dry-run metadata trial is currently restricted to legacy mode",
                }
            )
        else:
            self._metadata_trial_in_progress = True
            try:
                if dry_run:
                    result.update(
                        {
                            "status": "dry_run_ok",
                            "reason": "Metadata trial contract preflight passed (dry run)",
                        }
                    )
                else:
                    result.update(
                        {
                            "status": "noop_applied",
                            "reason": "Metadata trial contract executed with no write-side effects",
                        }
                    )
            finally:
                self._metadata_trial_in_progress = False

        result["effective_mode"] = self._write_authority_mode
        result["completed_at"] = datetime.now(UTC).isoformat()
        missing_audit_fields = self._metadata_trial_audit_missing_fields(result)
        audit_payload_complete = len(missing_audit_fields) == 0
        result["audit_payload_complete"] = audit_payload_complete
        result["missing_audit_fields"] = missing_audit_fields
        result["audit_payload_state"] = "COMPLETE" if audit_payload_complete else "PARTIAL"
        self._last_metadata_trial_attempt = result
        self.async_set_updated_data(self._build_snapshot())

    @callback
    def _handle_state_change(self, _event) -> None:
        try:
            self.async_set_updated_data(self._build_snapshot())
        except Exception:  # pragma: no cover - defensive callback hardening
            _LOGGER.exception("Failed to refresh Spectra LS snapshot on state-change event")
