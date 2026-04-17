# Description: PCF8575 input setup and decode helpers for Spectra LS RP2040 firmware.
# Version: 2026.04.17.1
# Last updated: 2026-04-17

import digitalio
from adafruit_debouncer import Debouncer


def setup_pcf_inputs(
    pcf,
    use_pullups,
    button_pins,
    mode_selector_pins,
    control_class_pins,
):
    buttons = {}
    mode_selector_inputs = []
    control_class_inputs = []

    if pcf is None:
        return buttons, mode_selector_inputs, control_class_inputs

    for name, pin in button_pins.items():
        p = pcf.get_pin(pin)
        try:
            if use_pullups:
                p.switch_to_input(pull=digitalio.Pull.UP)
            else:
                p.switch_to_input()
        except NotImplementedError:
            p.direction = digitalio.Direction.INPUT
        buttons[name] = Debouncer(lambda p=p: not p.value)

    for idx, pin in enumerate(mode_selector_pins):
        p = pcf.get_pin(pin)
        try:
            if use_pullups:
                p.switch_to_input(pull=digitalio.Pull.UP)
            else:
                p.switch_to_input()
        except NotImplementedError:
            p.direction = digitalio.Direction.INPUT
        mode_selector_inputs.append({"index": idx, "deb": Debouncer(lambda p=p: not p.value)})

    for pin in control_class_pins:
        p = pcf.get_pin(pin)
        try:
            if use_pullups:
                p.switch_to_input(pull=digitalio.Pull.UP)
            else:
                p.switch_to_input()
        except NotImplementedError:
            p.direction = digitalio.Direction.INPUT
        control_class_inputs.append(Debouncer(lambda p=p: not p.value))

    return buttons, mode_selector_inputs, control_class_inputs


def decode_mode_selector(states):
    active_count = 0
    active_idx = None
    for idx, state in enumerate(states):
        if state:
            active_count += 1
            active_idx = idx
    if active_count == 1:
        return active_idx
    return None


def decode_control_class(states, control_class_map):
    if len(states) != 2:
        return None
    return control_class_map.get((states[0], states[1]))
