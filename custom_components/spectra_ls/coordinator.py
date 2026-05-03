# Description: Data coordinator for Spectra LS parity diagnostics, Phase 3 guarded routing write-path controls, Phase 4 diagnostics scaffolding (F4-S01/F4-S03), Phase 5 metadata trial contract auditing, and Phase 6/8 control-center settings, fast-remap, execution visibility, startup auto-recovery orchestration (latency-hardened cadence), and selection-lock lifecycle parity migration (ambiguity lock, stale unlock, auto-select loop).
# Version: 2026.05.03.17
# Last updated: 2026-05-03
# PARITY DIRECTIVE (until full cutover): behavior/contract edits here require same-slice two-track parity review
# and version-metadata review in runtime (`packages/` + `esphome/`) and component (`custom_components/spectra_ls/`) tracks.

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import importlib
import json
import logging
from time import monotonic
from typing import Any
from uuid import uuid4

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONTROL_CENTER_INPUT_EVENTS,
    DOMAIN,
    FABRIC_AUTH_MODE_DEGRADED_FALLBACK,
    FABRIC_AUTH_MODE_PRIMARY,
    FABRIC_AUTH_REASON_API_UNREACHABLE,
    FABRIC_AUTH_REASON_DEGRADED_ACTIVE,
    FABRIC_AUTH_REASON_PAYLOAD_SHAPE_INVALID,
    FABRIC_AUTH_REASON_PAYLOAD_STALE,
    LEGACY_ACTIVE_META_ENTITY,
    LEGACY_LAST_VALID_TARGET,
    LEGACY_META_DETECTED_ENTITY,
    LEGACY_META_OVERRIDE_ACTIVE,
    LEGACY_META_OVERRIDE_ENTITY,
    LEGACY_META_PAUSED_HIDE_S,
    LEGACY_META_RESOLVER,
    LEGACY_META_STALE_S,
    LEGACY_META_CONFIDENCE_MIN,
    LEGACY_CONTROL_HOST,
    LEGACY_CONTROL_TARGETS,
    LEGACY_META_CANDIDATES,
    LEGACY_META_STALE,
    LEGACY_CONTROL_AMBIGUOUS,
    LEGACY_NO_CONTROL_CAPABLE_HOSTS,
    LEGACY_MA_PLAYERS,
    LEGACY_OVERRIDE_ACTIVE,
    LEGACY_SERVER_PROFILE,
    LEGACY_SERVER_PROFILE_EFFECTIVE,
    LEGACY_ACTIVE_TARGET_HELPER,
    LEGACY_NOW_PLAYING_ENTITY,
    LEGACY_NOW_PLAYING_MEDIA_CLASS,
    LEGACY_NOW_PLAYING_PREVIEW_KEY,
    LEGACY_NOW_PLAYING_DISPLAY_ALLOWED,
    LEGACY_NOW_PLAYING_STATE,
    LEGACY_NOW_PLAYING_TITLE,
    LEGACY_NOW_PLAYING_POSITION,
    LEGACY_NOW_PLAYING_DURATION,
    LEGACY_ACTIVE_DURATION,
    LEGACY_ROOMS_JSON,
    LEGACY_ROOMS_RAW,
    LEGACY_SURFACES,
    META_POLICY_DEFAULTS,
    META_SUPPRESSION_ENTITY_MISSING,
    META_SUPPRESSION_LONG_IDLE,
    META_SUPPRESSION_NO_FRESH_SIGNAL,
    META_SUPPRESSION_PAUSED_FRESH,
    META_SUPPRESSION_PAUSED_STALE,
    META_SUPPRESSION_PLAYING,
    META_SUPPRESSION_PLAYING_STALE,
    WRITE_AUTH_ALLOWED,
    WRITE_AUTH_COMPONENT,
    WRITE_AUTH_LEGACY,
    WRITE_DEBOUNCE_SECONDS,
    normalize_control_center_settings,
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

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=f"{DOMAIN}_shadow_parity",
        )
        self._entry = entry
        self._unsub_state_events = None
        self._unsub_global_state_events = None
        self._meta_stale_unlock_unsub = None
        self._write_authority_mode = WRITE_AUTH_LEGACY
        self._write_debounce_s = float(WRITE_DEBOUNCE_SECONDS)
        self._control_center_settings = normalize_control_center_settings(entry.options)
        self._last_control_center_action_attempt: dict[str, Any] = {
            "status": "never_attempted",
            "requested_at": None,
            "completed_at": None,
            "input_event": None,
            "mapped_action": None,
            "reason": "No control-center actions attempted yet",
        }
        self._write_in_progress = False
        self._last_write_monotonic = 0.0
        self._last_write_attempt: dict[str, Any] = {
            "status": "never_attempted",
            "timestamp": None,
            "reason": "No write attempts yet",
        }
        self._snapshot_refresh_min_interval_s = 0.75
        self._last_snapshot_refresh_monotonic = 0.0
        self._deferred_snapshot_refresh_unsub = None
        self._last_scheduler_decision: dict[str, Any] = {
            "status": "never_attempted",
            "requested_at": None,
            "completed_at": None,
            "selected_target": "",
            "reason": "No scheduler decisions requested yet",
            "policy": {},
            "ranked_candidates": [],
        }
        self._last_scheduler_apply: dict[str, Any] = {
            "status": "never_attempted",
            "requested_at": None,
            "completed_at": None,
            "selected_target": "",
            "reason": "No scheduler apply attempts requested yet",
            "policy": {},
            "dry_run": True,
            "force": False,
            "ranked_candidates": [],
        }
        self._last_target_options_attempt: dict[str, Any] = {
            "status": "never_attempted",
            "requested_at": None,
            "completed_at": None,
            "reason": "No target-options scaffold attempts requested yet",
            "dry_run": True,
            "force": False,
            "planned_options": [],
            "applied_options": [],
        }
        self._last_auto_select_attempt: dict[str, Any] = {
            "status": "never_attempted",
            "requested_at": None,
            "completed_at": None,
            "reason": "No auto-select scaffold attempts requested yet",
            "dry_run": True,
            "force": False,
            "selected_target": "",
            "selection_reason": "",
        }
        self._last_cycle_target_attempt: dict[str, Any] = {
            "status": "never_attempted",
            "requested_at": None,
            "completed_at": None,
            "reason": "No component target-cycle attempts requested yet",
            "next_target": "",
        }
        self._last_restore_last_valid_attempt: dict[str, Any] = {
            "status": "never_attempted",
            "requested_at": None,
            "completed_at": None,
            "reason": "No component restore-last-valid attempts requested yet",
            "restored_target": "",
        }
        self._last_track_last_valid_attempt: dict[str, Any] = {
            "status": "never_attempted",
            "requested_at": None,
            "completed_at": None,
            "reason": "No component last-valid tracking attempts requested yet",
            "tracked_target": "",
        }
        self._startup_recovery_unsub = None
        self._startup_recovery_task = None
        self._startup_recovery_attempt = 0
        self._startup_recovery_max_attempts = 3
        self._startup_recovery_initial_delay_s = 4.0
        self._startup_recovery_retry_delay_s = 8.0
        self._startup_recovery_wait_cycles = 0
        self._startup_recovery_max_wait_cycles = 20
        self._no_control_feedback_hold_unsub = None
        self._no_control_feedback_post_heal_unsub = None
        self._no_control_feedback_notification_id = "spectra_ls_no_control_capable_hosts"
        metadata_stack_module = importlib.import_module(f"{__package__}.metadata_stack")
        metadata_stack_workflow_cls = getattr(metadata_stack_module, "MetadataStackWorkflow")
        self._metadata_stack: Any = metadata_stack_workflow_cls(self)
        meta_fabric_module = importlib.import_module(f"{__package__}.meta_fabric")
        meta_fabric_workflow_cls = getattr(meta_fabric_module, "MetaFabricWorkflow")
        self._meta_fabric: Any = meta_fabric_workflow_cls(self)

    @property
    def metadata_stack(self) -> Any:
        return self._metadata_stack

    @property
    def meta_fabric(self) -> Any:
        return self._meta_fabric

    async def async_setup(self) -> None:
        """Initialize data and state listeners."""
        await self.async_refresh()

        watched_entities = set(LEGACY_SURFACES.values())
        watched_entities.update(
            {
                LEGACY_ACTIVE_TARGET_HELPER,
                LEGACY_OVERRIDE_ACTIVE,
                LEGACY_META_STALE,
                LEGACY_META_DETECTED_ENTITY,
                LEGACY_CONTROL_AMBIGUOUS,
                LEGACY_ACTIVE_META_ENTITY,
                LEGACY_NOW_PLAYING_ENTITY,
                LEGACY_NOW_PLAYING_STATE,
                LEGACY_NOW_PLAYING_TITLE,
                LEGACY_META_CANDIDATES,
                LEGACY_CONTROL_HOST,
                LEGACY_CONTROL_TARGETS,
                LEGACY_SERVER_PROFILE,
                LEGACY_SERVER_PROFILE_EFFECTIVE,
                LEGACY_ROOMS_JSON,
                LEGACY_ROOMS_RAW,
                LEGACY_NO_CONTROL_CAPABLE_HOSTS,
            }
        )

        self._unsub_state_events = async_track_state_change_event(
            self.hass,
            sorted(watched_entities),
            self._handle_state_change,
        )
        self._unsub_global_state_events = self.hass.bus.async_listen(
            "state_changed",
            self._handle_global_state_change,
        )

    async def async_shutdown(self) -> None:
        """Detach listeners on unload."""
        if self._unsub_state_events is not None:
            self._unsub_state_events()
            self._unsub_state_events = None
        if self._unsub_global_state_events is not None:
            self._unsub_global_state_events()
            self._unsub_global_state_events = None
        if self._meta_stale_unlock_unsub is not None:
            self._meta_stale_unlock_unsub()
            self._meta_stale_unlock_unsub = None
        if self._deferred_snapshot_refresh_unsub is not None:
            self._deferred_snapshot_refresh_unsub()
            self._deferred_snapshot_refresh_unsub = None
        if self._startup_recovery_unsub is not None:
            self._startup_recovery_unsub()
            self._startup_recovery_unsub = None
        if self._startup_recovery_task is not None and not self._startup_recovery_task.done():
            self._startup_recovery_task.cancel()
        self._startup_recovery_task = None
        if self._no_control_feedback_hold_unsub is not None:
            self._no_control_feedback_hold_unsub()
            self._no_control_feedback_hold_unsub = None
        if self._no_control_feedback_post_heal_unsub is not None:
            self._no_control_feedback_post_heal_unsub()
            self._no_control_feedback_post_heal_unsub = None

    async def async_schedule_startup_recovery(self) -> None:
        """Schedule bounded post-startup recovery for target/options and bridge alignment."""
        await self._meta_fabric.async_schedule_startup_recovery()

    @callback
    def _handle_startup_recovery_timer(self, _now) -> None:
        """Kick off one startup recovery attempt from timer callback."""
        self._meta_fabric.handle_startup_recovery_timer(_now)

    async def _async_run_startup_recovery_attempt(self) -> None:
        """Run one bounded startup recovery attempt and schedule retry if needed."""
        await self._meta_fabric.async_run_startup_recovery_attempt()

    def _is_startup_recovery_boot_ready(self) -> tuple[bool, list[str]]:
        """Return whether MA/runtime surfaces are ready for startup recovery attempts."""
        return self._meta_fabric.is_startup_recovery_boot_ready()

    def _startup_wait_reason_prefix(self, reasons: list[str]) -> str:
        """Return human-readable startup wait prefix aligned to the blocking phase."""
        return self._meta_fabric.startup_wait_reason_prefix(reasons)

    def _format_startup_boot_wait_reasons(self, reasons: list[str]) -> str:
        """Format startup readiness blockers into operator-friendly wait messaging."""
        return self._meta_fabric.format_startup_boot_wait_reasons(reasons)

    def _refresh_snapshot(self, *, force: bool = False) -> None:
        now_mono = monotonic()
        if (
            not force
            and self._last_snapshot_refresh_monotonic > 0
            and (now_mono - self._last_snapshot_refresh_monotonic) < self._snapshot_refresh_min_interval_s
        ):
            return

        self._last_snapshot_refresh_monotonic = now_mono
        self.async_set_updated_data(self._build_snapshot())

    def build_snapshot(self) -> dict[str, Any]:
        """Build and return current parity snapshot payload."""
        return self._build_snapshot()

    def refresh_snapshot(self) -> None:
        """Refresh coordinator data immediately from a newly built snapshot."""
        self.async_set_updated_data(self._build_snapshot())

    @callback
    def _handle_deferred_snapshot_refresh(self, _now) -> None:
        self._deferred_snapshot_refresh_unsub = None
        try:
            self._refresh_snapshot(force=True)
        except Exception:  # pragma: no cover - defensive callback hardening
            _LOGGER.exception("Failed deferred Spectra LS snapshot refresh")

    async def _async_update_data(self) -> dict[str, Any]:
        """Read legacy surfaces and compute parity snapshot."""
        return self._build_snapshot()

    @staticmethod
    def _normalize_state(state_value: str) -> str:
        return (state_value or "").strip().lower()

    @staticmethod
    def _parse_jsonish_payload(raw: Any) -> Any:
        if isinstance(raw, (list, dict)):
            return raw
        if isinstance(raw, str):
            trimmed = raw.strip()
            if not trimmed:
                return None
            if not (trimmed.startswith("[") or trimmed.startswith("{")):
                return None
            try:
                return json.loads(trimmed)
            except json.JSONDecodeError:
                return None
        return None

    def _compute_component_target_options_plan(self) -> dict[str, Any]:
        return self._meta_fabric.compute_component_target_options_plan()

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
        meta_policy = self._meta_fabric.build_meta_policy_surface()
        metadata_surfaces = self._meta_fabric.build_write_controls_metadata_surfaces()

        return {
            "authority_mode": self._write_authority_mode,
            "allowed_modes": list(WRITE_AUTH_ALLOWED),
            "debounce_s": self._write_debounce_s,
            "in_progress": self._write_in_progress,
            "last_attempt": self._last_write_attempt,
            **metadata_surfaces,
            "scheduler_last_decision": self._last_scheduler_decision,
            "scheduler_last_apply": self._last_scheduler_apply,
            "target_options_last_attempt": self._last_target_options_attempt,
            "auto_select_last_attempt": self._last_auto_select_attempt,
            "cycle_target_last_attempt": self._last_cycle_target_attempt,
            "restore_last_valid_last_attempt": self._last_restore_last_valid_attempt,
            "track_last_valid_last_attempt": self._last_track_last_valid_attempt,
            "target_helper_entity": LEGACY_ACTIVE_TARGET_HELPER,
            "control_center_settings": self._control_center_settings,
            "control_center_last_attempt": self._last_control_center_action_attempt,
            "meta_policy": meta_policy,
        }

    def _read_float_helper(self, entity_id: str, default: float) -> float:
        state = self.hass.states.get(entity_id)
        if state is None:
            return float(default)
        raw = str(state.state or "").strip().lower()
        if raw in {"", "unknown", "unavailable", "none"}:
            return float(default)
        try:
            return float(state.state)
        except (TypeError, ValueError):
            return float(default)

    @staticmethod
    def _availability_points(quality: str) -> int:
        q = str(quality or "").strip().lower()
        if q == "fresh":
            return 15
        if q == "warm":
            return 8
        if q == "stale":
            return 2
        return 0

    @staticmethod
    def _empirical_bonus(overlay: dict[str, Any]) -> float:
        if not isinstance(overlay, dict) or len(overlay) == 0:
            return 0.0

        bonus = 0.0
        score = overlay.get("score")
        if isinstance(score, (int, float)):
            bonus += max(min(float(score) * 0.2, 20.0), -20.0)

        success_rate = overlay.get("success_rate")
        if isinstance(success_rate, (int, float)):
            bonus += max(min(float(success_rate), 1.0), 0.0) * 20.0

        confidence = overlay.get("confidence")
        if isinstance(confidence, (int, float)):
            bonus += max(min(float(confidence), 1.0), 0.0) * 10.0

        latency_ms = overlay.get("latency_ms")
        if isinstance(latency_ms, (int, float)):
            if float(latency_ms) > 250:
                bonus -= min((float(latency_ms) - 250.0) / 50.0, 10.0)

        return round(bonus, 2)

    def _compute_scheduler_decision(
        self,
        *,
        registry: dict[str, Any],
        route_trace: dict[str, Any],
        policy: dict[str, Any],
    ) -> dict[str, Any]:
        return self._meta_fabric.compute_scheduler_decision(
            registry=registry,
            route_trace=route_trace,
            policy=policy,
        )

    def _build_scheduler_validation(
        self,
        *,
        registry: dict[str, Any],
        route_trace: dict[str, Any],
        contract_validation: dict[str, Any],
    ) -> dict[str, Any]:
        return self._meta_fabric.build_scheduler_validation(
            registry=registry,
            route_trace=route_trace,
            contract_validation=contract_validation,
        )

    def _build_control_center_validation(self) -> dict[str, Any]:
        return self._meta_fabric.build_control_center_validation()

    def _build_handoff_inventory(self) -> dict[str, Any]:
        """Expose legacy-only dependency map and component scaffolding status for cutover planning."""
        return self._meta_fabric.build_handoff_inventory()

    def _build_host_control_cutover_gate(
        self,
        *,
        parity: dict[str, Any],
        registry: dict[str, Any],
        route_trace: dict[str, Any],
    ) -> dict[str, Any]:
        return self._meta_fabric.build_host_control_cutover_gate(
            parity=parity,
            registry=registry,
            route_trace=route_trace,
        )

    def _build_component_scaffolds(self) -> dict[str, Any]:
        """Build initial component-native scaffold plans for legacy selection ownership handoff."""
        return self._meta_fabric.build_component_scaffolds()

    def _build_contract_validation(self) -> dict[str, Any]:
        return self._meta_fabric.build_contract_validation()

    def _build_selection_handoff_validation(
        self,
        *,
        parity: dict[str, Any],
        route_trace: dict[str, Any],
        contract_validation: dict[str, Any],
    ) -> dict[str, Any]:
        return self._meta_fabric.build_selection_handoff_validation(
            parity=parity,
            route_trace=route_trace,
            contract_validation=contract_validation,
        )

    def _build_route_safety_validation(
        self,
        *,
        parity: dict[str, Any],
        route_trace: dict[str, Any],
    ) -> dict[str, Any]:
        return self._meta_fabric.build_route_safety_validation(
            parity=parity,
            route_trace=route_trace,
        )

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

    def _build_capability_profile_validation(
        self,
        *,
        registry: dict[str, Any],
        route_trace: dict[str, Any],
        contract_validation: dict[str, Any],
        metadata_prep_validation: dict[str, Any],
    ) -> dict[str, Any]:
        return self._meta_fabric.build_capability_profile_validation(
            registry=registry,
            route_trace=route_trace,
            contract_validation=contract_validation,
            metadata_prep_validation=metadata_prep_validation,
        )

    def _build_action_catalog_validation(
        self,
        *,
        registry: dict[str, Any],
        contract_validation: dict[str, Any],
        capability_profile_validation: dict[str, Any],
    ) -> dict[str, Any]:
        return self._meta_fabric.build_action_catalog_validation(
            registry=registry,
            contract_validation=contract_validation,
            capability_profile_validation=capability_profile_validation,
        )

    def _build_crossfade_balance_validation(
        self,
        *,
        route_trace: dict[str, Any],
        contract_validation: dict[str, Any],
        action_catalog_validation: dict[str, Any] | None,
    ) -> dict[str, Any]:
        return self._meta_fabric.build_crossfade_balance_validation(
            route_trace=route_trace,
            contract_validation=contract_validation,
            action_catalog_validation=action_catalog_validation,
        )

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
            legacy_active_target_helper_entity=LEGACY_ACTIVE_TARGET_HELPER,
            legacy_active_target_entity=LEGACY_SURFACES["active_target"],
        )

        route_trace = build_route_trace(
            active_target=str(parity.get("active_target", "") or ""),
            active_control_path=str(parity.get("active_control_path", "") or ""),
            registry=registry,
        )
        validation_packet = self._meta_fabric.build_snapshot_validation_packet(
            parity=parity,
            registry=registry,
            route_trace=route_trace,
        )
        host_control_cutover_gate = (
            validation_packet.get("host_control_cutover_gate", {})
            if isinstance(validation_packet.get("host_control_cutover_gate", {}), dict)
            else {}
        )
        contract_validation = (
            validation_packet.get("contract_validation", {})
            if isinstance(validation_packet.get("contract_validation", {}), dict)
            else {}
        )
        selection_handoff_validation = (
            validation_packet.get("selection_handoff_validation", {})
            if isinstance(validation_packet.get("selection_handoff_validation", {}), dict)
            else {}
        )
        route_safety_validation = (
            validation_packet.get("route_safety_validation", {})
            if isinstance(validation_packet.get("route_safety_validation", {}), dict)
            else {}
        )
        metadata_prep_validation = (
            validation_packet.get("metadata_prep_validation", {})
            if isinstance(validation_packet.get("metadata_prep_validation", {}), dict)
            else {}
        )
        metadata_bridge_validation = (
            validation_packet.get("metadata_bridge_validation", {})
            if isinstance(validation_packet.get("metadata_bridge_validation", {}), dict)
            else {}
        )
        cutover_prep_validation = (
            validation_packet.get("cutover_prep_validation", {})
            if isinstance(validation_packet.get("cutover_prep_validation", {}), dict)
            else {}
        )
        capability_profile_validation = (
            validation_packet.get("capability_profile_validation", {})
            if isinstance(validation_packet.get("capability_profile_validation", {}), dict)
            else {}
        )
        action_catalog_validation = (
            validation_packet.get("action_catalog_validation", {})
            if isinstance(validation_packet.get("action_catalog_validation", {}), dict)
            else {}
        )
        crossfade_balance_validation = (
            validation_packet.get("crossfade_balance_validation", {})
            if isinstance(validation_packet.get("crossfade_balance_validation", {}), dict)
            else {}
        )
        scheduler_validation = (
            validation_packet.get("scheduler_validation", {})
            if isinstance(validation_packet.get("scheduler_validation", {}), dict)
            else {}
        )
        control_center_validation = (
            validation_packet.get("control_center_validation", {})
            if isinstance(validation_packet.get("control_center_validation", {}), dict)
            else {}
        )

        ma_backend_profile = self._build_ma_backend_profile()

        return {
            "legacy": legacy,
            "parity": parity,
            "unresolved_sources": unresolved_sources,
            "mismatches": mismatches,
            "registry": registry,
            "route_trace": route_trace,
            "host_control_cutover_gate": host_control_cutover_gate,
            "contract_validation": contract_validation,
            "selection_handoff_validation": selection_handoff_validation,
            "route_safety_validation": route_safety_validation,
            "metadata_prep_validation": metadata_prep_validation,
            "capability_profile_validation": capability_profile_validation,
            "action_catalog_validation": action_catalog_validation,
            "crossfade_balance_validation": crossfade_balance_validation,
            "scheduler_validation": scheduler_validation,
            "metadata_bridge_validation": metadata_bridge_validation,
            "cutover_prep_validation": cutover_prep_validation,
            "handoff_inventory": self._build_handoff_inventory(),
            "ma_backend_profile": ma_backend_profile,
            "control_center_validation": control_center_validation,
            "write_controls": self._build_write_controls(),
            "captured_at": datetime.now(UTC).isoformat(),
        }

    def _build_ma_backend_profile(self) -> dict[str, Any]:
        return self._meta_fabric.build_ma_backend_profile()

    async def async_apply_control_center_settings(self, raw_options: dict[str, Any] | None) -> dict[str, Any]:
        """Normalize and apply control-center settings from config-entry options."""
        self._control_center_settings = normalize_control_center_settings(raw_options)
        self.async_set_updated_data(self._build_snapshot())
        return dict(self._control_center_settings)

    async def async_execute_control_center_input(
        self,
        *,
        input_event: str,
        correlation_id: str | None,
        target_hint: str | None,
        dry_run: bool,
        delta: Any,
    ) -> dict[str, Any]:
        """Execute one mapped control-center input with dry-run-first safety."""
        requested_at = datetime.now(UTC).isoformat()
        normalized_event = (input_event or "").strip().lower()
        corr = (correlation_id or "").strip() or f"p6-input-{uuid4().hex[:12]}"
        hint = (target_hint or "").strip()

        result: dict[str, Any] = {
            "status": "pending",
            "requested_at": requested_at,
            "completed_at": requested_at,
            "correlation_id": corr,
            "input_event": normalized_event,
            "target_hint": hint,
            "dry_run": bool(dry_run),
            "delta": delta,
            "mapped_action": None,
            "reason": "",
            "read_only_mode": bool(self._control_center_settings.get("read_only_mode", True)),
        }

        if normalized_event not in CONTROL_CENTER_INPUT_EVENTS:
            result["status"] = "blocked_unknown_input_event"
            result["reason"] = "input_event is not part of the supported control-center contract"
        else:
            mapped_action: str = ""
            if normalized_event == "encoder_turn":
                mapped_action = str(self._control_center_settings.get("encoder_turn_action", "") or "").strip()
            elif normalized_event == "encoder_press":
                mapped_action = str(self._control_center_settings.get("encoder_press_action", "") or "").strip()
            elif normalized_event == "encoder_long_press":
                mapped_action = str(self._control_center_settings.get("encoder_long_press_action", "") or "").strip()
            elif normalized_event == "button_1":
                mapped_action = str(self._control_center_settings.get("button_1_scene", "") or "").strip()
            elif normalized_event == "button_2":
                mapped_action = str(self._control_center_settings.get("button_2_scene", "") or "").strip()
            elif normalized_event == "button_3":
                mapped_action = str(self._control_center_settings.get("button_3_scene", "") or "").strip()
            elif normalized_event == "button_4":
                mapped_action = str(self._control_center_settings.get("button_4_scene", "") or "").strip()

            result["mapped_action"] = mapped_action

            if not mapped_action:
                result["status"] = "blocked_unmapped_input"
                result["reason"] = "No mapping exists for the selected input_event"
            elif mapped_action.lower() in {"scene.none", "none"}:
                result["status"] = "blocked_scene_unconfigured"
                result["reason"] = "Input is mapped to placeholder scene.none"
            elif mapped_action == "no_op":
                result["status"] = "noop_action"
                result["reason"] = "Mapped action is no_op; execution intentionally performs no runtime write"
            elif mapped_action == "scene_quick_trigger":
                quick_scene = str(self._control_center_settings.get("button_1_scene", "scene.none") or "scene.none").strip()
                result["mapped_action"] = f"scene_quick_trigger:{quick_scene}"
                if quick_scene.lower() in {"", "scene.none"}:
                    result["status"] = "blocked_scene_unconfigured"
                    result["reason"] = "scene_quick_trigger requires button_1_scene to be configured"
                elif result["read_only_mode"] and not dry_run:
                    result["status"] = "blocked_read_only_mode"
                    result["reason"] = "Control-center read_only_mode is enabled; non-dry-run execution is blocked"
                elif dry_run:
                    result["status"] = "dry_run_ok"
                    result["reason"] = "scene_quick_trigger resolved successfully in dry-run mode"
                else:
                    try:
                        await self.hass.services.async_call(
                            "scene",
                            "turn_on",
                            {"entity_id": quick_scene},
                            blocking=True,
                        )
                        result["status"] = "applied_scene_turn_on"
                        result["reason"] = "scene_quick_trigger executed via button_1_scene binding"
                    except Exception as err:  # pragma: no cover - defensive runtime guard
                        result["status"] = "scene_turn_on_error"
                        result["reason"] = f"Scene call failed: {err}"
            elif result["read_only_mode"] and not dry_run:
                result["status"] = "blocked_read_only_mode"
                result["reason"] = "Control-center read_only_mode is enabled; non-dry-run execution is blocked"
            elif dry_run:
                result["status"] = "dry_run_ok"
                result["reason"] = "Mapping resolved successfully in dry-run mode"
            elif mapped_action.startswith("scene."):
                try:
                    await self.hass.services.async_call(
                        "scene",
                        "turn_on",
                        {"entity_id": mapped_action},
                        blocking=True,
                    )
                    result["status"] = "applied_scene_turn_on"
                    result["reason"] = "Mapped scene turn_on call executed"
                except Exception as err:  # pragma: no cover - defensive runtime guard
                    result["status"] = "scene_turn_on_error"
                    result["reason"] = f"Scene call failed: {err}"
            else:
                result["status"] = "blocked_unimplemented_action"
                result["reason"] = "Mapped action is reserved for future bounded execution slices"

        result["completed_at"] = datetime.now(UTC).isoformat()
        self._last_control_center_action_attempt = result
        self.async_set_updated_data(self._build_snapshot())
        return result

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

    async def async_validate_capability_profile(self) -> None:
        """Refresh parity data and emit F4-S01 capability/profile diagnostics."""
        self.async_set_updated_data(self._build_snapshot())

    async def async_validate_action_catalog(self) -> None:
        """Refresh parity data and emit F4-S02 action-catalog safety diagnostics."""
        self.async_set_updated_data(self._build_snapshot())

    async def async_validate_crossfade_balance(self) -> None:
        """Refresh parity data and emit F4-S03 crossfade/balance diagnostics."""
        self.async_set_updated_data(self._build_snapshot())

    async def async_validate_scheduler(self) -> None:
        """Refresh parity data and emit scheduler readiness/decision diagnostics."""
        self.async_set_updated_data(self._build_snapshot())

    async def async_run_scheduler_choice(
        self,
        *,
        require_control_capable: bool,
        prefer_fresh: bool,
        max_results: int,
        target_hint: str,
        correlation_id: str | None,
    ) -> dict[str, Any]:
        """Run scheduler ranking against current registry/profile snapshot and store decision payload."""
        return await self._meta_fabric.async_run_scheduler_choice(
            require_control_capable=require_control_capable,
            prefer_fresh=prefer_fresh,
            max_results=max_results,
            target_hint=target_hint,
            correlation_id=correlation_id,
        )

    async def async_apply_scheduler_choice(
        self,
        *,
        require_control_capable: bool,
        prefer_fresh: bool,
        max_results: int,
        target_hint: str,
        dry_run: bool,
        force: bool,
        correlation_id: str | None,
    ) -> dict[str, Any]:
        """Run scheduler decision and guardedly apply selected target to helper entity."""
        return await self._meta_fabric.async_apply_scheduler_choice(
            require_control_capable=require_control_capable,
            prefer_fresh=prefer_fresh,
            max_results=max_results,
            target_hint=target_hint,
            dry_run=dry_run,
            force=force,
            correlation_id=correlation_id,
        )

    async def async_build_target_options_scaffold(
        self,
        *,
        dry_run: bool,
        force: bool,
        include_none: bool,
        correlation_id: str | None,
    ) -> dict[str, Any]:
        """Build (and optionally apply) component-native target-options scaffold plan."""
        return await self._meta_fabric.async_build_target_options_scaffold(
            dry_run=dry_run,
            force=force,
            include_none=include_none,
            correlation_id=correlation_id,
        )

    async def async_run_auto_select_scaffold(
        self,
        *,
        dry_run: bool,
        force: bool,
        sync_options_if_missing: bool,
        include_none: bool,
        correlation_id: str | None,
    ) -> dict[str, Any]:
        """Run component-native auto-select scaffold with guarded helper apply semantics."""
        return await self._meta_fabric.async_run_auto_select_scaffold(
            dry_run=dry_run,
            force=force,
            sync_options_if_missing=sync_options_if_missing,
            include_none=include_none,
            correlation_id=correlation_id,
        )

    async def async_track_last_valid_target(
        self,
        *,
        dry_run: bool,
        force: bool,
        correlation_id: str | None,
        source: str = "service_track_last_valid_target",
    ) -> dict[str, Any]:
        """Track helper-selected target into last-valid helper with guarded writes."""
        return await self._meta_fabric.async_track_last_valid_target(
            dry_run=dry_run,
            force=force,
            correlation_id=correlation_id,
            source=source,
        )

    async def async_restore_last_valid_target(
        self,
        *,
        dry_run: bool,
        force: bool,
        correlation_id: str | None,
    ) -> dict[str, Any]:
        """Restore helper selection from last-valid helper when current selection is unresolved."""
        return await self._meta_fabric.async_restore_last_valid_target(
            dry_run=dry_run,
            force=force,
            correlation_id=correlation_id,
        )

    async def async_cycle_active_target(
        self,
        *,
        dry_run: bool,
        force: bool,
        include_none: bool,
        correlation_id: str | None,
    ) -> dict[str, Any]:
        """Cycle active-target helper options with optional none filtering and override activation."""
        return await self._meta_fabric.async_cycle_active_target(
            dry_run=dry_run,
            force=force,
            include_none=include_none,
            correlation_id=correlation_id,
        )

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

    def _auto_select_loop_preflight(self) -> tuple[bool, str]:
        return self._meta_fabric.auto_select_loop_preflight()

    async def async_run_component_auto_select_loop(self, *, source: str, force: bool = False) -> None:
        """Run component-side auto-select loop parity behavior under guarded semantics."""
        await self._meta_fabric.async_run_component_auto_select_loop(source=source, force=force)

    async def async_run_component_players_change_refresh(self, *, source: str) -> None:
        """Mirror legacy players-change sequencing: refresh options, then auto-select."""
        await self._meta_fabric.async_run_component_players_change_refresh(source=source)

    async def async_apply_ambiguity_lock(self, *, source: str) -> None:
        """Mirror legacy lock-on-ambiguous-select behavior for component authority windows."""
        await self._meta_fabric.async_apply_ambiguity_lock(source=source)

    async def async_apply_stale_unlock(self, *, source: str) -> None:
        """Mirror legacy stale-meta unlock behavior with bounded auto-select follow-up."""
        await self._meta_fabric.async_apply_stale_unlock(source=source)

    @callback
    def _handle_meta_stale_unlock_timer(self, _now) -> None:
        self._meta_fabric.handle_meta_stale_unlock_timer(_now)

    async def _async_dismiss_no_control_feedback_notification(self) -> None:
        await self._meta_fabric.async_dismiss_no_control_feedback_notification()

    @callback
    def _handle_no_control_feedback_hold_timer(self, _now) -> None:
        self._meta_fabric.handle_no_control_feedback_hold_timer(_now)

    async def _async_run_no_control_feedback_self_heal(self) -> None:
        await self._meta_fabric.async_run_no_control_feedback_self_heal()

    @callback
    def _handle_no_control_feedback_post_heal_timer(self, _now) -> None:
        self._meta_fabric.handle_no_control_feedback_post_heal_timer(_now)

    async def _async_finalize_no_control_feedback_notification(self) -> None:
        await self._meta_fabric.async_finalize_no_control_feedback_notification()

    @callback
    def _handle_global_state_change(self, event) -> None:
        """Mirror legacy event-based auto-select trigger for watched target entities."""
        self._meta_fabric.handle_global_state_change(event)

    @callback
    def _handle_state_change(self, event) -> None:
        self._meta_fabric.handle_state_change(event)
