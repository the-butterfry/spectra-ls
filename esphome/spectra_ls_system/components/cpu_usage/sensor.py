import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor
from esphome.const import UNIT_PERCENT, ICON_GAUGE

from . import cpu_usage_ns

CpuUsageSensor = cpu_usage_ns.class_("CpuUsageSensor", cg.PollingComponent, sensor.Sensor)

CONF_CORE0 = "core0"
CONF_CORE1 = "core1"
CONF_LOGGING_ENABLED = "logging_enabled"
CONF_LOG_INTERVAL = "log_interval"
CONF_LOG_TASKS_ENABLED = "log_tasks_enabled"
CONF_LOG_TASKS_TOP = "log_tasks_top"
CONF_LOG_TASKS_INTERVAL = "log_tasks_interval"

CONFIG_SCHEMA = sensor.sensor_schema(
    CpuUsageSensor,
    unit_of_measurement=UNIT_PERCENT,
    accuracy_decimals=1,
    icon=ICON_GAUGE,
).extend(
    {
        cv.Optional(CONF_CORE0): sensor.sensor_schema(
            unit_of_measurement=UNIT_PERCENT,
            accuracy_decimals=1,
            icon=ICON_GAUGE,
        ),
        cv.Optional(CONF_CORE1): sensor.sensor_schema(
            unit_of_measurement=UNIT_PERCENT,
            accuracy_decimals=1,
            icon=ICON_GAUGE,
        ),
        cv.Optional(CONF_LOGGING_ENABLED, default=False): cv.boolean,
        cv.Optional(CONF_LOG_INTERVAL, default="5s"): cv.positive_time_period_milliseconds,
        cv.Optional(CONF_LOG_TASKS_ENABLED, default=False): cv.boolean,
        cv.Optional(CONF_LOG_TASKS_TOP, default=5): cv.int_range(min=1, max=20),
        cv.Optional(CONF_LOG_TASKS_INTERVAL, default="10s"): cv.positive_time_period_milliseconds,
    }
).extend(cv.polling_component_schema("10s"))


async def to_code(config):
    var = await sensor.new_sensor(config)
    await cg.register_component(var, config)

    if CONF_CORE0 in config:
        core0 = await sensor.new_sensor(config[CONF_CORE0])
        cg.add(var.set_core0_sensor(core0))

    if CONF_CORE1 in config:
        core1 = await sensor.new_sensor(config[CONF_CORE1])
        cg.add(var.set_core1_sensor(core1))

    cg.add(var.set_logging_enabled(config[CONF_LOGGING_ENABLED]))
    if CONF_LOG_INTERVAL in config:
        cg.add(var.set_log_interval_ms(config[CONF_LOG_INTERVAL].total_milliseconds))
    cg.add(var.set_log_tasks_enabled(config[CONF_LOG_TASKS_ENABLED]))
    if CONF_LOG_TASKS_TOP in config:
        cg.add(var.set_log_tasks_top(config[CONF_LOG_TASKS_TOP]))
    if CONF_LOG_TASKS_INTERVAL in config:
        cg.add(var.set_log_tasks_interval_ms(config[CONF_LOG_TASKS_INTERVAL].total_milliseconds))
