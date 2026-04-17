## Description: RP2040 boot-time USB serial mode configuration for Spectra LS.
## Version: 2026.04.17.1
## Last updated: 2026-04-17
#
# RP FILE CONTRACT:
# - Owns boot-time USB CDC toggles only.
# - Must NOT contain runtime loop logic, input scanning, packet protocol, or calibration logic.

import usb_cdc

# Enable serial console, disable REPL on USB if needed
usb_cdc.enable(console=True, data=True)
