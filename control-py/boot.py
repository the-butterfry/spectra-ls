import usb_cdc

# Enable serial console, disable REPL on USB if needed
usb_cdc.enable(console=True, data=True)