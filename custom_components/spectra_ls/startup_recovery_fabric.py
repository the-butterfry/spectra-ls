# Description: Startup-recovery fabric workflow for Spectra LS metadata boot-gate orchestration extracted from meta-fabric.
# Version: 2026.05.03.2
# Last updated: 2026-05-03
# PARITY DIRECTIVE (until full cutover): behavior/contract edits here require same-slice two-track parity review
# and version-metadata review in runtime (`packages/` + `esphome/`) and component (`custom_components/spectra_ls/`) tracks.

from __future__ import annotations

from datetime import UTC, datetime
import logging
from typing import Any
from uuid import uuid4

from homeassistant.helpers.event import async_call_later

from .const import (
    LEGACY_ACTIVE_TARGET_HELPER,
    LEGACY_CONTROL_TARGETS,
    LEGACY_MA_PLAYERS,
    WRITE_AUTH_COMPONENT,
    WRITE_AUTH_LEGACY,
)
from .write_path_fabric import WritePathFabric

_LOGGER = logging.getLogger(__name__)


class StartupRecoveryFabricWorkflow:
    """Owns startup recovery orchestration extracted from meta-fabric."""

    def __init__(self, coordinator: Any) -> None:
        self._coordinator = coordinator

    async def async_schedule_startup_recovery(self) -> None:
        """Schedule bounded post-startup recovery for target/options and bridge alignment."""
        c = self._coordinator
        c._startup_recovery_attempt = 0
        c._startup_recovery_wait_cycles = 0
        if c._startup_recovery_unsub is not None:
            c._startup_recovery_unsub()
            c._startup_recovery_unsub = None
        c._startup_recovery_unsub = async_call_later(
            c.hass,
            c._startup_recovery_initial_delay_s,
            c._handle_startup_recovery_timer,
        )

    def handle_startup_recovery_timer(self, _now) -> None:
        """Kick off one startup recovery attempt from timer callback."""
        c = self._coordinator
        c._startup_recovery_unsub = None
        if c._startup_recovery_task is not None and not c._startup_recovery_task.done():
            return
        c._startup_recovery_task = c.hass.async_create_task(c._async_run_startup_recovery_attempt())

    async def async_run_startup_recovery_attempt(self) -> None:
        """Run one bounded startup recovery attempt and schedule retry if needed."""
        c = self._coordinator
        boot_ready, boot_reasons = self.is_startup_recovery_boot_ready()
        if not boot_ready:
            c._startup_recovery_wait_cycles += 1
            wait_reason = self.startup_wait_reason_prefix(boot_reasons)
            reason_suffix = self.format_startup_boot_wait_reasons(boot_reasons)

            c.metadata_stack.set_last_metadata_bridge_attempt({
                "status": "waiting_for_ma_boot",
                "requested_at": datetime.now(UTC).isoformat(),
                "completed_at": datetime.now(UTC).isoformat(),
                "reason": f"{wait_reason}: {reason_suffix}",
                "resolver_status": "never_attempted",
                "trial_status": "never_attempted",
            })
            c.async_set_updated_data(c.build_snapshot())

            if c._startup_recovery_wait_cycles <= c._startup_recovery_max_wait_cycles:
                _LOGGER.info(
                    "Startup auto-recovery is waiting for Music Assistant boot readiness (%s/%s): %s",
                    c._startup_recovery_wait_cycles,
                    c._startup_recovery_max_wait_cycles,
                    reason_suffix,
                )
                c._startup_recovery_unsub = async_call_later(
                    c.hass,
                    c._startup_recovery_retry_delay_s,
                    c._handle_startup_recovery_timer,
                )
                return

            _LOGGER.warning(
                "Startup auto-recovery readiness wait window exhausted after %s cycles; continuing with guarded recovery",
                c._startup_recovery_max_wait_cycles,
            )

        c._startup_recovery_wait_cycles = 0
        c._startup_recovery_attempt += 1
        attempt = c._startup_recovery_attempt

        try:
            await c.async_restore_last_valid_target(
                dry_run=c._write_authority_mode != WRITE_AUTH_COMPONENT,
                force=True,
                correlation_id=f"startup-restore-{attempt}-{uuid4().hex[:8]}",
            )

            if c._write_authority_mode == WRITE_AUTH_COMPONENT:
                options_result = await c.async_build_target_options_scaffold(
                    dry_run=False,
                    force=True,
                    include_none=True,
                    correlation_id=f"startup-component-options-{attempt}-{uuid4().hex[:8]}",
                )
                auto_result = await c.async_run_auto_select_scaffold(
                    dry_run=False,
                    force=True,
                    sync_options_if_missing=True,
                    include_none=True,
                    correlation_id=f"startup-component-auto-select-{attempt}-{uuid4().hex[:8]}",
                )

                now_iso = datetime.now(UTC).isoformat()
                c.metadata_stack.set_last_metadata_bridge_attempt({
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
                })
                c.async_set_updated_data(c.build_snapshot())
                _LOGGER.info(
                    "Startup auto-recovery completed with component-only no-mix flow (%s/%s)",
                    attempt,
                    c._startup_recovery_max_attempts,
                )
                return

            if c._write_authority_mode == WRITE_AUTH_LEGACY:
                now_iso = datetime.now(UTC).isoformat()
                c.metadata_stack.set_last_metadata_bridge_attempt({
                    "status": "skipped_legacy_authority",
                    "requested_at": now_iso,
                    "completed_at": now_iso,
                    "reason": (
                        "Startup bridge recovery skipped because authority mode is legacy; "
                        "runtime helper flow remains single-writer during boot"
                    ),
                    "resolver_status": "never_attempted",
                    "trial_status": "never_attempted",
                })
                c.async_set_updated_data(c.build_snapshot())
                _LOGGER.info(
                    "Startup auto-recovery skipped component bridge on legacy authority (%s/%s)",
                    attempt,
                    c._startup_recovery_max_attempts,
                )
                return

            result = await c.metadata_stack.async_run_metadata_trial_bridge_scaffold(
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
                    c._startup_recovery_max_attempts,
                )
                return

            if attempt < c._startup_recovery_max_attempts:
                _LOGGER.warning(
                    "Startup auto-recovery attempt %s/%s incomplete: status=%s reason=%s; retrying in %.1fs",
                    attempt,
                    c._startup_recovery_max_attempts,
                    status,
                    str(result.get("reason", "") or ""),
                    c._startup_recovery_retry_delay_s,
                )
                c._startup_recovery_unsub = async_call_later(
                    c.hass,
                    c._startup_recovery_retry_delay_s,
                    c._handle_startup_recovery_timer,
                )
            else:
                _LOGGER.warning(
                    "Startup auto-recovery exhausted after %s attempts (last_status=%s, last_reason=%s)",
                    c._startup_recovery_max_attempts,
                    status,
                    str(result.get("reason", "") or ""),
                )
        except Exception as err:  # pragma: no cover - defensive runtime guard
            if attempt < c._startup_recovery_max_attempts:
                _LOGGER.warning(
                    "Startup auto-recovery attempt %s/%s failed (%s); retrying in %.1fs",
                    attempt,
                    c._startup_recovery_max_attempts,
                    err,
                    c._startup_recovery_retry_delay_s,
                )
                c._startup_recovery_unsub = async_call_later(
                    c.hass,
                    c._startup_recovery_retry_delay_s,
                    c._handle_startup_recovery_timer,
                )
            else:
                _LOGGER.warning(
                    "Startup auto-recovery exhausted after %s attempts due to repeated failures",
                    c._startup_recovery_max_attempts,
                )

    def is_startup_recovery_boot_ready(self) -> tuple[bool, list[str]]:
        """Return whether MA/runtime surfaces are ready for startup recovery attempts."""
        c = self._coordinator
        reasons: list[str] = []

        ma_players_state = c.hass.states.get(LEGACY_MA_PLAYERS)
        ma_players_ready = ma_players_state is not None and c._is_resolved_state(ma_players_state.state)
        if not ma_players_ready:
            reasons.append("ma_players_not_ready")

        control_targets_state = c.hass.states.get(LEGACY_CONTROL_TARGETS)
        control_targets_ready = control_targets_state is not None and c._is_resolved_state(control_targets_state.state)
        if not control_targets_ready:
            reasons.append("control_targets_not_ready")

        helper_state = c.hass.states.get(LEGACY_ACTIVE_TARGET_HELPER)
        helper_exists = helper_state is not None
        if not helper_exists:
            reasons.append("active_target_helper_missing")

        helper_options_ready = False
        if helper_state is not None:
            normalized_options = WritePathFabric.normalize_options(helper_state.attributes.get("options", []))
            non_none_options = [item for item in normalized_options if c._normalize_state(item) != "none"]
            helper_options_ready = len(non_none_options) > 0
        if not helper_options_ready:
            reasons.append("active_target_options_not_ready")

        boot_ready = ma_players_ready and control_targets_ready and helper_exists and helper_options_ready
        return boot_ready, reasons

    @staticmethod
    def startup_wait_reason_prefix(reasons: list[str]) -> str:
        """Return human-readable startup wait prefix aligned to the blocking phase."""
        ma_boot_blockers = {"ma_players_not_ready", "control_targets_not_ready"}
        if any(item in ma_boot_blockers for item in reasons):
            return "waiting for Music Assistant boot readiness"
        return "waiting for control contract readiness after Music Assistant boot"

    @staticmethod
    def format_startup_boot_wait_reasons(reasons: list[str]) -> str:
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
