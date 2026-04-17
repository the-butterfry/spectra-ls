# Description: Shared RP2040 firmware constants for Spectra LS input/event contracts.
# Version: 2026.04.17.1
# Last updated: 2026-04-17

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
