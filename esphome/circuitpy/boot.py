## Description: RP2040 boot-time USB serial mode configuration for Spectra LS.
## Version: 2026.08.25.5
## Last updated: 2026-08-25
#
# RP FILE CONTRACT:
# - Owns boot-time USB CDC and USB mass-storage exposure toggles.
# - Must NOT contain runtime loop logic, input scanning, packet protocol, or calibration logic.

import storage
import usb_cdc

# Keep serial console/data available for diagnostics regardless of mass-storage policy.
usb_cdc.enable(console=True, data=True)

storage.enable_usb_drive()
print("USB MSC enabled (forced policy rollback: maintenance-first mount mode)")
