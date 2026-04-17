# Description: Analog read/scale helpers for Spectra LS RP2040 firmware.
# Version: 2026.04.17.2
# Last updated: 2026-04-17
#
# RP FILE CONTRACT:
# - Owns analog helper math (read/scale/name/source helpers).
# - Must NOT persist calibration, manage triggers, or emit packets.


def clamp_value(value, min_value, max_value):
    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    return value


def scale_analog_value(
    calibrated_value,
    cal,
    source,
    analog_output_mode,
    analog_percent_range,
    analog_raw_max_default_external,
    analog_raw_max_default_internal,
):
    if analog_output_mode == "raw":
        return int(calibrated_value)
    if analog_output_mode == "percent":
        if cal and cal.get("min") is not None and cal.get("max") is not None:
            max_range = 65535
        else:
            if source == "external":
                max_range = analog_raw_max_default_external
            else:
                max_range = analog_raw_max_default_internal
        if max_range <= 0:
            return 0
        scaled = int(round((calibrated_value * analog_percent_range) / max_range))
        return clamp_value(scaled, 0, analog_percent_range)
    return int(calibrated_value)


def read_analog_raw(analog, samples, debug_global=False):
    try:
        if samples <= 1:
            return analog.value
        total = 0
        for _ in range(samples):
            total += analog.value
        return int(total / samples)
    except OSError as exc:
        if debug_global:
            print(f"Analog read failed: {exc}")
        return None


def analog_name_for_index(analog_inputs, idx):
    if idx < len(analog_inputs):
        return analog_inputs[idx].get("name", f"analog_{idx}")
    return f"analog_{idx}"


def analog_source_for_index(analog_inputs, idx):
    if idx < len(analog_inputs):
        return analog_inputs[idx].get("source", "external")
    return "external"


def is_pot_name(name):
    return "pot" in name
