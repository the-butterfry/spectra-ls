# Description: Data coordinator for Spectra LS parity diagnostics, Phase 3 guarded routing write-path controls, and Phase 4 diagnostics scaffolding.
# Version: 2026.04.19.9
# Last updated: 2026-04-19

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
        return {
            "required_entities": required_entities,
            "missing_required": missing_required,
            "valid": len(missing_required) == 0,
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
        elif not now_playing_title_resolved or not candidate_payload_ready:
            verdict = "WARN"

        return {
            "verdict": verdict,
            "ready_for_metadata_handoff": verdict == "PASS",
            "required_entities": required_entities,
            "missing_required": missing_required,
            "contract_valid": contract_valid,
            "route_decision": route_decision,
            "checks": {
                "active_meta_entity_resolved": active_meta_entity_resolved,
                "now_playing_entity_resolved": now_playing_entity_resolved,
                "now_playing_state_resolved": now_playing_state_resolved,
                "now_playing_title_resolved": now_playing_title_resolved,
                "candidate_payload_ready": candidate_payload_ready,
                "route_trace_present": route_trace_present,
            },
            "values": {
                "active_meta_entity": active_meta_entity,
                "now_playing_entity": now_playing_entity,
                "now_playing_state": now_playing_state,
                "now_playing_title": now_playing_title,
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

    @callback
    def _handle_state_change(self, _event) -> None:
        self.async_set_updated_data(self._build_snapshot())
