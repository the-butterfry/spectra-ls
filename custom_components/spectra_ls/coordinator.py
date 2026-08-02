# Description: Data coordinator for Spectra LS parity diagnostics, Phase 3 guarded routing write-path controls, Phase 4 diagnostics scaffolding (F4-S01/F4-S03), Phase 5 metadata trial contract auditing, and Phase 6/8 control-center settings, fast-remap, execution visibility, startup auto-recovery orchestration (latency-hardened cadence), and selection-lock lifecycle parity migration (ambiguity lock, stale unlock, auto-select loop).
# Version: 2026.08.02.9
# Last updated: 2026-08-02
# PARITY DIRECTIVE (until full cutover): behavior/contract edits here require same-slice two-track parity review
# and version-metadata review in runtime (`packages/` + `esphome/`) and component (`custom_components/spectra_ls/`) tracks.

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from datetime import timedelta
import json
import logging
from time import monotonic
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .control_execution_fabric import ControlExecutionFabricWorkflow
from .const import (
    DOMAIN,
    FABRIC_AUTH_MODE_DEGRADED_FALLBACK,
    FABRIC_AUTH_MODE_PRIMARY,
    FABRIC_AUTH_REASON_API_UNREACHABLE,
    FABRIC_AUTH_REASON_DEGRADED_ACTIVE,
    FABRIC_AUTH_REASON_PAYLOAD_SHAPE_INVALID,
    FABRIC_AUTH_REASON_PAYLOAD_STALE,
    LEGACY_ACTIVE_META_ENTITY,
    LEGACY_LAST_VALID_TARGET,
    LEGACY_META_OVERRIDE_ACTIVE,
    LEGACY_META_OVERRIDE_ENTITY,
    LEGACY_META_PAUSED_HIDE_S,
    LEGACY_META_RESOLVER,
    LEGACY_META_CONFIDENCE_MIN,
    LEGACY_CONTROL_HOST,
    LEGACY_CONTROL_TARGETS,
    LEGACY_META_CANDIDATES,
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
    OPT_DEFAULT_WRITE_AUTHORITY_MODE,
    WRITE_AUTH_ALLOWED,
    WRITE_AUTH_COMPONENT,
    WRITE_DEBOUNCE_SECONDS,
    normalize_control_center_settings,
    normalize_setup_entity_policy,
)
from .lifecycle_fabric import LifecycleFabricWorkflow
from .meta_fabric import MetaFabricWorkflow
from .metadata_stack import MetadataStackWorkflow
from .refresh_validation_fabric import RefreshValidationFabricWorkflow
from .snapshot_fabric import SnapshotFabricWorkflow
from .utility_fabric import UtilityFabricWorkflow

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
            update_interval=timedelta(seconds=30),
        )
        self._entry = entry
        self._unsub_state_events = None
        self._unsub_global_state_events = None
        self._write_authority_mode = self._normalize_write_authority(
            str(entry.options.get(OPT_DEFAULT_WRITE_AUTHORITY_MODE, WRITE_AUTH_COMPONENT) or "")
        )
        self._write_debounce_s = float(WRITE_DEBOUNCE_SECONDS)
        self._control_center_settings = normalize_control_center_settings(entry.options)
        self._setup_entity_policy = normalize_setup_entity_policy(entry.options)
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
        self._snapshot_refresh_min_interval_s = 20.0
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
        self._last_set_active_target_attempt: dict[str, Any] = {
            "status": "never_attempted",
            "requested_at": None,
            "completed_at": None,
            "reason": "No component explicit active-target set attempts requested yet",
            "selected_target": "",
        }
        self._component_selection_state: dict[str, Any] = {
            "active_target": "",
            "last_valid_target": "",
            "options": [],
            "updated_at": None,
            "source": "component_default_state",
        }
        self._component_metadata_override_state: dict[str, Any] = {
            "active": False,
            "entity": "",
            "updated_at": None,
            "source": "component_default_state",
        }
        self._last_metadata_provider_packet: dict[str, Any] = {
            "status": "never_attempted",
            "response": "",
            "providers": "",
            "item_uri": "",
            "reason": "",
            "updated_at": "",
            "source": "component_default_state",
        }
        self._startup_recovery_unsub = None
        self._startup_recovery_task = None
        self._startup_recovery_attempt = 0
        self._startup_recovery_max_attempts = 3
        self._startup_recovery_initial_delay_s = 4.0
        self._startup_recovery_retry_delay_s = 8.0
        self._startup_recovery_wait_cycles = 0
        self._startup_recovery_max_wait_cycles = 20
        self._metadata_stack: Any = MetadataStackWorkflow(self)
        self._meta_fabric: Any = MetaFabricWorkflow(self)
        self._snapshot_fabric: Any = SnapshotFabricWorkflow(self)
        self._control_execution_fabric: Any = ControlExecutionFabricWorkflow(self)
        self._lifecycle_fabric: Any = LifecycleFabricWorkflow(self)
        self._refresh_validation_fabric: Any = RefreshValidationFabricWorkflow(self)
        self._utility_fabric: Any = UtilityFabricWorkflow(self)
        self._publish_signature_last = ""
        self._publish_monotonic_last = 0.0
        self._publish_min_interval_enabled_s = 15.0
        self._publish_min_interval_disabled_active_s = 10.0
        self._publish_min_interval_disabled_s = 60.0
        self._publish_heartbeat_disabled_active_s = 10.0
        self._publish_heartbeat_disabled_s = 180.0
        self._diagnostics_toggle_helper_entity = "input_boolean.spectra_ls_component_diagnostics_enabled"
        self._operational_fingerprint_last = ""

    def _diagnostics_refresh_enabled(self) -> bool:
        state = self.hass.states.get(self._diagnostics_toggle_helper_entity)
        if state is None:
            # Default fail-closed posture for churn control: diagnostics high-frequency
            # cadence is enabled only when operator explicitly opts in.
            return False
        normalized = self._normalize_state(getattr(state, "state", ""))
        return normalized in {"on", "true", "1"}

    def _stable_payload_signature(self, payload: Any) -> str:
        volatile_keys = {
            "captured_at",
            "updated_at",
            "requested_at",
            "completed_at",
            "timestamp",
            "last_changed",
            "last_updated",
        }

        def _strip(value: Any) -> Any:
            if isinstance(value, dict):
                out: dict[str, Any] = {}
                for key, item in value.items():
                    key_text = str(key)
                    lowered = key_text.lower()
                    if lowered in volatile_keys:
                        continue
                    if lowered.endswith("_age_s") or lowered.endswith("_age_ms"):
                        continue
                    out[key_text] = _strip(item)
                return out
            if isinstance(value, list):
                return [_strip(item) for item in value]
            return value

        try:
            return json.dumps(_strip(payload), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        except TypeError:
            return repr(_strip(payload))

    def _operational_fingerprint(self, data: dict[str, Any]) -> str:
        """Return compact fingerprint of behavior-relevant contract surfaces.

        Used when diagnostics cadence is disabled/off to avoid publishes for
        non-operational metadata churn.
        """
        route_trace = data.get("route_trace", {}) if isinstance(data.get("route_trace", {}), dict) else {}
        parity = data.get("parity", {}) if isinstance(data.get("parity", {}), dict) else {}
        metadata_prep = (
            data.get("metadata_prep_validation", {})
            if isinstance(data.get("metadata_prep_validation", {}), dict)
            else {}
        )
        values = metadata_prep.get("values", {}) if isinstance(metadata_prep.get("values", {}), dict) else {}

        payload = {
            "parity": {
                "active_target": parity.get("active_target"),
                "active_control_path": parity.get("active_control_path"),
                "control_hosts": parity.get("control_hosts"),
                "active_control_capable": parity.get("active_control_capable"),
            },
            "route": {
                "decision": route_trace.get("decision"),
                "active_target": route_trace.get("active_target"),
                "resolved_control_path": route_trace.get("resolved_control_path"),
                "control_host": route_trace.get("control_host"),
                "control_port": route_trace.get("control_port"),
            },
            "now_playing": {
                "entity": values.get("now_playing_entity"),
                "state": values.get("now_playing_state"),
                "title": values.get("now_playing_title"),
                "source": values.get("now_playing_source"),
                "preview_key": values.get("now_playing_preview_key"),
                "display_allowed": values.get("now_playing_display_allowed"),
            },
        }

        try:
            return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        except TypeError:
            return repr(payload)

    def _is_payload_playback_active(self, data: dict[str, Any]) -> bool:
        """Return True when payload indicates active playback context."""
        metadata_prep = data.get("metadata_prep_validation", {})
        values = metadata_prep.get("values", {}) if isinstance(metadata_prep, dict) else {}
        now_playing_state = str(values.get("now_playing_state", "") or "").strip().lower()
        if now_playing_state in {"playing", "buffering"}:
            return True

        route_trace = data.get("route_trace", {}) if isinstance(data.get("route_trace", {}), dict) else {}
        active_target = str(route_trace.get("active_target", "") or "").strip()
        if self._normalize_state(active_target) in {"", "none", "unknown", "unavailable", "null"}:
            return False

        state_obj = self.hass.states.get(active_target)
        normalized_state = self._normalize_state(state_obj.state if state_obj is not None else "")
        return normalized_state in {"playing", "buffering"}

    def async_set_updated_data(self, data: dict[str, Any]) -> None:
        """Publish data with coordinator-wide anti-churn gating.

        Applies to all call sites (poll refresh, service-triggered refresh, and
        event/recovery paths), ensuring a single suppression choke point.
        """
        signature = self._stable_payload_signature(data)
        operational_fingerprint = self._operational_fingerprint(data)
        now_mono = monotonic()
        diagnostics_enabled = self._diagnostics_refresh_enabled()
        playback_active = self._is_payload_playback_active(data)
        min_interval = (
            self._publish_min_interval_enabled_s
            if diagnostics_enabled
            else (
                self._publish_min_interval_disabled_active_s
                if playback_active
                else self._publish_min_interval_disabled_s
            )
        )

        active_heartbeat_s = self._publish_heartbeat_disabled_active_s if playback_active else self._publish_heartbeat_disabled_s

        if self._publish_signature_last and signature == self._publish_signature_last:
            if (
                not diagnostics_enabled
                and playback_active
                and self._publish_monotonic_last > 0
                and (now_mono - self._publish_monotonic_last) >= active_heartbeat_s
            ):
                pass
            else:
                return

        if (
            self._publish_monotonic_last > 0
            and (now_mono - self._publish_monotonic_last) < min_interval
        ):
            return

        if not diagnostics_enabled:
            if self._operational_fingerprint_last and operational_fingerprint == self._operational_fingerprint_last:
                # Heartbeat only: keep occasional samples while suppressing idle churn.
                if (
                    self._publish_monotonic_last > 0
                    and (now_mono - self._publish_monotonic_last) < active_heartbeat_s
                ):
                    return

        super().async_set_updated_data(data)
        self._publish_signature_last = signature
        self._operational_fingerprint_last = operational_fingerprint
        self._publish_monotonic_last = now_mono

    @property
    def metadata_stack(self) -> Any:
        return self._metadata_stack

    @property
    def meta_fabric(self) -> Any:
        return self._meta_fabric

    @property
    def snapshot_fabric(self) -> Any:
        return self._snapshot_fabric

    @property
    def control_execution_fabric(self) -> Any:
        return self._control_execution_fabric

    @property
    def lifecycle_fabric(self) -> Any:
        return self._lifecycle_fabric

    @property
    def refresh_validation_fabric(self) -> Any:
        return self._refresh_validation_fabric

    @property
    def utility_fabric(self) -> Any:
        return self._utility_fabric

    @property
    def setup_entity_policy(self) -> dict[str, Any]:
        return self._setup_entity_policy

    @property
    def last_metadata_provider_packet(self) -> dict[str, Any]:
        return self._last_metadata_provider_packet

    async def async_setup(self) -> None:
        """Initialize data and state listeners."""
        await self._lifecycle_fabric.async_setup()

    async def async_shutdown(self) -> None:
        """Detach listeners on unload."""
        await self._lifecycle_fabric.async_shutdown()

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
        self._refresh_validation_fabric.refresh_snapshot(force=force)

    def build_snapshot(self) -> dict[str, Any]:
        """Build and return current parity snapshot payload."""
        return self._build_snapshot()

    def refresh_snapshot(self) -> None:
        """Refresh coordinator data immediately from a newly built snapshot."""
        self.async_set_updated_data(self._build_snapshot())

    @callback
    def _handle_deferred_snapshot_refresh(self, _now) -> None:
        self._refresh_validation_fabric.handle_deferred_snapshot_refresh(_now)

    async def _async_update_data(self) -> dict[str, Any]:
        """Read legacy surfaces and compute parity snapshot."""
        return await self._refresh_validation_fabric.async_update_data()

    def _normalize_state(self, state_value: str) -> str:
        return self._utility_fabric.normalize_state(state_value)

    def _parse_jsonish_payload(self, raw: Any) -> Any:
        return self._utility_fabric.parse_jsonish_payload(raw)

    def _compute_component_target_options_plan(self) -> dict[str, Any]:
        return self._meta_fabric.compute_component_target_options_plan()

    def _snapshot_for_entity(self, entity_id: str, *, as_bool: bool = False) -> LegacySnapshot:
        packet = self._utility_fabric.snapshot_for_entity(entity_id, as_bool=as_bool)
        return LegacySnapshot(
            value=packet.get("value"),
            state=str(packet.get("state", "missing")),
            available=bool(packet.get("available", False)),
        )

    def _normalize_write_authority(self, mode: str) -> str:
        normalized = str(mode or "").strip().lower()
        if normalized in WRITE_AUTH_ALLOWED:
            return normalized
        return WRITE_AUTH_COMPONENT

    def _build_write_controls(self) -> dict[str, Any]:
        return self._snapshot_fabric.build_write_controls()

    def _read_float_helper(self, entity_id: str, default: float) -> float:
        return self._utility_fabric.read_float_helper(entity_id, default)

    def _availability_points(self, quality: str) -> int:
        return self._utility_fabric.availability_points(quality)

    def _empirical_bonus(self, overlay: dict[str, Any]) -> float:
        return self._utility_fabric.empirical_bonus(overlay)

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

    def _is_resolved_state(self, raw_state: str) -> bool:
        return self._utility_fabric.is_resolved_state(raw_state)

    def _timestamp_age_seconds(self, raw_value: Any) -> float | None:
        return self._utility_fabric.timestamp_age_seconds(raw_value)

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
        return self._snapshot_fabric.build_snapshot()

    def _build_ma_backend_profile(self) -> dict[str, Any]:
        return self._meta_fabric.build_ma_backend_profile()

    async def async_apply_control_center_settings(self, raw_options: dict[str, Any] | None) -> dict[str, Any]:
        """Normalize and apply control-center settings from config-entry options."""
        return await self._control_execution_fabric.async_apply_control_center_settings(raw_options)

    def apply_setup_entity_policy(self, raw_options: dict[str, Any] | None) -> dict[str, Any]:
        """Normalize and apply setup include/exclude policy from config-entry options."""
        self._setup_entity_policy = normalize_setup_entity_policy(raw_options)
        return self._setup_entity_policy

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
        return await self._control_execution_fabric.async_execute_control_center_input(
            input_event=input_event,
            correlation_id=correlation_id,
            target_hint=target_hint,
            dry_run=dry_run,
            delta=delta,
        )

    async def async_rebuild_registry(self) -> None:
        """Refresh parity data, including registry scaffold snapshot."""
        await self._refresh_validation_fabric.async_rebuild_registry()

    async def async_validate_contracts(self) -> None:
        """Refresh parity data and emit contract validation visibility in snapshot."""
        await self._refresh_validation_fabric.async_validate_contracts()

    async def async_dump_route_trace(self) -> None:
        """Refresh parity data so latest route trace appears in diagnostics."""
        await self._refresh_validation_fabric.async_dump_route_trace()

    async def async_validate_selection_handoff(self) -> None:
        """Refresh parity data and emit selection-handoff validation diagnostics."""
        await self._refresh_validation_fabric.async_validate_selection_handoff()

    async def async_validate_capability_profile(self) -> None:
        """Refresh parity data and emit F4-S01 capability/profile diagnostics."""
        await self._refresh_validation_fabric.async_validate_capability_profile()

    async def async_validate_action_catalog(self) -> None:
        """Refresh parity data and emit F4-S02 action-catalog safety diagnostics."""
        await self._refresh_validation_fabric.async_validate_action_catalog()

    async def async_validate_crossfade_balance(self) -> None:
        """Refresh parity data and emit F4-S03 crossfade/balance diagnostics."""
        await self._refresh_validation_fabric.async_validate_crossfade_balance()

    async def async_validate_scheduler(self) -> None:
        """Refresh parity data and emit scheduler readiness/decision diagnostics."""
        await self._refresh_validation_fabric.async_validate_scheduler()

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

    async def async_set_active_target(
        self,
        *,
        target: str,
        dry_run: bool,
        force: bool,
        sync_options_if_missing: bool,
        correlation_id: str | None,
    ) -> dict[str, Any]:
        """Set active-target helper selection through component-guarded explicit target contract."""
        return await self._meta_fabric.async_set_active_target(
            target=target,
            dry_run=dry_run,
            force=force,
            sync_options_if_missing=sync_options_if_missing,
            correlation_id=correlation_id,
        )

    async def async_set_metadata_provider_packet(
        self,
        *,
        status: str,
        response: str,
        providers: str,
        item_uri: str,
        reason: str,
        updated_at: str,
        source: str,
    ) -> dict[str, Any]:
        """Store component-owned metadata provider telemetry packet for diagnostics surfaces."""

        def _norm_text(value: Any) -> str:
            norm = str(value or "").strip()
            if norm.lower() in {"", "none", "unknown", "unavailable", "null"}:
                return ""
            return norm

        packet = {
            "status": _norm_text(status) or "never_attempted",
            "response": _norm_text(response),
            "providers": _norm_text(providers),
            "item_uri": _norm_text(item_uri),
            "reason": _norm_text(reason),
            "updated_at": _norm_text(updated_at) or datetime.now(UTC).isoformat(),
            "source": _norm_text(source) or "component_service_set_metadata_provider_packet",
        }

        self._last_metadata_provider_packet = packet
        self.refresh_snapshot()
        return packet

    async def async_set_write_authority(self, mode: str, reason: str = "") -> None:
        """Set write authority mode for guarded routing write-path trials."""
        await self._control_execution_fabric.async_set_write_authority(mode, reason)

    async def async_route_write_trial(self, correlation_id: str | None = None, force: bool = False) -> None:
        """Attempt a guarded routing write to the active-target helper."""
        await self._control_execution_fabric.async_route_write_trial(
            correlation_id=correlation_id,
            force=force,
        )

    def _auto_select_loop_preflight(self) -> tuple[bool, str]:
        return self._meta_fabric.auto_select_loop_preflight()

    async def async_run_component_auto_select_loop(self, *, source: str, force: bool = False) -> None:
        """Run component-side auto-select loop parity behavior under guarded semantics."""
        await self._meta_fabric.async_run_component_auto_select_loop(source=source, force=force)

    async def async_run_component_players_change_refresh(self, *, source: str) -> None:
        """Mirror legacy players-change sequencing: refresh options, then auto-select."""
        await self._meta_fabric.async_run_component_players_change_refresh(source=source)

    @callback
    def _handle_global_state_change(self, event) -> None:
        """Mirror legacy event-based auto-select trigger for watched target entities."""
        self._meta_fabric.handle_global_state_change(event)

    @callback
    def _handle_state_change(self, event) -> None:
        self._meta_fabric.handle_state_change(event)
