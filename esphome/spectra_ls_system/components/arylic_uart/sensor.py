import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor
from esphome.const import CONF_TYPE

from . import ArylicUart

CONF_ARYLIC_UART_ID = "arylic_uart_id"

TYPE_VOLUME = "volume"
TYPE_BASS = "bass"
TYPE_TREBLE = "treble"

CONFIG_SCHEMA = sensor.sensor_schema().extend(
    {
        cv.GenerateID(CONF_ARYLIC_UART_ID): cv.use_id(ArylicUart),
        cv.Required(CONF_TYPE): cv.one_of(TYPE_VOLUME, TYPE_BASS, TYPE_TREBLE, lower=True),
    }
)


async def to_code(config):
    hub = await cg.get_variable(config[CONF_ARYLIC_UART_ID])
    var = await sensor.new_sensor(config)
    sensor_type = config[CONF_TYPE]
    if sensor_type == TYPE_VOLUME:
        cg.add(hub.set_volume_sensor(var))
    elif sensor_type == TYPE_BASS:
        cg.add(hub.set_bass_sensor(var))
    else:
        cg.add(hub.set_treble_sensor(var))
