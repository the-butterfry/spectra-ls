# Description: Spectra LS custom integration setup for shadow parity and Phase 2 registry/router scaffold services.
# Version: 2026.04.19.2
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
    SERVICE_REBUILD_REGISTRY,
    SERVICE_VALIDATE_CONTRACTS,
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

    if not hass.services.has_service(DOMAIN, SERVICE_REBUILD_REGISTRY):
        hass.services.async_register(DOMAIN, SERVICE_REBUILD_REGISTRY, _service_rebuild_registry)
    if not hass.services.has_service(DOMAIN, SERVICE_VALIDATE_CONTRACTS):
        hass.services.async_register(DOMAIN, SERVICE_VALIDATE_CONTRACTS, _service_validate_contracts)
    if not hass.services.has_service(DOMAIN, SERVICE_DUMP_ROUTE_TRACE):
        hass.services.async_register(DOMAIN, SERVICE_DUMP_ROUTE_TRACE, _service_dump_route_trace)

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
    return unload_ok
