## Description: RP2040 firmware for Spectra LS input scanning and UART event transport.
## Version: 2026.04.17.1
## Last updated: 2026-04-17

import time
import json
import board
import busio
import digitalio
import adafruit_ticks
from adafruit_debouncer import Debouncer
from adafruit_pcf8575 import PCF8575
try:
    from adafruit_seesaw.seesaw import Seesaw
    from adafruit_seesaw.rotaryio import IncrementalEncoder
    from adafruit_seesaw.digitalio import DigitalIO
except ImportError:
    Seesaw = None
    IncrementalEncoder = None
    DigitalIO = None

# -----------------------------
# Config (RP2040 Feather)
# -----------------------------

# ADC mode: "auto" (detect ADS1015 on I2C), "internal", or "external".
ADC_MODE = "external"
EXTERNAL_ADC_ADDRESS = 0x48
ANALOG_INPUTS = [
    {"name": "eq_bass_pot", "source": "external", "channel": 0, "event_id": 104, "enabled": True},
    {"name": "lighting_slider", "source": "external", "channel": 1, "event_id": 101, "enabled": True},
    {"name": "volume_pot", "source": "external", "channel": 2, "event_id": 102, "enabled": True},
    {"name": "eq_treble_pot", "source": "external", "channel": 3, "event_id": 106, "enabled": True},
    # EQ mid uses the RP2040 internal ADC (no extra ADC chip required).
    {"name": "eq_mid_pot", "source": "internal", "pin": board.A0, "event_id": 105, "enabled": True},
]
ANALOG_ENABLED = True
ANALOG_OUTPUT_MODE = "percent"  # "raw" or "percent"
ANALOG_PERCENT_RANGE = 100
ANALOG_RAW_MAX_DEFAULT_INTERNAL = 65535
ANALOG_RAW_MAX_DEFAULT_EXTERNAL = 26367
ANALOG_SAMPLES = 3  # oversample count per read
ANALOG_MEDIAN_WINDOW = 3  # default rolling median window size
ANALOG_MEDIAN_WINDOW_MAX = 5
ANALOG_MEDIAN_WINDOW_BY_NAME = {
    "volume_pot": 5,
}
ANALOG_FILTER_ALPHA_SLOW = 0.18  # default EMA when stable
ANALOG_FILTER_ALPHA_FAST = 0.55  # default EMA when moving quickly
ANALOG_FILTER_ALPHA_SLOW_BY_NAME = {
    "volume_pot": 0.28,
}
ANALOG_FILTER_ALPHA_FAST_BY_NAME = {
    "volume_pot": 0.55,
}
ANALOG_FILTER_FAST_THRESHOLD_PCT = 2.5  # default % of full-scale to switch to fast
ANALOG_FILTER_FAST_THRESHOLD_PCT_BY_NAME = {
    "volume_pot": 1.5,
}
ANALOG_RAW_MIN_CHANGE = 2  # min raw delta to reprocess
ANALOG_MIN_CHANGE = 2  # min output step before sending
ANALOG_MIN_CHANGE_BY_NAME = {
    "eq_bass_pot": 3,
    "eq_mid_pot": 3,
    "eq_treble_pot": 3,
    "volume_pot": 2,
}
ANALOG_IDLE_LOCK_MS = 0  # idle gate disabled
ANALOG_IDLE_MIN_CHANGE_BY_NAME = {}
ANALOG_CONFIRM_SAMPLES_BY_NAME = {}
ANALOG_CONFIRM_DELTA_BY_NAME = {}
ANALOG_SEND_INTERVAL_MS = 20  # 0 disables rate limiting
ANALOG_SNAP_ZERO_PCT = 0  # 0 disables snap
ANALOG_SNAP_FULL_PCT = 0  # 0 disables snap
ANALOG_SNAP_ZERO_PCT_BY_NAME = {
    "lighting_slider": 2,
    "eq_bass_pot": 3,
    "eq_mid_pot": 3,
    "eq_treble_pot": 3,
}
ANALOG_SNAP_FULL_PCT_BY_NAME = {
    "lighting_slider": 2,
    "eq_bass_pot": 3,
    "eq_mid_pot": 3,
    "eq_treble_pot": 3,
}
ANALOG_REVERSE_BY_NAME = {
    "eq_bass_pot": True,
    "eq_mid_pot": True,
    "eq_treble_pot": True,
}
CALIBRATION_ENABLED = True
AUTOCAL_ENABLED = False
AUTOCAL_TRIGGER_BUTTON = "home"  # PCF8575 button name (optional)
AUTOCAL_TRIGGER_ENCODER = "menu"  # Seesaw encoder name (optional)
AUTOCAL_TRIGGER_HOLD_MS = 1500
AUTOCAL_REQUIRE_RELEASE = True
AUTOCAL_COOLDOWN_MS = 5000
AUTOCAL_DURATION_MS = 12000
AUTOCAL_SETTLE_MS = 300
AUTOCAL_HEADROOM_PCT = 2
AUTOCAL_TRIM_PCT = 2
AUTOCAL_SAMPLE_LIMIT = 600
AUTOCAL_MIN_SAMPLES = 60
AUTOCAL_EDGE_PCT = 5
AUTOCAL_EDGE_MIN_SAMPLES = 8
AUTOCAL_EDGE_HEADROOM_PCT = 0
AUTOCAL_CHANNEL_NAMES = ("eq_bass_pot", "lighting_slider", "volume_pot", "eq_treble_pot", "eq_mid_pot")
AUTOCAL_BOOT_IF_MISSING = False
AUTOCAL_BOOT_CHANNEL_NAMES = ("lighting_slider",)
AUTOCAL_MIN_RANGE = 200
AUTOCAL_SUSPEND_OUTPUT = True
DEBUG_CALIBRATION_SERIAL = True

CALIBRATION_TRACKING_ENABLED = True
CALIBRATION_TRACKING_CHANNEL_NAMES = ("eq_bass_pot", "eq_mid_pot", "eq_treble_pot")
CALIBRATION_TRACKING_MIN_RANGE = 6000
CALIBRATION_TRACKING_SETTLE_MS = 0
CALIBRATION_TRACKING_DYNAMIC = True
CALIBRATION_TRACKING_EDGE_PCT = 5
CALIBRATION_TRACKING_EDGE_MIN_SAMPLES = 3

CALIBRATION_FILE = "/calibration.json"
CALIBRATION_LEGACY_MAP = {
    "volume_pot": "pot_a2",
    "lighting_slider": "slider_a1",
}

# Debug over UART (ESP-readable)
DEBUG_GLOBAL = True
DEBUG_UART = True
DEBUG_INTERVAL_MS = 1000
DEBUG_EVENT_ID = 0
DEBUG_ENCODERS = True
DEBUG_ENCODER_INTERVAL_MS = 500
DEBUG_ENCODER_SERIAL = True
DEBUG_ENCODER_SERIAL_INTERVAL_MS = 120
DEBUG_BUTTONS_SERIAL = False
DEBUG_ANALOG_SERIAL = True
DEBUG_ANALOG_STREAM_NAMES = ("volume_pot", "eq_bass_pot", "eq_mid_pot", "eq_treble_pot")
DEBUG_ANALOG_STREAM_INTERVAL_MS = 120
DEBUG_ANALOG_STREAM_MIN_DELTA = 2
DEBUG_SEESAW_INIT = True
DEBUG_PCF8575_INIT = True
DEBUG_I2C_SCAN = True
DEBUG_UART_IDLE_SUPPRESS_MS = 2000

# Seesaw (STEMMA QT) rotary encoders on I2C
# Update IDs to match the logical encoder slots in ESPHome.
I2C_SCAN_ON_BOOT = True
PCF8575_ADDRESSES = [0x20, 0x21]
PCF8575_PULLUPS = True
SEESAW_MENU_ADDRESS = 0x36
SEESAW_LIGHTING_ADDRESS = 0x37
SEESAW_ENCODERS = [
    {"address": SEESAW_MENU_ADDRESS, "delta_id": 2, "press_id": 21, "name": "menu"},
    {"address": SEESAW_LIGHTING_ADDRESS, "delta_id": 1, "press_id": 20, "name": "lighting"},
]
ENCODER_TRANSITIONS_PER_DETENT = 1
ENCODER_STEPS_PER_DETENT = 1

# -----------------------------
# Hardware setup
# -----------------------------

# I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

def i2c_try_lock(bus, timeout_ms=200):
    start = adafruit_ticks.ticks_ms()
    while not bus.try_lock():
        if adafruit_ticks.ticks_diff(adafruit_ticks.ticks_ms(), start) > timeout_ms:
            return False
    return True

if I2C_SCAN_ON_BOOT and DEBUG_I2C_SCAN:
    if i2c_try_lock(i2c, 200):
        try:
            addrs = i2c.scan()
            print("I2C scan:", [f"0x{addr:02X}" for addr in addrs])
        finally:
            i2c.unlock()
    else:
        print("I2C scan skipped: lock timeout")

def i2c_has_address(bus, address):
    if not i2c_try_lock(bus, 200):
        if DEBUG_GLOBAL:
            print("I2C address check skipped: lock timeout")
        return False
    try:
        return address in bus.scan()
    finally:
        bus.unlock()

def load_calibration():
    if not CALIBRATION_ENABLED:
        return {"internal": {}, "external": {}}
    try:
        with open(CALIBRATION_FILE, "r") as handle:
            data = json.load(handle)
            if not isinstance(data, dict):
                return {"internal": {}, "external": {}}
            data.setdefault("internal", {})
            data.setdefault("external", {})
            return data
    except OSError:
        return {"internal": {}, "external": {}}

def save_calibration(data):
    if not CALIBRATION_ENABLED:
        return False
    try:
        with open(CALIBRATION_FILE, "w") as handle:
            json.dump(data, handle)
        return True
    except OSError as exc:
        err = getattr(exc, "errno", None)
        if DEBUG_CALIBRATION_SERIAL:
            print(f"Calibration save failed: {exc}")
        if err == 30:
            try:
                import storage  # type: ignore

                storage.remount("/", readonly=False)
                with open(CALIBRATION_FILE, "w") as handle:
                    json.dump(data, handle)
                if DEBUG_CALIBRATION_SERIAL:
                    print("Calibration save succeeded after remount")
                return True
            except Exception as remount_exc:
                if DEBUG_CALIBRATION_SERIAL:
                    print(f"Calibration remount failed: {remount_exc}")
        return False

def apply_calibration(raw_value, cal):
    if not CALIBRATION_ENABLED or not cal:
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

def clamp_value(value, min_value, max_value):
    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    return value

def scale_analog_value(calibrated_value, cal, source):
    if ANALOG_OUTPUT_MODE == "raw":
        return int(calibrated_value)
    if ANALOG_OUTPUT_MODE == "percent":
        if cal and cal.get("min") is not None and cal.get("max") is not None:
            max_range = 65535
        else:
            max_range = ANALOG_RAW_MAX_DEFAULT_EXTERNAL if source == "external" else ANALOG_RAW_MAX_DEFAULT_INTERNAL
        if max_range <= 0:
            return 0
        scaled = int(round((calibrated_value * ANALOG_PERCENT_RANGE) / max_range))
        return clamp_value(scaled, 0, ANALOG_PERCENT_RANGE)
    return int(calibrated_value)

def read_analog_raw(analog, samples):
    try:
        if samples <= 1:
            return analog.value
        total = 0
        for _ in range(samples):
            total += analog.value
        return int(total / samples)
    except OSError as exc:
        if DEBUG_GLOBAL:
            print(f"Analog read failed: {exc}")
        return None

def analog_name_for_index(idx):
    if idx < len(analog_inputs):
        return analog_inputs[idx].get("name", f"analog_{idx}")
    return f"analog_{idx}"

def analog_source_for_index(idx):
    if idx < len(analog_inputs):
        return analog_inputs[idx].get("source", "external")
    return "external"

def build_autocal_indices(names_override=None):
    if not AUTOCAL_ENABLED:
        return []
    if names_override:
        names = set(names_override)
    elif AUTOCAL_CHANNEL_NAMES:
        names = set(AUTOCAL_CHANNEL_NAMES)
    else:
        names = None
    indices = []
    for idx in range(len(analog_inputs)):
        if not analog_inputs[idx].get("enabled", True):
            continue
        name = analog_name_for_index(idx)
        if names and name not in names:
            continue
        indices.append(idx)
    return indices

def _ads_channel(module, index):
    if module is None:
        return None
    return getattr(module, f"P{index}", None)

# PCF8575 for buttons (optional)
pcf = None
pcf_addr = None
for addr in PCF8575_ADDRESSES:
    if i2c_has_address(i2c, addr):
        try:
            pcf = PCF8575(i2c, address=addr)
            pcf_addr = addr
            break
        except Exception as exc:
            if DEBUG_PCF8575_INIT:
                print(f"PCF8575 init failed at 0x{addr:02X}: {exc}")
            pcf = None
            pcf_addr = None
if pcf is None:
    if DEBUG_PCF8575_INIT:
        print("PCF8575 not found; button inputs disabled")

# Seesaw rotary encoders (STEMMA QT)
seesaw_encoders = []
if SEESAW_ENCODERS and Seesaw is None:
    if DEBUG_SEESAW_INIT:
        print("Seesaw library missing: add adafruit_seesaw.mpy + adafruit_seesaw/ to CIRCUITPY/lib")
elif SEESAW_ENCODERS:
    for idx, cfg in enumerate(SEESAW_ENCODERS):
        addr = cfg.get("address")
        if addr is None:
            continue
        if not i2c_has_address(i2c, addr):
            continue
        try:
            ss = Seesaw(i2c, addr=addr)
            encoder = IncrementalEncoder(ss)
            button = DigitalIO(ss, 24)
            button.switch_to_input(pull=digitalio.Pull.UP)
            deb = Debouncer(lambda b=button: not b.value)
            seesaw_encoders.append(
                {
                    "cfg": cfg,
                    "encoder": encoder,
                    "button": button,
                    "deb": deb,
                    "pos": encoder.position,
                    "accum": 0,
                    "idx": idx,
                    "last_dbg_ms": adafruit_ticks.ticks_ms(),
                }
            )
            if DEBUG_SEESAW_INIT:
                print(f"Seesaw encoder ready: {cfg.get('name','?')} @ 0x{addr:02X}")
        except Exception as exc:
            if DEBUG_SEESAW_INIT:
                print(f"Seesaw init failed at 0x{addr:02X}: {exc}")

# Analog inputs (ADS1015 external + optional internal ADC)
analog_inputs = []
calibration = load_calibration()
calibration.setdefault("internal", {})
calibration.setdefault("external", {})
ads = None
ADS = None
ADS1x15 = None
AnalogIn = None
external_analogs = {}
internal_analogs = {}
use_external_adc = False
external_adc_fail_count = 0
external_adc_disabled_until_ms = 0
EXTERNAL_ADC_FAIL_THRESHOLD = 3
EXTERNAL_ADC_DISABLE_MS = 2000

if ANALOG_ENABLED:
    external_required = any(
        cfg.get("enabled", True) and cfg.get("source") == "external" for cfg in ANALOG_INPUTS
    )
    internal_required = any(
        cfg.get("enabled", True) and cfg.get("source") == "internal" for cfg in ANALOG_INPUTS
    )

    ads_present = i2c_has_address(i2c, EXTERNAL_ADC_ADDRESS)
    if external_required and ADC_MODE == "external" and not ads_present:
        if DEBUG_GLOBAL:
            print(
                f"ADS1015 not found at 0x{EXTERNAL_ADC_ADDRESS:02X}. External inputs disabled;"
                " internal inputs/buttons will continue."
            )

    use_external_adc = external_required and (ADC_MODE == "external" or (ADC_MODE == "auto" and ads_present))

    if use_external_adc:
        try:
            from adafruit_ads1x15.analog_in import AnalogIn  # type: ignore
            import adafruit_ads1x15.ads1015 as ADS  # type: ignore
            import adafruit_ads1x15.ads1x15 as ADS1x15  # type: ignore
        except ImportError as exc:
            if ADC_MODE == "external":
                raise RuntimeError("ADS1015 libraries not found. Install in /lib or set ADC_MODE = 'internal'.") from exc
            if DEBUG_GLOBAL:
                print("ADS1015 libraries not found; falling back to internal ADC.")
            use_external_adc = False

    if use_external_adc:
        ads = ADS.ADS1015(i2c, address=EXTERNAL_ADC_ADDRESS)
        try:
            ads.gain = 1
        except AttributeError:
            pass

        channels = []
        for idx in range(4):
            ch = _ads_channel(ADS, idx)
            if ch is None:
                ch = _ads_channel(ADS1x15, idx)
            if ch is None:
                ch = idx
            channels.append(ch)

        for cfg in ANALOG_INPUTS:
            if not cfg.get("enabled", True) or cfg.get("source") != "external":
                continue
            ch = cfg.get("channel", 0)
            if ch not in external_analogs:
                external_analogs[ch] = AnalogIn(ads, channels[ch])

    if internal_required:
        import analogio

        for cfg in ANALOG_INPUTS:
            if not cfg.get("enabled", True) or cfg.get("source") != "internal":
                continue
            pin = cfg.get("pin")
            if pin is None:
                continue
            if pin not in internal_analogs:
                internal_analogs[pin] = analogio.AnalogIn(pin)

    for cfg in ANALOG_INPUTS:
        if not cfg.get("enabled", True):
            continue
        source = cfg.get("source")
        analog = None
        if source == "external":
            if not use_external_adc:
                continue
            analog = external_analogs.get(cfg.get("channel", 0))
        elif source == "internal":
            analog = internal_analogs.get(cfg.get("pin"))
        if analog is None:
            continue
        entry = {
            "name": cfg.get("name", "analog"),
            "source": source,
            "analog": analog,
            "event_id": cfg.get("event_id"),
            "enabled": True,
        }
        if source == "external":
            entry["channel"] = cfg.get("channel", 0)
        analog_inputs.append(entry)

def _reinit_external_adc():
    global ads, external_analogs, external_adc_fail_count
    if not use_external_adc or AnalogIn is None or ADS is None or ADS1x15 is None:
        return False
    if not i2c_has_address(i2c, EXTERNAL_ADC_ADDRESS):
        return False
    try:
        ads = ADS.ADS1015(i2c, address=EXTERNAL_ADC_ADDRESS)
        try:
            ads.gain = 1
        except AttributeError:
            pass
        channels = []
        for idx in range(4):
            ch = _ads_channel(ADS, idx)
            if ch is None:
                ch = _ads_channel(ADS1x15, idx)
            if ch is None:
                ch = idx
            channels.append(ch)
        external_analogs = {}
        for entry in analog_inputs:
            if entry.get("source") != "external":
                continue
            ch = entry.get("channel", 0)
            external_analogs[ch] = AnalogIn(ads, channels[ch])
            entry["analog"] = external_analogs[ch]
        external_adc_fail_count = 0
        if DEBUG_GLOBAL:
            print("ADS1015 reinitialized")
        return True
    except Exception as exc:
        if DEBUG_GLOBAL:
            print(f"ADS1015 reinit failed: {exc}")
        return False

autocal_active = False
autocal_channel_indices = []
autocal_channel_pos = 0
autocal_min = None
autocal_max = None
autocal_raw_min = None
autocal_raw_max = None
autocal_samples = []
autocal_start_ms = 0
autocal_source = None
autocal_hold_start_ms = None
autocal_triggered = False
autocal_cooldown_until = 0
autocal_armed = True

def autocal_current_index():
    if not autocal_channel_indices or autocal_channel_pos >= len(autocal_channel_indices):
        return None
    return autocal_channel_indices[autocal_channel_pos]

def autocal_begin_channel():
    global autocal_min, autocal_max, autocal_raw_min, autocal_raw_max, autocal_samples, autocal_start_ms, autocal_source
    autocal_min = None
    autocal_max = None
    autocal_raw_min = None
    autocal_raw_max = None
    autocal_samples = []
    autocal_start_ms = adafruit_ticks.ticks_ms()
    idx = autocal_current_index()
    if idx is not None:
        name = analog_name_for_index(idx)
        autocal_source = analog_source_for_index(idx)
        if DEBUG_CALIBRATION_SERIAL:
            print(f"Auto-cal start: {name} ({autocal_source})")

def autocal_finish_channel():
    global autocal_active, autocal_channel_pos, autocal_min, autocal_max, autocal_source
    idx = autocal_current_index()
    if idx is None:
        autocal_active = False
        return
    name = analog_name_for_index(idx)
    source = autocal_source or analog_source_for_index(idx)
    sample_count = len(autocal_samples)
    if sample_count < AUTOCAL_MIN_SAMPLES:
        if DEBUG_CALIBRATION_SERIAL:
            print(f"Auto-cal failed: {name} not enough samples ({sample_count})")
    else:
        sorted_samples = sorted(autocal_samples)
        trim = int(sample_count * AUTOCAL_TRIM_PCT / 100)
        if trim * 2 >= sample_count:
            trim = 0
        trimmed = sorted_samples[trim: sample_count - trim]
        autocal_min = trimmed[0]
        autocal_max = trimmed[-1]
        if DEBUG_CALIBRATION_SERIAL:
            print(
                f"Auto-cal samples={sample_count} raw_min={autocal_raw_min} raw_max={autocal_raw_max} "
                f"trimmed_min={autocal_min} trimmed_max={autocal_max} trim={AUTOCAL_TRIM_PCT}%"
            )
        span = int(autocal_max - autocal_min)
        if span < AUTOCAL_MIN_RANGE:
            if DEBUG_CALIBRATION_SERIAL:
                print(f"Auto-cal failed: {name} span too small ({span})")
        else:
            edge_span = max(1, int(span * AUTOCAL_EDGE_PCT / 100))
            high_threshold = autocal_max - edge_span
            low_threshold = autocal_min + edge_span
            high_hits = 0
            low_hits = 0
            for sample in autocal_samples:
                if sample >= high_threshold:
                    high_hits += 1
                if sample <= low_threshold:
                    low_hits += 1
            headroom_high = AUTOCAL_HEADROOM_PCT
            headroom_low = 0
            if high_hits < AUTOCAL_EDGE_MIN_SAMPLES:
                headroom_high += AUTOCAL_EDGE_HEADROOM_PCT
            if low_hits < AUTOCAL_EDGE_MIN_SAMPLES:
                headroom_low += AUTOCAL_EDGE_HEADROOM_PCT
            pad_high = int(span * headroom_high / 100)
            pad_low = int(span * headroom_low / 100)
            adjusted_min = min(autocal_min + pad_low, autocal_max - 1)
            adjusted_max = max(adjusted_min + 1, autocal_max - pad_high)
            calibration.setdefault(source, {})
            calibration[source][name] = {
                "min": int(adjusted_min),
                "max": int(adjusted_max),
            }
            saved = save_calibration(calibration)
            if DEBUG_CALIBRATION_SERIAL:
                if saved:
                    print(
                        f"Auto-cal saved: {name} min={int(adjusted_min)} max={int(adjusted_max)} "
                        f"(edge_hits low={low_hits} high={high_hits} headroom low={headroom_low}% high={headroom_high}%)"
                    )
                else:
                    print(
                        f"Auto-cal computed (not saved): {name} min={int(adjusted_min)} max={int(adjusted_max)} "
                        f"(edge_hits low={low_hits} high={high_hits} headroom low={headroom_low}% high={headroom_high}%)"
                    )

    autocal_channel_pos += 1
    if autocal_channel_pos >= len(autocal_channel_indices):
        autocal_active = False
        if DEBUG_CALIBRATION_SERIAL:
            print("Auto-cal complete")
        return
    autocal_begin_channel()

def start_autocalibration(names_override=None):
    global autocal_active, autocal_channel_indices, autocal_channel_pos
    if not AUTOCAL_ENABLED:
        return
    autocal_channel_indices = build_autocal_indices(names_override)
    if not autocal_channel_indices:
        if DEBUG_CALIBRATION_SERIAL:
            print("Auto-cal skipped: no enabled channels")
        return
    autocal_channel_pos = 0
    autocal_active = True
    autocal_begin_channel()

def update_autocal_trigger(pressed):
    global autocal_hold_start_ms, autocal_triggered, autocal_cooldown_until, autocal_armed
    if not AUTOCAL_ENABLED or autocal_active:
        return
    now = adafruit_ticks.ticks_ms()
    if adafruit_ticks.ticks_diff(now, autocal_cooldown_until) < 0:
        return
    if pressed:
        if AUTOCAL_REQUIRE_RELEASE and not autocal_armed:
            return
        if autocal_hold_start_ms is None:
            autocal_hold_start_ms = now
        elif not autocal_triggered and adafruit_ticks.ticks_diff(now, autocal_hold_start_ms) >= AUTOCAL_TRIGGER_HOLD_MS:
            autocal_triggered = True
            autocal_armed = False
            if DEBUG_CALIBRATION_SERIAL:
                print("Auto-cal trigger detected")
            start_autocalibration()
            autocal_cooldown_until = (now + AUTOCAL_COOLDOWN_MS) & 0xFFFFFFFF
    else:
        autocal_hold_start_ms = None
        autocal_triggered = False
        if AUTOCAL_REQUIRE_RELEASE:
            autocal_armed = True

def calibration_missing(name):
    for source in ("external", "internal"):
        cal = calibration.get(source, {}).get(name)
        if cal and cal.get("min") is not None and cal.get("max") is not None:
            return False
    return True

if AUTOCAL_ENABLED and AUTOCAL_BOOT_IF_MISSING:
    boot_names = AUTOCAL_BOOT_CHANNEL_NAMES or AUTOCAL_CHANNEL_NAMES
    missing = [name for name in (boot_names or []) if calibration_missing(name)]
    if missing:
        if DEBUG_CALIBRATION_SERIAL:
            print(f"Boot auto-cal: {', '.join(missing)}")
        start_autocalibration(missing)

tracking_indices = []
tracking_min = {}
tracking_max = {}
tracking_min_ms = {}
tracking_max_ms = {}
tracking_low_hits = {}
tracking_high_hits = {}
tracking_active = False

def init_calibration_tracking():
    global tracking_active, tracking_indices
    if not CALIBRATION_TRACKING_ENABLED:
        return
    names = set(CALIBRATION_TRACKING_CHANNEL_NAMES) if CALIBRATION_TRACKING_CHANNEL_NAMES else None
    for idx in range(len(analog_inputs)):
        if not analog_inputs[idx].get("enabled", True):
            continue
        name = analog_name_for_index(idx)
        if names and name not in names:
            continue
        if calibration_missing(name):
            tracking_indices.append(idx)
    tracking_active = bool(tracking_indices)
    if tracking_active and DEBUG_CALIBRATION_SERIAL:
        names = ", ".join(analog_name_for_index(idx) for idx in tracking_indices)
        print(f"Calibration tracking enabled for: {names}")

def update_calibration_tracking(idx, raw):
    global tracking_active
    if not tracking_active or idx not in tracking_indices:
        return
    now = adafruit_ticks.ticks_ms()
    min_val = tracking_min.get(idx)
    max_val = tracking_max.get(idx)
    min_changed = False
    max_changed = False
    if min_val is None or raw < min_val:
        tracking_min[idx] = raw
        tracking_min_ms[idx] = now
        min_val = raw
        min_changed = True
    if max_val is None or raw > max_val:
        tracking_max[idx] = raw
        tracking_max_ms[idx] = now
        max_val = raw
        max_changed = True
    if min_changed:
        tracking_low_hits[idx] = 0
    if max_changed:
        tracking_high_hits[idx] = 0
    if min_val is None or max_val is None:
        return
    span = (max_val - min_val)
    if span < CALIBRATION_TRACKING_MIN_RANGE:
        return
    edge_span = max(1, int(span * CALIBRATION_TRACKING_EDGE_PCT / 100))
    if raw <= (min_val + edge_span):
        tracking_low_hits[idx] = tracking_low_hits.get(idx, 0) + 1
    if raw >= (max_val - edge_span):
        tracking_high_hits[idx] = tracking_high_hits.get(idx, 0) + 1
    if tracking_low_hits.get(idx, 0) < CALIBRATION_TRACKING_EDGE_MIN_SAMPLES:
        return
    if tracking_high_hits.get(idx, 0) < CALIBRATION_TRACKING_EDGE_MIN_SAMPLES:
        return
    if adafruit_ticks.ticks_diff(now, tracking_min_ms.get(idx, now)) < CALIBRATION_TRACKING_SETTLE_MS:
        return
    if adafruit_ticks.ticks_diff(now, tracking_max_ms.get(idx, now)) < CALIBRATION_TRACKING_SETTLE_MS:
        return
    name = analog_name_for_index(idx)
    source = analog_source_for_index(idx)
    calibration.setdefault(source, {})
    calibration[source][name] = {"min": int(min_val), "max": int(max_val)}
    saved = save_calibration(calibration)
    if saved:
        print(f"Calibration saved: {name} min={int(min_val)} max={int(max_val)}")
    else:
        print(f"Calibration NOT saved (USB mounted): {name} min={int(min_val)} max={int(max_val)}")
    if DEBUG_CALIBRATION_SERIAL:
        print(f"Calibration tracking saved: {name} min={int(min_val)} max={int(max_val)}")
    tracking_indices.remove(idx)
    tracking_active = bool(tracking_indices)

def get_tracking_calibration(idx, source):
    if not CALIBRATION_TRACKING_DYNAMIC:
        return None
    min_val = tracking_min.get(idx)
    max_val = tracking_max.get(idx)
    if min_val is None or max_val is None:
        return None
    if (max_val - min_val) < CALIBRATION_TRACKING_MIN_RANGE:
        return None
    if tracking_low_hits.get(idx, 0) < CALIBRATION_TRACKING_EDGE_MIN_SAMPLES:
        return None
    if tracking_high_hits.get(idx, 0) < CALIBRATION_TRACKING_EDGE_MIN_SAMPLES:
        return None
    return {"min": int(min_val), "max": int(max_val)}

init_calibration_tracking()

# UART to ESP32-S3
uart = busio.UART(board.TX, board.RX, baudrate=115200)

# -----------------------------
# Button setup
# -----------------------------
# Map PCF8575 pins to logical button names
BUTTON_PINS = {
    "room": 0,
    "source": 1,
    "back": 2,
    "home": 3,
    "prev": 4,
    "play": 5,
    "next": 6,
    "mute": 7,
    "select": 8,
}

BUTTON_EVENT_IDS = {
    "room": 31,
    "source": 35,
    "back": 36,
    "prev": 34,
    "play": 32,
    "next": 33,
    "mute": 22,
    "select": 37,
}

# -----------------------------
# Phase B v-next input contract
# -----------------------------
# Reserved event IDs from v-next notes (Phase A): 120-129
MODE_SELECTOR_EVENT_ID = 120      # value: 0-4
CONTROL_CLASS_EVENT_ID = 121      # value: 0-2
MODE_NEXT_ITEM_EVENT_ID = 122     # momentary button value: 1/0
MODE_PREV_ITEM_EVENT_ID = 123     # momentary button value: 1/0
MODE_CONFIRM_EVENT_ID = 124       # momentary button value: 1/0

# Discrete selector wiring on spare PCF8575 inputs.
# One-hot expected: exactly one active-low pin selected maps to index 0-4.
MODE_SELECTOR_PINS = [9, 10, 11, 12, 13]

# 3-way control class selector on two pins (active-low):
# (True, False) -> 0 (Auto)
# (False, True) -> 1 (Primary Hardware)
# (True, True) -> 2 (Room Hardware)
# (False, False) -> invalid / disconnected (no emit)
CONTROL_CLASS_PINS = [14, 15]
CONTROL_CLASS_MAP = {
    (True, False): 0,
    (False, True): 1,
    (True, True): 2,
}

# Mirror existing physical buttons into v-next mode-navigation events.
MODE_NAV_BUTTON_MIRROR = {
    "next": MODE_NEXT_ITEM_EVENT_ID,
    "back": MODE_PREV_ITEM_EVENT_ID,
    "select": MODE_CONFIRM_EVENT_ID,
}

# Create debouncers
buttons = {}
mode_selector_inputs = []
control_class_inputs = []
if pcf is not None:
    for name, pin in BUTTON_PINS.items():
        p = pcf.get_pin(pin)
        try:
            if PCF8575_PULLUPS:
                p.switch_to_input(pull=digitalio.Pull.UP)
            else:
                p.switch_to_input()
        except NotImplementedError:
            p.direction = digitalio.Direction.INPUT
        buttons[name] = Debouncer(lambda p=p: not p.value)

    for idx, pin in enumerate(MODE_SELECTOR_PINS):
        p = pcf.get_pin(pin)
        try:
            if PCF8575_PULLUPS:
                p.switch_to_input(pull=digitalio.Pull.UP)
            else:
                p.switch_to_input()
        except NotImplementedError:
            p.direction = digitalio.Direction.INPUT
        mode_selector_inputs.append({"index": idx, "deb": Debouncer(lambda p=p: not p.value)})

    for pin in CONTROL_CLASS_PINS:
        p = pcf.get_pin(pin)
        try:
            if PCF8575_PULLUPS:
                p.switch_to_input(pull=digitalio.Pull.UP)
            else:
                p.switch_to_input()
        except NotImplementedError:
            p.direction = digitalio.Direction.INPUT
        control_class_inputs.append(Debouncer(lambda p=p: not p.value))

# -----------------------------
# Helper: send binary event to ESP32-S3
# -----------------------------
TYPE_BUTTON = 0x01
TYPE_ANALOG = 0x02
TYPE_ENCODER = 0x03
TYPE_DEBUG = 0xF0

def send_packet(event_type, event_id, value):
    global tx_len, last_activity_ms
    if event_id is None:
        return
    if not DEBUG_GLOBAL and event_type == TYPE_DEBUG:
        return
    ts = adafruit_ticks.ticks_ms() & 0xFFFFFFFF
    if tx_len + 10 > len(tx_buffer):
        _flush_tx()
    tx_buffer[tx_len] = 0xAA
    tx_buffer[tx_len + 1] = 0x55
    tx_buffer[tx_len + 2] = event_type & 0xFF
    tx_buffer[tx_len + 3] = event_id & 0xFF
    tx_buffer[tx_len + 4] = (ts >> 24) & 0xFF
    tx_buffer[tx_len + 5] = (ts >> 16) & 0xFF
    tx_buffer[tx_len + 6] = (ts >> 8) & 0xFF
    tx_buffer[tx_len + 7] = ts & 0xFF
    value &= 0xFFFF
    tx_buffer[tx_len + 8] = (value >> 8) & 0xFF
    tx_buffer[tx_len + 9] = value & 0xFF
    tx_len += 10
    if event_type != TYPE_DEBUG:
        last_activity_ms = ts

# -----------------------------
# Main loop
# -----------------------------
last_sent_values = [None for _ in range(len(analog_inputs))]
analog_filtered = [None for _ in range(len(analog_inputs))]
analog_history = [[] for _ in range(len(analog_inputs))]
analog_last_raw = [None for _ in range(len(analog_inputs))]
analog_last_send_ms = [None for _ in range(len(analog_inputs))]
analog_last_log_ms = [None for _ in range(len(analog_inputs))]
analog_last_log_value = [None for _ in range(len(analog_inputs))]
analog_pending_value = [None for _ in range(len(analog_inputs))]
analog_pending_count = [0 for _ in range(len(analog_inputs))]
autocal_trigger_pressed = False
debug_counter = 0
last_debug_ms = adafruit_ticks.ticks_ms()
last_activity_ms = 0
MAX_TX_BUFFER = 256
tx_buffer = bytearray(MAX_TX_BUFFER)
tx_len = 0

def _flush_tx():
    global tx_len
    if tx_len > 0:
        uart.write(tx_buffer[:tx_len])
        tx_len = 0

def _is_pot_name(name):
    return "pot" in name


def _decode_mode_selector(states):
    active_count = 0
    active_idx = None
    for idx, state in enumerate(states):
        if state:
            active_count += 1
            active_idx = idx
    if active_count == 1:
        return active_idx
    return None


def _decode_control_class(states):
    if len(states) != 2:
        return None
    return CONTROL_CLASS_MAP.get((states[0], states[1]))


while True:
    # Update Phase B selector/switch inputs and emit only on valid state transitions.
    for entry in mode_selector_inputs:
        entry["deb"].update()
    for deb in control_class_inputs:
        deb.update()

    mode_states = [entry["deb"].value for entry in mode_selector_inputs]
    control_states = [deb.value for deb in control_class_inputs]

    mode_selector_index = _decode_mode_selector(mode_states)
    control_class_index = _decode_control_class(control_states)

    if not hasattr(_decode_mode_selector, "last_index"):
        _decode_mode_selector.last_index = None
    if not hasattr(_decode_control_class, "last_index"):
        _decode_control_class.last_index = None

    if mode_selector_index is not None and mode_selector_index != _decode_mode_selector.last_index:
        _decode_mode_selector.last_index = mode_selector_index
        send_packet(TYPE_BUTTON, MODE_SELECTOR_EVENT_ID, mode_selector_index)
        if DEBUG_GLOBAL and DEBUG_BUTTONS_SERIAL:
            print(f"Mode selector -> {mode_selector_index} (id={MODE_SELECTOR_EVENT_ID})")

    if control_class_index is not None and control_class_index != _decode_control_class.last_index:
        _decode_control_class.last_index = control_class_index
        send_packet(TYPE_BUTTON, CONTROL_CLASS_EVENT_ID, control_class_index)
        if DEBUG_GLOBAL and DEBUG_BUTTONS_SERIAL:
            print(f"Control class -> {control_class_index} (id={CONTROL_CLASS_EVENT_ID})")

    # Update button debouncers
    for name, deb in buttons.items():
        deb.update()
        event_id = BUTTON_EVENT_IDS.get(name)
        mirror_id = MODE_NAV_BUTTON_MIRROR.get(name)
        if deb.fell:
            send_packet(TYPE_BUTTON, event_id, 1)
            if mirror_id is not None:
                send_packet(TYPE_BUTTON, mirror_id, 1)
            if DEBUG_GLOBAL and DEBUG_BUTTONS_SERIAL:
                print(f"Button {name} fell (id={event_id})")
        if deb.rose:
            send_packet(TYPE_BUTTON, event_id, 0)
            if mirror_id is not None:
                send_packet(TYPE_BUTTON, mirror_id, 0)
            if DEBUG_GLOBAL and DEBUG_BUTTONS_SERIAL:
                print(f"Button {name} rose (id={event_id})")

    # Read analog inputs (ADS1015 + internal ADC)
    for idx, analog_entry in enumerate(analog_inputs):
        if not analog_entry.get("enabled", True):
            continue
        analog = analog_entry["analog"]
        source = analog_entry.get("source", "external")
        name = analog_name_for_index(idx)
        now = adafruit_ticks.ticks_ms()
        if source == "external" and external_adc_disabled_until_ms:
            if adafruit_ticks.ticks_diff(now, external_adc_disabled_until_ms) < 0:
                continue
            if not _reinit_external_adc():
                external_adc_disabled_until_ms = (now + EXTERNAL_ADC_DISABLE_MS) & 0xFFFFFFFF
                continue
            external_adc_disabled_until_ms = 0
        raw = read_analog_raw(analog, ANALOG_SAMPLES)
        if raw is None:
            if source == "external":
                external_adc_fail_count += 1
                if external_adc_fail_count >= EXTERNAL_ADC_FAIL_THRESHOLD:
                    external_adc_disabled_until_ms = (now + EXTERNAL_ADC_DISABLE_MS) & 0xFFFFFFFF
                    if DEBUG_GLOBAL:
                        print("ADS1015 disabled temporarily after read errors")
            continue
        if source == "external":
            external_adc_fail_count = 0
        last_raw = analog_last_raw[idx]
        analog_last_raw[idx] = raw
        current_autocal_idx = autocal_current_index()
        if autocal_active and current_autocal_idx == idx:
            now = adafruit_ticks.ticks_ms()
            if adafruit_ticks.ticks_diff(now, autocal_start_ms) >= AUTOCAL_SETTLE_MS:
                autocal_samples.append(raw)
                if len(autocal_samples) > AUTOCAL_SAMPLE_LIMIT:
                    autocal_samples.pop(0)
                if autocal_raw_min is None or raw < autocal_raw_min:
                    autocal_raw_min = raw
                if autocal_raw_max is None or raw > autocal_raw_max:
                    autocal_raw_max = raw
            if adafruit_ticks.ticks_diff(now, autocal_start_ms) >= AUTOCAL_DURATION_MS:
                autocal_finish_channel()
                current_autocal_idx = autocal_current_index()
            if AUTOCAL_SUSPEND_OUTPUT and current_autocal_idx == idx:
                continue
        if (not autocal_active or current_autocal_idx != idx) and last_raw is not None and abs(raw - last_raw) < ANALOG_RAW_MIN_CHANGE:
            last_send = analog_last_send_ms[idx]
            if ANALOG_SEND_INTERVAL_MS and last_send is not None:
                now = adafruit_ticks.ticks_ms()
                if adafruit_ticks.ticks_diff(now, last_send) < ANALOG_SEND_INTERVAL_MS:
                    continue
        if not autocal_active:
            update_calibration_tracking(idx, raw)
        cal = calibration.get(source, {}).get(name)
        if cal is None:
            legacy = CALIBRATION_LEGACY_MAP.get(name)
            if legacy:
                cal = calibration.get(source, {}).get(legacy)
        if (cal is None or cal.get("min") is None or cal.get("max") is None):
            tracked = get_tracking_calibration(idx, source)
            if tracked is not None:
                cal = tracked
        event_id = analog_entry.get("event_id")
        history = analog_history[idx]
        history.append(raw)
        window = ANALOG_MEDIAN_WINDOW_BY_NAME.get(name, ANALOG_MEDIAN_WINDOW)
        if window > ANALOG_MEDIAN_WINDOW_MAX:
            window = ANALOG_MEDIAN_WINDOW_MAX
        if len(history) > window:
            history.pop(0)
        sorted_hist = sorted(history)
        median_raw = sorted_hist[len(sorted_hist) // 2] if sorted_hist else raw

        calibrated = apply_calibration(median_raw, cal)
        calibrated = clamp_value(calibrated, 0, 65535)
        previous = analog_filtered[idx]
        if previous is None:
            filtered = float(calibrated)
        else:
            diff = abs(calibrated - previous)
            threshold_pct = ANALOG_FILTER_FAST_THRESHOLD_PCT_BY_NAME.get(name, ANALOG_FILTER_FAST_THRESHOLD_PCT)
            threshold = (threshold_pct / 100.0) * 65535.0
            alpha_slow = ANALOG_FILTER_ALPHA_SLOW_BY_NAME.get(name, ANALOG_FILTER_ALPHA_SLOW)
            alpha_fast = ANALOG_FILTER_ALPHA_FAST_BY_NAME.get(name, ANALOG_FILTER_ALPHA_FAST)
            alpha = alpha_fast if diff >= threshold else alpha_slow
            filtered = previous + (alpha * (calibrated - previous))
        analog_filtered[idx] = filtered
        filtered_value = int(round(filtered))

        value = scale_analog_value(filtered_value, cal, source)
        if ANALOG_OUTPUT_MODE == "percent":
            snap_zero = ANALOG_SNAP_ZERO_PCT_BY_NAME.get(name, ANALOG_SNAP_ZERO_PCT)
            snap_full = ANALOG_SNAP_FULL_PCT_BY_NAME.get(name, ANALOG_SNAP_FULL_PCT)
            if snap_zero > 0 and value <= snap_zero:
                value = 0
            elif snap_full > 0 and value >= (ANALOG_PERCENT_RANGE - snap_full):
                value = ANALOG_PERCENT_RANGE
            if ANALOG_REVERSE_BY_NAME.get(name, False):
                value = ANALOG_PERCENT_RANGE - value
        last_sent = last_sent_values[idx]
        min_change = ANALOG_MIN_CHANGE_BY_NAME.get(name, ANALOG_MIN_CHANGE)
        idle_min_change = ANALOG_IDLE_MIN_CHANGE_BY_NAME.get(name)
        confirm_samples = ANALOG_CONFIRM_SAMPLES_BY_NAME.get(name, 0)
        confirm_delta = ANALOG_CONFIRM_DELTA_BY_NAME.get(name, 0)
        if last_sent is not None and idle_min_change is not None:
            last_send = analog_last_send_ms[idx]
            if last_send is not None:
                idle_ms = adafruit_ticks.ticks_diff(now, last_send)
                if idle_ms >= ANALOG_IDLE_LOCK_MS and abs(value - last_sent) < idle_min_change:
                    continue
        if last_sent is not None and abs(value - last_sent) < min_change:
            continue
        if confirm_samples and last_sent is not None:
            last_send = analog_last_send_ms[idx]
            idle_ms = 0
            if last_send is not None:
                idle_ms = adafruit_ticks.ticks_diff(now, last_send)
            if idle_ms >= ANALOG_IDLE_LOCK_MS:
                pending = analog_pending_value[idx]
                if pending is None or abs(value - pending) > confirm_delta:
                    analog_pending_value[idx] = value
                    analog_pending_count[idx] = 1
                    continue
                analog_pending_count[idx] += 1
                if analog_pending_count[idx] < confirm_samples:
                    continue
                analog_pending_value[idx] = None
                analog_pending_count[idx] = 0
        if ANALOG_SEND_INTERVAL_MS:
            now = adafruit_ticks.ticks_ms()
            last_send = analog_last_send_ms[idx]
            if last_send is not None and adafruit_ticks.ticks_diff(now, last_send) < ANALOG_SEND_INTERVAL_MS:
                continue
            analog_last_send_ms[idx] = now
        last_sent_values[idx] = value
        send_packet(TYPE_ANALOG, event_id, value)
        if DEBUG_GLOBAL and DEBUG_ANALOG_SERIAL and (not DEBUG_ANALOG_STREAM_NAMES or name in DEBUG_ANALOG_STREAM_NAMES):
            now = adafruit_ticks.ticks_ms()
            last_log_ms = analog_last_log_ms[idx]
            last_log_value = analog_last_log_value[idx]
            if last_log_ms is None or adafruit_ticks.ticks_diff(now, last_log_ms) >= DEBUG_ANALOG_STREAM_INTERVAL_MS:
                if last_log_value is None or abs(value - last_log_value) >= DEBUG_ANALOG_STREAM_MIN_DELTA:
                    analog_last_log_ms[idx] = now
                    analog_last_log_value[idx] = value
                    print(
                        f"Analog {name} raw={raw} median={median_raw} cal={calibrated} "
                        f"filt={filtered_value} out={value} id={event_id}"
                    )
        if DEBUG_GLOBAL and _is_pot_name(name) and name != "volume_pot":
            direction = "up" if (last_sent is None or value > last_sent) else "down" if value < last_sent else "hold"
            print(
                f"POT {name} {direction} raw={raw} median={median_raw} cal={calibrated} "
                f"filt={filtered_value} out={value} last={last_sent} id={event_id}"
            )

    # Read seesaw encoders (I2C)
    for enc in seesaw_encoders:
        cfg = enc["cfg"]
        enc["deb"].update()
        press_id = cfg.get("press_id")
        if cfg.get("name") == AUTOCAL_TRIGGER_ENCODER:
            autocal_trigger_pressed = autocal_trigger_pressed or enc["deb"].value
        if enc["deb"].rose:
            send_packet(TYPE_BUTTON, press_id, 1)
            if DEBUG_GLOBAL and DEBUG_ENCODER_SERIAL:
                now = adafruit_ticks.ticks_ms()
                last_serial_ms = enc.get("last_serial_ms")
                if last_serial_ms is None or adafruit_ticks.ticks_diff(now, last_serial_ms) >= DEBUG_ENCODER_SERIAL_INTERVAL_MS:
                    enc["last_serial_ms"] = now
                    print(f"Seesaw {cfg.get('name','?')} press")
        if enc["deb"].fell:
            send_packet(TYPE_BUTTON, press_id, 0)
            if DEBUG_GLOBAL and DEBUG_ENCODER_SERIAL:
                now = adafruit_ticks.ticks_ms()
                last_serial_ms = enc.get("last_serial_ms")
                if last_serial_ms is None or adafruit_ticks.ticks_diff(now, last_serial_ms) >= DEBUG_ENCODER_SERIAL_INTERVAL_MS:
                    enc["last_serial_ms"] = now
                    print(f"Seesaw {cfg.get('name','?')} release")

        pos = enc["encoder"].position
        delta = pos - enc["pos"]
        if delta != 0:
            enc["pos"] = pos
            if ENCODER_TRANSITIONS_PER_DETENT <= 1:
                step = int(delta) * ENCODER_STEPS_PER_DETENT
                if step != 0:
                    send_packet(TYPE_ENCODER, cfg.get("delta_id"), step)
                    if DEBUG_GLOBAL and DEBUG_ENCODER_SERIAL:
                        now = adafruit_ticks.ticks_ms()
                        last_serial_ms = enc.get("last_serial_ms")
                        if last_serial_ms is None or adafruit_ticks.ticks_diff(now, last_serial_ms) >= DEBUG_ENCODER_SERIAL_INTERVAL_MS:
                            enc["last_serial_ms"] = now
                            print(f"Seesaw {cfg.get('name','?')} delta={step} pos={pos}")
            else:
                enc["accum"] += int(delta)
                steps = int(enc["accum"] / ENCODER_TRANSITIONS_PER_DETENT)
                if steps != 0:
                    enc["accum"] -= steps * ENCODER_TRANSITIONS_PER_DETENT
                    step = steps * ENCODER_STEPS_PER_DETENT
                    if step != 0:
                        send_packet(TYPE_ENCODER, cfg.get("delta_id"), step)
                        if DEBUG_GLOBAL and DEBUG_ENCODER_SERIAL:
                            now = adafruit_ticks.ticks_ms()
                            last_serial_ms = enc.get("last_serial_ms")
                            if last_serial_ms is None or adafruit_ticks.ticks_diff(now, last_serial_ms) >= DEBUG_ENCODER_SERIAL_INTERVAL_MS:
                                enc["last_serial_ms"] = now
                                print(f"Seesaw {cfg.get('name','?')} delta={step} pos={pos}")

        if DEBUG_ENCODERS:
            now = adafruit_ticks.ticks_ms()
            if adafruit_ticks.ticks_diff(now, enc["last_dbg_ms"]) >= DEBUG_ENCODER_INTERVAL_MS:
                enc["last_dbg_ms"] = now
                dbg_id = 0x80 + (enc["idx"] & 0x0F)
                send_packet(TYPE_DEBUG, dbg_id, int(pos) & 0xFFFF)

    if DEBUG_UART:
        now = adafruit_ticks.ticks_ms()
        if last_activity_ms and adafruit_ticks.ticks_diff(now, last_activity_ms) > DEBUG_UART_IDLE_SUPPRESS_MS:
            pass
        elif DEBUG_GLOBAL and adafruit_ticks.ticks_diff(now, last_debug_ms) >= DEBUG_INTERVAL_MS:
            last_debug_ms = now
            debug_counter = (debug_counter + 1) & 0xFFFF
            send_packet(TYPE_DEBUG, DEBUG_EVENT_ID, debug_counter)

    if AUTOCAL_TRIGGER_BUTTON and AUTOCAL_TRIGGER_BUTTON in buttons:
        autocal_trigger_pressed = autocal_trigger_pressed or buttons[AUTOCAL_TRIGGER_BUTTON].value
    update_autocal_trigger(autocal_trigger_pressed)
    autocal_trigger_pressed = False

    _flush_tx()

    time.sleep(0.01)