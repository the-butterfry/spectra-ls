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
INTERNAL_ADC_PINS = (board.A0, board.A1, board.A2, board.A3)
ANALOG_NAMES = ("slider_a0", "slider_a1", "pot_a2", "pot_a3")
ANALOG_ENABLED = True
ANALOG_CHANNELS_ENABLED = (False, True, True, False)
ANALOG_OUTPUT_MODE = "percent"  # "raw" or "percent"
ANALOG_PERCENT_RANGE = 100
ANALOG_RAW_MAX_DEFAULT_INTERNAL = 65535
ANALOG_RAW_MAX_DEFAULT_EXTERNAL = 32767
ANALOG_SAMPLES = 3  # oversample count per read
ANALOG_MEDIAN_WINDOW = 3  # rolling median window size
ANALOG_FILTER_ALPHA_SLOW = 0.18  # EMA when stable
ANALOG_FILTER_ALPHA_FAST = 0.55  # EMA when moving quickly
ANALOG_FILTER_FAST_THRESHOLD_PCT = 2.5  # % of full-scale to switch to fast
ANALOG_MIN_CHANGE = 1  # min output step before sending
ANALOG_SEND_INTERVAL_MS = 20  # 0 disables rate limiting
ANALOG_SNAP_ZERO_PCT = 2  # 0 disables snap
ANALOG_SNAP_FULL_PCT = 2  # 0 disables snap
ANALOG_SNAP_ZERO_PCT_BY_NAME = {"slider_a1": 2, "pot_a2": 2, "pot_a3": 2}
ANALOG_SNAP_FULL_PCT_BY_NAME = {"slider_a1": 2, "pot_a2": 2, "pot_a3": 2}

# Calibration file (RP2040 local)
CALIBRATION_FILE = "/calibration.json"

# Debug over UART (ESP-readable)
DEBUG_UART = True
DEBUG_INTERVAL_MS = 1000
DEBUG_EVENT_ID = 0
DEBUG_ENCODERS = True
DEBUG_ENCODER_INTERVAL_MS = 500
DEBUG_ENCODER_SERIAL = True
DEBUG_BUTTONS_SERIAL = False
DEBUG_ANALOG_SERIAL = False
DEBUG_SEESAW_INIT = True
DEBUG_PCF8575_INIT = True
DEBUG_I2C_SCAN = True

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

if I2C_SCAN_ON_BOOT:
    while not i2c.try_lock():
        pass
    try:
        addrs = i2c.scan()
        if DEBUG_I2C_SCAN:
            print("I2C scan:", [f"0x{addr:02X}" for addr in addrs])
    finally:
        i2c.unlock()

def i2c_has_address(bus, address):
    while not bus.try_lock():
        pass
    try:
        return address in bus.scan()
    finally:
        bus.unlock()

def clamp_value(value, min_value, max_value):
    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    return value

def load_calibration():
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

def get_calibration_for_name(calibration, source, name):
    if not calibration:
        return None
    return calibration.get(source, {}).get(name)

def apply_calibration(raw_value, cal):
    if not cal:
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
    return clamp_value(scaled, 0, 65535)

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
    if samples <= 1:
        return analog.value
    total = 0
    for _ in range(samples):
        total += analog.value
    return int(total / samples)

def analog_name_for_index(idx):
    return ANALOG_NAMES[idx] if idx < len(ANALOG_NAMES) else f"analog_{idx}"


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

# Slider inputs (internal ADC preferred; ADS1015 optional)
sliders = []
adc_source = "internal"

if ANALOG_ENABLED:
    ads_present = i2c_has_address(i2c, EXTERNAL_ADC_ADDRESS)
    if ADC_MODE == "external" and not ads_present:
        raise RuntimeError(f"ADS1015 not found at 0x{EXTERNAL_ADC_ADDRESS:02X}. Check wiring or set ADC_MODE = 'internal'.")

    use_external_adc = ADC_MODE == "external" or (ADC_MODE == "auto" and ads_present)

    if use_external_adc:
        try:
            from adafruit_ads1x15.analog_in import AnalogIn  # type: ignore
            import adafruit_ads1x15.ads1015 as ADS  # type: ignore
            import adafruit_ads1x15.ads1x15 as ADS1x15  # type: ignore
        except ImportError as exc:
            if ADC_MODE == "external":
                raise RuntimeError("ADS1015 libraries not found. Install in /lib or set ADC_MODE = 'internal'.") from exc
            print("ADS1015 libraries not found; falling back to internal ADC.")
            use_external_adc = False

    if use_external_adc:
        ads = ADS.ADS1015(i2c, address=EXTERNAL_ADC_ADDRESS)

        def _ads_channel(module, index):
            if module is None:
                return None
            return getattr(module, f"P{index}", None)

        channels = []
        for idx in range(4):
            ch = _ads_channel(ADS, idx)
            if ch is None:
                ch = _ads_channel(ADS1x15, idx)
            if ch is None:
                ch = idx
            channels.append(ch)

        sliders = [
            AnalogIn(ads, channels[0]),
            AnalogIn(ads, channels[1]),
            AnalogIn(ads, channels[2]),
            AnalogIn(ads, channels[3]),
        ]
    else:
        import analogio

        sliders = [analogio.AnalogIn(pin) for pin in INTERNAL_ADC_PINS]

    adc_source = "external" if use_external_adc else "internal"

calibration = load_calibration()
calibration.setdefault("internal", {})
calibration.setdefault("external", {})


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

ANALOG_EVENT_IDS = (100, 101, 102, 103)

# Create debouncers
buttons = {}
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

# -----------------------------
# Helper: send binary event to ESP32-S3
# -----------------------------
TYPE_BUTTON = 0x01
TYPE_ANALOG = 0x02
TYPE_ENCODER = 0x03
TYPE_DEBUG = 0xF0

def send_packet(event_type, event_id, value):
    if event_id is None:
        return
    ts = adafruit_ticks.ticks_ms() & 0xFFFFFFFF
    packet = bytearray(10)
    packet[0] = 0xAA
    packet[1] = 0x55
    packet[2] = event_type & 0xFF
    packet[3] = event_id & 0xFF
    packet[4] = (ts >> 24) & 0xFF
    packet[5] = (ts >> 16) & 0xFF
    packet[6] = (ts >> 8) & 0xFF
    packet[7] = ts & 0xFF
    value &= 0xFFFF
    packet[8] = (value >> 8) & 0xFF
    packet[9] = value & 0xFF
    uart.write(packet)

# -----------------------------
# Main loop
# -----------------------------
last_sent_values = [None for _ in range(len(sliders))]
analog_filtered = [None for _ in range(len(sliders))]
analog_history = [[] for _ in range(len(sliders))]
analog_last_send_ms = [None for _ in range(len(sliders))]
debug_counter = 0
last_debug_ms = adafruit_ticks.ticks_ms()

while True:
    # Update button debouncers
    for name, deb in buttons.items():
        deb.update()
        event_id = BUTTON_EVENT_IDS.get(name)
        if deb.fell:
            send_packet(TYPE_BUTTON, event_id, 1)
            if DEBUG_BUTTONS_SERIAL:
                print(f"Button {name} fell (id={event_id})")
        if deb.rose:
            send_packet(TYPE_BUTTON, event_id, 0)
            if DEBUG_BUTTONS_SERIAL:
                print(f"Button {name} rose (id={event_id})")

    # Read sliders (internal ADC preferred; ADS1015 optional)
    for idx, analog in enumerate(sliders):
        if idx < len(ANALOG_CHANNELS_ENABLED) and not ANALOG_CHANNELS_ENABLED[idx]:
            continue
        raw = read_analog_raw(analog, ANALOG_SAMPLES)
        name = analog_name_for_index(idx)
        event_id = ANALOG_EVENT_IDS[idx] if idx < len(ANALOG_EVENT_IDS) else None
        history = analog_history[idx]
        history.append(raw)
        if len(history) > ANALOG_MEDIAN_WINDOW:
            history.pop(0)
        sorted_hist = sorted(history)
        median_raw = sorted_hist[len(sorted_hist) // 2]

        cal = get_calibration_for_name(calibration, adc_source, name)
        calibrated = apply_calibration(median_raw, cal)
        previous = analog_filtered[idx]
        if previous is None:
            filtered = float(calibrated)
        else:
            diff = abs(calibrated - previous)
            threshold = (ANALOG_FILTER_FAST_THRESHOLD_PCT / 100.0) * 65535.0
            alpha = ANALOG_FILTER_ALPHA_FAST if diff >= threshold else ANALOG_FILTER_ALPHA_SLOW
            filtered = previous + (alpha * (calibrated - previous))
        analog_filtered[idx] = filtered
        filtered_value = int(round(filtered))

        value = scale_analog_value(filtered_value, cal, adc_source)
        if ANALOG_OUTPUT_MODE == "percent":
            snap_zero = ANALOG_SNAP_ZERO_PCT_BY_NAME.get(name, ANALOG_SNAP_ZERO_PCT)
            snap_full = ANALOG_SNAP_FULL_PCT_BY_NAME.get(name, ANALOG_SNAP_FULL_PCT)
            if snap_zero > 0 and value <= snap_zero:
                value = 0
            elif snap_full > 0 and value >= (ANALOG_PERCENT_RANGE - snap_full):
                value = ANALOG_PERCENT_RANGE
        last_sent = last_sent_values[idx]
        if last_sent is not None and abs(value - last_sent) < ANALOG_MIN_CHANGE:
            continue
        if ANALOG_SEND_INTERVAL_MS:
            now = adafruit_ticks.ticks_ms()
            last_send = analog_last_send_ms[idx]
            if last_send is not None and adafruit_ticks.ticks_diff(now, last_send) < ANALOG_SEND_INTERVAL_MS:
                continue
            analog_last_send_ms[idx] = now
        last_sent_values[idx] = value
        send_packet(TYPE_ANALOG, event_id, value)
        if DEBUG_ANALOG_SERIAL:
            print(f"Analog {name} raw={raw} median={median_raw} filt={filtered_value} out={value} id={event_id}")

    # Read seesaw encoders (I2C)
    for enc in seesaw_encoders:
        cfg = enc["cfg"]
        enc["deb"].update()
        press_id = cfg.get("press_id")
        if enc["deb"].rose:
            send_packet(TYPE_BUTTON, press_id, 1)
            if DEBUG_ENCODER_SERIAL:
                print(f"Seesaw {cfg.get('name','?')} press")
        if enc["deb"].fell:
            send_packet(TYPE_BUTTON, press_id, 0)
            if DEBUG_ENCODER_SERIAL:
                print(f"Seesaw {cfg.get('name','?')} release")

        pos = enc["encoder"].position
        delta = pos - enc["pos"]
        if delta != 0:
            enc["pos"] = pos
            if ENCODER_TRANSITIONS_PER_DETENT <= 1:
                step = int(delta) * ENCODER_STEPS_PER_DETENT
                if step != 0:
                    send_packet(TYPE_ENCODER, cfg.get("delta_id"), step)
                    if DEBUG_ENCODER_SERIAL:
                        print(f"Seesaw {cfg.get('name','?')} delta={step} pos={pos}")
            else:
                enc["accum"] += int(delta)
                steps = int(enc["accum"] / ENCODER_TRANSITIONS_PER_DETENT)
                if steps != 0:
                    enc["accum"] -= steps * ENCODER_TRANSITIONS_PER_DETENT
                    step = steps * ENCODER_STEPS_PER_DETENT
                    if step != 0:
                        send_packet(TYPE_ENCODER, cfg.get("delta_id"), step)
                        if DEBUG_ENCODER_SERIAL:
                            print(f"Seesaw {cfg.get('name','?')} delta={step} pos={pos}")

        if DEBUG_ENCODERS:
            now = adafruit_ticks.ticks_ms()
            if adafruit_ticks.ticks_diff(now, enc["last_dbg_ms"]) >= DEBUG_ENCODER_INTERVAL_MS:
                enc["last_dbg_ms"] = now
                dbg_id = 0x80 + (enc["idx"] & 0x0F)
                send_packet(TYPE_DEBUG, dbg_id, int(pos) & 0xFFFF)

    if DEBUG_UART:
        now = adafruit_ticks.ticks_ms()
        if adafruit_ticks.ticks_diff(now, last_debug_ms) >= DEBUG_INTERVAL_MS:
            last_debug_ms = now
            debug_counter = (debug_counter + 1) & 0xFFFF
            send_packet(TYPE_DEBUG, DEBUG_EVENT_ID, debug_counter)

    time.sleep(0.01)