import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import binary_sensor
from esphome.const import CONF_TYPE

from . import ArylicUart

CONF_ARYLIC_UART_ID = "arylic_uart_id"

TYPE_MUTE = "mute"
TYPE_PLAYING = "playing"

CONFIG_SCHEMA = binary_sensor.binary_sensor_schema().extend(
    {
        cv.GenerateID(CONF_ARYLIC_UART_ID): cv.use_id(ArylicUart),
        cv.Required(CONF_TYPE): cv.one_of(TYPE_MUTE, TYPE_PLAYING, lower=True),
    }
)


async def to_code(config):
    hub = await cg.get_variable(config[CONF_ARYLIC_UART_ID])
    var = await binary_sensor.new_binary_sensor(config)
    if config[CONF_TYPE] == TYPE_MUTE:
        cg.add(hub.set_mute_sensor(var))
    else:
        cg.add(hub.set_playing_sensor(var))
