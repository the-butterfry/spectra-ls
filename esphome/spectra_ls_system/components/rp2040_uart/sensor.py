import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor
from esphome.const import CONF_TYPE

from . import Rp2040UartHub

CONF_RP2040_UART_ID = "rp2040_uart_id"
CONF_SENSOR_ID = "sensor_id"

TYPE_ANALOG = "analog"
TYPE_ENCODER = "encoder"

CONFIG_SCHEMA = sensor.sensor_schema().extend(
    {
        cv.GenerateID(CONF_RP2040_UART_ID): cv.use_id(Rp2040UartHub),
        cv.Required(CONF_TYPE): cv.one_of(TYPE_ANALOG, TYPE_ENCODER, lower=True),
        cv.Required(CONF_SENSOR_ID): cv.uint8_t,
    }
)


async def to_code(config):
    hub = await cg.get_variable(config[CONF_RP2040_UART_ID])
    var = await sensor.new_sensor(config)
    if config[CONF_TYPE] == TYPE_ENCODER:
        cg.add(hub.set_encoder_sensor(config[CONF_SENSOR_ID], var))
    else:
        cg.add(hub.set_analog_sensor(config[CONF_SENSOR_ID], var))
