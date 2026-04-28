# Description: Spectra LS custom integration setup for shadow parity, Phase 3 guarded routing write-path services, Phase 4 diagnostics scaffolding services (F4-S01/F4-S03), Phase 5 metadata trial contract service wiring, and Phase 6 control-center settings/execution services including bounded startup auto-recovery scheduling and selection-ownership migration services.
# Version: 2026.04.27.1
# Last updated: 2026-04-27

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.core import ServiceCall
from homeassistant.exceptions import HomeAssistantError

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


async def async_setup(hass: HomeAssistant, _config: dict[str, Any]) -> bool:
    """Set up Spectra LS integration domain."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Spectra LS from config entry."""
    coordinator = SpectraLsShadowCoordinator(hass, entry)
    await coordinator.async_setup()

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
        force = bool(call.data.get("force", False))
        await coordinator.async_route_write_trial(correlation_id=correlation_id, force=force)

    async def _service_metadata_write_trial(call: ServiceCall) -> None:
        mode = str(call.data.get("mode", "legacy"))
        window_id = str(call.data.get("window_id", "")).strip()
        reason = str(call.data.get("reason", "")).strip()
        dry_run = bool(call.data.get("dry_run", True))
        expected_target = str(call.data.get("expected_target", "")).strip() or None
        expected_route = str(call.data.get("expected_route", "")).strip() or None
        expected_meta_entity = str(call.data.get("expected_meta_entity", "")).strip() or None
        correlation_id = str(call.data.get("correlation_id", "")).strip() or None

        await coordinator.async_metadata_write_trial(
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
        force = bool(call.data.get("force", False))

        await coordinator.async_set_write_authority(mode=mode, reason=reason)
        await coordinator.async_rebuild_registry()
        await coordinator.async_validate_contracts()
        await coordinator.async_dump_route_trace()
        await coordinator.async_route_write_trial(correlation_id=correlation_id, force=force)

    async def _service_run_p3_s02_sequence(call: ServiceCall) -> None:
        mode = str(call.data.get("mode", "component"))
        reason = str(call.data.get("reason", ""))
        run_write_trial = bool(call.data.get("run_write_trial", False))
        correlation_id = str(call.data.get("correlation_id", "")).strip() or None
        force = bool(call.data.get("force", False))

        await coordinator.async_set_write_authority(mode=mode, reason=reason)
        await coordinator.async_rebuild_registry()
        await coordinator.async_validate_contracts()
        await coordinator.async_dump_route_trace()
        if run_write_trial:
            await coordinator.async_route_write_trial(correlation_id=correlation_id, force=force)
        await coordinator.async_validate_selection_handoff()

    async def _service_validate_metadata_prep(_call: ServiceCall) -> None:
        await coordinator.async_validate_metadata_prep()

    async def _service_validate_metadata_policy(_call: ServiceCall) -> None:
        # Policy status is synthesized from helper entities + metadata-prep checks;
        # refresh + prep validation keeps diagnostics consistent for operators.
        await coordinator.async_validate_metadata_prep()

    async def _service_run_p3_s03_sequence(call: ServiceCall) -> None:
        mode = str(call.data.get("mode", "legacy"))
        reason = str(call.data.get("reason", ""))

        await coordinator.async_set_write_authority(mode=mode, reason=reason)
        await coordinator.async_rebuild_registry()
        await coordinator.async_validate_contracts()
        await coordinator.async_dump_route_trace()
        await coordinator.async_validate_selection_handoff()
        await coordinator.async_validate_metadata_prep()

    async def _service_run_p5_s02_sequence(call: ServiceCall) -> None:
        mode = str(call.data.get("mode", "legacy"))
        reason = str(call.data.get("reason", "P5-S02 one-shot sequence"))
        window_id = str(call.data.get("window_id", "")).strip()
        dry_run = bool(call.data.get("dry_run", True))
        expected_target = str(call.data.get("expected_target", "")).strip() or None
        expected_route = str(call.data.get("expected_route", "")).strip() or None
        correlation_id = str(call.data.get("correlation_id", "")).strip() or None

        stages: list[tuple[str, Any, tuple[Any, ...], dict[str, Any]]] = [
            ("set_write_authority", coordinator.async_set_write_authority, (), {"mode": mode, "reason": reason}),
            ("rebuild_registry", coordinator.async_rebuild_registry, (), {}),
            ("validate_contracts", coordinator.async_validate_contracts, (), {}),
            ("dump_route_trace", coordinator.async_dump_route_trace, (), {}),
            ("validate_selection_handoff", coordinator.async_validate_selection_handoff, (), {}),
            ("validate_metadata_prep_pretrial", coordinator.async_validate_metadata_prep, (), {}),
            (
                "metadata_write_trial",
                coordinator.async_metadata_write_trial,
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
            ("validate_metadata_prep_posttrial", coordinator.async_validate_metadata_prep, (), {}),
        ]

        for stage, op, args, kwargs in stages:
            try:
                await op(*args, **kwargs)
            except Exception as err:
                _LOGGER.exception("P5-S02 sequence failed at stage '%s'", stage)
                raise HomeAssistantError(f"P5-S02 sequence failed at stage '{stage}': {err}") from err

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
            ("validate_metadata_prep", coordinator.async_validate_metadata_prep, (), {}),
            ("validate_capability_profile", coordinator.async_validate_capability_profile, (), {}),
        ]

        for stage, op, args, kwargs in stages:
            try:
                await op(*args, **kwargs)
            except Exception as err:
                _LOGGER.exception("F4-S01 sequence failed at stage '%s'", stage)
                raise HomeAssistantError(f"F4-S01 sequence failed at stage '{stage}': {err}") from err

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
            ("validate_metadata_prep", coordinator.async_validate_metadata_prep, (), {}),
            ("validate_capability_profile", coordinator.async_validate_capability_profile, (), {}),
            ("validate_action_catalog", coordinator.async_validate_action_catalog, (), {}),
        ]

        for stage, op, args, kwargs in stages:
            try:
                await op(*args, **kwargs)
            except Exception as err:
                _LOGGER.exception("F4-S02 sequence failed at stage '%s'", stage)
                raise HomeAssistantError(f"F4-S02 sequence failed at stage '{stage}': {err}") from err

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
            ("validate_metadata_prep", coordinator.async_validate_metadata_prep, (), {}),
            ("validate_capability_profile", coordinator.async_validate_capability_profile, (), {}),
            ("validate_action_catalog", coordinator.async_validate_action_catalog, (), {}),
            ("validate_crossfade_balance", coordinator.async_validate_crossfade_balance, (), {}),
        ]

        for stage, op, args, kwargs in stages:
            try:
                await op(*args, **kwargs)
            except Exception as err:
                _LOGGER.exception("F4-S03 sequence failed at stage '%s'", stage)
                raise HomeAssistantError(f"F4-S03 sequence failed at stage '{stage}': {err}") from err

    async def _service_validate_scheduler(_call: ServiceCall) -> None:
        await coordinator.async_validate_scheduler()

    async def _service_run_scheduler_choice(call: ServiceCall) -> None:
        require_control_capable = bool(call.data.get("require_control_capable", True))
        prefer_fresh = bool(call.data.get("prefer_fresh", True))
        max_results = int(call.data.get("max_results", 5) or 5)
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
        require_control_capable = bool(call.data.get("require_control_capable", True))
        prefer_fresh = bool(call.data.get("prefer_fresh", True))
        max_results = int(call.data.get("max_results", 5) or 5)
        target_hint = str(call.data.get("target_hint", "") or "").strip()
        dry_run = bool(call.data.get("dry_run", True))
        force = bool(call.data.get("force", False))
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
        dry_run = bool(call.data.get("dry_run", True))
        force = bool(call.data.get("force", False))
        include_none = bool(call.data.get("include_none", True))
        correlation_id = str(call.data.get("correlation_id", "") or "").strip() or None
        await coordinator.async_build_target_options_scaffold(
            dry_run=dry_run,
            force=force,
            include_none=include_none,
            correlation_id=correlation_id,
        )

    async def _service_run_auto_select_scaffold(call: ServiceCall) -> None:
        dry_run = bool(call.data.get("dry_run", True))
        force = bool(call.data.get("force", False))
        sync_options_if_missing = bool(call.data.get("sync_options_if_missing", False))
        include_none = bool(call.data.get("include_none", True))
        correlation_id = str(call.data.get("correlation_id", "") or "").strip() or None
        await coordinator.async_run_auto_select_scaffold(
            dry_run=dry_run,
            force=force,
            sync_options_if_missing=sync_options_if_missing,
            include_none=include_none,
            correlation_id=correlation_id,
        )

    async def _service_run_metadata_resolver_scaffold(call: ServiceCall) -> None:
        dry_run = bool(call.data.get("dry_run", True))
        force = bool(call.data.get("force", False))
        correlation_id = str(call.data.get("correlation_id", "") or "").strip() or None
        await coordinator.async_run_metadata_resolver_scaffold(
            dry_run=dry_run,
            force=force,
            correlation_id=correlation_id,
        )

    async def _service_run_metadata_trial_bridge_scaffold(call: ServiceCall) -> None:
        window_id = str(call.data.get("window_id", "") or "").strip()
        reason = str(call.data.get("reason", "") or "").strip()
        resolver_dry_run = bool(call.data.get("resolver_dry_run", True))
        trial_dry_run = bool(call.data.get("trial_dry_run", True))
        force = bool(call.data.get("force", False))
        expected_target = str(call.data.get("expected_target", "") or "").strip() or None
        expected_route = str(call.data.get("expected_route", "") or "").strip() or None
        expected_meta_entity = str(call.data.get("expected_meta_entity", "") or "").strip() or None
        correlation_id = str(call.data.get("correlation_id", "") or "").strip() or None

        await coordinator.async_run_metadata_trial_bridge_scaffold(
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
        dry_run = bool(call.data.get("dry_run", True))
        force = bool(call.data.get("force", False))
        include_none = bool(call.data.get("include_none", True))
        correlation_id = str(call.data.get("correlation_id", "") or "").strip() or None
        await coordinator.async_cycle_active_target(
            dry_run=dry_run,
            force=force,
            include_none=include_none,
            correlation_id=correlation_id,
        )

    async def _service_restore_last_valid_target(call: ServiceCall) -> None:
        dry_run = bool(call.data.get("dry_run", True))
        force = bool(call.data.get("force", False))
        correlation_id = str(call.data.get("correlation_id", "") or "").strip() or None
        await coordinator.async_restore_last_valid_target(
            dry_run=dry_run,
            force=force,
            correlation_id=correlation_id,
        )

    async def _service_track_last_valid_target(call: ServiceCall) -> None:
        dry_run = bool(call.data.get("dry_run", True))
        force = bool(call.data.get("force", False))
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
        dry_run = bool(call.data.get("dry_run", True))
        delta = call.data.get("delta")
        await coordinator.async_execute_control_center_input(
            input_event=input_event,
            correlation_id=correlation_id,
            target_hint=target_hint,
            dry_run=dry_run,
            delta=delta,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_REBUILD_REGISTRY):
        hass.services.async_register(DOMAIN, SERVICE_REBUILD_REGISTRY, _service_rebuild_registry)
    if not hass.services.has_service(DOMAIN, SERVICE_VALIDATE_CONTRACTS):
        hass.services.async_register(DOMAIN, SERVICE_VALIDATE_CONTRACTS, _service_validate_contracts)
    if not hass.services.has_service(DOMAIN, SERVICE_DUMP_ROUTE_TRACE):
        hass.services.async_register(DOMAIN, SERVICE_DUMP_ROUTE_TRACE, _service_dump_route_trace)
    if not hass.services.has_service(DOMAIN, SERVICE_SET_WRITE_AUTHORITY):
        hass.services.async_register(DOMAIN, SERVICE_SET_WRITE_AUTHORITY, _service_set_write_authority)
    if not hass.services.has_service(DOMAIN, SERVICE_ROUTE_WRITE_TRIAL):
        hass.services.async_register(DOMAIN, SERVICE_ROUTE_WRITE_TRIAL, _service_route_write_trial)
    if not hass.services.has_service(DOMAIN, SERVICE_METADATA_WRITE_TRIAL):
        hass.services.async_register(DOMAIN, SERVICE_METADATA_WRITE_TRIAL, _service_metadata_write_trial)
    if not hass.services.has_service(DOMAIN, SERVICE_RUN_P3_S01_SEQUENCE):
        hass.services.async_register(DOMAIN, SERVICE_RUN_P3_S01_SEQUENCE, _service_run_p3_s01_sequence)
    if not hass.services.has_service(DOMAIN, SERVICE_RUN_P3_S02_SEQUENCE):
        hass.services.async_register(DOMAIN, SERVICE_RUN_P3_S02_SEQUENCE, _service_run_p3_s02_sequence)
    if not hass.services.has_service(DOMAIN, SERVICE_VALIDATE_METADATA_PREP):
        hass.services.async_register(DOMAIN, SERVICE_VALIDATE_METADATA_PREP, _service_validate_metadata_prep)
    if not hass.services.has_service(DOMAIN, SERVICE_VALIDATE_METADATA_POLICY):
        hass.services.async_register(DOMAIN, SERVICE_VALIDATE_METADATA_POLICY, _service_validate_metadata_policy)
    if not hass.services.has_service(DOMAIN, SERVICE_RUN_P3_S03_SEQUENCE):
        hass.services.async_register(DOMAIN, SERVICE_RUN_P3_S03_SEQUENCE, _service_run_p3_s03_sequence)
    if not hass.services.has_service(DOMAIN, SERVICE_RUN_P5_S02_SEQUENCE):
        hass.services.async_register(DOMAIN, SERVICE_RUN_P5_S02_SEQUENCE, _service_run_p5_s02_sequence)
    if not hass.services.has_service(DOMAIN, SERVICE_VALIDATE_CAPABILITY_PROFILE):
        hass.services.async_register(DOMAIN, SERVICE_VALIDATE_CAPABILITY_PROFILE, _service_validate_capability_profile)
    if not hass.services.has_service(DOMAIN, SERVICE_RUN_F4_S01_SEQUENCE):
        hass.services.async_register(DOMAIN, SERVICE_RUN_F4_S01_SEQUENCE, _service_run_f4_s01_sequence)
    if not hass.services.has_service(DOMAIN, SERVICE_VALIDATE_ACTION_CATALOG):
        hass.services.async_register(DOMAIN, SERVICE_VALIDATE_ACTION_CATALOG, _service_validate_action_catalog)
    if not hass.services.has_service(DOMAIN, SERVICE_RUN_F4_S02_SEQUENCE):
        hass.services.async_register(DOMAIN, SERVICE_RUN_F4_S02_SEQUENCE, _service_run_f4_s02_sequence)
    if not hass.services.has_service(DOMAIN, SERVICE_VALIDATE_CROSSFADE_BALANCE):
        hass.services.async_register(DOMAIN, SERVICE_VALIDATE_CROSSFADE_BALANCE, _service_validate_crossfade_balance)
    if not hass.services.has_service(DOMAIN, SERVICE_RUN_F4_S03_SEQUENCE):
        hass.services.async_register(DOMAIN, SERVICE_RUN_F4_S03_SEQUENCE, _service_run_f4_s03_sequence)
    if not hass.services.has_service(DOMAIN, SERVICE_SET_CONTROL_CENTER_SETTINGS):
        hass.services.async_register(
            DOMAIN,
            SERVICE_SET_CONTROL_CENTER_SETTINGS,
            _service_set_control_center_settings,
        )
    if not hass.services.has_service(DOMAIN, SERVICE_EXECUTE_CONTROL_CENTER_INPUT):
        hass.services.async_register(
            DOMAIN,
            SERVICE_EXECUTE_CONTROL_CENTER_INPUT,
            _service_execute_control_center_input,
        )
    if not hass.services.has_service(DOMAIN, SERVICE_VALIDATE_SCHEDULER):
        hass.services.async_register(DOMAIN, SERVICE_VALIDATE_SCHEDULER, _service_validate_scheduler)
    if not hass.services.has_service(DOMAIN, SERVICE_RUN_SCHEDULER_CHOICE):
        hass.services.async_register(DOMAIN, SERVICE_RUN_SCHEDULER_CHOICE, _service_run_scheduler_choice)
    if not hass.services.has_service(DOMAIN, SERVICE_APPLY_SCHEDULER_CHOICE):
        hass.services.async_register(DOMAIN, SERVICE_APPLY_SCHEDULER_CHOICE, _service_apply_scheduler_choice)
    if not hass.services.has_service(DOMAIN, SERVICE_BUILD_TARGET_OPTIONS_SCAFFOLD):
        hass.services.async_register(
            DOMAIN,
            SERVICE_BUILD_TARGET_OPTIONS_SCAFFOLD,
            _service_build_target_options_scaffold,
        )
    if not hass.services.has_service(DOMAIN, SERVICE_RUN_AUTO_SELECT_SCAFFOLD):
        hass.services.async_register(
            DOMAIN,
            SERVICE_RUN_AUTO_SELECT_SCAFFOLD,
            _service_run_auto_select_scaffold,
        )
    if not hass.services.has_service(DOMAIN, SERVICE_RUN_METADATA_RESOLVER_SCAFFOLD):
        hass.services.async_register(
            DOMAIN,
            SERVICE_RUN_METADATA_RESOLVER_SCAFFOLD,
            _service_run_metadata_resolver_scaffold,
        )
    if not hass.services.has_service(DOMAIN, SERVICE_RUN_METADATA_TRIAL_BRIDGE_SCAFFOLD):
        hass.services.async_register(
            DOMAIN,
            SERVICE_RUN_METADATA_TRIAL_BRIDGE_SCAFFOLD,
            _service_run_metadata_trial_bridge_scaffold,
        )
    if not hass.services.has_service(DOMAIN, SERVICE_CYCLE_ACTIVE_TARGET):
        hass.services.async_register(DOMAIN, SERVICE_CYCLE_ACTIVE_TARGET, _service_cycle_active_target)
    if not hass.services.has_service(DOMAIN, SERVICE_RESTORE_LAST_VALID_TARGET):
        hass.services.async_register(
            DOMAIN,
            SERVICE_RESTORE_LAST_VALID_TARGET,
            _service_restore_last_valid_target,
        )
    if not hass.services.has_service(DOMAIN, SERVICE_TRACK_LAST_VALID_TARGET):
        hass.services.async_register(
            DOMAIN,
            SERVICE_TRACK_LAST_VALID_TARGET,
            _service_track_last_valid_target,
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
            if hass.services.has_service(DOMAIN, SERVICE_REBUILD_REGISTRY):
                hass.services.async_remove(DOMAIN, SERVICE_REBUILD_REGISTRY)
            if hass.services.has_service(DOMAIN, SERVICE_VALIDATE_CONTRACTS):
                hass.services.async_remove(DOMAIN, SERVICE_VALIDATE_CONTRACTS)
            if hass.services.has_service(DOMAIN, SERVICE_DUMP_ROUTE_TRACE):
                hass.services.async_remove(DOMAIN, SERVICE_DUMP_ROUTE_TRACE)
            if hass.services.has_service(DOMAIN, SERVICE_SET_WRITE_AUTHORITY):
                hass.services.async_remove(DOMAIN, SERVICE_SET_WRITE_AUTHORITY)
            if hass.services.has_service(DOMAIN, SERVICE_ROUTE_WRITE_TRIAL):
                hass.services.async_remove(DOMAIN, SERVICE_ROUTE_WRITE_TRIAL)
            if hass.services.has_service(DOMAIN, SERVICE_METADATA_WRITE_TRIAL):
                hass.services.async_remove(DOMAIN, SERVICE_METADATA_WRITE_TRIAL)
            if hass.services.has_service(DOMAIN, SERVICE_RUN_P3_S01_SEQUENCE):
                hass.services.async_remove(DOMAIN, SERVICE_RUN_P3_S01_SEQUENCE)
            if hass.services.has_service(DOMAIN, SERVICE_RUN_P3_S02_SEQUENCE):
                hass.services.async_remove(DOMAIN, SERVICE_RUN_P3_S02_SEQUENCE)
            if hass.services.has_service(DOMAIN, SERVICE_VALIDATE_METADATA_PREP):
                hass.services.async_remove(DOMAIN, SERVICE_VALIDATE_METADATA_PREP)
            if hass.services.has_service(DOMAIN, SERVICE_VALIDATE_METADATA_POLICY):
                hass.services.async_remove(DOMAIN, SERVICE_VALIDATE_METADATA_POLICY)
            if hass.services.has_service(DOMAIN, SERVICE_RUN_P3_S03_SEQUENCE):
                hass.services.async_remove(DOMAIN, SERVICE_RUN_P3_S03_SEQUENCE)
            if hass.services.has_service(DOMAIN, SERVICE_RUN_P5_S02_SEQUENCE):
                hass.services.async_remove(DOMAIN, SERVICE_RUN_P5_S02_SEQUENCE)
            if hass.services.has_service(DOMAIN, SERVICE_VALIDATE_CAPABILITY_PROFILE):
                hass.services.async_remove(DOMAIN, SERVICE_VALIDATE_CAPABILITY_PROFILE)
            if hass.services.has_service(DOMAIN, SERVICE_RUN_F4_S01_SEQUENCE):
                hass.services.async_remove(DOMAIN, SERVICE_RUN_F4_S01_SEQUENCE)
            if hass.services.has_service(DOMAIN, SERVICE_VALIDATE_ACTION_CATALOG):
                hass.services.async_remove(DOMAIN, SERVICE_VALIDATE_ACTION_CATALOG)
            if hass.services.has_service(DOMAIN, SERVICE_RUN_F4_S02_SEQUENCE):
                hass.services.async_remove(DOMAIN, SERVICE_RUN_F4_S02_SEQUENCE)
            if hass.services.has_service(DOMAIN, SERVICE_VALIDATE_CROSSFADE_BALANCE):
                hass.services.async_remove(DOMAIN, SERVICE_VALIDATE_CROSSFADE_BALANCE)
            if hass.services.has_service(DOMAIN, SERVICE_RUN_F4_S03_SEQUENCE):
                hass.services.async_remove(DOMAIN, SERVICE_RUN_F4_S03_SEQUENCE)
            if hass.services.has_service(DOMAIN, SERVICE_SET_CONTROL_CENTER_SETTINGS):
                hass.services.async_remove(DOMAIN, SERVICE_SET_CONTROL_CENTER_SETTINGS)
            if hass.services.has_service(DOMAIN, SERVICE_EXECUTE_CONTROL_CENTER_INPUT):
                hass.services.async_remove(DOMAIN, SERVICE_EXECUTE_CONTROL_CENTER_INPUT)
            if hass.services.has_service(DOMAIN, SERVICE_VALIDATE_SCHEDULER):
                hass.services.async_remove(DOMAIN, SERVICE_VALIDATE_SCHEDULER)
            if hass.services.has_service(DOMAIN, SERVICE_RUN_SCHEDULER_CHOICE):
                hass.services.async_remove(DOMAIN, SERVICE_RUN_SCHEDULER_CHOICE)
            if hass.services.has_service(DOMAIN, SERVICE_APPLY_SCHEDULER_CHOICE):
                hass.services.async_remove(DOMAIN, SERVICE_APPLY_SCHEDULER_CHOICE)
            if hass.services.has_service(DOMAIN, SERVICE_BUILD_TARGET_OPTIONS_SCAFFOLD):
                hass.services.async_remove(DOMAIN, SERVICE_BUILD_TARGET_OPTIONS_SCAFFOLD)
            if hass.services.has_service(DOMAIN, SERVICE_RUN_AUTO_SELECT_SCAFFOLD):
                hass.services.async_remove(DOMAIN, SERVICE_RUN_AUTO_SELECT_SCAFFOLD)
            if hass.services.has_service(DOMAIN, SERVICE_RUN_METADATA_RESOLVER_SCAFFOLD):
                hass.services.async_remove(DOMAIN, SERVICE_RUN_METADATA_RESOLVER_SCAFFOLD)
            if hass.services.has_service(DOMAIN, SERVICE_RUN_METADATA_TRIAL_BRIDGE_SCAFFOLD):
                hass.services.async_remove(DOMAIN, SERVICE_RUN_METADATA_TRIAL_BRIDGE_SCAFFOLD)
            if hass.services.has_service(DOMAIN, SERVICE_CYCLE_ACTIVE_TARGET):
                hass.services.async_remove(DOMAIN, SERVICE_CYCLE_ACTIVE_TARGET)
            if hass.services.has_service(DOMAIN, SERVICE_RESTORE_LAST_VALID_TARGET):
                hass.services.async_remove(DOMAIN, SERVICE_RESTORE_LAST_VALID_TARGET)
            if hass.services.has_service(DOMAIN, SERVICE_TRACK_LAST_VALID_TARGET):
                hass.services.async_remove(DOMAIN, SERVICE_TRACK_LAST_VALID_TARGET)
    return unload_ok
