# Description: UART packet writer helpers for Spectra LS RP2040 firmware.
# Version: 2026.04.17.1
# Last updated: 2026-04-17

import adafruit_ticks

TYPE_BUTTON = 0x01
TYPE_ANALOG = 0x02
TYPE_ENCODER = 0x03
TYPE_DEBUG = 0xF0


class PacketWriter:
    def __init__(self, uart, debug_enabled=True, max_buffer=256):
        self.uart = uart
        self.debug_enabled = debug_enabled
        self.buffer = bytearray(max_buffer)
        self.tx_len = 0
        self.last_activity_ms = 0

    def send_packet(self, event_type, event_id, value):
        if event_id is None:
            return
        if not self.debug_enabled and event_type == TYPE_DEBUG:
            return

        ts = adafruit_ticks.ticks_ms() & 0xFFFFFFFF
        if self.tx_len + 10 > len(self.buffer):
            self.flush()

        self.buffer[self.tx_len] = 0xAA
        self.buffer[self.tx_len + 1] = 0x55
        self.buffer[self.tx_len + 2] = event_type & 0xFF
        self.buffer[self.tx_len + 3] = event_id & 0xFF
        self.buffer[self.tx_len + 4] = (ts >> 24) & 0xFF
        self.buffer[self.tx_len + 5] = (ts >> 16) & 0xFF
        self.buffer[self.tx_len + 6] = (ts >> 8) & 0xFF
        self.buffer[self.tx_len + 7] = ts & 0xFF

        value &= 0xFFFF
        self.buffer[self.tx_len + 8] = (value >> 8) & 0xFF
        self.buffer[self.tx_len + 9] = value & 0xFF
        self.tx_len += 10

        if event_type != TYPE_DEBUG:
            self.last_activity_ms = ts

    def flush(self):
        if self.tx_len > 0:
            self.uart.write(self.buffer[:self.tx_len])
            self.tx_len = 0
