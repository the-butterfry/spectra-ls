# Description: Calibration persistence and scaling helpers for Spectra LS RP2040 firmware.
# Version: 2026.04.17.1
# Last updated: 2026-04-17

import json


def _empty_calibration():
    return {"internal": {}, "external": {}}


def load_calibration(calibration_enabled, calibration_file):
    if not calibration_enabled:
        return _empty_calibration()
    try:
        with open(calibration_file, "r") as handle:
            data = json.load(handle)
            if not isinstance(data, dict):
                return _empty_calibration()
            data.setdefault("internal", {})
            data.setdefault("external", {})
            return data
    except OSError:
        return _empty_calibration()


def save_calibration(data, calibration_enabled, calibration_file, debug_calibration_serial=False):
    if not calibration_enabled:
        return False
    try:
        with open(calibration_file, "w") as handle:
            json.dump(data, handle)
        return True
    except OSError as exc:
        err = getattr(exc, "errno", None)
        if debug_calibration_serial:
            print(f"Calibration save failed: {exc}")
        if err == 30:
            try:
                import storage  # type: ignore

                storage.remount("/", readonly=False)
                with open(calibration_file, "w") as handle:
                    json.dump(data, handle)
                if debug_calibration_serial:
                    print("Calibration save succeeded after remount")
                return True
            except Exception as remount_exc:
                if debug_calibration_serial:
                    print(f"Calibration remount failed: {remount_exc}")
        return False


def apply_calibration(raw_value, cal, calibration_enabled=True):
    if not calibration_enabled or not cal:
        return raw_value
    raw_min = cal.get("min")
    raw_max = cal.get("max")
    raw_mid = cal.get("mid")
    if raw_min is None or raw_max is None:
        return raw_value
    if raw_max == raw_min:
        return raw_value
    if raw_mid is None or raw_mid == raw_min or raw_mid == raw_max:
        scaled = int((raw_value - raw_min) * 65535 / (raw_max - raw_min))
    elif raw_value <= raw_mid:
        scaled = int((raw_value - raw_min) * 32768 / (raw_mid - raw_min))
    else:
        scaled = 32768 + int((raw_value - raw_mid) * 32767 / (raw_max - raw_mid))
    if scaled < 0:
        return 0
    if scaled > 65535:
        return 65535
    return scaled


def calibration_missing(calibration, name):
    for source in ("external", "internal"):
        cal = calibration.get(source, {}).get(name)
        if cal and cal.get("min") is not None and cal.get("max") is not None:
            return False
    return True
