# Description: Constants for Spectra LS custom integration shadow parity, Phase 3 guarded routing write-path controls, Phase 4 diagnostics scaffolding (F4-S01/F4-S03), Phase 5 metadata trial contract service, and Phase 6 control-center settings/execution contracts.
# Version: 2026.04.22.14
# Last updated: 2026-04-22

from __future__ import annotations

from typing import Any, Mapping

from homeassistant.const import Platform

DOMAIN = "spectra_ls"

SERVICE_REBUILD_REGISTRY = "rebuild_registry"
SERVICE_VALIDATE_CONTRACTS = "validate_contracts"
SERVICE_DUMP_ROUTE_TRACE = "dump_route_trace"
SERVICE_SET_WRITE_AUTHORITY = "set_write_authority"
SERVICE_ROUTE_WRITE_TRIAL = "route_write_trial"
SERVICE_METADATA_WRITE_TRIAL = "metadata_write_trial"
SERVICE_RUN_P3_S01_SEQUENCE = "run_p3_s01_sequence"
SERVICE_RUN_P3_S02_SEQUENCE = "run_p3_s02_sequence"
SERVICE_VALIDATE_METADATA_PREP = "validate_metadata_prep"
SERVICE_RUN_P5_S02_SEQUENCE = "run_p5_s02_sequence"
SERVICE_RUN_P3_S03_SEQUENCE = "run_p3_s03_sequence"
SERVICE_VALIDATE_CAPABILITY_PROFILE = "validate_capability_profile"
SERVICE_RUN_F4_S01_SEQUENCE = "run_f4_s01_sequence"
SERVICE_VALIDATE_ACTION_CATALOG = "validate_action_catalog"
SERVICE_RUN_F4_S02_SEQUENCE = "run_f4_s02_sequence"
SERVICE_VALIDATE_CROSSFADE_BALANCE = "validate_crossfade_balance"
SERVICE_RUN_F4_S03_SEQUENCE = "run_f4_s03_sequence"
SERVICE_SET_CONTROL_CENTER_SETTINGS = "set_control_center_settings"
SERVICE_EXECUTE_CONTROL_CENTER_INPUT = "execute_control_center_input"

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
LEGACY_ACTIVE_META_ENTITY = "sensor.ma_active_meta_entity"
LEGACY_NOW_PLAYING_ENTITY = "sensor.now_playing_entity"
LEGACY_NOW_PLAYING_STATE = "sensor.now_playing_state"
LEGACY_NOW_PLAYING_TITLE = "sensor.now_playing_title"
LEGACY_META_CANDIDATES = "sensor.ma_meta_candidates"
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

OPT_READ_ONLY_MODE = "read_only_mode"
OPT_ENCODER_TURN_ACTION = "encoder_turn_action"
OPT_ENCODER_PRESS_ACTION = "encoder_press_action"
OPT_ENCODER_LONG_PRESS_ACTION = "encoder_long_press_action"
OPT_BUTTON_1_SCENE = "button_1_scene"
OPT_BUTTON_2_SCENE = "button_2_scene"
OPT_BUTTON_3_SCENE = "button_3_scene"
OPT_BUTTON_4_SCENE = "button_4_scene"

CONTROL_CENTER_ACTIONS: tuple[str, ...] = (
    "volume",
    "brightness",
    "target_cycle",
    "source_cycle",
)

CONTROL_CENTER_PRESS_ACTIONS: tuple[str, ...] = (
    "play_pause",
    "mute_toggle",
    "scene_quick_trigger",
    "no_op",
)

CONTROL_CENTER_DEFAULTS: dict[str, Any] = {
    OPT_READ_ONLY_MODE: True,
    OPT_ENCODER_TURN_ACTION: "volume",
    OPT_ENCODER_PRESS_ACTION: "scene_quick_trigger",
    OPT_ENCODER_LONG_PRESS_ACTION: "no_op",
    OPT_BUTTON_1_SCENE: "scene.none",
    OPT_BUTTON_2_SCENE: "scene.none",
    OPT_BUTTON_3_SCENE: "scene.none",
    OPT_BUTTON_4_SCENE: "scene.none",
}

CONTROL_CENTER_INPUT_EVENTS: tuple[str, ...] = (
    "encoder_turn",
    "encoder_press",
    "encoder_long_press",
    "button_1",
    "button_2",
    "button_3",
    "button_4",
)


def normalize_control_center_settings(raw_options: Mapping[str, Any] | None) -> dict[str, Any]:
    """Return normalized P6 control-center settings with safe defaults."""
    options = dict(CONTROL_CENTER_DEFAULTS)
    if raw_options is None:
        return options

    raw_read_only = raw_options.get(OPT_READ_ONLY_MODE)
    if isinstance(raw_read_only, bool):
        options[OPT_READ_ONLY_MODE] = raw_read_only

    turn_action = str(raw_options.get(OPT_ENCODER_TURN_ACTION, options[OPT_ENCODER_TURN_ACTION]) or "").strip()
    if turn_action in CONTROL_CENTER_ACTIONS:
        options[OPT_ENCODER_TURN_ACTION] = turn_action

    press_action = str(raw_options.get(OPT_ENCODER_PRESS_ACTION, options[OPT_ENCODER_PRESS_ACTION]) or "").strip()
    if press_action in CONTROL_CENTER_PRESS_ACTIONS:
        options[OPT_ENCODER_PRESS_ACTION] = press_action

    long_press_action = str(
        raw_options.get(OPT_ENCODER_LONG_PRESS_ACTION, options[OPT_ENCODER_LONG_PRESS_ACTION]) or ""
    ).strip()
    if long_press_action in CONTROL_CENTER_PRESS_ACTIONS:
        options[OPT_ENCODER_LONG_PRESS_ACTION] = long_press_action

    for key in (OPT_BUTTON_1_SCENE, OPT_BUTTON_2_SCENE, OPT_BUTTON_3_SCENE, OPT_BUTTON_4_SCENE):
        scene_value = str(raw_options.get(key, options[key]) or "").strip()
        normalized_scene = scene_value.lower()
        if normalized_scene in {"", "none", "scene.none"}:
            options[key] = "scene.none"
            continue

        options[key] = scene_value if scene_value.startswith("scene.") else "scene.none"

    return options
