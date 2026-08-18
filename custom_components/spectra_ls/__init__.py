# Description: Spectra LS custom integration setup for shadow parity, Phase 3 guarded routing write-path services, Phase 4 diagnostics scaffolding services (F4-S01/F4-S03), Phase 5 metadata trial contract service wiring, and Phase 6 control-center settings/execution services including bounded startup auto-recovery scheduling and selection-ownership migration services with hardened authority-contract response service support.
# Version: 2026.08.18.1
# Last updated: 2026-08-18
# PARITY DIRECTIVE: Behavior/contract edits must include same-slice two-track parity review and version-metadata review (runtime + component).

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.core import SupportsResponse
from homeassistant.core import callback
from .const import (
    BLE_REMOTE_COMPANY_ID,
    BLE_REMOTE_EVENT_MAP,
    BLE_REMOTE_MAGIC,
    BLE_REMOTE_PROTO_VERSION,
    CONTROL_CENTER_DEFAULTS,
    DOMAIN,
    OPT_DEFAULT_WRITE_AUTHORITY_MODE,
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
    WRITE_AUTH_COMPONENT,
    SERVICE_RUN_SCHEDULER_CHOICE,
    SERVICE_APPLY_SCHEDULER_CHOICE,
    SERVICE_BUILD_TARGET_OPTIONS_SCAFFOLD,
    SERVICE_RUN_METADATA_RESOLVER_SCAFFOLD,
    SERVICE_RUN_METADATA_TRIAL_BRIDGE_SCAFFOLD,
    SERVICE_RUN_AUTO_SELECT_SCAFFOLD,
    SERVICE_CYCLE_ACTIVE_TARGET,
    SERVICE_RESTORE_LAST_VALID_TARGET,
    SERVICE_TRACK_LAST_VALID_TARGET,
    SERVICE_SET_ACTIVE_TARGET,
    SERVICE_SET_METADATA_OVERRIDE,
    SERVICE_SET_METADATA_PROVIDER_PACKET,
)
from .coordinator import SpectraLsShadowCoordinator
from .payload_surface_fabric import PayloadSurfaceFabric
from .service_registry import build_service_registrations

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
    SERVICE_SET_ACTIVE_TARGET,
    SERVICE_SET_METADATA_OVERRIDE,
    SERVICE_SET_METADATA_PROVIDER_PACKET,
)


def _build_authority_snapshot_summary(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Build compact authority-related snapshot summary for service consumers."""
    route_trace = PayloadSurfaceFabric.dict_surface(snapshot, "route_trace")
    contract_validation = PayloadSurfaceFabric.dict_surface(snapshot, "contract_validation")
    cutover_prep_validation = PayloadSurfaceFabric.dict_surface(snapshot, "cutover_prep_validation")

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
    route_trace = PayloadSurfaceFabric.dict_surface(snapshot, "route_trace")
    contract_validation = PayloadSurfaceFabric.dict_surface(snapshot, "contract_validation")
    host_gate = PayloadSurfaceFabric.dict_surface(snapshot, "host_control_cutover_gate")
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
    ble_remote_seen_seq: dict[str, int] = {}
    ble_adv_seen_count = 0
    ble_adv_with_manufacturer_data_count = 0

    @callback
    def _async_ble_remote_event(service_info: Any, _change: Any) -> None:
        """Parse Spectra remote BLE advertisement packets and dispatch input events."""
        nonlocal ble_adv_seen_count, ble_adv_with_manufacturer_data_count
        try:
            ble_adv_seen_count += 1
            if ble_adv_seen_count == 1:
                _LOGGER.warning("BLE callback live: first advertisement observed")
            elif ble_adv_seen_count % 500 == 0:
                _LOGGER.info(
                    "BLE callback heartbeat: adv_seen=%s manufacturer_seen=%s",
                    ble_adv_seen_count,
                    ble_adv_with_manufacturer_data_count,
                )

            manufacturer_data = getattr(service_info, "manufacturer_data", None)
            if not isinstance(manufacturer_data, dict):
                return
            ble_adv_with_manufacturer_data_count += 1
            raw_payload = manufacturer_data.get(BLE_REMOTE_COMPANY_ID)
            if raw_payload is None:
                return
            payload = bytes(raw_payload)
            if len(payload) < 6:
                _LOGGER.warning("BLE remote drop: short payload len=%s", len(payload))
                return
            if payload[0:2] != BLE_REMOTE_MAGIC:
                _LOGGER.warning("BLE remote drop: bad magic payload=%s", payload.hex())
                return
            if int(payload[2]) != BLE_REMOTE_PROTO_VERSION:
                _LOGGER.warning(
                    "BLE remote drop: unsupported proto=%s expected=%s",
                    int(payload[2]),
                    BLE_REMOTE_PROTO_VERSION,
                )
                return

            event_code = int(payload[3])
            input_event = BLE_REMOTE_EVENT_MAP.get(event_code)
            if not input_event:
                _LOGGER.warning("BLE remote drop: unknown event_code=%s", event_code)
                return

            delta_raw = int(payload[4])
            delta = delta_raw - 256 if delta_raw > 127 else delta_raw
            seq = int(payload[5])

            address = str(getattr(service_info, "address", "") or "unknown").upper()
            if ble_remote_seen_seq.get(address) == seq:
                return
            ble_remote_seen_seq[address] = seq

            correlation_id = f"ble-remote-{address.replace(':', '').lower()}-{seq}"
            task_kwargs: dict[str, Any] = {
                "input_event": input_event,
                "correlation_id": correlation_id,
                "target_hint": None,
                "dry_run": False,
                "delta": delta if input_event == "encoder_turn" else None,
            }
            _LOGGER.info(
                "BLE remote event: addr=%s seq=%s event=%s delta=%s",
                address,
                seq,
                input_event,
                delta,
            )
            hass.async_create_task(coordinator.async_execute_control_center_input(**task_kwargs))
        except Exception:
            _LOGGER.debug("Ignoring malformed BLE remote advertisement payload", exc_info=True)

    ble_unsubs: list[Any] = []
    try:
        ble_unsubs.append(
            bluetooth.async_register_callback(
                hass,
                _async_ble_remote_event,
                {},
                bluetooth.BluetoothScanningMode.ACTIVE,
            )
        )
    except Exception:
        _LOGGER.warning(
            "Unable to register ACTIVE BLE remote callback for %s",
            entry.entry_id,
            exc_info=True,
        )

    try:
        ble_unsubs.append(
            bluetooth.async_register_callback(
                hass,
                _async_ble_remote_event,
                {},
                bluetooth.BluetoothScanningMode.PASSIVE,
            )
        )
    except Exception:
        _LOGGER.warning(
            "Unable to register PASSIVE BLE remote callback for %s",
            entry.entry_id,
            exc_info=True,
        )

    if ble_unsubs:
        hass.data[DOMAIN][f"{entry.entry_id}_ble_unsub"] = ble_unsubs

    async def _handle_options_update(hass: HomeAssistant, updated_entry: ConfigEntry) -> None:
        coordinator_obj: SpectraLsShadowCoordinator | None = hass.data.get(DOMAIN, {}).get(updated_entry.entry_id)
        if coordinator_obj is not None:
            coordinator_obj.apply_setup_entity_policy(updated_entry.options)
            await coordinator_obj.async_apply_control_center_settings(updated_entry.options)

    options_update_unsub = entry.add_update_listener(_handle_options_update)
    hass.data[DOMAIN][f"{entry.entry_id}_options_unsub"] = options_update_unsub

    def _default_authority_mode() -> str:
        _ = entry.options.get(OPT_DEFAULT_WRITE_AUTHORITY_MODE, WRITE_AUTH_COMPONENT)
        return WRITE_AUTH_COMPONENT

    service_registrations = build_service_registrations(
        hass=hass,
        entry=entry,
        coordinator=coordinator,
        default_authority_mode=_default_authority_mode,
        coerce_bool=_coerce_bool,
        coerce_int=_coerce_int,
        build_authority_snapshot_summary=_build_authority_snapshot_summary,
        build_host_cutover_snapshot_summary=_build_host_cutover_snapshot_summary,
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
        ble_unsub = hass.data.get(DOMAIN, {}).pop(f"{entry.entry_id}_ble_unsub", None)
        if isinstance(ble_unsub, list):
            for unsub in ble_unsub:
                if callable(unsub):
                    unsub()
        elif callable(ble_unsub):
            ble_unsub()
        if not hass.data.get(DOMAIN):
            for service_name in _DOMAIN_SERVICE_NAMES:
                _remove_domain_service(hass, service_name)
    return unload_ok
