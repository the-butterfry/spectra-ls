import esphome.codegen as cg

CODEOWNERS = ["@local"]
DEPENDENCIES = ["sensor"]
AUTO_LOAD = ["sensor"]

cpu_usage_ns = cg.esphome_ns.namespace("cpu_usage")
