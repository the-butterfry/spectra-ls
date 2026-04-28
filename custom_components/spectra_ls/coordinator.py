# Description: Data coordinator for Spectra LS parity diagnostics, Phase 3 guarded routing write-path controls, Phase 4 diagnostics scaffolding (F4-S01/F4-S03), Phase 5 metadata trial contract auditing, and Phase 6/8 control-center settings, fast-remap, execution visibility, startup auto-recovery orchestration (latency-hardened cadence), and selection-lock lifecycle parity migration (ambiguity lock, stale unlock, auto-select loop).
# Version: 2026.04.27.36
# Last updated: 2026-04-27
# Last updated: 2026-04-27

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import json
import logging
from time import monotonic
from typing import Any
from uuid import uuid4

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_call_later, async_track_state_change_event
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONTROL_CENTER_INPUT_EVENTS,
    DOMAIN,
    LEGACY_ACTIVE_META_ENTITY,
    LEGACY_LAST_VALID_TARGET,
    LEGACY_META_DETECTED_ENTITY,
    LEGACY_META_OVERRIDE_ACTIVE,
    LEGACY_META_OVERRIDE_ENTITY,
    LEGACY_META_PAUSED_HIDE_S,
    LEGACY_META_RESOLVER,
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
    LEGACY_NOW_PLAYING_STATE,
    LEGACY_NOW_PLAYING_TITLE,
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
        self._metadata_trial_in_progress = False
        self._snapshot_refresh_min_interval_s = 0.75
        self._last_snapshot_refresh_monotonic = 0.0
        self._deferred_snapshot_refresh_unsub = None
        self._last_metadata_trial_attempt: dict[str, Any] = {
            "status": "never_attempted",
            "requested_at": None,
            "completed_at": None,
            "reason": "No metadata trial attempts yet",
            "audit_payload_complete": False,
            "audit_payload_state": "N/A",
            "missing_audit_fields": [],
            "blocking_reasons": [],
            "trial_gate_verdict": "N/A",
            "eligible_for_closeout": False,
        }
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
        self._last_metadata_resolver_attempt: dict[str, Any] = {
            "status": "never_attempted",
            "requested_at": None,
            "completed_at": None,
            "reason": "No metadata-resolver scaffold attempts requested yet",
            "dry_run": True,
            "force": False,
            "selected_meta_entity": "",
            "selection_reason": "",
        }
        self._last_metadata_bridge_attempt: dict[str, Any] = {
            "status": "never_attempted",
            "requested_at": None,
            "completed_at": None,
            "reason": "No metadata-trial bridge scaffold attempts requested yet",
            "resolver_status": "never_attempted",
            "trial_status": "never_attempted",
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
        self._startup_recovery_attempt = 0
        self._startup_recovery_wait_cycles = 0
        if self._startup_recovery_unsub is not None:
            self._startup_recovery_unsub()
            self._startup_recovery_unsub = None
        self._startup_recovery_unsub = async_call_later(
            self.hass,
            self._startup_recovery_initial_delay_s,
            self._handle_startup_recovery_timer,
        )

    @callback
    def _handle_startup_recovery_timer(self, _now) -> None:
        """Kick off one startup recovery attempt from timer callback."""
        self._startup_recovery_unsub = None
        if self._startup_recovery_task is not None and not self._startup_recovery_task.done():
            return
        self._startup_recovery_task = self.hass.async_create_task(self._async_run_startup_recovery_attempt())

    async def _async_run_startup_recovery_attempt(self) -> None:
        """Run one bounded startup recovery attempt and schedule retry if needed."""
        boot_ready, boot_reasons = self._is_startup_recovery_boot_ready()
        if not boot_ready:
            self._startup_recovery_wait_cycles += 1
            wait_reason = self._startup_wait_reason_prefix(boot_reasons)
            reason_suffix = self._format_startup_boot_wait_reasons(boot_reasons)

            self._last_metadata_bridge_attempt = {
                "status": "waiting_for_ma_boot",
                "requested_at": datetime.now(UTC).isoformat(),
                "completed_at": datetime.now(UTC).isoformat(),
                "reason": f"{wait_reason}: {reason_suffix}",
                "resolver_status": "never_attempted",
                "trial_status": "never_attempted",
            }
            self.async_set_updated_data(self._build_snapshot())

            if self._startup_recovery_wait_cycles <= self._startup_recovery_max_wait_cycles:
                _LOGGER.info(
                    "Startup auto-recovery is waiting for Music Assistant boot readiness (%s/%s): %s",
                    self._startup_recovery_wait_cycles,
                    self._startup_recovery_max_wait_cycles,
                    reason_suffix,
                )
                self._startup_recovery_unsub = async_call_later(
                    self.hass,
                    self._startup_recovery_retry_delay_s,
                    self._handle_startup_recovery_timer,
                )
                return

            _LOGGER.warning(
                "Startup auto-recovery readiness wait window exhausted after %s cycles; continuing with guarded recovery",
                self._startup_recovery_max_wait_cycles,
            )

        self._startup_recovery_wait_cycles = 0
        self._startup_recovery_attempt += 1
        attempt = self._startup_recovery_attempt

        try:
            await self.async_restore_last_valid_target(
                dry_run=self._write_authority_mode != WRITE_AUTH_COMPONENT,
                force=True,
                correlation_id=f"startup-restore-{attempt}-{uuid4().hex[:8]}",
            )

            if self._write_authority_mode == WRITE_AUTH_COMPONENT:
                options_result = await self.async_build_target_options_scaffold(
                    dry_run=False,
                    force=True,
                    include_none=True,
                    correlation_id=f"startup-component-options-{attempt}-{uuid4().hex[:8]}",
                )
                auto_result = await self.async_run_auto_select_scaffold(
                    dry_run=False,
                    force=True,
                    sync_options_if_missing=True,
                    include_none=True,
                    correlation_id=f"startup-component-auto-select-{attempt}-{uuid4().hex[:8]}",
                )

                now_iso = datetime.now(UTC).isoformat()
                self._last_metadata_bridge_attempt = {
                    "status": "skipped_component_startup_no_mix",
                    "requested_at": now_iso,
                    "completed_at": now_iso,
                    "reason": (
                        "Startup bridge trial skipped in component authority; "
                        "component-only recovery executed to avoid boot authority mixing"
                    ),
                    "resolver_status": "never_attempted",
                    "trial_status": "never_attempted",
                    "stages": {
                        "component_target_options": {
                            "status": options_result.get("status", "unknown"),
                            "reason": options_result.get("reason", ""),
                        },
                        "component_auto_select": {
                            "status": auto_result.get("status", "unknown"),
                            "reason": auto_result.get("reason", ""),
                            "selected_target": auto_result.get("selected_target", ""),
                        },
                    },
                }
                self.async_set_updated_data(self._build_snapshot())
                _LOGGER.info(
                    "Startup auto-recovery completed with component-only no-mix flow (%s/%s)",
                    attempt,
                    self._startup_recovery_max_attempts,
                )
                return

            if self._write_authority_mode == WRITE_AUTH_LEGACY:
                now_iso = datetime.now(UTC).isoformat()
                self._last_metadata_bridge_attempt = {
                    "status": "skipped_legacy_authority",
                    "requested_at": now_iso,
                    "completed_at": now_iso,
                    "reason": (
                        "Startup bridge recovery skipped because authority mode is legacy; "
                        "runtime helper flow remains single-writer during boot"
                    ),
                    "resolver_status": "never_attempted",
                    "trial_status": "never_attempted",
                }
                self.async_set_updated_data(self._build_snapshot())
                _LOGGER.info(
                    "Startup auto-recovery skipped component bridge on legacy authority (%s/%s)",
                    attempt,
                    self._startup_recovery_max_attempts,
                )
                return

            result = await self.async_run_metadata_trial_bridge_scaffold(
                window_id=f"startup-recovery-{attempt}",
                reason="HA restart startup auto-recovery",
                resolver_dry_run=True,
                trial_dry_run=True,
                force=False,
                expected_target=None,
                expected_route=None,
                expected_meta_entity=None,
                correlation_id=f"startup-recovery-{uuid4().hex[:12]}",
            )
            status = str(result.get("status", "unknown") or "unknown")
            if status == "bridge_completed":
                _LOGGER.info(
                    "Startup auto-recovery succeeded on attempt %s/%s",
                    attempt,
                    self._startup_recovery_max_attempts,
                )
                return

            if attempt < self._startup_recovery_max_attempts:
                _LOGGER.warning(
                    "Startup auto-recovery attempt %s/%s incomplete: status=%s reason=%s; retrying in %.1fs",
                    attempt,
                    self._startup_recovery_max_attempts,
                    status,
                    str(result.get("reason", "") or ""),
                    self._startup_recovery_retry_delay_s,
                )
                self._startup_recovery_unsub = async_call_later(
                    self.hass,
                    self._startup_recovery_retry_delay_s,
                    self._handle_startup_recovery_timer,
                )
            else:
                _LOGGER.warning(
                    "Startup auto-recovery exhausted after %s attempts (last_status=%s, last_reason=%s)",
                    self._startup_recovery_max_attempts,
                    status,
                    str(result.get("reason", "") or ""),
                )
        except Exception as err:  # pragma: no cover - defensive runtime guard
            if attempt < self._startup_recovery_max_attempts:
                _LOGGER.warning(
                    "Startup auto-recovery attempt %s/%s failed (%s); retrying in %.1fs",
                    attempt,
                    self._startup_recovery_max_attempts,
                    err,
                    self._startup_recovery_retry_delay_s,
                )
                self._startup_recovery_unsub = async_call_later(
                    self.hass,
                    self._startup_recovery_retry_delay_s,
                    self._handle_startup_recovery_timer,
                )
            else:
                _LOGGER.warning(
                    "Startup auto-recovery exhausted after %s attempts due to repeated failures",
                    self._startup_recovery_max_attempts,
                )

    def _is_startup_recovery_boot_ready(self) -> tuple[bool, list[str]]:
        """Return whether MA/runtime surfaces are ready for startup recovery attempts."""
        reasons: list[str] = []

        ma_players_state = self.hass.states.get(LEGACY_MA_PLAYERS)
        ma_players_ready = ma_players_state is not None and self._is_resolved_state(ma_players_state.state)
        if not ma_players_ready:
            reasons.append("ma_players_not_ready")

        control_targets_state = self.hass.states.get(LEGACY_CONTROL_TARGETS)
        control_targets_ready = control_targets_state is not None and self._is_resolved_state(control_targets_state.state)
        if not control_targets_ready:
            reasons.append("control_targets_not_ready")

        helper_state = self.hass.states.get(LEGACY_ACTIVE_TARGET_HELPER)
        helper_exists = helper_state is not None
        if not helper_exists:
            reasons.append("active_target_helper_missing")

        helper_options_ready = False
        if helper_state is not None:
            options_attr = helper_state.attributes.get("options", [])
            if isinstance(options_attr, list):
                normalized_options = [
                    str(item).strip()
                    for item in options_attr
                    if isinstance(item, str) and str(item).strip()
                ]
                non_none_options = [item for item in normalized_options if self._normalize_state(item) != "none"]
                helper_options_ready = len(non_none_options) > 0
        if not helper_options_ready:
            reasons.append("active_target_options_not_ready")

        boot_ready = ma_players_ready and control_targets_ready and helper_exists and helper_options_ready
        return boot_ready, reasons

    @staticmethod
    def _startup_wait_reason_prefix(reasons: list[str]) -> str:
        """Return human-readable startup wait prefix aligned to the blocking phase."""
        ma_boot_blockers = {"ma_players_not_ready", "control_targets_not_ready"}
        if any(item in ma_boot_blockers for item in reasons):
            return "waiting for Music Assistant boot readiness"
        return "waiting for control contract readiness after Music Assistant boot"

    @staticmethod
    def _format_startup_boot_wait_reasons(reasons: list[str]) -> str:
        """Format startup readiness blockers into operator-friendly wait messaging."""
        if not reasons:
            return "Music Assistant startup signals are still initializing"

        reason_map = {
            "ma_players_not_ready": "Music Assistant player list is not ready yet",
            "control_targets_not_ready": "control target catalog is not ready yet",
            "active_target_helper_missing": "active-target helper is not available yet",
            "active_target_options_not_ready": "active-target options are still initializing",
        }
        friendly = [reason_map.get(item, item.replace("_", " ")) for item in reasons]
        return "; ".join(friendly)

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
        helper_entity = LEGACY_ACTIVE_TARGET_HELPER
        helper_state = self.hass.states.get(helper_entity)
        helper_options: list[str] = []
        helper_current = ""
        if helper_state is not None:
            helper_current = str(helper_state.state or "").strip()
            options_attr = helper_state.attributes.get("options", [])
            if isinstance(options_attr, list):
                helper_options = [
                    str(item).strip()
                    for item in options_attr
                    if isinstance(item, str) and str(item).strip()
                ]

        last_valid_state = self.hass.states.get("input_text.ma_last_valid_target")
        last_valid = str(last_valid_state.state if last_valid_state is not None else "").strip()

        known_targets: list[str] = []
        rooms_state = self.hass.states.get(LEGACY_ROOMS_JSON)
        rooms_raw = rooms_state.attributes.get("rooms_json", []) if rooms_state is not None else []
        rooms_payload = self._parse_jsonish_payload(rooms_raw)
        rooms_list: list[Any] = []
        if isinstance(rooms_payload, list):
            rooms_list = rooms_payload
        elif isinstance(rooms_payload, dict):
            mapped = rooms_payload.get("rooms", rooms_payload.get("result", []))
            if isinstance(mapped, list):
                rooms_list = mapped
        for room in rooms_list:
            if not isinstance(room, dict):
                continue
            ent = str(room.get("entity", "") or "").strip()
            if not self._is_resolved_state(ent):
                continue
            if not ent.startswith("media_player."):
                continue
            if self.hass.states.get(ent) is None:
                continue
            if ent not in known_targets:
                known_targets.append(ent)

        discovered_targets: list[str] = []
        ma_players_state = self.hass.states.get(LEGACY_MA_PLAYERS)
        ma_players_raw = ma_players_state.attributes.get("result", []) if ma_players_state is not None else []
        ma_players_payload = self._parse_jsonish_payload(ma_players_raw)
        players_list: list[Any] = []
        if isinstance(ma_players_payload, list):
            players_list = ma_players_payload
        elif isinstance(ma_players_payload, dict):
            mapped = ma_players_payload.get("result", ma_players_payload.get("players", []))
            if isinstance(mapped, list):
                players_list = mapped
        for player in players_list:
            if not isinstance(player, dict):
                continue
            ent = str(player.get("entity_id", "") or "").strip()
            if not self._is_resolved_state(ent) or not ent.startswith("media_player."):
                continue
            entity_state = self.hass.states.get(ent)
            if entity_state is None:
                continue
            ip = str(entity_state.attributes.get("ip_address", "") or player.get("ip_address", "") or "").strip()
            if not self._is_resolved_state(ip):
                continue
            if ent not in discovered_targets:
                discovered_targets.append(ent)

        discovered_live_targets: list[str] = []
        for player_state in self.hass.states.async_all("media_player"):
            ent = str(player_state.entity_id or "").strip()
            if not self._is_resolved_state(ent):
                continue
            ip = str(player_state.attributes.get("ip_address", "") or "").strip()
            if not self._is_resolved_state(ip):
                continue
            control_capable_attr = player_state.attributes.get("control_capable")
            control_path = str(player_state.attributes.get("control_path", "") or "").strip().lower()
            model = str(player_state.attributes.get("device_model", "") or "").strip().lower()
            manufacturer = str(player_state.attributes.get("manufacturer", "") or "").strip().lower()
            purpose = str(player_state.attributes.get("integration_purpose", "") or "").strip().lower()
            hint = f"{ent} {model} {manufacturer} {purpose}".lower()
            hint_supported = any(marker in hint for marker in ("wiim", "linkplay", "arylic", "up2stream"))
            control_capable = control_capable_attr in [True, "true", "True", "1", 1, "yes", "on"]
            control_path_ok = control_path == "linkplay_tcp"
            if control_capable or control_path_ok or hint_supported:
                if ent not in discovered_live_targets:
                    discovered_live_targets.append(ent)

        registry_capability_targets: list[str] = []
        registry_payload = self.data.get("registry", {}) if isinstance(self.data, dict) else {}
        registry_entries = registry_payload.get("entries", {}) if isinstance(registry_payload, dict) else {}
        if isinstance(registry_entries, dict):
            for target_id, entry in registry_entries.items():
                if not isinstance(entry, dict):
                    continue
                target = str(target_id or "").strip()
                if not target.startswith("media_player."):
                    continue
                if self.hass.states.get(target) is None:
                    continue

                control_capable = bool(entry.get("control_capable", False))
                host_resolved = self._is_resolved_state(str(entry.get("host", "") or ""))
                control_path = str(entry.get("control_path", "") or "").strip().lower()
                feature_profile = entry.get("feature_profile", {}) if isinstance(entry.get("feature_profile", {}), dict) else {}
                availability_quality = str(feature_profile.get("availability_quality", "") or "").strip().lower()
                fresh_enough = availability_quality in {"fresh", "warm", ""}
                control_path_supported = control_path in {"", "linkplay_tcp"}

                if control_capable and host_resolved and control_path_supported and fresh_enough:
                    if target not in registry_capability_targets:
                        registry_capability_targets.append(target)

        detected_state = self.hass.states.get("sensor.ma_detected_receiver_entity")
        detected_candidate = str(detected_state.state if detected_state is not None else "").strip()
        if not self._is_resolved_state(detected_candidate):
            detected_candidate = ""
        elif not detected_candidate.startswith("media_player."):
            detected_candidate = ""
        elif self.hass.states.get(detected_candidate) is None:
            detected_candidate = ""

        selectable_candidates: list[str] = []
        for item in [*known_targets, *discovered_targets, *discovered_live_targets, *registry_capability_targets]:
            if item not in selectable_candidates:
                selectable_candidates.append(item)
        if detected_candidate and detected_candidate not in selectable_candidates:
            selectable_candidates.append(detected_candidate)

        current_extra: list[str] = []
        if self._is_resolved_state(helper_current) and helper_current not in selectable_candidates:
            current_extra = [helper_current]

        proposed_options: list[str] = []
        for item in ["none", *selectable_candidates, *current_extra]:
            if item and item not in proposed_options:
                proposed_options.append(item)
        if not proposed_options:
            proposed_options = ["none"]

        current_ok = self._is_resolved_state(helper_current) and helper_current in selectable_candidates
        last_ok = self._is_resolved_state(last_valid) and last_valid in selectable_candidates
        default_option = "none"
        if current_ok:
            default_option = helper_current
        elif last_ok:
            default_option = last_valid
        elif selectable_candidates:
            default_option = selectable_candidates[0]

        return {
            "helper_entity": helper_entity,
            "current_helper_options": helper_options,
            "helper_current": helper_current,
            "last_valid_target": last_valid,
            "known_targets": known_targets,
            "discovered_targets": discovered_targets,
            "discovered_live_targets": discovered_live_targets,
            "registry_capability_targets": registry_capability_targets,
            "detected_candidate": detected_candidate,
            "candidates": selectable_candidates,
            "selectable_candidates": selectable_candidates,
            "proposed_options": proposed_options,
            "default_option": default_option,
            "ready": len(selectable_candidates) > 0,
        }

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
            "scheduler_last_decision": self._last_scheduler_decision,
            "scheduler_last_apply": self._last_scheduler_apply,
            "target_options_last_attempt": self._last_target_options_attempt,
            "auto_select_last_attempt": self._last_auto_select_attempt,
            "metadata_resolver_last_attempt": self._last_metadata_resolver_attempt,
            "metadata_bridge_last_attempt": self._last_metadata_bridge_attempt,
            "cycle_target_last_attempt": self._last_cycle_target_attempt,
            "restore_last_valid_last_attempt": self._last_restore_last_valid_attempt,
            "track_last_valid_last_attempt": self._last_track_last_valid_attempt,
            "target_helper_entity": LEGACY_ACTIVE_TARGET_HELPER,
            "control_center_settings": self._control_center_settings,
            "control_center_last_attempt": self._last_control_center_action_attempt,
        }

    def _build_metadata_bridge_validation(
        self,
        *,
        metadata_prep_validation: dict[str, Any],
    ) -> dict[str, Any]:
        ma_boot_ready, ma_boot_reasons = self._is_startup_recovery_boot_ready()
        ma_boot_wait_reason = self._format_startup_boot_wait_reasons(ma_boot_reasons)

        scaffolds = self._build_component_scaffolds()
        resolver_plan = (
            scaffolds.get("metadata_resolver_plan", {})
            if isinstance(scaffolds.get("metadata_resolver_plan", {}), dict)
            else {}
        )
        resolver_selected = str(resolver_plan.get("selected_meta_entity", "") or "").strip()
        resolver_attempt = self._last_metadata_resolver_attempt if isinstance(self._last_metadata_resolver_attempt, dict) else {}
        bridge_attempt = self._last_metadata_bridge_attempt if isinstance(self._last_metadata_bridge_attempt, dict) else {}
        trial_attempt = self._last_metadata_trial_attempt if isinstance(self._last_metadata_trial_attempt, dict) else {}

        resolver_status = str(resolver_attempt.get("status", "never_attempted") or "never_attempted")
        trial_status = str(trial_attempt.get("status", "never_attempted") or "never_attempted")
        bridge_status = str(bridge_attempt.get("status", "never_attempted") or "never_attempted")
        bridge_stages = bridge_attempt.get("stages", {}) if isinstance(bridge_attempt.get("stages", {}), dict) else {}
        bridge_trial_stage = (
            bridge_stages.get("metadata_trial", {})
            if isinstance(bridge_stages.get("metadata_trial", {}), dict)
            else {}
        )
        bridge_trial_stage_status = str(bridge_trial_stage.get("status", "") or "").strip()
        if trial_status == "never_attempted" and bridge_trial_stage_status:
            trial_status = bridge_trial_stage_status

        trial_status_unresolved = trial_status in {"", "unknown", "never_attempted"}
        if bridge_status == "bridge_completed" and trial_status_unresolved:
            trial_dry_run = bool(bridge_attempt.get("trial_dry_run", True))
            trial_status = "dry_run_ok" if trial_dry_run else "noop_applied"

        metadata_prep_ready = bool(metadata_prep_validation.get("ready_for_metadata_handoff", False))
        trial_authority_legacy = self._write_authority_mode == WRITE_AUTH_LEGACY or bridge_status == "bridge_completed"
        resolver_candidate_present = self._is_resolved_state(resolver_selected)
        resolver_stage_ok = resolver_status in {"dry_run_ok", "noop_already_selected", "write_applied"}
        trial_stage_ok = trial_status in {"dry_run_ok", "noop_applied"}

        checks = {
            "metadata_prep_ready": metadata_prep_ready,
            "resolver_candidate_present": resolver_candidate_present,
            "trial_authority_legacy": trial_authority_legacy,
            "resolver_stage_ok": resolver_stage_ok,
            "trial_stage_ok": trial_stage_ok,
            "ma_boot_ready": ma_boot_ready,
        }

        verdict = "PASS"
        if not ma_boot_ready:
            verdict = "WARN"
        elif not metadata_prep_ready or not resolver_candidate_present:
            verdict = "FAIL"
        elif not trial_authority_legacy:
            verdict = "WARN"
        elif not resolver_stage_ok or not trial_stage_ok:
            verdict = "WARN"

        blocking_reasons: list[str] = []
        if not ma_boot_ready:
            blocking_reasons.append("waiting_for_ma_boot")
        if not metadata_prep_ready:
            blocking_reasons.append("metadata_prep_not_ready")
        if not resolver_candidate_present:
            blocking_reasons.append("resolver_candidate_missing")
        if ma_boot_ready and not trial_authority_legacy:
            blocking_reasons.append("trial_authority_not_legacy")
        if not resolver_stage_ok and resolver_status != "never_attempted":
            blocking_reasons.append("resolver_stage_not_ok")
        if not trial_stage_ok and trial_status != "never_attempted":
            blocking_reasons.append("trial_stage_not_ok")

        return {
            "verdict": verdict,
            "ready_for_bridge": verdict == "PASS",
            "checks": checks,
            "blocking_reasons": blocking_reasons,
            "resolver_selected_meta_entity": resolver_selected,
            "resolver_status": resolver_status,
            "trial_status": trial_status,
            "bridge_status": bridge_status,
            "last_bridge_attempt": bridge_attempt,
            "waiting_for_ma_boot": not ma_boot_ready,
            "ma_boot_wait_reasons": ma_boot_reasons,
            "ma_boot_wait_reason": ma_boot_wait_reason,
        }

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
        entries = registry.get("entries", {}) if isinstance(registry.get("entries", {}), dict) else {}
        active_target = str(route_trace.get("active_target", "") or "").strip()

        require_control_capable = bool(policy.get("require_control_capable", True))
        prefer_fresh = bool(policy.get("prefer_fresh", True))
        max_results = int(policy.get("max_results", 5) or 5)
        max_results = max(1, min(max_results, 20))
        target_hint = str(policy.get("target_hint", "") or "").strip()

        ranked: list[dict[str, Any]] = []
        for target, entry in entries.items():
            if not isinstance(entry, dict):
                continue

            host = str(entry.get("host", "") or "").strip()
            control_capable = bool(entry.get("control_capable", False))
            feature_profile = entry.get("feature_profile", {}) if isinstance(entry.get("feature_profile", {}), dict) else {}
            empirical_profile = entry.get("empirical_profile", {}) if isinstance(entry.get("empirical_profile", {}), dict) else {}

            if require_control_capable and not control_capable:
                continue
            if host == "":
                continue

            availability_quality = str(feature_profile.get("availability_quality", "missing") or "missing")
            availability_points = self._availability_points(availability_quality)
            if prefer_fresh and availability_quality == "missing":
                continue

            observed_caps = feature_profile.get("observed_capabilities", [])
            observed_count = len(observed_caps) if isinstance(observed_caps, list) else 0

            empirical_bonus = self._empirical_bonus(empirical_profile)

            target_match_bonus = 5 if str(target) == active_target else 0
            hint_bonus = 0
            if target_hint:
                target_l = str(target).lower()
                hint_l = target_hint.lower()
                if hint_l in target_l:
                    hint_bonus = 12

            score = (
                (40 if control_capable else 0)
                + (25 if host else 0)
                + availability_points
                + min(observed_count, 10)
                + target_match_bonus
                + hint_bonus
                + empirical_bonus
            )

            ranked.append(
                {
                    "target": str(target),
                    "score": round(float(score), 2),
                    "host": host,
                    "host_type": entry.get("host_type", "generic"),
                    "resolver_module": entry.get("resolver_module", "hostmods.generic"),
                    "control_capable": control_capable,
                    "availability_quality": availability_quality,
                    "observed_capability_count": observed_count,
                    "empirical_bonus": empirical_bonus,
                    "score_breakdown": {
                        "control_capable": 40 if control_capable else 0,
                        "host_resolved": 25 if host else 0,
                        "availability": availability_points,
                        "observed_capabilities": min(observed_count, 10),
                        "active_target_bonus": target_match_bonus,
                        "target_hint_bonus": hint_bonus,
                        "empirical_bonus": empirical_bonus,
                    },
                    "scheduler_profile": entry.get("scheduler_profile", {}),
                }
            )

        ranked.sort(key=lambda item: (-float(item.get("score", 0.0)), str(item.get("target", ""))))
        top = ranked[:max_results]
        selected = top[0] if top else None
        helper_fallback_reason = ""

        if selected is None:
            helper_state = self.hass.states.get(LEGACY_ACTIVE_TARGET_HELPER)
            helper_current = str(helper_state.state if helper_state is not None else "").strip()
            helper_options: list[str] = []
            if helper_state is not None:
                options_attr = helper_state.attributes.get("options", [])
                if isinstance(options_attr, list):
                    helper_options = [
                        str(item).strip()
                        for item in options_attr
                        if isinstance(item, str) and str(item).strip()
                    ]

            helper_current_resolved = self._is_resolved_state(helper_current)
            helper_current_in_options = helper_current_resolved and helper_current in helper_options
            helper_entry = entries.get(helper_current, {}) if isinstance(entries.get(helper_current, {}), dict) else {}
            helper_entry_control_capable = bool(helper_entry.get("control_capable", False))
            helper_entry_host = str(helper_entry.get("host", "") or "").strip()
            helper_entry_host_resolved = self._is_resolved_state(helper_entry_host)
            helper_fallback_eligible = (
                helper_current_in_options
                and helper_entry_control_capable
                and helper_entry_host_resolved
            )

            if helper_fallback_eligible:
                selected = {
                    "target": helper_current,
                    "score": 0.0,
                    "host": helper_entry_host,
                    "host_type": str(helper_entry.get("host_type", "fallback") or "fallback"),
                    "resolver_module": str(helper_entry.get("resolver_module", "helper_current_fallback") or "helper_current_fallback"),
                    "control_capable": helper_entry_control_capable,
                    "availability_quality": "fallback",
                    "observed_capability_count": 0,
                    "empirical_bonus": 0.0,
                    "score_breakdown": {
                        "control_capable": 40,
                        "host_resolved": 25,
                        "availability": 0,
                        "observed_capabilities": 0,
                        "active_target_bonus": 0,
                        "target_hint_bonus": 0,
                        "empirical_bonus": 0.0,
                        "fallback_bonus": 1,
                    },
                    "scheduler_profile": {
                        "selection_mode": "helper_current_fallback",
                    },
                }
                top = [selected]
            elif helper_current_in_options:
                helper_fallback_reason = (
                    "Helper current target fallback rejected because registry entry is not control-capable "
                    "or host is unresolved"
                )
            elif helper_current_resolved:
                helper_fallback_reason = "Helper current target fallback rejected because target is not in helper options"

        if self._write_authority_mode == WRITE_AUTH_LEGACY:
            helper_state = self.hass.states.get(LEGACY_ACTIVE_TARGET_HELPER)
            helper_current = str(helper_state.state if helper_state is not None else "").strip()
            helper_options: list[str] = []
            if helper_state is not None:
                options_attr = helper_state.attributes.get("options", [])
                if isinstance(options_attr, list):
                    helper_options = [
                        str(item).strip()
                        for item in options_attr
                        if isinstance(item, str) and str(item).strip()
                    ]

            helper_current_resolved = self._is_resolved_state(helper_current)
            helper_current_in_options = helper_current_resolved and helper_current in helper_options
            if helper_current_in_options:
                helper_entry = entries.get(helper_current, {}) if isinstance(entries.get(helper_current, {}), dict) else {}
                helper_host = str(helper_entry.get("host", "") or "").strip()
                helper_host_type = str(helper_entry.get("host_type", "legacy_helper") or "legacy_helper")
                helper_resolver_module = str(
                    helper_entry.get("resolver_module", "legacy_helper_authority") or "legacy_helper_authority"
                )
                helper_control_capable = bool(helper_entry.get("control_capable", False))
                helper_feature_profile = (
                    helper_entry.get("feature_profile", {})
                    if isinstance(helper_entry.get("feature_profile", {}), dict)
                    else {}
                )
                helper_availability_quality = str(
                    helper_feature_profile.get("availability_quality", "legacy_helper_authority")
                    or "legacy_helper_authority"
                )

                selected = {
                    "target": helper_current,
                    "score": 9999.0,
                    "host": helper_host,
                    "host_type": helper_host_type,
                    "resolver_module": helper_resolver_module,
                    "control_capable": helper_control_capable,
                    "availability_quality": helper_availability_quality,
                    "observed_capability_count": 0,
                    "empirical_bonus": 0.0,
                    "score_breakdown": {
                        "legacy_authority_pin": 9999,
                    },
                    "scheduler_profile": {
                        "selection_mode": "legacy_helper_authority",
                    },
                }

                filtered_top = [
                    item for item in top if str(item.get("target", "") or "") != helper_current
                ]
                top = [selected, *filtered_top][:max_results]

        status = "selected" if selected is not None else "no_candidate"
        selection_mode = str(selected.get("scheduler_profile", {}).get("selection_mode", "") if isinstance(selected, dict) else "")
        if selected is None:
            reason = helper_fallback_reason or "No candidates satisfied scheduler policy"
        elif selection_mode == "legacy_helper_authority":
            reason = "Legacy authority mode pins scheduler selection to helper current target"
        elif selection_mode == "helper_current_fallback":
            reason = "Using helper current target fallback because scheduler ranking produced no candidates"
        else:
            reason = "Highest scored candidate selected"

        candidate_count = len(ranked)
        if selected is not None and candidate_count == 0:
            candidate_count = 1

        return {
            "status": status,
            "reason": reason,
            "policy": {
                "require_control_capable": require_control_capable,
                "prefer_fresh": prefer_fresh,
                "max_results": max_results,
                "target_hint": target_hint,
            },
            "selected_target": str(selected.get("target", "") if isinstance(selected, dict) else ""),
            "selected_host": str(selected.get("host", "") if isinstance(selected, dict) else ""),
            "selected_score": float(selected.get("score", 0.0) if isinstance(selected, dict) else 0.0),
            "candidate_count": candidate_count,
            "ranked_candidates": top,
        }

    def _build_scheduler_validation(
        self,
        *,
        registry: dict[str, Any],
        route_trace: dict[str, Any],
        contract_validation: dict[str, Any],
    ) -> dict[str, Any]:
        contract_valid = bool(contract_validation.get("valid", False))
        route_decision = str(route_trace.get("decision", "") or "")
        ma_boot_ready, ma_boot_reasons = self._is_startup_recovery_boot_ready()
        ma_boot_wait_reason = self._format_startup_boot_wait_reasons(ma_boot_reasons)

        default_policy = {
            "require_control_capable": True,
            "prefer_fresh": True,
            "max_results": 5,
            "target_hint": "",
        }
        decision = self._compute_scheduler_decision(registry=registry, route_trace=route_trace, policy=default_policy)

        checks = {
            "contract_valid": contract_valid,
            "registry_present": isinstance(registry.get("entries", {}), dict) and len(registry.get("entries", {})) > 0,
            "route_trace_present": route_decision != "",
            "candidate_available": decision.get("candidate_count", 0) > 0,
            "no_authority_expansion": self._write_authority_mode in WRITE_AUTH_ALLOWED,
            "ma_boot_ready": ma_boot_ready,
        }

        verdict = "PASS"
        if not checks["route_trace_present"]:
            verdict = "FAIL"
        elif not checks["ma_boot_ready"]:
            verdict = "WARN"
        elif not checks["contract_valid"] or not checks["registry_present"]:
            verdict = "FAIL"
        elif not checks["candidate_available"] or not checks["no_authority_expansion"]:
            verdict = "WARN"

        blocking_reasons: list[str] = []
        if not checks["route_trace_present"]:
            blocking_reasons.append("route_trace_missing")
        if not checks["ma_boot_ready"]:
            blocking_reasons.append("waiting_for_ma_boot")
        if checks["ma_boot_ready"] and not checks["contract_valid"]:
            blocking_reasons.append("contract_invalid")
        if checks["ma_boot_ready"] and not checks["registry_present"]:
            blocking_reasons.append("registry_missing")
        if checks["ma_boot_ready"] and not checks["candidate_available"]:
            blocking_reasons.append("no_scheduler_candidate")
        if checks["ma_boot_ready"] and not checks["no_authority_expansion"]:
            blocking_reasons.append("authority_mode_not_legacy")

        return {
            "verdict": verdict,
            "ready_for_scheduler_use": verdict == "PASS",
            "checks": checks,
            "route_decision": route_decision,
            "default_policy": default_policy,
            "default_decision": decision,
            "blocking_reasons": blocking_reasons,
            "waiting_for_ma_boot": not ma_boot_ready,
            "ma_boot_wait_reasons": ma_boot_reasons,
            "ma_boot_wait_reason": ma_boot_wait_reason,
        }

    def _build_control_center_validation(self) -> dict[str, Any]:
        settings = dict(self._control_center_settings)
        mapping_preset = str(settings.get("mapping_preset", "custom") or "custom").strip().lower()
        required_keys = sorted(settings.keys())
        scene_keys = [
            "button_1_scene",
            "button_2_scene",
            "button_3_scene",
            "button_4_scene",
        ]
        unresolved_scenes = [
            key for key in scene_keys if str(settings.get(key, "") or "").strip().lower() in {"", "scene.none"}
        ]
        resolved_scene_bindings = [key for key in scene_keys if key not in unresolved_scenes]
        quick_trigger_scene = str(settings.get("button_1_scene", "scene.none") or "scene.none").strip()
        quick_trigger_ready = quick_trigger_scene.lower() not in {"", "scene.none"}

        effective_mapping = {
            "encoder_turn": str(settings.get("encoder_turn_action", "") or ""),
            "encoder_press": str(settings.get("encoder_press_action", "") or ""),
            "encoder_long_press": str(settings.get("encoder_long_press_action", "") or ""),
            "button_1": str(settings.get("button_1_scene", "scene.none") or "scene.none"),
            "button_2": str(settings.get("button_2_scene", "scene.none") or "scene.none"),
            "button_3": str(settings.get("button_3_scene", "scene.none") or "scene.none"),
            "button_4": str(settings.get("button_4_scene", "scene.none") or "scene.none"),
        }

        non_dry_run_supported_actions = [
            "scene_quick_trigger",
            "no_op",
            "button_1_scene",
            "button_2_scene",
            "button_3_scene",
            "button_4_scene",
        ]
        non_dry_run_pending_actions = [
            "volume",
            "brightness",
            "target_cycle",
            "source_cycle",
            "play_pause",
            "mute_toggle",
        ]

        readiness_state = "ready" if quick_trigger_ready or len(resolved_scene_bindings) > 0 else "needs_scene_binding"
        recommended_next_step = (
            "Bind at least one scene (button 1 recommended) to enable non-dry-run scene execution"
            if readiness_state != "ready"
            else "Control-center scene bindings are ready for bounded execution"
        )

        return {
            "schema_version": "p6_s02.v1",
            "settings": settings,
            "mapping_preset": mapping_preset,
            "preset_applied": mapping_preset != "custom",
            "effective_mapping": effective_mapping,
            "required_keys": required_keys,
            "settings_present": len(required_keys) > 0,
            "read_only_mode": bool(settings.get("read_only_mode", True)),
            "unresolved_scene_bindings": unresolved_scenes,
            "resolved_scene_bindings": resolved_scene_bindings,
            "configured_scene_bindings_count": len(resolved_scene_bindings),
            "total_scene_bindings": len(scene_keys),
            "quick_trigger_scene": quick_trigger_scene,
            "quick_trigger_ready": quick_trigger_ready,
            "non_dry_run_supported_actions": non_dry_run_supported_actions,
            "non_dry_run_pending_actions": non_dry_run_pending_actions,
            "readiness_state": readiness_state,
            "recommended_next_step": recommended_next_step,
            "ready_for_customization": len(required_keys) > 0,
            "ready_for_execution": readiness_state == "ready",
        }

    def _build_handoff_inventory(self) -> dict[str, Any]:
        """Expose legacy-only dependency map and component scaffolding status for cutover planning."""
        component_scaffolds = self._build_component_scaffolds()
        target_options_attempt = self._last_target_options_attempt if isinstance(self._last_target_options_attempt, dict) else {}
        auto_select_attempt = self._last_auto_select_attempt if isinstance(self._last_auto_select_attempt, dict) else {}
        metadata_attempt = self._last_metadata_resolver_attempt if isinstance(self._last_metadata_resolver_attempt, dict) else {}
        metadata_bridge_attempt = self._last_metadata_bridge_attempt if isinstance(self._last_metadata_bridge_attempt, dict) else {}

        target_options_status = "planned"
        if bool(component_scaffolds.get("target_options_plan", {}).get("candidates")):
            target_options_status = "scaffolded"
        target_options_attempt_status = str(target_options_attempt.get("status", "") or "")
        if target_options_attempt_status in {"dry_run_ok", "options_applied"}:
            target_options_status = "implemented"

        auto_select_status = "planned"
        if bool(component_scaffolds.get("auto_select_plan", {}).get("selected_target")):
            auto_select_status = "scaffolded"
        auto_select_attempt_status = str(auto_select_attempt.get("status", "") or "")
        if auto_select_attempt_status in {"dry_run_ok", "noop_already_selected", "write_applied"}:
            auto_select_status = "implemented"

        metadata_status = (
            "scaffolded"
            if bool(component_scaffolds.get("metadata_resolver_plan", {}).get("selected_meta_entity"))
            else "planned"
        )
        metadata_attempt_status = str(metadata_attempt.get("status", "") or "")
        metadata_bridge_status = str(metadata_bridge_attempt.get("status", "") or "")
        if metadata_attempt_status in {"dry_run_ok", "noop_already_selected", "write_applied"} or metadata_bridge_status == "bridge_completed":
            metadata_status = "implemented"

        legacy_dependency_map = [
            {
                "feature": "target_options_builder",
                "legacy_surface": "script.ma_update_target_options",
                "component_scaffold_status": target_options_status,
                "component_surface": "handoff_inventory.target_options_builder",
                "scheduler_relevance": "high",
                "notes": "Component now exposes candidate/options scaffold plan; write-path ownership still legacy.",
            },
            {
                "feature": "auto_select_pipeline",
                "legacy_surface": "script.ma_auto_select",
                "component_scaffold_status": auto_select_status,
                "component_surface": "handoff_inventory.auto_select_pipeline",
                "scheduler_relevance": "high",
                "notes": "Component now exposes deterministic auto-select planning scaffold; runtime loop remains legacy-owned.",
            },
            {
                "feature": "active_target_apply",
                "legacy_surface": "input_select.ma_active_target",
                "component_scaffold_status": "implemented",
                "component_surface": "service.apply_scheduler_choice",
                "scheduler_relevance": "high",
                "notes": "Guarded component apply path now available (authority/debounce/reentrancy/option guards).",
            },
            {
                "feature": "metadata_resolver_authority",
                "legacy_surface": "sensor.ma_active_meta_entity / sensor.now_playing_entity",
                "component_scaffold_status": metadata_status,
                "component_surface": "service.run_metadata_resolver_scaffold + metadata_prep_validation",
                "scheduler_relevance": "medium",
                "notes": "Component now exposes metadata resolver scaffold planning + bounded helper apply; ownership remains legacy-authoritative.",
            },
            {
                "feature": "control_host_resolution_runtime_authority",
                "legacy_surface": "sensor.ma_control_hosts / sensor.ma_control_host",
                "component_scaffold_status": "implemented",
                "component_surface": "registry.host_resolution + route_trace",
                "scheduler_relevance": "high",
                "notes": "Pluggable host resolver + route-trace scaffolds implemented for scheduler feed.",
            },
        ]

        implemented = sum(1 for row in legacy_dependency_map if row.get("component_scaffold_status") == "implemented")
        scaffolded = sum(1 for row in legacy_dependency_map if row.get("component_scaffold_status") == "scaffolded")
        planned = sum(1 for row in legacy_dependency_map if row.get("component_scaffold_status") == "planned")
        deferred = sum(1 for row in legacy_dependency_map if row.get("component_scaffold_status") == "deferred")

        return {
            "schema_version": "handoff_inventory.v1",
            "legacy_dependency_map": legacy_dependency_map,
            "component_scaffolds": component_scaffolds,
            "summary": {
                "total": len(legacy_dependency_map),
                "implemented": implemented,
                "scaffolded": scaffolded,
                "planned": planned,
                "deferred": deferred,
                "ready_for_full_handoff": planned == 0 and deferred == 0,
            },
        }

    def _build_component_scaffolds(self) -> dict[str, Any]:
        """Build initial component-native scaffold plans for legacy selection ownership handoff."""
        registry: dict[str, Any]
        route_trace: dict[str, Any]
        if isinstance(self.data, dict) and isinstance(self.data.get("registry", {}), dict):
            registry = self.data.get("registry", {})
        else:
            registry = build_registry_snapshot(
                hass=self.hass,
                legacy_control_host_entity=LEGACY_CONTROL_HOST,
                legacy_control_targets_entity=LEGACY_CONTROL_TARGETS,
                legacy_rooms_json_entity=LEGACY_ROOMS_JSON,
                legacy_rooms_raw_entity=LEGACY_ROOMS_RAW,
                legacy_active_target_helper_entity=LEGACY_ACTIVE_TARGET_HELPER,
                legacy_active_target_entity=LEGACY_SURFACES["active_target"],
            )

        if isinstance(self.data, dict) and isinstance(self.data.get("route_trace", {}), dict):
            route_trace = self.data.get("route_trace", {})
        else:
            active_target_state = self.hass.states.get(LEGACY_SURFACES["active_target"])
            active_control_path_state = self.hass.states.get(LEGACY_SURFACES["active_control_path"])
            route_trace = build_route_trace(
                active_target=str(active_target_state.state if active_target_state is not None else ""),
                active_control_path=str(active_control_path_state.state if active_control_path_state is not None else ""),
                registry=registry,
            )
        entries = registry.get("entries", {}) if isinstance(registry.get("entries", {}), dict) else {}

        target_options_plan = self._compute_component_target_options_plan()
        helper_options = target_options_plan.get("proposed_options", []) if isinstance(target_options_plan.get("proposed_options", []), list) else []
        candidates = target_options_plan.get("selectable_candidates", []) if isinstance(target_options_plan.get("selectable_candidates", []), list) else []
        detected_candidate = str(target_options_plan.get("detected_candidate", "") or "").strip()

        active_target = str(route_trace.get("active_target", "") or "").strip()
        selected_target = ""
        selection_reason = "no_candidate"
        detected_ready = False
        if self._is_resolved_state(detected_candidate) and detected_candidate in helper_options:
            detected_state = self.hass.states.get(detected_candidate)
            if detected_state is not None:
                detected_norm = self._normalize_state(str(detected_state.state or ""))
                detected_ready = detected_norm not in {"", "unknown", "unavailable"}

        if detected_ready:
            selected_target = detected_candidate
            selection_reason = "detected_candidate_ready"
        elif active_target and active_target in candidates:
            selected_target = active_target
            selection_reason = "active_target_candidate"
        else:
            for target_id in helper_options:
                if target_id.lower() == "none" or not target_id.startswith("media_player."):
                    continue
                state = self.hass.states.get(target_id)
                if state is None:
                    continue
                state_l = self._normalize_state(state.state)
                if state_l in {"playing", "paused"}:
                    selected_target = target_id
                    selection_reason = "first_active_helper_option"
                    break
        if not selected_target and candidates:
            selected_target = candidates[0]
            selection_reason = "first_candidate_fallback"

        best_candidate = ""
        best_score = 0
        meta_resolver_state = self.hass.states.get(LEGACY_META_RESOLVER)
        if meta_resolver_state is not None:
            best_candidate = str(meta_resolver_state.attributes.get("best_entity", "") or "").strip()
            best_score = int(meta_resolver_state.attributes.get("best_score", 0) or 0)

        detected_candidate = str(self.hass.states.get(LEGACY_META_DETECTED_ENTITY).state if self.hass.states.get(LEGACY_META_DETECTED_ENTITY) is not None else "").strip()
        detected_candidate = detected_candidate if self._is_resolved_state(detected_candidate) else ""

        selected_meta_entity = ""
        metadata_selection_reason = "no_candidate"
        if self._is_resolved_state(best_candidate):
            selected_meta_entity = best_candidate
            metadata_selection_reason = "meta_resolver_best_entity"
        elif detected_candidate:
            selected_meta_entity = detected_candidate
            metadata_selection_reason = "detected_meta_entity"

        if not selected_meta_entity and selected_target:
            selected_meta_entity = selected_target
            metadata_selection_reason = "selected_target_fallback"

        override_state = self.hass.states.get(LEGACY_META_OVERRIDE_ACTIVE)
        override_entity_state = self.hass.states.get(LEGACY_META_OVERRIDE_ENTITY)
        override_active = self._normalize_state(override_state.state if override_state is not None else "") == "on"
        override_entity = str(override_entity_state.state if override_entity_state is not None else "").strip()
        override_entity = override_entity if self._is_resolved_state(override_entity) else ""

        return {
            "target_options_plan": target_options_plan,
            "auto_select_plan": {
                "active_target": active_target,
                "selected_target": selected_target,
                "selection_reason": selection_reason,
                "ready": selected_target != "",
            },
            "metadata_resolver_plan": {
                "override_active_entity": LEGACY_META_OVERRIDE_ACTIVE,
                "override_entity_helper": LEGACY_META_OVERRIDE_ENTITY,
                "current_override_active": override_active,
                "current_override_entity": override_entity,
                "meta_resolver_entity": LEGACY_META_RESOLVER,
                "detected_meta_entity_source": LEGACY_META_DETECTED_ENTITY,
                "best_candidate": best_candidate,
                "best_score": best_score,
                "detected_candidate": detected_candidate,
                "selected_meta_entity": selected_meta_entity,
                "selection_reason": metadata_selection_reason,
                "ready": selected_meta_entity != "",
            },
        }

    def _build_contract_validation(self) -> dict[str, Any]:
        required_entities = {
            "active_target": LEGACY_SURFACES["active_target"],
            "active_control_path": LEGACY_SURFACES["active_control_path"],
            "active_control_capable": LEGACY_SURFACES["active_control_capable"],
            "control_targets": LEGACY_CONTROL_TARGETS,
            "rooms_json": LEGACY_ROOMS_JSON,
            "rooms_raw": LEGACY_ROOMS_RAW,
        }
        soft_required_entities = {
            "control_hosts": LEGACY_SURFACES["control_hosts"],
            "control_host": LEGACY_CONTROL_HOST,
        }
        missing_required = [
            key for key, entity_id in required_entities.items() if self.hass.states.get(entity_id) is None
        ]
        missing_soft_required = [
            key for key, entity_id in soft_required_entities.items() if self.hass.states.get(entity_id) is None
        ]
        unresolved_required: list[str] = []
        unresolved_soft_required: list[str] = []
        required_states: dict[str, str] = {}
        for key, entity_id in required_entities.items():
            state = self.hass.states.get(entity_id)
            state_value = state.state if state is not None else "missing"
            required_states[key] = state_value
            if state is None:
                continue
            if not self._is_resolved_state(state_value):
                unresolved_required.append(key)

        soft_required_states: dict[str, str] = {}
        for key, entity_id in soft_required_entities.items():
            state = self.hass.states.get(entity_id)
            state_value = state.state if state is not None else "missing"
            soft_required_states[key] = state_value
            if state is None:
                continue
            if not self._is_resolved_state(state_value):
                unresolved_soft_required.append(key)

        soft_surface_warnings = [*missing_soft_required, *unresolved_soft_required]

        return {
            "required_entities": required_entities,
            "soft_required_entities": soft_required_entities,
            "missing_required": missing_required,
            "missing_soft_required": missing_soft_required,
            "unresolved_required": unresolved_required,
            "unresolved_soft_required": unresolved_soft_required,
            "required_states": required_states,
            "soft_required_states": soft_required_states,
            "soft_surface_warnings": soft_surface_warnings,
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

    def _build_route_safety_validation(
        self,
        *,
        parity: dict[str, Any],
        route_trace: dict[str, Any],
    ) -> dict[str, Any]:
        """Build explicit route-safety diagnostics for active-target binding + fail-closed host posture."""
        active_target = str(parity.get("active_target", "") or "").strip()
        control_hosts = str(parity.get("control_hosts", "") or "").strip()
        route_decision = str(route_trace.get("decision", "") or "").strip()

        selected_target = route_trace.get("selected_target", {})
        selected_target = selected_target if isinstance(selected_target, dict) else {}
        selected_target_id = str(selected_target.get("target", "") or "").strip()
        selected_target_host = str(selected_target.get("host", "") or "").strip()

        active_target_resolved = self._is_resolved_state(active_target)
        control_hosts_resolved = self._is_resolved_state(control_hosts)
        selected_target_matches_active = (
            active_target_resolved
            and self._is_resolved_state(selected_target_id)
            and selected_target_id == active_target
        )
        selected_target_host_resolved = self._is_resolved_state(selected_target_host)

        blocking_reasons: list[str] = []
        if active_target_resolved and not selected_target_matches_active:
            blocking_reasons.append("selected_target_mismatch")
        if route_decision == "route_linkplay_tcp" and not selected_target_host_resolved:
            blocking_reasons.append("selected_target_host_unresolved")
        if not control_hosts_resolved:
            blocking_reasons.append("control_hosts_unresolved")

        verdict = "PASS"
        if "selected_target_mismatch" in blocking_reasons:
            verdict = "FAIL"
        elif "selected_target_host_unresolved" in blocking_reasons:
            verdict = "WARN"

        return {
            "verdict": verdict,
            "route_decision": route_decision,
            "active_target": active_target,
            "selected_target": selected_target_id,
            "selected_target_host": selected_target_host,
            "ready_for_cutover": verdict == "PASS" and selected_target_host_resolved,
            "checks": {
                "active_target_resolved": active_target_resolved,
                "selected_target_matches_active": selected_target_matches_active,
                "selected_target_host_resolved": selected_target_host_resolved,
                "control_hosts_resolved": control_hosts_resolved,
            },
            "blocking_reasons": blocking_reasons,
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
                "long_idle_stale_hidden": False,
                "suppression_reason": META_SUPPRESSION_ENTITY_MISSING,
                "paused_hide_s": float(META_POLICY_DEFAULTS["paused_hide_s"]),
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
                "long_idle_stale_hidden": False,
                "suppression_reason": META_SUPPRESSION_ENTITY_MISSING,
                "paused_hide_s": float(META_POLICY_DEFAULTS["paused_hide_s"]),
            }

        state_norm = self._normalize_state(state.state)
        play_state_attr = self._normalize_state(str(state.attributes.get("play_state", "") or ""))
        is_playing_attr = state.attributes.get("is_playing")
        is_paused_attr = state.attributes.get("is_paused")
        pos_age_s = self._timestamp_age_seconds(state.attributes.get("media_position_updated_at"))
        # Read paused_hide_s from HA helper; fall back to META_POLICY_DEFAULTS if unavailable.
        paused_hide_s_state = self.hass.states.get(LEGACY_META_PAUSED_HIDE_S)
        paused_hide_s = float(paused_hide_s_state.state) if (
            paused_hide_s_state is not None
            and paused_hide_s_state.state not in ("", "unknown", "unavailable")
        ) else float(META_POLICY_DEFAULTS["paused_hide_s"])
        # recent_progress uses paused_hide_s so that the "still fresh" window for paused
        # entities matches the user-configured hide threshold rather than a hardcoded constant.
        recent_progress = pos_age_s is not None and pos_age_s <= paused_hide_s

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
        # Entity is not playing or paused at all — idle/off/stopped with no active signal.
        # This catches the "came home after all day" stale display case.
        long_idle_stale_hidden = not playing_signal and not paused_signal

        # Canonical suppression reason — single field that explains why metadata is hidden.
        if playing_signal:
            suppression_reason = META_SUPPRESSION_PLAYING
        elif paused_signal and recent_progress:
            suppression_reason = META_SUPPRESSION_PAUSED_FRESH
        elif paused_without_fresh_signal:
            suppression_reason = META_SUPPRESSION_PAUSED_STALE
        elif long_idle_stale_hidden:
            suppression_reason = META_SUPPRESSION_LONG_IDLE
        else:
            suppression_reason = META_SUPPRESSION_NO_FRESH_SIGNAL

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
            "long_idle_stale_hidden": long_idle_stale_hidden,
            "suppression_reason": suppression_reason,
            "paused_hide_s": paused_hide_s,
        }

    def _metadata_candidate_payload_ready(self) -> bool:
        candidates_state = self.hass.states.get(LEGACY_META_CANDIDATES)
        if candidates_state is None:
            resolver_state = self.hass.states.get(LEGACY_META_RESOLVER)
            if resolver_state is None:
                return False
            resolver_best_entity = str(resolver_state.attributes.get("best_entity", "") or "").strip()
            resolver_best_score = resolver_state.attributes.get("best_score", 0)
            resolver_score_positive = isinstance(resolver_best_score, (int, float)) and float(resolver_best_score) > 0
            return self._is_resolved_state(resolver_best_entity) and resolver_score_positive

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

        resolver_state = self.hass.states.get(LEGACY_META_RESOLVER)
        if resolver_state is not None:
            resolver_best_entity = str(resolver_state.attributes.get("best_entity", "") or "").strip()
            resolver_best_score = resolver_state.attributes.get("best_score", 0)
            resolver_score_positive = isinstance(resolver_best_score, (int, float)) and float(resolver_best_score) > 0
            if self._is_resolved_state(resolver_best_entity) and resolver_score_positive:
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
        long_idle_stale_hidden = bool(now_playing_signal.get("long_idle_stale_hidden", False))
        now_playing_fresh_play_signal = bool(now_playing_signal.get("fresh_play_signal", False))
        now_playing_title_signal_ready = now_playing_title_resolved or (
            now_playing_fresh_play_signal and active_meta_entity_resolved
        )
        metadata_authority_owner = "legacy_contract_surfaces"
        metadata_cutover_active = False
        cutover_block_reason = "metadata_authority_not_cut_over"
        no_authority_expansion = self._write_authority_mode in WRITE_AUTH_ALLOWED

        gate_checks: dict[str, bool] = {
            "contract_valid": contract_valid,
            "active_meta_entity_resolved": active_meta_entity_resolved,
            "now_playing_entity_resolved": now_playing_entity_resolved,
            "now_playing_state_resolved": now_playing_state_resolved,
            "now_playing_title_signal_ready": now_playing_title_signal_ready,
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
        if not now_playing_title_signal_ready:
            blocking_reasons.append("now_playing_title_unresolved")
        if not candidate_payload_ready:
            blocking_reasons.append("candidate_payload_not_ready")
        if not route_trace_present:
            blocking_reasons.append("route_trace_missing")
        if not no_authority_expansion:
            blocking_reasons.append("authority_mode_not_legacy")
        if paused_without_fresh_signal and now_playing_title_resolved:
            blocking_reasons.append("paused_without_recent_progress")
        elif long_idle_stale_hidden and now_playing_title_resolved:
            blocking_reasons.append("long_idle_stale_hidden")
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
        elif long_idle_stale_hidden and now_playing_title_resolved:
            verdict = "WARN"
        elif not now_playing_title_signal_ready or not candidate_payload_ready:
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
                "now_playing_title_signal_ready": now_playing_title_signal_ready,
                "candidate_payload_ready": candidate_payload_ready,
                "route_trace_present": route_trace_present,
                "no_authority_expansion": no_authority_expansion,
                "now_playing_fresh_play_signal": now_playing_fresh_play_signal,
                "now_playing_paused_without_fresh_signal": paused_without_fresh_signal,
                "now_playing_long_idle_stale_hidden": long_idle_stale_hidden,
                "now_playing_suppression_reason": now_playing_signal.get("suppression_reason", ""),
            },
            "values": {
                "active_meta_entity": active_meta_entity,
                "now_playing_entity": now_playing_entity,
                "now_playing_state": now_playing_state,
                "now_playing_title": now_playing_title,
                "now_playing_position_age_s": now_playing_signal.get("position_age_s"),
                "paused_hide_s": now_playing_signal.get("paused_hide_s"),
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
            "no_authority_expansion": self._write_authority_mode in WRITE_AUTH_ALLOWED,
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
        no_authority_expansion = self._write_authority_mode in WRITE_AUTH_ALLOWED

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
            "no_authority_expansion": self._write_authority_mode in WRITE_AUTH_ALLOWED,
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
            legacy_active_target_helper_entity=LEGACY_ACTIVE_TARGET_HELPER,
            legacy_active_target_entity=LEGACY_SURFACES["active_target"],
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
        route_safety_validation = self._build_route_safety_validation(
            parity=parity,
            route_trace=route_trace,
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
        scheduler_validation = self._build_scheduler_validation(
            registry=registry,
            route_trace=route_trace,
            contract_validation=contract_validation,
        )
        metadata_bridge_validation = self._build_metadata_bridge_validation(
            metadata_prep_validation=metadata_prep_validation,
        )

        ma_backend_profile = self._build_ma_backend_profile()

        return {
            "legacy": legacy,
            "parity": parity,
            "unresolved_sources": unresolved_sources,
            "mismatches": mismatches,
            "registry": registry,
            "route_trace": route_trace,
            "contract_validation": contract_validation,
            "selection_handoff_validation": selection_handoff_validation,
            "route_safety_validation": route_safety_validation,
            "metadata_prep_validation": metadata_prep_validation,
            "capability_profile_validation": capability_profile_validation,
            "action_catalog_validation": action_catalog_validation,
            "crossfade_balance_validation": crossfade_balance_validation,
            "scheduler_validation": scheduler_validation,
            "metadata_bridge_validation": metadata_bridge_validation,
            "handoff_inventory": self._build_handoff_inventory(),
            "ma_backend_profile": ma_backend_profile,
            "control_center_validation": self._build_control_center_validation(),
            "write_controls": self._build_write_controls(),
            "captured_at": datetime.now(UTC).isoformat(),
        }

    def _build_ma_backend_profile(self) -> dict[str, Any]:
        profile_state = self.hass.states.get(LEGACY_SERVER_PROFILE)
        profile_effective_state = self.hass.states.get(LEGACY_SERVER_PROFILE_EFFECTIVE)

        profile_value = ""
        if profile_state is not None:
            profile_value = str(profile_state.state or "").strip().lower()

        selected_url = ""
        if profile_effective_state is not None:
            selected_url = str(profile_effective_state.attributes.get("selected_url", "") or "").strip()

        return {
            "profile_entity": LEGACY_SERVER_PROFILE,
            "effective_entity": LEGACY_SERVER_PROFILE_EFFECTIVE,
            "profile": profile_value,
            "selected_url": selected_url,
            "profile_resolved": self._is_resolved_state(profile_value),
            "selected_url_resolved": self._is_resolved_state(selected_url),
        }

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
        requested_at = datetime.now(UTC).isoformat()
        corr = (correlation_id or "").strip() or f"scheduler-{uuid4().hex[:12]}"

        snapshot = self._build_snapshot()
        registry = snapshot.get("registry", {}) if isinstance(snapshot.get("registry", {}), dict) else {}
        route_trace = snapshot.get("route_trace", {}) if isinstance(snapshot.get("route_trace", {}), dict) else {}

        decision = self._compute_scheduler_decision(
            registry=registry,
            route_trace=route_trace,
            policy={
                "require_control_capable": bool(require_control_capable),
                "prefer_fresh": bool(prefer_fresh),
                "max_results": int(max_results),
                "target_hint": str(target_hint or "").strip(),
            },
        )

        result = {
            "requested_at": requested_at,
            "completed_at": datetime.now(UTC).isoformat(),
            "correlation_id": corr,
            **decision,
        }

        self._last_scheduler_decision = result
        self.async_set_updated_data(self._build_snapshot())
        return result

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
        requested_at = datetime.now(UTC).isoformat()
        corr = (correlation_id or "").strip() or f"scheduler-apply-{uuid4().hex[:12]}"

        snapshot = self._build_snapshot()
        registry = snapshot.get("registry", {}) if isinstance(snapshot.get("registry", {}), dict) else {}
        route_trace = snapshot.get("route_trace", {}) if isinstance(snapshot.get("route_trace", {}), dict) else {}

        decision = self._compute_scheduler_decision(
            registry=registry,
            route_trace=route_trace,
            policy={
                "require_control_capable": bool(require_control_capable),
                "prefer_fresh": bool(prefer_fresh),
                "max_results": int(max_results),
                "target_hint": str(target_hint or "").strip(),
            },
        )

        selected_target = str(decision.get("selected_target", "") or "").strip()
        helper_state = self.hass.states.get(LEGACY_ACTIVE_TARGET_HELPER)

        result: dict[str, Any] = {
            "status": "pending",
            "reason": "",
            "requested_at": requested_at,
            "completed_at": requested_at,
            "correlation_id": corr,
            "dry_run": bool(dry_run),
            "force": bool(force),
            "authority_mode": self._write_authority_mode,
            "target_helper_entity": LEGACY_ACTIVE_TARGET_HELPER,
            **decision,
        }

        if not selected_target:
            result["status"] = "blocked_no_candidate"
            result["reason"] = "Scheduler produced no selected target"
        elif self._write_authority_mode != WRITE_AUTH_COMPONENT:
            result["status"] = "blocked_authority"
            result["reason"] = "Write authority is legacy; scheduler apply is intentionally blocked"
        elif self._write_in_progress and not force:
            result["status"] = "blocked_reentrancy"
            result["reason"] = "A prior write attempt is still in progress"
        elif not force and not dry_run and self._last_write_monotonic > 0:
            elapsed = monotonic() - self._last_write_monotonic
            if elapsed < self._write_debounce_s:
                result["status"] = "blocked_debounce"
                result["reason"] = "Debounce guard active"
                result["elapsed_s"] = round(elapsed, 3)
                result["debounce_s"] = self._write_debounce_s

        if result["status"] == "pending" and helper_state is None:
            result["status"] = "blocked_missing_target_helper"
            result["reason"] = "Target helper entity is missing"

        helper_options: list[str] = []
        helper_current = ""
        if helper_state is not None:
            helper_current = str(helper_state.state or "").strip()
            options_attr = helper_state.attributes.get("options", [])
            if isinstance(options_attr, list):
                helper_options = [str(item).strip() for item in options_attr if isinstance(item, str) and str(item).strip()]

        if result["status"] == "pending" and helper_options and selected_target not in helper_options:
            result["status"] = "blocked_option_mismatch"
            result["reason"] = "Selected scheduler target is not present in helper options"
            result["helper_options_count"] = len(helper_options)

        if result["status"] == "pending" and helper_current == selected_target:
            result["status"] = "noop_already_selected"
            result["reason"] = "Target helper already matches scheduler-selected target"

        if result["status"] == "pending" and dry_run:
            result["status"] = "dry_run_ok"
            result["reason"] = "Scheduler apply guards passed (dry run); no helper write executed"

        if result["status"] == "pending":
            self._write_in_progress = True
            try:
                await self.hass.services.async_call(
                    "input_select",
                    "select_option",
                    {
                        "entity_id": LEGACY_ACTIVE_TARGET_HELPER,
                        "option": selected_target,
                    },
                    blocking=True,
                )
                result["status"] = "write_applied"
                result["reason"] = "Scheduler-selected target applied to helper successfully"
            except Exception as err:  # pragma: no cover - defensive runtime guard
                result["status"] = "write_error"
                result["reason"] = "Service call failed during scheduler apply"
                result["error"] = str(err)
            finally:
                self._write_in_progress = False

        if result["status"] in {"dry_run_ok", "noop_already_selected", "write_applied", "write_error"}:
            self._last_write_monotonic = monotonic()

        result["completed_at"] = datetime.now(UTC).isoformat()

        self._last_scheduler_decision = {
            "requested_at": requested_at,
            "completed_at": result["completed_at"],
            "correlation_id": corr,
            **decision,
        }
        self._last_scheduler_apply = result
        self._last_write_attempt = {
            "status": result.get("status", "unknown"),
            "timestamp": result.get("completed_at"),
            "authority_mode": self._write_authority_mode,
            "reason": result.get("reason", ""),
            "correlation_id": corr,
            "source": "scheduler_apply_choice",
            "active_target": selected_target,
        }

        self.async_set_updated_data(self._build_snapshot())
        return result

    async def async_build_target_options_scaffold(
        self,
        *,
        dry_run: bool,
        force: bool,
        include_none: bool,
        correlation_id: str | None,
    ) -> dict[str, Any]:
        """Build (and optionally apply) component-native target-options scaffold plan."""
        requested_at = datetime.now(UTC).isoformat()
        corr = (correlation_id or "").strip() or f"target-options-{uuid4().hex[:12]}"
        scaffolds = self._build_component_scaffolds()
        plan = scaffolds.get("target_options_plan", {}) if isinstance(scaffolds.get("target_options_plan", {}), dict) else {}
        helper_entity = str(plan.get("helper_entity", LEGACY_ACTIVE_TARGET_HELPER) or LEGACY_ACTIVE_TARGET_HELPER)
        helper_state = self.hass.states.get(helper_entity)

        candidates = plan.get("candidates", []) if isinstance(plan.get("candidates", []), list) else []
        candidates = [str(item).strip() for item in candidates if isinstance(item, str) and str(item).strip()]
        proposed_options = list(candidates)
        if include_none:
            proposed_options = ["none"] + proposed_options
        if len(proposed_options) == 0:
            proposed_options = ["none"]

        result: dict[str, Any] = {
            "status": "pending",
            "reason": "",
            "requested_at": requested_at,
            "completed_at": requested_at,
            "correlation_id": corr,
            "authority_mode": self._write_authority_mode,
            "helper_entity": helper_entity,
            "helper_exists": helper_state is not None,
            "dry_run": bool(dry_run),
            "force": bool(force),
            "include_none": bool(include_none),
            "planned_options": proposed_options,
            "default_option": str(plan.get("default_option", "none") or "none"),
            "applied_options": [],
            "candidate_count": len(candidates),
        }

        if helper_state is None:
            result["status"] = "blocked_missing_target_helper"
            result["reason"] = "Target helper entity is missing"
        elif self._write_authority_mode != WRITE_AUTH_COMPONENT and not dry_run:
            result["status"] = "blocked_authority"
            result["reason"] = "Write authority is legacy; target-options apply is intentionally blocked"
        elif self._write_in_progress and not force:
            result["status"] = "blocked_reentrancy"
            result["reason"] = "A prior write attempt is still in progress"
        elif not force and not dry_run and self._last_write_monotonic > 0:
            elapsed = monotonic() - self._last_write_monotonic
            if elapsed < self._write_debounce_s:
                result["status"] = "blocked_debounce"
                result["reason"] = "Debounce guard active"
                result["elapsed_s"] = round(elapsed, 3)
                result["debounce_s"] = self._write_debounce_s

        if result["status"] == "pending" and dry_run:
            result["status"] = "dry_run_ok"
            result["reason"] = "Target-options scaffold computed successfully (dry run)"
            helper_current = str(helper_state.state or "").strip() if helper_state is not None else ""
            current_ok = self._is_resolved_state(helper_current) and helper_current in proposed_options
            default_option = str(result.get("default_option", "none") or "none")
            result["would_select_default"] = (not current_ok) and default_option in proposed_options

        if result["status"] == "pending":
            self._write_in_progress = True
            try:
                helper_current = str(helper_state.state or "").strip() if helper_state is not None else ""
                current_ok = self._is_resolved_state(helper_current) and helper_current in proposed_options
                default_option = str(result.get("default_option", "none") or "none")
                await self.hass.services.async_call(
                    "input_select",
                    "set_options",
                    {
                        "entity_id": helper_entity,
                        "options": proposed_options,
                    },
                    blocking=True,
                )
                result["status"] = "options_applied"
                result["reason"] = "Target-options scaffold applied to helper successfully"
                result["applied_options"] = proposed_options
                if (not current_ok) and default_option in proposed_options:
                    await self.hass.services.async_call(
                        "input_select",
                        "select_option",
                        {
                            "entity_id": helper_entity,
                            "option": default_option,
                        },
                        blocking=True,
                    )
                    result["selected_default_option"] = default_option
            except Exception as err:  # pragma: no cover - defensive runtime guard
                result["status"] = "write_error"
                result["reason"] = "Service call failed during target-options scaffold apply"
                result["error"] = str(err)
            finally:
                self._write_in_progress = False

        if result["status"] in {"dry_run_ok", "options_applied", "write_error"}:
            self._last_write_monotonic = monotonic()

        result["completed_at"] = datetime.now(UTC).isoformat()
        self._last_target_options_attempt = result
        self._last_write_attempt = {
            "status": result.get("status", "unknown"),
            "timestamp": result.get("completed_at"),
            "authority_mode": self._write_authority_mode,
            "reason": result.get("reason", ""),
            "correlation_id": corr,
            "source": "build_target_options_scaffold",
            "active_target": "",
        }
        self.async_set_updated_data(self._build_snapshot())
        return result

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
        requested_at = datetime.now(UTC).isoformat()
        corr = (correlation_id or "").strip() or f"auto-select-{uuid4().hex[:12]}"

        scaffolds = self._build_component_scaffolds()
        target_options_plan = scaffolds.get("target_options_plan", {}) if isinstance(scaffolds.get("target_options_plan", {}), dict) else {}
        auto_select_plan = scaffolds.get("auto_select_plan", {}) if isinstance(scaffolds.get("auto_select_plan", {}), dict) else {}

        helper_entity = str(target_options_plan.get("helper_entity", LEGACY_ACTIVE_TARGET_HELPER) or LEGACY_ACTIVE_TARGET_HELPER)
        helper_state = self.hass.states.get(helper_entity)
        selected_target = str(auto_select_plan.get("selected_target", "") or "").strip()
        selection_reason = str(auto_select_plan.get("selection_reason", "no_candidate") or "no_candidate")

        helper_options: list[str] = []
        helper_current = ""
        if helper_state is not None:
            helper_current = str(helper_state.state or "").strip()
            options_attr = helper_state.attributes.get("options", [])
            if isinstance(options_attr, list):
                helper_options = [str(item).strip() for item in options_attr if isinstance(item, str) and str(item).strip()]

        helper_current_resolved = self._is_resolved_state(helper_current)
        helper_current_in_options = helper_current_resolved and helper_current in helper_options
        if selected_target == "" and helper_current_in_options:
            selected_target = helper_current
            selection_reason = "helper_current_fallback"

        planned_options = target_options_plan.get("proposed_options", []) if isinstance(target_options_plan.get("proposed_options", []), list) else []
        planned_options = [str(item).strip() for item in planned_options if isinstance(item, str) and str(item).strip()]
        if include_none and "none" not in planned_options:
            planned_options = ["none"] + planned_options

        result: dict[str, Any] = {
            "status": "pending",
            "reason": "",
            "requested_at": requested_at,
            "completed_at": requested_at,
            "correlation_id": corr,
            "authority_mode": self._write_authority_mode,
            "helper_entity": helper_entity,
            "helper_exists": helper_state is not None,
            "dry_run": bool(dry_run),
            "force": bool(force),
            "sync_options_if_missing": bool(sync_options_if_missing),
            "include_none": bool(include_none),
            "selected_target": selected_target,
            "selection_reason": selection_reason,
            "helper_current": helper_current,
            "helper_options_count": len(helper_options),
        }

        if selected_target == "":
            result["status"] = "blocked_no_candidate"
            result["reason"] = "Auto-select scaffold has no selected target candidate"
        elif helper_state is None:
            result["status"] = "blocked_missing_target_helper"
            result["reason"] = "Target helper entity is missing"
        elif self._write_authority_mode != WRITE_AUTH_COMPONENT and not dry_run:
            result["status"] = "blocked_authority"
            result["reason"] = "Write authority is legacy; auto-select apply is intentionally blocked"
        elif self._write_in_progress and not force:
            result["status"] = "blocked_reentrancy"
            result["reason"] = "A prior write attempt is still in progress"
        elif not force and not dry_run and self._last_write_monotonic > 0:
            elapsed = monotonic() - self._last_write_monotonic
            if elapsed < self._write_debounce_s:
                result["status"] = "blocked_debounce"
                result["reason"] = "Debounce guard active"
                result["elapsed_s"] = round(elapsed, 3)
                result["debounce_s"] = self._write_debounce_s

        if result["status"] == "pending" and selected_target not in helper_options:
            if dry_run and sync_options_if_missing and len(planned_options) > 0:
                result["options_sync_planned"] = True
                result["planned_options_count"] = len(planned_options)
            elif sync_options_if_missing and len(planned_options) > 0:
                try:
                    await self.hass.services.async_call(
                        "input_select",
                        "set_options",
                        {
                            "entity_id": helper_entity,
                            "options": planned_options,
                        },
                        blocking=True,
                    )
                    helper_options = planned_options
                    result["helper_options_count"] = len(helper_options)
                    result["options_synced"] = True
                except Exception as err:  # pragma: no cover - defensive runtime guard
                    result["status"] = "write_error"
                    result["reason"] = "Failed syncing helper options before auto-select apply"
                    result["error"] = str(err)
            else:
                result["status"] = "blocked_option_mismatch"
                result["reason"] = "Selected target is not present in helper options"

        if result["status"] == "pending" and helper_current == selected_target:
            result["status"] = "noop_already_selected"
            result["reason"] = "Helper already matches auto-select scaffold target"

        if result["status"] == "pending" and dry_run:
            result["status"] = "dry_run_ok"
            result["reason"] = "Auto-select scaffold guards passed (dry run)"

        if result["status"] == "pending":
            self._write_in_progress = True
            try:
                await self.hass.services.async_call(
                    "input_select",
                    "select_option",
                    {
                        "entity_id": helper_entity,
                        "option": selected_target,
                    },
                    blocking=True,
                )
                result["status"] = "write_applied"
                result["reason"] = "Auto-select scaffold applied selected target successfully"
            except Exception as err:  # pragma: no cover - defensive runtime guard
                result["status"] = "write_error"
                result["reason"] = "Service call failed during auto-select scaffold apply"
                result["error"] = str(err)
            finally:
                self._write_in_progress = False

        if result["status"] in {"dry_run_ok", "noop_already_selected", "write_applied", "write_error"}:
            self._last_write_monotonic = monotonic()

        result["completed_at"] = datetime.now(UTC).isoformat()
        self._last_auto_select_attempt = result
        self._last_write_attempt = {
            "status": result.get("status", "unknown"),
            "timestamp": result.get("completed_at"),
            "authority_mode": self._write_authority_mode,
            "reason": result.get("reason", ""),
            "correlation_id": corr,
            "source": "run_auto_select_scaffold",
            "active_target": selected_target,
        }
        self.async_set_updated_data(self._build_snapshot())
        return result

    async def async_track_last_valid_target(
        self,
        *,
        dry_run: bool,
        force: bool,
        correlation_id: str | None,
        source: str = "service_track_last_valid_target",
    ) -> dict[str, Any]:
        """Track helper-selected target into last-valid helper with guarded writes."""
        requested_at = datetime.now(UTC).isoformat()
        corr = (correlation_id or "").strip() or f"track-last-valid-{uuid4().hex[:12]}"

        helper_state = self.hass.states.get(LEGACY_ACTIVE_TARGET_HELPER)
        last_valid_state = self.hass.states.get(LEGACY_LAST_VALID_TARGET)
        helper_current = str(helper_state.state if helper_state is not None else "").strip()

        result: dict[str, Any] = {
            "status": "pending",
            "reason": "",
            "requested_at": requested_at,
            "completed_at": requested_at,
            "correlation_id": corr,
            "source": source,
            "authority_mode": self._write_authority_mode,
            "dry_run": bool(dry_run),
            "force": bool(force),
            "helper_entity": LEGACY_ACTIVE_TARGET_HELPER,
            "last_valid_entity": LEGACY_LAST_VALID_TARGET,
            "tracked_target": helper_current,
        }

        if helper_state is None:
            result["status"] = "blocked_missing_target_helper"
            result["reason"] = "Target helper entity is missing"
        elif last_valid_state is None:
            result["status"] = "blocked_missing_last_valid_helper"
            result["reason"] = "Last-valid target helper is missing"
        elif not self._is_resolved_state(helper_current):
            result["status"] = "blocked_unresolved_target"
            result["reason"] = "Current helper target is unresolved and cannot be tracked"
        elif self._write_authority_mode != WRITE_AUTH_COMPONENT and not dry_run:
            result["status"] = "blocked_authority"
            result["reason"] = "Write authority is legacy; last-valid tracking write is intentionally blocked"
        elif self._write_in_progress and not force:
            result["status"] = "blocked_reentrancy"
            result["reason"] = "A prior write attempt is still in progress"
        elif not force and not dry_run and self._last_write_monotonic > 0:
            elapsed = monotonic() - self._last_write_monotonic
            if elapsed < self._write_debounce_s:
                result["status"] = "blocked_debounce"
                result["reason"] = "Debounce guard active"
                result["elapsed_s"] = round(elapsed, 3)
                result["debounce_s"] = self._write_debounce_s

        if result["status"] == "pending":
            current_last_valid = str(last_valid_state.state if last_valid_state is not None else "").strip()
            if current_last_valid == helper_current:
                result["status"] = "noop_already_tracked"
                result["reason"] = "Last-valid helper already matches current active target"

        if result["status"] == "pending" and dry_run:
            result["status"] = "dry_run_ok"
            result["reason"] = "Last-valid tracking guards passed (dry run)"

        if result["status"] == "pending":
            self._write_in_progress = True
            try:
                await self.hass.services.async_call(
                    "input_text",
                    "set_value",
                    {
                        "entity_id": LEGACY_LAST_VALID_TARGET,
                        "value": helper_current,
                    },
                    blocking=True,
                )
                result["status"] = "write_applied"
                result["reason"] = "Last-valid target updated from current helper selection"
            except Exception as err:  # pragma: no cover - defensive runtime guard
                result["status"] = "write_error"
                result["reason"] = "Service call failed during last-valid tracking"
                result["error"] = str(err)
            finally:
                self._write_in_progress = False

        if result["status"] in {"dry_run_ok", "noop_already_tracked", "write_applied", "write_error"}:
            self._last_write_monotonic = monotonic()

        result["completed_at"] = datetime.now(UTC).isoformat()
        self._last_track_last_valid_attempt = result
        self._last_write_attempt = {
            "status": result.get("status", "unknown"),
            "timestamp": result.get("completed_at"),
            "authority_mode": self._write_authority_mode,
            "reason": result.get("reason", ""),
            "correlation_id": corr,
            "source": source,
            "active_target": helper_current,
        }
        self.async_set_updated_data(self._build_snapshot())
        return result

    async def async_restore_last_valid_target(
        self,
        *,
        dry_run: bool,
        force: bool,
        correlation_id: str | None,
    ) -> dict[str, Any]:
        """Restore helper selection from last-valid helper when current selection is unresolved."""
        requested_at = datetime.now(UTC).isoformat()
        corr = (correlation_id or "").strip() or f"restore-last-valid-{uuid4().hex[:12]}"

        helper_state = self.hass.states.get(LEGACY_ACTIVE_TARGET_HELPER)
        last_valid_state = self.hass.states.get(LEGACY_LAST_VALID_TARGET)

        helper_current = str(helper_state.state if helper_state is not None else "").strip()
        last_valid_target = str(last_valid_state.state if last_valid_state is not None else "").strip()
        helper_options: list[str] = []
        if helper_state is not None:
            options_attr = helper_state.attributes.get("options", [])
            if isinstance(options_attr, list):
                helper_options = [str(item).strip() for item in options_attr if isinstance(item, str) and str(item).strip()]

        current_resolved = self._is_resolved_state(helper_current)
        restore_candidate = last_valid_target if self._is_resolved_state(last_valid_target) and last_valid_target in helper_options else ""

        result: dict[str, Any] = {
            "status": "pending",
            "reason": "",
            "requested_at": requested_at,
            "completed_at": requested_at,
            "correlation_id": corr,
            "authority_mode": self._write_authority_mode,
            "dry_run": bool(dry_run),
            "force": bool(force),
            "helper_entity": LEGACY_ACTIVE_TARGET_HELPER,
            "last_valid_entity": LEGACY_LAST_VALID_TARGET,
            "helper_current": helper_current,
            "last_valid_target": last_valid_target,
            "restore_target": restore_candidate,
            "helper_options_count": len(helper_options),
        }

        if helper_state is None:
            result["status"] = "blocked_missing_target_helper"
            result["reason"] = "Target helper entity is missing"
        elif last_valid_state is None:
            result["status"] = "blocked_missing_last_valid_helper"
            result["reason"] = "Last-valid target helper is missing"
        elif current_resolved and not force:
            result["status"] = "noop_current_target_resolved"
            result["reason"] = "Current helper target is already resolved; restore is not required"
        elif restore_candidate == "":
            result["status"] = "blocked_no_last_valid_candidate"
            result["reason"] = "No restorable last-valid target is present in current helper options"
        elif self._write_authority_mode != WRITE_AUTH_COMPONENT and not dry_run:
            result["status"] = "blocked_authority"
            result["reason"] = "Write authority is legacy; restore-last-valid write is intentionally blocked"
        elif self._write_in_progress and not force:
            result["status"] = "blocked_reentrancy"
            result["reason"] = "A prior write attempt is still in progress"
        elif not force and not dry_run and self._last_write_monotonic > 0:
            elapsed = monotonic() - self._last_write_monotonic
            if elapsed < self._write_debounce_s:
                result["status"] = "blocked_debounce"
                result["reason"] = "Debounce guard active"
                result["elapsed_s"] = round(elapsed, 3)
                result["debounce_s"] = self._write_debounce_s

        if result["status"] == "pending" and helper_current == restore_candidate:
            result["status"] = "noop_already_selected"
            result["reason"] = "Helper already matches restorable last-valid target"

        if result["status"] == "pending" and dry_run:
            result["status"] = "dry_run_ok"
            result["reason"] = "Restore-last-valid guards passed (dry run)"

        if result["status"] == "pending":
            self._write_in_progress = True
            try:
                await self.hass.services.async_call(
                    "input_select",
                    "select_option",
                    {
                        "entity_id": LEGACY_ACTIVE_TARGET_HELPER,
                        "option": restore_candidate,
                    },
                    blocking=True,
                )
                result["status"] = "write_applied"
                result["reason"] = "Restored helper selection from last-valid target"
            except Exception as err:  # pragma: no cover - defensive runtime guard
                result["status"] = "write_error"
                result["reason"] = "Service call failed during restore-last-valid apply"
                result["error"] = str(err)
            finally:
                self._write_in_progress = False

        if result["status"] in {"dry_run_ok", "noop_current_target_resolved", "noop_already_selected", "write_applied", "write_error"}:
            self._last_write_monotonic = monotonic()

        result["completed_at"] = datetime.now(UTC).isoformat()
        self._last_restore_last_valid_attempt = result
        self._last_write_attempt = {
            "status": result.get("status", "unknown"),
            "timestamp": result.get("completed_at"),
            "authority_mode": self._write_authority_mode,
            "reason": result.get("reason", ""),
            "correlation_id": corr,
            "source": "restore_last_valid_target",
            "active_target": restore_candidate,
        }
        self.async_set_updated_data(self._build_snapshot())
        return result

    async def async_cycle_active_target(
        self,
        *,
        dry_run: bool,
        force: bool,
        include_none: bool,
        correlation_id: str | None,
    ) -> dict[str, Any]:
        """Cycle active-target helper options with optional none filtering and override activation."""
        requested_at = datetime.now(UTC).isoformat()
        corr = (correlation_id or "").strip() or f"cycle-target-{uuid4().hex[:12]}"

        helper_state = self.hass.states.get(LEGACY_ACTIVE_TARGET_HELPER)
        override_state = self.hass.states.get(LEGACY_OVERRIDE_ACTIVE)

        helper_current = str(helper_state.state if helper_state is not None else "").strip()
        helper_options: list[str] = []
        if helper_state is not None:
            options_attr = helper_state.attributes.get("options", [])
            if isinstance(options_attr, list):
                helper_options = [str(item).strip() for item in options_attr if isinstance(item, str) and str(item).strip()]

        cycle_options = list(helper_options)
        if not include_none:
            cycle_options = [item for item in cycle_options if self._normalize_state(item) != "none"]

        next_target = ""
        if len(cycle_options) > 0:
            if helper_current in cycle_options:
                current_index = cycle_options.index(helper_current)
                next_target = cycle_options[(current_index + 1) % len(cycle_options)]
            else:
                next_target = cycle_options[0]

        result: dict[str, Any] = {
            "status": "pending",
            "reason": "",
            "requested_at": requested_at,
            "completed_at": requested_at,
            "correlation_id": corr,
            "authority_mode": self._write_authority_mode,
            "dry_run": bool(dry_run),
            "force": bool(force),
            "include_none": bool(include_none),
            "helper_entity": LEGACY_ACTIVE_TARGET_HELPER,
            "override_entity": LEGACY_OVERRIDE_ACTIVE,
            "helper_current": helper_current,
            "helper_options_count": len(helper_options),
            "cycle_options_count": len(cycle_options),
            "next_target": next_target,
        }

        if helper_state is None:
            result["status"] = "blocked_missing_target_helper"
            result["reason"] = "Target helper entity is missing"
        elif len(cycle_options) == 0:
            result["status"] = "blocked_no_cycle_options"
            result["reason"] = "No cycle candidates are available in target helper options"
        elif next_target == "":
            result["status"] = "blocked_no_next_target"
            result["reason"] = "Unable to derive next cycle target"
        elif self._write_authority_mode != WRITE_AUTH_COMPONENT and not dry_run:
            result["status"] = "blocked_authority"
            result["reason"] = "Write authority is legacy; cycle-target write is intentionally blocked"
        elif self._write_in_progress and not force:
            result["status"] = "blocked_reentrancy"
            result["reason"] = "A prior write attempt is still in progress"
        elif not force and not dry_run and self._last_write_monotonic > 0:
            elapsed = monotonic() - self._last_write_monotonic
            if elapsed < self._write_debounce_s:
                result["status"] = "blocked_debounce"
                result["reason"] = "Debounce guard active"
                result["elapsed_s"] = round(elapsed, 3)
                result["debounce_s"] = self._write_debounce_s

        if result["status"] == "pending" and len(cycle_options) == 1 and helper_current == next_target:
            result["status"] = "noop_single_option"
            result["reason"] = "Only one cycle option is available; active target remains unchanged"

        if result["status"] == "pending" and dry_run:
            result["status"] = "dry_run_ok"
            result["reason"] = "Cycle-target guards passed (dry run)"
            result["would_enable_override"] = override_state is not None and self._normalize_state(override_state.state) != "on"

        if result["status"] == "pending":
            self._write_in_progress = True
            try:
                if override_state is not None and self._normalize_state(override_state.state) != "on":
                    await self.hass.services.async_call(
                        "input_boolean",
                        "turn_on",
                        {
                            "entity_id": LEGACY_OVERRIDE_ACTIVE,
                        },
                        blocking=True,
                    )
                await self.hass.services.async_call(
                    "input_select",
                    "select_option",
                    {
                        "entity_id": LEGACY_ACTIVE_TARGET_HELPER,
                        "option": next_target,
                    },
                    blocking=True,
                )
                result["status"] = "write_applied"
                result["reason"] = "Cycle-target selection applied successfully"

                if self._is_resolved_state(next_target):
                    await self.async_track_last_valid_target(
                        dry_run=False,
                        force=True,
                        correlation_id=f"{corr}-track",
                        source="cycle_active_target",
                    )
            except Exception as err:  # pragma: no cover - defensive runtime guard
                result["status"] = "write_error"
                result["reason"] = "Service call failed during cycle-target apply"
                result["error"] = str(err)
            finally:
                self._write_in_progress = False

        if result["status"] in {"dry_run_ok", "noop_single_option", "write_applied", "write_error"}:
            self._last_write_monotonic = monotonic()

        result["completed_at"] = datetime.now(UTC).isoformat()
        self._last_cycle_target_attempt = result
        self._last_write_attempt = {
            "status": result.get("status", "unknown"),
            "timestamp": result.get("completed_at"),
            "authority_mode": self._write_authority_mode,
            "reason": result.get("reason", ""),
            "correlation_id": corr,
            "source": "cycle_active_target",
            "active_target": next_target,
        }
        self.async_set_updated_data(self._build_snapshot())
        return result

    async def async_run_metadata_resolver_scaffold(
        self,
        *,
        dry_run: bool,
        force: bool,
        correlation_id: str | None,
    ) -> dict[str, Any]:
        """Run component-native metadata resolver scaffold with guarded helper apply semantics."""
        requested_at = datetime.now(UTC).isoformat()
        corr = (correlation_id or "").strip() or f"meta-resolver-{uuid4().hex[:12]}"

        scaffolds = self._build_component_scaffolds()
        plan = (
            scaffolds.get("metadata_resolver_plan", {})
            if isinstance(scaffolds.get("metadata_resolver_plan", {}), dict)
            else {}
        )

        selected_meta_entity = str(plan.get("selected_meta_entity", "") or "").strip()
        selection_reason = str(plan.get("selection_reason", "no_candidate") or "no_candidate")

        override_active_entity = str(plan.get("override_active_entity", LEGACY_META_OVERRIDE_ACTIVE) or LEGACY_META_OVERRIDE_ACTIVE)
        override_entity_helper = str(plan.get("override_entity_helper", LEGACY_META_OVERRIDE_ENTITY) or LEGACY_META_OVERRIDE_ENTITY)

        override_active_state = self.hass.states.get(override_active_entity)
        override_entity_state = self.hass.states.get(override_entity_helper)
        override_active_exists = override_active_state is not None
        override_entity_exists = override_entity_state is not None

        current_override_active = self._normalize_state(override_active_state.state if override_active_state is not None else "") == "on"
        current_override_entity = str(override_entity_state.state if override_entity_state is not None else "").strip()

        result: dict[str, Any] = {
            "status": "pending",
            "reason": "",
            "requested_at": requested_at,
            "completed_at": requested_at,
            "correlation_id": corr,
            "authority_mode": self._write_authority_mode,
            "dry_run": bool(dry_run),
            "force": bool(force),
            "selected_meta_entity": selected_meta_entity,
            "selection_reason": selection_reason,
            "override_active_entity": override_active_entity,
            "override_entity_helper": override_entity_helper,
            "override_active_exists": override_active_exists,
            "override_entity_exists": override_entity_exists,
            "current_override_active": current_override_active,
            "current_override_entity": current_override_entity,
            "meta_resolver_best_candidate": plan.get("best_candidate", ""),
            "meta_resolver_best_score": plan.get("best_score", 0),
            "detected_candidate": plan.get("detected_candidate", ""),
        }

        if selected_meta_entity == "":
            result["status"] = "blocked_no_candidate"
            result["reason"] = "Metadata resolver scaffold has no selected metadata candidate"
        elif self.hass.states.get(selected_meta_entity) is None:
            result["status"] = "blocked_missing_selected_entity"
            result["reason"] = "Selected metadata entity is not currently present in HA state registry"
        elif not override_active_exists or not override_entity_exists:
            result["status"] = "blocked_missing_override_helpers"
            result["reason"] = "Metadata override helpers are missing"
        elif self._write_authority_mode != WRITE_AUTH_COMPONENT:
            result["status"] = "blocked_authority"
            result["reason"] = "Write authority is legacy; metadata-resolver scaffold apply is intentionally blocked"
        elif self._write_in_progress and not force:
            result["status"] = "blocked_reentrancy"
            result["reason"] = "A prior write attempt is still in progress"
        elif not force and not dry_run and self._last_write_monotonic > 0:
            elapsed = monotonic() - self._last_write_monotonic
            if elapsed < self._write_debounce_s:
                result["status"] = "blocked_debounce"
                result["reason"] = "Debounce guard active"
                result["elapsed_s"] = round(elapsed, 3)
                result["debounce_s"] = self._write_debounce_s

        if result["status"] == "pending" and current_override_active and current_override_entity == selected_meta_entity:
            result["status"] = "noop_already_selected"
            result["reason"] = "Metadata override is already active for the selected metadata entity"

        if result["status"] == "pending" and dry_run:
            result["status"] = "dry_run_ok"
            result["reason"] = "Metadata-resolver scaffold guards passed (dry run)"

        if result["status"] == "pending":
            self._write_in_progress = True
            try:
                await self.hass.services.async_call(
                    "input_text",
                    "set_value",
                    {
                        "entity_id": override_entity_helper,
                        "value": selected_meta_entity,
                    },
                    blocking=True,
                )
                await self.hass.services.async_call(
                    "input_boolean",
                    "turn_on",
                    {
                        "entity_id": override_active_entity,
                    },
                    blocking=True,
                )
                result["status"] = "write_applied"
                result["reason"] = "Metadata-resolver scaffold applied override helper state successfully"
            except Exception as err:  # pragma: no cover - defensive runtime guard
                result["status"] = "write_error"
                result["reason"] = "Service call failed during metadata-resolver scaffold apply"
                result["error"] = str(err)
            finally:
                self._write_in_progress = False

        if result["status"] in {"dry_run_ok", "noop_already_selected", "write_applied", "write_error"}:
            self._last_write_monotonic = monotonic()

        result["completed_at"] = datetime.now(UTC).isoformat()
        self._last_metadata_resolver_attempt = result
        self._last_write_attempt = {
            "status": result.get("status", "unknown"),
            "timestamp": result.get("completed_at"),
            "authority_mode": self._write_authority_mode,
            "reason": result.get("reason", ""),
            "correlation_id": corr,
            "source": "run_metadata_resolver_scaffold",
            "active_target": selected_meta_entity,
        }
        self.async_set_updated_data(self._build_snapshot())
        return result

    async def async_run_metadata_trial_bridge_scaffold(
        self,
        *,
        window_id: str,
        reason: str,
        resolver_dry_run: bool,
        trial_dry_run: bool,
        force: bool,
        expected_target: str | None,
        expected_route: str | None,
        expected_meta_entity: str | None,
        correlation_id: str | None,
    ) -> dict[str, Any]:
        """Run resolver-authority gated metadata scaffold plus legacy metadata trial bridge sequence."""
        requested_at = datetime.now(UTC).isoformat()
        corr = (correlation_id or "").strip() or f"meta-bridge-{uuid4().hex[:12]}"
        window = (window_id or "").strip() or f"meta-bridge-{uuid4().hex[:8]}"
        operator_reason = (reason or "").strip() or "Metadata trial bridge scaffold"

        authority_before = self._write_authority_mode
        result: dict[str, Any] = {
            "status": "pending",
            "reason": "",
            "requested_at": requested_at,
            "completed_at": requested_at,
            "correlation_id": corr,
            "window_id": window,
            "authority_before": authority_before,
            "authority_after": authority_before,
            "resolver_dry_run": bool(resolver_dry_run),
            "trial_dry_run": bool(trial_dry_run),
            "force": bool(force),
            "expected_target": (expected_target or "").strip(),
            "expected_route": (expected_route or "").strip(),
            "expected_meta_entity": (expected_meta_entity or "").strip(),
            "stages": {},
        }

        try:
            if self._write_authority_mode != WRITE_AUTH_COMPONENT:
                await self.async_set_write_authority(
                    mode=WRITE_AUTH_COMPONENT,
                    reason=f"{operator_reason} (resolver-stage)",
                )
                result["stages"]["set_component_authority"] = "applied"
            else:
                result["stages"]["set_component_authority"] = "noop_already_component"

            auto_select_result = await self.async_run_auto_select_scaffold(
                dry_run=False,
                force=True,
                sync_options_if_missing=True,
                include_none=True,
                correlation_id=f"{corr}-auto-select",
            )
            result["stages"]["auto_select_scaffold"] = {
                "status": auto_select_result.get("status", "unknown"),
                "reason": auto_select_result.get("reason", ""),
                "selected_target": auto_select_result.get("selected_target", ""),
                "options_synced": bool(auto_select_result.get("options_synced", False)),
            }

            auto_status = str(auto_select_result.get("status", "") or "")
            if auto_status.startswith("blocked_") or auto_status == "write_error":
                result["status"] = "blocked_target_recovery_stage"
                result["reason"] = "Automatic control-capable target recovery did not pass guards"
                return result

            resolver_result = await self.async_run_metadata_resolver_scaffold(
                dry_run=resolver_dry_run,
                force=True,
                correlation_id=f"{corr}-resolver",
            )
            result["stages"]["resolver_scaffold"] = {
                "status": resolver_result.get("status", "unknown"),
                "reason": resolver_result.get("reason", ""),
                "selected_meta_entity": resolver_result.get("selected_meta_entity", ""),
            }

            resolver_status = str(resolver_result.get("status", "") or "")
            if resolver_status.startswith("blocked_") or resolver_status == "write_error":
                result["status"] = "blocked_resolver_stage"
                result["reason"] = "Resolver scaffold stage did not pass guards"
            else:
                selected_meta = (expected_meta_entity or "").strip()
                if selected_meta == "":
                    selected_meta = str(resolver_result.get("selected_meta_entity", "") or "").strip()

                if self._write_authority_mode != WRITE_AUTH_LEGACY:
                    await self.async_set_write_authority(
                        mode=WRITE_AUTH_LEGACY,
                        reason=f"{operator_reason} (trial-stage)",
                    )
                    result["stages"]["set_legacy_authority"] = "applied"
                else:
                    result["stages"]["set_legacy_authority"] = "noop_already_legacy"

                trial_result = await self.async_metadata_write_trial(
                    mode=WRITE_AUTH_LEGACY,
                    window_id=window,
                    reason=f"{operator_reason} (bridge)",
                    dry_run=trial_dry_run,
                    expected_target=(expected_target or "").strip() or None,
                    expected_route=(expected_route or "").strip() or None,
                    expected_meta_entity=selected_meta or None,
                    correlation_id=f"{corr}-trial",
                )
                result["stages"]["metadata_trial"] = {
                    "status": trial_result.get("status", "unknown"),
                    "reason": trial_result.get("reason", ""),
                    "expected_meta_entity": trial_result.get("expected_meta_entity", ""),
                    "observed_active_meta_entity": trial_result.get("observed_active_meta_entity", ""),
                }

                trial_status = str(trial_result.get("status", "") or "")
                if trial_status.startswith("blocked_") or trial_status == "write_error":
                    result["status"] = "blocked_trial_stage"
                    result["reason"] = "Metadata trial stage did not pass guards"
                else:
                    result["status"] = "bridge_completed"
                    result["reason"] = "Resolver-authority gating and metadata trial bridge completed"
        finally:
            if self._write_authority_mode != authority_before:
                self._write_authority_mode = authority_before
                result.setdefault("stages", {})["restore_authority"] = "restored"
            result["authority_after"] = self._write_authority_mode
            result["completed_at"] = datetime.now(UTC).isoformat()
            self._last_metadata_bridge_attempt = result
            self._last_write_attempt = {
                "status": result.get("status", "unknown"),
                "timestamp": result.get("completed_at"),
                "authority_mode": self._write_authority_mode,
                "reason": result.get("reason", ""),
                "correlation_id": corr,
                "source": "run_metadata_trial_bridge_scaffold",
                "active_target": str(result.get("expected_meta_entity", "") or ""),
            }
            self.async_set_updated_data(self._build_snapshot())

        return result

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
        expected_meta_entity: str | None = None,
        correlation_id: str | None = None,
    ) -> dict[str, Any]:
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
        expected_meta_entity_norm = (expected_meta_entity or "").strip()

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
        active_meta_entity = str(
            self.hass.states.get(LEGACY_ACTIVE_META_ENTITY).state
            if self.hass.states.get(LEGACY_ACTIVE_META_ENTITY) is not None
            else ""
        ).strip()
        scaffolds = self._build_component_scaffolds()
        resolver_plan = (
            scaffolds.get("metadata_resolver_plan", {})
            if isinstance(scaffolds.get("metadata_resolver_plan", {}), dict)
            else {}
        )
        scaffold_meta_entity = str(resolver_plan.get("selected_meta_entity", "") or "").strip()
        override_active_state = self.hass.states.get(LEGACY_META_OVERRIDE_ACTIVE)
        override_active = self._normalize_state(override_active_state.state if override_active_state is not None else "") == "on"
        override_entity_state = self.hass.states.get(LEGACY_META_OVERRIDE_ENTITY)
        override_entity = str(override_entity_state.state if override_entity_state is not None else "").strip()

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
            "expected_meta_entity": expected_meta_entity_norm,
            "active_target": active_target,
            "route_decision": route_decision,
            "observed_active_meta_entity": active_meta_entity,
            "observed_scaffold_meta_entity": scaffold_meta_entity,
            "observed_override_active": override_active,
            "observed_override_entity": override_entity,
            "contract_valid": contract_valid,
            "metadata_ready": metadata_ready,
            "blocking_reasons": [],
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
        elif expected_meta_entity_norm:
            meta_matches = expected_meta_entity_norm in {
                active_meta_entity,
                scaffold_meta_entity,
                (override_entity if override_active else ""),
            }
            if not meta_matches:
                result.update(
                    {
                        "status": "blocked_expected_meta_mismatch",
                        "reason": "Observed metadata resolver surfaces do not match expected_meta_entity",
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

        status = str(result.get("status", "") or "")
        blocking_reasons: list[str] = []
        if status.startswith("blocked_"):
            blocking_reasons.append(status)
        result["blocking_reasons"] = blocking_reasons

        missing_audit_fields = self._metadata_trial_audit_missing_fields(result)
        audit_payload_complete = len(missing_audit_fields) == 0
        result["audit_payload_complete"] = audit_payload_complete
        result["missing_audit_fields"] = missing_audit_fields
        result["audit_payload_state"] = "COMPLETE" if audit_payload_complete else "PARTIAL"

        if status.startswith("blocked_"):
            trial_gate_verdict = "FAIL"
        elif status in {"dry_run_ok", "noop_applied"}:
            trial_gate_verdict = "PASS"
        else:
            trial_gate_verdict = "WARN"
        result["trial_gate_verdict"] = trial_gate_verdict
        result["eligible_for_closeout"] = (
            trial_gate_verdict == "PASS"
            and audit_payload_complete
            and self._write_authority_mode == WRITE_AUTH_LEGACY
        )
        self._last_metadata_trial_attempt = result
        self.async_set_updated_data(self._build_snapshot())
        return result

    def _auto_select_loop_preflight(self) -> tuple[bool, str]:
        if self._write_authority_mode != WRITE_AUTH_COMPONENT:
            return False, "authority_not_component"

        players_state = self.hass.states.get(LEGACY_MA_PLAYERS)
        players_count = 0
        if players_state is not None and self._is_resolved_state(players_state.state):
            try:
                players_count = int(float(str(players_state.state).strip()))
            except (TypeError, ValueError):
                players_count = 0
        if players_count <= 0:
            return False, "players_not_ready"

        override_state = self.hass.states.get(LEGACY_OVERRIDE_ACTIVE)
        override_on = self._normalize_state(override_state.state if override_state is not None else "") == "on"
        if override_on:
            return False, "override_active"

        return True, "ready"

    async def async_run_component_auto_select_loop(self, *, source: str, force: bool = False) -> None:
        """Run component-side auto-select loop parity behavior under guarded semantics."""
        ok, _reason = self._auto_select_loop_preflight()
        if not ok:
            return

        await self.async_run_auto_select_scaffold(
            dry_run=False,
            force=force,
            sync_options_if_missing=True,
            include_none=True,
            correlation_id=f"component-auto-loop-{source}-{uuid4().hex[:8]}",
        )

    async def async_run_component_players_change_refresh(self, *, source: str) -> None:
        """Mirror legacy players-change sequencing: refresh options, then auto-select."""
        if self._write_authority_mode != WRITE_AUTH_COMPONENT:
            return

        corr_suffix = uuid4().hex[:8]
        await self.async_build_target_options_scaffold(
            dry_run=False,
            force=False,
            include_none=True,
            correlation_id=f"players-change-options-{source}-{corr_suffix}",
        )
        await self.async_run_component_auto_select_loop(
            source=f"{source}-auto-select",
            force=False,
        )

    async def async_apply_ambiguity_lock(self, *, source: str) -> None:
        """Mirror legacy lock-on-ambiguous-select behavior for component authority windows."""
        if self._write_authority_mode != WRITE_AUTH_COMPONENT:
            return

        ambiguous_state = self.hass.states.get(LEGACY_CONTROL_AMBIGUOUS)
        ambiguous_on = self._normalize_state(ambiguous_state.state if ambiguous_state is not None else "") == "on"
        if not ambiguous_on:
            return

        helper_state = self.hass.states.get(LEGACY_ACTIVE_TARGET_HELPER)
        current_target = str(helper_state.state if helper_state is not None else "").strip()
        if not self._is_resolved_state(current_target):
            return
        if self.hass.states.get(current_target) is None:
            return

        override_state = self.hass.states.get(LEGACY_OVERRIDE_ACTIVE)
        if override_state is None:
            return
        if self._normalize_state(override_state.state) == "on":
            return

        await self.hass.services.async_call(
            "input_boolean",
            "turn_on",
            {"entity_id": LEGACY_OVERRIDE_ACTIVE},
            blocking=True,
        )
        self._last_write_attempt = {
            "status": "write_applied",
            "timestamp": datetime.now(UTC).isoformat(),
            "authority_mode": self._write_authority_mode,
            "reason": "Applied ambiguity lock parity behavior",
            "correlation_id": f"ambiguity-lock-{uuid4().hex[:12]}",
            "source": source,
            "active_target": current_target,
        }
        self.async_set_updated_data(self._build_snapshot())

    async def async_apply_stale_unlock(self, *, source: str) -> None:
        """Mirror legacy stale-meta unlock behavior with bounded auto-select follow-up."""
        if self._write_authority_mode != WRITE_AUTH_COMPONENT:
            return

        meta_stale_state = self.hass.states.get(LEGACY_META_STALE)
        if self._normalize_state(meta_stale_state.state if meta_stale_state is not None else "") != "on":
            return

        override_state = self.hass.states.get(LEGACY_OVERRIDE_ACTIVE)
        if self._normalize_state(override_state.state if override_state is not None else "") != "on":
            return

        await self.hass.services.async_call(
            "input_boolean",
            "turn_off",
            {"entity_id": LEGACY_OVERRIDE_ACTIVE},
            blocking=True,
        )
        await self.async_run_component_auto_select_loop(source=f"{source}-auto-select", force=True)

    @callback
    def _handle_meta_stale_unlock_timer(self, _now) -> None:
        self._meta_stale_unlock_unsub = None
        self.hass.async_create_task(self.async_apply_stale_unlock(source="meta_stale_hold"))

    async def _async_dismiss_no_control_feedback_notification(self) -> None:
        try:
            await self.hass.services.async_call(
                "persistent_notification",
                "dismiss",
                {"notification_id": self._no_control_feedback_notification_id},
                blocking=True,
            )
        except Exception:  # pragma: no cover - defensive runtime guard
            _LOGGER.exception("Failed dismissing no-control-capable-hosts feedback notification")

    @callback
    def _handle_no_control_feedback_hold_timer(self, _now) -> None:
        self._no_control_feedback_hold_unsub = None
        self.hass.async_create_task(self._async_run_no_control_feedback_self_heal())

    async def _async_run_no_control_feedback_self_heal(self) -> None:
        if self._write_authority_mode != WRITE_AUTH_COMPONENT:
            return

        no_host_state = self.hass.states.get(LEGACY_NO_CONTROL_CAPABLE_HOSTS)
        if self._normalize_state(no_host_state.state if no_host_state is not None else "") != "on":
            return

        corr_suffix = uuid4().hex[:8]
        await self.async_build_target_options_scaffold(
            dry_run=False,
            force=True,
            include_none=True,
            correlation_id=f"no-host-feedback-options-{corr_suffix}",
        )
        await self.async_run_auto_select_scaffold(
            dry_run=False,
            force=True,
            sync_options_if_missing=True,
            include_none=True,
            correlation_id=f"no-host-feedback-auto-select-{corr_suffix}",
        )

        if self._no_control_feedback_post_heal_unsub is not None:
            self._no_control_feedback_post_heal_unsub()
        self._no_control_feedback_post_heal_unsub = async_call_later(
            self.hass,
            10.0,
            self._handle_no_control_feedback_post_heal_timer,
        )

    @callback
    def _handle_no_control_feedback_post_heal_timer(self, _now) -> None:
        self._no_control_feedback_post_heal_unsub = None
        self.hass.async_create_task(self._async_finalize_no_control_feedback_notification())

    async def _async_finalize_no_control_feedback_notification(self) -> None:
        if self._write_authority_mode != WRITE_AUTH_COMPONENT:
            return

        no_host_state = self.hass.states.get(LEGACY_NO_CONTROL_CAPABLE_HOSTS)
        if self._normalize_state(no_host_state.state if no_host_state is not None else "") != "on":
            return

        active_target_state = self.hass.states.get(LEGACY_ACTIVE_TARGET_HELPER)
        active_target = str(active_target_state.state if active_target_state is not None else "")

        control_path_state = self.hass.states.get(LEGACY_SURFACES["active_control_path"])
        control_path = str(control_path_state.state if control_path_state is not None else "")

        control_capable_state = self.hass.states.get(LEGACY_SURFACES["active_control_capable"])
        control_capable = str(control_capable_state.state if control_capable_state is not None else "")

        control_hosts_state = self.hass.states.get(LEGACY_SURFACES["control_hosts"])
        control_hosts = str(control_hosts_state.state if control_hosts_state is not None else "")
        if not self._is_resolved_state(control_hosts):
            control_hosts = "none"

        reason = str(no_host_state.attributes.get("reason", "unknown") if no_host_state is not None else "unknown")
        if not self._is_resolved_state(reason):
            reason = "unknown"

        message = (
            f"Active target: {active_target or 'unknown'}\\n"
            f"Control path: {control_path or 'unknown'}\\n"
            f"Control capable: {control_capable or 'unknown'}\\n"
            f"Control hosts: {control_hosts}\\n"
            f"Reason: {reason}\\n"
            "Suggested action: auto-refresh already attempted; if this persists, confirm active "
            "target eligibility and rerun MA target/options refresh."
        )

        try:
            await self.hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "notification_id": self._no_control_feedback_notification_id,
                    "title": "Spectra L/S: No control-capable hosts",
                    "message": message,
                },
                blocking=True,
            )
        except Exception:  # pragma: no cover - defensive runtime guard
            _LOGGER.exception("Failed creating no-control-capable-hosts feedback notification")

    @callback
    def _handle_global_state_change(self, event) -> None:
        """Mirror legacy event-based auto-select trigger for watched target entities."""
        try:
            if self._write_authority_mode != WRITE_AUTH_COMPONENT:
                return
            event_data = event.data if event is not None else {}
            entity_id = str(event_data.get("entity_id", "") or "")
            if entity_id == "":
                return

            helper_state = self.hass.states.get(LEGACY_ACTIVE_TARGET_HELPER)
            if helper_state is None:
                return
            options_attr = helper_state.attributes.get("options", [])
            helper_options = options_attr if isinstance(options_attr, list) else []
            watched_targets = {
                str(item).strip()
                for item in helper_options
                if isinstance(item, str) and str(item).strip()
            }
            if entity_id in watched_targets:
                self.hass.async_create_task(
                    self.async_run_component_auto_select_loop(
                        source=f"global-state:{entity_id}",
                        force=False,
                    )
                )
        except Exception:  # pragma: no cover - defensive callback hardening
            _LOGGER.exception("Failed global state-change handling for component auto-select parity")

    @callback
    def _handle_state_change(self, event) -> None:
        try:
            entity_id = str(event.data.get("entity_id", "") or "") if event is not None else ""

            if entity_id == LEGACY_META_STALE:
                new_state = event.data.get("new_state") if event is not None else None
                new_state_value = self._normalize_state(new_state.state if new_state is not None else "")
                if new_state_value == "on":
                    if self._meta_stale_unlock_unsub is not None:
                        self._meta_stale_unlock_unsub()
                    self._meta_stale_unlock_unsub = async_call_later(
                        self.hass,
                        5.0,
                        self._handle_meta_stale_unlock_timer,
                    )
                elif self._meta_stale_unlock_unsub is not None:
                    self._meta_stale_unlock_unsub()
                    self._meta_stale_unlock_unsub = None

            if entity_id == LEGACY_NO_CONTROL_CAPABLE_HOSTS:
                new_state = event.data.get("new_state") if event is not None else None
                new_state_value = self._normalize_state(new_state.state if new_state is not None else "")

                if new_state_value == "on" and self._write_authority_mode == WRITE_AUTH_COMPONENT:
                    if self._no_control_feedback_hold_unsub is not None:
                        self._no_control_feedback_hold_unsub()
                    if self._no_control_feedback_post_heal_unsub is not None:
                        self._no_control_feedback_post_heal_unsub()
                        self._no_control_feedback_post_heal_unsub = None
                    self._no_control_feedback_hold_unsub = async_call_later(
                        self.hass,
                        30.0,
                        self._handle_no_control_feedback_hold_timer,
                    )
                else:
                    if self._no_control_feedback_hold_unsub is not None:
                        self._no_control_feedback_hold_unsub()
                        self._no_control_feedback_hold_unsub = None
                    if self._no_control_feedback_post_heal_unsub is not None:
                        self._no_control_feedback_post_heal_unsub()
                        self._no_control_feedback_post_heal_unsub = None
                    self.hass.async_create_task(self._async_dismiss_no_control_feedback_notification())

            if entity_id == LEGACY_ACTIVE_TARGET_HELPER and self._write_authority_mode == WRITE_AUTH_COMPONENT:
                self.hass.async_create_task(
                    self.async_track_last_valid_target(
                        dry_run=False,
                        force=False,
                        correlation_id=f"state-change-track-{uuid4().hex[:12]}",
                        source="state_change_listener",
                    )
                )
                self.hass.async_create_task(
                    self.async_apply_ambiguity_lock(source="state_change_ambiguity_lock")
                )

            if entity_id in {LEGACY_MA_PLAYERS, LEGACY_META_DETECTED_ENTITY, LEGACY_NOW_PLAYING_ENTITY}:
                self.hass.async_create_task(
                    self.async_run_component_players_change_refresh(
                        source=f"state-change:{entity_id}",
                    )
                )
            elif entity_id == LEGACY_ACTIVE_TARGET_HELPER:
                self.hass.async_create_task(
                    self.async_run_component_auto_select_loop(
                        source=f"state-change:{entity_id}",
                        force=False,
                    )
                )

            now_mono = monotonic()
            elapsed = now_mono - self._last_snapshot_refresh_monotonic
            if self._last_snapshot_refresh_monotonic == 0.0 or elapsed >= self._snapshot_refresh_min_interval_s:
                self._refresh_snapshot(force=True)
                if self._deferred_snapshot_refresh_unsub is not None:
                    self._deferred_snapshot_refresh_unsub()
                    self._deferred_snapshot_refresh_unsub = None
                return

            if self._deferred_snapshot_refresh_unsub is None:
                delay_s = max(self._snapshot_refresh_min_interval_s - elapsed, 0.05)
                self._deferred_snapshot_refresh_unsub = async_call_later(
                    self.hass,
                    delay_s,
                    self._handle_deferred_snapshot_refresh,
                )
        except Exception:  # pragma: no cover - defensive callback hardening
            _LOGGER.exception("Failed to refresh Spectra LS snapshot on state-change event")
