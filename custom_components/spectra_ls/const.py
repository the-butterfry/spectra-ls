# Description: Constants for Spectra LS custom integration shadow parity and Phase 3 guarded routing write-path controls.
# Version: 2026.04.19.5
# Last updated: 2026-04-19

from __future__ import annotations

from homeassistant.const import Platform

DOMAIN = "spectra_ls"

SERVICE_REBUILD_REGISTRY = "rebuild_registry"
SERVICE_VALIDATE_CONTRACTS = "validate_contracts"
SERVICE_DUMP_ROUTE_TRACE = "dump_route_trace"
SERVICE_SET_WRITE_AUTHORITY = "set_write_authority"
SERVICE_ROUTE_WRITE_TRIAL = "route_write_trial"
SERVICE_RUN_P3_S01_SEQUENCE = "run_p3_s01_sequence"
SERVICE_RUN_P3_S02_SEQUENCE = "run_p3_s02_sequence"

PLATFORMS: tuple[Platform, ...] = (
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
)

ENTRY_TITLE = "Spectra LS"
SINGLETON_UNIQUE_ID = "spectra_ls_shadow"

WRITE_AUTH_LEGACY = "legacy"
WRITE_AUTH_COMPONENT = "component"
WRITE_AUTH_ALLOWED: tuple[str, ...] = (
    WRITE_AUTH_LEGACY,
    WRITE_AUTH_COMPONENT,
)
WRITE_DEBOUNCE_SECONDS = 2.0

LEGACY_ACTIVE_TARGET = "sensor.ma_active_target"
LEGACY_ACTIVE_CONTROL_PATH = "sensor.ma_active_control_path"
LEGACY_ACTIVE_CONTROL_CAPABLE = "binary_sensor.ma_active_control_capable"
LEGACY_ACTIVE_TARGET_HELPER = "input_select.ma_active_target"
LEGACY_CONTROL_HOSTS = "sensor.ma_control_hosts"
LEGACY_CONTROL_HOST = "sensor.ma_control_host"
LEGACY_CONTROL_TARGETS = "sensor.ma_control_targets"
LEGACY_ROOMS_JSON = "sensor.spectra_ls_rooms_json"
LEGACY_ROOMS_RAW = "sensor.spectra_ls_rooms_raw"

LEGACY_SURFACES: dict[str, str] = {
    "active_target": LEGACY_ACTIVE_TARGET,
    "active_control_path": LEGACY_ACTIVE_CONTROL_PATH,
    "active_control_capable": LEGACY_ACTIVE_CONTROL_CAPABLE,
    "control_hosts": LEGACY_CONTROL_HOSTS,
}
