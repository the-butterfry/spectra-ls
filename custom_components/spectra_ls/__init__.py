# Description: Spectra LS custom integration setup for shadow parity, Phase 3 guarded routing write-path services, Phase 4 diagnostics scaffolding services (F4-S01/F4-S03), Phase 5 metadata trial contract service wiring, and Phase 6 control-center settings/execution services including bounded startup auto-recovery scheduling and selection-ownership migration services with hardened authority-contract response service support.
# Version: 2026.05.03.7
# Last updated: 2026-05-03
# PARITY DIRECTIVE: Behavior/contract edits must include same-slice two-track parity review and version-metadata review (runtime + component).

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.core import ServiceCall
from homeassistant.core import SupportsResponse
from homeassistant.exceptions import HomeAssistantError

from .authority_contract import build_authority_contract_packet
from .const import (
    CONTROL_CENTER_DEFAULTS,
    DOMAIN,
    PLATFORMS,
    SERVICE_DUMP_ROUTE_TRACE,
    SERVICE_METADATA_WRITE_TRIAL,
    SERVICE_RUN_P3_S01_SEQUENCE,
    SERVICE_RUN_P3_S02_SEQUENCE,
    SERVICE_RUN_P5_S02_SEQUENCE,
    SERVICE_ROUTE_WRITE_TRIAL,
    SERVICE_REBUILD_REGISTRY,
    SERVICE_SET_WRITE_AUTHORITY,
    SERVICE_VALIDATE_CONTRACTS,
    SERVICE_VALIDATE_METADATA_PREP,
    SERVICE_VALIDATE_METADATA_POLICY,
    SERVICE_GET_AUTHORITY_CONTRACT,
    SERVICE_GET_HOST_CUTOVER_GATE,
    SERVICE_RUN_P3_S03_SEQUENCE,
    SERVICE_VALIDATE_CAPABILITY_PROFILE,
    SERVICE_RUN_F4_S01_SEQUENCE,
    SERVICE_VALIDATE_ACTION_CATALOG,
    SERVICE_RUN_F4_S02_SEQUENCE,
    SERVICE_VALIDATE_CROSSFADE_BALANCE,
    SERVICE_RUN_F4_S03_SEQUENCE,
    SERVICE_EXECUTE_CONTROL_CENTER_INPUT,
    SERVICE_SET_CONTROL_CENTER_SETTINGS,
    SERVICE_VALIDATE_SCHEDULER,
    SERVICE_RUN_SCHEDULER_CHOICE,
    SERVICE_APPLY_SCHEDULER_CHOICE,
    SERVICE_BUILD_TARGET_OPTIONS_SCAFFOLD,
    SERVICE_RUN_METADATA_RESOLVER_SCAFFOLD,
    SERVICE_RUN_METADATA_TRIAL_BRIDGE_SCAFFOLD,
    SERVICE_RUN_AUTO_SELECT_SCAFFOLD,
    SERVICE_CYCLE_ACTIVE_TARGET,
    SERVICE_RESTORE_LAST_VALID_TARGET,
    SERVICE_TRACK_LAST_VALID_TARGET,
    normalize_control_center_settings,
)
from .coordinator import SpectraLsShadowCoordinator

_LOGGER = logging.getLogger(__name__)


_DOMAIN_SERVICE_NAMES: tuple[str, ...] = (
    SERVICE_REBUILD_REGISTRY,
    SERVICE_VALIDATE_CONTRACTS,
    SERVICE_DUMP_ROUTE_TRACE,
    SERVICE_SET_WRITE_AUTHORITY,
    SERVICE_ROUTE_WRITE_TRIAL,
    SERVICE_METADATA_WRITE_TRIAL,
    SERVICE_RUN_P3_S01_SEQUENCE,
    SERVICE_RUN_P3_S02_SEQUENCE,
    SERVICE_VALIDATE_METADATA_PREP,
    SERVICE_VALIDATE_METADATA_POLICY,
    SERVICE_GET_AUTHORITY_CONTRACT,
    SERVICE_GET_HOST_CUTOVER_GATE,
    SERVICE_RUN_P3_S03_SEQUENCE,
    SERVICE_RUN_P5_S02_SEQUENCE,
    SERVICE_VALIDATE_CAPABILITY_PROFILE,
    SERVICE_RUN_F4_S01_SEQUENCE,
    SERVICE_VALIDATE_ACTION_CATALOG,
    SERVICE_RUN_F4_S02_SEQUENCE,
    SERVICE_VALIDATE_CROSSFADE_BALANCE,
    SERVICE_RUN_F4_S03_SEQUENCE,
    SERVICE_SET_CONTROL_CENTER_SETTINGS,
    SERVICE_EXECUTE_CONTROL_CENTER_INPUT,
    SERVICE_VALIDATE_SCHEDULER,
    SERVICE_RUN_SCHEDULER_CHOICE,
    SERVICE_APPLY_SCHEDULER_CHOICE,
    SERVICE_BUILD_TARGET_OPTIONS_SCAFFOLD,
    SERVICE_RUN_AUTO_SELECT_SCAFFOLD,
    SERVICE_RUN_METADATA_RESOLVER_SCAFFOLD,
    SERVICE_RUN_METADATA_TRIAL_BRIDGE_SCAFFOLD,
    SERVICE_CYCLE_ACTIVE_TARGET,
    SERVICE_RESTORE_LAST_VALID_TARGET,
    SERVICE_TRACK_LAST_VALID_TARGET,
)


def _build_authority_snapshot_summary(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Build compact authority-related snapshot summary for service consumers."""
    route_trace = snapshot.get("route_trace", {}) if isinstance(snapshot.get("route_trace", {}), dict) else {}
    contract_validation = (
        snapshot.get("contract_validation", {})
        if isinstance(snapshot.get("contract_validation", {}), dict)
        else {}
    )
    cutover_prep_validation = (
        snapshot.get("cutover_prep_validation", {})
        if isinstance(snapshot.get("cutover_prep_validation", {}), dict)
        else {}
    )

    missing_required = contract_validation.get("missing_required", [])
    unresolved_required = contract_validation.get("unresolved_required", [])
    cutover_blocking = cutover_prep_validation.get("blocking_reasons", [])

    return {
        "captured_at": snapshot.get("captured_at"),
        "route_decision": str(route_trace.get("decision", "") or ""),
        "active_target": str(route_trace.get("active_target", "") or ""),
        "contract_valid": bool(contract_validation.get("valid", False)),
        "missing_required_count": len(missing_required) if isinstance(missing_required, list) else 0,
        "unresolved_required_count": len(unresolved_required) if isinstance(unresolved_required, list) else 0,
        "cutover_prep_complete": bool(cutover_prep_validation.get("cutover_prep_complete", False)),
        "cutover_prep_blocker_count": len(cutover_blocking) if isinstance(cutover_blocking, list) else 0,
    }


def _build_host_cutover_snapshot_summary(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Build compact host-cutover summary for service consumers."""
    route_trace = snapshot.get("route_trace", {}) if isinstance(snapshot.get("route_trace", {}), dict) else {}
    contract_validation = (
        snapshot.get("contract_validation", {})
        if isinstance(snapshot.get("contract_validation", {}), dict)
        else {}
    )
    host_gate = (
        snapshot.get("host_control_cutover_gate", {})
        if isinstance(snapshot.get("host_control_cutover_gate", {}), dict)
        else {}
    )
    gate_blockers = host_gate.get("gate_blockers", [])
    activation_blockers = host_gate.get("activation_blockers", [])

    return {
        "captured_at": snapshot.get("captured_at"),
        "route_decision": str(route_trace.get("decision", "") or ""),
        "active_target": str(route_trace.get("active_target", "") or ""),
        "contract_valid": bool(contract_validation.get("valid", False)),
        "authority_mode": str(host_gate.get("authority_mode", "legacy") or "legacy"),
        "gate_status": str(host_gate.get("status", "blocked") or "blocked"),
        "ready_for_cutover": bool(host_gate.get("ready_for_cutover", False)),
        "ready_for_authoritative_activation": bool(
            host_gate.get("ready_for_authoritative_activation", False)
        ),
        "gate_blocker_count": len(gate_blockers) if isinstance(gate_blockers, list) else 0,
        "activation_blocker_count": len(activation_blockers) if isinstance(activation_blockers, list) else 0,
    }


def _coerce_bool(value: object, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        norm = value.strip().lower()
        if norm in {"1", "true", "yes", "on"}:
            return True
        if norm in {"0", "false", "no", "off", ""}:
            return False
    return default


def _coerce_int(value: object, default: int = 0) -> int:
    if value is None:
        return default
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        norm = value.strip()
        if norm == "":
            return default
        try:
            return int(norm)
        except ValueError:
            return default
    return default


def _register_domain_service(
    hass: HomeAssistant,
    service_name: str,
    handler: Any,
    *,
    supports_response: SupportsResponse | None = None,
) -> None:
    if hass.services.has_service(DOMAIN, service_name):
        return
    kwargs: dict[str, Any] = {}
    if supports_response is not None:
        kwargs["supports_response"] = supports_response
    hass.services.async_register(DOMAIN, service_name, handler, **kwargs)


def _remove_domain_service(hass: HomeAssistant, service_name: str) -> None:
    if hass.services.has_service(DOMAIN, service_name):
        hass.services.async_remove(DOMAIN, service_name)


async def async_setup(hass: HomeAssistant, _config: dict[str, Any]) -> bool:
    """Set up Spectra LS integration domain."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Spectra LS from config entry."""
    coordinator = SpectraLsShadowCoordinator(hass, entry)
    await coordinator.async_setup()

    async def _run_service_sequence(
        sequence_label: str,
        stages: list[tuple[str, Any, tuple[Any, ...], dict[str, Any]]],
    ) -> None:
        for stage, op, args, kwargs in stages:
            try:
                await op(*args, **kwargs)
            except Exception as err:
                _LOGGER.exception("%s sequence failed at stage '%s'", sequence_label, stage)
                raise HomeAssistantError(
                    f"{sequence_label} sequence failed at stage '{stage}': {err}"
                ) from err

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    async def _handle_options_update(hass: HomeAssistant, updated_entry: ConfigEntry) -> None:
        coordinator_obj: SpectraLsShadowCoordinator | None = hass.data.get(DOMAIN, {}).get(updated_entry.entry_id)
        if coordinator_obj is not None:
            await coordinator_obj.async_apply_control_center_settings(updated_entry.options)

    options_update_unsub = entry.add_update_listener(_handle_options_update)
    hass.data[DOMAIN][f"{entry.entry_id}_options_unsub"] = options_update_unsub

    async def _service_rebuild_registry(_call: ServiceCall) -> None:
        await coordinator.async_rebuild_registry()

    async def _service_validate_contracts(_call: ServiceCall) -> None:
        await coordinator.async_validate_contracts()

    async def _service_dump_route_trace(_call: ServiceCall) -> None:
        await coordinator.async_dump_route_trace()

    async def _service_set_write_authority(call: ServiceCall) -> None:
        mode = str(call.data.get("mode", "legacy"))
        reason = str(call.data.get("reason", ""))
        await coordinator.async_set_write_authority(mode=mode, reason=reason)

    async def _service_route_write_trial(call: ServiceCall) -> None:
        correlation_id = str(call.data.get("correlation_id", "")).strip() or None
        force = _coerce_bool(call.data.get("force"), default=False)
        await coordinator.async_route_write_trial(correlation_id=correlation_id, force=force)

    async def _service_metadata_write_trial(call: ServiceCall) -> None:
        mode = str(call.data.get("mode", "legacy"))
        window_id = str(call.data.get("window_id", "")).strip()
        reason = str(call.data.get("reason", "")).strip()
        dry_run = _coerce_bool(call.data.get("dry_run"), default=True)
        expected_target = str(call.data.get("expected_target", "")).strip() or None
        expected_route = str(call.data.get("expected_route", "")).strip() or None
        expected_meta_entity = str(call.data.get("expected_meta_entity", "")).strip() or None
        correlation_id = str(call.data.get("correlation_id", "")).strip() or None

        await coordinator.metadata_stack.async_metadata_write_trial(
            mode=mode,
            window_id=window_id,
            reason=reason,
            dry_run=dry_run,
            expected_target=expected_target,
            expected_route=expected_route,
            expected_meta_entity=expected_meta_entity,
            correlation_id=correlation_id,
        )

    async def _service_run_p3_s01_sequence(call: ServiceCall) -> None:
        mode = str(call.data.get("mode", "component"))
        reason = str(call.data.get("reason", ""))
        correlation_id = str(call.data.get("correlation_id", "")).strip() or None
        force = _coerce_bool(call.data.get("force"), default=False)

        await coordinator.async_set_write_authority(mode=mode, reason=reason)
        await coordinator.async_rebuild_registry()
        await coordinator.async_validate_contracts()
        await coordinator.async_dump_route_trace()
        await coordinator.async_route_write_trial(correlation_id=correlation_id, force=force)

    async def _service_run_p3_s02_sequence(call: ServiceCall) -> None:
        mode = str(call.data.get("mode", "component"))
        reason = str(call.data.get("reason", ""))
        run_write_trial = _coerce_bool(call.data.get("run_write_trial"), default=False)
        correlation_id = str(call.data.get("correlation_id", "")).strip() or None
        force = _coerce_bool(call.data.get("force"), default=False)

        await coordinator.async_set_write_authority(mode=mode, reason=reason)
        await coordinator.async_rebuild_registry()
        await coordinator.async_validate_contracts()
        await coordinator.async_dump_route_trace()
        if run_write_trial:
            await coordinator.async_route_write_trial(correlation_id=correlation_id, force=force)
        await coordinator.async_validate_selection_handoff()

    async def _service_validate_metadata_prep(_call: ServiceCall) -> None:
        await coordinator.metadata_stack.async_validate_metadata_prep()

    async def _service_validate_metadata_policy(call: ServiceCall) -> None:
        # Policy status is synthesized from helper entities + metadata-prep checks;
        # refresh + prep validation keeps diagnostics consistent for operators.
        await coordinator.metadata_stack.async_validate_metadata_prep()

        trigger_provider_refresh = _coerce_bool(call.data.get("trigger_provider_refresh"), default=True)
        if not trigger_provider_refresh:
            return

        refresh_reason = str(call.data.get("refresh_reason", "validate_metadata_policy")).strip() or "validate_metadata_policy"
        force_refresh = _coerce_bool(call.data.get("force_refresh"), default=True)

        if not hass.services.has_service("script", "ma_send_metadata_to_providers"):
            _LOGGER.warning(
                "validate_metadata_policy requested provider refresh, but script.ma_send_metadata_to_providers is unavailable"
            )
            return

        await hass.services.async_call(
            "script",
            "ma_send_metadata_to_providers",
            {
                "reason": refresh_reason,
                "force_refresh": force_refresh,
            },
            blocking=True,
        )

    async def _service_get_authority_contract(call: ServiceCall) -> dict[str, Any]:
        refresh = _coerce_bool(call.data.get("refresh"), default=True)
        include_snapshot_summary = _coerce_bool(call.data.get("include_snapshot_summary"), default=False)
        fail_closed_if_unready = _coerce_bool(call.data.get("fail_closed_if_unready"), default=False)
        fail_closed_if_contract_not_ready = _coerce_bool(
            call.data.get("fail_closed_if_contract_not_ready"), default=False
        )
        required_checkpoint_count = _coerce_int(call.data.get("required_checkpoint_count"), default=0)
        if required_checkpoint_count < 0:
            required_checkpoint_count = 0
        if refresh:
            await coordinator.metadata_stack.async_validate_metadata_prep()
        snapshot = coordinator.data if isinstance(coordinator.data, dict) else {}
        packet = build_authority_contract_packet(snapshot)

        if fail_closed_if_unready and not bool(packet.get("cutover_prep_complete", False)):
            blocker_count = int(packet.get("cutover_prep_blocker_count", 0) or 0)
            raise HomeAssistantError(
                f"Authority contract is not cutover-ready (cutover_prep_complete=false, blockers={blocker_count})"
            )

        if fail_closed_if_contract_not_ready and not bool(packet.get("authority_contract_ready", False)):
            blocker_count = int(packet.get("authority_contract_blocker_count", 0) or 0)
            raise HomeAssistantError(
                f"Authority contract is not ready (authority_contract_ready=false, blockers={blocker_count})"
            )

        if required_checkpoint_count > 0:
            observed_checkpoint_count = int(packet.get("proof_checkpoint_count", 0) or 0)
            if observed_checkpoint_count < required_checkpoint_count:
                raise HomeAssistantError(
                    "Authority contract has insufficient proof checkpoints "
                    f"(required={required_checkpoint_count}, observed={observed_checkpoint_count})"
                )

        if include_snapshot_summary:
            return {
                "authority_contract": packet,
                "snapshot_summary": _build_authority_snapshot_summary(snapshot),
            }

        return packet

    async def _service_get_host_cutover_gate(call: ServiceCall) -> dict[str, Any]:
        refresh = _coerce_bool(call.data.get("refresh"), default=True)
        include_snapshot_summary = _coerce_bool(call.data.get("include_snapshot_summary"), default=False)
        fail_closed_if_not_ready = _coerce_bool(call.data.get("fail_closed_if_not_ready"), default=False)
        fail_closed_if_not_activation_ready = _coerce_bool(
            call.data.get("fail_closed_if_not_activation_ready"),
            default=False,
        )

        if refresh:
            coordinator.refresh_snapshot()

        snapshot = coordinator.data if isinstance(coordinator.data, dict) else {}
        host_gate = (
            snapshot.get("host_control_cutover_gate", {})
            if isinstance(snapshot.get("host_control_cutover_gate", {}), dict)
            else {}
        )

        if fail_closed_if_not_ready and not bool(host_gate.get("ready_for_cutover", False)):
            blocker_count = len(host_gate.get("gate_blockers", [])) if isinstance(host_gate.get("gate_blockers", []), list) else 0
            raise HomeAssistantError(
                f"Host cutover gate is not ready (ready_for_cutover=false, blockers={blocker_count})"
            )

        if fail_closed_if_not_activation_ready and not bool(
            host_gate.get("ready_for_authoritative_activation", False)
        ):
            blocker_count = len(host_gate.get("activation_blockers", [])) if isinstance(host_gate.get("activation_blockers", []), list) else 0
            raise HomeAssistantError(
                "Host cutover gate is not activation-ready "
                f"(ready_for_authoritative_activation=false, blockers={blocker_count})"
            )

        if include_snapshot_summary:
            return {
                "host_cutover_gate": host_gate,
                "snapshot_summary": _build_host_cutover_snapshot_summary(snapshot),
            }

        return host_gate

    async def _service_run_p3_s03_sequence(call: ServiceCall) -> None:
        mode = str(call.data.get("mode", "legacy"))
        reason = str(call.data.get("reason", ""))

        await coordinator.async_set_write_authority(mode=mode, reason=reason)
        await coordinator.async_rebuild_registry()
        await coordinator.async_validate_contracts()
        await coordinator.async_dump_route_trace()
        await coordinator.async_validate_selection_handoff()
        await coordinator.metadata_stack.async_validate_metadata_prep()

    async def _service_run_p5_s02_sequence(call: ServiceCall) -> None:
        mode = str(call.data.get("mode", "legacy"))
        reason = str(call.data.get("reason", "P5-S02 one-shot sequence"))
        window_id = str(call.data.get("window_id", "")).strip()
        dry_run = _coerce_bool(call.data.get("dry_run"), default=True)
        expected_target = str(call.data.get("expected_target", "")).strip() or None
        expected_route = str(call.data.get("expected_route", "")).strip() or None
        correlation_id = str(call.data.get("correlation_id", "")).strip() or None

        stages: list[tuple[str, Any, tuple[Any, ...], dict[str, Any]]] = [
            ("set_write_authority", coordinator.async_set_write_authority, (), {"mode": mode, "reason": reason}),
            ("rebuild_registry", coordinator.async_rebuild_registry, (), {}),
            ("validate_contracts", coordinator.async_validate_contracts, (), {}),
            ("dump_route_trace", coordinator.async_dump_route_trace, (), {}),
            ("validate_selection_handoff", coordinator.async_validate_selection_handoff, (), {}),
            ("validate_metadata_prep_pretrial", coordinator.metadata_stack.async_validate_metadata_prep, (), {}),
            (
                "metadata_write_trial",
                coordinator.metadata_stack.async_metadata_write_trial,
                (),
                {
                    "mode": mode,
                    "window_id": window_id,
                    "reason": reason,
                    "dry_run": dry_run,
                    "expected_target": expected_target,
                    "expected_route": expected_route,
                    "correlation_id": correlation_id,
                },
            ),
            ("validate_metadata_prep_posttrial", coordinator.metadata_stack.async_validate_metadata_prep, (), {}),
        ]

        await _run_service_sequence("P5-S02", stages)

    async def _service_validate_capability_profile(_call: ServiceCall) -> None:
        await coordinator.async_validate_capability_profile()

    async def _service_run_f4_s01_sequence(call: ServiceCall) -> None:
        mode = str(call.data.get("mode", "legacy"))
        reason = str(call.data.get("reason", ""))

        stages: list[tuple[str, Any, tuple[Any, ...], dict[str, Any]]] = [
            ("set_write_authority", coordinator.async_set_write_authority, (), {"mode": mode, "reason": reason}),
            ("rebuild_registry", coordinator.async_rebuild_registry, (), {}),
            ("validate_contracts", coordinator.async_validate_contracts, (), {}),
            ("dump_route_trace", coordinator.async_dump_route_trace, (), {}),
            ("validate_selection_handoff", coordinator.async_validate_selection_handoff, (), {}),
            ("validate_metadata_prep", coordinator.metadata_stack.async_validate_metadata_prep, (), {}),
            ("validate_capability_profile", coordinator.async_validate_capability_profile, (), {}),
        ]

        await _run_service_sequence("F4-S01", stages)

    async def _service_validate_action_catalog(_call: ServiceCall) -> None:
        await coordinator.async_validate_action_catalog()

    async def _service_run_f4_s02_sequence(call: ServiceCall) -> None:
        mode = str(call.data.get("mode", "legacy"))
        reason = str(call.data.get("reason", ""))

        stages: list[tuple[str, Any, tuple[Any, ...], dict[str, Any]]] = [
            ("set_write_authority", coordinator.async_set_write_authority, (), {"mode": mode, "reason": reason}),
            ("rebuild_registry", coordinator.async_rebuild_registry, (), {}),
            ("validate_contracts", coordinator.async_validate_contracts, (), {}),
            ("dump_route_trace", coordinator.async_dump_route_trace, (), {}),
            ("validate_selection_handoff", coordinator.async_validate_selection_handoff, (), {}),
            ("validate_metadata_prep", coordinator.metadata_stack.async_validate_metadata_prep, (), {}),
            ("validate_capability_profile", coordinator.async_validate_capability_profile, (), {}),
            ("validate_action_catalog", coordinator.async_validate_action_catalog, (), {}),
        ]

        await _run_service_sequence("F4-S02", stages)

    async def _service_validate_crossfade_balance(_call: ServiceCall) -> None:
        await coordinator.async_validate_crossfade_balance()

    async def _service_run_f4_s03_sequence(call: ServiceCall) -> None:
        mode = str(call.data.get("mode", "legacy"))
        reason = str(call.data.get("reason", ""))

        stages: list[tuple[str, Any, tuple[Any, ...], dict[str, Any]]] = [
            ("set_write_authority", coordinator.async_set_write_authority, (), {"mode": mode, "reason": reason}),
            ("rebuild_registry", coordinator.async_rebuild_registry, (), {}),
            ("validate_contracts", coordinator.async_validate_contracts, (), {}),
            ("dump_route_trace", coordinator.async_dump_route_trace, (), {}),
            ("validate_selection_handoff", coordinator.async_validate_selection_handoff, (), {}),
            ("validate_metadata_prep", coordinator.metadata_stack.async_validate_metadata_prep, (), {}),
            ("validate_capability_profile", coordinator.async_validate_capability_profile, (), {}),
            ("validate_action_catalog", coordinator.async_validate_action_catalog, (), {}),
            ("validate_crossfade_balance", coordinator.async_validate_crossfade_balance, (), {}),
        ]

        await _run_service_sequence("F4-S03", stages)

    async def _service_validate_scheduler(_call: ServiceCall) -> None:
        await coordinator.async_validate_scheduler()

    async def _service_run_scheduler_choice(call: ServiceCall) -> None:
        require_control_capable = _coerce_bool(call.data.get("require_control_capable"), default=True)
        prefer_fresh = _coerce_bool(call.data.get("prefer_fresh"), default=True)
        max_results = max(1, _coerce_int(call.data.get("max_results"), default=5))
        target_hint = str(call.data.get("target_hint", "") or "").strip()
        correlation_id = str(call.data.get("correlation_id", "") or "").strip() or None
        await coordinator.async_run_scheduler_choice(
            require_control_capable=require_control_capable,
            prefer_fresh=prefer_fresh,
            max_results=max_results,
            target_hint=target_hint,
            correlation_id=correlation_id,
        )

    async def _service_apply_scheduler_choice(call: ServiceCall) -> None:
        require_control_capable = _coerce_bool(call.data.get("require_control_capable"), default=True)
        prefer_fresh = _coerce_bool(call.data.get("prefer_fresh"), default=True)
        max_results = max(1, _coerce_int(call.data.get("max_results"), default=5))
        target_hint = str(call.data.get("target_hint", "") or "").strip()
        dry_run = _coerce_bool(call.data.get("dry_run"), default=True)
        force = _coerce_bool(call.data.get("force"), default=False)
        correlation_id = str(call.data.get("correlation_id", "") or "").strip() or None
        await coordinator.async_apply_scheduler_choice(
            require_control_capable=require_control_capable,
            prefer_fresh=prefer_fresh,
            max_results=max_results,
            target_hint=target_hint,
            dry_run=dry_run,
            force=force,
            correlation_id=correlation_id,
        )

    async def _service_build_target_options_scaffold(call: ServiceCall) -> None:
        dry_run = _coerce_bool(call.data.get("dry_run"), default=True)
        force = _coerce_bool(call.data.get("force"), default=False)
        include_none = _coerce_bool(call.data.get("include_none"), default=True)
        correlation_id = str(call.data.get("correlation_id", "") or "").strip() or None
        await coordinator.async_build_target_options_scaffold(
            dry_run=dry_run,
            force=force,
            include_none=include_none,
            correlation_id=correlation_id,
        )

    async def _service_run_auto_select_scaffold(call: ServiceCall) -> None:
        dry_run = _coerce_bool(call.data.get("dry_run"), default=True)
        force = _coerce_bool(call.data.get("force"), default=False)
        sync_options_if_missing = _coerce_bool(call.data.get("sync_options_if_missing"), default=False)
        include_none = _coerce_bool(call.data.get("include_none"), default=True)
        correlation_id = str(call.data.get("correlation_id", "") or "").strip() or None
        await coordinator.async_run_auto_select_scaffold(
            dry_run=dry_run,
            force=force,
            sync_options_if_missing=sync_options_if_missing,
            include_none=include_none,
            correlation_id=correlation_id,
        )

    async def _service_run_metadata_resolver_scaffold(call: ServiceCall) -> None:
        dry_run = _coerce_bool(call.data.get("dry_run"), default=True)
        force = _coerce_bool(call.data.get("force"), default=False)
        correlation_id = str(call.data.get("correlation_id", "") or "").strip() or None
        await coordinator.metadata_stack.async_run_metadata_resolver_scaffold(
            dry_run=dry_run,
            force=force,
            correlation_id=correlation_id,
        )

    async def _service_run_metadata_trial_bridge_scaffold(call: ServiceCall) -> None:
        window_id = str(call.data.get("window_id", "") or "").strip()
        reason = str(call.data.get("reason", "") or "").strip()
        resolver_dry_run = _coerce_bool(call.data.get("resolver_dry_run"), default=True)
        trial_dry_run = _coerce_bool(call.data.get("trial_dry_run"), default=True)
        force = _coerce_bool(call.data.get("force"), default=False)
        expected_target = str(call.data.get("expected_target", "") or "").strip() or None
        expected_route = str(call.data.get("expected_route", "") or "").strip() or None
        expected_meta_entity = str(call.data.get("expected_meta_entity", "") or "").strip() or None
        correlation_id = str(call.data.get("correlation_id", "") or "").strip() or None

        await coordinator.metadata_stack.async_run_metadata_trial_bridge_scaffold(
            window_id=window_id,
            reason=reason,
            resolver_dry_run=resolver_dry_run,
            trial_dry_run=trial_dry_run,
            force=force,
            expected_target=expected_target,
            expected_route=expected_route,
            expected_meta_entity=expected_meta_entity,
            correlation_id=correlation_id,
        )

    async def _service_cycle_active_target(call: ServiceCall) -> None:
        dry_run = _coerce_bool(call.data.get("dry_run"), default=True)
        force = _coerce_bool(call.data.get("force"), default=False)
        include_none = _coerce_bool(call.data.get("include_none"), default=True)
        correlation_id = str(call.data.get("correlation_id", "") or "").strip() or None
        await coordinator.async_cycle_active_target(
            dry_run=dry_run,
            force=force,
            include_none=include_none,
            correlation_id=correlation_id,
        )

    async def _service_restore_last_valid_target(call: ServiceCall) -> None:
        dry_run = _coerce_bool(call.data.get("dry_run"), default=True)
        force = _coerce_bool(call.data.get("force"), default=False)
        correlation_id = str(call.data.get("correlation_id", "") or "").strip() or None
        await coordinator.async_restore_last_valid_target(
            dry_run=dry_run,
            force=force,
            correlation_id=correlation_id,
        )

    async def _service_track_last_valid_target(call: ServiceCall) -> None:
        dry_run = _coerce_bool(call.data.get("dry_run"), default=True)
        force = _coerce_bool(call.data.get("force"), default=False)
        correlation_id = str(call.data.get("correlation_id", "") or "").strip() or None
        await coordinator.async_track_last_valid_target(
            dry_run=dry_run,
            force=force,
            correlation_id=correlation_id,
            source="service_track_last_valid_target",
        )

    async def _service_set_control_center_settings(call: ServiceCall) -> None:
        raw_patch = {key: call.data.get(key) for key in CONTROL_CENTER_DEFAULTS.keys() if key in call.data}
        merged = normalize_control_center_settings({**entry.options, **raw_patch})
        hass.config_entries.async_update_entry(entry, options=merged)
        await coordinator.async_apply_control_center_settings(merged)

    async def _service_execute_control_center_input(call: ServiceCall) -> None:
        input_event = str(call.data.get("input_event", "") or "").strip()
        correlation_id = str(call.data.get("correlation_id", "") or "").strip() or None
        target_hint = str(call.data.get("target_hint", "") or "").strip() or None
        dry_run = _coerce_bool(call.data.get("dry_run"), default=True)
        delta = call.data.get("delta")
        await coordinator.async_execute_control_center_input(
            input_event=input_event,
            correlation_id=correlation_id,
            target_hint=target_hint,
            dry_run=dry_run,
            delta=delta,
        )

    service_registrations: tuple[tuple[str, Any, SupportsResponse | None], ...] = (
        (SERVICE_REBUILD_REGISTRY, _service_rebuild_registry, None),
        (SERVICE_VALIDATE_CONTRACTS, _service_validate_contracts, None),
        (SERVICE_DUMP_ROUTE_TRACE, _service_dump_route_trace, None),
        (SERVICE_SET_WRITE_AUTHORITY, _service_set_write_authority, None),
        (SERVICE_ROUTE_WRITE_TRIAL, _service_route_write_trial, None),
        (SERVICE_METADATA_WRITE_TRIAL, _service_metadata_write_trial, None),
        (SERVICE_RUN_P3_S01_SEQUENCE, _service_run_p3_s01_sequence, None),
        (SERVICE_RUN_P3_S02_SEQUENCE, _service_run_p3_s02_sequence, None),
        (SERVICE_VALIDATE_METADATA_PREP, _service_validate_metadata_prep, None),
        (SERVICE_VALIDATE_METADATA_POLICY, _service_validate_metadata_policy, None),
        (SERVICE_GET_AUTHORITY_CONTRACT, _service_get_authority_contract, SupportsResponse.ONLY),
        (SERVICE_GET_HOST_CUTOVER_GATE, _service_get_host_cutover_gate, SupportsResponse.ONLY),
        (SERVICE_RUN_P3_S03_SEQUENCE, _service_run_p3_s03_sequence, None),
        (SERVICE_RUN_P5_S02_SEQUENCE, _service_run_p5_s02_sequence, None),
        (SERVICE_VALIDATE_CAPABILITY_PROFILE, _service_validate_capability_profile, None),
        (SERVICE_RUN_F4_S01_SEQUENCE, _service_run_f4_s01_sequence, None),
        (SERVICE_VALIDATE_ACTION_CATALOG, _service_validate_action_catalog, None),
        (SERVICE_RUN_F4_S02_SEQUENCE, _service_run_f4_s02_sequence, None),
        (SERVICE_VALIDATE_CROSSFADE_BALANCE, _service_validate_crossfade_balance, None),
        (SERVICE_RUN_F4_S03_SEQUENCE, _service_run_f4_s03_sequence, None),
        (SERVICE_SET_CONTROL_CENTER_SETTINGS, _service_set_control_center_settings, None),
        (SERVICE_EXECUTE_CONTROL_CENTER_INPUT, _service_execute_control_center_input, None),
        (SERVICE_VALIDATE_SCHEDULER, _service_validate_scheduler, None),
        (SERVICE_RUN_SCHEDULER_CHOICE, _service_run_scheduler_choice, None),
        (SERVICE_APPLY_SCHEDULER_CHOICE, _service_apply_scheduler_choice, None),
        (SERVICE_BUILD_TARGET_OPTIONS_SCAFFOLD, _service_build_target_options_scaffold, None),
        (SERVICE_RUN_AUTO_SELECT_SCAFFOLD, _service_run_auto_select_scaffold, None),
        (SERVICE_RUN_METADATA_RESOLVER_SCAFFOLD, _service_run_metadata_resolver_scaffold, None),
        (SERVICE_RUN_METADATA_TRIAL_BRIDGE_SCAFFOLD, _service_run_metadata_trial_bridge_scaffold, None),
        (SERVICE_CYCLE_ACTIVE_TARGET, _service_cycle_active_target, None),
        (SERVICE_RESTORE_LAST_VALID_TARGET, _service_restore_last_valid_target, None),
        (SERVICE_TRACK_LAST_VALID_TARGET, _service_track_last_valid_target, None),
    )

    for service_name, handler, supports_response in service_registrations:
        _register_domain_service(
            hass,
            service_name,
            handler,
            supports_response=supports_response,
        )

    try:
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    except Exception:
        await coordinator.async_shutdown()
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
        raise

    await coordinator.async_schedule_startup_recovery()

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Spectra LS config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator: SpectraLsShadowCoordinator | None = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
        if coordinator is not None:
            await coordinator.async_shutdown()
        unsub = hass.data.get(DOMAIN, {}).pop(f"{entry.entry_id}_options_unsub", None)
        if callable(unsub):
            unsub()
        if not hass.data.get(DOMAIN):
            for service_name in _DOMAIN_SERVICE_NAMES:
                _remove_domain_service(hass, service_name)
    return unload_ok
