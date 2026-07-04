# Description: ESPHome registration glue for Spectra CPU usage custom component.
# Version: 2026.06.22.1
# Last updated: 2026-06-22

import esphome.codegen as cg

CODEOWNERS = ["@local"]
DEPENDENCIES = ["sensor"]
AUTO_LOAD = ["sensor"]

cpu_usage_ns = cg.esphome_ns.namespace("cpu_usage")
