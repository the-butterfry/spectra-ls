# Description: Spectra LS custom integration setup for shadow parity and Phase 3 guarded routing write-path services.
# Version: 2026.04.19.6
# Last updated: 2026-04-19

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.core import ServiceCall

from .const import (
    DOMAIN,
    PLATFORMS,
    SERVICE_DUMP_ROUTE_TRACE,
    SERVICE_RUN_P3_S01_SEQUENCE,
    SERVICE_RUN_P3_S02_SEQUENCE,
    SERVICE_ROUTE_WRITE_TRIAL,
    SERVICE_REBUILD_REGISTRY,
    SERVICE_SET_WRITE_AUTHORITY,
    SERVICE_VALIDATE_CONTRACTS,
    SERVICE_VALIDATE_METADATA_PREP,
    SERVICE_RUN_P3_S03_SEQUENCE,
)
from .coordinator import SpectraLsShadowCoordinator


async def async_setup(hass: HomeAssistant, _config: dict[str, Any]) -> bool:
    """Set up Spectra LS integration domain."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Spectra LS from config entry."""
    coordinator = SpectraLsShadowCoordinator(hass)
    await coordinator.async_setup()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

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

    async def _service_run_p3_s03_sequence(call: ServiceCall) -> None:
        mode = str(call.data.get("mode", "legacy"))
        reason = str(call.data.get("reason", ""))

        await coordinator.async_set_write_authority(mode=mode, reason=reason)
        await coordinator.async_rebuild_registry()
        await coordinator.async_validate_contracts()
        await coordinator.async_dump_route_trace()
        await coordinator.async_validate_selection_handoff()
        await coordinator.async_validate_metadata_prep()

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
    if not hass.services.has_service(DOMAIN, SERVICE_RUN_P3_S01_SEQUENCE):
        hass.services.async_register(DOMAIN, SERVICE_RUN_P3_S01_SEQUENCE, _service_run_p3_s01_sequence)
    if not hass.services.has_service(DOMAIN, SERVICE_RUN_P3_S02_SEQUENCE):
        hass.services.async_register(DOMAIN, SERVICE_RUN_P3_S02_SEQUENCE, _service_run_p3_s02_sequence)
    if not hass.services.has_service(DOMAIN, SERVICE_VALIDATE_METADATA_PREP):
        hass.services.async_register(DOMAIN, SERVICE_VALIDATE_METADATA_PREP, _service_validate_metadata_prep)
    if not hass.services.has_service(DOMAIN, SERVICE_RUN_P3_S03_SEQUENCE):
        hass.services.async_register(DOMAIN, SERVICE_RUN_P3_S03_SEQUENCE, _service_run_p3_s03_sequence)

    try:
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    except Exception:
        await coordinator.async_shutdown()
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
        raise

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Spectra LS config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator: SpectraLsShadowCoordinator | None = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
        if coordinator is not None:
            await coordinator.async_shutdown()
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
            if hass.services.has_service(DOMAIN, SERVICE_RUN_P3_S01_SEQUENCE):
                hass.services.async_remove(DOMAIN, SERVICE_RUN_P3_S01_SEQUENCE)
            if hass.services.has_service(DOMAIN, SERVICE_RUN_P3_S02_SEQUENCE):
                hass.services.async_remove(DOMAIN, SERVICE_RUN_P3_S02_SEQUENCE)
            if hass.services.has_service(DOMAIN, SERVICE_VALIDATE_METADATA_PREP):
                hass.services.async_remove(DOMAIN, SERVICE_VALIDATE_METADATA_PREP)
            if hass.services.has_service(DOMAIN, SERVICE_RUN_P3_S03_SEQUENCE):
                hass.services.async_remove(DOMAIN, SERVICE_RUN_P3_S03_SEQUENCE)
    return unload_ok
