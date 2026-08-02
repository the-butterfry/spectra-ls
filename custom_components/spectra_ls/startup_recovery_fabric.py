# Description: Startup-recovery fabric workflow for Spectra LS metadata boot-gate orchestration extracted from meta-fabric.
# Version: 2026.08.01.4
# Last updated: 2026-08-01
# PARITY DIRECTIVE (until full cutover): behavior/contract edits here require same-slice two-track parity review
# and version-metadata review in runtime (`packages/` + `esphome/`) and component (`custom_components/spectra_ls/`) tracks.

from __future__ import annotations

from datetime import UTC, datetime
import logging
from time import monotonic
from typing import Any
from uuid import uuid4

from homeassistant.helpers.event import async_call_later

from .const import (
    COMPONENT_CONTROL_TARGETS,
    WRITE_AUTH_COMPONENT,
)

_LOGGER = logging.getLogger(__name__)


class StartupRecoveryFabricWorkflow:
    """Owns startup recovery orchestration extracted from meta-fabric."""

    def __init__(self, coordinator: Any) -> None:
        self._coordinator = coordinator
        self._last_wait_reason_key = ""
        self._last_wait_publish_monotonic = 0.0
        self._wait_publish_min_interval_s = 60.0

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
                "status": "waiting_for_startup_readiness",
                "requested_at": datetime.now(UTC).isoformat(),
                "completed_at": datetime.now(UTC).isoformat(),
                "reason": f"{wait_reason}: {reason_suffix}",
                "resolver_status": "never_attempted",
                "trial_status": "never_attempted",
            })

            wait_reason_key = "|".join(sorted(str(item) for item in boot_reasons)) or "boot_wait_unknown"
            now_mono = monotonic()
            should_publish_wait = (
                self._last_wait_reason_key != wait_reason_key
                or self._last_wait_publish_monotonic <= 0.0
                or (now_mono - self._last_wait_publish_monotonic) >= self._wait_publish_min_interval_s
            )
            if should_publish_wait:
                c.async_set_updated_data(c.build_snapshot())
                self._last_wait_reason_key = wait_reason_key
                self._last_wait_publish_monotonic = now_mono

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
        self._last_wait_reason_key = ""
        self._last_wait_publish_monotonic = 0.0
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

        component_targets_state = c.hass.states.get(COMPONENT_CONTROL_TARGETS)
        component_targets_count: float | None = None
        if component_targets_state is not None and c._is_resolved_state(component_targets_state.state):
            try:
                component_targets_count = float(component_targets_state.state)
            except (TypeError, ValueError):
                component_targets_count = None
        component_targets_ready = isinstance(component_targets_count, float) and component_targets_count > 0.0

        component_control_host_state = c.hass.states.get("sensor.component_control_host")
        component_control_port_state = c.hass.states.get("sensor.component_control_port")
        component_active_target_state = c.hass.states.get("sensor.component_active_target")
        component_now_playing_entity_state = c.hass.states.get("sensor.component_now_playing_entity")

        host_ready = bool(
            component_control_host_state is not None
            and c._is_resolved_state(component_control_host_state.state)
        )
        port_ready = bool(
            component_control_port_state is not None
            and c._is_resolved_state(component_control_port_state.state)
        )
        active_target_ready = bool(
            component_active_target_state is not None
            and c._is_resolved_state(component_active_target_state.state)
        )
        now_playing_entity_ready = bool(
            component_now_playing_entity_state is not None
            and c._is_resolved_state(component_now_playing_entity_state.state)
        )
        component_contract_live_ready = host_ready and port_ready and (active_target_ready or now_playing_entity_ready)

        target_options_plan = c._compute_component_target_options_plan()
        proposed_options = (
            target_options_plan.get("proposed_options", [])
            if isinstance(target_options_plan.get("proposed_options", []), list)
            else []
        )
        non_none_options = [item for item in proposed_options if c._normalize_state(str(item or "")) != "none"]
        target_options_ready = len(non_none_options) > 0

        strict_boot_ready = component_targets_ready and target_options_ready
        if not component_targets_ready:
            reasons.append("component_control_targets_not_ready")
        if not target_options_ready:
            reasons.append("active_target_options_not_ready")

        boot_ready = strict_boot_ready or component_contract_live_ready
        if boot_ready and component_contract_live_ready:
            reasons = []
        return boot_ready, reasons

    @staticmethod
    def startup_wait_reason_prefix(reasons: list[str]) -> str:
        """Return human-readable startup wait prefix aligned to the blocking phase."""
        ma_boot_blockers = {"component_control_targets_not_ready", "control_targets_not_ready"}
        if any(item in ma_boot_blockers for item in reasons):
            return "waiting for Music Assistant boot readiness"
        return "waiting for control contract readiness after Music Assistant boot"

    @staticmethod
    def format_startup_boot_wait_reasons(reasons: list[str]) -> str:
        """Format startup readiness blockers into operator-friendly wait messaging."""
        if not reasons:
            return "Music Assistant startup signals are still initializing"

        reason_map = {
            "component_control_targets_not_ready": "component control-target count is not ready yet",
            "control_targets_not_ready": "control target catalog is not ready yet",
            "active_target_helper_missing": "active-target helper is not available yet",
            "active_target_options_not_ready": "active-target options are still initializing",
        }
        friendly = [reason_map.get(item, item.replace("_", " ")) for item in reasons]
        return "; ".join(friendly)
