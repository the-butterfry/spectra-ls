## Description: RP2040 firmware for Spectra LS input scanning and UART event transport.
## Version: 2026.04.26.13
## Last updated: 2026-04-26
#
# RP FILE CONTRACT:
# - Owns hardware initialization and main-loop orchestration only.
# - Delegates protocol framing to sls_protocol.py.
# - Delegates PCF input setup/decode to sls_inputs_pcf.py.
# - Delegates analog math to sls_analog.py.
# - Delegates calibration persistence to sls_calibration.py.
# - Delegates autocal/tracking runtime state to sls_calibration_runtime.py.

import time
import board
import busio
import digitalio
import adafruit_ticks
from adafruit_debouncer import Debouncer
from adafruit_pcf8575 import PCF8575
from sls_config import (
    BUTTON_PINS,
    BUTTON_EVENT_IDS,
    MODE_SELECTOR_EVENT_ID,
    CONTROL_CLASS_EVENT_ID,
    MODE_SELECTOR_PINS,
    CONTROL_CLASS_PINS,
    CONTROL_CLASS_MAP,
    MODE_NAV_BUTTON_MIRROR,
)
from sls_inputs_pcf import (
    setup_pcf_inputs,
    decode_mode_selector,
    decode_control_class,
)
from sls_protocol import (
    PacketWriter,
    TYPE_BUTTON,
    TYPE_ANALOG,
    TYPE_ENCODER,
    TYPE_DEBUG,
)
from sls_calibration import (
    load_calibration,
    save_calibration,
    apply_calibration,
    calibration_missing,
)
from sls_calibration_runtime import CalibrationRuntimeManager
from sls_analog import (
    clamp_value,
    scale_analog_value,
    read_analog_raw,
    analog_name_for_index,
    analog_source_for_index,
    is_pot_name,
)
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
ANALOG_MEDIAN_WINDOW_BY_NAME = {}
ANALOG_FILTER_ALPHA_SLOW = 0.18  # default EMA when stable
ANALOG_FILTER_ALPHA_FAST = 0.55  # default EMA when moving quickly
# KNOWN-GOOD BASELINE (2026-04-26): validated by operator traces for full 0-100 sweep
# and responsive small-movement behavior on volume + EQ path.
# If future tuning regresses feel/endpoints, restore this constant set first.
ANALOG_FILTER_ALPHA_SLOW_BY_NAME = {
    "eq_bass_pot": 0.28,
    "eq_mid_pot": 0.28,
    "eq_treble_pot": 0.28,
    "volume_pot": 0.30,
}
ANALOG_FILTER_ALPHA_FAST_BY_NAME = {}
ANALOG_FILTER_FAST_THRESHOLD_PCT = 2.5  # default % of full-scale to switch to fast
ANALOG_FILTER_FAST_THRESHOLD_PCT_BY_NAME = {}
ANALOG_RAW_MIN_CHANGE = 1  # min raw delta to reprocess
# Reset median history when a strong opposite-direction raw jump is detected.
# Applies to named pots only (volume + EQ) to keep tactile response consistent.
ANALOG_DIRECTION_RESET_RAW_DELTA = 1200
ANALOG_DIRECTION_FAST_WINDOW_SAMPLES = 3
ANALOG_TAIL_CUT_RAW_STABLE_DELTA = 120
ANALOG_TAIL_CUT_FILTER_DELTA = 900
ANALOG_TAIL_CUT_JUMP_RESET_DELTA = 900
ANALOG_TAIL_CUT_ENDPOINT_RAW_MAX = 320
ANALOG_TAIL_CUT_STABLE_SNAP_SAMPLES = 1
ANALOG_MIN_CHANGE = 2  # min output step before sending
ANALOG_MIN_CHANGE_BY_NAME = {
    "eq_bass_pot": 2,
    "eq_mid_pot": 2,
    "eq_treble_pot": 2,
    "volume_pot": 1,
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
# Treat near-zero tails as zero for named pots (volume + EQ) to stabilize endpoints
# without swallowing small intended movement at the floor.
ANALOG_POT_ASSUME_ZERO_MAX = 1
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
DEBUG_POT_DIRECTION_SERIAL = False
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
calibration = load_calibration(CALIBRATION_ENABLED, CALIBRATION_FILE)
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


def median_window_value(values):
    count = len(values)
    if count == 0:
        return 0
    if count == 1:
        return values[0]
    if count == 2:
        a = values[0]
        b = values[1]
        return a if a >= b else b
    if count == 3:
        a = values[0]
        b = values[1]
        c = values[2]
        if a > b:
            a, b = b, a
        if b > c:
            b, c = c, b
        if a > b:
            b = a
        return b
    if count == 4:
        ordered = sorted(values)
        return ordered[2]
    if count == 5:
        ordered = sorted(values)
        return ordered[2]
    ordered = sorted(values)
    return ordered[count // 2]

def build_analog_profiles():
    profiles = []
    for idx in range(len(analog_inputs)):
        name = analog_name_for_index(analog_inputs, idx)
        profile = {
            "name": name,
            "window": min(ANALOG_MEDIAN_WINDOW_BY_NAME.get(name, ANALOG_MEDIAN_WINDOW), ANALOG_MEDIAN_WINDOW_MAX),
            "threshold": (
                ANALOG_FILTER_FAST_THRESHOLD_PCT_BY_NAME.get(name, ANALOG_FILTER_FAST_THRESHOLD_PCT) / 100.0
            ) * 65535.0,
            "alpha_slow": ANALOG_FILTER_ALPHA_SLOW_BY_NAME.get(name, ANALOG_FILTER_ALPHA_SLOW),
            "alpha_fast": ANALOG_FILTER_ALPHA_FAST_BY_NAME.get(name, ANALOG_FILTER_ALPHA_FAST),
            "min_change": ANALOG_MIN_CHANGE_BY_NAME.get(name, ANALOG_MIN_CHANGE),
            "idle_min_change": ANALOG_IDLE_MIN_CHANGE_BY_NAME.get(name),
            "confirm_samples": ANALOG_CONFIRM_SAMPLES_BY_NAME.get(name, 0),
            "confirm_delta": ANALOG_CONFIRM_DELTA_BY_NAME.get(name, 0),
            "snap_zero": ANALOG_SNAP_ZERO_PCT_BY_NAME.get(name, ANALOG_SNAP_ZERO_PCT),
            "snap_full": ANALOG_SNAP_FULL_PCT_BY_NAME.get(name, ANALOG_SNAP_FULL_PCT),
            "reverse": ANALOG_REVERSE_BY_NAME.get(name, False),
            "debug_stream_enabled": (not DEBUG_ANALOG_STREAM_NAMES) or (name in DEBUG_ANALOG_STREAM_NAMES),
            "is_named_pot": is_pot_name(name),
        }
        profiles.append(profile)
    return profiles


def emit_button_state(event_id, mirror_id, pressed, button_name=None):
    value = 1 if pressed else 0
    send_packet(TYPE_BUTTON, event_id, value)
    if mirror_id is not None:
        send_packet(TYPE_BUTTON, mirror_id, value)
    if DEBUG_GLOBAL and DEBUG_BUTTONS_SERIAL and button_name is not None:
        edge = "fell" if pressed else "rose"
        print(f"Button {button_name} {edge} (id={event_id})")


def maybe_log_encoder_serial(enc, message):
    if not (DEBUG_GLOBAL and DEBUG_ENCODER_SERIAL):
        return
    now = adafruit_ticks.ticks_ms()
    last_serial_ms = enc.get("last_serial_ms")
    if last_serial_ms is None or adafruit_ticks.ticks_diff(now, last_serial_ms) >= DEBUG_ENCODER_SERIAL_INTERVAL_MS:
        enc["last_serial_ms"] = now
        print(message)


def maybe_log_analog_serial(idx, profile, name, raw, median_raw, calibrated, filtered_value, value, event_id):
    if not (DEBUG_GLOBAL and DEBUG_ANALOG_SERIAL and profile["debug_stream_enabled"]):
        return
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


def maybe_log_pot_direction(profile, name, raw, median_raw, calibrated, filtered_value, value, last_sent, event_id):
    if not (DEBUG_GLOBAL and DEBUG_POT_DIRECTION_SERIAL and profile["is_named_pot"]):
        return
    direction = "up" if (last_sent is None or value > last_sent) else "down" if value < last_sent else "hold"
    print(
        f"POT {name} {direction} raw={raw} median={median_raw} cal={calibrated} "
        f"filt={filtered_value} out={value} last={last_sent} id={event_id}"
    )


CAL_RUNTIME_CONFIG = {
    "AUTOCAL_ENABLED": AUTOCAL_ENABLED,
    "AUTOCAL_CHANNEL_NAMES": AUTOCAL_CHANNEL_NAMES,
    "AUTOCAL_TRIGGER_HOLD_MS": AUTOCAL_TRIGGER_HOLD_MS,
    "AUTOCAL_REQUIRE_RELEASE": AUTOCAL_REQUIRE_RELEASE,
    "AUTOCAL_COOLDOWN_MS": AUTOCAL_COOLDOWN_MS,
    "AUTOCAL_DURATION_MS": AUTOCAL_DURATION_MS,
    "AUTOCAL_SETTLE_MS": AUTOCAL_SETTLE_MS,
    "AUTOCAL_HEADROOM_PCT": AUTOCAL_HEADROOM_PCT,
    "AUTOCAL_TRIM_PCT": AUTOCAL_TRIM_PCT,
    "AUTOCAL_SAMPLE_LIMIT": AUTOCAL_SAMPLE_LIMIT,
    "AUTOCAL_MIN_SAMPLES": AUTOCAL_MIN_SAMPLES,
    "AUTOCAL_EDGE_PCT": AUTOCAL_EDGE_PCT,
    "AUTOCAL_EDGE_MIN_SAMPLES": AUTOCAL_EDGE_MIN_SAMPLES,
    "AUTOCAL_EDGE_HEADROOM_PCT": AUTOCAL_EDGE_HEADROOM_PCT,
    "AUTOCAL_BOOT_IF_MISSING": AUTOCAL_BOOT_IF_MISSING,
    "AUTOCAL_BOOT_CHANNEL_NAMES": AUTOCAL_BOOT_CHANNEL_NAMES,
    "AUTOCAL_MIN_RANGE": AUTOCAL_MIN_RANGE,
    "AUTOCAL_SUSPEND_OUTPUT": AUTOCAL_SUSPEND_OUTPUT,
    "CALIBRATION_ENABLED": CALIBRATION_ENABLED,
    "CALIBRATION_FILE": CALIBRATION_FILE,
    "CALIBRATION_TRACKING_ENABLED": CALIBRATION_TRACKING_ENABLED,
    "CALIBRATION_TRACKING_CHANNEL_NAMES": CALIBRATION_TRACKING_CHANNEL_NAMES,
    "CALIBRATION_TRACKING_MIN_RANGE": CALIBRATION_TRACKING_MIN_RANGE,
    "CALIBRATION_TRACKING_SETTLE_MS": CALIBRATION_TRACKING_SETTLE_MS,
    "CALIBRATION_TRACKING_DYNAMIC": CALIBRATION_TRACKING_DYNAMIC,
    "CALIBRATION_TRACKING_EDGE_PCT": CALIBRATION_TRACKING_EDGE_PCT,
    "CALIBRATION_TRACKING_EDGE_MIN_SAMPLES": CALIBRATION_TRACKING_EDGE_MIN_SAMPLES,
}

cal_runtime = CalibrationRuntimeManager(
    analog_inputs=analog_inputs,
    calibration=calibration,
    save_calibration=save_calibration,
    calibration_missing=calibration_missing,
    analog_name_for_index=analog_name_for_index,
    analog_source_for_index=analog_source_for_index,
    cfg=CAL_RUNTIME_CONFIG,
    ticks_ms=adafruit_ticks.ticks_ms,
    ticks_diff=adafruit_ticks.ticks_diff,
    debug_calibration_serial=DEBUG_CALIBRATION_SERIAL,
)
cal_runtime.maybe_boot_autocal()
cal_runtime.init_calibration_tracking()

# UART to ESP32-S3
uart = busio.UART(board.TX, board.RX, baudrate=115200)

# Create debouncers
buttons, mode_selector_inputs, control_class_inputs = setup_pcf_inputs(
    pcf,
    PCF8575_PULLUPS,
    BUTTON_PINS,
    MODE_SELECTOR_PINS,
    CONTROL_CLASS_PINS,
)

# -----------------------------
# Main loop
# -----------------------------
last_sent_values = [None for _ in range(len(analog_inputs))]
analog_filtered = [None for _ in range(len(analog_inputs))]
analog_history = [[] for _ in range(len(analog_inputs))]
analog_last_raw = [None for _ in range(len(analog_inputs))]
analog_last_raw_delta = [0 for _ in range(len(analog_inputs))]
analog_raw_stable_count = [0 for _ in range(len(analog_inputs))]
analog_fast_window_remaining = [0 for _ in range(len(analog_inputs))]
analog_last_send_ms = [None for _ in range(len(analog_inputs))]
analog_last_log_ms = [None for _ in range(len(analog_inputs))]
analog_last_log_value = [None for _ in range(len(analog_inputs))]
analog_pending_value = [None for _ in range(len(analog_inputs))]
analog_pending_count = [0 for _ in range(len(analog_inputs))]
autocal_trigger_pressed = False
debug_counter = 0
last_debug_ms = adafruit_ticks.ticks_ms()
analog_profiles = build_analog_profiles()
packet_writer = PacketWriter(uart, debug_enabled=DEBUG_GLOBAL, max_buffer=256)
send_packet = packet_writer.send_packet
flush_tx = packet_writer.flush
last_mode_selector_index = None
last_control_class_index = None

while True:
    # Update Phase B selector/switch inputs and emit only on valid state transitions.
    for entry in mode_selector_inputs:
        entry["deb"].update()
    for deb in control_class_inputs:
        deb.update()

    mode_states = [entry["deb"].value for entry in mode_selector_inputs]
    control_states = [deb.value for deb in control_class_inputs]

    mode_selector_index = decode_mode_selector(mode_states)
    control_class_index = decode_control_class(control_states, CONTROL_CLASS_MAP)

    if mode_selector_index is not None and mode_selector_index != last_mode_selector_index:
        last_mode_selector_index = mode_selector_index
        send_packet(TYPE_ANALOG, MODE_SELECTOR_EVENT_ID, mode_selector_index)
        if DEBUG_GLOBAL and DEBUG_BUTTONS_SERIAL:
            print(f"Mode selector -> {mode_selector_index} (id={MODE_SELECTOR_EVENT_ID})")

    if control_class_index is not None and control_class_index != last_control_class_index:
        last_control_class_index = control_class_index
        send_packet(TYPE_ANALOG, CONTROL_CLASS_EVENT_ID, control_class_index)
        if DEBUG_GLOBAL and DEBUG_BUTTONS_SERIAL:
            print(f"Control class -> {control_class_index} (id={CONTROL_CLASS_EVENT_ID})")

    # Update button debouncers
    for name, deb in buttons.items():
        deb.update()
        event_id = BUTTON_EVENT_IDS.get(name)
        mirror_id = MODE_NAV_BUTTON_MIRROR.get(name)
        if deb.fell:
            emit_button_state(event_id, mirror_id, True, name)
        if deb.rose:
            emit_button_state(event_id, mirror_id, False, name)

    # Read analog inputs (ADS1015 + internal ADC)
    for idx, analog_entry in enumerate(analog_inputs):
        if not analog_entry.get("enabled", True):
            continue
        analog = analog_entry["analog"]
        source = analog_entry.get("source", "external")
        profile = analog_profiles[idx]
        name = profile["name"]
        now = adafruit_ticks.ticks_ms()
        if source == "external" and external_adc_disabled_until_ms:
            if adafruit_ticks.ticks_diff(now, external_adc_disabled_until_ms) < 0:
                continue
            if not _reinit_external_adc():
                external_adc_disabled_until_ms = (now + EXTERNAL_ADC_DISABLE_MS) & 0xFFFFFFFF
                continue
            external_adc_disabled_until_ms = 0
        raw = read_analog_raw(analog, ANALOG_SAMPLES, DEBUG_GLOBAL)
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
        jump_snap_now = False
        if last_raw is not None and profile["is_named_pot"]:
            raw_delta = raw - last_raw
            if abs(raw_delta) >= ANALOG_TAIL_CUT_JUMP_RESET_DELTA:
                analog_history[idx].clear()
                analog_history[idx].append(raw)
            last_delta = analog_last_raw_delta[idx]
            if raw_delta != 0:
                if last_delta != 0:
                    direction_changed = (raw_delta > 0 and last_delta < 0) or (raw_delta < 0 and last_delta > 0)
                    if direction_changed and abs(raw_delta) >= ANALOG_DIRECTION_RESET_RAW_DELTA:
                        analog_history[idx].clear()
                        analog_history[idx].append(raw)
                        analog_fast_window_remaining[idx] = ANALOG_DIRECTION_FAST_WINDOW_SAMPLES
                if abs(raw_delta) >= ANALOG_TAIL_CUT_JUMP_RESET_DELTA:
                    jump_snap_now = True
                analog_last_raw_delta[idx] = raw_delta
        if cal_runtime.process_autocal_sample(idx, raw, now):
            continue
        current_autocal_idx = cal_runtime.current_autocal_index()

        if (not cal_runtime.autocal_active or current_autocal_idx != idx) and last_raw is not None and abs(raw - last_raw) < ANALOG_RAW_MIN_CHANGE:
            last_send = analog_last_send_ms[idx]
            if ANALOG_SEND_INTERVAL_MS and last_send is not None:
                now = adafruit_ticks.ticks_ms()
                if adafruit_ticks.ticks_diff(now, last_send) < ANALOG_SEND_INTERVAL_MS:
                    continue
        if not cal_runtime.autocal_active:
            cal_runtime.update_calibration_tracking(idx, raw)
        cal = calibration.get(source, {}).get(name)
        if cal is None:
            legacy = CALIBRATION_LEGACY_MAP.get(name)
            if legacy:
                cal = calibration.get(source, {}).get(legacy)
        if (cal is None or cal.get("min") is None or cal.get("max") is None):
            tracked = cal_runtime.get_tracking_calibration(idx)
            if tracked is not None:
                cal = tracked
        event_id = analog_entry.get("event_id")
        window = profile["window"]
        raw_stable = False
        if profile["is_named_pot"] and last_raw is not None:
            raw_stable = abs(raw - last_raw) <= ANALOG_TAIL_CUT_RAW_STABLE_DELTA
            raw_max_default = ANALOG_RAW_MAX_DEFAULT_EXTERNAL if source == "external" else ANALOG_RAW_MAX_DEFAULT_INTERNAL
            near_endpoint = raw <= ANALOG_TAIL_CUT_ENDPOINT_RAW_MAX or raw >= (raw_max_default - ANALOG_TAIL_CUT_ENDPOINT_RAW_MAX)
            if near_endpoint:
                raw_stable = True
        if profile["is_named_pot"]:
            if raw_stable:
                analog_raw_stable_count[idx] += 1
            else:
                analog_raw_stable_count[idx] = 0
        if raw_stable:
            median_raw = raw
            analog_history[idx].clear()
            analog_history[idx].append(raw)
        elif window <= 1:
            median_raw = raw
        else:
            history = analog_history[idx]
            history.append(raw)
            if len(history) > window:
                history.pop(0)
            median_raw = median_window_value(history)

        calibrated = apply_calibration(median_raw, cal, CALIBRATION_ENABLED)
        calibrated = clamp_value(calibrated, 0, 65535)
        if jump_snap_now and profile["is_named_pot"]:
            analog_filtered[idx] = float(calibrated)
        previous = analog_filtered[idx]
        if previous is None:
            filtered = float(calibrated)
        else:
            diff = abs(calibrated - previous)
            if analog_fast_window_remaining[idx] > 0:
                alpha = profile["alpha_fast"]
                analog_fast_window_remaining[idx] -= 1
            else:
                alpha = profile["alpha_fast"] if diff >= profile["threshold"] else profile["alpha_slow"]
            filtered = previous + (alpha * (calibrated - previous))
        analog_filtered[idx] = filtered
        filtered_value = int(round(filtered))
        if profile["is_named_pot"] and raw_stable:
            if raw_stable and abs(filtered_value - calibrated) <= ANALOG_TAIL_CUT_FILTER_DELTA:
                filtered = float(calibrated)
                analog_filtered[idx] = filtered
                filtered_value = calibrated
            elif analog_raw_stable_count[idx] >= ANALOG_TAIL_CUT_STABLE_SNAP_SAMPLES:
                filtered = float(calibrated)
                analog_filtered[idx] = filtered
                filtered_value = calibrated

        value = scale_analog_value(
            filtered_value,
            cal,
            source,
            ANALOG_OUTPUT_MODE,
            ANALOG_PERCENT_RANGE,
            ANALOG_RAW_MAX_DEFAULT_EXTERNAL,
            ANALOG_RAW_MAX_DEFAULT_INTERNAL,
        )
        if ANALOG_OUTPUT_MODE == "percent":
            snap_zero = profile["snap_zero"]
            snap_full = profile["snap_full"]
            if snap_zero > 0 and value <= snap_zero:
                value = 0
            elif snap_full > 0 and value >= (ANALOG_PERCENT_RANGE - snap_full):
                value = ANALOG_PERCENT_RANGE
            if profile["reverse"]:
                value = ANALOG_PERCENT_RANGE - value
        if profile["is_named_pot"] and value <= ANALOG_POT_ASSUME_ZERO_MAX:
            value = 0
        last_sent = last_sent_values[idx]
        min_change = profile["min_change"]
        idle_min_change = profile["idle_min_change"]
        confirm_samples = profile["confirm_samples"]
        confirm_delta = profile["confirm_delta"]
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
        maybe_log_analog_serial(idx, profile, name, raw, median_raw, calibrated, filtered_value, value, event_id)
        maybe_log_pot_direction(profile, name, raw, median_raw, calibrated, filtered_value, value, last_sent, event_id)

    # Read seesaw encoders (I2C)
    for enc in seesaw_encoders:
        cfg = enc["cfg"]
        enc["deb"].update()
        press_id = cfg.get("press_id")
        if cfg.get("name") == AUTOCAL_TRIGGER_ENCODER:
            autocal_trigger_pressed = autocal_trigger_pressed or enc["deb"].value
        if enc["deb"].rose:
            send_packet(TYPE_BUTTON, press_id, 1)
            maybe_log_encoder_serial(enc, f"Seesaw {cfg.get('name','?')} press")
        if enc["deb"].fell:
            send_packet(TYPE_BUTTON, press_id, 0)
            maybe_log_encoder_serial(enc, f"Seesaw {cfg.get('name','?')} release")

        pos = enc["encoder"].position
        delta = pos - enc["pos"]
        if delta != 0:
            enc["pos"] = pos
            if ENCODER_TRANSITIONS_PER_DETENT <= 1:
                step = int(delta) * ENCODER_STEPS_PER_DETENT
                if step != 0:
                    send_packet(TYPE_ENCODER, cfg.get("delta_id"), step)
                    maybe_log_encoder_serial(enc, f"Seesaw {cfg.get('name','?')} delta={step} pos={pos}")
            else:
                enc["accum"] += int(delta)
                steps = int(enc["accum"] / ENCODER_TRANSITIONS_PER_DETENT)
                if steps != 0:
                    enc["accum"] -= steps * ENCODER_TRANSITIONS_PER_DETENT
                    step = steps * ENCODER_STEPS_PER_DETENT
                    if step != 0:
                        send_packet(TYPE_ENCODER, cfg.get("delta_id"), step)
                        maybe_log_encoder_serial(enc, f"Seesaw {cfg.get('name','?')} delta={step} pos={pos}")

        if DEBUG_ENCODERS:
            now = adafruit_ticks.ticks_ms()
            if adafruit_ticks.ticks_diff(now, enc["last_dbg_ms"]) >= DEBUG_ENCODER_INTERVAL_MS:
                enc["last_dbg_ms"] = now
                dbg_id = 0x80 + (enc["idx"] & 0x0F)
                send_packet(TYPE_DEBUG, dbg_id, int(pos) & 0xFFFF)

    if DEBUG_UART:
        now = adafruit_ticks.ticks_ms()
        if packet_writer.last_activity_ms and adafruit_ticks.ticks_diff(now, packet_writer.last_activity_ms) > DEBUG_UART_IDLE_SUPPRESS_MS:
            pass
        elif DEBUG_GLOBAL and adafruit_ticks.ticks_diff(now, last_debug_ms) >= DEBUG_INTERVAL_MS:
            last_debug_ms = now
            debug_counter = (debug_counter + 1) & 0xFFFF
            send_packet(TYPE_DEBUG, DEBUG_EVENT_ID, debug_counter)

    if AUTOCAL_TRIGGER_BUTTON and AUTOCAL_TRIGGER_BUTTON in buttons:
        autocal_trigger_pressed = autocal_trigger_pressed or buttons[AUTOCAL_TRIGGER_BUTTON].value
    cal_runtime.update_autocal_trigger(autocal_trigger_pressed)
    autocal_trigger_pressed = False

    flush_tx()

    time.sleep(0.01)