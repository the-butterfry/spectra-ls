#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import csv
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

FEATHER_PIN_TO_GPIO = {
    "TX": "GP0",
    "RX": "GP1",
    "SDA": "GP2",
    "SCL": "GP3",
    "A0": "GP26 / ADC0",
    "A1": "GP27 / ADC1",
    "A2": "GP28 / ADC2",
    "A3": "GP29 / ADC3",
}

CSV_HEADER = [
    "Friendly Name",
    "Knob or Description",
    "Area",
    "Subgroup",
    "Input Name",
    "Subsystem",
    "Signal/Channel",
    "RP2040 Feather Pin",
    "RP2040 GPIO",
    "ESP32 GPIO",
    "Device/Endpoint",
    "I2C Address",
    "Event ID",
    "Enabled",
    "Notes",
]


def board_to_gpio(board_pin: str) -> str:
    if not board_pin:
        return ""
    if board_pin.startswith("board."):
        key = board_pin.split(".", 1)[1]
    else:
        key = board_pin
    return FEATHER_PIN_TO_GPIO.get(key, "")


ACRONYM_MAP = {
    "rp2040": "RP2040",
    "esp32": "ESP32",
    "uart": "UART",
    "i2c": "I2C",
    "ads1015": "ADS1015",
    "oled": "OLED",
    "led": "LED",
    "tx": "TX",
    "rx": "RX",
    "sda": "SDA",
    "scl": "SCL",
    "adc": "ADC",
}

FRIENDLY_NAME_OVERRIDES = {
    "slider_a0": "Spare Slider A0 (unused)",
    "slider_a1": "Lighting Brightness Slider",
    "pot_a2": "Audio Volume Pot",
    "pot_a3": "Spare Pot A3 (unused)",
    "room button": "Lighting Room Select Button",
    "source button": "Lighting Source Toggle Button",
    "back button": "Back Button",
    "home button": "Home Button (Auto-cal Trigger)",
    "prev button": "Previous Track Button",
    "play button": "Play/Pause Button",
    "next button": "Next Track Button",
    "mute button": "Mute Button",
    "select button": "Select Button",
    "menu encoder delta": "Menu Encoder Turn",
    "menu encoder press": "Menu Encoder Center Button",
    "lighting encoder delta": "Lighting Encoder Turn",
    "lighting encoder press": "Lighting Encoder Center Button",
    "OLED Screen": "Main OLED Screen",
    "RP2040 UART TX": "Interconnect: RP2040 UART TX",
    "RP2040 UART RX": "Interconnect: RP2040 UART RX",
    "RP2040 I2C SDA": "Interconnect: RP2040 I2C SDA",
    "RP2040 I2C SCL": "Interconnect: RP2040 I2C SCL",
    "Arylic/Up2Stream UART TX": "Interconnect: ESP32 → Arylic UART TX",
    "Arylic/Up2Stream UART RX": "Interconnect: ESP32 ← Arylic UART RX",
    "ESP32 OLED SDA": "Interconnect: ESP32 OLED SDA",
    "ESP32 OLED SCL": "Interconnect: ESP32 OLED SCL",
    "Hue ring data": "Hue Ring Data",
    "Audio ring data": "Audio Ring Data",
}

AREA_SUBGROUP_OVERRIDES = {
    "OLED Screen": ("Display", "Screen"),
    "slider_a1": ("Lighting Controls", "Lighting Slider"),
    "lighting encoder delta": ("Lighting Controls", "Lighting Encoder (upper)"),
    "lighting encoder press": ("Lighting Controls", "Lighting Encoder (upper)"),
    "room button": ("Lighting Controls", "Lighting Button (lower)"),
    "source button": ("Lighting Controls", "Lighting Button (lower)"),
    "slider_a0": ("Spare/Unused", "Unused Analog"),
    "pot_a3": ("Spare/Unused", "Unused Analog"),
    "pot_a2": ("Audio Controls", "Volume"),
    "play button": ("Audio Controls", "Transport"),
    "next button": ("Audio Controls", "Transport"),
    "prev button": ("Audio Controls", "Transport"),
    "mute button": ("Audio Controls", "Volume"),
    "select button": ("Navigation", "Select"),
    "menu encoder delta": ("Navigation", "Menu Encoder"),
    "menu encoder press": ("Navigation", "Menu Encoder"),
    "back button": ("Navigation", "Back/Cancel"),
    "home button": ("Calibration", "Auto-cal Trigger"),
}

AREA_ORDER = {
    "Lighting Controls": 1,
    "Audio Controls": 2,
    "Navigation": 3,
    "Display": 4,
    "Calibration": 5,
    "Spare/Unused": 6,
}

SUBGROUP_ORDER = {
    "Lighting Encoder (upper)": 1,
    "Lighting Button (lower)": 2,
    "Lighting Slider": 3,
    "Volume": 1,
    "Transport": 2,
    "Menu Encoder": 1,
    "Select": 2,
    "Back/Cancel": 2,
    "Screen": 1,
    "Auto-cal Trigger": 1,
    "Unused Analog": 1,
}

NOTES_OVERRIDES = {
    "slider_a0": "Unused analog input; reserved for calibration/spare slider channel.",
    "slider_a1": "Adjusts lighting brightness; syncs menu selection and applies brightness updates.",
    "pot_a2": "Sets Arylic volume (rate-limited) and updates audio ring activity.",
    "pot_a3": "Unused analog input; reserved for calibration/spare pot channel.",
    "room button": "Cycles the selected lighting room.",
    "source button": "Cycles Arylic input source (audio).",
    "back button": "Menu back/cancel; exits calibration and navigates up a level.",
    "home button": "Auto-cal trigger (held) on RP2040; no ESP32 event sent.",
    "prev button": "Previous track on Arylic.",
    "play button": "Play/Pause on Arylic.",
    "next button": "Next track on Arylic.",
    "mute button": "Toggle mute (shares event id with volume encoder press).",
    "select button": "Menu select/confirm (mirrors menu encoder press).",
    "menu encoder delta": "Scrolls menu items.",
    "menu encoder press": "Menu select/enter; triggers calibration step if active.",
    "lighting encoder delta": "Adjusts lighting hue/saturation (or brightness in brightness mode).",
    "lighting encoder press": "Toggles hue/saturation mode or exits brightness adjust.",
    "OLED Screen": "Main 128x64 OLED display driven by ESP32 I2C.",
}


def friendly_from_input_name(name: str) -> str:
    if not name:
        return ""
    if name.startswith("==="):
        return name
    override = FRIENDLY_NAME_OVERRIDES.get(name)
    if override:
        return override
    parts = name.replace("_", " ").split(" ")
    friendly_parts = []
    for part in parts:
        if not part:
            continue
        if any(ch in part for ch in "/↔→←"):
            friendly_parts.append(part)
            continue
        key = re.sub(r"[^A-Za-z0-9]", "", part).lower()
        if key in ACRONYM_MAP:
            friendly_parts.append(ACRONYM_MAP[key])
            continue
        if re.match(r"^[a-zA-Z]\d+$", part):
            friendly_parts.append(part.upper())
            continue
        if part.isupper():
            friendly_parts.append(part)
            continue
        friendly_parts.append(part.capitalize())
    return " ".join(friendly_parts)


def area_from_input_name(name: str) -> str:
    if not name or name.startswith("==="):
        return ""
    return AREA_SUBGROUP_OVERRIDES.get(name, ("", ""))[0]


def subgroup_from_input_name(name: str) -> str:
    if not name or name.startswith("==="):
        return ""
    return AREA_SUBGROUP_OVERRIDES.get(name, ("", ""))[1]


def sort_key_for_input(name: str) -> tuple:
    area = area_from_input_name(name)
    subgroup = subgroup_from_input_name(name)
    return (
        AREA_ORDER.get(area, 99),
        SUBGROUP_ORDER.get(subgroup, 99),
        area,
        subgroup,
        name,
    )


def format_i2c_addresses(addresses: List[Any]) -> str:
    if not addresses:
        return ""
    rendered = []
    for addr in addresses:
        if isinstance(addr, int):
            rendered.append(f"0x{addr:02X}")
        else:
            rendered.append(str(addr))
    return " or ".join(rendered)


def safe_eval(node: ast.AST, env: Dict[str, Any]) -> Any:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        return env.get(node.id, node.id)
    if isinstance(node, ast.Attribute):
        base = safe_eval(node.value, env)
        if isinstance(base, str):
            return f"{base}.{node.attr}"
        return f"{node.value}.{node.attr}"
    if isinstance(node, ast.Tuple):
        return tuple(safe_eval(elt, env) for elt in node.elts)
    if isinstance(node, ast.List):
        return [safe_eval(elt, env) for elt in node.elts]
    if isinstance(node, ast.Dict):
        return {safe_eval(k, env): safe_eval(v, env) for k, v in zip(node.keys, node.values)}
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        val = safe_eval(node.operand, env)
        if isinstance(val, (int, float)):
            return -val
    return None


def parse_code_py(code_path: Path) -> Dict[str, Any]:
    tree = ast.parse(code_path.read_text(encoding="utf-8"))
    env: Dict[str, Any] = {}
    for stmt in tree.body:
        if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1:
            target = stmt.targets[0]
            if isinstance(target, ast.Name):
                value = safe_eval(stmt.value, env)
                env[target.id] = value
        elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            value = safe_eval(stmt.value, env)
            env[stmt.target.id] = value
    return env


def parse_esp32_yaml(yaml_path: Path, keys: List[str]) -> Dict[str, str]:
    values: Dict[str, str] = {}
    pattern_by_key = {
        key: re.compile(rf"^\s*{re.escape(key)}:\s*([^\s#]+)") for key in keys
    }
    for line in yaml_path.read_text(encoding="utf-8").splitlines():
        for key, pattern in pattern_by_key.items():
            match = pattern.search(line)
            if match:
                values[key] = match.group(1)
    return values


def section_row(title: str) -> List[str]:
    return [f"=== {title} ===", "", "", "", "", "", "", "", "", "", ""]


def build_rows(env: Dict[str, Any], esp32: Dict[str, str]) -> List[List[str]]:
    rows: List[List[str]] = []

    rp_tx = esp32.get("rp2040_uart_tx", "")
    rp_rx = esp32.get("rp2040_uart_rx", "")
    ary_tx = esp32.get("arylic_uart_tx", "")
    ary_rx = esp32.get("arylic_uart_rx", "")
    oled_sda = esp32.get("oled_sda_pin", "")
    oled_scl = esp32.get("oled_scl_pin", "")
    oled_addr = esp32.get("oled_address", "")
    hue_ring = esp32.get("hue_ring_pin", "")
    audio_ring = esp32.get("audio_ring_pin", "")

    internal_rows: List[List[str]] = []
    physical_rows: List[List[str]] = []

    internal_rows.append(
        [
            "RP2040 UART TX",
            "RP2040↔ESP32 UART",
            "TX → ESP32 RX",
            "board.TX",
            board_to_gpio("board.TX"),
            f"{rp_rx} (RX)" if rp_rx else "",
            "ESP32-S3 UART RX",
            "",
            "",
            "",
            "",
        ]
    )
    internal_rows.append(
        [
            "RP2040 UART RX",
            "RP2040↔ESP32 UART",
            "RX ← ESP32 TX",
            "board.RX",
            board_to_gpio("board.RX"),
            f"{rp_tx} (TX)" if rp_tx else "",
            "ESP32-S3 UART TX",
            "",
            "",
            "",
            "",
        ]
    )
    internal_rows.append(
        [
            "RP2040 I2C SDA",
            "RP2040 I2C bus",
            "SDA",
            "board.SDA",
            board_to_gpio("board.SDA"),
            "",
            "PCF8575 + Seesaw encoders + ADS1015 (optional)",
            "",
            "",
            "",
            "",
        ]
    )
    internal_rows.append(
        [
            "RP2040 I2C SCL",
            "RP2040 I2C bus",
            "SCL",
            "board.SCL",
            board_to_gpio("board.SCL"),
            "",
            "PCF8575 + Seesaw encoders + ADS1015 (optional)",
            "",
            "",
            "",
            "",
        ]
    )

    if oled_sda or oled_scl or oled_addr:
        esp32_gpio = ""
        if oled_sda and oled_scl:
            esp32_gpio = f"{oled_sda} (SDA), {oled_scl} (SCL)"
        elif oled_sda:
            esp32_gpio = f"{oled_sda} (SDA)"
        elif oled_scl:
            esp32_gpio = f"{oled_scl} (SCL)"
        physical_rows.append(
            [
                "OLED Screen",
                "Display",
                "I2C device",
                "",
                "",
                esp32_gpio,
                "OLED SSD1306/SSD1309",
                oled_addr,
                "",
                "",
                "",
            ]
        )

    analog_names = list(env.get("ANALOG_NAMES", []))
    analog_enabled = list(env.get("ANALOG_CHANNELS_ENABLED", []))
    analog_event_ids = list(env.get("ANALOG_EVENT_IDS", []))
    internal_pins = list(env.get("INTERNAL_ADC_PINS", []))
    adc_mode = env.get("ADC_MODE", "")
    external_addr = env.get("EXTERNAL_ADC_ADDRESS")
    external_addr_str = f"0x{external_addr:02X}" if isinstance(external_addr, int) else ""

    for idx, name in enumerate(analog_names):
        internal_pin = internal_pins[idx] if idx < len(internal_pins) else ""
        internal_pin_str = str(internal_pin) if internal_pin else ""
        internal_gpio = board_to_gpio(internal_pin_str)
        event_id = analog_event_ids[idx] if idx < len(analog_event_ids) else ""
        enabled = analog_enabled[idx] if idx < len(analog_enabled) else ""
        signal = f"ADS1015 P{idx} (external) / ADC{idx} (internal)"
        endpoint = f"ADS1015 analog input channel P{idx}"
        notes = f"ADC_MODE={adc_mode}; internal pins unused unless ADC_MODE='internal'" if adc_mode else ""
        physical_rows.append(
            [
                str(name),
                "Analog input (ADS1015 / internal ADC)",
                signal,
                f"{internal_pin_str} (internal only)" if internal_pin_str else "",
                f"{internal_gpio} (internal only)" if internal_gpio else "",
                "",
                endpoint,
                external_addr_str,
                str(event_id) if event_id != "" else "",
                str(enabled) if enabled != "" else "",
                notes,
            ]
        )

    button_pins: Dict[str, Any] = env.get("BUTTON_PINS", {}) or {}
    button_event_ids: Dict[str, Any] = env.get("BUTTON_EVENT_IDS", {}) or {}
    pcf_addresses = env.get("PCF8575_ADDRESSES", []) or []
    pcf_addr_str = format_i2c_addresses(list(pcf_addresses))

    for name, pin in button_pins.items():
        event_id = button_event_ids.get(name, "")
        notes = "Used for autocal trigger only; no ESP32 event" if name == "home" else ""
        if name == "mute":
            notes = "Shares event id with volume encoder press" if not notes else notes
        physical_rows.append(
            [
                f"{name} button",
                "PCF8575 button expander",
                f"P{pin}",
                "board.SDA/board.SCL",
                "GP2/GP3",
                "",
                "PCF8575 button expander",
                pcf_addr_str,
                str(event_id) if event_id != "" else "",
                "True",
                notes,
            ]
        )

    seesaw_encoders = env.get("SEESAW_ENCODERS", []) or []
    transitions = env.get("ENCODER_TRANSITIONS_PER_DETENT", "")
    steps = env.get("ENCODER_STEPS_PER_DETENT", "")
    encoder_notes = ""
    if transitions != "" and steps != "":
        encoder_notes = f"ENCODER_TRANSITIONS_PER_DETENT={transitions}; ENCODER_STEPS_PER_DETENT={steps}"

    for cfg in seesaw_encoders:
        name = cfg.get("name", "encoder")
        address = cfg.get("address")
        addr_str = f"0x{address:02X}" if isinstance(address, int) else ""
        delta_id = cfg.get("delta_id", "")
        press_id = cfg.get("press_id", "")
        physical_rows.append(
            [
                f"{name} encoder delta",
                "Seesaw rotary encoder",
                "Incremental delta",
                "board.SDA/board.SCL",
                "GP2/GP3",
                "",
                f"Seesaw @{addr_str} ({name})" if addr_str else f"Seesaw ({name})",
                addr_str,
                str(delta_id) if delta_id != "" else "",
                "True",
                encoder_notes,
            ]
        )
        physical_rows.append(
            [
                f"{name} encoder press",
                "Seesaw rotary encoder",
                "Digital button (Seesaw pin 24)",
                "board.SDA/board.SCL",
                "GP2/GP3",
                "",
                f"Seesaw @{addr_str} ({name})" if addr_str else f"Seesaw ({name})",
                addr_str,
                str(press_id) if press_id != "" else "",
                "True",
                "",
            ]
        )

    internal_rows.append(
        [
            "Arylic/Up2Stream UART TX",
            "ESP32↔Arylic UART",
            "TX → Arylic RX",
            "",
            "",
            f"{ary_tx} (TX)" if ary_tx else "",
            "Arylic Up2Stream PRO UART RX",
            "",
            "",
            "",
            "",
        ]
    )
    internal_rows.append(
        [
            "Arylic/Up2Stream UART RX",
            "ESP32↔Arylic UART",
            "RX ← Arylic TX",
            "",
            "",
            f"{ary_rx} (RX)" if ary_rx else "",
            "Arylic Up2Stream PRO UART TX",
            "",
            "",
            "",
            "",
        ]
    )
    internal_rows.append(
        [
            "ESP32 OLED SDA",
            "ESP32 OLED I2C",
            "SDA",
            "",
            "",
            f"{oled_sda} (SDA)" if oled_sda else "",
            "OLED SSD1306/SSD1309",
            "",
            "",
            "",
            "",
        ]
    )
    internal_rows.append(
        [
            "ESP32 OLED SCL",
            "ESP32 OLED I2C",
            "SCL",
            "",
            "",
            f"{oled_scl} (SCL)" if oled_scl else "",
            "OLED SSD1306/SSD1309",
            "",
            "",
            "",
            "",
        ]
    )
    internal_rows.append(
        [
            "Hue ring data",
            "ESP32 LED Ring",
            "Data",
            "",
            "",
            hue_ring,
            "Hue LED ring",
            "",
            "",
            "",
            "",
        ]
    )
    internal_rows.append(
        [
            "Audio ring data",
            "ESP32 LED Ring",
            "Data",
            "",
            "",
            audio_ring,
            "Audio LED ring",
            "",
            "",
            "",
            "",
        ]
    )

    physical_rows_sorted = sorted(physical_rows, key=lambda row: sort_key_for_input(row[0]))
    for row in physical_rows_sorted:
        note_override = NOTES_OVERRIDES.get(row[0])
        if note_override:
            row[-1] = note_override

    rows.append(section_row("Physical inputs (external control surface)"))
    rows.extend(physical_rows_sorted)
    rows.append(section_row("Internal wiring / interconnects"))
    rows.extend(internal_rows)

    rows_with_friendly = [
        [
            friendly_from_input_name(row[0]),
            "",
            area_from_input_name(row[0]),
            subgroup_from_input_name(row[0]),
        ]
        + row
        for row in rows
    ]
    return rows_with_friendly


def write_csv(output_path: Path, rows: List[List[str]]) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(CSV_HEADER)
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Update control-board-wiring.csv from code.py and ESPHome YAML.")
    parser.add_argument(
        "--code-py",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "code.py",
        help="Path to CircuitPython code.py (default: repo code.py)",
    )
    parser.add_argument(
        "--esp32-yaml",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "control-board-esp32.yaml",
        help="Path to control-board-esp32.yaml",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "control-board-wiring.csv",
        help="Path to output CSV",
    )
    args = parser.parse_args()

    env = parse_code_py(args.code_py)
    esp32 = parse_esp32_yaml(
        args.esp32_yaml,
        [
            "rp2040_uart_tx",
            "rp2040_uart_rx",
            "arylic_uart_tx",
            "arylic_uart_rx",
            "oled_sda_pin",
            "oled_scl_pin",
            "oled_address",
            "hue_ring_pin",
            "audio_ring_pin",
        ],
    )
    rows = build_rows(env, esp32)
    write_csv(args.output, rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
